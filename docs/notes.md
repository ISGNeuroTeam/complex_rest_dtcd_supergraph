# Заметки

## Операция `replace` класса `Manager`

- В конце замены и обновления сущностей мы снова соединяем их с родительским(и) контейнер[ом|ами]. При попытке добавления *уже существующего* узла к новому контейнеру связи со старым **сохраняются**.
- Операция `replace` *обновляет* указанные properties на существующих nodes. Эта операция **не производит замену**: старые properties сохраняются (см. функцию [`create_or_update()`](https://neomodel.readthedocs.io/en/latest/module_documentation.html#neomodel.core.StructuredNode.create_or_update)).
    > Например, если пользователь сохранил узел с property `age: 42`, а потом перезаписал тот же узел с парой `online: false`, то node в Neo4j будет хранить *и старые, и новые данные*: `{age: 42, online: false}`.
- Существует возможность **столкновения** между названиями сервисных полей nodes (например, поле `uid`) и user-defined properties в методах вспомогательного класса `_Merger`.

## Отсутствие тестов для модуля `managers.py`

Во время запуска тестов из модуля `test_managers.py` через команду

```sh
python complex_rest/manage.py test \
    plugin_dev/complex_rest_dtcd_supergraph/tests/ \
    --settings="core.settings.test" \
```

попытка импорта узлов библиотеки `neomodel` из модуля `models.py` выбрасывает странную ошибку типа [`RelationshipClassRedefined`](https://neomodel.readthedocs.io/en/latest/module_documentation.html#neomodel.exceptions.RelationshipClassRedefined). Такая ошибка возникает при попытке *ре-ассоциации* "tied" relationship label с новым relationship классом ([документация Relationship Inheritance](https://neomodel.readthedocs.io/en/latest/relationships.html#relationship-inheritance)):
> If a relationship label is already "tied" with a relationship model and an attempt is made to re-associate it with an entirely alien relationship class, an exception of type `neomodel.exceptions.RelationshipClassRedefined` is raised that contains full information about the current data model state and the re-definition attempt.

Возможно, проблема заключается в том, как взаимодействует импорт плагинов `complex_rest`, [Django test runner](https://docs.djangoproject.com/en/4.0/topics/testing/overview/#running-tests) и [инициализация registry](https://neomodel.readthedocs.io/en/latest/extending.html#automatic-class-resolution) в `neomodel`.

## Обратная совместимость с предыдущей версией API

Для сохранения совместимости со старой версией API мы оставили некоторые URLs и специальные views для работы c фрагментами и графами рута по-умолчанию. Такие куски можно найти по комментарию:

```python
# TODO deprecate ...
```

### `create_default_root.py`

Этот скрипт нужен для инициализации дефолтного `Root` node для поддержки совместимости со старым API. Его можно удалить и убрать соответствующую команду из `database_init.sh`, когда front-end перейдёт на самостоятельную работу с рутами.

## Идея переноса функционала `Manager` в класс `Container`

Всё, чем занимается `Manager`, так или иначе имеет отношение к узлам типа `Container`. Может быть, есть смысл перенести эти операции внутрь класса:

```python
class Container(StructuredNode):
    # ...

    def read_content(self):
        # ...
    def replace_content(self, new_content):
        # ...
```

## Custom generic views для `neomodel`

Можно сообразить что-то подобное [DRF generic views](https://www.django-rest-framework.org/api-guide/generic-views/) для `complex_rest` и `neomodel`.

## Hooks & signals

`neomodel` предоставляет вохможность работы с [hooks](https://neomodel.readthedocs.io/en/latest/hooks.html#hooks) - функциями, которые автоматически вызываются при определённых действиях.

Также доступны [Django signals](https://neomodel.readthedocs.io/en/latest/hooks.html#django-signals) (через плагин [`django_neomodel`](https://github.com/neo4j-contrib/django-neomodel)).
