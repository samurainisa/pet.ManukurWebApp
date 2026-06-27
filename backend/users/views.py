from django.contrib.auth import authenticate
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import LoginSerializer, RegisterSerializer, UserSerializer


def db_not_ready_response():
    return Response(
        {
            'detail': (
                'База данных не инициализирована. '
                'Примените миграции: python manage.py migrate.'
            )
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            user = authenticate(username=username, password=password)
        except (ProgrammingError, OperationalError):
            return db_not_ready_response()

        if not user:
            return Response({'detail': 'Неверный логин или пароль.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token, _ = Token.objects.get_or_create(user=user)
        except (ProgrammingError, OperationalError):
            return db_not_ready_response()

        return Response({'token': token.key, 'user': UserSerializer(user).data})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
        except (ProgrammingError, OperationalError):
            return db_not_ready_response()

        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'detail': 'Вы успешно вышли из системы.'})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            return Response(UserSerializer(request.user).data)
        except (ProgrammingError, OperationalError):
            return db_not_ready_response()