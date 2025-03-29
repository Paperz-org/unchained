from django.contrib import admin

from models import Product, User


class UserAdmin(admin.ModelAdmin):
    model = User


class ProductAdmin(admin.ModelAdmin):
    model = Product

