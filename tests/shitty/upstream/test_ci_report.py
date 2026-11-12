# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "ci_report",
    ROOT / "dev" / "ci_report.py",
)
CI_REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CI_REPORT)


class CiReportTests(unittest.TestCase):
    def test_collects_test_and_sanitizer_failures_but_not_xfails(self):
        findings = CI_REPORT.collect_findings(
            "shitty-tests> XFAIL VTE/known\n"
            "shitty-tests> FAIL xterm-vttests/resize\n"
            "FAILED (failures=1)\n"
            "==42==ERROR: AddressSanitizer: heap-use-after-free\n"
            "screen.cpp:7:9: runtime error: load of null pointer\n"
        )

        self.assertEqual(
            [finding.text for finding in findings],
            [
                "FAIL xterm-vttests/resize",
                "FAILED (failures=1)",
                "==42==ERROR: AddressSanitizer: heap-use-after-free",
                "runtime error: load of null pointer",
            ],
        )
        self.assertEqual(findings[-1].file, "screen.cpp")
        self.assertEqual(findings[-1].line, 7)
        self.assertEqual(findings[-1].column, 9)

    def test_compiler_error_becomes_a_source_annotation(self):
        findings = CI_REPORT.collect_findings(
            "shitty> /build/source/parser.cpp:12:3: error: broken parser\n"
        )

        self.assertEqual(
            findings,
            [
                CI_REPORT.Finding(
                    "error: broken parser",
                    "parser.cpp",
                    12,
                    3,
                )
            ],
        )
        self.assertEqual(
            CI_REPORT.annotation(findings[0], "Build"),
            "::error title=Build,file=parser.cpp,line=12,col=3::"
            "error: broken parser",
        )

    def test_summary_contains_reproduction_and_escapes_log_text(self):
        summary = CI_REPORT.render_summary(
            "Tests",
            "nix build .#checks.x86_64-linux.tests",
            [CI_REPORT.Finding("FAIL <case>")],
            True,
        )

        self.assertIn("nix build .#checks.x86_64-linux.tests", summary)
        self.assertIn("FAIL &lt;case&gt;", summary)


if __name__ == "__main__":
    unittest.main()
