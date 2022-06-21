from operator import itemgetter

from py2neo import Node, Relationship


def sort_payload(data: dict) -> None:
    """Sort payload dict according to spec in-place."""

    nodes = data["nodes"]

    for node in nodes:
        if "initPorts" in node:
            node["initPorts"] = sorted(node["initPorts"], key=itemgetter("primitiveID"))

    data["nodes"] = sorted(nodes, key=itemgetter("primitiveID"))
    data["edges"] = sorted(
        data["edges"],
        key=itemgetter("sourceNode", "sourcePort", "targetNode", "targetPort"),
    )


def generate_dummy():
    TheMatrix = Node(
        "Movie", title="The Matrix", released=1999, tagline="Welcome to the Real World"
    )
    Keanu = Node("Person", name="Keanu Reeves", born=1964)
    Carrie = Node("Person", name="Carrie-Anne Moss", born=1967)
    Laurence = Node("Person", name="Laurence Fishburne", born=1961)
    Hugo = Node("Person", name="Hugo Weaving", born=1960)
    LillyW = Node("Person", name="Lilly Wachowski", born=1967)
    LanaW = Node("Person", name="Lana Wachowski", born=1965)
    JoelS = Node("Person", name="Joel Silver", born=1952)
    Emil = Node("Person", name="Emil Eifrem", born=1978)

    # Relationships
    LillyWTheMatrix = Relationship(LillyW, "DIRECTED", TheMatrix)
    LanaWTheMatrix = Relationship(LanaW, "DIRECTED", TheMatrix)
    JoelSTheMatrix = Relationship(JoelS, "PRODUCED", TheMatrix)
    KeanuTheMatrix = Relationship(Keanu, "ACTED_IN", TheMatrix)
    KeanuTheMatrix["roles"] = ["Neo"]
    CarrieTheMatrix = Relationship(Carrie, "ACTED_IN", TheMatrix)
    CarrieTheMatrix["roles"] = ["Trinity"]
    LaurenceTheMatrix = Relationship(Laurence, "ACTED_IN", TheMatrix)
    LaurenceTheMatrix["roles"] = ["Morpheus"]
    HugoTheMatrix = Relationship(Hugo, "ACTED_IN", TheMatrix)
    HugoTheMatrix["roles"] = ["Agent Smith"]
    EmilTheMatrix = Relationship(Emil, "ACTED_IN", TheMatrix)
    EmilTheMatrix["roles"] = ["Emil"]

    # Subgraph
    subgraph = (
        TheMatrix
        | Keanu
        | Carrie
        | Laurence
        | Hugo
        | LillyW
        | LanaW
        | JoelS
        | Emil
        | LillyWTheMatrix
        | LanaWTheMatrix
        | JoelSTheMatrix
        | KeanuTheMatrix
        | KeanuTheMatrix
        | CarrieTheMatrix
        | CarrieTheMatrix
        | LaurenceTheMatrix
        | LaurenceTheMatrix
        | HugoTheMatrix
        | HugoTheMatrix
        | EmilTheMatrix
        | EmilTheMatrix
    )

    return subgraph


def generate_data():
    data = {
        "nodes": [
            {"primitiveID": "n1", "layout": {"x": 0, "y": 0}},
            {"primitiveID": "n2", "initPorts": [{"primitiveID": "p3"}]},
            {"primitiveID": "n3"},
            {"primitiveID": "n4"},
        ],
        "edges": [
            {
                "sourceNode": "n1",
                "sourcePort": "p1",
                "targetNode": "n2",
                "targetPort": "p3",
            },
            {
                "sourceNode": "n1",
                "sourcePort": "p2",
                "targetNode": "n3",
                "targetPort": "p4",
            },
            {
                "sourceNode": "n3",
                "sourcePort": "p5",
                "targetNode": "n4",
                "targetPort": "p6",
            },
        ],
    }

    # TODO replace with values from config
    n1 = Node("Node", "_Entity", primitiveID="n1")  # root
    # data tree
    n1d = Node("_Data", "_Composite", primitiveID="n1")
    attr = Node("_Attribute", x=0, y=0)
    n1d_has_attr = Relationship(n1d, "HAS_ATTRIBUTE", attr, _key="layout")
    ###
    n1_n1d = Relationship(n1, "HAS_DATA", n1d)

    n2 = Node("Node", "_Entity", primitiveID="n2")
    # data tree
    n2d = Node("_Data", "_Composite", primitiveID="n2")
    ports = Node("_Array", "_Attribute")
    item0 = Node("_Item", primitiveID="p3")
    ports_contains_item0 = Relationship(ports, "CONTAINS_ITEM", item0, _pos=0)
    n2d_has_ports = Relationship(n2d, "HAS_ATTRIBUTE", ports, _key="initPorts")
    ###
    n2_n2d = Relationship(n2, "HAS_DATA", n2d)

    n3 = Node("Node", "_Entity", primitiveID="n3")
    n3d = Node("_Data", primitiveID="n3")  # data tree
    n3_n3d = Relationship(n3, "HAS_DATA", n3d)

    n4 = Node("Node", "_Entity", primitiveID="n4")
    n4d = Node("_Data", primitiveID="n4")  # data tree
    n4_n4d = Relationship(n4, "HAS_DATA", n4d)

    e1 = Node(
        "Edge",
        "_Entity",
        sourceNode="n1",
        targetNode="n2",
        sourcePort="p1",
        targetPort="p3",
    )
    # data tree
    e1d = Node(
        "_Data", sourceNode="n1", targetNode="n2", sourcePort="p1", targetPort="p3"
    )
    ###
    e1_e1d = Relationship(e1, "HAS_DATA", e1d)
    # link vertex to edge
    n1_e1 = Relationship(n1, "OUT", e1)
    e1_n2 = Relationship(e1, "IN", n2)

    e2 = Node(
        "Edge",
        "_Entity",
        sourceNode="n1",
        targetNode="n3",
        sourcePort="p2",
        targetPort="p4",
    )
    # data tree
    e2d = Node(
        "_Data", sourceNode="n1", targetNode="n3", sourcePort="p2", targetPort="p4"
    )
    ###
    e2_e2d = Relationship(e2, "HAS_DATA", e2d)
    # link vertex to edge
    n1_e2 = Relationship(n1, "OUT", e2)
    e2_n3 = Relationship(e2, "IN", n3)

    e3 = Node(
        "Edge",
        "_Entity",
        sourceNode="n3",
        targetNode="n4",
        sourcePort="p5",
        targetPort="p6",
    )
    # data tree
    e3d = Node(
        "_Data", sourceNode="n3", targetNode="n4", sourcePort="p5", targetPort="p6"
    )
    ###
    e3_e3d = Relationship(e3, "HAS_DATA", e3d)
    # link vertex to edge
    n3_e3 = Relationship(n3, "OUT", e3)
    e3_n4 = Relationship(e3, "IN", n4)

    subgraph = (
        n1_n1d
        | n1d_has_attr
        | n2_n2d
        | ports_contains_item0
        | n2d_has_ports
        | n3_n3d
        | n4_n4d
        | e1_e1d
        | n1_e1
        | e1_n2
        | e2_e2d
        | n1_e2
        | e2_n3
        | e3_e3d
        | n3_e3
        | e3_n4
    )

    return {"data": data, "subgraph": subgraph}
