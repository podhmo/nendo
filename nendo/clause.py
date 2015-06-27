# -*- coding:utf-8 -*-
from .env import Env
from .expr import wrap
from .property import ConcreteProperty
from .value import Function, Constant


class Clause(object):
    __slots__ = ("args", "env")

    def __init__(self, *args, env=None):
        self.args = [wrap(e) for e in args]
        self.env = env or Env()

    def get_name(self):
        return getattr(self, "_name", None) or self.__class__.__name__.upper()

    def make(self, *args):
        return self.__class__(*self.args, env=self.env.make())

    def is_empty(self):
        return not bool(self.args)


class Select(Clause):
    __slots__ = ("args", "env")

    def __getattr__(self, k):
        for e in self.args:
            if e.name == k:
                return e
        raise AttributeError(k)

    def props(self):
        for e in self.args:
            yield from e.props()

    def swap(self, query, name):
        return SubSelect(*[e if isinstance(e, (Function, Constant)) else _SubSelectProperty(query, e) for e in self.args])


class SubSelect(Select):
    _name = "SELECT"


class _SubSelectProperty(ConcreteProperty):
    def __init__(self, query, prop):
        super().__init__(prop.record, prop.name, prop._key)
        self.prop = prop
        self.query = query

    @property
    def projection_name(self):
        return "{}_{}".format(self.prop.record.get_name(), self.prop.name)

    @property
    def original_name(self):
        return self.prop.orignal_name

    def __getattr__(self, k):
        return getattr(self.prop, k)


class From(Clause):
    __slots__ = ("args", "env")

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

    def swap(self, query, name):
        return self.__class__(*[e.swap(name) for e in self.args])


class Where(Clause):
    __slots__ = ("args", "env")

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


class GroupBy(Clause):
    _name = "GROUP BY"


class Having(Clause):
    __slots__ = ("args", "env")

    def __init__(self, *args, env=None):
        super().__init__(*args, env=env)
        if len(self.args) > 1:
            # where(<cond>, <cond>) == where(<cond> and <cond>)
            cond = self.args[0]
            for e in self.args[1:]:
                cond = cond.__and__(e)
            self.args = [cond]


class Limit(Clause):
    pass
