# Investigation to skill

*Keep the method that helped you solve a problem, and see whether it works on a different one.*

A developer spends an afternoon helping an agent work out whether a legacy CSV export can go. First the agent searches for callers. Then the developer remembers the scheduled delivery job. A look at the job's configuration reveals that finance reads the files straight from object storage, bypassing the HTTP endpoint entirely. After a conversation with finance, the team decides to keep delivery and replace the old serializer.

The answer belongs in a record about that export. The way the investigation went is useful for a different reason: the next suspected dead endpoint might have a consumer hiding behind a schedule, too.

A reusable skill captures the method. It tells an investigator where to start, which evidence matters, what to do with gaps and when to stop. A colleague can follow it; a compatible agent can load it when the task calls for it.

## Separate the answer from the method

In the example, "finance still needs the CSV" is local knowledge. "Check scheduled deliveries as well as requests before claiming an export is unused" is a question worth asking elsewhere. The distinction keeps a skill from becoming a bag of old decisions masquerading as general rules.

Start with two similar investigations if you have them. Compare the places where somebody needed help. A pattern that occurs once in a high-risk investigation can justify a trial too, as long as you treat it as an untested method.

For subtraction, the common sequence might be: draw a boundary around the candidate; trace references, indirect consumers and runtime obligations; identify what the evidence cannot show; then make a recommendation with conditions for removal or a reason to stop.

That sequence already exists in [Subtraction investigation](./subtraction-investigation.md). There is no need to turn it into a separate script that tries to guess what counts as dead code.

## Give it a useful shape

The [Agent Skills specification](https://agentskills.io/specification) describes a portable text format: a directory containing a `SKILL.md` with a name, description and instructions. Use it with a supporting tool, or give the file directly to a person or agent. It does not require a particular model or permission system.

Try the collection's [subtraction investigation skill](../skills/subtraction-investigation/SKILL.md). Its output is a recommendation with evidence, blind spots and next steps, not a deletion patch.

Keep the description narrow enough that the investigator recognizes when to use it. Include inputs, a few steps, what a satisfactory result looks like and the boundaries of the work. Link to the current domain evidence rather than repeating it. Use a command when that makes an evidence-gathering step repeatable; use a question when somebody needs to reason.

[Every's Compound Engineering guide](https://every.to/guides/compound-engineering) describes retaining domain expertise as skills and improving the system after completed work. Our adaptation adds a small trial: use the method on a new case before trusting it as a default procedure.

## Try a case where the answer changes

A skill distilled from a successful deletion is particularly prone to recommending another deletion.

Give it two tasks: investigate a genuinely unused export, and investigate a rarely used one with an unresolved consumer. Give each investigator only the usual repository access and the task. Record whether they identify missing evidence, not just whether they arrive at your preferred conclusion. Do not provide the expected answer as part of the instructions.

For a small real example, this collection's companion essay repository has an audio-speed script that is not loaded by the current text-only generator. The README and publishing guidance explicitly defer narration. A read-only investigation can establish that the script is unused in the current generated site, but cannot establish that the capability has been permanently retired. Leaving a low-cost file alone while the intended future use remains open is a reasonable recommendation.

Keep the next rehearsal comparable. Compare evidence, errors, review effort and whether the skill encouraged unnecessary work. A single example establishes that the method can be followed; it is not a productivity benchmark. [Verified retrieval](./verified-retrieval.md) helps test whether the method is even found in a fresh session.

## Keep the skill smaller than the problem

If a project already has a good checklist, link it. If a step is deterministic, a tested command may be a better home for it. If a review comment concerns an agreed and detectable violation, move it into a [guardrail](./review-comment-to-guardrail.md).

A skill is not authority to access production, modify shared resources or decide that a business obligation no longer matters. Keep its default permissions narrow, and ask an authorized owner to settle what the evidence cannot.

When you improve the method, retain the case that exposed the gap. Review the skill when its tools or assumptions change, or when someone follows it and gets a misleading result. If the procedure grows into a long ritual that adds no useful evidence, shorten it or retire it. The [investment retrospective](./investment-retrospective.md) applies to instructions as much as to tools.

A reliable method can make the next investigation cheaper. It begins to compound when that investigation produces a better check, a simpler system, or a method that opens up a class of work previously too difficult to attempt.
