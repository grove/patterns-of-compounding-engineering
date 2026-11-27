# Differential verification

*Run the old and new implementations on the same inputs, then sort out every disagreement.*

You want to replace an aging invoice calculator. Nobody loves the old code, yet it encodes years of billing edge cases that nobody can recite from memory. Your rewrite passes every test the team thought to write, which still leaves an uncomfortable gap: what did those tests forget?

Run both implementations side by side on the same inputs and inspect every disagreement before cutting over. Some mismatches will be bugs in your rewrite. Others will be old quirks nobody wanted to keep. Either way, you find them before customers do.

This is a well-worn technique. [GitHub's Scientist](https://github.com/github/scientist) runs a control and a candidate, logs mismatches, and returns the control's result. [SQLite's test suite](https://sqlite.org/testing.html) compares query outputs across different database engines. In both cases, agreement alone does not prove correctness, because two implementations can share the same bug.

## Pick a clean boundary first

Start with a calculation, query, or transform where you can capture every input and inspect the output directly. In our billing service, that boundary takes line items plus requested credit and returns the invoice breakdown, leaving email delivery and card charges outside it.

Capture *all* inputs the code depends on. If the calculator reads today's date, a feature flag, account history, or a price table, pass those in explicitly or freeze them in the snapshot. Otherwise the two implementations are answering different questions.

Never hand both runs the same mutable object. If the old code sorts or normalizes a list in place, the candidate sees already-mutated input; pass immutable values or deep copies. For database reads, compare against a fixed snapshot or recorded dataset instead of running two live queries that can straddle a concurrent write.

If you cannot isolate side effects completely, start offline. A `dry_run` flag is only as reliable as every branch that remembers to check it. Make it structurally hard for the candidate to send email, charge a card, or write to a live table.

## Where side-by-side comparison gets messy

Pure request/response calculations are the easy case. Stateful, asynchronous, and long-running workflows (a dunning state machine, a multi-step checkout, or a background billing pipeline) do not fit a single function call cleanly: two implementations may issue different intermediate writes, settle at different times, or interact with retries differently.

You can still compare them, just at a coarser seam. Replay a recorded event stream into two isolated copies of the database and compare the resulting ledger state at explicit checkpoints (after all events up to sequence N are processed, never after an arbitrary sleep). Where intermediate side effects cannot be cleanly isolated, do not force live shadow execution onto a stateful workflow; combine offline state-transition replays with [executable invariants](./executable-invariants.md) and tight production telemetry from [incident to instrument](./incident-to-instrument.md) during a staged rollout.

## Decide what counts as equal

Compare business outputs rather than object identities or incidental metadata. For an invoice, compare subtotal, applied credit, unused credit, amount due, and currency (if you support more than one). A freshly generated trace ID should not show up as a billing discrepancy.

Be picky about output normalization. Sorting an unordered set makes sense; sorting a ranked search list hides real regressions. Stripping incidental timestamps is fine, whereas slapping a loose numeric tolerance on money to quiet noisy diffs hides rounding bugs. Settle the rounding rules first.

Compare errors as well as normal returns. A candidate that rejects malformed input the old code quietly accepted might be an intentional improvement, or it might break a legacy caller. Track error mismatches separately from value mismatches so you actually make a call on them.

You can run a small local version in the [billing lab](../examples/README.md):

```sh
python3 examples/billing_lab.py compare --candidate correct
python3 examples/billing_lab.py compare --candidate buggy
```

The buggy candidate lets credit exceed the subtotal and prints the failing inputs alongside both outputs before exiting 1. Both runs stay local on synthetic data with no external effects, so a green run speaks only for that corpus.

## Build a corpus full of awkward cases

Start with a handful of cases you can work out by hand: normal credit, zero credit, exact credit, excess credit. Fold in your [persistent reproducers](./persistent-reproducer.md) from past incidents, and use [scenario builders](./scenario-builders.md) to vary combinations without copy-pasting setup.

Once the synthetic cases pass, sampled production inputs often uncover combinations nobody imagined. Decide which fields you need, strip sensitive customer data, and keep the sample small enough to inspect. A curated, reviewed corpus usually answers your migration question faster and more safely than a permanent traffic archive.

Check coverage by category, not just raw count. Ten thousand ordinary monthly invoices will not tell you whether an annual contract with a mid-cycle upgrade works. Note missing classes explicitly, since rare cases usually need deliberate construction or a longer capture window. Watch for policy drift too: running last year's invoices through this year's price table surfaces diffs caused by changed rules rather than bugs.

## Classify every mismatch, and do not let legacy win by default

Your diff report should point straight to the input case, show which fields disagreed, and make both runs easy to replay. "99.8% match" sounds reassuring right up until the missing 0.2% involves money or authorization.

Sort each mismatch into one of four buckets: a bug in the candidate, an intentional fix, a flaw in the comparator, or still under investigation.

Teams often get hooked on chasing 100% parity and end up carefully reproducing old bugs nobody wanted. Whenever a mismatch looks like an intentional fix, check it against your [executable invariants](./executable-invariants.md) and confirm it with the policy owner, then lock the new behavior into a dedicated test and plan the migration impact openly.

Set your cutover bar before scaling up: every known input class represented, zero unexplained monetary diffs, and an explicit call on every intentional change.

## Careful with production shadow traffic

Running the candidate alongside the old path on live traffic ("shadow execution") adds load and can shift latency. Measure the overhead, cap the sample rate, put it behind a kill switch, and isolate candidate exceptions so a failing experiment never breaks the live response.

Scientist explicitly warns that experiments must be read-only and that it does not guard requests against slow candidate timeouts. Check caches, database load, and outbound HTTP calls too, because even doubling read traffic can hurt customers at peak load. Skip trusting candidate latency measured right after the old code warmed the cache; benchmark performance separately if speed is part of the rewrite's goal.

## Tear down the dual run when you are done

Once you cut over and clear your observation window, delete the dual-execution plumbing, temporary flags, and old implementation. Keeping two calculators alive "just in case" eats the savings the rewrite was supposed to buy.

If you expect more pricing changes later, keep the curated corpus and a thin comparison adapter; otherwise archive it. If the comparator spends most of its time flagging harmless noise, tighten what it compares before trusting its green lights.

## What comes after the diff hits zero

Differential verification is where earlier verification work pays off at once: [persistent reproducers](./persistent-reproducer.md), [scenario builders](./scenario-builders.md), and [executable invariants](./executable-invariants.md) give you the corpus and the independent rules needed to judge disagreements.

What it makes practical is replacing old, poorly understood code without betting the business on guesswork. Once cutover holds, pair it with a [subtraction investigation](./subtraction-investigation.md) to delete the old path cleanly, and check whether the comparator itself is worth keeping in an [investment retrospective](./investment-retrospective.md).
