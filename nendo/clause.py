# -*- coding:utf-8 -*-
from .langhelpers import Registry
from .env import Env

registry = Registry()


class Clause(object):
    def get_name(self):
        return getattr(self, "_name", None) or self.__class__.__name__.upper()

    def make(self, *args):
        return self.__class__(*self.args, env=self.env.make())

    def __init__(self, *args, env=None):
        self.args = list(args)
        self.env = env or Env()

    def is_empty(self):
        return not bool(self.args)


@registry
class Select(Clause):
    def __getattr__(self, k):
        for e in self.args:
            if e.name == k:
                return e
        raise AttributeError(k)

    @property
    def props(self):
        return self.args


class SubSelect(Select):
    _name = "SELECT"


@registry
class From(Clause):
    def __getattr__(self, k):
        for record in self.tables:
            if record.get_name() == k:
                return record
        raise AttributeError(k)

    @property
    def tables(self):
        for record in self.args:
            yield from record.tables()


@registry
class Where(Clause):
    def __init__(self, *args, env=None):
        super().__init__(*args, env=env)
        if len(self.args) > 1:
            # where(<cond>, <cond>) == where(<cond> and <cond>)
            cond = self.args[0]
            for e in self.args[1:]:
                cond = cond.__and__(e)
            self.args = [cond]

    @property
    def tables(self):
        for cond in self.args:
            yield from cond.tables()


@registry
class OrderBy(Clause):
    _name = "ORDER BY"
    pass


@registry
class Having(Clause):
    pass
