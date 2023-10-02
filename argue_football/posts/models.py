from django.db import models
from django.utils.translation import gettext_lazy as _

# from argue_football.users.models import Account, User
from argue_football.utilities.utils import BaseModelMixin, OtherSharingOptions, SharingOptions

# class Feeds(BaseModelMixin):
#     pass

#     class Meta:
#         app_label = 'posts'


class ClubInterest(BaseModelMixin):
    name = models.CharField(_("club Name"), max_length=200, blank=True, null=True, db_index=True)
    league = models.CharField(_("club League"), max_length=200, blank=True, null=True, db_index=True)
    thumbnail = models.JSONField(_("Other Details"), default=dict, blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Post(BaseModelMixin):
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey(
        "users.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    body = models.TextField(_("Body"), blank=False, null=False, db_index=True)
    thumbnail = models.JSONField(_("Thumbnail"), default=dict, blank=True, null=True, db_index=True)
    shareable_link = models.URLField(_("Shareable_Link"), unique=True, blank=False, null=False, db_index=True)

    def __str__(self) -> str:
        return self.id

    def generate_shareable_link(self):
        from urllib.parse import urlencode, urlparse, urlunparse

        base_url = "https://argue_football.com"

        query_params = {}

        query_params["body"] = self.body[:10]

        # Generate the query string
        query_string = urlencode(query_params)

        # Create the final URL by combining the base URL, path (if needed), and query string
        final_url = urlunparse(urlparse(base_url)._replace(query=query_string))

        return final_url

    def save(self, *args, **kwargs):
        # Generate and store the shareable link before saving the post
        self.shareable_link = self.generate_shareable_link()
        super().save(*args, **kwargs)

    @property
    def likes(self, *args, **kwargs) -> int:
        return PostActivity.objects.filter(post=self, is_like__isnull=False).count()

    @property
    def comments(self, *args, **kwargs) -> int:
        return 0.0

    @property
    def bookmarks(self, *args, **kwargs) -> int:
        return 0.0

    @property
    def re_argue(self, *args, **kwargs) -> int:
        return 0.0


class PostActivity(BaseModelMixin):
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    account = models.ForeignKey("users.Account", on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, null=False, blank=False, db_index=True, related_name="post_engagements"
    )
    comment = models.TextField(_("Comment"), blank=True, null=True, db_index=True)
    is_like = models.BooleanField(_("Is_Like"), default=False, null=True, blank=True)
    is_repost = models.BooleanField(_("Is_Repost"), default=False, null=True, blank=True)
    is_bookmark = models.BooleanField(_("Is_BookMark"), default=False, null=True, blank=True)

    def __str__(self) -> str:
        return self.id


class ActivityFeedBack(BaseModelMixin):
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    account = models.ForeignKey("users.Account", on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    postactivity = models.ForeignKey(
        "PostActivity", on_delete=models.CASCADE, null=False, blank=False, db_index=True, related_name="feedback"
    )
    response = models.TextField(_("Response"), blank=True, null=True, db_index=True)
    is_like = models.BooleanField(_("Is_Like"), default=False, null=True, blank=True)

    def __str__(self) -> str:
        return self.postactivity.comment


class Share(BaseModelMixin):
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
    )
    account = models.ForeignKey(
        "users.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
    )
    post = models.ForeignKey(
        "POST", on_delete=models.SET_NULL, null=True, blank=True, db_index=True, related_name="share_post"
    )
    via = models.CharField(
        _("status"),
        choices=SharingOptions.choices,
        default=SharingOptions.DIRECT,
        max_length=50,
        db_index=True,
    )
    others = models.CharField(
        _("status"),
        choices=OtherSharingOptions.choices,
        default=OtherSharingOptions.WHATSAPP,
        max_length=50,
        db_index=True,
    )
    direct = models.ManyToManyField("community.Friends", blank=True, db_index=True, related_name="direct_sharing")
    community = models.ManyToManyField(
        "community.Communities", blank=True, db_index=True, related_name="community_sharing"
    )
