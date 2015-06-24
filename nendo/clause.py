# -*- coding:utf-8 -*-
from .env import Env


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


class Select(Clause):
    def __getattr__(self, k):
        for e in self.args:
            if e.name == k:
                return e
        raise AttributeError(k)

    def props(self):
        return self.args


class SubSelect(Select):
    _name = "SELECT"


class From(Clause):
    def __getattr__(self, k):
        for record in self.tables():
            if record.get_name() == k:
                return record
        raise AttributeError(k)

    def tables(self):
        for record in self.args:
            yield from record.tables()

    def props(self):
        for t in self.tables():
            yield from t.props()


class Where(Clause):
    def __init__(self, *args, env=None):
        super().__init__(*args, env=env)
        if len(self.args) > 1:
            # where(<cond>, <cond>) == where(<cond> and <cond>)
            cond = self.args[0]
            for e in self.args[1:]:
                cond = cond.__and__(e)
            self.args = [cond]

    def tables(self):
        for cond in self.args:
            yield from cond.tables()


class OrderBy(Clause):
    _name = "ORDER BY"
    pass


class Having(Clause):
    pass
