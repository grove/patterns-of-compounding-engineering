---
name: compounding-pass
description: Review completed engineering work for one worthwhile reusable improvement to tests, knowledge, tools, skills, or workflow. Use after a meaningful change or review, especially when a difficulty is likely to recur.
license: Apache-2.0
---

# Compounding pass

Use the actual completed work. Read the task, diff, review findings and available verification output; distinguish things you saw from things reported by others. If the history is missing, do not invent it.

1. Identify any moment the work became unnecessarily difficult. Was there missing knowledge, a hard-to-run check, a repeated correction, a needless procedure, or a decision that needed a person? If none is evident, say so; a known next task may still offer a useful opportunity for reuse.
2. Look for the existing record, check, command or skill that should have helped. Fix the route or improve that artifact before creating a new one. Consider removing the source of friction instead.
3. If a relevant next task is known, consider whether an existing capability makes a useful experiment or further improvement practical. Name what would be reused, what must be added, and what evidence could show that the connection helped. Do not invent an upcoming need or require a second investment.
4. Select at most one small improvement unless the user asks for a broader investigation. Explain why the need is likely to recur or matters to the known next task, who benefits, what it costs to maintain, and what evidence could demonstrate benefit on the next use.
5. State how to check the improvement, distinguishing verification already run from checks still proposed. For an executable check, include evidence that it detects the intended failure as well as accepting the correction, where safe and authorized. For a document or procedure, identify a representative task on which a fresh reader could try it.
6. Return a recommendation. Do not modify files, change access, publish, merge, or deploy as part of the pass unless the user has authorized those actions. If no investment is worthwhile, say so and stop.

## Output

- Friction and evidence (include a source, path or result).
- Proposed smallest improvement, or no change.
- Scope, upkeep and responsible owner if known.
- Verification now and a later task that could reveal whether it helped; identify any earlier capability the proposal depends on.
- Open questions or risks.

For example, if a catalogue entry existed but the README omitted it, check for an existing consistency test. A small test comparing the real README with the catalogue may be preferable to another instruction to remember every list. Passing the test on the corrected README and failing it with an entry omitted demonstrates its immediate purpose. The next catalogue change can reveal whether it saves review effort.

Do not keep a transcript, add a tool merely to show that the pass ran, or report a predicted saving as a measured return.
