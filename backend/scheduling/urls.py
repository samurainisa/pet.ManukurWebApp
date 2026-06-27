from django.urls import path

from scheduling.views import (
    AppointmentCancelView,
    AppointmentDetailView,
    AppointmentListCreateView,
    AppointmentNoShowView,
    AppointmentRescheduleView,
    AvailableSlotsView,
    CalendarDayView,
    CalendarWeekView,
    TimeOffBlockDeleteView,
    TimeOffBlockListCreateView,
    WorkScheduleRuleDetailView,
    WorkScheduleRuleListCreateView,
)

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointments-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointments-detail'),
    path('appointments/<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointments-cancel'),
    path('appointments/<int:pk>/reschedule/', AppointmentRescheduleView.as_view(), name='appointments-reschedule'),
    path('appointments/<int:pk>/mark-no-show/', AppointmentNoShowView.as_view(), name='appointments-no-show'),
    path('calendar/day/', CalendarDayView.as_view(), name='calendar-day'),
    path('calendar/week/', CalendarWeekView.as_view(), name='calendar-week'),
    path('available-slots/', AvailableSlotsView.as_view(), name='available-slots'),
    path('schedule-rules/', WorkScheduleRuleListCreateView.as_view(), name='schedule-rules-list-create'),
    path('schedule-rules/<int:pk>/', WorkScheduleRuleDetailView.as_view(), name='schedule-rules-detail'),
    path('time-off-blocks/', TimeOffBlockListCreateView.as_view(), name='time-off-blocks-list-create'),
    path('time-off-blocks/<int:pk>/', TimeOffBlockDeleteView.as_view(), name='time-off-blocks-delete'),
]
