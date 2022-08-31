"""
Custom generic views.
"""

import neomodel

from rest.views import APIView


class Neo4jAPIView(APIView):
    """Wraps `dispatch()` in `neomodel` transaction."""

    @neomodel.db.transaction
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
