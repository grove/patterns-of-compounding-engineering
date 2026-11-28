# Reusable domain scenarios

*Keep a small, reviewed account of the world your software needs to handle.*

Two payment notifications arrive with different event IDs. The handler counts both. Every retry test passes because those tests repeat the same event ID. A customer says they made one payment.

First check the payment provider's contract: do those notifications describe one transfer or two? More generated tests cannot settle it. Use this pattern when product, support and engineering repeatedly reconstruct the same customer situation, or when technically correct behavior no longer matches how the work happens.

## Keep the situation and its evidence together

Start with one consequential case. Describe what the customer or operator was trying to do, what happened and the rule being applied. Preserve the source and its limits: an observed support case, a reviewed contract, a product decision or an unresolved hypothesis are different kinds of evidence.

For the fictional billing service, a compact record could be:

```text
Situation: one settled payment produces two notification events.
Identity: event IDs differ; provider payment ID is the same.
Expected behavior: credit that payment once.
Basis: the provider's reviewed identity contract, linked here in a real service.
Nearby case: two separate payments toward one invoice must both count.
Revisit: the provider, identity scope or settlement rules change.
Open questions: refunds, disputes and conflicting amounts.
```

The nearby case matters. Deduplicating by invoice ID would stop the original double count but discard legitimate installments. A useful scenario records enough context to distinguish the two.

Keep private source records under their existing access controls. For examples and tests, use synthetic values that preserve the relevant relationships. Link back to the approved evidence where readers are entitled to see it; do not copy customer transcripts into a public fixture.

## Give the same case different jobs

Engineering can turn the reviewed expectation into a check. A designer can use the situation to explore how the account history should explain the two notifications. Support can use it to investigate a discrepancy. Product discovery can ask whether customers understand the resulting statement.

Those uses require different evidence. A fixture can establish what the software does with specified inputs. Only contact with real customers can establish how they interpret the statement. A synthetic persona's answer is another design hypothesis.

The [domain extension to the evolving lab](../examples/evolving-billing/README.md#6-change-the-identity-rule) demonstrates the technical part. It states a fictional payment-ID contract, adds a genuine second payment as a counterexample, and carries both through the existing restart and interruption runner. It contains no customer research or production payment rules.

## Keep new examples honest

AI can help turn an approved case into test data, suggest an overlooked boundary or locate related scenarios. Mark generated variations as synthetic and review their assumptions before treating their expectations as acceptance criteria.

Do not let a generator produce the case, invent its expected behavior and then treat agreement as confirmation of the business rule. Keep the reviewed expectation outside that loop. If a new observation conflicts with the expectation, ask whether the software, the scenario or the rule needs to change.

When the rule changes, update active checks and summaries and leave a clear route from the superseded decision. Sometimes the old rule still applies to older contracts. A date alone does not determine which expectation is correct.

## See whether the next person can use it

Try the next related task with someone who was not in the original investigation. Can they find the case, explain its source and scope, and distinguish a repeated notification from another payment? Can they identify the question the case cannot answer?

Watch for avoided reconstruction, missing evidence and time spent repairing stale fixtures. Keep only cases whose likely use or consequences justify the upkeep. A handful of well chosen examples can be easier to understand than a large scenario library with unclear provenance.

If the case later helps build a reconciliation experiment, record what carried over and what new work was needed. That connection is a possible compounding mechanism. Sharing the case between disciplines is useful in its own right; it is not proof that later capability development became cheaper.

## Where the idea comes from

Teresa Torres's account of [assumption testing](https://www.producttalk.org/assumption-testing/) connects specific assumptions to evidence and recommends keeping the context, audience, test and result. Her [product discovery overview](https://www.producttalk.org/glossary-discovery-product-discovery/) distinguishes ongoing customer interviewing from testing possible solutions. This pattern applies that discipline to the situations shared between product and engineering.

[Scenario builders](./scenario-builders.md) make reviewed situations cheap to construct. [Executable invariants](./executable-invariants.md) express relevant guarantees. [When software forgets the world](https://grove.github.io/engineering-that-compounds/essays/when-software-forgets-the-world.html) explains why those guarantees need continued contact with the work outside the software.
