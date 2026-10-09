from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = router.urls
