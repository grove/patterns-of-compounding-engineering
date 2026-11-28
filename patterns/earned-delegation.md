# Earned delegation

*Use the moments when you have to step in to decide what the engineering environment needs next.*

Suppose an engineer asks an agent to fix duplicate payment notifications. The agent runs the existing replay, sees green and recommends deploying the change to two workers. The engineer intervenes: the handler remembers event IDs in a local set. Two workers have separate sets. A green check has answered a smaller question than the deployment asks.

The engineer can repeat that warning every time, or the team can investigate what evidence is missing. It may need a better way to discover the limitation, a check using the real storage and transaction behavior, or a narrower task that does not promise safe concurrency.

Earned delegation is a way to choose that investment. Apply it to recurring tasks that require substantial supervision, not to a one-off risky operation merely because an agent could attempt it.

## Keep a record of useful interruptions

Choose a class of task with a clear outcome. During a normal attempt, record the interventions that changed the result, not every message in the conversation.

| Intervention | Missing capability | Small repair to try |
| --- | --- | --- |
| Explained a domain rule | Current contract was hard to find | Link the reviewed rule from the handler |
| Supplied a fixture | Hard to construct the failure | Retain a safe synthetic case |
| Rejected a green concurrency claim | Replay only covered sequential retries | Document scope and design a separate transaction-level check |
| Stopped a live write | Environment allowed an unnecessary side effect | Use an isolated target with restricted credentials |

Fix the most consequential recurring problem first. An instruction not to write to production is not a substitute for permissions that prevent it.

Sometimes the interruption is a real business decision. Preserve its owner and evidence rather than automating the judgment away.

## Write down the next agreement

The [billing lab](../examples/README.md) provides a small exercise. It contains synthetic data, deliberately broken examples and a fixed handler that deduplicates sequential deliveries in memory. A limited delegation agreement could look like this:

```text
Task: change or investigate sequential duplicate delivery.
Allowed: read the repository, edit a branch if requested,
         run the local synthetic replay and tests.
Evidence: reviewed fixture; broken implementation fails,
          fixed implementation passes; explain coverage limits.
Stop: requirement changes to concurrency, durable storage,
      refunds, real payments or external access.
Acceptance: reviewer inspects the diff and evidence.
```

Run the two examples from the repository root:

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
```

The first deliberately exits 1 after applying the payment twice. The second exits 0 after applying it once. Those results establish a particular sequential behavior. They do not establish that a production handler is safe across restarts or workers.

An agent can conduct this bounded exercise without being authorized to deploy anything. For the next class of change, investigate the real provider contract, durable state, transaction boundaries, crash windows and recovery before expanding scope. The lab cannot settle those questions.

## Investigate a failure before changing the instructions

An agent's failed attempt can reveal a missing capability, but it can also reveal a mistake that a new instruction will not fix. Keep the task, relevant output, tool versions and the intervention that changed the result. Ask an assistant to compare a few such attempts and identify competing explanations, with references to the evidence. Review those explanations before adopting them; [friction to hypothesis](./friction-to-hypothesis.md) gives this step a small scope.

For the payment example, distinguish an agent that never found the replay's limits from one that read them but had no way to test a restart. The first calls for a retrieval repair. The second may justify extending the harness. If the agent changed an expected total to make the check pass, inspect the acceptance process rather than adding another paragraph about careful testing. Keep the reviewed expectation outside the candidate's control.

Try the smallest repair on a different task, including one where the right answer is to stop. Preserve the failure only if it remains useful for that check. A longer instruction file, a quieter agent or fewer requests for help does not establish that delegation improved.

## Try again without widening the task

Give a teammate or fresh session a comparable task through the normal entry point, with the same permissions and independent evidence. Observe whether the previous intervention is still necessary. Inspect the result and check whether a new error escaped.

A useful trial records the task, where the investigator got stuck, which evidence was checked, time spent reviewing or reworking, and the decision about the next boundary. Fewer questions alone are not evidence of improvement. The reviewer may have had to redo the whole investigation.

Where appropriate, deliberately introduce a known mistake in an isolated environment and confirm that the check rejects it. If the agent fails to find the check, try [Verified retrieval](./verified-retrieval.md). If it can find it but cannot run it reliably, try a [Capability command](./capability-command.md).

## Stop before the permission boundary moves itself

A project may support unattended work on local previews but need a named owner for a migration. Keep the scope tied to the task. An agent should surface new risks and stop for authority rather than expand its own permissions. For high-stakes or irreversible changes, keep independent acceptance and tested recovery requirements; where those cannot be established, do not delegate execution.

Do not remove a useful human learning opportunity just to reduce supervision. A new engineer may need to predict, run and explain a replay. Delegate the repetitive setup, not necessarily the reasoning.

If a safeguard becomes costly to maintain, revisit the agreement. A changed contract or newly introduced worker may invalidate the old evidence. Reducing the permitted scope can be the right response.

[Every's Compound Engineering guide](https://every.to/guides/compound-engineering) discusses progression toward more independent agent work. Here that progression depends on the evidence and permissions for a particular task. The companion essay series [Engineering that compounds](https://grove.github.io/engineering-that-compounds/) develops the role of engineering judgment and the costs of retention.

The point of the pattern is to turn repeated supervision into a question the team can investigate. Sometimes the answer is a better check. Sometimes the safest and cheapest answer is to keep the supervision.
