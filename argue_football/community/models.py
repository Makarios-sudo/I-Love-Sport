from django.db import models
from django.utils.translation import gettext_lazy as _
from argue_football.utilities.utils import BaseModelMixin, FriendRequestStatus, RelationshipType, make_distinct


class Friends(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",  on_delete=models.CASCADE, null=True, blank=True
    )
    account = models.ForeignKey(
        "users.Account", on_delete=models.SET_NULL, null=True, blank=True, 
    )
    followers = models.ManyToManyField(
        "users.Account", blank=True, db_index=True, related_name="my_followers"
    )
    following = models.ManyToManyField(
        "users.Account", blank=True, db_index=True, related_name="Iam_following"
    )
    archived =  models.ManyToManyField(
        "users.Account", blank=True, db_index=True, related_name="archived_friends"
    )
    blocked =  models.ManyToManyField(
        "users.Account", blank=True, db_index=True, related_name="blocked_friends"
    )
    
    def __str__(self) -> str:
        return self.account.id
    
    def followers_count(self) -> int:
        return self.followers.all().count()
    
    def following_count(self) -> int:
        return self.following.all().count()
    
    def archived_count(self) -> int:
        return self.archived.all().count()
    
    def blocked_count(self) -> int:
        return self.blocked.all().count()
    
    def new_request_count(self) -> int:
        return make_distinct(
            FriendRequest.objects.filter(
                receiver = self.account,
                status = "PENDING"
            ) 
        ).count()
       
    def accept_request(self) -> bool:
        pass
    
    def decline_request(self) -> bool:
        pass
    
    def unfriend(self) -> bool:
        pass
    
    def block(self) -> bool:
        pass

    @property
    def get_followers(self) -> list:
        return self.followers.all()
        
    @property
    def get_following(self) -> list:
        return self.following.all().count()
    
    @property
    def get_blocked(self) -> list:
        return self.blocked.all().count()

    @property
    def get_new_requests(self) -> list:
        return self.new_request

class FriendRequest(BaseModelMixin):
    sender = models.ForeignKey(
        "users.Account",  
        on_delete=models.CASCADE, verbose_name=_("sender"), related_name="send_friend_requests"
    )
    receiver = models.ForeignKey(
        "users.Account", 
        on_delete=models.CASCADE, verbose_name=_("receiver"), related_name="receieved_friend_requests"
    )
    status= models.CharField(
        _("status"),
        choices=FriendRequestStatus.choices, 
        default=FriendRequestStatus.PENDING, max_length=50,
    )
    
    def __str__(self) -> str:
        return self.id
    
    @classmethod
    def get_pending_request_count(cls):
        return cls.objects.filter(
            status=FriendRequestStatus.PENDING
        ).count()
    
    def delete_send(self) -> bool:
        pass
    
    def suggest(self) -> bool:
        pass

class Communities(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",  on_delete=models.CASCADE, null=True, blank=True
    )
    account = models.ForeignKey(
        "users.Account", on_delete=models.SET_NULL, null=True, blank=True,
    )
    members = models.ManyToManyField(
        "users.Account", 
        blank=True,
        db_index=True, 
        related_name="community_members"
    )
    name = models.CharField(
        _("Header"), max_length=200, blank=True, null=True, db_index=True
    )
    description = models.TextField(
        _("Body"), blank=True, null=True, db_index=True
    )
    thumbnail = models.JSONField(
        _("Other Details"), default=dict, blank=True, null=True, db_index=True
    )
    
    
    def members_count(self) -> int:
        pass
    
    def post_count(self) -> int:
        pass
    
    def add_members(self) -> bool:
        pass
    
    def remove_members(self) -> bool:
        pass
    
    def unread_count(self) -> int:
        pass
    
class Messaging(BaseModelMixin):
    pass

class Notification(BaseModelMixin):
    pass