# Investment retrospective

*Check what happened when later work met the tool you built.*

A team spends four days building an invoice comparison runner. The first migration goes smoothly. Six months later the runner is still in the repository, someone has to patch its fixtures every time the invoice schema changes, and it still shows up on slide decks as a win for engineering productivity even though nobody remembers the last pull request it helped.

An investment retrospective puts one retained tool back in front of real work. What was it supposed to make easier? When did that work happen next? What did engineers use, what did they route around, and what did upkeep cost? End with one concrete call: keep it, simplify it, fix one gap, or delete it.

Save this for tools, checks, fixtures, telemetry, or abstractions that carry ongoing upkeep. A five-line helper script does not need a review process.

## Leave a baseline worth checking later

When you start building a capability, write down the job it is meant to help in plain terms. "Increase confidence" is impossible to audit six months later. "Compare old and new invoice totals without hand-building fixtures" gives you something real to check against.

Link one or two recent pull requests or incidents where that pain showed up, and jot down roughly where the time went: pulling data, setting up state, running checks, sorting out mismatches, waiting on a domain expert. Rough ranges are fine; do not invent fake precision from memory.

Pick a trigger that gives the tool a fair chance to prove itself, like the next three pricing changes, plus a fallback date in case that work never arrives. If nobody touches pricing for six months, that matters for upkeep even if the tool was cleanly built.

A short note in the tracking issue is plenty:

```text
Investment: invoice comparison runner
Expected use: pricing changes that must preserve existing invoice totals
Current pain: rebuilding fixtures by hand and diffing mismatches manually
Track: relevant PRs, fixture repairs, cases the runner cannot handle
Review after: three pricing changes, or next quarterly planning
Options: keep, simplify, fix one gap, archive
```

"Three changes" is a reminder to look back, not a statistical sample. Retrospective notes give you directional evidence, never controlled causal proof, so use them to steer your next decision rather than pretending they are a benchmark.

## Look at real work, including the bypasses

When the trigger hits, pull up a handful of recent changes in that area, including ones that never touched the tool. Looking only at successful runs hides setup friction, missing cases, and the workarounds people used to avoid your runner.

Talk to whoever made each change and compare their memory with the pull request, incident log, or CI output. Keep time spent learning the business domain separate from time spent fighting the tool, since they call for completely different fixes.

Here is a hypothetical review of our billing runner (invented observations, not real team metrics):

| Later change | What the runner did | What still hurt |
| --- | --- | --- |
| Effective-dated discount | Existing corpus caught an unintended change to old invoices | Needed a domain expert to judge whether one diff was a fix or a bug |
| Credit calculation refactor | Reused the corpus after patching the invoice adapter | Updating the adapter took longer than running the comparison |
| Refund correction | Bypassed completely; the runner does not support refunds | Engineer wrote a separate reproducer from scratch |

The takeaway is pretty blunt: the invoice cases are pulling their weight, the adapter is too brittle and should be simplified, and skipping refunds is fine if the runner was never meant to cover them. Turning every missing feature into a backlog item is how small helpers turn into unwanted internal platforms.

## Count hidden upkeep and what shifted around it

Add up the real carrying cost: broken fixtures, dependency bumps, cryptic CI failures, stale dashboards, onboarding questions, and the private Slack messages the original author answers to help people run it. Tools often look self-service on paper because nobody logs the DMs.

Keep sunk cost separate from future upkeep. The four days you spent building the tool tell you whether similar bets are worth starting next time; ongoing upkeep tells you whether *this* one is worth keeping. Sunk effort never justifies nursing a bad tool, and a rough first week is no reason to delete something that is now cheap and useful.

Check what moved outside the tool as well. Maybe the team understands billing better now, or the remaining migrations are tiny, or a library added the feature natively, or everyone postponed the hardest work. Any of those wrecks a naive before-and-after comparison. Google's [Eliminating Toil](https://sre.google/workbook/eliminating-toil/) chapter is clear on this: price in the maintenance of automation, and keep asking whether the underlying chore can be designed away.

## Look past raw runtime

Cutting a script from ten minutes to ten seconds helps very little if engineers still spend an afternoon arguing over what the output means. Ask harder questions alongside runtime:

- Could someone besides the author run it and interpret a failure?
- Did it catch a bug that mattered or verify a real guarantee?
- Did later work reuse its inputs or structure?
- Did it push work onto another team or add a new way to break CI?

A string of green runs only proves what sits inside the check's scope, and three quiet months never prove a tool prevented incidents. Meanwhile, a rarely run disaster-recovery command can still earn its keep if you rehearse it periodically, so do not judge everything by invocation count.

The [SPACE framework](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/) makes the broader point well: no single metric captures developer productivity. Keep this review tied to the work you tried to improve, and never turn tool usage or time estimates into individual performance metrics.

## Make a call, including deleting what failed

Pick one small, finishable decision. For the billing runner above: keep the corpus, simplify the adapter, document that refunds live elsewhere, assign an owner, and check again on the next schema change. Resist spinning up a "general billing test platform."

Just as often, the honest call is deletion. Imagine a second hypothetical bet from the same billing service: a custom PR bot built to auto-generate test scenarios from OpenAPI diffs. After four schema changes, engineers spent more time deleting noisy generated fixtures than writing focused tests by hand, and two teams muted the bot. Rather than spending another sprint tuning heuristics, delete the bot, note why it did not stick, and free up the maintenance slot.

Leave a few sentences next to the tool or in the issue: the changes you inspected, the main cost, the call you made, and what should trigger another look. Skip building a separate reporting system nobody reads.

## Zoom out to the whole portfolio

Auditing one artifact at a time has a real blind spot: ten tools, custom linters, and custom alerts that each look defensible alone can still add up to slow CI, brittle schema changes, noisy dashboards, and a repository newcomers are afraid to touch.

Once or twice a year, list the retained helpers, custom lint rules, frozen baselines, custom metrics from [incident to instrument](./incident-to-instrument.md), and fixture suites in one place and look at their combined drag. When every ordinary feature pull request drags three separate harnesses along behind it, you are living with negative compounding even if no single tool looks awful by itself. Prune the weakest ones first using a [subtraction investigation](./subtraction-investigation.md) so you do not break a hidden consumer.

## Did it just save time, or did it unlock new work?

A tool that saves an hour every migration pays for itself, and that is plenty. True compounding shows up when retained work makes something practical that used to be too slow or too risky: the invoice corpus feeds [competing prototypes](./competing-prototypes.md), or the scenario setup makes [differential verification](./differential-verification.md) feasible for a scary rewrite.

When that happens, note what got reused, what it unlocked, and what adapting it cost. Feed those lessons back into how you choose your next bet: the upfront selection questions in [Using the guide](../guide.md#choosing-between-competing-investments) get much sharper once you have audited two or three real tools. When compounding never shows up and maintenance outruns the benefit, retire the tool early while deletion is still cheap.
