from .token import Token
from .token_type import TokenType

KEYWORDS = {

    # ==================================================
    # Application
    # ==================================================

    "app": TokenType.APP,
    "import": TokenType.IMPORT,

    "target": TokenType.TARGET,
    "framework": TokenType.FRAMEWORK,
    "database": TokenType.DATABASE,

    "theme": TokenType.THEME,
    "intent": TokenType.INTENT,

    # ==================================================
    # UI
    # ==================================================

    "page": TokenType.PAGE,
    "hero": TokenType.HERO,
    "section": TokenType.SECTION,

    "image": TokenType.IMAGE,
    "headline": TokenType.HEADLINE,
    "subtitle": TokenType.SUBTITLE,
    "action": TokenType.ACTION,

    # ==================================================
    # Routing
    # ==================================================

    "route": TokenType.ROUTE,
    "path": TokenType.PATH,

    # ==================================================
    # Authentication & Authorization
    # ==================================================

    "auth": TokenType.AUTH,
    "role": TokenType.ROLE,
    "allow": TokenType.ALLOW,
    "inherits": TokenType.INHERITS,

    # ==================================================
    # Permissions
    # ==================================================

    "view": TokenType.VIEW,
    "get": TokenType.GET,
    "update": TokenType.UPDATE,
    "delete": TokenType.DELETE,
    "manage": TokenType.MANAGE,

    # ==================================================
    # Models
    # ==================================================

    "model": TokenType.MODEL,
    "type": TokenType.TYPE,

    # ==================================================
    # Relationships
    # ==================================================

    "belongsTo": TokenType.BELONGSTO,
    "hasOne": TokenType.HASONE,
    "hasMany": TokenType.HASMANY,
    "belongsToMany": TokenType.BELONGSTOMANY,
    "hasManyThrough": TokenType.HASMANYTHROUGH,

    # ==================================================
    # Field Constraints
    # ==================================================

    "primary": TokenType.PRIMARY,
    "required": TokenType.REQUIRED,
    "unique": TokenType.UNIQUE,
    "readonly": TokenType.READONLY,
    "nullable": TokenType.NULLABLE,

    "default": TokenType.DEFAULT,

    "min": TokenType.MIN,
    "max": TokenType.MAX,
    "minLength": TokenType.MINLEN,
    "maxLength": TokenType.MAXLEN,

    # ==================================================
    # Infrastructure
    # ==================================================

    "provider": TokenType.PROVIDER,
    "engine": TokenType.ENGINE,
    "api": TokenType.API,
    "storage": TokenType.STORAGE,
    "cache": TokenType.CACHE,

}

class Lexer:

    def __init__(self, source: str):

        self.source = source

        self.tokens = []

        self.start = 0
        self.current = 0

        self.line = 1
    
    def scan_tokens(self):

        while not self.is_at_end():

            self.start = self.current

            self.scan_token()

        self.tokens.append(
            Token(TokenType.EOF, "", self.line)
        )

        return self.tokens
    
    def scan_token(self):

        c = self.advance()

        match c:

            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case " " | "\r" | "\t":
                pass

            case "\n":
                self.line += 1

            case "$":
                if self.peek() == "(":
                    self.advance()
                    self.multiline_string()

                else:
                    self.literal()
            case "#":
                self.comment()
            case _:

                if c.isalpha():

                    self.identifier()

                else:

                    raise SyntaxError(
                        f"Unexpected character '{c}' at line {self.line}"
                    )
    
    def identifier(self):

        while self.peek().isalnum() or self.peek() == "_":

            self.advance()

        text = self.source[self.start:self.current]

        token_type = KEYWORDS.get(text)

        if token_type is None:

            raise SyntaxError(
                f"Unknown keyword '{text}' at line {self.line}"
            )

        self.add_token(token_type)

    
    def literal(self):
        # Skip the '$'
        self.start = self.current

        # Read until end of line
        while (
            not self.is_at_end()
            and self.peek() not in ("\n", "{")
        ):
            self.advance()

        value = self.source[self.start:self.current].rstrip()

        self.tokens.append(
            Token(
                TokenType.STRING,
                value,
                self.line,
            )
        )

    def multiline_literal(self):

        raise NotImplementedError(
            "Multiline literals are not implemented yet."
        )
    
    def comment(self):
        while (
            not self.is_at_end()
            and self.peek() != "\n"
        ):
            self.advance()

    def is_at_end(self):

        return self.current >= len(self.source)
    
    def advance(self):

        c = self.source[self.current]

        self.current += 1

        return c
    
    def peek(self):

        if self.is_at_end():
            return "\0"

        return self.source[self.current]
    
    def add_token(self, token_type):

        text = self.source[self.start:self.current]

        self.tokens.append(
            Token(token_type, text, self.line)
        )