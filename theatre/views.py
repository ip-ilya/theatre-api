from rest_framework.decorators import action
from django.db.models.fields import IntegerField
from django.db.models import Count, F, ExpressionWrapper
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Reservation
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer, PlaySerializer, PlayListSerializer, TheatreHallSerializer, PerformanceSerializer,
    PerformanceListSerializer, PlayRetrieveSerializer, TicketSerializer, ReservationSerializer,
    PerformanceRetrieveSerializer, ReservationListSerializer, PlayImageSerializer
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
        elif self.action == "upload_image":
            return PlayImageSerializer

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

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",

    )
    def upload_image(self, request, pk=None):
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


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
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def get_queryset(self):
        queryset = self.queryset

        queryset = queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__performance__play",
                "tickets__performance__theatre_hall"
            )

        return queryset
