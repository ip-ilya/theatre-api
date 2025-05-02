from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    GenreViewSet,
    ActorViewSet,
    PlayViewSet,
    TheatreHallViewSet, PerformanceViewSet,
)

app_name = "theatre"

router = routers.DefaultRouter()

router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("plays", PlayViewSet)
router.register("theatre_halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet )
urlpatterns = [
    path("", include(router.urls))
]
