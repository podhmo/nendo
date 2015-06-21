# -*- coding:utf-8 -*-
from .langhelpers import Registry
from .env import Env

registry = Registry()


class Clause(object):
    @property
    def name(self):
        return self.__class__.__name__.upper()

    def make(self, *args):
        return self.__class__(*self.args, env=self.env.make())

    def __init__(self, *args, env=None):
        self.args = list(args)
        self.env = env or Env()

    def is_empty(self):
        return not bool(self.args)


@registry
class Select(Clause):
    pass


@registry
class From(Clause):
    pass


@registry
class Where(Clause):
    pass


@registry
class Having(Clause):
    pass
