from django.urls import path

from user.views import UserView

app_name = "user"

urlpatterns = [
    path("register/", UserView.as_view(), name="create")
]
