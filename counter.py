from starkware.cairo.lang.compiler.ast.visitor import Visitor
from starkware.cairo.lang.compiler.ast.code_elements import CodeElementFunction, CodeBlock, CodeElementHint


class Counter(Visitor):
    """
    counts functions and code elements.
    """

    def __init__(self):
        super().__init__()
        self.total_functions = 0
        self.total_statements = 0

    def _visit_default(self, obj):
        pass

    def visit_CodeBlock(self, elm: CodeBlock):
        # we don't want to catch top level code elements since we can't instrument them with hints anyway
        if len(self.parents) > 1:
            self.total_statements += len(
                [x for x in elm.code_elements if not isinstance(x.code_elm, CodeElementHint)])

        super().visit_CodeBlock(elm)

    def visit_CodeElementFunction(self, elm: CodeElementFunction):
        # we remove the one we can't instrument
        need_instrumentation = any(decorator.name not in [
                                   "storage_var"] for decorator in elm.decorators) and elm.element_type not in ['struct', 'namespace']

        if not need_instrumentation:
            return

        self.total_functions += 1

        super().visit_CodeElementFunction(elm)
