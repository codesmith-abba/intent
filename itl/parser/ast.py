from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal


@dataclass(slots=True)
class Node: pass

@dataclass(slots=True)
class IntentNode(Node): intent: Optional[str]
@dataclass(slots=True)
class ImportNode(IntentNode): imports: Optional[list[str]]
@dataclass(slots=True)
class Framework(Node): value: Literal["react", "vue", "angular", "svelte", "django"] | str = "react"
@dataclass(slots=True)
class Engine(Node): value: str
@dataclass(slots=True)
class Provider(Node): value: str
@dataclass(slots=True)
class API(Node): value: str
@dataclass(slots=True)
class Frontend(IntentNode): framework: Framework | None = None
@dataclass(slots=True)
class Backend(IntentNode): framework: Framework | None = None; api: API | None = None
@dataclass(slots=True)
class Database(IntentNode): engine: Engine | None = None
@dataclass(slots=True)
class Cache(IntentNode): engine: Engine | None = None
@dataclass(slots=True)
class Storage(IntentNode): provider: Provider | None = None
@dataclass(slots=True)
class System(IntentNode):
    frontend: Frontend | None = None; backend: Backend | None = None; database: Database | None = None; cache: Cache | None = None; storage: Storage | None = None

@dataclass(slots=True)
class App(ImportNode):
    name: str; pages: list["Page"] = field(default_factory=list); system: System | None = None
    target: Literal["web", "mobile"] | str = "web"; models: "Models" | None = None; routes: "Routes" | None = None
    permissions: "Permissions" | None = None; auth: "Auth" | None = None

@dataclass(slots=True)
class Page(ImportNode):
    name: str; theme: Optional[str] = None; hero: Optional["Hero"] = None; sections: list["Section"] = field(default_factory=list)
@dataclass(slots=True)
class Hero(IntentNode):
    name: str; image: Optional[str] = None; headline: Optional[str] = None; subtitle: Optional[str] = None; action: Optional[str] = None
@dataclass(slots=True)
class Section(ImportNode):
    name: str; sections: list["Section"] = field(default_factory=list); image: Optional[str] = None; headline: Optional[str] = None; subtitle: Optional[str] = None; action: Optional[str] = None

@dataclass(slots=True)
class Field(Node):
    name: str; type: str; primary: bool = False; required: bool = False; unique: bool = False; readonly: bool = False; nullable: bool = False
    default: object | None = None; min: object | None = None; max: object | None = None; min_len: int | None = None; max_len: int | None = None
@dataclass(slots=True)
class Relationship(Node): kind: str; target: str
@dataclass(slots=True)
class Action(Node): kind: str; target: str
@dataclass(slots=True)
class Model(ImportNode):
    name: str; fields: list[Field] = field(default_factory=list); relationships: list[Relationship] = field(default_factory=list); actions: list[Action] = field(default_factory=list)
@dataclass(slots=True)
class Models(IntentNode): models: list[Model] = field(default_factory=list)
@dataclass(slots=True)
class Route(ImportNode): name: str; path: str | None = None; page: str | None = None; auth: str | None = None
@dataclass(slots=True)
class Routes(IntentNode): routes: list[Route] = field(default_factory=list)

@dataclass(slots=True)
class Permission(ImportNode):
    name: str; resource: str | None = None; action: str | None = None
@dataclass(slots=True)
class PermissionRole(ImportNode):
    name: str; inherits: list[str] = field(default_factory=list); actions: list[Action] = field(default_factory=list); permissions: list[str] = field(default_factory=list)
@dataclass(slots=True)
class Permissions(IntentNode):
    roles: list[PermissionRole] = field(default_factory=list); permissions: list[Permission] = field(default_factory=list)

@dataclass(slots=True)
class AuthProvider(Node): value: str
@dataclass(slots=True)
class RegistrationConfig(IntentNode):
    enabled: bool = True; verification: str | None = None
@dataclass(slots=True)
class LoginConfig(IntentNode):
    allow: list[str] = field(default_factory=list); remember_me: bool = False
@dataclass(slots=True)
class LogoutConfig(IntentNode): enabled: bool = True
@dataclass(slots=True)
class PasswordRecoveryConfig(IntentNode):
    enabled: bool = True; method: str | None = None; reset: bool = True
@dataclass(slots=True)
class VerificationConfig(IntentNode):
    enabled: bool = True; method: str | None = None
@dataclass(slots=True)
class SessionConfig(IntentNode):
    timeout: str | None = None; multiple_devices: bool = False
@dataclass(slots=True)
class MFAConfig(IntentNode):
    enabled: bool = False; method: str | None = None
@dataclass(slots=True)
class Auth(IntentNode):
    providers: list[AuthProvider] = field(default_factory=list)
    registration: RegistrationConfig | None = None; login: LoginConfig | None = None; logout: LogoutConfig | None = None
    password_recovery: PasswordRecoveryConfig | None = None; verification: VerificationConfig | None = None
    session: SessionConfig | None = None; mfa: MFAConfig | None = None
