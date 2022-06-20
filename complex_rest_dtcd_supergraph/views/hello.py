from rest.views import APIView
from rest.response import SuccessResponse, status
from rest.permissions import AllowAny


class HelloView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        return SuccessResponse(
            {
                'message': 'Hello',
            },
            status.HTTP_200_OK
        )


