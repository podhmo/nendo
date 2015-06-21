# -*- coding:utf-8 -*-
from .langhelpers import Registry, reify
from .env import Env

registry = Registry()


class Expr(object):
    @reify
    def env(self):
        return Env(self._env)

    def __init__(self, env=None):
        self._env = env


class UOp(Expr):
    op = ""
    __slots__ = ("value", "_env")

    def __init__(self, value, env=None):
        self.value = value
        super().__init__(env=env)

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


@registry
class Not(PreOp):
    op = "NOT"


@registry
class Add(BOp):
    op = '+'


@registry
class Sub(BOp):
    op = '-'


@registry
class Mul(BOp):
    op = '*'


@registry
class Div(BOp):
    op = '/'


@registry
class Gt(BOp):
    op = '>'


@registry
class Lt(BOp):
    op = '<'


@registry
class Ge(BOp):
    op = '>='


@registry
class Le(BOp):
    op = '<='


@registry
class And(BOp):
    op = 'AND'


@registry
class Or(BOp):
    op = 'OR'


@registry
class Eq(BOp):
    op = '='


@registry
class Ne(BOp):
    op = '<>'


@registry
class Is(BOp):
    op = 'IS'


@registry
class In(BOp):
    op = 'IN'


@registry
class NotIn(BOp):
    op = 'NOT IN'


@registry
class Like(BOp):
    op = 'LIKE'


@registry
class Ilike(BOp):
    op = 'ILIKE'


# join conditon
@registry
class Join(TriOp):
    op = "JOIN"


@registry
class LeftOuterJoin(TriOp):
    op = "LEFT OUTER JOIN"


@registry
class RightOuterJoin(TriOp):
    op = "RIGHT OUTER JOIN"


@registry
class FullOuterJoin(TriOp):
    op = "FULL OUTER JOIN"


@registry
class CrossJoin(TriOp):
    op = "Cross JOIN"
