# Verified retrieval

*Find out whether the next person can use the knowledge you kept.*

Imagine a fresh coding session investigating whether a payment handler can run in two worker processes. It finds the duplicate-delivery test, runs it, sees green and proposes the deployment change. The example handler keeps its event IDs in a local set. A second process would start with its own empty set.

The documentation was found. The command worked. The important qualification got lost between reading and deciding.

Verified retrieval is a rehearsal of that handoff. Give someone a representative task through the repository's ordinary entry point, then observe whether the relevant knowledge changes what they do. Try it when people keep rediscovering an answer, agents repeat a corrected mistake, or an old note keeps winning arguments it no longer applies to. One task is enough to expose a useful problem; you do not need a documentation benchmark for the whole repository.

## Start with the task, keep the answer out of it

Choose a recent or upcoming change for which a particular record or check matters. Before the rehearsal, write down what a competent investigation should uncover, why it matters and what would count as misuse. Keep that expectation separate from the instructions you give the participant.

For a small exercise using this repository's [billing lab](../examples/README.md), a teammate or fresh agent session could receive this task:

```text
We want two workers to process payments in the billing example.
Investigate whether the existing handler is ready for that change.
Use the repository to support your recommendation and identify
what still needs checking. Do not change the code yet.
```

Give them the checkout and the task. Let them start from the normal README or agent entry point. Do not supply the lab instructions, the replay command or your earlier conversation about the bug. If you provide those, you learn whether the explanation is understandable, but leave discovery untested.

For an agent, check what context the tool actually carries over. A new chat that imports the earlier summary is not a fresh attempt. Use the same ordinary repository guidance and permissions a later task would have, and note any retained context that could help it find the answer.

## Decide what you will look for

Here are the expected observations for the exercise. They are a reviewer's guide, not extra hints to put into the task:

| Observation | Evidence you can inspect |
| --- | --- |
| Finds the relevant material | The recommendation cites the [lab instructions](../examples/README.md), [replay implementation](../examples/billing_lab.py) and [duplicate-payment fixture](../examples/scenarios/duplicate-payment.json) |
| Checks the available claim | The fixed replay exits 0; the deliberately buggy replay exits 1, with the expected and observed totals visible |
| Recognizes the limit | The investigation identifies an event-ID set local to one replay call and explains why multiple workers or a restart need additional evidence |
| Changes the proposed work | The plan includes investigating durable deduplication and transaction behavior before recommending a production deployment |

The exercise stops at a recommendation. This repository has no production database or concurrent worker implementation, so it cannot establish that a particular deployment design is safe. Finding that missing evidence is a successful outcome.

In your own service, establish the rubric from the reviewed requirement, relevant decision and a check whose scope you understand. Having the same agent invent the rule, write the note and grade its own reading only gives you three versions of one assumption.

## Watch where the handoff breaks

A confident answer that says "I followed the documentation" is weak evidence. Inspect the cited records, command output, proposed checks and resulting diff. Ask a teammate to explain which fact changed their plan. If the agent environment does not expose what it opened, you can still check its citations and actions; be clear that you have less evidence about the search itself.

Separate the failures, because they need different repairs:

| What happened | Small repair to try |
| --- | --- |
| Never found the relevant record | Link it from the module, README or existing domain index where this task starts |
| Found it but missed the condition | Put the condition beside the instruction or command it limits |
| Followed superseded advice | Mark the old record superseded and link the current decision; remove the old rule from active summaries |
| Understood the note but could not check it | Repair the command, fixture or access to the cited evidence |
| Applied a valid rule to the wrong task | Add the missing scope boundary and rehearse a nearby case where the rule does not apply |

Suppose an older billing note recommends in-memory deduplication for a single-process demonstration. A newer deployment plan does not automatically make that note false; it changes where the recommendation is useful. Preserve that distinction. Dates and an "active" label help with navigation, but neither proves a rule still fits the task.

If two current sources disagree about the payment contract, a better index will not settle the disagreement. Surface it to the person responsible for that contract. Do not teach an agent to resolve it by choosing the newest file.

## Repair the route before adding more prose

Keep repository-wide instructions short. They can point a billing task toward the current decision, worked example and verification command without copying those three things into `AGENTS.md` or every tool's instruction file. A useful entry in an application repository might look like this adaptation sketch; the path is illustrative:

```text
For payment-handler changes, start with docs/billing/README.md.
It links the current delivery assumptions and the replay command.
Check the documented limits before treating a passing replay as
evidence for a concurrency or storage change.
```

Where a rule can be enforced, put it in a check and link the explanation from the failure output. Where judgment remains necessary, keep the evidence and the person responsible within reach. Writing "be careful with payments" into three instruction files gives the next session very little help.

After a repair, try a fresh participant or session. Keep the task and ordinary entry point comparable, record any changes in tools or context, and see whether the earlier failure disappears. Then vary the task: a change to invoice credit arithmetic should lead to the calculation contract, not a ritual replay of the payment webhook. One successful run shows that a route can work. The next real change is where you find out whether it helps without coaching.

## Try the lesson in another team's context

An assistant can suggest where a retained check might help by comparing relevant code, contracts or incident records that it is permitted to read. Keep the suggested match attached to its evidence and conditions. Finding the words “duplicate payment” in two repositories does not establish that they use the same delivery contract.

Ask one receiving team to test applicability during work it already needs to do. Can it find the current rule, adapt the check and explain which assumption changed? A team that decides the check does not fit has still produced a useful answer. Keep that reason with the attempted transfer so the next recommendation does not repeat it.

Record setup and support on both sides. The source team's check may save its own time while creating work for the receiver. Use the existing [capability transfer](https://grove.github.io/compounding-engineering/adoption/patterns.html#capability-transfer) practice to agree on ownership and adaptation. A useful independent application establishes transfer. A claim of compounding still needs evidence that earlier work helped build a later capability.

## Keep the rehearsal small

Retain the task, expected observations and the repair beside the knowledge it exercises. Revisit after a relevant decision changes, the entry point moves, or a real user misses the guidance again. Avoid a growing suite of prompts that insists on particular wording or exact file-opening sequences; a different route to sound evidence is fine.

If the answer is already obvious from a short README, read it and move on. If the guidance matters so rarely that rehearsing it costs more than reconstructing it, drop the rehearsal. Keep records whose evidence or consequences justify their upkeep, and retire obsolete routes along with obsolete tools.

## Related patterns and sources

[Every's Compound Engineering guide](https://every.to/guides/compound-engineering) calls for capturing solutions, making them findable and verifying the learning. This collection's proposed pattern turns that last question into an observable handoff; it does not establish a productivity benefit from retrieval alone.

[What software should remember](https://grove.github.io/engineering-that-compounds/essays/what-software-should-remember.html) develops the underlying requirements for provenance, current constraints and reconsideration triggers. A [capability command](./capability-command.md) makes the discovered procedure usable. A [review comment to guardrail](./review-comment-to-guardrail.md) can enforce a settled rule without relying on recall. The [investment retrospective](./investment-retrospective.md) follows these repairs into later work and asks whether they earned their upkeep.
