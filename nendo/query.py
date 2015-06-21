# -*- coding:utf-8 -*-
from itertools import chain
from .clause import Select, Where, From, Having
from .env import Env


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

    def select(self, *args):
        return self.make(select=Select(*chain(self._select.args, args)))

    def where(self, *args):
        return self.make(where=Where(*chain(self._where.args, args)))

    def from_(self, *args):
        return self.make(from_=From(*chain(self._from.args, args)))

    def having(self, *args):
        return self.make(having=Having(*chain(self._having.args, args)))
