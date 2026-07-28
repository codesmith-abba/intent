# `hero`

The `hero` keyword defines the primary introductory content of a page.

A hero typically presents the most important information users should see when they first arrive on a page.

The compiler determines how the hero is implemented for the selected target and framework.

---

# Syntax

```itl
hero $HeroName {

}
```

Example:

```itl
hero $main {

    headline $Everything Fashion.

    subtitle $Buy from trusted tailors.

    action $Start Shopping
}
```

---

# Purpose

The `hero` declaration defines the primary entry point of a page.

Its purpose is to communicate the page's central message and guide users toward an intended action.

The language defines the intent.

The compiler determines the presentation.

---

# Structure

```itl
hero $HeroName {

    ...

}
```

Where:

- `hero` is a reserved keyword.
- `$HeroName` uniquely identifies the hero within the page.
- `{}` defines the hero's scope.

---

# Placement

A `hero` declaration may only appear inside a `page`.

Example:

```itl
page $home {

    hero $main {

    }

}
```

Using `hero` outside a page is invalid.

---

# Children

The following declarations are currently valid inside a hero.

| Keyword | Required | Description |
|---------|----------|-------------|
| `intent` | No | Describes the purpose of the hero. |
| `image` | No | Defines the hero image or visual asset. |
| `headline` | No | Primary heading. |
| `subtitle` | No | Supporting text. |
| `action` | No | Primary call-to-action. |

Future versions may introduce additional hero content.

---

# Required

A hero declaration requires:

- a hero name

All child declarations are optional.

---

# Optional

A hero may contain:

- `image`
- `headline`
- `subtitle`
- `action`

Future versions may support:

- video
- buttons
- badges
- statistics
- animations
- layouts

---

# Semantics

The `hero` declaration represents the primary introductory content of a page.

It does not define visual appearance.

Instead, it expresses the information that should be presented.

Different targets may render the same hero differently.

For example:

Web:

```
Headline

Subtitle

Button
```

Mobile:

```
Headline

Subtitle

Bottom Action Button
```

Desktop:

```
Large Header

Supporting Content

Action Panel
```

The intent remains unchanged.

---

# Compiler Behavior

When the compiler encounters a `hero` declaration it should:

1. Create a hero node.
2. Store the hero name.
3. Parse child declarations.
4. Validate child uniqueness.
5. Add the hero to the current page.

---

# Errors

## Missing Hero Name

Invalid:

```itl
hero {

}
```

Compiler error:

```
Expected hero name.
```

---

## Invalid Placement

Invalid:

```itl
app $Portfolio {

    hero $main {

    }

}
```

Compiler error:

```
'hero' may only appear inside a page.
```

---

## Duplicate Headline

Invalid:

```itl
hero $main {

    headline $Hello

    headline $World
}
```

Compiler error:

```
Hero may contain only one headline.
```

---

## Duplicate Subtitle

Invalid:

```itl
hero $main {

    subtitle $One

    subtitle $Two
}
```

Compiler error:

```
Hero may contain only one subtitle.
```

---

## Duplicate Action

Invalid:

```itl
hero $main {

    action $Login

    action $Register
}
```

Compiler error:

```
Hero may contain only one action.
```

---

# Examples

## Basic Hero

```itl
hero $main {

    headline $Everything Fashion.

}
```

---

## Hero With Subtitle

```itl
hero $main {

    headline $Everything Fashion.

    subtitle $Buy from trusted tailors.
}
```

---

## Complete Hero

```itl
hero $main {

    image $assets/hero.png

    headline $Everything Fashion.

    subtitle $Buy from trusted tailors.

    action $Start Shopping
}
```

---

## Hero Inside a Page

```itl
page $home {

    hero $main {

        headline $Welcome

        subtitle $Let's build something amazing.

        action $Get Started
    }

}
```

---

# Notes

- A hero defines the primary introductory content of a page.
- A hero does not define layout or styling.
- The compiler determines how the hero is presented for each target.
- Child declarations should be unique within a hero.

---

# Version

Introduced in:

```
ITL 0.1
```