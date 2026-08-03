from dataclasses import fields, is_dataclass


class ASTPrinter:

    INDENT = "    "

    def print(self, node):

        self.visit(node)

    def visit(self, node, level=0):

        indent = self.INDENT * level

        if node is None:
            return

        if is_dataclass(node):

            print(f"{indent}{type(node).__name__}")

            for field in fields(node):

                value = getattr(node, field.name)

                self.visit_field(
                    field.name,
                    value,
                    level + 1,
                )

            return

        print(f"{indent}{node}")
    
    def visit_field(
        self,
        name,
        value,
        level,
    ):

        indent = self.INDENT * level

        if value is None:
            return

        if isinstance(value, list):

            print(f"{indent}{name}")

            for item in value:

                self.visit(item, level + 1)

            return

        if is_dataclass(value):

            print(f"{indent}{name}")

            self.visit(value, level + 1)

            return

        print(f"{indent}{name}: {value}")