# Principles

The following principles define the foundation of Intent Language (ITL).

Every language feature, compiler enhancement, runtime capability, and ecosystem extension should align with these principles.

They serve as the long-term guide for the evolution of ITL.

---

# 1. Intent Over Implementation

The primary purpose of ITL is to describe **what** software should accomplish, not **how** it should be implemented.

Developers express intent.

The compiler determines implementation.

---

# 2. The Compiler Owns Boilerplate

Developers should never be required to write repetitive implementation that can be generated automatically.

Project structure, configuration files, framework conventions, and other boilerplate belong to the compiler.

---

# 3. Keep the Language Small

The core language should remain intentionally minimal.

Every new keyword, syntax rule, or language feature increases complexity.

New additions must provide significant value before becoming part of the language.

---

# 4. Clarity Over Cleverness

Programs should be easy to read and understand.

Readable intent is more valuable than compact or clever syntax.

The language should favor explicitness whenever it improves understanding.

---

# 5. Humans First

ITL programs are written for humans before they are interpreted by machines.

Reading an ITL program should feel like reading the specification of an application.

---

# 6. Deterministic by Default

The same ITL program should always produce the same result under the same compiler version and configuration.

Compilation should be predictable and reproducible.

Artificial intelligence may assist development, but it should never compromise deterministic compilation unless explicitly requested.

---

# 7. Framework Independence

Intent should outlive frameworks.

Frameworks evolve.

Libraries change.

Technologies become obsolete.

The application's intent should remain valid regardless of the implementation target.

---

# 8. Security by Design

Security is part of the language, not an optional feature.

Sensitive information must never be embedded directly into ITL source files.

Applications should declare capabilities explicitly while allowing the compiler to generate secure implementations.

---

# 9. Extensible, Not Bloated

The language should grow through a healthy ecosystem rather than an ever-growing core.

Features that serve specialized domains should be implemented as extensions rather than becoming permanent language features whenever practical.

---

# 10. Consistency Above Convenience

Every feature should behave consistently with the rest of the language.

A small amount of additional typing is acceptable if it improves consistency and predictability.

---

# 11. Backward Compatibility Matters

As ITL evolves, changes should minimize unnecessary breakage.

When breaking changes are unavoidable, they should be carefully documented and supported with migration paths whenever possible.

---

# 12. Open by Default

The language, compiler, and specification are developed in the open.

Design decisions should be transparent, documented, and open for community discussion.

---

# 13. AI Is Optional

ITL is designed to work well with artificial intelligence, but it does not require AI.

A complete ITL application should be compilable without internet access or cloud-based AI services whenever the selected backend supports it.

AI should enhance the development experience, not define it.

---

# 14. One Source of Truth

An application's intent should be declared once.

The compiler should eliminate duplication by generating the implementation required by each target platform.

Developers should not repeat the same information across multiple files.

---

# 15. Every Feature Must Justify Its Complexity

Complexity is one of the greatest threats to language design.

Before introducing a new keyword, syntax rule, or compiler feature, ask:

- Does this solve a real problem?
- Can it be expressed using existing language constructs?
- Does it make the language easier to understand?
- Will developers use it frequently?
- Is there a simpler alternative?

If the answer is no, the feature should not become part of the language.

---

# 16. Intent Is Stable

Implementation changes over time.

Intent should not.

An ITL program written today should continue to describe the same application tomorrow, even if the generated implementation evolves.

The language should preserve the developer's intent while allowing the compiler and backends to improve independently.

---

# The Guiding Question

Whenever a new proposal is made for ITL, it should first answer one question:

> **Does this make it easier for developers to express their intent?**

If it does, it belongs in the discussion.

If it only makes implementation more complex without improving the expression of intent, it probably does not belong in the language.

---

> **These principles are the constitution of Intent Language.**

> Features may evolve.

> Syntax may change.

> The compiler may improve.

> But these principles should remain the foundation upon which ITL is built.