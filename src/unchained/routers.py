from unchained.meta import UnchainedRouterMeta
from penta import Router as NinjaRouter


class Router(NinjaRouter, metaclass=UnchainedRouterMeta): ...
