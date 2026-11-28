# One payment, changing assumptions

*Follow a retained failure into recovery checks, a simpler store and a new business rule.*

The duplicate-payment fix works. Then somebody asks what happens when the worker restarts. Later, the storage design changes. Do you have to build the evidence from scratch each time?

This walkthrough reuses the [original payment fixture](../scenarios/duplicate-payment.json) through those changes. You will see a green check become insufficient, extend it to expose another failure, and carry the resulting checks into a replacement. The final extension changes the meaning of a payment and tests which parts of the earlier work remain useful. Each step includes a prediction to make before running the code.

Use Python 3.10 or later with its standard `sqlite3` module. If you do not already have the repository, get a local copy:

```sh
git clone https://github.com/grove/patterns-of-compounding-engineering.git
cd patterns-of-compounding-engineering
```

Run the commands below separately **from this repository root**. No packages or services are needed. Each run creates a temporary SQLite database and removes it afterward; it makes no network requests and touches no application data. Exit status **1 means the stated expectation failed**; several commands do that deliberately. Invalid command arguments exit 2.

## 1. Keep the failure you already understand

The [introductory lab](../README.md) saved an invoice for 2,400 minor units, two deliveries of `evt_001`, and the expectation: 2,400 paid, one event applied. The new [runner](./replay.py) loads that fixture rather than copying its expected result from an implementation.

**Predict:** what should each delivery leave behind?

```sh
python3 examples/evolving-billing/replay.py run --case duplicate --implementation memory
```

Both checkpoints pass. The balance is stored in SQLite, while the event IDs live in a Python set. The second delivery leaves the balance at 2,400. This is evidence about duplicate delivery during one worker lifetime.

## 2. Ask the same question after a restart

**Predict:** the balance survives reopening the database. Does the set of event IDs survive too?

```sh
python3 examples/evolving-billing/replay.py run --case restart --implementation memory
```

The last checkpoint fails with 4,800 paid and two events applied; the command exits 1. The worker forgot the ID and counted the same event again.

The new capability is small: a `restart` action closes and reopens the connection with a fresh worker. It uses the same event and expectation. Try the design that also stores event IDs:

```sh
python3 examples/evolving-billing/replay.py run --case restart --implementation split
```

That case passes. We have fixed the restart problem. There is still a gap between storing the ID and updating the balance.

## 3. Interrupt the work between writes

**Predict:** if the ID is committed and the balance update never happens, what will a retry do?

```sh
python3 examples/evolving-billing/replay.py run --case after-record --implementation split
```

The final balance stays at zero. The retry finds a recorded ID and skips the missing payment. The command exits 1. Persisting both pieces separately was insufficient.

The `atomic` implementation puts the receipt and balance update in one transaction. Try it against the accumulated cases:

```sh
python3 examples/evolving-billing/replay.py verify --implementation atomic
```

All five cases pass. Their expectations are stated before either implementation runs:

| Case | What the check requires |
| --- | --- |
| `duplicate` | A second delivery of the same ID leaves one applied event |
| `restart` | Reopening the database does not make that ID new again |
| `after-record` | An interruption before commit leaves no payment; retry applies it once |
| `after-effect` | The balance update rolls back with the receipt; retry applies it once |
| `after-commit` | A committed payment survives an interrupted acknowledgment; retry leaves it alone |

The runner raises exceptions at named points and reopens the connection. Python's [SQLite connection context manager](https://docs.python.org/3/library/sqlite3.html#how-to-use-the-connection-context-manager) commits successful work or rolls back on an exception. This exercise checks our use of that behavior. It does not kill a process, interrupt disk writes or test SQLite's [power-failure guarantees](https://sqlite.org/atomiccommit.html).

## 4. Use the recovery checks to compare a replacement

The `ledger` design stores each accepted event once and calculates the balance from those rows. It has no separate stored balance to keep synchronized.

**Predict:** should this change any of the eleven observations in the five cases?

```sh
python3 examples/evolving-billing/replay.py compare
```

The command runs `atomic` and `ledger` on separate, fresh databases using the same cases. It checks every checkpoint, including interrupted states. It requires both agreement and conformance to the fixture's expectations. Agreement alone could preserve a shared defect.

To watch the comparison reject the earlier mistake:

```sh
python3 examples/evolving-billing/replay.py compare --candidate split
```

This deliberately exits 1. The recovery cases have become useful inputs to a second verification tool without being rewritten for either storage design. They still do not establish how to migrate an existing database, or whether summing a large ledger would be acceptably fast.

## 5. Keep the contract when the old implementation goes

**Predict:** can the replacement still be checked without executing the reference?

```sh
python3 examples/evolving-billing/replay.py verify --implementation ledger
```

All five cases pass using only `ledger` and the stated expectations. The reference is no longer required by this acceptance check. The replacement also needs only the receipt table; its stored balance and update path are gone.

The old designs stay in this teaching example so their failures remain reproducible. Removing a real implementation would also require checking existing data, consumers and rollback obligations. Those questions are covered by [Subtraction investigation](../../patterns/subtraction-investigation.md).

## A green suite still has a boundary

Suppose a provider confirms that two **different event IDs** describe the **same business payment**. Our stronger expectation would be one applied payment. Can any of these implementations establish that?

```sh
python3 examples/evolving-billing/replay.py run --case identity-gap --implementation ledger
```

It fails with 4,800 paid. Every implementation here deduplicates event IDs, and none knows business payment identity. The invoice ID identifies the bill; it does not identify the transfer. A real fix needs the provider's identity contract and an appropriate key before more code can help.

`identity-gap` is deliberately outside `verify`'s five event-ID cases. It is a new requirement, not a secretly failing case in the promised contract. The runner prints that scope. This is why the next change must revisit what a green check establishes.

## 6. Change the identity rule

For the next exercise, we supply a **fictional contract** in [domain-cases.json](./domain-cases.json): one settled payment has one stable `payment_id`, but may arrive under different event IDs. Two different payments can contribute to the same invoice. All events belong to one provider and one invoice, and repeated payment IDs carry the same amount.

In a real integration, these statements would need evidence from the provider and the domain owner. Here they are stipulated teaching assumptions. The accompanying [domain runner](./domain.py) tests code against them; it cannot verify the provider's actual behavior.

**Predict:** which identifier can distinguish a repeated notification from another installment? Try each choice:

```sh
python3 examples/evolving-billing/domain.py --identity event
python3 examples/evolving-billing/domain.py --identity invoice
python3 examples/evolving-billing/domain.py --identity payment
```

The event-key version exits 1: two notifications of one payment record 4,800 instead of 2,400. The invoice-key version also exits 1: it handles that duplicate but drops the second legitimate installment, leaving 1,200 instead of 2,400. The payment-key version exits 0 on the five stated cases.

| Case | Independent expectation |
| --- | --- |
| `same-payment` | Two event IDs for one payment produce 2,400 paid and one accepted payment |
| `installments` | Two payment IDs for one invoice produce 2,400 paid and two accepted payments |
| `restart` | A notification with another event ID remains a duplicate after reopening storage |
| `before-commit` | The interrupted receipt rolls back; the later notification records the payment once |
| `after-commit` | A committed receipt survives the interruption; the later notification adds nothing |

The new code adapts the ledger's key. It reuses the earlier delivery interface, transaction behavior, restart action, fault injection and checkpoint runner. It adds domain fixtures and expectations rather than deriving them from the chosen key. The inherited observation name `applied_events` now counts accepted payment records; it does not count every notification received.

This also shows where reuse stops. The script always starts with an empty database. Changing what an existing receipt column means requires a data migration strategy that the exercise does not provide. Conflicting amounts, refunds, multiple providers, multiple invoices and concurrency are outside the stated contract. A missing payment ID produces an error rather than a guessed identity.

## 7. Use the case to question the next change

These are human exercises, with no recorded results or automatic score:

- **A policy changes.** Suppose the next provider uses payment IDs unique only within an account. Identify the assumption that would fail, the evidence needed to establish the new scope and the stored data affected. Do not change the expected result merely to obtain a green run.
- **Another team adopts the method.** Give it the domain case and the normal repository entry point. Ask what fits its service, what background knowledge is missing and which check it would need to add. Count adaptation and teaching. Copying the script is not enough to establish independent use.
- **An AI model changes.** Give two assistants the same bounded investigation and independently maintained acceptance cases. Inspect whether they find the contract, reject invoice identity and notice the migration gap. Keep model versions, available context and review effort visible. These cases can reject particular mistakes; they cannot rank models generally or establish safe deployment.

The concrete opportunity is a future reconciliation check: reviewed payment identities plus a restartable ledger might make discrepancies easier to investigate. Build it only when that question matters. Record which pieces help and what new evidence is needed instead of treating this walkthrough as proof of organizational compounding.

## Try the investigation with an AI assistant

The lab can also support a small learning exercise. This is a proposed use of the existing checks, not a report that AI improved anyone's understanding or delivery time. Start with one question: why can a green duplicate-delivery replay still miss a lost or repeated payment?

Before asking for an explanation, predict what a restart, an interrupted transaction and a second event ID might change. Then ask an assistant to inspect the fixture and the implementations, suggest competing explanations, and identify a check that distinguishes each one. Require it to cite the relevant source and to separate the event-ID contract from business payment identity. Keep the fixture's expectations fixed during this exercise.

Run these commands separately from the repository root:

```sh
python3 examples/evolving-billing/replay.py run --case restart --implementation memory
python3 examples/evolving-billing/replay.py run --case restart --implementation split
python3 examples/evolving-billing/replay.py run --case after-record --implementation split
python3 examples/evolving-billing/replay.py run --case after-record --implementation atomic
python3 examples/evolving-billing/replay.py run --case identity-gap --implementation ledger
```

The first command exits 1 because the worker forgets the event ID; the second exits 0 because the ID survives. The third exits 1 because a committed receipt can outlive a missing balance update; the fourth exits 0 because those writes share a transaction. The fifth exits 1 because a different event ID is treated as a different payment. That last failure needs a clarified identity rule before a correction can be specified.

Explain those results yourself before reading the assistant's explanation. Ask it to challenge one of your assumptions or propose a nearby case these checks cannot settle. Check that proposal against the code and the stated limits. A plausible account of a concurrent-worker failure is still a hypothesis: this runner does not exercise concurrency.

For another engineer, turn one retained case into a prediction exercise. Hide the answer while they decide what survives a restart or interruption, then compare their explanation with the observed checkpoints. On a later, unfamiliar case, look for whether they identify the relevant contract and missing evidence. Repeating the assistant's explanation of the original case is a weaker check of understanding.

To try transfer, let a neighboring team examine whether its own delivery contract has the same assumption. It may use a different key, have different transaction boundaries or rely on an external side effect. Ask it to name one applicable check and one reason the lab's design would not carry over unchanged. This is a proposed adaptation exercise; the repository contains no results from another team.

Keep only useful corrections to the question, source links or exercise. Count the time spent verifying the assistant's suggestions and explaining false leads. If it adds little, use the replay without it. [Friction to hypothesis](../../patterns/friction-to-hypothesis.md) helps choose the investigation, [verified retrieval](../../patterns/verified-retrieval.md) checks the handoff, and [investment retrospective](../../patterns/investment-retrospective.md#review-the-way-you-look-for-improvements) asks whether the method earned its upkeep.

## What carried forward, and what it cost

| Earlier work reused | New capability | Additional work still required |
| --- | --- | --- |
| Original event and reviewed expectation | Restart replay | A lifecycle action and a persistent balance |
| Replay and restart handling | Interruption checks | Fault locations and expectations before and after commit |
| Those cases and observation format | Comparison of implementations | A replacement and checks at every checkpoint |
| Expected outcomes independent of the reference | Acceptance after replacement | Running the cases without the old implementation |
| Recovery runner and ledger interface | Verification of a changed identity rule | A reviewed domain contract, independent counterexample and key adapter |

You can inspect these connections in `cases()`, `run_steps()`, `compare()` and `verify()` in the [replay source](./replay.py), then `domain_cases()` and `KeyedLedger` in the [domain extension](./domain.py). The cases are deliberately small enough to read alongside the implementation. Keep them that way: refund rules, concurrent workers, external side effects and real process crashes need further work and may need a different harness.

This is an executable teaching example assembled as one exercise. It demonstrates reuse and failure detection. It does **not** measure whether a team builds later capabilities more cheaply, whether the investment pays back its upkeep, or whether the effect continues. The [measurement essay](https://grove.github.io/engineering-that-compounds/essays/measuring-the-capacity-for-change.html) explains how to investigate those claims.

For your own next change, look for one existing case you can carry into a new question. Note what needed adapting. If the adaptation costs more than a focused new check, keep the simpler check.
