# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .query import Query
from .clause import Clause, SubSelect
from .expr import BOp, PreOp, PostOp, TriOp
from .record import RecordMeta
from .property import ConcreteProperty
from .alias import AliasRecord, AliasProperty, QueryRecord
from .value import Value


@singledispatch
def compiler(v, context):
    raise NotImplementedError(v)


@compiler.register(Query)
def on_query(query, context):
    query.validate(context)

    r = []
    if query._select.is_empty():
        r.append("SELECT *")
    else:
        r.append(compiler(query._select, context))
    if not query._from.is_empty():
        r.append(compiler(query._from, context))
    if not query._where.is_empty():
        r.append(compiler(query._where, context))
    if not query._having.is_empty():
        r.append(compiler(query._having, context))
    return " ".join(r)


@compiler.register(Clause)
def on_clause(clause, context):
    return "{} {}".format(clause.get_name(), ", ".join(compiler(e, context) for e in clause.args))


@compiler.register(SubSelect)
def on_swap_select(clause, context):
    args = []
    for e in clause.args:
        column_name = compiler(e, context)
        args.append("{} as {}".format(column_name, column_name.replace(".", "_")))
    return "{} {}".format(clause.get_name(), ", ".join(args))


@compiler.register(BOp)
def on_bop(op, context):
    return "({} {} {})".format(compiler(op.left, context), op.op, compiler(op.right, context))


@compiler.register(PreOp)
def on_preop(op, context):
    return "({} {})".format(op.op, compiler(op.value, context))


@compiler.register(PostOp)
def on_postop(op, context):
    return "({} {})".format(compiler(op.value, context), op.op)


@compiler.register(TriOp)
def on_triop(op, context):
    r = []
    r.append(compiler(op.left, context))
    r.append(op.op)
    r.append(compiler(op.right, context))
    for e in op.args:
        r.append("ON {}".format(compiler(e, context)))
    return " ".join(r)


@compiler.register(QueryRecord)
def on_query_record(record, context):
    return "({}) as {}".format(
        compiler(record.query, context),
        record.get_name()
    )


@compiler.register(RecordMeta)
def on_record(record, context):
    return record.get_name()


@compiler.register(AliasRecord)
def on_alias_record(record, context):
    return record.get_name()


@compiler.register(ConcreteProperty)
def on_property(prop, context):
    return "{}.{}".format(prop.record.get_name(), prop.name)


@compiler.register(AliasProperty)
def on_alias_property(prop, context):
    return "{} as {}".format(compiler(prop.prop, context), prop.name)


@compiler.register(Value)
def on_value(v, context):
    v = v.value
    if v is None:
        return "NULL"
    elif isinstance(v, str):
        return "'{}'".format(v)
    elif isinstance(v, bool):
        return "{}".format(int(v))
    else:
        return str(v)
    raise NotImplementedError(v)
