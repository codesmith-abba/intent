# `framework`

The `framework` keyword specifies the implementation framework the compiler should target.

While an ITL application describes **intent**, the `framework` declaration tells the compiler which implementation technology should be generated.

---

# Syntax

```itl
framework $FrameworkName
```

Example:

```itl
framework $react
```

---

# Purpose

The `framework` keyword selects the framework that will receive the generated implementation.

It does not change the application's intent.

Instead, it determines how the compiler transforms the application's Intermediate Representation (IR) into executable source code.

---

# Structure

```itl
framework $FrameworkName
```

Where:

- `framework` is a reserved keyword.
- `$FrameworkName` is a string identifying the desired framework.

---

# Placement

The `framework` declaration may only appear directly inside an `app` block.

Example:

```itl
app $Portfolio {

    framework $react
}
```

Using `framework` inside any other declaration is invalid.

---

# Supported Frameworks

The compiler determines which frameworks are available.

Examples include:

| Framework | Description |
|-----------|-------------|
| `react` | React web application |
| `next` | Next.js application |
| `django` | Django project |
| `fastapi` | FastAPI backend |
| `flutter` | Flutter application *(future)* |
| `react-native` | React Native application *(future)* |

The list of supported frameworks may grow over time.

---

# Required

Every application must define exactly one `framework`.

---

# Semantics

The `framework` declaration determines which backend is responsible for generating the implementation.

Example:

```itl
framework $react
```

Compilation:

```
ITL

↓

IR

↓

React Backend

↓

React Project
```

Changing only the framework changes the generated implementation while preserving the application's intent.

Example:

```itl
framework $django
```

Compilation:

```
ITL

↓

IR

↓

Django Backend

↓

Django Project
```

---

# Compiler Behavior

When the compiler encounters a `framework` declaration it should:

1. Validate the framework name.
2. Verify that a matching backend exists.
3. Store the selected framework.
4. Pass the Intermediate Representation (IR) to the selected backend.

---

# Errors

## Missing Framework

Invalid:

```itl
app $Portfolio {

    target $web
}
```

Compiler error:

```
Application must define a framework.
```

---

## Multiple Frameworks

Invalid:

```itl
app $Portfolio {

    framework $react

    framework $django
}
```

Compiler error:

```
Only one framework declaration is permitted.
```

---

## Unsupported Framework

Invalid:

```itl
framework $unknown
```

Compiler error:

```
Unsupported framework 'unknown'.
```

---

## Invalid Placement

Invalid:

```itl
page $home {

    framework $react
}
```

Compiler error:

```
'framework' may only appear inside an application declaration.
```

---

# Examples

## React

```itl
app $Portfolio {

    page $home {}

    target $web

    framework $react
}
```

---

## Next.js

```itl
app $Store {

    page $home {}

    target $web

    framework $next
}
```

---

## Django

```itl
app $Dashboard {

    page $home {}

    target $web

    framework $django
}
```

---

# Notes

- The `framework` declaration affects only the generated implementation.
- It does not change the application's intent.
- Every application must define exactly one framework.
- Framework support depends on the compiler installation and available backends.

---

# Version

Introduced in:

```
ITL 0.1
```