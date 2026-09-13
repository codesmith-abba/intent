from pathlib import Path

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.compiler.compiler import Compiler
from itl.compiler.loader import ProjectLoader
from itl.gir.builder import GIRBuilder
from itl.parser.ast import App, Auth, Models, Model, Field, Permissions, Permission, PermissionRole
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile


def assert_raises(expected, callback):
    try:
        callback()
    except expected:
        return
    raise AssertionError(f"Expected {expected} to be raised")


def parse_module(text):
    source = SourceFile(path=Path("phase27.itl"), text=text)
    return Parser(Lexer(source).scan_tokens()).parse_module()


def base_model():
    return Model(intent=None, name="User", imports=[], fields=[Field(name="id", type="id", primary=True)])


def test_ecommerce_auth_module_parses_and_represents_configuration():
    auth = parse_module(Path("docs/examples/ecommerce/auth.itl").read_text(encoding="utf-8"))
    assert isinstance(auth, Auth)
    assert [p.value for p in auth.providers] == ["email", "phone", "google"]
    assert auth.registration.enabled is True
    assert auth.registration.verification == "email"
    assert auth.login.allow == ["email", "phone"]
    assert auth.login.remember_me is True
    assert auth.password_recovery.method == "email"
    assert auth.session.timeout == "30d"
    assert auth.session.multiple_devices is True
    assert auth.mfa.enabled is False


def test_ecommerce_auth_and_permissions_compile_through_gir():
    gir = Compiler(Path("docs/examples/ecommerce")).compile()
    assert gir.auth is not None
    assert len(gir.auth.providers) == 3
    assert gir.auth.session.timeout == "30d"
    assert gir.auth.login.remember_me is True
    assert {role.name for role in gir.permissions} == {"guest", "customer", "seller", "admin", "superAdmin"}


def test_custom_roles_are_not_hard_coded():
    permissions = Permissions(
        intent=None,
        roles=[
            PermissionRole(intent=None, name="owner", imports=[], actions=[]),
            PermissionRole(intent=None, name="auditor", imports=[], inherits=["owner"], actions=[]),
        ],
        permissions=[],
    )
    app = App(intent=None, name="Custom", imports=[], permissions=permissions)
    Analyzer().analyze(app)


def test_duplicate_roles_are_rejected():
    permissions = Permissions(intent=None, roles=[
        PermissionRole(intent=None, name="owner", imports=[], actions=[]),
        PermissionRole(intent=None, name="owner", imports=[], actions=[]),
    ], permissions=[])
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], permissions=permissions)))


def test_unknown_and_circular_role_inheritance_are_rejected():
    unknown = Permissions(intent=None, roles=[PermissionRole(intent=None, name="owner", imports=[], inherits=["missing"], actions=[])], permissions=[])
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], permissions=unknown)))
    circular = Permissions(intent=None, roles=[
        PermissionRole(intent=None, name="a", imports=[], inherits=["b"], actions=[]),
        PermissionRole(intent=None, name="b", imports=[], inherits=["a"], actions=[]),
    ], permissions=[])
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], permissions=circular)))


def test_resource_and_action_permissions_are_validated():
    valid = Permissions(intent=None, roles=[], permissions=[Permission(intent=None, name="readUser", resource="User", action="view")])
    app = App(intent=None, name="A", imports=[], models=Models(intent=None, models=[base_model()]), permissions=valid)
    Analyzer().analyze(app)
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], models=Models(intent=None, models=[base_model()]), permissions=Permissions(intent=None, roles=[], permissions=[Permission(intent=None, name="x", resource="Missing", action="view")])))
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], models=Models(intent=None, models=[base_model()]), permissions=Permissions(intent=None, roles=[], permissions=[Permission(intent=None, name="x", resource="User", action="execute")])))


def test_role_permission_reference_must_exist():
    permissions = Permissions(intent=None, roles=[PermissionRole(intent=None, name="owner", imports=[], permissions=["missing"], actions=[])], permissions=[])
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], permissions=permissions)))


def test_auth_provider_references_and_configuration_are_validated():
    auth = parse_module('''auth {
        provider $email
        registration { enabled true verification $email }
        login { allow $email rememberMe true }
        session { timeout 30d multipleDevices true }
        mfa { enabled true method $totp }
    }''')
    Analyzer().analyze(App(intent=None, name="A", imports=[], auth=auth))
    bad = parse_module('''auth {
        provider $email
        login { allow $phone }
    }''')
    assert_raises(SemanticError, lambda: Analyzer().analyze(App(intent=None, name="A", imports=[], auth=bad)))


def test_auth_gir_preserves_all_configuration():
    auth = parse_module('''auth {
        provider $email
        registration { enabled true verification $email }
        login { allow $email rememberMe true }
        logout { enabled true }
        passwordRecovery { enabled true method $email reset true }
        verification { enabled true method $email }
        session { timeout 7d multipleDevices true }
        mfa { enabled true method $totp }
    }''')
    gir = GIRBuilder().build(App(intent=None, name="A", imports=[], auth=auth))
    assert gir.auth.providers[0].value == "email"
    assert gir.auth.registration.verification == "email"
    assert gir.auth.login.remember_me is True
    assert gir.auth.logout.enabled is True
    assert gir.auth.password_recovery.reset is True
    assert gir.auth.verification.method == "email"
    assert gir.auth.session.multiple_devices is True
    assert gir.auth.mfa.method == "totp"
