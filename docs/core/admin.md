# Admin Interface

!!! info "Django Admin Integration"
    Unchained provides seamless integration with Django's admin interface, allowing you to manage your models through a web interface.

## Basic Usage

=== "Register a Model"
    ```python
    from django.contrib import admin
    from unchained import Unchained

    class UserAdmin(admin.ModelAdmin):
        list_display = ['name', 'email', 'is_active']
        search_fields = ['name', 'email']

    app = Unchained()
    app.admin.register(User, UserAdmin)
    ```

=== "Inline Admin"
    ```python
    class PostInline(admin.TabularInline):
        model = Post
        extra = 1

    class UserAdmin(admin.ModelAdmin):
        inlines = [PostInline]
    ```

## Admin Customization

=== "List Display"
    ```python
    class UserAdmin(admin.ModelAdmin):
        list_display = ['name', 'email', 'is_active', 'created_at']
        list_filter = ['is_active', 'created_at']
        search_fields = ['name', 'email']
        ordering = ['-created_at']
    ```

=== "Custom Actions"
    ```python
    class UserAdmin(admin.ModelAdmin):
        actions = ['activate_users', 'deactivate_users']

        @admin.action(description='Activate selected users')
        def activate_users(self, request, queryset):
            queryset.update(is_active=True)

        @admin.action(description='Deactivate selected users')
        def deactivate_users(self, request, queryset):
            queryset.update(is_active=False)
    ```

## Advanced Features

=== "Custom Fields"
    ```python
    class UserAdmin(admin.ModelAdmin):
        readonly_fields = ['created_at', 'updated_at']
        fieldsets = [
            (None, {'fields': ['name', 'email']}),
            ('Status', {'fields': ['is_active']}),
            ('Dates', {'fields': ['created_at', 'updated_at']})
        ]
    ```

=== "Custom Templates"
    ```python
    class UserAdmin(admin.ModelAdmin):
        change_list_template = 'admin/user_change_list.html'
        change_form_template = 'admin/user_change_form.html'
    ```

## Best Practices

1. **Security**: Always implement proper permissions
2. **Performance**: Use list_select_related for foreign keys
3. **Usability**: Add helpful filters and search fields
4. **Maintenance**: Keep admin classes simple and focused

## Common Patterns

### Model Mixins

```python
class TimestampAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at']
    list_display = ['created_at', 'updated_at']

class UserAdmin(TimestampAdmin):
    list_display = ['name', 'email', 'is_active'] + TimestampAdmin.list_display
```

### Custom Filters

```python
from django.contrib.admin import SimpleListFilter

class ActiveFilter(SimpleListFilter):
    title = 'Active Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Active'),
            ('no', 'Inactive')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_active=True)
        if self.value() == 'no':
            return queryset.filter(is_active=False)

class UserAdmin(admin.ModelAdmin):
    list_filter = [ActiveFilter]
```

### Custom Views

```python
from django.urls import path
from django.shortcuts import render

class UserAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-view/', self.admin_site.admin_view(self.custom_view))
        ]
        return custom_urls + urls

    def custom_view(self, request):
        return render(request, 'admin/custom_view.html')
```

## Example: Complete Admin Setup

```python
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import path
from django.shortcuts import render

class ActiveFilter(SimpleListFilter):
    title = 'Active Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Active'),
            ('no', 'Inactive')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_active=True)
        if self.value() == 'no':
            return queryset.filter(is_active=False)

class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_active', 'created_at']
    list_filter = [ActiveFilter, 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = [
        (None, {'fields': ['name', 'email']}),
        ('Status', {'fields': ['is_active']}),
        ('Dates', {'fields': ['created_at', 'updated_at']})
    ]

    actions = ['activate_users', 'deactivate_users']

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-view/', self.admin_site.admin_view(self.custom_view))
        ]
        return custom_urls + urls

    def custom_view(self, request):
        return render(request, 'admin/custom_view.html')

app = Unchained()
app.admin.register(User, UserAdmin)
``` 