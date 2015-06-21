import functools
from . import inspect as i
from . import condition as c
from .value import Value


def lift(method):
    @functools.wraps(method)
    def _lift(self, other):
        if other is None:
            value = method(self, None)
        elif not i.is_expr(other):
            value = method(self, Value(other))
        else:
            value = method(self, other)
        value.env.merge(self, other)  # side effect
        return value
    return _lift


class NamedProperty(object):
    __slots__ = ("name", "_concrete", "_key")

    def __init__(self, name):
        self.name = name
        self._concrete = None
        self._key = "_{}".format(name)

    def __get__(self, ob, type_=None):
        if ob is None:
            if self._concrete is None:
                self._concrete = ConcreteProperty(type_, self.name, self._key)
            return self._concrete
        return getattr(ob, self._key)


class ConcreteProperty(c.Expr):
    __slots__ = ("record", "name", "_key")

    def __init__(self, record, name, key):
        self.record = record
        self.name = name
        self._key = key

    def __repr__(self):
        return "<P: {}>".format(self.name)

    @lift
    def __add__(self, other):
        return c.Add(self, other)

    @lift
    def __radd__(self, other):
        return c.Add(other, self)

    @lift
    def __sub__(self, other):
        return c.Sub(self, other)

    @lift
    def __rsub__(self, other):
        return c.Sub(other, self)

    @lift
    def __mul__(self, other):
        return c.Mul(self, other)

    @lift
    def __rmul__(self, other):
        return c.Mul(other, self)

    @lift
    def __div__(self, other):
        return c.Div(self, other)

    @lift
    def __rdiv__(self, other):
        return c.Div(other, self)

    @lift
    def __and__(self, other):
        return c.And(self, other)

    @lift
    def __rand__(self, other):
        return c.And(other, self)

    @lift
    def __or__(self, other):
        return c.Or(self, other)

    @lift
    def __ror__(self, other):
        return c.Or(other, self)

    @lift
    def __gt__(self, other):
        return c.Gt(self, other)

    @lift
    def __lt__(self, other):
        return c.Lt(self, other)

    @lift
    def __ge__(self, other):
        return c.Ge(self, other)

    @lift
    def __le__(self, other):
        return c.Le(self, other)

    @lift
    def __eq__(self, other):
        if other is None:
            return c.self.is_(None)
        return c.Eq(self, other)

    @lift
    def __ne__(self, other):
        if other is None:
            return c.self.is_not(None)
        return c.Ne(self, other)

    @lift
    def is_(self, other):
        return c.Is(self, other)

    @lift
    def is_not(self, other):
        return c.Is(self, c.Not(other))

    @lift
    def in_(self, other):
        return c.In(self, other)

    @lift
    def not_in(self, other):
        return c.NotIn(self, other)

    @lift
    def like(self, other):
        return c.Like(self, other)

    @lift
    def ilike(self, other):
        return c.Ilike(self, other)

    @lift
    def rlike(self, other):
        return c.Like(other, self)

    @lift
    def rilike(self, other):
        return c.Ilike(other, self)
