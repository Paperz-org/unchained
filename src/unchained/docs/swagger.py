import json
from pathlib import Path
from typing import Any

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.openapi.docs import Swagger, _csrf_needed, render_template

template_path = Path(__file__).parent.parent / "templates/swagger.html"


class UnchainedSwagger(Swagger):
    template = str(template_path)
    template_cdn = str(template_path)

