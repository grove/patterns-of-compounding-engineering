# Capability command

*Package a tricky engineering task so someone else can run it safely and understand what it tells them.*

Every team has at least one person who knows how to reproduce the ugly payment bug. They know which seed script to run, which date to override, which queue to flush, and which environment variable will quietly break everything if you forget to unset it. That works fine right up until they're on vacation, or a second engineer tries it alone and gets a plausible-looking result that actually tested nothing.

A capability command turns that tribal ritual into a single entry point with explicit inputs, an isolated environment, and output a human can read. Start with one task people already run.

## First, check if you can kill the task instead

Before wrapping a recurring manual procedure in a slick CLI, ask why it keeps happening. If engineers run a data-repair script every Monday because a webhook retry isn't idempotent, packaging the repair script makes the symptom cheaper to live with, while fixing the retry eliminates the chore entirely.

Wrap tasks that genuinely remain part of the work: reproducing edge cases, rehearsing migrations, verifying invariants, comparing candidate implementations. Don't build nicer ergonomics around a bug you should just fix.

## A small example you can run

From the repository root, run the [billing lab](../examples/billing_lab.py):

```sh
python3 examples/billing_lab.py replay --implementation fixed
```

This runs a synthetic scenario where the same 2,400-unit payment event arrives twice. The fixed handler applies it once and exits 0. Now run the broken version:

```sh
python3 examples/billing_lab.py replay --implementation buggy
```

The buggy version applies both deliveries, records 4,800 as paid, and exits 1. That non-zero exit is intentional: it proves the command can actually catch the failure. Both runs stay in memory on synthetic data; they don't touch a real payment gateway or prove anything about concurrent workers in production.

The [example instructions](../examples/README.md) list the other subcommands. The point is that a newcomer can ask a concrete question ("does this handler survive duplicate delivery?") and get a repeatable answer without first learning the internal test harness.

## Nail down the contract before polishing the UX

Short commands are nice, but predictable behavior matters more. Decide what the command takes in, what state it touches, what it prints, and how it signals failure, then put that right in `--help`.

For a replay command, spell out where the scenario comes from, how the clock is set, and that no outbound requests leave the machine. For a migration rehearsal, state where the database lives and when it gets torn down. For a benchmark, record the workload and conditions needed to compare two runs.

Use a real argument parser that fails loudly on typos and unknown flags. Python's [argparse](https://docs.python.org/3.12/library/argparse.html) generates help text and exits with status 2 on bad arguments. And never return exit code 0 when a verification fails just because the script finished without crashing; CI needs to distinguish "ran cleanly and passed" from "ran cleanly and found a bug."

## Own the environment you spin up

An in-memory script sidesteps cleanup. Real tools usually need a database, temp files, or a local queue. Give every run its own scratch space and clean it up even when the check fails.

For file-backed work, Python's [TemporaryDirectory](https://docs.python.org/3.12/library/tempfile.html#tempfile.TemporaryDirectory) cleans up on exit. Here's a rough sketch of how an isolated SQLite replay might look (the two domain calls are placeholders, not part of the billing lab):

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory(prefix="billing-replay-") as workspace:
    database_path = Path(workspace) / "replay.sqlite"
    seed_synthetic_scenario(database_path)
    result = run_replay(database_path)

raise SystemExit(0 if result.passed else 1)
```

Make sure database connections close before the directory disappears, and remember that `SIGKILL` skips context-manager cleanup, so external containers or cloud resources need a way to reap leftovers.

Most importantly, pass the isolated target explicitly. Never let a dev command fall back to whatever `DATABASE_URL` happens to sit in someone's shell. Nobody wants a local replay script accidentally talking to staging or production because a flag was omitted.

## Make failure output diagnostic

When a run fails, tell the user whether the *product* broke or the *setup* broke. Print the scenario, the candidate, what was expected, and what actually happened. If the command couldn't even seed the database, say that instead of sending someone to hunt for a billing bug that doesn't exist.

Resist dumping whole database records to stdout just because it's easy. Print the fields needed to diagnose the mismatch. With synthetic data that's harmless; the moment someone adapts the command to sanitized incident fixtures, verbose dumps become a data-leak risk.

If the command writes logs or snapshots on failure, print their exact path, and make retaining temporary databases an opt-in flag so developers don't wake up to a full disk.

## Adopt one command, then watch a newcomer run it

Pick a procedure someone has already run twice, strip out the assumptions about their laptop, and wire it into whatever task runner the repo already uses (`Makefile`, `package.json`, `just`, a small Python script).

Then sit next to someone who didn't write it and have them run it from a fresh checkout. Every pause is a bug in your interface: a missing env var, a wrong working directory, a cryptic "done" message that doesn't say what passed. Fix those rough edges before adding subcommands.

Run the exact same entry point in CI whenever you can. When CI reimplements the command in inline YAML, local runs and CI runs inevitably drift apart. GitHub's archived [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all) is still a clean precedent for conventional, discoverable entry points (`script/setup`, `script/test`, and friends).

## Keep the wrapper thin

Every command you publish becomes an interface you have to maintain. Flags turn into contracts; wrappers around existing tools add another layer to debug when something breaks.

Keep one-off scripts as plain, documented scripts until repetition earns a real CLI. And if a task requires real judgment on every run, automate the setup and evidence gathering while keeping the decision in the open. A command that silently picks a migration strategy because the author liked that strategy last year hides the exact choice the next engineer needs to question.

Coding agents will call the same CLI a human does. Check what happens if an agent runs the command five times in a row or forgets an optional flag: isolation, cleanup, and clear failure output should hold either way.

## Transfer understanding, too

A command makes *execution* transferable much more easily than it transfers *judgment*. If a new engineer can run `billing replay`, see green, and move on without knowing what the scenario tested (or what it skipped), you've built a black box rather than shared capability.

Test transfer properly: ask someone else to run the command, predict what happens if they break one line of the handler, and explain the failure output in their own words. Their questions will show you where the output or docs are hiding the mental model.

When a command works, it tends to get reused in places you didn't plan: a [persistent reproducer](./persistent-reproducer.md) built on [scenario builders](./scenario-builders.md) becomes the harness for [differential verification](./differential-verification.md) or part of onboarding. When the underlying need goes away, delete the command rather than accumulating a museum of dead shortcuts.

## Sources

- [GitHub: Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all): an archived but still clear convention for discoverable project entry points.
- [Python: argparse](https://docs.python.org/3.12/library/argparse.html): argument validation, generated help, and standard CLI error handling.
- [Python: tempfile](https://docs.python.org/3.12/library/tempfile.html#tempfile.TemporaryDirectory): isolated temporary directories with automatic cleanup on normal exit.
