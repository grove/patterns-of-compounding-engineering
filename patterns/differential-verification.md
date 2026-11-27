# Differential verification

*Run the old and new implementations on the same inputs, then sort out every disagreement.*

You want to replace an aging invoice calculator. Nobody loves the old code, yet it encodes years of weird exceptions that nobody can list from memory. Your rewrite passes every test the team knows how to write, which still leaves the nagging question: what did those tests forget?

Run both implementations side by side on the same inputs and inspect every difference before cutting over. You turn the legacy system into an evidence source without pretending it's infallible; some disagreements will turn out to be old bugs you actually want to fix.

This is a well-worn technique. [GitHub's Scientist](https://github.com/github/scientist) runs a control and a candidate, logs mismatches, and always returns the control's result. [SQLite's test suite](https://sqlite.org/testing.html) compares query outputs across different database engines. In both cases, agreement still doesn't prove correctness. Two implementations can happily share the exact same bug.

## Pick a clean boundary first

Start with a calculation, query, or transform where you can capture all inputs and inspect the output directly. In our billing service, that boundary takes line items plus requested credit and returns the invoice breakdown; sending emails and charging cards stay outside it.

Capture *every* input the code depends on. If the calculator reads today's date, a feature flag, account history, or a price table, pass those in explicitly or freeze them in the snapshot. Otherwise the old and new implementations aren't answering the same question.

Never hand both runs the same mutable object. If the old code sorts or normalizes a list in place, the candidate sees already-mutated input. Pass immutable values or deep copies. For database reads, compare against a fixed snapshot or recorded dataset rather than running two live queries that might straddle a concurrent write.

If you can't completely isolate side effects, start offline. A `dry_run` boolean is only as trustworthy as every branch that remembers to check it. Make it structurally hard for the candidate to send email, charge a card, or write to a real table.

## Decide what counts as equal

Compare business outputs, not object identities or incidental metadata. For an invoice, compare subtotal, applied credit, unused credit, amount due, and currency (if you support more than one). A freshly generated trace ID shouldn't show up as a billing discrepancy.

Be careful when normalizing outputs. Sorting an unordered set makes sense; sorting a ranked search list hides real regressions. Stripping timestamps is fine when they're incidental. Never slap a loose numeric tolerance on money just to quiet noisy diffs; settle the rounding rules first.

Compare errors as well as normal returns. A candidate that rejects malformed input the old code quietly accepted might be an intentional improvement, or it might break a legacy caller. Either way, keep error mismatches separate from value mismatches.

You can see a small local version in the [billing lab](../examples/README.md):

```sh
python3 examples/billing_lab.py compare --candidate correct
python3 examples/billing_lab.py compare --candidate buggy
```

The buggy candidate lets credit exceed the subtotal and prints the failing inputs alongside both outputs before exiting 1. Both runs stay local on synthetic data with no external effects, so a green run only speaks for that corpus.

## Build a corpus full of awkward cases

Start with a handful of cases you can reason through by hand: normal credit, zero credit, exact credit, excess credit. Fold in your [persistent reproducers](./persistent-reproducer.md) from past incidents, and use [scenario builders](./scenario-builders.md) to vary combinations without copy-pasting setup.

Once the synthetic cases pass, sampled production inputs often uncover combinations nobody imagined. Decide which fields you need, strip sensitive customer data, and keep the sample small enough to inspect. A curated, reviewed set usually answers your migration question faster and more safely than a permanent traffic archive.

Check coverage by *category*, not volume alone. Ten thousand ordinary monthly invoices won't tell you whether an annual contract with a mid-cycle upgrade works. Note the missing classes explicitly, because rare cases usually need deliberate construction or a longer capture window. Also watch for policy drift: running last year's invoices through this year's price table will surface diffs that reflect changed rules rather than bugs.

## Classify every mismatch, and don't let legacy win by default

Your diff report should point straight to the input case, highlight which fields disagreed, and make both runs easy to replay. "99.8% match" is a terrible decision metric when the missing 0.2% involves money or authorization.

Sort each mismatch into one of four buckets: a bug in the candidate, an intentional fix, a flaw in the comparator, or still under investigation.

Here is the real hazard with differential verification: **behavioral compatibility can quietly turn into a veto against fixing old mistakes.** Teams get hooked on chasing 100% parity and end up reproducing legacy quirks nobody wanted. Whenever a mismatch looks like an intentional correction, check it against your [executable invariants](./executable-invariants.md) and confirm it with the policy owner, then lock in the new expected behavior with a dedicated test and plan the migration impact openly.

Set your cutover bar before scaling up: every known input class represented, zero unexplained monetary diffs, and an explicit call on every intentional change.

## Be careful with production shadow traffic

Running the candidate alongside the old path on live traffic ("shadow execution") adds load and can shift latency. Measure the overhead, cap the sample rate, put it behind a kill switch, and isolate candidate exceptions so a failing experiment never breaks the live response.

Scientist explicitly warns that experiments must be read-only and that it doesn't guard requests against slow candidate timeouts. Double-check caches, database load, and outbound HTTP calls; even doubling read traffic can hurt customers at peak load. And don't trust candidate latency measured right after the old code warmed the cache. Benchmark performance separately if speed is part of the rewrite's goal.

## Tear down the dual run when you're done

Once you've cut over and survived your observation window, delete the dual-execution plumbing, temporary flags, and old implementation. Keeping two implementations alive "just in case" quietly eats the savings the rewrite was supposed to deliver.

If you expect more pricing changes later, keep the curated corpus and a thin comparison adapter. Otherwise, archive it. The evidence that this paid off is concrete: a bug caught before cutover, an undocumented legacy exception brought into the light, or a future rewrite checked against the same corpus. If the comparator spends most of its time flagging harmless noise, tighten what it compares before trusting its green lights.
