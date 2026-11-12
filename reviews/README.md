# Independent review notes

The three neighboring reports were produced by three independent Pi subprocesses
before fixes, with read-only instructions. Their original findings are retained
as review artifacts, not as a description of current bugs. All three used
openai-codex/gpt-6-astra with separate contexts.

Resolution:
- `history.md`: resize invalidates ordinary selections; rectangular copy no
  longer forms/dereferences a pointer before a line; RI no longer changes
  history; navigation clamps to populated history and rejects alternate
  screen; copy-mode search skips wide continuations; selection includes the
  wide leading cell; soft-wrap spaces are preserved.
- `x11.md`: INCR is drained on cancellation and bracketed once per transfer;
  alpha colors/pixels are premultiplied; Cyrillic command keys are normalized
  even in the first keyboard group; CapsLock is ignored for modifier matching
  and Ctrl-modified Enter combinations are explicit; focus reports are
  suppressed during copy mode.
- `test-sources.md`: added a selected headless test adaptation with upstream
  notices. Fixed history pollution from interior scroll regions and broken
  wide-cell pairs after erase/edit/resize. Added reset and parser regressions.

Additional fixes include clearing history on RIS, usable page scrolling in
one-row windows, preserving explicitly selected spaces, and rejecting NaN or
malformed opacity values.

Tests run with `make test` and `make test-sanitize`. Tests exercise real core
code; the X11 transport is simulated. This review is not a full terminal
standards conformance or security audit.
