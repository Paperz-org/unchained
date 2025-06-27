from .depends import Depends
from .header import Header
from .query_params import QueryParams

Body = lambda: None
__all__ = ["Depends", "Header", "QueryParams", "Body"]
