# Pre-reg: agreement_attractor_role_binding_cg_viability_v1

TWO-STAGE VIABILITY PROBE (design-gated, can-fail). First real-text compositional-generalization
(chain-grade) shot in the program: can the glass-box substrate LEARN subject-verb agreement ACROSS AN
ATTRACTOR -- discover from labeled examples on RAW token structure that predictive weight belongs on the
syntactic-HEAD noun (subject), not the linearly-NEAREST noun -- without being handed a parse?

- Cell: `experiments/exp_agreement_attractor_role_binding_cg_viability_v1.py`
- Prep:  `tools/prep_agreement_probe_cache.py` -> `data/corpora/agreement/agreement_probe_cache_v1.json.gz`
- Governing drill: `notes/research_drill_agreement_attractor_real_text_CG_bar_scoping_2026-07-22.md`
- Reuses role-binding + glass-box-readout + must-fail-control machinery from atom 29441
  (`exp_relational_vs_similarity_conflict_viability_probe_v1.py`).

## Prior-work check (substrate KB)
`substrate_query.sh "subject verb agreement attractor syntactic head number learn real text
compositional generalization"` -> top hit "Compositional generalization" cosine=0.3975
(notes/wave14e_hierarchical_composition_research.md), "Compositional generalization context" 0.3896,
prereg substrate_compositional_generalization_CORRECTED_v1 0.3584. These are GENERIC CG notes (SCAN/
skill-composition/synthetic-KG); NONE is subject-verb agreement-attraction or real-text agreement.
Verdict: this cell is GENUINELY NOVEL in the arc (first real-text agreement-attraction probe); the
prior CG notes are adjacent framing, not a rediscovery.

## Data (real text, public)
- PRIMARY: Linzen, Dupoux & Goldberg 2016 Wikipedia agreement corpus (agr_50_mostcommon_10K; fetched
  from the paper's public Dropbox). 14,761-item balanced subset across attractor bins 0-4 (label
  `verb_pos`: VBP plural=1 / VBZ singular=0; attractor count = `n_diff_intervening`).
- CROSS-CHECK: Gulordava et al 2018 English nonce (github facebookresearch/colorlessgreenRNNs), 410
  constructions -> optional FROZEN-readout transfer arm (POS-tagged via hdlab.pos_tagger; graceful defer
  if unavailable). NOTE: the substrate encoding is LEXEME-FREE by construction, so lexical-memorization
  is architecturally excluded regardless of the nonce arm.
- Data is local-only (631MB corpus); the cell reads the SMALL committed cache (0.14 MB) so it is
  reproducible on any runner. CITED@ the two public repos above.

## Fairness design (USER-directed; a violation voids the result)
TAUGHT-then-GENERALIZE. FAIR to TEACH the role/position-binding scaffold + raw-token-derivable HINTS
(position ranks + preceding function-word class per noun -- all in the raw input, NOT a parse). What
must be the SUBSTRATE'S OWN is the learned WEIGHTING that GENERALIZES to held-out items; we never
hand-install "the subject is noun k". Held-out by NOVEL subject lexeme (disjoint pools).

## Stages
- STAGE 1 (representability, gate): the whole prefix's noun-number map is held in ONE HRR superposition
  S (brain-faithful cue-based content-addressable WM, Wagers/Lau/Phillips 2009). GIVEN the ORACLE
  subject position, unbind its role and read the number. Gate: oracle-read acc >= 0.90 (else
  REPRESENTABILITY_FAIL_REDESIGN; a downstream learning failure would be a rigged-encoding artifact).
  MEASURED@smoke: 1.0 at N_DIM=2048.
- STAGE 2 (learnability): NO oracle. A glass-box logistic readout reads the substrate's own role-slots
  (unbind -> signed number score per RV/RS/FW slot) and must DISCOVER the head-tracking weighting from
  labels alone. Inspectable weights.

## Baselines (SAME raw structural input; computed directly, NOT via substrate)
- B_nearest (nearest-noun-number): standard surface baseline. On the label-balanced attractor subset the
  nearest noun is ~always the attractor -> BELOW chance (this corpus makes the surface heuristic actively
  wrong). MEASURED@smoke conflict-subset near=0.0.
- B_first (first-noun-number): STRONGER positional heuristic here (subjects sit early); beating
  nearest-noun is trivial, so the HONEST bar is beating first-noun on the subject-NOT-first (SNF) subset.
- B_major (majority/frequency), B_bagcount (net plural-vs-singular noun count), B_anynoun (permissive OR
  loophole check).

## Discriminator (primary, can-fail) + must-fail controls
- HEAD-TRACKING discriminator = substrate_SNF_acc - max(first, majority, bagcount)_SNF on the held-out
  subject-not-first subset. `HEADTRACK_MARGIN >= 0.10`.
- STRUCTURE-SHUFFLE must-fail: same encoder, each sentence's number<->slot associations permuted (counts
  preserved). `structure_used` iff substrate_SNF - structshuffle_SNF >= 0.10 -> proves the win comes from
  POSITION/function-word STRUCTURE not noun COUNTS.
- Attribution: clean-features ablation (crosstalk cost) + kNN-on-substrate-features (representation vs
  learner).

## Pre-registered bands
- REPRESENTABILITY_FAIL_REDESIGN: Stage-1 oracle-read < 0.90.
- HARD_PASS_LEARNED_HEADTRACK (GREEN-LIGHT-PENDING-VET): Stage-1 passes AND headtrack_win (SNF beats
  strongest non-structural base by >=0.10) AND conflict_win (beats majority by >=0.15 on conflict subset,
  and beats nearest) AND structure_used (beats structure-shuffle on SNF by >=0.10) AND bin4 acc >= 0.55
  (degradation above chance at 4 attractors) AND arms_differ AND weights_nondeg.
- HARD_FAIL_NO_LEARNED_STRUCTURE: substrate barely beats majority (<0.05) OR does not beat nearest on the
  conflict subset OR arms bit-identical.
- MIDDLE_BAND_POSITIONAL_OR_COUNT_HEURISTIC: beats nearest/frequency in aggregate but does NOT clear the
  SNF head-tracking bar and/or the structure-shuffle control -> reduces to a positional/count heuristic
  (a well-specified negative: a real CG needs a structure-induction capability beyond fixed
  position/function-word weighting on a bound superposition).
- CALIBRATION: a modest human-comparable residual (5-20%) on the hardest condition is BRAIN-FAITHFUL,
  part of PASS, not a disqualifier (Staub 2009; Wagers 2009 cue-based retrieval).

## Design-gate (verified at smoke)
- REAL baseline: yes (5 clean baselines on identical raw input).
- Discriminator CAN-FAIL: yes -- MEASURED@smoke headtrack_win=False, structure_used=False -> MIDDLE
  (not saturated). Discriminator FIRES (controls collapse; structure-shuffle separates counts from
  structure).
- DIFFICULTY ON: results binned by attractor count 0-4; conflict subset (nearest != label).
- ONE variable: mechanism (substrate role-binding readout) vs baselines/controls on identical input.
- baseline_in_band: majority ~0.46-0.62 (0.05<acc<0.95) MEASURED@smoke.

## Compute architecture / schema-vet
- compute_architecture: sequential_cpu, light probe (smoke 11.9s; FULL est <~6 min), no_storage,
  no_composition (single-hop readout). GPU-batching N/A (wall << 10 min; numpy FFT).
- storage_strategy: no_storage / no_composition.
- final_metrics_atomicity: tmp_replace. except SystemExit: raise BEFORE except Exception (no
  BaseException). Bare-except grep: clean. Nondeterminism scan: clean (hashlib + fixed ints; no builtin
  hash/list-set).
- discriminator survives scale: smoke N_DIM=2048 == FULL N_DIM (option A).
- crlb_n/a: real-text head-tracking discrimination; floor = HRR superposition crosstalk (reported as
  Stage-1 oracle-read acc), not an argmax-capacity CRLB.
- cardinality_ok: n_seed_rows == len(seeds).
- real_code_path: self-test asserts the vectorized numpy-FFT bind/unbind == hdlab.binding (real
  primitive) at N=64; F.2/F.3 N/A (no KGStore/fit-module); guard_baseline N/A.
- progress_logging: print_flush_true.
- self-test asserts VALIDITY only (Stage-1 floor, arms_differ, baseline-in-band, runs) -- NOT the
  mechanism outcome (can-fail hypothesis, not asserted).

## Dispatch
- Local SMOKE: PASS (ran clean, discriminator fires) -> MIDDLE at 2 seeds.
- FULL: 3 seeds [7,13,19], train_cap 6000 / test_cap 6000, N_DIM 2048. CPU-light. Cache committed so
  reproducible on remote_cpu_queue. Timeout 1800s.

HONEST FRAMING: a HARD_PASS is a GREEN-LIGHT-PENDING-VET, never a self-declared CG. A HARD_FAIL/MIDDLE is
"THIS mechanism + THESE conditions did not acquire the feature here" (a well-specified negative pointing
at a needed structure-induction capability), never "the substrate cannot". No store write / no push /
no atom bank (Skunkworks owns banking).
