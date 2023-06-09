from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view
def wage_list(request, *args, **kwargs):
    params = request.query_params
    return Response(params, status=status.HTTP_200_OK)
