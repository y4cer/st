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
- `test_sessions.c` checks the real session manager: incremental parser and
  reply isolation, copy/history ownership, resize, stable IDs, queued writes,
  focus routing, actual child exit and refused PTY creation. `run_sessions.py`
  runs its seven cases with deadlines, also under all three sanitizers.
- `make test-x11` runs `test_tabs_x11.py` against the production binary in its
  own Xvfb server, with three real PTYs. It checks keyboard/copy-mode/keyboard-lock
  routing, background replies and titles, dynamic Xft palette isolation, resize
  of all children, tab clicks, shell exits and hiding the bar. Screenshots are
  saved to `tests/bin/tabs-{three,one}.png`. It requires Xvfb, libXtst and Pillow;
  `ST_XVFB` may point to a non-system Xvfb binary. This test never uses the user's
  display. Headless INCR tests separately cover paste destination across a
  switch and draining a transfer after its recipient closes.
  Pixel comparisons also verify that old greeting/output rows survive closing
  the first tab and hiding the bar, and a shrinking pixel resize that keeps the
  same cell grid. That last case does not necessarily emit Expose; replacing the
  backing pixmap must explicitly redraw every row.
  It also fills the viewport, grows its height and compares the bottom row at
  its new pixel position, then checks that shrinking restores the entire image.
- Seven native vertical-resize cases cover history restoration, insufficient
  history, short output, repeated shrink/grow, alternate screen, saved cursors
  and a parked scrollback view. Synthetic top padding is discarded on shrink;
  explicit writes into it turn it into real content that must be retained.
- Five native clear-screen cases cover preservation of populated rows and blank
  lines between them, repeated empty clears, cursor/margins, partial/alternate
  erases, resize padding, and wide/color cells through history-ring wraparound.
  The session test clears a background tab and checks ownership. X11 compares
  old output pixels with scrollback after a full erase and Shift+PageUp.

- Nine native URL cases cover scheme case, punctuation, malformed/concealed
  text, soft/hard line boundaries, wide cells, the UTF-8 byte limit, history,
  snapshots and session isolation. `make test-x11` also runs `test_urls_x11.py`:
  real pixel underlines and bold hover, pointer gestures, stale-target cancellation, application
  mouse reports and a private fake opener recording exact argv. It never opens
  a browser. See [URL scope and provenance](shitty/URLS.md).

- Copy-mode operator tests in `test_browse_ops.h` exercise the real snapshot,
  command state and clipboard. X11 also types `yw`, `ye`, `yW`, `y$`, counts,
  `yG`, `yy` and Escape, reads both PRIMARY/CLIPBOARD, and checks that keys do
  not reach the live PTY. Physical Shift presses are included in these tests.
  Scope and provenance: [Vim-style operators](shitty/VIM.md).

- `test_fonts_x11.py` (also in `make test-x11`) exercises actual Xft glyph
  uploads, all four font styles, large glyphs and an explicitly selected color
  font. It requires a color emoji font such as Noto Color Emoji. This regresses
  the Pi `RenderAddGlyphs / BadLength` crash with its original three codepoints;
  screenshots and delayed liveness checks ensure actual rendering took place.
  Xft older than 2.3.5 uses monochrome fallback, including for primary fonts;
  newer runtime libraries keep color support. This is inspired by the pinned
  Shitty `tst/test_color_font_render.py`, but does not claim its color-pixel or
  ZWJ-shaping assertions. `ST_TEST_ST` can select an old binary to verify that
  the regression fails. Logs contain no literal emoji.

## Full Shitty reference suite

The selected native adaptations below are now supplemented by the complete
reference inventory and portable adapters in [shitty/README.md](shitty/README.md).
Both make targets run it. See [coverage](shitty/COVERAGE.md) for passing cases,
explicit exclusions and documented behavior differences; XFAIL is not a pass.
All C targets compile with `-Wall -Werror -Wpedantic`.

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
- `tst/test_plain_uri_input.py`: plain-URL detection, cell mapping, limits and
  underline/open behavior, adapted through core and real X11 tests.

The corresponding notices are retained in `LICENSE.shitty` and
`LICENSE.xtermjs`. **The Shitty repository as a whole is not MIT**: its imported
baseline contains GPL code. No GPL terminal implementation is imported here.
The native C suite is a selected adaptation. The complete imported inventory
and its portable execution scope are documented under shitty/.
Custom copy-mode/history/X11 regressions are additional tests for this fork.

Unsupported features (full grapheme clusters, resize reflow, DECSTR, Kitty
keyboard negotiation) are not advertised as implemented or covered.
