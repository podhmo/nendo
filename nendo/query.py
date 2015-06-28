# -*- coding:utf-8 -*-
from itertools import chain
from .langhelpers import reify, COUNTER
from .clause import Select, Where, From, OrderBy, Having, Limit, GroupBy
from .env import Env
from .exceptions import ConflictName, MissingName, InvalidCombination
from .property import ConcreteProperty


class _QueryFrom(From):
    _name = "FROM"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        props = [list(e.props()) for e in self.args]
        for another in props[1:]:
            if len(props[0]) != len(another):
                raise InvalidCombination("conflict number of column {} != {}".format(len(props[0]), len(another)))

    @reify
    def _props(self):
        return [_QueryProperty(self.args[0], p, p.name) for p in self.args[0].props()]

    def tables(self):
        return []

    def props(self):
        yield from self._props


class _UnionFrom(_QueryFrom):
    separator = "UNION"


class _UnionAllFrom(_QueryFrom):
    separator = "UNION ALL"


class _QueryProperty(ConcreteProperty):
    def __init__(self, query, prop, name):
        self.query = query
        super().__init__(prop.record, name, prop._key)

    @property
    def original_name(self):
        return self.name

    @property
    def full_name(self):
        return "{}.{}".format(self.query.get_name(), self.name)


class Query(object):
    def __init__(self, select=None, where=None, from_=None, having=None, group_by=None, order_by=None, limit=None, env=None):
        self.env = env or Env()
        self._select = select or Select()
        self._where = where or Where()
        self._from = from_ or From()
        self._group_by = group_by or GroupBy()
        self._order_by = order_by or OrderBy()
        self._having = having or Having()
        self._limit = limit or Limit()

    def union(self, other):
        return self.__class__(from_=_UnionFrom(self, other))

    def union_all(self, other):
        return self.__class__(from_=_UnionAllFrom(self, other))

    def make(self, select=None, where=None, from_=None, having=None, group_by=None, order_by=None, limit=None, env=None):
        return self.__class__(
            select=select or self._select.make(),
            where=where or self._where.make(),
            from_=from_ or self._from.make(),
            group_by=group_by or self._group_by.make(),
            order_by=order_by or self._order_by.make(),
            having=having or self._having.make(),
            limit=limit or self._limit.make(),
            env=env or self.env.make()
        )

    def swap(self, name):
        return self.make(
            select=self._select.swap(self, name),
            from_=self._from.swap(self, name)
        )

    def select(self, *args, replace=False, distinct=False):
        suffix = "DISTINCT" if distinct else ""
        if replace:
            return self.make(select=Select(*args, suffix=suffix))
        else:
            return self.make(select=Select(*chain(self._select.args, args), suffix=suffix))

    def where(self, *args, replace=False):
        if replace:
            return self.make(where=Where(*args))
        else:
            return self.make(where=Where(*chain(self._where.args, args)))

    def from_(self, *args, replace=False):
        if replace:
            return self.make(from_=From(*args))
        else:
            return self.make(from_=From(*chain(self._from.args, args)))

    def order_by(self, *args, replace=False):
        if replace:
            return self.make(order_by=OrderBy(*args))
        else:
            return self.make(order_by=OrderBy(*chain(self._order_by.args, args)))

    def group_by(self, *args, replace=False):
        if replace:
            return self.make(group_by=GroupBy(*args))
        else:
            return self.make(group_by=GroupBy(*chain(self._group_by.args, args)))

    def having(self, *args, replace=False):
        if replace:
            return self.make(having=Having(*args))
        else:
            return self.make(having=Having(*chain(self._having.args, args)))

    def limit(self, *args, replace=False):
        if replace:
            return self.make(limit=Limit(*args))
        else:
            return self.make(limit=Limit(*chain(self._limit.args, args)))

    def _table_validation(self, context, tables):
        # from validation
        table_name_list = [r.get_name() for r in tables]
        table_name_set = set(table_name_list)
        if len(table_name_set) != len(table_name_list):
            raise ConflictName(", ".join(table_name_list))

        if not tables:
            return  # todo:fix (on union query, tables() return empty list)

        # select validation
        for prop in self._select.props():
            if prop.record.get_name() not in table_name_set:
                raise MissingName("SELECT: table {}.{} is not in {}".format(prop.record.get_name(), prop.name, table_name_set))
        # where validation
        for table in set(self._where.tables()):
            if table.get_name() not in table_name_set:
                if table.is_table():
                    raise MissingName("WHERE: table {} is not in {}".format(table.get_name(), table_name_set))

    def _column_validation(self, context, tables):
        prop_name_set = set([p.projection_name for p in self._from.props()])
        # select validation
        for p in self._select.props():
            if p.original_name not in prop_name_set:
                raise ConflictName("SELECT: {} is not found from FROM clause in {}".format(p.original_name, prop_name_set))

        if not tables:
            return  # todo:fix (on union query, tables() return empty list)

        # from validation (on)
        for cond in self._from.args:
            for p in cond.props():
                if p.original_name not in prop_name_set:
                    raise ConflictName("FROM: {} is not found from FROM clause in {}".format(p.original_name, prop_name_set))

    def validate(self, context):
        tables = self.tables()
        self._table_validation(context, tables)
        self._column_validation(context, tables)

    def props(self):
        return list(self._select.props()) or list(self._from.props())

    def tables(self):
        return list(self._from.tables())

    def __getattr__(self, k):
        for prop in self.props():
            if prop.name == k:
                prop = _QueryProperty(self, prop, prop.name)
                setattr(self, k, prop)
                return prop
        raise AttributeError(k)

    @reify
    def _name(self):
        return "_t{}".format(COUNTER())

    def get_name(self):
        return self._name
