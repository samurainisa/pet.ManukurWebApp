from django.db.models import ProtectedError
from rest_framework import status
from rest_framework import generics, permissions
from rest_framework.response import Response

from services.models import Service
from services.serializers import ServiceSerializer
from users.permissions import IsMasterRole


class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
    search_fields = ['name']
    ordering_fields = ['sort_order', 'name', 'base_price']
    ordering = ['sort_order', 'name']

    def get_queryset(self):
        queryset = Service.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class ServiceRetrieveUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {'detail': 'Нельзя удалить услугу, которая уже используется в записях. Отключите ее вместо удаления.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicServiceListView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['sort_order', 'name']
