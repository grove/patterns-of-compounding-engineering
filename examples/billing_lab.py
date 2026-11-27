#!/usr/bin/env python3
"""Small, local demonstrations of four verification patterns. Python 3.10+."""

import argparse
from dataclasses import asdict, dataclass
from itertools import product
import json
from pathlib import Path
import sys

DEFAULT_SCENARIO = Path(__file__).parent / "scenarios" / "duplicate-payment.json"


class ContractError(ValueError):
    """Input does not satisfy this deliberately narrow example contract."""


class CheckFailure(Exception):
    """An observation violates an independently stated expectation."""


def integer(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        raise ContractError(f"{label} must be an integer >= {minimum}; got {value!r}")
    return value


def fields(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ContractError(f"{label} must contain exactly: {', '.join(expected)}")


def identifier(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a nonempty string")


def validate_scenario(scenario):
    fields(scenario, ("name", "invoice", "events", "expected"), "scenario")
    identifier(scenario["name"], "scenario.name")
    invoice = scenario["invoice"]
    fields(invoice, ("id", "amount_cents"), "invoice")
    identifier(invoice["id"], "invoice.id")
    integer(invoice["amount_cents"], "invoice.amount_cents", minimum=1)
    if not isinstance(scenario["events"], list) or not scenario["events"]:
        raise ContractError("events must be a nonempty list")
    seen = {}
    for index, event in enumerate(scenario["events"]):
        label = f"events[{index}]"
        fields(event, ("id", "type", "invoice_id", "amount_cents"), label)
        identifier(event["id"], f"{label}.id")
        if event["type"] != "payment_succeeded":
            raise ContractError(f"{label}.type must be payment_succeeded")
        if event["invoice_id"] != invoice["id"]:
            raise ContractError(f"{label}.invoice_id does not match the invoice")
        integer(event["amount_cents"], f"{label}.amount_cents", minimum=1)
        if event["amount_cents"] != invoice["amount_cents"]:
            raise ContractError(f"{label}.amount_cents must settle the full invoice")
        if event["id"] in seen and event != seen[event["id"]]:
            raise ContractError(f"{label}.id was reused with a different payload")
        seen[event["id"]] = event
    fields(scenario["expected"], ("paid_cents", "applied_events"), "expected")
    for name, value in scenario["expected"].items():
        integer(value, f"expected.{name}")


def load_scenario(path=DEFAULT_SCENARIO):
    scenario = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_scenario(scenario)
    return scenario


def replay(scenario, implementation="fixed"):
    """Sequential in-memory illustration; no durable/concurrent guarantee."""
    validate_scenario(scenario)
    if implementation not in ("fixed", "buggy"):
        raise ContractError("unknown replay implementation")
    seen, paid, applied = set(), 0, 0
    for event in scenario["events"]:
        if implementation == "fixed" and event["id"] in seen:
            continue
        paid += event["amount_cents"]
        applied += 1
        seen.add(event["id"])
    return {"paid_cents": paid, "applied_events": applied}


@dataclass(frozen=True)
class Calculation:
    subtotal_cents: int
    applied_credit_cents: int
    due_cents: int
    unused_credit_cents: int


def calculation_inputs(lines, available_credit):
    integer(available_credit, "available_credit")
    if not isinstance(lines, (list, tuple)):
        raise ContractError("lines must be a list or tuple")
    normalized = []
    for index, line in enumerate(lines):
        if not isinstance(line, (list, tuple)) or len(line) != 2:
            raise ContractError(f"lines[{index}] must be (quantity, unit_price_cents)")
        quantity = integer(line[0], f"lines[{index}].quantity")
        price = integer(line[1], f"lines[{index}].unit_price_cents")
        normalized.append((quantity, price))
    return tuple(normalized), available_credit


def reference_invoice(lines, available_credit):
    lines, credit = calculation_inputs(lines, available_credit)
    subtotal = sum(quantity * price for quantity, price in lines)
    applied = min(credit, subtotal)
    return Calculation(subtotal, applied, subtotal - applied, credit - applied)


def candidate_invoice(lines, available_credit, *, buggy=False):
    lines, credit = calculation_inputs(lines, available_credit)
    subtotal = 0
    for quantity, price in lines:
        subtotal += quantity * price
    # The seeded defect forgets that credit applied is bounded by the invoice.
    due = subtotal - credit if buggy else max(0, subtotal - credit)
    applied = subtotal - due
    return Calculation(subtotal, applied, due, credit - applied)


COMPARISON_CASES = (
    ("empty", (), 0),
    ("empty-with-credit", (), 300),
    ("ordinary", ((3, 800),), 0),
    ("partial-credit", ((3, 800),), 900),
    ("exact-credit", ((3, 800),), 2400),
    ("excess-credit", ((1, 500),), 1200),
    ("multiple-lines", ((2, 700), (1, 1000)), 500),
    ("zero-value-lines", ((2, 0), (0, 100)), 500),
    ("large-credit", ((10, 1000000),), 1000000000),
)


def compare(candidate="correct"):
    if candidate not in ("correct", "buggy"):
        raise ContractError("unknown candidate")
    differences = []
    for name, lines, credit in COMPARISON_CASES:
        expected = reference_invoice(lines, credit)
        observed = candidate_invoice(lines, credit, buggy=candidate == "buggy")
        if expected != observed:
            differences.append({
                "case": name, "lines": lines, "available_credit": credit,
                "expected": asdict(expected), "observed": asdict(observed),
            })
    return {"candidate": candidate, "cases": len(COMPARISON_CASES),
            "differences": differences, "matches": not differences}


def require(condition, explanation):
    if not condition:
        raise CheckFailure(explanation)


def verify():
    """Check a bounded, deterministic input set; this is not a proof or fuzzer."""
    atoms = tuple(product((0, 1, 2, 17), (0, 1, 99, 500)))
    line_sets = [()] + [(line,) for line in atoms] + list(product(atoms, repeat=2))
    checks = 0
    calculators = (reference_invoice, candidate_invoice)
    for lines in line_sets:
        subtotal = sum(quantity * price for quantity, price in lines)
        credits = sorted({0, 1, max(0, subtotal - 1), subtotal, subtotal + 1, subtotal + 500})
        for credit in credits:
            for calculate in calculators:
                result = calculate(lines, credit)
                context = f"{calculate.__name__}: lines={lines!r}, credit={credit}"
                require(all(type(value) is int for value in asdict(result).values()), context)
                require(result.subtotal_cents == subtotal, f"subtotal: {context}")
                require(0 <= result.applied_credit_cents <= min(credit, subtotal), context)
                require(result.due_cents >= 0 and result.unused_credit_cents >= 0, context)
                require(result.due_cents + result.applied_credit_cents == subtotal, context)
                require(result.unused_credit_cents + result.applied_credit_cents == credit, context)
                require(calculate(tuple(reversed(lines)), credit) == result, f"order: {context}")
                require(calculate(lines, credit + 1).due_cents <= result.due_cents,
                        f"credit monotonicity: {context}")
                checks += 1
    # Reviewed examples reject a calculator that simply never applies credit.
    for calculate in calculators:
        require(calculate(((2, 500),), 300) == Calculation(1000, 300, 700, 0),
                "partial credit: expected 300 applied and 700 due")
        require(calculate(((2, 500),), 1200) == Calculation(1000, 1000, 0, 200),
                "excess credit: expected 200 unused")
    invalid = (
        (((-1, 100),), 0), (((1, -100),), 0), (((True, 100),), 0),
        (((1, True),), 0), (((1, 1.5),), 0), (((1, 100),), -1),
        (((1, 100),), True), (((1, 100),), "1"), (((1, 100, 5),), 0),
        ("not-lines", 0),
    )
    rejected = 0
    for calculate in calculators:
        for lines, credit in invalid:
            try:
                calculate(lines, credit)
            except ContractError:
                rejected += 1
            else:
                raise CheckFailure(f"accepted invalid input: {lines!r}, {credit!r}")
    scenario = load_scenario()
    require(replay(scenario) == scenario["expected"], "duplicate payment affected the balance")
    require(replay(scenario, "buggy") != scenario["expected"], "reproducer missed seeded defect")
    return {"status": "passed", "bounded_calculations": checks,
            "rejected_invalid_inputs": rejected, "replay_checks": 2}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    replay_parser = commands.add_parser("replay", help="replay a duplicate payment")
    replay_parser.add_argument("--implementation", choices=("fixed", "buggy"), default="fixed")
    replay_parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    commands.add_parser("verify", help="run bounded invariant and boundary checks")
    comparison = commands.add_parser("compare", help="compare two invoice calculators")
    comparison.add_argument("--candidate", choices=("correct", "buggy"), default="correct")
    args = parser.parse_args(argv)
    try:
        if args.command == "replay":
            scenario = load_scenario(args.scenario)
            observed = replay(scenario, args.implementation)
            report = {"scenario": scenario["name"], "implementation": args.implementation,
                      "expected": scenario["expected"], "observed": observed,
                      "matches": observed == scenario["expected"]}
        elif args.command == "compare":
            report = compare(args.candidate)
        else:
            report = verify()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("matches", True) else 1
    except CheckFailure as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1
    except (ContractError, OSError, json.JSONDecodeError) as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
