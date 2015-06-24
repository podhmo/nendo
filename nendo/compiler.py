# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .query import Query
from .clause import Clause, SubSelect
from .expr import BOp, PreOp, PostOp, TriOp
from .record import RecordMeta
from .property import ConcreteProperty
from .alias import AliasRecord, AliasProperty, AliasExpressionProperty, QueryRecord
from .value import Value


@singledispatch
def compiler(v, context, force=False):
    raise NotImplementedError(v)


@compiler.register(Query)
def on_query(query, context, force=False):
    if not force:
        query.validate(context)

    r = []
    if query._select.is_empty():
        r.append("SELECT")
        columns = []
        for p in query.props():
            columns.append(compiler(p, context, force=force))
        r.append(", ".join(columns))
    else:
        r.append(compiler(query._select, context, force=force))
    if not query._from.is_empty():
        r.append(compiler(query._from, context, force=force))
    if not query._where.is_empty():
        r.append(compiler(query._where, context, force=force))
    if not query._order_by.is_empty():
        r.append(compiler(query._order_by, context, force=force))
    if not query._having.is_empty():
        r.append(compiler(query._having, context, force=force))
    if not query._limit.is_empty():
        r.append(compiler(query._limit, context, force=force))
    return " ".join(r)


@compiler.register(Clause)
def on_clause(clause, context, force=False):
    return "{} {}".format(clause.get_name(), ", ".join(compiler(e, context, force=force) for e in clause.args))


@compiler.register(SubSelect)
def on_swap_select(clause, context, force=False):
    args = []
    for e in clause.args:
        column_name = compiler(e, context, force=force)
        args.append("{} as {}".format(column_name, e.projection_name))
    return "{} {}".format(clause.get_name(), ", ".join(args))


@compiler.register(BOp)
def on_bop(op, context, force=False):
    return "({} {} {})".format(compiler(op.left, context, force=force), op.op, compiler(op.right, context, force=force))


@compiler.register(PreOp)
def on_preop(op, context, force=False):
    return "({} {})".format(op.op, compiler(op.value, context, force=force))


@compiler.register(PostOp)
def on_postop(op, context, force=False):
    return "{} {}".format(compiler(op.value, context, force=force), op.op)


@compiler.register(TriOp)
def on_triop(op, context, force=False):
    r = []
    r.append(compiler(op.left, context, force=force))
    r.append(op.op)
    r.append(compiler(op.right, context, force=force))
    for e in op.args:
        r.append("ON {}".format(compiler(e, context, force=force)))
    return " ".join(r)


@compiler.register(QueryRecord)
def on_query_record(record, context, force=False):
    return "({}) as {}".format(
        compiler(record.query, context, force=force),
        record.get_name()
    )


@compiler.register(RecordMeta)
def on_record(record, context, force=False):
    return record.get_name()


@compiler.register(AliasRecord)
def on_alias_record(record, context, force=False):
    return "{} as {}".format(compiler(record._core, context, force=force), record.get_name())


@compiler.register(ConcreteProperty)
def on_property(prop, context, force=False):
    return "{}.{}".format(prop.record.get_name(), prop.name)


@compiler.register(AliasProperty)
def on_alias_property(prop, context, force=False):
    return "{} as {}".format(compiler(prop.prop, context, force=force), prop.name)


# xxx:
@compiler.register(AliasExpressionProperty)
def on_alias_expression_property(prop, context, force=False):
    return "({})".format(compiler(prop.record._parent.query, context, force=force))


@compiler.register(Value)
def on_value(v, context, force=False):
    v = v.value
    if v is None:
        return "NULL"
    elif isinstance(v, (list, tuple)):
        r = []
        for e in v:
            if isinstance(e, Value):
                r.append(compiler(e, context, force=force))
            else:
                r.append(compiler(Value(e), context, force=force))
        return "({})".format(", ".join(r))
    elif isinstance(v, str):
        return "'{}'".format(v)
    elif isinstance(v, bool):
        return "{}".format(int(v))
    else:
        return str(v)
    raise NotImplementedError(v)
