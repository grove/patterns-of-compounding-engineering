# Architectural ratchet

*Stop new dependency violations today while chipping away at the old ones.*

An invoice calculator shouldn't need payment gateway credentials just to run. Yet in plenty of older codebases, a handful of billing modules reach straight into the gateway client to look up customer details. Every test gets harder to wire up, and swapping payment providers turns into a scavenger hunt.

The team agrees on a rule: billing calculations receive the data they need as inputs and never import the payment gateway. You write the architecture test, run it, and immediately hit fifteen existing violations. Fixing all fifteen before shipping blocks everything else; leaving the check off lets violations keep creeping in.

A ratchet splits the difference. Record the exact violations that exist today, fail CI on any new one, and shrink the baseline automatically as people clean up old edges.

## Pick a boundary that actually buys you something

Don't add a ratchet just to make a package diagram look tidy. Tie it to work the team expects to do soon: running invoice calculations without gateway mocks, stopping one service from querying another's tables, or breaking a module cycle that makes builds painful.

Make sure the tool can actually see what you care about. An import checker catches a forbidden dependency on a database client, not raw SQL reading another team's table. And inspect the initial findings before turning enforcement on: generated code, tests, and intentionally shared interfaces often need separate handling. Whatever you do, don't slap a blanket ignore on `legacy/`, or that folder becomes a dumping ground for fresh coupling forever.

## Record specific violations, not just a count

Never implement a ratchet as "fail if violation count > 5." If someone removes one old violation and sneaks in a brand-new one somewhere else, the count stays at 5 and your boundary quietly rots.

Store the identity of each accepted violation instead:

```text
rule: billing-domain-without-payment-gateway
origin: billing.domain.MonthlyInvoice.build
target: payments.gateway.Client.fetchCustomer
kind: method-call
```

Pick the granularity carefully. Module-to-module edges stop new modules from coupling; member-level edges also stop existing offenders from adding more calls across the same seam. Keep line numbers out of the baseline, because ordinary edits move lines around and create meaningless diff noise.

On every run, compare current findings against the committed baseline. Any finding missing from the baseline fails the build. Any baseline entry that's no longer in the code should drop out of the baseline in the same PR so nobody can quietly re-introduce it later. Also guard against silent scanner bugs: if the build step didn't compile the expected classes, an empty dependency graph should fail, not pass.

## How it looks in Java with ArchUnit

[ArchUnit's frozen rules](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules) build this workflow straight in: they record existing violations, fail on new ones, remove resolved ones from disk, and ignore line-number shifts by default.

Here's an adaptation sketch for a Java codebase (separate from this repo's Python billing lab), assuming ArchUnit's `noClasses` and `freeze` static imports:

```java
ArchRule rule = freeze(
    noClasses().that().resideInAPackage("..billing.domain..")
        .should().dependOnClassesThat()
        .resideInAPackage("..payments.gateway..")
).as("billing-domain-without-payment-gateway");

rule.check(importedClasses);
```

Commit the violation store to git. Generate it once after reviewing every existing entry, then lock down the config so a missing store can't be silently recreated:

```properties
freeze.store.default.path=architecture/violations
freeze.store.default.allowStoreCreation=false
freeze.refreeze=false
```

When tests run locally with store updates enabled, ArchUnit trims resolved entries from the store. In CI, verify that any shrinkage was committed:

```sh
git diff --exit-code -- architecture/violations
```

Only run that diff check after the architecture tests pass, and make sure the store is already tracked in git. Never enable `freeze.refreeze=true` in CI, since that would rubber-stamp every new violation a PR introduces.

## Treat baseline edits like design reviews

Renaming or moving a class can make one violation disappear and an identical one appear under the new name. Review the pair; migrating the entry makes sense if the coupling didn't actually change. What you want to avoid is blindly regenerating the whole file and smuggling in unrelated new dependencies.

Keep rule IDs stable when you refactor the test itself, and explain any rule changes in the PR. [Apache Flink's architecture test guide](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md) is a solid real-world example of this upkeep in practice.

For each exemption, note *why* it's still there and what condition removes it (like finishing a customer migration). Fake calendar deadlines rarely help; real removal conditions do.

## Prove both directions on day one

Start with one boundary connected to active work. Walk through the initial violations with someone who owns that area, commit the check and baseline together, and test both directions before enabling it for everyone: confirm that adding a forbidden import breaks the check, and remove one small violation to confirm its baseline entry disappears.

After that, pay down old violations opportunistically when work already touches those files. Forcing unrelated cleanup into every PR is the fastest way to make engineers resent the check.

## Watch out for freezing the wrong architecture

A ratchet protects a bad boundary just as loyally as a good one. Business domains evolve; a split that made sense two years ago can turn into pure friction once the product shifts.

Re-examine the rule whenever ordinary features keep needing exemptions, when complying requires awkward indirection, or when the original reason for the boundary is gone. A shrinking violation list only proves the list is shrinking; it doesn't prove the code is actually easier to change. Check the real outcome: can invoice calculations run without gateway setup now? Do provider changes stay contained?

Once the last baseline entry vanishes, delete the frozen store and turn it into a plain, permanent rule.

## Related patterns and sources

Start from a concrete catch using [review comment to guardrail](./review-comment-to-guardrail.md), pair extracted boundaries with [scenario builders](./scenario-builders.md) so the decoupled code is cheap to test, and audit whether the boundary still earns its keep in an [investment retrospective](./investment-retrospective.md).

- [ArchUnit: Freezing Arch Rules](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules): frozen violation stores, configuration flags, and line-insensitive matching.
- [Apache Flink: architecture tests](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md): a live project's workflow for reviewing and shrinking frozen violation baselines.
