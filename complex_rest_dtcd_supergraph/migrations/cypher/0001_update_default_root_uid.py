"""
This migration will try to find old default :Root and set it's UID to 0.
If some other root in this graph has UID=0, generate a new one for it.

See Neo4j Python Driver docs for more info:
https://neo4j.com/docs/api/python-driver/current/api.html#api-documentation
"""

# debug
# import sys
# print("In module:")
# print("  sys.path[0]: ", sys.path[0])
# print("  __package__: ", __package__)
# -----

import argparse
import uuid

from neo4j import GraphDatabase, Transaction

from ... import settings  # FIXME relative import will not work in __main__


ROOT_LABEL = "Root"
ID_PROPERTY = "uid"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reset ID to zero for a Root node with the given UUID."
    )
    parser.add_argument(
        "uuid",
        type=uuid.UUID,
        help="hex UUID of the default Root node",
    )

    return parser.parse_args()


def reset_existing_root_with_zero_uuid(tx: Transaction):
    """Find existing Root node with uid=0 and reset it to random UUID."""

    query = (
        f"MATCH (n:{ROOT_LABEL}) "
        f"WHERE n.{ID_PROPERTY} = $uid "
        f"SET n.{ID_PROPERTY} = replace(randomUUID(), '-', '') "
        "RETURN n"
    )
    result = tx.run(query, uid=settings.DEFAULT_ROOT_UUID.hex)
    record = result.single()  # can be None

    if record:
        node = record["n"]
        return node
    else:
        return None


def set_root_uid_to_zero(tx, uid: uuid.UUID):
    """Find the Root node with given 'uid' and set it to zero."""

    # FIXME this can fail if we already have an existing Root with zero
    # UUID and uniqueness constraint
    query = (
        f"MATCH (n:{ROOT_LABEL}) "
        f"WHERE n.{ID_PROPERTY} = $current "
        f"SET n.{ID_PROPERTY} = $new "
        "RETURN n"
    )

    result = tx.run(
        query,
        current=uid.hex,
        new=settings.DEFAULT_ROOT_UUID.hex,
    )
    record = result.single()  # can be None

    if record:
        node = record["n"]
        return node
    else:
        return None


if __name__ == "__main__":

    args = parse_args()

    uri = f"{settings.protocol}://{settings.address}:{settings.port}"
    driver = GraphDatabase.driver(uri, auth=(settings.user, settings.password))

    with driver.session() as session:
        # reset existing root with zero uid
        old = session.write_transaction(reset_existing_root_with_zero_uuid)
        if old:
            print("Found and reset 'uid' for existing node with zero uid:\n" f"{old}")

        # reset uid for default root
        current = session.write_transaction(set_root_uid_to_zero, args.uuid)
        if current is None:
            raise Exception(
                "Default Root node with the given 'uid' is missing.\n"
                "Did you provide correct ID?"
            )
        else:
            print(
                "Successfully re-set 'uid' for default Root node to zero:\n"
                f"{current}"
            )

    driver.close()
