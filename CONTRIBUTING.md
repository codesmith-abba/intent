# Contributing to Intent Language (ITL)

First, thank you for considering contributing to Intent Language (ITL)!

ITL is an open-source programming language focused on describing **intent rather than implementation**. Our goal is to make software development more expressive, portable, and AI-native.

Whether you're fixing a typo, improving documentation, designing a language feature, or implementing part of the compiler, your contribution is appreciated.

---

# Code of Conduct

Please be respectful and constructive.

We welcome contributors of all experience levels.

Healthy technical discussions are encouraged, but all conversations should remain professional and focused on improving the language.

---

# Before You Contribute

Before opening a Pull Request, please:

- Read the documentation.
- Search existing Issues and Pull Requests.
- Discuss major language changes before implementing them.
- Keep changes focused on a single feature or fix.

---

# Ways to Contribute

There are many ways to help ITL grow.

## Documentation

Improve:

- language documentation
- examples
- tutorials
- compiler documentation
- README
- API documentation

---

## Language Design

Help improve:

- syntax
- grammar
- keywords
- semantics
- language consistency

Large language proposals should begin as a GitHub Discussion or Issue before implementation.

---

## Compiler

Contribute to:

- Lexer
- Parser
- AST
- Semantic Analyzer
- IR
- Runtime
- Backend generators
- CLI

---

## Backends

Create or improve backend implementations.

Examples include:

- React
- Vue
- Angular
- Django
- Flutter
- React Native
- Next.js

Future backends are always welcome.

---

## Runtime

Help improve the ITL Runtime.

Examples:

- runtime management
- dependency management
- project generation
- caching
- environment preparation

---

## Plugins

In the future, ITL will support plugins that extend the language without modifying the compiler.

Plugin contributions will have their own development guide when the plugin system becomes available.

---

# Development Workflow

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test your changes.
5. Update documentation if necessary.
6. Submit a Pull Request.

Example:

```
main
    │
    └── feature/parser-imports
```

---

# Pull Requests

A good Pull Request should:

- solve one problem
- include clear commit history
- include documentation updates when appropriate
- avoid unrelated changes

Large Pull Requests are harder to review.

Prefer smaller, focused contributions.

---

# Documentation

Documentation is considered part of the project.

If you introduce:

- a new keyword
- a syntax change
- semantic changes
- compiler behavior

please update the corresponding documentation.

Documentation should remain synchronized with the language.

---

# Coding Style

Follow the existing project structure.

General guidelines:

- write readable code
- prefer clarity over cleverness
- keep functions small
- avoid unnecessary abstractions
- document public APIs

Consistency is more important than personal preference.

---

# Design Principles

Every contribution should align with ITL's philosophy.

Before implementing a feature, ask:

- Does this express intent?
- Does it simplify development?
- Does it reduce boilerplate?
- Does it improve readability?
- Can the compiler or backend handle this automatically?

If the answer is "no", reconsider the design.

---

# Language Evolution

The language should evolve carefully.

We value:

- simplicity
- consistency
- predictability
- extensibility
- backward compatibility whenever practical

Features should solve real problems rather than add unnecessary complexity.

---

# Reporting Bugs

When reporting a bug, include:

- ITL version
- operating system
- source code
- expected behavior
- actual behavior
- compiler output

A minimal reproducible example is greatly appreciated.

---

# Suggesting Features

Feature requests should explain:

- the problem being solved
- why existing features are insufficient
- the proposed syntax (if applicable)
- expected compiler behavior
- potential impact on existing code

Discussion is encouraged before implementation.

---

# Testing

Contributions should include tests whenever possible.

Examples include:

- lexer tests
- parser tests
- analyzer tests
- backend tests
- CLI tests

Documentation-only contributions do not require tests.

---

# Project Structure

```
docs/
itl/
examples/
tests/
```

Please place new files in the appropriate directory.

---

# Getting Help

If you're unsure where to start:

- browse open Issues
- improve documentation
- fix compiler diagnostics
- expand examples
- ask questions in Discussions

We are happy to help new contributors.

---

# Recognition

Every contribution matters.

Whether you improve a sentence, fix a bug, or implement a major compiler feature, you are helping shape the future of Intent Language.

Thank you for contributing to ITL ❤️