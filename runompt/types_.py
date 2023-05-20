# number, string
# #       $

# (#"1") == 1

from typing import Union


class BaseType:
    pass


class Number(BaseType):
    def __init__(self, value: int):
        self.value = value

    def display(self):
        return str(self.value)

    def do_add(self, other: Union["Number", int]) -> int:
        match other:
            case Number():
                return self.value + other.value
            case int():
                return self.value + other
            case _:
                raise TypeError(f"Cannot add number and {type(other)!r}")

    def do_sub(self, other: Union["Number", int]) -> int:
        match other:
            case Number():
                return self.value - other.value
            case int():
                return self.value - other
            case _:
                raise TypeError(f"Cannot subtract number from {type(other)!r}")

    def __repr__(self):
        return f"Number(value={self.value})"


class String(BaseType):
    def __init__(self, value: str):
        self.value = value

    def display(self) -> str:
        return self.value

    def do_add(self, other: Union["String", str]) -> str:
        match other:
            case String():
                return self.value + other.value
            case str():
                return self.value + other
            case _:
                raise TypeError(f"Cannot add string and {type(other)!r}")

    def do_sub(self, other: Union["String", str]) -> str:
        match other:
            case String():
                return self.value.replace(other.value, "")
            case str():
                return self.value.replace(other, "")
            case _:
                raise TypeError(f"Cannot subtract string from {type(other)!r}")

    def __repr__(self):
        return f"String(value={self.value})"
