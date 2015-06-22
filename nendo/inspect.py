# -*- coding:utf-8 -*-
def is_empty_clause(clause):
    return clause.is_empty()


def is_expr(expr):
    from .condition import Expr
    return isinstance(expr, Expr)


def is_prepared(v):
    from .value import Prepared
    return isinstance(v, Prepared)


def has_env(v):
    return hasattr(v, "env")
