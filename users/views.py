from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API для перегляду/створення/оновлення/видалення користувачів.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Дозволяємо створювати нових користувачів без авторизації
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
