#!/usr/bin/env python3
"""Follow one synthetic payment through retries, restarts and storage changes."""

from copy import deepcopy
from dataclasses import dataclass
import argparse
from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory

# The first investment is already here: retain its input and reviewed expectation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from billing_lab import load_scenario


IMPLEMENTATIONS = ("memory", "split", "atomic", "ledger")
CORE_CASES = ("duplicate", "restart", "after-record", "after-effect", "after-commit")


class Interrupted(Exception):
    """A deterministic interruption at a named point, not a process/power crash."""


@dataclass(frozen=True)
class Step:
    action: str
    expected: dict
    event: dict | None = None
    interrupt: str | None = None


def cases():
    """Extend the original fixture; never derive expectations from a handler."""
    original = load_scenario()
    first, repeated = original["events"]
    paid = original["expected"]
    unpaid = {"paid_cents": 0, "applied_events": 0}
    deliver = Step("deliver", paid, first)
    retry = Step("deliver", paid, repeated)
    alternate = dict(first, id="evt_002")
    return {
        "duplicate": (deliver, retry),
        "restart": (deliver, Step("restart", paid), retry),
        "after-record": (Step("deliver", unpaid, first, "after_record"), retry),
        "after-effect": (Step("deliver", unpaid, first, "after_effect"), retry),
        "after-commit": (Step("deliver", paid, first, "after_commit"), retry),
        # A deliberately stronger requirement, outside the event-ID contract:
        # suppose the provider confirms both IDs describe one business payment.
        "identity-gap": (deliver, Step("deliver", paid, alternate)),
    }


class Store:
    """Four small designs sharing only a delivery interface and observation shape."""

    def __init__(self, path, implementation):
        if implementation not in IMPLEMENTATIONS:
            raise ValueError("unknown implementation")
        self.implementation = implementation
        self.seen = set()
        self.db = sqlite3.connect(path)
        with self.db:
            if implementation != "memory":
                self.db.execute("CREATE TABLE IF NOT EXISTS receipts "
                                "(event_id TEXT PRIMARY KEY, amount_cents INTEGER NOT NULL)")
            if implementation != "ledger":
                self.db.execute("CREATE TABLE IF NOT EXISTS balance "
                                "(id INTEGER PRIMARY KEY CHECK(id = 1), "
                                "paid_cents INTEGER NOT NULL, applied_events INTEGER NOT NULL)")
                self.db.execute("INSERT OR IGNORE INTO balance VALUES (1, 0, 0)")

    def close(self):
        self.db.close()

    def record(self, event):
        return self.db.execute(
            "INSERT OR IGNORE INTO receipts VALUES (?, ?)",
            (event["id"], event["amount_cents"]),
        ).rowcount == 1

    def apply(self, event):
        self.db.execute("UPDATE balance SET paid_cents = paid_cents + ?, "
                        "applied_events = applied_events + 1 WHERE id = 1",
                        (event["amount_cents"],))

    def deliver(self, event, interrupt=None):
        def stop_at(point):
            if interrupt == point:
                raise Interrupted(point)

        if self.implementation == "memory":
            if event["id"] in self.seen:
                return
            self.seen.add(event["id"])
            stop_at("after_record")
            with self.db:
                self.apply(event)
                stop_at("after_effect")
        elif self.implementation == "split":
            # Seeded defect: committing these writes separately loses atomicity.
            with self.db:
                fresh = self.record(event)
            if not fresh:
                return
            stop_at("after_record")
            with self.db:
                self.apply(event)
            stop_at("after_effect")
        else:
            with self.db:
                if not self.record(event):
                    return
                stop_at("after_record")
                if self.implementation == "atomic":
                    self.apply(event)
                # The ledger derives the balance: there is no second write.
                stop_at("after_effect")
        stop_at("after_commit")

    def snapshot(self):
        if self.implementation == "ledger":
            paid, applied = self.db.execute(
                "SELECT COALESCE(SUM(amount_cents), 0), COUNT(*) FROM receipts"
            ).fetchone()
        else:
            paid, applied = self.db.execute(
                "SELECT paid_cents, applied_events FROM balance WHERE id = 1"
            ).fetchone()
        return {"paid_cents": paid, "applied_events": applied}


def run_case(name, implementation="atomic"):
    steps = cases()[name]
    observations = []
    # Each run starts empty and removes its own database when finished.
    with TemporaryDirectory(prefix="evolving-billing-") as directory:
        database = Path(directory) / "payments.sqlite"
        store = Store(database, implementation)
        try:
            for index, step in enumerate(steps, 1):
                label = "restart"
                interruption = None
                if step.action == "restart":
                    store.close()
                    store = Store(database, implementation)
                else:
                    label = f"deliver {step.event['id']}"
                    try:
                        store.deliver(step.event, step.interrupt)
                    except Interrupted as error:
                        interruption = str(error)
                        label += f"; interrupted {error}"
                        store.close()
                        store = Store(database, implementation)
                observed = store.snapshot()
                observations.append({"step": index, "action": label,
                                     "expected": deepcopy(step.expected),
                                     "observed": observed,
                                     "expected_interruption": step.interrupt,
                                     "observed_interruption": interruption,
                                     "matches": observed == step.expected
                                     and interruption == step.interrupt})
        finally:
            store.close()
    return {"case": name, "implementation": implementation,
            "observations": observations,
            "matches": all(item["matches"] for item in observations)}


def verify(implementation="atomic"):
    return [run_case(name, implementation) for name in CORE_CASES]


def compare(candidate="ledger", reference="atomic"):
    comparisons = []
    for name in CORE_CASES:
        old, new = run_case(name, reference), run_case(name, candidate)
        agrees = [item["observed"] for item in old["observations"]] == [
            item["observed"] for item in new["observations"]]
        comparisons.append({"case": name, "agrees": agrees,
                            "reference_passes": old["matches"],
                            "candidate_passes": new["matches"],
                            "matches": agrees and old["matches"] and new["matches"]})
    return comparisons


def amounts(state):
    return f"paid {state['paid_cents']}; applied {state['applied_events']}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="inspect each checkpoint of one case")
    run.add_argument("--case", choices=(*CORE_CASES, "identity-gap"), default="duplicate")
    run.add_argument("--implementation", choices=IMPLEMENTATIONS, default="atomic")
    check = commands.add_parser("verify", help="check the five event-ID cases")
    check.add_argument("--implementation", choices=IMPLEMENTATIONS, default="atomic")
    comparison = commands.add_parser("compare", help="compare with the atomic reference")
    comparison.add_argument("--candidate", choices=IMPLEMENTATIONS, default="ledger")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            report = run_case(args.case, args.implementation)
            print(f"{args.case} / {args.implementation}")
            for row in report["observations"]:
                verdict = "PASS" if row["matches"] else "FAIL"
                print(f"{verdict} {row['step']}. {row['action']}: {amounts(row['observed'])}")
                if not row["matches"]:
                    print(f"        expected {amounts(row['expected'])}")
                    if row["observed_interruption"] != row["expected_interruption"]:
                        print(f"        expected interruption {row['expected_interruption']}")
            if args.case == "identity-gap":
                print("This case assumes two event IDs describe one business payment.")
                print("Event-ID deduplication cannot establish payment identity.")
            return 0 if report["matches"] else 1
        if args.command == "verify":
            reports = verify(args.implementation)
            for report in reports:
                print(f"{'PASS' if report['matches'] else 'FAIL'} {report['case']}")
            print("Scope: five sequential event-ID cases; identity-gap is a separate requirement.")
        else:
            reports = compare(args.candidate)
            for report in reports:
                verdict = "PASS" if report["matches"] else "FAIL"
                print(f"{verdict} {report['case']}: agree={report['agrees']}, "
                      f"reference meets expectation={report['reference_passes']}, "
                      f"candidate meets expectation={report['candidate_passes']}")
            print("Compared fresh databases at every checkpoint; no existing data was migrated.")
        return 0 if all(report["matches"] for report in reports) else 1
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Input or local database error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
