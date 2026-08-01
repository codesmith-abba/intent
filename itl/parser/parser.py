from platform import system

from .token_type import TokenType
from .ast import *

from .errors import ParseError

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens

        self.current = 0

        self.APP_DECLARATIONS = {

            TokenType.IMPORT: self.parse_import,

            TokenType.PAGE: self.parse_page,

            TokenType.SYSTEM: self.parse_system,

            TokenType.TARGET: self.parse_target,

        }

        self.PAGE_MEMBERS = {

            TokenType.THEME:
                lambda page: setattr(
                    page,
                    "theme",
                    self.theme(),
                ),

            TokenType.INTENT:
                lambda page: setattr(
                    page,
                    "intent",
                    self.intent(),
                ),

            TokenType.HERO:
                lambda page: setattr(
                    page,
                    "hero",
                    self.hero(),
                ),

            TokenType.SECTION:
                lambda page: page.sections.append(
                    self.section()
                ),

        }

        self.HERO_MEMBERS = {

            TokenType.IMAGE:
                lambda hero: setattr(
                    hero,
                    "image",
                    self.image(),
                ),

            TokenType.HEADLINE:
                lambda hero: setattr(
                    hero,
                    "headline",
                    self.headline(),
                ),

            TokenType.SUBTITLE:
                lambda hero: setattr(
                    hero,
                    "subtitle",
                    self.subtitle(),
                ),

            TokenType.ACTION:
                lambda hero: setattr(
                    hero,
                    "action",
                    self.action(),
                ),

        }

        self.FRONTEND_MEMBERS = {
            TokenType.FRAMEWORK: lambda frontend: setattr(
                frontend,
                "framework",
                self.framework(),
            ),
        }

        self.BACKEND_MEMBERS = {
            TokenType.FRAMEWORK: lambda backend: setattr(
                backend,
                "framework",
                self.framework(),
            ),
            TokenType.API: lambda backend: setattr(
                backend,
                "api",
                self.api(),
            ),
        }

        self.DATABASE_MEMBERS = {
            TokenType.ENGINE: lambda database: setattr(
                database,
                "engine",
                self.engine(),
            ),
        }
        
        self.CACHE_MEMBERS = {
            TokenType.ENGINE: lambda cache: setattr(
                cache,
                "engine",
                self.engine(),
            ),
        }

        self.STORAGE_MEMBERS = {
            TokenType.PROVIDER: lambda storage: setattr(
                storage,
                "provider",
                self.provider(),
            ),
        }

        self.SYSTEM_MEMBERS = {
            TokenType.FRONTEND: lambda system: setattr(
                system,
                "frontend",
                self.frontend(),
            ),
            TokenType.BACKEND: lambda system: setattr(
                system,
                "backend",
                self.backend(),
            ),
            TokenType.DATABASE: lambda system: setattr(
                system,
                "database",
                self.database(),
            ),
            TokenType.CACHE: lambda system: setattr(
                system,
                "cache",
                self.cache(),
            ),
            TokenType.STORAGE: lambda system: setattr(
                system,
                "storage",
                self.storage(),
            ),
        }

    def parse(self):
        return self.app()
    
    def dispatch(
        self,
        handlers: dict,
        *args,
    ):
        handler = handlers.get(
            self.peek().type
        )

        if handler is None:

            token = self.peek()

            raise ParseError(
                f"[Line {token.line}] "
                f"Unexpected token '{token.lexeme}'."
            )

        self.advance()

        return handler(*args)
    
    def declaration(self, app: App):

        self.dispatch(
            self.APP_DECLARATIONS,
            app
        )
    
    def page_member(self, page: Page):

        self.dispatch(
            self.PAGE_MEMBERS,
            page
        )

    def hero_member(self, hero: Hero):

        self.dispatch(
            self.HERO_MEMBERS,
            hero
        )

    def system_member(self, system: System):

        self.dispatch(
            self.SYSTEM_MEMBERS,
            system
        )
        

    def app(self) -> App:

        self.consume(
            TokenType.APP,
            "Expected 'app'."
        )

        name = self.consume(
            TokenType.STRING,
            "Expected application name."
        ).lexeme

        self.consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after application name."
        )

        app = App(
            intent=self.intent(),
            name=name,
            imports=[],
        )

        while (
            not self.check(TokenType.RIGHT_BRACE)
            and not self.is_at_end()
        ):

            self.declaration(app)
        
        return app
    
    def page(self) -> Page:

        name = self.consume(
            TokenType.STRING,
            "Expected page name."
        ).lexeme

        return self.parse_block(
            Page(intent=self.intent(), name=name, imports=[]),
            self.PAGE_MEMBERS,
            "Expected '{' after page name.",
        )
    
    def hero(self) -> Hero:

        name = self.consume(
            TokenType.STRING,
            "Expected hero name."
        ).lexeme

        return self.parse_block(
            Hero(intent=self.intent(), name=name),
            self.HERO_MEMBERS,
            "Expected '{' after hero name.",
        )
    
    
    def section(self) -> Section:

        name = self.consume(
            TokenType.STRING,
            "Expected section name."
        ).lexeme

        self.consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after section name."
        )

        self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after section."
        )

        return Section(intent=self.intent(), name=name, imports=[])

    def image(self) -> str:

        return self.literal_value(
            "Expected image path."
        )
    
    def headline(self) -> str:

        return self.literal_value(
            "Expected headline."
        )
    
    def subtitle(self) -> str:

        return self.literal_value(
            "Expected subtitle."
        )
    
    def intent(self) -> str:

        self.consume(
            TokenType.INTENT,
            "Expected 'intent'."
        )

        return self.literal_value("Expected intent value.")
    
    def optional_intent(self):

        if self.check(TokenType.INTENT):
            return self.intent()

        return None

    def action(self) -> str:

        return self.literal_value(
            "Expected action."
        )

    def theme(self) -> str:

        return self.literal_value(
            "Expected theme."
        )

    def target(self) -> str:

        return self.literal_value(
            "Expected target value."
        )
    
    def framework(self) -> Framework:

        return Framework(
            value=self.literal_value("Expected framework value.")
        )
    
    def api(self) -> API:

        return API(
            value=self.literal_value("Expected API value.")
        )

    def engine(self) -> Engine:

        return Engine(
            value=self.literal_value("Expected engine value.")
        )

    def import_(self) -> str:

        return self.literal_value("Expected import value.")

    def provider(self) -> Provider:

        return Provider(
            value=self.literal_value("Expected provider value.")
        )

    def frontend(self) -> Frontend:

        return self.parse_block(
            Frontend(intent=self.optional_intent()),
            self.FRONTEND_MEMBERS,
            "Expected '{' after frontend.",
        )

    def backend(self) -> Backend:

        return self.parse_block(
            Backend(intent=self.optional_intent()),
            self.BACKEND_MEMBERS,
            "Expected '{' after backend.",
        )

    def database(self) -> Database:

        return self.parse_block(
            Database(intent=self.optional_intent()),
            self.DATABASE_MEMBERS,
            "Expected '{' after database.",
        )

    def cache(self) -> Cache:

        return self.parse_block(
            Cache(intent=self.optional_intent()),
            self.CACHE_MEMBERS,
            "Expected '{' after cache.",
        )

    def storage(self) -> Storage:

        return self.parse_block(
            Storage(intent=self.optional_intent()),
            self.STORAGE_MEMBERS,
            "Expected '{' after storage.",
        )
    
    def system(self):

        return self.parse_block(
            System(intent=self.optional_intent()),
            self.SYSTEM_MEMBERS,
            "Expected '{' after system.",
        )

    def is_at_end(self):
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()
    
    def check(self, token_type):

        if self.is_at_end():
            return False

        return self.peek().type == token_type
        
    def match(self, *types):

        for token_type in types:

            if self.check(token_type):

                self.advance()

                return True

        return False
    
    def consume(self, token_type, message):

        if self.check(token_type):

            return self.advance()

        raise ParseError(message)
    
    def literal_value(self, message: str) -> str:

        return self.consume(
            TokenType.STRING,
            message,
        ).lexeme

    # Application Declarations
    def parse_import(self, app: App):

        app.imports.append(
            self.import_()
        )
    
    def parse_page(self, app: App):
        app.pages.append(
            self.page()
        )
    
    def parse_system(self, app: App):

        app.system = self.system()
    
    def parse_target(self, app: App):

        app.target = self.target()

    # Block Parsing
    def parse_block(
        self,
        node,
        handlers,
        message: str,
    ):

        self.consume(
            TokenType.LEFT_BRACE,
            message,
        )

        while (
            not self.check(TokenType.RIGHT_BRACE)
            and not self.is_at_end()
        ):

            self.dispatch(
                handlers,
                node,
            )

        self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}'."
        )

        return node