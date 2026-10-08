import django_filters
from django.contrib.auth import get_user_model

from .models import Task

User = get_user_model()


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Task.Status.choices)
    priority = django_filters.ChoiceFilter(choices=Task.Priority.choices)
    project = django_filters.NumberFilter(field_name="project_id")
    assignee = django_filters.CharFilter(method="filter_assignee")
    due_before = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="lte",
    )
    due_after = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="gte",
    )

    class Meta:
        model = Task
        fields = ["status", "priority", "project", "assignee", "due_before", "due_after"]

    def filter_assignee(self, queryset, name, value):
        """`?assignee=me` → zadania przypisane do zalogowanego usera."""
        if value == "me":
            return queryset.filter(assignee=self.request.user)
        if value == "none":
            return queryset.filter(assignee__isnull=True)
        return queryset.filter(assignee_id=value)