# Using the guide

*Pick one real point of friction, keep only what earns its upkeep, and see what becomes easier next.*

Most messy debugging sessions leave useful scraps behind: a replay script in `/tmp`, a few weird test payloads, a SQL query that finally exposed the broken rows. Some of those scraps belong in the repository. Plenty of them do not, because keeping them working as schemas and libraries move turns into a second job nobody signed up for.

This guide is about making that call and shaping the things you keep so a teammate can actually use them without pinging you on Slack. None of the patterns require a platform team or a quarterly roadmap item. You can try one on a Tuesday afternoon inside the codebase you already have.

## Start with something that already hurt

Pick a real task that recently burned an afternoon. Maybe the last two billing bugs forced someone to rebuild the same broken subscription state by hand. Maybe a 2 a.m. timeout left on-call grepping raw container logs for an hour. Maybe reviewers keep leaving the same comment about billing handlers importing the payment SDK directly. Write down what happened, where the time went, and who got stuck.

"We need better developer experience" can justify almost anything and proves nothing later. "A new engineer cannot reproduce the duplicate-payment bug without pulling the original author into a call" gives you something concrete to test against.

Before you automate or wrap a recurring chore, check whether you can just eliminate it. If someone runs a repair script every Monday because a webhook handler drops idempotency keys, fix the handler instead of putting a nicer CLI on the repair script.

When the underlying work is staying around, jump straight to the pattern closest to your problem:

- [Reproduce a hard failure](./patterns/persistent-reproducer.md), [instrument a production blind spot](./patterns/incident-to-instrument.md), [build awkward states cheaply](./patterns/scenario-builders.md), [check business guarantees](./patterns/executable-invariants.md), or [compare a replacement against legacy code](./patterns/differential-verification.md).
- [Contain a dependency mess](./patterns/architectural-ratchet.md), [turn a repeated review catch into a check](./patterns/review-comment-to-guardrail.md), or [package an investigation so someone else can run it](./patterns/capability-command.md).
- [Test competing designs on real cases](./patterns/competing-prototypes.md), [gather evidence before deleting old code](./patterns/subtraction-investigation.md), or [check whether an earlier tool paid off](./patterns/investment-retrospective.md).

## Reuse is not compounding

Keeping more scripts and tests does not automatically make a team faster. When you retain an engineering artifact, it usually ends up in one of four places:

| Outcome | What it looks like |
| --- | --- |
| Accumulation | A pile of brittle regression tests that protects past fixes while dragging down every schema change |
| Recurring return | A replay command that saves an hour whenever a payment bug comes back |
| Compounding | A scenario builder written for one incident that later makes invariant tests and a migration comparator cheap to build |
| Negative compounding | Fragile helper scripts whose upkeep costs more than they save, until people route around them or avoid touching the module |

Recurring returns are completely fine; plenty of useful tools stop there and still earn their keep. Actual compounding is rarer, and the sharpest test for it is not "did this save time?" It is: **what becomes practical after this investment that was too slow or too risky before?**

That usually happens across a short chain of capabilities rather than inside a single tool:

- **From one bad incident to deleting old code:** Capture a repeatable logic bug as a [persistent reproducer](./patterns/persistent-reproducer.md), or turn an unrepeatable production outage into durable telemetry with [incident to instrument](./patterns/incident-to-instrument.md). Once a few cases repeat the same setup boilerplate, pull out [scenario builders](./patterns/scenario-builders.md). Feed those builders into [executable invariants](./patterns/executable-invariants.md), reuse the same corpus for [differential verification](./patterns/differential-verification.md) when you replace the old calculator, and use a [subtraction investigation](./patterns/subtraction-investigation.md) to delete the legacy path cleanly.
- **From noisy reviews to steady cleanup:** Turn a repeated review correction into a [review comment to guardrail](./patterns/review-comment-to-guardrail.md). Freeze legacy violations with an [architectural ratchet](./patterns/architectural-ratchet.md) so you can ship while cleaning up. Put the checks behind a [capability command](./patterns/capability-command.md) that runs identically locally and in CI, and check whether the setup still pays rent in an [investment retrospective](./patterns/investment-retrospective.md).

Stop walking a chain as soon as the next piece stops paying for itself.

## How patterns reinforce and pull against each other

These patterns do not always point in the same direction. Some stack cleanly; others create real tension you have to manage on purpose.

| Pattern pair | How they interact |
| --- | --- |
| [Scenario builders](./patterns/scenario-builders.md) + [Executable invariants](./patterns/executable-invariants.md) | Reinforce each other, with a catch: defaults baked into builders can silently shrink what your invariants actually test |
| [Persistent reproducer](./patterns/persistent-reproducer.md) + [Incident to instrument](./patterns/incident-to-instrument.md) | Complementary sides of failure debugging: replay deterministic bugs locally, instrument emergent production failures |
| [Executable invariants](./patterns/executable-invariants.md) + [Differential verification](./patterns/differential-verification.md) | Invariants stop a migration comparator from blindly treating legacy bugs as expected behavior |
| [Review comment to guardrail](./patterns/review-comment-to-guardrail.md) + [Architectural ratchet](./patterns/architectural-ratchet.md) | Ratchets make strict rules adoptable in messy codebases without blocking releases |
| [Differential verification](./patterns/differential-verification.md) + [Subtraction investigation](./patterns/subtraction-investigation.md) | Proving a replacement covers real cases clears the main blocker to deleting old code |
| [Architectural ratchet](./patterns/architectural-ratchet.md) vs. [Competing prototypes](./patterns/competing-prototypes.md) | Real tension: ratchets lock existing boundaries down, while spikes sometimes need to cross them to test a new shape |
| [Capability command](./patterns/capability-command.md) / [Guardrails](./patterns/review-comment-to-guardrail.md) vs. human understanding | Making checks effortless can hide how the system works unless failure output and walkthroughs keep the mental model visible |

## Choosing between competing investments

Teams rarely run out of ideas for internal tooling; they run out of time. Say you have two days and four real candidates: cleaner billing fixtures, better webhook telemetry, a custom lint rule, or deleting a legacy CSV export.

Skip weighted scoring spreadsheets and ask five plain questions:

- **What does it unlock?** Does this make a risky upcoming change (like a rewrite or deletion) practical? A comparator you only run for one quarter can beat a daily convenience script if it unblocks replacing a tangled module.
- **How often does the pain hit?** Frequent friction usually wins, unless you are about to polish a workaround for a bug you should just fix.
- **Who benefits?** Does this speed up one person's terminal workflow, or does it unblock newcomers, code reviewers, on-call, and CI?
- **How fast will it go stale?** Assumptions expire. A fixture suite welded to a billing model you plan to retire next quarter has a short shelf life.
- **What is the carrying cost?** What breaks when schemas, dependencies, or product rules shift? A built-in ESLint rule costs almost nothing to own compared to a bespoke test harness.

Teams usually misjudge the first and last ones: they over-invest in frequent minor annoyances and under-invest in the one capability that makes an upcoming structural change safe, while forgetting that every helper has to be fed every time the domain moves.

## Keep the first version small

Solve the case sitting in front of you before generalizing. Keep one incident reproducible before designing an event-replay framework. Add one narrow lint rule before drafting a company policy. Investigate one legacy export before pitching a platform cleanup.

Put a time cap on the first cut (an afternoon for a reproducer, a day or two for a migration comparator) and write down what would make you drop it. Half-built internal tools have a habit of hanging around for years if nobody names a stopping point.

A six-line note in the issue or pull request is enough, and it also makes a half-day investment easy to explain to a manager or product lead when you fold it into feature work:

```text
Problem: Reproducing a failed payment requires the original author's help.
First attempt: Save one synthetic input and a command to replay it.
Unlocks: Any engineer can test webhook changes safely without live staging setup.
Budget: One afternoon for the first version.
Review: After the next payment change.
Stop if: It needs a private production snapshot to stay useful.
```

Scale the budget to the stakes. Some checks take an hour; a cross-service migration takes days.

## Try the billing example

Most of the patterns share a synthetic subscription billing service so you can see how the pieces fit together. It handles async payment events, calculates invoices with credits, deals with pricing changes, and drags around an old CSV export. The bugs are ordinary ones: duplicate webhook delivery, credit larger than an invoice, copy-pasted test setup, a 2 a.m. lock timeout, and a rewrite that passes happy paths while botching the edges.

You can run a small piece of it locally from this repository using the [billing lab](./examples/README.md):

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
python3 examples/billing_lab.py verify
python3 examples/billing_lab.py compare --candidate buggy
python3 examples/billing_lab.py compare --candidate correct
```

Run them one at a time so you can see the exit codes. Both `--implementation buggy` and `--candidate buggy` are supposed to fail, because a check you have never watched fail is hard to trust. The buggy webhook handler applies the same event twice, while the fixed one tracks seen event IDs in memory. The buggy invoice calculator lets applied credit exceed the subtotal and drives the balance negative.

The lab is deliberately toy-sized: single-process, in-memory, no tax, no concurrency, no database transactions. It shows the shape of the checks, not a production ledger.

## Keep evidence independent (especially with AI)

A retained tool only outlives its author if the next person can tell what it actually proves. Put the command, its assumptions, and sample output beside the code, and be plain about what data is synthetic, what the check catches, and what it leaves uncovered.

Coding agents make generating implementation code and test scaffolding cheap, which pushes the bottleneck onto verification and comprehension. When you already have solid reproducers, invariants, and comparison corpora, cheaper implementation lets you delegate more safely and spend the saved time on harder improvements. When you do not, cheaper code generation mostly yields more code, more tests that mirror the code, and a heavier review burden with less understanding of how the system behaves.

Watch closely for shared assumptions. An agent can generate an implementation, a matching test suite, fixtures, and a confident explanation from the exact same bug. Two generated artifacts agreeing with each other is not independent proof of correctness. Keep the problem statement, boundary cases, and expected outcomes anchored outside the code under test, and read diffs to fixtures and assertions with the same skepticism you give production code.

Do not generalize early either. Three plain 40-line scripts are almost always easier to live with (and easier to delete) than one configurable framework nobody trusts. Extract shared code once real reuse shows you what actually varies.

## Check upkeep, and know where this guide stops

A clean first run only tells you an idea worked once. The next two or three real changes tell you whether it was worth keeping.

Watch someone else pick the tool up. Notice where they pause, whether they bypassed it because it did not cover refunds, or whether fixing a fixture took longer than the bug fix itself. The [investment retrospective](./patterns/investment-retrospective.md) gives you a lightweight way to check both individual tools and the combined drag of everything you have accumulated, without pretending rough numbers are hard science. Deleting a tool that stopped earning its keep is a good day's work.

One deliberate boundary: this guide covers code, tests, telemetry, and local workflows an engineering team controls directly. It is not a continuous-delivery handbook or an org-design book. Technical tools alone cannot force compounding; if a team frees up 20% of its capacity and the organization immediately absorbs all of it into feature throughput, nothing gets reinvested. The organizational half (incentives, capability traps, and room to reinvest) lives in [Organizations that improve with age](https://grove.github.io/engineering-that-compounds/essays/organizations-that-improve-with-age.html).

## About the sources and examples

The pattern names are editorial handles for established techniques (property testing, Object Mother, differential testing, frozen architecture rules, structured observability, online migrations) rather than claims of invention. Every pattern links to primary tools or practitioner write-ups and separates what generalizes from what belongs to a specific stack.

The billing scenarios and retrospective tables are invented for teaching, not empirical case studies. This collection builds on [Software that improves with age](https://grove.github.io/software-that-improves-with-age/) and [Engineering that compounds](https://grove.github.io/engineering-that-compounds/), though it is meant to stand on its own.

