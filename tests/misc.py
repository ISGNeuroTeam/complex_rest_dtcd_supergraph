"""
Helper module for tests.
"""

import json
from operator import itemgetter

from rest_framework import test

from complex_rest_dtcd_supergraph.settings import KEYS


class APITestCase(test.APITestCase):
    """Wrapper around DRF's test case for multiple DBs.

    See `rest.test.TestCase` for more info.
    """

    databases = "__all__"


def sort_payload(data: dict) -> None:
    """Sort payload dict according to spec in-place.

    See docs or `serializers.py` for more info about the format.
    """

    nodes = data[KEYS.nodes]

    for node in nodes:
        if KEYS.init_ports in node:
            node[KEYS.init_ports] = sorted(
                node[KEYS.init_ports], key=itemgetter(KEYS.yfiles_id)
            )

    data[KEYS.nodes] = sorted(nodes, key=itemgetter(KEYS.yfiles_id))
    data[KEYS.edges] = sorted(
        data[KEYS.edges],
        key=itemgetter(
            KEYS.source_node,
            KEYS.source_port,
            KEYS.target_node,
            KEYS.target_port,
        ),
    )
    data[KEYS.groups] = sorted(
        data.get(KEYS.groups, []), key=itemgetter(KEYS.yfiles_id)
    )


def load_data(path) -> dict:
    """Load from JSON and return sorted graph data."""

    with open(path) as f:
        data = json.load(f)
    sort_payload(data)

    return data
