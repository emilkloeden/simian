from __future__ import annotations
import simian.objects as objects

__all__ = ["new_environment", "new_enclosed_environment", "Environment"]


class Environment:
    def __init__(self, store, outer: Environment):
        self.store = store
        self.outer = outer

    def get(self, name: str) -> objects.Object:
        obj = self.store.get(name, None)

        if obj is None and self.outer is None:
            return None

        if obj is None and self.outer is not None:
            return self.outer.get(name)

        elif obj is not None:
            return obj
        else:
            return None

    def set(self, name: str, val: objects.Object) -> objects.Object:
        self.store[name] = val
        return val

    def exported_hash(self) -> objects.Hash:
        pairs = {}
        for k, v in self.store.items():
            s = objects.String(k)
            pairs[s.hash_key()] = objects.HashPair(s, v)
        return objects.Hash(pairs)


def new_environment() -> Environment:
    return Environment({}, None)


def new_enclosed_environment(outer: Environment) -> Environment:
    env = new_environment()
    env.outer = outer
    return env
