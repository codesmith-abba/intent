# Intermediate Representation (IR)

The Intermediate Representation (IR) is the compiler's internal representation of a validated ITL application.

It is produced after semantic analysis and serves as the input to backend generators.

The IR is independent of any specific framework or programming language.

---

# Purpose

The IR provides a stable, implementation-independent model of an application.

Its primary purposes are:

- separating language analysis from code generation
- simplifying backend development
- enabling multiple backends to share the same compiler
- providing a normalized representation of the application

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
Abstract Syntax Tree (AST)
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

---

# AST vs IR

The Abstract Syntax Tree (AST) represents the source code as written by the developer.

The IR represents the application after semantic validation.

The IR removes syntax-specific details and exposes only the information required by backend generators.

---

# Example

ITL Source:

```itl
app $Portfolio {

    page $home {

        theme $dark

        hero $main {

            image $assets/hero.png

            headline $Welcome

        }

    }

    target $web

    framework $react
}
```

AST (simplified):

```
App
├── Page
│   ├── Theme
│   ├── Hero
│   │   ├── Image
│   │   └── Headline
├── Target
└── Framework
```

IR (simplified):

```
Application
├── name = Portfolio
├── target = web
├── framework = react
└── pages
    └── home
        ├── theme = dark
        └── hero
            ├── image = assets/hero.png
            └── headline = Welcome
```

---

# Responsibilities

The IR should:

- contain only validated data
- be independent of source syntax
- preserve application structure
- expose information required by backends
- remain stable across compiler implementations

---

# Compiler Behavior

After successful semantic analysis, the compiler:

1. Traverses the AST.
2. Creates IR objects.
3. Copies validated information into the IR.
4. Removes syntax-specific details.
5. Produces a backend-independent representation.

---

# Backend Consumption

Backends consume the IR to generate projects.

For example:

```
IR
 │
 ├── React Backend
 │       │
 │       ▼
 │   React Project
 │
 ├── Django Backend
 │       │
 │       ▼
 │   Django Project
 │
 └── Flutter Backend
         │
         ▼
     Flutter Project
```

Each backend reads the same IR.

---

# IR Structure

An IR typically contains:

- application metadata
- pages
- themes
- heroes
- sections
- image sources
- intent blocks
- target
- framework

Future versions may include:

- plugins
- runtime metadata
- permissions
- configuration
- AI metadata

---

# Benefits

Using an Intermediate Representation provides several advantages:

- backend independence
- cleaner compiler architecture
- easier testing
- reusable compiler logic
- simpler backend development
- improved maintainability

---

# Notes

- The IR is generated after semantic analysis.
- The IR is consumed by backend generators.
- The IR is framework-independent.
- The IR contains only validated application data.
- Source code is never generated directly from the AST.

---

# Version

Introduced in:

```
ITL 0.1
```