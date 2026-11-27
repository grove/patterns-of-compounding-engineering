# Competing prototypes

*Stop debating two designs on a whiteboard; run both against the same awkward cases.*

A team burns two design meetings arguing over whether billing rules belong in plain application functions or a data-driven rule engine. Both sides have strong advocates and increasingly elaborate diagrams, and nobody has tried adding the next pricing rule to either design.

Build the smallest believable version of each option, put them both through the same uncomfortable cases, and keep the evidence so someone can revisit the decision later without starting the argument from zero.

Save this for genuine forks where running code can settle the question. Skip it when an external contract forces your hand, when the choice is easy to reverse later, or when the real unknown is whether customers want the feature at all. Two technical prototypes will not answer a product question.

## Frame the question before writing code

"Which architecture is cleaner?" leads nowhere. Ask questions tied to work the team has to live with:

- Can we add a backdated plan change without breaking how historical invoices are explained?
- Can the system catch contradictory rules before they hit production?
- Can an engineer who did not write this trace a disputed charge back to the rule that caused it?

Passing tests cannot answer that third question. Someone unfamiliar with the code has to sit down and read it.

In our billing example, say the immediate ask is an effective-dated discount. The team expects more pricing tweaks later, and nobody in finance has asked to edit rules without a deploy. That scopes the experiment right away: a rule-authoring UI stays out of bounds for today's decision.

Write a half-page brief before starting:

```text
Decision: keep explicit pricing functions or introduce a rule table
Question: which makes an effective-dated discount easier to add and explain?

Candidates:
  A. Small refactor of the existing pricing functions
  B. Rules stored as data, evaluated by a generic runner

Shared cases:
  Existing invoice corpus (including credits and a backdated change)
  One new discount checked before, on, and after its effective date
  An explanation naming which rule produced each invoice line

Timebox: one day
Out of scope: config UI, production rollout, migrating old invoices
Stop when: the hard cases expose a clear difference, or the day ends
```

Scale the timebox to the stakes: an afternoon for picking a helper library, a few days for a cross-service boundary.

## Run a fair comparison

Give both prototypes the same interface: account state, proposed change, and effective date go in; invoice lines and explanations come out. Keep network calls, database writes, and ambient clocks outside the comparison.

Feed both designs cases that hurt. Include at least one ugly synthetic case drawn from a real past incident, since clean happy-path invoices make almost any architecture look good. Run the current production implementation alongside them when it is relevant, and check both candidates against your [executable invariants](./executable-invariants.md) so neither inherits an old bug unchallenged.

Then try making the *next* change in both prototypes and notice where the friction lands. Did the rule table suddenly need a precedence mechanism to resolve overlapping discounts? Did the explicit functions make it clumsy to generate a line-by-line explanation?

Watch out for two traps that skew short spikes. First, people polish the option they already favor, and someone who knows the existing codebase moves faster in it. Note uneven familiarity honestly instead of mistaking it for long-term cost. Second, short prototypes flatter designs with low upfront cost over designs with better long-term economics. A quick hack almost always wins a one-day race against a cleaner model unless you test a realistic follow-up change, like adding a second overlapping rule or debugging an unexpected output.

## Keep "do less" on the table

Sometimes the comparison points to a smaller move than either camp expected. Maybe the rule table handles the new discount cleanly and immediately needs priority ordering and conflict validation, while plain functions stay local, readable, and easy for support to trace.

Picking plain functions for today means you wait until rule count or non-engineering authoring justifies the extra machinery. Keep the overlap cases you discovered so they are ready if that day arrives. Whenever "handle it manually for now" is a real option, include it honestly along with the operational work and error risk it puts on whoever has to run it.

## Leave a decision trail

Save the shared test cases, expected outputs, commit hashes, run commands, and a short note explaining why you chose one option, what you rejected, and what condition should trigger revisiting the call:

```text
Chosen: explicit pricing functions for the effective-dated discount
Rejected: generic rule table (needed precedence and conflict validation immediately)
Why: changes stayed local and invoice explanations were easy to follow

Unresolved: non-engineer editing, large overlapping rule sets
Revisit if: business staff need to author pricing rules directly, or rule count exceeds ~15
Evidence: shared corpus, both prototypes, notes from the trace exercise
Status: experiment only; neither prototype is a supported API
```

Keep prototype code clearly separated from production code. When keeping both prototypes runnable as dependencies move becomes expensive, keep the commit references, test cases, and decision note rather than promising to maintain dead spikes forever.

Simon Willison's [Hoard things you know how to do](https://simonwillison.net/guides/agentic-engineering-patterns/hoard-things-you-know-how-to-do/) makes a strong case for keeping working small experiments around to combine later. On a team, the crucial addition is a clear label on each experiment: what it proved, under what assumptions, and what it deliberately left untouched.

## Know when to stop

A prototype can expose an awkward data model or a missing input, yet it will not prove production scalability or failure recovery just because the happy path ran. When load or migration safety is the deciding factor, include the smallest credible test of that concern before choosing, or mark it unresolved and budget for it explicitly.

Stop once extra work stops changing the decision. You rarely need a third prototype unless the first two uncovered a brand-new question neither can answer.

## How it connects and sources

Competing prototypes are much cheaper to run when [scenario builders](./scenario-builders.md) and [executable invariants](./executable-invariants.md) already exist to supply the shared cases and verify both options. Even the discarded prototype earns its keep when those shared cases later feed [differential verification](./differential-verification.md) or save someone from re-running the same debate next year. Check whether kept spikes are still earning their upkeep in an [investment retrospective](./investment-retrospective.md).

- Ryan Singer, [Find the Elements](https://basecamp.com/shapeup/1.3-chapter-04) (*Shape Up*): sketching alternative approaches at low fidelity when writing code too early slows exploration down.
- Martin Fowler, [Sacrificial Architecture](https://martinfowler.com/bliki/SacrificialArchitecture.html): why deliberately temporary software still needs enough internal clarity to teach you something real.
