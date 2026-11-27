# Review comment to guardrail

*Turn an agreed, recurring review catch into a check that explains itself.*

In a JavaScript version of our billing service, a reviewer flags the same bug for the third time this month: a billing handler imported the payment SDK directly instead of going through `src/payments/client.js`, which handles retries, idempotency keys, and error mapping. The reviewer types the same explanation, the author edits the import, and two weeks later somebody else makes the exact same mistake.

A ten-line static check catches that before anyone opens a pull request. Blocking the import is only half of it; putting the reason and the approved replacement straight into the error message is what actually saves everyone's time.

## Make sure the team agrees on the rule

Some review catches are mechanical: a forbidden import, a missing migration field, a generated file edited without its source. Others are judgment calls: whether an abstraction is worth its weight, whether a name fits the domain, whether a change needs another test.

Before automating a rule, write down one case that should fail and one nearby case that should pass. If two experienced reviewers disagree on those examples, hash it out with the team first. Encoding one loud reviewer's preference into CI just turns personal taste into mandatory friction.

Also check that the compliant path actually works. If `src/payments/client.js` lacks an operation a new feature needs, blocking direct SDK imports turns every pull request into an argument over `eslint-disable` comments. Fix the adapter or narrow the rule first.

## Use a built-in rule before writing a plugin

For this import boundary, ESLint already ships [no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports) with custom messages. You do not need a custom AST plugin.

In a flat ESLint config, keeping `src/payments/` outside the restricted directory looks like this:

```javascript
export default [{
  files: ["src/billing/**/*.js"],
  rules: {
    "no-restricted-imports": ["error", {
      paths: [{
        name: "stripe",
        message: "Use src/payments/client.js; it owns retry and idempotency policy."
      }]
    }]
  }
}];
```

The message tells the author what to use instead and why bypassing it causes bugs. A message saying "Violation of Policy 14" sends them right back to the same reviewer.

Be honest about what the rule misses. `no-restricted-imports` checks static import statements, so dynamic imports, indirect re-exports, and package aliases get past it. Leave a short comment next to the config noting that limit so reviewers do not assume the linter guarantees more than it does; if you need full module-graph enforcement, use a dependency checker built for that job.

## Test the rule through your real config

More lint rules fail silently because of a bad glob or an ignored directory than because of bad rule logic. Keep a small set of test fixtures and run them through the *effective* ESLint configuration, not just in an isolated unit test.

For the billing import rule, five cases cover most ways it can quietly break:

| Fixture | Expected result |
| --- | --- |
| A billing handler imports `stripe` | Reject, with the adapter guidance |
| A billing handler imports `stripe` under a local alias | Reject |
| A billing handler imports `src/payments/client.js` | Accept |
| The payments adapter imports `stripe` | Accept |
| A string or comment mentions `stripe` | Accept |

Run these in a dedicated rule-test harness (or via virtual file paths) so deliberate violations do not break normal linting. Assert the specific rule ID instead of checking only for a non-zero exit code, because a stray syntax error should not pass as a rule hit. When you do write a custom rule, ESLint's [RuleTester](https://eslint.org/docs/latest/extend/custom-rule-tutorial) handles valid and invalid cases cleanly, paired with one smoke test against the real repository config.

## Rolling it out without a wall of warnings

Confirm the rule against a few recent pull requests, run it across the repository, and read every existing match before enabling it.

If there are three existing violations, fix them in the same pull request. If there are forty and untangling them takes real work, freeze them with an [architectural ratchet](./architectural-ratchet.md) instead of setting the rule to "warn." Permanent CI warnings become wallpaper within a week.

Wire the check into whatever local command developers already run before asking for review, and into the editor if it is fast, while keeping CI as the final gate so enforcement never depends on everyone running the same plugins.

## Exceptions are feedback

Occasionally a direct SDK call is genuinely needed during a migration or spike. Put the inline exemption right next to the call with one line saying why it is there and when it can leave, and skip blanket directory ignores that linger for years.

Pay attention when exemptions pile up. Three people bypassing the same rule in a month usually means the adapter is missing something or the rule is out of date. Skip auto-fixers for anything that changes runtime behavior too: swapping an import path can change retry semantics or error shapes, and a human needs to look at that.

## Leave judgment (and teaching) in code review

Automating mechanical catches frees reviewers to look at things a linter cannot see: whether a payment operation needs an idempotency key, whether that key stays stable across retries, and whether the adapter's failure mode fits the caller. A handler can import the approved client and still pass a fresh UUID on every retry.

There is also a subtler cost to over-automating: when every design rule gets turned into a silent CI block with a vague error message, newcomers learn to satisfy the linter without learning *why* the boundary exists. Writing the rationale directly into the error message—and reserving automation for clear mechanical mistakes—keeps review time focused on the conversations that actually build judgment.

Judge the rule later by whether the repeated comment vanishes, whether newcomers can fix failures from the message without asking around, and how often false positives waste time. Once people internalize the convention, a good rule fires rarely. When the underlying reason disappears, delete the rule.

## What guardrails free up, and sources

Every mechanical check that moves into CI buys back review attention for harder correctness and design questions, and makes delegating routine edits (to newcomers or coding agents) noticeably safer.

When a new guardrail hits a backlog of legacy violations, pair it with an [architectural ratchet](./architectural-ratchet.md). When a recurring review catch is about runtime behavior that static analysis cannot express, move it into [executable invariants](./executable-invariants.md). Run the checks through a [capability command](./capability-command.md) so local runs and CI stay in sync.

- [ESLint: no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports): built-in import restrictions, custom messages, and static versus dynamic limits.
- [ESLint: Custom Rule Tutorial](https://eslint.org/docs/latest/extend/custom-rule-tutorial): testing valid and invalid cases with `RuleTester`.
