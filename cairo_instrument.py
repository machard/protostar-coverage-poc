import argparse
import sys
import os
from typing import Callable

from starkware.cairo.lang.compiler.ast.module import CairoFile, CairoModule
from starkware.cairo.lang.compiler.parser import parse_file
from starkware.cairo.lang.version import __version__

from counter import Counter
from instrumentor import Instrumentor


def cairo_instrument_common(cairo_parser: Callable[[str, str], CairoFile], description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("files", metavar="file", type=str,
                        nargs="+", help="File names")

    args = parser.parse_args()

    for path in args.files:
        old_content = open(path).read()
        dirpath, filename = os.path.split(path)
        newfilename = "instrumented_" + filename
        newpath = os.path.join(dirpath, newfilename)

        try:
            module = CairoModule(
                cairo_file=cairo_parser(old_content, filename),
                module_name=path,
            )

            # instrument logic goes here
            counter = Counter()
            counter.visit(module)

            instrumentor = Instrumentor(
                total_functions=counter.total_functions,
                total_statements=counter.total_statements
            )
            instrumentor.visit(module)

            new_content = module.format()
        except Exception as exc:
            print(exc, file=sys.stderr)
            return 2

        open(newpath, "w").write(new_content)

    return 0


def main():
    def cairo_parser(code, filename): return parse_file(
        code=code, filename=filename)

    return cairo_instrument_common(
        cairo_parser=cairo_parser, description="A tool to automatically instrument Cairo code."
    )


if __name__ == "__main__":
    sys.exit(main())
