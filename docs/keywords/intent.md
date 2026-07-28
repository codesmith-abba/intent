# `intent`

The `intent` keyword describes the purpose, goals, and desired behavior of a declaration.

Unlike implementation-specific declarations, `intent` captures the semantic meaning behind an application or component.

The compiler stores this information as part of the program's metadata and may use it to guide code generation, analysis, documentation, and AI-assisted workflows.

---

# Syntax

```itl
intent $(
    Multi-line description...
)
```

Example:

```itl
intent $(
    A modern portfolio website for an AI engineer.

    Showcase projects, technical articles,
    and contact information.

    The homepage should immediately communicate
    professionalism and innovation.
)
```

---

# Purpose

The `intent` declaration allows developers to describe **what they are trying to build**, rather than **how it should be implemented**.

Intent serves as semantic context for the compiler, tooling, plugins, and AI systems.

It is considered part of the application's metadata.

---

# Structure

```itl
intent $(

    ...

)
```

Where:

- `intent` is a reserved keyword.
- `$(` begins a multi-line intent block.
- `)` ends the block.

Everything between `$(` and `)` is treated as a single string.

The compiler preserves formatting while normalizing line endings.

---

# Placement

An `intent` declaration may appear inside any scoped declaration.

Examples include:

- `app`
- `page`
- `hero`
- `section`

Future language constructs may also support `intent`.

---

# Required

An `intent` declaration is optional.

However, providing an intent is recommended because it gives the compiler and tooling additional semantic information.

---

# Semantics

The `intent` declaration describes the purpose of the enclosing declaration.

For example:

```itl
app $Portfolio {

    intent $(
        Personal portfolio website.
    )

}
```

describes the purpose of the entire application.

Likewise,

```itl
page $home {

    intent $(
        Welcome first-time visitors and guide them
        toward exploring projects.
    )

}
```

describes only the home page.

The meaning of an intent is always relative to the declaration that contains it.

---

# Compiler Behavior

When the compiler encounters an `intent` declaration it should:

1. Read the complete multi-line block.
2. Preserve the text as metadata.
3. Associate the intent with the enclosing declaration.
4. Include the intent in the Intermediate Representation (IR).
5. Make the intent available to compiler backends, plugins, and AI systems.

The compiler itself remains responsible for validating and supervising generated output.

---

# AI Integration

When AI-assisted generation is enabled, the compiler may provide the intent as contextual information.

The AI should treat the intent as guidance rather than executable instructions.

The compiler remains responsible for:

- semantic validation
- language correctness
- security
- deterministic compilation

When AI is unavailable, the intent remains part of the application's metadata and may still be used by documentation tools, analyzers, or plugins.

---

# Errors

## Missing Intent Block

Invalid:

```itl
intent
```

Compiler error:

```
Expected intent block.
```

---

## Unclosed Intent Block

Invalid:

```itl
intent $(
    This application...
```

Compiler error:

```
Unterminated intent block.
```

---

## Duplicate Intent

Invalid:

```itl
page $home {

    intent $(First)

    intent $(Second)

}
```

Compiler error:

```
A declaration may contain only one intent.
```

---

# Examples

## Application Intent

```itl
app $Portfolio {

    intent $(
        A personal portfolio website showcasing
        projects, technical writing,
        and professional experience.
    )

    target $web

    framework $react
}
```

---

## Page Intent

```itl
page $home {

    intent $(
        Introduce visitors to the application
        and encourage them to explore further.
    )

}
```

---

## Hero Intent

```itl
hero $main {

    intent $(
        Capture the user's attention immediately
        and encourage them to get started.
    )

}
```

---

## Section Intent

```itl
section $projects {

    intent $(
        Present featured projects in order
        of importance.
    )

}
```

---

# Notes

- Intent describes purpose, not implementation.
- Intent is preserved as metadata.
- Intent may be consumed by compiler backends, plugins, documentation generators, and AI systems.
- Intent does not replace language semantics or compiler validation.
- Each declaration may contain at most one intent.

---

# Version

Introduced in:

```
ITL 0.1
```