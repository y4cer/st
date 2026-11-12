# Shitty reference suite for this st fork

Reference: [pg83/shitty](https://github.com/pg83/shitty/tree/509bd3f95778729d9890c68ab150d94bff372a0e),
revision `509bd3f95778729d9890c68ab150d94bff372a0e`, fetched 2026-11-12.
The user's standing instruction is to use Shitty as the reference for future st work.

## Running

`make test` runs the original native tests, the bridge contract checks, and this
reference suite. `make test-sanitize` repeats them with AddressSanitizer,
UndefinedBehaviorSanitizer and LeakSanitizer. Every C target uses
`-Wall -Werror -Wpedantic`. Tests need Python 3.10+, the normal st build dependencies,
and a C.UTF-8 locale. They do not need a display, network, user configuration, or a
Shitty binary. The build/test reference environment is Ubuntu 22.04 / glibc.

LeakSanitizer cannot run under a ptrace-based sandbox: use a normal host process
rather than disabling leak detection. Test artifacts and decompressed corpora live
under ignored `tests/bin/`. A full run takes several minutes.

## What actually runs

- `bridge.c` executes **the repository's real st.c**: parsing, cells, cursor,
  attributes, screen swaps, resize, history, selection, and terminal replies.
- `frontend.c` executes **the repository's real x.c**: key mapping/routing, focus
  reports, paste delivery and mouse-report encoding. X11 lookup/property callbacks
  supply deterministic platform input; no desktop or clipboard is touched.
- `harness.py` maps Shitty's API, half-open coordinates, platform key IDs and
  snapshot representation to those bridges. It is not a terminal implementation.
- `upstream/` preserves the 286 Python test files unchanged. `inventory.json`
  records 6,201 source method declarations / 6,194 unique IDs (some upstream
  methods override earlier definitions).
- `corpora.tar.gz` preserves the nested source fixtures, adapters and attribution;
  `corpora-index.json` records hashes for its 6,021 files. `corpora.py` inventories
  2,612 named corpus cases plus 400 fuzz seeds. `sources.json` pins vendored bytes.

The runner compares the original assertions wherever the API is portable.
For the Alacritty and application-output recordings it explicitly projects golden
cells onto st's fields: characters, width/continuation/wrap flags, supported
rendition and colors. Grapheme, semantic, hyperlink, protected/written-cell and
renderer-private fields are not claimed. Application recordings use their original
bold-brightens-colors profile. Kitty/WezTerm/Ghostty/Konsole parser fixtures and fuzz
seeds additionally compare whole vs chunked input using **st state and replies**;
this establishes streaming invariance, not conformance to another parser's callbacks.

## Result policy

`baseline.json` is a **compatibility inventory, not a blanket green result**:

- `pass`: the portable assertions pass.
- `failure`: a documented, still-executed difference (reported as XFAIL). The
  precise assertion/diagnostic fingerprint is pinned. A new failure, changed
  failure, or unexpected pass fails `make test` and requires review.
- `excluded`: an explicit unsupported feature, implementation-specific API,
  duplicate source inventory, or platform/interactive-only fixture. Changes in
  the reason also fail the gate. `scope.py` decides these from capabilities and
  source usage, not from whether a test happened to pass.

XFAIL is **not coverage of the rest of a failing scenario**: an assertion can stop
that scenario early. The baseline does not say that each difference is desirable;
there are real behavior gaps to address. In particular CSI overflow handling,
margin barriers, history/resize policies and legacy key encodings differ from the
reference. Unsupported features are not silently added to st just to pass tests.
Crashes, timeouts, missing adapter APIs and sanitizer reports are not acceptable
expected failures. The thirteen contract checks validate the adapter separately; four gate-policy
regressions check rejection of crashes, changed results and lost assertions.
See [REVIEW.md](REVIEW.md) for the independent review and corrections.

Full diagnostics are in `tests/bin/reference-{python,corpora}[-asan].json`.
`COVERAGE.md` summarizes the audited result by source module/corpus. Review those
files and the source case before updating an expectation; there is intentionally
no automatic “accept failures” command in the test target.

## Adaptation boundaries

Shitty-specific GPU/font shaping, Cocoa/Wayland window lifecycle, multi-session
management, configuration parser, shell integration, Kitty protocols, reflow and
Unicode-table APIs have no direct st equivalent. Native `copy_*`, selection,
X11 INCR and history stress regressions remain alongside this suite.

Interactive tack/vttest/wraptest drivers require Shitty's process-control API and
are inventoried separately; corresponding portable cursor/editing/wrapping cases
run through the Python ports, libvterm and esctest. Performance-only vtebench jobs
are not correctness tests. Windows Terminal source inventories are represented by
the executable root Python ports. Platform mouse-selection gestures are excluded
where they cannot be mapped faithfully; direct st selection tests still execute.
Dynamic Xft palette allocation and actual glyph rendering are outside the headless
bridges. Every call to a dynamic palette callback raises an explicit exclusion;
it cannot supply a dummy color or count as a passing color test. `-allowWindowOps`
maps to the real core variable. `-/+boldColors` select snapshot color profiles.
Libvterm's fixed fixture palette is an explicit index-to-RGB projection, without
OSC mutation. Its text comparisons trim trailing spaces on both sides because st
has no written-space bit; interior spaces and line breaks remain significant.
Libvterm reports checked/skipped assertion counts, including partial fixtures;
these counts are pinned by the gate. They are not complete fixture conformance.
Termless calls the original case functions directly, bypassing its CLI catch-all;
its backend reads real st modes/title and declares reflow unavailable.

## Updating the reference

1. Fetch an explicit Shitty revision and inspect its test and licensing changes.
2. Refresh unchanged upstream sources, archives, inventories and SHA256 manifests.
3. Review capability boundaries and adapter changes; preserve the real-code path.
4. Run `run.py --audit` and `corpora.py --audit` to collect full diagnostics.
5. Review every changed disposition. Fix regressions rather than merely recording
   their current result; use the reference assertions to justify deliberate gaps.
6. Update `baseline.json` only after review; run both strict targets. The ordinary
   and sanitized runs must have identical dispositions/fingerprints.

## Provenance and licenses

Shitty's contribution layer offers MIT terms (`LICENSE.MIT`); its imported baseline
and third-party material keep their original licenses. This does **not** relicense
all of Shitty as MIT. Per-corpus notices are retained under `licenses/` and inside
the source archive. Test/source fixtures are distinct from the st production
binary. No Shitty terminal implementation is linked into st.
