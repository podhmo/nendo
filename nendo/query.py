# -*- coding:utf-8 -*-
from itertools import chain
from .clause import SubSelect, Select, Where, From, Having
from .env import Env


class Alias(object):
    pass


class Query(object):
    def __init__(self, select=None, where=None, from_=None, having=None, env=None):
        self.env = env or Env()
        self._select = select or Select()
        self._where = where or Where()
        self._from = from_ or From()
        self._having = having or Having()

    def make(self, select=None, where=None, from_=None, having=None, env=None):
        return self.__class__(
            select=select or self._select.make(),
            where=where or self._where.make(),
            from_=from_ or self._from.make(),
            having=having or self._having.make(),
            env=env or self.env.make()
        )

    def swap(self, name):
        return self.make(
            select=SubSelect(*self._select.args),
            from_=From(*[e.swap(name) for e in self._from.args])
        )

    def select(self, *args):
        return self.make(select=Select(*chain(self._select.args, args)))

    def where(self, *args):
        return self.make(where=Where(*chain(self._where.args, args)))

    def from_(self, *args):
        return self.make(from_=From(*chain(self._from.args, args)))

    def having(self, *args):
        return self.make(having=Having(*chain(self._having.args, args)))

    def validate(self, context):
        # from validation
        table_name_list = [r.get_name() for r in self._from.tables]
        table_name_set = set(table_name_list)
        if len(table_name_set) != len(table_name_list):
            raise ConflictName(", ".join(table_name_list))

        # select validation
        for prop in self._select.props:
            if prop.record.get_name() not in table_name_set:
                raise MissingName("{}.{}".format(prop.record.get_name(), prop.name))
        # where validation
        # TODO:


class ValidationError(Exception):
    pass


class ConflictName(ValidationError):
    pass


class MissingName(ValidationError):
    pass
