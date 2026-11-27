# Investment retrospective

*Look at what happened when later work met the tool you built.*

A team spends several days building an invoice comparison tool. The first migration goes well. Months later, the tool is still in the repository, and someone repairs its fixtures whenever the invoice schema changes. It appears in presentations as an investment in engineering productivity. Nobody can readily name the last change it helped.

An investment retrospective examines one such investment using subsequent work. What was it supposed to make easier? When did that work occur? What did people use, what did they work around, and what did upkeep cost? End with a decision about what to keep maintaining.

This proposed practice helps a team decide what remains worth maintaining. Use it for tools, checks, documentation or abstractions with a meaningful continuing cost. A useful five-line script does not need a quarterly business case.

## Leave yourself something to compare

When starting an investment, record its intended benefit in terms of a recognizable task. “Improve confidence” is hard to revisit. “Compare old and new invoice totals without rebuilding the same fixtures” gives you somewhere to look.

Keep a link to one or two recent examples of that task. Note where the effort went: acquiring data, constructing a scenario, running checks, interpreting mismatches, waiting for a specialist. Record rough ranges if that is all you know. Do not invent a precise baseline from a vague memory.

Choose a review trigger that gives the investment a chance to be used. For the fictional subscription service, that might be after the next few pricing changes or the next migration. Also choose a date at which to ask whether that work has occurred. If demand disappears, that is relevant to maintenance, even though it says little about how good the tool was.

An illustrative note could be this short:

```text
Investment: invoice comparison runner
Expected use: pricing changes that must preserve existing invoice results
Current difficulty: engineers rebuild fixtures and inspect mismatches by hand
Evidence to keep: relevant PRs, fixture repairs, cases the runner cannot handle
Review trigger: three relevant changes, or the next planning review
Possible decisions: keep, simplify, repair one gap, archive
```

The number of changes is a chosen review budget, not a statistical sample size.

## Read the work, including the bypasses

At review time, inspect a small set of actual changes. Include relevant work that did not use the investment. If you examine only successful runs, you will miss setup friction, gaps and situations where an engineer found a simpler route.

For each change, ask the engineer who did it what happened. Compare their account with the PR, incident notes or command output. Separate time spent learning the domain from time spent operating the tool; both matter, but they suggest different repairs.

Here is an invented review of the billing runner. These are illustrative observations, not measured results from a real team:

| Later work | What the runner contributed | Work still needed |
| --- | --- | --- |
| Effective-dated discount | Existing cases exposed an unintended change to old invoices | A domain expert resolved whether one difference was intended |
| Credit calculation refactor | Fixtures were reused after updating the invoice adapter | The adapter change took longer than running the comparison |
| Refund correction | The engineer bypassed the runner because refunds were unsupported | A separate reproducer was built for the failing sequence |

That table supports several decisions. The invoice cases seem useful. The adapter may deserve simplification. The refund gap might be acceptable if the runner was never meant to cover refunds. Automatically expanding it would turn the review into another project proposal.

## Count upkeep and changed circumstances

Collect the cost of fixture repairs, dependency upgrades, confusing failures, onboarding and ownership. Include help provided informally by the tool's author. A command can look self-service because nobody records the private messages required to run it.

Separate the initial cost from future upkeep. The first matters when deciding whether to make similar investments again. The second matters when deciding whether this one should remain supported. Past effort does not make a tool worth keeping, and a disappointing initial return does not require deleting something that is now useful and cheap to maintain.

Also ask what changed around it. Perhaps the team learned the billing domain, the migration became smaller, or a third-party tool acquired the needed feature. Perhaps the hardest changes were deliberately postponed. These differences make a simple before-and-after time comparison unreliable.

Google's [Eliminating Toil](https://sre.google/workbook/eliminating-toil/) chapter discusses measurement and the cost of developing automation, as well as alternatives to automating a task. That is a useful discipline here: include the effort needed to keep the improvement working and consider whether the underlying task can disappear.

## Use several kinds of evidence

A shorter run time matters when running the check was the bottleneck. It matters less when engineers still spend a day explaining its output. Combine observations about effort with evidence about the result:

- Could someone other than the author carry out the task?
- Did the check find a consequential defect or help establish a required property?
- Did a later change reuse the inputs or machinery?
- Did the tool shift work to another team or add a new failure mode?

A clean run is useful evidence only within the checks' scope. Several quiet months do not show that the tool prevented incidents. Likewise, a rare recovery tool may remain worth keeping without frequent use; examine the need it covers and rehearse it instead of demanding a high run count.

The [SPACE framework](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/) argues that developer productivity cannot be captured by one metric or dimension. Keep this review close to the tasks being improved. Do not turn command invocations, PR counts or individual time estimates into performance rankings.

## Make a maintenance decision

Choose a change small enough to complete. For the illustrative billing review, keep the invoice cases and runner, simplify the adapter, and document that refunds need another approach. Assign the adapter repair to an owner and review it when the next relevant schema change occurs. There is no reason to commission a general billing test platform from this evidence.

Other reasonable outcomes include archiving an experiment, removing a redundant check, or keeping a tool unchanged until a known upcoming migration. If evidence is missing, name the next event that would supply it. “Collect more data” without a decision or stopping condition can become its own maintenance burden.

Record a few sentences beside the tool or its tracking issue. Include the changes examined, the main cost, the decision and what would make you revisit it. There is little value in creating a separate reporting system that nobody uses for the next decision.

## Recognize a further return when it happens

Repeated use can repay an investment without producing any further capability. A stronger result appears when retained work makes another useful investment cheaper: the invoice cases become inputs to [Competing prototypes](./competing-prototypes.md), or the runner makes a risky replacement practical through [Differential verification](./differential-verification.md).

Record which artifact was reused, what new work it enabled, and the cost of adapting it. The next review can then ask whether those new uses still justify the machinery they inherited.

For tools whose upkeep exceeds their remaining value, use a [Subtraction investigation](./subtraction-investigation.md) to find their consumers and retire them deliberately.
