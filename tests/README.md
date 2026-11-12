# Regression suite

Run from the repository root:

```sh
make test
make test-sanitize
```

Requirements: C compiler, Python 3, X11/Xft/fontconfig development files (the
same libraries used by st), UTF-8 locale, and GCC/Clang sanitizer runtimes
for `test-sanitize`. No graphical session or network access is required.

- `test_terminal.c` compiles the **real st.c and browse.c**, using frontend
  stubs. Tests feed bytes through `twrite`, allocate with `tnew`, resize with
  `tresize`, and inspect actual cells, cursor, selection and history. It also
  includes a fixed-seed 2,000-operation stress test.
- `test_x11.c` compiles the **real x.c**. A deterministic simulated X11
  property transport checks INCR acknowledgement, cancellation, bracketed
  paste boundaries and allocation/free balance. Other tests exercise key
  mapping, focus-report suppression, opacity parsing and premultiplication.
  These are frontend unit tests, not a claim to test a real compositor/XIM.
- `run.py` launches each case in a fresh process, sets a timeout, reports all
  failures and returns nonzero if any case fails. Sanitized runs enable
  AddressSanitizer, UndefinedBehaviorSanitizer and leak detection. Test
  binaries are isolated from production objects and are not installed.

## Shitty provenance and license

Selected cases are C adaptations of the public MIT-licensed test contribution
layer of https://github.com/pg83/shitty at commit
`509bd3f95778729d9890c68ab150d94bff372a0e`:

- `tst/test_xtermjs_input_handler_margins.py`: DECSTBM defaults/clamping/home,
  scrolling within margins, insert/delete lines, ICH with delayed wrap.
- `tst/test_xtermjs_input_handler_text.py`: rendition reset, alternate-buffer
  round trip and DEC graphics.
- `tst/test_xtermjs_input_handler_wide.py`: wide-cell erase and edit boundaries.
- `tst/test_resize_wide_grapheme.py`: truncation of wide glyphs on resize.
- `tst/test_parser_states.py`: embedded NUL during CSI and incremental parsing.
- `tst/test_reset_matrix.py`: RIS restoring tab stops and defaults.
- `tst/test_scrollback.py`: reverse index, history isolation and scrolled views.

The corresponding notices are retained in `LICENSE.shitty` and
`LICENSE.xtermjs`. **The Shitty repository as a whole is not MIT**: its imported
baseline contains GPL code. No GPL terminal implementation is imported here.
The suite is a selected adaptation, not a port of Shitty's entire test corpus.
Custom copy-mode/history/X11 regressions are additional tests for this fork.

Unsupported features (full grapheme clusters, resize reflow, DECSTR, Kitty
keyboard negotiation) are not advertised as implemented or covered.
