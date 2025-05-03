from django.core.serializers import serialize
from rest_framework.viewsets import ModelViewSet

from theatre.models import (
    Actor,
    Genre,
    Play, TheatreHall, Performance, Ticket, Reservation
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer, PlaySerializer, PlayListSerializer, TheatreHallSerializer, PerformanceSerializer,
    PerformanceListSerializer, PlayRetrieveSerializer, TicketSerializer, ReservationSerializer
)


class ActorViewSet(ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayRetrieveSerializer

        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "actors", "genres"
            )

        return queryset


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "play", "theatre_hall"
            )
        return queryset


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
