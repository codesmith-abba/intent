from .models import (
    GIRApplication, GIRPage, GIRHero, GIRSection, GIRSystem,
    GIRModel, GIRField, GIRRelationship, GIRAction, GIRRoute, GIRPermissionRole,
)


class GIRBuilder:
    def build(self, app):
        return self.application(app)

    def application(self, app):
        return GIRApplication(
            name=app.name,
            intent=app.intent,
            target=app.target,
            system=self.system(app.system),
            pages=[self.page(page) for page in app.pages],
            models=[self.model(model) for model in app.models.models] if app.models else [],
            routes=[self.route(route) for route in app.routes.routes] if app.routes else [],
            permissions=[self.permission_role(role) for role in app.permissions.roles] if app.permissions else [],
        )

    def page(self, page):
        gir = GIRPage(name=page.name, intent=page.intent, theme=page.theme)
        if page.hero:
            gir.components.append(self.hero(page.hero))
        for section in page.sections:
            gir.components.append(self.section(section))
        return gir

    def hero(self, hero):
        return GIRHero(name=hero.name, intent=hero.intent, image=hero.image, headline=hero.headline, subtitle=hero.subtitle, action=hero.action)

    def section(self, section):
        gir = GIRSection(name=section.name, intent=section.intent)
        for child in section.sections:
            gir.children.append(self.section(child))
        return gir

    def model(self, model):
        return GIRModel(
            name=model.name,
            fields=[GIRField(name=f.name, type=f.type, primary=f.primary, required=f.required, unique=f.unique, readonly=f.readonly, nullable=f.nullable, default=f.default, min=f.min, max=f.max, min_len=f.min_len, max_len=f.max_len) for f in model.fields],
            relationships=[GIRRelationship(kind=r.kind, target=r.target) for r in model.relationships],
            actions=[GIRAction(kind=a.kind, target=a.target) for a in model.actions],
        )

    def route(self, route):
        return GIRRoute(name=route.name, path=route.path, page=route.page, auth=route.auth)

    def permission_role(self, role):
        return GIRPermissionRole(name=role.name, inherits=list(role.inherits), actions=[GIRAction(kind=a.kind, target=a.target) for a in role.actions])

    def system(self, system):
        if system is None:
            return None
        return GIRSystem(
            intent=system.intent or None,
            frontend=system.frontend.framework.value if system.frontend else None,
            backend=system.backend.framework.value if system.backend else None,
            api=system.backend.api.value if system.backend and system.backend.api else None,
            database=system.database.engine.value if system.database else None,
            cache=system.cache.engine.value if system.cache else None,
            storage=system.storage.provider.value if system.storage else None,
        )
