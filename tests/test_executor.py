from pprint import pprint

from runompt import Parser, Executor


basic = """
= x "hello"
<< -= x "l"
<< x
""".strip("\n")


def test_basic():
    code = Parser().parse(basic)

    pprint(code)

    print("----execution----")

    executor = Executor()

    executor.execute(code)

test_basic()
