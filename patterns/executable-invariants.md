# Executable invariants

*Write down the guarantees that must survive a change.*

A billing test expects an invoice total of 8,750. The implementation returns 8,750. That is useful evidence for one case, but the number tells a reviewer little about what the system promises. Does credit reduce the amount due? Can it make the balance negative? Is the same payment allowed to affect two invoices?

An invariant states a relationship that should hold across a defined set of situations. It gives tests something to challenge when the inputs change. The hard part is deciding which relationship the business actually requires.

Use this pattern when the team repeatedly explains the same rule, when examples miss important combinations, or when replacing an implementation would otherwise mean trusting its old outputs wholesale.

## Agree on the boundary of the claim

For the illustrative billing model in this guide, assume one currency and integer minor units, with nonnegative quantities, unit prices and requested credit. There is no tax or prorating. Requested credit may exceed the current invoice. The model applies credit only up to the subtotal and leaves the rest unused.

Under those assumptions, useful relationships include:

- Applied credit is between zero and the subtotal, inclusive.
- Amount due plus applied credit equals the subtotal.
- Applied credit never exceeds requested credit.
- Reordering invoice lines does not change the result.
- Delivering the same payment event again does not apply the payment again.

These rules are proposals for this small model, not universal rules for billing. A system that represents account credit as a negative balance needs different assertions. An invoice with tax, exchange rates or line-level rounding needs a more detailed contract. State those limits beside the check so a future developer can tell when it stops applying.

Ask the person who owns the policy to review a few boundary examples. Zero credit, credit exactly equal to the subtotal, and excess credit often expose disagreements that a normal invoice conceals. Resolve the disagreement before encoding it as a release gate.

## Check relationships independently

The following is illustrative test logic for that contract. `calculate` is the implementation under test; the result fields are explanatory names:

```python
result = calculate(lines, requested_credit)
subtotal = sum(quantity * unit_minor for quantity, unit_minor in lines)

assert 0 <= result.credit_applied <= subtotal
assert result.credit_applied <= requested_credit
assert result.amount_due + result.credit_applied == subtotal
```

Those assertions still allow some wrong results. An implementation that never applies any credit would satisfy all three. Add an independently agreed example for a 1,000 subtotal and 300 requested credit: 300 applied and 700 due. Add the boundary case where requested credit exceeds the subtotal. Properties and examples cover different gaps.

A test oracle is the source of the expected answer. Keep it easy to inspect. Calling the same production helper to compute both expected and actual values checks that the helper agrees with itself. A simple expression for a limited contract, a reviewed worked example, or a separately maintained model can provide a useful independent check. Independence depends on the assumptions and implementation; moving a copy into another file does not provide it.

The [billing lab](../examples/README.md) runs a small set of such checks with:

```sh
python3 examples/billing_lab.py verify
```

The lab uses a finite set of inputs and deliberately simple policies. Passing it establishes only what those checks exercise. It is not a production billing specification.

## Choose inputs that challenge the rule

Begin with the boundaries you can explain: zero, one unit, exact credit, excess credit, empty inputs if permitted, and the largest supported amount. Include invalid inputs separately and define their expected rejection behavior. Mixing invalid states into an ordinary property without specifying what should happen makes failures ambiguous.

Property-based testing can generate more combinations and reduce failing inputs to manageable examples. [Hypothesis's stateful testing documentation](https://hypothesis.readthedocs.io/en/latest/stateful.html) goes further by generating sequences of actions and checking them against a model. That is useful when correctness depends on a history of payments, retries and refunds rather than one calculation.

Keep the generator's assumptions visible. A generator that always emits positive balances cannot find a bug involving exhausted credit. A generator that always presents events in order cannot test a handler's response to reordered delivery. Inspect the actual inputs produced, including whether the boundary cases you care about appear.

Retain a meaningful failing input as a [persistent reproducer](./persistent-reproducer.md). The property can keep exploring while the retained example protects a failure the team now understands.

## Be precise about time and state

Some guarantees should hold after every operation. Others hold only after a transaction commits or a batch finishes. Checking a ledger halfway through an intentional transfer can report an imbalance that disappears at the actual consistency boundary. Conversely, checking only the final balance can miss an invalid intermediate state that another reader can observe.

Name the boundary. For an asynchronous invoice projection, the claim might be that the projection agrees with the authoritative ledger once processing has reached a specified event position. A timeout alone does not describe what completion means.

The payment-retry guarantee also needs a definition of identity. The same event delivered again differs from a second legitimate payment for the same amount. Reusing an amount as a deduplication key would reject valid work. In production, the durable deduplication record and the payment effect need a failure-safe relationship; an in-memory set demonstrates the rule but cannot provide it across processes.

## Check that the checks can fail

Temporarily introduce a plausible defect in an isolated copy: apply excess credit, forget one line, or process a duplicate payment. The relevant check should fail for an understandable reason. If it does not, either the inputs never reach the defect or the property is too weak.

This need not become a project-wide mutation-testing initiative. One deliberately broken implementation can answer the immediate question. [SQLite's testing account](https://sqlite.org/testing.html) describes mutation testing among its broader verification techniques; it is a useful example of questioning the test machinery itself.

When asking an agent to suggest missing cases, supply the policy and examples before the implementation. Ask which assumptions its proposed checks leave untested. Review those assumptions yourself: a plausible assertion may simply repeat the mistake in the code.

## Keep the guarantees useful

An invariant carries a maintenance obligation. When product rules change, review the relevant assertions and their scope. Record why the change is allowed. Do not turn an outdated rule into an obstacle that everyone learns to bypass.

Look for evidence that the check catches an actual mistake, makes a review easier, or allows a replacement to be assessed with less manual reconstruction. If failures routinely demand edits to expected values without discussion of behavior, the check may be a snapshot of implementation details wearing a stronger name.

[Scenario builders](./scenario-builders.md) make the input space easier to explore. [Differential verification](./differential-verification.md) can reveal where a replacement changes behavior. The invariants then help decide which differences are defects and which are corrections.
