# Using the guide

*Pick a real point of friction, make one small change, and see whether the next job gets easier.*

A messy debugging session often ends with something useful sitting in a scratch directory: a replay script, a handful of nasty test cases, a query that exposes broken state. Sometimes it's worth keeping. Other times it depends on so much local context that keeping it alive becomes a second job.

This guide is about making that call and shaping the things you keep so someone else can actually use them. Every pattern here is something a team can try inside an existing codebase. You don't need a platform initiative, a rewrite, or permission to adopt all ten.

## Start with real friction

Pick something that already got in your way. Maybe the last two billing incidents forced someone to hand-assemble the same broken account state from scratch. Maybe reviewers keep leaving the same comment about why billing handlers shouldn't import the payment SDK directly. Write down the task, what slowed it down, and who ran into it.

That specificity keeps you honest. "We need better developer experience" can justify almost any tool. "A new engineer can't reproduce this duplicate payment without pulling the original author into a call" gives you something concrete to test against.

Before you build a tool or a check, ask one blunt question: **can we eliminate the task instead?** Sometimes the highest-return move isn't making a recurring workaround easier to run, but removing the design quirk that forces people to run it in the first place.

If the work stays, pick the pattern closest to the problem:

- [Understand a failure](./patterns/persistent-reproducer.md), [construct awkward states](./patterns/scenario-builders.md), [check business guarantees](./patterns/executable-invariants.md), or [compare a replacement](./patterns/differential-verification.md).
- [Contain a dependency mess](./patterns/architectural-ratchet.md), [automate a recurring review catch](./patterns/review-comment-to-guardrail.md), or [package an investigation for someone else](./patterns/capability-command.md).
- [Test competing designs](./patterns/competing-prototypes.md), [prove whether old code can be deleted](./patterns/subtraction-investigation.md), or [audit whether an earlier tool actually paid off](./patterns/investment-retrospective.md).

## Reuse is not compounding

Adding tests and scripts does not automatically make a team faster. Four different things happen when you retain engineering artifacts, and it helps to tell them apart:

| Outcome | What it looks like |
| --- | --- |
| Accumulation | A growing pile of regression tests that protects past fixes but slows down every schema change |
| Recurring return | A replay command that saves an hour whenever a billing bug shows up |
| Compounding | A scenario builder built for one bug that makes invariant tests and a migration comparator cheap to build next |
| Negative compounding | Fragile helper scripts whose upkeep eats more time than they save and discourages people from touching the code |

Recurring returns are good, and plenty of worthwhile tools stop there. Compounding happens when one capability lowers the cost of building the next one. Often the useful unit is a short sequence where each piece stands on the previous one:

- **From one bad incident to a safe replacement:** Turn a painful bug into a [persistent reproducer](./patterns/persistent-reproducer.md). When a few cases share the same setup pain, extract [scenario builders](./patterns/scenario-builders.md). Use those builders to run [executable invariants](./patterns/executable-invariants.md) across edge cases, feed the same corpus into [differential verification](./patterns/differential-verification.md) when you replace the old calculator, and finish with a [subtraction investigation](./patterns/subtraction-investigation.md) to delete the legacy path cleanly.
- **From noisy reviews to steady cleanup:** Turn a repeated review correction into a [review comment to guardrail](./patterns/review-comment-to-guardrail.md). If legacy violations get in the way, freeze them with an [architectural ratchet](./patterns/architectural-ratchet.md). Wrap the checks behind a [capability command](./patterns/capability-command.md) anyone can run locally and in CI, and check whether the whole setup is earning its keep with an [investment retrospective](./patterns/investment-retrospective.md).

None of these sequences is mandatory. Stop as soon as the next step isn't paying for itself.

## Keep the first version small

Solve the problem in front of you before generalizing. Keep one incident reproducible before designing an event-replay framework. Write one narrow lint rule before rolling out a company-wide policy. Investigate one legacy export before pitching a service cleanup.

Agree on a time cap upfront (an afternoon for a reproducer, maybe a day or two for a migration comparison) and decide what would make you drop the experiment. Without a stopping condition, failed prototypes have a habit of turning into permanent maintenance work.

A five-line note in the issue or PR is usually enough:

```text
Problem: Reproducing a failed payment requires the original author's help.
First attempt: Save one synthetic input and a command to replay it.
Useful result: Another engineer can run it and explain why it failed.
Budget: One afternoon for the first version.
Review: After the next payment change.
Stop if: It needs a private production snapshot to stay useful.
```

Treat that budget as a sketch, not a universal rule. Some problems take an hour; a cross-service migration takes longer.

## Try the billing example

Most of the patterns share a synthetic subscription billing service so you can see how the pieces connect. It handles async payment events, calculates invoices with credits, changes pricing rules, and drags around an old CSV export. The examples stick to ordinary, irritating bugs: duplicate webhook delivery, credit larger than an invoice, copy-pasted test setup, and a rewrite that passes the easy cases while botching the edge cases.

You can run a small piece of it right from this repo using the [billing lab](./examples/README.md):

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
python3 examples/billing_lab.py verify
python3 examples/billing_lab.py compare --candidate buggy
python3 examples/billing_lab.py compare --candidate correct
```

Run them one at a time so you can see the exit codes. Both `--implementation buggy` and `--candidate buggy` are meant to fail; that's how you verify the checks can catch a defect. The buggy webhook handler applies the same event twice, while the fixed one tracks seen event IDs in memory. The buggy invoice calculator lets applied credit exceed the subtotal and drives the balance negative.

The lab is intentionally toy-sized: single-process, in-memory, no tax, no concurrency, no database transactions. It shows the shape of the checks, not how to build a production ledger.

## Keep limits next to the artifact (especially with AI)

A tool outlives its author only if the next person can tell what it actually proves. Put the command, its assumptions, and a sample output right beside the code. Spell out what data is synthetic, what the check catches, and what it leaves uncovered.

This matters twice as much when you work with AI coding agents. Code generation, prototypes, and test scaffolding are cheap now; verifying that you built the right thing is still hard. An agent can happily generate an implementation, a matching test suite, fixtures, and a plausible explanation, all from the same wrong assumption. **Agreement between generated artifacts is not independent evidence of correctness.** Keep the problem statement, boundary examples, and expected results anchored outside the code being tested, and review edits to fixtures and assertions just as skeptically as edits to production logic.

Resist the urge to generalize early. Three readable 40-line scripts are often cheaper to live with than one configurable framework nobody trusts. Extract shared code once real reuse shows you what actually varies.

## Check the upkeep, too

A clean first run proves an idea worked once. Later changes tell you whether it was worth keeping.

Watch what happens when someone else picks it up. Where did they get stuck? Did they silently bypass the tool because it didn't handle refunds? Did updating a fixture take longer than the bug fix itself? The [investment retrospective](./patterns/investment-retrospective.md) gives you a lightweight way to check both individual tools and the combined drag of everything you've accumulated, without pretending rough time estimates are hard science. Simplifying or deleting a tool is a perfectly good outcome.

One more boundary is worth stating plainly: **technical capability alone doesn't guarantee compounding.** If a team frees up 20% of its time and the organization immediately absorbs all of it into higher feature output, the flywheel stalls. Compounding requires reinvesting some of what you save into the next improvement. This field guide focuses on what an engineering team can practice locally without waiting for a reorg. The organizational side (incentives, capability traps, and room to reinvest) is covered in [Organizations that improve with age](https://grove.github.io/engineering-that-compounds/essays/organizations-that-improve-with-age.html).

## About the sources and examples

The pattern names here are editorial handles for established engineering techniques (property testing, Object Mother, differential testing, frozen architecture rules, online migrations), not claims of invention. Every pattern links to primary tools or practitioner write-ups and notes what carries over versus what's specific to a particular stack.

The billing scenarios and retrospective numbers are invented for teaching; they aren't empirical case studies. This collection builds on [Software that improves with age](https://grove.github.io/software-that-improves-with-age/) and [Engineering that compounds](https://grove.github.io/engineering-that-compounds/), though it stands on its own.

