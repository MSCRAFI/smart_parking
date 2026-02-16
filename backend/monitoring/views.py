from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from .serializers import TelemetrySerializer, BulkTelemetrySerializer, DashboardSummarySerializer, AlertSerializer, ParkingLogSerializer
from .models import Alert
from django.utils import timezone

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
    
@api_view(['GET'])
def dashboard_summary(request):
    date_str = request.query_params.get('date')

    data = {}
    if date_str:
        try:
            from datetime import datetime
            data['date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    'error': 'Invalid date format. Use YYYY-MM-DD.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    serializer = DashboardSummarySerializer(data=data)
    serializer.is_valid(raise_exception=True)

    return Response(serializer.data)

@api_view(['GET'])
def alerts_list(request):
    queryset = Alert.objects.select_related('device', 'device__zone')

    # Filters
    severity = request.query_params.get('severity')
    is_acknowledged = request.query_params.get('is_acknowledged')

    if severity:
        queryset = queryset.filter(severity=severity.upper())

    if is_acknowledged is not None:
        queryset = queryset.filter(is_acknowledged=is_acknowledged.lower() == 'true')

    serializer = AlertSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
def alert_acknowledge(request, pk):
    try:
        alert = Alert.objects.get(pk=pk)
        alert.is_acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.save()

        serializer = AlertSerializer(alert)
        return Response(serializer.data)
    except Alert.DoesNotExist:
        return Response(
            {
                'error': 'Alert not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
@api_view(['POST'])
def parking_log_submit(request):
    serializer = ParkingLogSerializer(data=request.data)

    try:
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    'message': 'Parking log recorded'
                },
                status=status.HTTP_201_CREATED
            )
    except Exception as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )