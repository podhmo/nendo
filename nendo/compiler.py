# -*- coding:utf-8 -*-
from singledispatch import singledispatch
from datetime import date, datetime, time
from .query import Query, _QueryFrom, _QueryProperty
from .clause import Clause, _SubSelectProperty
from .expr import BOp, PreOp, PostOp, TriOp, JoinOp, Expr
from .record import RecordMeta
from .property import ConcreteProperty
from .alias import AliasRecord, AliasProperty, AliasExpressionProperty, QueryRecord
from .value import Value, Prepared, List, Constant, Function
from .options import Options


ARGS = "__i_args"  # xxx: this is the keyname of stored arguments
DEFAULT_OPTIONS = Options(use_validation=True, one_table=False, one_line_sql=True)


@singledispatch
def compiler(v, context, options=None, path=None):
    raise NotImplementedError(v)


@compiler.register(Query)
def on_query(query, context, options=None, path=None):
    options = options or DEFAULT_OPTIONS
    if ARGS not in context:
        context[ARGS] = []

    path = path or []
    if options.use_validation:
        query.validate(context)

    r = []

    if query._select.is_empty():
        r.append("SELECT")
        columns = []
        for p in query.props():
            columns.append(compiler(p, context, options=options, path=path))
        r.append(", ".join(columns))
    else:
        r.append(compiler(query._select, context, options=options, path=path))

    if not query._from.is_empty():
        r.append(compiler(query._from, context, options=options, path=path))

    if not query._where.is_empty():
        r.append(compiler(query._where, context, options=options, path=path))
    if not query._group_by.is_empty():
        r.append(compiler(query._group_by, context, options=options, path=path))
    if not query._order_by.is_empty():
        r.append(compiler(query._order_by, context, options=options, path=path))
    if not query._having.is_empty():
        r.append(compiler(query._having, context, options=options, path=path))
    if not query._limit.is_empty():
        r.append(compiler(query._limit, context, options=options, path=path))

    if options.one_line_sql:
        return " ".join(r)
    else:
        return "\n".join(r)


@compiler.register(Clause)
def on_clause(clause, context, options=None, path=None):
    return "{} {}".format(clause.get_name(), ", ".join(compiler(e, context, options=options, path=path) for e in clause.args))


@compiler.register(_QueryFrom)
def on_union_from(clause, context, options=None, path=None):
    r = []
    for e in clause.args:
        r.append("{}".format(compiler(e, context, options=options, path=path)))
    return "{} ({}) as {}".format(clause.get_name(), " {} ".format(clause.separator).join(r), clause.args[0].get_name())


@compiler.register(BOp)
def on_bop(op, context, options=None, path=None):
    return "({} {} {})".format(compiler(op.left, context, options=options, path=path), op.op, compiler(op.right, context, options=options, path=path))


@compiler.register(PreOp)
def on_preop(op, context, options=None, path=None):
    return "({} {})".format(op.op, compiler(op.value, context, options=options, path=path))


@compiler.register(PostOp)
def on_postop(op, context, options=None, path=None):
    return "{} {}".format(compiler(op.value, context, options=options, path=path), op.op)


@compiler.register(TriOp)
def on_triop(op, context, options=None, path=None):
    return "({} {} {} {} {})".format(compiler(op.left, context, options=options, path=path),
                                     op.op,
                                     compiler(op.middle, context, options=options, path=path),
                                     op.op2,
                                     compiler(op.right, context, options=options, path=path))


@compiler.register(JoinOp)
def on_joinop(op, context, options=None, path=None):
    r = []
    r.append(compiler(op.left, context, options=options, path=path))
    r.append(op.op)
    r.append(compiler(op.right, context, options=options, path=path))
    for e in op.args:
        r.append("ON {}".format(compiler(e, context, options=options, path=path)))
    return " ".join(r)


@compiler.register(QueryRecord)
def on_query_record(record, context, options=None, path=None):
    name = record.get_name()
    if name:
        path = path or []
        path.append(name)
        value = "({}) as {}".format(compiler(record.query, context, options=options, path=path), name)
        path.pop()
    else:
        value = "({})".format(compiler(record.query, context, options=options, path=path))
    return value


@compiler.register(RecordMeta)
def on_record(record, context, options=None, path=None):
    return record.get_name()


@compiler.register(AliasRecord)
def on_alias_record(record, context, options=None, path=None):
    return "{} as {}".format(compiler(record._core, context, options=options, path=path), record.get_name())


@compiler.register(ConcreteProperty)
def on_property(prop, context, options=None, path=None):
    options = options or DEFAULT_OPTIONS
    if options.one_table:
        return prop.name
    else:
        return prop.full_name


@compiler.register(_QueryProperty)
def on_query_property(prop, context, options=None, path=None):
    return prop.full_name


@compiler.register(_SubSelectProperty)
def on_subselect_property(prop, context, options=None, path=None):
    column_name = compiler(prop.prop, context, options=options, path=path)
    return "{} as {}".format(column_name, prop.projection_name)


@compiler.register(AliasProperty)
def on_alias_property(prop, context, options=None, path=None):
    return "{} as {}".format(compiler(prop.prop, context, options=options, path=path), prop.name)


# xxx:
@compiler.register(AliasExpressionProperty)
def on_alias_expression_property(prop, context, options=None, path=None):
    return "({})".format(compiler(prop.record._parent.query, context, options=options, path=path))


@compiler.register(Prepared)
def on_prepared(v, context, options=None, path=None):
    if not path:
        context[ARGS].append(context[v.key])
        return "%s"
    else:
        path.append(v.key)
        k = ".".join(path)
        context[ARGS].append(context[k])  # side-effect!
        return "%s"


@compiler.register(List)  # list is not python's list
def on_list(v, context, options=None, path=None):
    v = v.value
    r = []
    for e in v:
        if isinstance(e, Expr):
            r.append(compiler(e, context, options=options, path=path))
        else:
            r.append(compiler(Value(e), context, options=options, path=path))
    return ", ".join(r)


@compiler.register(Constant)
def on_constant(v, context, options=None, path=None):
    return v.expr or v.value


@compiler.register(Function)
def on_function(v, context, options=None, path=None):
    return "{}({})".format(v.value, ", ".join(compiler(e, context, options=options, path=path) for e in v.args))


@compiler.register(Value)
def on_value(v, context, options=None, path=None):
    v = v.value
    if v is None:
        return "NULL"
    elif isinstance(v, (list, tuple)):
        r = []
        for e in v:
            if isinstance(e, Expr):
                r.append(compiler(e, context, options=options, path=path))
            else:
                r.append(compiler(Value(e), context, options=options, path=path))
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
