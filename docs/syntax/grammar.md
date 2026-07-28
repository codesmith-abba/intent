# Grammar

Grammar defines how valid Intent Language (ITL) programs are structured.

It specifies how declarations are combined, how scopes are formed, and how a complete application is organized.

Grammar describes the structure of a program.

It does **not** define the meaning of the program. Semantic correctness is handled during semantic analysis.

---

# Program Structure

Every ITL program consists of one root application declaration.

Example:

```itl
app $Portfolio {

}
```

The application declaration forms the root of the program.

All other declarations belong directly or indirectly to this application.

---

# Declarations

A declaration introduces a language construct.

Examples include:

```itl
app

page

hero

section

intent

import

target

framework

theme
```

Each declaration has its own syntax and semantic rules.

---

# Scope

Some declarations create scopes.

A scope begins with:

```itl
{
```

and ends with:

```itl
}
```

Example:

```itl
page $home {

    hero $main {

    }

}
```

Child declarations belong to the scope in which they are declared.

---

# Hierarchy

Declarations are organized into a hierarchical tree.

Example:

```
App
│
├── Page
│   ├── Theme
│   ├── Hero
│   └── Section
│
├── Target
└── Framework
```

The compiler represents this hierarchy as an Abstract Syntax Tree (AST).

---

# Declaration Order

Declarations are parsed in the order they appear.

The compiler preserves declaration order whenever possible.

Example:

```itl
page $home {

    hero $main {}

    section $about {}

    section $projects {}

}
```

The generated application preserves this logical order unless the selected backend specifies otherwise.

---

# Strings

ITL supports two string forms.

Single-line strings:

```itl
headline $Welcome
```

Multi-line strings:

```itl
intent $(
    Welcome to Intent Language.
)
```

Everything after `$` (or inside `$(` `)`) is treated as a string.

---

# Imports

Imports insert declarations from another ITL source file into the current scope.

Example:

```itl
import $footer
```

If `footer.itl` contains:

```itl
section $footer {

}
```

the compiler behaves as though the section had been written directly in the importing scope.

Import resolution occurs before semantic analysis.

---

# Nesting

Only scoped declarations may contain child declarations.

Example:

```itl
page $home {

    hero $main {

    }

}
```

Invalid:

```itl
headline $Welcome {

}
```

Compiler error:

```
'headline' cannot contain child declarations.
```

---

# Whitespace

Outside of strings, whitespace has no semantic meaning.

The following programs are equivalent.

```itl
page $home {

    hero $main {

    }

}
```

```itl
page $home{
hero $main{
}
}
```

Consistent indentation is recommended for readability.

---

# Comments

Comments are ignored by the compiler.

Example:

```itl
// Homepage
page $home {

}
```

Comments do not affect parsing or code generation.

---

# Grammar and Semantics

Grammar determines whether a program is structurally valid.

For example:

```itl
page $home {

    hero $main {}

}
```

is grammatically valid.

Semantic analysis determines whether the program is meaningful.

Example:

```itl
page $home {

    hero $main {}

    hero $secondary {}

}
```

Although grammatically valid, this may be semantically invalid because a page currently allows only one hero.

---

# Language Processing

An ITL program is processed in several stages.

```
ITL Source Files
        │
        ▼
Import Resolution
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

Each stage transforms the program into a more refined representation.

---

# Notes

- Every ITL program has exactly one root application.
- Declarations define the structure of the program.
- Scoped declarations may contain child declarations.
- Imports are resolved before semantic analysis.
- Grammar defines structure.
- Semantic analysis defines correctness.

---

# Version

Introduced in:

```
ITL 0.1
```