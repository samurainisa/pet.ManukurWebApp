from django.urls import path

from services.views import ServiceListCreateView, ServiceRetrieveUpdateView

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='services-list-create'),
    path('<int:pk>/', ServiceRetrieveUpdateView.as_view(), name='services-detail'),
]
