"""
Helper module for tests.
"""

import json
from operator import itemgetter

from complex_rest_dtcd_supergraph.settings import SCHEMA


KEYS = SCHEMA["keys"]
LABELS = SCHEMA["labels"]
TYPES = SCHEMA["types"]


def sort_payload(data: dict) -> None:
    """Sort payload dict according to spec in-place."""

    nodes = data[KEYS["nodes"]]

    for node in nodes:
        if "initPorts" in node:
            node["initPorts"] = sorted(
                node["initPorts"], key=itemgetter(KEYS["yfiles_id"])
            )

    data[KEYS["nodes"]] = sorted(nodes, key=itemgetter(KEYS["yfiles_id"]))
    data[KEYS["edges"]] = sorted(
        data[KEYS["edges"]],
        key=itemgetter(
            KEYS["source_node"],
            KEYS["source_port"],
            KEYS["target_node"],
            KEYS["target_port"],
        ),
    )


def load_data(path) -> dict:
    """Load and sort graph data."""

    with open(path) as f:
        data = json.load(f)
    sort_payload(data)

    return data


# def generate_dummy():
#     TheMatrix = Node(
#         "Movie", title="The Matrix", released=1999, tagline="Welcome to the Real World"
#     )
#     Keanu = Node("Person", name="Keanu Reeves", born=1964)
#     Carrie = Node("Person", name="Carrie-Anne Moss", born=1967)
#     Laurence = Node("Person", name="Laurence Fishburne", born=1961)
#     Hugo = Node("Person", name="Hugo Weaving", born=1960)
#     LillyW = Node("Person", name="Lilly Wachowski", born=1967)
#     LanaW = Node("Person", name="Lana Wachowski", born=1965)
#     JoelS = Node("Person", name="Joel Silver", born=1952)
#     Emil = Node("Person", name="Emil Eifrem", born=1978)

#     # Relationships
#     LillyWTheMatrix = Relationship(LillyW, "DIRECTED", TheMatrix)
#     LanaWTheMatrix = Relationship(LanaW, "DIRECTED", TheMatrix)
#     JoelSTheMatrix = Relationship(JoelS, "PRODUCED", TheMatrix)
#     KeanuTheMatrix = Relationship(Keanu, "ACTED_IN", TheMatrix)
#     KeanuTheMatrix["roles"] = ["Neo"]
#     CarrieTheMatrix = Relationship(Carrie, "ACTED_IN", TheMatrix)
#     CarrieTheMatrix["roles"] = ["Trinity"]
#     LaurenceTheMatrix = Relationship(Laurence, "ACTED_IN", TheMatrix)
#     LaurenceTheMatrix["roles"] = ["Morpheus"]
#     HugoTheMatrix = Relationship(Hugo, "ACTED_IN", TheMatrix)
#     HugoTheMatrix["roles"] = ["Agent Smith"]
#     EmilTheMatrix = Relationship(Emil, "ACTED_IN", TheMatrix)
#     EmilTheMatrix["roles"] = ["Emil"]

#     # Subgraph
#     subgraph = (
#         TheMatrix
#         | Keanu
#         | Carrie
#         | Laurence
#         | Hugo
#         | LillyW
#         | LanaW
#         | JoelS
#         | Emil
#         | LillyWTheMatrix
#         | LanaWTheMatrix
#         | JoelSTheMatrix
#         | KeanuTheMatrix
#         | KeanuTheMatrix
#         | CarrieTheMatrix
#         | CarrieTheMatrix
#         | LaurenceTheMatrix
#         | LaurenceTheMatrix
#         | HugoTheMatrix
#         | HugoTheMatrix
#         | EmilTheMatrix
#         | EmilTheMatrix
#     )

#     return subgraph


# def generate_data():
#     data = {
#         KEYS["nodes"]: [
#             {KEYS["yfiles_id"]: "n1", "layout": {"x": 0, "y": 0}},
#             {KEYS["yfiles_id"]: "n2", "initPorts": [{KEYS["yfiles_id"]: "p3"}]},
#             {KEYS["yfiles_id"]: "n3"},
#             {KEYS["yfiles_id"]: "n4"},
#         ],
#         KEYS["edges"]: [
#             {
#                 KEYS["source_node"]: "n1",
#                 KEYS["source_port"]: "p1",
#                 KEYS["target_node"]: "n2",
#                 KEYS["target_port"]: "p3",
#             },
#             {
#                 KEYS["source_node"]: "n1",
#                 KEYS["source_port"]: "p2",
#                 KEYS["target_node"]: "n3",
#                 KEYS["target_port"]: "p4",
#             },
#             {
#                 KEYS["source_node"]: "n3",
#                 KEYS["source_port"]: "p5",
#                 KEYS["target_node"]: "n4",
#                 KEYS["target_port"]: "p6",
#             },
#         ],
#     }

#     # TODO replace with values from config
#     n1 = Node(LABELS["node"], LABELS["entity"], primitiveID="n1")  # root
#     # data tree
#     n1d = Node(LABELS["data"], LABELS["composite"], primitiveID="n1")
#     attr = Node(LABELS["attribute"], x=0, y=0)
#     n1d_has_attr = Relationship(n1d, TYPES["has_attribute"], attr, key="layout")
#     ###
#     n1_n1d = Relationship(n1, TYPES["has_data"], n1d)

#     n2 = Node(LABELS["node"], LABELS["entity"], primitiveID="n2")
#     # data tree
#     n2d = Node(LABELS["data"], LABELS["composite"], primitiveID="n2")
#     ports = Node(LABELS["array"], LABELS["attribute"])
#     item0 = Node(LABELS["item"], primitiveID="p3")
#     ports_contains_item0 = Relationship(ports, TYPES["contains_item"], item0, pos=0)
#     n2d_has_ports = Relationship(n2d, TYPES["has_attribute"], ports, key="initPorts")
#     ###
#     n2_n2d = Relationship(n2, TYPES["has_data"], n2d)

#     n3 = Node(LABELS["node"], LABELS["entity"], primitiveID="n3")
#     n3d = Node(LABELS["data"], primitiveID="n3")  # data tree
#     n3_n3d = Relationship(n3, TYPES["has_data"], n3d)

#     n4 = Node(LABELS["node"], LABELS["entity"], primitiveID="n4")
#     n4d = Node(LABELS["data"], primitiveID="n4")  # data tree
#     n4_n4d = Relationship(n4, TYPES["has_data"], n4d)

#     e1 = Node(
#         LABELS["edge"],
#         LABELS["entity"],
#         sourceNode="n1",
#         targetNode="n2",
#         sourcePort="p1",
#         targetPort="p3",
#     )
#     # data tree
#     e1d = Node(
#         LABELS["data"],
#         sourceNode="n1",
#         targetNode="n2",
#         sourcePort="p1",
#         targetPort="p3",
#     )
#     ###
#     e1_e1d = Relationship(e1, TYPES["has_data"], e1d)
#     # link vertex to edge
#     n1_e1 = Relationship(n1, TYPES["out"], e1)
#     e1_n2 = Relationship(e1, TYPES["in"], n2)

#     e2 = Node(
#         LABELS["edge"],
#         LABELS["entity"],
#         sourceNode="n1",
#         targetNode="n3",
#         sourcePort="p2",
#         targetPort="p4",
#     )
#     # data tree
#     e2d = Node(
#         LABELS["data"],
#         sourceNode="n1",
#         targetNode="n3",
#         sourcePort="p2",
#         targetPort="p4",
#     )
#     ###
#     e2_e2d = Relationship(e2, TYPES["has_data"], e2d)
#     # link vertex to edge
#     n1_e2 = Relationship(n1, TYPES["out"], e2)
#     e2_n3 = Relationship(e2, TYPES["in"], n3)

#     e3 = Node(
#         LABELS["edge"],
#         LABELS["entity"],
#         sourceNode="n3",
#         targetNode="n4",
#         sourcePort="p5",
#         targetPort="p6",
#     )
#     # data tree
#     e3d = Node(
#         LABELS["data"],
#         sourceNode="n3",
#         targetNode="n4",
#         sourcePort="p5",
#         targetPort="p6",
#     )
#     ###
#     e3_e3d = Relationship(e3, TYPES["has_data"], e3d)
#     # link vertex to edge
#     n3_e3 = Relationship(n3, TYPES["out"], e3)
#     e3_n4 = Relationship(e3, TYPES["in"], n4)

#     subgraph = (
#         n1_n1d
#         | n1d_has_attr
#         | n2_n2d
#         | ports_contains_item0
#         | n2d_has_ports
#         | n3_n3d
#         | n4_n4d
#         | e1_e1d
#         | n1_e1
#         | e1_n2
#         | e2_e2d
#         | n1_e2
#         | e2_n3
#         | e3_e3d
#         | n3_e3
#         | e3_n4
#     )

#     return {"data": data, "subgraph": subgraph}
