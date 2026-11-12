"""Failure-policy regressions, including a mistakenly edited baseline."""
import unittest
from check import compare, signature


def baseline(record):
    return {'case': {'status': record['status'], 'signature': signature(record)}}


class GateTest(unittest.TestCase):
    def test_process_errors_never_become_expected_failures(self):
        for kind in ('RuntimeError', 'TimeoutError', 'BrokenPipeError'):
            record={'status':'failure','error_type':kind,'reason':'child failed'}
            with self.subTest(kind=kind):
                self.assertTrue(compare({'case':record},baseline(record)))

    def test_assertion_change_and_unexpected_pass_require_review(self):
        old={'status':'failure','error_type':'AssertionError','reason':'cursor mismatch'}
        self.assertFalse(compare({'case':old},baseline(old)))
        for new in ({'status':'pass'},dict(old,reason='history mismatch')):
            with self.subTest(record=new):
                self.assertTrue(compare({'case':new},baseline(old)))

    def test_partial_fixture_cannot_silently_skip_more_assertions(self):
        old={'status':'pass','coverage':{'checked':35,'skipped':1}}
        new={'status':'pass','coverage':{'checked':34,'skipped':2}}
        self.assertTrue(compare({'case':new},baseline(old)))

    def test_inventory_and_exclusions_cannot_silently_change(self):
        old={'status':'excluded','reason':'requires Xft display'}
        self.assertTrue(compare({},baseline(old)))
        self.assertTrue(compare({'case':dict(old,reason='missing adapter')},baseline(old)))
        gap={'status':'adapter-gap','reason':'missing adapter'}
        self.assertTrue(compare({'case':gap},baseline(gap)))


if __name__=='__main__':unittest.main()
