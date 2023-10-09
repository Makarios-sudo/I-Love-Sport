from rest_framework import serializers

from argue_football.community.models import Friends
from argue_football.posts import models as v2_models
from argue_football.posts.api import serializers as v2_serializer
from argue_football.users.models import Account, User
from argue_football.utilities.utils import OPT_EXPIRE, OTP, OTP_MAX_TRY

# User = get_user_model()


class RegisterSerializer:
    class UserSignup(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
        password2 = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
        date_of_birth = serializers.DateField(write_only=True, required=True, style={"input_type": "date"})

        class Meta:
            model = User
            fields = ["name", "email", "password", "password2", "date_of_birth"]

        def validate(self, attrs):
            if attrs["password2"] != attrs["password"]:
                raise serializers.ValidationError("Passwords do not match")
            return attrs

        def create(self, validated_data):
            email = validated_data.pop("email")
            name = validated_data.pop("name")
            date_of_birth = validated_data.pop("date_of_birth")
            password = validated_data.pop("password")

            user = User.objects.create_user(
                username=email,
                name=name,
                email=email,
                date_of_birth=date_of_birth,
                password=password,
                otp=OTP,
                otp_max_try=OTP_MAX_TRY,
                otp_expire=OPT_EXPIRE,
            )

            user.save()
            return user

    class EmailVerifyOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["email", "otp"]

    class PhoneVerifyOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["email", "otp"]


class UserSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "name", "email", "date_of_birth"]

    class PublicRetrieve(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "full_name", "email", "date_of_birth"]

    class VerifyOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["otp"]

    class EmailRegenerateOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["email"]

    class PhoneRegenerateOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["phone_number"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class AccountSerializer:
    class BaseRetrieve(serializers.ModelSerializer):
        user = UserSerializer.BaseRetrieve(source="owner")

        class Meta:
            model = Account
            fields = [
                "id",
                "user",
                "first_name",
                "last_name",
                "club_interests",
                "extradata",
                "metadata",
                "settings",
                "active",
                "isverified",
                "created_at",
                "updated_at",
            ]

    class Retrieve(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ["id", "owner", "extradata", "metadata", "active", "created_at", "updated_at"]

    class PublicRetrieve(serializers.ModelSerializer):
        profile_picture = serializers.SerializerMethodField()

        def get_profile_picture(self, obj: Account):
            if not obj.extradata:
                return None
            return obj.extradata.get("avatar")

        class Meta:
            model = Account
            fields = [
                "full_name",
                "profile_picture",
                "id",
            ]

    class UpdateAccount(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ["first_name", "last_name", "extradata"]

    class UpdateInterest(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = [
                "club_interests",
            ]

    class UpdateBusiness(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ["metadata"]

    class ChangeSettings(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ["settings"]

    class DeleteAccount(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = ["settings"]

    class AddInterest(serializers.Serializer):
        club_interests_ids = serializers.ListField(
            child=serializers.PrimaryKeyRelatedField(queryset=v2_models.ClubInterest.objects.all())
        )

        def validate_club_interests_ids(self, club_interests_ids: list[v2_models.ClubInterest]):
            if not v2_models.ClubInterest.objects.filter(
                id__in=[interest.id for interest in club_interests_ids]
            ).exists():
                raise serializers.ValidationError("One or more ClubInterest IDs do not exist.")
            return club_interests_ids

    class PublicRetrieveView(serializers.ModelSerializer):
        profile_picture = serializers.SerializerMethodField()
        about = serializers.SerializerMethodField()
        contacts = serializers.SerializerMethodField()
        business = serializers.SerializerMethodField()
        club_interests = serializers.SerializerMethodField()
        posts = serializers.SerializerMethodField()
        followers = serializers.SerializerMethodField()
        following = serializers.SerializerMethodField()
        mutual = serializers.SerializerMethodField()

        def get_followers(self, obj: Account):
            qs = Friends.objects.filter(owner=obj.owner, account=obj).first()

            if not qs or not qs.followers.exists():
                return None

            return AccountSerializer.PublicRetrieve(qs.followers.all(), many=True).data[:10]

        def get_following(self, obj: Account):
            qs = Friends.objects.filter(owner=obj.owner, account=obj).first()

            if not qs or not qs.following.exists():
                return None

            return AccountSerializer.PublicRetrieve(qs.following.all(), many=True).data[:10]

        def get_posts(self, obj: Account):
            posts = v2_serializer.PostSerializer.PublicRetreive(obj.get_posts(), many=True).data[:10]
            if not posts:
                return None
            return posts

        def get_contacts(self, obj: Account):
            keys_to_exclude = ["nick_name", "Bio", "gender", "avatar"]
            filtered_extradata = {key: value for key, value in obj.extradata.items() if key not in keys_to_exclude}
            return filtered_extradata

        def get_business(self, obj: Account):
            if not obj.metadata:
                return None
            return obj.metadata

        def get_profile_picture(self, obj: Account):
            if not obj.extradata.get("avatar"):
                return None
            return obj.extradata.get("avatar")

        def get_about(self, obj: Account):
            if not obj.extradata.get("Bio"):
                return None
            return obj.extradata.get("Bio")

        def get_club_interests(self, obj: Account):
            club_interests = v2_serializer.ClubInterestSerializer.BaseRetrieve(
                obj.club_interests.all(), many=True
            ).data[:10]
            if not club_interests:
                return None
            return club_interests

        def get_mutual(self, obj: Account):
            request_user = self.context.get("request_user_account")
            param_account_qs = obj.friends.first()
            request_user_account_qs = request_user.friends.first()

            if not param_account_qs or not request_user_account_qs:
                return None

            mutuals = request_user_account_qs.followers.filter(id__in=param_account_qs.followers.all())

            if not mutuals:
                return None

            return AccountSerializer.PublicRetrieve(mutuals, many=True).data[:10]

        class Meta:
            model = Account
            fields = [
                "id",
                "full_name",
                "profile_picture",
                "about",
                "contacts",
                "business",
                "clubs_interest_count",
                "club_interests",
                "posts_count",
                "posts",
                "followers_count",
                "followers",
                "following_count",
                "following",
                "mutual",
            ]
