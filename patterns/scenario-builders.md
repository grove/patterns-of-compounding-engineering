# Scenario builders

*Make awkward business states cheap to set up without hiding what matters.*

Try writing a test for a refund on an overdue subscription. Before you even call the refund code, you have to create a customer, a plan, a subscription, an invoice, a failed payment, and a credit. Almost everybody copies forty lines of setup from an older test, tweaks one number in the middle, and hopes nothing else in those forty lines quietly matters.

The same drag hits during debugging and demos. Someone wants to inspect an account halfway through a plan change, and a developer spends an hour clicking through a local environment to reach that state. A scenario builder gives that business situation a plain name and a fast way to construct it.

Wait until setup boilerplate actually starts slowing people down. If a test only needs two or three constructor calls, write them out directly.

## Name the business situation

In our billing service, the situations engineers talk about with finance or support are things like an unpaid invoice, credit larger than the subtotal, or a duplicate payment event. Name builders after those situations rather than internal table layouts.

Hide the boring defaults and surface the one parameter the test cares about. A test for excess credit should show the credit amount right at the call site; a test for subscription expiry should pass the clock explicitly.

Martin Fowler documented this years ago as the [Object Mother pattern](https://martinfowler.com/bliki/ObjectMother.html): a factory hands out recognizable example objects so tests do not assemble them from scratch. Fowler also noted how it rots: once dozens of tests rely on the same pre-baked fixture, changing one field breaks half the suite. Small factories with explicit keyword overrides keep that coupling visible.

Here is a minimal Python sketch showing the interface (separate from the billing lab's own functions):

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

You can read the whole test condition in four lines: two units at 500, asking for 1,200 in credit. Notice that the builder stops at inputs. The test states the expected outcome itself (1,000 applied, 0 due, 200 unused) rather than calling the production calculator inside the fixture, because a builder that computes expected values using production logic lets a shared bug slip past the entire suite.

## Separate the data from how it gets loaded

A unit test for pricing math wants plain values. An integration test needs database rows and queued events. A browser demo needs a real user account you can log into.

Keep the core scenario as plain data and add a persistence or HTTP adapter only where a caller actually needs one. Pure pricing logic should not boot Postgres because a demo script seeds one.

Be deliberate about shortcuts when seeding databases. Going through public application services runs real validation and blocks impossible combinations; inserting SQL rows directly is faster and fine for testing a read query, but it bypasses the workflows real users hit, so it cannot prove the application can actually reach that state.

When you intentionally need a corrupt state (an invoice pointing at a deleted account, say), name it `orphaned_invoice()` so nobody mistakes it for a healthy fixture.

## Keep runs isolated

Every call needs fresh state. Returning a shared mutable object lets one test poison the next. Immutable dataclasses handle this in memory; database adapters need unique IDs per run and reliable cleanup so parallel tests do not collide on `customer_id = 1`. Repeatability means the relationships stay constant, not the primary keys.

Pass the clock into anything time-sensitive. An `overdue_account()` helper that calls `datetime.now()` works today and breaks on the first of next month, or across a daylight-saving shift. Pin the business date and timezone whenever they affect the rule, and leave incidental timestamps out of assertions.

Randomization is fine for exploration as long as a failure prints the seed or inputs needed to replay it. [Hypothesis's notes on flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html) list the usual culprits: leftover state, unseeded randomness, and ambient clocks. If a builder leaks any of those, every test built on top of it inherits the flakiness.

## Extract from two real callers

Take two existing tests or debugging scripts with nearly identical setup and pull out one factory for the overlap. Migrate one caller at a time and check that the test still reads cleanly. If the helper immediately grows twelve boolean flags, those two cases were probably different concepts.

Keep unusual inputs readable at the call site. `invoice_case(credit_minor=1200)` makes sense to a reviewer six months later; `special_customer(variant=7)` sends everyone hunting through fixture files.

Coding agents are quick at spotting copy-pasted setup and pulling it into a builder, so inspect the defaults they pick. Averaging existing fixtures together tends to freeze accidental assumptions (a single currency, one timezone, an active plan) into every future test. Builder defaults deserve the same review scrutiny as defaults in production code.

## Where builders go sideways

Two failure modes show up reliably once builders get popular.

The first is building an increasingly inaccurate second copy of the domain. Once an account builder contains its own mini pricing engine, tax rules, and state machine, every product change means updating two systems, and the builder drifts away from production behavior. Call real domain operations whenever they are fast enough; when you insert state directly, note what you bypassed and keep at least one integration test confirming the normal workflow produces the same shape.

The second is correlated blind spots. Once the same builder feeds your [persistent reproducers](./persistent-reproducer.md), [executable invariants](./executable-invariants.md), [differential verification](./differential-verification.md), and [competing prototypes](./competing-prototypes.md), any assumption hidden in its defaults blinds all four at once. If every builder defaults to USD and in-order webhook delivery, your whole verification stack turns green while hiding FX rounding and out-of-order events. Every so often, ask what business states the builder makes awkward or impossible to construct—that is usually where the next production surprise lives.

Retire old scenarios when the product moves on. If legacy plans still exist in production, tag those builders with their policy version instead of silently updating them to current rules.

## What builders make practical later

Shorter test files are nice, but the real shift is what becomes cheap enough to actually do: once awkward billing states take three lines to construct, engineers stop skipping edge cases, you can feed varied states straight into [executable invariants](./executable-invariants.md), compare [competing prototypes](./competing-prototypes.md) on realistic data instead of toy inputs, and assemble a corpus for [differential verification](./differential-verification.md) in an afternoon instead of a week.

Builders usually grow out of two or three [persistent reproducers](./persistent-reproducer.md) that share the same setup pain, and they often plug straight into a [capability command](./capability-command.md) for local demos or debugging. When maintaining a builder starts taking longer than the changes it supports, trim it back or put it through an [investment retrospective](./investment-retrospective.md).
