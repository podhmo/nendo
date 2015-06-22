# -*- coding:utf-8 -*-
class Env(object):
    def __init__(self, env=None):
        self.env = env or {}
        assert isinstance(self.env, dict)

    def make(self):
        return self.__class__(env=self.env.copy())

    def merge(self, *targets):
        for t in targets:
            # broken?
            while hasattr(t, "env"):
                t = t.env
            if hasattr(t, "items"):
                for k, v in t.items():
                    self.env[k] = v
