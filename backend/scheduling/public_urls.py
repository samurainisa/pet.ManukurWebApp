from django.urls import path

from scheduling.views import PublicAvailableSlotsView, PublicBookingCreateView, PublicProfileView
from services.views import PublicServiceListView

urlpatterns = [
    path('profile/', PublicProfileView.as_view(), name='public-profile'),
    path('services/', PublicServiceListView.as_view(), name='public-services'),
    path('available-slots/', PublicAvailableSlotsView.as_view(), name='public-available-slots'),
    path('bookings/', PublicBookingCreateView.as_view(), name='public-bookings'),
]
