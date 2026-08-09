from .models import (
    GIRApplication,
    GIRPage,
    GIRHero,
    GIRSection,
    GIRSystem,
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
            pages=[
                self.page(page)
                for page in app.pages
            ],
        )

    def page(self, page):

        gir = GIRPage(
            name=page.name,
            intent=page.intent,
            theme=page.theme,
        )

        if page.hero:
            gir.components.append(
                self.hero(page.hero)
            )

        for section in page.sections:
            gir.components.append(
                self.section(section)
            )

        return gir

    def hero(self, hero):

        return GIRHero(
            name=hero.name,
            intent=hero.intent,
            image=hero.image,
            headline=hero.headline,
            subtitle=hero.subtitle,
            action=hero.action,
        )

    def section(self, section):

        gir = GIRSection(
            name=section.name,
            intent=section.intent,
        )

        for child in section.sections:
            gir.children.append(
                self.section(child)
            )

        return gir

    def system(self, system):

        if system is None:
            return None

        return GIRSystem(
            intent=system.intent or None,
            frontend=(
                system.frontend.framework.value
                if system.frontend else None
            ),
            backend=(
                system.backend.framework.value
                if system.backend else None
            ),
            api=(
                system.backend.api.value
                if system.backend and system.backend.api else None
            ),
            database=(
                system.database.engine.value
                if system.database else None
            ),
            cache=(
                system.cache.engine.value
                if system.cache else None
            ),
            storage=(
                system.storage.provider.value
                if system.storage else None
            ),
        )