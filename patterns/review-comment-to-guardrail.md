# Review comment to guardrail

*Turn an agreed, recurring review catch into a check that explains itself.*

Picture a JavaScript version of our billing service. For the third time this month, a reviewer flags a billing handler importing the payment SDK directly instead of going through `src/payments/client.js`, which handles retries, idempotency keys, and error mapping. The reviewer writes the same explanation, the author updates the pull request, and two weeks later somebody else makes the same mistake.

A ten-line static check catches that before anyone opens a pull request. Blocking the import helps, and putting the reason plus the approved replacement right in the error message is what saves everyone's time.

## Check that the team agrees on the rule

Some review catches are mechanical: a forbidden import, a missing migration field, a generated file edited without its source. Others are judgment calls: whether an abstraction pulls its weight, whether a name fits the domain, whether a change needs more tests.

Before automating anything, write down one case that should fail and one nearby case that should pass. If two experienced reviewers disagree on those examples, hash it out with the team first. Encoding one loud reviewer's preference into CI just turns personal taste into mandatory friction.

Also check that people can comply cleanly. If `src/payments/client.js` lacks the operation a new feature needs, blocking direct SDK imports turns every pull request into an argument over lint-ignore comments. Fix the adapter or narrow the rule until the normal path works.

## Reach for a built-in rule first

For this import boundary, ESLint already ships [no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports) with custom error messages. You do not need a custom AST plugin.

Here is how that looks in a flat ESLint config, keeping `src/payments/` outside the restricted directory:

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

The error message names the replacement and explains why bypassing it causes bugs. A message saying "Violation of Policy 14" sends the author right back to the same reviewer.

Be upfront about what the rule cannot see. `no-restricted-imports` checks static import statements, so dynamic imports, indirect re-exports, and package aliases get past it. Note that limit in a comment next to the config so reviewers do not assume the linter guarantees more than it does. When you need full module-graph enforcement, use a dependency checker built for that job.

## Test the rule through your real config

More lint rules fail because of a bad glob or an ignored directory than because of bad logic. Keep a small set of test fixtures and run them through the *effective* ESLint configuration, alongside any isolated unit tests for the rule.

For the billing import rule, five cases cover most ways it can silently break:

| Fixture | Expected result |
| --- | --- |
| A billing handler imports `stripe` | Reject, with the adapter guidance |
| A billing handler imports `stripe` under a local alias | Reject |
| A billing handler imports `src/payments/client.js` | Accept |
| The payments adapter imports `stripe` | Accept |
| A string or comment mentions `stripe` | Accept |

Run these in a dedicated rule-test harness (or via virtual file paths) so deliberate violations do not break normal linting. Assert the specific rule ID instead of checking only for a non-zero exit code, so a stray syntax error cannot pass as a rule hit. If you write a custom rule, ESLint's [RuleTester](https://eslint.org/docs/latest/extend/custom-rule-tutorial) handles valid and invalid cases cleanly, paired with one smoke test against the real repository config.

## Ship it cleanly, without a wall of warnings

Confirm the rule against a few recent pull requests, run it across the repository, and read every existing match before enabling it.

If there are three existing violations, fix them in the same pull request. If there are forty and untangling them takes real work, freeze them with an [architectural ratchet](./architectural-ratchet.md) instead of downgrading the rule to "warn." Permanent CI warnings quickly become background noise.

Hook the check into whatever local command developers already run before asking for review, and wire it into the editor if it is fast. Keep CI as the final gate so enforcement never depends on everyone having the same IDE plugins.

## Treat exceptions as a signal

Occasionally a direct SDK call is necessary during a migration or spike. Put the inline exemption next to the call with a short explanation of why it is needed and when it can go away. Avoid blanket directory ignores that linger in the config for years.

Pay attention when exemptions pile up. Three people bypassing the same rule in a month usually points to a missing capability in the adapter or an outdated rule. Skip auto-fixers for anything that changes runtime behavior, too: swapping an import path can change retry semantics or error shapes, and a human needs to inspect that.

## Leave judgment in code review

Automating the import check frees reviewers to look at the things a linter misses: whether a payment operation needs an idempotency key, whether that key stays stable across retries, and whether the adapter's failure mode fits the caller. A handler can import the approved client and still pass a fresh UUID on every retry.

## Check whether it helped

Judge the rule by whether the repeated review comment disappears, whether newcomers can fix failures from the error message without asking around, and how often false positives waste time. Once people learn the convention, a good rule fires rarely. When the underlying reason goes away, delete the rule.

## How it connects and sources

When a new guardrail runs into a backlog of legacy violations, pair it with an [architectural ratchet](./architectural-ratchet.md). When a recurring review catch is about runtime behavior that static checks cannot express, move it into [executable invariants](./executable-invariants.md). Run the checks through a [capability command](./capability-command.md) so local runs and CI stay aligned.

- [ESLint: no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports): built-in import restrictions, custom messages, and static versus dynamic limits.
- [ESLint: Custom Rule Tutorial](https://eslint.org/docs/latest/extend/custom-rule-tutorial): testing valid and invalid cases with `RuleTester`.
