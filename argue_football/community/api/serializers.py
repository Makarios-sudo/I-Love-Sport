from rest_framework import serializers

from argue_football.community import models as v2_models
from argue_football.users.api.serializers import AccountSerializer


class FriendsSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = v2_models.Friends
            fields = [
                "id",
                "followers_count",
                "following_count",
                "archived_count",
                "blocked_count",
                "new_request_count",
            ]

    class List(serializers.ModelSerializer):
        followers = AccountSerializer.PublicRetrieve(
            many=True,
        )
        following = AccountSerializer.PublicRetrieve(
            many=True,
        )
        archived = AccountSerializer.PublicRetrieve(
            many=True,
        )
        blocked = AccountSerializer.PublicRetrieve(
            many=True,
        )
        pending_request = serializers.SerializerMethodField()

        def get_pending_request(self, obj):
            qs = v2_models.FriendRequest.objects.filter(receiver=self.context.get("account"), status="PENDING")
            return FriendRequestSerializer.ListRequest(qs, many=True).data

        class Meta:
            model = v2_models.Friends
            fields = ["id", "followers", "following", "archived", "blocked", "pending_request"]

    class Followers(serializers.ModelSerializer):
        followers = AccountSerializer.PublicRetrieve(
            many=True,
        )

        class Meta:
            model = v2_models.Friends
            fields = ["id", "followers_count", "followers"]

    class Following(serializers.ModelSerializer):
        following = AccountSerializer.PublicRetrieve(many=True)

        class Meta:
            model = v2_models.Friends
            fields = ["id", "get_following", "following"]

    class Blocked(serializers.ModelSerializer):
        blocked = AccountSerializer.PublicRetrieve(many=True)

        class Meta:
            model = v2_models.Friends
            fields = ["id", "get_blocked", "blocked"]


class FriendRequestSerializer:
    class SendRequest(serializers.ModelSerializer):
        class Meta:
            model = v2_models.FriendRequest
            fields = ["receiver", "pending"]

    class ListRequest(serializers.ModelSerializer):
        sender = AccountSerializer.PublicRetrieve()
        # pending_requests_count = serializers.SerializerMethodField()

        # def get_pending_requests_count(self, obj):
        #     receiver = obj.receiver
        #     return v2_models.FriendRequest.pending_requests_count(receiver)

        class Meta:
            model = v2_models.FriendRequest
            fields = ["id", "sender"]
