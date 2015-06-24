# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from nendo.record import make_record
from nendo.query import Query
from nendo.alias import alias
from nendo.compiler import compiler, ARGS


def render(query, **context):
    sql = compiler(query, context)
    return (sql, context[ARGS])

__all__ = [
    "make_record",
    "alias",
    "Query",
    "render"
]
