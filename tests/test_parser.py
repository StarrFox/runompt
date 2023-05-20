from pprint import pprint

from runompt import Parser


basic = """
= x 1
<< x
+ 1 1
+ x 1
""".strip("\n")


def test_basic():
    code = Parser().parse(basic)
    pprint(code.lines)

test_basic()
