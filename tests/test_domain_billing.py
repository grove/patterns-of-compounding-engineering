"""Check the changed contract and the tempting fixes that violate it."""

import importlib.util
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "examples" / "evolving-billing"
sys.path.insert(0, str(DIRECTORY))
SPEC = importlib.util.spec_from_file_location("domain_billing", DIRECTORY / "domain.py")
lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab)


class DomainBillingTests(unittest.TestCase):
    def test_event_identity_double_counts_one_payment(self):
        reports = {row["case"]: row for row in lab.verify("event")}
        self.assertFalse(reports["same-payment"]["matches"])
        self.assertEqual(reports["same-payment"]["observations"][-1]["observed"],
                         {"paid_cents": 4800, "applied_events": 2})
        self.assertTrue(reports["installments"]["matches"])

    def test_invoice_identity_discards_a_legitimate_installment(self):
        reports = {row["case"]: row for row in lab.verify("invoice")}
        self.assertTrue(reports["same-payment"]["matches"])
        self.assertFalse(reports["installments"]["matches"])
        self.assertEqual(reports["installments"]["observations"][-1]["observed"],
                         {"paid_cents": 1200, "applied_events": 1})

    def test_payment_identity_preserves_both_cases_across_recovery(self):
        for report in lab.verify("payment"):
            with self.subTest(case=report["case"]):
                self.assertTrue(report["matches"], report)
        reports = {row["case"]: row for row in lab.verify("payment")}
        self.assertEqual(reports["before-commit"]["observations"][0]["observed"],
                         {"paid_cents": 0, "applied_events": 0})
        self.assertEqual(reports["after-commit"]["observations"][0]["observed"],
                         {"paid_cents": 2400, "applied_events": 1})

    def test_missing_identity_is_rejected_without_writing_a_payment(self):
        with TemporaryDirectory() as directory:
            store = lab.KeyedLedger(Path(directory) / "payments.sqlite", "payment")
            try:
                with self.assertRaisesRegex(ValueError, "missing payment_id"):
                    store.deliver({"id": "evt_001", "amount_cents": 2400})
                self.assertEqual(store.snapshot(), {"paid_cents": 0, "applied_events": 0})
            finally:
                store.close()

    def test_each_run_starts_empty_and_leaves_fixture_unchanged(self):
        before = lab.FIXTURE.read_bytes()
        self.assertEqual(lab.verify("payment"), lab.verify("payment"))
        self.assertEqual(before, lab.FIXTURE.read_bytes())

    def test_documented_commands_report_meaningful_exit_statuses(self):
        for identity, status in (("event", 1), ("invoice", 1), ("payment", 0), ("unknown", 2)):
            with self.subTest(identity=identity):
                result = subprocess.run(
                    [sys.executable, str(DIRECTORY / "domain.py"), "--identity", identity],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, status, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
