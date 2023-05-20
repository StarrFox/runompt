from dataclasses import dataclass

from runompt.types_ import Number, String


class BaseConstruct:
    pass


@dataclass
class Label(BaseConstruct):
    name: str


@dataclass
class Argument(BaseConstruct):
    name: str


@dataclass
class Function(BaseConstruct):
    name: str
    arguments: list[Argument]


@dataclass
class Variable(BaseConstruct):
    name: str


@dataclass
class Literal(BaseConstruct):
    value: Number | String
