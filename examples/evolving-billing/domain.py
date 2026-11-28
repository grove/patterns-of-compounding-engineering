#!/usr/bin/env python3
"""Reuse the recovery runner under a fictional business-payment identity rule."""

import argparse
import json
from pathlib import Path
import sqlite3
import sys

from replay import Store, Step, amounts, run_steps


KEYS = {"event": "id", "invoice": "invoice_id", "payment": "payment_id"}
FIXTURE = Path(__file__).with_name("domain-cases.json")


def domain_cases():
    """Construct recovery steps from expectations stated in the domain fixture."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    same = fixture["same_payment"]
    first, repeated = same["events"]
    paid, empty = same["expected"], fixture["empty"]
    installments = fixture["installments"]
    deliver, retry = Step("deliver", paid, first), Step("deliver", paid, repeated)
    return {
        "same-payment": (deliver, retry),
        "installments": (
            Step("deliver", installments["expected_after_first"], installments["events"][0]),
            Step("deliver", installments["expected"], installments["events"][1]),
        ),
        "restart": (deliver, Step("restart", paid), retry),
        "before-commit": (Step("deliver", empty, first, "after_record"), retry),
        "after-commit": (Step("deliver", paid, first, "after_commit"), retry),
    }


class KeyedLedger(Store):
    """Adapt identity while keeping the earlier ledger and transaction behavior."""

    def __init__(self, path, identity):
        self.identity = KEYS[identity]
        super().__init__(path, "ledger")

    def record(self, event):
        value = event.get(self.identity)
        if not isinstance(value, str) or not value:
            raise ValueError(f"missing {self.identity}; do not guess payment identity")
        # The inherited receipt column is a deduplication key. In a real migration,
        # changing its meaning also requires an explicit existing-data strategy.
        return super().record(dict(event, id=value))


def verify(identity="payment"):
    return [run_steps(name, steps, identity, KeyedLedger)
            for name, steps in domain_cases().items()]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", choices=KEYS, default="payment")
    args = parser.parse_args(argv)
    try:
        reports = verify(args.identity)
        print(f"Synthetic settled-payment contract / {args.identity} identity")
        for report in reports:
            print(f"{'PASS' if report['matches'] else 'FAIL'} {report['case']}")
            for row in report["observations"]:
                if not row["matches"]:
                    print(f"  step {row['step']}: observed {amounts(row['observed'])}; "
                          f"expected {amounts(row['expected'])}")
        print("'applied' counts accepted payment records in this exercise.")
        print("Scope: one provider and invoice, consistent amounts, sequential deliveries.")
        print("No existing data was migrated; no customer or provider evidence is claimed.")
        return 0 if all(report["matches"] for report in reports) else 1
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Input or local database error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
