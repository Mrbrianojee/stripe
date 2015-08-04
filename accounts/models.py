from django.contrib.auth.models import AbstractBaseUser
from django.db import models

class User(AbstractBaseUser):
    email = models.EmailField(blank=True, unique=True)
