# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from nendo.record import make_record
from nendo.query import Query
from nendo.alias import alias, subquery
from nendo.compiler import compiler, ARGS
from nendo.options import Options


class Renderer(object):
    def __init__(self, use_validation=True, one_line_sql=True, interpolation="%s"):
        self.use_validation = use_validation
        self.one_line_sql = one_line_sql
        self.interpolation = interpolation

    def get_options(self, query):
        return Options(use_validation=self.use_validation,
                       one_table=len(list(query.tables())) <= 1,
                       interpolation=self.interpolation,
                       one_line_sql=self.one_line_sql)

    def __call__(self, query, **context):
        options = self.get_options(query)
        return _render(query, options, context)


def _render(query, options, context):
    sql = compiler(query, context, options=options)
    return (sql, context[ARGS])

render = Renderer()
SelectQuery = Query

__all__ = [
    "make_record",
    "alias",
    "Query",
    "SelectQuery",
    "render",
    "subquery"
]
