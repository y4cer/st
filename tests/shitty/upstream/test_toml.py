# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import json
import math
import os
import subprocess
import unittest
from pathlib import Path

CORPUS = Path(__file__).parent / "toml"
DUMP_BINARY = os.environ.get("SHITTY_TOML_DUMP_BINARY", "")


def run_dump_batch(paths):
    # One process for the whole corpus: per-file subprocesses pay the
    # sanitizer startup cost hundreds of times over and time the shard out
    # under ASan.
    result = subprocess.run(
        [DUMP_BINARY, *map(str, paths)],
        capture_output=True,
        timeout=120,
    )
    outcomes = {}
    for line in result.stdout.decode().splitlines():
        path, _, rest = line.partition("\t")
        status, _, encoded = rest.partition("\t")
        outcomes[path] = (status, encoded)
    return outcomes


def normalize_moment(kind, text):
    text = text.replace(" ", "T").replace("t", "T").replace("z", "Z")
    if kind in ("datetime", "datetime-local", "time-local"):
        head, dot, frac = text.partition(".")
        tail = ""
        if dot:
            for zone in ("Z", "+", "-"):
                # A '-' after the dot can only start a zone offset: the date
                # part before the dot has its own dashes, but they are all
                # before any '.' in the string.
                cut = frac.find(zone)
                if cut != -1:
                    tail = frac[cut:]
                    frac = frac[:cut]
                    break
            frac = frac.rstrip("0")
            text = head + ("." + frac if frac else "") + tail
    if kind == "datetime":
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        text = text[:-6] + text[-6:].replace("-00:00", "+00:00")
    return text


def same_value(expected, actual):
    if isinstance(expected, dict) and "type" in expected and "value" in expected:
        if not isinstance(actual, dict) or actual.get("type") != expected["type"]:
            return False
        kind = expected["type"]
        want = expected["value"]
        have = actual["value"]
        if kind == "integer":
            return int(want) == int(have)
        if kind == "float":
            if want in ("nan", "-nan", "+nan"):
                return have == "nan"
            try:
                left = float(want)
                right = float(have)
            except ValueError:
                return False
            if math.isinf(left) or math.isinf(right):
                return left == right
            return math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-300)
        if kind in ("datetime", "datetime-local", "date-local", "time-local"):
            return normalize_moment(kind, want) == normalize_moment(kind, have)
        return want == have
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(expected) != set(actual):
            return False
        return all(same_value(expected[key], actual[key]) for key in expected)
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return False
        return all(same_value(want, have) for want, have in zip(expected, actual))
    return expected == actual


class TomlComplianceTest(unittest.TestCase):
    maxDiff = None

    def test_valid_documents_match_their_reference_json(self):
        cases = sorted((CORPUS / "valid").rglob("*.toml"))
        self.assertGreater(len(cases), 150)
        outcomes = run_dump_batch(cases)
        for case in cases:
            with self.subTest(case=str(case.relative_to(CORPUS))):
                status, encoded = outcomes.get(str(case), ("missing", ""))
                self.assertEqual(status, "ok", "rejected valid document")
                expected = json.loads(case.with_suffix(".json").read_text())
                actual = json.loads(encoded)
                self.assertTrue(
                    same_value(expected, actual),
                    f"expected {expected!r}, parsed {actual!r}",
                )

    def test_invalid_documents_are_rejected(self):
        cases = sorted((CORPUS / "invalid").rglob("*.toml"))
        self.assertGreater(len(cases), 300)
        outcomes = run_dump_batch(cases)
        for case in cases:
            with self.subTest(case=str(case.relative_to(CORPUS))):
                status, _ = outcomes.get(str(case), ("missing", ""))
                self.assertEqual(status, "error", "accepted invalid document")


    def test_unreadable_files_and_the_stdin_mode(self):
        result = subprocess.run(
            [DUMP_BINARY, "/nonexistent/document.toml"],
            capture_output=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.decode().split("\t")[1].strip(), "error"
        )
        result = subprocess.run(
            [DUMP_BINARY], input=b"a = 1\n", capture_output=True, timeout=60
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout), {"a": {"type": "integer", "value": "1"}}
        )
        result = subprocess.run(
            [DUMP_BINARY], input=b"a = [\n", capture_output=True, timeout=60
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"syntax error", result.stderr)


if __name__ == "__main__":
    unittest.main()
