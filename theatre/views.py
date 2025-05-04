from django.db.models.fields import IntegerField
from django.db.models import Count, F, ExpressionWrapper
from rest_framework.viewsets import ModelViewSet

from theatre.models import (
    Actor,
    Genre,
    Play, TheatreHall, Performance, Ticket, Reservation
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer, PlaySerializer, PlayListSerializer, TheatreHallSerializer, PerformanceSerializer,
    PerformanceListSerializer, PlayRetrieveSerializer, TicketSerializer, ReservationSerializer,
    PerformanceRetrieveSerializer
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

    @staticmethod
    def _query_params_to_ints(query_string):
        return [int(element) for element in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayRetrieveSerializer

        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset

        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        if genres:
            queryset = queryset.filter(
                genres__id__in=self._query_params_to_ints(genres)
            )
        if actors:
            queryset = queryset.filter(
                actors__id__in=self._query_params_to_ints(actors)
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "actors", "genres"
            )

        return queryset.distinct()


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceRetrieveSerializer

        return PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset

        date = self.request.query_params.get("date")

        if date:
            queryset = queryset.filter(show_time__date=date)

        if self.action == "list":
            queryset = queryset.select_related(
                "play", "theatre_hall"
            ).annotate(
                tickets_available=ExpressionWrapper(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    - Count("tickets"),
                    output_field=IntegerField()
                )
            )

        elif self.action == "retrieve":
            queryset = queryset.select_related(
                "play", "theatre_hall"
            )

        return queryset.distinct()


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
