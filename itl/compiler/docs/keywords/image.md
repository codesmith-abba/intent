# `image`

The `image` keyword specifies the image source associated with a declaration.

Rather than describing how an image should be rendered, the `image` keyword expresses **which image the developer intends to use**.

The selected backend determines how the image source is resolved and consumed.

---

# Syntax

```itl
image $ImageSource
```

Example:

```itl
hero $main {

    image $assets/hero.png

}
```

---

# Purpose

The `image` keyword associates an image source with the current declaration.

The source may represent:

- a local asset
- a remote image
- a backend-managed resource
- an AI-generated asset
- any future image source supported by the selected backend

The compiler records the source without interpreting its meaning.

---

# Structure

```itl
image $ImageSource
```

Where:

- `image` is a reserved keyword.
- `$ImageSource` identifies the image to be used.

---

# Placement

The `image` keyword may appear anywhere an image is valid.

Current examples include:

- `hero`
- `section`

Future versions of ITL may allow images in additional declarations.

Example:

```itl
hero $landing {

    image $assets/banner.png

}
```

---

# Required

Images are optional.

When an image is not supplied, a backend may:

- display no image,
- use a default placeholder,
- generate an image from an `intent` block,
- or apply backend-specific behavior.

---

# Image Sources

The language does not restrict the format of an image source.

Common examples include:

## Local Asset

```itl
image $assets/profile.png
```

---

## Remote Resource

```itl
image $https://example.com/banner.jpg
```

---

## Backend Storage

```itl
image $storage://avatars/profile.png
```

---

## Generated Asset

```itl
image $generated:hero
```

The interpretation of these source formats is entirely backend-specific.

---

# AI Integration

The `image` keyword works naturally with the `intent` keyword.

Example:

```itl
hero $main {

    intent $(
        Create a futuristic workspace
        featuring holographic interfaces
        and warm blue lighting.
    )

}
```

If no image is supplied, an AI-capable backend may generate one using the declaration's intent.

Generated images behave exactly like manually supplied image sources.

---

# Semantics

The `image` declaration identifies the visual resource associated with its enclosing declaration.

Example:

```itl
hero $main {

    image $assets/hero.png

}
```

The compiler stores the image source in the Intermediate Representation (IR).

The backend resolves the source during project generation or runtime.

---

# Compiler Behavior

When the compiler encounters an `image` declaration it should:

1. Read the image source.
2. Validate that a source exists.
3. Associate the source with the current declaration.
4. Store it in the Intermediate Representation (IR).

The compiler does not process, resize, optimize, or download images.

---

# Errors

## Missing Image Source

Invalid:

```itl
image
```

Compiler error:

```
Expected image source.
```

---

## Invalid Placement

Invalid:

```itl
framework $react {

    image $assets/logo.png

}
```

Compiler error:

```
'image' is not valid in this scope.
```

---

# Examples

## Local Asset

```itl
hero $main {

    image $assets/hero.png

}
```

---

## Remote Image

```itl
section $gallery {

    image $https://example.com/gallery.jpg

}
```

---

## Generated Image

```itl
hero $landing {

    image $generated:landing

}
```

---

## AI Generated

```itl
hero $landing {

    intent $(
        Design a clean SaaS landing page
        with abstract gradients,
        floating geometric shapes,
        and a modern technology aesthetic.
    )

}
```

An AI-capable backend may generate an image automatically.

---

# Notes

- `image` specifies an image source, not an implementation.
- Image sources are backend-defined.
- Images are optional.
- AI-capable backends may generate images using an `intent` block.
- The compiler records image metadata but does not manipulate image resources.

---

# Version

Introduced in:

```
ITL 0.1
```