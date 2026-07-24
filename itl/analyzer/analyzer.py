from .errors import SemanticError


class Analyzer:

    VALID_THEMES = {

        "dark",

        "light",

        "custom",
    }

    VALID_TARGETS = {

        "web",

        "mobile",

        "desktop",
    }
    VALID_FRAMEWORKS = {

        "react",

        "next",

        "vue",

        "django",
    }

    def analyze(self, app):

        self.app(app)

        return app
    
    def app(self, app):

        self.check_duplicate_pages(app)

        for page in app.pages:

            self.page(page)

        self.target(app.target)

        self.framework(app.framework)
    
    def check_duplicate_pages(self, app):

        seen = set()

        for page in app.pages:

            if page.name in seen:

                raise SemanticError(
                    f"Duplicate page '{page.name}'."
                )

            seen.add(page.name)
    
    def page(self, page):

        self.theme(page.theme)

        if page.hero:

            self.hero(page.hero)

        self.check_duplicate_sections(page)
    
    def theme(self, theme):

        if theme not in self.VALID_THEMES:

            raise SemanticError(
                f"Unknown theme '{theme}'."
            )
    
    def hero(self, hero):

        if not hero.headline:

            raise SemanticError(
                "Hero must contain a headline."
            )
    
    def check_duplicate_sections(self, page):

        seen = set()

        for section in page.sections:

            if section.name in seen:

                raise SemanticError(
                    f"Duplicate section '{section.name}' "
                    f"in page '{page.name}'."
                )

            seen.add(section.name)
    
    def target(self, target):

        if target not in self.VALID_TARGETS:

            raise SemanticError(
                f"Unknown target '{target}'."
            )
        
    def framework(self, framework):

        if framework not in self.VALID_FRAMEWORKS:

            raise SemanticError(
                f"Unknown framework '{framework}'."
            )