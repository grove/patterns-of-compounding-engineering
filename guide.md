# Using the guide

*Choose a recurring problem, make one useful change, and watch what happens next.*

A difficult investigation often ends with something that could help the next person: a short script, a collection of awkward inputs, a way to create a particular state. Sometimes it is worth keeping. Sometimes the script depends on so much local knowledge that preserving it would be another job.

These patterns help you make that decision. They describe work a team can try within an existing system. You do not need a platform programme, a new architecture or agreement to adopt the entire collection.

## Start with evidence of friction

Choose something that has actually interrupted work. Perhaps the last two production incidents required someone to rebuild the same data by hand. Perhaps a reviewer keeps explaining why billing code cannot import the payment provider's SDK. Write down the task, the obstacle and who encountered it.

That is enough to choose an entry. If you start with “we need a better developer experience,” almost any tool can seem relevant. “A new engineer cannot reproduce this failed payment without help” gives you a result you can check.

The catalogue groups the patterns by the kind of work involved:

- [Understand a failure](./patterns/persistent-reproducer.md), [construct useful states](./patterns/scenario-builders.md), [check business guarantees](./patterns/executable-invariants.md), or [compare a replacement](./patterns/differential-verification.md).
- [Contain an architectural problem](./patterns/architectural-ratchet.md), [automate a recurring correction](./patterns/review-comment-to-guardrail.md), or [make an investigation available to other people](./patterns/capability-command.md).
- [Try competing designs](./patterns/competing-prototypes.md), [investigate a deletion](./patterns/subtraction-investigation.md), or [review an earlier investment](./patterns/investment-retrospective.md).

## Make the first attempt small

The first version should solve the problem in front of you. Keep one incident reproducible before designing an event-replay framework. Write one precise check before buying into a new linting policy. Investigate one old export before proposing a service-wide cleanup.

Agree on an effort limit with the people doing the work. The right limit depends on the task; it could be an afternoon for preserving a reproducer, or a longer piece of work to isolate a migration. Also name what you will stop doing if the experiment does not help. Otherwise even an unsuccessful trial tends to acquire a backlog.

A short note is usually enough:

```text
Problem: The payment investigation needs the original author's help.
First attempt: Save one synthetic input and a command to replay it.
Useful result: A second engineer can reproduce and explain the failure.
Budget: One afternoon for this first version.
Review: After the next payment-related change.
Stop if: The setup needs a private production snapshot to remain useful.
```

This note is an illustrative starting point, not a recommended time allowance for every incident.

## Try the billing example

Several entries use a fictional subscription billing system. It receives asynchronous payment events, calculates invoices, changes pricing rules and carries old integrations. The examples concentrate on ordinary awkwardness: repeated delivery, credit larger than an invoice, setup that conceals assumptions, and a replacement that matches the easy cases.

The [billing lab](./examples/README.md) implements a small part of that system. From a checkout of this repository:

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
python3 examples/billing_lab.py verify
python3 examples/billing_lab.py compare --candidate buggy
python3 examples/billing_lab.py compare --candidate correct
```

The two commands selecting a buggy implementation should return a failing exit status. They demonstrate that the checks can detect a defect. Run the commands separately so you can inspect both failure and success.

A repeated event pays the fictional invoice twice in the buggy handler. The corrected handler remembers the event ID during the run. The invoice comparison then reveals a candidate that applies more credit than the invoice can absorb.

The implementation is deliberately limited. It runs sequentially in memory. It does not demonstrate how to make a database transaction safe against competing workers, how long to retain event IDs, or how a payment provider's contracts should be interpreted. Those are questions to settle when adapting the technique to a real service.

## Keep the artifact with its limits

A useful artifact needs enough context to survive its author moving on. Store the command, the assumptions and an example result beside the code. Explain which data is synthetic, what the check detects and what it cannot detect.

That context is especially important when reusing examples with an AI coding agent. A passing replay is evidence about the scenario it ran. An agent's confident description does not expand that evidence. Review changes to fixtures and expected results as carefully as changes to the implementation.

Do not generalize every artifact. Several small, readable scripts can be cheaper to maintain than a framework with configuration nobody understands. Extract a shared component when actual uses reveal what is shared.

## Look for reuse, then ask about cost

A successful first run tells you the intervention worked once. Later work tells you whether it was worth retaining.

Ask the next person who uses it what they could do, where they needed help and what they had to repair. If a test fixture takes longer to update than the investigation it supports, that belongs in the assessment. So does a tool that everyone bypasses because its assumptions no longer match production.

The [investment retrospective](./patterns/investment-retrospective.md) gives a way to make that assessment without pretending that a time-saving estimate proves causation. A reasonable outcome may be to simplify the tool, narrow its purpose, or remove it.

There is a stronger claim behind the title of this collection: earlier work can make later improvements cheaper. A reproducer might lead to reusable scenario builders, which make a comparison harness practical, which allows a risky implementation to be replaced. That sequence is a possibility to investigate. It is not an automatic return on adding tests or tools.

## Read the sources as part of the pattern

Each entry links to established techniques, implementations or practitioner accounts. The pattern names here organize those ideas around a problem; they are not a claim to have invented the underlying methods.

The worked billing examples and their outcomes are illustrative. They are not case studies or measured productivity results. Where a source demonstrates a particular tool, the article explains what carries over and what depends on that tool.

The two earlier collections provide the broader argument: [Software that improves with age](https://grove.github.io/software-that-improves-with-age/) considers how software can become easier to change; [Engineering that compounds](https://grove.github.io/engineering-that-compounds/) asks what engineering leaves behind. You can use this guide without reading either first.

