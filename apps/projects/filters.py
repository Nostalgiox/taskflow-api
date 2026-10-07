import django_filters

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Project.Status.choices)
    team = django_filters.NumberFilter(field_name="team_id")

    class Meta:
        model = Project
        fields = ["status", "team"]