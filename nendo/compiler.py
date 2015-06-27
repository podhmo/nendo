# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from datetime import date, datetime, time
from .query import Query
from .clause import Clause, _SubSelectProperty
from .expr import BOp, PreOp, PostOp, TriOp, JoinOp, Expr
from .record import RecordMeta
from .property import ConcreteProperty
from .alias import AliasRecord, AliasProperty, AliasExpressionProperty, QueryRecord
from .value import Value, Prepared, List, Constant, Function


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
            columns.append(compiler(p, context, force=force, path=path))
        r.append(", ".join(columns))
    else:
        r.append(compiler(query._select, context, force=force, path=path))
    if not query._from.is_empty():
        r.append(compiler(query._from, context, force=force, path=path))
    if not query._where.is_empty():
        r.append(compiler(query._where, context, force=force, path=path))
    if not query._order_by.is_empty():
        r.append(compiler(query._order_by, context, force=force, path=path))
    if not query._having.is_empty():
        r.append(compiler(query._having, context, force=force, path=path))
    if not query._limit.is_empty():
        r.append(compiler(query._limit, context, force=force, path=path))
    return " ".join(r)


@compiler.register(Clause)
def on_clause(clause, context, force=False, path=None):
    return "{} {}".format(clause.get_name(), ", ".join(compiler(e, context, force=force, path=path) for e in clause.args))


@compiler.register(BOp)
def on_bop(op, context, force=False, path=None):
    return "({} {} {})".format(compiler(op.left, context, force=force, path=path), op.op, compiler(op.right, context, force=force, path=path))


@compiler.register(PreOp)
def on_preop(op, context, force=False, path=None):
    return "({} {})".format(op.op, compiler(op.value, context, force=force, path=path))


@compiler.register(PostOp)
def on_postop(op, context, force=False, path=None):
    return "{} {}".format(compiler(op.value, context, force=force, path=path), op.op)


@compiler.register(TriOp)
def on_triop(op, context, force=False, path=None):
    return "({} {} {} {} {})".format(compiler(op.left, context, force=force, path=path),
                                     op.op,
                                     compiler(op.middle, context, force=force, path=path),
                                     op.op2,
                                     compiler(op.right, context, force=force, path=path))


@compiler.register(JoinOp)
def on_joinop(op, context, force=False, path=None):
    r = []
    r.append(compiler(op.left, context, force=force, path=path))
    r.append(op.op)
    r.append(compiler(op.right, context, force=force, path=path))
    for e in op.args:
        r.append("ON {}".format(compiler(e, context, force=force, path=path)))
    return " ".join(r)


@compiler.register(QueryRecord)
def on_query_record(record, context, force=False, path=None):
    name = record.get_name()
    if name:
        path = path or []
        path.append(name)
        value = "({}) as {}".format(compiler(record.query, context, force=force, path=path), name)
        path.pop()
    else:
        value = "({})".format(compiler(record.query, context, force=force, path=path))
    return value


@compiler.register(RecordMeta)
def on_record(record, context, force=False, path=None):
    return record.get_name()


@compiler.register(AliasRecord)
def on_alias_record(record, context, force=False, path=None):
    return "{} as {}".format(compiler(record._core, context, force=force, path=path), record.get_name())


@compiler.register(ConcreteProperty)
def on_property(prop, context, force=False, path=None):
    return "{}.{}".format(prop.record.get_name(), prop.name)


@compiler.register(_SubSelectProperty)
def on_subselect_property(prop, context, force=False, path=None):
    column_name = compiler(prop.prop, context, force=force, path=path)
    return "{} as {}".format(column_name, prop.projection_name)

@compiler.register(AliasProperty)
def on_alias_property(prop, context, force=False, path=None):
    return "{} as {}".format(compiler(prop.prop, context, force=force, path=path), prop.name)


# xxx:
@compiler.register(AliasExpressionProperty)
def on_alias_expression_property(prop, context, force=False, path=None):
    return "({})".format(compiler(prop.record._parent.query, context, force=force, path=path))


@compiler.register(Prepared)
def on_prepared(v, context, force=False, path=None):
    if not path:
        context[ARGS].append(context[v.key])
        return "%s"
    else:
        path.append(v.key)
        k = ".".join(path)
        context[ARGS].append(context[k])  # side-effect!
        return "%s"


@compiler.register(List)  # list is not python's list
def on_list(v, context, force=False, path=None):
    v = v.value
    r = []
    for e in v:
        if isinstance(e, Expr):
            r.append(compiler(e, context, force=force, path=path))
        else:
            r.append(compiler(Value(e), context, force=force, path=path))
    return ", ".join(r)


@compiler.register(Constant)
def on_constant(v, context, force=False, path=None):
    return v.expr or v.value


@compiler.register(Function)
def on_function(v, context, force=False, path=None):
    return "{}({})".format(v.value, ", ".join(compiler(e, context, force=force, path=path) for e in v.args))


@compiler.register(Value)
def on_value(v, context, force=False, path=None):
    v = v.value
    if v is None:
        return "NULL"
    elif isinstance(v, (list, tuple)):
        r = []
        for e in v:
            if isinstance(e, Expr):
                r.append(compiler(e, context, force=force, path=path))
            else:
                r.append(compiler(Value(e), context, force=force, path=path))
        return "({})".format(", ".join(r))
    elif isinstance(v, str):
        return "'{}'".format(v)
    elif isinstance(v, bool):
        return "{}".format(int(v))
    else:
        return convert(v)


@singledispatch
def convert(v):
    return str(v)


@convert.register(date)
def on_date(v):
    return v.strftime("'%Y-%m-%d'")


@convert.register(datetime)
def on_datetime(v):
    return v.strftime("'%Y-%m-%d %H:%M:%S'")


@convert.register(time)
def on_time(v):
    return v.strftime("'%H:%M:%S'")
