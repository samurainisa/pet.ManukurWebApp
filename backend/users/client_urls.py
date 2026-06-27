from django.urls import path

from users.client_views import ClientAvailableSlotsView, ClientBookingsView, ClientNotificationsView

urlpatterns = [
    path('available-slots/', ClientAvailableSlotsView.as_view(), name='client-available-slots'),
    path('bookings/', ClientBookingsView.as_view(), name='client-bookings'),
    path('notifications/', ClientNotificationsView.as_view(), name='client-notifications'),
]
