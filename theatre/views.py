from rest_framework.viewsets import ModelViewSet

from theatre.models import (
    Actor,
    Genre,
    Play, TheatreHall, Performance
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer, PlaySerializer, PlayListSerializer, TheatreHallSerializer, PerformanceSerializer,
    PerformanceListSerializer
)


class ActorViewSet(ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        return PlaySerializer


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        return PerformanceSerializer
