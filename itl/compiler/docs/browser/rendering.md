# Rendering

Rendering is the process of transforming an ITL application's Intermediate Representation (IR) into a visual and interactive user interface.

Unlike traditional browsers that render HTML and CSS, the ITL Browser renders directly from the application's intent as represented by the IR.

---

# Purpose

The rendering system is responsible for presenting the application to the user.

Its responsibilities include:

- rendering pages
- rendering components
- applying themes
- displaying assets
- managing layouts
- updating the interface when application state changes

---

# Rendering Pipeline

The browser renders an application through several stages.

```
Intermediate Representation (IR)
            │
            ▼
Page Resolver
            │
            ▼
Layout Engine
            │
            ▼
Theme Engine
            │
            ▼
Renderer
            │
            ▼
Display
```

Each stage contributes to producing the final user interface.

---

# Page Rendering

When an application starts, the browser determines which page should be displayed.

Example:

```itl
page $home {

}
```

The page becomes the root of the rendered interface.

Navigation between pages causes the browser to render the newly selected page.

---

# Rendering Hierarchy

Rendering follows the structure of the Intermediate Representation.

Example:

```
Application
│
└── Home Page
    │
    ├── Hero
    │
    ├── About
    │
    ├── Projects
    │
    └── Footer
```

The browser renders parent declarations before their children.

---

# Layout

The browser determines how declarations are arranged on the screen.

Layout behavior depends on:

- declaration type
- application structure
- selected theme
- device characteristics

Developers describe *what* should appear.

The browser determines *how* it should appear.

---

# Themes

Themes influence the visual appearance of an application.

Example:

```itl
theme $dark
```

The rendering engine applies the appropriate colors, typography, spacing, and visual styles.

Theme implementation is handled entirely by the browser.

---

# Assets

Assets referenced by the application are loaded during rendering.

Examples include:

- images
- icons
- fonts
- media

The browser resolves asset sources before displaying them.

---

# Intent-Aware Rendering

The browser may use `intent` blocks to improve rendering.

Example:

```itl
section $hero {

    intent $(
        Create a clean and modern landing page
        with generous spacing and a professional appearance.
    )

}
```

Depending on browser capabilities, the rendering engine may use this information to enhance layout, visuals, or accessibility while preserving the application's intended structure.

---

# Incremental Rendering

When only part of the application changes, the browser updates only the affected portions of the interface.

This improves performance and avoids unnecessary rendering.

---

# Responsive Rendering

Applications automatically adapt to different screen sizes.

The browser determines the most appropriate layout for:

- desktop
- tablet
- mobile
- future devices

Developers are not required to create separate layouts for each platform.

---

# Accessibility

Rendering should prioritize accessibility.

The browser should support:

- keyboard navigation
- screen readers
- scalable text
- sufficient color contrast
- semantic interface structure

Accessibility should be built into the rendering engine rather than relying solely on application developers.

---

# Performance

The rendering engine should be optimized for efficiency.

Typical optimizations include:

- lazy loading
- incremental updates
- intelligent asset caching
- efficient layout calculation

Applications should remain responsive even as they grow.

---

# Compiler Relationship

The compiler does not perform rendering.

Its responsibility ends after generating the Intermediate Representation (IR).

The browser is solely responsible for converting the IR into a user interface.

---

# Notes

- Rendering begins from the Intermediate Representation (IR).
- The browser determines how applications are presented.
- Developers express intent rather than implementation.
- Rendering is responsive and platform-aware.
- Themes and assets are applied during rendering.

---

# Version

Introduced in:

```
ITL 0.1
```