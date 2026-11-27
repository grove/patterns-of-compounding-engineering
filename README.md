# Patterns of compounding engineering

*A practical field guide to recurring software problems*

A team fixes a duplicate payment, replaces a calculation, or removes an old export. Some of that work can make the next change easier: a reproducible failure, a trusted comparison, a way to find the remaining consumers. Keeping those things has a cost. This guide is about choosing what is worth keeping and making it usable by someone else.

The collection follows [Software that improves with age](https://grove.github.io/software-that-improves-with-age/) and [Engineering that compounds](https://grove.github.io/engineering-that-compounds/). It puts their arguments to work through fourteen patterns, with examples, adoption steps, limits and sources.

**Website address:** [grove.github.io/patterns-of-compounding-engineering](https://grove.github.io/patterns-of-compounding-engineering/)

Have a task open already? Start with [a small loop for everyday work](./guide.md#use-the-task-already-open), then [walk a duplicate-payment fix through it](./guide.md#walk-one-fix-through-the-loop). For a particular recurring problem, choose a pattern below.

## Understand failures and check behavior

1. **[Persistent reproducer](./patterns/persistent-reproducer.md)** — Keep the inputs and sequence that made a difficult failure understandable.
2. **[Incident to instrument](./patterns/incident-to-instrument.md)** — Leave production able to answer the question that held up the last investigation.
3. **[Scenario builders](./patterns/scenario-builders.md)** — Make meaningful business states cheap to construct.
4. **[Executable invariants](./patterns/executable-invariants.md)** — Check the guarantees the business needs across many inputs.
5. **[Differential verification](./patterns/differential-verification.md)** — Compare old and new implementations, then investigate their disagreements.

## Make changes easier to carry out

6. **[Architectural ratchet](./patterns/architectural-ratchet.md)** — Stop new dependency violations while repairing existing ones.
7. **[Review comment to guardrail](./patterns/review-comment-to-guardrail.md)** — Turn an agreed, detectable mistake into a useful automated check.
8. **[Capability command](./patterns/capability-command.md)** — Package an investigation so someone else can run it safely.
9. **[Verified retrieval](./patterns/verified-retrieval.md)** — Check whether a fresh attempt finds the relevant knowledge and uses it within its limits.

10. **[Investigation to skill](./patterns/investigation-to-skill.md)** — Keep a useful investigative method and try it on a different problem.
11. **[Earned delegation](./patterns/earned-delegation.md)** — Turn repeated supervision into evidence about what the environment needs next.

## Choose what deserves the effort

12. **[Competing prototypes](./patterns/competing-prototypes.md)** — Answer a design question with a few small implementations.
13. **[Subtraction investigation](./patterns/subtraction-investigation.md)** — Gather the evidence needed to remove a piece of software.
14. **[Investment retrospective](./patterns/investment-retrospective.md)** — Find out whether a retained tool helped subsequent work.

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

