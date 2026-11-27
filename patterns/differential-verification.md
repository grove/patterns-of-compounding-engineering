# Differential verification

*Run the old and new implementations on the same cases.*

The team wants to replace an invoice calculator. The existing code is difficult to change, yet it embodies years of exceptions that nobody can list confidently. A new implementation passes the tests the team understands. The question is what those tests have missed.

Run both implementations on the same inputs and inspect their differences before switching. This makes the existing system a useful source of evidence, including evidence of behavior the team may decide to correct.

The technique has established uses. [GitHub's Scientist library](https://github.com/github/scientist) runs a control and a candidate, compares their results and returns the control's result. [SQLite's testing documentation](https://sqlite.org/testing.html) describes comparing SQL results across database engines. Neither comparison makes agreement synonymous with correctness: both implementations can share a mistake.

## Find a boundary with observable results

Start with a calculation, query or transformation whose inputs can be captured and whose outputs can be compared. For the illustrative billing service, that boundary accepts line items and requested credit and returns an invoice calculation. Sending the invoice and charging the customer happen outside it.

Define the input completely. If the calculator consults today's date, a feature flag, account history or a price table, pass or capture those values too. Otherwise the two runs may answer different questions even though they received the same request object.

Avoid sharing mutable inputs between runs. One implementation may normalize a collection in place, leaving altered input for the second. Use immutable values or separate copies. For database queries, account for changes between reads; a consistent snapshot or a recorded dataset can be more useful than comparing two live queries that observe different transactions.

If you cannot isolate external effects, begin offline. A flag called `dry_run` is only as good as every path that honors it. Make it structurally difficult for the candidate to send email, charge a card or write to an authoritative store.

## Define what counts as the same answer

Compare business outputs rather than object identities or incidental serialization. For the billing example, compare subtotal, applied credit, unused credit and amount due. If the system accepts multiple currencies, compare currency too. A new trace ID should not count as a pricing difference.

Be conservative about normalization. Sorting an unordered result can be appropriate; sorting a ranked search result would erase meaningful behavior. Removing timestamps is reasonable only when they are incidental to the contract. Never introduce a broad numeric tolerance merely to make a money comparison pass. Agree on rounding rules first.

Compare failure behavior as well as successful results. A candidate that rejects an invalid input previously accepted may be an intentional tightening of the contract. A candidate that raises on a valid legacy account is a migration problem. Keep those outcomes separate from ordinary value mismatches.

In the [billing lab](../examples/README.md), run:

```sh
python3 examples/billing_lab.py compare --candidate correct
python3 examples/billing_lab.py compare --candidate buggy
```

The second candidate is deliberately wrong. It gives the comparison something concrete to catch. Both commands work on local synthetic data and have no payment or messaging effects. A successful comparison covers that corpus only.

## Build a corpus with awkward cases

Begin with a handful of cases the team can explain: ordinary credit, no credit, credit that exhausts the invoice, and credit left over after it. Include [persistent reproducers](./persistent-reproducer.md) from earlier bugs. Use [scenario builders](./scenario-builders.md) to vary the details without duplicating setup.

Later, recorded production inputs can expose combinations absent from synthetic cases. Decide which fields are necessary, remove sensitive material, and preserve the relationships relevant to the computation. Data capture and retention become part of the experiment's cost. A small reviewed sample may answer the current question better than a permanent traffic archive.

Look at coverage by meaningful class. A large sample of ordinary monthly invoices says little about an annual contract with a mid-period change. Record missing classes explicitly. Rare cases often need deliberate construction or a longer observation period.

Historical inputs also depend on historical rules. If a current price table is applied to last year's invoices, differences may reflect a changed context rather than a defect. Preserve the policy version or narrow the experiment's claim.

## Decide what each difference means

Produce a report that lets a developer locate the case, understand which fields differ, and reproduce both results. A percentage of matching outputs is insufficient for a decision when the remaining differences involve money or permissions.

Classify each difference as a candidate defect, an intended correction, a comparison problem, or a case still under investigation. An intended correction needs an expected outcome supported by the policy owner or an independent rule. Add a focused test so it does not remain an unexplained exception in the comparator.

[Executable invariants](./executable-invariants.md) are useful here. If both implementations agree but violate a reviewed guarantee, agreement should not win the argument. If the candidate differs because it satisfies a rule the old code violates, document that as a behavior change and plan the migration accordingly.

Set the decision criteria before expanding the experiment. For example: all known input classes represented, no unexplained monetary differences, and explicit treatment of every intended change. These are proposed criteria for the example, not universal release thresholds.

## Take care when moving into production

To compare on production traffic, run the candidate alongside the old implementation while only the old result determines the response. This is often called shadow execution. It adds load and may change timing. Measure the overhead, cap the sample and give the experiment an off switch. Isolate candidate failures so they cannot prevent the authoritative operation from completing.

Scientist supports custom comparisons and cleaned reporting values. Its documentation restricts experiments to methods that do not change data and warns that it does not protect requests from candidate timeouts. Review caches, database writes and outbound calls at the boundary. Even a read can be expensive enough to affect customers when doubled.

Do not infer production latency from a candidate run on a warm cache immediately after the old implementation. Benchmark performance deliberately if that is part of the replacement's purpose. Correct outputs and acceptable operating cost are separate questions.

## Remove the experiment when it has answered its question

Keep the useful corpus and a small comparison adapter if another replacement is likely. Remove dual execution, temporary flags and the obsolete implementation after the switch and its agreed observation period. Maintaining both forever can consume the savings the replacement was meant to create.

The evidence of value is specific: a mismatch found before cutover, a previously unknown exception made explicit, or a later implementation evaluated with the existing corpus. Record those uses alongside the time spent investigating noisy differences and maintaining adapters. If the comparator mostly reports irrelevant changes, narrow its contract before trusting its results.
