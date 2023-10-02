from django.urls import include, path
from argue_football.community.api.views import FriendsViewSet
from rest_framework import routers


app_name = "community"

router = routers.DefaultRouter()
router.register(r"friends", FriendsViewSet, basename="friends")

urlpatterns = [
    path('', include(router.urls)),
]
