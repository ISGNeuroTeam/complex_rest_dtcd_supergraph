# Migrations

Neo4j is a schema free or a database with little schema. There are labels for nodes, types for relationships and both can have properties. Hence, property graph. But there’s no *hard* schema determining that all nodes have all the same properties with the same type. The main idea here is to sync database content with application-specific functionality.

`neomodel` library does not require a hard schema either; it is fairly liberal with regards to the database content. However, there are some things we have to keep in mind like [automatic class resolution](https://neomodel.readthedocs.io/en/latest/extending.html#automatic-class-resolution), [mandatory/optional properties](https://neomodel.readthedocs.io/en/latest/properties.html#mandatory-optional-properties) and [existing constraints and indexes](https://neomodel.readthedocs.io/en/latest/getting_started.html#applying-constraints-and-indexes). Finally, there are simple things like renaming, deletion, etc. that we need to sync with older versions of the DB.


## Useful links

- [Schema migration](https://en.wikipedia.org/wiki/Schema_migration) article on Wikipedia.
- [Evolutionary Database Design](https://martinfowler.com/articles/evodb.html) post by Pramod Sadalage & Martin Fowler.
- [Neo4j-Migrations](https://neo4j.com/labs/neo4j-migrations/) tool (it's in Java, but we can use the ideas here).
