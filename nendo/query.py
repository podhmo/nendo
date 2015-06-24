# -*- coding:utf-8 -*-
from itertools import chain
from .clause import Select, Where, From, OrderBy, Having
from .env import Env
from .exceptions import ConflictName, MissingName


class Alias(object):
    pass


class Query(object):
    def __init__(self, select=None, where=None, from_=None, having=None, order_by=None, env=None):
        self.env = env or Env()
        self._select = select or Select()
        self._where = where or Where()
        self._from = from_ or From()
        self._order_by = order_by or OrderBy()
        self._having = having or Having()

    def make(self, select=None, where=None, from_=None, having=None, order_by=None, env=None):
        return self.__class__(
            select=select or self._select.make(),
            where=where or self._where.make(),
            from_=from_ or self._from.make(),
            order_by=order_by or self._order_by.make(),
            having=having or self._having.make(),
            env=env or self.env.make()
        )

    def swap(self, name):
        return self.make(
            select=self._select.swap(self, name),
            from_=self._from.swap(self, name)
        )

    def select(self, *args):
        return self.make(select=Select(*chain(self._select.args, args)))

    def where(self, *args):
        return self.make(where=Where(*chain(self._where.args, args)))

    def from_(self, *args):
        return self.make(from_=From(*chain(self._from.args, args)))

    def order_by(self, *args):
        return self.make(order_by=OrderBy(*chain(self._order_by.args, args)))

    def having(self, *args):
        return self.make(having=Having(*chain(self._having.args, args)))

    def _table_validation(self, context):
        # from validation
        tables = list(self._from.tables())
        table_name_list = [r.get_name() for r in tables]
        table_name_set = set(table_name_list)
        if len(table_name_set) != len(table_name_list):
            raise ConflictName(", ".join(table_name_list))

        # select validation
        for prop in self._select.props():
            if prop.record.get_name() not in table_name_set:
                raise MissingName("{}.{}".format(prop.record.get_name(), prop.name))
        # where validation
        for table in set(self._where.tables()):
            if table.get_name() not in table_name_set:
                if table.is_table():
                    raise MissingName(table.get_name())

    def _column_validation(self, context):
        prop_name_set = set([p.projection_name for p in self._from.props()])
        # select validation
        for p in self._select.props():
            if p.original_name not in prop_name_set:
                raise ConflictName("SELECT: {} is not found from FROM clause".format(p.name))

        # from validation (on)
        for cond in self._from.args:
            for p in cond.props():
                if p.original_name not in prop_name_set:
                    raise ConflictName("FROM: {} is not found from FROM clause".format(p.original_name))

    def validate(self, context):
        self._table_validation(context)
        self._column_validation(context)

    def props(self):
        return list(self._select.props()) or list(self._from.props())
