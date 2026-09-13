from .token import Token
from .token_type import TokenType
from .ast import *
from .errors import ParseError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.current = 0
        self.APP_DECLARATIONS = {
            TokenType.IMPORT: self.parse_import, TokenType.PAGE: self.parse_page_into_app, TokenType.SYSTEM: self.parse_system,
            TokenType.TARGET: self.parse_target, TokenType.MODELS: self.parse_models_into_app, TokenType.ROUTES: self.parse_routes_into_app,
            TokenType.PERMISSIONS: self.parse_permissions_into_app, TokenType.AUTH: self.parse_auth_into_app,
            TokenType.INTENT: lambda app: setattr(app, "intent", self.intent()),
        }
        self.PAGE_MEMBERS = {TokenType.IMPORT: self.parse_import, TokenType.THEME: lambda n: setattr(n, "theme", self.theme()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent()), TokenType.HERO: lambda n: setattr(n, "hero", self.hero()), TokenType.SECTION: lambda n: n.sections.append(self.section())}
        self.HERO_MEMBERS = {TokenType.IMAGE: lambda n: setattr(n, "image", self.image()), TokenType.HEADLINE: lambda n: setattr(n, "headline", self.headline()), TokenType.SUBTITLE: lambda n: setattr(n, "subtitle", self.subtitle()), TokenType.ACTION: lambda n: setattr(n, "action", self.action()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        self.SECTION_MEMBERS = {TokenType.SECTION: lambda n: n.sections.append(self.section()), TokenType.IMAGE: lambda n: setattr(n, "image", self.image()), TokenType.HEADLINE: lambda n: setattr(n, "headline", self.headline()), TokenType.SUBTITLE: lambda n: setattr(n, "subtitle", self.subtitle()), TokenType.ACTION: lambda n: setattr(n, "action", self.action()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        self.FRONTEND_MEMBERS = {TokenType.FRAMEWORK: lambda n: setattr(n, "framework", self.framework())}
        self.BACKEND_MEMBERS = {TokenType.FRAMEWORK: lambda n: setattr(n, "framework", self.framework()), TokenType.API: lambda n: setattr(n, "api", self.api())}
        self.DATABASE_MEMBERS = {TokenType.ENGINE: lambda n: setattr(n, "engine", self.engine())}
        self.CACHE_MEMBERS = {TokenType.ENGINE: lambda n: setattr(n, "engine", self.engine())}
        self.STORAGE_MEMBERS = {TokenType.PROVIDER: lambda n: setattr(n, "provider", self.provider())}
        self.SYSTEM_MEMBERS = {TokenType.FRONTEND: lambda n: setattr(n, "frontend", self.frontend()), TokenType.BACKEND: lambda n: setattr(n, "backend", self.backend()), TokenType.DATABASE: lambda n: setattr(n, "database", self.database()), TokenType.CACHE: lambda n: setattr(n, "cache", self.cache()), TokenType.STORAGE: lambda n: setattr(n, "storage", self.storage())}
        self.MODULE_DECLARATIONS = {TokenType.PAGE: self.page, TokenType.SECTION: self.section, TokenType.MODELS: self.models, TokenType.ROUTES: self.routes, TokenType.PERMISSIONS: self.permissions, TokenType.AUTH: self.auth}
    def parse(self):
        app = self.app(); self.consume(TokenType.EOF, "Unexpected declaration after application block."); return app
    def parse_module(self):
        handler = self.MODULE_DECLARATIONS.get(self.peek().type)
        if handler is None: raise ParseError("Expected a module declaration.")
        self.advance(); node = handler(); self.consume(TokenType.EOF, "Unexpected declaration after module block."); return node
    def dispatch(self, handlers, *args):
        handler = handlers.get(self.peek().type)
        if handler is None:
            token = self.peek(); raise ParseError(f"'{token.file}', line {token.line} Unexpected token '{token.lexeme}'.")
        self.advance(); return handler(*args)
    def app(self):
        self.consume(TokenType.APP, "Expected 'app'."); name = self.consume(TokenType.STRING, "Expected application name.").lexeme
        return self.parse_block(App(intent=self.optional_intent(), name=name, imports=[]), self.APP_DECLARATIONS, "Expected '{' after application name.")
    def page(self):
        name = self.consume(TokenType.STRING, "Expected page name.").lexeme; return self.parse_block(Page(intent=self.optional_intent(), name=name, imports=[]), self.PAGE_MEMBERS, "Expected '{' after page name.")
    def hero(self):
        name = self.consume(TokenType.STRING, "Expected hero name.").lexeme; return self.parse_block(Hero(intent=self.optional_intent(), name=name), self.HERO_MEMBERS, "Expected '{' after hero name.")
    def section(self):
        name = self.consume(TokenType.STRING, "Expected section name.").lexeme; return self.parse_block(Section(intent=self.optional_intent(), name=name, imports=[]), self.SECTION_MEMBERS, "Expected '{' after section name.")
    def models(self):
        node = Models(intent=self.optional_intent(), models=[])
        return self.parse_block(node, {TokenType.MODEL: lambda n: n.models.append(self.model()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}, "Expected '{' after models.")
    def model(self):
        name = self.consume(TokenType.STRING, "Expected model name.").lexeme; node = Model(intent=self.optional_intent(), name=name, imports=[])
        handlers = {TokenType.FIELD: lambda n: n.fields.append(self.field())}
        for t in (TokenType.BELONGSTO, TokenType.HASONE, TokenType.HASMANY, TokenType.BELONGSTOMANY, TokenType.HASMANYTHROUGH): handlers[t] = lambda n, t=t: n.relationships.append(self.relationship(t))
        for t in (TokenType.GET, TokenType.CREATE, TokenType.UPDATE, TokenType.DELETE, TokenType.MANAGE): handlers[t] = lambda n, t=t: n.actions.append(self.action_node(t))
        return self.parse_block(node, handlers, "Expected '{' after model name.")
    def field(self):
        name = self.consume(TokenType.STRING, "Expected field name.").lexeme; self.consume(TokenType.LEFT_BRACE, "Expected '{' after field name.")
        field_type = None; values = {"primary": False, "required": False, "unique": False, "readonly": False, "nullable": False, "default": None, "min": None, "max": None, "min_len": None, "max_len": None}
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            token = self.peek().type; self.advance()
            if token == TokenType.TYPE: field_type = self.value("Expected field type.")
            elif token in (TokenType.PRIMARY, TokenType.REQUIRED, TokenType.UNIQUE, TokenType.READONLY, TokenType.NULLABLE): values[{TokenType.PRIMARY:"primary",TokenType.REQUIRED:"required",TokenType.UNIQUE:"unique",TokenType.READONLY:"readonly",TokenType.NULLABLE:"nullable"}[token]] = True
            elif token in (TokenType.DEFAULT, TokenType.MIN, TokenType.MAX): values[{TokenType.DEFAULT:"default",TokenType.MIN:"min",TokenType.MAX:"max"}[token]] = self.value("Expected field value.")
            elif token in (TokenType.MINLEN, TokenType.MAXLEN):
                value = self.value("Expected length value.")
                if not isinstance(value, int): raise ParseError(f"'{self.previous().file}', line {self.previous().line} Expected integer length value.")
                values[{TokenType.MINLEN:"min_len",TokenType.MAXLEN:"max_len"}[token]] = value
            else: raise ParseError(f"'{self.previous().file}', line {self.previous().line} Unexpected field member '{self.previous().lexeme}'.")
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after field.")
        if field_type is None: raise ParseError("Expected field type.")
        return Field(name=name, type=field_type, **values)
    def relationship(self, token_type):
        target = self.consume(TokenType.STRING, "Expected relationship target.").lexeme; kind = {TokenType.BELONGSTO:"belongsTo",TokenType.HASONE:"hasOne",TokenType.HASMANY:"hasMany",TokenType.BELONGSTOMANY:"belongsToMany",TokenType.HASMANYTHROUGH:"hasManyThrough"}[token_type]; return Relationship(kind, target)
    def routes(self):
        node = Routes(intent=self.optional_intent(), routes=[]); return self.parse_block(node, {TokenType.ROUTE: lambda n: n.routes.append(self.route())}, "Expected '{' after routes.")
    def route(self):
        name = self.consume(TokenType.STRING, "Expected route name.").lexeme; node = Route(intent=None, name=name, imports=[])
        handlers = {TokenType.PATH: lambda n: setattr(n, "path", self.literal_value("Expected route path.")), TokenType.PAGE: lambda n: setattr(n, "page", self.literal_value("Expected route page.")), TokenType.AUTH: lambda n: setattr(n, "auth", self.literal_value("Expected route auth role.")), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent()), TokenType.IMPORT: lambda n: self.parse_import(n)}
        return self.parse_block(node, handlers, "Expected '{' after route name.")
    def permissions(self):
        node = Permissions(intent=self.optional_intent(), roles=[], permissions=[])
        handlers = {TokenType.ROLE: lambda n: n.roles.append(self.permission_role()), TokenType.PERMISSION: lambda n: n.permissions.append(self.permission())}
        return self.parse_block(node, handlers, "Expected '{' after permissions.")
    def permission(self):
        name = self.consume(TokenType.STRING, "Expected permission name.").lexeme; node = Permission(intent=None, name=name, imports=[])
        handlers = {TokenType.RESOURCE: lambda n: setattr(n, "resource", self.literal_value("Expected permission resource.")), TokenType.ACTION: lambda n: setattr(n, "action", self.literal_value("Expected permission action.")), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after permission name.")
    def permission_role(self):
        name = self.consume(TokenType.STRING, "Expected role name.").lexeme; node = PermissionRole(intent=None, name=name, imports=[])
        handlers = {TokenType.INHERITS: lambda n: n.inherits.append(self.literal_value("Expected inherited role.")), TokenType.ALLOW: self.parse_allow_for_role, TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after role name.")
    def parse_allow_for_role(self, role):
        if self.check(TokenType.STRING): role.permissions.append(self.advance().lexeme); return
        self.allow_actions(role)
    def allow_actions(self, role):
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after allow.")
        action_types = (TokenType.VIEW, TokenType.GET, TokenType.CREATE, TokenType.UPDATE, TokenType.DELETE, TokenType.MANAGE)
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            token = self.peek().type
            if token not in action_types: raise ParseError(f"Unexpected token '{self.peek().lexeme}' in allow block.")
            self.advance(); role.actions.append(self.action_node(token))
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after allow block.")
    def action_node(self, token_type):
        target = self.consume(TokenType.STRING, "Expected action target.").lexeme; kind = {TokenType.VIEW:"view",TokenType.GET:"get",TokenType.CREATE:"create",TokenType.UPDATE:"update",TokenType.DELETE:"delete",TokenType.MANAGE:"manage"}[token_type]; return Action(kind, target)
    def auth(self):
        node = Auth(intent=self.optional_intent())
        handlers = {
            TokenType.INTENT: lambda n: setattr(n, "intent", self.intent()),
            TokenType.PROVIDER: lambda n: n.providers.append(AuthProvider(self.literal_value("Expected authentication provider."))),
            TokenType.REGISTRATION: lambda n: setattr(n, "registration", self.registration()), TokenType.LOGIN: lambda n: setattr(n, "login", self.login()),
            TokenType.LOGOUT: lambda n: setattr(n, "logout", self.logout()), TokenType.PASSWORD_RECOVERY: lambda n: setattr(n, "password_recovery", self.password_recovery()),
            TokenType.VERIFICATION: lambda n: setattr(n, "verification", self.verification()), TokenType.SESSION: lambda n: setattr(n, "session", self.session()),
            TokenType.MFA: lambda n: setattr(n, "mfa", self.mfa()),
        }
        return self.parse_block(node, handlers, "Expected '{' after auth.")
    def registration(self):
        node = RegistrationConfig(intent=self.optional_intent()); handlers = {TokenType.ENABLED: lambda n: setattr(n, "enabled", self.boolean_value()), TokenType.VERIFICATION: lambda n: setattr(n, "verification", self.literal_value("Expected verification provider.")), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after registration.")
    def login(self):
        node = LoginConfig(intent=self.optional_intent()); handlers = {TokenType.ALLOW: lambda n: n.allow.append(self.literal_value("Expected login provider.")), TokenType.REMEMBER_ME: lambda n: setattr(n, "remember_me", self.boolean_value()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after login.")
    def logout(self):
        node = LogoutConfig(intent=self.optional_intent()); handlers = {TokenType.ENABLED: lambda n: setattr(n, "enabled", self.boolean_value()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after logout.")
    def password_recovery(self):
        node = PasswordRecoveryConfig(intent=self.optional_intent()); handlers = {TokenType.ENABLED: lambda n: setattr(n, "enabled", self.boolean_value()), TokenType.METHOD: lambda n: setattr(n, "method", self.literal_value("Expected password recovery method.")), TokenType.RESET: lambda n: setattr(n, "reset", self.boolean_value()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after passwordRecovery.")
    def verification(self):
        node = VerificationConfig(intent=self.optional_intent()); handlers = {TokenType.ENABLED: lambda n: setattr(n, "enabled", self.boolean_value()), TokenType.METHOD: lambda n: setattr(n, "method", self.literal_value("Expected verification method.")), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after verification.")
    def session(self):
        node = SessionConfig(intent=self.optional_intent()); handlers = {TokenType.TIMEOUT: lambda n: setattr(n, "timeout", self.duration_value()), TokenType.MULTIPLE_DEVICES: lambda n: setattr(n, "multiple_devices", self.boolean_value()), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after session.")
    def mfa(self):
        node = MFAConfig(intent=self.optional_intent()); handlers = {TokenType.ENABLED: lambda n: setattr(n, "enabled", self.boolean_value()), TokenType.METHOD: lambda n: setattr(n, "method", self.literal_value("Expected MFA method.")), TokenType.INTENT: lambda n: setattr(n, "intent", self.intent())}
        return self.parse_block(node, handlers, "Expected '{' after mfa.")
    def boolean_value(self):
        if self.check(TokenType.BOOLEAN): return self.advance().literal
        token = self.peek(); raise ParseError(f"'{token.file}', line {token.line} Expected boolean value.")
    def duration_value(self):
        if self.check(TokenType.DURATION): return self.advance().lexeme
        token = self.peek(); raise ParseError(f"'{token.file}', line {token.line} Expected duration value.")
    def image(self): return self.literal_value("Expected image path.")
    def headline(self): return self.literal_value("Expected headline.")
    def subtitle(self): return self.literal_value("Expected subtitle.")
    def action(self): return self.literal_value("Expected action.")
    def intent(self): return self.literal_value("Expected intent value.")
    def theme(self): return self.literal_value("Expected theme.")
    def target(self): return self.literal_value("Expected target value.")
    def framework(self): return Framework(self.literal_value("Expected framework value."))
    def api(self): return API(self.literal_value("Expected API value."))
    def engine(self): return Engine(self.literal_value("Expected engine value."))
    def provider(self): return Provider(self.literal_value("Expected provider value."))
    def optional_intent(self): return self.intent() if self.match(TokenType.INTENT) else None
    def frontend(self): return self.parse_block(Frontend(intent=self.optional_intent()), self.FRONTEND_MEMBERS, "Expected '{' after frontend.")
    def backend(self): return self.parse_block(Backend(intent=self.optional_intent()), self.BACKEND_MEMBERS, "Expected '{' after backend.")
    def database(self): return self.parse_block(Database(intent=self.optional_intent()), self.DATABASE_MEMBERS, "Expected '{' after database.")
    def cache(self): return self.parse_block(Cache(intent=self.optional_intent()), self.CACHE_MEMBERS, "Expected '{' after cache.")
    def storage(self): return self.parse_block(Storage(intent=self.optional_intent()), self.STORAGE_MEMBERS, "Expected '{' after storage.")
    def system(self): return self.parse_block(System(intent=self.optional_intent()), self.SYSTEM_MEMBERS, "Expected '{' after system.")
    def parse_import(self, node): node.imports.append(self.literal_value("Expected import value."))
    def parse_page_into_app(self, app): app.pages.append(self.page())
    def parse_system(self, app): app.system = self.system()
    def parse_target(self, app): app.target = self.target()
    def parse_models_into_app(self, app): app.models = self.models()
    def parse_routes_into_app(self, app): app.routes = self.routes()
    def parse_permissions_into_app(self, app): app.permissions = self.permissions()
    def parse_auth_into_app(self, app): app.auth = self.auth()
    def value(self, message):
        token = self.peek()
        if token.type in (TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN): self.advance(); return token.literal if token.type in (TokenType.NUMBER, TokenType.BOOLEAN) else token.lexeme
        raise ParseError(f"'{token.file}', line {token.line} {message}")
    def literal_value(self, message): return self.consume(TokenType.STRING, message).lexeme
    def parse_block(self, node, handlers, message):
        self.consume(TokenType.LEFT_BRACE, message)
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end(): self.dispatch(handlers, node)
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'."); return node
    def is_at_end(self): return self.peek().type == TokenType.EOF
    def peek(self): return self.tokens[self.current]
    def previous(self): return self.tokens[self.current - 1]
    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()
    def check(self, token_type): return self.peek().type == token_type
    def match(self, *types):
        for token_type in types:
            if self.check(token_type): self.advance(); return True
        return False
    def consume(self, token_type, message):
        if self.check(token_type): return self.advance()
        token = self.peek(); raise ParseError(f"'{token.file}', line {token.line} {message}")
