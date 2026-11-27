# Persistent reproducer

*Keep the conditions that triggered a hard bug, not just the fix.*

A subscription service occasionally applies the same payment twice. Somebody spends an afternoon piecing together the sequence: the payment provider sent a webhook, the handler updated the balance, the HTTP response dropped on the wire, and the provider retried. Fixing it takes five lines of code after four hours of detective work.

If the pull request ships only those five lines, the next engineer inherits the conclusion with no way to test it. A paragraph in a postmortem helps until six months later, when someone edits the handler and has to reconstruct the setup from memory. While the details are fresh, keep an executable version of the failure.

Duplicate webhook delivery is a real integration hazard ([Stripe documents both duplicate and out-of-order event delivery](https://docs.stripe.com/webhooks#event-delivery-behaviors)). A reproducer puts your own handler through those conditions with its assumptions exposed.

## Keep one small, self-contained case

A useful reproducer packs four things together: the starting state, the event sequence that triggers the bug, the expected outcome, and one command to run it. Add a two-line comment explaining *why* that outcome is right. Without the rationale, a failing test six months later looks like a stale assertion someone can update to turn CI green.

In the billing example, you start with an unpaid 2,400-unit invoice and deliver the same `evt_001` payment event twice. Then you check both the paid total and the count of applied events. Checking only HTTP 200 responses lets the test pass while the customer's balance doubles.

You can run a small version in the [billing lab](../examples/README.md) from the repository root:

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
```

The buggy run records 4,800 as paid across two applied events and exits with status 1. The fixed run keeps the same input and expectation, records 2,400 across one applied event, and exits 0. Holding the scenario fixed while swapping only the implementation is the habit you want in real bug fixes too.

Be explicit about what a reproducer leaves uncovered. This lab runs sequentially in memory. It says nothing about two concurrent workers racing on the same webhook, a process crashing right after commit, or a lost database acknowledgement. A historical reproducer guards against *that* failure returning; it does not discover novel failure modes on its own.

## Preserve the cause, then strip the noise

Start with whatever reproduces the bug, even if it is an ugly script or a slow integration test. Trying to design an elegant fixture before you understand the failure drags out the investigation.

Once it fails reliably, trim it down. Drop accounts, fields, and intermediate steps one at a time, rerunning against the broken code after each cut. Stop before the next cut obscures why the bug happened. A reproducer that only repeats a surface symptom (like a canned error code) without recreating the underlying mechanism misses the bug when it returns in slightly different form.

Verify that the reproducer fails on the unfixed code before merging it. A regression test written *after* the fix often passes without touching the buggy branch. If checking out the old commit is painful, re-introduce the bug locally and watch the assertion catch it. Make the failure message name the domain problem ("payment applied twice") instead of burying the reader in a fixture setup traceback.

## Pin down everything that drifts

Give the reproducer its own isolated state. Swap live payment APIs for a local stub that records attempted calls. Replace production payloads with synthetic IDs and amounts that keep the structural relationships intact, such as the repeated `evt_001`. Copying raw production JSON pulls in customer data and fifty unrelated fields.

Pin the clock whenever deadlines or billing periods matter, including the timezone. Pin random seeds when randomness is involved, while remembering that a seed will not make an uncontrolled thread schedule deterministic.

For a race condition, put a controllable barrier at the contested step so both workers meet there reliably. A `time.sleep(0.5)` turns a reproducer into a flake that depends on CI load. For a crash mid-flight, capture the durable state before and after the interruption and replay the retry explicitly. Add that extra plumbing only when the bug demands it.

[Hypothesis's guide to flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html) covers the usual culprits: leftover state, ambient clocks, and unseeded randomness. The bar is simple: does the reproducer behave the same way tomorrow, and after twenty other tests ran ahead of it?

## Put it where people will run it

Most reproducers belong inside the existing test suite. Name the test after the failure mode, link the incident or issue number, and leave the rationale next to the assertion. Almost nobody remembers to run a separate `reproducers/` folder sitting off to the side.

Some failures genuinely need a slower environment or multiple processes. Keep those near the code with one documented command and run them on an appropriate trigger: changes to that component, a nightly job, or a release check. A twenty-minute multi-process replay should not block a README typo fix.

When a property-based test discovers a nasty failure, pin that case as an explicit regression test. [Hypothesis recommends `@example`](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html), since its local example database can be invalidated across versions or test edits.

## Know what is worth keeping

Keep a reproducer when reconstructing the setup took real effort, the bug could return, or the case will help verify a future rewrite. A trivial typo covered by a five-line unit test does not need a replay harness.

Every saved case carries upkeep. Dependencies move, schemas shift, and product rules change. Give each reproducer a clear owner, usually the team that owns the behavior. When a rule changes, update the explanation alongside the assertion, and delete redundant cases once a stronger invariant or clearer test covers the same ground.

Watch out for replay suites that only work on the author's laptop. Have someone who was not part of the incident run the command and explain what the assertion protects. Their questions show you what is still missing.

## How it connects

The immediate payoff is narrow: the next person can replay this bug without spending another afternoon rebuilding it. Count it as a win when setup stays cheap and later changes reuse the case, not when the folder grows large.

This pattern is often the first step in a longer chain. Once two or three reproducers repeat the same setup, pull the shared parts into [scenario builders](./scenario-builders.md). If the same class of bug keeps showing up, generalize the check into an [executable invariant](./executable-invariants.md). If someone else needs to run the replay outside the test suite, wrap it in a [capability command](./capability-command.md). And when it is time to replace that legacy module, your saved reproducers become the starting corpus for [differential verification](./differential-verification.md). Let real pain pull you into the next step instead of building all of it upfront.
