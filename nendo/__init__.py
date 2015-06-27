# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from nendo.record import make_record
from nendo.query import Query
from nendo.alias import alias, subquery
from nendo.compiler import compiler, ARGS
from nendo.options import Options


def render(query, **context):
    options = Options(use_validation=True,
                      one_table=len(list(query.tables())) <= 1,
                      one_line_sql=True)
    sql = compiler(query, context, options=options)
    return (sql, context[ARGS])

__all__ = [
    "make_record",
    "alias",
    "Query",
    "render",
    "subquery"
]
