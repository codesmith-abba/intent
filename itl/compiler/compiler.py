from .loader import ProjectLoader
from .resolver import ImportResolver
from itl.analyzer.analyzer import Analyzer
from itl.gir.builder import GIRBuilder


class Compiler:

    def __init__(self, root):

        self.loader = ProjectLoader(root)

        self.resolver = ImportResolver(self.loader)

        self.analyzer = Analyzer()

        self.builder = GIRBuilder()

    def compile(self):

        app = self.loader.load_app("app.itl")

        app = self.resolver.resolve(app)

        self.analyzer.analyze(app)

        gir = self.builder.build(app)

        return gir