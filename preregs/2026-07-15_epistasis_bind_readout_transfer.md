# Pre-registration: epistasis non-additive cluster -> STRONG gate -> symmetric-bind transfer proof (2026-07-15)

Author: hdi_exp_dev. Fixed BEFORE running. Revival of the chem_bind_readout REFUTE per skunkworks VET a2f9a9e8:
the mechanism is HEALTHY (on ARBITRARY-seen pure-nonadditive labels SYM=1.000 vs ADD=0.830); the prior REFUTE was a
DATA/foundation gate (chem SDS mixing-hazard is ~98% main-effects vs a STRONG categorical additive, +0.022 non-additivity).
This cell re-runs the transfer proof on a GENUINE-interaction pocket gated against a STRONG capacity-matched CATEGORICAL
additive. Two foundation fixes (both required): (1) STRONG non-additivity gate = multinomial-logistic-on-counts categorical
additive (NOT weak ordinal-lstsq); (2) genuine-interaction pocket = genetic EPISTASIS / synthetic lethality (pure AND-gate),
stronger generator (claude-sonnet-4-5, not haiku).

## Prior-work check
`tools/substrate_query.sh "epistasis synthetic lethality genetic interaction non-additive symmetric bind readout"`:
NONE at cosine>0.30 (top hit 0.3047 = wordnet token 'genetic', not a prior arc cell). Genuinely novel pocket.

## Pocket / data
- Entity = a real named gene PAIR. Constituent = functional pathway CLASS of each gene (categorical, canonical-sorted
  unordered pair). 12 classes: dna_repair_hr, dna_repair_nhej, dna_repair_ber_parp, dna_repair_mmr, dna_repair_ner,
  dna_damage_checkpoint, cell_cycle_core, chromatin_remodeling, spindle_mitosis, proteostasis_autophagy,
  metabolism_general, signaling_growth.
- Held-out TARGET = negative genetic-interaction SEVERITY of the double perturbation, 5 ordinal-flavored CATEGORICAL
  levels: none / mild / moderate / severe / lethal. (Positive/suppressive epistasis EXCLUDED to keep the scale a clean
  negative-interaction severity and reduce adjacent-level vet noise.)
- Why genuinely non-additive vs a strong categorical additive: with FINE-GRAINED repair sub-pathway classes,
  "count of DNA-repair genes" is NOT a usable additive feature -- HR+NHEJ (redundant DSB repair) -> lethal while HR+MMR
  (different lesions) -> none, both "2 DNA-repair genes". Outcome is determined by the class-PAIR redundancy relationship,
  not per-class main effects. Single-KO is viable by construction (SL screen) -> per-class marginal is weak.
- Generation = build-time-local (claude-sonnet-4-5 generate + adversarial-vet). Measurement = glass-box CPU, NO LLM.

## Compute architecture
(b) sequential-CPU with justification: arena ~120-150 real pairs x NCLS=12; per-seed work is a handful of tiny (<=150x32)
Adam fits (ms) + numpy softmax-regression (ms). Total wall < 90s over 10 seeds. GPU batching yields no speedup on
sub-ms matmuls. Storage strategy: no_storage / no_composition-chaining (single-hop readout). torch thread-capped
(HDI_TORCH_THREADS default 2). Determinism: ALL RNG from FIXED integer seeds + stable sorted-unique class-pair ids +
stable enumerated regime indices; NO Python hash(), NO list(set()) ordering (PROT-023; queue_add static scan enforces).
ASCII-only; no bare except; except SystemExit before except Exception; atomic tmp+os.replace metrics write.

## The STRONG categorical additive (Fix 1)
`arm_additive_cat` = multinomial logistic regression (softmax) on the per-class COUNT design (NCLS+1 features -> L classes),
deterministic full-batch GD (zero init, no RNG). This is the STRONGEST main-effects-only CATEGORICAL additive (no ordinal
assumption, no round-to-bin loss). The strong additive bar = max(ordinal-lstsq, multinomial-logistic). A genuinely
non-additive cluster must beat BOTH.

## STEP 1: generation truth gate (build-time)
- truth_rate (adversarial vet, sonnet) >= 0.85. If below -> generation REFUTE (generator cannot produce vettable epistasis
  at bar). This was the OTHER gap last time (haiku 0.833 < 0.85); sonnet + crisp level anchors targets >= 0.85.

## STEP 2: STRONG non-additivity gate (generation cell `--run`; glass-box; >=5 seeds, default 10)
Fixed bands:
- STRONG_NONADD_HP: interactive_seen - max(add_lstsq_seen, add_cat_seen) >= 0.12  (STRONG bar; the load-bearing fix)
- dominance_ratio = best_single_mi / joint_mi <= 0.60
- mi_margin = joint_mi - best_single_mi >= 0.30 bits
- Discriminator-valid: ADDITIVE_SYNTH control non-additivity (vs SAME strong additive) <= 0.10 AND
  clean_nonadd > addsynth_nonadd + 0.05 AND SHUFFLE destroys (clean > shuffle + 0.05); oracle_ceiling = 1.0.
- HARD_PASS_STEP2 (cluster is genuinely non-additive vs strong baseline) = truth_ok & conj_present & STRONG_NONADD_HP &
  discriminator-valid & ceiling.
- REFUTE_STEP2 (DEEP NEGATIVE: even a genuine pocket is main-effects-capturable, OR single class dominates, OR generator
  cannot vet) = (truth<0.85) OR (dominance_ratio>0.80) OR (strong_nonadd <= 0.05). Trusted iff discriminator-valid+ceiling.
  This is a valuable finding about the FOUNDATION; if it fires, DO NOT dispatch the transfer proof.
- MIDDLE_STEP2 = else.

## STEP 3: transfer proof (transfer cell; SYM vs capacity-matched additive; >=5 seeds, default 10)
Arms: LEARN_SYM (shared per-class code + elementwise PRODUCT = substrate symmetric bind; WINNER hypothesis) ;
LEARN_ADD (shared code + SUM; capacity-matched LEARNED categorical additive) ; ADD_MULTINOM (softmax-on-counts strong
categorical additive) ; ADD_LSTSQ (ordinal closed-form) ; LEARN_ROLE (role-keyed product; algebra contrast) ;
HOMOPHILY ; MEMORIZE ; POP ; ORACLE(ceiling) ; FREQ_NULL=max(HOMOPHILY,POP). strong_additive = max(LEARN_ADD, ADD_MULTINOM,
ADD_LSTSQ). Strata on held-out pairs: SEEN class-pair (PRIMARY) / NOVEL class-pair (STRETCH). Regimes: CLEAN /
ARBITRARY (random label per unique class-pair; must-fail on NOVEL) / SHUFFLE (label permutation; must-fail on ALL).

PRIMARY (SEEN, CLEAN, multi-seed mean):
- LEARN_SYM_seen - max(strong_additive_seen) >= 0.10
- AND LEARN_SYM_seen - FREQ_seen >= 0.10  AND  LEARN_SYM_seen - chance >= 0.15
ALGEBRA: LEARN_SYM_seen >= LEARN_ROLE_seen - 0.05 (symmetric not beaten by role-keyed on symmetric target).
MUST-FAILS: SHUFFLE (SYM_all - FREQ_all) <= 0.12 AND ARBITRARY (SYM_novel - FREQ_novel) <= 0.12 ; oracle=1.0 ; leak_ok.
STRETCH (NOVEL): LEARN_SYM_novel - max(strong_additive_novel) >= 0.08 -> suffix _NOVEL_GENERALIZES.
- HARD_PASS_TRANSFER = PRIMARY & algebra & must-fails & oracle & leak (the learned symmetric bind READS the real
  non-additive conjunction on held-out pairs, beating a capacity-matched categorical additive + freq).
- REFUTE_NO_TRANSFER = LEARN_SYM_seen - max(strong_additive_seen) <= 0.03 (mechanism does NOT read the real conjunction
  even in-distribution). Trusted iff must-fails fire + oracle=1.0.
- MIDDLE_BAND = else (partial margins / role beats sym).

## OVERALL LINCHPIN VERDICT
- HARD_PASS (linchpin proven): HARD_PASS_STEP2 AND HARD_PASS_TRANSFER. A genuine pocket clears the STRONG non-additivity
  gate AND the learned symmetric product bind BEATS a capacity-matched categorical additive + freq on held-out pairs.
- REFUTE_FOUNDATION (deep negative): REFUTE_STEP2 fires -> pocket main-effects-dominated / not vettable at bar; transfer
  not dispatched. Honest finding about the FOUNDATION.
- REFUTE_MECHANISM (drill-worthy, contradicts VET): HARD_PASS_STEP2 but REFUTE_NO_TRANSFER.
- MIDDLE: partial.

## Self-test floors (both cells; on REAL bind path + guard-vs-arena-floor + planted discriminators)
Generation cell: interaction plant gate FIRES vs strong additive (nonadd_i >= STRONG_NONADD_HP; int>add strictly);
additive plant gate does NOT fire (nonadd_a <= 0.10); shuffle destroys; separation margins hold; oracle=1.0; enough_seen>=8.
Transfer cell: FHRR-bind homomorphism (real substrate hd_bind); hadamard==complex-bind-real; SYM beats strong-additive on
interaction plant seen >= 0.12; SYM beats FREQ >= 0.10; role not beating sym; product NOT spurious on additive plant <= 0.10;
shuffle must-fail fires; oracle=1.0; guard-floor valid (freq>=pop>0.05); arms-differ on REAL data; real_code_path exercised;
determinism; enough_seen>=8.

## META_RULE schema-vet
arms_differ_verified (AF); final_metrics_atomicity=tmp_replace (AH); except SystemExit before except Exception (no
BaseException); crlb_n/a="accuracy discriminator over categorical readout; no closed-form noise floor -- feasibility set
by planted-arena preview in self-test"; baseline_in_band checked at smoke (0.05<additive<0.95); discriminator survives
scale (self-test planted arena at n=600 fires the SYM-beats-strong-additive gap >= transfer HARD_PASS margin);
HARD_PASS strictly above floor +5% (L); HP_SCOPE: gates apply to LEARN_SYM vs additive arms only, not POP/HOM sentinels;
calibration_check="default_ok_for_this_regime" (real-data readout, adaptive-none); PROT-023 static scan clean.
