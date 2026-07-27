# `section`

The `section` keyword defines a logical section within a page.

A section groups related content together, allowing the compiler to organize the page into meaningful areas without exposing implementation details.

The compiler determines how each section is implemented for the selected target and framework.

---

# Syntax

```itl
section $SectionName {

}
```

Example:

```itl
section $about {

}
```

---

# Purpose

The `section` declaration identifies a logical portion of a page.

It provides structure to an application while allowing the compiler to determine the most appropriate implementation.

A section represents **what** the content is, not **how** it should appear.

---

# Structure

```itl
section $SectionName {

    ...

}
```

Where:

- `section` is a reserved keyword.
- `$SectionName` uniquely identifies the section within the page.
- `{}` defines the section's scope.

---

# Placement

A `section` declaration may only appear inside a `page`.

Example:

```itl
page $home {

    section $about {

    }

}
```

Using `section` outside a page is invalid.

---

# Children

The following declarations are currently supported inside a section.

| Keyword | Required | Description |
|---------|----------|-------------|
| *(none)* | — | Sections are currently empty containers. |

Future versions of ITL will allow sections to contain additional declarations such as components, layouts, media, and interactive elements.

---

# Required

A section declaration requires:

- a section name

No child declarations are currently required.

---

# Optional

A section may currently have an empty body.

Future versions may introduce support for:

- text
- image
- gallery
- cards
- features
- pricing
- testimonials
- forms
- custom components

---

# Semantics

A section represents a logical grouping of related content.

Its name communicates the purpose of the content rather than its presentation.

For example:

```itl
section $about
```

expresses that this part of the page contains information about the application or organization.

Likewise,

```itl
section $projects
```

indicates a collection of projects, regardless of how they are displayed.

The compiler determines the final implementation.

---

# Compiler Behavior

When the compiler encounters a `section` declaration it should:

1. Create a section node.
2. Store the section name.
3. Parse child declarations.
4. Add the section to the current page.
5. Preserve declaration order.

Sections should appear in the generated application in the same order they are declared.

---

# Errors

## Missing Section Name

Invalid:

```itl
section {

}
```

Compiler error:

```
Expected section name.
```

---

## Invalid Placement

Invalid:

```itl
app $Portfolio {

    section $about {

    }

}
```

Compiler error:

```
'section' may only appear inside a page.
```

---

## Duplicate Section Name

Invalid:

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

---

# Examples

## Empty Section

```itl
section $about {

}
```

---

## Multiple Sections

```itl
page $home {

    section $hero {}

    section $about {}

    section $projects {}

    section $contact {}

    section $footer {}

}
```

---

## Imported Page

```itl
page $about {

    section $company {}

    section $team {}

}
```

When imported into an application, these sections become part of the page as if they were declared locally.

---

# Notes

- A section is a logical grouping of related content.
- Sections do not define layout or styling.
- The compiler determines how sections are implemented.
- Sections preserve declaration order.
- Section names should be unique within a page.

---

# Version

Introduced in:

```
ITL 0.1
```