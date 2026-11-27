---
name: subtraction-investigation
description: Investigate whether obsolete code, flags, scheduled jobs, exports, dependencies or tooling can be safely removed. Use when a removal candidate is named and its consumers or obligations are uncertain.
license: Apache-2.0
---

# Subtraction investigation

Default to read-only investigation. Do not disable services, delete data or files, run destructive commands, change production configuration, or request broad access merely to complete the investigation.

## Method

1. Name the candidate, its boundary and the reason to investigate. Identify what must remain unchanged and who owns the capability. Set a small timebox.
2. Trace direct and indirect references in code, generated output, configuration, scheduled jobs, deployment definitions, dependency declarations and relevant documentation. Record the paths and searches used. Do not assume a zero-result text search covers dynamically assembled names or external consumers.
3. Inspect available runtime evidence where authorized. Note the covered time range, tenants, regions, entry points, sampling and missing business cycles. No access or no traffic is not proof of no consumer.
4. Separate technical use from obligations: customer contracts, audits, scheduled reports, emergency fallbacks, retention and other teams' workflows. Ask the appropriate owner when evidence is absent or contradictory.
5. Where removal looks plausible, propose a reversible disablement or migration, verification with representative cases, a restoration condition, and the evidence and sign-off needed before deletion. Keep historical data and unrelated functionality outside the decision.
6. If the remaining consumer, risk or investigation cost outweighs the benefit, recommend keeping or shrinking the capability. Do not force a deletion recommendation.

## Deliverable

Return a short removal investigation:

- Candidate and scope; reason for removal.
- Observed references and runtime evidence, with source paths or commands.
- Blind spots and obligations; owner or unresolved authority.
- Recommendation: keep, shrink, investigate further or remove subject to named conditions.
- If appropriate, disablement, verification, restoration and deletion conditions.

Example: a script may have no references in the current generated site while the project still plans to restore the feature it supports. Distinguish "unused in today's build" from "no remaining obligation." A decision to retain the script until the feature's future is settled is a valid result.

When using this skill outside the collection, use the target repository's own tools, contracts and permissions. Never infer production safety from a synthetic example.
