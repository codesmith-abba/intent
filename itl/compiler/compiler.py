from .loader import ProjectLoader
from .resolver import ImportResolver


class Compiler:

    def __init__(self, root):

        self.loader = ProjectLoader(root)

        self.resolver = ImportResolver(self.loader)

    def compile(self):

        app = self.loader.load_app("app.itl")

        return self.resolver.resolve(app)