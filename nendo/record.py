# -*- coding:utf-8 -*-
from .langhelpers import as_python_code
from . import condition as c


class As(object):
    def __init__(self, core, name):
        self.name = name
        self.core = core

    def get_name(self):
        return self.name

    def __getattr__(self, k):
        return getattr(self.core, k)


class RecordMeta(type):
    pass


class Record(RecordMeta("RecordBase", (), {})):
    @classmethod
    def get_name(cls):
        return getattr(cls, "tablename", None) or cls.__name__

    @classmethod
    def join(cls, other, *args):
        return c.Join(cls, other, args)

    @classmethod
    def left_outer_join(cls, other, *args):
        return c.LeftOuterJoin(cls, other, args)

    @classmethod
    def right_outer_join(cls, other, *args):
        return c.RightOuterJoin(cls, other, args)

    @classmethod
    def cross_join(cls, other, *args):
        return c.CrossJoin(cls, other, args)


@as_python_code
def make_record(m, name, template):
    """
    >>> make_record("Foo",  "x, y, z")
    """
    from nendo.record import Record
    from nendo.property import NamedProperty
    m.env["Record"] = Record
    m.env["NamedProperty"] = NamedProperty

    names = [x.strip() for x in template.replace(",", "").split(" ") if x != ""]
    with m.class_(name, "Record"):
        if names:
            with m.method("__init__", ", ".join(names)):
                for name in names:
                    fmt = "self._{name} = {name}"
                    m.stmt(fmt.format(name=name))
        for name in names:
            m.stmt("{name} = NamedProperty({name!r})".format(name=name))
