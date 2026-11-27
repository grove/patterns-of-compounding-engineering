# Executable invariants

*Turn the rules the business depends on into checks that hold across many inputs.*

A unit test asserts that an invoice total equals 8,750, and the code returns 8,750. That confirms one arithmetic case while telling a reviewer almost nothing about what the system actually promises. Can credit push the balance below zero? Does line-item order matter? Can one payment settle two invoices?

An invariant states a relationship that must hold across a whole class of inputs rather than one hand-picked example. They earn their keep when the team keeps re-explaining the same rule in code review, when example tests keep missing weird combinations, or when you are about to replace legacy code and do not want to treat its old outputs as gospel.

## Discover and bound the rule first

In real codebases, business rules rarely sit cleanly on a whiteboard waiting to be coded. More often, finance assumes one thing, support handles exceptions another way, and legacy code does a third thing nobody documented.

Using three or four uncomfortable boundary cases—zero credit, credit equal to the subtotal, excess credit, a refund after cancellation—is the fastest way to smoke out those disagreements with whoever owns the policy. Getting an explicit answer on those edges is often more valuable than the test code itself.

Take our simplified billing model: one currency, integer minor units, nonnegative quantities and prices, no tax or proration. Requested credit can exceed the invoice subtotal, and any leftover credit stays unused. Under that contract, five guarantees stand out:

- Applied credit stays between zero and the subtotal.
- Amount due plus applied credit always equals the subtotal.
- Applied credit never exceeds requested credit.
- Reordering invoice lines produces the same result.
- Replaying the same payment event does not apply the payment twice.

None of these are universal laws of accounting. If a later product change represents account credit as a negative balance, or introduces per-line tax rounding and FX rates, some of these guarantees stop holding. Write the scope assumptions right next to the check so the next engineer knows when a rule was an intentional policy choice and when it needs renegotiating.

## Keep the oracle independent of the code

In Python, where `calculate` is the function under test, the core assertions are short:

```python
result = calculate(lines, requested_credit)
subtotal = sum(quantity * unit_minor for quantity, unit_minor in lines)

assert 0 <= result.credit_applied <= subtotal
assert result.credit_applied <= requested_credit
assert result.amount_due + result.credit_applied == subtotal
```

Those three lines still have a glaring hole: a broken implementation that always returns `credit_applied = 0` passes all three. Pair general invariants with a couple of independently worked examples (say, 1,000 subtotal with 300 credit gives 300 applied and 700 due, plus an excess-credit case). Properties explore combinations you did not think of; worked examples anchor the concrete behavior.

Check where your expected values come from. Calling a production helper inside the test only proves the helper agrees with itself, and copying that helper into `tests/` does not make it independent either. Real independence comes from a simpler formula for a narrow case, a hand-worked example, or a separate reference model.

This matters even more with coding agents. Show an agent an implementation and ask for invariant tests, and it will happily derive "invariants" straight from the code's existing bugs—giving you green checks built on the exact same mistake. Give the agent the policy and boundary examples *before* showing it the implementation, and ask what assumptions its checks leave uncovered.

You can run a small version in the [billing lab](../examples/README.md):

```sh
python3 examples/billing_lab.py verify
```

It runs over a finite, deterministic grid of cases with simple rules, so passing it is evidence about that small contract, not a full billing spec.

## Pick inputs that try to break the rule

Start with boundaries anyone can check by hand: zero, one unit, exact credit, excess credit, empty lists (if valid), and the upper bound you support. Test invalid inputs separately with explicit expected errors so malformed inputs do not muddy an ordinary property failure.

Once the rules are solid, property-based testing can explore combinations you would never type by hand and shrink failures down to tiny counterexamples. When correctness depends on a *sequence* of actions (payments, retries, refunds, cancellations), [Hypothesis's stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html) lets you generate action histories and check them against a small state model.

Audit what your generators actually produce. A generator that only builds positive balances will never hit an exhausted-credit bug, and one that only emits ordered events will never hit out-of-order delivery. Whenever a property uncovers a real bug, pin that input as a [persistent reproducer](./persistent-reproducer.md) so the team keeps the concrete case even as the generator keeps wandering.

## State when the rule is supposed to hold

Some guarantees hold after every single call. Others only hold once a transaction commits or an async worker catches up. Checking a ledger mid-transfer complains about a temporary imbalance that vanishes at commit time; checking only the final total can miss a broken intermediate state that another reader sees.

Name the consistency boundary directly. For an async invoice projection, "matches the ledger once processed up to event N" is testable; "matches after sleeping two seconds" is a flake waiting to happen.

The same precision applies to identity. Re-delivering `evt_001` is a duplicate, whereas a customer paying the same 2,400 amount a second time under `evt_002` is a legitimate payment. Deduplicating by amount drops real revenue. Keep in mind that an in-memory set only models the rule; production idempotency needs a failure-safe link between the deduplication record and the payment write.

## Make sure the checks can fail

Temporarily break the code in a local copy: let credit exceed the subtotal, drop a line item, or disable duplicate checks. Your invariants should fail loudly and for the right reason. If they stay green, either your inputs never reached the bug or your assertions are too weak.

You do not need a full mutation-testing pipeline to get most of that signal; one or two hand-injected faults tell you right away. ([SQLite's testing write-up](https://sqlite.org/testing.html) includes mutation testing among its layers of defense, and it is a useful reminder to test your tests as well as your code.)

## Keep invariants from rotting into snapshots

Product rules move, and invariants have to move with them. When finance changes a credit policy, revisit the affected checks, update the scope notes, and record why the contract shifted. Letting an outdated rule linger teaches people to silence or bypass the suite.

Watch how engineers react when an invariant fails in CI. If the failure triggers a real question about expected behavior, the check is doing its job. If people routinely tweak assertions to match whatever the code just returned without asking why, you are maintaining brittle snapshots under a fancier name.

## What invariants make possible later

Invariants rarely start from scratch. Usually a [persistent reproducer](./persistent-reproducer.md) exposes a recurring class of failure, and [scenario builders](./scenario-builders.md) make it cheap to feed the rule varied business states.

The compounding shows up when you have to make a bigger move later. When [differential verification](./differential-verification.md) turns up a mismatch during a rewrite, or when you run [competing prototypes](./competing-prototypes.md) to settle a design question, executable invariants give you an independent referee instead of forcing you to treat old code as truth.
