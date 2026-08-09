from dataclasses import fields, is_dataclass
from itl.analyzer.analyzer import Analyzer

from itl.gir.models import (
    GIRApplication,
    GIRPage,
    GIRHero,
    GIRSection,
    GIRSystem,
)


class ASTPrinter:

    INDENT = "    "

    def print(self, node):

        self.analyzer = Analyzer()

        self.analyzer.analyze(node)

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


class GIRPrinter:

    def __init__(self):

        self.indent = 0

    def print(self, node):

        self.visit(node)

    def visit(self, node):

        if node is None:
            return

        method = getattr(
            self,
            f"visit_{type(node).__name__}",
            self.generic_visit,
        )

        return method(node)

    def generic_visit(self, node):

        raise NotImplementedError(
            f"No printer for '{type(node).__name__}'."
        )

    # =====================================================
    # Helpers
    # =====================================================

    def line(self, text=""):

        print("    " * self.indent + text)

    def push(self):

        self.indent += 1

    def pop(self):

        self.indent -= 1

    # =====================================================
    # Application
    # =====================================================

    def visit_GIRApplication(self, app: GIRApplication):

        self.line("GIRApplication")

        self.push()

        self.line(f"name: {app.name}")
        self.line(f"target: {app.target}")

        if app.intent:
            self.line("intent:")
            self.push()

            for line in app.intent.splitlines():
                self.line(line)

            self.pop()

        if app.system:
            self.visit(app.system)

        if app.pages:

            self.line("pages")

            self.push()

            for page in app.pages:
                self.visit(page)

            self.pop()

        self.pop()

    # =====================================================
    # System
    # =====================================================

    def visit_GIRSystem(self, system: GIRSystem):

        self.line("system")

        self.push()

        if system.frontend:
            self.line(f"frontend: {system.frontend}")

        if system.backend:
            self.line(f"backend: {system.backend}")

        if system.api:
            self.line(f"api: {system.api}")

        if system.database:
            self.line(f"database: {system.database}")

        if system.cache:
            self.line(f"cache: {system.cache}")

        if system.storage:
            self.line(f"storage: {system.storage}")

        self.pop()

    # =====================================================
    # Page
    # =====================================================

    def visit_GIRPage(self, page: GIRPage):

        self.line("GIRPage")

        self.push()

        self.line(f"name: {page.name}")

        if page.theme:
            self.line(f"theme: {page.theme}")

        if page.intent:
            self.line("intent:")
            self.push()

            for line in page.intent.splitlines():
                self.line(line)

            self.pop()

        if page.components:

            self.line("components")

            self.push()

            for component in page.components:
                self.visit(component)

            self.pop()

        self.pop()

    # =====================================================
    # Hero
    # =====================================================

    def visit_GIRHero(self, hero: GIRHero):

        self.line("GIRHero")

        self.push()

        self.line(f"name: {hero.name}")

        if hero.image:
            self.line(f"image: {hero.image}")

        if hero.headline:
            self.line(f"headline: {hero.headline}")

        if hero.subtitle:
            self.line(f"subtitle: {hero.subtitle}")

        if hero.action:
            self.line(f"action: {hero.action}")

        if hero.intent:
            self.line("intent:")
            self.push()

            for line in hero.intent.splitlines():
                self.line(line)

            self.pop()

        self.pop()

    # =====================================================
    # Section
    # =====================================================

    def visit_GIRSection(self, section: GIRSection):

        self.line("GIRSection")

        self.push()

        self.line(f"name: {section.name}")

        if section.intent:
            self.line("intent:")
            self.push()

            for line in section.intent.splitlines():
                self.line(line)

            self.pop()

        if section.children:

            self.line("children")

            self.push()

            for child in section.children:
                self.visit(child)

            self.pop()

        self.pop()