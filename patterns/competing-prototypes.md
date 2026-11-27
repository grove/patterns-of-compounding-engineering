# Competing prototypes

*Stop debating two designs on a whiteboard; run both against the same awkward cases.*

A team burns two design meetings arguing over whether billing rules belong in plain application functions or a data-driven rule engine. Both sides have strong advocates and increasingly neat diagrams, and nobody has tried adding the next pricing rule to either design.

Build the smallest believable version of each option, put both through the same uncomfortable cases, and keep the evidence so someone can revisit the call next year without starting the argument from scratch.

Save this for genuine forks where running code can settle the question. Skip it when an external contract forces your hand, when the choice is cheap to reverse later, or when the real unknown is whether customers want the feature at all. Two technical prototypes will not answer a product question.

## Frame a concrete question first

"Which architecture is cleaner?" goes in circles. Ask questions tied to work the team actually has to live with:

- Can we add a backdated plan change without breaking how historical invoices are explained?
- Can the system catch contradictory rules before they hit production?
- Can an engineer who did not write this trace a disputed charge back to the rule that produced it?

Notice that tests alone cannot answer that third question; someone who was not in the design meeting has to read the code and try tracing a charge.

In our billing service, say the immediate ask is an effective-dated discount. The team expects more pricing tweaks later, and nobody in finance has asked to edit rules without a deploy. That keeps a rule-authoring UI out of scope for today's decision.

Write a half-page brief before opening an editor:

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

Feed both designs cases that hurt. Include at least one ugly synthetic case drawn from a real past incident, because happy-path invoices make almost any architecture look clean. Run the current production implementation alongside them when it applies, and check both candidates against your [executable invariants](./executable-invariants.md) so neither quietly inherits an old bug.

Then try making the *next* change in both prototypes and see where the friction lands. Did the rule table suddenly need priority ordering and conflict validation to handle overlapping discounts? Did the explicit functions make it clumsy to produce a line-by-line explanation?

Watch out for two biases that skew short spikes. First, people polish the option they already prefer, and whoever knows the existing codebase moves faster in it; note uneven familiarity honestly instead of mistaking it for long-term cost. Second, short timeboxes flatter designs with low upfront setup over designs with better long-term economics. A quick hack almost always wins a one-day race against a cleaner model unless you test a realistic follow-up change, like adding a second overlapping rule or debugging an unexpected output.

## Run investigations separately, decide together

If the alternatives really are independent, give each investigator the same brief, reviewed cases and timebox, and a separate checkout and test state. Keep the evidence and failures visible until the comparison. Ask each to return its assumptions, results, costs and unresolved questions rather than competing to be the first with a green test.

It is often easier to parallelize research than implementation. Two people can independently investigate a design without merging conflicting patches. Where their findings disagree, settle the shared contract before committing either design. Agreement between agents that share a prompt or mistaken requirement is not independent evidence.

When integrating changes, rerun the cross-boundary checks on the combined result. Count coordination and review time as part of the experiment; more concurrent attempts are not automatically more accepted work.

## Keep "do less" on the table

Sometimes the comparison points to a smaller move than either camp expected. Maybe the rule table handles the new discount cleanly and immediately needs precedence rules and conflict checks, while plain functions stay local, readable, and easy for support to trace.

Picking plain functions for today means waiting until rule count or non-engineering authoring justifies the extra machinery, while keeping the overlap cases you discovered ready if that day arrives. Whenever "handle it manually for now" is a real option, include it honestly along with the operational effort and error risk it puts on whoever runs it.

## Leave a decision trail with expiry conditions

Save the shared test cases, expected outputs, commit hashes, run commands, and a short note explaining why you picked one option, what you rejected, and what concrete signal should trigger revisiting the call:

```text
Chosen: explicit pricing functions for the effective-dated discount
Rejected: generic rule table (needed precedence and conflict validation immediately)
Why: changes stayed local and invoice explanations were easy to follow

Unresolved: non-engineer editing, large overlapping rule sets
Revisit if: business staff need to author pricing rules directly, or rule count exceeds ~15
Evidence: shared corpus, both prototypes, notes from the trace exercise
Status: experiment only; neither prototype is a supported API
```

Keep prototype code clearly separated from production code (and outside any [architectural ratchet](./architectural-ratchet.md) that might block exploring a new boundary). Once keeping both spikes runnable as dependencies move gets expensive, keep the commit hashes, test cases, and decision note rather than nursing dead prototypes forever.

Simon Willison's [Hoard things you know how to do](https://simonwillison.net/guides/agentic-engineering-patterns/hoard-things-you-know-how-to-do/) makes a strong case for keeping small working experiments around to combine later. On a team, the crucial addition is a label on each experiment: what it proved, under what assumptions, and what it deliberately skipped.

## Know when to stop

A prototype can expose a bad data model or a missing input, yet it will not prove production scalability or failure recovery just because the happy path ran. When load or migration safety is the deciding factor, include the smallest credible test of that concern before picking, or mark it unresolved and budget for it explicitly.

Stop once extra work stops changing the decision. You rarely need a third prototype unless the first two turned up a brand-new question neither can answer.

## What survives the losing prototype, and sources

Even the discarded prototype earns its keep: the shared awkward cases you built to test it stay behind and later feed [differential verification](./differential-verification.md), and the decision note with explicit revisit conditions saves the team from re-litigating the same argument twelve months later.

Competing prototypes are much cheaper to run when [scenario builders](./scenario-builders.md) and [executable invariants](./executable-invariants.md) already exist to supply realistic cases and verify both options. Check whether any retained spikes are still earning their upkeep in an [investment retrospective](./investment-retrospective.md).

- Ryan Singer, [Find the Elements](https://basecamp.com/shapeup/1.3-chapter-04) (*Shape Up*): sketching alternative approaches at low fidelity when writing code too early slows exploration down.
- Martin Fowler, [Sacrificial Architecture](https://martinfowler.com/bliki/SacrificialArchitecture.html): why deliberately temporary software still needs enough internal clarity to teach you something real.
