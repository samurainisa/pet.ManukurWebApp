from django.urls import path

from analytics.views import (
    AnalyticsRevenueView,
    AnalyticsServicesView,
    AnalyticsSummaryView,
    AnalyticsVisitsView,
)

urlpatterns = [
    path('analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('analytics/services/', AnalyticsServicesView.as_view(), name='analytics-services'),
    path('analytics/visits/', AnalyticsVisitsView.as_view(), name='analytics-visits'),
    path('analytics/revenue/', AnalyticsRevenueView.as_view(), name='analytics-revenue'),
]
