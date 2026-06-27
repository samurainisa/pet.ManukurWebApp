import calendar
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from clients.models import Client
from payments.models import Payment
from scheduling.models import Appointment, WorkScheduleRule
from services.models import Service
from visits.models import VisitResult

User = get_user_model()

FIRST_NAMES = [
    'Анна', 'Мария', 'Елена', 'Светлана', 'Ольга', 'Юлия', 'Татьяна', 'Ирина', 'Виктория', 'Ксения',
    'Дарья', 'Полина', 'Алина', 'Наталья', 'Людмила', 'Екатерина', 'Анастасия', 'Нина', 'Валерия', 'Жанна',
]

LAST_NAMES = [
    'Иванова', 'Петрова', 'Сидорова', 'Кузнецова', 'Морозова', 'Волкова', 'Соколова', 'Лебедева', 'Новикова',
    'Федорова', 'Смирнова', 'Крылова', 'Алексеева', 'Орлова', 'Попова', 'Романова', 'Васильева', 'Громова',
]

CLIENT_NOTES = [
    '',
    'Предпочитает спокойные оттенки.',
    'Чувствительная кутикула, работать аккуратно.',
    'Обычно приходит вечером после работы.',
    'Любит короткую длину и минимализм.',
    'Часто просит укрепление.',
]

RESULT_NOTES = [
    'Покрытие ровное, клиент доволен.',
    'Сделан аккуратный аппаратный маникюр.',
    'Добавлен легкий дизайн на 2 ногтях.',
    'Выполнено укрепление без замечаний.',
    'Отработано по референсу клиента.',
]

MATERIALS = [
    'База, топ, однотон гель-лак',
    'База, камуфляж, топ',
    'База, гель для укрепления, топ',
    'База, цвет, матовый топ',
]

SERVICE_TEMPLATES = [
    ('Маникюр классический', 60, Decimal('1500.00'), 1),
    ('Маникюр + покрытие', 90, Decimal('2000.00'), 2),
    ('Маникюр + укрепление', 120, Decimal('2400.00'), 3),
    ('Коррекция ногтей', 120, Decimal('2600.00'), 4),
    ('Снятие + маникюр', 75, Decimal('1800.00'), 5),
]


class Command(BaseCommand):
    help = 'Generates demo clients and appointments for a month with realistic statuses.'

    def add_arguments(self, parser):
        parser.add_argument('--clients', type=int, default=50)
        parser.add_argument('--appointments', type=int, default=90)
        parser.add_argument('--seed', type=int, default=20260413)
        parser.add_argument('--month', type=str, default='')

    def handle(self, *args, **options):
        clients_count = options['clients']
        appointments_target = options['appointments']
        rng = random.Random(options['seed'])

        if clients_count <= 0:
            raise CommandError('--clients должен быть больше 0.')
        if appointments_target <= 0:
            raise CommandError('--appointments должен быть больше 0.')

        month_start, month_end = self._resolve_month(options['month'])
        now = timezone.now()
        today = timezone.localdate(now)

        self._ensure_schedule_rules()
        services = self._ensure_services()
        master = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()

        clients = self._create_clients(clients_count, month_start, month_end, now, rng)
        appointments = self._create_appointments(
            clients=clients,
            services=services,
            target=appointments_target,
            month_start=month_start,
            month_end=month_end,
            today=today,
            now=now,
            master=master,
            rng=rng,
        )

        self._enforce_minimum_statuses(appointments, today, rng)

        status_counts = {}
        for status_value, _ in Appointment.AppointmentStatus.choices:
            status_counts[status_value] = Appointment.objects.filter(id__in=[a.id for a in appointments], status=status_value).count()

        self.stdout.write(self.style.SUCCESS('Генерация демо-данных завершена.'))
        self.stdout.write(f'Период: {month_start} - {month_end}')
        self.stdout.write(f'Создано клиентов: {len(clients)}')
        self.stdout.write(f'Создано записей: {len(appointments)}')
        self.stdout.write(
            'Статусы: '
            + ', '.join(
                f'{status_value}={count}'
                for status_value, count in status_counts.items()
                if count > 0
            )
        )

    def _resolve_month(self, month_raw: str):
        if not month_raw:
            anchor = timezone.localdate()
            year = anchor.year
            month = anchor.month
        else:
            try:
                year_str, month_str = month_raw.split('-', 1)
                year = int(year_str)
                month = int(month_str)
                if month < 1 or month > 12:
                    raise ValueError
            except ValueError as exc:
                raise CommandError('Формат --month: YYYY-MM, например 2026-04.') from exc

        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)

    def _ensure_schedule_rules(self):
        for weekday in range(7):
            WorkScheduleRule.objects.get_or_create(
                weekday=weekday,
                defaults={
                    'start_time': time(9, 0),
                    'end_time': time(18, 0),
                    'is_working_day': weekday != 6,
                },
            )

    def _ensure_services(self):
        services = list(Service.objects.filter(is_active=True))
        if services:
            return services

        if Service.objects.count() == 0:
            for name, duration, price, sort_order in SERVICE_TEMPLATES:
                Service.objects.create(
                    name=name,
                    base_duration_min=duration,
                    base_price=price,
                    is_active=True,
                    sort_order=sort_order,
                )
            return list(Service.objects.filter(is_active=True))

        fallback = Service.objects.order_by('id').first()
        if fallback:
            fallback.is_active = True
            fallback.save(update_fields=['is_active', 'updated_at'])
            return [fallback]

        raise CommandError('Не удалось подготовить услуги для генерации.')

    def _create_clients(self, count, month_start, month_end, now, rng):
        existing_phones = set(Client.objects.values_list('phone', flat=True))
        clients = []

        for index in range(count):
            full_name = f'{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}'
            phone = self._generate_phone(existing_phones, index, rng)
            email = f'client{timezone.now().strftime("%Y%m")}{index + 1}@demo.local' if rng.random() < 0.45 else None
            notes = rng.choice(CLIENT_NOTES) or None

            client = Client.objects.create(
                full_name=full_name,
                phone=phone,
                email=email,
                notes=notes,
            )

            created_at = self._random_datetime(month_start, month_end, rng, time(9, 0), time(19, 0))
            updated_at = min(created_at + timedelta(days=rng.randint(0, 7)), now)
            Client.objects.filter(pk=client.pk).update(created_at=created_at, updated_at=updated_at)
            client.refresh_from_db()
            clients.append(client)

        return clients

    def _generate_phone(self, existing_phones, index, rng):
        while True:
            number = f'+79{rng.randint(10, 99)}{rng.randint(1000000, 9999999)}'
            if number not in existing_phones:
                existing_phones.add(number)
                return number

    def _create_appointments(self, clients, services, target, month_start, month_end, today, now, master, rng):
        appointments = []
        rules_map = {rule.weekday: rule for rule in WorkScheduleRule.objects.all()}

        max_duration = max(service.base_duration_min for service in services)
        current_day = month_start
        visits_per_client = {client.id: 0 for client in clients}

        while current_day <= month_end and len(appointments) < target:
            rule = rules_map.get(current_day.weekday())
            is_working_day = rule.is_working_day if rule else current_day.weekday() != 6
            if not is_working_day:
                current_day += timedelta(days=1)
                continue

            start_time = rule.start_time if rule else time(9, 0)
            end_time = rule.end_time if rule else time(18, 0)

            cursor = timezone.make_aware(datetime.combine(current_day, start_time), timezone.get_current_timezone())
            day_end = timezone.make_aware(datetime.combine(current_day, end_time), timezone.get_current_timezone())

            while len(appointments) < target and cursor + timedelta(minutes=30) <= day_end:
                remaining_minutes = int((day_end - cursor).total_seconds() // 60)
                fitting_services = [service for service in services if service.base_duration_min <= remaining_minutes]
                if not fitting_services:
                    break

                service = rng.choice(fitting_services)
                duration = service.base_duration_min
                start_dt = cursor
                end_dt = start_dt + timedelta(minutes=duration)

                client = self._pick_client(clients, visits_per_client, rng)
                visits_per_client[client.id] += 1

                status_value = self._pick_status(current_day, today, rng)
                source_value = Appointment.AppointmentSource.PUBLIC_BOOKING if rng.random() < 0.25 else Appointment.AppointmentSource.MASTER_MANUAL

                appointment = Appointment.objects.create(
                    client=client,
                    service=service,
                    status=status_value,
                    source=source_value,
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    planned_duration_min=duration,
                    planned_price=service.base_price,
                    comment_client='Хочу аккуратное покрытие.' if rng.random() < 0.35 else None,
                    comment_master='Постоянный клиент.' if rng.random() < 0.2 else None,
                    created_by=master if source_value == Appointment.AppointmentSource.MASTER_MANUAL else None,
                    needs_removal=rng.random() < 0.18,
                    needs_strengthening=rng.random() < 0.28,
                    design_notes='Минималистичный дизайн.' if rng.random() < 0.15 else None,
                )

                created_at = start_dt - timedelta(days=rng.randint(0, 10), hours=rng.randint(0, 8))
                month_start_dt = timezone.make_aware(datetime.combine(month_start, time(0, 0)), timezone.get_current_timezone())
                created_at = max(created_at, month_start_dt)
                created_at = min(created_at, now)

                Appointment.objects.filter(pk=appointment.pk).update(created_at=created_at, updated_at=created_at)
                appointment.refresh_from_db()

                if status_value == Appointment.AppointmentStatus.COMPLETED:
                    self._create_visit_result_and_payment(appointment, end_dt, now, rng)

                appointments.append(appointment)
                cursor = end_dt + timedelta(minutes=rng.choice([0, 15, 30]))

            current_day += timedelta(days=1)

        return appointments

    def _pick_client(self, clients, visits_per_client, rng):
        if rng.random() < 0.45:
            frequent = sorted(clients, key=lambda client: visits_per_client[client.id], reverse=True)[:12]
            return rng.choice(frequent)
        return rng.choice(clients)

    def _pick_status(self, day, today, rng):
        if day < today:
            pool = (
                [Appointment.AppointmentStatus.COMPLETED] * 72
                + [Appointment.AppointmentStatus.CANCELLED] * 13
                + [Appointment.AppointmentStatus.NO_SHOW] * 8
                + [Appointment.AppointmentStatus.RESCHEDULED] * 7
            )
            return rng.choice(pool)

        if day == today:
            pool = (
                [Appointment.AppointmentStatus.COMPLETED] * 30
                + [Appointment.AppointmentStatus.CONFIRMED] * 35
                + [Appointment.AppointmentStatus.CREATED] * 25
                + [Appointment.AppointmentStatus.CANCELLED] * 10
            )
            return rng.choice(pool)

        pool = (
            [Appointment.AppointmentStatus.CREATED] * 55
            + [Appointment.AppointmentStatus.CONFIRMED] * 30
            + [Appointment.AppointmentStatus.RESCHEDULED] * 10
            + [Appointment.AppointmentStatus.CANCELLED] * 5
        )
        return rng.choice(pool)

    def _create_visit_result_and_payment(self, appointment, end_dt, now, rng):
        if rng.random() < 0.9:
            actual_duration = max(30, appointment.planned_duration_min + rng.choice([-10, -5, 0, 5, 10, 15]))
            VisitResult.objects.create(
                appointment=appointment,
                actual_service_summary='Маникюр с покрытием.' if rng.random() < 0.6 else 'Маникюр без покрытия.',
                materials_used=rng.choice(MATERIALS),
                result_notes=rng.choice(RESULT_NOTES),
                actual_duration_min=actual_duration,
            )

        status_pool = (
            [Payment.PaymentStatus.PAID] * 75
            + [Payment.PaymentStatus.PARTIAL] * 15
            + [Payment.PaymentStatus.UNPAID] * 10
        )
        payment_status = rng.choice(status_pool)

        if payment_status == Payment.PaymentStatus.PAID:
            amount = appointment.planned_price
        elif payment_status == Payment.PaymentStatus.PARTIAL:
            amount = (appointment.planned_price * Decimal('0.5')).quantize(Decimal('0.01'))
        else:
            amount = Decimal('0.00')

        paid_at = min(end_dt + timedelta(minutes=15), now) if payment_status != Payment.PaymentStatus.UNPAID else None

        Payment.objects.create(
            appointment=appointment,
            amount=amount,
            payment_method=rng.choice([choice for choice, _ in Payment.PaymentMethod.choices]),
            payment_status=payment_status,
            paid_at=paid_at,
            comment='Оплата принята.' if payment_status == Payment.PaymentStatus.PAID and rng.random() < 0.4 else None,
        )

    def _enforce_minimum_statuses(self, appointments, today, rng):
        self._ensure_status_minimum(
            appointments,
            Appointment.AppointmentStatus.CANCELLED,
            minimum=4,
            today=today,
            rng=rng,
        )
        self._ensure_status_minimum(
            appointments,
            Appointment.AppointmentStatus.NO_SHOW,
            minimum=2,
            today=today,
            rng=rng,
        )

    def _ensure_status_minimum(self, appointments, target_status, minimum, today, rng):
        current = sum(1 for appointment in appointments if appointment.status == target_status)
        if current >= minimum:
            return

        eligible = [
            appointment
            for appointment in appointments
            if appointment.appointment_date <= today and appointment.status == Appointment.AppointmentStatus.COMPLETED
        ]
        rng.shuffle(eligible)

        for appointment in eligible:
            if current >= minimum:
                break

            appointment.status = target_status
            appointment.save(update_fields=['status', 'updated_at'])
            VisitResult.objects.filter(appointment=appointment).delete()
            Payment.objects.filter(appointment=appointment).delete()
            current += 1

    def _random_datetime(self, start_day, end_day, rng, start_time, end_time):
        day_offset = rng.randint(0, (end_day - start_day).days)
        target_day = start_day + timedelta(days=day_offset)

        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        minute = rng.randrange(start_minutes, end_minutes, 15)

        target_time = time(minute // 60, minute % 60)
        return timezone.make_aware(datetime.combine(target_day, target_time), timezone.get_current_timezone())
