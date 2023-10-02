from django.contrib import admin

from argue_football.posts.models import ActivityFeedBack, ClubInterest, Post, PostActivity

# Register your models here.

admin.site.register(Post)
admin.site.register(ClubInterest)
admin.site.register(PostActivity)
admin.site.register(ActivityFeedBack)
