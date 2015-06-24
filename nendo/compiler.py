# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .query import Query
from .clause import Clause, SubSelect
from .expr import BOp, PreOp, PostOp, TriOp
from .record import RecordMeta
from .property import ConcreteProperty
from .alias import AliasRecord, AliasProperty, AliasExpressionProperty, QueryRecord
from .value import Value, Prepared


ARGS = "__i_args"  # xxx: this is the keyname of stored arguments


@singledispatch
def compiler(v, context, force=False, path=None):
    raise NotImplementedError(v)


@compiler.register(Query)
def on_query(query, context, force=False, path=None):
    if ARGS not in context:
        context[ARGS] = []
    path = path or []
    if not force:
        query.validate(context)

    r = []
    if query._select.is_empty():
        r.append("SELECT")
        columns = []
        for p in query.props():
            columns.append(compiler(p, context, path=path))
        r.append(", ".join(columns))
    else:
        r.append(compiler(query._select, context, path=path))
    if not query._from.is_empty():
        r.append(compiler(query._from, context, path=path))
    if not query._where.is_empty():
        r.append(compiler(query._where, context, path=path))
    if not query._order_by.is_empty():
        r.append(compiler(query._order_by, context, path=path))
    if not query._having.is_empty():
        r.append(compiler(query._having, context, path=path))
    if not query._limit.is_empty():
        r.append(compiler(query._limit, context, path=path))
    return " ".join(r)


@compiler.register(Clause)
def on_clause(clause, context, path=None):
    return "{} {}".format(clause.get_name(), ", ".join(compiler(e, context, path=path) for e in clause.args))


@compiler.register(SubSelect)
def on_swap_select(clause, context, path=None):
    args = []
    for e in clause.args:
        column_name = compiler(e, context, path=path)
        args.append("{} as {}".format(column_name, e.projection_name))
    return "{} {}".format(clause.get_name(), ", ".join(args))


@compiler.register(BOp)
def on_bop(op, context, path=None):
    return "({} {} {})".format(compiler(op.left, context, path=path), op.op, compiler(op.right, context, path=path))


@compiler.register(PreOp)
def on_preop(op, context, path=None):
    return "({} {})".format(op.op, compiler(op.value, context, path=path))


@compiler.register(PostOp)
def on_postop(op, context, path=None):
    return "{} {}".format(compiler(op.value, context, path=path), op.op)


@compiler.register(TriOp)
def on_triop(op, context, path=None):
    r = []
    r.append(compiler(op.left, context, path=path))
    r.append(op.op)
    r.append(compiler(op.right, context, path=path))
    for e in op.args:
        r.append("ON {}".format(compiler(e, context, path=path)))
    return " ".join(r)


@compiler.register(QueryRecord)
def on_query_record(record, context, path=None):
    name = record.get_name()
    path = path or []
    path.append(name)
    value = "({}) as {}".format(compiler(record.query, context, path=path), name)
    path.pop()
    return value


@compiler.register(RecordMeta)
def on_record(record, context, path=None):
    return record.get_name()


@compiler.register(AliasRecord)
def on_alias_record(record, context, path=None):
    return "{} as {}".format(compiler(record._core, context, path=path), record.get_name())


@compiler.register(ConcreteProperty)
def on_property(prop, context, path=None):
    return "{}.{}".format(prop.record.get_name(), prop.name)


@compiler.register(AliasProperty)
def on_alias_property(prop, context, path=None):
    return "{} as {}".format(compiler(prop.prop, context, path=path), prop.name)


# xxx:
@compiler.register(AliasExpressionProperty)
def on_alias_expression_property(prop, context, path=None):
    return "({})".format(compiler(prop.record._parent.query, context, path=path))


@compiler.register(Prepared)
def on_prepared(v, context, path=None):
    if not path:
        context[ARGS].append(context[v.key])
        return "%s"
    else:
        path.append(v.key)
        k = ".".join(path)
        context[ARGS].append(context[k])  # side-effect!
        return "%s"


@compiler.register(Value)
def on_value(v, context, path=None):
    v = v.value
    if v is None:
        return "NULL"
    elif isinstance(v, (list, tuple)):
        r = []
        for e in v:
            if isinstance(e, Value):
                r.append(compiler(e, context, path=path))
            else:
                r.append(compiler(Value(e), context, path=path))
        return "({})".format(", ".join(r))
    elif isinstance(v, str):
        return "'{}'".format(v)
    elif isinstance(v, bool):
        return "{}".format(int(v))
    else:
        return str(v)
    raise NotImplementedError(v)
