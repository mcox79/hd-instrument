# Pre-reg: exp_intrinsic_foundation_loop_tie_gaps_defmatch_v2

REFINED definitional-structure match that fixes the 3 operationalization flaws defmatch_v1's VET found
(c6aeeb2b3, HONEST_NEG operationalization-bound), and DECISIVELY tests whether definitional grounding lifts
the CHALLENGE-split ceiling or is genuinely dead. DIAGNOSTIC, not a rescue expected to succeed -- designed
to fail cleanly if the signal isn't there.

## Question class + compute-proportionality
DIRECTIONAL GATE / can-fail diagnostic (does discriminating-predicate-weighted, label-inclusive def match
lift the Challenge tie ceiling over scramble?). Cheapest decisive method: re-score the SAME n=128 tie pool
with a refined match; NO training fit. FULL wall ~= defmatch_v1's 219s (<10 min). INLINE-LOCAL
foreground-to-completion (no push/remote authorized). Sequential-CPU justified: HDFactStore trust-gate
ingest+glass-box-recover per (unit,choice) is the substrate primitive being exercised, and n=128 is tiny;
wall < 10 min. No GPU batching candidate.

## The 3 refinements (isolate the MATCH SCORING; reuse everything else)
- **R1 keep the label**: concept label (choice_text) is a scored CANDIDATE alongside the definitional
  predicates. The label-only candidate reduces to FLOOR, so the refined match strictly generalizes floor.
- **R2 specificity weighting**: tie-pool IDF over the filler distribution across the n=128 tie set.
  dfc(w) = # of (unit,choice) profile-bags (label words + predicate-object words) containing content-word w;
  idf(w) = log((1+N_bags)/(1+dfc(w))). Generic hubs (water/energy/object/push -> high dfc) get LOW idf and
  cannot dominate. Answer-agnostic (never uses correct_index). Glass-box: up/down-weighted tokens reported.
- **R3 non-lossy monotone aggregation**: per candidate discriminating-score = specificity(pred) *
  relevance(pred, stem); BEST candidate decides (max). Generic hubs suppressed by low specificity -> adding
  MORE true facts only adds MORE discriminating candidates -> oracle (more facts) >= auto. Two backends:
  GROUNDED (specificity*cosine, encoder held CONSTANT vs GloVe arms = structure is the one var) and SYMBOLIC
  (GloVe-free rarity-weighted lexical overlap = sum idf over content(pred) INTERSECT content(stem)).

## Reuse UNCHANGED (VET-cleared, leak-free)
Arms + n=128 tie pool + FLOOR + GLOBAL-scramble + positive control, imported from powered_v1 (build_pool,
mcnemar) + v1 (decide_by_meaning, retrieval, autonomous loop, scramble) + defmatch_v1 (build_def_profile
trust-gate glass-box recover, grounded_align, _content_set, _heldout_side). Reused ARM0/FLOOR/ARM1(GloVe
oracle)/ARM2(GloVe auto)/ARM3within/ARM3global replicate powered's EXACT rng draw order (refined arms use a
SEPARATE rng that never perturbs the reused grng).

## Arms
- REUSED (positive control): arm0_legacy_combiner, floor_mm_no_facts, arm1_oracle_ceiling,
  arm2_autonomous_loop, arm3_scramble_within, arm3_scramble_global.
- NEW refined (label + tie-pool IDF + specificity*relevance monotone-max):
  - rdef_oracle_grounded  -- refined grounded over ORACLE facts (ceiling + oracle>=auto sanity).
  - rdef_auto_grounded    -- refined grounded over AUTONOMOUS facts (PRIMARY decisive arm).
  - rdef_scramble_grounded-- refined grounded over GLOBALLY-SCRAMBLED facts (MUST-FAIL control for auto).
  - rdef_auto_symbolic    -- refined SYMBOLIC (GloVe-free) over AUTONOMOUS facts (companion).
  - rdef_scramble_symbolic-- refined SYMBOLIC over scrambled facts (MUST-FAIL for symbolic).
  (label included in ALL refined arms, so rdef_auto vs rdef_scr isolates the incremental value of TRUE
  definitional STRUCTURE over-and-above the label -- the honest must-fail control.)

## HARD CAN-FAIL BANDS (pre-registered BEFORE the run; DECISIVE gate = CHALLENGE split, n=44)
- **PRIMARY GATE** = per-split (Challenge) paired McNemar rdef_auto_grounded vs rdef_scramble_grounded:
  `p_exact < 0.05 AND acc(rdef_auto|challenge) > acc(rdef_scr|challenge)`.
- **HARD_PASS** = primary gate passes AND guardrails ok => definitional grounding REAL, greenlight build B.
- **HONEST_NEG** = Challenge rdef_auto does NOT beat scramble (collapses) => definitional/taxonomic grounding
  genuinely dead, B DISCONFIRMED, route to a different grounding. DECISIVE: saves the B investment.
- **MIDDLE_BAND** = lift on FULL pool or EASY but Challenge collapses (not decisive), OR Challenge significant
  in the WRONG direction (rdef_auto < rdef_scr significantly; investigate). Per META_RULE_L, marginal/at-floor
  is MIDDLE_BAND not HARD_PASS.
- Guardrails (required for HARD_PASS): gold_only preserved @1.00; positive control reproduces powered EXACT
  (n_pool=128, arm0=48, floor=51, arm1=68, arm2=60, arm3global=47) MEASURED@
  data/exp_intrinsic_foundation_loop_tie_gaps_powered_v1/metrics.json.

## Also reported (informative)
- Per-split (Challenge AND Easy) McNemar: rdef_auto vs scramble, vs GloVe ARM2, vs GloVe ARM1; symbolic
  companion vs its scramble.
- oracle>=auto sanity (R3 lossy-scoring fixed?) FULL + per-split.
- IDF glass-box: top-20 down-weighted (generic hubs) + top-20 up-weighted (discriminators) with dfc.
- Per-arity, per-mode, per-heldout-concept breakdowns; coverage preflight (thin_flag if cov_gold < 0.5).
- FEED B: per-concept role-slot profiles + deterministic sha256 held-out split.

## Discriminator-fires (SCALE)
FULL is at the canonical n=128 pool (no smoke-vs-full scale gap). Self-test plants a discriminator with a
generic hub ('water') present in BOTH choices and a rare discriminator ('dissolved solute') in gold only,
and asserts: (a) refined match CAN-FIRE (grounded + symbolic pick gold), (b) CAN-FAIL (scrambled predicate
does NOT pick gold), (c) tie-pool IDF down-weights the hub below the discriminators (R2), (d) gold_only
single-valid returned unchanged. Baseline-in-band: the tie pool is genuine ties (arm0=0.375, GloVe arms
0.47-0.53, scramble ~0.37-0.40) -- squarely in the discriminating band, no saturation.

## Anti-leak
Acquisition answer-agnostic (retrieval keyed on choice text, not the answer). Tie-pool IDF built from
objects/labels only (never correct_index). Refined match uses stem + profile + label, never the answer.
correct_index only enters the tally + the decision-independent sha256 held-out split. HELD-OUT ARC test
sets; rules not derived from test labels.

## Cell-template mandates (satisfied)
- except SystemExit raised BEFORE except Exception (no bare/BaseException).
- Atomic metrics (tmp + os.replace); start-marker; crash-diagnostic; heartbeat jsonl; progress prints flush=True.
- arms_differ: refined arms score by distinct backends/fact-sets; positive-control reused arms reproduce
  powered EXACT (a strong same-object identity check).
- final_metrics_atomicity: tmp_replace.
- deterministic_seeding: fixed SEED, numpy default_rng, sorted iteration, sha256 (NOT python hash()); refined
  scramble rng is SEPARATE from the reused grng.
- real_code_path: self-test constructs the REAL HDFactStore + real acquisition index + reused imports.
- calibration_check: default_ok_for_this_regime (reuses VET-cleared pool + arms; only the match scoring changes).
- progress_logging: line-flushed heartbeat + per-20-unit progress.

VET-PENDING; skunkworks owns landed-VET. LOCAL-only; no atom banking; no push/remote-persist.
