# Shorten the learning loop

*Get an answer while it can still change the work.*

A developer changes a retry handler, pushes it and waits for the shared test environment. By the time the failure arrives, they are deep in another task. An agent can prepare the next patch during that wait. The team now has two uncertain changes to track.

Use this pattern when a consequential question waits for setup, a queue or an unnecessarily large experiment. Follow one question from the moment it arises to the point where someone acts on a trustworthy answer. Optimizing the command in the middle may leave most of the delay untouched.

## Name the decision the answer should change

In this hypothetical case, the question is whether a retry after an interrupted write can lose a payment. The team does not need the entire staging environment to investigate the handler's transaction boundary. It needs storage with the relevant transaction behavior, a controlled interruption and an independently stated result.

Before changing the workflow, inspect a few recent attempts. Separate time spent preparing the case, waiting to run it, running it and interpreting the result. Notice whether the answer arrived soon enough to affect the design. Use actual traces or notes where available rather than an engineer's guess about an average week.

Then look for the smallest useful change. It might be making a fixture easy to run locally, giving a customer interview a place in the team's normal week, or asking the owner of a business rule before starting implementation.

| Question | A smaller attempt | Evidence it still needs |
| --- | --- | --- |
| Does a retry lose a payment? | Replay one interruption locally | A reviewed expectation and representative transaction behavior |
| Can customers understand a refund? | Observe them using a small prototype | Actual customer behavior; a generated persona cannot provide it |
| Is a new architecture suitable? | Try two designs on the hardest relevant case | The same acceptance question and stated limits for both |

These checks answer different questions. A faster technical replay cannot establish that customers want the feature.

## Predict, run, study

Write the prediction before running the check. For the interrupted payment, it might be: “If receipt and balance share a transaction, an interruption before commit leaves neither; the retry records one payment.” A failure should prompt an investigation of the prediction as well as the code.

The [evolving billing lab](../examples/evolving-billing/README.md#3-interrupt-the-work-between-writes) provides this bounded technical example:

```sh
python3 examples/evolving-billing/replay.py run --case after-record --implementation split
python3 examples/evolving-billing/replay.py run --case after-record --implementation atomic
```

The first command exits 1 with the payment missing. The second exits 0. Both use deterministic exceptions and a temporary SQLite database. Neither tests concurrent workers or a power failure. A production decision involving those conditions needs additional evidence.

Keep broader checks where their coverage matters. A useful local check helps an engineer discard a bad approach earlier; it does not automatically replace integration or release checks.

## Find out whether people use the earlier answer

On the next relevant change, let another engineer use the normal entry point. Can they run the check while considering alternatives, understand a failure and change their decision? Does it catch the relevant defect, or simply return green more quickly?

Count setup, false alarms, interpretation and upkeep. Watch the whole route to an accepted change so you can see if waiting merely moved into review. Record whether the cheaper check made a previously impractical comparison possible. More experiment runs are useful only when they resolve worthwhile uncertainty.

If AI generates work faster than it can be assessed, reduce the amount in flight while repairing the feedback path. Producing another candidate can increase the review queue without bringing the answer closer. Leave enough capacity to handle unexpected findings; filling every gap with another commitment defeats the point.

## Stop where the question is answered

Keep the small check if it changes decisions at an acceptable cost. Repair it if results are unreliable. Remove it when the underlying behavior no longer exists. Do not build a new testing platform to shave seconds from an occasional command while the actual decision waits days for an owner.

The [PDSA cycle described by the Deming Institute](https://deming.org/explore/pdsa/) grounds this pattern's learning discipline: predict an outcome, study what happened and revise the theory. This pattern proposes reducing the cost and delay around that cycle.

See [The economics of feedback](https://grove.github.io/engineering-that-compounds/essays/the-economics-of-feedback.html) for the broader argument. [Friction to hypothesis](./friction-to-hypothesis.md) helps when you do not yet know which question matters. [Capability command](./capability-command.md) helps when the useful check exists but remains awkward to run.
