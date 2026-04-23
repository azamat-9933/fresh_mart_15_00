from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .serializers import UserRegisterSerializer, UserProfileSerializer, ChangePasswordSerializer, CustomTokenObtainPairSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse

# JWT --- JSON Web Token

User = get_user_model()


#   1. Пользователь отправляет логин (username + password)
#            |
#            v
#   2. TokenObtainPairView проверяет данные
#            |
#            v
#    Генерируются два токена:
#    -------------------------
#    |  Access Token (короткий) |
#    |  Refresh Token (длинный) |
#    -------------------------
#            |
#            v
#   3. Пользователь получает токены и использует их для запросов к API
#            |
#            v
#   4. Если Access Token истёк:
#       - Отправляет Refresh Token
#       - Получает новый Access Token (без повторного логина)
#            |
#            v
#   5. Продолжает работать с API безопасно


# 1️⃣ Пользователь заходит на сайт:
#    - Вводит логин и пароль
#    - Нажимает "Войти"
#
#            |
#            v
#
# 2️⃣ Django проверяет логин через TokenObtainPairView
#    - Если всё ок → выдаёт:
#      • Access Token (короткий) для API
#      • Refresh Token (длинный) для обновления access
#
#            |
#            v
#
# 3️⃣ Пользователь добавляет товары в корзину и делает заказ
#    - Все запросы к API отправляются с Access Token
#    - Сервер проверяет Access Token перед выполнением действия
#
#            |
#            v
#
# 4️⃣ Через 10–15 минут Access Token истекает
#    - Пользователь не теряет сессию
#    - Отправляет Refresh Token на сервер
#    - Сервер возвращает новый Access Token
#
#            |
#            v
#
# 5️⃣ Пользователь продолжает покупки без повторного логина

@extend_schema(tags=['auth'])
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Регистрация успешна!',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['auth'])
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(
    tags=['auth'],
    request=None,
    responses={200: OpenApiResponse(description='Выход выполнен')}
)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            return Response({'message': 'Выход выполнен'})
        except Exception:
            return Response(
                {'error': 'Неверный токен'},
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema(tags=['auth'])
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['auth'],
    request=ChangePasswordSerializer,
    responses={200: OpenApiResponse(description='Пароль изменён')}
)
class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Пароль изменён'})
