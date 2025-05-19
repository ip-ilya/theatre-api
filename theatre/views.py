from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    GenreSerializer,
    TheatreHallSerializer,

    PlaySerializer,
    PlayListSerializer,
    PlayRetrieveSerializer,
    PlayImageSerializer,

    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceRetrieveSerializer,

    ReservationSerializer,
    ReservationListSerializer,
)


def query_params_to_ints(query_string):
    return [int(element) for element in query_string.split(",")]


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
        elif self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        if title:
            queryset = queryset.filter(
                title__icontains=title
            )

        if genres:
            queryset = queryset.filter(
                genres__id__in=query_params_to_ints(genres)
            )

        if actors:
            queryset = queryset.filter(
                actors__id__in=query_params_to_ints(actors)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by play title (e.g., ?title=Macbeth)",
            ),
            OpenApiParameter(
                name="genres",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by genres ids (e.g., ?genres=1,2)",
                style="form",
                explode=False,
            ),
            OpenApiParameter(
                name="actors",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by actors ids (e.g., ?actors=1,2)",
                style="form",
                explode=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """Get list of plays."""
        return super().list(request, *args, **kwargs)


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
        plays = self.request.query_params.get("plays")

        if date:
            queryset = queryset.filter(show_time__date=date)

        if plays:
            plays_ids = query_params_to_ints(plays)
            queryset = queryset.filter(
                play_id__in=plays_ids
            )

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by date (e.g., ?date=2022-12-12)",
            ),
            OpenApiParameter(
                name="plays",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by plays ids (e.g., ?plays=1,2)",
                style="form",
                explode=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of performances"""
        return super().list(request, *args, **kwargs)


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
