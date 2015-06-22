# -*- coding:utf-8 -*-
from .langhelpers import as_python_code
from . import expr


class RecordMeta(type):
    pass


RecordBase = RecordMeta("RecordBase", (), {})


class Record(RecordBase):
    @classmethod
    def get_name(cls):
        return getattr(cls, "_name", None) or cls.__name__

    @classmethod
    def tables(cls):
        yield cls

    @classmethod
    def join(cls, other, *args):
        return expr.Join(cls, other, args)

    @classmethod
    def left_outer_join(cls, other, *args):
        return expr.LeftOuterJoin(cls, other, args)

    @classmethod
    def right_outer_join(cls, other, *args):
        return expr.RightOuterJoin(cls, other, args)

    @classmethod
    def cross_join(cls, other, *args):
        return expr.CrossJoin(cls, other, args)


@as_python_code
def make_record(m, clsname, template, name=None):
    """
    >>> make_record("Foo",  "x, y, z")
    """
    from nendo.record import Record
    from nendo.property import NamedProperty
    m.env["Record"] = Record
    m.env["NamedProperty"] = NamedProperty

    attrs = [x.strip() for x in template.replace(",", "").split(" ") if x != ""]
    with m.class_(clsname, "Record"):
        if attrs:
            with m.method("__init__", ", ".join(attrs)):
                for attr in attrs:
                    fmt = "self._{attr} = {attr}"
                    m.stmt(fmt.format(attr=attr))
        for attr in attrs:
            m.stmt("{attr} = NamedProperty({attr!r})".format(attr=attr))

        if name is not None:
            m.stmt("_name = {!r}".format(name))
