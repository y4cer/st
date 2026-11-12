# Independent review of the Shitty test adaptation

2026-11-12, separate agent `/root/review_st_tests`, requested by the user.
The review inspected production changes, adapter code, failure policy, provenance,
and reports; independently ran the contract tests and targeted gate/Termless checks.
Full suite execution and installation were performed by the primary agent.

## Improvements

- Tests execute real st.c/x.c and shared utf8.c. The expansion exposed an
  uninitialized wide-cell boundary during resize and signed CSI coordinate
  overflow; both have production fixes and focused regressions. Negative-count clearing
  was subsequently found and fixed as well.
- Every C target builds with `-Wall -Werror -Wpedantic`. Sanitizer builds also
  use `-fno-sanitize-recover=all` and retain leak detection.
- The reference inventory and exact failure/exclusion fingerprints make newly
  failing, unexpectedly passing, missing, or differently skipped cases visible.
  Process failures and adapter gaps are rejected even if added to a baseline.

## Problems found and fixed during review

1. Dummy palette callbacks made reset/replay cases pass without testing colors.
   Dynamic Xft callbacks now produce an explicit headless exclusion.
2. A native fixture's utf8encode stub discarded Alt input in MODE_8BIT.
   The existing production UTF-8 code now lives in utf8.c and is linked by both
   production and tests. Function bodies were independently checked unchanged.
3. Blanket launch-option exclusions discarded portable scenarios. Color profile
   and allowWindowOps options now map to representation/real core configuration.
   Libvterm tracks checked/skipped assertions and documents its projection.
4. Termless swallowed all exceptions and advertised reflow unconditionally.
   Its original case functions now run directly through an st backend reading
   real modes/title and declaring reflow unavailable. Exceptions retain type.
5. Early parallel normal/sanitized runs shared per-case output directories.
   Each report now uses its own directory; final comparisons use isolated runs.
6. The initial overflow fix mapped negative counts to zero, which CSI defaults
   to one. A reference DCH test caught the regression. Invalid negative counts
   now retain a negative sentinel. A stronger regression exposed old zero-count
   clearing; insert/delete/scroll now return early, and negative ECH is ignored.
   The reviewer independently verified all seven operations and 13 contracts.

## Costs and limits

- Around 15 MB in the working tree (including generated Python caches), about
  3 MB of compressed corpus data, and several minutes per complete run.
- Known differences are baseline observations, not desirable behavior or full
  feature compatibility. Early assertion failures leave later statements untested.
- Streaming-invariance cases only compare whole/chunked input to the same st;
  they are separated in COVERAGE.md from golden/reference comparisons.
- Headless tests do not validate real Xft glyph rendering or dynamic palette
  allocation. Partial/projection fixtures explicitly describe omitted fields.

The independent reviewer found no new product regression in the reviewed changes
and confirmed the adapter fixes. Final run results are recorded in COVERAGE.md.
