# -*- coding:utf-8 -*-
from functools import wraps, partial
from .langhelpers import reify
from .env import Env


def lift(method):
    @wraps(method)
    def _lift(self, other):
        if other is None:
            value = method(self, None)
        elif not isinstance(other, Expr):
            from .value import Value
            value = method(self, Value(other))
        else:
            value = method(self, other)
        value.env.merge(self, other)  # side effect
        return value
    return _lift


class Expr(object):
    @reify
    def env(self):
        return Env(self._env)

    def __init__(self, env=None):
        self._env = env

    @lift
    def __and__(self, other):
        return And(self, other)

    @lift
    def __rand__(self, other):
        return And(other, self)

    @lift
    def __or__(self, other):
        return Or(self, other)

    @lift
    def __ror__(self, other):
        return Or(other, self)

    def __invert__(self):
        return Not(self)


class UOp(Expr):
    __slots__ = ("op", "value", "_env")

    def __init__(self, op, value, env=None):
        self.op = op
        self.value = value
        super().__init__(env=env)

    def tables(self):
        yield from self.value.tables()

    def props(self):
        yield from self.value

    def __repr__(self):
        return "<U: {} {} {}>".format(self.op, self.value)


class PreOp(UOp):
    @property
    def right(self):
        return self.value


class PostOp(UOp):
    @property
    def left(self):
        return self.value


class BOp(Expr):
    __slots__ = ("op", "left", "right", "_env")

    def __init__(self, op, left, right, env=None):
        self.op = op
        self.left = left
        self.right = right
        super().__init__(env=env)

    def tables(self):
        yield from self.left.tables()
        yield from self.right.tables()

    def props(self):
        yield from self.left.props()
        yield from self.right.props()

    def __repr__(self):
        return "<B: {} {} {}>".format(self.op, self.left, self.right)


class TriOp(Expr):  # todo: move
    __slots__ = ("op", "left", "right", "args", "_env")

    def __init__(self, op, left, right, args, env=None):
        self.op = op
        self.left = left
        self.right = right
        self.args = args
        super().__init__(env=env)

    def __repr__(self):
        return "<T: {} {} {} {}>".format(self.op, self.left, self.right, self.args)

    def tables(self):
        yield from self.left.tables()
        yield from self.right.tables()

    def props(self):
        for cond in self.args:
            yield from cond.props()

    def swap(self, name):
        return self  # xxx

    def join(self, other, *args):
        return Join(self, other, args)

    def left_outer_join(self, other, *args):
        return LeftOuterJoin(self, other, args)

    def right_outer_join(self, other, *args):
        return RightOuterJoin(self, other, args)

    def cross_join(self, other, *args):
        return CrossJoin(self, other, args)

Not = partial(PreOp, "NOT")
Asc = partial(PostOp, "ASC")
Desc = partial(PostOp, "DESC")
Add = partial(BOp, "+")
Sub = partial(BOp, '-')
Mul = partial(BOp, '*')
Div = partial(BOp, '/')
Gt = partial(BOp, '>')
Lt = partial(BOp, '<')
Ge = partial(BOp, '>=')
Le = partial(BOp, '<=')
And = partial(BOp, 'AND')
Or = partial(BOp, 'OR')
Eq = partial(BOp, '=')
Ne = partial(BOp, '<>')
Is = partial(BOp, 'IS')
In = partial(BOp, 'IN')
NotIn = partial(BOp, 'NOT IN')
Between = partial(BOp, "BETWEEN")
Like = partial(BOp, 'LIKE')
Ilike = partial(BOp, 'ILIKE')
Join = partial(TriOp, "JOIN")
LeftOuterJoin = partial(TriOp, "LEFT OUTER JOIN")
RightOuterJoin = partial(TriOp, "RIGHT OUTER JOIN")
FullOuterJoin = partial(TriOp, "FULL OUTER JOIN")
CrossJoin = partial(TriOp, "CROSS JOIN")
