from .token_type import TokenType
from .ast import App, Page, Hero, Section

from .errors import ParseError, LexerError

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens

        self.current = 0

    def parse(self):
        return self.app()
    

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

        app = App(name=name)

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():

            if self.match(TokenType.PAGE):

                app.pages.append(self.page())

            elif self.match(TokenType.TARGET):

                app.target = self.target()

            elif self.match(TokenType.FRAMEWORK):

                app.framework = self.framework()

            else:

                token = self.peek()

                raise ParseError(
                    f"[Line {token.line}] "
                    f"Unexpected token '{token.lexeme}'. "
                    "Expected 'page', 'target', or 'framework'."
                )

        self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after application body."
        )

        return app
    
    def page(self) -> Page:

        name = self.consume(
            TokenType.STRING,
            "Expected page name."
        ).lexeme

        self.consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after page name."
        )

        page = Page(name=name)

        while (
            not self.check(TokenType.RIGHT_BRACE)
            and not self.is_at_end()
        ):

            if self.match(TokenType.THEME):

                page.theme = self.theme()

            elif self.match(TokenType.HERO):

                page.hero = self.hero()

            elif self.match(TokenType.SECTION):

                page.sections.append(self.section())

            else:

                token = self.peek()

                raise ParseError(
                    f"[Line {token.line}] "
                    f"Unexpected token '{token.lexeme}' inside page."
                )

        self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after page."
        )

        return page
    
    def hero(self) -> Hero:

        name = self.consume(
            TokenType.STRING,
            "Expected hero name."
        ).lexeme

        self.consume(
            TokenType.LEFT_BRACE,
            "Expected '{' after hero name."
        )

        hero = Hero(name=name)

        while (
            not self.check(TokenType.RIGHT_BRACE)
            and not self.is_at_end()
        ):

            if self.match(TokenType.IMAGE):

                hero.image = self.image()

            elif self.match(TokenType.HEADLINE):

                hero.headline = self.headline()

            elif self.match(TokenType.SUBTITLE):

                hero.subtitle = self.subtitle()

            elif self.match(TokenType.ACTION):

                hero.action = self.action()

            else:

                token = self.peek()

                raise ParseError(
                    f"[Line {token.line}] "
                    f"Unexpected token '{token.lexeme}' inside hero."
                )

        self.consume(
            TokenType.RIGHT_BRACE,
            "Expected '}' after hero."
        )

        return hero
    
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

        return Section(name=name)

    def image(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected image path."
        ).lexeme
    
    def headline(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected headline."
        ).lexeme
    
    def subtitle(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected subtitle."
        ).lexeme
    
    def action(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected action."
        ).lexeme

    def theme(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected theme."
        ).lexeme

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
    
    def target(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected target value."
        ).lexeme
    
    def framework(self) -> str:

        return self.consume(
            TokenType.STRING,
            "Expected framework value."
        ).lexeme
    
    def consume(self, token_type, message):

        if self.check(token_type):

            return self.advance()

        raise LexerError(message)