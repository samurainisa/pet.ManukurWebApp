from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from clients.models import Client
from payments.models import Payment
from scheduling.models import Appointment, WorkScheduleRule
from services.models import Service


class MVPFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='master', password='secret123')
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        for day in range(7):
            WorkScheduleRule.objects.create(
                weekday=day,
                is_working_day=day != 6,
                start_time='09:00',
                end_time='18:00',
            )

        self.client_obj = Client.objects.create(full_name='Анна Клиент', phone='+79990000001')
        self.service = Service.objects.create(
            name='Маникюр базовый',
            base_duration_min=60,
            base_price='1500.00',
            is_active=True,
            sort_order=1,
        )

    def _future_start(self, days=1, hour=11):
        day = timezone.localdate() + timedelta(days=days)
        dt = datetime.combine(day, datetime.min.time().replace(hour=hour))
        return timezone.make_aware(dt, timezone.get_current_timezone())

    def test_master_login(self):
        self.client.credentials()
        response = self.client.post('/api/v1/auth/login/', {'username': 'master', 'password': 'secret123'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_master_register(self):
        self.client.credentials()
        response = self.client.post(
            '/api/v1/auth/register/',
            {
                'username': 'master2',
                'password': 'secret12345',
                'password_confirm': 'secret12345',
                'first_name': 'Demo',
                'last_name': 'Master',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'master2')

    def test_create_client(self):
        response = self.client.post(
            '/api/v1/clients/',
            {'full_name': 'Елена Иванова', 'phone': '+79990000002', 'notes': 'Любит короткую форму'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['full_name'], 'Елена Иванова')

    def test_create_service(self):
        response = self.client.post(
            '/api/v1/services/',
            {
                'name': 'Укрепление',
                'description': 'Гель',
                'base_duration_min': 90,
                'base_price': '2200.00',
                'is_active': True,
                'sort_order': 2,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Укрепление')

    def test_delete_service(self):
        removable = Service.objects.create(
            name='Удаляемая услуга',
            base_duration_min=30,
            base_price='900.00',
            is_active=True,
            sort_order=99,
        )

        response = self.client.delete(f'/api/v1/services/{removable.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_service_used_in_appointments_returns_400(self):
        start = self._future_start(hour=16)
        used_service = Service.objects.create(
            name='Нельзя удалять',
            base_duration_min=45,
            base_price='1200.00',
            is_active=True,
            sort_order=3,
        )
        Appointment.objects.create(
            client=self.client_obj,
            service=used_service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=45),
            planned_duration_min=45,
            planned_price='1200.00',
            appointment_date=timezone.localdate(start),
            created_by=self.user,
        )

        response = self.client.delete(f'/api/v1/services/{used_service.id}/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)

    def test_create_appointment_and_block_overlap(self):
        start = self._future_start(hour=10)

        response = self.client.post(
            '/api/v1/appointments/',
            {
                'client': self.client_obj.id,
                'service': self.service.id,
                'start_datetime': start.isoformat(),
                'planned_duration_min': 60,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)

        overlap = self.client.post(
            '/api/v1/appointments/',
            {
                'client': self.client_obj.id,
                'service': self.service.id,
                'start_datetime': (start + timedelta(minutes=30)).isoformat(),
                'planned_duration_min': 60,
            },
            format='json',
        )
        self.assertEqual(overlap.status_code, 400)

    def test_create_appointment_requires_valid_client_and_service(self):
        start = self._future_start(hour=10)
        response = self.client.post(
            '/api/v1/appointments/',
            {
                'client': 0,
                'service': self.service.id,
                'start_datetime': start.isoformat(),
                'planned_duration_min': 60,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('client', response.data)

    def test_reschedule_cancel_and_no_show(self):
        start = self._future_start(hour=12)
        appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=60),
            planned_duration_min=60,
            planned_price='1500.00',
            appointment_date=timezone.localdate(start),
            created_by=self.user,
        )

        reschedule = self.client.post(
            f'/api/v1/appointments/{appointment.id}/reschedule/',
            {'start_datetime': self._future_start(hour=14).isoformat(), 'planned_duration_min': 60},
            format='json',
        )
        self.assertEqual(reschedule.status_code, 200)
        self.assertEqual(reschedule.data['status'], Appointment.AppointmentStatus.RESCHEDULED)

        cancel = self.client.post(f'/api/v1/appointments/{appointment.id}/cancel/', {'reason': 'Клиент заболел'}, format='json')
        self.assertEqual(cancel.status_code, 200)
        self.assertEqual(cancel.data['status'], Appointment.AppointmentStatus.CANCELLED)

        no_show = self.client.post(f'/api/v1/appointments/{appointment.id}/mark-no-show/', format='json')
        self.assertEqual(no_show.status_code, 200)
        self.assertEqual(no_show.data['status'], Appointment.AppointmentStatus.NO_SHOW)

    def test_visit_result_and_payment(self):
        start = self._future_start(hour=15)
        appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=60),
            planned_duration_min=60,
            planned_price='1500.00',
            appointment_date=timezone.localdate(start),
            created_by=self.user,
        )

        result = self.client.put(
            f'/api/v1/appointments/{appointment.id}/result/',
            {
                'actual_service_summary': 'Маникюр с покрытием',
                'materials_used': 'База, топ',
                'result_notes': 'Без повреждений',
                'actual_duration_min': 70,
            },
            format='json',
        )
        self.assertEqual(result.status_code, 200)

        payment = self.client.put(
            f'/api/v1/appointments/{appointment.id}/payment/',
            {'amount': '1500.00', 'payment_method': Payment.PaymentMethod.CASH, 'payment_status': Payment.PaymentStatus.PAID},
            format='json',
        )
        self.assertEqual(payment.status_code, 200)
        self.assertEqual(payment.data['payment_status'], Payment.PaymentStatus.PAID)

    def test_public_booking_and_filters(self):
        self.client.credentials()

        slots_response = self.client.get(
            '/api/v1/public/available-slots/',
            {
                'service_id': self.service.id,
                'date': (timezone.localdate() + timedelta(days=1)).isoformat(),
            },
        )
        self.assertEqual(slots_response.status_code, 200)
        self.assertTrue(len(slots_response.data['slots']) > 0)

        start_dt = slots_response.data['slots'][0]
        parsed_start = datetime.fromisoformat(start_dt)

        booking = self.client.post(
            '/api/v1/public/bookings/',
            {
                'service_id': self.service.id,
                'date': parsed_start.date().isoformat(),
                'time': parsed_start.time().isoformat(timespec='minutes'),
                'full_name': 'Мария Публичная',
                'phone': '+79990000003',
                'comment': 'Нужен дизайн',
                'website': '',
            },
            format='json',
        )
        self.assertEqual(booking.status_code, 201)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        search = self.client.get('/api/v1/clients/?search=000003')
        self.assertEqual(search.status_code, 200)
        self.assertGreaterEqual(search.data['count'], 1)

    def test_public_booking_validates_phone(self):
        self.client.credentials()
        day = timezone.localdate() + timedelta(days=1)

        response = self.client.post(
            '/api/v1/public/bookings/',
            {
                'service_id': self.service.id,
                'date': day.isoformat(),
                'time': '10:00',
                'full_name': 'Мария',
                'phone': 'abc',
                'comment': '',
                'website': '',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)

    def test_client_registration_and_booking_flow(self):
        self.client.credentials()
        register = self.client.post(
            '/api/v1/auth/register/',
            {
                'role': 'client',
                'username': 'client_demo',
                'password': 'client12345',
                'password_confirm': 'client12345',
                'full_name': 'Мария Клиент',
                'phone': '+79990000999',
                'email': 'client@example.com',
            },
            format='json',
        )
        self.assertEqual(register.status_code, 201)
        self.assertEqual(register.data['user']['role'], 'client')
        self.assertTrue(register.data['user']['client_id'])

        client_token = register.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {client_token}')

        slots_response = self.client.get(
            '/api/v1/client/available-slots/',
            {
                'service_id': self.service.id,
                'date': (timezone.localdate() + timedelta(days=1)).isoformat(),
            },
        )
        self.assertEqual(slots_response.status_code, 200)
        self.assertTrue(len(slots_response.data['slots']) > 0)

        start_dt = slots_response.data['slots'][0]
        parsed_start = datetime.fromisoformat(start_dt)

        booking = self.client.post(
            '/api/v1/client/bookings/',
            {
                'service_id': self.service.id,
                'date': parsed_start.date().isoformat(),
                'time': parsed_start.time().isoformat(timespec='minutes'),
                'comment': 'Нужен дизайн',
            },
            format='json',
        )
        self.assertEqual(booking.status_code, 201)
        self.assertEqual(booking.data['source'], Appointment.AppointmentSource.PUBLIC_BOOKING)

        history = self.client.get('/api/v1/client/bookings/')
        self.assertEqual(history.status_code, 200)
        self.assertGreaterEqual(len(history.data['items']), 1)

        notifications = self.client.get('/api/v1/client/notifications/')
        self.assertEqual(notifications.status_code, 200)
        self.assertGreaterEqual(len(notifications.data['items']), 1)

    def test_client_cannot_access_master_endpoints(self):
        self.client.credentials()
        register = self.client.post(
            '/api/v1/auth/register/',
            {
                'role': 'client',
                'username': 'client_lock',
                'password': 'client12345',
                'password_confirm': 'client12345',
                'full_name': 'Тестовый Клиент',
                'phone': '+79990000888',
            },
            format='json',
        )
        self.assertEqual(register.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {register.data['token']}")

        clients_response = self.client.get('/api/v1/clients/')
        services_response = self.client.get('/api/v1/services/')
        schedule_response = self.client.get('/api/v1/appointments/')

        self.assertEqual(clients_response.status_code, 403)
        self.assertEqual(services_response.status_code, 403)
        self.assertEqual(schedule_response.status_code, 403)
