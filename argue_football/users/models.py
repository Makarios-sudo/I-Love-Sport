from django.contrib.auth.models import AbstractUser
from django.db import models 
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from argue_football.posts.models import ClubInterest
from argue_football.community import models as v2_models
from argue_football.users.manager import UserManager
from argue_football.utilities.utils import (
    BaseModelMixin, 
    generate_id,
    make_distinct, 
    validate_email, 
    phone_regex_check, 
    OTP_MAX_TRY
)



class User(AbstractUser):
    object = UserManager()
    
    id = models.CharField(
        primary_key=True, default=generate_id, editable=True, max_length=255,
    )
    name = models.CharField(
        _("Name of User"), blank=False, max_length=255, db_index=True
    )
    email = models.CharField(
        _("Email"), unique=True, max_length=225, db_index=True, 
    )
    phone_number = models.CharField(
        _("Phone Number"),unique=True, max_length=10, db_index=True, null=True, blank=True, validators=[phone_regex_check]
    )
    date_of_birth = models.DateField( _("Date Of Birth"), null=False, blank=False)
    isverify = models.BooleanField(_("IsVerify"), default=False)
    otp = models.CharField(_("OTP"), max_length=4, db_index=True, null=True, blank=True)
    otp_expire = models.DateTimeField(_("Otp Expire"), blank=True, null=True, db_index=True)
    otp_max_try = models.CharField(_("OTP Max Try"), max_length=2, db_index=True, null=True, blank=True, default=OTP_MAX_TRY)
    otp_max_out = models.DateTimeField(_("Otp Time Out"), blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    
    is_active = models.BooleanField(_("is_active"), default=True)
    is_staff = models.BooleanField(_("is_staff"), default=False)
    
  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name", "date_of_birth"]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def full_name(self:"User") -> str:
        if not self.first_name or not self.last_name:
            return " first name or last name was not provided "
        return f"{self.first_name}  {self.last_name}"
    
    # def account(self):
    #     return self.account
    
    # def my_account(self):
    #     account =  Account.objects.filter(owner=self)
    #     return account
        

class Account(BaseModelMixin):    
    owner = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accounts",
    )
    first_name = models.CharField(
        _("First Name"), blank=True, null=True, max_length=255, db_index=True
    )
    last_name = models.CharField(
        _("Last Name"), blank=True, null=True, max_length=255, db_index=True
    )
    club_interests = models.ManyToManyField(
        ClubInterest, blank=True, related_name="clubs_interest"
    )
    extradata = models.JSONField(_("extradata"), default=dict, blank=True, null=True)
    metadata = models.JSONField(_("metaadata"), default=dict, blank=True, null=True)
    settings = models.JSONField(_("settings"), default=dict, blank=True, null=True)
    isverified = models.BooleanField(_("IsVerify"), default=False, null=True, blank=True)
    
    def __str__(self):
        return self.full_name
    
    def get_user(self:"Account") -> str:
        return self.owner.name
    
    @property
    def full_name(self:"Account") -> str:
        if not self.first_name or not self.last_name:
            return " first name or last name was not provided "
        return f"{self.first_name} {self.last_name}"
    
    def verified(self:"Account"):
        return self.isverified is True 
        
    def new_request(self:"Account", sender_account:"Account", *args, **kwargs):
        return v2_models.FriendRequest.objects.get_or_create(
            sender=sender_account, 
            receiver=self, 
            status="PENDING"
        )
       
    def add_new_followers(self: "Account", sender_account: "Account", *args, **kwargs):
        friends, created = v2_models.Friends.objects.get_or_create(
            owner=self.owner, account=self, 
        )
        friends.followers.add(sender_account)
        return friends
    
    def add_new_following(self: "Account", follow: "Account", *args, **kwargs):
        new_following, created = v2_models.Friends.objects.get_or_create(
            owner=self.owner, account=self, 
        )
        new_following.following.add(follow)
        return new_following
    
    def unfollow_account(self: "Account", to_unfollow_account: "Account", *args, **kwargs):
        unfollow, created = v2_models.Friends.objects.get_or_create(
            owner=self.owner, account=self, 
        )
        unfollow.following.remove(to_unfollow_account)
        # unfollow.archived.add(to_unfollow_account)
        return unfollow
    
    def block_account(self: "Account", to_block_account: "Account", *args, **kwargs):
        blocking, created = v2_models.Friends.objects.get_or_create(
            owner=self.owner, account=self, 
        )
        blocking.blocked.add(to_block_account)
        return blocking
    
    def unblock_account(self:"Account", to_unblock_account:"Account", *args, **kwargs):
        unblocking, created = v2_models.Friends.objects.get_or_create(
            owner=self.owner, account=self
        )
        unblocking.blocked.remove(to_unblock_account)
        return unblocking
        
    def followers(self:"Account", *args, **kwargs):
        return v2_models.Friends.objects.get(
            owner=self.owner, account=self
        )