from unchained.ninja.security.apikey import APIKeyCookie, APIKeyHeader, APIKeyQuery
from unchained.ninja.security.http import HttpBasicAuth, HttpBearer
from unchained.ninja.security.session import (
    SessionAuth,
    SessionAuthIsStaff,
    SessionAuthSuperUser,
)

__all__ = [
    "APIKeyCookie",
    "APIKeyHeader",
    "APIKeyQuery",
    "HttpBasicAuth",
    "HttpBearer",
    "SessionAuth",
    "SessionAuthSuperUser",
    "django_auth",
    "django_auth_superuser",
    "django_auth_is_staff",
]

django_auth = SessionAuth()
django_auth_superuser = SessionAuthSuperUser()
django_auth_is_staff = SessionAuthIsStaff()
