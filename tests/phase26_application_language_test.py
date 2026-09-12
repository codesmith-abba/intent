from pathlib import Path

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.compiler.loader import ProjectLoader
from itl.gir.builder import GIRBuilder
from itl.parser.ast import App, Model
from itl.parser.errors import ParseError
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile
from itl.parser.token_type import TokenType


def parse(source: str):
    tokens = Lexer(SourceFile("phase26.itl", source)).scan_tokens()
    return Parser(tokens).parse()


def assert_raises(expected, callback):
    try:
        callback()
    except expected:
        return
    raise AssertionError(f"Expected {expected} to be raised")


def test_model_fields_constraints_and_relationships_parse():
    app = parse("""app $Store {
    models {
        model $User {
            field $id {
                type $id
                primary
            }
            field $email {
                type $email
                required
                unique
            }
            field $name {
                type $string
                nullable
                maxLen 100
            }
            field $active {
                type $boolean
                default true
                readonly
            }
            hasMany $Order
        }
        model $Order {
            field $id {
                type $id
                primary
            }
            belongsTo $User
        }
    }
}""")
    user = app.models.models[0]
    assert isinstance(user, Model)
    assert user.fields[1].unique is True
    assert user.fields[2].nullable is True
    assert user.fields[3].default is True
    assert user.relationships[0].kind == "hasMany"


def test_all_relationship_kinds_are_accepted():
    app = parse("""app $Store {
    models {
        model $A {
            field $id {
                type $id
                primary
            }
            belongsTo $B
            hasOne $B
            hasMany $B
            belongsToMany $B
            hasManyThrough $B
        }
        model $B {
            field $id {
                type $id
                primary
            }
        }
    }
}""")
    Analyzer().analyze(app)


def test_invalid_model_semantics_are_rejected():
    duplicate_field = """app $X {
    models {
        model $User {
            field $id {
                type $id
                primary
            }
            field $id {
                type $string
            }
        }
    }
}"""
    unknown_type = """app $X {
    models {
        model $User {
            field $id {
                type $id
                primary
            }
            field $x {
                type $unknown
            }
        }
    }
}"""
    nullable_primary = """app $X {
    models {
        model $User {
            field $id {
                type $id
                primary
                nullable
            }
        }
    }
}"""
    missing_relationship = """app $X {
    models {
        model $User {
            field $id {
                type $id
                primary
            }
            belongsTo $Missing
        }
    }
}"""

    for source in (
        duplicate_field,
        unknown_type,
        nullable_primary,
        missing_relationship,
    ):
        assert_raises((ParseError, SemanticError), lambda source=source: Analyzer().analyze(parse(source)))


def test_routes_and_permissions_have_application_semantics():
    app = parse("""app $Store {
    page $home {}
    routes {
        route $home {
            path $/
            page $home
            auth $guest
        }
    }
    permissions {
        role $guest {
            allow {
                view $home
                create $order
            }
        }
    }
}""")
    Analyzer().analyze(app)
    assert app.routes.routes[0].path == "/"
    assert app.permissions.roles[0].actions[1].kind == "create"


def test_invalid_route_page_reference_is_rejected():
    app = parse("""app $Store {
    page $home {}
    routes {
        route $missing {
            path $/missing
            page $missing
        }
    }
}""")
    assert_raises(SemanticError, lambda: Analyzer().analyze(app))


def test_ecommerce_models_compile_through_gir():
    # The ecommerce example also contains auth.itl, whose authentication
    # grammar is outside Phase 26. Test the Phase 26 model pipeline directly
    # so this acceptance test is isolated from future application modules.
    loader = ProjectLoader(Path("docs/examples/ecommerce"))
    models = loader.load_module("models")
    app = App(name="SMarket", imports=[], models=models)

    Analyzer().analyze(app)
    gir = GIRBuilder().build(app)

    assert gir.name == "SMarket"
    assert len(gir.models) >= 10
    assert any(model.name == "Product" for model in gir.models)
    product = next(model for model in gir.models if model.name == "Product")
    assert any(field.name == "price" and field.required for field in product.fields)
    assert any(rel.kind == "belongsTo" and rel.target == "Seller" for rel in product.relationships)


def test_model_keywords_are_lexed_as_reserved_tokens():
    tokens = Lexer(SourceFile("keywords.itl", "models model field type primary required unique readonly nullable default belongsTo hasOne hasMany belongsToMany hasManyThrough create get update delete manage route")).scan_tokens()
    assert tokens[-1].type == TokenType.EOF
    assert all(token.type != TokenType.STRING for token in tokens[:-1])
