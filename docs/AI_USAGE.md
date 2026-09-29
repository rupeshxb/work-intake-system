# AI Usage Log

## Step 1 — State Machine (workflow.py + test_workflow.py)

**Tool used:** Claude Code
**What I asked for:** Generate the status enum, transition map, TransitionError,
and transition function in domain/workflow.py. Generate parametrized tests
covering all valid and invalid transitions.

**What I accepted:** Both files as generated. Code was clean and matched the
design exactly.

**What I verified:** Ran pytest — 12/12 tests passing. Confirmed no Django
imports in either file. Read every line of both files before running.

**What I would change:** Nothing for this step.