"""Check the lesson's independent outcomes and deliberately defective designs."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "evolving-billing" / "replay.py"
SPEC = importlib.util.spec_from_file_location("evolving_billing", SCRIPT)
lab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lab
SPEC.loader.exec_module(lab)


class EvolvingBillingTests(unittest.TestCase):
    def test_memory_check_passes_until_restart_loses_the_event_id(self):
        self.assertTrue(lab.run_case("duplicate", "memory")["matches"])
        report = lab.run_case("restart", "memory")
        self.assertFalse(report["matches"])
        self.assertEqual(report["observations"][-1]["observed"],
                         {"paid_cents": 4800, "applied_events": 2})

    def test_split_commit_loses_payment_when_receipt_survives_interruption(self):
        self.assertTrue(lab.run_case("restart", "split")["matches"])
        report = lab.run_case("after-record", "split")
        self.assertFalse(report["matches"])
        self.assertEqual(report["observations"][-1]["observed"],
                         {"paid_cents": 0, "applied_events": 0})

    def test_atomic_and_ledger_recover_at_each_stated_interruption(self):
        for implementation in ("atomic", "ledger"):
            for name in lab.CORE_CASES:
                with self.subTest(implementation=implementation, case=name):
                    report = lab.run_case(name, implementation)
                    self.assertTrue(report["matches"], report)
                    self.assertEqual(report["observations"][-1]["observed"],
                                     {"paid_cents": 2400, "applied_events": 1})
                    if name in ("after-record", "after-effect"):
                        self.assertEqual(report["observations"][0]["observed"],
                                         {"paid_cents": 0, "applied_events": 0})

    def test_committed_payment_survives_lost_acknowledgment(self):
        report = lab.run_case("after-commit", "atomic")
        self.assertTrue(report["matches"])
        self.assertEqual(report["observations"][0]["observed"],
                         {"paid_cents": 2400, "applied_events": 1})

    def test_missing_fault_injection_cannot_pass_as_a_recovery_check(self):
        deliver = lab.Store.deliver
        with patch.object(lab.Store, "deliver", lambda self, event, interrupt=None:
                          deliver(self, event)):
            report = lab.run_case("after-commit", "atomic")
        self.assertFalse(report["matches"])
        self.assertEqual(report["observations"][0]["observed"],
                         {"paid_cents": 2400, "applied_events": 1})

    def test_two_different_event_ids_do_not_prove_two_business_payments(self):
        for implementation in lab.IMPLEMENTATIONS:
            with self.subTest(implementation=implementation):
                report = lab.run_case("identity-gap", implementation)
                self.assertFalse(report["matches"])
                self.assertEqual(report["observations"][-1]["observed"],
                                 {"paid_cents": 4800, "applied_events": 2})

    def test_comparison_requires_independent_expectations_as_well_as_agreement(self):
        self.assertTrue(all(row["matches"] for row in lab.compare()))
        self.assertFalse(all(row["matches"] for row in lab.compare("split")))
        # Two copies of the same defect agree; the retained oracle still rejects it.
        both_wrong = lab.compare("split", "split")
        self.assertTrue(all(row["agrees"] for row in both_wrong))
        self.assertFalse(all(row["matches"] for row in both_wrong))

    def test_ledger_needs_no_stored_balance_or_reference_calculation(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            store = lab.Store(Path(directory) / "ledger.sqlite", "ledger")
            try:
                tables = store.db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                self.assertEqual({row[0] for row in tables}, {"receipts"})
                store.deliver(lab.cases()["duplicate"][0].event)
                self.assertEqual(store.snapshot(), {"paid_cents": 2400, "applied_events": 1})
            finally:
                store.close()

    def test_runs_start_empty_and_do_not_mutate_the_original_fixture(self):
        original = lab.load_scenario()
        first = lab.run_case("restart", "atomic")
        self.assertEqual(first, lab.run_case("restart", "atomic"))
        self.assertEqual(original, lab.load_scenario())

    def test_documented_commands_have_meaningful_exit_statuses(self):
        commands = (
            (("run", "--case", "duplicate", "--implementation", "memory"), 0),
            (("run", "--case", "restart", "--implementation", "memory"), 1),
            (("run", "--case", "after-record", "--implementation", "split"), 1),
            (("verify", "--implementation", "atomic"), 0),
            (("compare",), 0),
            (("compare", "--candidate", "split"), 1),
            (("verify", "--implementation", "ledger"), 0),
            (("run", "--case", "identity-gap", "--implementation", "ledger"), 1),
            (("run", "--case", "unknown"), 2),
            (("verify", "--implementation", "unknown"), 2),
        )
        for command, expected_status in commands:
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(SCRIPT), *command],
                                        cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, expected_status, result.stdout + result.stderr)
                if expected_status != 2:
                    self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
