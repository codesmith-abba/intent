# `theme`

The `theme` keyword specifies the preferred visual theme for a page.

A theme communicates the desired appearance of the page without defining colors, fonts, spacing, or other implementation details.

The compiler and selected backend determine how the theme is realized.

---

# Syntax

```itl
theme $ThemeName
```

Example:

```itl
theme $dark
```

---

# Purpose

The `theme` declaration expresses the intended visual appearance of a page.

It allows developers to describe whether a page should use a light, dark, or custom theme while keeping styling decisions independent of the language.

---

# Structure

```itl
theme $ThemeName
```

Where:

- `theme` is a reserved keyword.
- `$ThemeName` identifies the desired theme.

---

# Placement

A `theme` declaration may only appear inside a `page` declaration.

Example:

```itl
page $home {

    theme $dark

}
```

Using `theme` outside a page is invalid.

---

# Supported Themes

The compiler defines the themes supported by the selected backend.

Common themes include:

| Theme | Description |
|--------|-------------|
| `dark` | Dark appearance |
| `light` | Light appearance |
| `custom` | A user-defined theme |

Additional themes may be introduced by compiler backends or plugins.

---

# Required

A page does not require a theme.

If no theme is specified, the compiler or backend selects an appropriate default.

---

# Semantics

A theme expresses the preferred appearance of a page.

It does not define implementation details such as:

- colors
- typography
- spacing
- shadows
- animations

Instead, those details are determined by the selected backend or design system.

For example:

```itl
theme $dark
```

may produce different implementations across platforms while preserving the same intent.

---

# Compiler Behavior

When the compiler encounters a `theme` declaration it should:

1. Store the selected theme.
2. Validate that only one theme exists per page.
3. Pass the theme information to the selected backend.

The backend determines how the theme is implemented.

---

# Errors

## Missing Theme Name

Invalid:

```itl
theme
```

Compiler error:

```
Expected theme name.
```

---

## Duplicate Theme

Invalid:

```itl
page $home {

    theme $dark

    theme $light

}
```

Compiler error:

```
A page may contain only one theme declaration.
```

---

## Invalid Placement

Invalid:

```itl
app $Portfolio {

    theme $dark

}
```

Compiler error:

```
'theme' may only appear inside a page declaration.
```

---

## Unsupported Theme

Invalid:

```itl
theme $retro
```

Compiler error:

```
Unsupported theme 'retro'.
```

> **Note:** Compiler implementations may allow custom themes or plugins to register additional theme names.

---

# Examples

## Dark Theme

```itl
page $home {

    theme $dark

}
```

---

## Light Theme

```itl
page $home {

    theme $light

}
```

---

## Custom Theme

```itl
page $home {

    theme $custom

}
```

The compiler resolves the custom theme according to the active backend or project configuration.

---

# Notes

- A theme describes appearance, not styling.
- A page may contain at most one theme declaration.
- Themes are backend-independent.
- Different backends may implement the same theme differently.
- If no theme is declared, the compiler or backend applies a default theme.

---

# Version

Introduced in:

```
ITL 0.1
```