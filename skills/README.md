# Try a skill on your own work

These are small, experimental procedures derived from the patterns. Read them yourself, or ask a coding agent to follow one. Each is a directory with a [standard SKILL.md](https://agentskills.io/specification). If your tool supports Agent Skills, use its documented installation or loading mechanism; otherwise point it at the file. Nothing here requires a plugin, special model or automatic execution.

| Skill | When it helps | Start with |
| --- | --- | --- |
| [Compounding pass](./compounding-pass/SKILL.md) | Finishing a task that exposed recurring friction | The diff, failed attempts and verification results |
| [Subtraction investigation](./subtraction-investigation/SKILL.md) | A capability looks obsolete but deletion could break an unseen consumer | A named removal candidate and read-only repository access |
| [Technical review](./technical-review/SKILL.md) | Checking a pattern, guide or example before publication | The changed files and available checks |

The companion essay repository has an [editorial review skill](https://github.com/grove/engineering-that-compounds/tree/main/skills/editorial-review) for assessing argument, examples and prose.

Give a skill a concrete task and the evidence it needs, not a broad instruction to improve everything. For example:

> Read skills/subtraction-investigation/SKILL.md and investigate whether this repository still needs its compatibility flag. Do not change the code. Return evidence, blind spots and a recommendation.

Use ordinary repository permissions. These procedures do not grant access or authorize changes. Review the result before accepting it, and ask whether a fresh attempt without the original conversation can find and apply the guidance. See [Investigation to skill](../patterns/investigation-to-skill.md) and [Verified retrieval](../patterns/verified-retrieval.md).

These first skills are proposals, not validated general-purpose agent evaluations. Keep cases that expose an actual weakness and improve the existing instruction before adding another skill. Retire a skill if the task goes away or a simpler command does its job.
