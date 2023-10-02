from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommuintyConfig(AppConfig):
    name = "argue_football.community"
    verbose_name = _("Communities")
    
    def ready(self) -> None:
        try:
            import argue_football.community.signals # noqa F401
        except ImportError:
            pass
    
