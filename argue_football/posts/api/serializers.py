from rest_framework import serializers

from argue_football.posts import models as v2_models
from argue_football.users.api import serializers as v2_serializers


class ClubInterestSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = v2_models.ClubInterest
            fields = [
                "id",
                "name",
                "league",
                "thumbnail",
            ]


class PostSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        account = v2_serializers.AccountSerializer.PublicRetrieve()
        comments_count = serializers.IntegerField(read_only=True)
        likes_count = serializers.IntegerField(read_only=True)
        reposts_count = serializers.IntegerField(read_only=True)
        bookmarks_count = serializers.IntegerField(read_only=True)

        class Meta:
            model = v2_models.Post
            fields = [
                "id",
                "account",
                "body",
                "thumbnail",
                # "shareable_link"
                "likes_count",
                "comments_count",
                "reposts_count",
                "bookmarks_count",
                "created_at",
            ]

    class Create(serializers.ModelSerializer):
        class Meta:
            model = v2_models.Post
            fields = ["body", "thumbnail", "created_at"]

    class List(serializers.ModelSerializer):
        account = v2_serializers.AccountSerializer.PublicRetrieve()
        comments_count = serializers.IntegerField(read_only=True)
        likes_count = serializers.IntegerField(read_only=True)
        reposts_count = serializers.IntegerField(read_only=True)
        bookmarks_count = serializers.IntegerField(read_only=True)
        comments = serializers.SerializerMethodField()
        likes = serializers.SerializerMethodField()

        def get_likes(self, obj: v2_models.Post):
            likes = PostActivitySerializer.PeopleWhoLikes(
                obj.post_engagements.filter(is_like=True, active=True), many=True
            ).data[:10]

            if not likes:
                return None
            return likes

        def get_comments(self, obj: v2_models.Post):
            comments = PostActivitySerializer.Comments(
                obj.post_engagements.filter(comment__isnull=False, active=True), many=True
            ).data[:10]

            if not comments:
                return None
            return comments

        class Meta:
            model = v2_models.Post
            fields = [
                "account",
                "body",
                "thumbnail",
                "likes_count",
                "likes",
                "reposts_count",
                "bookmarks_count",
                "id",
                "comments_count",
                "comments",
                "created_at",
            ]


class PostActivitySerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        post = PostSerializer.BaseRetrieve()

        class Meta:
            model = v2_models.PostActivity
            fields = ["id", "post", "created_at"]

    class Repost(serializers.ModelSerializer):
        class Meta:
            model = v2_models.PostActivity
            fields = ["post", "id", "created_at"]

    class Bookmark(serializers.ModelSerializer):
        class Meta:
            model = v2_models.PostActivity
            fields = ["post", "id", "created_at"]

    class AddComment(serializers.ModelSerializer):
        class Meta:
            model = v2_models.PostActivity
            fields = ["post", "comment"]

    class LikeUnlikePost(serializers.ModelSerializer):
        class Meta:
            model = v2_models.PostActivity
            fields = ["post"]

    class PeopleWhoLikes(serializers.ModelSerializer):
        account = v2_serializers.AccountSerializer.PublicRetrieve()

        class Meta:
            model = v2_models.PostActivity
            fields = ["account"]

    class Comments(serializers.ModelSerializer):
        account = v2_serializers.AccountSerializer.PublicRetrieve()
        response = serializers.SerializerMethodField()
        liked_comment = serializers.SerializerMethodField()

        def get_response(self, obj: v2_models.PostActivity):
            responses = ActivityFeedBackSerializer.BaseRetrieve(
                obj.feedback.filter(response__isnull=False, active=True), many=True
            ).data[:10]

            if not responses:
                return None
            return responses

        def get_liked_comment(self, obj: v2_models.PostActivity):
            liked = obj.feedback.filter(active=True).values_list("is_like", flat=True)

            if liked.exists():
                if True in liked:
                    return True
            return None

        class Meta:
            model = v2_models.PostActivity
            fields = ["id", "account", "comment", "liked_comment", "response", "created_at"]


class ActivityFeedBackSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = v2_models.ActivityFeedBack
            fields = ["response"]

    class LikeComment(serializers.ModelSerializer):
        class Meta:
            model = v2_models.ActivityFeedBack
            fields = ["is_like"]

    class ReplyComment(serializers.ModelSerializer):
        class Meta:
            model = v2_models.ActivityFeedBack
            fields = [
                "postactivity",
                "response",
            ]

    class LikeActivity(serializers.ModelSerializer):
        class Meta:
            model = v2_models.ActivityFeedBack
            fields = ["postactivity"]
