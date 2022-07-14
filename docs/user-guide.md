# User guide

In this guide you'll find examples of core operations provided by this plugin.

> You can follow examples using Django-provided shell of `complex_rest` project.

## Vertices and edges

We get vertices and edges in the form of Python dictionaries (check out the [Format](Format.md) for details). Here is a couple of simple examples.

```python
vertex = {
    "primitiveID": "amy",
    "properties": {
        "height": {"value": 167},
        "age": {"type": "days"}
    }
}
```

Front-end guys call these *nodes*, but we use the term *vertex* because Neo4j has its own nodes, and they are different.

```python
edge = {
    "sourceNode": "amy",
    "sourcePort": "mobile",
    "targetNode": "bob",
    "targetPort": "laptop",
    "connection": {
        "status": 7,
        "online": True
    }
}
```

Edges represent a connection between two nodes and their corresponding ports.

We get these in the form of graphs, like so:

```python
graph = {
    "nodes": [
        {"primitiveID": "amy"},
        {"primitiveID": "bob"}
    ],
    "edges": [
        {
            "sourceNode": "amy",
            "sourcePort": "mobile",
            "targetNode": "bob",
            "targetPort": "laptop"
        }
    ]
}
```

> We run validation on this data before we proceed further: check consistent IDs, etc. You can see more in `serializers` and `fields` modules.

## Representation

We want to represent these as graph structures inside Neo4j. Unfortunately, Neo4j cannot store nested objects on either nodes or relationships, so we *do not* have 1:1 mappings for vertices-nodes and edges-relationships. Instead, we represent vertices & edges as *tree structures* and convert back and forth between them. Check out the [Format](./Format.md) document for more information.

To support that, we use the `Converter` class:

```python
>>> from converters import Converter
>>> converter = Converter()
```

`Converter` can translate between the `graph` dictionary and structures which can be saved with Neo4j - back and forth:

```python
>>> subgraph = converter.load(graph)
>>> original = converter.dump(subgraph)
>>> graph == original
True
```

We use `py2neo` library to work with Neo4j. `subgraph` is a [`Subgraph`](https://py2neo.org/2021.1/data/index.html#py2neo.data.Subgraph) object - an arbitrary collection of nodes and relationships.

## Manager

To start, we need a connection to Neo4j database. `Neo4jGraphManager` provides just that, as well as all database-related operations we are interested in.

```python
>>> from managers import Neo4jGraphManager
>>> manager = Neo4jGraphManager("bolt://localhost:7687", auth=("neo4j", "neo4j"))
>>> manager.clear()  # reset Neo4j database
```

## Fragments

Let's create some **fragments** to work with. These behave just like Django models, except they are [Neo4j OGM models](https://py2neo.org/2021.1/ogm/index.html) from `py2neo`.

```python
>>> from models import Fragment
>>> marketing = Fragment(name="marketing")
>>> research = Fragment(name="research")
>>> sales = Fragment(name="sales")
```

For now these fragments are *unbound*: they exist only in memory, there is no counterpart in Neo4j database. We *bind* them by saving these with the help of a `FragmentManager`.
> `FragmentManager` provides basic CRUD operations for fragments.

```python
>>> # .fragments is a FragmentManager for this graph
>>> manager.fragments.save(marketing, research, sales)
```

Now we have 3 fragments in the database. We use fragments to partition the graph into regions for *security control* and *ease of work*: each fragment may contain a set of vertices and edges between them.

The graph has a special **root** fragment, which includes all *content* of a graph (vertices, edges, groups, etc). All new and existing entities are included in the root fragment by default.

Additional notes:

- Currently, the security control is not implemented.
- Under the hood, we store fragments as **nodes** with a specific label.
- Containment is implemented as a relationship between the fragment node and root nodes of entities (vertices, edges, groups): `(fragment) --> (entity)`
- Currently, we have no idea how to handle connections & interaction between fragments.
- Currently, the root fragment is a *logical construct*; not an instance of `Fragment` model.

## Graph operations

The main operation is a **replacement** of a graph. We can do this either for a given fragment, or for the whole graph using the *root* fragment.

Let's start and add some graph data.

```python
>>> data = {"nodes": [{"primitiveID": "amy"}], "edges": []}
>>> subgraph = converter.load(data)
>>> # .content is a ContentManger for this graph
>>> maanger.fragments.content.replace(subgraph, marketing)
```

We just merged (with replacement) new content into the fragment `marketing`. Now it contains one *vertex tree* with a given ID.

Let's add some more data to another fragment:

```python
>>> data = {
...  'edges': [{'sourceNode': 'bob',
...          'sourcePort': 'mobile',
...          'targetNode': 'cloe',
...          'targetPort': 'laptop'}],
...  'nodes': [{'primitiveID': 'bob'}, {'primitiveID': 'cloe'}]}
>>> subgraph = converter.load(data)
>>> maanger.fragments.content.replace(subgraph, research)
```

The `research` fragment now contains 2 vertex trees and 1 *edge tree*, with a *relationship* between roots of entity trees like so:

```
(bob_root) --> (edge_root) --> (cloe_root)
```

We can get this data back just as easy:

```python
>>> subgraph = manager.fragments.content.read(research)
>>> data = converter.dump(subgraph)
>>> data
{'edges': [{'sourceNode': 'bob',
            'sourcePort': 'mobile',
            'targetNode': 'cloe',
            'targetPort': 'laptop'}],
 'nodes': [{'primitiveID': 'bob'}, {'primitiveID': 'cloe'}]}
```

We can also get the whole graph (notice a node object with `amy` ID):

```python
>>> # reads root fragment by default
>>> subgraph = manager.fragments.content.read()
>>> data = converter.dump(subgraph)
>>> data
{'edges': [{'sourceNode': 'bob',
            'sourcePort': 'mobile',
            'targetNode': 'cloe',
            'targetPort': 'laptop'}],
 'nodes': [{'primitiveID': 'amy'},
           {'primitiveID': 'bob'},
           {'primitiveID': 'cloe'}]}
```

Notes:

- `ContentManger` is responsible for all the logic related to graph updates.


---


## Graph operations workflow

This is a quick recap of how the plugin works.

### Saving graph objects

```
json --> [validation] --> dict
dict --> [converter] --> subgraph
subgraph --> [managers] --> neo4j
```

### Retrieving graph objects

Same as saving, but backwards:

```
neo4j --> [managers] --> subgraph
subgraph --> [converter] --> dict
dict --> json
```

Converter helps to translate back and forth between original data and structures for Neo4j.

Managers support main graph operations.