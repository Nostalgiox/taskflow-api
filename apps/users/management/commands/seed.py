from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.projects.models import Project
from apps.tasks.models import Comment, Task
from apps.teams.models import Membership, Team

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with example data for demo purposes."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding database..."))

        # Demo user (not a superuser!)
        demo, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@example.com"},
        )
        if created:
            demo.set_password("demo12345")
            demo.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Created user 'demo'"))
        else:
            self.stdout.write("  • User 'demo' already exists")

        # Second user (member of the team)
        anna, created = User.objects.get_or_create(
            username="anna",
            defaults={"email": "anna@example.com"},
        )
        if created:
            anna.set_password("demo12345")
            anna.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Created user 'anna'"))
        else:
            self.stdout.write("  • User 'anna' already exists")

        # Team
        team, created = Team.objects.get_or_create(
            name="Demo Team",
            defaults={
                "owner": demo,
                "description": "Example team for demo purposes",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created team 'Demo Team'"))

        # Memberships
        Membership.objects.get_or_create(
            team=team,
            user=demo,
            defaults={"role": Membership.Role.OWNER},
        )
        Membership.objects.get_or_create(
            team=team,
            user=anna,
            defaults={"role": Membership.Role.MEMBER},
        )

        # Project
        project, created = Project.objects.get_or_create(
            team=team,
            name="Demo Project",
            defaults={"description": "Example project with sample tasks"},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created project 'Demo Project'"))

        # Tasks
        task1, _ = Task.objects.get_or_create(
            project=project,
            title="Set up CI pipeline",
            defaults={
                "description": "Configure GitHub Actions for automated testing",
                "priority": Task.Priority.HIGH,
                "status": Task.Status.DONE,
                "assignee": demo,
            },
        )
        Task.objects.get_or_create(
            project=project,
            title="Write API documentation",
            defaults={
                "description": "Document all endpoints with drf-spectacular",
                "priority": Task.Priority.MEDIUM,
                "status": Task.Status.IN_PROGRESS,
                "assignee": anna,
            },
        )
        Task.objects.get_or_create(
            project=project,
            title="Add rate limiting",
            defaults={
                "description": "Protect endpoints with django-ratelimit",
                "priority": Task.Priority.LOW,
                "status": Task.Status.TODO,
            },
        )

        # Comment
        Comment.objects.get_or_create(
            task=task1,
            author=demo,
            defaults={"content": "Pipeline is green. Moving on to docs."},
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✓ Database seeded successfully."))
        self.stdout.write("")
        self.stdout.write("Demo credentials:")
        self.stdout.write("  Username: demo")
        self.stdout.write("  Password: demo12345")
        self.stdout.write("")
