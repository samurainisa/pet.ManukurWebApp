from django.urls import include, path

urlpatterns = [
    path('auth/', include('users.urls')),
    path('client/', include('users.client_urls')),
    path('clients/', include('clients.urls')),
    path('services/', include('services.urls')),
    path('', include('scheduling.urls')),
    path('', include('visits.urls')),
    path('', include('payments.urls')),
    path('', include('analytics.urls')),
    path('public/', include('scheduling.public_urls')),
]
