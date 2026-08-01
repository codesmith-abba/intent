from enum import Enum, auto


class TokenType(Enum):

    # ==================================================
    # Application
    # ==================================================

    APP = auto()
    IMPORT = auto()

    TARGET = auto()
    FRAMEWORK = auto()
    DATABASE = auto()
    FRONTEND = auto()
    BACKEND = auto()

    THEME = auto()
    INTENT = auto()

    # ==================================================
    # Declarations
    # ==================================================

    MODELS = auto()
    ROUTES = auto()
    PERMISSIONS = auto()
    # AUTH = auto()

    # ==================================================
    # UI
    # ==================================================

    PAGE = auto()
    HERO = auto()
    SECTION = auto()

    IMAGE = auto()

    HEADLINE = auto()
    SUBTITLE = auto()
    ACTION = auto()

    # ==================================================
    # Routing
    # ==================================================

    ROUTE = auto()
    PATH = auto()

    # ==================================================
    # Authentication & Authorization
    # ==================================================

    AUTH = auto()

    ROLE = auto()
    ALLOW = auto()
    INHERITS = auto()

    # ==================================================
    # Permissions / Operations
    # ==================================================

    VIEW = auto()
    GET = auto()
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    MANAGE = auto()

    # ==================================================
    # Data Models
    # ==================================================
    FIELD = auto()
    MODEL = auto()
    TYPE = auto()

    # ==================================================
    # Relationships
    # ==================================================

    BELONGSTO = auto()
    HASONE = auto()
    HASMANY = auto()

    BELONGSTOMANY = auto()
    HASMANYTHROUGH = auto()

    # ==================================================
    # Field Constraints
    # ==================================================

    PRIMARY = auto()
    REQUIRED = auto()
    UNIQUE = auto()
    READONLY = auto()
    NULLABLE = auto()

    DEFAULT = auto()

    MIN = auto()
    MAX = auto()

    MINLEN = auto()
    MAXLEN = auto()

    # ==================================================
    # Built-in Types
    # ==================================================

    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()

    # ==================================================
    # Infrastructure
    # ==================================================

    SYSTEM = auto()
    ENGINE = auto()
    API = auto()
    PROVIDER = auto()
    STORAGE = auto()
    CACHE = auto()

    # ==================================================
    # Symbols
    # ==================================================

    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()

    # ==================================================
    # Special
    # ==================================================

    EOF = auto()