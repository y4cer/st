# Plain web links

Reference: pg83/shitty revision `509bd3f95778729d9890c68ab150d94bff372a0e`,
`upstream/test_plain_uri_input.py` (MIT, unchanged).

The native cases in `tests/test_terminal.c` adapt its case-insensitive scheme,
malformed/empty target, surrounding punctuation and balanced parentheses,
soft-wrap versus hard-newline, scrollback/wide-cell, concealed text and 4096-byte
scan-limit scenarios to the real st core. They also check immutable copy snapshots,
per-tab/alternate-screen isolation, exact cell masks and unchanged stored attributes.

`tests/test_urls_x11.py` adapts complete-link underlining and content-change
invalidation through real X11 events, pixels and PTYs. It additionally checks
Ctrl-click release, drag/content-change/tab-close cancellation, application mouse
report priority, wrapped URLs, scrollback and copy mode, and opener argument
integrity with shell metacharacters. Its private `xdg-open` records argv; it never
launches a browser or contacts the URL. Run with `make test-x11` (Xvfb, Xtst,
Python Pillow required).

Deliberate boundary: st detects visible http://, https:// and www. addresses;
www. opens with https:// prepended. Shitty's configurable arbitrary scheme list,
OSC 8 precedence, pointer icon state, combining-grapheme and DEC double-width
mapping remain outside this implementation. No OSC 8 URL is inferred from a
label. Core Glyph attributes are not changed by presentation. Copy mode's status
line is excluded. Only st's existing ATTR_WRAP connections are joined; explicit
newlines and lost connections after width changes are not reconstructed.

Consequently the original Shitty desktop-state/render API tests remain explicitly
excluded by the reference adapter. These native adaptations are additional
coverage, not a claim that the unmodified desktop API suite passes.

Hover refinement (2026-11-13): the hovered cell range is marked separately
from other occurrences of the same URI. Bold is applied to a temporary Glyph
row before font-spec generation. X11 tests compare hover pixels with actual
SGR bold and verify leave/re-entry, identical URIs, soft wrap and stationary
pointer invalidation, adapting Shitty
`test_stationary_hover_is_recomputed_after_content_changes`. Hover is active
without Ctrl; mouse reporting continues to follow application modes.
