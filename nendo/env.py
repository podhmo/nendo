# -*- coding:utf-8 -*-
class Env(object):
    def __init__(self, env=None):
        self.env = env or {}
        assert isinstance(self.env, dict)

    def make(self):
        return self.__class__(env=self.env.copy())

    def merge(self, *targets):
        for t in targets:
            if hasattr(t, "env"):
                for k, v in t.env.items():
                    self.env[k] = v
