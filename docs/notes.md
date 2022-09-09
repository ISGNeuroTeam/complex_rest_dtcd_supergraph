# Заметки

## Операция `replace_content` класса `Container`

- В конце замены и обновления сущностей мы снова соединяем их с родительским(и) контейнер[ом|ами]. При попытке добавления *уже существующего* узла к новому контейнеру связи со старым **сохраняются**.
- Операция `replace_content` *обновляет* указанные properties на существующих nodes. Эта операция **не производит замену**: старые properties сохраняются (см. функцию [`create_or_update()`](https://neomodel.readthedocs.io/en/latest/module_documentation.html#neomodel.core.StructuredNode.create_or_update)).
    > Например, если пользователь сохранил узел с property `age: 42`, а потом перезаписал тот же узел с парой `online: false`, то node в Neo4j будет хранить *и старые, и новые данные*: `{age: 42, online: false}`.
- Существует возможность **столкновения** между названиями сервисных полей nodes (например, поле `uid`) и user-defined properties в методах вспомогательного класса `management.Merger`.

## Обратная совместимость с предыдущей версией API

Для сохранения совместимости со старой версией API мы оставили некоторые URLs и специальные views для работы c фрагментами и графами рута по-умолчанию. Такие куски можно найти по комментарию:

```python
# TODO deprecate ...
```

### Команда Django `create_default_root`

Эта командаинициализирует дефолтный `Root` node для поддержки совместимости со старым API. Её можно удалить и убрать соответствующую строку из `database_init.sh`, когда front-end перейдёт на самостоятельную работу с рутами.

## Тип ID для примитивов (узлы, порты, тд.)

Когда будет понятно, какие именно ID (uuid, snowflake, etc.) front-end использует для примитивов, можно дополнить или заменить type alias `CustomUniqueIdProperty` на что-то более подходящее.

## Custom generic views для `neomodel`

Можно сообразить что-то подобное [DRF generic views](https://www.django-rest-framework.org/api-guide/generic-views/) для `complex_rest` и `neomodel`.

## Hooks & signals

`neomodel` предоставляет вохможность работы с [hooks](https://neomodel.readthedocs.io/en/latest/hooks.html#hooks) - функциями, которые автоматически вызываются при определённых действиях.

Также доступны [Django signals](https://neomodel.readthedocs.io/en/latest/hooks.html#django-signals) (через плагин [`django_neomodel`](https://github.com/neo4j-contrib/django-neomodel)).
