from .property import Property


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
