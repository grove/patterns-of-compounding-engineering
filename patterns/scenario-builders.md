# Scenario builders

*Make important business states cheap to construct.*

An engineer wants to test a refund on an overdue subscription. Before reaching the refund, the test creates a customer, a plan, a subscription, an invoice, a failed payment and a credit. Much of the setup is copied from another test. Somewhere in that block is the detail the new test depends on.

The same work appears in bug investigations and demonstrations. Someone asks to see an account halfway through a plan change; a developer spends an hour clicking through a local application. A scenario builder gives that state a name and a reliable construction path.

Start when setup is repeatedly obscuring the behavior you are trying to examine. A few direct constructor calls are often clearer than introducing another abstraction.

## Name the situation you need

For the illustrative billing service used in this guide, useful situations include an unpaid invoice, a credit larger than the current invoice, and a payment delivered twice. These names describe things a developer can discuss with someone in support or finance.

The builder should make the relevant differences obvious. A test about excess credit ought to show the credit amount. A test about expiry ought to show the clock. Hide only the details that do not affect the question being asked.

This is closely related to the [Object Mother pattern described by Martin Fowler](https://martinfowler.com/bliki/ObjectMother.html): a factory supplies familiar example objects instead of requiring each test to build them. Fowler also describes the coupling that arises when many tests rely on the same exact fixture data. Explicit overrides and small factories help keep that coupling visible.

Here is a standalone, simplified Python example. It illustrates the construction interface; it is not the API of the billing lab:

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class InvoiceCase:
    lines: tuple[tuple[int, int], ...]
    credit_minor: int
    now: datetime

def invoice_case(*, now, lines=((2, 500),), credit_minor=0):
    items = tuple((quantity, unit_minor) for quantity, unit_minor in lines)
    return InvoiceCase(items, credit_minor, now)

case = invoice_case(
    now=datetime(2026, 1, 15, tzinfo=timezone.utc),
    lines=((2, 500),),  # quantity, unit price in minor units
    credit_minor=1200,
)
```

The case says that the invoice contains two units at 500 and requests 1,200 of credit. The test can then state the expected result independently: apply 1,000, leave nothing due, and retain 200 of unused credit if that is the chosen policy. The builder should not compute those expected values using the production calculator. That would make a shared mistake difficult to detect.

## Separate the description from its delivery

For a calculation test, plain values may be enough. For an integration test, the same scenario may need database rows and queued events. For a browser demonstration, it may need an account that someone can sign into.

Do not make every caller pay for the most expensive version. Keep a small description of the business state and introduce an adapter only when another environment actually needs it. A pure calculation should not start a database because the demonstration tool happens to use one.

Decide how faithfully construction must follow the application's normal path. Calling public application services exercises validation and avoids impossible combinations. Direct database setup can be much faster and may be appropriate when testing a read query. It also bypasses behavior that ordinary users rely on. A test built through that shortcut cannot establish that the real workflow creates the same state.

Keep invalid states explicit. A corruption test may need an invoice with a missing account. Give that construction a name that exposes the inconsistency instead of letting the ordinary builder quietly create it.

## Keep each run independent

Every call should receive fresh mutable state. Returning the same account object to several tests lets one test alter the next test's starting point. Immutable descriptions help, but their adapters still need isolated rows, queues and files.

For database scenarios, allocate identifiers within a test namespace and make cleanup part of the runner. If tests run concurrently, fixed primary keys can collide. Repeatability means preserving meaningful relationships and inputs; it does not require every concurrent run to write the same database key.

Require an explicit clock for time-sensitive situations. A scenario called `overdue_account()` that uses today's date can change behavior next month or around a timezone boundary. Record the business date and the timezone when those affect the rule. Keep irrelevant timestamps out of assertions.

Be equally careful with random example data. Variety helps exploration, but a failing run must print enough information to reproduce its starting state. [Hypothesis documents leftover state, unmanaged randomness and external timing as common sources of flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html). A builder that depends on any of them makes every test using it harder to trust.

## Extract one repeated setup first

Choose two existing tests or investigations with similar preparation. Write a factory for the shared state. Move one caller at a time and check that its behavior remains clear. If the factory needs a dozen flags immediately, the cases may not share a useful concept.

Keep important setup visible at the call site. `invoice_case(credit_minor=1200)` tells a reviewer more than `special_customer(variant=7)`. Avoid a catalogue of opaque named customers whose significance lives in people's memories.

Add a short example beside the builder. Show a common case and one override. That is usually enough documentation to start. A command that creates a scenario for interactive inspection can come later, when someone needs that use rather than another test.

An agent can help identify duplicated setup or move callers, but review the defaults closely. Automatically extracting the most common values may preserve accidental assumptions. The business meaning of a default deserves the same scrutiny as a default in production.

## Watch for a second application

A builder becomes expensive when it reimplements the workflow it is meant to support. If account setup includes a parallel pricing engine, tax calculator and state machine, every product change now has several implementations to update.

Prefer existing domain operations where their cost is acceptable. Where direct setup is necessary, document what it bypasses and keep a small integration check that an equivalent ordinary workflow produces the relevant state. There is no need to reproduce every production field merely because it exists.

Retire scenarios that no longer correspond to supported behavior. If legacy subscriptions remain in production, label them with the policy version they represent. Silently updating a legacy example to current rules removes the very distinction it was meant to preserve.

## Look for reuse outside the original test

Measure whether a developer can construct the next awkward case without copying a large fixture or asking its author. Compare setup time for similar investigations. Notice whether reviewers can identify what makes a case unusual. Fewer setup lines are useful only if the remaining lines still explain the test.

The builders may eventually support a [persistent reproducer](./persistent-reproducer.md), a demonstration for a domain expert, and a corpus for [differential verification](./differential-verification.md). The same inputs can also exercise [executable invariants](./executable-invariants.md) across variations that would otherwise be tedious to set up.
