# -*- coding:utf-8 -*-
import functools
from .langhelpers import reify
from .env import Env


def lift(method):
    @functools.wraps(method)
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
    op = ""
    __slots__ = ("value", "_env")

    def __init__(self, value, env=None):
        self.value = value
        super().__init__(env=env)

    def tables(self):
        yield from self.value.tables()

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
    op = ""
    __slots__ = ("left", "right", "_env")

    def __init__(self, left, right, env=None):
        self.left = left
        self.right = right
        super().__init__(env=env)

    def tables(self):
        yield from self.left.tables()
        yield from self.right.tables()

    def __repr__(self):
        return "<B: {} {} {}>".format(self.op, self.left, self.right)


class TriOp(Expr):  # todo: move
    op = ""
    __slots__ = ("left", "right", "args", "_env")

    def __init__(self, left, right, args, env=None):
        self.left = left
        self.right = right
        self.args = args
        super().__init__(env=env)

    def __repr__(self):
        return "<T: {} {} {} {}>".format(self.op, self.left, self.right, self.args)

    def tables(self):
        yield from self.left.tables()
        yield from self.right.tables()

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


@registry
class Not(PreOp):
    op = "NOT"


class Asc(PostOp):
    op = "ASC"


class Desc(PostOp):
    op = "DESC"


class Add(BOp):
    op = '+'


class Sub(BOp):
    op = '-'


class Mul(BOp):
    op = '*'


class Div(BOp):
    op = '/'


class Gt(BOp):
    op = '>'


class Lt(BOp):
    op = '<'


class Ge(BOp):
    op = '>='


class Le(BOp):
    op = '<='


class And(BOp):
    op = 'AND'


class Or(BOp):
    op = 'OR'


class Eq(BOp):
    op = '='


class Ne(BOp):
    op = '<>'


class Is(BOp):
    op = 'IS'


class In(BOp):
    op = 'IN'


class NotIn(BOp):
    op = 'NOT IN'


class Between(BOp):
    op = "BETWEEN"


class Like(BOp):
    op = 'LIKE'


class Ilike(BOp):
    op = 'ILIKE'


# join conditon
class Join(TriOp):
    op = "JOIN"


class LeftOuterJoin(TriOp):
    op = "LEFT OUTER JOIN"


class RightOuterJoin(TriOp):
    op = "RIGHT OUTER JOIN"


class FullOuterJoin(TriOp):
    op = "FULL OUTER JOIN"


class CrossJoin(TriOp):
    op = "CROSS JOIN"
