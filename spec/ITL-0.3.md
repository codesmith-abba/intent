# Intent Language (ITL) Language Specification — v0.3

**Status:** Implemented / normative
**Specification version:** 0.3
**Scope:** authentication and authorization semantics implemented by the lexer, parser, import resolver, semantic analyzer, and GIR.

## 1. Pipeline

`Source → Lexer → Parser → Import Resolution → Semantic Analysis → GIR`

ITL 0.3 extends ITL 0.2 with first-class authentication and authorization.

## 2. Authentication

An authentication module has the form:

```itl
auth {
    provider $email
    provider $phone

    registration {
        enabled true
        verification $email
    }

    login {
        allow $email
        rememberMe true
    }

    logout {
        enabled true
    }

    passwordRecovery {
        enabled true
        method $email
        reset true
    }

    verification {
        enabled true
        method $email
    }

    session {
        timeout 30d
        multipleDevices true
    }

    mfa {
        enabled true
        method $totp
    }
}
```

Implemented authentication semantics include:

- `auth`
- `provider`
- `registration`
- `login`
- `logout`
- `passwordRecovery`
- `reset`
- `verification`
- `session`
- `timeout`
- `rememberMe`
- `multipleDevices`
- `mfa`
- `enabled`
- `method`

Providers are user-defined strings; the compiler does not hard-code provider names.

Session durations use a numeric value with `s`, `m`, `h`, `d`, or `w` suffixes, for example `30d`.

The analyzer verifies duplicate providers, provider references, session duration syntax, and required MFA configuration.

## 3. Authorization roles

Permissions contain general-purpose roles:

```itl
permissions {
    role $owner {
        allow {
            view $dashboard
            update $User
        }
    }

    role $auditor {
        inherits $owner
        allow {
            view $reports
        }
    }
}
```

Roles are not predefined. Names such as `guest`, `customer`, `seller`, `admin`, and `superAdmin` are ordinary user-defined role names in the ecommerce example.

`inherits` creates role inheritance. The analyzer rejects unknown parents and circular inheritance.

## 4. Named permissions

A permission may explicitly bind an action to a resource:

```itl
permission $updateUser {
    resource $User
    action $update
}
```

Roles may reference named permissions with `allow`:

```itl
role $owner {
    allow $updateUser
}
```

Resources must resolve to application models, pages, or routes. Actions use the common vocabulary:

`view`, `get`, `create`, `update`, `delete`, `manage`.

Unknown resources, invalid actions, duplicate permissions, and unknown role permission references are semantic errors.

## 5. Direct action permissions

Existing direct authorization rules remain supported:

```itl
allow {
    view $products
    create $order
    update $profile
    delete $wishlist
    manage $settings
}
```

These rules are represented as action/resource pairs in the AST and GIR.

## 6. Routes and authorization

Routes may reference a role:

```itl
route $orders {
    path $/orders
    page $orders
    auth $customer
}
```

When roles are declared, the analyzer validates route role references.

## 7. AST

ITL 0.3 introduces first-class AST nodes for:

- `Auth`
- authentication providers and configuration blocks
- `Permission`
- permission roles
- named permission references

Authentication and authorization data is no longer represented only as raw keywords.

## 8. GIR

The GIR contains backend-independent representations for:

- authentication providers
- registration
- login and remember-me
- logout
- password recovery and reset
- verification
- sessions and multi-device sessions
- MFA
- named permissions
- roles, inheritance, direct actions, and named permission references

## 9. Semantic diagnostics

The analyzer rejects, among other cases:

- duplicate roles;
- unknown inherited roles;
- circular role inheritance;
- duplicate permissions;
- unknown permission resources;
- invalid permission actions;
- unknown role permission references;
- duplicate authentication providers;
- unknown authentication provider references;
- invalid session durations;
- enabled MFA without a method;
- invalid authentication configuration.

## 10. Compatibility

ITL 0.3 preserves ITL 0.2 model, route, page, section, import, and direct permission syntax. `import $all` remains the application-level all-module import form.
