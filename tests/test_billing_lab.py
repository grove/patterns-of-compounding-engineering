"""Checks that the teaching examples fail and pass for the stated reasons."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))
import billing_lab as lab


class BillingLabTests(unittest.TestCase):
    def command(self, *args):
        result = subprocess.run(
            [sys.executable, str(ROOT / "examples" / "billing_lab.py"), *args],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_default_replay_applies_payment_once(self):
        status, report = self.command("replay")
        self.assertEqual(status, 0)
        self.assertEqual(report["implementation"], "fixed")
        self.assertEqual(report["observed"], {"paid_cents": 2400, "applied_events": 1})
        self.assertTrue(report["matches"])

    def test_buggy_replay_exposes_the_original_failure(self):
        status, report = self.command("replay", "--implementation", "buggy")
        self.assertEqual(status, 1)
        self.assertEqual(report["expected"], {"paid_cents": 2400, "applied_events": 1})
        self.assertEqual(report["observed"], {"paid_cents": 4800, "applied_events": 2})
        self.assertFalse(report["matches"])

    def test_comparison_defaults_to_correct_candidate(self):
        status, report = self.command("compare")
        self.assertEqual(status, 0)
        self.assertEqual(report["candidate"], "correct")
        self.assertEqual(report["differences"], [])

    def test_comparison_preserves_a_useful_counterexample(self):
        status, report = self.command("compare", "--candidate", "buggy")
        self.assertEqual(status, 1)
        mismatch = next(case for case in report["differences"] if case["case"] == "excess-credit")
        self.assertEqual(mismatch["available_credit"], 1200)
        self.assertEqual(mismatch["expected"]["due_cents"], 0)
        self.assertEqual(mismatch["observed"]["due_cents"], -700)

    def test_bounded_verification_runs(self):
        status, report = self.command("verify")
        self.assertEqual(status, 0)
        self.assertEqual(report["status"], "passed")
        self.assertGreater(report["bounded_calculations"], 0)
        self.assertGreater(report["rejected_invalid_inputs"], 0)
        self.assertEqual(report["replay_checks"], 2)

    def test_hand_calculated_boundaries_and_multiple_lines(self):
        cases = (
            ((), 50, lab.Calculation(0, 0, 0, 50)),
            (((2, 700), (1, 1000)), 500, lab.Calculation(2400, 500, 1900, 0)),
            (((1, 500),), 1200, lab.Calculation(500, 500, 0, 700)),
            (((3, 800),), 2400, lab.Calculation(2400, 2400, 0, 0)),
        )
        for calculate in (lab.reference_invoice, lab.candidate_invoice):
            for lines, credit, expected in cases:
                with self.subTest(calculator=calculate.__name__, lines=lines, credit=credit):
                    self.assertEqual(calculate(lines, credit), expected)

    def test_replay_does_not_mutate_or_retain_state_between_runs(self):
        scenario = lab.load_scenario()
        original = deepcopy(scenario)
        self.assertEqual(lab.replay(scenario), lab.replay(scenario))
        self.assertEqual(scenario, original)

    def test_scenario_rejects_unknown_missing_and_mismatched_fields(self):
        edits = (
            lambda s: s.update(extra=True),
            lambda s: s["invoice"].pop("id"),
            lambda s: s["invoice"].update(amount_cents=True),
            lambda s: s["events"][0].update(invoice_id="another-invoice"),
            lambda s: s["events"][0].update(amount_cents=1200),
            lambda s: s["events"][0].update(amount_cents=2400.0),
            lambda s: s["events"][0].update(type="refund"),
            lambda s: s["events"][0].update(id=""),
            lambda s: s["events"][0].update(extra="ignored?"),
            lambda s: s["expected"].update(applied_events=False),
        )
        for index, edit in enumerate(edits):
            with self.subTest(edit=index):
                scenario = lab.load_scenario()
                edit(scenario)
                with self.assertRaises(lab.ContractError):
                    lab.replay(scenario)

    def test_calculation_rejects_bool_fractional_and_negative_inputs(self):
        for lines, credit in ((((True, 100),), 0), (((1, False),), 0),
                              (((1, 100),), True), (((1, 1.5),), 0),
                              (((-1, 100),), 0), (((1, 100),), -5)):
            with self.subTest(lines=lines, credit=credit):
                with self.assertRaises(lab.ContractError):
                    lab.reference_invoice(lines, credit)


if __name__ == "__main__":
    unittest.main()
