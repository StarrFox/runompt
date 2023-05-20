"""
execution page:
           function args...
           function args...
(label)    :label
(function) -> label

(arg, arg) name
    | multiline
    | miltiline
    return implicit

function is actually just a label and calls are goto
the difference is that the args are set

do we preserve variable scope from outside? yes

= x 1
(x) modify 2
modify 3
<< x

is x 1 or 3? it is 1

: is label
~ is overwrite
= is set var
:= is set var expressioned
-> is goto
[] is function define
<< is print
>> is input
== and it's friends for comparison

:start = x 20
\1~start += x 20
(q, w) add + q w
== x 20 -> 0
<< add x x
"""

from typing import TypeAlias, Union

from .parser import Code, Parameter, FunctionCall
from .types_ import Number, String
from .constructs import Literal, Variable


Settable: TypeAlias = Union[Number, int, String, str]


class Scope:
    def __init__(self):
        self.variables: dict[str, int | str] = {}

    def set(self, name: str, value: Settable):
        match value:
            case Number() | String():
                self.variables[name] = value.value
            case int() | str():
                self.variables[name] = value
            case _:
                raise NotImplementedError("Setting to that type hasn't been added")

    def get(self, name: str) -> int | str:
        return self.variables[name]


class Executor:
    def __init__(self):
        self.global_scope = Scope()

    def set_variable(self, variable: Variable, value: Parameter):
        match value:
            case Literal():
                self.global_scope.set(variable.name, value.value)
            case Variable():
                self.global_scope.set(
                    variable.name,
                    self.global_scope.get(value.name)
                )
            case FunctionCall():
                result = self.execute_function(value)
                self.global_scope.set(variable.name, result)
            case _:
                raise NotImplementedError("Assigning to that hasn't been added")

    def stream_out(self, value: Variable | Literal | FunctionCall):
        match value:
            case Variable():
                print(self.global_scope.get(value.name))
            case Literal():
                print(value.value.display())
            case FunctionCall():
                print(self.execute_function(value))
            case _:
                raise NotImplementedError("Streaming that hasn't been added yet")

    def do_add(self, param_a: Variable | Literal, param_b: Union[Variable, Literal, FunctionCall]):
        match param_a:
            case Variable():
                match param_b:
                    case Variable():
                        a = self.global_scope.get(param_a.name)
                        b = self.global_scope.get(param_b.name)

                        if not isinstance(a, type(b)):
                            raise SyntaxError("Variables must be the same type to be added")

                        return a + b
                    case Literal():
                        a = self.global_scope.get(param_a.name)

                        return param_b.value.do_add(a)
                    case FunctionCall():
                        # the right hand function needs to be executed first
                        b = self.execute_function(param_b)
                        a = self.global_scope.get(param_a.name)

                        if not isinstance(a, type(b)):
                            raise SyntaxError("Variables must be the same type to be added")

                        return a + b
                    case _:
                        raise SyntaxError(f"Cannot add variable to {type(param_b)!r}")

            case Literal():
                match param_b:
                    case Literal():
                        return param_a.value.do_add(param_b.value)
                    case Variable():
                        b = self.global_scope.get(param_b.name)

                        return param_a.value.do_add(b)
                    case _:
                        raise SyntaxError(f"Cannot add literal to {type(param_b)!r}")

    def do_sub(self, param_a: Variable | Literal, param_b: Union[Variable, Literal, FunctionCall]):
        match param_a:
            case Variable():
                match param_b:
                    case Variable():
                        a = self.global_scope.get(param_a.name)
                        b = self.global_scope.get(param_b.name)

                        if not isinstance(a, type(b)):
                            raise SyntaxError("Variables must be the same type to be subtracted")

                        return a - b
                    case Literal():
                        a = self.global_scope.get(param_a.name)

                        match a:
                            case int():
                                return param_b.value.do_sub(a)
                            case str():
                                return String(a).do_sub(param_b.value)
                            case _:
                                raise NotImplementedError(f"{type(a)} literal sub hasn't been added")
                    case FunctionCall():
                        # the right hand function needs to be executed first
                        b = self.execute_function(param_b)
                        a = self.global_scope.get(param_a.name)

                        if not isinstance(a, type(b)):
                            raise SyntaxError("Variables must be the same type to be subtracted")

                        return a - b
                    case _:
                        raise SyntaxError(f"Cannot subtract variable from {type(param_b)!r}")

            case Literal():
                match param_b:
                    case Literal():
                        return param_a.value.do_sub(param_b.value)
                    case Variable():
                        b = self.global_scope.get(param_b.name)

                        return param_a.value.do_sub(b)
                    case _:
                        raise SyntaxError(f"Cannot add literal to {type(param_b)!r}")

    def do_add_set(self, variable: Variable, to_add: Union[Variable, Literal, FunctionCall]):
        added = self.do_add(variable, to_add)
        self.global_scope.set(variable.name, added)
        return added

    def do_sub_set(self, variable: Variable, to_sub: Union[Variable, Literal, FunctionCall]):
        subbed = self.do_sub(variable, to_sub)
        self.global_scope.set(variable.name, subbed)
        return subbed

    def execute_function(self, function_call: FunctionCall):
        match function_call.function.name:
            case "=":
                return self.set_variable(*function_call.parameters)
            case "<<":
                return self.stream_out(*function_call.parameters)
            case "+":
                return self.do_add(*function_call.parameters)
            case "+=":
                return self.do_add_set(*function_call.parameters)
            case "-":
                return self.do_sub(*function_call.parameters)
            case "-=":
                return self.do_sub_set(*function_call.parameters)

    def execute(self, code: Code):
        for function_call in code.lines:
            self.execute_function(function_call)
