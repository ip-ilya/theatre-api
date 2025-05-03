from django.db import models

from theatre_api import settings


class Actor(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class Play(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")

    def __str__(self) -> str:
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=64)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Performance(models.Model):
    play = models.ForeignKey(
        Play,
        on_delete=models.CASCADE,
        related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall,
        on_delete=models.CASCADE,
        related_name="performances"
    )
    show_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.play} at {self.theatre_hall} on {self.show_time.strftime('%Y-%m-%d %H:%M')}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    def __str__(self) -> str:
        return f"Reservation by {self.user} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets"

    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self) -> str:
        return f"Row {self.row}, Seat {self.seat}"

    @staticmethod
    def validate_place_value(
            place: str,
            current_value: int,
            max_value: int,
            error_to_raise
    ):
        if not (1 <= current_value <= max_value):
            raise error_to_raise(
                {
                    f"{place}": f"{place} must be in range [1, {max_value}], "
                                f"not {current_value}"
                }
            )

    def clean(self):
        Ticket.validate_place_value(
            "row",
            self.row,
            self.performance.theatre_hall.rows,
            ValueError
        )
        Ticket.validate_place_value(
            "seat",
            self.seat,
            self.performance.theatre_hall.seats_in_row,
            ValueError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("row", "seat", "performance")
        ordering = ("row",)
