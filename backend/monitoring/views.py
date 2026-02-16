from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from .serializers import TelemetrySerializer, BulkTelemetrySerializer

# view for telemetry data submit
@api_view(['POST'])
def telemetry_submit(request):
    serializer = TelemetrySerializer(data=request.data)

    try:
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {'message': 'Telemetry data received'},
                status=status.HTTP_201_CREATED
            )
    except IntegrityError:
        return Response(
            {
                'error': 'Duplicate telemetry data'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

 # view for bulk telemetry data submit   
@api_view(['POST'])
def telemetry_bulk_submit(request):
    serializer = BulkTelemetrySerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        result = serializer.save()
        return Response(
            result,
            status=status.HTTP_201_CREATED
        )