# Intent Language Specification

**Version:** 0.1 (Draft)

The Intent Language (ITL) Specification defines the syntax, semantics, compilation process, runtime model, and design principles of the language.

This document serves as the primary reference for compiler developers, tool authors, contributors, and language users.

The specification evolves alongside the language.

---

# Purpose

The purpose of this specification is to provide a precise definition of Intent Language.

It answers questions such as:

- What is valid ITL syntax?
- What does an ITL program mean?
- How should the compiler interpret it?
- How should tools behave?
- What guarantees does the language provide?

Whenever ambiguity exists, this specification is the source of truth.

---

# Specification Structure

The specification is divided into the following sections.

## 1. Overview

Introduces Intent Language and its goals.

Reference:

```
docs/overview.md
```

---

## 2. Philosophy

Explains the design philosophy behind the language.

Reference:

```
docs/philosophy.md
```

---

## 3. Principles

Defines the long-term principles that guide language evolution.

Reference:

```
docs/principles.md
```

---

## 4. Lexical Structure

Defines how source code is interpreted before parsing.

Topics include:

- Characters
- Tokens
- Keywords
- Identifiers
- Strings
- Comments
- Whitespace

Reference:

```
docs/syntax/
```

---

## 5. Grammar

Defines the formal syntax of ITL.

Future versions of the specification will include a complete EBNF grammar.

Topics include:

- Applications
- Pages
- Components
- Blocks
- Expressions
- Statements

Reference:

```
docs/syntax/grammar.md
```

---

## 6. Keywords

Each keyword has its own specification.

Examples:

```
app

page

hero

section

target

framework
```

Reference:

```
docs/keywords/
```

---

## 7. Semantics

Syntax defines how programs are written.

Semantics define what they mean.

Topics include:

- Applications
- Pages
- Components
- Targets
- Assets
- Runtime behavior

Reference:

```
docs/semantics/
```

---

## 8. Compiler

Defines how ITL programs are compiled.

Compilation pipeline:

```
Source (.itl)

↓

Lexer

↓

Parser

↓

AST

↓

Semantic Analyzer

↓

Intermediate Representation (IR)

↓

Backend

↓

Generated Project
```

Reference:

```
docs/compiler/
```

---

## 9. Runtime

Defines how generated applications behave.

Topics include:

- Rendering
- State
- Navigation
- Events
- Assets

Reference:

```
docs/browser/
```

---

## 10. Extensions

Defines how ITL can grow without expanding the core language.

Topics include:

- Packages
- Plugins
- Compiler extensions
- Backend extensions

Reference:

```
docs/plugins/
```

---

## 11. Examples

Provides complete reference applications.

Examples include:

- Portfolio
- Landing Page
- E-commerce
- Blog
- Dashboard

Reference:

```
docs/examples/
```

---

## 12. RFCs

Major language changes begin as RFCs.

Every proposal should explain:

- Motivation
- Design
- Alternatives
- Backward compatibility
- Implementation strategy

Reference:

```
docs/rfcs/
```

---

# Versioning

The language specification follows semantic versioning.

Major versions may introduce breaking language changes.

Minor versions introduce backward-compatible language features.

Patch versions clarify documentation and fix specification errors.

Example:

```
0.1.0

0.2.0

1.0.0
```

---

# Conformance

An implementation is considered conformant if it follows the rules defined by this specification.

Examples of implementations include:

- ITL Compiler
- Language Server
- Formatter
- Static Analyzer
- IDE Integrations

Whenever implementation behavior differs from this specification, the specification takes precedence.

---

# Language Evolution

Intent Language is an evolving research project.

Changes to the language should follow the RFC process before becoming part of the specification.

The long-term objective is to maintain a language that is:

- Small
- Predictable
- Human-readable
- Secure
- Extensible
- Framework-independent

---

# Source of Truth

This specification is the authoritative definition of Intent Language.

Compiler implementations should conform to the specification.

Documentation should reference the specification.

Language discussions should begin from the specification.

---

> **Programming by intention, not implementation.**