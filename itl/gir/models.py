from dataclasses import dataclass, field
from typing import Optional

@dataclass(slots=True)
class GIRNode: intent: str | None
@dataclass(slots=True)
class GIRApplication(GIRNode):
    name: str; target: str; system: Optional["GIRSystem"] = None; pages: list["GIRPage"] = field(default_factory=list)
    models: list["GIRModel"] = field(default_factory=list); routes: list["GIRRoute"] = field(default_factory=list)
    permissions: list["GIRPermissionRole"] = field(default_factory=list); permission_definitions: list["GIRPermission"] = field(default_factory=list); auth: Optional["GIRAuth"] = None
@dataclass(slots=True)
class GIRPage(GIRNode): name: str; theme: str | None = None; components: list[GIRNode] = field(default_factory=list)
@dataclass(slots=True)
class GIRHero(GIRNode): name: str; image: str | None = None; headline: str | None = None; subtitle: str | None = None; action: str | None = None
@dataclass(slots=True)
class GIRSection(GIRNode): name: str; children: list["GIRSection"] = field(default_factory=list)
@dataclass(slots=True)
class GIRField:
    name: str; type: str; primary: bool = False; required: bool = False; unique: bool = False; readonly: bool = False; nullable: bool = False; default: object | None = None; min: object | None = None; max: object | None = None; min_len: int | None = None; max_len: int | None = None
@dataclass(slots=True)
class GIRRelationship: kind: str; target: str
@dataclass(slots=True)
class GIRAction: kind: str; target: str
@dataclass(slots=True)
class GIRModel:
    name: str; fields: list[GIRField] = field(default_factory=list); relationships: list[GIRRelationship] = field(default_factory=list); actions: list[GIRAction] = field(default_factory=list)
@dataclass(slots=True)
class GIRRoute: name: str; path: str | None = None; page: str | None = None; auth: str | None = None
@dataclass(slots=True)
class GIRPermission: name: str; resource: str; action: str; intent: str | None = None
@dataclass(slots=True)
class GIRPermissionRole:
    name: str; inherits: list[str] = field(default_factory=list); actions: list[GIRAction] = field(default_factory=list); permissions: list[str] = field(default_factory=list); intent: str | None = None
@dataclass(slots=True)
class GIRAuthProvider: value: str
@dataclass(slots=True)
class GIRRegistration: enabled: bool; verification: str | None = None; intent: str | None = None
@dataclass(slots=True)
class GIRLogin: allow: list[str] = field(default_factory=list); remember_me: bool = False; intent: str | None = None
@dataclass(slots=True)
class GIRLogout: enabled: bool = True; intent: str | None = None
@dataclass(slots=True)
class GIRPasswordRecovery: enabled: bool = True; method: str | None = None; reset: bool = True; intent: str | None = None
@dataclass(slots=True)
class GIRVerification: enabled: bool = True; method: str | None = None; intent: str | None = None
@dataclass(slots=True)
class GIRSession: timeout: str | None = None; multiple_devices: bool = False; intent: str | None = None
@dataclass(slots=True)
class GIRMFA: enabled: bool = False; method: str | None = None; intent: str | None = None
@dataclass(slots=True)
class GIRAuth:
    intent: str | None = None; providers: list[GIRAuthProvider] = field(default_factory=list); registration: GIRRegistration | None = None; login: GIRLogin | None = None; logout: GIRLogout | None = None; password_recovery: GIRPasswordRecovery | None = None; verification: GIRVerification | None = None; session: GIRSession | None = None; mfa: GIRMFA | None = None
@dataclass(slots=True)
class GIRSystem(GIRNode):
    frontend: str | None = None; backend: str | None = None; api: str | None = None; database: str | None = None; cache: str | None = None; storage: str | None = None
