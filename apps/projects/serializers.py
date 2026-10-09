from rest_framework import serializers

from apps.teams.models import Membership, Team

from .models import Project


class TeamBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "slug"]


class ProjectSerializer(serializers.ModelSerializer):
    team = TeamBriefSerializer(read_only=True)
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source="team",
        write_only=True,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "team",
            "team_id",
            "name",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "team", "created_at", "updated_at"]

    def validate_team_id(self, team: Team) -> Team:
        """Tworzyć/edytować projekt może tylko owner/admin teamu."""
        user = self.context["request"].user
        is_admin = Membership.objects.filter(
            team=team,
            user=user,
            role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
        ).exists()

        if not is_admin:
            raise serializers.ValidationError(
                "You must be an owner or admin of this team to manage projects."
            )
        return team
