# SUBSTRATE PROCESS + ROADMAP — the single owner's-eye view of how this project is managed and where it's going

> **Owner 2026-09-10: "we don't yet have a robust process that ensures the substrate is optimally managed and
> evaluated, with a clear plan for development" + "you are strategy — you need to OWN this project."**
> This is the answer: ONE authoritative doc for the PROCESS (how the substrate stays healthy) and the ROADMAP
> (the prioritized development plan). It ends the plan-doc fragmentation (BUILD_PLAN / THE_PLAN / LONG_TERM_PLAN /
> PLAN_NEXT_* / OVERNIGHT_PLAN / CONSOLIDATION_PHASE_PLAN / … were ~15 overlapping files). **This doc + the derived
> `tools/substrate_health.py` are the two things to read; everything else is detail they point to.**

---

## 1. THE HEALTH VIEW (derived — the single source of truth for "is it healthy")
**`python tools/substrate_health.py`** — derived from disk every run (cannot rot). Reports: BF status (BF/BF_SPIRIT/
NOT_BF + each NOT_BF's fix problem + state), the integration backlog (owner-DONE awaiting fold-in), in-flight
submissions (awaiting owner review), the assignable-problem queue, lifetime integrated count, the board aggregate +
its age, and the CONSISTENCY GATES that must hold. `--gaps` = only failures; `--check` = exit 1 if a gate fails.
**The gates (must always hold):** every live `situation_reader` import is BF-tagged · open-problem priorities are
unique · the owner-DONE fold-in backlog is empty · STATUS.md is fresh (<2 days).

## 2. THE PROCESS (the maintenance cadence I drive as strategy)
Every working cycle, in order:
1. **`substrate_health.py` → act on TOP ISSUES worst-first.** A failing gate or a non-empty owner-DONE backlog is
   the highest priority — fix it before anything else.
2. **Integrate owner-DONE promptly** (the standing rule): reverify first-hand → grade → land the BF pieces + ALL
   upstream-chain fixes → INGEST any grown knowledge LIVE (`KNOWLEDGE_ASSET_REGISTER.md`) → §2b + ledger + the
   cross-solution map's PROPAGATION STATUS → commit path-limited, NOTHING pushed.
3. **Keep the fleet fed:** if `assignable OPEN == 0`, post the next ROADMAP items (§4) as briefs (8 guard sections
   + the standing blockquotes; cert `verification/test_problem_briefs_and_flags.py`). De-dup against existing
   problems first.
4. **Propagate:** when a component is improved, walk `CROSS_SOLUTION_IMPROVEMENT_MAP.md` PART 2 for its consumers and
   apply/queue each; record in the PROPAGATION STATUS block.
5. **Evaluate on a cadence:** run the full board (`exp_situation_model_qa_modern_v1.py --run`) at each integration
   wave to get a fresh trend point; a board-invisible proven win gets its own instrument-arm (unless, like
   `causal_sign`, its signal needs a scale the board can't run — then its dedicated witness is the instrument).
6. **Prune + re-audit at land:** orphaned old versions pruned (3-gate; dormant ORGANS never pruned); every incoming
   solution re-audits its entire upstream chain for BF-fidelity (that audit seeds the next problem).
7. **Keep the anchors current:** STATUS.md top block + this roadmap reflect what actually landed (a plan you didn't
   update is a plan you didn't read).

## 3. THE GOVERNANCE MODEL (roles + gates)
- **Strategy (this session) OWNS:** the roadmap, all `hdlab/` writes (Q111), brief authoring, integration, the BF
  registry, this process. **Solvers** each solve one bounded posted problem (experiments/ + verification/ + their
  folder). **Owner** reviews submissions (`owner_verdict: DONE` gates integration) + answers the board.
- **Hard invariants (never violated):** NO external LLM/tool at inference · every live component 100% BF (a NOT_BF
  organ is a DEFECT that blocks — fix or remove) · integrate only on owner-DONE · commit path-limited, only the
  orchestrator pushes · never edit `preregs/**` or `arm_key*` · 19c corpora banned for grading.

## 4. THE DEVELOPMENT ROADMAP (prioritized — the clear plan)
Ordered by leverage; re-derive the live status any time with `substrate_health.py`.
**NOW — close out the NOT_BF defects (the 100%-BF gate).** 7 of the 8 NOT_BF organs have fleet solutions in the
review queue (parser cluster → pri-3 PARTIAL; commonnoun_binder → pri-4 SOLVED; force_dynamics_valence → pri-7
SOLVED); scene_segment is dead-in-default. **Action: owner reviews → I integrate the wave → NOT_BF → ~1.** Board
Q124 asks whether to integrate the fleet-SOLVED ones now vs. hold.
**NEXT — the two learned-from-reading north-star levers (posted, assignable):** pri-1 the learned is-a/taxonomic
identity meaning channel (the dominant meaning lever, +0.488 CI-sep, no WordNet) · pri-2 scale the reading-learned
arc scorer (the shared extraction wall; retires the supervised-parser root).
**THE MAIN EVENT — the generative world-model program (in-flight, ~9 solvers):** the recurrent predictive-coding
loop / result-state model / chain-multi-step / forward-projection; the everyday-causation sign tail is a DOWNSTREAM
read over it (do NOT post separately — it activates when the world-model is perturbable).
**STANDING FIDELITY WORK (mine, fresh-budget, invasive — measure-first + board-no-regress):** the `causal_reasoner`
abduction upgrade (rung-2→3) · the directed-causal-store live wire (+0.139 WIQA-instrument) · full Rhea/formal-DB
ingest (causal-sign coverage 13%→65%). Off-path/lower: the reward-cluster vigor dial (+579, dormant).

## 5. DOC MAP (what is authoritative for what — read these, ignore the rest)
- **THIS doc** — process + roadmap. · **`tools/substrate_health.py`** — derived health.
- `notes/STATUS.md` — the per-session recovery anchor (top block only; the tail is archived).
- `notes/INTEGRATION_LEDGER.md` — per-solution gain/wiring/next-steps. · `notes/bf_status_registry.jsonl` — per-organ BF status (machine-checked).
- `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` — the by-target reverse-index + PROPAGATION STATUS.
- `notes/KNOWLEDGE_ASSET_REGISTER.md` — grown/curated knowledge DBs (LIVE/LATENT). · `notes/BRAIN_FOUNDATIONAL_AUDIT.md` — the §2b audit log.
- `tools/substrate_map.py` — the derived organ/stage/brief join. · `notes/problems/README.md` — the brief format + owner-DONE workflow.
- **SUPERSEDED / historical** (kept for lineage, NOT the live plan): `BUILD_PLAN_post_audit_2026-08-19.md` (its top block still carries the latest per-session handoff — read that; the roadmap here is authoritative), THE_PLAN.md, LONG_TERM_PLAN*.md, PLAN_NEXT_*.md, OVERNIGHT_PLAN*.md, CONSOLIDATION_PHASE_PLAN.md, INTEGRATION_PASS_PLAN.md, PLAN*.md.

*Maintenance: strategy keeps §4 current at each integration; the rest is derived. If this doc and `substrate_health.py`
ever disagree, the tool (derived from disk) wins — fix this doc.*
