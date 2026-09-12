import json
import subprocess
from dataclasses import dataclass

from .base import Backend
from itl.gir.models import GIRHero, GIRSection


@dataclass(frozen=True, slots=True)
class ReactExecutionPolicy:
    """Controls external package/process execution during React generation."""

    install_dependencies: bool = False
    allow_install_scripts: bool = False
    start_dev_server: bool = False


class ReactBackend(Backend):

    @property
    def name(self) -> str:
        return "react"

    def generate(self, project, output, policy: ReactExecutionPolicy | None = None):
        policy = policy or ReactExecutionPolicy()
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

        if policy.install_dependencies:
            self.install_dependencies(root, allow_install_scripts=policy.allow_install_scripts)

        if policy.start_dev_server:
            if not (root / "node_modules").is_dir():
                self.install_dependencies(root, allow_install_scripts=policy.allow_install_scripts)
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=root,
                start_new_session=True,
            )

    def install_dependencies(self, root, *, allow_install_scripts: bool = False):
        command = ["npm", "install"]
        if not allow_install_scripts:
            command.append("--ignore-scripts")
        subprocess.run(command, cwd=root, check=True)

    def package_json(self, root):
        package = {
            "name": "itl-app",
            "private": True,
            "version": "0.1.0",
            "scripts": {"dev": "vite", "build": "vite build"},
            "dependencies": {"react": "^19.0.0", "react-dom": "^19.0.0"},
            "devDependencies": {"@vitejs/plugin-react": "^4.0.0", "vite": "^7.0.0"},
        }
        with open(root / "package.json", "w", encoding="utf-8") as f:
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
""",
            encoding="utf-8",
        )

    def main_tsx(self, root):
        (root / "src" / "main.tsx").write_text(
            """
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
""",
            encoding="utf-8",
        )

    def app_tsx(self, root, project):
        imports = []
        routes = []
        for page in project.pages:
            component = page.name.title() + "Page"
            imports.append(f'import {component} from "./pages/{page.name}";')
            routes.append(f"<{component} />")
        code = f"""
{"\n".join(imports)}

export default function App() {{
    return (<>{"".join(routes)}</>);
}}
"""
        (root / "src" / "App.tsx").write_text(code, encoding="utf-8")

    def page(self, page, pages_dir):
        code = f"""
export default function {page.name.title()}Page() {{
    return (
        <main>
            {self.render_components(page.components)}
        </main>
    );
}}
"""
        (pages_dir / f"{page.name}.tsx").write_text(code, encoding="utf-8")

    def render_components(self, components):
        return "".join(self.render_component(component) for component in components)

    def render_component(self, component):
        if isinstance(component, GIRHero):
            return self.render_hero(component)
        if isinstance(component, GIRSection):
            return self.render_section(component)
        return ""

    def render_hero(self, hero):
        return f"""
<section>
    <h1>{hero.headline or ""}</h1>
    <p>{hero.subtitle or ""}</p>
    <button>{hero.action or ""}</button>
</section>
"""

    def render_section(self, section):
        children = self.render_components(section.children)
        return f"""
<section>
    <h2>{section.name.title()}</h2>
    {children}
</section>
"""

    def vite_config(self, root):
        (root / "vite.config.ts").write_text(
            """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({ plugins: [react()] })
""",
            encoding="utf-8",
        )

    def tsconfig(self, root):
        config = {
            "compilerOptions": {
                "target": "ES2020",
                "jsx": "react-jsx",
                "module": "ESNext",
                "moduleResolution": "Node",
            }
        }
        with open(root / "tsconfig.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
