from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostsConfig(AppConfig):
    name = "argue_football.posts"
    verbose_name = _("Posts")
