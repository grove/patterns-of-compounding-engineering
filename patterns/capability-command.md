# Capability command

*Make a useful engineering task safe and repeatable for its next user.*

Someone on the team knows how to reproduce a failed payment. They know which seed script to run, which date to substitute, which queue to clear and which environment variable must be unset. The procedure works while that person is available. A second engineer attempting it alone has several opportunities to get a plausible but irrelevant result.

Package that procedure as a command with explicit inputs, a known environment and an outcome people can interpret. Begin with one task that is already useful. The command should remove setup decisions the next person would otherwise have to rediscover.

## A small example you can run

From the root of this repository, run the supplied [billing lab](../examples/billing_lab.py):

```sh
python3 examples/billing_lab.py replay --implementation fixed
```

The fictional scenario delivers the same payment event twice against an invoice for 2,400 minor units. The fixed implementation applies one event and records 2,400 as paid. Change the implementation to see the original failure:

```sh
python3 examples/billing_lab.py replay --implementation buggy
```

The buggy version applies both deliveries, records 4,800 as paid and exits unsuccessfully. That failure is expected: it demonstrates that the scenario can distinguish the implementations. Both runs use in-memory synthetic state. They do not contact a payment service, read production data or prove that a real concurrent service handles duplicate delivery correctly.

The [example instructions](../examples/README.md) describe the other commands. A reader can start with a concrete question and obtain a repeatable result without learning the internal test runner first.

## Define the contract before shortening the command

A short command is only useful if its meaning is stable. Decide what it takes as input, what it changes, what it reports and how it fails. Put these decisions in its help text and a brief repository entry.

For a replay command, specify the source of the scenario, how the clock is set and whether it can send external requests. For a migration rehearsal, specify the source and lifetime of its database. For a benchmark, record the workload and the conditions needed to compare runs.

Use a command-line parser to reject unknown flags and invalid values. Python's [argparse](https://docs.python.org/3.12/library/argparse.html) generates help and normally reports invalid arguments with exit status 2. Keep an unsuccessful verification distinct from successful execution in the command's exit status, and explain the difference in its output.

For example, a replay can complete normally while establishing that the candidate applied a payment twice. Returning success because the script reached its last line would make it unsuitable for CI.

## Own the environment you create

The in-memory lab avoids most cleanup problems. A real application may need a database, files or a queue. Give each invocation its own resources and arrange cleanup even when the verification fails.

For a file-based exercise, Python's [TemporaryDirectory](https://docs.python.org/3.12/library/tempfile.html#tempfile.TemporaryDirectory) provides a directory with cleanup on context exit. The following sketch shows how a command might isolate a database-backed replay; the two domain functions are application-specific, not functions supplied by the billing lab:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory(prefix="billing-replay-") as workspace:
    database_path = Path(workspace) / "replay.sqlite"
    seed_synthetic_scenario(database_path)
    result = run_replay(database_path)

raise SystemExit(0 if result.passed else 1)
```

The domain functions must close their database connections before the temporary directory is removed. External resources need their own cleanup, including a way to recover leftovers after a killed process. A context manager cannot clean up after every possible termination.

Pass the isolated resource explicitly to the application. Avoid a fallback that reads whichever database URL happens to exist in the shell. A development command should not acquire a production destination because its preferred local configuration was missing.

## Make failure useful

Report enough context to distinguish a failed assertion from a failed setup: the selected scenario, candidate, expected value and observed value. If the command could not construct its environment, say so before suggesting a product defect.

Avoid printing full records merely to make debugging easier. Choose the fields needed to understand the result. With synthetic data this is straightforward; a later extension to sanitized incident fixtures needs a deliberate review of what its output exposes.

A command that leaves useful diagnostic artifacts should say where they are. If preserving those artifacts changes the cleanup contract, make that an explicit option. Do not retain every temporary database by default and leave developers to discover why their disk is full.

## Adopt one command at a time

Choose a procedure that has already been repeated, or one whose next use is close enough to matter. Preserve the working script, remove assumptions about the author's machine and write down its dependencies. A task runner or package script is sufficient when the project already has one.

Then ask someone unfamiliar with the task to run it from a fresh checkout. Watch where they pause. Missing credentials, an undocumented working directory and an ambiguous success message are defects in the command's interface. Fix those before adding a menu of related operations.

Use the same entry point in CI when the environment permits it. A second implementation of the procedure in a workflow file can drift from what developers run locally.

GitHub's historical [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all) gives a concrete precedent: conventional entry points for setup, tests and other development tasks across projects. The repository is archived, but the convention remains a useful example of making common work discoverable.

## Keep the abstraction small

There is a cost to supporting a command. Its flags become an interface. Its dependencies need updates. An obscure wrapper around a perfectly adequate existing tool may add another place to investigate when something fails.

Keep one-off experiments as documented scripts until repetition justifies more. If the task requires substantial judgment on every run, automate preparation and evidence gathering while leaving the decision visible. A command that silently chooses a migration strategy because the author once made that choice hides the part a later engineer most needs to reconsider.

An agent can use the same interface as a person. Check what happens when an automated caller repeats the command or omits a flag: each invocation should retain the same isolation, cleanup and failure reporting.

## Check whether the capability transferred

Success means another engineer can complete the task, interpret its result and recover from a failure without its original author. Note the time spent on setup, requests for help and differences between local and CI results. Count the maintenance work too.

A reliable replay command can later serve a migration comparison or an onboarding exercise. That reuse is the practical return. If nobody uses the command and the underlying task disappears, remove it instead of preserving a growing catalogue of obsolete shortcuts.

## Related patterns

[Persistent reproducer](./persistent-reproducer.md) supplies a valuable first task. [Scenario builders](./scenario-builders.md) supply explicit starting states. [Differential verification](./differential-verification.md) can reuse the command's isolated setup to compare alternatives.

## Sources

- [GitHub: Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all). An archived, concrete example of shared command conventions for development work.
- [Python: argparse](https://docs.python.org/3.12/library/argparse.html). Input validation, help generation and command-line errors.
- [Python: tempfile](https://docs.python.org/3.12/library/tempfile.html#tempfile.TemporaryDirectory). Temporary resource ownership and normal context-manager cleanup.
