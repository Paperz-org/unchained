from models_base import MainModel
from django.db import models

class User(MainModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

