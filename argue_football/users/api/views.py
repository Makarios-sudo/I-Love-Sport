from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# from argue_football.posts.api import serializers as v2_serializers
from argue_football.posts.api import serializers as v2_postApp_serializer
from argue_football.users import custom_exceptions
from argue_football.users.api.serializers import AccountSerializer, RegisterSerializer, UserSerializer
from argue_football.users.models import Account, User
from argue_football.utilities.utils import OTP, OTP_MAX_TRY, send_otp_by_mail, send_otp_by_phone


class UserRegister(generics.CreateAPIView):
    serializer_class = RegisterSerializer.UserSignup
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_otp_by_mail(email=serializer.data["email"])

        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "user": RegisterSerializer.UserSignup(user).data,
                "message": "Registeration Successful,",
            }
        )


class UserLogin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        account = Account.objects.get(owner=user)

        if account.settings.get("enable_2fa") is True:
            return Response(
                {
                    "token": token.key,
                    "message": "Please Provide Your OTP, Check your mail ",
                }
            )
        return Response(
            {
                "token": token.key,
                "message": "Login Successfull ",
            }
        )


class UserLogout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.auth.delete()
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class AccountView(viewsets.ModelViewSet):
    serializer_class = AccountSerializer.BaseRetrieve
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Account.objects.filter(isverified=True)

    @action(detail=False, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def verify_otp(self, request, *args, **kwargs):
        serializer = UserSerializer.VerifyOtpSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user: User = request.user
        account: Account = getattr(user, "accounts").first()

        otp = serializer.validated_data["otp"]
        user = User.objects.filter(otp=otp).first()

        if not user:
            return Response("You do not have the permission to take this action", status=status.HTTP_400_BAD_REQUEST)

        if user.otp_expire is None:
            user.otp_expire = timezone.now() + timedelta(minutes=2)
            user.save()

        if timezone.now() > user.otp_expire:
            return Response("Invalid OTP", status=status.HTTP_400_BAD_REQUEST)

        user.isverify = True
        user.is_active = True
        user.otp_expire = None
        user.otp_max_try = OTP_MAX_TRY
        user.otp_max_out = None
        user.save()
        account.isverified = True
        account.save()

        return Response(
            {
                "message": "Successfully verified otp",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def regenerate_otp_by_email(self, request, *args, **kwargs):
        user_id = request.user.id
        user = get_object_or_404(User, pk=user_id)
        account: Account = getattr(user, "accounts").first()

        if account.settings.get("enable_2fa") is not True:
            return Response(
                {
                    "message": "Enable your 2fa in settings to access this action",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.otp_expire is not None:
            count_down = user.otp_expire - timezone.now()
        else:
            count_down = None

        if int(user.otp_max_try) == 0 and timezone.now() < user.otp_max_out:
            return Response(
                {
                    "message": f"Maximun otp try exceeded, try later in {count_down} minutes",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = OTP
        otp_expire = timezone.now() + timedelta(minutes=2)
        otp_max_try = int(user.otp_max_try) - 1

        user.otp = otp
        user.otp_expire = otp_expire
        user.otp_max_try = otp_max_try

        if otp_max_try == 0:
            user.otp_max_out = timezone.now() + timedelta(minutes=2)
        elif otp_max_try == -1:
            user.otp_max_try = OTP_MAX_TRY
        else:
            user.otp_max_out = None
            user.otp_max_try = otp_max_try

        user.save()
        send_otp_by_mail(email=user.email)
        return Response(
            {
                "message": "Successfully Generated OTP, check",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def regenerate_otp_by_phone(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get("id"))

        if int(user.otp_max_try) == 0 and timezone.now() < user.otp_max_out:
            return Response(
                {
                    "message": "Maximun otp try exceeded, try later in 5 minutes",
                }
            )

        otp = OTP
        otp_expire = timezone.now() + datetime.now() + timedelta(minutes=2)
        otp_max_try = int(user.otp_max_try) - 1

        user.otp = otp
        user.otp_expire = otp_expire
        user.otp_max_try = otp_max_try

        if otp_max_try == 0:
            user.otp_max_out = timezone.now() + datetime.timedelta(minutes=5)
        elif otp_max_try == -1:
            user.otp_max_out = OTP_MAX_TRY
        else:
            user.otp_max_out = None
            user.otp_max_try = otp_max_try

        user.save()
        send_otp_by_phone(phone_number=user.phone_number)
        return Response(
            {
                "message": "Successfully Generated OTP, check",
            }
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        user = self.request.user
        user_account = getattr(user, "accounts").filter(isverified=True).first()

        if not user_account:
            return Response({"message": "No verified account found for this user"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountSerializer.BaseRetrieve(
            user_account,
            context={"request": request},
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def add_interest(self, request, *args, **kwargs):
        user = self.request.user
        account = get_object_or_404(Account, id=kwargs.get("pk"))

        if user != account.owner or not account.isverified:
            raise custom_exceptions.Forbidden("You do not have permission to perform this action on the given course.")

        serializer = AccountSerializer.AddInterest(instance=account, data=request.data)
        serializer.is_valid(raise_exception=True)
        interest_ids = serializer.validated_data.get("club_interests_ids")
        account.club_interests.add(*interest_ids)

        return Response(
            {
                "message": "Interest Added Successfully",
                "data": v2_postApp_serializer.ClubInterestSerializer.BaseRetrieve(interest_ids, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def update_profile(self, request, *args, **kwargs):
        user = self.request.user
        account = get_object_or_404(Account, id=kwargs.get("pk"))

        if user != account.owner or account.isverified is False:
            raise custom_exceptions.Forbidden("You do not have permisison to perform this action on the given course.")

        serializer = AccountSerializer.UpdateAccount(
            instance=account,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
        return Response(
            {"message": "Account Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK
        )

    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def update_business(self, request, *args, **kwargs):
        user = self.request.user
        account = get_object_or_404(Account, id=kwargs.get("pk"))

        if user != account.owner or account.isverified is False:
            raise custom_exceptions.Forbidden("You do not have permisison to perform this action on the given course.")

        serializer = AccountSerializer.UpdateBusiness(
            instance=account,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
        return Response({"message": "Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    @action(methods=["PUT"], detail=True, permission_classes=[IsAuthenticated])
    def change_settings(self, request, *args, **kwargs):
        user = self.request.user
        account = get_object_or_404(Account, id=kwargs.get("pk"))

        if user != account.owner or account.isverified is False:
            raise custom_exceptions.Forbidden("You do not have permisison to perform this action.")

        serializer = AccountSerializer.ChangeSettings(
            instance=account,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
        return Response(
            {"message": "settings changes Successfully", "data": serializer.data}, status=status.HTTP_200_OK
        )

    @action(methods=["DELETE"], detail=True, permission_classes=[IsAuthenticated])
    def delete_account(self, request, *args, **kwargs):
        user = self.request.user
        account = get_object_or_404(Account, id=kwargs.get("pk"))

        if user != account.owner or account.isverified is False:
            return Response(
                {"detail": "You do not have permission to delete this account."}, status=status.HTTP_403_FORBIDDEN
            )

        user.delete()
        account.delete()

        return Response(
            {"detail": "Account and associated user deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )
