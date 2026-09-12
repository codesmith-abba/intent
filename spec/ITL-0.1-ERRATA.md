# ITL v0.1 Specification Errata

**Applies to:** `spec/ITL-0.1.md`  
**Specification version:** 0.1  
**Status:** Normative correction

This errata records corrections found while running the v0.1 conformance suite against the implemented lexer/parser. It is part of the v0.1 specification and overrides conflicting wording in `ITL-0.1.md`.

## E1. Optional intent syntax

An optional intent attached directly to an application, page, hero, section, system, or infrastructure block is introduced by the `intent` keyword.

For example:

```itl
app $Example intent $Describe the application {
    page $home intent $Describe the page {}
}
```

Therefore the grammar form is conceptually:

```ebnf
named-declaration = keyword , string , [ "intent" , string ] , block ;
```

The phrase “optional intent immediately after its name” means the optional **`intent` declaration**, not a bare string.

## E2. Section imports are not source-level syntax in v0.1

Although the `Section` AST type contains an `imports` field and the resolver has import-related type handling, the current parser's `SECTION_MEMBERS` table does not accept the `import` keyword inside a section.

Therefore v0.1 source conformance supports:

- `App` imports
- `Page` imports

It does **not** support a source-level section import declaration.

The v0.1 supported parser forms are:

```itl
app $Example {
    import $home

    page $local {
        import $footer
    }
}
```

A section containing `import $details` currently raises `ParseError`.

## E3. Single-line literal termination

A `$` single-line literal continues until a newline or `{`. Consequently, closing braces do not terminate the literal.

This is important when writing negative semantic conformance cases. For example:

```itl
app $Example {
    target $console
}
```

terminates `$console` at the newline, allowing the parser to see `}`. The one-line form:

```itl
app $Example { target $console }
```

causes the literal to consume `console }` and therefore does not produce the intended semantic target error.

## E4. Page intent conformance example

To test the single-line literal boundary before `{`, the parser-supported form is:

```itl
app $Example {
    page $home intent $Intent text {}
}
```

The page intent value is `Intent text`.

## E5. Conformance principle

Conformance tests must exercise syntax accepted by the current parser, not syntax implied by AST fields, lexer keywords, or future resolver capabilities. If a construct is not dispatched by the parser, it is not part of the v0.1 source language.
