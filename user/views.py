from django.contrib.auth import get_user_model
from rest_framework import generics

from user.serializers import UserSerializer


class UserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
