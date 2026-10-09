import factory

from apps.projects.tests.factories import ProjectFactory
from apps.tasks.models import Comment, Task
from apps.users.tests.factories import UserFactory


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    project = factory.SubFactory(ProjectFactory)
    title = factory.Sequence(lambda n: f"Task {n}")
    status = Task.Status.TODO
    priority = Task.Priority.MEDIUM


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    task = factory.SubFactory(TaskFactory)
    author = factory.SubFactory(UserFactory)
    content = "Test comment"
