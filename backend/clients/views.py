from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from clients.models import Client
from clients.serializers import ClientHistoryItemSerializer, ClientSerializer
from scheduling.models import Appointment
from users.permissions import IsMasterRole


class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
    search_fields = ['full_name', 'phone']
    ordering_fields = ['id', 'full_name', 'created_at']
    ordering = ['full_name']


class ClientRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]


class ClientHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get(self, request, pk: int):
        client = get_object_or_404(Client, pk=pk)
        appointments = (
            Appointment.objects.filter(client=client)
            .select_related('service', 'payment')
            .order_by('-start_datetime')
        )
        serializer = ClientHistoryItemSerializer(appointments, many=True)
        total_paid = (
            appointments.filter(payment__payment_status__in=['paid', 'partial'])
            .aggregate(total=Sum('payment__amount'))
            .get('total')
            or 0
        )
        return Response(
            {
                'client': ClientSerializer(client).data,
                'history': serializer.data,
                'total_paid': total_paid,
                'visits_count': appointments.count(),
            }
        )
