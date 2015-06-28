# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .record import RecordMeta
from .property import ConcreteProperty
from .value import Function
from .query import Query
from . import expr


class AliasFunction(Function):
    def __init__(self, fn, alias_name):
        super().__init__(fn.value, *fn.args)
        self.fn = fn
        self.alias_name = alias_name


class AliasRecordProperty(ConcreteProperty):
    def __init__(self, alias, prop, name):
        super().__init__(alias, name, prop._key)
        self.prop = prop

    def make(self):
        return self.__class__(self.record, self.prop, self.name)


class AliasExpressionProperty(ConcreteProperty):
    def __init__(self, alias, prop, name):
        super().__init__(alias, name, prop._key)
        self.prop = prop

    def make(self):
        return self.__class__(self.record, self.prop, self.name)


class AliasProperty(ConcreteProperty):  # todo: cache via weak reference
    def __init__(self, prop, name):
        super().__init__(prop.record, name, prop._key)
        self.prop = prop

    @property
    def original_name(self):
        return self.prop.original_name


class _Joinable(object):
    def join(self, other, *args):
        return expr.Join(self, other, args)

    def left_outer_join(self, other, *args):
        return expr.LeftOuterJoin(self, other, args)

    def right_outer_join(self, other, *args):
        return expr.RightOuterJoin(self, other, args)

    def cross_join(self, other, *args):
        return expr.CrossJoin(self, other, args)


class AliasRecord(_Joinable):
    PropertyFactory = AliasRecordProperty

    def __init__(self, core, name, prefix="", parent=None):
        self.alias_name = name
        self._core = core
        self._prefix = prefix
        self._parent = parent

    def get_name(self):
        return self.alias_name

    def is_table(self):
        return True

    def __getattr__(self, k):
        value = getattr(self._core, k)
        if isinstance(value, (ConcreteProperty, Function)):
            alias_name = "{}{}".format(self._prefix, value.name)
            value = self.PropertyFactory(self, value, alias_name)
            setattr(self, k, value)
        return value

    def tables(self):
        yield self

    def props(self):
        return [getattr(self, p.name) for p in self._core.props()]

    def swap(self, name):  # xxx
        return self


class AliasExpressionRecord(AliasRecord):
    PropertyFactory = AliasExpressionProperty

    def is_table(self):
        return False


class QueryRecord(_Joinable):
    """record like object from query"""
    RecordFactory = AliasRecord

    def __init__(self, query, name, swapped=False):
        self.query = query.swap(name) if not swapped else query
        self.alias_name = name

    def is_table(self):
        return False  # xxx

    def __getattr__(self, k):
        value = getattr(self.query._from, k)
        if isinstance(value, RecordMeta):  # xxx:
            prefix = "{}_".format(value.get_name())
            value = self.RecordFactory(value, self.alias_name, prefix=prefix, parent=self)
            setattr(self, k, value)
        return value

    def get_name(self):
        return self.alias_name

    def union(self, other, *args):
        return self.__class__(self.query.union(other), self.alias_name, swapped=True)

    def union_all(self, other, *args):
        return self.__class__(self.query.union_all(other), self.alias_name, swapped=True)

    def __call__(self):
        return QueryBodyRecord(self.query, self.alias_name, swapped=True)

    def tables(self):
        yield self

    def swap(self, name):  # xxx
        return self

    def props(self):
        for prop in self.query.props():
            record = getattr(self, prop.record.get_name())
            yield getattr(record, prop.original_name)


class QueryBodyRecord(QueryRecord):
    """record like object but this is unfolded like a subquery"""
    RecordFactory = AliasExpressionRecord


def subquery(query, name=None):
    return QueryBodyRecord(query, name=name)


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


@alias.register(Function)
def on_function(fn, name):
    return AliasFunction(fn, name)
