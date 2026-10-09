from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return self.username
