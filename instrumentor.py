from tokenize import Number
from starkware.cairo.lang.compiler.ast.code_elements import CodeElementHint, CodeElementFunction, CommentedCodeElement, CodeBlock
from starkware.cairo.lang.compiler.ast.expr import (
    ExprHint,
)
from starkware.cairo.lang.compiler.ast.visitor import Visitor


class Instrumentor(Visitor):
    """
    Instrument functions with tracking code.
    """

    def __init__(self, total_functions: int, total_statements: Number):
        super().__init__()
        self.total_functions = total_functions
        self.total_statements = total_statements

    def _visit_default(self, obj):
        return obj

    def visit_CodeBlock(self, elm: CodeBlock):
        # we don't do top level
        if len(self.parents) <= 1:
            return super().visit_CodeBlock(elm)

        total_elements = len(elm.code_elements)

        for i in range(total_elements - 1, -1, -1):
            if i > 0:
                code = f'''
                    fi = getframeinfo(currentframe())
                    context.COVERAGE["statements"][fi.filename + \
                        "_" + str(fi.lineno)] = True
                '''
            else:
                code = f'''
                    from inspect import currentframe, getframeinfo
                    try:
                        # context is immutable, allows to only set it up once
                        context.COVERAGE = {{
                            "functions": {{}},
                            "statements": {{}},
                            "total_functions": {self.total_functions},
                            "total_statements": {self.total_statements}
                        }}
                    except:
                        pass
                    fi = getframeinfo(currentframe())
                    context.COVERAGE["functions"][fi.filename + \
                        "_" + "increase_balance"] = True
                    context.COVERAGE["statements"][fi.filename + \
                        "_" + str(fi.lineno)] = True,
                '''

            elm.code_elements.insert(
                i,
                CommentedCodeElement(
                    comment="",
                    code_elm=CodeElementHint(
                        hint=ExprHint(
                            hint_code=code,
                            n_prefix_newlines=4
                        )
                    )
                )
            )

        return super().visit_CodeBlock(elm)
