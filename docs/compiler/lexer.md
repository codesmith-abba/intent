# Lexer

The Lexer is the first stage of the ITL compiler.

Its responsibility is to read raw ITL source code and convert it into a sequence of tokens that can be understood by the parser.

The lexer does not understand the structure or meaning of the program. It only recognizes lexical elements such as keywords, strings, symbols, and comments.

---

# Purpose

The lexer transforms plain text into a stream of tokens.

Its responsibilities include:

- reading source files
- recognizing keywords
- recognizing strings
- recognizing punctuation
- ignoring whitespace
- ignoring comments
- reporting lexical errors

---

# Position in the Compiler

```
ITL Source
      │
      ▼
Lexer
      │
      ▼
Token Stream
      │
      ▼
Parser
```

---

# Input

The lexer receives the contents of one or more ITL source files.

Example:

```itl
app $Portfolio {

    page $home {

        theme $dark

    }

}
```

---

# Output

The lexer produces a sequence of tokens.

Example:

```
APP
STRING("Portfolio")
LEFT_BRACE

PAGE
STRING("home")
LEFT_BRACE

THEME
STRING("dark")

RIGHT_BRACE
RIGHT_BRACE

EOF
```

The parser consumes these tokens to build the Abstract Syntax Tree (AST).

---

# Tokens

A token represents the smallest meaningful unit in the language.

Examples include:

- keywords
- strings
- braces
- end of file

Example:

```itl
page $home {

}
```

Produces:

```
PAGE
STRING("home")
LEFT_BRACE
RIGHT_BRACE
```

---

# Keywords

The lexer recognizes reserved keywords.

Examples include:

- app
- page
- hero
- section
- image
- import
- framework
- target
- theme
- intent

When one of these words is encountered, the lexer produces the corresponding keyword token.

---

# Strings

ITL supports two string forms.

Single-line strings:

```itl
headline $Welcome
```

Everything after `$` until the end of the line becomes a single string token.

Multi-line strings:

```itl
intent $(
    Build a modern portfolio website.
)
```

Everything between `$(` and the matching `)` becomes a single string token.

---

# Symbols

The lexer recognizes punctuation symbols.

Current symbols include:

```
{
}
```

These are emitted as individual tokens.

---

# Comments

Single-line comments begin with:

```itl
//
```

Everything from `//` to the end of the line is ignored.

Example:

```itl
// Homepage
page $home {

}
```

Comments do not produce tokens.

---

# Whitespace

Whitespace outside strings has no semantic meaning.

The lexer ignores:

- spaces
- tabs
- blank lines
- carriage returns

Newline information may be preserved internally for diagnostics.

---

# Errors

If the lexer encounters invalid input, it reports a lexical error.

Example:

```itl
@
```

Compiler error:

```
Unexpected character '@'.
```

Example:

```itl
intent $(
Hello
```

Compiler error:

```
Unterminated string.
```

---

# Compiler Behavior

The lexer processes the source code from left to right.

For each character it:

1. identifies the current lexical element
2. produces the appropriate token
3. skips ignored characters
4. continues until the end of the source

Finally, it appends an EOF token.

---

# End of File

After the entire source has been processed, the lexer emits a final EOF token.

Example:

```
EOF
```

The EOF token signals the parser that no more input remains.

---

# Notes

- The lexer does not build the AST.
- The lexer does not validate program semantics.
- The lexer only recognizes lexical elements.
- Comments and whitespace are ignored.
- The lexer always produces an EOF token.

---

# Version

Introduced in:

```
ITL 0.1
```