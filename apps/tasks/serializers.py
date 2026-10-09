from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.projects.models import Project
from apps.teams.models import Membership

from .models import Comment, Task

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProjectBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "status"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "content", "created_at"]
        read_only_fields = ["id", "task", "author", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectBriefSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source="project",
        write_only=True,
    )
    assignee = UserBriefSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_id",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_project_id(self, project: Project) -> Project:
        """Dostęp tylko dla członka teamu, do którego projekt należy."""
        user = self.context["request"].user
        is_member = Membership.objects.filter(
            team=project.team,
            user=user,
        ).exists()

        if not is_member:
            raise serializers.ValidationError("You must be a member of the project's team.")
        return project

    def validate_assignee_id(self, assignee):
        """Assignee musi być członkiem teamu projektu."""
        if assignee is None:
            return assignee

        project = self.initial_data.get("project_id") or (
            self.instance.project_id if self.instance else None
        )

        if not project:
            return assignee

        try:
            project_obj = Project.objects.get(id=project)
        except Project.DoesNotExist:
            return assignee

        is_member = Membership.objects.filter(
            team=project_obj.team,
            user=assignee,
        ).exists()

        if not is_member:
            raise serializers.ValidationError("Assignee must be a member of the project's team.")
        return assignee


class TaskDetailSerializer(TaskSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ["comments"]
