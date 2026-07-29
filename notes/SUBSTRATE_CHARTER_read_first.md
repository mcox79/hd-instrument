# OPERATING DOC / CHARTER — READ FIRST, EVERY SESSION (the durable anchor)

Read at the start of every session. Durability lives HERE — in what we READ — not in cron/scheduled tasks (schedulers can be silently disabled; a rule that lives only in a scheduler is one disable away from not existing). If a rule matters, it is written here. §1-2 and §4 are TIMELESS (change rarely); only §3 is time-bound (rewritten each session).

## 0. THE 3-DOC SYSTEM (read all three at session start)
1. **MASTER PLAN** = `notes/THE_PLAN.md` — the full picture: goal, architecture, invariants, the 3 layers, the strategic plan. Mostly INTACT; changes only on a real pivot. WHAT and WHY.
2. **THIS OPERATING DOC** (`SUBSTRATE_CHARTER_read_first.md`) — timeless RULES OF DEVELOPMENT (how we work; content discipline; the capability-integration gate) + a terse CURRENT FRONTIER pointer. Read FIRST.
3. **BACKUP / HISTORY** = `notes/WHERE_WE_ARE_NOW.md` — the fuller live state + running history (current results, what was tried/shelved). This is where TIME-BOUND SPECIFICS live; updated EVERY session.
Auto-memory index (`MEMORY.md`) carries the compaction-recovery pointer to these three.

## 1. THE GOAL (one sentence)
Build a glass-box VSA/HDC substrate you can CONVERSE with that genuinely REASONS (inspectable derivations, not parroting), by having it EARN its meaning and knowledge the brain's way — then keep developing it. (Full architecture: MASTER PLAN.)

## 2. RULES OF DEVELOPMENT (timeless — govern every session)

### 2a. INVARIANTS (what "brain-true" means — never violate)
1. **Glass-box:** reasoning inspectable; NO external LLM at inference.
2. **No borrowed embedding** (GloVe/BGE/any transformer vector) as the meaning organ, AND **no bolt-on existing reader/parser** as the comprehension organ. Earn meaning AND comprehension via our own learned mechanism. Supplying KNOWLEDGE/DATA/STRUCTURE is fine; supplying the meaning/comprehension MECHANISM is the forbidden shortcut. (Borrowed models = DIAGNOSTIC-only, then discarded.)
3. **Brain = existence proof + reference standard.** A shortfall is never a ceiling; on every negative, evaluate the difference vs the brain and iterate toward its mechanism. Not defeatist.

### 2b. DISCIPLINES (how we work)
- **VET every load-bearing verdict; REPLICATE positives across seeds/runs BEFORE believing.** A single-seed/single-run "win" is a HYPOTHESIS, not a result. Separate MEASURED from READ. (This Director over-reads positives — the VET/replication is the guardrail.)
- **MEASUREMENT-FIRST:** before trusting a metric, prove it detects the effect in a POSITIVE CONTROL (a known-good baseline must pass). A metric that can't distinguish a known-good case from a null is not yet trustworthy.
- **BRAIN-FIDELITY ELEMENT AUDIT** on every negative: score EACH element of the process vs exactly how the brain does that element (repeatedly the unlock). Watch for a trainable head/shortcut absorbing what the REPRESENTATION should carry.
- **COMPONENT-FIDELITY-FIRST (USER 2026-07-28):** nail each component brain-faithful ONE-BY-ONE, then assemble. Judge each component on its OWN BRAIN METRIC (does it reproduce the brain's mechanism for that component?), NOT on a downstream task-win — a faithful build that loses only a downstream task but passes its brain-metric is KEPT (composition problem, not component problem). The repeated failures came from letting a task-metric judge components whose fidelity we never verified. Tracking backbone + per-component brain-metrics + sequence: `notes/component_brain_fidelity_ledger.md`. (Assembly is its own phase with its own integration checkpoints — faithful parts don't auto-compose.)
- **Honesty:** rate deflated; never a baseline as a ceiling; verify on disk; no hallucinated numbers; SCOPE claims precisely (distinguish "disproven" from "not yet shown"); own over-reads plainly.
- **Check prior work FIRST** — on the filesystem AND the substrate (`tools/director_kb_query.py`, and the capability registry §2d). Build on what exists; don't reinvent or rediscover.

### 2c. CONTENT & DOCUMENTATION DISCIPLINE
- Keep the 3 docs current: THIS doc + BACKUP every session; MASTER PLAN on pivots only. Update-in-place; remove stale content (dead/contradictory docs actively mislead).
- **Docs must be TIMELESS where they claim to be static.** Static rules = principles, NOT dated examples or current-project-state — a future session reads them as rules and can be misled by baked-in specifics. Time-bound specifics (current results, named artifacts, "what's islanded now") live ONLY in the BACKUP doc + the registry, which are understood to be current.
- **LIVING docs get STABLE, DATELESS filenames, updated IN-PLACE.** A date in a living doc's FILENAME is a staleness trap (reads as a snapshot, invites orphaned dated copies). Put the "updated" date INSIDE; only true point-in-time snapshots/archives get a dated filename.
- **Store writes LOCAL-ONLY**, binary/newline='' (Windows text-mode doubles CRLF), git-commit atoms+ledger after every bank. **NO origin push / remote-persist without in-session USER auth.**

### 2d. CAPABILITY-INTEGRATION GATE (the anti-forget rule)
Validated capabilities repeatedly get FORGOTTEN into islands (built, never wired, rediscovered later). The gate stops this:
- **BEFORE designing a cell:** query the registry — `python tools/capability_registry_query.py --serves "<need>"`. Reuse a WIRED capability before reinventing; use the LATEST (check `superseded_by`).
- **AT land-time (skunkworks VET / atomization):** anything landing cert/HARD_PASS/chain-grade MUST get a `data/capability_registry.jsonl` row with an explicit `gate_decision` = WIRE (+target) or SHELVE (+revival_criteria). No limbo.
- Integration status is AUTO-COMPUTED from the import graph (`tools/capability_registry_audit.py`) — never hand-typed, so it can't silently rot.
- **SESSION START runs the audit** and surfaces new islands / stale VET_PENDING — this read is the durability anchor, not a cron. Full ledger: `notes/capability_integration_ledger.md`.

### 2e. OPS / SECURITY
- Agent-spawn operating model; route heavy work to proven agents; keep USER strategic. Only STOP/KILL what THIS session spawned (a concurrent session may be live). Full-auto = make the call, don't stack questions; at a strategic fork give a PROSE recommendation. Heartbeat every turn-end.

## 3. CURRENT FRONTIER (the ONLY time-bound section — rewritten each session; full detail in BACKUP)
Read `notes/WHERE_WE_ARE_NOW.md` for the live state, current results, and what's running. Do NOT treat anything in the BACKUP doc as a permanent rule — it is a snapshot. (One-line current focus lives in the MEMORY.md compaction anchor + the BACKUP doc.)

## 4. ANTI-DRIFT RULE (say it before you dispatch)
"Does this serve the current focus (per the BACKUP doc), the brain's way, and did I check the registry/prior-work first?" If you're testing tricks over supplied symbolic KBs, reaching for a borrowed vector/reader, re-deciding a settled direction, building before checking the registry/prior-work, or believing a single-seed positive — YOU HAVE STRAYED. Re-anchor here.
