# ITL v1.0 Language Reference

This is the stable release-facing reference for the implemented ITL source language. The normative grammar remains `spec/ITL-0.1.md`; this page provides the entry point for users.

## Supported top-level form

```itl
app $Name {
    import $page-module
    page $home {}
    system {}
    target $web
    intent $Describe the application.
}
```

## Supported page members

```itl
page $home {
    import $section-module
    theme $light
    hero $main {}
    section $content {}
    intent $Describe this page.
}
```

## Supported hero members

```itl
hero $main {
    image $assets/hero.svg
    headline $Welcome
    subtitle $A short description
    action $Continue
    intent $Describe the hero.
}
```

## Supported section members

Sections support nested sections plus `image`, `headline`, `subtitle`, `action`, and `intent`.

## System declarations

The implemented parser supports `frontend`, `backend`, `database`, `cache`, and `storage` inside `system` blocks. Their supported values are defined by the full specification and semantic analyzer.

Example:

```itl
system {
    frontend {
        framework $react
    }
    backend {
        framework $django
        api $rest
    }
    database {
        engine $postgres
    }
}
```

## Strings

Names and values use `$` strings. `$(` starts a multiline string and `)` terminates it. `//` starts a comment. Braces and multiline termination follow the lexical rules in the normative specification.

## Imports

The current resolver supports:

- `App <- Page`
- `Page <- Section`

Imports are implementation-resolved modules, not arbitrary filesystem expressions.

## Semantic constraints

The analyzer enforces supported targets, themes, frontend/backend frameworks, unique page names, unique direct section names, and the required hero headline rule, among other implemented checks.

## Reserved but unsupported syntax

The lexer recognizes additional keywords for future language growth. Lexical recognition alone does not make a construct valid ITL source. Unsupported declarations must not be used in v1.0 programs.

## Normative reference

See `spec/ITL-0.1.md` for the complete implemented grammar and semantic rules. Changes to the stable language require a new specification version and conformance coverage.
