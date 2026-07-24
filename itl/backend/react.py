import json
import subprocess

from .base import Backend


class ReactBackend(Backend):

    @property
    def name(self) -> str:
        return 'react'

    def generate(self, project, output):

        root = output / self.name

        root.mkdir(parents=True, exist_ok=True)

        (root / "src").mkdir(exist_ok=True)

        self.package_json(root)

        self.index_html(root)

        self.main_tsx(root)

        self.vite_config(root)

        self.tsconfig(root)

        pages_dir = root / "src" / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)

        for page in project.pages:
            self.page(page, pages_dir)

        self.app_tsx(root, project)

        subprocess.run(
            ["npm", "install"],
            cwd=root,
            check=True
        )

        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=root
        )
    
    def package_json(self, root):

        package = {
            "name": "itl-app",
            "private": True,
            "version": "0.1.0",
            "scripts": {
                "dev": "vite",
                "build": "vite build"
            },
            "dependencies": {
                "react": "^19.0.0",
                "react-dom": "^19.0.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^7.0.0"
            }
        }

        with open(root / "package.json", "w") as f:
            json.dump(package, f, indent=4)
    
    def index_html(self, root):

        (root / "index.html").write_text(
            """<!DOCTYPE html>
            <html>
            <body>
            <div id="root"></div>
            <script type="module" src="/src/main.tsx"></script>
            </body>
            </html>
            """
        )
    
    def main_tsx(self, root):

        (root / "src" / "main.tsx").write_text(
            """
            import React from "react";
            import ReactDOM from "react-dom/client";
            import App from "./App";

            ReactDOM.createRoot(
                document.getElementById("root")!
            ).render(
                <App />
            );
            """
        )
    
    def app_tsx(self, root, project):

        imports = []

        routes = []

        for page in project.pages:

            component = page.name.title() + "Page"

            imports.append(
                f'import {component} from "./pages/{page.name}";'
            )

            routes.append(
                f"<{component} />"
            )

        code = f"""
    {"\n".join(imports)}

    export default function App() {{

        return (

            <>

                {"".join(routes)}

            </>

        );

    }}
    """

        (root / "src" / "App.tsx").write_text(code)
    
    def page(self, page, pages_dir):

        code = f"""
        export default function {page.name.title()}Page() {{

            return (

                <main>

                    {self.render_hero(page)}

                    {self.render_sections(page)}

                </main>

            );

        }}
        """

        (pages_dir / f"{page.name}.tsx").write_text(code)
    
    def render_hero(self, page):

        if page.hero is None:
            return ""

        hero = page.hero

        return f"""
        <section>

            <h1>{hero.headline}</h1>

            <p>{hero.subtitle}</p>

            <button>{hero.action}</button>

        </section>
        """
    
    def render_sections(self, page):

        html = ""

        for section in page.sections:

            html += f"""

            <section>

                <h2>{section.name.title()}</h2>

            </section>
            """

        return html
    
    def vite_config(self, root):

        (root / "vite.config.ts").write_text(
    """import { defineConfig } from 'vite'
    import react from '@vitejs/plugin-react'

    export default defineConfig({
        plugins: [react()],
    })
    """,
    encoding="utf-8"
        )
    
    def tsconfig(self, root):

        config = {
            "compilerOptions": {
                "target": "ES2020",
                "jsx": "react-jsx",
                "module": "ESNext",
                "moduleResolution": "Node"
            }
        }

        with open(root / "tsconfig.json", "w") as f:
            json.dump(config, f, indent=4)