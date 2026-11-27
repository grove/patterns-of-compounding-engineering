# Review comment to guardrail

*Turn an agreed, recurring review catch into a check that explains itself.*

Picture a JavaScript version of our billing service. For the third time this month, a reviewer flags a billing handler importing the payment SDK directly instead of going through `src/payments/client.js`, which handles retries, idempotency keys, and error mapping. The reviewer writes the same explanation, the author revises the PR, and two weeks later somebody else makes the exact same mistake.

A ten-line static check can catch that before anyone opens a pull request. Blocking the import helps, and attaching the *reason* plus the approved alternative right to the error message is what actually saves everyone's time.

## Make sure it's a real team rule, not one reviewer's taste

Some review catches are clean and mechanical: a forbidden import, a missing migration field, a generated file edited without its source. Others are judgment calls: whether an abstraction pulls its weight, whether a name fits the domain, whether a change needs more tests.

Before automating anything, write down one case that should fail and one nearby case that should pass. If two experienced reviewers disagree on those examples, hash it out with the team first. Encoding the loudest reviewer's personal preference into CI turns a guardrail into institutional bureaucracy.

Also make sure people *can* actually comply. If `src/payments/client.js` doesn't support the operation a new feature needs, blocking direct SDK imports just turns every PR into an argument over lint-ignore comments. Fix the adapter or narrow the rule until the happy path works.

## Reach for a built-in rule first

For this import boundary, ESLint already ships [no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports) with custom error messages. No custom AST plugin required.

Here's how that looks in a flat ESLint config, keeping `src/payments/` outside the restricted directory:

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

The error message names the exact replacement and explains *why* bypassing it causes bugs. A message that says "Violation of Policy 14" forces the author to hunt down the same reviewer anyway.

Be upfront about what the rule can't see. `no-restricted-imports` checks static import statements, not dynamic imports, indirect re-exports, or clever package aliases. Note that limit in the config comment so reviewers don't assume the linter guarantees something it doesn't. If you need full module-graph enforcement, use a dependency checker built for that job.

## Test the rule through your real config

More lint rules fail because of a bad glob or an ignored directory than because of bad logic. Keep a small set of test fixtures and run them through the *actual* effective ESLint configuration, not just a unit test of the rule in isolation.

For the billing import rule, five cases cover most ways it can silently break:

| Fixture | Expected result |
| --- | --- |
| A billing handler imports `stripe` | Reject, with the adapter guidance |
| A billing handler imports `stripe` under a local alias | Reject |
| A billing handler imports `src/payments/client.js` | Accept |
| The payments adapter imports `stripe` | Accept |
| A string or comment mentions `stripe` | Accept |

Run these in a dedicated rule-test harness (or via virtual file paths) so deliberate violations don't break normal linting. Assert the specific rule ID rather than just a non-zero exit code, so a stray syntax error can't pass as a rule hit. If you eventually write a custom rule, ESLint's [RuleTester](https://eslint.org/docs/latest/extend/custom-rule-tutorial) handles valid and invalid cases cleanly, though you still want one smoke test against the real repo config.

## Ship it cleanly, without a wall of warnings

Confirm the rule against a few recent PRs, run it across the whole repo, and read every existing match before turning it on.

If there are three existing violations, just fix them in the same PR. If there are forty and untangling them takes real work, freeze them with an [architectural ratchet](./architectural-ratchet.md) instead of downgrading the rule to "warn." Nobody reads a permanent stream of CI warnings.

Hook the check into whatever local command developers already run before asking for review, and wire it into the editor if it's fast. Keep CI as the final gate so enforcement doesn't depend on everyone having the same IDE plugins.

## Treat exceptions as a signal

Occasionally a direct SDK call is genuinely necessary during a migration or spike. Put the inline exemption right next to the call with a short explanation of why it's needed and when it can go away. Avoid blanket directory ignores that quietly stay in the config for years.

Pay attention when exemptions pile up. Three people bypassing the same rule in a month rarely means the team is sloppy; it usually means the adapter is missing something or the rule itself is outdated. Skip auto-fixers for anything that changes runtime behavior, too. Swapping an import path can change retry semantics or error shapes, and a human needs to inspect that.

## Leave judgment in code review

Automating the import check doesn't eliminate review; it frees reviewers to check the things a linter *can't* see: whether a payment operation actually needs an idempotency key, whether that key stays stable across retries, and whether the adapter's failure mode makes sense here. A handler can import the approved client and still pass a fresh UUID on every retry.

## Check whether it actually helped

Don't measure success by how many PRs the rule rejects. Once people learn the pattern, a good rule fires rarely. Instead, watch whether the same review comment disappears, whether newcomers can fix failures from the diagnostic without asking around, and how often false positives waste time. When the rule's reason disappears, delete it.

## Related patterns and sources

Use an [architectural ratchet](./architectural-ratchet.md) when a new rule meets a backlog of legacy violations, [executable invariants](./executable-invariants.md) for behavioral rules static checks can't express, and a [capability command](./capability-command.md) to keep local and CI runs aligned.

- [ESLint: no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports): built-in import restrictions, custom messages, and static vs. dynamic limits.
- [ESLint: Custom Rule Tutorial](https://eslint.org/docs/latest/extend/custom-rule-tutorial): testing valid and invalid cases with `RuleTester`.
