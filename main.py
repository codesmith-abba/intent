from itl.compiler.printer import ASTPrinter

from itl.compiler.compiler import Compiler

compiler = Compiler(
    "docs/examples/ecommerce"
)

app = compiler.compile()

printer = ASTPrinter()

printer.print(app)