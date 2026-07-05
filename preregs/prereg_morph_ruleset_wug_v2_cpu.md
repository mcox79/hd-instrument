# Pre-reg: full English inflectional-morphology ruleset (WUG width extension) v2 -- CPU

- Cell: `experiments/exp_morph_ruleset_wug_v2_cpu.py`
- Anchor: `morph_ruleset_wug_v2_cpu`
- Metrics: `data/exp_morph_ruleset_wug_v2_cpu/metrics.json`
- Extends: `exp_lex_wug_test_cpu_v1` (HARD_PASS; ONE rule present->past, novel-stem gen
  1.000 MEASURED@data/exp_lex_wug_test_cpu_v1/metrics.json:per_seed[0].reg_3shot)
- Date: 2026-07-05. Author: hdi_exp_dev. Handoff: `notes/exp_dev_handoff_research_language_ingest_glassbox_scoping_2026-07-05.md` ANCHOR_2.
- Prior-work check: NONE at cosine>0.30 that is a prior morphology CELL arc. Substrate-KB top hits are WordNet
  lexical atoms (`inflectional_morphology` 0.368, `pluralization` 0.323, `generalization` 0.323) + one code-transfer
  methodology note (0.322) -- no competing morphology cell. Genuine width extension of the one prior WUG cell.

## HONEST SCOPE (USER-LOCKED framing; over-claim guard is a HARD-FAIL condition below)
STRUCTURED, rule-based word-form inflection -- an inspectable glass-box language LAYER. NOT fluent language, NOT
"speaking", NOT the capstone. The claim is: the substrate produces plurals / past tense / -ing / etc. from stems via
literal algebraic transforms it can print, selects the right allomorph by phonological class, and overrides regular
rules with a memorized exception list (dual-route, Pinker/Prince 1988). Telegraphic, synthetic stems, no syntax.

## Question
Does the width-1 WUG mechanism (infer an algebraic inflection transform from a few example pairs, apply to a NOVEL
stem) extend from 1 rule to the field's own count of the 8 core English productive inflectional rules (CITED@ exactly
8, research note Section 1 Layer B), including (a) the 3 allomorph-conditioned rules (plural -s, 3rd-sing -s, past -ed;
allomorphs /s,z,Iz/ and /t,d,Id/) and (b) a ~150-200-entry irregular exception list (CITED@Pinker 1999 Words and
Rules: 160-180 irregular verbs)?

## Mechanism (FHRR N=8192 complex phasor; bind=elementwise mul, unbind=mul by conj, cleanup=argmax Re inner-prod)
Citation form base[s] = stem[s] (X) BASE. Inflection surf[s] = stem[s] (X) TAG_rule. Rule R = TAG_rule (X) conj(BASE)
inferred by averaging a few (base,surface) pairs, applied to novel stems. Allomorphic rules: surf[s] =
stem[s] (X) ALLO[c(s)] with class c(s) in {voiceless,voiced,sibilant}; a CONDITIONED mechanism infers one transform
per (rule,class) and selects by perceived class. Irregulars: an associative-memory gate (cosine retrieval over an
exception codebook) overrides the regular rule with a memorized arbitrary surface for listed stems.

## Arms (per rule, over NOVEL stems -- never-shown)
- `conditioned`   : per-class transform (allomorphic) / single transform (simple). [MECHANISM / DELIVERABLE]
- `naive_single`  : ONE transform per rule regardless of class. [DISCRIMINATOR-allomorphy: collapses on allo rules]
- `scrambled`     : transform inferred from cyclic-shift-DERANGED (base,surface) correspondences. [DISCRIMINATOR-no-rule]
Irregular test: `dual_route` (exception-lookup then rule) vs `regular_only` (over-regularization). [DISCRIMINATOR-exception]
Primary per-rule metric = novel-stem SURFACE-form production accuracy (argmax over candidate codebook): for
allomorphic rules the candidate set is the 3 allomorph realizations of that stem (correct = c(s), chance=0.333); for
simple rules it is the correct surface + 7 distractor-stem surfaces (chance=0.125).

## Grid / cardinality
Rules=8 (3 allomorphic + 5 simple). Arms per rule: conditioned+scrambled (all 8) + naive_single (allomorphic).
FULL: TR=40 trials/rule x 3 seeds (7,13,19); NIRREG=180. `EXPECTED_N_UNITS = 8 rules x 40 trials x 3 seeds = 960`
rule-trial units + 3 irregular blocks. `cardinality_ok` gate: per-rule aggregation asserts all 8 rules present across
all 3 seeds; verdict HARD_FAIL if any rule/seed missing. SMOKE: TR=6, 1 seed (7), NIRREG=24 (N held at FULL 8192).

## Bands (envelope-fail-bands; gates on conditioned per-rule + irregular dual_route + discriminator collapse)
- HARD_PASS: all 8 conditioned rules novel-stem surface acc >= 0.90 AND irregular dual_route >= 0.90 AND all three
  discriminators fire (naive_single <= 0.55 on allomorphic rules, scrambled <= 0.55 on every rule, regular_only <= 0.30
  on irregulars). Cross-seed cv reported per rule. MEASURED (smoke, FULL N=8192): all 8 conditioned=1.000, dual_route
  =1.000, naive_allo=0.317/0.346/0.320, scrambled<=0.36 all rules, regular_only=0.000. Strictly-above-floor
  (META_RULE_L): floor 0.90, band from HF=0.60 width 0.30, +5%=0.615; 0.90 well above; measured 1.000 >> 0.90.
- HARD_FAIL: any conditioned rule < 0.60 (research band -- would mean the WUG HARD_PASS was rule-specific, a genuine
  useful negative) OR dual_route < 0.60 (exceptions not handled) OR any discriminator does NOT collapse (test vacuous).
- HARD_FAIL (over-claim guard, applies regardless of numeric result): representing a pass as "the substrate speaks
  English" / "language solved". The honest scope is rule-based synthetic-stem inflection, an inspectable layer.
- MIDDLE_BAND: >=5 of 8 rules clear 0.90 but not all, OR dual_route in [0.60,0.90), OR any conditioned rule in
  [0.60,0.90) -- diagnostic of which rule classes need richer transforms, not a wall.

## Discriminator-fires gates (ALL modes incl smoke; META_RULE_K) -- smoke BLOCKS dispatch if any fails
1. naive single-transform COLLAPSES on the 3 allomorphic rules (<=0.55; chance 0.333) -- proves allomorphy needs
   conditioned structure, so the 8-rule pass is NOT by-construction trivial. MEASURED 0.317/0.346/0.320.
2. scrambled no-rule control COLLAPSES on every rule (<=0.55) -- proves the rule is learned from correct
   correspondences, not by construction. MEASURED <=0.36 (allomorphic 3-cand), <=0.21 (simple 8-cand).
3. regular_only OVER-REGULARIZES on irregulars (<=0.30) while dual_route holds (>=0.90) -- proves the exception list
   is load-bearing (emits "went" not "goed"). MEASURED regular_only=0.000, dual_route=1.000.
Smoke ran ALL THREE at FULL N=8192 (reduces trials/seeds/NIRREG only); all fired. The `main()` smoke gate writes
`smoke_block` and BLOCK_DISPATCH_META_RULE_K if any control fails to collapse.

## SCHEMA-VET mandatory fields
- `cardinality_ok`: true (per-rule x per-seed aggregation gate).
- `final_metrics_atomicity`: tmp_replace (metrics.json.tmp -> os.replace; then write_metrics idempotent re-write).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; grep-gate clean, verified).
- `crlb_n_a`: "Discriminator is an argmax over a SMALL candidate codebook (3 near-orthogonal allomorph phasors, or
  8 stem surfaces) with a clean unbind, not a superposition-noise readout. Conditioned pred == true surface EXACTLY
  (stem factor cancels on unbind); a miss requires a candidate collision, not a noise-floor event. Failure modes are
  STRUCTURAL and N-independent: naive averages 3 near-orthogonal tags -> centroid equidistant -> chance; scrambled
  averages mismatched-stem products -> ~0 transform -> chance; regular_only emits a distractor in the candidate set.
  No Cramer-Rao argmax-noise floor gates the deliverable."
- `baseline_in_band` (META_RULE_AG): the DISCRIMINATING arms are the low-side controls (naive_allo ~0.33, scrambled
  0.006-0.36, regular_only 0.0) -- all in (0.0,0.55), NOT saturated. conditioned ~1.0 is the POSITIVE control
  (simple English inflection IS easy; the gap vs the failing control is the signal). Positive-control saturation is
  intentional and paired with a collapsing negative control, per the standard AG-satisfying design.
- `arms_differ_verified` (META_RULE_AF): conditioned/naive/scrambled prediction arrays for plural_s (trial 0) are
  hash-distinct (three genuinely different transforms). MEASURED arms_differ_verified=True.
- `discriminator_survives_scale`: (A) smoke runs every discriminator AT full N=8192 (reduces trials/seeds/NIRREG
  only) + (B) analytical: the three collapses are structural, N-independent (see crlb_n_a). MEASURED at N=8192 smoke.
- `HP_SCOPE`: {conditioned: [HP_rule_floor_0.90, cv], dual_route: [HP_irreg_0.90], naive_single: [disc_collapse_allo],
  scrambled: [disc_collapse_all], regular_only: [over_regularize_<=0.30]}. The 0.90 mechanism floor applies ONLY to
  conditioned + dual_route; the control arms carry collapse gates, not the mechanism floor.
- `calibration_check`: default_ok_for_this_regime. Allomorph tags and stems are iid random phasors (clean synthetic
  regime, matching the predecessor WUG cell exactly); no distribution-fit tuning. IRREG_THRESH=0.5 cleanly separates
  self-cosine 1.0 from non-member ~1/sqrt(2N)~0.008 (MEASURED gate_sep=0.964); not tuned for pass.

## §15 composition/sweep gates
- `sweep_alignment_verdict`: ALIGNED. The "sweep axis" is the 8 rules (not a numeric parameter). Each rule's
  conditioned arm experiences exactly the tag(s) it is meant to learn; allomorphic rules experience 3 class-tags, the
  conditioned mechanism sees each class in its shown examples. No nominal-vs-effective mismatch.
- `discriminating_fraction`: the allomorphic rules (3/8) put naive_single squarely in the discriminating band (0.33)
  vs conditioned 1.0; every rule (8/8) puts scrambled in the discriminating band. Irregular test puts regular_only at
  0.0 vs dual_route 1.0. This is the opposite of by-construction saturation: each rule has a failing control.
- `composition_edges`: (1) base -[infer transform]-> R (SHAPE_MATCH: both phasor N-vectors); (2) base (X) R -> pred
  surface (SHAPE_MATCH: bind); (3) stem -[cosine gate]-> exception codebook -> memorized surface (SHAPE_MATCH:
  retrieval over unit phasors). No SHAPE_MISMATCH.
- `positive_control_arms`: conditioned reproduces the predecessor WUG single-rule result (novel-stem gen 1.000) AT the
  test regime for the analog of the present->past transform (stem_recovery metric = 1.000 MEASURED across all 8 rules,
  matching MEASURED@data/exp_lex_wug_test_cpu_v1/metrics.json:per_seed[0].reg_3shot=1.000). Regime-extension audit:
  SHAPE_MATCH (same FHRR bind/unbind algebra, same N=8192, same synthetic-phasor stems as the predecessor).
- `functional_requirements`: (1) inflect a novel stem by a rule -> WUG algebraic transform (predecessor CG); (2)
  select the right allomorph by phonological class -> conditioned per-class transforms + class-cued selection; (3)
  override the rule for listed exceptions -> associative-memory retrieval gate (dual-route); (4) prove the pass is a
  real mechanism -> naive/scrambled/regular_only collapsing controls.

## Formula self-test (--self-test; halts before any full run)
On a tiny fixed regime (N=4096, 30 stems, NIRREG=20) asserts the algebra: conditioned allomorphic >= 0.95 AND naive
allomorphic <= 0.60 (collapse); conditioned simple >= 0.95 AND scrambled simple <= 0.40 (collapse); dual_route >= 0.95
AND regular_only <= 0.10 (over-regularization); exception gate separation > 0.4. MEASURED@self-test: cond_allo=1.000
naive_allo=0.333 cond_simple=1.000 scram_simple=0.000 dual=1.000 reg_only=0.000 gate_sep=0.972.

## Compute architecture
- Class (b) sequential-CPU with justification: reuses the predecessor WUG cell's proven CPU FHRR pipeline (v1 FULL=12s
  CPU); task mandates CPU-local (no LLM/GPU); cleanup is BLAS-vectorized (cand @ conj(pred)); the only Python loops are
  over rules/trials/novel-stems (cheap). Largest cost is the 3 allomorphic rules x 3 arms; MEASURED smoke (1 seed, 6
  trials, N=8192) = 36.3s. No matmul-in-python-loop scaling.
- Storage strategy: no_composition_bundling. Each stem/tag is its own vector; inflections are single binds; the
  exception codebook is a sharded set (each irregular its own vector). No superposition interference.
- `progress_logging`: print_flush_true (line_buffered stdout + per-unit progress print + per-unit _heartbeat.jsonl +
  _start_marker.json at main() entry + CELL_CRASHED crash-diagnostic on Exception).
- `cell_chunked`: false. Justification: fast deterministic CPU cell (full estimate ~12 min for all 3 seeds); multi-seed
  handled by an internal seed loop with per-seed prints + heartbeat + start-marker + atomic crash-diagnostic. Runner
  death re-runs cheaply; no per-seed matmul zombie risk (numpy CPU, no GPU allocation). Multi-seed cv reported.

## Dispatch
- SMOKE: LOCAL, run directly (--smoke) as the pre-flight gate. MEASURED HARD_PASS at FULL N=8192, elapsed 36.3s,
  smoke_block=None, arms_differ_verified=True, all 3 discriminators fired.
- FULL: STAGE for remote (remote_cpu_queue via orchestrator; push needed, harness-denied to exp_dev). Recommended
  `--timeout 1800`. Timeout formula (per queue_add.sh): ceil(1.5 * smoke_wall * (FULL_units/smoke_units)) =
  ceil(1.5 * 36.3 * (960/48)) = ceil(1089) = 1090s; rounded UP to 1800s for slower remote CPU margin (~2.5x).
  timeout_s=1800 crosses the §17 threshold, satisfied by progress_logging=print_flush_true. run_mode must land `full`
  (verify §16: expect size > 5KB, elapsed > 60s, run_mode=full, NIRREG=180).
