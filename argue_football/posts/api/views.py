from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from argue_football.posts import models as v2_model
from argue_football.posts.api import serializers as v2_serializers
from argue_football.users import custom_exceptions
from argue_football.users.models import Account, User
from argue_football.utilities.utils import make_distinct


class ClubInterestViewSet(viewsets.ModelViewSet):
    queryset = v2_model.ClubInterest.objects.all()
    serializer_class = v2_serializers.ClubInterestSerializer.BaseRetrieve
    permission_classes = [IsAuthenticated | IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class PostViewSet(viewsets.ModelViewSet):
    queryset = v2_model.Post.objects.all()
    serializer_class = v2_serializers.PostSerializer.BaseRetrieve
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        qs = (
            make_distinct(v2_model.Post.objects.filter(owner=user, account=account, active=True))
            .annotate(
                comments_count=Count(
                    "post_engagements", filter=Q(post_engagements__comment__isnull=False), distinct=True
                ),
                likes_count=Count("post_engagements", filter=Q(post_engagements__is_like=True), distinct=True),
                reposts_count=Count("post_engagements", filter=Q(post_engagements__is_repost=True), distinct=True),
                bookmarks_count=Count("post_engagements", filter=Q(post_engagements__is_bookmark=True), distinct=True),
            )
            .order_by("-created_at")
        )
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "delete"]:
            return v2_serializers.PostSerializer.Create
        if self.action == "list":
            return v2_serializers.PostSerializer.BaseRetrieve
        if self.action == "retrieve":
            return v2_serializers.PostSerializer.List
        return v2_serializers.PostSerializer.BaseRetrieve

    def create(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=user, account=account)
            return Response(
                data=serializer.data,
            )
        else:
            return Response(data=serializer.errors)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def get_reposts(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        reposts = make_distinct(
            v2_model.PostActivity.objects.filter(
                owner=user, account=account, post__isnull=False, active=True, is_repost=True
            )
        )

        qs = self.paginate_queryset(reposts)
        return self.get_paginated_response(v2_serializers.PostActivitySerializer.BaseRetrieve(qs, many=True).data)

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def repost_unrepost(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        serializer = v2_serializers.PostActivitySerializer.Repost(
            data=request.data,
        )

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data.get("post")

        if post.owner == user or post.account == account:
            raise custom_exceptions.Forbidden("You can not repost your own post.")

        reposted = make_distinct(
            v2_model.PostActivity.objects.filter(owner=user, account=account, post=post, is_repost=True)
        )
        if reposted.exists():
            reposted.delete()
            return Response("You Unrepost this post")

        reposted = v2_model.PostActivity.objects.create(owner=user, account=account, post=post, is_repost=True)
        return Response(
            {"repost": v2_serializers.PostSerializer.BaseRetrieve(post).data, "message": "Repost Successful"}
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def get_bookmarks(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        reposts = make_distinct(
            v2_model.PostActivity.objects.filter(
                owner=user, account=account, post__isnull=False, active=True, is_bookmark=True
            )
        )

        qs = self.paginate_queryset(reposts)
        return self.get_paginated_response(v2_serializers.PostActivitySerializer.BaseRetrieve(qs, many=True).data)

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def bookmark_unbookmark(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        serializer = v2_serializers.PostActivitySerializer.Repost(
            data=request.data,
        )

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data.get("post")

        if post.owner == user or post.account == account:
            raise custom_exceptions.Forbidden("You can not bookmark your own post.")

        bookmarked = make_distinct(
            v2_model.PostActivity.objects.filter(owner=user, account=account, post=post, is_bookmark=True)
        )

        if bookmarked.exists():
            bookmarked.delete()
            return Response("You unbookmark this post")

        bookmarked = v2_model.PostActivity.objects.create(owner=user, account=account, post=post, is_bookmark=True)
        return Response(
            {"repost": v2_serializers.PostSerializer.BaseRetrieve(post).data, "message": "Bookmark Successful"}
        )

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def like_unlike_post(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        serializer = v2_serializers.PostActivitySerializer.LikeUnlikePost(
            data=request.data,
        )

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data.get("post")

        liked_post = make_distinct(
            v2_model.PostActivity.objects.filter(
                owner=user,
                account=account,
                post=post,
                is_like=True,
            )
        )

        if liked_post.exists():
            liked_post.delete()
            return Response("You unlike this post")

        v2_model.PostActivity.objects.create(owner=user, post=post, account=account, is_like=True)
        return Response("You like this post")

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def comment(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        serializer = v2_serializers.PostActivitySerializer.AddComment(
            data=request.data,
        )
        # """TODO== check if the request user is a friend to the post owner"""

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data.get("post")

        if post.owner == user or post.account == account:
            raise custom_exceptions.Forbidden("You can not comment on your own post.")

        instance = serializer.save(owner=user, account=account)
        return Response(v2_serializers.PostActivitySerializer.AddComment(instance).data)

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def reply_comment(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        serializer = v2_serializers.ActivityFeedBackSerializer.ReplyComment(
            data=request.data, context={"owner": user, "account": account}
        )

        if not account.isverified:
            raise custom_exceptions.Forbidden("Please Verify Your Account")

        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data.get("postactivity")

        if user != comment.post.owner and account != comment.post.owner:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action")

        serializer.save(owner=user, account=account, is_like=None)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def like_unlike_comment(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        serializer = v2_serializers.ActivityFeedBackSerializer.LikeActivity(data=request.data)

        if not account.isverified:
            raise custom_exceptions.Forbidden("Please Verify Your Account")

        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data.get("postactivity")

        if user != comment.post.owner and account != comment.post.owner:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action")

        liked = make_distinct(
            v2_model.ActivityFeedBack.objects.filter(owner=user, account=account, postactivity=comment, is_like=True)
        )

        if liked.exists():
            liked.delete()
            return Response("You unlike the comment")

        v2_model.ActivityFeedBack.objects.create(owner=user, account=account, postactivity=comment, is_like=True)
        return Response("You like the comment")

    def share_via_direct():
        pass

    def share_via_community():
        pass

    def share_via_others():
        pass

    def feeds():
        pass
