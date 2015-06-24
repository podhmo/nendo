# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .record import RecordMeta
from .property import ConcreteProperty
from .query import Query
from . import expr


class AliasRecordProperty(ConcreteProperty):
    def __init__(self, alias, prop, prefix=""):
        name = "{}{}".format(prefix, prop.name)
        super().__init__(alias, name, prop._key)
        self.prop = prop


class AliasExpressionProperty(ConcreteProperty):
    def __init__(self, alias, prop, prefix=""):
        name = "{}{}".format(prefix, prop.name)
        super().__init__(alias, name, prop._key)
        self.prop = prop


class AliasProperty(ConcreteProperty):  # todo: cache via weak reference
    def __init__(self, prop, name):
        super().__init__(prop.record, name, prop._key)
        self.prop = prop

    @property
    def original_name(self):
        return self.prop.name


class AliasRecord(object):
    PropertyFactory = AliasRecordProperty

    def __init__(self, core, name, prefix="", parent=None):
        self._name = name
        self._core = core
        self._prefix = prefix
        self._parent = parent

    def get_name(self):
        return self._name

    def is_table(self):
        return True

    def __getattr__(self, k):
        value = getattr(self._core, k)
        if isinstance(value, ConcreteProperty):
            value = self.PropertyFactory(self, value, prefix=self._prefix)
            setattr(self, k, value)
        return value

    def tables(self):
        yield self

    def props(self):
        return [getattr(self, p.name) for p in self._core.props()]


class AliasExpressionRecord(AliasRecord):
    PropertyFactory = AliasExpressionProperty

    def is_table(self):
        return False


class QueryRecord(object):
    """record like object from query"""
    RecordFactory = AliasRecord

    def __init__(self, query, name, swapped=False):
        self.query = query.swap(name) if not swapped else query
        self._name = name

    def __getattr__(self, k):
        value = getattr(self.query._from, k)
        if isinstance(value, RecordMeta):  # xxx:
            prefix = "{}_".format(value.get_name())
            value = self.RecordFactory(value, self._name, prefix=prefix, parent=self)
            setattr(self, k, value)
        return value

    def get_name(self):
        return self._name

    def join(self, other, *args):
        return expr.Join(self, other, args)

    def left_outer_join(self, other, *args):
        return expr.LeftOuterJoin(self, other, args)

    def right_outer_join(self, other, *args):
        return expr.RightOuterJoin(self, other, args)

    def cross_join(self, other, *args):
        return expr.CrossJoin(self, other, args)

    def __call__(self):
        return QueryBodyRecord(self.query, self._name, swapped=True)

    def tables(self):
        yield self

    def props(self):
        yield from self.query.props()


class QueryBodyRecord(QueryRecord):
    """record like object but this is unfolded like a subquery"""
    RecordFactory = AliasExpressionRecord


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
