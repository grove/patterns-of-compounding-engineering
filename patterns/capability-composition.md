# Capability composition

*Use what the team can already do to make a new kind of work practical.*

Suppose a billing team wants to replace its payment store. It already has a way to construct awkward invoices, a replay that can interrupt a worker, and agreed expectations for what survives a retry. Each was built for a different problem. Together, they might provide most of a replacement check.

Start here when a worthwhile change looks expensive or risky and the team may already have some of the means to attempt it. Find the relevant checks and run them. A list of repository names tells you little about whether anyone can use them together.

## Start with the work you want to make possible

For this hypothetical migration, the desired capability is specific: an engineer can compare two storage designs against the same recovery expectations, explain disagreements and identify what remains untested.

Name a few relevant things the team can already do, then try them:

| Available capability | What it contributes | What still needs checking |
| --- | --- | --- |
| Construct a duplicate-delivery case | Meaningful input and an expected balance | Whether the identity rule fits the new provider |
| Restart or interrupt the worker | A repeatable way to expose incomplete writes | Whether the interruption models the risk being investigated |
| Read a stored balance | A common observation for two designs | Whether comparing only the final balance would miss a bad intermediate state |

The team still needs an adapter for the new store and a comparison at every relevant checkpoint. Someone must understand the transaction boundary. Access to a production release remains a separate decision.

An AI assistant can help find candidate checks and explain their interfaces. Ask for the files and assumptions behind each suggestion. A match in vocabulary is a lead to investigate: two things called “payment” may represent different events.

## Build one connection

Choose the smallest combination that could answer the question. For the migration, run one retained case through both stores. Keep the expected result separate from both implementations. Deliberately try a store with the known defect so the new comparison has something to reject.

The [evolving billing lab](../examples/evolving-billing/README.md#4-use-the-recovery-checks-to-compare-a-replacement) contains a runnable version. From the repository root:

```sh
python3 examples/evolving-billing/replay.py compare
python3 examples/evolving-billing/replay.py compare --candidate split
```

The first comparison passes. The second exits 1 because separate commits can preserve a receipt without its payment. The comparison uses cases developed earlier in the walkthrough and checks their expectations as well as agreement between implementations.

This demonstrates how the pieces connect. It does not measure how much time an actual team would save by building them in that order.

## Check what the combination adds

A scenario builder and an invariant check can be more useful together than either is alone. That is complementarity. Running them on another release is reuse. Compounding is the further claim that earlier investments made a later capability cheaper or more effective to develop.

Keep a short account in the migration issue:

```text
New capability: compare recovery behavior before replacing storage.
Reused: delivery cases, restart action, expected checkpoint results.
New work: adapter, comparison runner, investigation of disagreements.
Costs: adaptation, review, training and upkeep of both interfaces.
Next use: another engineer evaluates a proposed storage change.
```

On that next use, watch whether the engineer can reach a sound conclusion without the original authors reconstructing the setup. Record what the old pieces helped with and what had to be rebuilt. If you estimate the cost of starting over, label it as an estimate; a plausible counterfactual is not an observed saving.

The useful outcome may be that the proposed replacement is unsuitable. A capability that stops a poor investment can earn its cost.

## Keep the joins cheap

Composition creates maintenance at the joins: formats, versions, permissions and assumptions. A universal harness can cost more than the two checks it connects. Start with a small adapter and a clear owner. Keep separate tools when their assumptions differ enough that sharing would make either harder to understand.

Also examine common failure modes. If the scenario generator, implementation and acceptance check all inherit one mistaken rule, combining them increases confidence without improving the evidence. Preserve an independent source for the expectation.

Stop if the new work has no credible use, the required evidence is unavailable, or adapting the old pieces costs more than a focused new check. There is no need to map the entire organization's capabilities before trying one useful combination.

## Where the idea comes from

Kogut and Zander's [Knowledge of the Firm, Combinative Capabilities, and the Replication of Technology](https://doi.org/10.1287/orsc.3.3.383) describes new skills emerging through combinations of existing capabilities and the ways people cooperate. Weitzman's [Recombinant Growth](https://doi.org/10.1162/003355398555595) models ideas becoming ingredients for further ideas. These provide reasons to investigate composition; neither establishes this pattern's return in an engineering team.

[Improving our ability to improve](https://grove.github.io/engineering-that-compounds/essays/improving-our-ability-to-improve.html) develops the argument. Use an [investment retrospective](./investment-retrospective.md) to follow the costs, and [verified retrieval](./verified-retrieval.md) to check whether someone else can use the result.
