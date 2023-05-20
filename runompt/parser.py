"""
entry =
    = x 2
    << x

parse(entry) -> Code
    Code:
        .lines:
            Function(=) Argument(x) Argument(2)
            Function(<<) Argument(x)
        .info:
            variables [x(Number)] defined? yes
            functions [<<(Number.display) =] defined? yes
            constants [2(Number)] defined? yes
            replaces ... (~ function)
vm.execute(Code)
    ...
"""
from dataclasses import dataclass
from typing import Generator, Union, TypeAlias

from .constructs import Function, Variable, Literal, Argument
from .types_ import Number, String


builtins = {
    "=": Function("=", [Argument("to_set"), Argument("set_to")]),
    "<<": Function("<<", [Argument("to_stream")]),
    "+": Function("+", [Argument("to_add_a"), Argument("to_add_b")]),
    "+=": Function("+=", [Argument("var"), Argument("to_add")]),
    "-": Function("-", [Argument("to_sub_a"), Argument("to_sub_b")]),
    "-=": Function("-=", [Argument("var"), Argument("to_sub")]),
}


StringGen: TypeAlias = Generator[str, None, None]
Parameter: TypeAlias = Union["FunctionCall", Literal, Variable]


def _split_space(entry: str) -> StringGen:
    last = 0
    for idx, char in enumerate(entry):
        if char == " ":
            yield entry[last:idx]
            # skip over the space
            last = idx + 1

    yield entry[last:]


@dataclass
class FunctionCall:
    function: Function
    parameters: list[Parameter]


@dataclass
class Code:
    lines: list[FunctionCall]


class Parser:
    def __init__(self):
        # function name: Function
        self.functions: dict[str, Function] = {}
        self.variables: dict[str, Variable] = {}

    def get_function_named(self, name: str) -> Function:
        try:
            return builtins[name]
        except KeyError:
            try:
                return self.functions[name]
            except KeyError:
                raise SyntaxError(f"Function {name} is not defined") from None

    def get_variable_named(self, name: str) -> Variable:
        try:
            return self.variables[name]
        except KeyError:
            raise SyntaxError(f"Variable {name} is not defined") from None

    def get_identifier_named(self, name: str) -> Function | Variable:
        try:
            return self.get_function_named(name)
        except SyntaxError:
            try:
                return self.get_variable_named(name)
            except KeyError:
                raise SyntaxError(f"{name} is not defined") from None

    @staticmethod
    def resolve_literal(entry: str, rest: StringGen) -> Literal:
        if entry.isnumeric():
            return Literal(Number(int(entry)))

        if entry.startswith("\""):
            if entry.endswith("\""):
                return Literal(String(entry.strip("\"")))

            for str_continue in rest:
                entry += " " + str_continue

                if str_continue.endswith("\""):
                    return Literal(String(entry.strip("\"")))

        raise SyntaxError(f"{entry} is not a literal")

    def resolve_parameter(
            self,
            argument: Argument,
            entry: str,
            rest: StringGen,
    ) -> Parameter:
        try:
            return self.get_variable_named(entry)
        except SyntaxError:
            pass

        try:
            function = self.get_function_named(entry)
            return self.resolve_function(function, rest)
        except SyntaxError:
            pass

        return self.resolve_literal(entry, rest)

    def resolve_set_variable(self, function: Function, rest: StringGen) -> FunctionCall:
        variable_name = next(rest)
        variable = Variable(variable_name)

        self.variables[variable_name] = variable

        entry = next(rest)
        set_to = self.resolve_parameter(function.arguments[1], entry, rest)

        return FunctionCall(function, [variable, set_to])

    def resolve_function(
            self,
            function: Function,
            rest: StringGen,
    ) -> FunctionCall:
        parameters: list[Parameter] = []
        if function.name == "=":
            return self.resolve_set_variable(function, rest)

        for argument in function.arguments:
            entry = next(rest)
            parameters.append(self.resolve_parameter(argument, entry, rest))

        return FunctionCall(function, parameters)

    def parse(self, entry: str) -> Code:
        code = Code([])

        for line in entry.split("\n"):
            tokens = _split_space(line)

            function = self.get_function_named(next(tokens))
            code.lines.append(self.resolve_function(function, tokens))

        return code
