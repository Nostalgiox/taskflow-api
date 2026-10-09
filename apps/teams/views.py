from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Team
from .permissions import IsTeamAdmin, IsTeamOwner
from .serializers import (
    AddMemberSerializer,
    MembershipSerializer,
    TeamDetailSerializer,
    TeamSerializer,
)
from .services import add_member, create_team, remove_member


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        # Użytkownik widzi tylko teamy, do których należy
        return (
            Team.objects.filter(memberships__user=self.request.user)
            .distinct()
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsTeamAdmin()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsTeamOwner()]
        return super().get_permissions()

    def perform_create(self, serializer):
        team = create_team(
            owner=self.request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )
        serializer.instance = team

    @action(detail=True, methods=["post"], url_path="members")
    def add_member_action(self, request, id=None):
        team = self.get_object()
        self.check_object_permissions(request, team)

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        membership = add_member(
            team=team,
            user_id=serializer.validated_data["user_id"],
            role=serializer.validated_data["role"],
        )
        return Response(
            MembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"members/(?P<user_id>\d+)",
    )
    def remove_member_action(self, request, id=None, user_id=None):
        team = self.get_object()
        self.check_object_permissions(request, team)

        remove_member(team=team, user_id=int(user_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
