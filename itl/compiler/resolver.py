from itl.compiler.errors import ITLTypeError
from itl.parser.ast import App, Page, Section


class ImportResolver:

    def __init__(self, loader):

        self.loader = loader

        self.loaded: set[str] = set()

        self.MERGE_HANDLERS = {
            (App, Page): lambda app, page: app.pages.append(page),
            (Page, Section): lambda page, section: page.sections.append(section),
        }

    def resolve(self, app: App) -> App:

        self.resolve_node(app)

        return app

    def resolve_node(self, node):

        if not node.imports:
            return

        for import_name in node.imports:

            self.resolve_import(
                node,
                import_name,
            )

    def resolve_import(self, parent, name: str):

        if name in self.loaded:
            return

        self.loaded.add(name)

        module = self.loader.load_module(name)

        self.merge(parent, module)

        # Resolve nested imports recursively
        self.resolve_node(module)

    def merge(self, parent, node):

        handler = self.MERGE_HANDLERS.get(
            (type(parent), type(node))
        )

        if handler is None:

            raise ITLTypeError(
                f"Cannot merge "
                f"{type(node).__name__} "
                f"into "
                f"{type(parent).__name__}."
            )

        handler(parent, node)