# Patterns of compounding engineering

*A practical field guide to recurring software problems*

A team fixes a duplicate payment, replaces a calculation, or removes an old export. Some of that work can make the next change easier: a reproducible failure, a trusted comparison, a way to find the remaining consumers. Keeping those things has a cost. This guide is about choosing what is worth keeping and making it usable by someone else.

The collection follows [Software that improves with age](https://grove.github.io/software-that-improves-with-age/) and [Engineering that compounds](https://grove.github.io/engineering-that-compounds/). It puts their arguments to work through practical patterns, with examples, adoption steps, limits and sources.

**Website address:** [grove.github.io/patterns-of-compounding-engineering](https://grove.github.io/patterns-of-compounding-engineering/)

Have a task open already? Start with [a small loop for everyday work](./guide.md#use-the-task-already-open), then [walk a duplicate-payment fix through it](./guide.md#walk-one-fix-through-the-loop). For a particular recurring problem, choose a pattern below.

Working toward a larger change? See how the patterns can help you [replace a difficult subsystem](./guide.md#make-a-difficult-subsystem-replaceable), [reduce recurring review work](./guide.md#reduce-recurring-review-work), or [delegate one kind of task](./guide.md#delegate-one-kind-of-task). Each route explains when to stop adding machinery. To choose an investment, try [the tenfold exercise](./guide.md#use-the-tenfold-ambition-to-choose-the-next-investment): use the Theory of Constraints to identify what limits a worthwhile outcome before deciding which pattern deserves the effort.

If the same difficulty keeps returning, [use AI to help investigate why](./guide.md#use-ai-to-investigate-recurring-friction). Follow one question from the original evidence to a small experiment, then check whether later work benefits. Start with [capability composition](./patterns/capability-composition.md) when existing checks might make a new kind of work practical. The [investment canvas](https://grove.github.io/compounding-engineering/adoption/investment-canvas.html) helps a team choose one bounded attempt.

For a change to the workflow itself, [investigate a recurring intervention](./patterns/recurring-intervention.md) or [retire a workaround](./patterns/retire-the-workaround.md) after its original constraint has gone. [Paths towards 10×](https://grove.github.io/compounding-engineering/paths/) shows how such choices can connect across several investments.

## Understand the work and check behavior

1. **[Persistent reproducer](./patterns/persistent-reproducer.md)** — Keep the sequence, inputs and expected result that made a difficult bug understandable.
2. **[Incident to instrument](./patterns/incident-to-instrument.md)** — Turn a hard production investigation into permanent telemetry that exposes the same failure class early.
3. **[Successful work investigation](./patterns/successful-work-investigation.md)** — Examine the information, adjustments and options that helped ordinary work succeed.
4. **[Scenario builders](./patterns/scenario-builders.md)** — Make meaningful business states cheap to construct, with time and defaults under control.
5. **[Reusable domain scenarios](./patterns/reusable-domain-scenarios.md)** — Keep reviewed situations, their evidence and their limits usable across product and engineering.
6. **[Executable invariants](./patterns/executable-invariants.md)** — State the guarantees the business needs and check them across many inputs.
7. **[Differential verification](./patterns/differential-verification.md)** — Compare old and new behavior on the same inputs, then investigate the differences.

## Make changes easier to carry out

8. **[Architectural ratchet](./patterns/architectural-ratchet.md)** — Record existing violations precisely and stop new ones while making room for gradual repair.
9. **[Review comment to guardrail](./patterns/review-comment-to-guardrail.md)** — Turn one agreed, detectable mistake into a check with a useful explanation.
10. **[Capability command](./patterns/capability-command.md)** — Package a useful engineering task so someone else can run it safely and understand the result.
11. **[Verified retrieval](./patterns/verified-retrieval.md)** — Rehearse a task with fresh context and check whether current knowledge changes the plan or result.
12. **[Investigation to skill](./patterns/investigation-to-skill.md)** — Retain a successful method, then try it on a different task with a different answer.
13. **[Earned delegation](./patterns/earned-delegation.md)** — Find and repair the missing evidence or safeguard before widening a task's delegation boundary.
14. **[Capability composition](./patterns/capability-composition.md)** — Combine a few proven capabilities to answer a new question, and count the cost of joining them.

## Choose what deserves the effort

15. **[Friction to hypothesis](./patterns/friction-to-hypothesis.md)** — Test competing explanations for recurring friction before choosing a repair.
16. **[Investigate the recurring intervention](./patterns/recurring-intervention.md)** — Decide whether a recurring stop needs better evidence, a different design or a human decision.
17. **[Shorten the learning loop](./patterns/shorten-the-learning-loop.md)** — Reduce the delay around a consequential question while keeping the evidence trustworthy.
18. **[Competing prototypes](./patterns/competing-prototypes.md)** — Compare a few small implementations against the same question before committing.
19. **[Subtraction investigation](./patterns/subtraction-investigation.md)** — Trace obligations and usage, rehearse removal, and name the evidence needed to delete.
20. **[Retire the workaround](./patterns/retire-the-workaround.md)** — Check which duties remain before retiring a booking, approval or coordination step.
21. **[Investment retrospective](./patterns/investment-retrospective.md)** — Follow an investment into later work, including the time spent maintaining and teaching it.

## Apply a skill

The [experimental skill collection](./skills/README.md) contains three small procedures you can read yourself or give to a compatible coding agent. Try the compounding pass after a change, use subtraction investigation before a proposed removal, or review a technical example. Start with one real task and check the outcome.

## Run the example

The [billing lab](./examples/README.md) uses Python 3.10 or later and the standard library. All data is synthetic. It makes no network requests and changes no external state.

```sh
python3 examples/billing_lab.py replay
python3 examples/billing_lab.py verify
python3 examples/billing_lab.py compare
```

The lab includes deliberately buggy implementations. Its documentation explains how to run them and why those commands should fail. It is a small teaching example, with no tax, currency conversion, durable storage or concurrent processing.

The [evolving billing lab](./examples/evolving-billing/README.md) follows the same failure through restarts, interrupted writes, a replacement implementation and a changed payment-identity rule. Try a prediction before each command, then inspect which earlier checks still help and which assumptions need revisiting.

## Build and check

No package installation is required.

```sh
python3 -m unittest discover -s tests -v
python3 site/build.py --check
python3 -m http.server --directory _site 8000
```

Open [localhost:8000](http://localhost:8000). Generated files stay in `_site/` and are not committed. The site uses the Nordic Crisp palette, adapts to light and dark preferences, and remains readable without JavaScript.

The [publishing and editing guide](./CONTRIBUTING.md) covers the GitHub Pages setting, workflow and how to add an entry. Pull requests build a downloadable preview. Publication runs after a merge to `main`.

## Sources and license

The pattern names are editorial groupings of established techniques and proposed practices. Sources describe their relevance; the fictional billing examples are not reports of measured industry results. AI can help implement or explore a pattern, but none requires an agent.

The Markdown renderer and part of the build validation derive from the companion collections. See [NOTICE](./NOTICE) for attribution. Licensed under [Apache 2.0](./LICENSE).

