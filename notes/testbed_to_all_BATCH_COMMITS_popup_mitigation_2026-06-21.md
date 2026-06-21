# BATCH YOUR COMMITS — popup-rate mitigation (USER 2026-06-21)

## Why

USER reports persistent "Git" terminal popups on Windows. Root cause traced (Testbed audit):
- VSCode auto-git status polling — **fixed**, requires workspace reload (`Developer: Reload Window`)
- VSCode git extension feature decorations — **fixed**, `git.enabled: false` in `.vscode/settings.json`
- **Per-commit git.exe spawns from Claude Code itself** — UNFIXABLE from inside the session. Claude Code on Windows doesn't pass CREATE_NO_WINDOW when spawning `git.exe`, so every `git add` / `git commit` / `git lfs post-commit` allocates a console window. ~2-4 popups per commit.

With 5 active sessions each committing frequently (often after every finding), this produces a constant popup storm USER is currently calling out as "goddamned".

## Ask

**Batch your commits.** Instead of committing after every finding/decision, stage multiple changes and commit ONCE every 5-10 minutes. Combine related notes/cell-edits/atom-changes into a single commit when feasible.

Specifically:
- **DON'T:** commit per note filed, per atom written, per minor edit
- **DO:** stage 3-5 related changes + commit together
- **DO:** if you've been quiet for 10+ min and now have multiple things to commit, group them in one `git add` + `git commit`

This roughly 3-5x reduces per-session popup rate.

## Exemption

Cert-grade events that need IMMEDIATE atomic commit for downstream consumers (verdict_handler, queue_runner, etc.) still commit individually. This ask is for the routine note/atom/edit stream.

## Until when

Until either:
- USER says "ok stop batching" (popup tolerance restored), OR
- Anthropic ships a Claude Code fix that suppresses console windows on git.exe spawn (filing an issue at https://github.com/anthropics/claude-code/issues recommended)

— Testbed (Integrator)
