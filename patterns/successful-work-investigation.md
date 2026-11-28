# Successful work investigation

*Find out what made ordinary work succeed, especially when the plan needed adjusting.*

A database migration finishes without an incident. During the rollout, an engineer notices an unusual lock, pauses the next batch and checks with the team running a background job. The ticket closes with “migration complete.” The adjustment that made the migration work disappears from view.

This hypothetical example is a reason to investigate successful work. Use the pattern when a difficult change went well, an operator made a useful adjustment, or you are about to automate work whose interruptions you do not yet understand. Include routine successes too; choosing only dramatic rescues can hide the conditions that usually make work manageable.

## Reconstruct what people could see at the time

Take one completed change and talk to the people involved while they still remember it. Use the rollout log, relevant messages and system observations to walk through the decisions. A short conversation may be enough.

Ask what they expected, what caught their attention and which alternatives were available. What did the engineer see in the lock information? Why was that signal meaningful? How did they know whom to contact? What allowed the next batch to wait?

Keep uncertainty visible. Knowing that the deployment succeeded does not tell you that every action was necessary, or that the same decision would always work. Do not turn the conversation into a search for the one person who “saved” the migration. The useful explanation may involve good telemetry, small batches, a cooperative neighboring team and time to pause.

## Look for conditions another person could use

In this example, the investigation might reveal four different needs:

| What helped | A possible next step |
| --- | --- |
| The engineer recognized a lock pattern | Add a small rehearsal with the expected observation |
| The rollout could pause between batches | Preserve that option in the deployment tool |
| Another team knew the background job's schedule | Put the current owner and schedule near the migration instructions |
| Someone had time to investigate | Keep that capacity in the plan for the next migration |

Each is a candidate to examine, not a required artifact. The existing tools may already provide enough help. The finding may instead explain why removing a pause or handoff would make the system harder to operate.

Before automating the adjustment, determine what it protected. A fixed rule to stop on every lock could prevent useful work. A rule to ignore brief locks could miss an unfamiliar pattern. Retaining visible information and an escalation route may be a better investment than automating the decision.

## Rehearse a nearby case

If recognizing the lock mattered, use an isolated environment or a reviewed recording to prepare a variation. Let another engineer explain what they see, what they would investigate next and what information is missing. Change one condition: perhaps the lock is harmless, the background job has a new owner, or pausing has a cost of its own.

The exercise should leave room for more than one sound response. Check whether the engineer notices the relevant conditions and can justify an action. Memorizing the original sequence does not establish that they can adapt.

An AI assistant can assemble a timeline from permitted records or propose variations. Participants must check its reconstruction. A neat account written after the fact can conceal the uncertainty people actually faced. Keep synthetic variations labeled and their expected observations independently reviewed.

## Follow the investment into later work

On the next migration, look for whether the needed information and options are available without the original engineer's intervention. Count rehearsal, documentation and maintenance effort. Notice whether a new rule causes unnecessary stops or leaves people less willing to use judgment.

A second successful migration is useful evidence about how the work was done. It cannot prove that an outage would otherwise have occurred. Claims about avoided incidents need more than a plausible story.

Stop when the investigation no longer offers a consequential decision or a useful lesson. Do not require a success review for every ticket. If a control is a legal, safety or security obligation, investigate how it works and take any proposed change through its owner; this exercise does not authorize removing it.

## Where the idea comes from

Hollnagel and colleagues' [From Safety-I to Safety-II](https://www.era.europa.eu/system/files/2022-10/From%20Safety-I%20to%20Safety-II%20White%20Paper.pdf) examines how everyday adjustments help work succeed under varying conditions. It extends attention beyond adverse outcomes. Here the practical question is which conditions another engineer needs to do the work well.

[Learning from things that go right](https://grove.github.io/engineering-that-compounds/essays/learning-from-things-that-go-right.html) develops the argument. [Incident to instrument](./incident-to-instrument.md) remains useful after failures. [Verified retrieval](./verified-retrieval.md) can test whether the knowledge from either kind of investigation reaches the next person.
