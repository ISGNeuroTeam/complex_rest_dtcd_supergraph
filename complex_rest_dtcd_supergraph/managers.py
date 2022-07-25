"""
Custom managers designed to work with Neo4j database.

These help us abstract management operations for graphs, fragments, etc.
and isolate details and complexity.
"""

from collections import defaultdict
from itertools import chain

from .models import Fragment
from .structures import Content, Edge, Group, Port, Vertex
from .utils import free_properties


class Manager:
    def read(self, fragment: Fragment) -> Content:
        # TODO a lot of queries

        # --------------------------------------------------------------
        # step 1 - get the insides
        # --------------------------------------------------------------
        foreign_key_mapping = defaultdict(set)  # parent:children uid pairs

        # vertices
        vertices = {  # ID:vertex pairs
            vertex.uid: vertex for vertex in fragment.vertices.all()
        }

        # ports
        input_ports, output_ports = {}, {}  # ID:port pairs
        for vertex in vertices.values():
            parent = vertex.uid
            # TODO refactor
            for ip in vertex.input_ports.all():
                input_ports[ip.uid] = ip
                foreign_key_mapping[parent].add(ip.uid)
            for op in vertex.output_ports.all():
                output_ports[op.uid] = op
                foreign_key_mapping[parent].add(op.uid)

        # edges inside the fragment
        edges = {}  # (opID,ipID):edge pairs
        for op in output_ports.values():
            neighbor = op.neighbor.single()  # can be None

            # skip missing ports or ports from outside this fragment
            if neighbor is None or neighbor.uid not in input_ports:
                continue

            edge = op.neighbor.relationship(neighbor)
            edge_uid = (op.uid, neighbor.uid)
            edges[edge_uid] = edge

        # groups
        groups = {group.uid: group for group in fragment.groups.all()}

        # --------------------------------------------------------------
        # step 2 - map to content
        # --------------------------------------------------------------
        groups = [
            Group(uid=g.uid, properties=free_properties(g), meta=g.meta_)
            for g in groups.values()
        ]

        edges = [
            Edge(start=opID, end=ipID, meta=edge.meta_)
            for (opID, ipID), edge in edges.items()
        ]

        ports = [
            Port(uid=p.uid, properties=free_properties(p), meta=p.meta_)
            for p in chain(input_ports.values(), output_ports.values)
        ]

        vs = []
        for uid, v in vertices.items():
            vertex = Vertex(v.uid, properties=free_properties(v), meta=v.meta_)

            # populate ports mappings
            for child_uid in foreign_key_mapping.get(uid, []):
                if child_uid in input_ports:
                    vertex.ports.incoming.add(child_uid)
                else:
                    vertex.ports.outgoing.add(child_uid)

            vs.append[vertex]
        vertices = vs

        return Content(vertices, ports, edges, groups)

    def replace(self, fragment: Fragment, content: Content):
        raise NotImplementedError
