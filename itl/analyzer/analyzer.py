from .errors import SemanticError
from .constants import VALID_FRONTEND_FRAMEWORKS, VALID_BACKEND_FRAMEWORKS, VALID_THEMES, VALID_TARGETS
from .scope import Scope
from .symbols import Symbol
from itl.parser.ast import (
    App, System, Frontend, Backend, Database, Cache, Storage,
    Page, Hero, Section, Models, Model, Field, Relationship,
    Routes, Route, Permissions, PermissionRole,
)

VALID_FIELD_TYPES = {
    "id", "string", "text", "email", "phone", "password", "image",
    "boolean", "datetime", "date", "time", "slug", "decimal",
    "integer", "number", "float", "json", "uuid",
}
VALID_RELATIONSHIPS = {"belongsTo", "hasOne", "hasMany", "belongsToMany", "hasManyThrough"}
VALID_ACTIONS = {"view", "get", "create", "update", "delete", "manage"}


class Analyzer:
    def analyze(self, app: App):
        self.scope = Scope()
        self.visit(app)
        return app

    def visit(self, node):
        if node is None:
            return
        method = getattr(self, f"visit_{type(node).__name__.lower()}", self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise SemanticError(f"No analyzer for '{type(node).__name__}'.")

    def visit_app(self, app: App):
        self.validate_target(app.target)
        self.check_duplicate_pages(app)
        self.visit(app.system)
        self.visit(app.models)
        self.visit(app.routes)
        self.visit(app.permissions)
        for page in app.pages:
            self.scope.define(Symbol(page.name, page))
        for page in app.pages:
            self.visit(page)

    def visit_system(self, system: System):
        self.visit(system.frontend); self.visit(system.backend)
        self.visit(system.database); self.visit(system.cache); self.visit(system.storage)

    def visit_frontend(self, frontend: Frontend):
        if frontend.framework and frontend.framework.value not in VALID_FRONTEND_FRAMEWORKS:
            raise SemanticError(f"Unknown frontend framework '{frontend.framework.value}'.")

    def visit_backend(self, backend: Backend):
        if backend.framework and backend.framework.value not in VALID_BACKEND_FRAMEWORKS:
            raise SemanticError(f"Unknown backend framework '{backend.framework.value}'.")

    def visit_database(self, database: Database): pass
    def visit_cache(self, cache: Cache): pass
    def visit_storage(self, storage: Storage): pass

    def visit_models(self, models: Models):
        seen = set()
        for model in models.models:
            if model.name in seen:
                raise SemanticError(f"Duplicate model '{model.name}'.")
            seen.add(model.name)
        model_names = seen
        for model in models.models:
            self.visit_model(model, model_names)

    def visit_model(self, model: Model, model_names: set[str]):
        fields = {field.name: field for field in model.fields}
        if len(fields) != len(model.fields):
            raise SemanticError(f"Duplicate field in model '{model.name}'.")
        primary_fields = [field for field in model.fields if field.primary]
        if len(primary_fields) > 1:
            raise SemanticError(f"Model '{model.name}' cannot have more than one primary key.")
        if not primary_fields:
            raise SemanticError(f"Model '{model.name}' must define a primary key.")
        for field in model.fields:
            self.validate_field(model, field)
        for relationship in model.relationships:
            if relationship.kind not in VALID_RELATIONSHIPS:
                raise SemanticError(f"Unknown relationship '{relationship.kind}'.")
            if relationship.target not in model_names:
                raise SemanticError(
                    f"Model '{model.name}' references unknown model '{relationship.target}' "
                    f"through '{relationship.kind}'."
                )
        for action in model.actions:
            if action.kind not in VALID_ACTIONS:
                raise SemanticError(f"Unknown action '{action.kind}'.")

    def validate_field(self, model: Model, field: Field):
        if field.type not in VALID_FIELD_TYPES:
            raise SemanticError(f"Unknown field type '{field.type}' for '{model.name}.{field.name}'.")
        if field.required and field.nullable:
            raise SemanticError(f"Field '{model.name}.{field.name}' cannot be both required and nullable.")
        if field.min_len is not None and field.min_len < 0:
            raise SemanticError(f"Field '{model.name}.{field.name}' has invalid minLen.")
        if field.max_len is not None and field.max_len < 0:
            raise SemanticError(f"Field '{model.name}.{field.name}' has invalid maxLen.")
        if field.min_len is not None and field.max_len is not None and field.min_len > field.max_len:
            raise SemanticError(f"Field '{model.name}.{field.name}' has minLen greater than maxLen.")
        if field.min is not None and field.max is not None and field.min > field.max:
            raise SemanticError(f"Field '{model.name}.{field.name}' has min greater than max.")
        if field.primary and field.nullable:
            raise SemanticError(f"Primary key '{model.name}.{field.name}' cannot be nullable.")

    def visit_routes(self, routes: Routes):
        seen = set()
        for route in routes.routes:
            if route.name in seen:
                raise SemanticError(f"Duplicate route '{route.name}'.")
            seen.add(route.name)
            if not route.path:
                raise SemanticError(f"Route '{route.name}' must define a path.")
            if not route.page:
                raise SemanticError(f"Route '{route.name}' must define a page.")
            if route.path in {r.path for r in routes.routes if r is not route}:
                raise SemanticError(f"Duplicate route path '{route.path}'.")

    def visit_permissions(self, permissions: Permissions):
        seen = set()
        for role in permissions.roles:
            if role.name in seen:
                raise SemanticError(f"Duplicate role '{role.name}'.")
            seen.add(role.name)
        for role in permissions.roles:
            for inherited in role.inherits:
                if inherited not in seen:
                    raise SemanticError(f"Role '{role.name}' inherits unknown role '{inherited}'.")
            for action in role.actions:
                if action.kind not in VALID_ACTIONS:
                    raise SemanticError(f"Unknown permission action '{action.kind}'.")

    def visit_page(self, page: Page):
        self.validate_theme(page.theme)
        self.check_duplicate_sections(page)
        self.visit(page.hero)
        page_scope = Scope(parent=self.scope)
        old = self.scope; self.scope = page_scope
        for section in page.sections:
            self.scope.define(Symbol(section.name, section))
        for section in page.sections:
            self.visit(section)
        self.scope = old

    def visit_hero(self, hero: Hero):
        if not hero.headline:
            raise SemanticError("Hero must contain a headline.")

    def visit_section(self, section: Section):
        for child in section.sections:
            self.visit(child)

    def validate_theme(self, theme):
        if theme is not None and theme not in VALID_THEMES:
            raise SemanticError(f"Unknown theme '{theme}'.")

    def validate_target(self, target):
        if target not in VALID_TARGETS:
            raise SemanticError(f"Unknown target '{target}'.")

    def check_duplicate_pages(self, app: App):
        seen = set()
        for page in app.pages:
            if page.name in seen:
                raise SemanticError(f"Duplicate page '{page.name}'.")
            seen.add(page.name)

    def check_duplicate_sections(self, page: Page):
        seen = set()
        for section in page.sections:
            if section.name in seen:
                raise SemanticError(f"Duplicate section '{section.name}' in page '{page.name}'.")
            seen.add(section.name)
