# Blocks

Blocks define the scope and ownership of declarations in Intent Language (ITL).

A block groups related declarations together and establishes their relationship within the application.

Blocks are the primary mechanism used to organize ITL programs.

---

# Purpose

Blocks allow developers to:

- group related declarations
- define ownership
- establish scope
- organize applications
- create hierarchical program structures

Every declaration inside a block belongs to its enclosing declaration.

---

# Syntax

A block begins with an opening brace:

```itl
{
```

and ends with a closing brace:

```itl
}
```

Example:

```itl
page $home {

}
```

---

# Scope

A block creates a new scope.

Declarations inside the block belong only to that scope.

Example:

```itl
page $home {

    theme $dark

    hero $main {

    }

}
```

In this example:

- `theme` belongs to `home`
- `hero` belongs to `home`

---

# Ownership

Blocks express ownership.

Example:

```itl
page $home {

    hero $main {

    }

    section $about {

    }

}
```

Hierarchy:

```
Page (home)

├── Hero (main)

└── Section (about)
```

The `page` owns both the `hero` and the `section`.

---

# Nested Blocks

Blocks may contain other blocks.

Example:

```itl
hero $main {

    intent $(
        Create a welcoming hero section with
        a bold headline and clear call-to-action.
    )

}
```

Nested blocks form a hierarchical tree that the compiler represents as an Abstract Syntax Tree (AST).

---

# Empty Blocks

A block may be empty.

Example:

```itl
section $contact {

}
```

An empty block is grammatically valid.

Semantic analysis determines whether additional declarations are required.

---

# Declaration Order

Declarations inside a block are processed in the order they appear.

Example:

```itl
page $home {

    hero $main {}

    section $about {}

    section $projects {}

    section $contact {}

}
```

The compiler preserves this logical order whenever possible.

---

# Importing Into Blocks

Blocks may import declarations from other ITL source files.

Example:

```itl
page $home {

    hero $main {}

    import $footer

}
```

If `footer.itl` contains:

```itl
section $footer {

}
```

the imported section becomes part of the current page.

---

# Valid Nesting

Only declarations that define scopes may contain child declarations.

Example:

```itl
page $home {

    hero $main {

    }

}
```

Invalid:

```itl
headline $Welcome {

}
```

Compiler error:

```
'headline' cannot contain child declarations.
```

---

# Whitespace

Whitespace inside blocks is not significant.

These examples are equivalent:

```itl
page $home {

    hero $main {

    }

}
```

```itl
page $home{
hero $main{
}
}
```

Consistent indentation is strongly recommended.

---

# Compiler Behavior

When the parser encounters an opening brace (`{`), it begins a new scope.

It continues parsing declarations until the matching closing brace (`}`) is found.

Nested blocks are parsed recursively.

---

# Errors

## Missing Opening Brace

Invalid:

```itl
page $home

    hero $main

}
```

Compiler error:

```
Expected '{' after page declaration.
```

---

## Missing Closing Brace

Invalid:

```itl
page $home {

    hero $main {

}
```

Compiler error:

```
Expected '}' before end of file.
```

---

## Unbalanced Blocks

Invalid:

```itl
page $home {

    section $about {

}
```

Compiler error:

```
Unbalanced block structure.
```

---

# Examples

## Application Block

```itl
app $Portfolio {

    target $web

    framework $react

}
```

---

## Page Block

```itl
page $home {

    theme $dark

    hero $main {}

}
```

---

## Hero Block

```itl
hero $main {

    image $assets/hero.png

    headline $Welcome

}
```

---

## Section Block

```itl
section $projects {

    intent $(
        Display recent work in a responsive grid.
    )

}
```

---

# Notes

- Blocks define scope.
- Blocks establish ownership.
- Blocks create the application's hierarchy.
- Child declarations belong to their enclosing block.
- Nested blocks are supported.
- Empty blocks are allowed.
- Imports merge declarations into the current block.

---

# Version

Introduced in:

```
ITL 0.1
```