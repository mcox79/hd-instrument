# PRE-REG: SCALE meaning-learning from ARC, leak-proof held-out-NEW concepts

- anchor: `scale_meaning_learn_arc_heldout_v1`
- cell: `experiments/exp_scale_meaning_learn_arc_heldout_v1.py`
- date: 2026-07-26
- author: exp_dev (hdi_exp_dev), per Director scale-run green-light
- plan: `notes/scale_corpus_and_data_integrity_plan_2026-07-26.md`
- target queue: `overnight_queue` (GPU: remote RTX 4060 Ti, ~6GB) -- pushed + launched by orchestrator
- compute class: (a) batched-GPU (transformer MLM + concept encode fully batched; AMP on cuda)
- storage strategy: no_composition (no HD store / no bundled composition; this is a learned-encoder cell)

## Question (one line)
Does REAL text experience at scale (ARC, ~240M alpha tokens; median 376 mentions/concept) let a
from-scratch, teacher-free transformer earn concept MEANING that BEATS raw grounding on leak-proof
held-out-NEW concepts -- i.e. does scale break the data-starvation wall the prior 265k-token run hit?

## Hypothesized vs measured numbers
- prior data-starved null: raw_deeptext-alone 0.519; deep-text -0.018 over grounding
  MEASURED@data/exp_deep_text_encoder_self_teacher_heldout_new_v1/metrics.json
- ARC coverage: 237.7M alpha tokens, median 376 mentions/concept, 68.1% concepts >=100 mentions
  CITED@notes/scale_corpus_and_data_integrity_plan_2026-07-26.md (measured this session by research)
- smoke preview (2.4M-token slice, 3.16M trained tokens, d128/2-layer/250 steps, CPU):
  raw_grounding=0.6118, text=0.5047, fused=0.6119, margin=0.0001, collapse=0.4945, popularity=0.5008,
  n_query=242, zero-overlap witness=0
  MEASURED@data/exp_scale_meaning_learn_arc_heldout_v1_smoke/metrics.json
  (text near-chance at the data-STARVED slice = the pre-scale can-fail floor, as expected.)

## Arms (per-query AUC over held-out-NEW concepts; base 0.5)
- ARM_RAW_GROUNDING : cosine over raw 20d grounding norms, no learning.        [the ceiling to beat]
- ARM_RAW_TEXT      : cosine over the MLM-learned text-rep alone.               [signal in text-at-scale?]
- ARM_FUSED         : 0.5*(cos_grounding + cos_text) late fusion.              [PRIMARY]
- ARM_RANDOM_INIT   : cosine over text-rep from an UNTRAINED transformer.       [isolate learning]
- ARM_COLLAPSE_SHUFFLE : text-reps permuted across concept ids.                 [can-fail / leak witness]
- ARM_POPULARITY    : rank by mention-frequency / train-degree only.            [validity control]
Evaluated on BOTH: SEMANTIC (WordNet-supersense same-lexname) and RELATIONAL (leak-proof neighbour
inference). Ablation attribution = ARM_RAW_TEXT (text only) vs ARM_RAW_GROUNDING (grounding only) vs
ARM_FUSED (fused).

## Pre-registered bands (SEMANTIC held-out-NEW same-lexname per-query AUC is THE one number)
- HARD_PASS: FUSED - RAW_GROUNDING >= 0.03 AND per-seed min margin > 0 AND RAW_TEXT > RANDOM_INIT
  (learning is real), with VALIDITY holding.
- HARD_FAIL_DATASCALE_REFUTED (the plan's fork): on the WELL-COVERED subset (concepts with
  >= 100 mentions) FUSED - RAW_GROUNDING <= 0 at ~240M-token scale => data-scale hypothesis REFUTED;
  the null is OBJECTIVE-level (R1 geometry), redirect budget off larger corpora.
- MIDDLE_BAND_TIE_NULL: |FUSED - RAW_GROUNDING| < 0.03 (text-at-scale ties raw grounding; decisive honest
  finding = relational/semantic learning ~null at this scale).
- HARD_FAIL_INVALID: validity fails.
- VALIDITY (required or the number is untrustworthy): COLLAPSE_SHUFFLE in [0.44,0.56], POPULARITY in
  [0.44,0.56], RAW_GROUNDING >= 0.55 (a real, non-saturated signal), min held-out query power >= 120.
- Relational bar reported alongside (FUSED - RAW_GROUNDING on the leak-proof neighbour-inference AUC).

## Discriminator-must-survive-scale (option B: analytical + smoke preview)
The mechanism (learned text-at-scale) is EXPECTED to be near-chance at the smoke slice (2.4M tokens =
the data-starved regime that already produced the null) and to fire ONLY at FULL scale (~40-50x more
tokens, 512d/6-layer/60k steps). The smoke confirms the discriminator CAN FAIL (text=0.5047 ~ chance
at the starved slice) and that all controls sit at floor while RAW_GROUNDING is a real 0.61 signal.
The FULL run is the discriminating test; either outcome (PASS or the HARD_FAIL fork) is decisive and
pre-registered. RAW_GROUNDING (0.61 at smoke) is NOT saturated (< 0.95) so FUSED has headroom.

## Leak-proofness (the load-bearing structural design)
- Concept-level (NOT edge-level) held-out split, sha256-ranked, freq-stratified (PYTHONHASHSEED-free).
- Every held-out concept's mentioning lines (exact surface + light inflection variants) are SCRUBBED
  from ALL training text: the BPE tokenizer, the MLM stream, and train-concept mention postings.
- BPE tokenizer trained on TRAIN text ONLY (subword-merge-statistics leak channel closed).
- VERIFIED-ZERO-OVERLAP GATE: 0 training lines may contain a held-out surface (asserted; halts on breach).
  Smoke witness = 0. FULL witness must also be 0.
- Relational target edge is NEVER an input to any rep (reps are grounding + text only, zero relational
  input) => the relational bar is leak-proof by construction.

## SCHEMA-VET declarations
- cardinality_ok: EXPECTED_N_UNITS = n_seeds (2 for FULL); verdict checks len(per_seed)==n_seeds.
- final_metrics_atomicity: tmp_replace (write_metrics os.replace) + per-seed partials (write_partial).
- except-ordering: `except SystemExit: raise` before `except Exception` (no BaseException, no bare except). VERIFIED by grep gate.
- crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity + random-init controls witness the floor empirically.
- baseline_in_band: smoke shows collapse ~0.49, popularity ~0.50, raw 0.61 (0.05 < baseline < 0.95). PASS.
- HP_SCOPE: HARD_PASS gates apply to ARM_FUSED (semantic primary) only; relational is a reported secondary bar.
- arms_differ_verified: True (sha256 hash-test over RAW/TEXT/RANDOM base rep matrices; halts if bit-identical).
- calibration_check: default_ok_for_this_regime (AUC base 0.5 analytic; controls witness it).
- defensive_error_checking: start_marker + crash-diagnostic (CELL_CRASHED + traceback) + _heartbeat.jsonl (per MLM log step) + specific-exception classes. cell_chunked: false (per-seed partials + shared bundle; single cell).
- real_code_path: --self-test constructs the REAL objects (load_concept_universe, count/collect/tokenize passes, build_bpe, mlm_train, encode, semantic+relational eval, zero-overlap gate) at N~16 scale. SELF-TEST PASS.
- progress_logging: print_flush_true + _heartbeat.jsonl (timeout_s >> 1800). REQUIRED and present.
- test-design gates: no sweep axis (bracket/effective-param N/A); positive control = RAW_GROUNDING reproduced as the ceiling at the test regime; discriminator can-fail confirmed at smoke.

## HARD INVARIANTS
TEACHER-FREE. NO borrowed vectors anywhere (learned token embeddings + from-scratch Transformer; BPE
vocab built FROM ARC). INDUCTIVE (held-out placed from its own text + grounding; never a training
target). LEAK-PROOF (above). ASCII-only. Deterministic seeds. AI2 ARC Corpus = INTERNAL research use
only (do NOT redistribute corpus / derived raw text).

## Remote dependencies (orchestrator: verify before launch)
- torch with CUDA on the GPU box (cell is device-agnostic; uses AMP only when cuda available).
- python package `tokenizers` (HuggingFace, BPE trainer) present in the remote venv.
- ARC corpus staged at `data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt` on the remote (in progress).
- NLTK WordNet data (for EVAL-only lexname truth); lexname cache regenerates if absent.

## Runtime + timeout
Est FULL on RTX 4060 Ti: ~3-5h (data prep ~15-25min shared once; MLM 60k steps batch128 ~2 seeds;
concept encode 2 seeds; evals). Timeout 28800s (8h) generous. FULL profile: max_lines=10M,
train_token_budget=130M, vocab=16000, d512/6-layer/8-head/seq128, cap_mentions=128, heldout=800.
