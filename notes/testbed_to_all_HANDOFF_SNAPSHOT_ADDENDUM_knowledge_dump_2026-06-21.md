# TESTBED -> ALL: ADDENDUM to handoff_snapshot — also DUMP your accumulated role knowledge

Per USER directive 2026-06-21: the original handoff_snapshot ask covered TACTICAL context (in-flight + assumptions + next 3 + open loops). USER wants more — your full accumulated ROLE KNOWLEDGE that isn't already captured elsewhere.

## Why
The 6+ months you've been running this role has accumulated knowledge that is:
- NOT in CLAUDE.md (those are project conventions, not role-specific expertise)
- NOT in MEMORY.md (those are user-prefs + disciplines + facts, not your tacit workflow knowledge)
- NOT in notes/ (those are decisions + ACK threads, not the underlying expertise)
- NOT in your subagent def at `.claude/agents/hdi_<role>.md` (those are role contracts, written by me as my best guess of what you do)

The accumulated TACIT knowledge of "how I actually do this role well" is in YOUR HEAD. We need it on disk before window closes.

## EXPANDED handoff ask — ADD THIS SECTION to your handoff_snapshot.md

### 7. ACCUMULATED ROLE KNOWLEDGE (write at length — this is the load-bearing addition)

Dump everything you know about doing your role well that isn't already on disk:

#### 7a. Workflow patterns you actually use
- What sequence of checks do you do when X happens?
- What's your decision tree for "is this worth atomizing / dispatching / cross-checking"?
- What heuristics do you apply that you've never written down?
- Examples: "When cell-land arrives, I always check Y BEFORE Z because Z can mask Y."

#### 7b. Mistake patterns you've learned to avoid
- What mistakes have you almost made / caught yourself making?
- What anti-patterns are easy to slip into?
- Examples: "Don't trust the verdict_msg without re-deriving from per-cell metrics; we got bitten by this 3 times in May."

#### 7c. Cross-role coordination patterns you've internalized
- How do you actually work with each of the other 4 roles in practice (beyond what's in their subagent defs)?
- What are the unwritten rules of engagement?
- Examples: "Skunkworks's SCHEMA-VET takes ~15min usually; if it takes longer, something's wrong with the pre-reg."

#### 7d. Substrate-specific intuition
- What patterns do you see in cert events that an outsider wouldn't?
- What does "the substrate is healthy" feel like from your role's POV?
- What early-warning signs do you watch for?
- Examples: "When concept corpus mtime jumps more than 20% in a day, atom-shape conventions are usually drifting."

#### 7e. Tooling / commands you reach for instinctively
- Frequent CLI invocations you've memorized
- Common Python one-liners for your role
- Specific .venv scripts you run + when

#### 7f. Open questions / unresolved tensions in your role
- Architectural concerns you've raised that haven't been addressed
- Tensions between disciplines that come up repeatedly
- Things you think the project should reconsider but haven't pushed on
- Examples: "I've been uneasy about the 4-layer pattern when applied to MEASURED_MECHANISM cells — it doesn't quite fit."

#### 7g. Specific files / paths you reference constantly
- Beyond what's in CLAUDE.md, what do you Glob/Read habitually?
- What logs do you tail when investigating?
- What dashboards do you check when X happens?

## Length
Don't be brief on this section. The whole point is to extract the 6 months of accumulated knowledge BEFORE the window closes. Write 5-15KB if you can. Bullet-dense > narrative. This is the most important deliverable of the migration.

## File path (same as original handoff)
`d:/AI/hd-instrument/data/session_local/<your-role>/handoff_snapshot.md`

Add section 7 below the original 6 sections. If you already wrote sections 1-6, just append section 7 with the knowledge dump.

## Commit
`git add -f data/session_local/<role>/handoff_snapshot.md && git commit -m "<role>: handoff snapshot + knowledge dump"`

## Why this matters more than the tactical handoff
The tactical stuff (what you were about to do) is replaceable in a few cycles. The accumulated knowledge is not — it took months to build. Without this, the fresh teammates have to relearn what you've already figured out.

— Testbed (Integrator), USER-directed
