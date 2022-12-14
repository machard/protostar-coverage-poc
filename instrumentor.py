import textwrap
from starkware.cairo.lang.compiler.ast.code_elements import CodeElementHint, CodeElementFunction, CommentedCodeElement, CodeBlock
from starkware.cairo.lang.compiler.ast.expr import (
    ExprHint,
)
from starkware.cairo.lang.compiler.ast.visitor import Visitor


class Instrumentor(Visitor):
    """
    Instrument functions with tracking code.
    """

    def __init__(self, total_functions: int, total_statements: int):
        super().__init__()
        self.total_functions = total_functions
        self.total_statements = total_statements

    def _visit_default(self, obj):
        return obj

    def visit_CodeElementFunction(self, elm: CodeElementFunction):
        need_instrumentation = any(decorator.name not in [
                                   "storage_var"] for decorator in elm.decorators) and elm.element_type not in ['struct', 'namespace']

        if not need_instrumentation:
            return

        elm.code_block.code_elements.insert(
            0,
            CommentedCodeElement(
                comment="",
                code_elm=CodeElementHint(
                    hint=ExprHint(
                        hint_code=textwrap.dedent(f'''\
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
                            context.COVERAGE["functions"]["{elm.name + "@" + str(elm.code_block.code_elements[0].location)}"] = True
                        '''),
                        n_prefix_newlines=4
                    )
                )
            ),
        )

        return super().visit_CodeElementFunction(elm)

    def visit_CodeBlock(self, elm: CodeBlock):
        # we don't do top level
        if len(self.parents) <= 1:
            return super().visit_CodeBlock(elm)

        total_elements = len(elm.code_elements)

        for i in range(total_elements - 1, -1, -1):
            if isinstance(elm.code_elements[i].code_elm, CodeElementHint):
                continue

            elm.code_elements.insert(
                i,
                CommentedCodeElement(
                    comment="",
                    code_elm=CodeElementHint(
                        hint=ExprHint(
                            hint_code=textwrap.dedent(f'''\
                                    context.COVERAGE["statements"]["{elm.code_elements[i].location}"] = True
                            '''),
                            n_prefix_newlines=4
                        )
                    )
                )
            )

        return super().visit_CodeBlock(elm)
