# Executable invariants

*Turn the rules the business actually depends on into checks that hold across many inputs.*

A unit test asserts that an invoice total equals 8,750, and the code returns 8,750. That confirms one calculation, yet tells a reviewer almost nothing about what the system promises. Can credit push the balance below zero? Does line-item order matter? Can one payment settle two invoices?

An invariant states a relationship that must hold across a whole space of inputs, not just one hand-picked example. The tricky part is rarely writing the assertion; it's getting clear on what the business actually requires.

Reach for invariants when the team keeps re-explaining the same rule in reviews, when hand-picked examples keep missing ugly combinations, or when you're about to replace legacy code and don't want to treat its old outputs as gospel.

## Spell out where the rule applies

Take our simplified billing model: one currency, integer minor units, nonnegative quantities and prices, no tax or proration. Requested credit can exceed the invoice subtotal, and any leftover credit stays unused.

Under those rules, a few guarantees stand out immediately:

- Applied credit stays between zero and the subtotal.
- Amount due plus applied credit always equals the subtotal.
- Applied credit never exceeds requested credit.
- Reordering invoice lines produces the exact same result.
- Replaying the same payment event doesn't apply the payment twice.

None of these are universal laws of accounting. If your system represents account credit as a negative balance, or applies per-line tax rounding and FX rates, your invariants look completely different. Write those scope boundaries right beside the check so the next engineer knows when the rule stops being valid instead of treating a stale assumption as bedrock.

Walk a few boundary cases past whoever owns the business policy before turning them into CI gates. Zero credit, credit exactly equal to the subtotal, and excess credit are where hidden policy disagreements usually surface.

## Keep the check independent of the code

Here's the shape of those assertions in Python (`calculate` is the function under test):

```python
result = calculate(lines, requested_credit)
subtotal = sum(quantity * unit_minor for quantity, unit_minor in lines)

assert 0 <= result.credit_applied <= subtotal
assert result.credit_applied <= requested_credit
assert result.amount_due + result.credit_applied == subtotal
```

Those three lines still leave a hole: a buggy implementation that always sets `credit_applied = 0` passes all three without blinking. Pair invariants with a couple of independently worked examples (say, 1,000 subtotal with 300 credit gives 300 applied and 700 due, plus an excess-credit case). Properties catch weird combinations; worked examples pin down the concrete behavior.

Watch your test oracle. Calling a production helper inside the test to compute the expected answer only proves the helper agrees with itself, and copying that helper into a test file doesn't make it independent either. Real independence comes from a simpler formula for a restricted case, a hand-verified example, or a separate reference model.

This matters even more with AI coding agents. If you hand an agent an implementation and ask for invariant tests, it can easily derive the "invariants" from the code's existing bugs, giving you green checks built on the exact same mistaken assumption. Give the agent the policy and boundary examples *before* showing it the implementation, and ask what assumptions its checks leave untested.

You can run a small version of these checks in the [billing lab](../examples/README.md):

```sh
python3 examples/billing_lab.py verify
```

It checks a finite, deterministic grid of cases with deliberately simple rules, so passing it is evidence about that small contract, not a full billing spec.

## Pick inputs that try to break the rule

Start with the boundaries you can explain on a whiteboard: zero, one unit, exact credit, excess credit, empty lists (if valid), and the upper limit you support. Test invalid inputs separately with explicit expected errors; mixing bad inputs into an ordinary property makes failures murky.

Once the rules are clear, property-based testing can explore combinations you wouldn't think to type by hand and shrink failures down to small counterexamples. When correctness depends on a *sequence* of events (payments, retries, refunds, cancellations), [Hypothesis's stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html) lets you generate action histories and check them against a model.

Always inspect what your generators actually produce. A generator that only builds positive balances will never catch an exhausted-credit bug; one that only emits ordered events won't catch out-of-order delivery. When a property uncovers a real bug, pin that input as a [persistent reproducer](./persistent-reproducer.md) so the team keeps the concrete case even while the generator keeps exploring.

## State the consistency boundary

Some invariants must hold after every single operation; others only hold once a transaction commits or an async worker catches up. Checking a ledger mid-transfer will complain about a temporary imbalance that disappears at commit time. Checking only the final total can miss a broken intermediate state that another reader observes.

Be explicit about when the guarantee kicks in. For an async invoice projection, "matches the ledger once processed up to event N" is testable; "matches after waiting two seconds" is a flake waiting to happen.

The same precision applies to identity. Re-delivering `evt_001` is a duplicate; a customer paying the same 2,400 amount a second time under `evt_002` is a legitimate payment. Deduplicating by amount would silently drop real revenue. And remember that an in-memory set only models the rule; production idempotency needs a failure-safe link between the deduplication record and the payment write.

## Make sure the checks can actually fail

Temporarily break the code in an isolated copy: allow excess credit, drop a line item, or disable duplicate checks. Your invariants should fail loudly and for the right reason. If they stay green, either your inputs never hit the bug or your assertions are too weak.

You don't need a full mutation-testing pipeline to get most of this benefit; one or two hand-injected bugs answer the immediate question. ([SQLite's testing write-up](https://sqlite.org/testing.html) includes mutation testing among its layers of defense, and it's a good reminder to test your tests as well as your code.)

## Keep invariants from rotting into snapshots

Business rules change, and invariants have to move with them. When a policy shifts, review the affected checks, update the scope notes, and record why the rule changed. Even an independently written invariant is only as good as the domain assumptions behind it; letting an outdated rule linger teaches everyone to silence or skip the suite.

A good sign that an invariant is working is that it catches real regressions, shortens reviews, or helps evaluate a rewrite. A bad sign is engineers routinely editing expected values to match code changes without discussing behavior; at that point you're maintaining brittle snapshots wearing a fancier name.

In practice, invariants rarely live alone: [scenario builders](./scenario-builders.md) make it cheap to feed them varied states, and when [differential verification](./differential-verification.md) turns up a mismatch during a rewrite, your invariants help decide which implementation is actually right.
