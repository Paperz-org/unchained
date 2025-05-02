from functools import partial
from typing import Generic, TypeVar

from unchained.signature.signature import Signature

from .depends import Depends

T = TypeVar("T")


class BaseCustom(Depends, Generic[T]):
    annotation_type: type[T]

    def __init__(
        self,
        *,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        dependency = partial(self.__call__)
        dependency.__signature__ = Signature.from_callable(self.__call__)
        super().__init__(dependency, use_cache=use_cache, cast=cast)
        self.param_name: str | None = None
        self.annotation_type: type[T]
        self.default: type[T]
