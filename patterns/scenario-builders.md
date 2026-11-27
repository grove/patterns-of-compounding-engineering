# Scenario builders

*Make awkward business states cheap to set up without hiding what matters.*

Suppose you need to test a refund on an overdue subscription. Before you even get to the refund, you have to create a customer, a plan, a subscription, an invoice, a failed payment, and a credit. Most of that setup gets copy-pasted from another test, and buried somewhere in those forty lines is the one field your new test actually depends on.

The exact same tax shows up during debugging and demos. Someone asks to see an account halfway through a plan change, and a developer burns an hour clicking through a local environment to reach that state. A scenario builder gives that business situation a clear name and a reliable way to construct it.

Wait until the setup boilerplate is actually getting in your way. For a simple test, two or three plain constructor calls are almost always clearer than a helper.

## Name the situation, not the plumbing

In our billing example, the situations engineers talk about with finance or support are things like an unpaid invoice, credit larger than the subtotal, or a duplicate payment event. Name your builders after those situations.

The rule of thumb is simple: hide the boring defaults, expose the difference the test is actually about. A test for excess credit should show the credit amount right at the call site. A test for subscription expiry should pass the clock explicitly.

Martin Fowler wrote this up years ago as the [Object Mother pattern](https://martinfowler.com/bliki/ObjectMother.html): a factory hands out recognizable example objects instead of making every test assemble them from scratch. Fowler also warned about the trap: once dozens of tests depend on the exact same pre-baked fixture, changing one field breaks half the suite. Small factories with explicit overrides keep that coupling visible.

Here's a minimal Python sketch showing the shape of the interface (separate from the billing lab's own functions):

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

One glance tells you the setup: two units at 500, requesting 1,200 of credit. The test then states the expected outcome itself (1,000 applied, 0 due, 200 unused) without calling the production calculator to compute the expected answer. If the builder calculates expected values with production code, a shared bug passes quietly.

## Split the description from how it's loaded

A unit test for pricing math only needs plain data. An integration test needs database rows and queued events. A browser demo needs a real user account you can log into.

Don't force every caller to pay for the heaviest version. Keep the core description as plain values and add a persistence or HTTP adapter only when a test or demo actually needs it. Pure pricing logic shouldn't spin up Postgres just because the local demo script happens to seed one.

Be deliberate about how faithfully you build state. Going through public application services runs real validation and blocks impossible combinations. Writing rows straight to the database is much faster (and totally fine for testing a read query), but it skips all the workflows real users hit. A shortcut setup can't prove the application itself can ever reach that state.

When you *do* need a broken state (say, an invoice pointing at a deleted account for a corruption test), give it an obvious name like `orphaned_invoice()` so nobody mistakes it for a normal fixture.

## Keep runs isolated

Every call needs fresh state. Handing back a shared mutable object lets one test poison the next. Immutable case objects solve this in memory, and database adapters need their own isolation: unique IDs per test run and reliable cleanup, so parallel runs don't collide on hardcoded primary keys. Repeatability means the relationships stay the same, not that every test insists on owning `customer_id = 1`.

Always pass the clock into time-sensitive builders. An `overdue_account()` helper that reads wall-clock time works today and flakes on the first of next month—or across a daylight-saving boundary. Pin the business date and timezone when they affect the rule, and keep incidental timestamps out of your assertions.

The same goes for random test data. Randomization is great for exploration, as long as a failure prints the seed or inputs needed to replay it. [Hypothesis's notes on flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html) list the usual suspects: leftover state, unseeded randomness, and ambient clocks. If your builder leaks any of those, every test built on top of it becomes harder to trust.

## Extract from two real callers, not a wish list

Grab two existing tests or debugging scripts with nearly identical setup and pull out one factory for what they share. Migrate one caller at a time and check that the test still reads cleanly. If the factory immediately grows twelve boolean flags, those two cases probably weren't the same concept after all.

Keep the unusual bits visible at the call site. `invoice_case(credit_minor=1200)` makes sense to a reviewer six months later; `special_customer(variant=7)` forces everyone to memorize a private cast of characters.

An AI coding agent is decent at spotting copy-pasted test setup and refactoring callers onto a builder, but inspect the defaults it picks. Averaging together existing fixtures often freezes accidental assumptions (a hardcoded currency, a single timezone, an active plan) into every future test. Default values in a builder deserve the same scrutiny as defaults in production code.

## Watch for a second application and correlated blind spots

Builders go sideways in two quiet ways.

First, they can turn into a parallel implementation of your product. Once your account builder contains its own mini pricing engine, tax rules, and state machine, every product change means updating two systems. Prefer real domain operations whenever they're fast enough. When you must insert state directly, note what you bypassed and keep at least one integration test verifying that the normal workflow produces the same shape.

Second, **shared builders create correlated blind spots.** Once the same builder feeds your [persistent reproducers](./persistent-reproducer.md), [executable invariants](./executable-invariants.md), [differential verification](./differential-verification.md), and [competing prototypes](./competing-prototypes.md), any assumption baked into its defaults quietly hides bugs from *all four*. If the builder always constructs single-currency invoices or always delivers events in order, every green check built on top of it shares that blind spot. Periodically ask what states the builder makes hard or impossible to construct; that's usually where the next production surprise lives.

Retire scenarios when the product moves on. If legacy plans still exist in production, tag those builders with their policy version instead of silently updating them to current rules.

## How to tell if it's helping

Fewer lines of setup matter only if someone else can build the next weird case without copy-pasting a wall of fixtures or pinging the original author, and a code reviewer can immediately spot what makes the test case interesting.

When a builder works well, it stops being "just a test helper": the same scenario feeds a bug reproducer, a walkthrough with finance, a property check, and eventually a migration comparison. That reuse is where the payoff actually compounds. If updating the builder starts taking longer than the changes it supports, trim it back or review it in an [investment retrospective](./investment-retrospective.md).
