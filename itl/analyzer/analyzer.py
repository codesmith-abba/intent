from .errors import SemanticError
from .constants import (
    VALID_FRONTEND_FRAMEWORKS,
    VALID_BACKEND_FRAMEWORKS,
    VALID_THEMES,
    VALID_TARGETS,
)
from .scope import Scope
from .symbols import Symbol

from itl.parser.ast import (
    App,
    System,
    Frontend,
    Backend,
    Database,
    Cache,
    Storage,
    Page,
    Hero,
    Section,
)


class Analyzer:

    # ==================================================
    # Public API
    # ==================================================

    def analyze(self, app: App):

        self.scope = Scope()

        self.visit(app)

        return app

    # ==================================================
    # Visitor
    # ==================================================

    def visit(self, node):

        if node is None:
            return

        method = getattr(
            self,
            f"visit_{type(node).__name__.lower()}",
            self.generic_visit,
        )

        return method(node)

    def generic_visit(self, node):

        raise SemanticError(
            f"No analyzer for '{type(node).__name__}'."
        )

    # ==================================================
    # App
    # ==================================================

    def visit_app(self, app: App):

        self.validate_target(app.target)

        self.check_duplicate_pages(app)

        self.visit(app.system)

        for page in app.pages:
            self.scope.define(Symbol(page.name, page))

        for page in app.pages:
            self.visit(page)

    # ==================================================
    # System
    # ==================================================

    def visit_system(self, system: System):

        self.visit(system.frontend)
        self.visit(system.backend)
        self.visit(system.database)
        self.visit(system.cache)
        self.visit(system.storage)

    def visit_frontend(self, frontend: Frontend):

        if (
            frontend.framework
            and frontend.framework.value
            not in VALID_FRONTEND_FRAMEWORKS
        ):
            raise SemanticError(
                f"Unknown frontend framework "
                f"'{frontend.framework.value}'."
            )

    def visit_backend(self, backend: Backend):

        if (
            backend.framework
            and backend.framework.value
            not in VALID_BACKEND_FRAMEWORKS
        ):
            raise SemanticError(
                f"Unknown backend framework "
                f"'{backend.framework.value}'."
            )

    def visit_database(self, database: Database):
        pass

    def visit_cache(self, cache: Cache):
        pass

    def visit_storage(self, storage: Storage):
        pass

    # ==================================================
    # Pages
    # ==================================================

    def visit_page(self, page: Page):

        self.validate_theme(page.theme)

        self.check_duplicate_sections(page)

        self.visit(page.hero)

        page_scope = Scope(parent=self.scope)
        old = self.scope
        self.scope = page_scope

        for section in page.sections:
            self.scope.define(Symbol(section.name, section))

        for section in page.sections:
            self.visit(section)
        
        self.scope = old

    def visit_hero(self, hero: Hero):

        if not hero.headline:

            raise SemanticError(
                "Hero must contain a headline."
            )

    def visit_section(self, section: Section):

        for child in section.sections:
            self.visit(child)

    # ==================================================
    # Validation Helpers
    # ==================================================

    def validate_theme(self, theme):

        if theme is None:
            return

        if theme not in VALID_THEMES:

            raise SemanticError(
                f"Unknown theme '{theme}'."
            )

    def validate_target(self, target):

        if target not in VALID_TARGETS:

            raise SemanticError(
                f"Unknown target '{target}'."
            )

    # ==================================================
    # Duplicate Checks
    # ==================================================

    def check_duplicate_pages(self, app: App):

        seen = set()

        for page in app.pages:

            if page.name in seen:

                raise SemanticError(
                    f"Duplicate page '{page.name}'."
                )

            seen.add(page.name)

    def check_duplicate_sections(self, page: Page):

        seen = set()

        for section in page.sections:

            if section.name in seen:

                raise SemanticError(
                    f"Duplicate section '{section.name}' "
                    f"in page '{page.name}'."
                )

            seen.add(section.name)