# Pre-reg: arc_combiner_confidence_gated_escalation_v1 (2026-07-24)

## Question (compute-proportionality class: MECHANISM MAGNITUDE on the real task)
Our bind+settle (CI) reasoning scores ~0.690 ARC-Challenge on GOLD facts but ~0.341 on the best real
retrieved+selected pool. Retrieval is recall-capped (pool never = gold), so the REASONING step must
become robust to imperfect facts. Does a confidence-gated, bounded ESCALATION LOOP wrapped around the
UNCHANGED CI settle close a real fraction of that in-cell gap on the REAL selected pool?

Numbers 0.690/0.341 are Director-supplied (HYPOTHESIZED@task; the research drill flagged them not
disk-re-verified). This cell MEASURES its OWN baseline and oracle IN-CELL on the same combiner+pool, so
the gap is measured consistently and the HARD-PASS margin is a FRACTION of the IN-CELL gap, not of the
external number.

## One variable
The reasoning-side ESCALATION LOOP. UNCHANGED: PPR spreading pool (ppr arm B), the selection gate
(sel.gate_scores -> B_gate top-K_SEL selected pool), and the CI settle combiner (agg.aggregate
mode="settle"). Only what happens BEFORE/AROUND the settle changes across arms.

## Primitives wired (both VERIFIED-ON-DISK, per task)
- BRIDGING = substrate/khop.py (traverse; FHRR unbind+cleanup; Merkle AuditChain). Adapter
  `_pool_to_mini_kg` (NAMED, self-tested) builds a per-question mini-KG from selected-pool content-word
  co-occurrence: entities = content words (FHRR cphasor), one generic RELATES relation, subject_memory =
  khop bundle format. Bridge = >=1-hop traverse from a stem-anchor word to synthesize a connecting fact
  concept; encode "head pivot tail" with SemanticHDEncoder, add to pool, re-settle ONCE.
- CONFIDENCE GATE = conformal_tau (experiments/_substrate_refuse_gate_v8_conformal_v1_core.py). Confidence
  signal = CI-settle choice-margin (top1 - top2 of settled choice activations). tau = conformal_tau(margins
  of CORRECTLY-answered CALIBRATION questions, alpha=ALPHA_GATE). Commit if margin>=tau, else escalate.

## Arms (settle mechanics identical across all; judged on the ANSWER)
- A baseline        -- selected pool -> settle once -> argmax. Full coverage. (== the ~0.341 condition, re-measured.)
- B abstain_only    -- settle; if margin<tau -> ABSTAIN (no answer). Isolates value of knowing-when-not-to-guess.
- C bridge          -- on margin<tau: ONE khop bridging pass over selected pool -> add bridged fact -> re-settle -> argmax. Full coverage.
- F bridge_random   -- MUST-FAIL: same trigger, compose a RANDOM in-pool pair into a bridged fact. Must NOT beat A.
- D gapfill_disc    -- on margin<tau: inject the top goal-relevant STORE fact NOT in pool at DISCOUNTED weight -> re-settle -> argmax. Full coverage.
- E gapfill_undisc  -- MUST-FAIL control: identical to D but FULL (retrieved) weight. Prediction: MORE confident-wrong => WORSE than D.
- G combined        -- gate; if low-confidence: bridge-if-premises-present else discounted gap-fill; terminal fallback = low-confidence guess (settle argmax). Bounded to ONE escalation attempt. Full coverage.
- O oracle_gold     -- CONTEXT ceiling: gold central facts -> settle -> argmax (the ~0.690 ceiling).

Gap-fill source = the WorldTree tablestore (STORE), selected by answer-AGNOSTIC goal_score (stem relevance +
choice-separating margin; NEVER uses correct_index). NOT gold labels. Oracle-gold uses gold ONLY as a ceiling ref.

## Metrics (per arm, on the TEST split; Easy + Challenge separately; PRIMARY = Challenge)
- end-to-end accuracy (full-coverage arms; abstentions on G fall back to a guess so G is comparable to A)
- accuracy-when-answered + coverage + risk-adjusted (acc_when_answered * coverage) for abstain arm B
- confident_wrong_rate = frac(answered-and-wrong with FINAL margin >= tau)  [secondary; the D-vs-E discriminator]
- escalation-path glass-box counts: committed / bridged / gap_filled / abstained; khop AuditChain roots sampled
- in-cell gap = O_challenge - A_challenge (TEST); HARD-PASS margin is a FRACTION of THIS gap

## Bands (author-designed a priori; NOT tuned to force a win)
- GAP_FRAC_HP = 0.20 : (G_chal - A_chal) >= 0.20 * gap  AND  (G_chal - A_chal) >= ABS_G_MIN, replicated >= 2 seeds
- ABS_G_MIN   = 0.02 : absolute floor so a vacuously tiny gap cannot pass
- GAP_FRAC_MB = 0.05 : MIDDLE band lower edge
- DISCOUNT guard  : E_confident_wrong_rate - D_confident_wrong_rate >= 0.01  (undiscounted MORE confident-wrong)  AND  D_acc_chal >= E_acc_chal - 0.005
- BRIDGE guard    : (C_chal - F_chal) >= 0.0  AND  (F_chal - A_chal) <= 0.02  (random-bridge does NOT help)
- GAP_MIN_HEADROOM = 0.03 : if in-cell gap < 0.03 -> INCONCLUSIVE (no headroom; not a mechanism failure)
- AG_BASELINE_SAT = 0.95 : A_chal >= this -> vacuous

Verdict:
- gap < GAP_MIN_HEADROOM or A_chal >= AG_BASELINE_SAT -> ESCALATION_INCONCLUSIVE_NO_HEADROOM
- (G-A) >= GAP_FRAC_HP*gap and (G-A) >= ABS_G_MIN and BRIDGE guard ok and DISCOUNT guard ok -> ESCALATION_HARD_PASS
- (G-A) >= GAP_FRAC_MB*gap (or HP arithmetic met but a guard violated) -> ESCALATION_MIDDLE_BAND
- else -> ESCALATION_HARD_FAIL (reasoning-robustness is not the lever; report straight, redirect to retrieval quality)

## HARD-PASS / HARD-FAIL (falsifiable, pre-registered)
HARD-PASS: G closes >= 20% of the in-cell Challenge gap (>= 0.02 absolute) on >= 2 seeds; random-bridge does
NOT beat baseline; undiscounted gap-fill is WORSE (more confident-wrong) than discounted.
HARD-FAIL: G does not beat A -> reasoning-robustness isn't the lever; direct future effort to retrieval quality.

## SCHEMA-VET gates
- sweep_alignment_verdict: ALIGNED (no nominal-vs-effective sweep; arms differ by escalation op only)
- discriminating_fraction: N/A (not a sweep; discriminator = per-arm accuracy gap + confident-wrong rate;
  smoke verifies A in-band [0.05,0.95] with real headroom vs O, and escalation FIRES on a nonzero low-conf subset)
- composition_edges: pool->selection = SHAPE_MATCH (reused UNCHANGED). selection->settle = SHAPE_MATCH
  (fact_hd[K,N] + q_rel[K] -> agg.aggregate, reused UNCHANGED). pool->khop = SHAPE_MISMATCH_adapter__pool_to_mini_kg
  (NAMED adapter builds FHRR entity/relation codebooks + subject_memory from pool content words; self-tested).
  khop_bridge->settle = SHAPE_MATCH (bridged concept re-encoded to [N] fact, appended to fact_hd).
  gapfill->settle = SHAPE_MATCH (store fact embedding appended to fact_hd at discounted q_rel).
- positive_control_arms: A baseline reproduces the ~0.341 selected-pool condition (Director-supplied,
  unverified) AT THE TEST REGIME; O reproduces the ~0.690 gold ceiling. Reported; not hard-gated on the exact
  external numbers (they are HYPOTHESIZED, not disk-verified). Regime-extension: SHAPE_MATCH (same combiner,
  same pool, same corpus as the selection-gate cell).
- functional_requirements:
  1. Know when the settle is under-confident -> conformal_tau on settle-margin (CONFIDENCE GATE).
  2. Recover a missing connecting fact from two present premises -> khop.traverse (BRIDGING).
  3. Supply a plausible missing fact without over-trusting it -> discounted gap-fill (NEW mechanism; the
     literature's confidence-discount that schema completion does not supply for free).
  4. Decline rather than confidently guess wrong -> abstain arm B.
- real_code_path_exercised: [SemanticHDEncoder, ppr pool, sel.gate_scores, agg.aggregate(mode="settle"),
  khop.traverse, conformal_tau] all constructed/called in self_test at tiny scale.
- substrate_signature_checked: [agg.aggregate, khop.traverse, conformal_tau] bound via a planted call.
- guard_baseline_validated: N/A (no control-beats-baseline break-guard; must-fail controls are reported, not run-breaking).
- deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration + stratified CAL split by
  sorted-index modulus (CAL_EVERY); NO hash()-seeded RNG, NO list(set()) ordering.

## Cell-template mandates
- except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
- final_metrics_atomicity: tmp_replace ; start_marker_written ; crash_diagnostic_present ; heartbeat_present
- arms_differ_verified at smoke (A/B/C/D/E/F/G pick-digests differ where semantically expected)
- baseline_in_band: A_chal in (0.05, 0.95) with headroom vs O (AG guard)
- crlb_n/a: end-to-end accuracy has no closed-form noise floor; discriminator = measured accuracy gap
- storage_strategy: sharded (each fact = own embedding; each mini-KG concept = own FHRR codebook vector)
- calibration_check: adaptive_with_discriminator_gate -- tau is conformal-calibrated on held-out CAL
  (NOT hand-set); discriminator-still-fires check = escalation fires on a nonzero low-confidence subset, logged.
- progress_logging: line_buffered_stdout (line-buffered stdout + per-stage heartbeat)
- multi_seed_smoke: >= 3 seeds at reduced scale on arms A/D/E/G; D-vs-E and G-vs-A signal must not vanish across seeds
- all reported numbers MEASURED@ this cell's metrics.json

## Compute architecture
mixed CPU: batched GloVe encode (SemanticHDEncoder) + scipy.sparse batched PPR (imported UNCHANGED) +
cheap per-question CI settle (K_SEL~4 facts, tiny matrices) + escalation re-settles ONLY on the
low-confidence subset + tiny per-question khop mini-KG (K_SEL words). Sequential-CPU justified: settle has
genuine per-question sequential structure and the substrate primitive IS the CI settle being validated
(bit-identical CPU). Wall target: smoke (question subset, 1 seed) < 5 min; FULL (2 seeds) < 10 min
foreground (INLINE-LOCAL; reduce n_dim/questions if over). NOT remote-portable (GloVe + WorldTree
git-ignored/large). No push/remote-persist. VET-PENDING.
