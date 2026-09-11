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
   cross-solution map's PROPAGATION STATUS → **clear the problem's `priority` frontmatter field + set `status: INTEGRATED`
   (a finished problem is not assignable — leaving a priority clutters the queue; owner-flagged 2026-09-11)** → commit
   path-limited, NOTHING pushed.
3. **Keep the fleet fed:** if `assignable OPEN == 0`, post the next ROADMAP items (§4) as briefs (8 guard sections
   + the standing blockquotes; cert `verification/test_problem_briefs_and_flags.py`). De-dup against existing
   problems first.
4. **Propagate:** when a component is improved, walk `CROSS_SOLUTION_IMPROVEMENT_MAP.md` PART 2 for its consumers and
   apply/queue each; record in the PROPAGATION STATUS block. **BF component updates:** every incoming SOLVED carries
   AUDIT UPDATEs — add/refresh its row in `BF_COMPONENT_UPDATE_LEDGER.md`, classify NARROW (lands with the solution) vs
   GENERAL (a correction to a shared LIVE organ); at integration apply the solution's BF updates AND walk that ledger's
   GENERAL rows on the same organ. This is how a BF fix "focused on its own problem" that actually corrects a shared
   organ does not get lost.
5. **Evaluate on a cadence:** the TRIGGER is the INTEGRATION WAVE (a live change landed), NOT every cycle —
   between waves nothing new is live, so the fast `--self-test` (capped, ~2min) suffices to confirm no-regress
   (it re-confirmed AGG 0.6294 across this session's additive/latent integrations). The FULL board
   (`exp_situation_model_qa_modern_v1.py --run`, the full-population trend point) takes ~40min and EXCEEDS a single
   10-min tool window, so run it **DETACHED** (`run_in_background`, NO `timeout` wrapper) and record the aggregate
   when it lands (CONT-95 dogfood finding: a `timeout 590` wrapper kills it before the aggregate). A board-invisible
   proven win gets its own instrument-arm — unless, like `causal_sign`, its signal needs a scale the board can't run
   in smoke (then its dedicated full-scale witness IS the instrument; do not add a misleading smoke-board arm).
   **⚠️ BOARD-PROXY CAVEAT (strategy 2026-09-11): some board arms score a SIMPLIFIED STAND-IN, not the full live
   `read()` — e.g. `who_did_what_patient` calls `structural_patient_pick` DIRECTLY (no marginals), bypassing the
   live `_router_roles`. So a FLAT board delta can mean the wire never ran on the scored path, NOT that it failed.
   Before trusting (or dismissing) a board number for a live wire, INSTRUMENT it — count invocations on the scored
   path. A board arm that measures a proxy should be pointed at the live `read()` output (a fidelity fix in its own right).**
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
**NEXT — ⚠️ PIVOTED 2026-09-10 (the CAPABILITY WALL, owner-flagged). pri-1 (the learned is-a channel) is REFUTED (owner-DONE, 36/36):** grown-SEQ already banks the distributional identity signal (Harris); 6 BF mechanisms null; **first-order co-occurrence PROVABLY conflates syn/antonym/cohyp (Scheible-Schulte)** → ALL type-level text-distributional meaning channels are EXHAUSTED (durable negative; §2b). **The two REAL meaning levers (both already in motion — the fleet converged on them):** (a) **GROUNDING BEYOND TEXT** — a real perceptual/VISUAL cross-modal spoke (DINOv2 referent hub; `DESIGN_visual_referent_hub`, in progress) supplies the distinctive-feature DIFFERENTIA that separates syn/antonym/cohyp, which text provably cannot; (b) **IN-CONTEXT / TOKEN-LEVEL reading** — meaning read as a context-gated PREDICTION (validated: WiC type 0.485→ctx 0.582→landed 0.66-0.68), NOT a type lookup (`wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector`; the WiC cells). **pri-2** (scale the reading-learned arc scorer) still stands — the same text-only ceiling applies (parser residual = perceptual grounding), so it too pivots toward the grounded/in-context frame. The cross-wall pattern (pri-1/pri-3/pos_tagger/pri-5): the substrate has exhausted TEXT-DISTRIBUTIONAL + TYPE-LEVEL; the frontier is grounding-coverage + the generative in-context frame = THE MAIN EVENT below.
**THE MAIN EVENT — the generative world-model program:** its mechanism problems (result-state model, recurrent
predictive-coding loop / N400, forward-projection, chain-multi-step) are ALL SOLVED + INTEGRATED as located-negatives
that BUILT the mechanisms (verified CONT-116: none are open/in-flight). The program is therefore NOT advanced by a new
world-model problem — **it is gated on EXTRACTION quality (the shared wall), and advances THROUGH the posted extraction
front: pri-2/pri-3 (parser) + pri-4 (coref)** ([[reasoning-machinery-shown-not-end-to-end-build-the-generative-world-model]]).
The everyday-causation sign tail is a DOWNSTREAM read over it (do NOT post separately — it activates when the world-model
is perturbable, which the extraction front delivers). ⇒ DO NOT post a redundant world-model problem; feed the extraction front.
**STANDING FIDELITY WORK (mine):** ✅ `causal_reasoner` rung-3 abduction primitive LANDED (CONT-97, `fd0bca071`,
pure-add). **STRATEGIC CEILING FOUND (CONT-98): the causal machinery is BOARD-INVISIBLE** — no smoke-viable modern
causal gold (WIQA needs full-scale; the smoke self-test underpowers it, per the reverted board_causal_sign arm), so
the LIVE FLIP of any further causal fidelity (directed-store wire +0.139 WIQA-instrument · Rhea ingest 13%→65% ·
abduction-FROM-evidence) CANNOT be measured on the board -> a mine-side default-off landing would be latent +
unmeasurable (violates measure-first). ⇒ the leverage is NOT more mine-side board-invisible causal builds; it is
either (a) a SMOKE-VIABLE causal board INSTRUMENT (the prerequisite that makes all of it measurable), or (b) posting
the causal-fidelity pieces as FLEET problems with their own full-scale witnesses. Both are candidate roadmap items,
not mine-side grinds. Off-path/lower: the reward-cluster vigor dial (+579, dormant, off the reading board).
**🧠🧩 AGGREGATE-BF CONSOLIDATION PROGRAM (owner 2026-09-10, NEW track) — `notes/BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md`.**
The 83 organs map to ~25 brain structures — several structures are built as 3–8 organs (our fragmentation), the aggregate-BF gap per-organ certification never caught. Ranked merges (each: code-verify the two organs compute ONE operation → merge to one organ with cue/task ARMS → prove byte-identical/no-regress): (1) coreference/entity → one cue-based `entity_resolver` (6→1+arms; Lewis-Vasishth uni-modular retrieval; drop NOT_BF commonnoun_binder); (2) fused `meaning_representation` (conceptual+distributional+Osgood axes = the ALREADY-ACTIVE pri-2/pri-5 fusion — formalize it; KEEP the distinct task-reads); (3) `temporal_model` (ordering trio → one order-core + tense/aspect arms); (4) `thematic_roles` (graded_role_assigner ≡ thematic_role_labeler, identical Competition-Model eq — cleanest); (5) `force_dynamics` (lexicon + causation_typing). **KEEP (counter-caution, pri-3): causal Pearl-ladder rungs + predictive-coding stages + situation-model per-dimension registers are FAITHFUL sub-modularity — do NOT merge.** INVERSE (split): reading_grounding_loop mega-organ, coref's name-individuation, context_grounded_valence, predictive_world_model, safe_kb_gate. GATE: code-verify the 4 uncertain assignments (§d) before any merge. Approach = owner's call (fleet problems vs mine-side, one merge at a time).

## 5. DOC MAP (what is authoritative for what — read these, ignore the rest)
- **THIS doc** — process + roadmap. · **`tools/substrate_health.py`** — derived health.
- `notes/STATUS.md` — the per-session recovery anchor (top block only; the tail is archived).
- `notes/INTEGRATION_LEDGER.md` — per-solution gain/wiring/next-steps. · `notes/bf_status_registry.jsonl` — per-organ BF status (machine-checked).
- `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` — the by-target reverse-index + PROPAGATION STATUS.
- `notes/KNOWLEDGE_ASSET_REGISTER.md` — grown/curated knowledge DBs (LIVE/LATENT). · `notes/BRAIN_FOUNDATIONAL_AUDIT.md` — the §2b audit log.
- `notes/BF_COMPONENT_UPDATE_LEDGER.md` — every solution's BF component updates, classified NARROW-vs-GENERAL + status (APPLIED / PENDING-DONE / LOCATED-NEGATIVE). The organ-indexed queue of pending BF corrections; walk its GENERAL rows at each integration.
- `notes/BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md` — the AGGREGATE brain-foundationality audit (owner 2026-09-10): 83 organs → ~25 brain structures; per-cluster KEEP (faithful sub-modularity) vs CONSOLIDATE (our fragmentation) vs INVERSE (under-fragmentation), research-cited. The organ-BOUNDARY companion to the per-organ registry — consult before creating a new organ (does an existing structure already own this?) and when planning consolidation.
- `tools/substrate_map.py` — the derived organ/stage/brief join. · `notes/problems/README.md` — the brief format + owner-DONE workflow.
- **SUPERSEDED / historical** (kept for lineage, NOT the live plan): `BUILD_PLAN_post_audit_2026-08-19.md` (its top block still carries the latest per-session handoff — read that; the roadmap here is authoritative), THE_PLAN.md, LONG_TERM_PLAN*.md, PLAN_NEXT_*.md, OVERNIGHT_PLAN*.md, CONSOLIDATION_PHASE_PLAN.md, INTEGRATION_PASS_PLAN.md, PLAN*.md.

*Maintenance: strategy keeps §4 current at each integration; the rest is derived. If this doc and `substrate_health.py`
ever disagree, the tool (derived from disk) wins — fix this doc.*
