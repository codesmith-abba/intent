# `app`

The `app` keyword defines the root of an Intent Language (ITL) application.

Every ITL program must contain exactly one `app` declaration.

The `app` block serves as the entry point of the application and provides the context in which all top-level declarations exist.

---

# Syntax

```itl
app $ApplicationName {

}
```

Example:

```itl
app $Portfolio {

}
```

---

# Purpose

The `app` keyword declares a new application.

Everything that belongs to an application must exist within its `app` block, either directly or through imported ITL source files.

No top-level declarations may exist outside an `app` declaration.

---

# Structure

```itl
app $ApplicationName {

    ...

}
```

Where:

- `app` is a reserved keyword.
- `$ApplicationName` is the application's name.
- `{}` defines the application's scope.

---

# Children

The following declarations are currently valid inside an `app` block.

| Keyword | Required | Description |
|---------|----------|-------------|
| `intent` | No | Describes the application's purpose. |
| `import` | No | Imports declarations from other ITL files. |
| `page` | No | Declares a page within the application. |
| `target` | Yes | Defines the compilation target. |
| `framework` | Yes | Defines the implementation framework. |

Future versions of ITL may introduce additional top-level declarations.

---

# Required

Every application must define:

- one `target`
- one `framework`

An application must also contain **at least one page after import resolution**.

Pages may be declared directly within the application or imported from other ITL source files.

---

# Optional

Applications may additionally contain:

- `import`
- `page`
- `assets` *(future)*
- `permissions` *(future)*
- `configuration` *(future)*

---

# Semantics

The `app` declaration creates the root node of the program.

During compilation, the compiler first resolves all imports before validating the application.

After import resolution, every top-level declaration becomes a child of the application's root node, regardless of which source file originally declared it.

Example:

```
App

├── Imports

├── Pages

├── Target

└── Framework
```

The `app` declaration itself does not directly generate code.

Instead, it provides the context from which the compiler builds the complete application.

---

# Compiler Behavior

When the compiler encounters an `app` declaration it should:

1. Create the application node.
2. Store the application name.
3. Parse top-level declarations.
4. Resolve imported ITL files.
5. Merge imported declarations into the application.
6. Validate the complete application.
7. Produce the root Intermediate Representation (IR).

---

# Errors

## Missing Application Name

Invalid:

```itl
app {

}
```

Compiler error:

```
Expected application name.
```

---

## Missing Opening Brace

Invalid:

```itl
app $Portfolio
```

Compiler error:

```
Expected '{' after application name.
```

---

## Multiple Applications

Invalid:

```itl
app $One {}

app $Two {}
```

Compiler error:

```
Only one application declaration is permitted.
```

---

## Missing Target

Invalid:

```itl
app $Portfolio {

    page $home {}

    framework $react
}
```

Compiler error:

```
Application must define a target.
```

---

## Missing Framework

Invalid:

```itl
app $Portfolio {

    page $home {}

    target $web
}
```

Compiler error:

```
Application must define a framework.
```

---

## No Pages After Import Resolution

Invalid:

```itl
app $Portfolio {

    target $web

    framework $react
}
```

Compiler error:

```
Application must contain at least one page after import resolution.
```

---

# Examples

## Minimal Application

```itl
app $Portfolio {

    page $home {}

    target $web

    framework $react
}
```

---

## Multiple Pages

```itl
app $Store {

    page $home {}

    page $products {}

    page $checkout {}

    target $web

    framework $react
}
```

---

## Using Imports

```itl
app $Portfolio {

    import all

    target $web

    framework $react
}
```

The compiler resolves `import all` before validation. If one or more imported files declare pages, the application is considered valid.

---

## Mixed Declarations

```itl
app $Portfolio {

    import $about

    page $home {}

    page $contact {}

    target $web

    framework $react
}
```

Pages may be declared both locally and through imports.

---

# Notes

- Every ITL program begins with exactly one `app` declaration.
- The `app` declaration defines the root scope of the application.
- Nested `app` declarations are not permitted.
- Imported declarations become part of the application during compilation.
- The compiler validates the complete application only after all imports have been resolved.

---

# Version

Introduced in:

```
ITL 0.1
```