from . import expr
from .expr import lift, Expr, liftN


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


class Property(Expr):
    @lift
    def __add__(self, other):
        return expr.Add(self, other)

    @lift
    def __radd__(self, other):
        return expr.Add(other, self)

    @lift
    def __sub__(self, other):
        return expr.Sub(self, other)

    @lift
    def __rsub__(self, other):
        return expr.Sub(other, self)

    @lift
    def __mul__(self, other):
        return expr.Mul(self, other)

    @lift
    def __rmul__(self, other):
        return expr.Mul(other, self)

    @lift
    def __div__(self, other):
        return expr.Div(self, other)

    @lift
    def __rdiv__(self, other):
        return expr.Div(other, self)

    @lift
    def __gt__(self, other):
        return expr.Gt(self, other)

    @lift
    def __lt__(self, other):
        return expr.Lt(self, other)

    @lift
    def __ge__(self, other):
        return expr.Ge(self, other)

    @lift
    def __le__(self, other):
        return expr.Le(self, other)

    @lift
    def __eq__(self, other):
        if other is None:
            return expr.self.is_(None)
        return expr.Eq(self, other)

    @lift
    def __ne__(self, other):
        if other is None:
            return expr.self.is_not(None)
        return expr.Ne(self, other)

    @lift
    def is_(self, other):
        return expr.Is(self, other)

    @lift
    def is_not(self, other):
        return expr.Is(self, expr.Not(other))

    @lift
    def in_(self, other):
        return expr.In(self, other)

    @lift
    def not_in(self, other):
        return expr.NotIn(self, other)

    @liftN
    def between(self, left, right):
        return expr.Between(self, left, right)

    @lift
    def like(self, other):
        return expr.Like(self, other)

    @lift
    def ilike(self, other):
        return expr.Ilike(self, other)

    @lift
    def rlike(self, other):
        return expr.Like(other, self)

    @lift
    def rilike(self, other):
        return expr.Ilike(other, self)

    def asc(self):
        return expr.Asc(self)

    def desc(self):
        return expr.Desc(self)


class ConcreteProperty(Property):
    __slots__ = ("record", "_key")

    @property
    def original_name(self):
        return self.name

    @property
    def projection_name(self):
        return self.name

    def __repr__(self):
        return "<P: {}>".format(self.name)

    def __init__(self, record, name, key):
        self.record = record
        self.name = name
        self._key = key
        super().__init__()

    def tables(self):
        yield self.record

    def props(self):
        yield self
