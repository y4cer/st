# st development

- For every future st change, use https://github.com/pg83/shitty as the reference for terminal behavior, regression cases, and relevant implementation ideas. This is the user's standing preference (2026-11-12).
- Compare against the pinned revision in tests/shitty/README.md; inspect newer upstream changes when relevant. Preserve st's supported feature boundary and document deliberate differences rather than silently weakening assertions.
- Exercise real st.c/x.c through the test adapters. Do not replace terminal behavior with a Python model. Keep upstream test provenance, licenses, and explicit exclusions/known differences current.
- Run make test and make test-sanitize after terminal behavior or test-adapter changes. Keep config.h and config.def.h synchronized.
- Compile every C target (including test adapters and sanitizer builds) with `-Wall -Werror -Wpedantic`; fix diagnostics rather than suppressing them. User requirement, 2026-11-12.
- Do not automatically accept new XFAILs or skips. Inspect the exact source assertion and failure signature; crashes, timeouts, adapter gaps and sanitizer errors must fail. XFAIL is not a passing compatibility claim.
