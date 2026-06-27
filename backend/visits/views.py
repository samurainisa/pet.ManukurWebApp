from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from scheduling.models import Appointment
from users.permissions import IsMasterRole
from visits.models import VisitPhoto, VisitResult
from visits.serializers import VisitPhotoSerializer, VisitResultSerializer


class AppointmentResultView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get(self, request, appointment_id: int):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        result = VisitResult.objects.filter(appointment=appointment).first()
        if not result:
            return Response(
                {
                    'appointment': appointment.id,
                    'actual_service_summary': None,
                    'materials_used': None,
                    'result_notes': None,
                    'actual_duration_min': None,
                },
                status=status.HTTP_200_OK,
            )
        return Response(VisitResultSerializer(result).data)

    def put(self, request, appointment_id: int):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        result, _ = VisitResult.objects.get_or_create(appointment=appointment)
        serializer = VisitResultSerializer(result, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AppointmentPhotoUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, appointment_id: int):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        serializer = VisitPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(appointment=appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentPhotoDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def delete(self, request, appointment_id: int, photo_id: int):
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        photo = get_object_or_404(VisitPhoto, pk=photo_id, appointment=appointment)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
