import re

from .errors import SemanticError
from .constants import VALID_FRONTEND_FRAMEWORKS, VALID_BACKEND_FRAMEWORKS, VALID_THEMES, VALID_TARGETS
from .scope import Scope
from .symbols import Symbol
from itl.parser.ast import App, System, Frontend, Backend, Database, Cache, Storage, Page, Hero, Section, Models, Model, Field, Routes, Permissions, Auth

VALID_FIELD_TYPES = {"id", "string", "text", "email", "phone", "password", "image", "boolean", "datetime", "date", "time", "slug", "decimal", "integer", "number", "float", "json", "uuid"}
VALID_RELATIONSHIPS = {"belongsTo", "hasOne", "hasMany", "belongsToMany", "hasManyThrough"}
VALID_ACTIONS = {"view", "get", "create", "update", "delete", "manage"}
DURATION_RE = re.compile(r"^[1-9][0-9]*(s|m|h|d|w)$")


class Analyzer:
    def analyze(self, app: App):
        self.scope = Scope(); self.visit(app); return app
    def visit(self, node):
        if node is None: return
        return getattr(self, f"visit_{type(node).__name__.lower()}", self.generic_visit)(node)
    def generic_visit(self, node): raise SemanticError(f"No analyzer for '{type(node).__name__}'.")

    def visit_app(self, app: App):
        self.validate_target(app.target); self.check_duplicate_pages(app); self.visit(app.system); self.visit(app.models)
        self.visit_auth(app.auth)
        self.visit_permissions(app.permissions, app)
        self.visit_routes(app.routes, {page.name for page in app.pages}, app.permissions)
        for page in app.pages: self.scope.define(Symbol(page.name, page))
        for page in app.pages: self.visit(page)

    def visit_system(self, system: System):
        self.visit(system.frontend); self.visit(system.backend); self.visit(system.database); self.visit(system.cache); self.visit(system.storage)
    def visit_frontend(self, frontend: Frontend):
        if frontend.framework and frontend.framework.value not in VALID_FRONTEND_FRAMEWORKS: raise SemanticError(f"Unknown frontend framework '{frontend.framework.value}'.")
    def visit_backend(self, backend: Backend):
        if backend.framework and backend.framework.value not in VALID_BACKEND_FRAMEWORKS: raise SemanticError(f"Unknown backend framework '{backend.framework.value}'.")
    def visit_database(self, database: Database): pass
    def visit_cache(self, cache: Cache): pass
    def visit_storage(self, storage: Storage): pass

    def visit_models(self, models: Models):
        seen = set()
        for model in models.models:
            if model.name in seen: raise SemanticError(f"Duplicate model '{model.name}'.")
            seen.add(model.name)
        for model in models.models: self.visit_model(model, seen)
    def visit_model(self, model: Model, model_names: set[str]):
        if len({field.name for field in model.fields}) != len(model.fields): raise SemanticError(f"Duplicate field in model '{model.name}'.")
        primary = [field for field in model.fields if field.primary]
        if len(primary) > 1: raise SemanticError(f"Model '{model.name}' cannot have more than one primary key.")
        if not primary: raise SemanticError(f"Model '{model.name}' must define a primary key.")
        for field in model.fields: self.validate_field(model, field)
        for relationship in model.relationships:
            if relationship.kind not in VALID_RELATIONSHIPS: raise SemanticError(f"Unknown relationship '{relationship.kind}'.")
            if relationship.target not in model_names: raise SemanticError(f"Model '{model.name}' references unknown model '{relationship.target}' through '{relationship.kind}'.")
        for action in model.actions:
            if action.kind not in VALID_ACTIONS: raise SemanticError(f"Unknown action '{action.kind}'.")
    def validate_field(self, model: Model, field: Field):
        if field.type not in VALID_FIELD_TYPES: raise SemanticError(f"Unknown field type '{field.type}' for '{model.name}.{field.name}'.")
        if field.required and field.nullable: raise SemanticError(f"Field '{model.name}.{field.name}' cannot be both required and nullable.")
        if field.min_len is not None and field.min_len < 0: raise SemanticError(f"Field '{model.name}.{field.name}' has invalid minLen.")
        if field.max_len is not None and field.max_len < 0: raise SemanticError(f"Field '{model.name}.{field.name}' has invalid maxLen.")
        if field.min_len is not None and field.max_len is not None and field.min_len > field.max_len: raise SemanticError(f"Field '{model.name}.{field.name}' has minLen greater than maxLen.")
        if field.min is not None and field.max is not None and field.min > field.max: raise SemanticError(f"Field '{model.name}.{field.name}' has min greater than max.")
        if field.primary and field.nullable: raise SemanticError(f"Primary key '{model.name}.{field.name}' cannot be nullable.")

    def visit_auth(self, auth: Auth | None):
        if auth is None: return
        providers = [p.value for p in auth.providers]
        if len(providers) != len(set(providers)): raise SemanticError("Duplicate authentication provider.")
        provider_set = set(providers)
        if not providers and any(x is not None for x in (auth.registration, auth.login, auth.verification, auth.password_recovery, auth.mfa)):
            raise SemanticError("Authentication configuration requires at least one provider.")
        if auth.registration:
            if auth.registration.verification and auth.registration.verification not in provider_set: raise SemanticError(f"Unknown registration verification provider '{auth.registration.verification}'.")
        if auth.login:
            for provider in auth.login.allow:
                if provider not in provider_set: raise SemanticError(f"Unknown login provider '{provider}'.")
        if auth.password_recovery and auth.password_recovery.method and auth.password_recovery.method not in provider_set:
            raise SemanticError(f"Unknown password recovery method '{auth.password_recovery.method}'.")
        if auth.verification and auth.verification.method and auth.verification.method not in provider_set:
            raise SemanticError(f"Unknown verification method '{auth.verification.method}'.")
        if auth.session and auth.session.timeout and not DURATION_RE.fullmatch(auth.session.timeout):
            raise SemanticError(f"Invalid session timeout '{auth.session.timeout}'.")
        if auth.mfa and auth.mfa.enabled and not auth.mfa.method:
            raise SemanticError("Enabled MFA must define a method.")

    def visit_routes(self, routes: Routes | None, page_names: set[str] | None = None, permissions: Permissions | None = None):
        if routes is None: return
        seen_names, seen_paths = set(), set(); role_names = {r.name for r in permissions.roles} if permissions else set()
        for route in routes.routes:
            if route.name in seen_names: raise SemanticError(f"Duplicate route '{route.name}'.")
            seen_names.add(route.name)
            if not route.path: raise SemanticError(f"Route '{route.name}' must define a path.")
            if route.path in seen_paths: raise SemanticError(f"Duplicate route path '{route.path}'.")
            seen_paths.add(route.path)
            if not route.page: raise SemanticError(f"Route '{route.name}' must define a page.")
            if page_names is not None and route.page not in page_names: raise SemanticError(f"Route '{route.name}' references unknown page '{route.page}'.")
            if route.auth and role_names and route.auth not in role_names: raise SemanticError(f"Route '{route.name}' references unknown auth role '{route.auth}'.")

    def visit_permissions(self, permissions: Permissions | None, app: App):
        if permissions is None: return
        role_names = {r.name for r in permissions.roles}
        if len(role_names) != len(permissions.roles): raise SemanticError("Duplicate role declaration.")
        permission_names = set()
        resource_names = set()
        if app.models: resource_names.update(m.name for m in app.models.models)
        resource_names.update(p.name for p in app.pages)
        if app.routes: resource_names.update(r.name for r in app.routes.routes)
        for permission in permissions.permissions:
            if permission.name in permission_names: raise SemanticError(f"Duplicate permission '{permission.name}'.")
            permission_names.add(permission.name)
            if not permission.resource: raise SemanticError(f"Permission '{permission.name}' must define a resource.")
            if permission.resource not in resource_names: raise SemanticError(f"Permission '{permission.name}' references unknown resource '{permission.resource}'.")
            if not permission.action or permission.action not in VALID_ACTIONS: raise SemanticError(f"Permission '{permission.name}' has invalid action '{permission.action}'.")
        graph = {r.name: list(r.inherits) for r in permissions.roles}
        for role in permissions.roles:
            for inherited in role.inherits:
                if inherited not in role_names: raise SemanticError(f"Role '{role.name}' inherits unknown role '{inherited}'.")
            for permission_name in role.permissions:
                if permission_name not in permission_names: raise SemanticError(f"Role '{role.name}' references unknown permission '{permission_name}'.")
            for action in role.actions:
                if action.kind not in VALID_ACTIONS: raise SemanticError(f"Unknown permission action '{action.kind}'.")
        visiting, visited = set(), set()
        def dfs(role):
            if role in visiting: raise SemanticError(f"Circular role inheritance involving '{role}'.")
            if role in visited: return
            visiting.add(role)
            for parent in graph[role]: dfs(parent)
            visiting.remove(role); visited.add(role)
        for role in role_names: dfs(role)

    def visit_page(self, page: Page):
        self.validate_theme(page.theme); self.check_duplicate_sections(page); self.visit(page.hero)
        page_scope = Scope(parent=self.scope); old = self.scope; self.scope = page_scope
        for section in page.sections: self.scope.define(Symbol(section.name, section))
        for section in page.sections: self.visit(section)
        self.scope = old
    def visit_hero(self, hero: Hero):
        if not hero.headline: raise SemanticError("Hero must contain a headline.")
    def visit_section(self, section: Section):
        for child in section.sections: self.visit(child)
    def validate_theme(self, theme):
        if theme is not None and theme not in VALID_THEMES: raise SemanticError(f"Unknown theme '{theme}'.")
    def validate_target(self, target):
        if target not in VALID_TARGETS: raise SemanticError(f"Unknown target '{target}'.")
    def check_duplicate_pages(self, app: App):
        seen = set()
        for page in app.pages:
            if page.name in seen: raise SemanticError(f"Duplicate page '{page.name}'.")
            seen.add(page.name)
    def check_duplicate_sections(self, page: Page):
        seen = set()
        for section in page.sections:
            if section.name in seen: raise SemanticError(f"Duplicate section '{section.name}' in page '{page.name}'.")
            seen.add(section.name)
