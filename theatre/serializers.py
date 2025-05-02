from rest_framework import serializers

from theatre.models import (
    Actor,
    Genre,
    Play, TheatreHall, Performance
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
