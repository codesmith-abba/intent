# `page`

The `page` keyword defines a logical page within an ITL application.

A page represents a destination users can navigate to.

The compiler determines how a page is implemented for the selected target and framework.

---

# Syntax

```itl
page $PageName {

}
```

Example:

```itl
page $home {

}
```

---

# Purpose

The `page` declaration defines a distinct destination within an application.

A page groups together the content, components, and behavior associated with a particular part of the application.

The language defines the page's intent.

The compiler determines its implementation.

---

# Structure

```itl
page $PageName {

    ...

}
```

Where:

- `page` is a reserved keyword.
- `$PageName` uniquely identifies the page.
- `{}` defines the page's scope.

---

# Placement

A `page` declaration may appear:

- directly inside an `app` declaration
- inside an imported ITL file

A page may not be declared inside another page or component.

---

# Children

The following declarations are currently valid inside a page.

| Keyword | Required | Description |
|---------|----------|-------------|
| `theme` | No | Defines the page's theme. |
| `hero` | No | Defines the primary introductory content. |
| `section` | No | Defines a logical section of the page. |

Future versions may introduce additional page-level declarations.

---

# Required

A page declaration requires:

- a page name

All child declarations are optional.

---

# Optional

A page may contain:

- `theme`
- `hero`
- `section`

Future versions may support:

- layout
- navigation
- metadata
- permissions
- animations

---

# Semantics

A page represents a navigable destination within an application.

Its meaning is independent of any particular framework.

For example:

Web

```
page $about
```

may become

```
/about
```

React Native

```
page $about
```

may become

```
AboutScreen
```

Flutter

```
page $about
```

may become

```
AboutPage
```

The page's intent remains unchanged.

---

# Compiler Behavior

When the compiler encounters a `page` declaration it should:

1. Create a page node.
2. Store the page name.
3. Parse child declarations.
4. Validate page contents.
5. Add the page to the application.

---

# Errors

## Missing Page Name

Invalid:

```itl
page {

}
```

Compiler error:

```
Expected page name.
```

---

## Duplicate Page

Invalid:

```itl
page $home {}

page $home {}
```

Compiler error:

```
Duplicate page 'home'.
```

---

## Invalid Placement

Invalid:

```itl
page $home {

    page $about {}

}
```

Compiler error:

```
A page cannot be declared inside another page.
```

---

## Multiple Heroes

Invalid:

```itl
page $home {

    hero $main {}

    hero $secondary {}

}
```

Compiler error:

```
A page may contain only one hero.
```

---

# Examples

## Minimal Page

```itl
page $home {

}
```

---

## Page With Theme

```itl
page $home {

    theme $dark
}
```

---

## Page With Hero

```itl
page $home {

    hero $main {

        headline $Welcome

        subtitle $Build with intent.
    }
}
```

---

## Complete Page

```itl
page $home {

    theme $dark

    hero $main {

        headline $Everything Fashion.

        subtitle $Buy from trusted tailors.

        action $Start Shopping
    }

    section $featured {}

    section $categories {}

    section $footer {}
}
```

---

## Imported Page

```itl
page $about {

    hero $intro {

        headline $About Us
    }

}
```

```itl
app $Portfolio {

    import $about

    target $web

    framework $react
}
```

After import resolution, the `about` page becomes part of the application.

---

# Notes

- A page represents a logical destination, not a specific implementation.
- Pages may be declared locally or imported from other ITL files.
- Page names should be unique within an application after import resolution.
- A page may contain at most one hero.
- A page may contain zero or more sections.

---

# Version

Introduced in:

```
ITL 0.1
```