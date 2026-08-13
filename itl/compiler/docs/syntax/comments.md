# Comments

Comments allow developers to document ITL source code without affecting compilation.

Comments are ignored by the compiler and are not included in the generated application.

They are intended to improve readability, explain intent, and temporarily disable code during development.

---

# Purpose

Comments help developers:

- explain code
- describe design decisions
- organize source files
- leave notes for collaborators
- temporarily disable declarations

Comments have no effect on the compiled output.

---

# Single-line Comments

A single-line comment begins with:

```itl
//
```

Everything following `//` until the end of the line is ignored.

Example:

```itl
// Homepage

page $home {

}
```

Another example:

```itl
hero $main {

    // Main banner image
    image $assets/banner.png

}
```

---

# Commenting Out Code

Entire declarations may be disabled by commenting each line.

Example:

```itl
// page $pricing {
//
// }
```

The compiler ignores all commented lines.

---

# Placement

Comments may appear almost anywhere outside string literals.

Example:

```itl
app $Portfolio {

    // Main application page
    page $home {

        // Site theme
        theme $dark

    }

    // Target platform
    target $web

    framework $react
}
```

---

# Comments Inside Multi-line Strings

Comments inside a multi-line string are treated as plain text.

Example:

```itl
intent $(
This line is part of the string.

// This is NOT a comment.

Everything inside this block is preserved.
)
```

The compiler does not interpret `//` inside a string as a comment.

---

# Compiler Behavior

When the lexer encounters:

```itl
//
```

it should:

1. Consume the `//` marker.
2. Ignore every character until the end of the current line.
3. Resume scanning on the following line.

Comments do not produce tokens.

---

# Future Comment Types

Future versions of ITL may support additional comment forms.

For example:

Block comments:

```itl
/*
    Multi-line comment
*/
```

Documentation comments:

```itl
///
/// Generates the application's homepage.
```

These comment styles are not part of ITL 0.1.

---

# Examples

## Documenting a Page

```itl
// Landing page
page $home {

}
```

---

## Documenting a Hero

```itl
hero $main {

    // Hero background image
    image $assets/hero.png

}
```

---

## Documenting an Import

```itl
// Shared footer
import $footer
```

---

# Notes

- Comments are ignored during compilation.
- Comments do not generate tokens.
- Comments may appear almost anywhere outside string literals.
- Single-line comments begin with `//`.
- Block comments are reserved for a future version of ITL.

---

# Version

Introduced in:

```
ITL 0.1
```