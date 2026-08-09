from itl.compiler.printer import ASTPrinter, GIRPrinter

from itl.compiler.compiler import Compiler

compiler = Compiler(
    "docs/examples/ecommerce"
)

app = compiler.compile()

printer = GIRPrinter()

printer.print(app)