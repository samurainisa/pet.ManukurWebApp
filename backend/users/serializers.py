import re

from django.contrib.auth.models import User
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import serializers

from clients.models import Client
from users.models import UserProfile
from users.utils import ensure_user_profile

PHONE_PATTERN = re.compile(r'^\+?[0-9()\-\s]{7,20}$')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите логин.',
            'blank': 'Логин не может быть пустым.',
        },
    )
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        error_messages={
            'required': 'Укажите пароль.',
            'blank': 'Пароль не может быть пустым.',
        },
    )


class RegisterSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=UserProfile.Role.choices,
        default=UserProfile.Role.MASTER,
        error_messages={
            'invalid_choice': 'Выберите корректную роль.',
        },
    )
    username = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        error_messages={
            'required': 'Укажите логин.',
            'blank': 'Логин не может быть пустым.',
            'max_length': 'Логин не должен превышать 150 символов.',
        },
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
        error_messages={
            'required': 'Укажите пароль.',
            'blank': 'Пароль не может быть пустым.',
            'min_length': 'Пароль должен содержать минимум 8 символов.',
        },
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
        error_messages={
            'required': 'Подтвердите пароль.',
            'blank': 'Подтверждение пароля не может быть пустым.',
            'min_length': 'Подтверждение пароля должно содержать минимум 8 символов.',
        },
    )
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate_username(self, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 3:
            raise serializers.ValidationError('Логин должен содержать минимум 3 символа.')
        if re.search(r'\s', normalized):
            raise serializers.ValidationError('Логин не должен содержать пробелы.')
        if User.objects.filter(username=normalized).exists():
            raise serializers.ValidationError('Пользователь с таким логином уже существует.')
        return normalized

    def validate_full_name(self, value: str) -> str:
        return re.sub(r'\s+', ' ', value.strip())

    def validate_phone(self, value: str) -> str:
        normalized = re.sub(r'\s+', ' ', value.strip())
        if normalized and not PHONE_PATTERN.match(normalized):
            raise serializers.ValidationError('Укажите корректный телефон.')
        if normalized and sum(char.isdigit() for char in normalized) < 7:
            raise serializers.ValidationError('Телефон должен содержать минимум 7 цифр.')
        return normalized

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': ['Пароли не совпадают.']})

        role = attrs.get('role', UserProfile.Role.MASTER)

        if 'first_name' in attrs:
            attrs['first_name'] = attrs['first_name'].strip()
        if 'last_name' in attrs:
            attrs['last_name'] = attrs['last_name'].strip()
        if 'email' in attrs and attrs['email']:
            attrs['email'] = attrs['email'].strip()

        if role == UserProfile.Role.CLIENT:
            full_name = attrs.get('full_name', '').strip()
            phone = attrs.get('phone', '').strip()
            if len(full_name) < 2:
                raise serializers.ValidationError(
                    {'full_name': ['Укажите имя клиента (минимум 2 символа).']}
                )
            if not phone:
                raise serializers.ValidationError({'phone': ['Укажите телефон клиента.']})
        else:
            attrs['full_name'] = ''
            attrs['phone'] = ''
            attrs['email'] = attrs.get('email') or None

        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', UserProfile.Role.MASTER)
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        full_name = validated_data.pop('full_name', '').strip()
        phone = validated_data.pop('phone', '').strip()
        email = validated_data.pop('email', None)

        user = User.objects.create_user(password=password, **validated_data)

        if role == UserProfile.Role.MASTER:
            if not user.is_staff:
                user.is_staff = True
                user.save(update_fields=['is_staff'])
            ensure_user_profile(user, role=UserProfile.Role.MASTER)
            return user

        client = Client.objects.filter(phone=phone).first()
        if client:
            changed = False
            if full_name and client.full_name != full_name:
                client.full_name = full_name
                changed = True
            if email and client.email != email:
                client.email = email
                changed = True
            if changed:
                client.save(update_fields=['full_name', 'email', 'updated_at'])
        else:
            client = Client.objects.create(
                full_name=full_name,
                phone=phone,
                email=email,
            )

        ensure_user_profile(user, role=UserProfile.Role.CLIENT, client=client)
        return user


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    role = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    def get_role(self, obj):
        try:
            profile = getattr(obj, 'profile', None)
        except (OperationalError, ProgrammingError):
            return UserProfile.Role.MASTER
        if profile:
            return profile.role
        if obj.is_staff or obj.is_superuser:
            return UserProfile.Role.MASTER
        return UserProfile.Role.MASTER

    def get_client_id(self, obj):
        try:
            profile = getattr(obj, 'profile', None)
        except (OperationalError, ProgrammingError):
            return None
        return profile.client_id if profile else None

    def get_client_name(self, obj):
        try:
            profile = getattr(obj, 'profile', None)
        except (OperationalError, ProgrammingError):
            return None
        if profile and profile.client:
            return profile.client.full_name
        return None
