# Semantic Analyzer

The Semantic Analyzer verifies that a parsed ITL program is meaningful.

After the parser has constructed the Abstract Syntax Tree (AST), the analyzer traverses the tree and validates the program according to the language's semantic rules.

Unlike the parser, which checks syntax, the analyzer checks correctness.

---

# Purpose

The analyzer ensures that an ITL program is logically valid before code generation begins.

Its responsibilities include:

- validating declarations
- enforcing language rules
- detecting duplicate declarations
- validating declaration placement
- resolving imports
- validating references
- reporting semantic errors

If semantic analysis succeeds, the compiler produces an Intermediate Representation (IR).

---

# Position in the Compiler

```
Source Files
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
```

The analyzer is the final validation stage before code generation.

---

# Responsibilities

The analyzer is responsible for verifying:

- application structure
- declaration placement
- duplicate names
- import validity
- framework compatibility
- target compatibility
- future type rules
- backend requirements

---

# What the Analyzer Does

Given the following program:

```itl
app $Portfolio {

    page $home {

        hero $main {}

    }

    target $web

    framework $react
}
```

The analyzer verifies:

- exactly one application exists
- the page is valid
- the hero is valid inside a page
- the target is supported
- the framework is supported
- no duplicate declarations exist

If all checks succeed, semantic analysis completes successfully.

---

# Declaration Validation

Every declaration has semantic rules.

Example:

```itl
page $home {

    hero $main {}

}
```

The analyzer confirms that a `hero` declaration is permitted inside a `page`.

---

# Duplicate Detection

Example:

```itl
page $home {

    section $about {}

    section $about {}

}
```

Compiler error:

```
Duplicate section 'about'.
```

Duplicate declarations are rejected.

---

# Scope Validation

Declarations may only appear inside valid scopes.

Example:

```itl
framework $react {

}
```

Compiler error:

```
'framework' cannot contain child declarations.
```

---

# Import Validation

The analyzer validates imported declarations after import resolution.

Example:

```itl
page $home {

    import $footer

}
```

If `footer.itl` contains:

```itl
section $footer {

}
```

the import succeeds.

If it instead contains:

```itl
page $about {

}
```

Compiler error:

```
Cannot import 'page' into a page scope.
```

---

# Framework Validation

The analyzer verifies that the selected framework is compatible with the selected target.

Example:

```itl
target $web

framework $react
```

Valid.

Example:

```itl
target $mobile

framework $django
```

Compiler error:

```
Framework 'django' does not support target 'mobile'.
```

---

# Intent Validation

The analyzer verifies that `intent` blocks appear only where they are permitted.

Example:

```itl
hero $main {

    intent $(
        Create a modern landing page hero.
    )

}
```

Valid.

If an `intent` block appears in an unsupported declaration, the analyzer reports an error.

---

# Error Reporting

The analyzer should produce clear and actionable diagnostics.

Example:

```
Duplicate page 'home'.

First declared at line 4.

Second declared at line 18.
```

Diagnostics should include:

- error message
- declaration name
- source location
- suggestion when possible

---

# Compiler Behavior

The analyzer traverses the AST recursively.

For each declaration it:

1. validates placement
2. validates uniqueness
3. validates child declarations
4. validates references
5. records semantic information
6. reports any errors

Only semantically valid programs continue to IR generation.

---

# Future Responsibilities

As ITL evolves, the analyzer may also validate:

- plugin compatibility
- backend capabilities
- permissions
- configuration
- dependency graphs
- AI metadata
- runtime requirements

The analyzer should remain independent of backend implementations.

---

# Notes

- The analyzer operates on the AST.
- It does not generate code.
- It does not modify source files.
- It validates program meaning rather than syntax.
- Successful semantic analysis produces a valid program ready for IR generation.

---

# Version

Introduced in:

```
ITL 0.1
```