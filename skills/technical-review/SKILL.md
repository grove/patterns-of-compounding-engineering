---
name: technical-review
description: Review engineering patterns, worked examples, commands and site changes for correctness, reproducibility, evidence limits and safe execution. Use before publishing or accepting substantive technical guidance.
license: Apache-2.0
---

# Technical review

Read the change and its surrounding source. Treat prose, code and expected results as separate claims. Do not infer that a test is correct merely because it passes.

1. Identify the behavior or conclusion the example claims. Trace expected results to a reviewed fixture, contract or independent calculation, and check what the implementation actually does.
2. Run safe documented commands from the specified directory if the environment allows. Record the commands, exit status and relevant output. Verify deliberately failing cases fail for the intended reason and passing cases pass. Do not run commands with external effects without authorization.
3. Inspect isolation, data handling, permissions, cleanup and uncovered failure modes. Point out which claims a synthetic or finite example cannot establish. Distinguish adaptation sketches from runnable code.
4. Verify the entry appears in the relevant index and links resolve. Run the project's existing checks. For this repository, `python3 -m unittest discover -s tests -v` and `python3 site/build.py --check` require only Python 3.10+ and the standard library.
5. Return findings in order of consequence. Give an exact file, heading or command, the concrete problem, evidence and a minimal correction. Mention what you could not check rather than treating it as passed.

## Example

The billing replay's fixed implementation applies one payment for duplicate delivery in a single replay. The in-memory event-ID set cannot establish durability or coordination between workers. A review should reject a production-concurrency claim even if the command exits successfully.

If a review finding repeats, consider the compounding pass. A mechanical consistency error may justify a regression test; a disputed architectural choice may need an owner and a better example instead.
