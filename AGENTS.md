# Working on the field guide

Read [CONTRIBUTING.md](./CONTRIBUTING.md) and [Using the guide](./guide.md). Keep examples synthetic and distinguish tested behavior from production guarantees.

Use [technical review](./skills/technical-review/SKILL.md) for substantive pattern or example changes. Use [subtraction investigation](./skills/subtraction-investigation/SKILL.md) for a proposed removal; it defaults to read-only. For substantial writing changes, use the companion [editorial review procedure](https://github.com/grove/engineering-that-compounds/tree/main/skills/editorial-review) if available.

Run from the root:

```sh
python3 -m unittest discover -s tests -v
python3 site/build.py --check
```

At the end of a meaningful task, consider a [compounding pass](./skills/compounding-pass/SKILL.md). It recommends at most one small improvement by default. Do not create a document or skill just to demonstrate that the pass ran; nothing may be worth retaining.

Keep changes within the requested scope. The skills do not grant permissions or authorize deployment, deletion, or access to live systems.
