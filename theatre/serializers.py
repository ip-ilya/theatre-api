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


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "row",
            "seat",
            "performance",
        ]

    def validate(self, attrs):
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


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    class Meta:
        model = Reservation
        fields = [
            "tickets",
            "user"
        ]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)

            return reservation
