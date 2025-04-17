from pathlib import Path


from unchained.ninja.openapi.docs import Swagger

template_path = Path(__file__).parent.parent / "templates/swagger.html"


class UnchainedSwagger(Swagger):
    template = str(template_path)
    template_cdn = str(template_path)

