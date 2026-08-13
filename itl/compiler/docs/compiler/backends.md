# Backend

A backend transforms an Intermediate Representation (IR) into a concrete software project.

Unlike the parser or semantic analyzer, a backend does not understand ITL source code directly.

Instead, it consumes the IR produced by the compiler and generates code for a specific platform or framework.

---

# Purpose

The backend converts application intent into an executable project.

Its responsibilities include:

- generating project structure
- generating source code
- creating configuration files
- preparing assets
- integrating runtime requirements
- producing a runnable application

---

# Position in the Compiler

```
ITL Source
      │
      ▼
Lexer
      │
      ▼
Parser
      │
      ▼
AST
      │
      ▼
Semantic Analyzer
      │
      ▼
Intermediate Representation (IR)
      │
      ▼
Backend
      │
      ▼
Generated Project
```

The backend is the final stage of compilation.

---

# Backend Independence

Backends are independent of the language.

The compiler produces the same IR regardless of the selected backend.

For example:

```itl
app $Portfolio {

    page $home {

        hero $main {

        }

    }

    target $web

    framework $react
}
```

The compiler always produces the same IR.

Only the backend changes.

---

# Responsibilities

A backend is responsible for:

- interpreting the IR
- generating source files
- generating folders
- writing configuration files
- copying assets
- preparing runtime metadata

A backend should not perform semantic validation.

---

# Example

IR:

```
Application
│
├── Home Page
│
│   ├── Hero
│   └── Sections
│
├── Target = Web
└── Framework = React
```

React Backend:

```
.project/

    src/

        App.tsx

        pages/

        components/

    public/

    package.json

    vite.config.ts

    ...
```

Django Backend:

```
.project/

    manage.py

    settings.py

    urls.py

    templates/

    static/

    ...
```

Both consume the same IR.

---

# Backend Selection

The selected framework determines which backend is used.

Example:

```itl
framework $react
```

↓

```
ReactBackend
```

Example:

```itl
framework $django
```

↓

```
DjangoBackend
```

The compiler automatically selects the appropriate backend.

---

# Backend Interface

Every backend should expose a common interface.

Example:

```python
class Backend:

    def generate(self, ir):
        pass
```

Each backend implements this interface.

Example:

```python
class ReactBackend(Backend):

    def generate(self, ir):
        ...
```

---

# Generated Project

A backend generates a complete project.

Example:

```
.project/

    src/

    assets/

    package.json

    README.md

    ...
```

The generated project should be ready for development.

---

# Runtime Integration

A backend declares the runtime requirements needed to execute the generated project.

Example:

React Backend:

```
Runtime

Node.js

npm
```

Django Backend:

```
Runtime

Python

pip
```

The ITL Runtime prepares these automatically before development begins.

Backends describe their requirements—they do not install runtimes themselves.

---

# Assets

Backends determine how assets are organized.

Example:

```
assets/

images/

fonts/
```

The compiler records asset metadata.

The backend decides where assets are written.

---

# AI Integration

Backends may integrate AI capabilities.

For example:

- image generation
- content generation
- layout generation
- code refinement

These features are optional and backend-dependent.

---

# Extensibility

New backends may be added without modifying the language.

Examples include:

- React
- Vue
- Angular
- Svelte
- Django
- Flutter
- React Native
- Next.js

The compiler remains unchanged.

---

# Compiler Behavior

The compiler invokes exactly one backend for a compilation.

The backend:

1. receives the IR
2. generates project files
3. writes the project structure
4. prepares runtime metadata
5. completes generation

After generation, the project is ready for development.

---

# Notes

- Backends consume the IR.
- Backends do not parse ITL source files.
- Backends are independent of the parser and analyzer.
- Multiple backends may target the same platform.
- New backends can be added without changing the language.

---

# Version

Introduced in:

```
ITL 0.1
```