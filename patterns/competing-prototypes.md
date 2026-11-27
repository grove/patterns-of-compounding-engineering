# Competing prototypes

*Use the same awkward cases to put two plausible designs to work.*

A team has spent two design meetings discussing whether billing rules belong in ordinary application code or a configurable rule engine. Each approach has an advocate. The diagrams are getting more detailed, but nobody has tried adding the next rule to either design.

This is a good time for competing prototypes. Choose a question that could change the decision, build the smallest credible versions of two alternatives, and evaluate them against the same cases. Keep the evidence that another engineer could use to revisit the choice.

Use this pattern when there are plausible alternatives and an unresolved question that running code can answer. Skip it when a contract already determines the implementation, the change is easy to reverse, or the uncertainty concerns what customers need. Two technical prototypes will not tell you whether anyone wants the feature.

## Choose the question before the designs

“Which architecture is better?” is too broad. A useful question names the work the design must support:

- Can we add a backdated plan change without changing how historical invoices are explained?
- Can the implementation reject contradictory rules at configuration time?
- Can someone unfamiliar with the code find the rule responsible for a disputed charge?

The last question needs a person trying the task. Passing a test suite cannot answer it.

For the fictional subscription service used in this guide, suppose the immediate request is a new discount with an effective date. The team expects further pricing changes but has no evidence that business staff need to configure rules themselves. That distinction matters. A configuration interface brings work that may be irrelevant to the current decision.

Write a short brief before building. This is an illustrative brief for that service:

```text
Decision: keep explicit pricing functions or introduce a rule table
Question: which makes an effective-dated discount easier to add and explain?

Candidates:
  A. A small refactor of the current pricing functions
  B. Rules stored as data, evaluated by a separate function

Shared evidence:
  Existing invoice cases, including credits and a backdated change
  One new discount applied before, on and after its effective date
  An explanation identifying the rule behind each invoice line

Budget: one working day for the comparison
Excluded: configuration UI, production rollout, migration of old invoices
Stop when: the hard cases expose a relevant difference, or time runs out
```

That budget is a choice for this example. A decision affecting several services may justify more work; choosing a helper library may justify less.

## Give the alternatives a fair test

Use a shared boundary: the same account state, proposed change and effective time go in; invoice lines and their explanations come out. Use integer minor units for amounts and explicit dates. Keep network calls and writes outside the comparison.

Start with cases whose expected behavior the team understands. Include one uncomfortable case from a real investigation if you have permission to turn it into synthetic test data. A tidy set of ordinary invoices will flatter both designs.

Run the current implementation as a reference where it is relevant. Differences need explanation: an existing result may be wrong, and matching it is not sufficient evidence of correctness. The checks in [Executable invariants](./executable-invariants.md) help establish which obligations both candidates must meet.

Then make the proposed change in both implementations. Inspect the work it actually requires. Did the rule table need a new exception to its evaluator? Did the explicit functions make it difficult to explain which discount won? Can either representation describe the effective date without hiding it in a default?

Avoid spending the whole budget polishing the favored option. Record uneven familiarity and unfinished work. If one person knows the existing approach well and is learning the alternative, the first attempt measures that difference too. It can still reveal useful constraints, but it does not establish the alternative's long-term cost.

## Include the option of doing less

Sometimes the comparison exposes a smaller decision. In this fictional case, imagine the rule table handles the new discount neatly but needs evaluation priorities to resolve overlapping discounts. The explicit functions are less general, yet the next rule requires only a localized change and produces an explanation the support team can follow.

The team can choose the smaller change and retain the cases about overlap. It has learned something specific: configuration will become more attractive if rules are numerous enough to justify validation and priority management. It has not demonstrated that rule engines are bad.

Also consider whether the offer could be handled through an existing adjustment process while demand becomes clearer. Include the work and errors this would create for the people using that process. “Do nothing” is rarely free, but it belongs in the comparison when it is a credible option.

## Keep an experiment that can be understood later

Retain the input cases, expected results, source revision, run instructions and a short decision note. Record the limits beside the result:

```text
Chosen: explicit pricing functions for the effective-dated discount
Reason: the required change stayed local; invoice explanations remained clear

Unresolved: editing rules without deployment; large rule sets
Revisit if: people outside engineering need to maintain pricing rules
Evidence: shared cases, both implementations, notes from the explanation task
Status: experiment only; neither implementation is a supported billing API
```

In your repository, link the decision note to the commits and commands that support it.

Keep the experiment separate from supported production code. Someone should be able to tell whether it still runs, what environment it needs, and whether a changed dependency invalidates the result. If maintaining both prototypes would be expensive, preserve the relevant source revision and the evidence instead of promising that both remain runnable forever.

Simon Willison describes collecting working demonstrations and later combining them into new work in [Hoard things you know how to do](https://simonwillison.net/guides/agentic-engineering-patterns/hoard-things-you-know-how-to-do/). For a team, the useful addition is a boundary around each demonstration: what it established, under which conditions, and what it left unanswered.

## Know what the result can support

A prototype can expose a missing input or an awkward rule representation. It cannot demonstrate production reliability simply because the happy path ran. If the decision depends on migration, load or failure recovery, include the smallest credible exercise of that concern before choosing. Otherwise mark it unresolved and budget for it.

Stop when further work is unlikely to change the choice. A third prototype needs a specific question that the first two left open. Check that the alternatives differ in the assumption being examined; changing the implementation language alone may teach you very little about the design.

The retained cases may later support [Differential verification](./differential-verification.md), and the discarded approach may answer a future feasibility question. Count that as a benefit when it happens. Until then, the experiment has earned its keep if it improved this decision at an acceptable cost.

## Sources and related patterns

- Ryan Singer's [Find the Elements](https://basecamp.com/shapeup/1.3-chapter-04), in *Shape Up*, describes exploring alternative flows at a deliberately limited level of detail. It is a useful companion when code would make the exploration slower.
- Martin Fowler's [Sacrificial Architecture](https://martinfowler.com/bliki/SacrificialArchitecture.html) explains why useful software can be deliberately temporary, while still needing care in its internal structure.
- [Investment retrospective](./investment-retrospective.md) provides a way to revisit the cost of maintaining experiments after the original decision.
