# Review comment to guardrail

*Turn a recurring, objective correction into a check with a useful explanation.*

In a JavaScript version of the fictional billing service, reviewers keep spotting direct imports of the payment SDK in billing handlers. The application has a payments adapter that owns retry settings, idempotency-key policy and error translation. A direct SDK call skips that adapter, leaving each handler to get those decisions right.

The reviewer catches an import, explains the preferred route and waits for another revision. The same correction appears on a later change from somebody else. A short static check could catch this particular mistake before review.

The useful part of the comment is the constraint it reveals. Preserve the reason for that constraint alongside the check, and tell the author how to satisfy it.

## Decide whether the comment is a rule

Some review feedback is straightforward to test: a forbidden dependency, an omitted field in a migration manifest, a generated file changed without its source. Other feedback depends on context: whether an abstraction is useful, whether a name explains the business concept, whether a change deserves more tests.

Before automating a correction, write down the condition that should fail and a nearby case that should pass. If two experienced reviewers disagree about those examples, resolve the disagreement before encoding either opinion in CI.

Also check that there is an acceptable way to comply. If the payments adapter cannot express the operation the new feature needs, rejecting the direct import merely moves the problem into a conversation about exemptions. Fix the adapter or narrow the rule to what it can support.

## Start with a built-in check

For this example, ESLint's [no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports) rule can reject imports from a named package and include a project-specific message. There is no need to write a new parser.

This illustrative excerpt belongs in an existing JavaScript project's flat ESLint configuration. The `src/payments/` adapter is outside the restricted billing directory:

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

The message names the permitted route and explains the consequence of bypassing it. A message that only reports a policy number would send the author back to the same reviewer for help.

This rule checks static import statements. It does not prove that a handler can never contact a provider. Dynamic imports, other package entry points and local modules that expose the SDK need separate consideration. Test the import forms actually used by the application. For a broad dependency guarantee, use a tool that resolves the project's module graph and aliases.

Keep that limit in the rule's documentation. An honest check of a narrow condition is useful. An overstated guarantee can make reviewers stop looking for failures the tool cannot detect.

## Check the rule in its actual configuration

A rule can be correct and still cover no files because a glob, parser setting or ignore pattern is wrong. Keep a few deliberate fixtures and run them through the same effective configuration as application code.

For the example, useful cases include:

| Fixture | Expected result |
| --- | --- |
| A billing handler imports `stripe` | Reject, with the adapter guidance |
| A billing handler imports `stripe` under a different local name | Reject |
| A billing handler imports the approved adapter | Accept |
| The payments adapter imports `stripe` | Accept |
| A string or comment mentions `stripe` | Accept |

These fixtures belong in a separate rule-test harness or use virtual filenames; leaving deliberate violations inside the normal application scan would break every build. Assert the expected rule identifier as well as the exit status, so a syntax error cannot masquerade as a successful test of the restriction.

If the project needs a custom ESLint rule, its [RuleTester](https://eslint.org/docs/latest/extend/custom-rule-tutorial) provides valid and invalid cases. A test of the real configuration is still needed to establish that the rule reaches the intended files.

## Introduce it without a pile of warnings

Collect a few recent examples of the correction and confirm the underlying decision with the team. Implement the narrowest check that catches those cases. Run it against the current codebase and read every finding before making it required.

If there are only a few existing violations, fix them with the rule. If there are many legitimate constraints on cleanup, use an [architectural ratchet](./architectural-ratchet.md) or a similarly precise baseline. A permanent warning stream is easy to stop reading, and it leaves authors uncertain about which findings matter.

Make the check available through the command developers already run before asking for review. For a fast rule, an editor integration can shorten the feedback cycle further. Keep CI as the shared enforcement point so the result does not depend on an individual's editor setup.

## Give exceptions a reason

Sometimes a direct call is needed for a provider migration or an experiment. Keep the exception near the relevant code, state the reason and identify what permits its removal. Review it as part of the design. A blanket directory exclusion can outlive the situation that justified it.

Watch exceptions for another signal: the rule may be wrong. If several legitimate operations cannot use the approved adapter, expanding the adapter might help, but so might retiring the restriction. Do not treat every exception as evidence that developers need stricter enforcement.

Avoid automatic fixes for changes that affect behavior. Replacing an import may require translating errors or preserving retry semantics. A useful diagnostic can guide that work without attempting an unsafe edit.

## Keep the judgment in review

Reviewers still need to examine whether a payment operation needs an idempotency key, whether it remains stable across retries and whether the adapter's failure behavior fits this operation. A handler can import the approved adapter and still pass a different key on every retry. The static check leaves these questions for review and behavioral tests.

## Find out whether it helped

Look for fewer repeated corrections of the same kind, findings authors can resolve without asking around, and fewer accidental bypasses. Also record false alarms and time spent maintaining the check. The number of rejected pull requests is a poor target: a successful rule may quickly stop finding anything because the normal route has become familiar.

A new engineer should be able to follow the diagnostic without finding the reviewer who first raised the issue. If the policy changes, change its diagnostic, fixtures and documentation together. Remove the check when its reason disappears.

## Related patterns

[Architectural ratchet](./architectural-ratchet.md) handles rules with existing violations. [Executable invariants](./executable-invariants.md) cover behavior a source check cannot establish. [Capability command](./capability-command.md) makes the check easy to discover and run.

## Sources

- [ESLint: no-restricted-imports](https://eslint.org/docs/latest/rules/no-restricted-imports). Configuration, custom diagnostics and the distinction between static and dynamic imports.
- [ESLint: Custom Rule Tutorial](https://eslint.org/docs/latest/extend/custom-rule-tutorial). Building a rule and testing valid and invalid examples with `RuleTester`.
