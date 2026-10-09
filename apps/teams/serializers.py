from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Membership, Team

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class MembershipSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class TeamSerializer(serializers.ModelSerializer):
    owner = UserBriefSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "slug", "description", "owner", "created_at"]
        read_only_fields = ["id", "slug", "owner", "created_at"]


class TeamDetailSerializer(TeamSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ["memberships"]


class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(
        choices=Membership.Role.choices,
        default=Membership.Role.MEMBER,
    )

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        return value
