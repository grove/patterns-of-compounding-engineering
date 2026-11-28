# Retire the workaround

*After removing a constraint, examine the procedure that grew around it.*

A team once shared a single test environment. It introduced a booking calendar, a weekly meeting and a release coordinator to keep people from overwriting one another's work. Later, each change gained its own isolated environment. Engineers could run investigations independently, but they still booked slots and waited for the meeting.

The new infrastructure removed a technical constraint. The organization kept paying for the arrangement built around it.

This hypothetical example is about retiring that arrangement. [Subtraction investigation](./subtraction-investigation.md) traces the obligations behind software proposed for removal. This pattern asks what remains of a procedure's purpose after the condition that justified it has changed. A calendar, approval step, status report or recurring meeting can acquire duties that were never in its original description.

## Find the original reason and the current job

Start with a specific procedure that delays useful work. Ask why it was introduced, then look at what people actually do through it now. The first answer suggests a removal candidate; the second determines whether removal is justified.

For the booking meeting, review recent agendas and follow a few changes through to release. Include an awkward change, not only routine ones. The coordinator might use the meeting to reserve the shared environment, alert support to a customer-visible change, identify a database migration and check that someone is available to respond after release.

Only the first job necessarily disappeared when isolated environments arrived. If all four jobs are bundled into one meeting, cancelling the meeting without assigning the remaining work may cause a failure that appears to vindicate the whole old arrangement.

Speak with the people who rely on the procedure. They may know about a duty that leaves no repository trace. Ask what would go wrong if the next change skipped it, and what evidence would establish that the concern is covered elsewhere. This is also the point to identify who can revise the working agreement.

## Check that the constraint really moved

An isolated environment can still depend on a shared test account, a scarce external sandbox or a common data-refresh job. If investigations interfere through one of those dependencies, the booking system may still be doing useful work.

Rehearse the relevant overlap. Can two ordinary changes be evaluated at once without overwriting data, consuming one another's limits or producing misleading results? Can an engineer tell which version and configuration an environment contains? Examine the failure cases the original booking rule was intended to prevent.

A successful rehearsal supports changing the rule for those conditions. It does not establish that every release can proceed independently. Shared production state and customer commitments may still require coordination after testing becomes parallel.

The useful finding may be that the platform investment is incomplete. Repairing the remaining shared dependency could be a better next step than either retaining the entire process indefinitely or pretending it is already obsolete.

## Remove one dependency from the procedure

Choose a narrow trial with the people who own the remaining duties. In this example, let changes using verified isolated environments proceed through testing without a booking. Keep the existing release requirements. Put the revised rule where engineers and agents already look when preparing a change.

If customer communication still matters, connect it to the work that triggers it. A change to a public workflow may need support preparation; an internal refactoring may not. If a database migration needs coordination, make that requirement discoverable from the migration. Avoid recreating the old meeting as a checklist on every change just to preserve a familiar approval moment.

Use a current change to test the arrangement. Agree in advance what would cause the trial to stop: interference between environments, a missed release obligation or extra coordination that exceeds the waiting removed. Keep a clear way to restore booking for work that still needs it. The trial changes a working agreement; it does not grant new deployment authority.

Once the trial supports the narrower rule, remove its obsolete reminders, calendar instructions and duplicate status requests together. Leaving conflicting instructions in place invites people to keep following whichever version looks safest.

## Notice who inherits the work

The coordinator may have spent time resolving misunderstandings before the meeting. Removing their role from the workflow could distribute that work across several engineers and support staff. Ask those people what changed. Count their preparation and interruptions, not just the time no longer spent in the room.

There may also be value worth preserving that was never part of the approval process. A junior engineer might learn why a migration needs a particular sequence by listening to the discussion. The team can retain that learning through a focused walkthrough of a consequential change. An obsolete booking requirement is an expensive way to preserve an accidental teaching opportunity.

Pay attention to where waiting goes. Testing that starts immediately but then waits in a larger release queue has removed one delay without improving the whole route to value. That may still be a useful advance, especially for investigations that never ship, but report the outcome that actually changed.

## Check a later kind of work

For ordinary changes, look for evidence that testing can begin independently, required communication still happens and the total coordination burden is worthwhile. Record failed cases and the revised boundary as well as successful ones. Fewer meetings alone establish little.

Then ask what the change permits the team to try. Perhaps engineers can compare two interface designs while a third person investigates a production failure. If those investigations were previously impractical because they needed the same booking and coordination, the retired procedure has helped make a new working method possible.

That is a proposal to test, not a reason to invent more parallel work. Choose an investigation whose answer could change a decision. Record how the isolated environments and revised agreement helped, along with any new comparison or integration costs. A second capability may depend on both the technical investment and the removal of the old procedure.

Keep a short explanation with the revised working agreement: what constraint the procedure addressed, what changed, which duties remain and what would justify reconsidering it. That is enough to answer the next colleague who asks why nobody books the environment anymore.

## Sources and related patterns

The site's [Theory of Constraints discussion](https://grove.github.io/compounding-engineering/foundations.html#transformation) treats improvement as a repeated examination of what limits valuable outcomes. This pattern addresses an easy-to-miss consequence: rules introduced around an earlier constraint may continue limiting work after that constraint moves.

Use [Friction to hypothesis](./friction-to-hypothesis.md#challenge-the-premise) when the rule's purpose is uncertain, [Subtraction investigation](./subtraction-investigation.md) for software and data affected by retiring it, and [Investment retrospective](./investment-retrospective.md) to examine the full cost of the technical change and the working agreement together.
