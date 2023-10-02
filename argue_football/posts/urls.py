from django.urls import include, path
from rest_framework import routers

from argue_football.posts.api.views import ClubInterestViewSet, PostViewSet

app_name = "posts"

router = routers.DefaultRouter()
router.register(r"club_interest", ClubInterestViewSet, basename="club_interest")
router.register(r"posts", PostViewSet, basename="posts")

urlpatterns = [
    path("", include(router.urls)),
]
