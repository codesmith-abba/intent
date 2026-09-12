# Intent Language (ITL) Language Specification — v0.1

**Status:** Experimental / implemented specification  
**Specification version:** 0.1  
**Scope:** source language accepted by the current lexer, parser, import resolver, and semantic analyzer.

> This document is normative for ITL v0.1. It describes implemented behavior only. Proposed or reserved syntax is not part of this specification.

---

## 1. Overview

An ITL source file is a textual program containing one application declaration or, when loaded as an imported module, one supported module declaration. A normal project is rooted at `app.itl`.

The implemented compiler path is:

```text
Source → Lexer → Parser → Import Resolution → Semantic Analysis → GIR
```

The broader build system may continue from GIR into dependency analysis, planning, generation, validation, repair, and emission. Those services are implementation behavior rather than additional source-language syntax.

---

## 2. Lexical grammar

### 2.1 Character handling

The lexer processes source character by character. The following are significant:

- `{` — left brace
- `}` — right brace
- `(` — left parenthesis
- `)` — right parenthesis
- `$` — starts a single-line string or, when immediately followed by `(`, a multiline string
- `//` — starts a comment extending to the end of the line
- newline — increments the source line counter
- spaces, carriage returns, and tabs — ignored outside literals

Other characters are not generally accepted as free-form syntax. Unexpected characters raise a lexical `SyntaxError`.

### 2.2 Approximate EBNF

The grammar below describes the implemented syntax at a useful language level; lexical details in sections 3–5 take precedence.

```ebnf
program        = app , EOF ;

app            = "app" , string , [ intent-value ] , "{" , { app-declaration } , "}" ;

app-declaration
               = import-decl | page-decl | system-decl | target-decl | intent-decl ;

page-decl      = "page" , string , [ intent-value ] , "{" , { page-member } , "}" ;
page-member    = import-decl | theme-decl | intent-decl | hero-decl | section-decl ;

hero-decl      = "hero" , string , [ intent-value ] , "{" , { hero-member } , "}" ;
hero-member    = image-decl | headline-decl | subtitle-decl | intent-decl | action-decl ;

section-decl   = "section" , string , [ intent-value ] , "{" , { section-member } , "}" ;
section-member = section-decl | image-decl | headline-decl | subtitle-decl | intent-decl | action-decl ;

system-decl    = "system" , [ intent-value ] , "{" , { system-member } , "}" ;
system-member  = frontend-decl | backend-decl | database-decl | cache-decl | storage-decl ;

frontend-decl  = "frontend" , [ intent-value ] , "{" , [ framework-decl ] , "}" ;
backend-decl   = "backend" , [ intent-value ] , "{" , [ framework-decl ] , [ api-decl ] , "}" ;
database-decl  = "database" , [ intent-value ] , "{" , [ engine-decl ] , "}" ;
cache-decl     = "cache" , [ intent-value ] , "{" , [ engine-decl ] , "}" ;
storage-decl   = "storage" , [ intent-value ] , "{" , [ provider-decl ] , "}" ;

import-decl    = "import" , string ;
target-decl    = "target" , string ;
intent-decl    = "intent" , string ;
theme-decl     = "theme" , string ;
image-decl     = "image" , string ;
headline-decl  = "headline" , string ;
subtitle-decl  = "subtitle" , string ;
action-decl    = "action" , string ;
framework-decl = "framework" , string ;
api-decl       = "api" , string ;
engine-decl    = "engine" , string ;
provider-decl  = "provider" , string ;

string         = single-line-string | multiline-string ;
```

The parser also contains module entry points for standalone `page` and `section` declarations. Those are used by the import resolver and are described in §7.

---

## 3. Keywords

The lexer reserves the following words as keyword tokens:

```text
app import target framework database frontend backend
system theme intent models permissions routes
page hero section image headline subtitle action
route path auth role allow inherits
view get create update delete manage
field model type
belongsTo hasOne hasMany belongsToMany hasManyThrough
primary required unique readonly nullable default
min max minLen maxLen
provider engine api storage cache
```

`true` and `false` are lexed as boolean tokens.

Important: being recognized lexically does **not** mean a keyword is currently accepted by the top-level parser. For example, `models`, `routes`, `auth`, `field`, and related tokens exist in the lexer but have no active parser production in v0.1. They must therefore not be treated as supported source constructs.

---

## 4. Identifiers and names

ITL v0.1 does not expose a separate identifier token to the parser. Names are represented by `$`-prefixed string literals.

Examples:

```itl
app $Storefront {}
page $home {}
section $featured {}
hero $main {}
```

The `$` is not part of the stored value. For example `$home` produces the string value `home`.

Bare alphabetic words are interpreted as keywords. An alphabetic word that is not a recognized keyword produces a lexical error such as `Unknown keyword '...'`.

Consequently, this is not a valid name form:

```itl
page home {}
```

Use:

```itl
page $home {}
```

---

## 5. Strings and literals

### 5.1 Single-line strings

A single-line string begins with `$` and continues until the next newline or `{` character. Leading `$` is removed and trailing whitespace is stripped.

Example:

```itl
headline $Welcome to our store
```

The string value is `Welcome to our store`.

Because `{` terminates a single-line literal, a literal containing `{` cannot be represented directly with this form.

### 5.2 Multiline strings

A multiline string begins with `$(` and ends at the next `)`.

Example:

```itl
intent $(
    Help customers discover products.
    Show clear product information.
)
```

The captured value is trimmed. Newlines inside the literal increment the lexer line counter.

An unterminated multiline literal raises `SyntaxError("Unterminated multiline literal.")`.

There is no implemented escape syntax for `$`, `)`, or `{` inside these literals.

### 5.3 Numbers and booleans

The lexer recognizes integer and decimal numeric tokens and the boolean literals `true` and `false`. The currently supported application/page/component grammar does not consume numeric or boolean values, so they are not general-purpose source values in v0.1.

---

## 6. Blocks

Blocks use `{` and `}` and contain zero or more declarations permitted by their parent production.

Empty blocks are valid where the parent production permits the block:

```itl
section $footer {}
```

An unexpected declaration inside a block is a parse error. An unterminated block results in an error when the parser expects `}`.

The parser does not use indentation as syntax.

---

## 7. Imports

The implemented AST supports imports on `App`, `Page`, and `Section` nodes.

Syntax:

```itl
import $module-name
```

The import value is a string and is passed to the project loader. The resolver loads the module, merges it into the importing node according to the supported parent/module type, and recursively resolves nested imports.

Supported merge relationships are:

| Importing node | Imported node | Effect |
|---|---|---|
| `App` | `Page` | imported page is appended to `app.pages` |
| `Page` | `Section` | imported section is appended to `page.sections` |

An incompatible import, such as importing a `Section` into an `App`, raises an `ITLTypeError`.

The resolver tracks loaded import names and does not load the same name more than once during a resolution pass.

The exact filesystem lookup is compiler/project-loader behavior, not language syntax.

---

## 8. Pages

A page has:

- a required `$`-string name;
- an optional intent immediately after its name;
- optional theme;
- optional page intent declaration;
- optional hero;
- zero or more sections;
- optional imports.

Example:

```itl
page $home {
    theme $light

    hero $main {
        headline $Welcome
        subtitle $A simple storefront
        action $Browse catalog
    }

    section $featured {
        intent $Show featured products.
    }
}
```

Page names must be unique within an application. Duplicate pages are semantic errors.

---

## 9. Components

### 9.1 Hero

A hero requires a name and a block. Its supported members are:

- `image $...`
- `headline $...`
- `subtitle $...`
- `intent $...` 
- `action $...`

A hero must contain a non-empty headline during semantic analysis.

Example:

```itl
hero $main {
    image $assets/hero.svg
    headline $Build with intention
    subtitle $Describe what you want
    action $Learn more
}
```

### 9.2 Section

A section has a required name, an optional immediate intent, optional section members, and nested sections.

Supported section members are the same content members recognized by the parser (`image`, `headline`, `subtitle`, `intent`, `action`) plus nested `section` declarations.

Section names must be unique among a page's direct sections. Nested sections are represented recursively in the AST/GIR.

---

## 10. Targets

Application target syntax is:

```itl
target $web
```

The semantic analyzer currently accepts exactly:

```text
web
mobile
desktop
```

An unknown target produces a semantic error.

The AST defaults `target` to `web` when no target declaration is present.

---

## 11. Frameworks

Framework values are strings carried by `Framework` AST nodes.

### Frontend

Accepted frontend framework values:

```text
react
next
vue
angular
svelte
```

### Backend

Accepted backend framework values:

```text
django
fastapi
flask
express
laravel
```

Framework declarations are currently parsed inside the corresponding `frontend` or `backend` system block:

```itl
system {
    frontend {
        framework $react
    }

    backend {
        framework $django
        api $rest
    }
}
```

The analyzer rejects an unknown framework for its corresponding side.

The AST's `Framework` type contains a broader typing annotation, but semantic conformance is determined by the analyzer's accepted sets above.

---

## 12. Semantic rules

After parsing and import resolution, the semantic analyzer enforces the following rules:

1. The application target must be one of `web`, `mobile`, or `desktop`.
2. Page names must be unique within the application.
3. Page themes, when present, must be one of `light`, `dark`, or `custom`.
4. A frontend framework, when present, must be one of `react`, `next`, `vue`, `angular`, or `svelte`.
5. A backend framework, when present, must be one of `django`, `fastapi`, `flask`, `express`, or `laravel`.
6. Every hero must contain a headline.
7. Direct section names on a page must be unique.
8. Analyzer visitors must exist for the node types used by the compiler; unsupported semantic node types result in a semantic error.

Database, cache, and storage values currently have no additional semantic-value validation beyond parsing.

---

## 13. GIR semantics

The compiler transforms the resolved and semantically analyzed AST into the Graph Intermediate Representation (GIR).

The principal GIR structures are:

```text
GIRApplication
├── name
├── target
├── intent
├── system?
└── pages[]

GIRPage
├── name
├── theme?
├── intent
└── components[]

GIRHero
├── name
├── image?
├── headline?
├── subtitle?
├── action?
└── intent

GIRSection
├── name
├── children[]
└── intent

GIRSystem
├── frontend?
├── backend?
├── api?
├── database?
├── cache?
├── storage?
└── intent
```

GIR is an implementation-facing intermediate representation. It is not itself source syntax. The GIR is the stable conceptual boundary consumed by build, generation, validation, emission, and runtime services.

---

## 14. Project structure

A normal ITL project is discovered by locating a `.project` directory and then requiring `app.itl` as the compiler entrypoint.

A minimal initialized project is conceptually:

```text
my-project/
├── app.itl
└── .project/
```

Compiler/project services may create additional `.project` state, cache, graph, GIR, build, runtime, and emission files. Those generated files are implementation artifacts, not language constructs.

Imported modules are resolved by the project loader from the project source tree according to its module-loading rules.

---

## 15. Build behavior

The language compiler produces GIR. The wider ITL build system can then perform:

```text
GIR
 ↓
Dependency graph
 ↓
Change detection / diff analysis
 ↓
Build planning
 ↓
Scheduling
 ↓
Generation
 ↓
Validation
 ↓
Repair (when configured)
 ↓
Emission
```

Build outputs are target/backend dependent. The language specification does not mandate a particular generated framework or file layout.

The browser runtime consumes a generated runtime manifest derived from GIR; it does not parse `.itl` source in the browser.

---

## 16. Incremental compilation

The implementation supports incremental build infrastructure around GIR fingerprints, dependency graphs, diff categories, planning, scheduling, caching, and emission manifests.

Conceptually:

1. Source is compiled to GIR.
2. GIR nodes receive deterministic fingerprints.
3. Changes are classified.
4. The dependency graph determines affected work.
5. The build planner creates work items.
6. The scheduler orders work by dependencies.
7. Cached generation may be reused where applicable.
8. Successful emission updates generated output and manifest state.

Change categories implemented by the GIR diff analyzer include:

```text
STYLE
LAYOUT
CONTENT
LOGIC
ARCHITECTURE
STRUCTURAL
```

The exact invalidation policy is compiler implementation behavior and may differ by build integration. The language itself has no incremental-build syntax.

---

## 17. Plugin behavior

Plugins extend generation and/or validation without changing ITL source syntax.

The implemented plugin system defines compatibility around target/framework selection and plugin API/compiler versions. Plugin generation providers can be selected through the plugin manager and used by the generation layer. Validators can be adapted through the validation pipeline.

A plugin is therefore an implementation extension point. The v0.1 language specification does not define a plugin declaration keyword or plugin source grammar.

The reference React plugin identifies itself as a web/React generation and validation capability.

---

## 18. Error model

Errors occur in distinct implementation stages:

### Lexical errors

Raised by the lexer for invalid characters, unknown bare words, or unterminated multiline literals. The implementation uses `SyntaxError` for these failures.

Examples include:

```text
Unexpected character '...'
Unknown keyword '...'
Unterminated multiline literal.
```

### Parse errors

Raised when the token stream violates the grammar expected by the current parser production. The implementation uses `ParseError` and reports the source file and line for consumption failures.

Examples include missing `app`, missing names, missing `{`, missing `}`, or unsupported declarations inside a block.

### Semantic errors

Raised after parsing when the AST violates semantic constraints. The implementation uses `SemanticError`.

Examples include:

```text
Unknown target '...'
Duplicate page '...'
Unknown theme '...'
Hero must contain a headline.
Duplicate section '...' in page '...'.
```

### Compiler/import errors

Import resolution can raise `ITLTypeError` when an imported module type cannot be merged into its parent.

The compiler/project loader can also surface filesystem and project errors. These are compiler-service behavior rather than lexical grammar rules.

### Build/runtime errors

Generation, validation, repair, emission, and browser runtime layers have structured result/error models of their own. They do not change the source-language grammar.

---

## 19. Conformance examples

### Valid minimal application

```itl
app $Hello {
    target $web
}
```

### Valid application with system and page

```itl
app $Storefront {
    system {
        frontend {
            framework $react
        }
    }

    page $home {
        theme $light

        hero $main {
            headline $Welcome to our store
            subtitle $Discover our products
            action $Browse catalog
        }

        section $featured {
            intent $Show featured products.
        }
    }

    target $web
}
```

### Valid multiline intent

```itl
app $Example {
    intent $(
        Describe the application clearly.
        Keep the implementation framework independent.
    )

    target $web
}
```

### Valid imports

`app.itl`:

```itl
app $Storefront {
    import $home
    target $web
}
```

`home.itl`:

```itl
page $home {
    hero $main {
        headline $Welcome
    }
}
```

The project compiler resolves the page module and merges it into the application.

### Invalid examples

Bare names are invalid:

```itl
app Storefront {}
```

Unknown targets are semantically invalid:

```itl
app $Example {
    target $console
}
```

A hero without a headline is semantically invalid:

```itl
app $Example {
    page $home {
        hero $main {
            subtitle $Missing headline
        }
    }
}
```

---

## 20. Versioning and compatibility

This document is **ITL Language Specification v0.1**.

A future language version may add, remove, or change syntax and semantic rules. A compiler claiming conformance to v0.1 should accept the valid constructs defined here and reject constructs that are outside the implemented v0.1 grammar and semantic rules.

Implementation details may evolve without changing the language version when they do not alter source-language meaning or conformance behavior.

Proposed syntax belongs in the roadmap until implemented and covered by conformance tests.
