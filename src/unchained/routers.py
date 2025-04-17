from unchained.meta import UnchainedRouterMeta
from unchained.ninja import Router as NinjaRouter


class Router(NinjaRouter, metaclass=UnchainedRouterMeta): ...
