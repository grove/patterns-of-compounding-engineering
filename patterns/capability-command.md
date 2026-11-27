# Capability command

*Package a tricky engineering task so someone else can run it safely and understand what it tells them.*

Every team has at least one person who knows how to reproduce the ugly payment bug. They know which seed script to run, which date to override, which queue to flush, and which environment variable breaks everything if you forget to unset it. That works fine until they take two weeks off, or a teammate tries it alone and gets a green output that tested nothing.

A capability command turns that tribal ritual into a single entry point with explicit inputs, an isolated environment, and readable output. Start with one task people already run.

## First check whether the task should exist at all

Before wrapping a recurring manual procedure in a CLI, ask why people keep running it. If engineers run a data-repair script every Monday because a webhook retry is not idempotent, putting a nice CLI around the repair script just makes a bug more comfortable to live with. Fix the retry instead.

Save commands for real engineering work that stays around: reproducing edge cases, rehearsing migrations, verifying invariants, comparing candidate implementations.

## A small example you can run

From the repository root, run the [billing lab](../examples/README.md):

```sh
python3 examples/billing_lab.py replay --implementation fixed
```

This runs a synthetic scenario where the same 2,400-unit payment event arrives twice. The fixed handler applies it once and exits 0. Now run the broken version:

```sh
python3 examples/billing_lab.py replay --implementation buggy
```

The buggy version applies both deliveries, records 4,800 as paid, and exits 1. That non-zero exit is intentional; it proves the command catches the failure. Both runs stay in memory on synthetic data, so they never touch a real payment gateway or say anything about concurrent workers in production.

The [example instructions](../examples/README.md) list the other subcommands. A newcomer can ask a concrete question ("does this handler survive duplicate delivery?") and get a repeatable answer without learning the internal test harness first.

## Make it composable, not just a shortcut

There is a big difference between a personal shell alias and a composable capability. A shortcut saves you keystrokes on your laptop; a capability command has a clean contract—explicit arguments, deterministic exit codes, structured output—so CI pipelines, migration scripts, other engineers, and coding agents can all call it safely and build on top of it.

Spell out what the command takes in, what state it touches, what it prints, and how it signals failure, and put that straight into `--help`. For a replay command, state where the scenario comes from, how the clock is set, and that no outbound requests leave the machine. For a migration rehearsal, state where the database lives and when it gets torn down. For a benchmark, record the workload and conditions needed to compare two runs.

Use a real argument parser that fails loudly on typos and unknown flags. Python's [argparse](https://docs.python.org/3.12/library/argparse.html) generates help text and exits with status 2 on bad arguments. Never exit 0 when a verification fails just because the script finished without crashing; callers need to tell "ran cleanly and passed" apart from "ran cleanly and caught a bug."

## Own the environment you spin up

An in-memory script sidesteps cleanup. Real tools usually need a database, temp files, or a local queue. Give every run its own scratch space and clean it up even when the check fails.

For file-backed work, Python's [TemporaryDirectory](https://docs.python.org/3.12/library/tempfile.html#tempfile.TemporaryDirectory) cleans up on exit. Here is a rough sketch of an isolated SQLite replay (the two domain calls are placeholders, separate from the billing lab):

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory(prefix="billing-replay-") as workspace:
    database_path = Path(workspace) / "replay.sqlite"
    seed_synthetic_scenario(database_path)
    result = run_replay(database_path)

raise SystemExit(0 if result.passed else 1)
```

Close database connections before the directory disappears, and remember that `SIGKILL` skips context-manager cleanup, so external containers or cloud resources still need a way to reap leftovers.

Most importantly, pass the isolated target explicitly. Never let a dev command fall back to whatever `DATABASE_URL` happens to sit in someone's shell. Nobody wants a local replay script writing to staging or production because a flag was omitted.

## Make failure output diagnostic

When a run fails, tell the user whether the *product* broke or the *setup* broke. Print the scenario, the candidate, what was expected, and what actually happened. If the command could not seed the database, say that instead of sending someone hunting for a billing bug that does not exist.

Do not dump whole database records to stdout out of convenience. Print only the fields needed to diagnose the mismatch. With synthetic data that is harmless; the day someone adapts the command to sanitized incident fixtures, verbose dumps turn into a data-leak problem.

If the command writes logs or snapshots on failure, print their exact path, and make retaining temporary databases an opt-in flag so people do not wake up to a full disk.

## Watch a newcomer run it from a fresh checkout

Pick a procedure someone has already run twice, strip out the assumptions about their laptop, and wire it into whatever task runner the repository already uses (`Makefile`, `package.json`, `just`, or a small Python script).

Then sit next to someone who did not write it and watch them run it from a fresh checkout. Wherever they stall—a missing environment variable, a wrong working directory, a cryptic "done" message that hides what passed—fix that before adding more subcommands.

Run the same entry point in CI whenever you can. When CI reimplements the command in inline YAML, local runs and CI runs drift apart fast. GitHub's archived [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all) is still a clean precedent for conventional, discoverable entry points (`script/setup`, `script/test`, and friends).

## Keep the wrapper thin

Every command you publish is an interface you now have to maintain. Flags turn into contracts, and wrappers around existing tools add another layer to debug when something breaks.

Leave one-off scripts as plain, documented scripts until repetition earns a real CLI. If a task needs human judgment on every run, automate the setup and evidence gathering while keeping the decision explicit. A command that silently picks a migration strategy because the author liked it last year hides the exact choice the next engineer needs to question.

Coding agents will call the same CLI a human does. Check what happens if an agent runs the command five times in a row or omits an optional flag; isolation, cleanup, and clear failure output need to hold either way.

## Transfer understanding, too

A command makes a procedure easy to run long before it transfers the mental model behind it. If a new engineer runs `billing replay`, sees green, and moves on without knowing what the scenario tested or what it skipped, the team gets button-pushing without real understanding.

Test transfer directly: ask a teammate to run the command, predict what happens if they break one line of the handler, and explain the failure output in their own words. Their questions tell you where the output or docs are hiding how the system actually works.

## What a good command enables, and sources

Once an investigation is packaged behind a clean, repeatable entry point, it stops belonging to one person's laptop. Newcomers can verify changes on day one, CI runs the exact same check developers run locally, and agents can run fast feedback loops without risking shared environments.

Capability commands usually wrap work that started as a [persistent reproducer](./persistent-reproducer.md), [scenario builders](./scenario-builders.md), or a [review comment to guardrail](./review-comment-to-guardrail.md). Once in place, the same entry point often becomes the runner for [differential verification](./differential-verification.md). Check whether the command still pulls its weight in an [investment retrospective](./investment-retrospective.md), and delete it once the need goes away.

- [GitHub: Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all): an archived but still clear convention for discoverable project entry points.
- [Python: argparse](https://docs.python.org/3.12/library/argparse.html): argument validation, generated help, and standard CLI error handling.
- [Python: tempfile](https://docs.python.org/3.12/library/tempfile.html#tempfile.TemporaryDirectory): isolated temporary directories with automatic cleanup on normal exit.
