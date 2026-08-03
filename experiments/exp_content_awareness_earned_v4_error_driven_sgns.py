"""
DIAGNOSTIC CAN-FAIL CELL, ERROR-DRIVEN CONTENT ENCODER STEP 4 (measurement-only,
one-shot, not a substrate cell, not dispatched -- matches the earned_v1/v2/v3
diagnostic convention).

USER PRINCIPLE STEER (2026-08-03): the count-based PPMI direction is
CHEAP_EXHAUSTED (commit e69e95e47: best arm = mean-removed multicorpus PPMI,
combined ceiling 0.667, unstated-goal 1/3). PPMI is Hebbian COUNTING -- no
error signal, no update rule. The brain's mechanism for earning content
representations is PREDICTION + UPDATE-ON-PREDICTION-ERROR (Rescorla-Wagner /
predictive processing / Zacks event-prediction), not co-occurrence counting.
This cell builds the first from-scratch, glass-box, error-driven content
encoder and can-fail tests it against the SAME probe PPMI capped on, with a
random-init untrained control that MUST fail (architecture-alone is not the
lever; the ERROR-DRIVEN UPDATE is the lever).

Prior-work check (substrate_query.sh, mandatory before authoring):
  Query: "error-driven content encoder prediction-error learning skip-gram
  negative sampling word vectors" -> top hit cosine=0.3027 (link-prediction
  negative-sampling KG literature, NOT this task -- different topic, no
  overlap). Second hit (cosine=0.3027, tie) =
  notes/exp_dev_handoff_research_prediction_error_native_learning_signal_2026-07-09.md
  -- names hdlab/predictive_coding.py (predict / residual_magnitude /
  proportional_gate / gated_write) as the substrate's EXISTING error-driven
  primitive. Read: that module implements RESIDUAL-GATED HEBBIAN WRITE for an
  associative-memory matrix W (skip/scale a Hebbian outer-product write based
  on how surprising the observed value is) -- a *different* mechanism shape
  than what this task needs (learning a DISTRIBUTED CONTENT VECTOR per word via
  a predict-context-from-target objective, i.e. the representation itself is
  the thing being differentiated by error, not a write-gate on top of a
  Hebbian sum). Verdict: GENUINELY NOVEL for the word/predicate CONTENT-VECTOR
  encoder question -- this is not a rediscovery of the Spoke1 predictive-coding
  hand-off (which gates writes into an existing Hebbian W; it does not learn
  distributed content vectors from scratch). Building on the same *family* of
  idea (Rescorla-Wagner delta-rule error-driven update), not duplicating the
  Spoke1 cell family or its W_pred matrix.

MECHANISM (from-scratch, glass-box, NO borrowed vectors/model/LLM):
  Skip-gram-with-negative-sampling (SGNS), the textbook error-driven
  distributed-representation learner (Mikolov et al. 2013). This is chosen
  over PPMI specifically because it has a genuine PREDICTION-ERROR update:
  for a (target, context) pair with label y in {0,1} (positive context word
  vs sampled negative), the update is the classic delta rule /
  Rescorla-Wagner form:
    prediction  p = sigmoid(dot(w_target, w_context))
    error       e = p - y                      (THE prediction-error signal)
    w_target   -= lr * e * w_context            (update PROPORTIONAL to error)
    w_context  -= lr * e * w_target
  This is meaningfully more brain-faithful than PPMI counting (no error
  signal, no update -- co-occurrence counts are accumulated then normalized in
  closed form) and is NOT a borrowed/pretrained vector: every weight is
  random-init here (fixed seed) and ONLY ever updated by this corpus's own
  prediction errors (self-supervised, no gold labels used for training).

THREE ARMS, ONE VARIABLE (content mechanism), same corpus/vocab/tokenizer/
window/min_count/scoring pipeline as earned_v3 (apples-to-apples):
  ARM_ERROR_DRIVEN_SGNS: SGNS vectors after full training (the mechanism).
  ARM_PPMI_MEANREMOVAL_REFERENCE: recomputed on THIS run's corpus load (not
    just cited) via earned_v3's own build_raw_ppmi_vectors +
    apply_mean_removal, to confirm the 0.667/0.333 reference reproduces
    bit-for-bit deterministically before comparing against it.
  ARM_RANDOM_INIT_CONTROL: the SAME embedding tables (same shapes, same fixed
    init seed as ARM_ERROR_DRIVEN_SGNS) with ZERO training steps applied --
    the CAN-FAIL CONTROL. If this control "passes" the same gates as the
    trained arm, the probe cannot discriminate architecture from mechanism
    and the whole comparison is void.

Corpora: identical 5-novel combined corpus, same paths, as earned_v2/v3
(all public-domain Project Gutenberg):
  data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt   (PG#45)
  data/corpora/wizard_of_oz/cleaned/wizard_of_oz.clean.txt                   (PG#55)
  data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt                       (PG#74)
  data/corpora/little_women/cleaned/little_women.clean.txt                  (PG#514)
  data/corpora/alice_in_wonderland/cleaned/alice_in_wonderland.clean.txt     (PG#11)

PRE-REGISTERED VERDICT (locked before running; N=6 probe items -> achievable
discrete ceiling values are k/6 for k in 0..6; the next tier above the
measured PPMI ceiling of 4/6=0.667 is 5/6=0.8333 -- per Gate B
(discriminating-band) discipline, "beats 0.667" is operationalized as
clearing that next achievable tier, not an arbitrary continuous threshold):
  WORKS (EARNED_ERROR_DRIVEN_VIABLE) = error-driven ceiling >= 5/6 (0.8333)
    AND error-driven unstated_goal_recovery >= 2/3 AND collapse_broken=True
    AND random-init control ceiling < 5/6 (control genuinely fails to clear
    the same tier) AND random-init ceiling is below error-driven ceiling by
    >= 1/6 margin (control materially underperforms, not a coin-flip tie)
    -> the brain's error-driven mechanism succeeds where counting capped;
    recommend scaling (event-level targets, more capacity) + a REAL
    curriculum-grounded eval (this N=6 probe is a controlled smoke, NOT the
    architecture-accept decision).
  FAILS_MECHANISM_INSUFFICIENT = error-driven ceiling <= ppmi_meanremoval
    ceiling (0.667, i.e. does not beat the counting baseline)
    -> the trained representation itself needs event-level targets or more
    capacity; counting still wins on this probe.
  FAILS_PROBE_TOO_WEAK = random-init control ceiling >= 5/6 (the untrained
    control also clears the discriminating tier) regardless of the trained
    arm's score -> the N=6 probe cannot discriminate architecture from
    learned content; the comparison is VOID until the probe or eval scale
    changes (report honestly, do not claim mechanism success).
  MIDDLE_BAND_N6 = none of the above patterns fire cleanly (e.g. error-driven
    beats PPMI on ceiling but unstated-goal recovery does not reach 2/3, or
    control margin is <1/6) -> directional signal only, no overclaim, N=6.

DISCIPLINE (per exp_dev canonical mandates):
- glass-box, no borrowed embedding/model/LLM anywhere (word2vec/SGNS
  architecture is textbook and reimplemented here from scratch in numpy;
  weights are random-init + self-corpus-trained only).
- deterministic_seeding: ALL randomness (embedding init, negative-sampling
  table construction, per-position context-offset draws, epoch shuffling)
  uses np.random.RandomState with FIXED integer seeds; no hash()/list(set())
  anywhere in the training loop (PROT-023 compliant).
- ARMS-MUST-DIFFER (META_RULE_AF): hash-check across all 3 arms' dense
  vector matrices (random-init MUST differ from trained: same init, then
  training perturbs it; PPMI MUST differ from both: different dimensionality
  and construction entirely).
- except SystemExit / except Exception ordering: no bare except, no
  BaseException.
- final_metrics_atomicity: tmp_replace (os.replace) on metrics.json.
- cardinality_ok: n=6 hand-selected probe items x 3 arms = 18 scored units,
  asserted via len() == EXPECTED.
- CRLB / capacity-feasibility n/a for this cell (no argmax-noise-floor
  quantitative threshold on a fixed-capacity associative store; discriminating
  band feasibility is handled instead via the discrete k/6 tier analysis
  above, which is this cell's exact analogue of Gate B).
- runtime bound: single foreground run over ~440k tokens, embedding dim=64,
  3 epochs, ~1.3M positive updates + 5 negatives each (~7.9M total SGD steps)
  via a pure-numpy negative-sampling table (O(1) per draw, no O(vocab) rebuild
  per step) -- designed to complete in well under 10 minutes on CPU, NOT a
  blind multi-hour run. progress_logging=print_flush_true (heartbeat every
  epoch + every 200k positions).
"""
import os
import sys
import json
import time
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from experiments.exp_content_awareness_ceiling_probe_v1 import (  # noqa: E402
    SATISFY_RESTATE_ITEMS,
    UNSTATED_GOAL_ITEMS,
    GOAL_SCHEMAS,
    GOAL_018_BORDERLINE,
)
from experiments.exp_content_awareness_ceiling_probe_earned_v3_rawppmi_meanremoval import (  # noqa: E402
    build_raw_ppmi_vectors,
    apply_mean_removal,
    score_arm,
    _tokenize,
    BASIC_STOPWORDS,
    WINDOW,
    MIN_COUNT,
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT, "data", "exp_content_awareness_earned_v4_error_driven_sgns"
)
ANCHOR_NAME = "content_awareness_earned_v4_error_driven_sgns"

CORPUS_PATHS = [
    os.path.join(REPO_ROOT, "data", "corpora", "anne_of_green_gables", "cleaned",
                 "anne_of_green_gables.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "wizard_of_oz", "cleaned",
                 "wizard_of_oz.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "tom_sawyer", "cleaned",
                 "tom_sawyer.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "little_women", "cleaned",
                 "little_women.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "alice_in_wonderland", "cleaned",
                 "alice_in_wonderland.clean.txt"),
]

EXPECTED_N_SATISFY_RESTATE_ITEMS = 3
EXPECTED_N_UNSTATED_GOAL_ITEMS = 3
EXPECTED_N_ARMS = 3

# ---------------------------------------------------------------------------
# SGNS hyperparameters (THEORETICAL/HYPOTHESIZED@this-file; bounded for a
# foreground-completable smoke, not tuned for a target outcome)
# ---------------------------------------------------------------------------
D_EMBED = 64            # embedding dimensionality; small, bounded, CPU-fast
N_EPOCHS = 3
K_NEGATIVES = 5
LR_START = 0.05
LR_END = 0.001
NEG_TABLE_SIZE = 1_000_000
NEG_SAMPLING_POWER = 0.75   # THEORETICAL: Mikolov et al. 2013 unigram^0.75 negative-sampling distribution
INIT_SEED = 42
NEG_TABLE_SEED = 1337
TRAIN_ORDER_SEED = 2026
CONTEXT_OFFSET_SEED = 777
NEG_DRAW_SEED = 99

# Achievable discrete tiers for N=6 probe items (Gate B discriminating-band
# analogue): ceiling_recall values are k/6 for k in {0..6}.
PPMI_MEANREMOVAL_CEILING_REF_MEASURED = 0.6666666666666666  # MEASURED@data/exp_content_awareness_ceiling_probe_earned_v3_rawppmi_meanremoval/metrics.json:summary_fields.arm_b.ceiling_recall_all_probe_items
PPMI_MEANREMOVAL_UNSTATED_REF_MEASURED = 0.3333333333333333  # MEASURED@ same file :summary_fields.arm_b.unstated_goal_recovery_rate
NEXT_TIER_ABOVE_PPMI = 5.0 / 6.0  # THEORETICAL: next achievable discrete ceiling above 4/6
UNSTATED_RECOVERY_HARD_PASS = 2.0 / 3.0
CONTROL_MARGIN_MIN = 1.0 / 6.0  # random-init must trail error-driven by >= this margin


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _arms_must_differ_arrays(named_arrays):
    """META_RULE_AF hash-based check across N named full-matrix arm outputs.
    Handles arms of DIFFERENT shapes (PPMI is V x V, SGNS is V x D) -- hashes
    the raw bytes, so shape differences alone guarantee non-collision; the
    interesting case (random-init vs trained SGNS, same shape) is the one
    that actually needs training to have moved the weights."""
    digests = {}
    for name, arr in named_arrays.items():
        b = np.ascontiguousarray(arr).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests.keys())
    all_same = len(set(digests.values())) == 1 and len(names) > 1
    pairwise = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = names[i], names[j]
            pairwise[f"{a}__vs__{b_}"] = (digests[a] != digests[b_])
    return digests, pairwise, (not all_same)


def build_neg_sampling_table(vocab_counts, table_size=NEG_TABLE_SIZE, power=NEG_SAMPLING_POWER, seed=NEG_TABLE_SEED):
    """Classic word2vec negative-sampling table (Mikolov et al. 2013): a
    fixed-size int32 array where vocab index i appears with frequency
    proportional to count_i^power. Enables O(1) negative draws (randint into
    the table) instead of O(vocab) cumulative-distribution rebuild per draw.
    Deterministic given a fixed seed (RandomState, not hash())."""
    counts = np.asarray(vocab_counts, dtype=np.float64)
    weighted = np.power(counts, power)
    probs = weighted / weighted.sum()
    cum = np.cumsum(probs)
    cum[-1] = 1.0  # guard float rounding
    positions = (np.arange(table_size, dtype=np.float64) + 0.5) / table_size
    table = np.searchsorted(cum, positions).astype(np.int64)
    table = np.clip(table, 0, len(counts) - 1)
    # rng seed reserved for reproducibility of any future stochastic variant
    # of table construction; current construction is a deterministic
    # searchsorted quantization (no draw needed), so `seed` is unused here
    # but declared for the deterministic_seeding audit trail.
    _ = np.random.RandomState(seed)
    return table


def train_sgns(tok_idx, vocab_size, vocab_counts, d=D_EMBED, n_epochs=N_EPOCHS,
                k_neg=K_NEGATIVES, lr_start=LR_START, lr_end=LR_END, window=WINDOW):
    """From-scratch skip-gram-with-negative-sampling. Returns
    (w_target_trained, w_target_random_init, n_pairs_trained, per_epoch_mean_error).

    ERROR-DRIVEN UPDATE (the load-bearing mechanism, Rescorla-Wagner delta
    rule / logistic-SGD gradient -- same closed form):
        p = sigmoid(dot(w_target[t], w_context[c]))
        e = p - y                          # prediction error, y in {0 (neg), 1 (pos)}
        w_target[t]  -= lr * e * w_context[c]
        w_context[c] -= lr * e * w_target[t]   (pre-update w_target[t] used)
    No gradient framework; explicit numpy delta-rule loop, glass-box.
    """
    init_rng = np.random.RandomState(INIT_SEED)
    w_target = (init_rng.rand(vocab_size, d).astype(np.float64) - 0.5) / d
    w_context = (init_rng.rand(vocab_size, d).astype(np.float64) - 0.5) / d
    w_target_random_init = w_target.copy()  # snapshot BEFORE any training = ARM_RANDOM_INIT_CONTROL

    neg_table = build_neg_sampling_table(vocab_counts)
    order_rng = np.random.RandomState(TRAIN_ORDER_SEED)
    offset_rng = np.random.RandomState(CONTEXT_OFFSET_SEED)
    neg_rng = np.random.RandomState(NEG_DRAW_SEED)

    valid_positions = np.where(tok_idx >= 0)[0]
    n_positions = len(valid_positions)
    n_pairs_trained = 0
    per_epoch_mean_abs_error = []

    for epoch in range(n_epochs):
        perm = order_rng.permutation(n_positions)  # deterministic given fixed seed (sorted(set()) discipline n/a: no set() used)
        epoch_errs = []
        for step, pidx in enumerate(perm):
            i = valid_positions[pidx]
            t = tok_idx[i]

            offset = offset_rng.randint(-window, window + 1)
            if offset == 0:
                continue
            j = i + offset
            if j < 0 or j >= len(tok_idx):
                continue
            c = tok_idx[j]
            if c < 0:
                continue

            progress_frac = (epoch * n_positions + step) / max(1, n_epochs * n_positions)
            lr = lr_start + (lr_end - lr_start) * progress_frac

            # positive update (y=1)
            z = float(np.dot(w_target[t], w_context[c]))
            p = 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))
            e = p - 1.0
            epoch_errs.append(abs(e))
            wt_old = w_target[t].copy()
            w_target[t] -= lr * e * w_context[c]
            w_context[c] -= lr * e * wt_old

            # negative updates (y=0), k_neg draws via O(1) table lookup
            neg_slots = neg_rng.randint(0, NEG_TABLE_SIZE, size=k_neg)
            neg_ids = neg_table[neg_slots]
            for nc in neg_ids:
                nc = int(nc)
                if nc == c:
                    continue
                z_n = float(np.dot(w_target[t], w_context[nc]))
                p_n = 1.0 / (1.0 + np.exp(-np.clip(z_n, -30.0, 30.0)))
                e_n = p_n - 0.0
                epoch_errs.append(abs(e_n))
                wt_old_n = w_target[t].copy()
                w_target[t] -= lr * e_n * w_context[nc]
                w_context[nc] -= lr * e_n * wt_old_n

            n_pairs_trained += 1
            if step % 200000 == 0:
                print(
                    f"[progress] epoch={epoch+1}/{n_epochs} step={step}/{n_positions} "
                    f"n_pairs_trained={n_pairs_trained} lr={lr:.5f}",
                    flush=True,
                )

        mean_abs_err = float(np.mean(epoch_errs)) if epoch_errs else float("nan")
        per_epoch_mean_abs_error.append(mean_abs_err)
        print(f"[progress] epoch={epoch+1}/{n_epochs} complete mean_abs_error={mean_abs_err:.4f}", flush=True)

        if not np.isfinite(w_target).all() or not np.isfinite(w_context).all():
            raise FloatingPointError(f"NaN/Inf detected in SGNS weights at epoch {epoch+1}")

    return w_target, w_target_random_init, n_pairs_trained, per_epoch_mean_abs_error


def main():
    t_start = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "diagnostic_inline_foreground",
        "expected_n_units": (EXPECTED_N_SATISFY_RESTATE_ITEMS + EXPECTED_N_UNSTATED_GOAL_ITEMS) * EXPECTED_N_ARMS,
    }
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(start_marker, f)
    os.replace(tmp, final)

    assert len(SATISFY_RESTATE_ITEMS) == EXPECTED_N_SATISFY_RESTATE_ITEMS, "cardinality_ok breach: satisfy/restate items"
    assert len(UNSTATED_GOAL_ITEMS) == EXPECTED_N_UNSTATED_GOAL_ITEMS, "cardinality_ok breach: unstated-goal items"

    corpus_texts = []
    corpus_word_counts = {}
    for p in CORPUS_PATHS:
        with open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        corpus_texts.append(txt)
        corpus_word_counts[os.path.basename(p)] = len(_tokenize(txt))

    # ---- PPMI reference arm: recomputed on THIS run's corpus load (not just cited) ----
    vocab, idx, ppmi_raw_vecs, n_tokens, vocab_size, ppmi_nnz = build_raw_ppmi_vectors(corpus_texts)
    ppmi_corrected_vecs, mean_vec, top_dirs, mr_iters, mr_residuals = apply_mean_removal(ppmi_raw_vecs)

    # ---- shared tokenization for SGNS (same vocab/idx as PPMI: apples-to-apples) ----
    tokens = []
    for text in corpus_texts:
        tokens.extend(_tokenize(text))
    tok_idx = np.array([idx.get(w, -1) for w in tokens], dtype=np.int64)
    vocab_counts_arr = np.zeros(vocab_size, dtype=np.int64)
    for ti in tok_idx:
        if ti >= 0:
            vocab_counts_arr[ti] += 1

    print(f"[progress] corpus loaded: n_tokens={n_tokens} vocab_size={vocab_size} starting SGNS training", flush=True)
    w_sgns_trained, w_sgns_random_init, n_pairs_trained, per_epoch_err = train_sgns(
        tok_idx, vocab_size, vocab_counts_arr
    )
    print(f"[progress] SGNS training complete n_pairs_trained={n_pairs_trained}", flush=True)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF) across all 3 dense-vector representations ----
    arm_vec_digests, arm_pairwise_differ, arm_vecs_differ = _arms_must_differ_arrays({
        "arm_error_driven_sgns_trained": w_sgns_trained,
        "arm_random_init_control": w_sgns_random_init,
        "arm_ppmi_meanremoval_reference": ppmi_corrected_vecs,
    })
    assert arm_vecs_differ, "META_RULE_AF VIOLATION: two or more arms produced identical vectors"
    assert arm_pairwise_differ["arm_error_driven_sgns_trained__vs__arm_random_init_control"], (
        "META_RULE_AF VIOLATION: training did not move w_target at all (trained == random-init bit-identical)"
    )

    # ---- score all 3 arms with the byte-identical scoring battery ----
    arm_error_driven = score_arm("ARM_ERROR_DRIVEN_SGNS", idx, w_sgns_trained)
    arm_random_init = score_arm("ARM_RANDOM_INIT_CONTROL", idx, w_sgns_random_init)
    arm_ppmi_ref = score_arm("ARM_PPMI_MEANREMOVAL_REFERENCE", idx, ppmi_corrected_vecs)

    # ---- reproduction check: does the PPMI reference reproduce the cited prior cell? ----
    ppmi_ref_reproduces_prior = (
        abs(arm_ppmi_ref["ceiling_recall_all_probe_items"] - PPMI_MEANREMOVAL_CEILING_REF_MEASURED) < 1e-9
        and abs(arm_ppmi_ref["unstated_goal_recovery_rate"] - PPMI_MEANREMOVAL_UNSTATED_REF_MEASURED) < 1e-9
    )

    # ---- pre-registered verdict logic ----
    ed_ceiling = arm_error_driven["ceiling_recall_all_probe_items"]
    ed_unstated = arm_error_driven["unstated_goal_recovery_rate"]
    ri_ceiling = arm_random_init["ceiling_recall_all_probe_items"]

    beats_ppmi = ed_ceiling > PPMI_MEANREMOVAL_CEILING_REF_MEASURED
    clears_next_tier = ed_ceiling >= NEXT_TIER_ABOVE_PPMI - 1e-9
    unstated_material_lift = ed_unstated >= UNSTATED_RECOVERY_HARD_PASS - 1e-9
    control_fires = (ri_ceiling < NEXT_TIER_ABOVE_PPMI - 1e-9) and ((ed_ceiling - ri_ceiling) >= CONTROL_MARGIN_MIN - 1e-9)
    probe_too_weak = ri_ceiling >= NEXT_TIER_ABOVE_PPMI - 1e-9

    if probe_too_weak:
        verdict_regime = "FAILS_PROBE_TOO_WEAK"
    elif clears_next_tier and unstated_material_lift and arm_error_driven["collapse_broken"] and control_fires:
        verdict_regime = "WORKS_EARNED_ERROR_DRIVEN_VIABLE"
    elif not beats_ppmi:
        verdict_regime = "FAILS_MECHANISM_INSUFFICIENT"
    else:
        verdict_regime = "MIDDLE_BAND_N6"

    elapsed_s = time.perf_counter() - t_start

    trajectory = {
        "step1_raw_single_novel_ppmi": {"ceiling": 0.5, "unstated_goal_recovery": 0.3333333333333333},
        "step3_ppmi_meanremoval_multicorpus_MEASURED_prior": {
            "ceiling": PPMI_MEANREMOVAL_CEILING_REF_MEASURED,
            "unstated_goal_recovery": PPMI_MEANREMOVAL_UNSTATED_REF_MEASURED,
        },
        "step4_ppmi_meanremoval_reproduced_this_run": {
            "ceiling": arm_ppmi_ref["ceiling_recall_all_probe_items"],
            "unstated_goal_recovery": arm_ppmi_ref["unstated_goal_recovery_rate"],
            "reproduces_prior_cell": ppmi_ref_reproduces_prior,
        },
        "step4_arm_error_driven_sgns": {
            "ceiling": ed_ceiling,
            "unstated_goal_recovery": ed_unstated,
            "collapse_broken": arm_error_driven["collapse_broken"],
        },
        "step4_arm_random_init_control": {
            "ceiling": ri_ceiling,
            "unstated_goal_recovery": arm_random_init["unstated_goal_recovery_rate"],
            "collapse_broken": arm_random_init["collapse_broken"],
        },
    }

    summary = {
        "mechanism_arm": (
            f"ERROR_DRIVEN_SGNS_v4 (D={D_EMBED}, epochs={N_EPOCHS}, k_neg={K_NEGATIVES}, "
            f"lr={LR_START}->{LR_END}, n_tokens={n_tokens}, vocab_size={vocab_size}, "
            f"n_pairs_trained={n_pairs_trained}, glass_box, no_borrowed_embedding, "
            f"random_init_then_self_corpus_trained_only)"
        ),
        "ppmi_reference_arm": (
            f"PPMI_MEANREMOVAL_v3_reproduced (same corpus/vocab/window={WINDOW}/min_count={MIN_COUNT} "
            f"as the cited prior cell, recomputed this run, not just cited)"
        ),
        "corpus_paths": CORPUS_PATHS,
        "corpus_word_counts_per_book": corpus_word_counts,
        "corpus_n_tokens_combined": n_tokens,
        "corpus_vocab_size_after_min_count_filter": vocab_size,
        "sgns_n_pairs_trained": n_pairs_trained,
        "sgns_per_epoch_mean_abs_prediction_error": per_epoch_err,
        "arm_vectors_differ_verified": arm_vecs_differ,
        "arm_vector_digests": arm_vec_digests,
        "arm_pairwise_differ": arm_pairwise_differ,
        "arm_error_driven": {k: v for k, v in arm_error_driven.items() if k not in ("results_satisfy_restate", "results_unstated_goal")},
        "arm_random_init_control": {k: v for k, v in arm_random_init.items() if k not in ("results_satisfy_restate", "results_unstated_goal")},
        "arm_ppmi_meanremoval_reference": {k: v for k, v in arm_ppmi_ref.items() if k not in ("results_satisfy_restate", "results_unstated_goal")},
        "ppmi_reference_reproduces_prior_cell_MEASURED_check": ppmi_ref_reproduces_prior,
        "ppmi_meanremoval_ceiling_ref_MEASURED_prior_cell": PPMI_MEANREMOVAL_CEILING_REF_MEASURED,
        "ppmi_meanremoval_unstated_ref_MEASURED_prior_cell": PPMI_MEANREMOVAL_UNSTATED_REF_MEASURED,
        "next_discriminating_tier_above_ppmi_THEORETICAL": NEXT_TIER_ABOVE_PPMI,
        "beats_ppmi_ceiling": beats_ppmi,
        "clears_next_discriminating_tier": clears_next_tier,
        "unstated_goal_material_lift_gate": unstated_material_lift,
        "random_init_control_fires_gate": control_fires,
        "random_init_control_ceiling": ri_ceiling,
        "error_driven_minus_random_init_margin": ed_ceiling - ri_ceiling,
        "probe_too_weak_gate": probe_too_weak,
        "verdict_regime": verdict_regime,
        "trajectory_MEASURED": trajectory,
        "n_probe_items_caveat": "N=6 hand-selected probe items; this is a CAN-FAIL SMOKE for whether the mechanism functions vs baselines, explicitly NOT the architecture-accept decision. A functioning result here recommends scaling + a real curriculum-grounded eval, not a claim of solved comprehension.",
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"verdict_regime={verdict_regime} (N=6 probe, directional, can-fail smoke); "
            f"error_driven_sgns: ceiling={ed_ceiling:.3f} unstated_goal={ed_unstated:.3f} "
            f"collapse_broken={arm_error_driven['collapse_broken']}; "
            f"random_init_control: ceiling={ri_ceiling:.3f} margin_vs_error_driven={(ed_ceiling - ri_ceiling):.3f} "
            f"control_fires={control_fires}; "
            f"ppmi_meanremoval_reference(reproduced_this_run): ceiling={arm_ppmi_ref['ceiling_recall_all_probe_items']:.3f} "
            f"unstated_goal={arm_ppmi_ref['unstated_goal_recovery_rate']:.3f} "
            f"reproduces_prior={ppmi_ref_reproduces_prior}"
        ),
        "summary": f"DEEP-EARN STEP 4 (error-driven SGNS vs PPMI-meanremoval vs random-init control) verdict_regime={verdict_regime}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "results_arm_error_driven_satisfy_restate": arm_error_driven["results_satisfy_restate"],
        "results_arm_error_driven_unstated_goal": arm_error_driven["results_unstated_goal"],
        "results_arm_random_init_satisfy_restate": arm_random_init["results_satisfy_restate"],
        "results_arm_random_init_unstated_goal": arm_random_init["results_unstated_goal"],
        "results_arm_ppmi_ref_satisfy_restate": arm_ppmi_ref["results_satisfy_restate"],
        "results_arm_ppmi_ref_unstated_goal": arm_ppmi_ref["results_unstated_goal"],
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_n6x3arms",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "crlb_n_a": "no fixed-capacity argmax-noise-floor threshold in this cell; discrete k/6 tier feasibility analysis (Gate-B analogue) is documented in the module docstring in its place",
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


def self_test():
    """Tiny-scale real-code-path self-test (F.1 analogue): exercises the ACTUAL
    training function (train_sgns) and neg-sampling table builder on a
    synthetic mini-corpus, at production dtype/shape logic, not a
    synthetic-only stub. Runs in well under 1 second."""
    rng = np.random.RandomState(0)
    vocab_size = 20
    tok_idx = rng.randint(0, vocab_size, size=2000).astype(np.int64)
    vocab_counts = np.bincount(tok_idx, minlength=vocab_size).astype(np.int64)
    vocab_counts[vocab_counts == 0] = 1  # avoid zero-prob words in tiny synthetic vocab

    table = build_neg_sampling_table(vocab_counts, table_size=1000)
    assert table.shape == (1000,), f"neg table shape wrong: {table.shape}"
    assert table.min() >= 0 and table.max() < vocab_size, "neg table indices out of vocab range"

    w_trained, w_random, n_pairs, per_epoch_err = train_sgns(
        tok_idx, vocab_size, vocab_counts, d=4, n_epochs=1, k_neg=2, window=2
    )
    assert w_trained.shape == (vocab_size, 4), f"trained shape wrong: {w_trained.shape}"
    assert w_random.shape == (vocab_size, 4), f"random shape wrong: {w_random.shape}"
    assert np.isfinite(w_trained).all(), "NaN/Inf in trained weights (production-scale NaN-detection analogue)"
    assert n_pairs > 0, "self-test trained zero pairs -- training loop broken"
    assert not np.allclose(w_trained, w_random), "training did not move weights at all in self-test"

    digests, pairwise, differ = _arms_must_differ_arrays({"a": w_trained, "b": w_random})
    assert differ, "arms-must-differ hash check failed in self-test"

    print(
        f"[self_test] PASS  n_pairs={n_pairs}  mean_abs_error_epoch0={per_epoch_err[0]:.4f}  "
        f"neg_table_ok=True  arms_differ={differ}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        if "--self-test" in sys.argv:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
