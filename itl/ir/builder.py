from .models import (
    IRApplication,
    IRPage,
    IRHero,
    IRSection,
)


class IRBuilder:

    def build(self, app):

        ir = IRApplication(
            name=app.name,
            target=app.target,
            framework=app.framework,
        )

        for page in app.pages:

            ir.pages.append(
                self.page(page)
            )

        return ir
    
    def page(self, page):

        ir_page = IRPage(
            name=page.name,
            theme=page.theme,
        )

        if page.hero:

            ir_page.hero = self.hero(
                page.hero
            )

        for section in page.sections:

            ir_page.sections.append(
                self.section(section)
            )

        return ir_page
    
    def hero(self, hero):

        return IRHero(
            image=hero.image,
            headline=hero.headline,
            subtitle=hero.subtitle,
            action=hero.action,
        )
    
    def section(self, section):

        return IRSection(
            name=section.name
        )