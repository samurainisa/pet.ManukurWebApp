from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from scheduling.models import Appointment
from users.permissions import IsMasterRole


class AnalyticsBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get_period(self, request):
        today = timezone.localdate()
        default_start = today - timedelta(days=30)
        date_from_raw = request.query_params.get('date_from', '')
        date_to_raw = request.query_params.get('date_to', '')

        date_from = parse_date(date_from_raw) if date_from_raw else default_start
        date_to = parse_date(date_to_raw) if date_to_raw else today

        if date_from_raw and not date_from:
            raise ValidationError({'date_from': ['Некорректный формат date_from. Ожидается YYYY-MM-DD.']})
        if date_to_raw and not date_to:
            raise ValidationError({'date_to': ['Некорректный формат date_to. Ожидается YYYY-MM-DD.']})
        if date_from > date_to:
            raise ValidationError({'date_from': ['Дата начала периода не может быть позже даты окончания.']})

        return date_from, date_to


class AnalyticsSummaryView(AnalyticsBaseView):
    def get(self, request):
        date_from, date_to = self.get_period(request)

        appointments = Appointment.objects.filter(appointment_date__range=[date_from, date_to])
        today = timezone.localdate()

        visits_count = appointments.exclude(status=Appointment.AppointmentStatus.CANCELLED).count()
        cancelled_count = appointments.filter(status=Appointment.AppointmentStatus.CANCELLED).count()
        no_show_count = appointments.filter(status=Appointment.AppointmentStatus.NO_SHOW).count()
        revenue = (
            Payment.objects.filter(
                appointment__appointment_date__range=[date_from, date_to],
                payment_status__in=[Payment.PaymentStatus.PAID, Payment.PaymentStatus.PARTIAL],
            ).aggregate(total=Sum('amount')).get('total')
            or 0
        )

        upcoming = Appointment.objects.filter(
            appointment_date__gte=today,
            status__in=Appointment.ACTIVE_SLOT_STATUSES,
        ).count()

        today_count = Appointment.objects.filter(appointment_date=today).count()

        return Response(
            {
                'date_from': date_from,
                'date_to': date_to,
                'visits_count': visits_count,
                'cancelled_count': cancelled_count,
                'no_show_count': no_show_count,
                'revenue': revenue,
                'today_count': today_count,
                'upcoming_count': upcoming,
            }
        )


class AnalyticsServicesView(AnalyticsBaseView):
    def get(self, request):
        date_from, date_to = self.get_period(request)

        rows = (
            Appointment.objects.filter(appointment_date__range=[date_from, date_to])
            .values('service_id', 'service__name')
            .annotate(count=Count('id'), planned_revenue=Sum('planned_price'))
            .order_by('-count', 'service__name')
        )

        return Response({'items': list(rows)})


class AnalyticsVisitsView(AnalyticsBaseView):
    def get(self, request):
        date_from, date_to = self.get_period(request)

        rows = (
            Appointment.objects.filter(appointment_date__range=[date_from, date_to])
            .values('client_id', 'client__full_name', 'client__phone')
            .annotate(visits_count=Count('id'))
            .order_by('-visits_count', 'client__full_name')
        )

        repeated = [row for row in rows if row['visits_count'] > 1]

        return Response({'all_clients': list(rows), 'repeat_clients': repeated})


class AnalyticsRevenueView(AnalyticsBaseView):
    def get(self, request):
        date_from, date_to = self.get_period(request)

        rows = (
            Payment.objects.filter(
                appointment__appointment_date__range=[date_from, date_to],
                payment_status__in=[Payment.PaymentStatus.PAID, Payment.PaymentStatus.PARTIAL],
            )
            .annotate(day=TruncDate('appointment__appointment_date'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

        return Response({'items': list(rows)})
