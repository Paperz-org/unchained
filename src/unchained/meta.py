class URLPatterns(list):
    def add(self, value):
        if isinstance(value, list):
            self.extend(value)
        else:
            self.append(value)


class UnchainedMeta(type):
    urlpatterns = URLPatterns()

    def __new__(cls, name, bases, attrs):
        from django import setup as django_setup
        from django.conf import settings as django_settings

        from unchained.settings import settings

        new_cls = super().__new__(cls, name, bases, attrs)

        django_settings.configure(**settings.django.get_settings(), ROOT_URLCONF=new_cls)
        django_setup()

        new_cls.settings = settings

        return new_cls
