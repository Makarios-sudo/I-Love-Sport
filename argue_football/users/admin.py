from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model, decorators
from django.utils.translation import gettext_lazy as _
from argue_football.users.models import Account, User

# from argue_football.users.forms import UserAdminChangeForm, UserAdminCreationForm

# User = get_user_model()

# if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
#     # Force the `admin` sign in process to go through the `django-allauth` workflow:
#     # https://django-allauth.readthedocs.io/en/stable/advanced.html#admin
#     admin.site.login = decorators.login_required(admin.site.login)  # type: ignore[method-assign]


# @admin.register(User)
# class UserAdmin(auth_admin.UserAdmin):
#     form = UserAdminChangeForm
#     add_form = UserAdminCreationForm
#     fieldsets = (
#         (None, {"fields": ("username", "password")}),
#         (_("Personal info"), {"fields": ("name", "email")}),
#         (
#             _("Permissions"),
#             {
#                 "fields": (
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 ),
#             },
#         ),
#         (_("Important dates"), {"fields": ("last_login", "date_joined")}),
#     )
#     list_display = ["username", "name", "is_superuser"]
#     search_fields = ["name"]

class YourModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date_of_birth')  # Fields to display in the list view
    search_fields = ('name', 'email')  # Fields for searching
    list_filter = ('email',)  # Fields for filtering
    
admin.site.register(Account)
admin.site.register(User)
