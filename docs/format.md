# Graph data format for communication between Neo4j and Y-files

The (sub)graph is represented using JSON with the following structure:

```
{
    "nodes": [node, node, ...],
    "edges": [edge, edge, ...],
    "groups" : [group, group, ...]
}
```

Arrays may be empty.

## Nodes

Top-level `nodes` key corresponds to an *array* of objects, each representing a particular node.

Each object is a *mapping* that may contain a variable amount of keys and values of arbitrary nesting. Every node object **must** have a `primitiveID` key with an **unique** ID. In addition, a node may have an array of *ports* in its `initPorts` field, and user-defined properties in its `properties` field.

Example of a valid node object:

```json
{
    "primitiveID": "n1",
    "primitiveName": "name",
    "extensionName": "extension",
    "nodeTitle": "title",
    "properties": {
        "custom_field": {"attribute": "value"}
    },
    "initPorts": [
        {
            "primitiveID": "p1",
            "primitiveName": "port_name",
            "type": "port_type",
            "properties": {"property": "value"}
        }
    ]
}
```

## Edges

`edges` is an array of objects which represent edges.

Every edge object **must** have:
- `sourceNode` and `targetNode` keys corresponding to valid node object IDs.
- `sourcePort` and `targetPort` keys corresponding to valid port IDs on start and end nodes.

Example of a valid edge object

```json
{
    "sourceNode": "n1",
    "targetNode": "n2",
    "sourcePort": "p1",
    "targetPort": "p3",
    "extensionName": "extension",
    "meta": {"field": 42}
}
```

## Requirements

- All IDs must be unique.
- Referential integrity must be preserved: referenced entities must exist within the payload.
