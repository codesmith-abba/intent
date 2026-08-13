# `import`

The `import` keyword incorporates declarations from another ITL source file into the current scope.

Imports allow applications to be organized across multiple files while preserving a single logical program.

The compiler resolves all imports before semantic analysis.

---

# Syntax

Import a single file:

```itl
import $about
```

Import multiple files:

```itl
import $about

import $contact

import $pricing
```

Import every eligible ITL source:

```itl
import $all
```

---

# Purpose

The `import` declaration allows developers to split large applications into smaller, reusable ITL source files.

Rather than duplicating declarations, developers can organize related functionality into separate files and compose applications through imports.

Imported declarations behave exactly as if they had been written directly inside the importing scope.

---

# Structure

```itl
import $FileName
```

or

```itl
import $all
```

Where:

- `import` is a reserved keyword.
- `$FileName` refers to an ITL source file.
- `$all` imports every eligible ITL source within the current project.

For example:

```itl
import $about
```

loads:

```
about.itl
```

---

# Placement

An `import` declaration may appear inside any scoped declaration.

Examples include:

- `app`
- `page`
- `section`
- `hero`
- future language constructs

The imported file must contain declarations that are valid for the scope into which it is imported.

---

# Required

Imports are optional.

Applications may declare everything in a single source file or compose declarations from many files.

---

# Semantics

An import inserts the contents of another ITL source file into the current scope.

For example:

```itl
page $home {

    hero $main {}

    import $footer

}
```

Assume:

```
footer.itl
```

contains:

```itl
section $footer {

}
```

After import resolution, the compiler behaves as though the source were:

```itl
page $home {

    hero $main {}

    section $footer {

    }

}
```

The imported declarations become part of the page.

Likewise,

```itl
app $Portfolio {

    import $pages

    target $web

    framework $react
}
```

may load:

```
pages.itl
```

containing:

```itl
page $home {}

page $about {}

page $contact {}
```

These pages become part of the application.

---

# Scope Validation

Imported declarations must be valid for the scope into which they are imported.

For example,

Valid:

```itl
page $home {

    import $footer
}
```

where `footer.itl` contains:

```itl
section $footer {

}
```

Invalid:

```itl
page $home {

    import $about
}
```

where `about.itl` contains:

```itl
page $about {

}
```

Compiler error:

```
Cannot import 'page' into a page scope.
```

---

# Import Resolution

The compiler performs the following steps:

1. Locate the referenced ITL file.
2. Parse the imported source.
3. Resolve nested imports.
4. Validate imported declarations.
5. Merge declarations into the current scope.
6. Detect duplicate declarations.
7. Detect circular imports.
8. Continue semantic analysis.

Import resolution is deterministic.

---

# Compiler Behavior

When the compiler encounters an `import` declaration it should:

1. Locate the referenced ITL file.
2. Parse the imported source.
3. Resolve nested imports.
4. Verify scope compatibility.
5. Merge declarations into the current scope.
6. Preserve source locations for diagnostics.

---

# Errors

## Missing Import Name

Invalid:

```itl
import
```

Compiler error:

```
Expected import target.
```

---

## Missing File

Invalid:

```itl
import $dashboard
```

Compiler error:

```
Unable to locate 'dashboard.itl'.
```

---

## Circular Import

Example:

```
home.itl

↓

footer.itl

↓

home.itl
```

Compiler error:

```
Circular import detected.
```

---

## Invalid Scope

Example:

```itl
page $home {

    import $about

}
```

where `about.itl` contains:

```itl
page $about {

}
```

Compiler error:

```
Imported declarations are not valid in the current scope.
```

---

## Duplicate Declarations

If imported declarations conflict with existing declarations, the compiler should report an error.

---

# Examples

## Import Pages

```itl
app $Portfolio {

    import $pages

    target $web

    framework $react
}
```

---

## Import Sections

```itl
page $home {

    hero $main {}

    import $footer
}
```

---

## Import Hero Content

```itl
hero $main {

    import $headline
}
```

---

## Import All

```itl
app $Portfolio {

    import $all

    target $web

    framework $react
}
```

The compiler imports every eligible ITL source before semantic analysis.

---

# Notes

- Imports are resolved before semantic analysis.
- Imports insert declarations into the current scope.
- Importing the same file multiple times has no effect beyond the first successful import unless explicitly configured otherwise.
- Circular imports are not permitted.
- Imported declarations must be valid for the destination scope.
- Import resolution is deterministic.

---

# Version

Introduced in:

```
ITL 0.1
```