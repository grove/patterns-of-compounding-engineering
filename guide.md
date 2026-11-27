# Using the guide

*Pick a real point of friction, make one small change, and see whether the next job gets easier.*

A messy debugging session often ends with something useful sitting in a scratch directory: a replay script, a handful of awkward test cases, or a query that exposes broken state. Some of those artifacts earn a place in the repository. Others depend on so much local context that keeping them alive turns into a second job.

This guide is about making that call and shaping what you keep so a teammate can use it without calling you over. Every pattern fits inside an existing codebase. You can try one on a Tuesday afternoon without pitching a platform initiative or waiting for permission to adopt all ten.

## Start with real friction

Pick something that already cost you time. Maybe the last two billing incidents forced someone to assemble the same broken account state from scratch. Maybe reviewers keep leaving the same comment about billing handlers importing the payment SDK directly. Write down the task, what slowed it down, and who ran into it.

Specificity keeps you honest. "We need better developer experience" can justify almost any tool. "A new engineer cannot reproduce this duplicate payment without pulling the original author into a call" gives you something concrete to test against.

Before building a tool or a check, ask whether you can eliminate the chore altogether. If engineers run a repair script every Monday because a webhook handler drops idempotency keys, fixing the handler beats wrapping the repair script in a friendlier CLI.

When the work itself stays, start with the pattern closest to your problem:

- [Understand a failure](./patterns/persistent-reproducer.md), [construct awkward states](./patterns/scenario-builders.md), [check business guarantees](./patterns/executable-invariants.md), or [compare a replacement](./patterns/differential-verification.md).
- [Contain a dependency mess](./patterns/architectural-ratchet.md), [automate a recurring review catch](./patterns/review-comment-to-guardrail.md), or [package an investigation for someone else](./patterns/capability-command.md).
- [Test competing designs](./patterns/competing-prototypes.md), [prove whether old code can be deleted](./patterns/subtraction-investigation.md), or [audit whether an earlier tool paid off](./patterns/investment-retrospective.md).

## Reuse is not compounding

Adding tests and scripts does not automatically speed a team up. Retaining an artifact can end in four different places:

| Outcome | What it looks like |
| --- | --- |
| Accumulation | A growing pile of regression tests that protects past fixes while slowing down every schema change |
| Recurring return | A replay command that saves an hour whenever a billing bug shows up |
| Compounding | A scenario builder written for one bug that makes invariant tests and a migration comparator cheap to build next |
| Negative compounding | Fragile helper scripts whose upkeep eats more time than they save and makes people avoid touching the code |

Recurring returns are fine. Plenty of worthwhile tools stop there. Compounding happens when one capability lowers the cost of building the next one, so the useful unit is often a short chain of patterns:

- **From one bad incident to deleting old code:** Turn a painful bug into a [persistent reproducer](./patterns/persistent-reproducer.md). Once a few cases share the same setup pain, extract [scenario builders](./patterns/scenario-builders.md). Feed those builders into [executable invariants](./patterns/executable-invariants.md) across edge cases, reuse the same corpus for [differential verification](./patterns/differential-verification.md) when you replace the old calculator, and finish with a [subtraction investigation](./patterns/subtraction-investigation.md) to delete the legacy path cleanly.
- **From noisy reviews to steady cleanup:** Turn a repeated review correction into a [review comment to guardrail](./patterns/review-comment-to-guardrail.md). Freeze legacy violations with an [architectural ratchet](./patterns/architectural-ratchet.md) so you can ship while cleaning up. Put the checks behind a [capability command](./patterns/capability-command.md) that runs identically locally and in CI, and check whether the whole setup still earns its keep in an [investment retrospective](./patterns/investment-retrospective.md).

You never have to walk the whole chain. Stop as soon as the next step stops paying for itself.

## Choosing between competing investments

Most teams do not lack ideas for tooling; they lack time. Suppose you have two days and four real candidates: better billing fixtures, a custom lint rule, an investigation CLI, or deleting a legacy CSV export.

Skip elaborate scoring matrices and run five plain questions past each candidate:

- **Generativity:** Does this unlock a later change or capability that is currently too risky? A rarely used migration comparator can matter more than a daily convenience script if it makes replacing a tangled module safe.
- **Frequency:** How often does this friction hit? High frequency usually wins, unless you are about to polish a workaround for a bug you should just fix.
- **Reach:** Does this help one person's workflow, or does it unblock newcomers, code reviewers, and CI?
- **Depreciation:** How fast will the underlying assumptions expire? A fixture suite tied to a billing model you plan to retire next quarter has a short shelf life.
- **Carrying cost:** What breaks when schemas, dependencies, or product rules move? A small check that rides on an existing linter costs far less to own than a bespoke harness.

Generativity and carrying cost are the two easiest factors to misjudge. Teams over-invest in frequent minor annoyances and under-invest in the one capability that makes an upcoming architectural change safe.

## Keep the first version small

Solve the problem in front of you before generalizing. Keep one incident reproducible before designing an event-replay framework. Write one narrow lint rule before rolling out a company-wide policy. Investigate one legacy export before pitching a service cleanup.

Set a time cap upfront — an afternoon for a reproducer, a day or two for a migration comparison — and name what would make you drop the experiment. Without a stopping condition, half-working prototypes turn into permanent maintenance debt.

A short note in the issue or pull request is enough, and it also makes the work legible to a manager or product lead when you want to fold a half-day investment into active delivery work:

```text
Problem: Reproducing a failed payment requires the original author's help.
First attempt: Save one synthetic input and a command to replay it.
Useful result: Another engineer can run it and explain why it failed.
Budget: One afternoon for the first version.
Review: After the next payment change.
Stop if: It needs a private production snapshot to stay useful.
```

Scale the budget to the job. Some problems take an hour, while a cross-service migration takes days.

## Try the billing example

Most of the patterns share a synthetic subscription billing service so you can see how the pieces connect. It handles async payment events, calculates invoices with credits, changes pricing rules, and drags around an old CSV export. The examples stick to ordinary bugs: duplicate webhook delivery, credit larger than an invoice, copy-pasted test setup, and a rewrite that passes the easy cases while botching the edges.

You can run a small piece of it from this repository using the [billing lab](./examples/README.md):

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
python3 examples/billing_lab.py verify
python3 examples/billing_lab.py compare --candidate buggy
python3 examples/billing_lab.py compare --candidate correct
```

Run them one at a time so you can see the exit codes. Both `--implementation buggy` and `--candidate buggy` are meant to fail — that is how you verify the checks can catch a defect. The buggy webhook handler applies the same event twice, while the fixed one tracks seen event IDs in memory. The buggy invoice calculator lets applied credit exceed the subtotal and drives the balance negative.

The lab is intentionally toy-sized: single-process, in-memory, no tax, no concurrency, no database transactions. It demonstrates the shape of the checks. It is not a blueprint for a production ledger.

## Keep evidence independent (especially with AI)

A tool outlives its author only when the next person can tell what it proves. Put the command, its assumptions, and sample output beside the code. Spell out what data is synthetic, what the check catches, and what it leaves uncovered.

When coding agents make generating code and test scaffolding cheap, verification becomes the bottleneck. That cuts two ways. With solid reproducers, invariants, and comparison corpora, you can delegate more work to agents safely and free up time for harder improvements. Without them, cheaper code generation produces more code, more test volume, and a heavier verification burden with less human understanding.

The biggest trap is shared assumptions. An agent can generate an implementation, a matching test suite, fixtures, and a plausible explanation from the exact same mistake. Agreement between generated artifacts is not independent evidence of correctness. Keep the problem statement, boundary examples, and expected results anchored outside the code under test, and review edits to fixtures and assertions with the same skepticism you apply to production logic.

Resist generalizing early. Three readable 40-line scripts are often cheaper to live with than one configurable framework nobody trusts. Extract shared code once real reuse shows you what varies.

## Check the upkeep and know the scope

A clean first run proves an idea worked once. Later changes tell you whether it was worth keeping.

Watch what happens when someone else picks it up. Where did they stall? Did they route around the tool because it missed refunds? Did updating a fixture take longer than the bug fix? The [investment retrospective](./patterns/investment-retrospective.md) gives you a lightweight way to check both individual tools and the combined drag of everything you have accumulated, without pretending rough estimates are hard science. Simplifying or deleting a tool is a good outcome.

This field guide has a deliberate boundary: it covers code, tests, and local workflows an engineering team controls directly. It is not a continuous-delivery manual or an org-design book. Technical capability alone cannot guarantee compounding — if a team frees up 20% of its time and the organization immediately absorbs all of it into feature output, nothing compounds because nothing gets reinvested. The organizational side (incentives, capability traps, and room to reinvest) lives in [Organizations that improve with age](https://grove.github.io/engineering-that-compounds/essays/organizations-that-improve-with-age.html).

## About the sources and examples

The pattern names are editorial handles for established engineering techniques — property testing, Object Mother, differential testing, frozen architecture rules, online migrations — rather than claims of invention. Every pattern links to primary tools or practitioner write-ups and notes what carries over versus what belongs to a specific stack.

The billing scenarios and retrospective numbers are invented for teaching and are not empirical case studies. This collection builds on [Software that improves with age](https://grove.github.io/software-that-improves-with-age/) and [Engineering that compounds](https://grove.github.io/engineering-that-compounds/), though it stands on its own.

