# Investment retrospective

*Check what actually happened when later work met the tool you built.*

A team spends four days building an invoice comparison runner. The first migration goes smoothly. Six months later the runner is still in the repo, someone has to patch its fixtures every time the invoice schema changes, and it still shows up on slide decks as a win for engineering productivity, even though nobody can remember the last PR it actually helped.

An investment retrospective puts one of those retained tools back in front of real work. What was it supposed to make easier? When did that work happen next? What did engineers actually use, what did they route around, and what did upkeep cost? End with a concrete call: keep it, simplify it, fix one gap, or delete it.

Save this for tools, checks, fixtures, or abstractions that carry ongoing upkeep. A five-line helper script doesn't need a review process.

## Leave yourself a baseline worth revisiting

When you start building a capability, write down the job it's meant to help in plain terms. "Increase confidence" is impossible to audit six months later. "Compare old and new invoice totals without hand-building fixtures" gives you something real to look at.

Link one or two recent PRs or incidents where that pain showed up. Jot down roughly where the time went: pulling data, setting up state, running checks, sorting out mismatches, waiting on a domain expert. Rough ranges are fine; don't fabricate fake precision from memory.

Pick a trigger that gives the tool a fair chance to prove itself, like the next three pricing changes, plus a fallback date in case that work never arrives. If nobody touches pricing for six months, that matters for upkeep even if the tool itself was well built.

A short note in the tracking issue is plenty:

```text
Investment: invoice comparison runner
Expected use: pricing changes that must preserve existing invoice totals
Current pain: rebuilding fixtures by hand and diffing mismatches manually
Track: relevant PRs, fixture repairs, cases the runner can't handle
Review after: three pricing changes, or next quarterly planning
Options: keep, simplify, fix one gap, archive
```

"Three changes" is a review budget, not a statistical sample. It just makes sure you actually look back instead of forgetting.

## Look at real work, especially the bypasses

When the trigger hits, pull up a handful of recent changes in that area, **including ones that didn't use the tool.** If you only look at successful runs, you'll miss setup friction, missing features, and the shortcuts people took to avoid dealing with your runner.

Talk to the person who made each change and compare their memory with the PR, incident log, or CI output. Keep time spent learning the business domain separate from time spent fighting the tool; both are real, but they point to very different fixes.

Here's a hypothetical review of our billing runner (invented observations, not real team metrics):

| Later change | What the runner did | What still hurt |
| --- | --- | --- |
| Effective-dated discount | Existing corpus caught an unintended change to old invoices | Needed a domain expert to judge whether one diff was a fix or a bug |
| Credit calculation refactor | Reused the corpus after patching the invoice adapter | Updating the adapter took longer than running the comparison |
| Refund correction | Bypassed completely; the runner doesn't support refunds | Engineer wrote a separate reproducer from scratch |

You don't need a big presentation to read that table. The invoice cases are pulling their weight, the adapter is too brittle and should be simplified, and skipping refunds might be totally fine if the runner was never meant to cover them. Turning every missing feature into a roadmap item is how small helpers balloon into internal platforms.

## Count the hidden upkeep and what changed around it

Add up the real carrying cost: broken fixtures, dependency bumps, cryptic CI failures, onboarding questions, and the private Slack messages the original author answers to help people run it. Tools often look "self-service" on paper only because nobody logs the DMs.

Keep sunk cost separate from future upkeep. The four days you spent building it tell you whether similar investments are worth starting in the future; ongoing upkeep tells you whether *this* one is worth keeping. Sunk effort is never a reason to keep nursing a bad tool, and a painful first week isn't a reason to delete something that's now cheap and genuinely useful.

Look at what changed outside the tool, too. Maybe the team understands billing better now, or the remaining migrations are tiny, or a library added the feature natively, or everyone simply postponed the hardest work. Any of those wrecks a naive before-and-after comparison. Google's [Eliminating Toil](https://sre.google/workbook/eliminating-toil/) chapter is good on this: price in the maintenance of automation, and always check whether the underlying chore can be designed away.

## Look beyond raw runtime

Cutting a script from ten minutes to ten seconds doesn't help much if engineers still spend an afternoon arguing over what the output means. Combine effort with harder questions:

- Could someone besides the author run it and interpret the failure?
- Did it catch a bug that mattered or verify a real guarantee?
- Did a later piece of work reuse its inputs or structure?
- Did it quietly push work onto another team or introduce a new way to break CI?

A string of green runs only proves what's inside the check's scope; three quiet months don't prove a tool prevented incidents. On the flip side, a rarely used disaster-recovery command can still earn its keep if you rehearse it periodically; don't judge everything by invocation count.

The [SPACE framework](https://www.microsoft.com/en-us/research/publication/the-space-of-developer-productivity-theres-more-to-it-than-you-think/) makes the broader point well: no single number captures developer productivity. Keep this review grounded in the specific work you were trying to improve, and never turn tool usage or time estimates into individual performance metrics.

## Make a call, including deleting what failed

Pick one small, finishable decision. For the billing runner above: keep the corpus, simplify the adapter, document that refunds live elsewhere, assign an owner, and check again on the next schema change. Don't spin up a "general billing test platform."

Just as often, the honest call is to retire something. Imagine a second hypothetical investment from the same billing service: a custom PR bot built to auto-generate test scenarios from OpenAPI diffs. After four schema changes, engineers spent more time deleting noisy generated fixtures than writing focused tests by hand, and two teams muted the bot. Rather than spending another sprint tuning heuristics, delete the bot, write down why it didn't stick, and free up the maintenance slot.

Write a few sentences right next to the tool or in the issue: the changes you inspected, the main cost, the call you made, and what would trigger another look. Don't build a separate reporting system nobody reads.

## Zoom out to the whole portfolio

Reviewing one artifact at a time has a blind spot: ten tools that each look "worth it" in isolation can still add up to slow CI, fragile schema changes, and a repo newcomers are afraid to touch.

Once or twice a year, list the retained helpers, custom linters, frozen baselines, and fixture suites in one place and look at their combined drag. If every ordinary feature PR now drags three separate harnesses along behind it, you're seeing negative compounding even if no single tool looks terrible on its own. Prune the weakest ones first using a [subtraction investigation](./subtraction-investigation.md) so you don't break a hidden consumer.

## Tell recurring savings apart from true compounding

A tool that saves an hour every migration pays for itself, and that's plenty. True compounding shows up when retained work makes the *next* capability cheaper to build: the invoice corpus feeds [competing prototypes](./competing-prototypes.md), or the scenario setup makes [differential verification](./differential-verification.md) practical for a scary rewrite.

When that happens, note what got reused, what it unlocked, and what adapting it cost. When it *doesn't* happen and maintenance starts growing faster than the benefit, retire it early while deletion is still cheap.
