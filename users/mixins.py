from rest_framework import status
from rest_framework.response import Response


class ApiResponseMixin:
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data or {},
            },
            status=status_code,
        )

    def error_response(self, message="Error", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "status": "error",
                "message": message,
                "data": data or {},
            },
            status=status_code,
        )
