
from django.db import models
from django.contrib.auth.models import AbstractUser, User
import uuid

# Create your models here.


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.token)