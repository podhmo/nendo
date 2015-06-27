# -*- coding:utf-8 -*-
class ValidationError(Exception):
    pass


class ConflictName(ValidationError):
    pass


class MissingName(ValidationError):
    pass


class InvalidCombination(ValidationError):
    pass
