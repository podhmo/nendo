from . import condition as c


class Value(c.Expr):
    """constant value"""
    def __init__(self, value):
        super(Value, self).__init__()
        self.value = value

    def __repr__(self):
        return "<V: {}>".format(self.value)


class Prepared(Value):
    """using for prepared statement"""
    def __init__(self, value):
        self.value = value
        super(Value, self).__init__(env={value: self})

    @property
    def key(self):
        return self.value

    def __repr__(self):
        return "<pV: {}>".format(self.value)
