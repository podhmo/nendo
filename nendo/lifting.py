# -*- coding:utf-8 -*-
import functools
from . import inspect as i


def lift(method):
    @functools.wraps(method)
    def _lift(self, other):
        from .value import Value
        if other is None:
            value = method(self, None)
        elif not i.is_expr(other):
            value = method(self, Value(other))
        else:
            value = method(self, other)
        value.env.merge(self, other)  # side effect
        return value
    return _lift
