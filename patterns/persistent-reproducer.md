# Persistent reproducer

*Keep the conditions that triggered a hard bug, not just the fix.*

A subscription service occasionally applies the same payment twice. Somebody spends an afternoon piecing together what happened: the payment provider sent a webhook, the handler updated the balance, the HTTP response dropped on the wire, and the provider retried. The actual fix is five lines. The investigation was the whole afternoon.

If the pull request only ships those five lines, the next engineer inherits the conclusion with no way to test it. A paragraph in a postmortem helps, until six months later when someone touches the handler and has to reconstruct the whole setup from scratch. While the details are fresh, keep an executable version of the failure.

Duplicate webhook delivery is a real integration hazard ([Stripe documents both duplicate and out-of-order event delivery](https://docs.stripe.com/webhooks#event-delivery-behaviors)). The point of a reproducer is to put your own handler through those exact conditions, with all its real assumptions exposed.

## Keep one small, self-contained case

A good reproducer packs four things together: the starting state, the sequence of events that triggers the bug, the outcome you expect, and a single command to check it. Add a two-line comment explaining *why* that outcome is right. Without the why, a failing test six months later looks like a stale assertion someone can casually update to make CI green.

In the billing example, you start with an unpaid 2,400-unit invoice and deliver the same `evt_001` payment event twice. Then you check both the paid total and the count of applied events. Checking only HTTP 200 responses lets the test pass while the customer's balance is quietly doubled.

You can try a tiny version in the [billing lab](../examples/README.md) from the repository root:

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
```

The buggy run records 4,800 as paid across two applied events and exits with status 1. The fixed run keeps the exact same input and expectation, records 2,400 across one applied event, and exits 0. Holding the scenario fixed while swapping only the implementation is the habit you want in real bug fixes too.

Be honest about what a reproducer does *not* cover. This lab runs sequentially in memory. It says nothing about two concurrent workers racing on the same webhook, a process crashing right after commit, or a lost database acknowledgement. If one of those is the actual failure mode, reproduce that instead.

## Preserve the cause, then strip the noise

Start with whatever actually reproduces the bug, even if it's an ugly script or a bulky integration test. Trying to design the cleanest possible fixture before you understand the failure just drags out the investigation.

Once it fails reliably, trim it down. Remove accounts, fields, and intermediate steps one at a time, rerunning against the broken code after each cut. Stop when the next cut obscures the *cause* of the bug. A reproducer that merely repeats a surface symptom (say, a canned error code) without recreating the underlying mechanism won't catch the bug when it comes back in slightly different clothes. Minimal is good; inscrutable is not.

Always verify that your reproducer actually fails on the unfixed code before merging it. A regression test written *after* the fix often passes without ever hitting the buggy branch. If checking out the old commit is too painful, temporarily re-introduce the bug in a local copy and watch the assertion catch it. And make sure the failure message names the domain problem ("payment applied twice") instead of burying the reader in a fixture setup stack trace.

## Pin down everything that drifts

Give the reproducer its own isolated state. Swap live payment APIs for a local stub that records attempted calls. Replace production payloads with synthetic IDs and amounts that keep the structural relationships intact (like the repeated `evt_001`). Copying raw production JSON usually drags in sensitive customer data and fifty fields the bug doesn't care about.

Pin the clock whenever deadlines or billing periods matter, including the timezone. Pin random seeds when randomness is involved, while remembering that a seed won't make an uncontrolled thread schedule deterministic.

If the bug is a race condition, put a controllable barrier at the contested step so both workers meet there reliably; `time.sleep(0.5)` turns a reproducer into a flake that depends on CI load. If the bug is a crash mid-flight, capture the durable state before and after the interruption and replay the retry explicitly. Only add that extra plumbing when the bug actually demands it.

[Hypothesis's guide to flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html) is a useful reminder of how leftover state, ambient clocks, and unseeded randomness break repeatability. The bar is simple: does the reproducer behave the same way tomorrow, and after twenty other tests ran ahead of it?

## Put it where people will actually run it

Most reproducers belong right inside the existing test suite. Name the test after the failure mode, link the incident or issue number, and leave the rationale next to the assertion. Nobody remembers to run a separate `reproducers/` folder hidden off to the side.

Some failures genuinely need a slower environment or multiple processes. Keep those close to the code with one documented command and run them on an appropriate trigger: changes to that component, a nightly job, or a release check. A twenty-minute multi-process replay shouldn't block a typo fix in a README.

If a property-based test discovers a nasty failure, promote it into an explicit regression case. [Hypothesis recommends pinning must-keep cases with `@example`](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html), because its local example database can be invalidated across versions or test edits.

## Know what is worth keeping

Keep a reproducer when reconstructing the setup took real work, the bug could easily return, or the case will help check a future rewrite. A trivial typo that a five-line unit test already covers doesn't need a replay harness.

Every saved case carries upkeep. Dependencies move, schemas shift, and product rules change. Give each reproducer a clear owner (normally the team that owns the behavior). When a rule changes, update the explanation alongside the assertion, and delete redundant cases once a stronger invariant or clearer test covers the same ground.

Watch out for replay suites that only work on the author's laptop. Have someone who wasn't part of the incident run the command and explain what the assertion protects. Their confusion will tell you exactly what's still missing.

## Where it leads next

The immediate win is small and practical: the next person can replay this bug without spending another afternoon rebuilding it. Don't judge success by how many reproducers you collect; judge it by whether setup stayed cheap and later changes actually used them.

Once two or three reproducers repeat the same painful setup, pull the shared parts into [scenario builders](./scenario-builders.md). If the same class of bug keeps showing up, generalize the check into an [executable invariant](./executable-invariants.md). And when it's time to replace that legacy module, your saved reproducers become the starting corpus for [differential verification](./differential-verification.md). Let real pain pull you into the next step rather than building all of it upfront.
