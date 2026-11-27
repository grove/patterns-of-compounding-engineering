# Architectural ratchet

*Keep a useful boundary intact while removing the old violations.*

An invoice calculation ought to run without payment credentials. In the fictional billing service used here, several calculations import a gateway client to fetch customer details. That makes the calculations harder to test and makes a gateway replacement touch more of the application than expected.

The team agrees on a boundary: billing calculations should receive the facts they need as inputs. They should not depend on the payment gateway. A new architecture check immediately fails on existing code. Removing every dependency would turn a modest improvement into a separate project.

Record the specific violations already present. Reject new ones. As existing violations disappear, remove their exemptions in the same change.

## Choose a boundary that matters

A ratchet needs a reason people can evaluate. In this example, the reason is to exercise invoice calculations independently and eventually replace the gateway. A package diagram alone is a weak reason to hold up a useful change.

Start with one rule tied to work the team expects to do. Good candidates include a domain module importing an infrastructure client, an application reading another service's tables, or a new dependency creating a cycle between modules. The mechanism has to match the property: an import checker can detect a dependency on a database adapter, but it cannot establish which tables a query reads.

Before enforcing the rule, inspect its findings. Generated code, test fixtures and deliberately shared interfaces may need different treatment. Decide those boundaries explicitly. A broad exclusion for the whole legacy directory would let that directory accumulate fresh violations indefinitely.

## Record which violations already exist

Suppose a check currently reports five forbidden dependencies. A build rule that permits up to five violations can pass after someone removes one dependency and introduces an unrelated one. The count stayed flat; the intended boundary moved.

The baseline needs the identities of the accepted violations. A simplified representation might contain:

```text
rule: billing-domain-without-payment-gateway
origin: billing.domain.MonthlyInvoice.build
target: payments.gateway.Client.fetchCustomer
kind: method-call
```

Choose the level of detail deliberately. Recording a module-to-module edge prevents new module coupling. Recording individual member accesses can also prevent new uses across an existing boundary. Line numbers are poor identities because unrelated edits move them.

For each run, compare the current findings with the committed baseline. Findings absent from the baseline fail the check. Entries no longer present in the code should disappear from the baseline. Commit that reduction so a later change cannot quietly restore the dependency.

Keep scanner failures separate from an empty result. If a build no longer produces the classes the check expects, an empty dependency graph should not earn a pass.

## One implementation with ArchUnit

[ArchUnit's freezing support](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules) implements this approach for Java. It records existing violations, reports new ones and removes resolved violations from its store. Its default matching tolerates changes in source line numbers.

The following is an adaptation sketch for a Java service, separate from this guide's Python billing lab. It assumes ArchUnit's `noClasses` and `freeze` static imports and a populated `importedClasses` collection:

```java
ArchRule rule = freeze(
    noClasses().that().resideInAPackage("..billing.domain..")
        .should().dependOnClassesThat()
        .resideInAPackage("..payments.gateway..")
).as("billing-domain-without-payment-gateway");

rule.check(importedClasses);
```

Store the baseline in version control. Create it once, after reviewing the initial findings. The ordinary configuration should prevent an absent store from being recreated silently:

```properties
freeze.store.default.path=architecture/violations
freeze.store.default.allowStoreCreation=false
freeze.refreeze=false
```

With store updates enabled, ArchUnit can write reductions during a test run. A CI step can then require those reductions to have been committed:

```sh
git diff --exit-code -- architecture/violations
```

That last check is useful only after the architecture tests succeed, and the store must already be tracked. During normal development, run the tests, inspect any reduced store and include it in the pull request. Never make automatic refreezing part of the normal CI command; that would accept whichever violations the current change introduced.

## Treat baseline changes as design changes

Moving or renaming a class may make an old violation appear to disappear while a new one appears. Review the pair. If the relationship is unchanged, a deliberate baseline migration is reasonable. Replacing the entire store without looking at its diff can hide unrelated additions.

Keep the rule's identity stable when its implementation changes. If its meaning changes, explain that change and reconsider the exemptions. The [Apache Flink architecture-test instructions](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md) describe this maintenance work: developers commit resolved violations, investigate new findings and give frozen rules stable descriptions.

An exemption should say why it remains acceptable and what would remove it. It need not carry an arbitrary deadline. A dependency blocked by an unfinished customer migration has a real removal condition; a date chosen to satisfy a template adds little.

## Make the first change small

Choose a boundary involved in a current task. Review the findings with someone who works on that part of the system. Add the check and its baseline together, then prove that a new violation fails. Remove one existing dependency and verify that its exemption disappears. This establishes both directions of the ratchet before it begins blocking other people's work.

Remove another violation when work already touches the relevant code. Requiring unrelated cleanup on every pull request can turn a useful constraint into an obstacle to ordinary delivery.

## Watch what the rule costs

The check can preserve an awkward architecture as effectively as a good one. Reconsider it when ordinary changes repeatedly need exemptions, when the permitted route introduces more indirection than it removes, or when the original reason for the boundary disappears.

A shrinking baseline is evidence that recorded violations are disappearing. It does not establish that the system is easier to change. Look at the work the boundary was supposed to enable: can an invoice calculation now run without gateway setup? Does a provider change stay within fewer modules? How often does the check send a developer to someone else for an explanation?

Once the last exemption disappears, replace the frozen rule with an ordinary check. The boundary stays enforced without a baseline to maintain.

## Related patterns

[Review comment to guardrail](./review-comment-to-guardrail.md) helps select a narrow rule worth enforcing. [Scenario builders](./scenario-builders.md) make it easier to test behavior after extracting a dependency. An [investment retrospective](./investment-retrospective.md) can determine whether the boundary still earns its upkeep.

## Sources

- [ArchUnit user guide: Freezing Arch Rules](https://www.archunit.org/userguide/html/000_Index.html#_freezing_arch_rules). The implementation, store configuration and matching behavior used in the Java example.
- [Apache Flink: architecture tests](https://github.com/apache/flink/blob/master/flink-architecture-tests/README.md). A maintained project's instructions for reviewing violations and updating their stored baseline.
