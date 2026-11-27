# Architectural ratchet

*Stop new dependency violations today while chipping away at the old ones.*

An invoice calculator should not need payment gateway credentials just to run. Yet in plenty of older codebases, a handful of billing modules reach straight into the gateway client to fetch customer details. Tests become harder to wire up, and swapping payment providers turns into a scavenger hunt.

The team agrees on a rule: billing calculations receive the data they need as inputs and never import the payment gateway. You write the architecture test, run it, and immediately hit fifteen existing violations. Fixing all fifteen before shipping blocks everything else, while leaving the check off lets new violations keep creeping in.

A ratchet splits the difference. Record the exact violations that exist today, fail CI on any new one, and shrink the baseline automatically as people clean up old edges.

## Pick a boundary that buys you something

Tie the ratchet to work the team expects to do soon: running invoice calculations without gateway mocks, stopping one service from querying another's tables, or breaking a module cycle that slows down builds. A rule added purely to keep a package diagram tidy tends to turn into friction.

Check that your tool can see the dependency you care about. An import checker catches a forbidden reference to a database client, whereas raw SQL reading another team's table slips right past it. Inspect the initial findings before turning enforcement on, since generated code, tests, and intentionally shared interfaces often need separate handling. Avoid putting a blanket ignore on `legacy/`, or that folder becomes a permanent dumping ground for fresh coupling.

## Record each violation by identity

Do not implement a ratchet as "fail if violation count > 5." If someone removes one old violation and adds a brand-new one somewhere else, the count stays at 5 while the boundary rots.

Store the identity of each accepted violation instead:

```text
rule: billing-domain-without-payment-gateway
origin: billing.domain.MonthlyInvoice.build
target: payments.gateway.Client.fetchCustomer
kind: method-call
```

Choose the granularity deliberately. Module-to-module edges stop new modules from coupling; member-level edges also stop existing offenders from adding more calls across the same seam. Keep line numbers out of the baseline so ordinary edits do not create diff noise.

On every run, compare current findings against the committed baseline. Any finding missing from the baseline fails the build. Any baseline entry that is no longer in the code drops out of the baseline in the same pull request so nobody re-introduces it later. Also guard against silent scanner bugs: if the build step failed to compile the expected classes, an empty dependency graph should fail the test.

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

Commit the violation store to git. Generate it once after reviewing every existing entry, then lock down the config so a missing store cannot be silently recreated:

```properties
freeze.store.default.path=architecture/violations
freeze.store.default.allowStoreCreation=false
freeze.refreeze=false
```

When tests run locally with store updates enabled, ArchUnit trims resolved entries from the store. In CI, verify that any shrinkage was committed:

```sh
git diff --exit-code -- architecture/violations
```

Run that diff check only after the architecture tests pass, and make sure the store is already tracked in git. Never enable `freeze.refreeze=true` in CI, since that would rubber-stamp every new violation a pull request introduces.

## Treat baseline edits like design reviews

Renaming or moving a class can make one violation disappear and an identical one appear under the new name. Review the pair; migrating the entry makes sense when the coupling stayed the same. What you want to block is someone regenerating the whole file and smuggling in unrelated new dependencies.

Keep rule IDs stable when you refactor the test itself, and explain any rule changes in the pull request. [Apache Flink's architecture test guide](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md) is a good real-world example of managing frozen violation stores at scale.

For each exemption, note *why* it is still there and what condition removes it, such as finishing a customer migration. Concrete removal conditions age far better than arbitrary calendar dates.

## Prove both directions on day one

Start with one boundary connected to active work. Walk through the initial violations with someone who owns that area, commit the check and baseline together, and test both directions before enabling it for everyone: confirm that adding a forbidden import breaks the check, and remove one small violation to confirm its baseline entry disappears.

Pay down old violations opportunistically when work already touches those files. Forcing unrelated cleanup into every pull request is the fastest way to make engineers resent the check.

## Watch out for freezing the wrong architecture

A ratchet entrenches a misguided boundary just as loyally as a good one. Business domains evolve, and a split that made sense two years ago can turn into pure friction once the product shifts.

Re-examine the rule whenever ordinary features keep needing exemptions, when complying requires awkward indirection, or when the original reason for the boundary is gone. A shrinking violation list only tells you the list is shrinking. Check the outcome you wanted in the first place: can invoice calculations run without gateway setup now, and do payment provider changes stay contained?

Once the last baseline entry vanishes, delete the frozen store and turn the check into a plain, permanent rule.

## How it connects and sources

Ratchets often start from a recurring catch turned into a [review comment to guardrail](./review-comment-to-guardrail.md) that runs into legacy violations. Run the check through a [capability command](./capability-command.md) so local runs match CI, use it alongside a [subtraction investigation](./subtraction-investigation.md) to stop new callers from hooking onto code you plan to delete, and check whether the boundary still earns its keep in an [investment retrospective](./investment-retrospective.md).

- [ArchUnit: Freezing Arch Rules](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules): frozen violation stores, configuration flags, and line-insensitive matching.
- [Apache Flink: architecture tests](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md): a live project's workflow for reviewing and shrinking frozen violation baselines.
