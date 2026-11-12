# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from run_unittest_group import iter_tests, select_group


class UnittestGroupTest(unittest.TestCase):
    def sample_suite(self):
        class SampleTest(unittest.TestCase):
            def test_a(self):
                pass

            def test_b(self):
                pass

            def test_c(self):
                pass

            def test_d(self):
                pass

            def test_e(self):
                pass

        tests = [
            SampleTest("test_a"),
            SampleTest("test_b"),
            SampleTest("test_c"),
            SampleTest("test_d"),
            SampleTest("test_e"),
        ]
        return unittest.TestSuite(
            [
                unittest.TestSuite(tests[:2]),
                unittest.TestSuite(tests[2:]),
            ]
        )

    def test_selects_tests_by_stable_ordinal(self):
        selected, total = select_group(self.sample_suite(), 1, 3)

        self.assertEqual(total, 5)
        self.assertEqual(
            [test.id().rsplit(".", 1)[-1] for test in iter_tests(selected)],
            ["test_b", "test_e"],
        )

    def test_groups_are_disjoint_and_complete(self):
        all_groups = []
        for group in range(3):
            selected, _ = select_group(self.sample_suite(), group, 3)
            all_groups.extend(
                test.id().rsplit(".", 1)[-1]
                for test in iter_tests(selected)
            )

        self.assertCountEqual(
            all_groups,
            ["test_a", "test_b", "test_c", "test_d", "test_e"],
        )
        self.assertEqual(len(all_groups), len(set(all_groups)))

    def test_rejects_invalid_groups(self):
        for group, group_count in ((0, 0), (-1, 3), (3, 3)):
            with self.subTest(group=group, group_count=group_count):
                with self.assertRaises(ValueError):
                    select_group(self.sample_suite(), group, group_count)


if __name__ == "__main__":
    unittest.main()
