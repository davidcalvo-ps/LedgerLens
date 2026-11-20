from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Membership, Organization

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "base_currency"]


class MembershipSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "role", "organization"]


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "display_name"]

    def get_display_name(self, user) -> str:
        return user.get_full_name() or user.email
