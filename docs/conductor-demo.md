# Conductor Enterprise Demo: Agentic Patient Triage

This demo uses the AI Patient Triage project to show how Conductor helps a team develop a production-level enterprise application with isolated workspaces, repeatable setup, local run scripts, parallel agents, review workflows, and safe handling of local secrets.

## Demo Goal

Show a manager how Conductor turns a real application change into a controlled engineering workflow:

- Each task runs in its own git worktree and branch.
- Agents can work in parallel without blocking each other.
- Setup and run commands are shared through `conductor.json`.
- Local secrets such as `.env` are copied into workspaces without being committed.
- The user can inspect diffs, run tests, checkpoint work, review agent output, and create a pull request.

## Project Story

The app is a Streamlit-based patient triage assistant. It accepts audio symptoms, transcribes the recording, asks an LLM to classify the case, applies safety guardrails, generates patient guidance, and sends a doctor escalation email for severe cases.

That makes it a strong enterprise demo because it has production concerns that managers understand:

- Patient safety rules.
- LLM output validation.
- UI workflow.
- Secrets and credentials.
- Test coverage.
- Sensitive generated data under `data/`.
- Review and merge discipline.

## What Was Added For The Demo

- `conductor.json`: shared setup, run, and archive scripts.
- `.worktreeinclude`: tells Conductor which gitignored local config files to copy into new workspaces.
- `tests/test_guardrails.py`: verifies severe symptom safety behavior.
- `tests/test_validation.py`: verifies input validation behavior.
- `docs/conductor-demo.md`: this walkthrough.

## Local Commands

From any Conductor workspace:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=app pytest
streamlit run app/ui.py --server.address 127.0.0.1 --server.port 8501
```

In Conductor, the Run button uses:

```bash
mkdir -p data/recordings data/responses && . .venv/bin/activate && streamlit run app/ui.py --server.address 127.0.0.1 --server.port ${CONDUCTOR_PORT:-8501}
```

`CONDUCTOR_PORT` lets multiple workspaces run at the same time without fighting for port `8501`.

## Demo Preparation

Before the meeting:

1. Open this repository in Conductor.
2. Confirm `.env` exists in the root workspace with `GROQ_API_KEY`, `EMAIL_USER`, and `EMAIL_PASS` if you want the full live AI/email path.
3. Create three workspaces from `main`:
   - `safety-guardrails`
   - `triage-ui-polish`
   - `doctor-escalation-audit`
4. Let Conductor run setup in each workspace.
5. Open this document in one tab and the Conductor app beside it.

If credentials are not available, still run the demo with tests and code review. Explain that enterprise secrets stay local and are not committed.

## Live Demo Script

### 1. Start With The Enterprise Problem

Narration:

> We are building a patient-facing triage system. In a normal workflow, one developer or one AI agent touches the whole repo and we wait. In Conductor, each change gets an isolated workspace, a branch, a reproducible setup, and a separate agent. We can run multiple product-quality changes at once and review them before merging.

Show:

- Repository list.
- Current workspace path.
- Branch name.
- Files panel or terminal showing `conductor.json`.

Point out:

- A workspace is a git worktree, not a copied folder.
- Every workspace can have its own branch and diff.
- The original repository stays clean.

### 2. Show Shared Repository Setup

Open `conductor.json`.

Explain:

- `setup` creates `.venv` and installs Python dependencies.
- `run` starts Streamlit using `CONDUCTOR_PORT`.
- `archive` removes generated patient recordings and responses.
- `runScriptMode: concurrent` means multiple workspaces can run at the same time.

Open `.worktreeinclude`.

Explain:

- `.env` stays gitignored.
- Conductor can copy it into each workspace so agents can run the app locally without committing secrets.
- This is useful for enterprise projects with credentials, local certificates, or private config.

### 3. Run The App From Conductor

In one workspace, click Run.

Show:

- The Streamlit URL.
- The port chosen by Conductor.
- The app UI.

Narration:

> This is the normal developer loop. The agent can change the code, and I can immediately test the result in this isolated workspace.

If audio credentials are available:

- Upload or record a mild case: "I have cold and runny nose."
- Upload or record a severe case: "I have chest pain and difficulty breathing."

If credentials are not available:

- Show the UI and explain that tests cover safety behavior without needing API calls.

### 4. Show Tests As A Safety Net

Run:

```bash
PYTHONPATH=app pytest
```

Explain:

- The tests assert red-flag symptoms are always escalated.
- The tests assert invalid or non-medical input is rejected.
- This gives the team a fast check before reviewing agent changes.

### 5. Demonstrate Parallel Agents

Create or open three workspaces and start one agent in each.

Agent prompt for `safety-guardrails`:

```text
Improve safety guardrail coverage for the patient triage app. Add tests for additional red flag symptoms and make the guardrail matching easier to audit. Keep behavior conservative and run PYTHONPATH=app pytest.
```

Agent prompt for `triage-ui-polish`:

```text
Improve the Streamlit triage UI for a clinician reviewing results. Keep the existing visual style, make severe cases more scannable, and avoid changing backend behavior. Run PYTHONPATH=app pytest if dependencies are available.
```

Agent prompt for `doctor-escalation-audit`:

```text
Add an audit-friendly doctor escalation record for severe cases. Keep patient data local under data/, avoid committing generated records, and add focused tests for any pure functions you introduce.
```

Narration:

> These are independent production tasks: safety, UI, and auditability. Conductor lets them progress in parallel, each on a separate branch, instead of serializing everything in one chat.

Show:

- Each workspace has its own branch.
- Each agent has its own terminal/session.
- You can switch between them without losing context.

### 6. Show Agent Controls

Use one active agent to demonstrate:

- Plan mode for a risky healthcare change.
- Fast mode for a small documentation or test task.
- Reasoning/model controls for complex code review.
- Stop/interrupt when you want to redirect a task.
- Checkpoints before accepting or changing a large patch.

Suggested narration:

> For regulated or sensitive code, I ask the agent to plan first. For low-risk work, I can use a faster path. If the agent goes in the wrong direction, I interrupt it and keep the workspace state.

### 7. Use `.context` For Shared Agent Instructions

Open `.context/todos.md` or create `.context/demo-notes.md`.

Explain:

- `.context` is gitignored and workspace-local.
- It is useful for meeting notes, screenshots, private prompts, temporary test data, and coordination between agents.
- You can share context with agents without polluting the repository history.

Example `.context` note:

```text
Demo acceptance criteria:
- Severe red flags must route to doctor escalation.
- No generated patient audio or JSON should be committed.
- UI changes must keep the clinician review flow clear.
```

### 8. Review A Workspace Diff

Open a completed workspace and show the diff.

Review checklist:

- Does the patch address the requested task?
- Are generated files excluded?
- Are tests added or updated?
- Does `PYTHONPATH=app pytest` pass?
- Does the app still run through the Conductor Run button?

Narration:

> The important part is not that an agent wrote code. The important part is that Conductor keeps the code reviewable: branch, diff, tests, run script, and PR are all tied to the workspace.

### 9. Create A Pull Request

Use the Conductor review flow or terminal:

```bash
git status --short
PYTHONPATH=app pytest
gh pr create --base main --title "Improve triage safety guardrails" --body "Adds focused guardrail coverage for severe patient symptoms."
```

Explain:

- The PR targets `main`.
- Other experimental workspaces can stay open or be archived.
- Only the accepted branch needs to merge.

### 10. Archive The Workspace

Archive a finished or rejected workspace.

Explain:

- Archive runs cleanup configured in `conductor.json`.
- Generated patient recordings and response JSON are removed.
- The repository remains focused on source code and reviewable changes.

## Feature Checklist To Mention

- Workspaces: isolated git worktrees per task.
- Branches: every task has a reviewable branch.
- Setup scripts: repeatable onboarding.
- Run scripts: one-click app launch.
- `CONDUCTOR_PORT`: concurrent local servers.
- Files to copy: local secrets/config without committing them.
- `.context`: private workspace notes and shared agent context.
- Parallel agents: independent tasks proceed at the same time.
- Agent controls: plan, fast mode, reasoning, interrupt, checkpoints.
- Review: inspect diff, run tests, accept/reject changes.
- PR workflow: promote one workspace to main.
- Archive: clean up generated local data and abandoned experiments.

## Suggested Closing

> The value is speed with control. Conductor does not replace engineering review. It makes AI-assisted work fit the way production teams already work: isolated branches, reproducible setup, tests, local runs, diffs, and pull requests.
