"""
This module contains object factories for tests.

See the following links for more information:
- https://factoryboy.readthedocs.io/en/stable/
- https://faker.readthedocs.io/en/stable/
"""

import uuid

import factory

from complex_rest_dtcd_supergraph import models


class AbstractPrimitiveFactory(factory.Factory):
    """Abstract factory for generating local instances of `AbstractPrimitive` nodes."""

    class Meta:
        # model is unset - this is an abstract factory
        abstract = True
        strategy = factory.BUILD_STRATEGY  # get local object, do not save to DB

    uid = factory.LazyFunction(lambda: uuid.uuid4().hex)
    # everything from profile except 'birthdate': cannot serialize datetime to JSON
    meta_ = factory.LazyAttribute(
        lambda obj: {key: val for key, val in obj.profile.items() if key != "birthdate"}
    )

    class Params:
        # see #faker.providers.profile.Provider.simple_profile
        # at https://faker.readthedocs.io/en/latest/providers/faker.providers.profile.html
        profile = factory.Faker("simple_profile")


class VertexFactory(AbstractPrimitiveFactory):
    class Meta:
        model = models.Vertex


class PortFactory(AbstractPrimitiveFactory):
    class Meta:
        model = models.Port


class GroupFactory(AbstractPrimitiveFactory):
    class Meta:
        model = models.Group


class ContainerFactory(factory.Factory):
    class Meta:
        model = models.Container
        strategy = factory.BUILD_STRATEGY

    name = factory.Faker("name")
    # keychain_id = None
    # owner_id = None


class FragmentFactory(ContainerFactory):
    class Meta:
        model = models.Fragment


class RootFactory(ContainerFactory):
    class Meta:
        model = models.Root
