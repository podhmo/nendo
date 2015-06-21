# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from .query import Query
from .clause import Clause
from .condition import BOp, PreOp, PostOp, TriOp
from .record import RecordMeta, As
from .property import ConcreteProperty


@singledispatch
def compiler(v, context):
    raise NotImplementedError(v)


@compiler.register(Query)
def on_query(query, context):
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
    return "{} {}".format(clause.name, ", ".join(compiler(e, context) for e in clause.args))


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


@compiler.register(RecordMeta)
def on_record(record, context):
    return record.get_name()


@compiler.register(As)
def on_alias(ob, context):
    return "(({}) as {})".format(compiler(ob.core, context), ob.name)


@compiler.register(ConcreteProperty)
def on_property(prop, context):
    return "{}.{}".format(prop.record.get_name(), prop.name)
