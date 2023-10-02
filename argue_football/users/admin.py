from django.contrib import admin

from argue_football.users.models import Account, User


class YourModelAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "date_of_birth")  # Fields to display in the list view
    search_fields = ("name", "email")  # Fields for searching
    list_filter = ("email",)  # Fields for filtering


admin.site.register(Account)
admin.site.register(User)
