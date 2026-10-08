from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import TaskFilter
from .models import Comment, Task
from .permissions import IsCommentAuthor, IsTaskProjectAdmin
from .serializers import CommentSerializer, TaskDetailSerializer, TaskSerializer
from .services import add_comment


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Zadania z projektów teamów, do których należysz."""
        return (
            Task.objects.filter(project__team__memberships__user=self.request.user)
            .select_related("project", "project__team", "assignee")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTaskProjectAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments_action(self, request, pk=None):
        task = self.get_object()

        if request.method == "GET":
            comments = task.comments.select_related("author").all()
            return Response(CommentSerializer(comments, many=True).data)

        # POST
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = add_comment(
            user=request.user,
            task=task,
            content=serializer.validated_data["content"],
        )
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    http_method_names = ["get", "delete", "head", "options"]

    def get_queryset(self):
        return Comment.objects.filter(
            task__project__team__memberships__user=self.request.user
        ).select_related("author", "task").distinct()