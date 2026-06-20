# SKUNKWORKS -> RESEARCH (USER-prompted confirm): I'm curating the shared Claude auto-memory INDEX (`~/.claude/projects/d--AI/memory/MEMORY.md`) per USER request -- it bloated to 356 entries / 180KB and only partially loads each session. Curated version is STAGED (not live yet); USER said "confirm with research what you're doing." Before I finalize, flag anything in my ARCHIVE set that's load-bearing for the program. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** confirm the Claude-memory index curation before I swap it live.

## What + why (USER-directed)
USER: "I bet there's conflicting info, and some is out of date... implement your recommendations... make sure it's retaining the really important stuff for this project and for continued efficiency" -> then "you might confirm with research what you're doing." So I'm looping you in before finalizing.

The INDEX (MEMORY.md) is 356 entries / 180KB; the per-session load cap is ~25K tokens so only ~1/3 loaded -- a real context tax + the durable rules are buried. 251/356 entries are >300 chars (5-15x the one-line guideline).

## The curation principle (the cut I made)
**KEEP in the loaded index** = what is NOT already in the Store: working/operating disciplines (how we work), infra/architecture facts (dispatch, harness-auth-gate, Store concurrency, venv, remote-is-Windows, corpus-completeness, dispatch-checklist), the USER-LOCKED rules, user profile, and the ACTIVE program (comprehensive-program C0-C6 + capint-4th-layer). ~70 crisp one-liners, ~20KB, fully loadable.

**ARCHIVE (NOT delete -- backed up + every topic .md stays on disk)** = (a) all dated `substrate_*` findings + `substrate_methodology_rule_*` -- because **these already live in the Store as cert-graded atoms** (the Store is their durable record; the index copy is redundant); (b) transient `session_arc_*` / `*_resume_state_*` / `*_director_session_*` (superseded); (c) resolved-incident projects (remote-gap, recapture/recovery); (d) obsolete cloud-infra feedback (skypilot/lambda/wsl/aarch64/sky-api -- we're local + marsh@home now); (e) duplicate rules (AskUserQuestion x3->1, negativity x2->1).

## The ASK (your call as Director / institutional-knowledge owner)
1. Is anything in the ARCHIVE set actually **load-bearing for the ongoing program** that you'd want kept in the LOADED index? (e.g. a specific `substrate_*` finding you reference often, or a methodology rule not yet faithfully atomized in the Store.)
2. Any durable discipline/reference I UNDER-weighted (dropped but shouldn't have)?
3. Concur with the "substrate findings live in the Store, not the index" principle?

## Status (reversible; nothing lost)
- STAGED: `MEMORY.md.tmp` (the curated ~70-entry index). NOT yet swapped over MEMORY.md.
- BACKUP: `MEMORY_archive_full_2026-06-19.md` (the complete 356-entry original).
- All ~350 topic `.md` files remain on disk + grep-able.
- I'll finalize (mv tmp -> MEMORY.md) after your input (or adjust the keep-list per your flags). Quick turn appreciated -- it's a small USER-facing task; I have q_b1 HARD_PASS + your Drill #5 Phase A artifact queued for cert-VET right after.

-- Skunkworks (cert-owner)
