# Stage-status reconciliation — where we are on the numbered plan (Stage 1-4 + M3/M4/M5)

**Written 2026-07-05 (Director). Read + reconcile only; no experiments.** Sources quoted, not invented:
`PLAN.md`, `PROGRESS.md`, and Director memories `project_stage1_regime_map_of_CG_META_axes`,
`project_M3_M4_milestones_glass_box_conversational_agentic`, `project_M3_architecture_needs_cortex_layer`,
`project_comprehensive_program_cert_architecture_C0C6`, `feedback_stage_progression_1234_dont_skip`.

---

## 0. THE LOAD-BEARING RECONCILIATION FINDING: there are TWO stage-numbering schemes, and they diverged

This is the single most important thing for the next session to not trip on.

- **Scheme A** — the USER-LOCKED stage-progression discipline (`feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md`, echoed in PROGRESS.md's "Prior phase 2026-06-30" section):
  > "Stage 1 base -> Stage 2 optimize -> Stage 3 higher functions -> Stage 4 LM equivalence. Don't skip."
  - Stage 1 = foundational primitives (chain-grade). Stage 2 = meta-primitives + **optimization** (incl. "better encoders"). Stage 3 = capability / higher functions. Stage 4 = LM equivalence (DEFERRED).
- **Scheme B** — the newer build-plan in `PLAN.md` ("Program shape revised under brain-best-in-class", 2026-07-02):
  ```
  Stage 1 (substrate algebra + physics + KB) CLOSED
  Stage 2 (substrate-owned concept encoder) LAUNCHED
  Stage 3 (cortex primitives operating on concept vectors)
  Stage 4 (language ingest at real corpus scale)
  Stage 5 (M3 glass-box conversational)
  ```

**These are NOT the same numbering.** In Scheme A the concept encoder is a Stage-2-**optimize** sub-item ("better encoders"). In Scheme B the encoder is promoted to **its own Stage 2**, and everything shifts down (LM-equivalence/M3 slide to Stage 4/5). Same "Stage N" label -> different content across docs. **Both docs are live; neither is wrong; they just count differently.** This reconciliation uses **Scheme B (PLAN.md) as the primary axis** (it is the newer authoritative build-plan and matches how the work is actually sequenced), and annotates the Scheme-A mapping. The USER-LOCKED *sequence rule* (don't skip to LM-equivalence) is honored under BOTH schemes.

---

## 1. Per-stage / per-milestone status (quote + evidence)

### Stage 1 — "substrate algebra + physics + KB" (PLAN.md) / "foundational primitives" (Scheme A)
**IS:** PLAN.md: *"Stage 1 CLOSED (2026-07-02): Physics-law META covers ... storage-strategy (SHARDED vs BUNDLED) + scale-free (N=8192->16384) + composition-depth (L=1->L=20) + topology-free ... Substrate-KB critical bugs fixed ... unified into one KB 970K entities + 1.6M triples."*
**STATUS: DONE / CLOSED for the main-effect laws; a SECONDARY finalization arc is ongoing.**
- Evidence: 5 CG_META axes stand; KB unified; OOM fix (22GB->4.5GB). PROGRESS.md live CERT floor **~633**.
- Ongoing finalization (USER 2026-07-03, `project_stage1_regime_map_of_CG_META_axes`): a **Regime Map** of the 5 CG_META axes — "not just 'we have 5 laws' but 'here is where each law holds, where it degenerates, and how they compose'." SECONDARY to the encoder.
- This session's Stage-1 work (2026-07-04) = an honest integrity correction + one genuine replacement:
  - The **mechanism-moderation cross-term family DEMOTED 4/4** as unpaired-sampling artifacts (mechanisms are argmax-readout-degenerate = bit-identical); the Probe-1 CG_META was demoted (CERT -1). Discipline filed: `feedback_paired_trials_mandatory_for_arm_comparison_discriminators_2026-07-04`.
  - **probe_18** (paired storage-advantage boundary that SCALES with N, cv=1%) landed **HARD_PASS -> MM_STANDARD** — the first genuine paired measurement replacing the retired mechanism-mirage. Main-effect laws (storage 0.93, scale-free, M-scaling, N x L additive) all stand.

### Stage 2 — "substrate-owned concept encoder" (PLAN.md) / part of "optimize" (Scheme A)  **[PRIMARY FOCUS]**
**IS:** PLAN.md: *"Stage 2 concept encoder arc LAUNCHED ... cortex primitives require concept-vector inputs from substrate-owned encoder; NOT random codebooks."* PROGRESS.md 2026-07-04: *"PRIMARY FOCUS (USER 2026-07-04): the concept encoder. It is the load-bearing component — the substrate's word/concept -> vector frontend that every downstream layer ... inherits quality from."* Goals (`project_encoder_goals_native_perception_085_sparse_algebra`): (1) OWN it, (2) ~0.85 semantic cosine, (3) ~2% sparse, (4) algebra survives.
**STATUS: essentially DONE (perception layer built); final integration into the live store IN FLIGHT.**
- Converged to **GSBC_EXPAND2X** (graded global-top-k + 2x-FlyHash-expansion single code, 8192-dim, **~2.34% active**), after the whole 2026-07-04 session: distillation first FAILED at full scale (v2 BLOCK 0.31 < CHARPOS orthographic baseline 0.66), then an 8x-drill converged the fix to the **CODE FORMAT** (graded global-top-k, not per-block-argmax), not any training trick.
- Both seeds **HARD_PASS verified off-disk + Skunkworks VET'd MM_STANDARD**: ret_agree10 **0.60/0.68** (clears the 0.35 scoreboard), hi80_cos **0.83/0.845** (goal #2 ~met), keyed@J5 = **1.000** through J=32 (goal #4), native calibration. **All 4 USER goals met.**
- Honest tier: MM_STANDARD, **not CHAIN_GRADE** — composes existing primitives; **teacher-dependent on BGE-large** (not yet self-grounded); "mediocre-but-works" in absolute terms (field-standard GSBC+FlyHash). Not the prize; the frontend to the prize.
- Remaining before Stage-2 fully closes: FULL-ckpt local persistence + **step-0 INTEGRATION-VERIFY** through the real substrate store/retrieve/compose path (a3e5f89a in flight).

### Stage 3 — "cortex primitives operating on concept vectors" (PLAN.md) / "capability / higher functions" (Scheme A)  **[the M3 cortex layer]**
**IS:** PLAN.md: *"Stage 3 (cortex primitives operating on concept vectors)."* Architecture (`project_M3_architecture_needs_cortex_layer`): the cortex/planner is a **SEPARATE module above** the substrate — *"hierarchical planning is not substrate-native (5 cells across 4 mechanism classes all HARD_FAIL)."*
**STATUS: IN-PROGRESS, partially built (~40% of "memory+basic-reasoning" per the 07-04 build-status); deferred behind the encoder, now unblocked.**
- **M3 Cortex-2 atom-consultation is 4 primitives deep** (advisory -> SHADOW -> dose-response -> multi-atom); PROGRESS.md: *"LIVE-mode ring rollout DEFERRED behind the encoder."*
- The recent cortex experiments the USER asked about land HERE (Stage 3):
  - **cortex2 provenance / multihop / hard-unanswerables** + **algebra-on-real-atoms** (a97751df, verdict GOOD_SHALLOW_MEDIOCRE_HUBS): memory algebra works for typical cases (deg1=1.0, uniform 0.74-0.92) but **high-degree hubs collapse** (deg5+ exact 0.21, need top-k). "Competent memory index, not reasoning-superiority."
  - The **standalone-reasoning-MOAT** comparison (cortex vs a fair multi-hop agentic baseline) reached **PARITY** (completeness 1.0 vs 0.96, faithfulness 0.85 vs 0.87, loses recall 0.96 vs 1.0) — the moat thesis was DISPROVEN, and that whole comparison arm was **ABORTED per the USER reframe** (see §2).
- Scheme-A "Stage 3 capability primitives" already banked (~60%): multi-hop depth-15 CG, compositional-gen CG, cross-modal CG, CF-regret vmPFC CG, TASK_VECTOR CG.

### Stage 4 — "language ingest at real corpus scale" (PLAN.md) / "LM equivalence" (Scheme A)
**IS:** PLAN.md: *"Stage 4 (language ingest at real corpus scale)."* Scheme A: *"Stage 4 = LM equivalence ... DEFER until Stages 1-3 mature."*
**STATUS: NOT STARTED — deliberately deferred (USER-locked).**
- General-knowledge ingest = **USER-LOCKED "not yet"** (backup 07-04 §NEXT-STEPS; `project_encoder_goals`). Foundational anchor: **"SUBSTRATE KNOWS NOTHING"**. Do-not-run Stage-4 benchmarks (text8/BPC/bigram-gap) per the stage-progression lock.
- First toe-dip = **dogfood ingest of our OWN notes** (step 2 of the post-encoder plan), gated behind encoder integration — not the broad Stage-4 corpus ingest.

### M3 — glass-box conversational AI (= Stage 5 in Scheme B)
**IS:** `project_M3_M4_milestones`: *"substrate handles 10-turn conversation without Claude in loop (12-18 months)"* — SUBSTRATE-NATIVE language, no external LLM. 6 capability blocks; Pass = 10/10 demo properties.
**STATUS: NOT STARTED as a milestone; foundational blocks partially built.** Block status: (1) compositional understanding — partial (Stage 3); (2) language input parser — not built; (3) language output generator — not built; (4) multi-turn context — WM primitive exists, not wired to dialogue; (5) self-knowledge — refuse-gate + META v4 exist; (6) self-improvement loop — encoder-done is one piece. **0 of 10 demo properties formally demonstrated** (proto-versions of a few). USER target = "aim for M3."

### M4 — hybrid agentic experiment loop (substrate as research director)
**IS:** *"substrate proposes STRUCTURED experiment spec, human/Claude templates code, substrate executes (18-30 months, stretch)."*
**STATUS: NOT STARTED.** (Note: our human/agent Director->exp_dev->orchestrator loop is the *human-analog* of M4; the substrate-driven version is untouched.)

### M5 — substrate writes own code
**IS:** *"5+ years if achievable at all ... Don't bet on it."*
**STATUS: NOT STARTED — parking-lot, aspirational.**

---

## 2. Where the encoder rescue + cortex experiments fit; did we drift?

**The encoder was NOT an original numbered stage — it emerged/was-promoted mid-program.** In the USER-LOCKED Scheme A it was a Stage-2-**optimize** sub-item ("better encoders"). It was **legitimately elevated to THE primary focus + its own Stage 2 (Scheme B)** on 2026-07-04 because it is the load-bearing frontend every downstream layer inherits quality from (USER-confirmed). **This is disciplined re-sequencing, not aimless drift** — the enabling work was correctly sequenced first (matches `capability_dev_is_goal` + `discriminator_must_survive_scale`).

**The cortex experiments (cortex2 provenance/multihop/hard-unanswerables, algebra-on-real-atoms) are Stage 3 / M3-cortex probes** — they belong exactly where the plan puts them.

**Did we drift? Three honest answers:**
1. **Sequence: NO drift.** Stage 4 LM-equivalence is still correctly deferred; general-knowledge ingest held per USER-lock; no jump to Stage-4 benchmarks. The 1->2->3->4 rule was honored.
2. **One genuine mini-drift, USER-caught same-session.** Around 03:00Z the work drifted into a **vs-LLM "does the glass-box cortex out-reason RAG / is there a differentiator / pivot-or-kill" competitive frame**. The USER corrected it at ~03:40Z (verbatim): *"do not compare us against an LLM. I want to work towards a fully functional substrate with glass-box-LLM capabilities. do not spend time comparing us."* The comparison arm (LLM-reader a643c8f9) was **ABORTED**. So yes — a brief drift into benchmarking-vs-LLM, caught and reversed by the USER within the session.
3. **Documentation drift (real; flagged in §0).** PLAN.md's Stage numbering diverged from the USER-LOCKED stage-progression memory's numbering. Latent confusion risk; this memo makes it explicit.

---

## 3. How the numbered stages map onto the USER REFRAME + the honest next step

**USER reframe (backup 07-04 handoff):** build a **fully-functional standalone glass-box substrate WITH LLM-like capabilities** (perception, memory, deep reasoning, generation, continual learning) — every step inspectable, every memory editable, learns without forgetting. Brain = existence-proof/target, **NOT a benchmark**. Do NOT compare vs LLMs.

**The reframe's BUILD ROADMAP maps cleanly onto the numbered stages** (the stages are still a coherent skeleton; the reframe removes the vs-LLM framing and re-centers on constructive building):

| Reframe roadmap step | Maps to |
|---|---|
| perception **[DONE]** | Stage 2 encoder (GSBC_EXPAND2X) |
| deepen reasoning over own memory | **Stage 3** cortex primitives on concept vectors (the current frontier) |
| continual learning (no forgetting) | substrate-native strength; BCT compat mechanism already exists (Stage 2/3) |
| generation/composition (interpretable) | M3 capability block #3 (substrate-native language output) |
| ingest real knowledge (own first, then wider) | Stage 4 (deferred; dogfood-own-notes is the first gated step) |
| 10-turn glass-box conversation | M3 (= Stage 5) — the integration target |

**HONEST NEXT STEP per the plan** (`notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md` + backup handoff):
Close out Stage 2 into Stage 3 —
1. **step 0 INTEGRATION-VERIFY** the (done) encoder through the REAL substrate store/retrieve/compose path (a3e5f89a in flight) -> **step 1 BCT-safe re-encode** existing content -> **step 2 dogfood ingest** our own notes.
2. Read the reframed-constructive **a0c4d73d** build-path result, present the intuitive BUILD ROADMAP, and **fire the FIRST constructive build experiment** (fill idle compute with BUILDING, not comparing).
3. Resume **Stage 3 / M3 Cortex-2** reasoning-deepening (advisory -> SHADOW -> dose-response -> multi-atom LIVE-mode ring).
NOT: any vs-LLM comparison (aborted), NOT Stage-4 general-knowledge ingest (USER-locked "not yet").

---

## Intuitive summary
- **Where we are:** Stage 1 (substrate physics/algebra/KB) is essentially **done**; Stage 2 (the concept encoder = perception) is **essentially done** this session (GSBC_EXPAND2X, all 4 goals met, mediocre-but-works, integration into the live store still in flight); Stage 3 (cortex reasoning over concept vectors) is the **current, partially-built frontier**; Stage 4 (broad language/knowledge ingest) and M3/M4/M5 are **deliberately not started yet**.
- **Why it matters:** the encoder was the bottleneck the whole downstream stack inherits quality from — finishing it unblocks the actual prize (Stage 3 cortex reasoning). We are exactly where a disciplined build should be, one stage from the interesting part.
- **Did we drift:** the *sequence* was not skipped; there was one brief drift into "compare-vs-LLM" that the USER caught and reversed the same session; and there's a documentation numbering mismatch (two Stage-N schemes) that this memo now makes explicit so it stops causing confusion.
- **Honest next step:** wire the done encoder into the live substrate (integration-verify -> re-encode -> dogfood-ingest our own notes) and move into Stage 3 cortex reasoning-deepening — i.e., "deepen reasoning over own memory," building not benchmarking.
