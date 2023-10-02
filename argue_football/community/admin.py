from django.contrib import admin

from argue_football.community import models as v2_models

# Register your models here.

admin.site.register(v2_models.Friends)
admin.site.register(v2_models.FriendRequest)
admin.site.register(v2_models.Communities)
admin.site.register(v2_models.Messaging)
admin.site.register(v2_models.Notification)
