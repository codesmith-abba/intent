# `target`

The `target` keyword specifies the platform for which an ITL application should be generated.

While the application describes **intent**, the target defines the execution environment.

The selected target determines which compiler backends are compatible with the application.

---

# Syntax

```itl
target $TargetName
```

Example:

```itl
target $web
```

---

# Purpose

The `target` declaration specifies the platform on which the generated application is intended to run.

It does not describe how the application is implemented.

Instead, it identifies the execution environment, allowing the compiler to select compatible backends and runtime behavior.

---

# Structure

```itl
target $TargetName
```

Where:

- `target` is a reserved keyword.
- `$TargetName` identifies the intended execution platform.

---

# Placement

A `target` declaration may only appear directly inside an `app` declaration.

Example:

```itl
app $Portfolio {

    target $web

}
```

Using `target` anywhere else is invalid.

---

# Supported Targets

The compiler determines which targets are available.

Examples include:

| Target | Description |
|---------|-------------|
| `web` | Browser-based applications |
| `mobile` | Mobile applications |
| `desktop` | Desktop applications |
| `server` | Server-side applications |
| `embedded` | Embedded systems *(future)* |
| `robotics` | Robotics applications *(future)* |

The list of supported targets may expand as the language evolves.

---

# Required

Every application must define exactly one `target`.

---

# Semantics

The `target` declaration identifies the execution environment for the application.

It influences backend selection, runtime capabilities, and generated project structure.

For example:

```itl
target $web
framework $react
```

Compilation:

```
ITL

↓

IR

↓

Web Target

↓

React Backend

↓

React Application
```

Changing the target changes the class of application being generated.

Example:

```itl
target $mobile
framework $flutter
```

Compilation:

```
ITL

↓

IR

↓

Mobile Target

↓

Flutter Backend

↓

Flutter Application
```

The application's intent remains unchanged.

---

# Target and Framework Compatibility

Not every framework supports every target.

For example:

| Target | Compatible Frameworks |
|---------|-----------------------|
| `web` | `react`, `next`, `django`, `fastapi` |
| `mobile` | `flutter`, `react-native` |
| `desktop` | `tauri`, `electron` *(future)* |

The compiler validates compatibility during semantic analysis.

---

# Compiler Behavior

When the compiler encounters a `target` declaration it should:

1. Store the selected target.
2. Validate that the target is supported.
3. Verify compatibility with the selected framework.
4. Pass the target information to the backend.

---

# Errors

## Missing Target

Invalid:

```itl
app $Portfolio {

    framework $react

}
```

Compiler error:

```
Application must define a target.
```

---

## Multiple Targets

Invalid:

```itl
app $Portfolio {

    target $web

    target $mobile

}
```

Compiler error:

```
Only one target declaration is permitted.
```

---

## Unsupported Target

Invalid:

```itl
target $console
```

Compiler error:

```
Unsupported target 'console'.
```

---

## Invalid Placement

Invalid:

```itl
page $home {

    target $web

}
```

Compiler error:

```
'target' may only appear inside an application declaration.
```

---

## Incompatible Target and Framework

Invalid:

```itl
target $mobile

framework $react
```

Compiler error:

```
Framework 'react' does not support target 'mobile'.
```

---

# Examples

## Web Application

```itl
app $Portfolio {

    page $home {}

    target $web

    framework $react
}
```

---

## Mobile Application

```itl
app $Fitness {

    page $home {}

    target $mobile

    framework $flutter
}
```

---

## Server Application

```itl
app $API {

    page $root {}

    target $server

    framework $fastapi
}
```

---

# Notes

- A target defines **where** an application runs.
- A framework defines **how** the application is implemented.
- Every application must define exactly one target.
- The compiler validates compatibility between targets and frameworks.
- Adding new targets does not require changes to existing ITL programs.

---

# Version

Introduced in:

```
ITL 0.1
```