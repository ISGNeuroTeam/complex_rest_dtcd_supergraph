# UNDER CONSTRUCTION

- `Root` node, `Fragment` node (containers)
- `Vertex` node, `Port` nodes, `Edge` relations (content)
- Relations between *containers* and *content*
- JSON from front-end, validation and conversion (awkward format) to objects
    - format details
    - validation details
    - converter
- Replacement
    - Logical flow of replacement: no granular ops, user sends new content, we replace old one using `Manager`
    - What happends: delete difference, merge data, re-connect to container
- Merge gotchas
    - old parent stays
    - old properties
    - clashes

# User guide

Здесь вы найдёте примеры основных операций, которые поддерживает плагин `supergraph`. Обратитесь к документу [Format](format.md) за подробностями о формате JSON файлов, которыми мы обмениваемся с front-end, а также к [OpenAPI schema](openapi.yaml) для обзора URLs.

Для взаимодействия с Neo4j мы используем Object Graph Mapper (OGM) библиотеку [`neomodel`](https://neomodel.readthedocs.io/en/latest/index.html). Логика напоминает работу с моделями Django с поправкой на графы - за подробностями обратитесь к [секции Getting Started](https://neomodel.readthedocs.io/en/latest/getting_started.html).

> Для работы с примерами вы можете использовать *Python shell*. Не забудьте добавить путь к модулю `complex_rest` в переменную `PYTHONPATH`.

## Введение

- для чего нужен плагин
- импорт и прочее

Для начала работы подготовим соединение с Neo4j:

```python
>>> from pprint import pp
>>> from neomodel import clear_neo4j_database, config, db
>>> config.DATABASE_URL = "bolt://neo4j:password@localhost:7687"
>>> clear_neo4j_database(db)
```

## Контейнеры roots и fragments

Community version, только одна БД Neo4j = one big graph. Для деления - разбиваем полотно на суб-графы (связанные между собой узлы и связи). В роли этих суб-графов выступают *корни* и *фрагменты*. Корни делят полотно на **несвязанные суб-графы**; фрагменты в свою очередь делят корневые суб-графы. Для репрезентации корней и фрагментов мы используем Neo4j nodes с лейблами `Root` и `Fragment`. Такие nodes связаны с объектами, которые входят в данный суб-граф корня / фрагмента.

Начнём с одного корня и пары фрагментов:

```python
>>> from models import Root, Fragment
>>> root = Root(name="main").save()
>>> sales = Fragment(name="sales").save()
>>> marketing = Fragment(name="marketing").save()
>>>
>>> root
<Root: {'uid': '6e36897428954a25b5c2aa9a381a84a6', 'name': 'main', 'id': 0}>
>>> sales
<Fragment: {'uid': 'c98020faa5d5452c89cb6c400c9cbded', 'name': 'sales', 'id': 1}>
>>> marketing
<Fragment: {'uid': 'f840ab6aefbb4fd5a7d87de1a4f7f85d', 'name': 'marketing', 'id': 2}>
>>> pp(Fragment.nodes.all())  # Query API похож на Django
[<Fragment: {'uid': 'c98020faa5d5452c89cb6c400c9cbded', 'name': 'sales', 'id': 1}>,
 <Fragment: {'uid': 'f840ab6aefbb4fd5a7d87de1a4f7f85d', 'name': 'marketing', 'id': 2}>]
```

Корни включают в себя набор фрагментов, а фрагменты не могут существовать сами по себе - давайте это исправим:

```python
>>> root.fragments.connect(sales)
True
>>> root.fragments.connect(marketing)
True
>>> pp(root.fragments.all())  # фрагменты, связанные с этим корнем
[<Fragment: {'uid': 'c98020faa5d5452c89cb6c400c9cbded', 'name': 'sales', 'id': 1}>]
```

## TODO Узлы и связи Y-files

## TODO Converter

## TODO Manager

## TODO Всё вместе

- high-level overview of how these fit together



# Old user guide

> The information here is deprecated.

In this guide you'll find examples of core operations provided by this plugin.

Check out check out the  and `neo-tools` library for details on why and how we represent nested structures in the database and [OpenAPI schema](./openapi.yaml) to get a general idea for the plugin.

> You can follow examples using Django-provided shell of `complex_rest` project.

## Vertices and edges

We get vertices and edges in the form of Python dictionaries (check out the [Format](format.md) for details). Here is a couple of simple examples.

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

> We run validation on this data before we proceed further: check consistent IDs, etc. You can see more in `serializers.py` and `fields.py` modules.

## Representation

------------------------------------------------------------------------
>>> UNDER CONSTRUCTIONS
------------------------------------------------------------------------

We want to represent these as graph structures inside Neo4j. Unfortunately, Neo4j cannot store nested objects on either nodes or relationships, so we *do not* have 1:1 mappings for vertices-nodes and edges-relationships. Instead, we represent vertices & edges as *tree structures* and convert back and forth between them. Check out the [Format](./format.md) document for more information.

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

The main operation is a **merge with replacement**. We can do this either for a given fragment, or for the whole graph using the *root* fragment.

### Basic save and read

Let's add some graph data to the `marketing` fragment:

```python
>>> data = {'edges': [], 'nodes': [{'primitiveID': 'amy'}, {'primitiveID': 'bob'}]}
>>> subgraph = converter.load(data)
>>> # .content is a ContentManger for this graph
>>> manager.fragments.content.replace(subgraph, marketing)
```

We just merged (with replacement) new content into the fragment `marketing`. Now the fragment node has a link to the roots of 2 *vertex trees*: a tree-like subgraph of nodes and relationships representing our initial data. Each tree stores the data for a corresponding node.

> Remember that we *cannot* save nested data structures as Neo4j properties. We represent these as tree-like entities on the backend.

We can get this data back just as easy:

```python
>>> subgraph = manager.fragments.content.read(marketing)
>>> data = converter.dump(subgraph)
>>> data
{'edges': [], 'nodes': [{'primitiveID': 'amy'}, {'primitiveID': 'bob'}]}
```

### Merge with replacement

Now for something interesting - let's try and save the following graph in the same fragment:

```python
>>> data = {'edges': [], 'nodes': [{'primitiveID': 'amy'}, {'primitiveID': 'dan'}]}
>>> subgraph = converter.load(data)
>>> manager.fragments.content.replace(subgraph, marketing)
```

The idea here is that we want to **replace** the content of the `marketing` fragment in a smart way:

- create new nodes & relationships
- update existing stuff with new data if needed
- delete the old stuff

We also want to *preserve existing relationships* between updated nodes and other entities in the graph. Here's how we do it:

1. Merge the *root nodes* of the following entity trees:
    1. Vertex trees.
    2. Edge trees.
    3. Group trees (if any).
2. Remove old nodes & relationships.
3. Re-link fragment with the root nodes of new entities to be created.
4. Merge the rest and fragment-entity links.

> See `managers.ContentManager._merge` for details.

In the example above, we create `dan`, delete `bob` and update `amy` vertices. We preserve all connections from `amy` vertex to other intact members of the same graph.

Now the fragment contains just two vertices:

```python
>>> subgraph = manager.fragments.content.read(marketing)
>>> data = converter.dump(subgraph)
>>> data
{'edges': [], 'nodes': [{'primitiveID': 'amy'}, {'primitiveID': 'dan'}]}
```

### Multiple fragments and the root

Let's add some more data to another fragment:

```python
>>> data = {
...  'edges': [{'sourceNode': 'bob',
...          'sourcePort': 'mobile',
...          'targetNode': 'cloe',
...          'targetPort': 'laptop'}],
...  'nodes': [{'primitiveID': 'bob'}, {'primitiveID': 'cloe'}]}
>>> subgraph = converter.load(data)
>>> manager.fragments.content.replace(subgraph, research)
```

The `research` fragment now contains 2 vertex trees and 1 *edge tree*, with a *relationship* between roots of entity trees:

```
(bob_root) --> (edge_root) --> (cloe_root)
```

We can get the *whole* graph (same as the *root* fragment):

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
           {'primitiveID': 'cloe'},
           {'primitiveID': 'dan'}]}
```

Now for something interesting. Let's save the following graph on the `root` fragment:

```python
>>> data = {
...  'edges': [{'sourceNode': 'bob',
...             'sourcePort': 'IoT device',
...             'targetNode': 'eve',
...             'targetPort': 'server'}],
...  'nodes': [{'primitiveID': 'amy'},
...            {'primitiveID': 'bob'},
...            {'primitiveID': 'eve'}]}
>>> subgraph = converter.load(data)
>>> # replaces root fragment by default
>>> manager.fragments.content.replace(subgraph)
```

Here we:

- create `eve` vertex and `bob-eve` edge
- *update* `amy` and `bob` vertices while preserving relationships to parent fragment 
- delete vertices `cloe`, `dan` and `bob-cloe` edge

The state of fragments' content:
- `marketing` fragment still contains `amy` vertex
- `research` fragment still has `bob` vertex
- `eve` vertex and `bob-eve` edge do not belong to *any* fragment

Notes:

- `ContentManger` is responsible for all the logic related to graph updates.