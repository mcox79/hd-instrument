# Pre-reg: intrinsic_foundation_loop_tie_gaps_defmatch_v1

Filed 2026-07-25. Cell author: hdi_exp_dev. VET-PENDING (skunkworks owns landed-VET). LOCAL-only, no push, no atom banking.

## Question (one change, can-fail)
The VET-cleared powered loop (banked 29573) proved that acquiring the RIGHT definitional fact resolves
reasoner tie-gaps (ARM1 oracle 0.5312 vs ARM3global scramble 0.3672, McNemar p=0.00985) but is CAPPED: the
oracle ceiling is only 0.531 and the autonomous arm (ARM2 0.4688) does NOT clear the global scramble. Both
caps are attributed to the MATCH being thin-GloVe cosine over augmented choice-text vs stem: near-synonym
choice tokens ({solute,dissolved,water} vs {solvent,dissolved,water}) collapse to one blended vector.

THE ONE CHANGE: swap ONLY the decision meaning-match. Instead of a flat GloVe cosine of (choice_label +
concatenated fact-texts) vs stem, match on DEFINITIONAL STRUCTURE -- keep the role/relation structure, DROP
the near-synonym concept label, and score each definitional PREDICATE (the role-filler = the fact object
recovered glass-box from the trust-gate store) SEPARATELY against the stem, taking the best-aligned role-filler.
Everything else (leak-free arms, tie population n=128, controls, encoder, reasoner, retrieval) is IMPORTED
UNCHANGED from powered_v1 (build_pool, mcnemar, breakdown) + v1 (arm functions).

## Arms (ISOLATE the match as the one variable)
Reused UNCHANGED (imported; reproduce powered EXACT as positive control):
- ARM0 arm0_legacy_combiner (reasoner legacy tie-break) = 0.375 (48/128)
- FLOOR floor_mm_no_facts (GloVe match, no facts) = 0.3984 (51/128)
- ARM1 arm1_oracle_ceiling (GloVe match, oracle facts) = 0.5312 (68/128)  <- ceiling comparator
- ARM2 arm2_autonomous_loop (GloVe match, autonomous facts) = 0.4688 (60/128)  <- autonomous comparator
- ARM3g arm3_scramble_global (GloVe match, globally scrambled oracle facts) = 0.3672 (47/128)  <- scramble
NEW (the definitional-structure match; role-slot profile via hd_fact_store trust-gate, glass-box recovered):
- ARM_DEF def_oracle_grounded: def-structure match over ORACLE facts (same fids as ARM1). ONE variable vs ARM1 = match.
- ARM_DEF_AUTO def_auto_grounded: def-structure match over AUTONOMOUS facts (same fids as ARM2). ONE variable vs ARM2 = match.
- ARM_DEF_SCR def_scramble_global_grounded: def-structure match over globally-scrambled oracle facts (MUST-FAIL for the new match).
- ARM_DEF_SYM def_oracle_symbolic: GloVe-FREE variant (rarity-weighted content-word overlap of predicate vs stem) -- purely propositional assignment-lookup; diagnostic for build B.

## Match definitions
- def-structure score(choice C, stem): profile_C = list of (relation, object) recovered glass-box from an
  HDFactStore ingest of C's facts (WorldTree=TRUST_HIGH). score(C) = max over (rel,obj) in profile_C of
  filler_align(obj, stem). Concept LABEL excluded; predicates scored SEPARATELY (no blend), best role-filler wins.
  grounded filler_align = cosine(L2(encode(object)), stem_vec) [same encoder, isolates STRUCTURE not encoder].
  symbolic filler_align = sum over shared content-words w of rarity(w), rarity(w)=1/log(2+df(w)) [GloVe-free].
- gold_only guardrail: len(valid)==1 -> return the single choice UNCHANGED (identical to legacy) -> gold_only@1.00.
- empty profile -> score sentinel -2.0 (below any cosine/overlap); all-empty -> deterministic lowest index.

## PRIMARY comparisons (paired McNemar exact two-sided binomial; SAME n=128 pool; per-arity + per-split)
- ARM_DEF vs ARM1 (does def-structure LIFT the ceiling?)
- ARM_DEF_AUTO vs ARM2 (does it lift the autonomous arm?)
- ARM_DEF_AUTO vs ARM_DEF_SCR and vs ARM3g (does the autonomous def arm CLEAR scramble?)
- ARM_DEF vs ARM_DEF_SCR (must-fail: the def gain must be concept-specific)
- ARM_DEF_SYM vs ARM1 (does PURELY propositional structure lift?)

## Bands (pre-registered, fixed BEFORE the run, reported STRAIGHT)
- HARD_PASS = definitional-structure match significantly lifts the ceiling AND/OR moves the autonomous arm to
  clear scramble: (ARM_DEF vs ARM1 McNemar p<0.05 AND arm_def_acc>arm1_acc) OR (ARM_DEF_AUTO vs ARM_DEF_SCR
  McNemar p<0.05 AND arm_def_auto_acc>arm_def_scr_acc). => target is REAL, greenlights earn-it build B.
- HONEST_NEG = no lift over the GloVe match (ARM_DEF not-significantly > ARM1 AND ARM_DEF_AUTO not-clearing
  scramble). => definitional structure ALONE insufficient; decisive: saves B, routes to a different grounding.
- MIDDLE_BAND = mixed / wrong-direction-significant / guardrail breach.
- Guardrails (must hold for HARD_PASS): gold_only preserved >= 1.0; positive control reproduces powered EXACT.

## Positive control (Gate D; reproduce prior at test regime)
FULL run must reproduce the powered_v1 arms EXACTLY (same pool, same imported arm functions, same seed):
n_pool==128, arm0=48, floor=51, arm1=68, arm2=60, arm3global=47 correct. Mismatch -> POSITIVE_CONTROL_FAIL.

## Coverage preflight (report; if thin, say so -- a win over 3 concepts is an artifact)
def_profile_coverage = fraction of tie GOLD concepts with >=1 WorldTree definitional fact (non-empty profile);
also fraction over ALL tie choices. Reported in metrics.

## FEED B (deliverable, not optional)
(1) per-concept role-slot definitional profile {relation: [objects]} emitted for every tie choice concept.
(2) held-out-to-new-concepts split: tie GOLD concepts partitioned by deterministic sha256 hash (30% held-out);
    ARM_DEF accuracy reported per side (train-concept vs held-out-concept units) so B has a target + yardstick.

## Anti-leak (hard)
acquisition keyed on choice/stem content-words NEVER correct_index; def match uses stem + profile, never the
answer; correct_index enters ONLY the tally + the (decision-independent) held-out split partition. gold_only
single-valid decisions returned UNCHANGED in every arm. Held-out ARC (Easy+Challenge test); science rules not
from test labels. Deterministic (fixed seeds, numpy default_rng, sorted iteration, sha256 not python hash()).

## Compute architecture
class: (b) sequential-CPU with justification. Per-unit HDFactStore ingest has genuine sequential dependency
(store state per choice); the cell IS the substrate-primitive path (glass-box role-slot bind/unbind); full
wall ~2-4 min (<10 min), FOREGROUND-to-completion (INLINE-LOCAL, remote-not-authorized). storage: sharded
(each choice its own HDFactStore; role-slot bound facts). no batching candidate (wall<10s per-point n/a; total<10min).

## Schema-vet fields
- cardinality_ok: n/a (no sweep axis; fixed n=128 pool + fixed arm set).
- final_metrics_atomicity: tmp_replace.
- discriminator_fires: def-structure match must produce DIFFERENT picks than FLOOR (smoke asserts pick-vector != floor).
- baseline_in_band: ARM1 comparator 0.531 in [0.05,0.95]; ties are genuine multi-valid (not saturated).
- crlb_n/a: "categorical tie-break accuracy over a fixed pool; no continuous noise floor; chance ~ 1/mean_arity".
- arms_differ_verified: smoke hashes pick-vectors; ARM_DEF vs FLOOR must differ (concept-specific gain must move picks).
- calibration_check: default_ok_for_this_regime (STORE_DIM=4096, K_FACTS=8 inherited from VET-cleared v1).
- real_code_path_exercised: [build_acq_index, HDFactStore, build_def_profile, decide_by_def_structure, powered_v1.build_pool, mcnemar].
- deterministic_seeding: true (fixed int seeds; sha256 for the held-out split; no python hash()).
- progress_logging: print_flush_true + heartbeat jsonl.
- positive_control_arms: reproduce powered_v1 arm0/floor/arm1/arm2/arm3global EXACT (integer counts).
