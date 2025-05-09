from django.db import transaction
from rest_framework import serializers

from theatre.models import (
    Actor,
    Genre,
    Play, TheatreHall, Performance, Reservation, Ticket
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = [
            "id",
            "first_name",
            "last_name"
        ]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            "id",
            "name"
        ]


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = [
            "id",
            "title",
            "description",
            "actors",
            "genres",
        ]


class PlayListSerializer(PlaySerializer):
    actors = serializers.StringRelatedField(many=True)
    genres = serializers.StringRelatedField(many=True)


class PlayRetrieveSerializer(PlaySerializer):
    actors = ActorSerializer(many=True)
    genres = GenreSerializer(many=True)


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row"
        ]


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = [
            "id",
            "play",
            "theatre_hall",
            "show_time"
        ]


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.StringRelatedField()
    theatre_hall = serializers.StringRelatedField()
    theatre_hall_capacity = serializers.IntegerField(source="theatre_hall.capacity")
    tickets_available = serializers.IntegerField()

    class Meta:
        model = Performance
        fields = [
            "id",
            "play",
            "theatre_hall",
            "show_time",
            "theatre_hall_capacity",
            "tickets_available"
        ]


class PerformanceSerializerForTicketList(PerformanceSerializer):
    play = serializers.StringRelatedField()
    theatre_hall = serializers.StringRelatedField()

    class Meta:
        model = Performance
        fields = [
            "id",
            "play",
            "theatre_hall",
            "show_time"
        ]


class PerformanceRetrieveSerializer(PerformanceSerializer):
    play = PlayListSerializer()
    theatre_hall = TheatreHallSerializer()
    taken_seats = serializers.StringRelatedField(
        many=True,
        source="tickets"
    )

    class Meta:
        model = Performance
        fields = [
            "id",
            "play",
            "theatre_hall",
            "show_time",
            "taken_seats"
        ]


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_place_value(
            "row",
            attrs["row"],
            attrs["performance"].theatre_hall.rows,
            serializers.ValidationError
        )
        Ticket.validate_place_value(
            "seat",
            attrs["seat"],
            attrs["performance"].theatre_hall.seats_in_row,
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "performance",
        ]


class TicketListSerializer(TicketSerializer):
    performance = PerformanceSerializerForTicketList(read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "tickets"
        ]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)

            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class PlayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = [
            "id",
            "image"
        ]
