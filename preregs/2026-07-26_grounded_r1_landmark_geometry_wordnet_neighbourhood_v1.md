# Pre-reg: grounded_r1_landmark_geometry_wordnet_neighbourhood_v1

Date: 2026-07-26
Author: hdi_exp_dev
Cell: `experiments/exp_grounded_r1_landmark_geometry_wordnet_neighbourhood_v1.py`
Compute: CPU-only, local (INLINE-LOCAL; no push authorized). No GPU. No network at run time.

## Question (Director contract)
A CONSIDERED PIVOT off the v1->v2->v3 link-prediction encoder arc (plateaued: raw grounding carried the
modest novel-concept signal; the learned objective added only +0.043 over raw grounding; v3 mechanism
regressed; "beats structure" headline was a construction artifact). CHANGE the OBJECTIVE and the TEST:
- OBJECTIVE = R1 teacher-free LANDMARK-anchored graded-geometry (form a semantic manifold where
  concept-to-concept distance is graded by shared-vs-distinct property/relational overlap), NOT in-batch
  contrastive link-prediction.
- TEST = WordNet semantic-neighbourhood generalization on HELD-OUT NEW concepts (independent ground truth).

THE ONE NUMBER THAT MATTERS: does LEARNING add a REAL margin OVER RAW GROUNDING on held-out-NEW concepts?
margin = same_lex_auc(LEARNED) - same_lex_auc(RAW_GROUNDING). If ~0 -> HONEST input-ceiling finding.

## Objective (teacher-free)
Landmark-anchored relational KD: fixed anchor frame of L top-train-degree TRAIN concepts. TARGET geometry
T[c,l] = cosine(rich_feat_c, rich_feat_l), rich_feat = [standardized grounding(20) ++ per-rel-type
mean-pool of train-neighbour grounding]. TEACHER-FREE: target = concepts' OWN property/relational overlap,
no borrowed vector. Encoder f(rich_feat)->code trained so row-centered code-vs-landmark cosine profile S
matches T (smooth-L1) + VICReg variance (anti-collapse).

## Semantic-truth (INDEPENDENT, EVAL-ONLY)
WordNet dominant-synset LEXNAME (supersense; 45 classes) per concept from NLTK. Cached to
`data/wordnet_lexname_cache_v1.json`. NEVER an input nor a training target. Independent of the
ConceptNet/ATOMIC commonsense edges used as input (no /r/IsA / hypernym in the foundation edges).
Coverage MEASURED@probe: 24938/25312 grounded concepts (98.5%) have a lexname; 45 distinct.

## Metric
Primary: SAME-LEXNAME AUC on held-out NEW concepts. Query = held-out concept, gallery = TRAIN concepts;
rank gallery by code-cosine; AUC = P(same-lexname gallery ranks above different-lexname). Base = 0.5
exactly (class-balance-independent) => THEORETICAL@Mann-Whitney base=0.5. Secondary: precision@10,
recall@1, category base-rate (random-retrieval floor).

## Arms
- ARM_LEARNED (PRIMARY): R1 landmark-geometry encoder over rich feature.
- ARM_RAW_GROUNDING: cosine over raw standardized grounding (20d), NO learning. [THE contract baseline]
- ARM_RAW_GROUND_PLUS_CTX: cosine over raw [grounding ++ context], NO learning. [decompose input vs learning]
- ARM_RANDOM_INIT: untrained encoder, SAME input as LEARNED. [isolate learning from arch/input-mixing]
- ARM_COLLAPSE_SHUFFLE: rich input rows permuted across ids, target geo recomputed, trained. [can-fail ~0.5]

## Bands (applied to ARM_LEARNED primary; HP_SCOPE = ARM_LEARNED only)
- HP_LEARNED_SIGNAL = 0.60  HYPOTHESIZED@this prereg (LEARNED must be a genuine held-out signal; prior
  edge-pred enc AUC 0.674 CITED@notes/encoder_rescue... so 0.60 on a related metric is a reasonable floor)
- HF_AUC = 0.53 (below = chance = HARD_FAIL)
- HP_MARGIN_OVER_RAW = 0.03  HYPOTHESIZED@this prereg (THE number: grow the +0.043 prior;
  0.043 CITED@Director contract = prior learning-over-raw-grounding margin on edge-pred)
- COLLAPSE_BAND = (0.44, 0.56) for ARM_COLLAPSE_SHUFFLE (can-fail witness)
- MIN_QUERY_TASKS = 150 (power floor)

## Verdict logic
- can_fail = COLLAPSE_SHUFFLE in [0.44,0.56].
- HARD_PASS = can_fail AND power_ok AND (margin_raw_mean>=0.03 AND margin_raw_min>0) AND learned>=0.60
  AND learned>=random_init.
- HARD_FAIL = (not can_fail) OR learned<0.53 OR (not power_ok).
- else MIDDLE_BAND = LEARNED a real held-out signal + valid controls, but margin over RAW GROUNDING below
  the bar -> the HONEST INPUT-CEILING finding (grounding carries the signal; learning adds ~nothing).
  Reported plainly with `input_ceiling=True`. DEFLATE hard.

## SCHEMA-VET gates
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (no sweep axis).
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
- discriminator-fires (META_RULE_K): discriminator_selftest plants category structure -> struct AUC>=0.85,
  random ~0.5, label-shuffle ~0.5, prec > base_rate+0.2. Gate before any data run.
- baseline_in_band (META_RULE_AG): COLLAPSE_SHUFFLE control must sit ~0.5 (can-fail); LEARNED not
  by-construction saturated (base 0.5, held-out inductive). RAW_GROUNDING measured, expected a real >0.5
  signal (not saturated >0.95: 45-class inductive AUC cannot saturate).
- arms_differ_verified (META_RULE_AF): hash-test over the 5 arm code matrices at run.
- crlb_n/a: AUC discriminator base=0.5 exactly; random-init + collapse controls witness the floor.
- calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; controls witness empirically).
- deterministic_seeding: sha256 concept split + fixed int seeds + sorted(); no hash()/list(set()) (PROT-023).
- real_code_path / substrate_signature: N/A (self-contained jsonl reader + NLTK; no KGStore/fit objects).
- discriminator survives scale: smoke IS a genuine held-out-new-concept WordNet-neighbourhood test at
  cap_nodes=2500; FULL at 5000. No synthetic-only proxy.
- progress_logging: print_flush_true (all _log flush=True; timeout < 30min).

## Compute architecture
Class: (b) sequential-CPU with justification. MLP (feat_dim ~ 20+17*22 ~ 394 -> hidden 256 -> code 128),
train on ~4000 concepts, per-step matmuls [256x394]@... and [256x128]@[128x192]; total FLOPs trivial; GPU
launch overhead dominates; no substrate primitives (bind/bundle/cleanup). Eval = [~1000x128]@[128x4000]
per arm (<1s). Wall-time target < 10 min FULL foreground (INLINE-LOCAL). Storage strategy: no_storage
(no composition; encoder + cosine retrieval). Non-determinism source-scan clean.

## Held-out fraction / leak-proofing
heldout_frac=0.2 (sha256 on concept id). Held-out NEVER a landmark nor a training anchor. Held-out ctx
uses its TRAIN neighbours (input, inductive). WordNet lexname disjoint from every input/target. LOOKUP not
applicable (no per-concept table). COLLAPSE_SHUFFLE is the leak witness.

## Cardinality
EXPECTED_N_UNITS: smoke=2 seeds, full=3 seeds. Verdict enforces len(per_seed)==expected (META_RULE_H).
