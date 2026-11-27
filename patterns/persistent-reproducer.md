# Persistent reproducer

*Keep the conditions that made a failure possible.*

Consider a subscription service that occasionally applies the same payment twice. A developer spends an afternoon reconstructing the sequence: the provider sent an event, the handler updated the balance, the response was lost, and the provider tried again. The fix is small. The investigation was most of the work.

If the pull request contains only the fix, the next developer inherits the conclusion without the means to check it. A sentence in an incident report helps, but it still leaves someone to reconstruct the setup. Preserve an executable version of the failure while those details are fresh.

The subscription service in this guide is an illustrative example. Duplicate delivery is a real integration concern: [Stripe documents both duplicate events and delivery without a guaranteed order](https://docs.stripe.com/webhooks#event-delivery-behaviors). Your reproducer needs to exercise the behavior of your own handler, including the assumptions it makes about those deliveries.

## Keep a small, complete case

A useful reproducer contains four things: the starting state, the actions that trigger the failure, the result you expect, and a command that checks it. Include a short explanation of why that result is correct. Without the explanation, an inconvenient assertion can look like something to update when the implementation changes.

For the payment example, begin with one unpaid invoice and two deliveries of the same successful payment event. Check the amount recorded as paid and the number of applied events. A check that merely counts HTTP responses could pass while the account is still wrong.

The [billing lab](../examples/README.md) includes a small version of this case. From the repository root, run:

```sh
python3 examples/billing_lab.py replay --implementation buggy
python3 examples/billing_lab.py replay --implementation fixed
```

The invoice amount is 2,400 minor units. Both deliveries carry event ID `evt_001`. The buggy implementation records 4,800 as paid and applies two events; the corrected one records 2,400 and applies one. The first command deliberately exits with status 1. The second runs the same scenario successfully against the corrected implementation. The data and expectation stay the same; only the implementation changes. Keep that distinction visible in a real incident fix too.

The lab models sequential delivery in memory. It does not establish that a production handler survives concurrent requests, process crashes, or a database transaction that commits just before its acknowledgement is lost. Those are separate cases to reproduce when they matter.

## Capture the cause, then remove the clutter

Start with whatever reproduces the failure reliably. That might be a script, a failing integration test, or a recorded sequence of commands. Reduce it after it works. Trying to design the ideal fixture before understanding the bug can slow the investigation considerably.

Remove accounts, fields and actions one at a time, rerunning the old implementation after each removal. Stop reducing when another deletion would hide the cause or make the example harder to understand. The shortest possible input is not always the best explanation.

Check the case against a known failing revision before accepting it as regression coverage. A passing test added after the fix may never have exercised the defect. If running the old revision is impractical, temporarily restore the specific defect in an isolated checkout and check that the assertion catches it. Record any remaining gap rather than treating a successful run as proof.

A useful failure message names the observation: the same payment affected the balance twice. A stack trace from fixture setup is evidence that the case did not run.

## Control the parts that would change tomorrow

Give the case its own state. Replace live payment calls with a local boundary that can record attempted effects. Use synthetic identifiers and amounts while preserving relationships that matter, such as the repeated event ID. Copying an entire production payload usually preserves more sensitive and irrelevant material than the test needs.

Supply the clock when the failure depends on a deadline. Record the timezone and the relevant instant explicitly. Supply random inputs or a seed when randomness matters. A seed alone cannot reproduce an uncontrolled thread schedule or a response from a live service.

For a race, introduce a controllable pause at the contested operation and drive both workers to it. Sleeping for an arbitrary duration leaves the test dependent on machine load. For a crash, retain the durable state before and after the interruption and define which operation is retried. These additions belong only where the failure requires them.

[Hypothesis's discussion of flaky failures](https://hypothesis.readthedocs.io/en/latest/tutorial/flaky.html) gives concrete examples of the trouble caused by leftover state and uncontrolled randomness. The practical question is whether another run sees the same relevant conditions, including when it follows other tests.

## Put it where it will be used

For an ordinary regression, the existing test suite is usually the right home. Name the test after the behavior, link the incident or issue, and leave the reason beside the assertion. There is little value in creating a parallel catalogue that engineers must remember to run.

Some failures need a slower environment or several processes. Keep those cases close to the code, with one documented command and their prerequisites. Choose a sensible trigger: a relevant component change, a nightly run, or a release rehearsal. A twenty-minute reproduction need not delay every documentation edit.

Property-based tools can preserve failures automatically, but their caches are not a permanent specification. [Hypothesis recommends an explicit `@example` for an input that must always run](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html), because its stored examples can be invalidated by changes to tests or versions. Keep the meaningful case in a form the team can review.

## Decide what is worth maintaining

This pattern is particularly useful when creating the conditions was expensive, the failure can recur, or the case will help evaluate a replacement. A simple typo already covered by a focused test does not need an additional replay package.

Every retained scenario has a cost. Dependency upgrades may break it; changed product rules may invalidate its expectation. Give it an owner through the component that owns the behavior. When the rule changes, update the explanation as well as the result. If a broader test now covers the same failure clearly, delete the redundant machinery.

Be suspicious of a replay archive that nobody can run without its author. Ask someone outside the investigation to execute the command and explain the assertion. Use their questions to improve the instructions and setup.

## What later work gets easier?

The first return is modest: another engineer can reproduce this failure without repeating the investigation. Note how long setup takes and whether a later change actually reuses the case. Counting retained scenarios says little about their value.

Several cases may reveal reusable ways to create accounts or drive events. Extract those into [scenario builders](./scenario-builders.md) when the repetition becomes visible. A repeated cause may suggest an [executable invariant](./executable-invariants.md) that checks many more cases. The same scenario can then become input to [differential verification](./differential-verification.md) during a replacement. Each step should earn its upkeep through a real use.
