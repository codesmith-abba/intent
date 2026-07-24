class Explainer:

    def explain(self, project):

        print("=" * 50)
        print("Intent Language")
        print("=" * 50)

        print(f"Application : {project.name}")
        print(f"Target      : {project.target}")
        print(f"Framework   : {project.framework}")

        print()

        for page in project.pages:

            print(f"Page : {page.name}")
            print(f"Theme: {page.theme}")

            if page.hero:

                print(f"Hero : {page.hero.headline}")

            print()