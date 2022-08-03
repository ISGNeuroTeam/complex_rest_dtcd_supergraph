"""
This module contains various framework extensions for ISG Neuro project
standard.

Custom generic views resembling those from REST framework. These are 
customized for ISG Neuro requirements and work with neomodel.
"""

import uuid

import neomodel
from rest_framework import status

from rest.views import APIView
from rest.response import SuccessResponse

from .utils import get_node_or_404


class GenericNeomodelAPIView(APIView):
    """Base class for custom generic views resembling those from DRF.

    This satisfies ISG Neuro requirements and works with neomodel.
    """

    lookup_field = "pk"
    lookup_url_kwarg = None
    model: neomodel.StructuredNode = None
    permission_classes = []
    response_field_names = {"singular": None, "plural": None}
    serializer_class = None

    def get_queryset(self) -> neomodel.NodeSet:
        assert self.model is not None, (
            "'%s' should include a `model` attribute." % self.__class__.__name__
        )

        return self.model.nodes

    def get_object(self):
        queryset = self.get_queryset()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_node_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """

        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(
                    request,
                    message=getattr(permission, "message", None),
                    code=getattr(permission, "code", None),
                )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        return [permission() for permission in self.permission_classes]

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """

        serializer_class = self.get_serializer_class()

        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """

        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )

        return self.serializer_class

    def get_singular_field_name(self):
        name = self.response_field_names.get("singular")

        if name is None:
            assert self.model is not None, (
                "'%s' should include a `model` attribute." % self.__class__.__name__
            )
            name = self.model.__name__.lower()

        return name

    def get_plural_field_name(self):
        name = self.response_field_names.get("plural")

        if name is None:
            name = self.get_singular_field_name() + "s"

        return name


class CustomNeomodelAPIView(GenericNeomodelAPIView):
    """Overwrites `get_object` to deal with searches on UUID primary key."""

    def get_object(self):
        """Return an object instance that should be used for detail views.

        Expects captured URL parameter to be a UUID instance.
        """

        queryset = self.get_queryset()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        val = self.kwargs[lookup_url_kwarg]
        assert isinstance(val, uuid.UUID), (
            f"Expected captured parameter {lookup_url_kwarg} to be of "
            f" type UUID, got {type(val)} instead."
        )

        filter_kwargs = {self.lookup_field: val.hex}
        obj = get_node_or_404(queryset, **filter_kwargs)

        return obj


class CreateNeomodelMixin:
    """Create a `neomodel` instance."""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        key = self.get_singular_field_name()

        return SuccessResponse(
            data={key: serializer.data}, http_status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save()


class DestroyNeomodelMixin:
    """Destroy a `neomodel` instance."""

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return SuccessResponse(http_status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class ListNeomodelMixin:
    """List a queryset of `neomodel` instances."""

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # TODO filtering
        # TODO pagination
        serializer = self.get_serializer(queryset, many=True)
        key = self.get_plural_field_name()

        return SuccessResponse(data={key: serializer.data})


class RetrieveNeomodelMixin:
    """Retrieve a `neomodel` instance."""

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        key = self.get_singular_field_name()

        return SuccessResponse(data={key: serializer.data})


class UpdateNeomodelMixin:
    """Update a `neomodel` instance."""

    def update(self, request, *args, **kwargs):
        # TODO partial update
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # TODO prefetched objs cache?
        key = self.get_singular_field_name()

        return SuccessResponse(data={key: serializer.data})

    def perform_update(self, serializer):
        serializer.save()


class ListCreateNeomodelAPIView(
    ListNeomodelMixin, CreateNeomodelMixin, CustomNeomodelAPIView
):
    """Concrete view for listing a queryset or creating a `neomodel` instance."""

    @neomodel.db.transaction
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @neomodel.db.transaction
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateDestroyNeomodelAPIView(
    RetrieveNeomodelMixin,
    UpdateNeomodelMixin,
    DestroyNeomodelMixin,
    CustomNeomodelAPIView,
):
    """Concrete view for retrieving, updating or deleting a `neomodel` instance."""

    @neomodel.db.transaction
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @neomodel.db.transaction
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # TODO patch

    @neomodel.db.transaction
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
