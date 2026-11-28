# Investigate the recurring intervention

*Use a repeated stop in delivery to decide whether the work needs better evidence, a different design or a human decision.*

A migration is ready, but someone needs the database specialist again. The review asks familiar questions: how long could the operation hold a lock, what happens if it stops halfway, and can the previous application version still run afterwards? An agent can prepare the change quickly. The specialist still reconstructs the same evidence before each release.

There are several possible repairs. The team could make that evidence available without an investigation. It could redesign the feature so this class of schema change is unnecessary. It could discover that the proposed change involves a decision the specialist should continue to make. Counting interruptions will not tell those answers apart.

This pattern examines a recurring stop across a class of work. [Earned delegation](./earned-delegation.md) helps establish what a particular task can be trusted to do. Here the earlier question is whether to expand delegation, change the work or preserve the decision. The migration team below is hypothetical; its checks and results must be established in a real system before changing a release policy.

## Reconstruct what made the intervention necessary

Choose one recognizable class, such as changes to the customer-profile schema. Read a small selection of recent migrations, including a rejected change and one that passed without help. Follow each through preparation, review, release and operational follow-up.

For each consequential intervention, identify what the person supplied. Did they find existing evidence, run an experiment, notice a missing assumption, choose between conflicting requirements or grant authority? Keep the relevant passage or result with the example. An AI assistant can group the records, but a grouping is useful only if an engineer can follow it back to the work.

Suppose the specialist repeatedly builds a representative database and rehearses the migration. The problem may be that nobody else can construct that environment. If the same person instead keeps deciding whether a customer can tolerate an interruption, a better rehearsal will supply evidence for the decision without settling it.

Include the interventions that prevented mistakes. A trial that rewards fewer questions may teach the system to conceal exactly the uncertainty the reviewer needs to see.

## Compare three repairs

For the rehearsal problem, try making one existing check usable from the normal migration workflow. Preserve the database version, starting schema, representative data distribution and competing traffic that make its result relevant. Report observed locks, elapsed time, resource use and recovery behavior, together with what the rehearsal does not cover. Those details belong to the team's system; they cannot be inferred from a statement being syntactically valid.

Before building a general migration service, also ask why these changes keep arriving. Suppose new customer requests repeatedly add optional profile fields. Some might fit a reviewed configuration model. That could remove a class of migrations altogether. It could also make validation, indexing and reporting harder. Compare one actual field request under both designs; do not move the complexity into an unstructured field and call the work eliminated.

The third repair may be to keep a decision with a person while improving its preparation. A change that reinterprets existing customer data needs an agreed meaning, even if its execution is flawless. A release that needs an interruption requires someone to weigh its consequences. Make the evidence and the decision owner easy to find. Requiring the owner to reconstruct a failed rehearsal adds nothing to their judgment.

These alternatives need not share a tool. [Friction to hypothesis](./friction-to-hypothesis.md) helps when the records support several competing explanations; use it before deciding that the next investment must be automation.

## Try the repair without changing release authority

Choose a pending migration whose decision is still open. Have the proposed workflow prepare its evidence in isolation while the existing review continues. Ask the specialist to inspect the evidence, identify omissions and explain whether it answers the questions they would otherwise investigate. Keep setup, interpretation and corrections in the cost of the trial.

Include a deliberately unsuitable candidate in the rehearsal: for example, one that fails the application's supported-version check or cannot resume after an interruption. The point is to establish that the proposed evidence distinguishes the cases the team cares about. Passing a representative workload is still limited evidence about production behavior.

Then try a different migration. A check tailored around the first answer may be cheap to demonstrate and expensive to use. Watch whether another engineer can choose the right starting state and explain a surprising result without the specialist taking over.

Only after this should the owner consider changing what may proceed without routine review. Tie any change to explicit eligibility and evidence. Keep changes to the eligibility rules separate from the work being evaluated. A workflow cannot justify a candidate by relaxing its own acceptance standard.

## Count the work that moves

The specialist may receive fewer requests because application engineers now spend longer preparing the rehearsal. That could still be worthwhile if it relieves a genuine constraint and improves their understanding, but it is not a saving in total effort. Include environment upkeep, model use, interpretation, rework and operational consequences.

Retain the complete set of relevant changes when comparing before and after. If difficult migrations are quietly redirected into a manual queue, the automated queue will look impressive while the team's overall delivery remains unchanged. Report which work was eligible, what completed, what stopped, what was rejected and what happened afterwards.

Use successful runs to check the boundary too. A missed stop may be more consequential than several unnecessary escalations. The goal is a useful migration reaching production with its requirements met, at a worthwhile total cost. An intervention rate is a diagnostic measure within that goal.

## Leave a reason to keep the human decision

Stop expanding the trial when the missing evidence cannot be obtained at a reasonable cost, the class is too varied to define usefully, or the remaining work is a legitimate choice between consequences. Record which condition applies. Otherwise the next automation effort will rediscover the same boundary.

If the rehearsal is costly to maintain and migrations are infrequent, an occasional specialist review may be the cheaper arrangement. If data meaning is unsettled, settle it with the people who own that meaning. Neither outcome represents a failed attempt to automate.

When the repair does help, follow the next use. A repeatable environment might later make it feasible to compare a different storage design or investigate a recovery protocol. Record which existing pieces helped, what had to be added and whether the earlier assumptions still held. That second investment is where a claim about compounding becomes testable. Simply running the migration check again establishes reuse.

## Sources and related patterns

Google's [Eliminating Toil](https://sre.google/sre-book/eliminating-toil/) distinguishes repetitive operational work from work requiring judgment and includes designing away a task among the ways to remove toil. This proposed pattern applies that distinction to interruptions in a delivery workflow; the source does not establish the return from this migration example.

[Capability command](./capability-command.md) helps make an existing check usable. [Capability composition](./capability-composition.md) addresses the later step of combining it with other capabilities. Use an [investment retrospective](./investment-retrospective.md) when there has been enough subsequent work to assess both the return and the upkeep.
