# Friction to hypothesis

*Find out why the same difficulty keeps returning before building something to fix it.*

Suppose reviewers keep asking what happens when a payment worker restarts. An agent reads the recent pull requests and suggests a better retry guide. That might help. It might also add a page nobody needs: perhaps engineers understand the rule but cannot construct a restart in the test harness.

The repeated question tells you where to look. It does not yet tell you what to build.

Use this pattern when a difficulty recurs and several explanations would lead to different investments. Start with a few examples from ordinary work, ask what would distinguish the explanations, and try the smallest useful investigation. If the cause and remedy are already clear, make the repair.

## Keep the observation separate from the explanation

In this hypothetical team, payment changes repeatedly wait for a specialist to review recovery behavior. The team considers three explanations:

| Possible explanation | What would support it | Different investment it suggests |
| --- | --- | --- |
| Engineers cannot find the delivery contract | Investigators miss the current contract and use an older assumption | Repair the route to the contract |
| Engineers know the contract but cannot check it | They explain the expected result, then get stuck constructing a restart or interruption | Extend the test harness |
| The contract leaves the question open | Engineers find the same current sources but disagree about which deliveries represent one payment | Get the provider or domain owner to settle the identity rule |

More than one explanation may apply, and each calls for a different repair.

Read the original changes before accepting the grouping. Include a payment change that passed review without that question. Ask the people involved what they were trying to establish. A comment about a retry may concern a forgotten event ID, an interrupted transaction or a different event for the same payment. Similar words can hide different obligations.

An AI assistant can collect the relevant passages, link each one to its source and suggest alternative explanations. Give it a bounded set of records the team is permitted to use. Ask it to show examples that do not fit its grouping and to leave unknowns visible. Review the source links yourself. A summary that says “retry problems” may have erased the distinction the investigation needs.

## Choose a question the next attempt can answer

The team chooses an upcoming recovery change. Before anyone starts, the reviewer records the expected behavior from the current delivery contract, the relevant evidence and the conditions that remain uncertain. This expectation stays separate from the task given to the investigator.

Ask a teammate or fresh agent session to investigate the change using the usual repository entry point. Observe where the work stops. If the investigator finds the contract, explains the restart expectation correctly and then cannot make the harness reopen storage, that is evidence of a missing test capability. Another page describing retries would not repair that gap.

If they miss the contract, repair its existing link and try a comparable task with a fresh investigator. If they find contradictory rules, take those rules to their owner. Do not make the agent choose the interpretation that is easiest to implement.

Keep the first trial small: one investigation, one proposed repair and a review after the next relevant change. Record other differences, including the investigator's experience, model, available context and task difficulty. The attempt can expose a practical obstacle. You will need a stronger comparison to establish whether the repair, the investigator or the task explains a later improvement.

## Follow the result into a repair

Suppose the investigation shows that the contract is available and understood, but the harness can only deliver events within one worker lifetime. The team adds a restart action to the existing replay. The reviewed expectation remains one applied payment after a duplicate delivery.

The new check must fail against a handler that forgets delivery IDs on restart and pass against one that preserves them. Review the expected result and the check independently of the proposed handler. Having an agent write all three from the same assumption can make them agree for the wrong reason.

The [evolving billing lab](../examples/evolving-billing/README.md#2-ask-the-same-question-after-a-restart) provides a runnable, synthetic version of this technical step. It demonstrates the difference between the two storage designs. It contains no observations about the fictional team's review time.

Now watch the next relevant change. Can its author find the replay, run it and explain the remaining limits without the specialist reconstructing the investigation? If the same interruption remains, inspect it. Perhaps the new task concerns two workers, while the replay still uses one. A different question deserves different evidence.

## Challenge the premise

Sometimes the repeated difficulty comes from the rule everyone is trying to satisfy. Suppose every deployment still needs a senior engineer's approval. An assistant could prepare the approval packet faster. First ask what the approval protects, who owns it and whether that reason still applies.

Perhaps it was introduced when releases required a manual data conversion that has since disappeared. Perhaps it now catches a different risk that nobody has documented. Read the original decision and examine recent approvals, including ones where the reviewer intervened. Compare improving compliance, replacing the control and changing the work so the risk no longer arises.

Take the evidence to whoever can change the rule. A team should not quietly bypass a required control because its history is unclear. If the rule changes, update the active instructions and checks together; otherwise people and agents may keep following the old version.

Argyris's [Double Loop Learning in Organizations](https://store.hbr.org/product/double-loop-learning-in-organizations/77502) distinguishes correcting actions within existing governing assumptions from reconsidering those assumptions. Here the practical question is whether to improve the handoff or change the reason it exists. The essay [Getting better at the wrong thing](https://grove.github.io/engineering-that-compounds/essays/getting-better-at-the-wrong-thing.html) follows that question further.

## Decide what deserves to survive

Keep the cases and result beside the affected code or existing issue. A short record is enough:

```text
Observation: recovery changes wait for a specialist to establish restart behavior.
Alternatives: missing contract, missing harness action, unsettled identity rule.
Evidence: link the reviewed changes and the attempted investigation.
Finding: state which explanation the attempt supports and what remains open.
Repair: link the change, or explain why no change is warranted.
Review: next recovery change, with a fallback date if that work does not arrive.
```

Fill in the evidence and finding from the actual attempt. An existing issue may already contain most of this; avoid copying it into another document.

If a hypothesis was wrong, keep the reason only when someone is likely to repeat the same expensive investigation. A finding that the existing check already covers the risk can end the work. There is no requirement to produce a new tool, instruction or pattern.

## Price the investigation as well as the repair

Someone must check an AI summary, follow its references, dismiss false matches and maintain any retained extraction procedure. Count that attention along with model use, setup and the repair itself. Include the work passed to reviewers or neighboring teams. Generating ten plausible explanations is unhelpful if sorting them costs more than reading the three original changes.

Agree on a stopping point before expanding the search. For this example, use the one recovery change to choose a next step. If it cannot distinguish the explanations, state the missing evidence and decide whether the decision is valuable enough to investigate further. Do not quietly turn a small review problem into a scan of every repository and conversation.

These records belong to an investigation of work, not a ranking of employees. A person who asks the right question may create more visible comments while preventing a mistake. Counting comments or interventions cannot tell you whether their contribution helped.

## Check the next use

Saving the investigation is accumulation. If it helps a later recovery change meet the same acceptance standard with less total effort, there is evidence of a return. If the retained restart action then helps someone build interruption checks or compare a new storage design, investigate whether it made that later capability cheaper or more effective to build. That is the possible compounding step.

Another team can try the method where its conditions fit. Its independent use is evidence of transfer; transfer alone does not establish compounding. The original team can also compound its learning without involving another team.

Use an [investment retrospective](./investment-retrospective.md#review-the-way-you-look-for-improvements) if the AI-assisted investigation itself becomes a recurring practice. Check whether it finds useful questions at an acceptable cost, including misses and abandoned suggestions. Shorten or stop it when reading the original work is more useful.

## Related patterns and sources

Google's [Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) describes generating possible causes and testing them against observations or controlled changes. It also discusses spurious correlations. This proposed pattern applies that discipline to recurring engineering friction; the source does not establish a benefit from AI analysis of review history.

[Verified retrieval](./verified-retrieval.md) tests whether someone finds and applies existing knowledge. [Review comment to guardrail](./review-comment-to-guardrail.md) fits an agreed, detectable mistake. [Competing prototypes](./competing-prototypes.md) fits a design question that small implementations can answer. Choose among them after examining the difficulty. The companion essay [Compounding learning](https://grove.github.io/engineering-that-compounds/essays/compounding-learning.html) follows how AI might help this investigation and how to evaluate its contribution.
