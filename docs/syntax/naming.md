# Naming

Naming defines how identifiers are written throughout Intent Language (ITL).

Consistent naming improves readability, tooling, diagnostics, and generated code.

Although many names are represented as strings, the compiler interprets them as identifiers within their respective declarations.

---

# Purpose

Naming conventions provide a predictable structure for applications.

The compiler uses identifiers to reference declarations, generate code, detect duplicates, and produce meaningful diagnostics.

---

# Naming Rules

Identifiers should:

- begin with a letter
- contain only letters and digits
- avoid spaces
- avoid punctuation
- be descriptive
- be unique within their scope

Examples:

Valid:

```itl
page $home

page $about

hero $main

section $projects

app $Portfolio
```

Invalid:

```itl
page $123home

page $home page

hero $main-hero

section $about!

app $My Portfolio
```

---

# Recommended Conventions

The following conventions are recommended throughout ITL.

| Declaration | Convention | Example |
|-------------|------------|---------|
| `app` | PascalCase | `Portfolio` |
| `page` | camelCase | `home` |
| `hero` | camelCase | `mainHero` |
| `section` | camelCase | `featuredProjects` |


These conventions improve readability but may not be strictly enforced by every compiler implementation.

---

# Scope

Identifiers must be unique within their scope.

Example:

Valid:

```itl
page $home {

    section $about

    section $projects

}
```

Invalid:

```itl
page $home {

    section $about

    section $about

}
```

Compiler error:

```
Duplicate section 'about'.
```

---

# Case Sensitivity

Identifiers are case-sensitive.

Example:

```itl
page $home

page $Home
```

These are considered different identifiers.

Compiler implementations may optionally warn about confusing names.

---

# Reserved Keywords

Reserved keywords cannot be used where the language expects a keyword.

Examples of reserved keywords include:

- app
- page
- hero
- section
- import
- target
- framework
- theme
- intent

---

# Examples

## Application

```itl
app $Portfolio
```

---

## Pages

```itl
page $home

page $about

page $contact
```

---

## Hero

```itl
hero $mainHero
```

---

## Sections

```itl
section $featuredProjects

section $customerReviews

section $contactForm
```

---

# Compiler Behavior

When the compiler reads an identifier it should:

1. Validate its syntax.
2. Validate uniqueness within the current scope.
3. Associate it with the enclosing declaration.
4. Preserve the original spelling.

---

# Errors

## Invalid Identifier

Invalid:

```itl
page $123home
```

Compiler error:

```
Invalid identifier.
```

---

## Duplicate Identifier

Invalid:

```itl
section $about

section $about
```

Compiler error:

```
Duplicate identifier 'about'.
```

---

# Notes

- Identifiers should clearly describe their purpose.
- Naming conventions improve readability and generated code.
- The compiler preserves the original identifier names.
- Identifiers are scoped to their enclosing declaration.

---

# Version

Introduced in:

```
ITL 0.1
```