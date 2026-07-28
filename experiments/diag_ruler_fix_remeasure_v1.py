"""RULER-FIX RE-MEASURE + CALIBRATION (2026-07-28). NOT a dispatched cell. No queue, no GPU, no
bank/push. Standalone script; run to completion in the foreground and read results.json off disk.

WHY: eval_battery_relational_cloze_v7.py's fit_linear_decoder used PLAIN (unweighted) CE. TRAIN's
label distribution is skewed (one relation ~65-66% of items at this regime), so the linear decoder
COLLAPSED to predicting the majority class -- LEARNED_DECODER(coherent) == LEARNED_DECODER
(scrambled) == MAJORITY_KWAY exactly (0.3448, see data/eval_battery_relational_cloze_v7/
results.json, pre-fix) -> comprehension_specific=False BY ARTIFACT, not by a real absence of
reading signal. Tonight's diag_comprehension_readout_sweep_v1.py shotgun found the fix (inverse-
class-frequency CE weighting + a balanced_acc>=chance validity gate), which is now landed directly
in eval_battery_relational_cloze_v7.fit_linear_decoder + the new _train_fit_sanity gate (this repo,
2026-07-28 commit).

THIS SCRIPT re-measures cleanly with the FIXED decoder + gate for THREE arms, sharing ONE
bundle/dataset build (encoder-independent: corpus/splits/edges/B0-table/adversarial-pool/
stratification never touch the encoder -- see V7.build_bundle/build_dataset) so the comparison is
paired (identical TRAIN instances + identical Tier-A balanced held-out items across all three):

  (a) BASELINE  -- data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt (the frozen ckpt that
      scored comprehension_specific=False under the OLD collapsed-CE decoder).
  (b) RELOBJ    -- data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt, if present:
      same architecture, retrained with a relation-aware objective -- did the objective help, now
      that the detector is no longer collapsed?
  (c) CALIBRATION -- sentence-transformers/all-MiniLM-L6-v2 (offline, HF-cache-only,
      DIAGNOSTIC-ONLY -- NOT wired into the substrate per standing USER directive against borrowed
      embeddings as an encoder). Uses the model's OWN standard mean-pooled sentence embedding (its
      native readout, the fair comparison point for an off-the-shelf sentence encoder) as the
      gestalt. This is the key calibration: if a KNOWN reader now scores comprehension_specific=
      TRUE with the FIXED decoder, the ruler is fair; if even it fails, the task construction
      (held-out-concept swap, adversarial K-way pool) is still too hard and needs revisiting, not
      just the decoder.

For (a)/(b), gestalts are V7's own ContentRoleReadout(mode="fixed") over the frozen model's
per-token hiddens (V7.compute_gestalts, unchanged -- identical to what run_battery uses). For (c),
gestalts are SentenceTransformer.encode() (mean-pooling over the model's own tokenizer + attention
mask, L2-normalized) -- the standard SBERT sentence-embedding convention for that model family.

REUSE (wiring only, no new mechanism beyond the encoder-swap + calibration arm): V7.build_bundle /
build_dataset / annotate_items / stratify_balanced / compute_gestalts / fit_linear_decoder (FIXED,
class-weighted) / _train_fit_sanity (NEW gate) / relation_centroids / score_pool_arms, all
imported directly; diag_readout_limit_probe_v1.load_frozen_encoder (frozen ckpt loader);
exp_unified_self_learning_loop_v2._scramble_words (scramble control). New code: the MiniLM
gestalt path and the per-arm orchestration loop.

LEAK-PROOFING: identical to V7 (Tier-A subjects never in TRAIN, asserted inside V7.build_dataset).
The calibration arm's decoder is fit ONLY on the SAME TRAIN instances V7 already leak-proofed --
no additional leak surface is introduced by swapping the encoder.
"""
from __future__ import annotations

import os
import sys
import time
import traceback
from datetime import datetime, timezone

# Force fully offline HF usage before any transformers/sentence_transformers import -- this arm is
# DIAGNOSTIC/calibration-only against a LOCALLY CACHED model; it must never attempt a network call.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import numpy as np
import torch
import json  # noqa: E402

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.eval_battery_relational_cloze_v7 as V7  # noqa: E402
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402

OUT_DIR = os.path.join(_REPO, "data", "diag_ruler_fix_remeasure_v1")
SEED = 20260728
CALIBRATION_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COMPREHENSION_SPECIFIC_MARGIN = 0.03  # matches V7's own threshold

BASELINE_CKPT = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")
RELOBJ_CKPT = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")

# Reduced-scale cfg (same lineage as diag_comprehension_readout_sweep_v1.SWEEP_CFG): V7's own
# FULL_CFG (max_lines=3M) took ~1300s wall for bundle+dataset alone -- too slow for a single
# foreground call. This cuts the corpus scans while keeping the IDENTICAL K-way adversarial ruler
# construction (build_dataset/annotate_items/stratify_balanced unchanged).
CFG = dict(
    min_deg=2, cap_eval_concepts=8000, heldout_count=800, min_mentions_eval=3,
    max_lines=1800000, dedup_cap=1800000, bpe_sample_lines=50, cap_mentions=16,
    max_len=32, n_freq_buckets=6, max_shards=16, encode_batch=256,
    top_n_relations=8, min_train_per_rel=5, max_sent_per_edge=2,
    K=4, pair_withhold_frac=0.15, tier_c_count_lo=5, tier_c_count_hi=5000,
    decoder_steps=400, decoder_lr=0.03, decoder_wd=0.005,
    stratify_cap_per_bucket=60, tier_bc_cap=60,
)


def _log(msg):
    print("[ruler_fix_remeasure] %s" % msg, flush=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _score_arm(name, G_train, G_a, G_as, train_y, n_labels, tier_a_bal, label_relations, cfg, seed):
    t0 = time.perf_counter()
    lin_decoder, final_loss = V7.fit_linear_decoder(
        G_train, train_y, n_labels, cfg["decoder_steps"], cfg["decoder_lr"], cfg["decoder_wd"], seed)
    t_fit = time.perf_counter() - t0
    sanity = V7._train_fit_sanity(lin_decoder, G_train, train_y, n_labels)
    centroids = V7.relation_centroids(G_train, train_y, n_labels)
    res = V7.score_pool_arms(tier_a_bal, G_a, G_as, lin_decoder, centroids, label_relations)
    decoder_margin = res["LEARNED_DECODER"] - res["LEARNED_DECODER_SCRAMBLED"]
    cosine_margin = res["COSINE_CENTROID"] - res["COSINE_CENTROID_SCRAMBLED"]
    comprehension_specific = bool(decoder_margin >= COMPREHENSION_SPECIFIC_MARGIN
                                   and sanity["decoder_valid"])
    out = dict(name=name, t_fit_s=t_fit, decoder_final_loss=final_loss,
               train_fit_sanity=sanity, cosine_margin=cosine_margin, decoder_margin=decoder_margin,
               comprehension_specific=comprehension_specific, decoder_valid=sanity["decoder_valid"])
    out.update(res)
    _log("%s: decoder_valid=%s balanced_acc=%.3f coherent=%.4f scrambled=%.4f margin=%.4f "
         "comprehension_specific=%s"
         % (name, sanity["decoder_valid"], sanity["balanced_acc"], res["LEARNED_DECODER"],
            res["LEARNED_DECODER_SCRAMBLED"], decoder_margin, comprehension_specific))
    return out


def _own_encoder_gestalts(ckpt_path, train_sents, tier_a_sents, tier_a_scr_sents, cfg, seed):
    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)
    device = torch.device("cpu")
    readout = V7.ContentRoleReadout(model.d_model, mode="fixed", seed=seed)
    G_train = V7.compute_gestalts(model, tok, spec, train_sents, cfg, readout, device)
    G_a = V7.compute_gestalts(model, tok, spec, tier_a_sents, cfg, readout, device)
    G_as = V7.compute_gestalts(model, tok, spec, tier_a_scr_sents, cfg, readout, device)
    return G_train, G_a, G_as, ckpt_meta


def _minilm_gestalts(train_sents, tier_a_sents, tier_a_scr_sents):
    from sentence_transformers import SentenceTransformer
    t0 = time.perf_counter()
    st = SentenceTransformer(CALIBRATION_MODEL_NAME, device="cpu", local_files_only=True)
    t_load = time.perf_counter() - t0
    _log("MiniLM loaded (%.1fs) dim=%d" % (t_load, st.get_sentence_embedding_dimension()))
    t0 = time.perf_counter()
    G_train = st.encode(train_sents, batch_size=64, convert_to_numpy=True,
                         normalize_embeddings=True, show_progress_bar=False).astype(np.float32)
    G_a = st.encode(tier_a_sents, batch_size=64, convert_to_numpy=True,
                     normalize_embeddings=True, show_progress_bar=False).astype(np.float32)
    G_as = st.encode(tier_a_scr_sents, batch_size=64, convert_to_numpy=True,
                      normalize_embeddings=True, show_progress_bar=False).astype(np.float32)
    t_enc = time.perf_counter() - t0
    _log("MiniLM encoded TRAIN=%d TIER_A=%d SCR=%d (%.1fs)"
         % (G_train.shape[0], G_a.shape[0], G_as.shape[0], t_enc))
    return G_train, G_a, G_as, dict(model_name=CALIBRATION_MODEL_NAME, dim=int(G_train.shape[1]),
                                     t_load_s=t_load, t_encode_s=t_enc)


def main():
    t_wall0 = time.perf_counter()
    os.makedirs(OUT_DIR, exist_ok=True)

    t0 = time.perf_counter()
    bundle = V7.build_bundle(CFG)
    dataset = V7.build_dataset(bundle, CFG)
    t_dataset = time.perf_counter() - t0
    n_labels = len(dataset["label_relations"])
    K = min(CFG["K"], n_labels)
    label_relations = dataset["label_relations"]
    global_majority_rel = dataset["b0_global_majority"]
    _log("bundle+dataset built (%.1fs) n_labels=%d K=%d train=%d tier_a_raw=%d"
         % (t_dataset, n_labels, K, len(dataset["train_instances"]), len(dataset["tier_a_instances"])))

    tier_a_items = V7.annotate_items(dataset["tier_a_instances"], dataset, K)
    for it in tier_a_items:
        it["_global_majority_in_pool"] = global_majority_rel if global_majority_rel in it["pool"] else None
    tier_a_bal, strat_meta = V7.stratify_balanced(tier_a_items, K, CFG["stratify_cap_per_bucket"], SEED + 601)
    _log("TIER_A stratified: n=%d meta=%s" % (len(tier_a_bal), strat_meta))
    if len(tier_a_bal) < 20:
        raise RuntimeError("too few TIER_A balanced items (%d) -- widen CFG" % len(tier_a_bal))

    b0_kway = float(np.mean([it["b0_pred"] == it["ri"] for it in tier_a_bal]))
    chance = 1.0 / K
    b0_near_chance = bool(abs(b0_kway - chance) <= 0.10)
    _log("B0_KWAY (identity-only memorization baseline) on Tier-A balanced = %.4f (chance=%.4f) "
         "near_chance=%s -- UNCHANGED by the decoder fix (B0 never touches the decoder)"
         % (b0_kway, chance, b0_near_chance))

    train_sents = [s for (_si, _ri, _oi, s) in dataset["train_instances"]]
    train_y = np.array([ri for (_si, ri, _oi, _s) in dataset["train_instances"]], dtype=np.int64)
    tier_a_sents = [it["sent"] for it in tier_a_bal]
    srng = np.random.default_rng(SEED + 202)
    tier_a_scr_sents = [LOOP2._scramble_words(it["sent"], srng) for it in tier_a_bal]

    results = {}

    # --- (a) BASELINE frozen v2 ckpt ---
    t0 = time.perf_counter()
    G_train, G_a, G_as, ckpt_meta_a = _own_encoder_gestalts(
        BASELINE_CKPT, train_sents, tier_a_sents, tier_a_scr_sents, CFG, SEED)
    _log("BASELINE gestalts computed (%.1fs)" % (time.perf_counter() - t0))
    results["BASELINE"] = _score_arm("BASELINE", G_train, G_a, G_as, train_y, n_labels,
                                      tier_a_bal, label_relations, CFG, SEED)
    results["BASELINE"]["ckpt_path"] = BASELINE_CKPT
    results["BASELINE"]["ckpt_meta"] = ckpt_meta_a

    # --- (b) RELOBJ retrain ckpt, if present ---
    if os.path.exists(RELOBJ_CKPT):
        t0 = time.perf_counter()
        G_train_b, G_a_b, G_as_b, ckpt_meta_b = _own_encoder_gestalts(
            RELOBJ_CKPT, train_sents, tier_a_sents, tier_a_scr_sents, CFG, SEED)
        _log("RELOBJ gestalts computed (%.1fs)" % (time.perf_counter() - t0))
        results["RELOBJ"] = _score_arm("RELOBJ", G_train_b, G_a_b, G_as_b, train_y, n_labels,
                                        tier_a_bal, label_relations, CFG, SEED)
        results["RELOBJ"]["ckpt_path"] = RELOBJ_CKPT
        results["RELOBJ"]["ckpt_meta"] = ckpt_meta_b
    else:
        _log("RELOBJ ckpt not found at %s -- skipping arm" % RELOBJ_CKPT)
        results["RELOBJ"] = None

    # --- (c) CALIBRATION: real cached transformer, diagnostic-only ---
    t0 = time.perf_counter()
    G_train_c, G_a_c, G_as_c, minilm_meta = _minilm_gestalts(train_sents, tier_a_sents, tier_a_scr_sents)
    _log("CALIBRATION (MiniLM) gestalts computed (%.1fs)" % (time.perf_counter() - t0))
    results["CALIBRATION_MINILM"] = _score_arm("CALIBRATION_MINILM", G_train_c, G_a_c, G_as_c,
                                                train_y, n_labels, tier_a_bal, label_relations, CFG, SEED)
    results["CALIBRATION_MINILM"]["model_meta"] = minilm_meta

    calibration_passes = bool(results["CALIBRATION_MINILM"]["comprehension_specific"])
    baseline_flips_true = bool(results["BASELINE"]["comprehension_specific"])
    relobj_flips_true = bool(results["RELOBJ"]["comprehension_specific"]) if results["RELOBJ"] else None

    if not results["BASELINE"]["decoder_valid"] or not results["CALIBRATION_MINILM"]["decoder_valid"]:
        bottom_line = "DECODER_STILL_UNDERFIT_INCONCLUSIVE"
    elif not calibration_passes:
        bottom_line = "RULER_STILL_UNFAIR_TASK_TOO_HARD_EVEN_FOR_KNOWN_READER"
    elif baseline_flips_true:
        bottom_line = "OLD_FALSE_WAS_ARTIFACT_RULER_NOW_FAIR_AND_ENCODER_SHOWS_SIGNAL"
    else:
        bottom_line = "OLD_FALSE_CONFIRMED_REAL_RULER_NOW_FAIR_BUT_ENCODER_STILL_SHOWS_NO_SIGNAL"

    verdict_msg = ("ruler-fix re-measure: chance=%.3f B0_KWAY=%.4f (near_chance=%s, unaffected by "
                   "decoder fix) | BASELINE decoder_valid=%s comprehension_specific=%s margin=%.4f "
                   "| RELOBJ %s | CALIBRATION_MINILM decoder_valid=%s comprehension_specific=%s "
                   "margin=%.4f | BOTTOM_LINE=%s"
                   % (chance, b0_kway, b0_near_chance, results["BASELINE"]["decoder_valid"],
                      baseline_flips_true, results["BASELINE"]["decoder_margin"],
                      ("decoder_valid=%s comprehension_specific=%s margin=%.4f"
                       % (results["RELOBJ"]["decoder_valid"], relobj_flips_true,
                          results["RELOBJ"]["decoder_margin"])) if results["RELOBJ"] else "SKIPPED_NO_CKPT",
                      results["CALIBRATION_MINILM"]["decoder_valid"], calibration_passes,
                      results["CALIBRATION_MINILM"]["decoder_margin"], bottom_line))
    _log("VERDICT: %s" % verdict_msg)

    payload = dict(
        script=os.path.basename(_THIS), ts_iso=_now(), pid=os.getpid(), cfg=CFG, seed=SEED,
        n_labels=n_labels, K=K, label_relations=label_relations, chance_1_over_k=chance,
        n_train_instances=len(dataset["train_instances"]), n_tier_a_balanced=len(tier_a_bal),
        tier_a_strat_meta=strat_meta, b0_kway=b0_kway, b0_near_chance=b0_near_chance,
        t_stage=dict(dataset_build_s=t_dataset),
        results=results, bottom_line=bottom_line, verdict_msg=verdict_msg,
        note_caveat=("Reduced-scale harness (cap_eval_concepts=%s, max_lines=%s, decoder_steps=%s) "
                     "for CPU-minutes turnaround, sharing V7's adversarial K-way construction -- a "
                     "diagnostic/instrument-validation run, not a capability-scale claim. All three "
                     "arms score the IDENTICAL Tier-A balanced item set (same adversarial pools, "
                     "same TRAIN instances) so this is a fair, paired comparison. MiniLM is used "
                     "DIAGNOSTIC-ONLY for ruler calibration -- it is NOT wired into the substrate "
                     "and is not being proposed as the encoder (per standing USER directive against "
                     "borrowed embeddings as the substrate's encoder)."
                     % (CFG["cap_eval_concepts"], CFG["max_lines"], CFG["decoder_steps"])),
        elapsed_s_total=time.perf_counter() - t_wall0,
    )
    tmp = os.path.join(OUT_DIR, "results.json.tmp")
    final = os.path.join(OUT_DIR, "results.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)
    _log("wrote %s (elapsed %.1fs)" % (final, payload["elapsed_s_total"]))
    return payload


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        traceback.print_exc()
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "crash.txt"), "w", encoding="utf-8") as f:
            f.write("%s: %s\n\n%s" % (type(e).__name__, e, traceback.format_exc()))
        sys.exit(1)
