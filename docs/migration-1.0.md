# ITL v1.0 Migration Notes

ITL v1.0 is the first stable release. There is no earlier stable language contract to migrate from.

## From the pre-v1.0 repository state

### 1. Treat the implemented language as the contract

Use `spec/ITL-0.1.md` and `docs/language-reference.md` as the source-language references. Do not rely on the older README examples that describe experimental or future syntax.

### 2. Do not use lexer-only keywords as language features

Some keywords remain reserved lexically but are not accepted by the parser. Existing source files using unsupported declarations must be rewritten using the supported grammar.

### 3. Use the packaged CLI

Install ITL with:

```bash
python -m pip install .
```

Then use:

```bash
itl check <project>
itl build <project>
itl dev <project>
```

### 4. Rebuild generated state

Generated `.project` state is implementation data. For projects carried forward from development snapshots, run a clean build when compatibility-sensitive generated state is present:

```bash
itl clean <project>
itl build <project>
```

### 5. Plugins

Review plugin compatibility and trust before upgrading. Plugins remain implementation extensions and are not part of ITL source syntax.

## No automatic source rewrite

v1.0 does not introduce an automatic migration tool. The language did not have a prior stable compatibility contract, so migration is intentionally explicit and source-driven.
