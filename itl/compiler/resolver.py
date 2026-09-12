from itl.compiler.errors import ITLTypeError
from itl.parser.ast import (
    App, Page, Section, Models, Routes, Permissions,
)


class ImportResolver:
    def __init__(self, loader):
        self.loader = loader
        self.loaded: set[str] = set()

    def resolve(self, app: App) -> App:
        self.resolve_node(app)
        return app

    def resolve_node(self, node):
        if not node.imports:
            return
        for import_name in node.imports:
            if import_name == "all" and isinstance(node, App):
                for name in self.loader.list_modules():
                    self.resolve_import(node, name)
                continue
            self.resolve_import(node, import_name)

    def resolve_import(self, parent, name: str):
        if name in self.loaded:
            return
        self.loaded.add(name)
        module = self.loader.load_module(name)
        self.merge(parent, module)
        self.resolve_node(module)

    def merge(self, parent, node):
        if isinstance(parent, App):
            if isinstance(node, Page):
                parent.pages.append(node)
            elif isinstance(node, Models):
                if parent.models is not None:
                    parent.models.models.extend(node.models)
                else:
                    parent.models = node
            elif isinstance(node, Routes):
                if parent.routes is not None:
                    parent.routes.routes.extend(node.routes)
                else:
                    parent.routes = node
            elif isinstance(node, Permissions):
                if parent.permissions is not None:
                    parent.permissions.roles.extend(node.roles)
                else:
                    parent.permissions = node
            else:
                raise ITLTypeError(f"Cannot merge {type(node).__name__} into App.")
            return

        if isinstance(parent, Page) and isinstance(node, Section):
            parent.sections.append(node)
            return

        raise ITLTypeError(f"Cannot merge {type(node).__name__} into {type(parent).__name__}.")
