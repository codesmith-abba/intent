from .loader import ProjectLoader
from .resolver import ImportResolver
from itl.analyzer.analyzer import Analyzer


class Compiler:

    def __init__(self, root):

        self.loader = ProjectLoader(root)

        self.resolver = ImportResolver(self.loader)

        self.analyzer = Analyzer()

    def compile(self):

        app = self.loader.load_app("app.itl")

        app = self.resolver.resolve(app)

        app = self.analyzer.analyze(app)

        return app