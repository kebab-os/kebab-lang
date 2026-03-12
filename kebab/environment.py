"""Runtime environment (variable scopes) for the kebab interpreter."""


class Environment:
    """A scoped variable store. Child scopes can read/write parent scopes."""

    def __init__(self, parent=None):
        self._values: dict = {}
        self._parent = parent

    def define(self, name: str, value):
        """Bind a new name in the current scope."""
        self._values[name] = value

    def get(self, name: str, line: int):
        if name in self._values:
            return self._values[name]
        if self._parent is not None:
            return self._parent.get(name, line)
        from .interpreter import RuntimeError as KebabRuntimeError
        raise KebabRuntimeError(f"undefined variable '{name}'", line)

    def assign(self, name: str, value, line: int):
        if name in self._values:
            self._values[name] = value
            return
        if self._parent is not None:
            self._parent.assign(name, value, line)
            return
        from .interpreter import RuntimeError as KebabRuntimeError
        raise KebabRuntimeError(f"undefined variable '{name}'", line)
