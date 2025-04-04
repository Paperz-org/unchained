from django.db import models

from unchained.models.base import BaseModel

class User(BaseModel):
    name: str = models.CharField(max_length=255)
    email: str = models.EmailField(unique=True)
    password: str = models.CharField(max_length=255)


class Product(BaseModel):
    name: str = models.CharField(max_length=255)
    description: str = models.TextField(blank=True)
    price: float = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock: bool = models.BooleanField(default=True)
