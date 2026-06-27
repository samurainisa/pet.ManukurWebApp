from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import MasterProfile, UserProfile
from users.utils import ensure_user_profile


class Command(BaseCommand):
    help = 'Creates demo master account for local MVP run.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='master')
        parser.add_argument('--password', default='master12345')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        user = User.objects.filter(username=username).first()
        if user:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['password', 'is_staff', 'is_superuser'])
            ensure_user_profile(user, role=UserProfile.Role.MASTER)
            MasterProfile.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': 'Мастер маникюра',
                    'city': 'Санкт-Петербург',
                    'phone': '+7 (900) 000-00-00',
                    'bio': 'Аккуратный маникюр и приятный сервис.',
                },
            )
            self.stdout.write(self.style.SUCCESS(f'Updated master account: {username}'))
            return

        user = User.objects.create_superuser(username=username, password=password, email='')
        ensure_user_profile(user, role=UserProfile.Role.MASTER)
        MasterProfile.objects.get_or_create(
            user=user,
            defaults={
                'display_name': 'Мастер маникюра',
                'city': 'Санкт-Петербург',
                'phone': '+7 (900) 000-00-00',
                'bio': 'Аккуратный маникюр и приятный сервис.',
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Created master account: {username}'))
