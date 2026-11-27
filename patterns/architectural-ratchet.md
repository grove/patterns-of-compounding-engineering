# Architectural ratchet

*Stop new dependency violations today while chipping away at the old ones.*

An invoice calculator should not need payment gateway credentials just to run. Yet in plenty of older codebases, a handful of billing modules reach straight into the gateway client to fetch customer details. Tests get harder to wire up, and swapping payment providers turns into a scavenger hunt.

The team agrees on a rule: billing calculations take the data they need as inputs and never import the payment gateway. You write the architecture test, run it, and immediately get fifteen existing violations. Fixing all fifteen before shipping stalls everything else; leaving the check turned off lets violation sixteen land next Tuesday.

A ratchet splits the difference. Record the exact violations that exist today, fail CI on any new one, and shrink the baseline automatically as people clean up old edges.

## Pick a boundary tied to real work

Connect the ratchet to something the team expects to do soon: running invoice calculations without gateway mocks, stopping one service from querying another's tables, or breaking a module cycle that slows down builds. A rule added just to keep a package diagram neat turns into friction fast.

Check that your tool can actually see the dependency you care about. An import checker catches a forbidden reference to a database client, while raw SQL reading another team's table slips straight past it. Read the initial findings before turning enforcement on, since generated code, tests, and intentionally shared interfaces often need separate handling. Do not slap a blanket ignore on `legacy/`, or that folder turns into a permanent dumping ground for fresh coupling.

## Record violations by identity, not by count

Never write a ratchet as "fail if violation count > 5." If someone removes one old violation and introduces a brand-new one somewhere else, the count stays at 5 while the boundary rots.

Store the identity of each accepted violation instead:

```text
rule: billing-domain-without-payment-gateway
origin: billing.domain.MonthlyInvoice.build
target: payments.gateway.Client.fetchCustomer
kind: method-call
```

Pick the granularity on purpose. Module-to-module edges stop new modules from coupling; member-level edges also stop existing offenders from adding more calls across the same seam. Keep line numbers out of the baseline so ordinary edits do not churn the diff.

On every run, compare current findings against the committed baseline. Anything missing from the baseline fails the build. Anything in the baseline that is no longer in the code drops out in the same pull request so nobody re-introduces it later. Guard against silent scanner bugs too: if compilation failed and produced an empty dependency graph, fail the test instead of celebrating zero violations.

## How it looks in Java with ArchUnit

[ArchUnit's frozen rules](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules) build this workflow straight in: they record existing violations, fail on new ones, remove resolved ones from disk, and ignore line-number shifts by default.

Here is an adaptation sketch for a Java codebase (separate from this repository's Python billing lab), assuming ArchUnit's `noClasses` and `freeze` static imports:

```java
ArchRule rule = freeze(
    noClasses().that().resideInAPackage("..billing.domain..")
        .should().dependOnClassesThat()
        .resideInAPackage("..payments.gateway..")
).as("billing-domain-without-payment-gateway");

rule.check(importedClasses);
```

Commit the violation store to git. Generate it once after reviewing every existing entry, then lock down the config so a missing store cannot be recreated silently:

```properties
freeze.store.default.path=architecture/violations
freeze.store.default.allowStoreCreation=false
freeze.refreeze=false
```

When tests run locally with store updates enabled, ArchUnit trims resolved entries from the store. In CI, check that any shrinkage was actually committed:

```sh
git diff --exit-code -- architecture/violations
```

Run that diff check only after the architecture tests pass, and make sure the store is already tracked in git. Never turn on `freeze.refreeze=true` in CI, or it will quietly approve every new violation a pull request introduces.

## Treat baseline edits like design reviews

Renaming or moving a class makes one violation vanish and an identical one appear under the new name. Review the pair; migrating the entry makes sense when the coupling stayed the same. What you want to block is someone regenerating the whole file and smuggling in unrelated new dependencies.

Keep rule IDs stable when you refactor the test itself, and explain rule changes in the pull request. [Apache Flink's architecture test guide](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md) is a solid real-world example of managing frozen violation stores at scale.

For each exemption, note *why* it is still there and what condition removes it, like finishing a customer migration. Concrete removal conditions age much better than arbitrary calendar dates.

## Prove both directions on day one

Start with one boundary tied to active work. Walk through the initial violations with someone who owns that area, commit the check and baseline together, and test both directions before enabling it for everyone: confirm that adding a forbidden import breaks the check, and delete one small violation to confirm its baseline entry disappears.

Pay down old violations opportunistically when work already touches those files. Forcing unrelated cleanup into every pull request is the quickest way to make engineers hate the check.

## Watch out for freezing the wrong architecture

A ratchet defends a bad boundary just as loyally as a good one. Domains change, and a split that made sense two years ago can turn into pure drag once the product moves on.

Re-examine the rule whenever ordinary features keep needing exemptions, when complying requires awkward indirection, or when the original reason for the boundary is gone. Also watch the tension with [competing prototypes](./competing-prototypes.md): exploratory spikes sometimes need to cross an existing boundary to test a different design, so keep throwaway spikes outside the ratchet until the team decides whether the boundary itself should move.

A shrinking violation list only tells you the list is shrinking. Check the outcome you actually wanted: can invoice calculations run without gateway setup now, and do payment provider changes stay contained? Once the last baseline entry vanishes, delete the frozen store and turn the check into a plain, permanent rule.

## What a ratchet makes practical, and sources

Without a ratchet, teams end up choosing between a big-bang rewrite they never have time for and a slow slide into more coupling. Freezing the baseline lets you clean up a messy boundary across ordinary feature work instead of stopping the roadmap.

Ratchets often start from a recurring catch turned into a [review comment to guardrail](./review-comment-to-guardrail.md) that runs into legacy violations. Run the check through a [capability command](./capability-command.md) so local runs match CI, pair it with a [subtraction investigation](./subtraction-investigation.md) to stop new callers from attaching to code you plan to delete, and check whether the boundary still earns its keep in an [investment retrospective](./investment-retrospective.md).

- [ArchUnit: Freezing Arch Rules](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules): frozen violation stores, configuration flags, and line-insensitive matching.
- [Apache Flink: architecture tests](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md): a live project's workflow for reviewing and shrinking frozen violation baselines.
