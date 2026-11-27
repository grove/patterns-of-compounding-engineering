# Billing lab

A small local example for the guide's first four patterns. It contains a retained failure, explicit scenario data, executable guarantees and a comparison between implementations. Python 3.10 or later is enough. It makes no network requests, writes no application data and has no package dependencies.

Run the following commands from the repository root.

## Reproduce a duplicate payment

```sh
python3 examples/billing_lab.py replay
python3 examples/billing_lab.py replay --implementation fixed
python3 examples/billing_lab.py replay --implementation buggy
```

The first two commands are equivalent and exit successfully. The last command **deliberately exits with status 1**. Its JSON report shows expected `paid_cents: 2400` and `applied_events: 1`, but observed `paid_cents: 4800` and `applied_events: 2`.

[The committed scenario](./scenarios/duplicate-payment.json) starts with an unpaid invoice for 2,400 minor units and delivers `evt_001` twice. The expected outcome is part of the reviewed fixture. The runner does not calculate it from the implementation.

To explore another local fixture, copy the JSON, edit it and pass `--scenario path/to/case.json`. Unknown fields, missing fields, the wrong invoice, unsupported event types, partial-payment amounts and invalid numeric types produce an input error and exit status 2. Booleans are rejected even though Python treats them as integers. Repeated event IDs must retain the same payload.

The fixed implementation keeps event IDs in memory. It demonstrates sequential deduplication only. It does not handle concurrent workers, process crashes, durable storage, signatures, refunds or recovery after a partial transaction. Do not use it as a production webhook handler.

## Check the calculation contract

```sh
python3 examples/billing_lab.py verify
```

This command checks both calculators against a bounded, deterministic set of empty, single-line and two-line invoices, with zero, partial, exact and excess credit. It checks conservation of amounts, credit bounds, integer results, ordering independence and the effect of increasing credit. Two worked examples supply expected amounts independently. It also checks invalid inputs and the payment reproducer.

The model uses one currency and whole minor units; field names use `_cents` for readability. Line quantities and prices are nonnegative integers. Credit can reduce the amount due to zero; any remainder stays unused. There is no tax, proration, foreign exchange, rounding or persistence. Passing these checks covers the stated examples and finite input set, not every possible billing rule or input.

## Compare a replacement

```sh
python3 examples/billing_lab.py compare
python3 examples/billing_lab.py compare --candidate correct
python3 examples/billing_lab.py compare --candidate buggy
```

The correct candidate agrees with the reference on the named corpus and exits with status 0. The buggy candidate applies more credit than the invoice can absorb; its report includes negative amounts due. It **deliberately exits with status 1**, preserving the inputs and both results for each mismatch.

The two calculators share input validation. Their arithmetic is expressed differently, but they still share the same policy assumptions. Agreement cannot establish that those assumptions are right. The separately stated examples and invariants provide additional checks.

## Read alongside the example

- [Persistent reproducer](../patterns/persistent-reproducer.md): retain the conditions and expectation of a failure.
- [Scenario builders](../patterns/scenario-builders.md): construct meaningful states without opaque shared fixtures.
- [Executable invariants](../patterns/executable-invariants.md): check the guarantees and their limits.
- [Differential verification](../patterns/differential-verification.md): investigate differences before replacing an implementation.

Run the lab's tests with `python3 -m unittest discover -s tests -p 'test_billing_lab.py' -v`. The tests treat the seeded failures as expected outcomes. They cover CLI defaults and exit codes, fixture validation and manually calculated boundaries.
