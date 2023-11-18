from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from argue_football.community import models as v2_model
from argue_football.community.api import serializers as v2_serializers
from argue_football.users import custom_exceptions
from argue_football.users.api.serializers import AccountSerializer
from argue_football.users.models import Account, User
from argue_football.utilities.utils import make_distinct


class FriendsViewSet(viewsets.ModelViewSet):
    queryset = v2_model.Friends.objects.all()
    serializer_class = v2_serializers.FriendsSerializer.BaseRetrieve
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        return make_distinct(
            v2_model.Friends.objects.filter(
                owner=user,
                account=account,
            )
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def friends_details(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        friends_qs = make_distinct(v2_model.Friends.objects.filter(owner=user, account=account, active=True))

        qs = self.paginate_queryset(friends_qs)
        return self.get_paginated_response(
            v2_serializers.FriendsSerializer.List(qs, many=True, context={"user": user, "account": account}).data
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def followers(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        friends_qs = make_distinct(v2_model.Friends.objects.filter(owner=user, account=account, active=True))

        qs = self.paginate_queryset(friends_qs)
        return self.get_paginated_response(v2_serializers.FriendsSerializer.Followers(qs, many=True).data)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def followings(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        friends_qs = make_distinct(v2_model.Friends.objects.filter(owner=user, account=account, active=True))

        qs = self.paginate_queryset(friends_qs)
        return self.get_paginated_response(v2_serializers.FriendsSerializer.Following(qs, many=True).data)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def blocked(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        friends_qs = make_distinct(v2_model.Friends.objects.filter(owner=user, account=account, active=True))

        qs = self.paginate_queryset(friends_qs)
        return self.get_paginated_response(v2_serializers.FriendsSerializer.Blocked(qs, many=True).data)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def new_requests(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        friends_qs = make_distinct(v2_model.FriendRequest.objects.filter(receiver=account, status="PENDING"))

        qs = self.paginate_queryset(friends_qs)
        return self.get_paginated_response(
            v2_serializers.FriendRequestSerializer.ListRequest(
                qs,
                many=True,
            ).data
        )

    @action(methods=["GET"], detail=True, permission_classes=[IsAuthenticated])
    def view_account(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        account_to_view = get_object_or_404(Account, id=kwargs.get("pk"))

        if not account.isverified or not account_to_view.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        try:
            qs = v2_model.Friends.objects.get(owner=user, account=account)
        except v2_model.Friends.DoesNotExist:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        if account_to_view not in qs.followers.all() and account_to_view not in qs.following.all():
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        return Response(
            AccountSerializer.PublicRetrieveView(
                account_to_view, context={"account_to_view": account_to_view, "request_user_account": account}
            ).data
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def send_request(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        receiver = get_object_or_404(Account, id=kwargs.get("pk"))

        if not account.isverified or not receiver.isverified or account == receiver:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        if receiver.settings.get("make_private") is True:
            receiver.new_request(account)
            return Response(
                {
                    "message": f"Your friend request has been sent to {receiver.owner.name}. "
                    "You will be added when this account accepts your invite."
                }
            )

        try:
            qs = v2_model.Friends.objects.get(owner=user, account=account)
        except v2_model.Friends.DoesNotExist:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        if receiver in qs.following.all():
            raise custom_exceptions.Forbidden({"message": f"You are already following {receiver.full_name}."})

        account.add_new_following(receiver)
        receiver.add_new_followers(account)
        return Response({"message": f"You are now following {receiver.owner.name}"})

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def accept_request(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        pending_request = get_object_or_404(v2_model.FriendRequest, id=kwargs.get("pk"))

        if not account.isverified or pending_request.receiver != account:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        pending_request.status = "ACCEPT"
        pending_request.save()

        try:
            sender_account = Account.objects.get(id=pending_request.sender.id)
        except Account.DoesNotExist:
            raise custom_exceptions.Forbidden("No Account with that id")

        account.add_new_followers(sender_account)
        sender_account.add_new_following(account)
        return Response(
            {"message": f"you accepted {pending_request.sender.owner.name}'s and is now added to your followers."}
        )

    @action(methods=["DELETE"], detail=True, permission_classes=[IsAuthenticated])
    def decline_request(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        pending_request = get_object_or_404(v2_model.FriendRequest, id=kwargs.get("pk"))

        if not account.isverified or pending_request.receiver != account:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        pending_request.status = "DECLINED"
        pending_request.delete()
        return Response(f"You declined {pending_request.sender.owner.name}'s request.")

    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def block_unblock_toggle(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        to_block = get_object_or_404(Account, id=kwargs.get("pk"))

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        try:
            qs = v2_model.Friends.objects.get(owner=user, account=account)
        except v2_model.Friends.DoesNotExist:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        if to_block not in qs.followers.all() and to_block not in qs.blocked.all():
            raise custom_exceptions.Forbidden(f"{to_block.full_name} is not among your followers")

        if to_block not in qs.blocked.all():
            qs.followers.remove(to_block)
            qs.blocked.add(to_block)
            qs.save()
            return Response({"message": f"You have block {to_block.full_name.capitalize()}"})
        qs.blocked.remove(to_block)
        qs.followers.add(to_block)
        qs.save()
        return Response({"message": f"You have unblock {to_block.full_name.capitalize()}"})

    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def follow_unfollow_toggle(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()
        to_follow_unfollow = get_object_or_404(Account, id=kwargs.get("pk"))

        if not account.isverified and not to_follow_unfollow.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        try:
            qs = v2_model.Friends.objects.get(owner=user, account=account)
        except v2_model.Friends.DoesNotExist:
            raise custom_exceptions.Forbidden("Nothing Found")

        if to_follow_unfollow.settings.get("make_private") is True:
            return Response({"message": "This account is private, send a friend request"})

        if to_follow_unfollow not in qs.following.all():
            qs.following.add(to_follow_unfollow)
            qs.save()
            return Response({"message": f"You are now following {to_follow_unfollow.full_name}"})
        qs.following.remove(to_follow_unfollow)
        qs.save()
        return Response({"message": f"You unfollowed {to_follow_unfollow.full_name}"})

        # if to_unfollow not in qs.following.all():
        #     raise custom_exceptions.Forbidden("You can only unfollow an account that you are following.")

        # qs.following.remove(to_unfollow)

        # return Response({"message":f"You have Unfollowed {to_unfollow.full_name}"})

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def suggest(self, request, *args, **kwargs):
        user: User = self.request.user
        account: Account = getattr(user, "accounts").first()

        if not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action.")

        try:
            request_user_followers = v2_model.Friends.objects.get(owner=user, account=account).followers.all()
        except v2_model.Friends.DoesNotExist:
            raise custom_exceptions.Forbidden("Nothing Found")

        request_user_followers_owners = request_user_followers.values_list("owner", flat=True)

        followers_followers = (
            make_distinct(v2_model.Friends.objects.filter(owner__in=request_user_followers_owners))
            .annotate(followers_id=F("followers__id"))
            .values_list("followers_id", flat=True)
        )

        suggested_users = (
            make_distinct(Account.objects.filter(id__in=followers_followers))
            .exclude(id=account.id)
            .exclude(id__in=request_user_followers)
        )

        qs = self.paginate_queryset(suggested_users)
        return self.get_paginated_response(AccountSerializer.PublicRetrieve(qs, many=True).data)
