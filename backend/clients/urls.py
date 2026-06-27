from django.urls import path

from clients.views import ClientHistoryView, ClientListCreateView, ClientRetrieveUpdateView

urlpatterns = [
    path('', ClientListCreateView.as_view(), name='clients-list-create'),
    path('<int:pk>/', ClientRetrieveUpdateView.as_view(), name='clients-detail'),
    path('<int:pk>/history/', ClientHistoryView.as_view(), name='clients-history'),
]
