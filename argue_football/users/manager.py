from django.contrib.auth.base_user import BaseUserManager

# from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """create and save User with the given email and password

        Args:
            emaill (_type_): _description_
            password (_type_): _description_
        """

        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        self.isverify = True

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have 'is_staff' as True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have 'is_superuser' as True.")

        return self.create_user(email, password, **extra_fields)
