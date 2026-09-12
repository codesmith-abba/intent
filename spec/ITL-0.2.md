# Intent Language (ITL) Language Specification — v0.2

**Status:** Implemented / normative
**Specification version:** 0.2
**Scope:** application language constructs implemented by the lexer, parser, import resolver, semantic analyzer, and GIR.

## 1. Pipeline

The implemented source path is:

`Source → Lexer → Parser → Import Resolution → Semantic Analysis → GIR`

ITL 0.2 extends the existing language with application data and navigation semantics. The existing page, section, system, import, and target syntax remains compatible.

## 2. Application modules

The following module declarations are implemented:

- `page`
- `section`
- `models`
- `routes`
- `permissions`

An application may also contain these declarations directly inside `app { ... }`.

`import $all` is implemented at application level and loads every `.itl` module in the project root except `app.itl`. Compatible modules are merged into the application. Existing explicit imports remain supported.

## 3. Models

A models module has the form:

```itl
models {
    model $User {
        field $id {
            type $id
            primary
        }
    }
}
```

A model has a `$`-string name and may contain fields, relationships, and CRUD-style actions.

## 4. Fields

Fields use:

```itl
field $name {
    type $string
    primary
    required
    unique
    readonly
    nullable
    default $value
    min 0
    max 100
    minLen 1
    maxLen 100
}
```

Implemented field types include `id`, `string`, `text`, `email`, `phone`, `password`, `image`, `boolean`, `datetime`, `date`, `time`, `slug`, `decimal`, `integer`, `number`, `float`, `json`, and `uuid`.

The analyzer rejects unknown types, conflicting `required` + `nullable`, invalid ranges, invalid length ranges, and nullable primary keys. A model must have exactly one primary key in the current semantic contract.

## 5. Relationships

Implemented relationship declarations are:

```text
belongsTo
hasOne
hasMany
belongsToMany
hasManyThrough
```

Each relationship takes a `$`-string target model. The analyzer verifies that the referenced model exists.

## 6. CRUD and application actions

The parser represents the following actions:

```text
view
get
create
update
delete
manage
```

Actions are represented in the AST and GIR and are available to model and permission semantics. Permission `allow` blocks use the same action vocabulary.

## 7. Routes

Routes use:

```itl
routes {
    route $home {
        path $/
        page $home
        auth $customer
    }
}
```

`path`, `page`, and optional `auth` are represented semantically. Route names and paths must be unique, paths are required, and referenced pages must exist in the application.

## 8. Permissions

Permissions contain roles. Roles may inherit other roles and may contain `allow` blocks with the implemented action vocabulary. Duplicate roles and references to unknown inherited roles are semantic errors.

## 9. AST and GIR

Application semantics are represented explicitly rather than as raw keyword tokens. The AST contains model, field, relationship, action, route, and permission-role nodes. The GIR contains corresponding application-level nodes so later backend generators can consume backend-independent semantics.

## 10. Diagnostics

Invalid application programs produce parser or semantic diagnostics for, among other cases:

- duplicate models;
- duplicate fields;
- missing primary keys;
- multiple primary keys;
- unknown field types;
- invalid field constraints;
- unknown relationship targets;
- duplicate routes or paths;
- missing route paths/pages;
- unknown route page references;
- duplicate roles;
- unknown inherited roles;
- unsupported declarations in a block.

## 11. Compatibility

ITL 0.2 retains the existing page/component grammar and `$` string rules. No replacement import mechanism is introduced; `import $all` is the application-level all-module import form used by the ecommerce example.
