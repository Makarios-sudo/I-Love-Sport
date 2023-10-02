from django.contrib.auth import get_user_model
from rest_framework import serializers
from argue_football.users.models import User, Account
from django.core.validators import MinValueValidator, MaxValueValidator
# from argue_football.utilities.utils import OPT_EXPIRE, OTP
from argue_football.utilities.utils import OPT_EXPIRE, OTP, OTP_MAX_TRY, send_otp_by_mail
from argue_football.posts import models as v2_models
from argue_football.posts.api import serializers as v2_serailizers


User = get_user_model()

class RegisterSerializer:
    class UserSignup(serializers.ModelSerializer):
        password = serializers.CharField(
            write_only=True, required=True, style={"input_type": "password"}
        )
        password2 = serializers.CharField(
            write_only=True, required=True, style={"input_type": "password"}
        )
        date_of_birth = serializers.DateField(
            write_only=True, required=True, style={"input_type": "date"}
        )
        
        class Meta:
            model = User
            fields = [ "name", "email", "password", "password2", "date_of_birth"]
            
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
                username = email,
                name = name,
                email = email,
                date_of_birth = date_of_birth,
                password = password,
                otp = OTP,
                otp_max_try = OTP_MAX_TRY,
                otp_expire = OPT_EXPIRE
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
            fields = [ "id", "name", "email",  "date_of_birth"]
            
    class PublicRetrieve(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [ "id", "full_name", "email",  "date_of_birth"]
            
    class VerifyOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [ "otp"]
            
    class EmailRegenerateOtpSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [ "email"]
            
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
                "id", "user", "first_name", "last_name", "club_interests", "extradata", 
                "metadata", "settings", "active", "isverified", "created_at", "updated_at"
            ]
      
    class Retrieve(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = [ 
                "id", "owner", "extradata", "metadata", "active", "created_at", "updated_at"
            ]
     
    class Public(serializers.Serializer):
        full_name = serializers.CharField()
        profile_picture = serializers.CharField()
        id = serializers.UUIDField
        
    class PublicRetrieve(serializers.ModelSerializer):
        profile_picture = serializers.SerializerMethodField()
        
        def get_profile_picture(self, obj:Account):
            return obj.extradata.get("avatar")
        
        class Meta:
            model = Account
            fields = [ "full_name", "profile_picture", "id", ]
          
    class UpdateAccount(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = [ "first_name", "last_name", "extradata"]
            
    class UpdateInterest(serializers.ModelSerializer):
        class Meta:
            model = Account
            fields = [ "club_interests",]
    
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
            child=serializers.PrimaryKeyRelatedField(
                queryset = v2_models.ClubInterest.objects.all()
            )
        )
        
        def validate_club_interests_ids(
            self, club_interests_ids: list[v2_models.ClubInterest]
            ):
            
            if not v2_models.ClubInterest.objects.filter(
                id__in=[interest.id for interest in club_interests_ids]
            ).exists():
                raise serializers.ValidationError(
                    "One or more ClubInterest IDs do not exist."
                )
            
            return club_interests_ids
        

