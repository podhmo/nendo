# -*- coding:utf-8 -*-
from .condition import Expr
from .value import Prepared


def is_empty_clause(clause):
    return clause.is_empty()


def is_expr(expr):
    return isinstance(expr, Expr)


def is_prepared(v):
    return isinstance(v, Prepared)


def has_env(v):
    return hasattr(v, "env")
