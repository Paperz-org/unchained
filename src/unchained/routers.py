from ninja import Router as NinjaRouter

from unchained.meta import UnchainedRouterMeta


class Router(NinjaRouter, metaclass=UnchainedRouterMeta): ...
