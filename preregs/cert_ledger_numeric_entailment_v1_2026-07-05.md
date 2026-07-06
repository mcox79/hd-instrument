# Pre-reg: exp_cert_ledger_numeric_entailment_v1 (TIER-2 SELF-CHECK LOOP)

Date: 2026-07-05
Author: hdi_exp_dev (spawned by Director)
Design source: notes/exp_dev_handoff_research_entailment_self_check_first_cell_2026-07-05.md
  (anchor #3, "Tier-2 wiring", DEFERRED-now-READY) + notes/research_entailment_self_check_first_cell_2026-07-05.md (Q1 Tier 2, Q2 loop).
Cell: experiments/exp_cert_ledger_numeric_entailment_v1.py
Referent: data/substrate_index/meta/cert_ledger.jsonl + data/**/metrics.json (# KB_REFERENT; live self-record)

## What / why (the north-star payoff, narrowly scoped)

The substrate CHECKS, via its OWN retrieval + comparator primitives, whether each recorded
verdict FOLLOWS from the number it cites -- e.g. a cell whose own verdict_msg says
"spearman=0.886 >= 0.80" is re-checked: does the >= actually hold? The loop COMPOSES two
already-landed, by-construction-exact primitives:

- RETRIEVAL leg: exact-match retrieval over the substrate's own self-record
  (cert_ledger.jsonl), the same Task-B-style HAS_STATUS exact-match validated in
  exp_cert_ledger_self_query_v1 (SMOKE HARD_PASS). CPU-light exact-match form (the KGStore
  vector variant is validated in that parent cell; not re-run here).
- COMPARISON leg: numeric-threshold three-way compare via the JUST-VET'd comparator,
  imported VERBATIM from experiments.exp_math_rns_subtract_compare_v1 (decode_then_compare:
  encode value + threshold as RNS integers, two exact CRT decodes, compare in scalar space;
  MEASURED_MECHANISM@data/exp_math_rns_subtract_compare_v1/metrics.json:arms.large.decode_then_compare.three_way_mean=1.0).

TASK SHAPE: harvest REAL (cited_value, op, cited_threshold, recorded_verdict) triples from
the substrate's own on-disk record -- every metrics.json whose own verdict_msg literally
cites a `NUM op NUM` inequality. For each: retrieve the source claim from the ledger,
quantize the cited numbers into the exact-residue encoding, run the comparator, and FLAG any
recorded inequality that is arithmetically FALSE (the loop catches an inconsistency in the
substrate's OWN self-record). Oracle = the trivial Python `value op threshold` on the SAME
quantized integers.

## Honest real-data scope (MEASURED on disk 2026-07-05, reproducible)

- 5794 metrics.json on disk; 3653 carry a canonical top-level verdict; 689 cite a parseable
  `NUM op NUM` inequality in their own verdict_msg (the REAL triple source).
  MEASURED@survey (reproducible: regex `(?:name=)?NUM (>=|<=|==|>|<) NUM` over verdict_msg).
- cert_ledger.jsonl: 1444 rows -> exp-key -> recorded-verdict index (the retrieval leg's
  self-record). MEASURED@data/substrate_index/meta/cert_ledger.jsonl.
- Dynamic range: LARGE regime M=70520; quantize q(v)=round(v*1000)+20000 in [0,M) covers
  v in [-20.0, +50.5). Triples outside are skipped + reported (n_triples_skipped_out_of_range).
- The FINDING is loop-closure over REAL data, NOT a new mechanism: both legs are
  by-construction exact -> substrate==oracle (~1.0) is EXPECTED. The discriminator is the
  CONTRAST (catches injected inconsistencies ~1.0; random ~0.5; scrambled-residue ~chance).

## USER-LOCKED scope guardrail

NARROW glass-box numeric self-check: verifies whether a cited number satisfies a cited
threshold over the substrate's own record. Explicitly NOT full autonomous self-improvement
and NOT the substrate rewriting itself. Even a full HARD_PASS reaches only Tier 2 (numeric
threshold entailment on a real, on-disk metric/threshold/verdict corpus). Honest tier -- VET decides.

## Compute architecture

- Class: (b) sequential-CPU with justification. numpy complex64 FPE; no GPU, no LLM. Reuses
  the VET'd comparator's per-integer encode/decode verbatim (bit-identical CPU reference).
  Wall time smoke ~ minutes (200 triples x 3 seeds x ~4 decodes each at N=8192). No batching
  candidate: this cell VALIDATES the primitive composition, not a phase-point sweep; genuine
  sequential dependency (retrieve -> quantize -> compare -> flag per triple).
- Storage strategy: no_storage_algebraic_bind (algebraic FPE; no item store, no composition depth).
- progress_logging: print_flush_true (line-buffered stdout + per-seed _say + heartbeat).

## Arms (per codebook seed; all on the SAME harvested real triples)

- substrate_op_agreement [MECHANISM] -- substrate decode_then_compare op-eval == Python oracle
  on the SAME quantized integers, over in-range real triples. Expected ~1.0.
- corrupted_metric_flag_recall [DETECTION] -- corrupt cited VALUE so inequality FLIPS;
  substrate must CATCH. Expected ~1.0.
- scrambled_threshold_flag_recall [DETECTION] -- corrupt cited THRESHOLD so inequality FLIPS;
  substrate must CATCH. Expected ~1.0.
- scram_residue_agreement [CONTROL] -- derange residues before CRT on BOTH operands -> garbage
  decode -> op-agreement collapses toward chance. Confirms CRT decode load-bearing. ~chance.
- random_baseline_agreement [CONTROL / AG-baseline] -- fair coin over boolean op-result. ~0.5.
- retrieval_hit_rate [REPORTED] -- fraction of harvested source claims found in the ledger
  self-record via exact-match retrieval. Not pass-gated.
- real_inconsistencies [REPORTED AUDIT BYPRODUCT] -- count + list of real on-disk cited
  inequalities that are arithmetically FALSE (float-holds False, quant-faithful, substrate agrees).

## Pre-registered bands (HYPOTHESIZED from exact-decode theory; MEASURED filled by smoke)

| Gate | HARD-PASS | HARD-FAIL | Applies to |
|---|---|---|---|
| substrate_op_agreement (min over seeds) | >= 0.99 | < 0.90 | MECHANISM |
| injected flag-recall (min of corrupt-metric & scramble-threshold) | >= 0.95 | < 0.70 | DETECTION |
| random_baseline_agreement (max over seeds) | <= 0.72 (control collapses) | -- | CONTROL |
| scram_residue_agreement (max over seeds) | <= 0.72 (control collapses) | -- | CONTROL |
| injection flip-rate (min) | >= 0.99 (discriminator-fires; injection creates real inconsistency) | < 0.99 -> DISCRIMINATOR_DID_NOT_FIRE | GATE |
| n_triples_checked | >= 100 (smoke) / >= 300 (full) | below -> DISCRIMINATOR_DID_NOT_FIRE | GATE |

HARD-PASS overall: op_agreement >= 0.99 AND injected flag-recall >= 0.95 AND both controls
collapse (<= 0.72) AND injection actually flips the oracle (>= 0.99) AND enough real triples.

HARD-FAIL overall: op_agreement < 0.90 (comparator broke on real quantized data) OR injected
flag-recall < 0.70 (loop cannot catch inconsistencies).

MIDDLE_BAND: above HF but below HP on op_agreement or flag-recall.

Per [feedback-research-every-finding]: the count of REAL arithmetically-false cited
inequalities is reported regardless of tier -- 0 is a legitimate finding (self-record's cited
numeric inequalities are internally consistent); >0 is a genuine audit surface (list persisted).

## SCHEMA-VET checklist (self-verified)

- cardinality_ok: EXPECTED_N_UNITS = 6 * n_seeds; verdict counts len(per_unit).
- per-unit failure-class: harvest catches json.JSONDecodeError / OSError / ValueError by
  class, counted in harvest_parse_failures; does NOT gate verdict (no bare except).
- discriminator-fires (META_RULE_K): injection must flip the oracle (>=0.99) + >=100 real
  triples; else DISCRIMINATOR_DID_NOT_FIRE (not a pass).
- strictly-above-floor (META_RULE_L): HP op 0.99 (HF 0.90), HP recall 0.95 (HF 0.70).
- HP_SCOPE: op_agreement + flag-recall apply to MECHANISM only; random + scram are floors.
- calibration_check: default_ok_for_this_regime (exact CRT decode; SCALE/OFFSET cover range;
  resolution-guard RES=0.002 excludes sub-resolution ties from the audit).
- arms_differ (META_RULE_AF): pred_substrate != pred_random and != pred_scram_residue (hash).
  Exempt pair: substrate_op vs oracle_quant (identical by construction = the correctness finding).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise before except Exception (no BaseException).
- crlb_n/a: correctness/detection test; contrast controls are the floor (no noise-floor sweep).
- baseline_in_band (META_RULE_AG): random_baseline ~0.5 in (0.05,0.95); mechanism saturation
  is an exactness test with contrast controls (AG-exempt).
- discriminator survives scale: smoke at FULL N=8192, LARGE regime; reduces triple count only.
- start_marker / crash_diagnostic / heartbeat present; cell_chunked=false (no seed-death risk;
  seeds are codebook seeds, cheap, single cell).
- run_mode verified post-write (assert written run_mode == mode).

## Gate audit (composition/sweep gates §15)

- effective_vs_nominal: no swept difficulty param; seeds are codebook seeds. ALIGNED.
- discriminating_fraction: n/a (correctness test); controls provide the contrast. crlb_n/a.
- composition_edges: retrieval(exact-match ledger) -> triple -> comparator(decode_then_compare).
  SHAPE_MATCH (both operate on discrete integers / exact-match strings; the comparator's own
  threshold_entailment arm is the identical shape, MEASURED_MECHANISM at large regime).
- positive_control: the comparison leg IS the reproduced prior CG primitive (imported verbatim
  from exp_math_rns_subtract_compare_v1); op_eval_selftest reproduces exact decode AT THIS
  regime (large, M=70520) before any arm measurement. tolerance 0.01.
- functional_requirements: (1) retrieve a recorded claim from own record -> exact-match ledger
  index; (2) compare cited value vs cited threshold -> decode_then_compare; (3) flag verdicts
  that do not follow -> op-eval mismatch vs cited-inequality truth.

## Dispatch

- SMOKE: local_cpu_queue (USER-lock: SMOKE-only-local). Demonstrates the loop at FULL N.
- FULL: PARKED for Orchestrator. Reads the LIVE self-record referent (whole data/ tree +
  cert_ledger.jsonl); on the autonomous remote pipeline this trips the remote-stale-gate that
  needs a USER-auth deploy. Staged, not auto-dispatched. Canonical run = remote (per
  feedback-canonical-run-is-remote-queue), but gated on USER auth for the live-referent read.

## MEASURED (post-smoke, FULL N=8192, 2026-07-05)

Source: data/exp_cert_ledger_numeric_entailment_v1/metrics.json (run_mode=smoke, HARD_PASS, 12.6s).

- Corpus: scanned 5800 metrics.json; 654 cite a `NUM op NUM` inequality in their own
  verdict_msg; 948 unique triples; 915 in dynamic range (33 skipped out-of-range).
  Ledger self-record: 1445 rows -> 950 exp-key verdicts.
- substrate_op_agreement = 1.0000 (all 3 seeds) MEASURED@arms.{7,13,19}.op_agreement -- the
  substrate re-derives every cited quantized inequality EXACTLY (== Python oracle).
- corrupted_metric_flag_recall = 1.0 AND scrambled_threshold_flag_recall = 1.0 (all seeds) --
  the loop CATCHES every injected inconsistency; inject_flip_min = 1.000.
- scram_residue_agreement = 0.5550 (<= 0.72 -> CRT decode load-bearing); random_baseline =
  0.455-0.510 (~chance) -- both controls collapse.
- retrieval_hit_rate = 0.145 (200 capped triples; the ledger indexes a subset of exp keys).
- n_triples_checked (smoke cap) = 200; cardinality_ok = True; arms_differ_verified = True.

## AUDIT BYPRODUCT (honest; Fix#28 caught 2 false-positive classes at author time)

- Whole-corpus scan: 915 in-range real triples; 899 cited inequalities parse as TRUE, 16 parse
  as arithmetically FALSE. Manual review of representative FALSE cases classifies ALL as
  free-text verdict_msg PARSE ARTIFACTS, NOT genuine verdict-vs-number contradictions:
  - Author-time Fix#28 catch #1: metric-NAME trailing digit misread as operand
    ("chunk-F1 <0.90" -> bogus "1<0.90"; "pass@1 <0.20"; "recall@2 <0.50"). Fixed via
    left-boundary lookbehind. Removed 9 false-positives.
  - Author-time Fix#28 catch #2: scientific-notation split ("5.32e-05<0.0001" -> bogus
    "5.0<0.0001") + relative-threshold coefficient ("0.737 >= 0.90 * ORACLE=0.817"). Fixed by
    parsing sci-notation as a unit + a coefficient right-guard. Removed 11 more.
  - Residual 16: cross-clause number joins ("K=3 <0.75" = success@K3=0.7 < 0.75), garbled
    shorthand ("a3=1.000<0.95" where the real arm is heldout_top1=1.000>=0.85), malformed
    inline annotations ("BPC=4.8466 >= 6.99"), display-precision ties ("0.035 > 0.035").
- CONFIRMED genuine inconsistencies: 0. Honest limitation reported: free-text verdict_msg is
  not a clean structured (metric,threshold,verdict) source; a reliable Tier-2 audit needs a
  STRUCTURED gate field in metrics.json. The mechanical loop is the validated capability; the
  audit is a reported byproduct with this caveat (NOT an overclaim of "N real inconsistencies").
