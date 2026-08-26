# BRAIN-FOUNDATIONAL AUDIT — the whole substrate against the brain it reconstructs

**updated: 2026-08-26** · living document, edit in place · **THE single reconciled map of substrate-vs-brain.**
Reconciles the three prior audits onto one list: `ORGAN_MAP.md` (38 organs, per-organ brain-math, 08-22),
`component_brain_fidelity_ledger.md` (14 components, 07-30), `LONG_TERM_PLAN.md` §4 (phases, 08-16). Where
they disagree, this file is the current view and names what went stale.

**Provenance / honesty scope:** the per-organ fidelity verdicts below are carried from `ORGAN_MAP.md` (read in
full 2026-08-26), not independently re-derived this pass; the whole-brain coverage is from a full read of all
155 `hdlab/*.py` docstrings. Treat verdicts as "as-audited," re-verify before acting on any single one. Numbers
are as-quoted from their source cells and do not cross scorers/populations.

---

## 1. THE HEADLINE (plain language)

We mapped 38 "organs" the brain uses to read, mean, remember and reason, plus the systems around them.

- **Only 5 of 38 organs compute the brain's actual equation.** For **12** neuroscience has written down the
  equation, so "build the brain's version" is even a well-posed instruction; for **14** the core operation is a
  mystery *even in neuroscience*, so we are inventing (honestly labelled) — including **our single most central
  operation, binding**. **7 organs don't exist in code at all.**
- **~54% of the code is unreachable** from any live entry point — built-but-unwired islands.
- **Two defects are bigger than any single organ:** (1) **we ask every question of the wrong memory** — the fast
  episodic "sketchpad," never the consolidated long-term store that was written but never read back; (2) a
  **`sign()` quantiser at the end of almost every step** throws away signal strength and keeps only direction,
  which quietly turns the whole system into an averaging machine.
- **The systems we DO build well are lopsided toward reading:** coreference, goals/reward, valence, and
  metacognition are richly built; **Theory of Mind is absent, dedicated meaning-selection (semantic control) is
  thin, and the speaking side is essentially one file.** This substrate is a reader, not a speaker.
- **Corrected this pass:** the 07-30 ledger called coreference and discourse "ABSENT." That is **stale** — both
  are now substantially built. And the meaning step is **no longer "empty" (see §7):** on a fair test it beats
  frequency; it is unwired, not absent.

---

## 2. HOW THIS DOC IS USED (it is a living, shared reference)

- **Every solver brief references this file.** A solver reads the entry for the system it is touching before it
  starts, so it inherits the brain frame and the known deviation instead of re-deriving it.
- **Solvers report deviations/updates they find.** If, during the work, a solver discovers the fidelity verdict
  here is wrong, stale, or incomplete — or finds a new deviation — **that goes in the submission** (a short
  "AUDIT UPDATE" note), and **the strategy session incorporates it here at integration.** The audit improves as
  the work proceeds; it is not frozen.
- **Marking convention:** each entry carries the brain structure, whether the brain's equation is **PINNED**
  (neuroscience fixes it) or **UNPINNED/CONTESTED** (we are inventing — an OUR-INVENTION-UNDER-TEST, not a
  replication), our organ (or ABSENT), a fidelity verdict, and the specific gap/deviation.

---

## 2b. AUDIT UPDATES (from integrated solver work + strategy fidelity extensions — newest first)

- **2026-08-26 — CONTENT-ADDRESSABLE RETRIEVAL: bar MET, and it RE-FRAMES the fix — the missing organ is cue-based
  RETRIEVAL (additive Lewis-Vasishth), NOT "separate the store"** (from `content_addressable_retrieval_over_a_separated_store`,
  integrated SOLVED/EXCELLENT, owner-DONE; witness `verify_content_addressable_register_retrieval.py` PASS, re-verified
  first-hand). Content-addressable retrieval over the SEPARATED register (match the partial cue against the stored slots,
  read the clean slot) beats the LIVE exact-key routes CI-separated under a partial cue: **SEP_CA 0.991 [0.988,0.993] vs
  the exact-key HASH route 0.287 and the naive flat register 0.068**; twins at chance (~0.05); at a FULL cue everything
  ties (the Nakazawa CA3 partial-cue dissociation, predicted not swept); generalises across D×load×rho. **BUT the drills
  RE-FRAME the fix, with multiple honest self-corrections:** (1) an **EQUAL-TOTAL-STORAGE flat store (`FLAT_MATCHED`)
  recovers to 1.000** — so separation is NOT uniquely necessary; the flat register's partial-cue failure is
  CAPACITY/crosstalk, curable by separation OR dimension. **The genuinely-missing, brain-foundational mechanism is
  content-addressable RETRIEVAL (the cue-MATCH), which the substrate lacks entirely; separation (DG / multibank) is its
  storage-EFFICIENT substrate, not the lever.** (2) The **CA3 iterative settle is NOT load-bearing** — 1-step argmax
  (SEP_ARGMAX 0.990) ties SEP_CA in every regime (the 1-step match is already the MAP estimate). (3) **DG pattern
  separation did NOT help** in any tested regime (worse at rho=0, neutral at rho=0.5) — a rigorous negative on the DG→CA3
  pairing the binding SOLVED flagged. (4) **LOAD-BEARING NEGATIVE reproduced on the register:** CA3 cleanup on the flat
  readback TIES argmax exactly (0.607=0.607) — you cannot clean your way out of superposition; the fix is architecture.
  **NEW DEVIATION (the deeper E2/E3 fidelity gap):** our register retrieves by a MULTIPLICATIVE composite key (`bind` the
  cue features, match one vector); FHRR bind orthogonalises the whole composite on any one wrong/missing feature, so a
  partial/competitor-dominated cue COLLAPSES. **The brain's PINNED cue-based retrieval (Lewis & Vasishth 2005; ACT-R;
  already pinned for E3 coref) is ADDITIVE:** activation = Σ_f w_f·sim(cue_f, item_f), retrieve the max — degrading
  GRACEFULLY (additive 0.33–0.70 vs composite 0.03–0.04 under a dropped/interfering feature). ⚠️ **Honestly DEFLATED by
  the owner-directed real-grounded drill:** with the substrate's OWN grounded feature vectors (real graded similarity) the
  additive-vs-composite gap is mostly a TIE (clean/near/dropped tie; additive only edges under a truly-dissimilar
  corruption, which real similarity makes rare) — so additive is the RIGHT DEFAULT (never worse, natively serves partial
  cues, no unphysical collapse) but the everyday lift is SMALL. **The REAL open problem is similarity-INTERFERENCE
  resolution (the fan effect) — and it should NOT be "solved": the fan effect / false memories are real human behaviour, a
  faithful model must EXHIBIT it. Open it as its own problem, not a switch here.** **Effect on the audit:** E2 gains a
  RETRIEVAL deviation (missing content-addressable read path — both registers' `decode()` require the exact key); the
  E1/E2/E3 re-location is SHARPENED (the lever is content-addressable RETRIEVAL, separation is the substrate); the owned
  fix is HALF-owned (`ca3_completer` needs an FHRR [Re;Im] adapter + its settle is un-earned; `dg_pattern_separation`
  didn't help); the retrieval RULE should be ADDITIVE (Lewis-Vasishth), not a multiplicative composite. 🔌 hdlab landing
  EARNED (a default-off additive `decode_cue` over the separated multibank register + an FHRR adapter for `ca3_completer`)
  — queued as a focused default-off landing with its own witness; SYNTHETIC construction proof, measure on the LIVE
  reading/QA task before any capability claim.

- **2026-08-26 — THE TWO-SIMILARITY-SYSTEMS BUILD: the FEATURE-SIMILARITY system is BUILT + PROVEN; the
  SEMANTIC-CONTROL SWITCH is REFUTED (fixed fusion wins)** (from `the_substrate_has_one_meaning_system_where_the_brain_has_two`,
  integrated PARTIAL/EXCELLENT, owner-DONE; witness `test_two_meaning_systems_feature_similarity_and_gate.py` PASS,
  re-verified first-hand). The re-point's #1 lever, delivered. **BAR #1 MET — the missing feature-similarity system,
  built brain-faithfully:** the ATL's "privilege DISTINCTIVE features" = DECORRELATION (WHITEN away the dominant shared
  axis — concreteness, the top PC is 26.7% of the grounding variance — which is exactly the grounding carrier's own
  documented "raw cosine can't separate synonym from sibling; apple/orange 0.952" ceiling, stated as a bug). The
  distinctive-feature-weighted grounding rep beats RAW grounded cosine **CI-separated on two HELD-OUT similarity golds**
  (SimLex 0.291 vs 0.245, +0.046 CI_lo 0.019; SimVerb 0.287 vs 0.264, +0.023 CI_lo 0.008 — reproduced first-hand) and
  it LOWERS relatedness (the exact brain signature — specialises toward alike-in-kind); it beats the ASSOCIATIVE
  co-occurrence rep on similarity by +0.197/+0.233; info-free twin (shuffled grounding rows) loses (~0.014), floors
  cleared, whitening fit gold-blind + vocab-disjoint, hyperparams fit only on a dev split. **A REPRESENTATION-level op
  (suppress shared covariance), different-in-kind from the refuted sign/graded/sparse read-out family.** **FINER DRILL
  (a fidelity BOUNDARY, honestly found):** LINEAR whitening is SUFFICIENT — a per-concept NONLINEAR distinctiveness (the
  sharper McRae/semantic-dementia account) does NOT add on a 12-dim CONTINUOUS grounding space (Δ 0.000) and the
  zebra→horse signature does NOT reproduce, because that space lacks the rich binary "few-concepts-have-this-feature"
  structure the account assumes → the next distinctiveness gain is a RICHER FEATURE SUPPLY, not a fancier transform.
  **BAR #2 REFUTED (robustly; a brief-named valid outcome) — the two systems are better FUSED than SWITCHED:** a
  task-gate does not beat the best FIXED blend even with a STRONG associative system (gate−fixed −0.026 CI[−0.048,−0.006])
  or on a conflict population, and it ties its random-switch control on a mixed pool. The brain-grounded reason (NOT an
  exhausted-engineering wall): the IFG gate resolves COMPETITION using CONTEXT, and a decontextualised word pair gives
  it nothing to gate on — so for graded similarity/relatedness RATING the faithful op is FIXED multiplicative
  INTEGRATION (recovers BOTH axes, mean 0.378 > feature-pure 0.309 > associative-pure 0.338); the gate's proving ground
  is a genuine-selection task (homonym WSD), owned by `reader_meaning_channel` (which HARD_FAILED there) and deliberately
  not re-built here. **Effect on the audit:** (a) Tier-2 ATL/sensorimotor RIGHT-OP-WRONG-METRIC now has a fix + a number
  (whitening); (b) the "semantic control THIN" gap is RE-POINTED — the near-term win is the FIXED two-system fusion, the
  task-switch gate is a later SELECTION-task deliverable, NOT for graded rating; (c) the two-similarity-systems row (from
  the sign_quantiser drill) is CONFIRMED + BUILT. Converges with the session theme: the remaining wall is meaning SUPPLY
  (richer features), not the transform. 🔌 hdlab landing **LANDED 2026-08-26**: the distinctive-feature WHITENING read-out is in
  `hdlab/grounded_similarity.py` (`distinctive_grounded_vector` / `distinctive_grounded_similarity`, a NEW uncapped
  meaning read-out; the capped link score is byte-identical), witness `test_distinctive_feature_grounding_organ.py`
  PASS (distinctive rho 0.292 > raw 0.245 on SimLex through the organ's own transform; whitened covariance is exactly
  identity), registered `distinctive_feature_grounding_v1` (WIRE_CANDIDATE, ISLAND). Use it as the feature-similarity
  axis + a FIXED two-system fusion, NOT a switch; measure on the live read-out before any capability claim.

- **2026-08-26 — F5 (N400 COHERENCE MONITOR): the MISSING organ now has a validated build spec + a decisive
  existence proof; and DEVIATION #6 SPLITS** (from `the_substrate_does_not_learn_or_update_by_prediction_error`,
  integrated EXCELLENT, owner-DONE; witness `verify_prediction_error_event_segmentation.py` PASS, re-verified
  first-hand). The brain's UPDATE signal was MISSING, not impossible. A **GRADED forward CONTENT prediction error
  against the RUNNING (reset-per-event) situation-model state** — `e = 1 − cos(content, running_event_gist)`,
  boundary-posted via the existing EST `relative_threshold_gate` (Reynolds/Zacks/Braver 2007, already in
  `predictive_coding.py`) — segments a discourse near-perfectly and fills the situation model: downstream within-event
  cross-role recovery **0.988 [0.980,0.995]** vs FIXED 0.523 / RANDOM 0.438 / FORM_NOVELTY 0.737 (strongest floor) /
  PERMUTED_SURPRISE 0.487, boundary F1 0.987, WIN in all 9 D×coherence cells, at a MATCHED boundary rate (so the win
  is boundary POSITION, not rate). **Key dissociation — the p1 coupling made concrete:** the naive `||Δregister||` in
  the near-orthogonal BINDING space TIES no-segmentation (0.202 vs 0.198); the residual must be graded AND computed in
  a CONTENT-similar space, not the sign-quantised/near-orthogonal one. Escapes the two prior negatives' trap:
  FORM_NOVELTY (surprise vs a whole-stream anchor that NEVER resets) caps at 0.737 — the RUNNING RESET is what makes it
  the N400. Foundationality drill: the win does not hinge on the predictor (running-mean / last-item / online
  Rao-Ballard learned transition all win identically). **Effect on the audit:** (1) **F5 (§4 Tier 3) MISSING → spec'd +
  existence-proven.** (2) **E2's "missing the PE segmentation that decides WHEN to write" confirmed + actionable** —
  advance `situation_model_accumulate`'s event slot on an F5 boundary (0.20→0.99 in-instrument). (3) **DEVIATION #6
  SPLITS into two rows with OPPOSITE verdicts:** the UPDATE half (N400/SEM segmentation) is missing-buildable-and-WINS
  → BUILD; the LEARNING half ("cloze not forward-PC") is a RIGOROUS NEGATIVE (forward-PC does NOT beat cloze on
  paradigmatic meaning) → DEPRIORITISE. (4) **Tier 5 `predictive_coding.py` RIGHT-OP-WRONG-METRIC confirmed** + a
  companion positive: the residual is graded in salience (ρ 0.77) and the EST relative-threshold machinery there is
  correct but UNWIRED. ⚠️ Synthetic construction proof — the N400 organ (graded content-PE + EST boundary + wire to
  `situation_model_accumulate`) is **LANDED 2026-08-26 as `hdlab/n400_coherence_monitor.py`** — off-path
  WIRE_CANDIDATE, witness `test_n400_coherence_monitor_organ.py` PASS (running-reset F1 1.0 > never-reset anchor 0.44;
  a near-orthogonal binding-like code is unsegmentable F1 0.0 — the content-space finding; coherent stream quiet),
  reuses the pinned `predictive_coding.running_avg_update`, registered `n400_coherence_monitor_v1`. **Next:** wire a
  posted boundary → advance `situation_model_accumulate`'s event slot, and MEASURE on the live reader before any
  capability claim (the win is still a synthetic construction proof).

- **2026-08-26 — DEVIATION #2 (`sign()`) BINDING REGIME: CONFIRMED-but-LATENT, coupled to B4** (from
  `the_sign_quantiser_makes_the_substrate_an_averaging_machine`, **RE-INTEGRATED PROPERLY on the owner's per-problem
  owner-DONE**; the binding drill + live verification re-verified scaffold-free first-hand, both reproduce). This is the
  ADDITIVE binding half that makes the FINAL verdict **PARTIAL** — the read-out refutation (next entry) STANDS. In the
  binding/superposition regime sign() IS a real averaging machine for CORRELATED bound codes: recovering B role-filler
  pairs from a bundle (MAP-VSA, 512-filler cleanup, d=256), GRADED beats SIGN by a CI-separated, GROWING margin (B6
  0.98/0.73, B8 0.88/0.58, B12 0.67/0.36 — reproduced), raising the capacity cliff **B\*=8 → 12** for correlated codes
  (~50% capacity loss at d=256; correlation-specific — RANDOM gap +0.08 vs CORRELATED +0.146). **BUT LIVE VERIFICATION
  shows it does NOT bite today:** the real StructuralEncoder binds at mean B=2.85 (median 3; 14% B>4) with ATOMIC
  near-orthogonal fillers (|cos| 0.063) → recovery gap +0.013 (~0 for B≤4). It becomes real ONLY when binding is made
  brain-faithful (graded-semantic fillers, |cos| 0.248) → gap +0.044 overall, **+0.087 on the 14% B>4 tail** (verdict
  `SIGN_SAFE_TODAY_BUT_BITES_IF_BINDING_MADE_FAITHFUL`, reproduced first-hand). **So deviation #2 at binding is a
  GUARDRAIL COUPLED to the graded-code (B4) fix — NOT a current bug, NOT a standalone win:** when B4 makes fillers
  graded-semantic, the `sign()`-on-a-bundle sites (`situation_focus.py`, `role_slot_summarizer.py`, `event_bundle.py`,
  CA3 `cleanup_family.py`) must go graded in the SAME change, gated on `exp_live_binding_load_signgap_v1` /
  `exp_superposition_capacity_binding_v1`. Connects to the binding/memory line (p3 content-addressable retrieval, p5
  one-store). **NO hdlab landing now** (latent; the solver's explicit guidance: do NOT land it standalone). §8 lever #1
  (`sign→graded`) is demoted only AS A READ-OUT lever; it is ALIVE as this binding-site guardrail.

- **2026-08-26 — DEVIATION #2 (`sign()` QUANTISER) REFUTED AS THE AVERAGING-MACHINE LEVER *ON THE READ-OUT*; the
  read-out wall is meaning SUPPLY, and there are TWO SIMILARITY SYSTEMS** (from
  `the_sign_quantiser_makes_the_substrate_an_averaging_machine` — the READ-OUT half of the PARTIAL verdict; the binding
  half is the entry ABOVE; headline re-verified scaffold-free PASS + the stale-premise correction confirmed on disk).
  **Three load-bearing corrections:** (1) **STALE PREMISE** — `GRADED_COMPARATOR`/`graded_query` have been **default-ON since 2026-08-14**
  (env `HD_GRADED_COMPARATOR` defaults "1"; confirmed in `reading_grounding_loop.py`). The comparator field+query are
  already graded; the only unconditional live `sign()` left is the banking query (`canonicalize()`), measured ~0 cost.
  The audit's "graded flags exist default-OFF" (§5.2) is WRONG. (2) **REFUTED** — on the REAL open-vocab hit@1 task,
  graded vs sign = `+0.0015` NULL, and the ENTIRE brain-faithful code-format family (graded / divisive-norm at read-out
  or composition / in-place sparse / DG expansive-sparse) **plus a faithful self-supervised CBOW learner** ALL land at
  the same distributional ceiling ~`0.05`, all CI-BELOW a generic-word averaging floor `0.171`. The read-out is
  strictly WORSE than naming the average thing — "averaging machine" is a signal-EXTRACTION failure, not a quantiser
  artifact. Only WordNet-**SUPERVISED** learning exceeds the floor (`0.108`); the brain gets no such labels from
  reading (CBOW-NS ≈ shifted-PMI factorisation, Levy & Goldberg 2014 — the self-supervised learner and the counting
  cosine are two compressions of one signal and land together). **So the loss is a meaning-SUPPLY gap (grounding /
  knowledge source), UPSTREAM of the `sign()` and every read-out mechanism.** (3) **NEW & first-class — TWO SIMILARITY
  SYSTEMS, measured on our own reps:** the distribution/co-occurrence channel carries **ASSOCIATIVE RELATEDNESS**
  (WordSim ρ `0.25`, twin loses) but ~0 **FEATURE SIMILARITY** (SimLex `0.04`); GROUNDING carries **both** (`0.42`/`0.21`).
  This is the ATL-feature-similarity vs LIFG/pMTG-associative dissociation, now quantified here. Consequences: (a)
  grading meaning against WordNet **TAXONOMIC** gold systematically UNDER-credits the associative channel we actually
  have — prefer human relatedness/similarity or a relation-controlled gold as the standing meaning metric; (b) the
  SIMILARITY axis is recovered by brain-faithful **STRUCTURE** (narrow ordered context: SimLex `0.075→0.112` as window
  0→±1) and by grounding, **not** by any read-out format; (c) the two systems need **SEMANTIC CONTROL** (IFG,
  task-gated multiplicative gain) — a fixed blend HELPS relatedness but HURTS similarity, so the currently-THIN
  semantic-control deviation now has a concrete measured need. **Effect on this audit:** DEVIATION #2 re-pointed from
  "quantiser/format lever" to "meaning-SUPPLY + two-systems + semantic-control"; §8 lever #1 (`sign→graded`) DEMOTED;
  §7 (meaning present-but-unwired) BOUNDED (distribution alone is insufficient on the taxonomic/similarity axis — it
  carries relatedness; supply/grounding + structure carry similarity). ⚠️ Corpus-age is NOT this instrument's confound
  (`load_corpus_v5` is MODERN — OneStopEnglish + OpenStax — the solver's disk-checked correction; the confound here is
  taxonomic-gold-vs-associative-representation, not archaism). Optional default-off micro-win NOT yet landed:
  divisive-normalisation `center_field` read-out option (direction-correct `+0.007` but within noise — an option, never
  a capability). **This is the concrete brain-foundational re-point: the foundation is not the code FORMAT — it is the
  two-similarity-systems architecture (grounding + structured context) + semantic-control gating + meaning supply.**

- **2026-08-26 — DEVIATION #3 (WRONG MEMORY) REFINED: the cortical READ is real and fixable, but the wall is
  the consolidated CONTENT/CODE, not the read** (from `the_consolidated_cortical_store_is_written_but_never_read`,
  integrated PARTIAL/EXCELLENT, owner-DONE; witness `test_cortical_store_read_path.py` PASS). Built the actual CLS
  read (consolidation by `continual.replay_cycle` → read by pattern completion) and ran the two controls no prior
  cortical problem had: the **live EPISODIC arm** ("wrong memory") and the **consolidation-ablation positive
  control**. Result, 6 held-out units: the brain-faithful cortical read **beats the episodic path ~7-10× on
  transfer, CI-separated over its info-free twin in-domain** (0.484 vs episodic 0.064 vs twin 0.158), and ablating
  consolidation collapses it to 0 while episodic is invariant (the 0.0000 becomes a real drop). **BUT** it does NOT
  clear the first-order counting floor (ties 0.474 in-domain) and on the **powered unseen-cooc regime it sits
  at/below its own twin at no k on any unit** → no cue-specific transfer on genuinely novel queries. **So the
  read-path defect is real and worth wiring, but the standing "memorises-not-transfers" wall is NOT dissolved by
  the read alone — the residual is the consolidated CONTENT/CODE.** Reframe the missing-organ verdict (dev #3):
  "missing cortical-read organ **AND** transfer-bearing consolidated content." Two deeper findings folded in:
  **(a) DEVIATION #4 (dense vs sparse+graded) is LOAD-BEARING ON THE READ** — a dense frequency-summed associator
  collapses to hubs (0.025); **k-WTA sparse coding + frequency-normalised inhibition rescues it to 0.156**, beating
  cosine. Couple B4 with the cortical-read work, not only the `sign()` line. **(b) NEW DEVIATION — recurrent
  ATTRACTOR completion (CA3-class) HURTS pool-RANKING**: settling re-promotes concept-code hubs (a hub jumps rank
  2→0, robust across temperature 1-64), so the faithful semantic *ranking* read is a **graded population read**, and
  the attractor is a *recognition* op, not a ranking op (`cleanup_family`'s modern-Hopfield variant terminates in
  `sign()` — another dev #2 site). **(c) DEVIATION #5 tested and closed:** the interleaved-online CLS process
  (`continual.py` replay actually building the code) is **more data-hungry than batch SVD** and shares its
  data-bound ceiling (SGNS ≈ SVD-of-shifted-PPMI; Levy & Goldberg 2014) — it fails the seen-cooc positive control at
  our ~2400-8000-sentence scale. So "make the code-learning more brain-faithful" is a FALSE lever when the constraint
  is the DATA the process needs; the honest deepening names the binding constraint (lifetime-scale experience). The
  hippocampus (which we have) is what the brain uses for zero-experience concepts; cortical transfer needs experience
  we lack. ⚠️ Proposed hdlab landing (the CLS matched pair — graded sparse+inhibited `space="overlap"` cortical read
  routed against episodic by the p2 recollection-confidence gate) is architecture validation, NOT a floor-beater;
  land default-off. **Re-points §8 lever #2 (cortical-read): validated-but-content-bound, not a stand-alone win.**

- **2026-08-26 — E1 (BINDING) RE-LOCATED: the OPERATOR is VALIDATED; the deviation is the flat-superposition
  RETRIEVAL** (from `the_core_binding_operator_may_not_be_brain_faithful`, integrated EXCELLENT). At EQUAL storage
  our compressed FHRR bind **beats the two WRITABLE brain theories** (tensor-product / TEM product; Rigotti-Fusi
  conjunctive) — TPR loses to FHRR in every exact-cue cell. **So E1's "UNSCORABLE, the deepest deviation, our
  central op has no brain equation" framing is mis-located: the operator is an EFFICIENT choice, validated, not a
  liability.** The REAL deviation is one level up (the superposition-and-unbind RETRIEVAL, shared with E2/E3): we
  superpose many bindings into one vector and un-mix on demand; the brain SEPARATES into slots and retrieves
  CONTENT-ADDRESSABLY, so a brain-faithful version (theta-gamma temporal separation) beats FHRR **CI-separated by
  ~5x under a PARTIAL cue at equal storage** (0.128 vs 0.025), info-free twins losing (predicted by the CA3
  partial-cue dissociation, Nakazawa 2002). **Load-bearing negative:** routing FHRR through the real CA3 attractor
  TIES argmax — you cannot clean your way out of superposition; the fix is the STORAGE architecture, not a terminal
  cleanup. **Sharpens E1:** the per-component normaliser only ever HURTS (L2/raw-sum beat it 32/32 on binding
  recovery, wins zero). **Confirms E2:** `situation_model_multibank` routes by deterministic hash (exact key only,
  no partial-cue path); the owned `ca3_completer` (default-off) is the content-addressable fix, realised only over
  the SEPARATED store. **UNIFIES E1/E2/E3** under one brain mechanism — cue-based content-addressable retrieval with
  similarity interference (Lewis & Vasishth 2005; McElree; Nakazawa 2002). ⚠️ Synthetic construction proof — the
  fix (owned `ca3_completer` + `dg_pattern_separation`, unwired) must be measured on the LIVE reading task before
  any capability claim.

- **2026-08-26 — GOALS/REWARD & METACOGNITION tiers fidelity-scored (strategy extension, closing the §6 scope gap).**
  **GOALS/REWARD:** only two organs are PINNABLE and both are already in the ORGAN_MAP — `action_selection` (BG
  Go/NoGo + TD) is **SAME op-class**, and `successor_representation` (D7) is a **FULLY-PINNED closed form** (faithful
  but MEASURED-AND-LOST). The goal-COMPREHENSION organs (`goal_typing`, `goal_outcome_relation(_grounded)`,
  `goal_achievement`, `outcome_event_extraction`, `parse_goal_extraction`) are **UNSCORABLE** — goal / means-end
  comprehension is a cognitive-level function with NO pinned neural equation, so they are OUR-INVENTIONS judged on
  task, not brain-fidelity (like the POS/parse organs F1/F2). Their live weakness (`organ_abstains`: refuses 2/3)
  is a **COVERAGE** gap — missing broad grounded meaning — NOT a fidelity flaw. `self_manager` (DA vigor / ACC-EVC
  halting) mirrors the neuromodulatory G3 deviation (global scalars, not per-dimension task-driven gain).
  **METACOGNITION (TIER 5):** `gap_detector` is **SAME** ("the healthiest organ"); the abstention family
  (`refuse_gate` / `conformal` / `clarify_gate`) has a real deviation — **no floor on refusal CORRECTNESS**, and
  `state.refusals` is written, counted, reloaded, then never consulted. **NET:** affect (p3) + goals + metacognition
  are now scored; the honest finding is that the higher cognitive tiers are largely **UNSCORABLE** (brain equation
  unpinned), so "brain-faithful" is undefined there and they are inventions judged on task — the fidelity levers
  concentrate in the reading→meaning→memory pipeline.

- **2026-08-26 — AFFECT / VALENCE TIER now has a fidelity verdict** (from `propagate_along_the_relation_that_carries_valence`,
  integrated EXCELLENT). This tier was flagged "built but never fidelity-scored" (§6 scope gap); it now has one.
  `wordnet_polarity_propagation.py`'s shipped **Stage B (taxonomic path-similarity vote) is UNFAITHFUL** — taxonomic
  distance carries NO valence (Spearman −0.0023, inside its null). **The faithful shape** is SIGNED propagation along
  the relations that transfer affect (antonym FLIPS, synonym/derivational/verb-group PRESERVE), plus an **explicit,
  irreducible opposition operator**: antonyms are similar in EVERY feature space (embodied 0.270 ≈ synonym 0.266) yet
  flip the human valence rating (−0.556), so no similarity metric can supply the flip — it must be an explicit
  relation `[P]`. **The one real deviation is the READOUT:** valence is a graded bipolar axis (Osgood; OFC), but the
  organ reports a discrete pole — the signed-vote magnitude already tracks the continuous rating at ρ 0.400, so the
  binary readout hides ~half the signal. Signed propagation reaches 0.726 on 485 words (vs shipped 0.660 on 326);
  universal across POS, sharpest on adjectives (0.8845). **LANDED 2026-08-26** in
  `hdlab/wordnet_polarity_propagation.py` as `dictionary_lookup(..., signed_propagation=True)` (DEFAULT-OFF,
  byte-identical when off, verified identical to the proven cell mechanism; witness
  `test_valence_signed_propagation_landing.py` PASS) -- turn on when the consumer wants the wider/sharper axis.

- **2026-08-26 — MEMORY TIER / DEVIATION #2 advanced** (from `no_automatic_reliability_signal_reaches_the_source_oracle`,
  integrated EXCELLENT). A **DG pattern-separation + CA3 completion recollection gate** was built and re-verified:
  recollection now **self-certifies** (top-5% precision 0.938 vs counting 0.533 on the same items) and dual-process
  routing beats the counting floor CI-separated for the first time (0.365 vs UB 0.336), capturing ~half the oracle
  headroom; info-free twin loses, scramble collapses to 0.00. **Effect on this audit:** D1 (DG separation) moves
  from "SAME but orphan" toward a **proven role**; D2 (CA3 completion) gains the **self-certifying confidence** it
  lacked (for this use it no longer just "terminates in sign and buys nothing"). Answers board Q118 — a label-free
  selection signal IS CA3 completion confidence. **NOT closed:** deviation #3's *cortical-consolidated* read — this
  is the *episodic* recollection side. Lever for more = reading VOLUME (coverage), not a better gate. **Organ LANDED
  2026-08-26 as `hdlab/dg_ca3_recollection_gate.py`** (off-path WIRE_CANDIDATE, witness `test_dg_ca3_recollection_gate_organ.py`
  PASS, registered `dg_ca3_recollection_gate_v1`) — so D1 (DG separation) now has a live, importable, self-certifying
  recollection organ; wire it into the episodic retrieval path (see p2 `the_consolidated_cortical_store...`).

---

## 3. THE SCORECARD (from ORGAN_MAP §1 tally, 38 organs)

| fidelity of our op vs the brain's | count |
|---|---|
| **SAME — our equation IS the brain's** | **5 / 38** |
| RIGHT-OP, WRONG-METRIC | 13 / 38 |
| RIGHT-OP, WRONG-PLACE | 3 / 38 |
| WRONG-OP | 6 / 38 |
| **MISSING entirely** | **7 / 38** |
| UNSCORABLE (brain math UNPINNED) | 4 / 38 |

| how well the brain itself is pinned | count |
|---|---|
| an implementable equation exists in the literature | 12 / 38 |
| form pinned, key function/parameter UNPINNED | 12 / 38 |
| **core operation UNPINNED** | **14 / 38** |

Reachability: **~23 / 38 organs are on the live path (44 of 155 modules)** → ~54% of code unreachable.
Evidence: **10 / 38 organs' only evidence is a self-test PASS** (a construction proof, not a capability).

---

## 4. THE ARCHITECTURE, RECONCILED — every system, its organ, its fidelity

Grouped by the brain's functional tiers. `[P]` = brain equation PINNED, `[U]` = UNPINNED/contested (we invent).

### TIER 1 — PERCEPTION & LEXICAL FORM
- **Visual word form** (VWFA) `[U]` — `vwfa.py`/`char_*`. **RIGHT-OP-WRONG-METRIC:** 1-bit terminal quantiser; trigram order destroyed (position is a hashed atom, not a rotation).
- **Lexical category / POS** (post. temporal) `[U]` — `pos_tagger.py`+`perceptron.py`. **UNSCORABLE** (brain unpinned); own learned perceptron, HARD_PASS 0.906.
- **Dependency / argument-structure parse** (LIFG/pSTS) `[U]` — `arc_parser.py`. **UNSCORABLE**, and a real hole: head/deprel fields are **PLACEHOLDERS at inference** (only form+upos read). *This is the parser the p4 relcl brief is about.*

### TIER 2 — SEMANTIC MEMORY (meaning)
- **Amodal concept hub** (ATL) `[U]` (sub-fact: combination ≈ additive `[P]`) — `lexical_similarity.py`. **WRONG-OP:** unweighted feature overlap is the *inverse* of the brain privileging distinctive features; feature dict hand-built.
- **Per-occurrence pooling** (cortical, divisive normalisation `[P]`) — `grounding_acquisition_loop.py`. **WRONG-OP:** `sign(Σ±1)` where the brain does pooled divisive normalisation; amplifies a noise dim to full weight ~1 in 7.
- **Across-occurrence accumulation** (CLS) `[U]` (weight function) — `reading_grounding_loop.py::observe`. **RIGHT-OP-WRONG-PLACE:** a real graded accumulator, thrown away by `sign()` one line before use (`freeze_graded` default OFF).
- **Representation format** (cortex: graded, low-dim, sparse `[P]`) — 256-dim bipolar default. **WRONG-OP + under-capacity:** dense binary where the brain is graded/sparse; 2,377 concepts in 256 dims; **16× dims buys +0.0843 (largest measured single lever we own).**
- **Sensorimotor spokes** (modality→hub, rule `[U]`) — `grounded_similarity.py`/`sensorimotor_spoke.py`. **RIGHT-OP-WRONG-METRIC + mis-applied:** cosine can't separate synonym from sibling (apple/orange 0.952), capped 0.45 so it never decides; SUPPLY not learning.
- **Semantic comparison** (ATL recurrent settling `[U]`) — `canonicalize_fast`. **RIGHT-OP-WRONG-METRIC:** Hamming between two 256-bit majority patterns ("there is no cosine in the brain").
- **Semantic control** (IFG, multiplicative gain `[P]`; gain function `[U]`) — `context_vector_masked`; dedicated organ is `modern_hopfield_readout.py` (softmax sharpen/blend) + scattered sub-parts. **RIGHT-IDEA-WRONG-ALGEBRA:** context enters *additively*, not as multiplicative gain; the faithful multiplicative version scored WORSE — but that is an estimation-noise result **blocked behind the dense-code defect (B4)**, not evidence against the brain. **Dedicated semantic control is THIN** — a gap.

### TIER 3 — COMBINATORICS & STRUCTURE
- **Thematic role assignment** (Competition Model: cue validity `[P]`) — `thematic_role_labeler.py`. **RIGHT-OP-WRONG-METRIC:** raw counts are not cue-validity; cue *cost* absent; animacy-dominant; HARD_FAIL on real text.
- **Role–filler binding** (theta-gamma / conjunctive / tensor-product — **UNPINNED & 3-way CONTESTED** `[U]`) — `binding.py` (FHRR complex-multiply). **OPERATOR VALIDATED 2026-08-26** (see §2b): at EQUAL storage FHRR beats the writable brain theories (TPR/conjunctive), so it is an efficient choice, NOT the "deepest deviation." ➡️ **The deviation is one level up — the flat-superposition RETRIEVAL (shared with E2/E3): the brain SEPARATES into slots + retrieves CONTENT-ADDRESSABLY; a faithful version beats FHRR ~5x under a partial cue.** The owned fix (`ca3_completer` + `dg_pattern_separation`, both default-off) is unwired.
- **Situation-model register / event indexing** (SEM, PE-segmented `[U]`) — `situation_model_accumulate.py`/`_multibank`, `situation_reader.py`. **RIGHT-OP-WRONG-PLACE:** has the register; **missing the prediction-error segmentation that decides WHEN to write.**
- **N400 coherence monitor** (running-model update magnitude; reference `[P]`, norm `[U]`) — **BUILT 2026-08-26 (§2b): `hdlab/n400_coherence_monitor.py`** (off-path WIRE_CANDIDATE, witness PASS). No longer MISSING. The norm that WORKS is a GRADED forward CONTENT prediction error `1 − cos(content, running_event_gist)` (running reset per event), boundary-posted via the EST relative threshold; it segments discourse and fills the situation model 0.988 vs ≤0.762 floors. The norm that FAILS is the literal `||Δregister||` in the binding space (ties no-op). **Still ISLAND** — wire to `situation_model_accumulate` + measure on the live reader before any capability claim.
- **Construction-Integration** (Kintsch `[P]-ish`) — **MISSING.**

### TIER 4 — MEMORY SYSTEMS
- **DG pattern separation** `[U]` (level ~0.2% `[P]`) — `dg_pattern_separation.py`. **SAME** — but orphan (WIRED NO), untested.
- **CA3 completion** (auto-assoc; update rule = our Hopfield import `[U]`) — `cleanup_family.py`/`iterative_attractor.py`. **RIGHT-OP-WRONG-METRIC:** terminates in `sign()`; measured settling buys nothing. **2026-08-26 (§2b): recurrent attractor completion HURTS semantic pool-RANKING** — it re-promotes concept-code hubs (robust across temperature); the faithful ranking read is a *graded population read*, not a settled attractor (the attractor is a recognition op). *Consistent with the binding load-bearing negative: CA3 cleanup on a flat superposed read TIES argmax.*
- **Hippocampal one-shot write** (Marr `[P]`; allocation `[U]`) — `hippocampal_encoder.py`. **SAME (write op)** — index/allocation half missing; its 14/14 self-test is a **ceiling, not evidence** (exact cue solved by projection alone).
- **Consolidation / replay** (SWR; selection function `[U]`) — live: `reading_grounding_loop.py::checkpoint`; faithful: `continual.py` (**ISLANDED**). **WRONG-OP-CLASS at the live site:** single averaging op, ungated/un-interleaved/un-budgeted.
- **Working memory** (attractor vs synaptic — CONTESTED `[U]`) — `working_memory.py` **contains no WM (filename trap)**; `slot_attention_wm.py` = learned softmax head. **MISSING / RIGHT-OP-WRONG-METRIC.**
- **Sequence/order** (asymmetric Hebbian `[U]`) — `sequence_memory.py`. **SAME op-class.**
- **Successor representation** (`M=(I−γP)⁻¹` **FULLY PINNED** `[P]`) — `successor_representation.py`. **Faithfully implemented but MEASURED AND LOST** — 0/24 arms clear the bar; **degrades with scale** (its own ladder refutes "scale it up").
- **Cascade synapse** (multi-timescale, **FULLY PINNED** `[P]`) — **MISSING.** PARKED-BY-SCALE (advantage crossover N>~1e6; we run d≤4096, so a null here is the *published prediction*).
- **Synaptic tag & capture** (tag×PRP product `[P]`, but §10.1 says drop from pinned) — `excitability.py`. **RIGHT-OP-WRONG-METRIC:** single EWMA, not a two-factor product; WIRED NO.
- **Theta-gamma ordered buffer** (~7 slots `[P]`; encoding op `[U]`) — `situation_focus.py`. **RIGHT-OP-WRONG-METRIC:** capacity 4 vs ~7; order channel empty (HARD_FAIL).
- **Long-term semantic store** (no single brain analogue `[U]`) — `hd_fact_store.py`. **RIGHT-OP-WRONG-METRIC** ("the fourth prototype operator"); 65.7% of grounded facts are self-referential tautologies.

### TIER 5 — CONTROL, PREDICTION, METACOGNITION
- **Prediction / predictive coding** (residual precision-weighted `[P]`) — `predictive_coding.py`, `slot_attention_wm.py`. **RIGHT-OP-WRONG-METRIC:** residual computed on a `sign()`-quantised prediction (big & small flips indistinguishable); no precision term; WIRED NO; MIDDLE_BAND. *Encoder objective is also cloze, not forward-PC — see DEVIATIONS.*
- **Attention / information foraging** (MVT leave rule `[P]`) — `information_foraging.py`, `gap_driven_reader.py`, `corpus_registry.py`, `self_manager.py` (ACC/EVC halting), `situation_focus.py`. **The leave-rule exists but "WHAT TO READ NEXT" is effectively MISSING:** readable universe is a hard-coded 4-entry dict vs 36 corpora on disk; downgraded to MIDDLE_BAND (FROZEN beats FORAGE); the organ has never seen real text.
- **Metacognition / familiarity / abstention** (SDT criterion `[U]`) — `gap_detector.py` (**SAME — "the healthiest organ," AUC 1.000**, but its output has nowhere to go because foraging is unbuilt), plus a rich family: `refuse_gate.py`, `conformal.py`, `clarify_gate.py`, `completeness_checker.py`, `reachability_audit.py`, `quality_proxy.py`, `coref_distractor_suppress.py`. **Deviation:** no floor on refusal *correctness*; `state.refusals` written, counted, reloaded, then **never consulted**.
- **Reasoning over knowledge** (constraint satisfaction) — `reasoner.py` (**FAITHFUL, banked**), `multi_hop.py`, `gather_reason.py`, `glass_box_loop.py`, `kg_traversal.py`. Coverage-bound, not mechanism-bound.

### TIER 6 — AFFECT · GOALS · SOCIAL (BUILT, BUT LARGELY OUTSIDE THE FIDELITY AUDIT)
> These systems have real organs but are **NOT in the ORGAN_MAP's 38** — so their brain-fidelity has **never been
> scored.** That is itself a finding: the fidelity audit stops at the reading/memory pipeline.
- **Affect / valence / appraisal** (amygdala, vmPFC) — **richly built, UN-AUDITED:** `context_grounded_valence.py`, `consequence_learning_loop.py`, `wordnet_polarity_propagation.py`, `word_learning_tool.py`, `word_acquisition_loop.py`, `idiom_grounding.py`. *p3 (`propagate_along_the_relation`) lives here.*
- **Goals / reward / motivation** (BG, OFC) — **richly built:** `goal_typing.py`, `goal_owner_select.py`, `goal_achievement.py`, `goal_outcome_relation(_grounded).py`, `outcome_event_extraction.py`, `parse_goal_extraction.py`, `action_selection.py` (**BG Go/NoGo + TD, SAME op-class**), `successor_representation.py`, `self_manager.py` (DA vigor). *p1's convergent line (`organ_abstains`) lives here.*
- **Theory of mind / mentalizing** (TPJ, mPFC) — **ABSENT.** `state_of_mind.py` is explicitly *not* ToM (it's a coref tracker); the only false-belief (Sally-Anne, nested-HRR) work sits in `experiments/` and **was never promoted to `hdlab/`.** Clean gap + clean build target.

### TIER 7 — LEARNING & OUTPUT
- **Cortical learning rule** (lexical-semantic acquisition **UNPINNED, deliberately** `[U]`) — `learner/core.py`. **WRONG-OP:** MDL is model-selection, not a synaptic update rule; **the loop was never measured as a learner.**
- **Read→extract→consolidate loop** — PARTIAL (CLS shape right; the "what to extract from reading" step unsolved).
- **Language production / generation** (Levelt staged; lemma/lexeme split `[P]`) — **THIN, essentially ABSENT:** only `generation.py` (S-matrix + Langevin + cleanup). `substrate.py` production slots are EMPTY. The expressive side does not exist as an organ.

### COREFERENCE / ENTITY TRACKING — (spans tiers; the 07-30 "ABSENT" is corrected)
Heavily built: `coref.py`, `coreference_resolver.py`, `coref_distractor_suppress.py`, `bundle_focus_coref.py`,
`event_centrality_coref.py`, `scene_segment.py`, `state_of_mind.py`, `entity_slot_gate.py`, `slot_attention_wm.py`,
`situation_reader.py`, `event_bundle.py`. **RIGHT-OP-WRONG-METRIC:** invented arithmetic (`count + β·exp(−λΔ)`)
over a pinned *ordering*; **mentions are SUPPLIED (gold), so it does not transfer to raw prose**; margin over the
strong floor NOT CI-separated at n=57. *Competitive antecedent resolution among 2+ plausible referents remains the
real open case.*

### DISCOURSE / BRIDGING — (also corrected from "ABSENT")
Exists as *relation* inference (`situation_model_accumulate` CausalLinkRegister, `goal_outcome_relation*`,
`gather_reason`, `multi_hop`). **Explicit causal/elaborative bridging of the UNSTATED** (Graesser) is still
thin/UNPINNED and, structurally, "IS coreference in disguise → must reuse the coref organ."

---

## 5. THE LARGE-SCALE DEVIATIONS (we do it, not the brain's way)

1. **MOST OF THE ARCHITECTURE IS INVENTION, NOT REPLICATION** — 14/38 core operations UNPINNED, 4 UNSCORABLE,
   only 5 SAME. Including **the central binding operation (3-way contested)**. Honestly labelled, but it means
   "brain-faithful" is *undefined* for a large fraction of the substrate; those parts are bets, and should be
   named as bets.
2. **~~THE `sign()` QUANTISER EVERYWHERE~~ — REFUTED 2026-08-26 AS THE AVERAGING-MACHINE LEVER (see §2b).** The
   34-site `sign()` was theorised to make the system an averaging machine. **It does not, and the graded flags are
   already default-ON (since 08-14), not default-OFF.** On the real open-vocab task graded vs sign is NULL, and the
   whole brain-faithful code-format family + a self-supervised learner all tie plain counting below a generic-word
   floor. **The SUM is faithful; the terminal normaliser is a non-issue.** The real deviation is one level up:
   **meaning SUPPLY + the TWO SIMILARITY SYSTEMS (associative relatedness vs feature similarity) + SEMANTIC CONTROL
   gating.** The averaging machine is a signal-EXTRACTION/supply failure, not a quantiser artifact.
3. **WE QUERY THE WRONG MEMORY** — retrieval answers out of the fast episodic (hippocampal) codes and **never
   reads the consolidated cortical store** (ablating consolidation moved the read-out by 0.0000). The standing
   "memorises but does not transfer" negative is the *signature of hippocampus-only retrieval*. **REFINED
   2026-08-26 (measured, §2b):** reading the store the brain's way DOES beat the episodic path ~10× on transfer
   (CI-separated over the twin), so the cortical-read organ is real and fixable — BUT it does not clear counting
   and carries no cue-specific signal on powered unseen queries, so the wall is **BOTH a MISSING cortical-read
   organ AND transfer-bearing consolidated CONTENT** (data/lifetime-scale, not the read op).
4. **DENSE where the brain is SPARSE + GRADED** (B4) — the largest measured single lever we own (16× dims).
5. **ONE STORE DOING TWO JOBS** — fast hippocampal binding and slow cortical consolidation are conflated; the
   faithful consolidation engine (`continual.py`) is **islanded**.
6. **ADDITIVE where control is MULTIPLICATIVE** (IFG gain, C3); **CLOZE where learning is FORWARD-PREDICTIVE** —
   **SPLIT 2026-08-26 (§2b) into two rows with OPPOSITE verdicts:** the UPDATE/segmentation half (the N400 coherence
   monitor, F5) is missing-buildable-and-WINS → BUILD; the LEARNING half ("we learn by cloze not forward-PC") is a
   RIGOROUS NEGATIVE (forward-PC does NOT beat cloze on paradigmatic meaning) → DEPRIORITISE. Do not couple them.
7. **~54% OF THE CODE IS UNREACHABLE** — built-but-unwired islands; several *faithful* organs (DG separation,
   cascade-adjacent, `continual.py`) sit unwired.

---

## 6. THE LARGE-SCALE GAPS (absent or thin systems)

- **7 organs MISSING outright**, the load-bearing ones being: the **cortical-read organ** (fixes deviation #3),
  the **N400 coherence monitor**, **Construction-Integration**, **corpus-selection foraging** ("what to read
  next"), the **cascade synapse** (parked-by-scale), and **discourse bridging of the unstated**.
- **Theory of Mind — ABSENT** (mechanism exists in `experiments/`, never promoted).
- **Dedicated semantic control — THIN** (one primitive + scattered sub-parts).
- **Language production — THIN** (one file; the expressive half of a brain is missing).
- **Scope gap in the audit itself:** affect, goals/reward, and metacognition are **built but never fidelity-scored**
  against the brain — likely deviations are hiding there, unmeasured.

---

## 7. THE MEANING RE-FRAME (2026-08-26 — updates the plan's foundational premise)

`LONG_TERM_PLAN.md` is built on "meaning is absent / you cannot route meaning that was never supplied / every
downstream fix is a better filing system for empty folders," and every phase is gated **supply-before-architecture**.

**This session weakened that premise.** On a **frequency-controlled (fair) metric**, the grounded meaning signal
**beats the strongest frequency floor CI-separated** (0.741 vs 0.558; info-free twins lose) — the old "counting
beats us" was measured on a metric that was secretly scoring frequency. **So meaning is present-but-unwired and
context-free, not empty.** The block has moved from "there is nothing to route" to "route it, and condition it on
context." The plan's Phase-1 "supply more norms" lever is also downgraded (projecting the norms we
have covers the gap). **Reconcile the plan's §3 diagnosis with this before quoting it.**

**BOUNDED 2026-08-26 (§2b — the `sign()` refutation drills):** "meaning present-but-unwired" is TRUE for the
**ASSOCIATIVE RELATEDNESS** system (distribution carries it, WordSim ρ 0.25) — that read-out we can wire. It is
**NOT** true for the **FEATURE SIMILARITY** system (distribution ~0 on SimLex): that axis is genuinely thin and must
be BUILT brain-faithfully from grounding + structured local context, then GATED against the associative system by
semantic control. So "present-but-unwired" splits: one system to wire, a second system to build. Grade meaning on
human relatedness/similarity, not taxonomic WordNet, or the associative system reads as broken when it is not.

---

## 8. LEVERAGE RANKING — and how it reshuffles the queue

The current problem queue (p1–p4) captures **only one** of the top brain-fidelity levers. The biggest
cross-cutting deviations are **not queued.** Candidates, ranked by leverage (blast radius × tractability):

1. **The `sign()` → graded path — DEMOTED *as a READ-OUT lever* 2026-08-26; but ALIVE as a BINDING-SITE guardrail
   (§2b CORRECTION).** On the read-out the graded switch is already ON and buys ~null. **BUT** in the
   binding/superposition regime sign() IS a real averaging machine for CORRELATED fillers, coupled to B4 (graded
   fillers + a signed bundle re-creates the averaging machine; capacity cliff B*=8→B*=12) — so keep it as a joint
   sign()+B4 guardrail on the binding/memory line (p3, p5), NOT a read-out change. **At the read-out, REPLACED at the
   top by the meaning-SUPPLY / TWO-SIMILARITY-SYSTEMS / SEMANTIC-CONTROL line.** **✅ DELIVERED 2026-08-26 (§2b,
   integrated PARTIAL/EXCELLENT):** the feature-similarity system is BUILT + proven (distinctive-feature WHITENING beats
   raw grounding CI-separated on held-out SimLex/SimVerb; specialises toward similarity); the semantic-control SWITCH is
   REFUTED (fixed multiplicative FUSION beats the task-gate even with a strong associative system) — so the near-term
   wire is the whitening transform + a FIXED two-system fusion, NOT a switch; the gate is a later selection-task (WSD)
   deliverable. Residual = meaning SUPPLY (richer features, per the finer drill's fidelity boundary).
2. **The cortical-read organ (deviation #3) — VALIDATED-BUT-CONTENT-BOUND 2026-08-26 (§2b).** The read beats the
   wrong memory ~10× but the residual wall is the consolidated CONTENT (data/scale), not the read op. Land the CLS
   matched-pair read default-off (architecture hygiene); route the residual to the content/supply lane (item #1).
3. **Meaning wiring + context-conditioning — QUEUED (p6).** The fair-metric win made it actionable; now bounded by
   §2b — wire the ASSOCIATIVE read-out we have, but the SIMILARITY axis needs the item-#1 build, not wiring.
4. **Dense → sparse+graded code (B4, deviation #4).** Now measured LOAD-BEARING on the cortical READ (0.025→0.156),
   NOT on the open-vocab read-out (null there). Couple with the cortical-read work (#2), not the retired `sign()` line.
5. **The binding operator (E1) — RESOLVED 2026-08-26 (p3, EXCELLENT).** The operator is VALIDATED at equal
   storage (beats the writable brain theories); the REAL lever is one level up — the flat-superposition
   **RETRIEVAL**. Wire the owned content-addressable path (`ca3_completer` + `dg_pattern_separation`) into the
   separated store, measured on the live task (~5x under partial cue). See §2b + the binding SOLVED Rec B.
6. **Fidelity-audit the affect / goals / metacognition systems** — built but never scored against the brain.
7. **Promote Theory of Mind** from `experiments/` into a real organ.
8. p2 (reliability signal), p3 (valence propagation), p4 (relcl parser) — the existing queue, unchanged.

**Recommendation:** the next problems to package are #1 (`sign→graded`) and #2 (cortical-read), because they are
cross-cutting, tractable (flags/organs partly exist), and outrank most of the current queue on blast radius. Do
NOT flood — package them as the current builds converge.

---

## 9. OPEN RECONCILIATION ITEMS (to close in later passes)
- Re-verify the ORGAN_MAP verdicts that are load-bearing here against HEAD (esp. B4's +0.0843, the `sign()`
  2AFC/hit@1 split, the retrieval-order 0.0000 ablation).
- Fold the affect/goals/metacognition organs into a fidelity table (currently un-scored).
- Reconcile `LONG_TERM_PLAN.md` §3 with the §7 re-frame in the plan file itself.
