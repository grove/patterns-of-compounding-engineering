# Competing prototypes

*Stop debating two designs on a whiteboard; run both against the same awkward cases.*

A team burns two design meetings arguing over whether billing rules belong in plain application functions or a data-driven rule engine. Both sides have eloquent advocates and increasingly ornate diagrams, and nobody has actually tried adding the next pricing rule to either design.

Build the smallest believable version of each option, put them both through the exact same uncomfortable cases, and keep the evidence so someone can revisit the decision later without starting the argument from zero.

Save this for genuine forks where running code can settle the question. Skip it when an external contract forces your hand, when the choice is trivial to reverse later, or when the real unknown is whether customers want the feature at all. Two technical prototypes won't answer a product question.

## Frame the question before writing code

"Which architecture is cleaner?" leads nowhere. Ask questions tied to work the team actually has to live with:

- Can we add a backdated plan change without breaking how historical invoices are explained?
- Can the system catch contradictory rules before they hit production?
- Can an engineer who didn't write this trace a disputed charge back to the rule that caused it?

Passing tests can't answer that third question; someone unfamiliar with the code has to sit down and try to read it.

In our billing example, say the immediate ask is an effective-dated discount. The team expects more pricing tweaks later, but nobody in finance has asked to edit rules without a deploy. That scopes the experiment immediately: a rule-authoring UI is out of bounds for today's decision.

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

Feed both designs cases that actually hurt. Include at least one ugly synthetic case drawn from a real past incident; clean happy-path invoices make almost any architecture look good. Run the current production implementation alongside them if it's relevant, while checking both candidates against your [executable invariants](./executable-invariants.md) so neither inherits an old bug unchallenged.

Then try making the *next* change in both prototypes and pay attention to where the friction lands. Did the rule table suddenly need a precedence mechanism to resolve overlapping discounts? Did the explicit functions make it ugly to generate a line-by-line explanation?

Watch out for two traps that skew short spikes. First, people naturally polish the option they already favor, and someone who already knows the existing codebase will always move faster in it. Note uneven familiarity honestly rather than mistaking it for long-term cost. Second, **short prototypes flatter designs with low upfront cost over designs with better long-term economics.** A quick hack almost always wins a one-day race against a cleaner model unless you deliberately test a realistic follow-up change (like adding a second overlapping rule or debugging an unexpected output).

## Keep "do less" on the table

Sometimes the comparison points to a smaller move than either camp expected. Maybe the rule table handles the new discount cleanly but immediately needs priority ordering and conflict validation, while plain functions stay local, readable, and easy for support to trace.

Choosing plain functions doesn't prove rule engines are bad; it proves you don't need one until rule count or non-engineering authoring actually justifies the extra complexity. Keep the overlap cases you discovered so you have them ready if that day comes. And whenever "handle it manually for now" is a real option, include it honestly along with the operational work and error risk it dumps on whoever has to run it.

## Leave a decision trail, not two live codebases

Save the shared test cases, expected outputs, commit hashes, run commands, and a short note explaining the call and what would flip it:

```text
Chosen: explicit pricing functions for the effective-dated discount
Why: changes stayed local and invoice explanations were easy to follow

Unresolved: non-engineer editing, large overlapping rule sets
Revisit if: business staff need to author pricing rules directly
Evidence: shared corpus, both prototypes, notes from the trace exercise
Status: experiment only; neither prototype is a supported API
```

Keep prototype code clearly separated from production code. If keeping both prototypes runnable as dependencies move is expensive, preserve the commit references, test cases, and decision note instead of promising to maintain dead spikes forever.

Simon Willison's [Hoard things you know how to do](https://simonwillison.net/guides/agentic-engineering-patterns/hoard-things-you-know-how-to-do/) makes a great case for keeping working small experiments around to combine later. On a team, the crucial addition is a clear label on each experiment: what it proved, under what assumptions, and what it deliberately left untouched.

## Know when to stop

A prototype can expose an awkward data model or a missing input; it won't prove production scalability or failure recovery just because the happy path ran. If load or migration safety is the real deciding factor, include the smallest credible test of that concern before choosing, or mark it unresolved and budget for it explicitly.

Stop once extra work stops changing the decision. You rarely need a third prototype unless the first two uncovered a brand-new question neither can answer. Even the discarded prototype earns its keep if the shared cases later feed [differential verification](./differential-verification.md) or save someone from re-running the same debate next year.

## Sources and related patterns

- Ryan Singer, [Find the Elements](https://basecamp.com/shapeup/1.3-chapter-04) (*Shape Up*): sketching alternative approaches at low fidelity when writing code too early slows exploration down.
- Martin Fowler, [Sacrificial Architecture](https://martinfowler.com/bliki/SacrificialArchitecture.html): why deliberately temporary software still needs enough internal clarity to teach you something real.
- [Investment retrospective](./investment-retrospective.md): checking whether kept experiments and spikes are still worth maintaining after the original decision.
