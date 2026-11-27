# Persistent reproducer

*Keep the conditions that triggered a hard bug, not just the fix.*

A subscription service occasionally applies the same payment twice. Somebody spends an afternoon piecing together the sequence: the payment provider sent a webhook, the handler updated the balance, the HTTP response dropped on the wire, and the provider retried. The actual fix is five lines of code after four hours of detective work.

If the pull request ships only those five lines, the next person who edits the handler inherits the conclusion with no way to test it. A paragraph in a postmortem helps until six months later, when someone refactors the webhook path and has to reconstruct the failure conditions from memory. While the details are still in your head, save a runnable version of the failure.

Duplicate webhook delivery is a routine integration hazard ([Stripe documents both duplicate and out-of-order event delivery](https://docs.stripe.com/webhooks#event-delivery-behaviors)). A reproducer puts your own handler through those conditions with its assumptions visible in code.

## What goes into a small reproducer

Pack four things together: the starting state, the event sequence that triggers the bug, the expected outcome, and one command to run it. Add two lines of comment explaining *why* that outcome is right. Without the rationale, a failing test six months later looks like a stale assertion someone can casually update to make CI pass.

In the billing example, you start with an unpaid 2,400-unit invoice and deliver the same `evt_001` payment event twice. Then you check both the paid total and the count of applied events. Checking only HTTP 200 responses lets the test stay green while the customer's balance doubles.

You can run a small version in the [billing lab](../examples/README.md) from the repository root:

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
```

The buggy run records 4,800 as paid across two applied events and exits 1. The fixed run keeps the exact same input and expectation, records 2,400 across one applied event, and exits 0. Holding the scenario still while swapping only the implementation is the habit you want in real bug fixes too.

Be explicit about what the reproducer does not test. This lab runs sequentially in memory; it says nothing about two concurrent workers racing on the same webhook, a process crashing right after commit, or a lost database acknowledgement.

## Reproduce first, trim second

Start with whatever makes the bug fail, even if it is an ugly script or a slow integration test. Designing an elegant fixture before you understand the failure just drags out the investigation.

Once it fails reliably, strip it down. Drop accounts, fields, and intermediate steps one at a time, rerunning against the broken code after each cut, and stop before the next cut obscures why the bug happened. A reproducer that only repeats a surface symptom (like a canned error code) without recreating the mechanism misses the bug when it comes back in slightly different clothes.

Watch the reproducer fail on the unfixed code before merging. Regression tests written *after* a fix pass all too often without ever exercising the broken branch. If checking out the old commit is painful, re-introduce the bug locally and confirm the assertion catches it. Make the failure message name the domain problem ("payment applied twice") instead of burying the reader in a fixture setup traceback.

## Pin down what drifts

Give the reproducer its own isolated state. Swap live payment APIs for a local stub that records attempted calls, and replace production payloads with synthetic IDs and amounts that preserve the structural relationships (like the repeated `evt_001`). Copying raw production JSON drags in customer data and fifty unrelated fields.

Pin the clock whenever deadlines or billing periods matter, timezone included. Pin random seeds when randomness is involved, keeping in mind that a seed will not make an uncontrolled thread schedule deterministic.

For a race condition, put a controllable barrier at the contested step so both workers meet there on purpose; a `time.sleep(0.5)` turns the reproducer into a flake that depends on CI load. For a crash mid-flight, capture the durable state before and after the interruption and replay the retry explicitly. Add that plumbing only when the bug actually needs it.

[Hypothesis's guide to flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html) covers the usual culprits: leftover state, ambient clocks, and unseeded randomness. You want the reproducer to give the same answer tomorrow, and after twenty other tests ran ahead of it.

## Put it where CI will actually run it

Most reproducers belong right inside the existing test suite. Name the test after the failure mode, link the incident or issue number, and leave the explanation next to the assertion. Almost nobody remembers to run a separate `reproducers/` folder sitting off to the side.

Some failures genuinely need a slower environment or multiple processes. Keep those near the code behind one documented command and run them on a sensible trigger: changes to that component, a nightly job, or a release check. A twenty-minute multi-process replay should not block a README typo fix.

When a property-based test uncovers an ugly failure, pin that case as an explicit regression test. [Hypothesis recommends `@example`](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html), since its local example database can go stale across versions or test edits.

## When *not* to force a local reproducer

Not every production failure is worth cramming into a deterministic test. Emergent outages—database lock storms, tail-latency cascades, connection-pool exhaustion under real traffic, or a payment provider's intermittent 502s—often resist faithful local reproduction. Spending three days mocking a whole cluster to simulate a timing window usually yields a brittle test that breaks on unrelated refactors and still misses the next trigger.

When local reproduction stops being economical, switch to [incident to instrument](./incident-to-instrument.md): add the structured fields, timings, or counters you wished you had during the outage so the next occurrence shows up in minutes.

Even for deterministic bugs, skip a heavy harness when a five-line unit test covers a plain typo. Every saved case carries upkeep as schemas and product rules move. Assign an owner (usually the team that owns the behavior), update the rationale when a rule intentionally changes, and delete redundant cases once a broader invariant covers the same ground.

Watch out for replay scripts that only work on the author's laptop. Have someone who was not involved in the incident run the command and explain what the assertion protects; their questions show you what is still implicit.

## What a reproducer opens up

Right away, a saved reproducer stops the next engineer from burning another afternoon reconstructing the same bug. The bigger payoff comes when later changes stop being guesswork: you can refactor the webhook handler or swap a storage layer knowing the ugliest past cases are runnable on demand.

Once two or three reproducers repeat the same setup pain, pull the shared parts into [scenario builders](./scenario-builders.md). When the same *class* of bug keeps coming back, turn the rule into an [executable invariant](./executable-invariants.md). If someone needs to run the replay outside the test runner, wrap it in a [capability command](./capability-command.md). Later, when you replace a legacy module, those saved reproducers become the starting corpus for [differential verification](./differential-verification.md). Let real pain pull you into the next piece rather than building all of it upfront.
