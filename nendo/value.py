from functools import partial
from .property import Property
from .langhelpers import reify


class FakeRecord(object):
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def is_table(self):
        return False


class Constant(object):
    def __init__(self, value, expr=None):
        self.value = value
        self.expr = expr

    def tables(self):
        return []

    def props(self):
        return []


class Function(object):
    def __init__(self, value, *args):
        self.value = value
        self.args = args

    def tables(self):
        return []

    def props(self):
        return []

    @reify
    def record(self):
        return FakeRecord(self.value)

    @property
    def name(self):
        return self.value

    @reify
    def _key(self):
        return "_{}".format(self.name)


class Value(Property):
    """constant value"""
    def __init__(self, value, env=None):
        super().__init__(env=env)
        self.value = value

    def __repr__(self):
        return "<V: {}>".format(self.value)

    def tables(self):
        return []

    def props(self):
        return []


class List(Value):
    pass


class Prepared(Value):
    """using for prepared statement"""
    def __init__(self, value):
        self.value = value
        super().__init__(value, env={value: self})

    @property
    def key(self):
        return self.value

    def __repr__(self):
        return "<pV: {}>".format(self.value)


NULL = Constant("NULL")
STAR = ALL = Constant("*")


class FunctionPool(object):
    def __getattr__(self, k):
        v = partial(Function, k)
        setattr(self, k, v)
        return v

fn = FunctionPool()
