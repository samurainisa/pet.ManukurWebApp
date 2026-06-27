from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from scheduling.models import Appointment, TimeOffBlock, WorkScheduleRule
from scheduling.public_serializers import (
    PublicLandingSerializer,
    PublicMasterProfileSerializer,
    PublicPortfolioItemSerializer,
    PublicReviewSerializer,
)
from scheduling.serializers import (
    AppointmentSerializer,
    AppointmentStatusActionSerializer,
    AvailableSlotsQuerySerializer,
    PublicBookingSerializer,
    PublicBookingSuccessSerializer,
    RescheduleSerializer,
    TimeOffBlockSerializer,
    WorkScheduleRuleSerializer,
)
from scheduling.slot_service import generate_available_slots
from services.models import Service
from services.serializers import ServiceSerializer
from users.models import MasterProfile, PublicReview, UserProfile
from users.permissions import IsMasterRole
from users.utils import ensure_user_profile
from visits.models import VisitPhoto

User = get_user_model()


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
    search_fields = ['client__full_name', 'client__phone', 'service__name']
    ordering_fields = ['start_datetime', 'appointment_date', 'created_at']
    ordering = ['start_datetime']

    def get_queryset(self):
        queryset = Appointment.objects.select_related('client', 'service', 'payment').prefetch_related('photos')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        status_param = self.request.query_params.get('status')

        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Appointment.objects.select_related('client', 'service', 'payment').prefetch_related('photos')
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]


class AppointmentCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def post(self, request, pk: int):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment.status = Appointment.AppointmentStatus.CANCELLED
        if serializer.validated_data.get('reason'):
            appointment.comment_master = serializer.validated_data['reason']
        appointment.save()

        return Response(AppointmentSerializer(appointment).data)


class AppointmentRescheduleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def post(self, request, pk: int):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = RescheduleSerializer(data=request.data, context={'appointment': appointment})
        serializer.is_valid(raise_exception=True)

        appointment.start_datetime = serializer.validated_data['start_datetime']
        appointment.end_datetime = serializer.validated_data['end_datetime']
        appointment.planned_duration_min = serializer.validated_data['planned_duration_min']
        appointment.status = Appointment.AppointmentStatus.RESCHEDULED
        appointment.save()

        return Response(AppointmentSerializer(appointment).data)


class AppointmentNoShowView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def post(self, request, pk: int):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.status = Appointment.AppointmentStatus.NO_SHOW
        appointment.save()
        return Response(AppointmentSerializer(appointment).data)


class CalendarDayView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': 'Параметр date обязателен.'}, status=status.HTTP_400_BAD_REQUEST)

        target_date = parse_date(date_str)
        if not target_date:
            return Response({'detail': 'Некорректный формат date (ожидается YYYY-MM-DD).'}, status=400)

        appointments = (
            Appointment.objects.filter(appointment_date=target_date)
            .select_related('client', 'service', 'payment')
            .order_by('start_datetime')
        )

        return Response(
            {
                'date': target_date,
                'appointments': AppointmentSerializer(appointments, many=True).data,
            }
        )


class CalendarWeekView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': 'Параметр date обязателен.'}, status=status.HTTP_400_BAD_REQUEST)

        anchor = parse_date(date_str)
        if not anchor:
            return Response({'detail': 'Некорректный формат date (ожидается YYYY-MM-DD).'}, status=400)

        week_start = anchor - timedelta(days=anchor.weekday())
        week_end = week_start + timedelta(days=6)

        appointments = (
            Appointment.objects.filter(appointment_date__range=[week_start, week_end])
            .select_related('client', 'service', 'payment')
            .order_by('start_datetime')
        )

        by_date = {}
        for appt in appointments:
            day_key = appt.appointment_date.isoformat()
            by_date.setdefault(day_key, []).append(appt)

        days = []
        for offset in range(7):
            day = week_start + timedelta(days=offset)
            key = day.isoformat()
            days.append(
                {
                    'date': key,
                    'appointments': AppointmentSerializer(by_date.get(key, []), many=True).data,
                }
            )

        return Response({'week_start': week_start, 'week_end': week_end, 'days': days})


class AvailableSlotsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]

    def get(self, request):
        serializer = AvailableSlotsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        service = serializer.validated_data['service']
        day = serializer.validated_data['date']
        slots = generate_available_slots(day, service.base_duration_min)

        return Response(
            {
                'service_id': service.id,
                'date': day,
                'slots': [slot.isoformat() for slot in slots],
            }
        )


class PublicAvailableSlotsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        serializer = AvailableSlotsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        service = serializer.validated_data['service']
        day = serializer.validated_data['date']
        slots = generate_available_slots(day, service.base_duration_min)

        return Response(
            {
                'service_id': service.id,
                'date': day,
                'slots': [slot.isoformat() for slot in slots],
            }
        )


class PublicBookingCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PublicBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(PublicBookingSuccessSerializer(appointment).data, status=status.HTTP_201_CREATED)


class PublicProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        master_user = (
            User.objects.filter(profile__role=UserProfile.Role.MASTER).order_by('id').first()
            or User.objects.filter(is_staff=True).order_by('id').first()
            or User.objects.order_by('id').first()
        )

        if not master_user:
            return Response(
                {
                    'master': {
                        'display_name': 'Мастер маникюра',
                        'city': '',
                        'address': '',
                        'phone': '',
                        'bio': '',
                        'telegram': '',
                        'avatar': None,
                    },
                    'rating_avg': 0,
                    'reviews_count': 0,
                    'reviews': [],
                    'portfolio': [],
                    'services': [],
                }
            )

        ensure_user_profile(master_user, role=UserProfile.Role.MASTER)

        master_profile, _ = MasterProfile.objects.get_or_create(
            user=master_user,
            defaults={
                'display_name': f'{master_user.first_name} {master_user.last_name}'.strip() or master_user.username,
                'city': '',
                'address': '',
                'phone': '',
                'bio': '',
                'telegram': '',
            },
        )

        reviews_qs = PublicReview.objects.filter(is_published=True).order_by('-created_at', '-id')
        rating_stats = reviews_qs.aggregate(avg=Avg('rating'), count=Count('id'))
        rating_avg = float(rating_stats.get('avg') or 0)
        reviews_count = int(rating_stats.get('count') or 0)
        reviews = reviews_qs[:8]

        portfolio = (
            VisitPhoto.objects.select_related('appointment__service')
            .filter(appointment__status=Appointment.AppointmentStatus.COMPLETED)
            .order_by('-created_at', '-id')[:10]
        )

        services = Service.objects.filter(is_active=True).order_by('sort_order', 'name')[:12]

        services_data = ServiceSerializer(services, many=True).data

        payload = {
            'master': PublicMasterProfileSerializer(master_profile, context={'request': request}).data,
            'rating_avg': round(rating_avg, 1),
            'reviews_count': reviews_count,
            'reviews': PublicReviewSerializer(reviews, many=True).data,
            'portfolio': PublicPortfolioItemSerializer(portfolio, many=True, context={'request': request}).data,
            'services': services_data,
        }
        serializer = PublicLandingSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return Response(payload)


class WorkScheduleRuleListCreateView(generics.ListCreateAPIView):
    queryset = WorkScheduleRule.objects.all()
    serializer_class = WorkScheduleRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
    ordering = ['weekday']


class WorkScheduleRuleDetailView(generics.RetrieveUpdateAPIView):
    queryset = WorkScheduleRule.objects.all()
    serializer_class = WorkScheduleRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]


class TimeOffBlockListCreateView(generics.ListCreateAPIView):
    queryset = TimeOffBlock.objects.all()
    serializer_class = TimeOffBlockSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
    ordering = ['start_datetime']


class TimeOffBlockDeleteView(generics.DestroyAPIView):
    queryset = TimeOffBlock.objects.all()
    serializer_class = TimeOffBlockSerializer
    permission_classes = [permissions.IsAuthenticated, IsMasterRole]
