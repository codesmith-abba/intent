# Strings

A string represents textual data in Intent Language (ITL).

Unlike many programming languages, ITL uses the dollar (`$`) prefix to denote strings.

This keeps the language concise while avoiding the need for quotation marks in common cases.

---

# Syntax

Single-line string:

```itl
$Hello World
```

Example:

```itl
headline $Welcome to ITL
```

---

# Multi-line Strings

A multi-line string begins with `$(` and ends with `)`.

Everything between these delimiters is treated as a single string.

Example:

```itl
intent $(
    A modern portfolio website for an AI engineer.

    Showcase projects, skills,
    technical articles,
    and contact information.
)
```

---

# Purpose

Strings are used to represent textual values throughout ITL.

Common examples include:

- names
- titles
- descriptions
- paths
- identifiers
- semantic intent

---

# Single-line Strings

A single-line string begins with `$`.

Everything following the dollar sign until the end of the line is considered part of the string.

Example:

```itl
headline $Everything Fashion.
```

Value:

```
Everything Fashion.
```

Example:

```itl
framework $react
```

Value:

```
react
```

Leading whitespace after `$` is ignored.

---

# Multi-line Strings

Multi-line strings begin with:

```itl
$(
```

and end with:

```itl
)
```

Everything inside the block becomes a single string.

Example:

```itl
intent $(
    Build a modern marketplace
    connecting customers with tailors.
)
```

The compiler preserves line breaks while normalizing line endings.

---

# Escaping

Strings are intended to be written naturally.

Most characters do not require escaping.

Future versions of ITL may introduce escape sequences where necessary.

---

# Whitespace

For single-line strings:

```itl
headline $Hello World
```

produces

```
Hello World
```

For multi-line strings:

```itl
intent $(
    Hello

    World
)
```

the compiler preserves internal whitespace while trimming the surrounding delimiters.

---

# Examples

## Application Name

```itl
app $Portfolio {

}
```

---

## Theme

```itl
theme $dark
```

---

## Framework

```itl
framework $react
```

---

## Image Path

```itl
image $assets/hero.png
```

---

## Headline

```itl
headline $Build Software Faster
```

---

## Intent

```itl
intent $(
    Create a modern e-commerce application
    focused on simplicity and speed.
)
```

---

# Compiler Behavior

When the compiler encounters a single-line string it should:

1. Consume the `$` character.
2. Read until the end of the line.
3. Produce a single string token.

For a multi-line string the compiler should:

1. Consume `$(`.
2. Read until the matching `)`.
3. Preserve the contents.
4. Produce a single string token.

---

# Errors

## Missing String

Invalid:

```itl
headline
```

Compiler error:

```
Expected string.
```

---

## Unterminated Multi-line String

Invalid:

```itl
intent $(
    Hello
```

Compiler error:

```
Unterminated string.
```

---

# Notes

- Strings always begin with `$`.
- Single-line strings continue until the end of the line.
- Multi-line strings begin with `$(` and end with `)`.
- Quotation marks are not required.
- Strings may contain spaces and punctuation.
- The compiler interprets string values according to the surrounding declaration.

---

# Version

Introduced in:

```
ITL 0.1
```