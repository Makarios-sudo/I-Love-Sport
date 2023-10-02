from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

# from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.authtoken.models import Token

from argue_football.users.models import Account, User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_account(sender, instance=None, created=False, **kwargs):
    if created:
        Account.objects.create(
            owner=instance,
            id=instance.id,
            first_name=None,
            last_name=None,
            extradata={
                "nick_name": None,
                "Bio": None,
                "phone_number": None,
                "gender": None,
                "avatar": None,
                "facebook_link": None,
                "instagram_link": None,
                "titok_link": None,
            },
            # club_interests = {},
            settings={
                "hide_likes": None,
                "hide_account": None,
                "allow_comments_from": {
                    "following": None,
                    "followers": None,
                    "everyone": None,
                    "both_followers_and_follwowing": None,
                },
                "make_private": False,
                "enable_2fa": True,
                "delete_account": None,
            },
            metadata={
                "country": None,
                "business_website": None,
                "business_phone_number": None,
                "business_description": None,
            },
        )


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        "current_user": reset_password_token.user,
        "username": reset_password_token.user.username,
        "email": reset_password_token.user.email,
        "reset_password_url": "{}?token={}".format(
            instance.request.build_absolute_uri("/password_reset/confirm/"), reset_password_token.key
        )
        # 'reset_password_url': "{}?token={}".format(
        #     instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
        #     reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string("email/password_reset_email.html", context)
    email_plaintext_message = render_to_string("email/password_reset_email.txt", context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Argue Football"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@arguefootball.local",
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
