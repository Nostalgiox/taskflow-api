import factory

from apps.projects.models import Project
from apps.teams.tests.factories import TeamFactory


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    team = factory.SubFactory(TeamFactory)
    name = factory.Sequence(lambda n: f"Project {n}")
