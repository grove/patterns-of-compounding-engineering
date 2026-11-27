# Subtraction investigation

*Find out what a piece of software still does for people before removing it.*

Every pricing change touches a legacy export format. The format has its own serializer, fixtures and compatibility flag. Nobody on the team remembers the last customer who asked for it. Removing it sounds sensible; proving that removal is safe sounds like a project nobody has time to start.

A subtraction investigation gives that question a small, explicit budget. Pick one candidate, gather evidence about its remaining obligations, and decide whether to remove it, narrow it or leave it alone. A decision to keep it can be a useful result if the investigation uncovers a real consumer.

This pattern fits obsolete feature branches, compatibility layers, jobs, configuration options and duplicated paths. Start where there is an observed cost: repeated edits, support work, operational confusion or an expensive dependency. A large directory is a poor reason by itself.

## Define the candidate precisely

For the fictional subscription service, take the old monthly invoice CSV export. The proposed removal includes its endpoint, serializer, scheduled delivery job and rollout flag. It does not include historical invoice records or the newer export format.

Write down why the team cares. Perhaps every new invoice field requires updating two serializers, and the old format prevents removal of an outdated library. Those are costs another engineer can verify. “Cleaner architecture” leaves too much room for disagreement.

Check ownership early. A service may belong to engineering while its output is part of another team's monthly work. Name the person who can confirm that obligation; a repository owner is not necessarily the person who can approve ending a customer-facing capability.

## Gather evidence from different directions

Search the code and configuration for callers, scheduled jobs, feature-flag branches, scripts and deployment settings. Follow how names are constructed: a text search for an endpoint can miss a generated URL or a job registered through configuration. Check adjacent repositories and runbooks where they are available.

Then inspect runtime evidence. Establish what the signal measures before interpreting a zero:

- Does the counter cover every deployment, account and invocation path?
- Are requests sampled, filtered or dropped when telemetry fails?
- Does the observation period include the relevant billing or reporting cycle?
- Is this path normally used only during recovery or a provider outage?

In the fictional example, access logs show no requests to the old download endpoint. The scheduled job still writes files to a shared bucket, however, and a finance process reads that bucket directly at month end. Endpoint logs say nothing about that consumer.

Record blind spots. If storage access cannot be attributed reliably, use another source of evidence: the consumer's job configuration, a controlled rehearsal, or confirmation from the people running it.

## Distinguish use from obligation

A capability may be unused this month and still be required. An annual export, an emergency recovery route or a contractual format can survive a long quiet period. The relevant business cycle determines the observation window; a convenient number of days does not.

Ask consumers which behavior they need. They may depend on a column order or a delivery schedule rather than the whole implementation. In this example, a small adapter around the newer export might satisfy the remaining monthly importer and allow the old serializer to go. That still leaves a supported adapter, with an owner and a test.

Keep data retention separate from code retirement. Removing a delivery job does not establish that its historical outputs may be deleted. A destructive data migration also changes what rollback would require. Resolve those decisions explicitly before treating the old implementation as disposable.

## Disable it before making recovery expensive

When feasible, separate stopping use from deleting the implementation. First migrate the identified consumer and verify its required behavior. Then disable the old path for a controlled scope, while keeping a tested way to restore it.

For the CSV example, the consumer could import a synthetic month-end file from the replacement before its live schedule changes. Compare the fields that matter to the import, including credits and cancelled invoices. A byte-for-byte comparison is useful only if byte identity is actually required.

An illustrative removal record might read:

```text
Candidate: legacy monthly CSV delivery
Cost: duplicate serializer changes and an otherwise unused dependency
Remaining consumer: finance month-end import
Replacement evidence: consumer rehearsal with credit and cancellation cases

Disable: stop the old delivery schedule after the consumer switches
Observe: successful replacement delivery and completion of the import
Restore if: the import fails or a required field cannot be reproduced
Restore method: re-enable the retained job against compatible source data
Delete after: the agreed billing-cycle checks pass and the owner signs off
```

Fill this with actual evidence, a named owner and a review date. A flag that can be switched back is useful only if the old path still works with current data. Test restoration before relying on it. If a rollout changes data irreversibly, design the migration and recovery plan first; a flag cannot undo lost information.

Stripe's [Online migrations at scale](https://stripe.com/blog/online-migrations) describes moving reads and writes in stages before removing the old data model. That separation is useful here: ending dependence on an implementation and deleting it are different steps, with different evidence.

## Finish the removal

Once the agreed conditions hold, remove the obsolete code, flag, tests for retired behavior, job definitions and unused dependencies. Update documentation and alerts that would otherwise send someone looking for a vanished path. Preserve tests for obligations that still exist, moving them to the replacement where appropriate.

Leave a short record of the decision and the evidence behind it. This lets a future engineer understand why an old customer setting no longer has an effect. Keep the signal that demonstrates the replacement is working for as long as it remains useful, then remove temporary instrumentation as well.

GitHub describes a concrete cleanup script in [How we ship code faster and safer with feature flags](https://github.blog/engineering/infrastructure/ship-code-faster-safer-feature-flags/). It rewrites Ruby branches after rollout and leaves some affected tests for an engineer to resolve. Automation can handle repetitive edits once the intended behavior is known. It cannot decide whether an unknown consumer may still need the old behavior.

## Set a stopping point

Time spent investigating removal has an opportunity cost. Stop if a low-maintenance component turns out to have a legitimate consumer and replacing it costs more than keeping it. Leave the ownership and dependency findings beside the code so the next person can make progress from there.

For a frequently changed component, record what disappears from subsequent work: a serializer no longer needs updating, an exception no longer enters code review, or a dependency upgrade loses a blocker. Lines deleted are a useful description of the patch, but they do not establish the benefit.

Repeated investigations may justify better usage instrumentation or a standard removal record. Build those when the repetition is visible. A fleet-wide deletion dashboard would be an expensive first response to one stale export.

## Related patterns

- [Differential verification](./differential-verification.md) helps compare a replacement against the behavior a consumer still needs.
- [Architectural ratchet](./architectural-ratchet.md) can prevent new dependencies on a component while existing consumers move away.
- [Investment retrospective](./investment-retrospective.md) applies the same scrutiny to the team's own tools and checks.
