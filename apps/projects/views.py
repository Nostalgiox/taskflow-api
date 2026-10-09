from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .filters import ProjectFilter
from .models import Project
from .permissions import IsProjectTeamAdmin
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProjectFilter
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Widzisz tylko projekty z teamów, do których należysz."""
        return (
            Project.objects.filter(team__memberships__user=self.request.user)
            .select_related("team")
            .distinct()
        )

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProjectTeamAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Walidacja uprawnień już jest w validate_team_id w serializerze
        serializer.save()
