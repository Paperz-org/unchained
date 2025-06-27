from .custom import BaseCustom
from .depends import Depends
from .header import Header
from .query_params import QueryParams

Body = lambda: None
__all__ = ["BaseCustom", "Depends", "Header", "QueryParams", "Body"]
