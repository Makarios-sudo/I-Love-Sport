from django.urls import include, path
from rest_framework import routers

from argue_football.users.api.views import AccountView, UserLogin, UserLogout, UserRegister

urlpatterns = [
    path("register", UserRegister.as_view()),
    path("login", UserLogin.as_view()),
    path(
        "logout",
        UserLogout.as_view(),
    ),
    path("password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
]

app_name = "users"

router = routers.DefaultRouter()
router.register(r"accounts", AccountView, basename="accounts")

app_name = "users"
urlpatterns += router.urls
