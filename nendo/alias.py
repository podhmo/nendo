# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .record import RecordMeta
from .property import ConcreteProperty
from .query import Query
from . import condition as c


class QueryRecord(object):
    """record like object from query"""
    def __init__(self, query, name):
        self.query = query.swap(name)
        self._name = name

    def __getattr__(self, k):
        value = getattr(self.query._from, k)
        if isinstance(value, RecordMeta):  # xxx:
            value = AliasRecord(value, self._name, prefix="{}_".format(value.get_name()))
            setattr(self, k, value)
        return value

    def get_name(self):
        return self._name

    def tables(self):
        yield self

    def join(self, other, *args):
        return c.Join(self, other, args)

    def left_outer_join(self, other, *args):
        return c.LeftOuterJoin(self, other, args)

    def right_outer_join(self, other, *args):
        return c.RightOuterJoin(self, other, args)

    def cross_join(self, other, *args):
        return c.CrossJoin(self, other, args)


class AliasRecord(object):
    def __init__(self, core, name, prefix=""):
        self._name = name
        self._core = core
        self._prefix = prefix

    def get_name(self):
        return self._name

    def __getattr__(self, k):
        value = getattr(self._core, k)
        if isinstance(value, ConcreteProperty):
            value = AliasRecordProperty(self, value, prefix=self._prefix)
            setattr(self, k, value)
        return value

    def tables(self):
        yield self


class AliasRecordProperty(ConcreteProperty):
    def __init__(self, alias, prop, prefix=""):
        name = "{}{}".format(prefix, prop.name)
        super().__init__(alias, name, prop._key)
        self.prop = prop


class AliasProperty(ConcreteProperty):  # todo: cache via weak reference
    def __init__(self, prop, name):
        super().__init__(prop.record, name, prop._key)
        self.prop = prop


@singledispatch
def alias(v, name):
    raise NotImplementedError(v)


@alias.register(Query)
def on_query(query, name):
    return QueryRecord(query, name)


@alias.register(RecordMeta)
def on_record(record, name):
    return AliasRecord(record, name)


@alias.register(ConcreteProperty)
def on_property(prop, name):
    return AliasProperty(prop, name)
