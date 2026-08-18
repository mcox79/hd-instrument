"""Derived filler-typing for single-edge substrate-native grounding (v1).

Closes the single-edge grounding proof's one remaining ceiling: the filler-TYPE for a candidate noun
(ARTIFACT vs LOCATION) was HAND-STIPULATED (a dict) in the original cell. Here it is DERIVED from the
noun's own LEARNED codebook encoding -- integrating three already-credited/VET'd pieces UNMODIFIED:

  1. exp_single_edge_grounding_hd_binding_verbnet_v1 (`se`): the FHRR storage/recall skeleton
     (build_atoms/build_webs_and_keys -> WEB_BUILD_EDGE = bind(KEY_BUILD, TYPE_ARTIFACT), unbind +
     atoms.similarity cleanup). REUSED BYTE-IDENTICAL (same fixed seed) -- storage/recall never changes.
  2. exp_learned_codebook_generalization_gate_v1 (`cb`, atom 29368): the real text8 PPMI+TruncatedSVD
     codebook pipeline (held-out relatedness AUC=0.927). REUSED UNMODIFIED to build the TRUE codebook.
  3. exp_novel_atom_real_codebook_generalization_v1 (`na`, atoms 29379-82): the capacity-gated ridge-
     induction mechanism (fit on SEEN words' features -> true codes; apply to a held-out word's
     PARTIAL/noisy feature draw). REUSED UNMODIFIED to recover a genuinely-novel test noun's code.

THE 4 TYPING ARMS (one variable = how type_vec(candidate_noun) is obtained; storage/recall identical):
  DERIVED  : cos(induced_code(test_noun), prototype_ARTIFACT) vs cos(..., prototype_LOCATION);
             prototypes = mean(true codebook codes of curated EXEMPLAR words); induced_code = ridge map
             W (fit on SEEN words only) applied to the test noun's partial/noisy feature draw [genuine].
  NAIVE    : 1-NN over the SAME exemplar set's full features vs the test noun's partial feature draw
             [fair capacity-matched must-beat baseline, per atom 29382].
  HAND     : oracle true category [ceiling reference].
  RANDOM   : cos to two independent random-Gaussian "prototypes", uncorrelated with content
             [must-fail format-only control].

Pre-reg: preregs/2026-07-20_derived_filler_typing_single_edge_grounding_v1.md

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import torch  # noqa: E402

ANCHOR_NAME = "derived_filler_typing_single_edge_grounding_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import atoms as A  # noqa: E402
from hdlab import binding as B  # noqa: E402
import experiments.exp_single_edge_grounding_hd_binding_verbnet_v1 as se  # noqa: E402
import experiments.exp_learned_codebook_generalization_gate_v1 as cb  # noqa: E402
import experiments.exp_novel_atom_real_codebook_generalization_v1 as na  # noqa: E402

# --------------------------------------------------------------------------- config
N_CODE = 1024                # codebook/prototype target dim (matches na.N / cb usage)
RI_SPARSITY = 10
FEAT_PROJ_SEED = 9101
CODE_SEED = 7
RIDGE_ALPHA = 10.0
ALPHA_FRAC = 0.3
MIN_OCC_PER_DRAW = 20
RANDOM_PROTO_SEED = 4242
MARGIN_THRESH = se.MARGIN_THRESH  # 0.10, same threshold as the reused single-edge cell

ARTIFACT_POOL = ["church", "temple", "stadium", "tower", "monastery", "palace", "cathedral",
                 "castle", "factory", "monument", "fortress", "chapel", "pyramid", "lighthouse",
                 "windmill", "mansion", "cottage", "warehouse", "shrine", "citadel"]
LOCATION_POOL = ["island", "mountain", "desert", "peninsula", "plateau", "forest", "delta",
                  "harbor", "prairie", "reef", "cliff", "swamp", "volcano", "canyon", "glacier",
                  "lagoon", "tundra", "marsh", "meadow", "hillside"]

N_EXEMPLAR_ARTIFACT = 6
N_TEST_ARTIFACT = 4
N_EXEMPLAR_LOCATION = 5
N_TEST_LOCATION = 4

STORED_SENTENCE_NOUNS = {"fort", "cabin", "bridge", "dam", "house", "hut", "river", "lake",
                          "valley", "kitchen", "barn", "garden", "soup", "bread", "cake"}

SENTENCE_TEMPLATES = [
    "The team built a {a} near the {l}.",
    "The workers built a {a} beside the {l}.",
    "The settlers built a {a} across the {l}.",
    "The monks built a {a} within the {l}.",
]

ARMS = ["derived", "naive", "hand", "random"]

DFEAT_CURVE_FULL = [256, 512, 1024]
DFEAT_CURVE_SMOKE = [256, 1024]
SEEDS = [7, 13, 19]
K_DRAWS_FULL = 30
K_DRAWS_SMOKE = 10

FULL_CFG = dict(n_tokens=8_000_000, vocab_size=10000, window=5, min_count=5)
SMOKE_CFG = dict(n_tokens=1_500_000, vocab_size=6000, window=5, min_count=5)

# Pre-registered bands (headline = D_FEAT=1024; see prereg; NOT tuned to pass).
HP_TYPING_ACC_MIN = 0.60
HP_VS_NAIVE_MARGIN_MIN = 0.05
HP_VS_RANDOM_MARGIN_MIN = 0.15
HP_RANDOM_AT_CHANCE_MAX = 0.65
HP_SENTENCE_RESOLUTION_MIN = 0.50
HF_VS_NAIVE_MARGIN_MAX = 0.00
HF_TYPING_ACC_FLOOR = 0.30
CEIL_CHECK_MIN = 0.95


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(marker, fh)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def _normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


# --------------------------------------------------------------------------- word-pool construction
def build_word_pools(w2i, counts, n_exemplar_artifact=N_EXEMPLAR_ARTIFACT, n_test_artifact=N_TEST_ARTIFACT,
                      n_exemplar_location=N_EXEMPLAR_LOCATION, n_test_location=N_TEST_LOCATION):
    """Filter candidate pools to in-vocab words, rank by descending frequency (deterministic:
    (-count, word) tuple sort, no hash()/list(set())), split into disjoint EXEMPLAR / TEST slices.
    Fail loud (RuntimeError) if coverage is insufficient -- never silently truncate."""
    def present_sorted(pool):
        pres = [(w, w2i[w], float(counts[w2i[w]])) for w in pool if w in w2i]
        pres.sort(key=lambda x: (-x[2], x[0]))
        return pres

    art = present_sorted(ARTIFACT_POOL)
    loc = present_sorted(LOCATION_POOL)
    need_art = n_exemplar_artifact + n_test_artifact
    need_loc = n_exemplar_location + n_test_location
    if len(art) < need_art:
        raise RuntimeError(f"INSUFFICIENT_ARTIFACT_VOCAB_COVERAGE: {len(art)} present (need >= "
                            f"{need_art}): {art}")
    if len(loc) < need_loc:
        raise RuntimeError(f"INSUFFICIENT_LOCATION_VOCAB_COVERAGE: {len(loc)} present (need >= "
                            f"{need_loc}): {loc}")

    exemplar_artifact = art[:n_exemplar_artifact]
    test_artifact = art[n_exemplar_artifact:n_exemplar_artifact + n_test_artifact]
    exemplar_location = loc[:n_exemplar_location]
    test_location = loc[n_exemplar_location:n_exemplar_location + n_test_location]

    ex_words = {w for w, _, _ in exemplar_artifact + exemplar_location}
    test_words = {w for w, _, _ in test_artifact + test_location}
    assert ex_words.isdisjoint(test_words), (
        f"DESIGN_GATE_VIOLATION: exemplar/test overlap: {ex_words & test_words}")
    assert test_words.isdisjoint(STORED_SENTENCE_NOUNS), (
        f"DESIGN_GATE_VIOLATION: test noun leaks into original stored-sentence lexicon: "
        f"{test_words & STORED_SENTENCE_NOUNS}")
    assert ex_words.isdisjoint(STORED_SENTENCE_NOUNS), (
        f"DESIGN_GATE_VIOLATION: exemplar leaks into original stored-sentence lexicon: "
        f"{ex_words & STORED_SENTENCE_NOUNS}")

    return exemplar_artifact, test_artifact, exemplar_location, test_location


# --------------------------------------------------------------------------- per-D_FEAT-point classifier
def run_dfeat_point(dfeat, V, ppmi, ids, true_codes_np, positions, exemplar_artifact, test_artifact,
                     exemplar_location, test_location, window, seeds, k_draws, col_stats, output_dir):
    """Rebuilds the D_FEAT-dependent pieces (R_feat, feat_full_all, ridge map W) once; classifies every
    test word under DERIVED / NAIVE / RANDOM / HAND, multi-sampled over seeds x k_draws partial-feature
    draws. Reuses na.ridge_fit/ridge_predict/feat_from_raw_row/build_partial_cooc_row/
    cb.sparse_ternary_projection UNCHANGED."""
    R_feat = cb.sparse_ternary_projection(V, dfeat, RI_SPARSITY, FEAT_PROJ_SEED)
    feat_full_all = (ppmi @ R_feat).toarray().astype(np.float64)
    nrm = np.linalg.norm(feat_full_all, axis=1, keepdims=True)
    nrm[nrm < 1e-12] = 1.0
    feat_full_all = feat_full_all / nrm

    exemplar_artifact_idx = [i for _, i, _ in exemplar_artifact]
    exemplar_location_idx = [i for _, i, _ in exemplar_location]
    test_words = [(w, i, "ARTIFACT") for w, i, _ in test_artifact] + \
                 [(w, i, "LOCATION") for w, i, _ in test_location]
    test_idx_set = {i for _, i, _ in test_words}

    seen_idx = np.array([i for i in range(V) if i not in test_idx_set])
    X_train = feat_full_all[seen_idx]
    Y_train = true_codes_np[seen_idx]
    W_ridge = na.ridge_fit(X_train, Y_train, RIDGE_ALPHA)

    prototype_artifact = _normalize(true_codes_np[exemplar_artifact_idx].mean(axis=0))
    prototype_location = _normalize(true_codes_np[exemplar_location_idx].mean(axis=0))

    proto_rng = np.random.default_rng(RANDOM_PROTO_SEED + dfeat)  # dfeat-offset so each point gets its
                                                                    # own fixed-but-distinct random draw
    random_proto_a = _normalize(proto_rng.standard_normal(N_CODE))
    random_proto_l = _normalize(proto_rng.standard_normal(N_CODE))

    exemplar_feats_full = feat_full_all[exemplar_artifact_idx + exemplar_location_idx]
    exemplar_labels = ["ARTIFACT"] * len(exemplar_artifact_idx) + ["LOCATION"] * len(exemplar_location_idx)

    # per (word, seed, draw) -> {arm: predicted_type}
    per_word_draws = {}
    n_units = 0
    for word, idx, true_type in test_words:
        pos_i = positions[idx]
        n_take = min(max(MIN_OCC_PER_DRAW, int(ALPHA_FRAC * len(pos_i))), len(pos_i))
        draws = []
        for seed in seeds:
            rng = np.random.default_rng(seed * 100000 + int(idx))  # fixed-integer composition (PROT-023)
            for _d in range(k_draws):
                subset = rng.choice(pos_i, size=n_take, replace=False)
                raw_row = na.build_partial_cooc_row(ids, subset, V, window)
                feat = na.feat_from_raw_row(raw_row, R_feat, *col_stats)

                pred = na.ridge_predict(W_ridge, feat[None, :])[0]
                predn = _normalize(pred)
                cos_a = float(predn @ prototype_artifact)
                cos_l = float(predn @ prototype_location)
                derived_type = "ARTIFACT" if cos_a >= cos_l else "LOCATION"

                dists = np.linalg.norm(exemplar_feats_full - feat[None, :], axis=1)
                naive_type = exemplar_labels[int(dists.argmin())]

                cos_ra = float(predn @ random_proto_a)
                cos_rl = float(predn @ random_proto_l)
                random_type = "ARTIFACT" if cos_ra >= cos_rl else "LOCATION"

                draws.append({"seed": seed, "derived": derived_type, "naive": naive_type,
                              "hand": true_type, "random": random_type})
                n_units += len(ARMS)  # one classification decision per arm per draw (cardinality unit)
        per_word_draws[word] = {"idx": int(idx), "true_type": true_type, "draws": draws}
        _hb(output_dir, f"dfeat={dfeat} word={word} true={true_type}: "
                         f"derived_acc={np.mean([d['derived'] == true_type for d in draws]):.3f} "
                         f"naive_acc={np.mean([d['naive'] == true_type for d in draws]):.3f} "
                         f"random_acc={np.mean([d['random'] == true_type for d in draws]):.3f}")

    # aggregate typing accuracy per arm (+ per-seed for the multi-seed-flip gate)
    typing_acc = {}
    typing_acc_per_seed = {}
    for arm in ARMS:
        all_correct = []
        per_seed_correct = {s: [] for s in seeds}
        for word, rec in per_word_draws.items():
            for d in rec["draws"]:
                c = (d[arm] == rec["true_type"])
                all_correct.append(c)
                per_seed_correct[d["seed"]].append(c)
        typing_acc[arm] = float(np.mean(all_correct))
        typing_acc_per_seed[arm] = {str(s): float(np.mean(v)) if v else float("nan")
                                     for s, v in per_seed_correct.items()}

    # arms-must-differ (predicted-type arrays, in fixed word/seed/draw order)
    pred_arrays = {arm: [] for arm in ARMS}
    for word in sorted(per_word_draws):
        for d in per_word_draws[word]["draws"]:
            for arm in ARMS:
                pred_arrays[arm].append(d[arm])
    pred_hashes = {arm: hashlib.sha256("|".join(pred_arrays[arm]).encode()).hexdigest() for arm in ARMS}

    return {
        "dfeat": dfeat,
        "typing_acc": typing_acc,
        "typing_acc_per_seed": typing_acc_per_seed,
        "n_units": n_units,
        "per_word_draws": per_word_draws,
        "pred_hashes": pred_hashes,
        "prototype_artifact": prototype_artifact,
        "prototype_location": prototype_location,
        "random_proto_a": random_proto_a,
        "random_proto_l": random_proto_l,
        "W_ridge": W_ridge,
        "R_feat": R_feat,
        "col_stats": col_stats,
    }


# --------------------------------------------------------------------------- sentence-resolution scoring
def score_sentences(atom, webs, keys, dfeat_point, test_artifact, test_location, seeds, k_draws,
                     output_dir):
    """Feeds each arm's typing decision into the REUSED, byte-identical single-edge FHRR storage/recall
    (se.build_atoms/build_webs_and_keys, unbind + atoms.similarity, MARGIN_THRESH) -- storage/recall
    code is untouched; only which TYPE atom is selected for each candidate changes per arm."""
    web = webs["WEB_BUILD_EDGE"]
    key = keys["key_build"]
    recovered = B.unbind(web, key)

    per_word_draws = dfeat_point["per_word_draws"]
    n_sent = min(len(test_artifact), len(test_location))
    per_sentence = []
    per_arm_resolved = {arm: [] for arm in ARMS}

    for i in range(n_sent):
        a_word, a_idx, _ = test_artifact[i]
        l_word, l_idx, _ = test_location[i]
        sentence = SENTENCE_TEMPLATES[i % len(SENTENCE_TEMPLATES)].format(a=a_word, l=l_word)
        a_draws = per_word_draws[a_word]["draws"]
        l_draws = per_word_draws[l_word]["draws"]
        n_trials = min(len(a_draws), len(l_draws))
        sent_rows = {arm: [] for arm in ARMS}
        for t in range(n_trials):
            for arm in ARMS:
                type_a = a_draws[t][arm]
                type_l = l_draws[t][arm]
                s_true = float(A.similarity(recovered, atom[f"TYPE_{type_a}"]))
                s_false = float(A.similarity(recovered, atom[f"TYPE_{type_l}"]))
                margin = s_true - s_false
                resolved = bool(margin >= MARGIN_THRESH)  # true patient is always the artifact candidate
                sent_rows[arm].append({"margin": round(margin, 6), "resolved_correct": resolved,
                                        "type_a": type_a, "type_l": type_l})
                per_arm_resolved[arm].append(resolved)
        per_sentence.append({
            "sentence": sentence, "true_patient": a_word, "false_candidate": l_word,
            "arm_resolution_rate": {arm: float(np.mean([r["resolved_correct"] for r in sent_rows[arm]]))
                                     for arm in ARMS},
        })
        _hb(output_dir, f"sentence[{i}]='{sentence}' "
                        f"resolution_rate={ {arm: round(float(np.mean([r['resolved_correct'] for r in sent_rows[arm]])), 3) for arm in ARMS} }")

    resolution_acc = {arm: float(np.mean(per_arm_resolved[arm])) if per_arm_resolved[arm] else float("nan")
                       for arm in ARMS}
    return per_sentence, resolution_acc


# --------------------------------------------------------------------------- runner
def run(output_dir, cfg, dfeat_curve, seeds, k_draws, run_mode):
    t0 = time.perf_counter()
    expected_n_units = (len(dfeat_curve) * len(ARMS) * (N_TEST_ARTIFACT + N_TEST_LOCATION)
                         * len(seeds) * k_draws)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"building real world (shared across D_FEAT curve): n_tokens={cfg['n_tokens']} "
                     f"vocab_size={cfg['vocab_size']}")
    tokens = cb.load_tokens(cfg["n_tokens"])
    w2i, counts = cb.build_vocab(tokens, vocab_size=cfg["vocab_size"], min_count=cfg["min_count"])
    V = len(w2i)
    ids = np.fromiter((w2i.get(t, -1) for t in tokens), dtype=np.int64, count=len(tokens))
    cooc = cb.build_cooc(tokens, w2i, cfg["window"])
    ppmi = cb.build_ppmi(cooc)
    true_codes_np = cb.build_codebook("ppmi_svd", cooc, ppmi, V, N_CODE, CODE_SEED, RI_SPARSITY)
    col_stats = na.compute_ppmi_col_stats(cooc)
    _hb(output_dir, f"world built: V={V}")

    exemplar_artifact, test_artifact, exemplar_location, test_location = build_word_pools(w2i, counts)
    _hb(output_dir, f"exemplar_artifact={[w for w,_,_ in exemplar_artifact]} "
                    f"test_artifact={[w for w,_,_ in test_artifact]}")
    _hb(output_dir, f"exemplar_location={[w for w,_,_ in exemplar_location]} "
                    f"test_location={[w for w,_,_ in test_location]}")

    positions = {i: np.where(ids == i)[0] for _, i, _ in (test_artifact + test_location)}
    for w, i, t in test_artifact + test_location:
        n_pos = len(positions[i])
        assert n_pos >= MIN_OCC_PER_DRAW, (
            f"TEST_WORD_TOO_RARE: {w!r} has only {n_pos} occurrence positions (need >= "
            f"{MIN_OCC_PER_DRAW} for a partial draw)")

    # mechanics sanity: the REUSED single-edge FHRR storage/recall must still recover correctly here
    atom = se.build_atoms()
    webs, keys = se.build_webs_and_keys(atom)
    se.mechanism_integrity_check(webs)
    se_digests = se.arms_differ_hash(webs)
    recovered_check = B.unbind(webs["WEB_BUILD_EDGE"], keys["key_build"])
    ceiling_check_val = float(A.similarity(recovered_check, atom["TYPE_ARTIFACT"]))
    baseline_in_band = ceiling_check_val >= CEIL_CHECK_MIN
    _hb(output_dir, f"mechanics sanity (reused se storage/recall): ceiling_check={ceiling_check_val:.4f}")

    by_dfeat = {}
    n_units_done_total = 0
    for dfeat in dfeat_curve:
        _hb(output_dir, f"=== D_FEAT={dfeat} ===")
        pt = run_dfeat_point(dfeat, V, ppmi, ids, true_codes_np, positions, exemplar_artifact,
                              test_artifact, exemplar_location, test_location, cfg["window"], seeds,
                              k_draws, col_stats, output_dir)
        by_dfeat[str(dfeat)] = pt
        n_units_done_total += pt["n_units"]

    cardinality_ok = (n_units_done_total == expected_n_units)

    # arms-must-differ across the curve (predicted-type-array hashes)
    arms_differ_all = True
    arms_differ_detail = {}
    arms_differ_exempted = []
    for dfeat in dfeat_curve:
        hd = by_dfeat[str(dfeat)]["pred_hashes"]
        acc = by_dfeat[str(dfeat)]["typing_acc"]
        for i in range(len(ARMS)):
            for j in range(i + 1, len(ARMS)):
                a, b = ARMS[i], ARMS[j]
                key = f"dfeat{dfeat}__{a}_vs_{b}"
                same = hd[a] == hd[b]
                arms_differ_detail[key] = not same
                if same:
                    if acc[a] >= 0.95 and acc[b] >= 0.95:
                        arms_differ_exempted.append({"dfeat": dfeat, "pair": [a, b],
                                                      "rationale": "both near-ceiling; identical "
                                                                    "predictions indicates ceiling-"
                                                                    "matching, not a bug",
                                                      "acc_a": acc[a], "acc_b": acc[b]})
                    else:
                        arms_differ_all = False

    # headline (last point of the curve) sentence-resolution scoring
    headline_dfeat = dfeat_curve[-1]
    hp = by_dfeat[str(headline_dfeat)]
    per_sentence, resolution_acc = score_sentences(atom, webs, keys, hp, test_artifact, test_location,
                                                    seeds, k_draws, output_dir)

    headline_typing_acc = hp["typing_acc"]
    headline_margin_vs_naive = headline_typing_acc["derived"] - headline_typing_acc["naive"]
    headline_margin_vs_random = headline_typing_acc["derived"] - headline_typing_acc["random"]
    per_seed_margins = [hp["typing_acc_per_seed"]["derived"][str(s)] - hp["typing_acc_per_seed"]["naive"][str(s)]
                        for s in seeds]
    all_seeds_positive = all(m > 0 for m in per_seed_margins)

    margins_by_point = [by_dfeat[str(d)]["typing_acc"]["derived"] - by_dfeat[str(d)]["typing_acc"]["naive"]
                        for d in dfeat_curve]
    if margins_by_point[0] > 0 and margins_by_point[-1] > 0:
        flip_classification = "POSITIVE_THROUGHOUT_CURVE"
    elif margins_by_point[0] <= 0 and margins_by_point[-1] > HF_VS_NAIVE_MARGIN_MAX:
        flip_classification = "FLIPS_POSITIVE_WITH_CAPACITY"
    elif margins_by_point[0] <= 0 and margins_by_point[-1] <= 0 and margins_by_point[-1] > margins_by_point[0]:
        flip_classification = "CONVERGES_TOWARD_ZERO_BUT_DOES_NOT_BEAT"
    elif margins_by_point[0] <= 0 and margins_by_point[-1] <= margins_by_point[0]:
        flip_classification = "NEGATIVE_THROUGHOUT_NO_IMPROVEMENT_WITH_CAPACITY"
    else:
        flip_classification = "NEGATIVE_THROUGHOUT_NONMONOTONIC"

    random_beats_derived = headline_typing_acc["random"] >= headline_typing_acc["derived"]

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ_all:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band:
        verdict = "HARD_FAIL_MECHANICS_SANITY_CEILING_CHECK_BELOW_BAND"
    elif random_beats_derived:
        verdict = "HARD_FAIL_RANDOM_PROTOTYPE_BEATS_DERIVED_MECHANISM_VACUOUS"
    elif headline_margin_vs_naive <= HF_VS_NAIVE_MARGIN_MAX:
        verdict = "HARD_FAIL_DERIVED_TYPING_DOES_NOT_BEAT_NAIVE_NN_AT_D_FEAT_1024"
    elif headline_typing_acc["derived"] <= HF_TYPING_ACC_FLOOR:
        verdict = "HARD_FAIL_DERIVED_TYPING_COLLAPSES_ON_NOVEL_NOUNS"
    elif (headline_typing_acc["derived"] >= HP_TYPING_ACC_MIN
          and headline_margin_vs_naive >= HP_VS_NAIVE_MARGIN_MIN and all_seeds_positive
          and headline_margin_vs_random >= HP_VS_RANDOM_MARGIN_MIN
          and headline_typing_acc["random"] <= HP_RANDOM_AT_CHANCE_MAX
          and resolution_acc["derived"] >= HP_SENTENCE_RESOLUTION_MIN):
        verdict = "HARD_PASS_DERIVED_TYPING_GROUNDING"
    else:
        verdict = "MIDDLE_BAND_DERIVED_TYPING_PARTIAL"

    elapsed = time.perf_counter() - t0
    typing_curve = {arm: [round(by_dfeat[str(d)]["typing_acc"][arm], 4) for d in dfeat_curve]
                     for arm in ARMS}
    margin_curve = [round(m, 4) for m in margins_by_point]

    verdict_msg = (
        f"HEADLINE D_FEAT={headline_dfeat}: typing_acc derived={headline_typing_acc['derived']:.3f} "
        f"naive={headline_typing_acc['naive']:.3f} hand={headline_typing_acc['hand']:.3f} "
        f"random={headline_typing_acc['random']:.3f} | margin_vs_naive={headline_margin_vs_naive:.4f} "
        f"(per_seed={[round(m,4) for m in per_seed_margins]} all_positive={all_seeds_positive}) "
        f"margin_vs_random={headline_margin_vs_random:.4f} | "
        f"sentence_resolution_acc derived={resolution_acc['derived']:.3f} "
        f"naive={resolution_acc['naive']:.3f} hand={resolution_acc['hand']:.3f} "
        f"random={resolution_acc['random']:.3f} | CURVE D_FEAT={list(dfeat_curve)}: "
        f"derived={typing_curve['derived']} naive={typing_curve['naive']} margin={margin_curve} | "
        f"flip_classification={flip_classification} | mechanics_ceiling_check={ceiling_check_val:.4f} "
        f"| cardinality_ok={cardinality_ok} ({n_units_done_total}/{expected_n_units}) "
        f"arms_differ={arms_differ_all}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:220]}", "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {**cfg, "N_CODE": N_CODE, "RI_SPARSITY": RI_SPARSITY, "RIDGE_ALPHA": RIDGE_ALPHA,
                   "ALPHA_FRAC": ALPHA_FRAC, "MIN_OCC_PER_DRAW": MIN_OCC_PER_DRAW, "seeds": seeds,
                   "k_draws": k_draws, "dfeat_curve": list(dfeat_curve), "V": V,
                   "exemplar_artifact": [w for w, _, c in exemplar_artifact],
                   "test_artifact": [w for w, _, c in test_artifact],
                   "exemplar_location": [w for w, _, c in exemplar_location],
                   "test_location": [w for w, _, c in test_location]},
        "typing_acc_by_dfeat": {d: by_dfeat[d]["typing_acc"] for d in by_dfeat},
        "typing_acc_per_seed_headline": hp["typing_acc_per_seed"],
        "typing_curve": typing_curve, "margin_curve": margin_curve,
        "headline_dfeat": headline_dfeat,
        "headline_typing_acc": headline_typing_acc,
        "headline_margin_vs_naive": headline_margin_vs_naive,
        "headline_margin_vs_random": headline_margin_vs_random,
        "headline_per_seed_margins": per_seed_margins,
        "headline_all_seeds_positive": all_seeds_positive,
        "flip_classification": flip_classification,
        "sentence_resolution_acc": resolution_acc,
        "per_sentence": per_sentence,
        "mechanics_ceiling_check": ceiling_check_val,
        "baseline_in_band": baseline_in_band,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units,
        "n_units_done": n_units_done_total,
        "arms_differ_verified": arms_differ_all, "arms_differ_detail": arms_differ_detail,
        "arms_differ_exempted": arms_differ_exempted,
        "se_webs_hashes": se_digests,
        "bands": {"HP_TYPING_ACC_MIN": HP_TYPING_ACC_MIN, "HP_VS_NAIVE_MARGIN_MIN": HP_VS_NAIVE_MARGIN_MIN,
                  "HP_VS_RANDOM_MARGIN_MIN": HP_VS_RANDOM_MARGIN_MIN,
                  "HP_RANDOM_AT_CHANCE_MAX": HP_RANDOM_AT_CHANCE_MAX,
                  "HP_SENTENCE_RESOLUTION_MIN": HP_SENTENCE_RESOLUTION_MIN,
                  "HF_VS_NAIVE_MARGIN_MAX": HF_VS_NAIVE_MARGIN_MAX,
                  "HF_TYPING_ACC_FLOOR": HF_TYPING_ACC_FLOOR, "CEIL_CHECK_MIN": CEIL_CHECK_MIN,
                  "CHANCE_FLOOR": 0.50},
        "crlb_n/a": "binary typing-accuracy + categorical sentence-resolution metric over discrete "
                    "ARTIFACT/LOCATION candidates; closed-form chance floor = 0.50 (THEORETICAL); not a "
                    "CRLB regime",
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True,
        "integration_of": ["exp_single_edge_grounding_hd_binding_verbnet_v1 (storage/recall, reused "
                           "byte-identical)",
                           "exp_learned_codebook_generalization_gate_v1 (atom 29368, real codebook, "
                           "AUC=0.927, reused unmodified)",
                           "exp_novel_atom_real_codebook_generalization_v1 (atoms 29379-82, ridge "
                           "induction, reused unmodified)"],
        "claim_ceiling": ("This cell measures whether filler-typing can be DERIVED from a noun's own "
                          "learned codebook encoding rather than hand-stipulated, on a small curated "
                          "exemplar/test-noun set at real-corpus scale. Per 29379-82's own finding, the "
                          "induction-vs-naive margin is expected to be CAPACITY-GATED (D_FEAT-dependent); "
                          "a MIDDLE_BAND / flip-only-at-headline result is the honest expected outcome, "
                          "not evidence against the integration."),
        "REQUIRED_FIELDS": ["verdict", "typing_acc_by_dfeat", "sentence_resolution_acc",
                            "cardinality_ok", "arms_differ_verified", "baseline_in_band"],
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test: builds a tiny toy corpus with clear ARTIFACT-like /
    LOCATION-like clusters, exercises the REAL builders (cb.build_vocab/build_cooc/build_ppmi/
    build_codebook, na.ridge_fit/ridge_predict/feat_from_raw_row/build_partial_cooc_row) through THIS
    cell's own orchestration (build_word_pools + run_dfeat_point), plus the REAL FHRR single-edge
    storage/recall (se.build_atoms/build_webs_and_keys + hdlab bind/unbind/similarity) at production
    N_DIM -- not a synthetic-only branch (Gate F.1)."""
    print("[self-test] real_code_path: building tiny toy corpus with artifact/location clusters",
          flush=True)
    base = (["church", "pew", "steeple", "aisle", "altar"] * 10
            + ["temple", "shrine", "monk", "incense", "altar"] * 10
            + ["tower", "wall", "gate", "stone", "bell"] * 10
            + ["castle", "moat", "knight", "banner", "keep"] * 10
            + ["forest", "tree", "leaf", "trail", "deer"] * 10
            + ["mountain", "peak", "snow", "trail", "cliff"] * 10
            + ["island", "shore", "wave", "sand", "palm"] * 10
            + ["desert", "sand", "dune", "cactus", "heat"] * 10)
    rng = np.random.default_rng(0)
    tokens = list(rng.permutation(base * 8))
    w2i, counts = cb.build_vocab(tokens, vocab_size=60, min_count=1)
    V = len(w2i)
    assert V >= 20, f"toy vocab too small V={V}"
    ids = np.fromiter((w2i.get(t, -1) for t in tokens), dtype=np.int64, count=len(tokens))
    cooc = cb.build_cooc(tokens, w2i, window=3)
    ppmi = cb.build_ppmi(cooc)
    tiny_N = 32
    true_codes_np = cb.build_codebook("ppmi_svd", cooc, ppmi, V, tiny_N, CODE_SEED, ri_sparsity=4)
    col_stats = na.compute_ppmi_col_stats(cooc)

    global N_CODE
    orig_n_code = N_CODE
    N_CODE = tiny_N
    try:
        toy_artifact_pool = ["church", "temple", "tower", "castle"]
        toy_location_pool = ["forest", "mountain", "island", "desert"]
        assert all(w in w2i for w in toy_artifact_pool + toy_location_pool)
        print("[self-test] real_code_path: exercising build_word_pools with toy pools "
              "(2 exemplar / 2 test per category)", flush=True)

        def present_sorted(pool):
            pres = [(w, w2i[w], float(counts[w2i[w]])) for w in pool if w in w2i]
            pres.sort(key=lambda x: (-x[2], x[0]))
            return pres

        art = present_sorted(toy_artifact_pool)
        loc = present_sorted(toy_location_pool)
        exemplar_artifact, test_artifact = art[:2], art[2:4]
        exemplar_location, test_location = loc[:2], loc[2:4]
        ex_words = {w for w, _, _ in exemplar_artifact + exemplar_location}
        test_words = {w for w, _, _ in test_artifact + test_location}
        assert ex_words.isdisjoint(test_words), "toy exemplar/test overlap"

        positions = {i: np.where(ids == i)[0] for _, i, _ in (test_artifact + test_location)}
        for w, i, _ in test_artifact + test_location:
            assert len(positions[i]) >= 5, f"toy word {w!r} too rare for a partial draw"

        print("[self-test] real_code_path: exercising run_dfeat_point (THIS cell's orchestration) "
              "at 2 tiny D_FEAT points", flush=True)
        tiny_dfeat_curve = [16, 32]  # must be >= RI_SPARSITY=10 (nonzeros/row, sampled w/o replacement)
        scratch_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest_scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        by_dfeat = {}
        for dfeat in tiny_dfeat_curve:
            pt = run_dfeat_point(dfeat, V, ppmi, ids, true_codes_np, positions, exemplar_artifact,
                                  test_artifact, exemplar_location, test_location, window=3,
                                  seeds=[0, 1], k_draws=2, col_stats=col_stats, output_dir=scratch_dir)
            by_dfeat[dfeat] = pt
            expected_units = len(ARMS) * 4 * 2 * 2  # 4 test words x 2 seeds x 2 draws
            assert pt["n_units"] == expected_units, f"cardinality mismatch at tiny dfeat={dfeat}"
            for arm in ARMS:
                acc = pt["typing_acc"][arm]
                assert np.isfinite(acc), f"non-finite acc for arm={arm} dfeat={dfeat}: {acc}"
            assert pt["typing_acc"]["hand"] == 1.0, "hand-stipulated arm must be exact oracle (acc=1.0)"

        margins = [by_dfeat[d]["typing_acc"]["derived"] - by_dfeat[d]["typing_acc"]["naive"]
                   for d in tiny_dfeat_curve]
        print(f"[self-test] toy margins (derived-naive) by dfeat={tiny_dfeat_curve}: "
              f"{[round(m, 4) for m in margins]}", flush=True)

        print("[self-test] real_code_path: exercising REAL single-edge FHRR storage/recall "
              "(se.build_atoms/build_webs_and_keys, production N_DIM) + score_sentences", flush=True)
        atom = se.build_atoms()
        webs, keys = se.build_webs_and_keys(atom)
        se.mechanism_integrity_check(webs)
        se.arms_differ_hash(webs)
        recovered = B.unbind(webs["WEB_BUILD_EDGE"], keys["key_build"])
        sim = float(A.similarity(recovered, atom["TYPE_ARTIFACT"]))
        assert sim >= 0.95, f"reused se storage/recall mechanics sanity failed: sim={sim:.4f}"

        headline_pt = by_dfeat[tiny_dfeat_curve[-1]]
        per_sentence, resolution_acc = score_sentences(atom, webs, keys, headline_pt, test_artifact,
                                                        test_location, seeds=[0, 1], k_draws=2,
                                                        output_dir=scratch_dir)
        assert len(per_sentence) == min(len(test_artifact), len(test_location))
        for arm in ARMS:
            assert 0.0 <= resolution_acc[arm] <= 1.0, f"resolution_acc[{arm}] out of range"
        assert resolution_acc["hand"] == 1.0, (
            f"hand-stipulated arm must resolve every held-out sentence exactly (FHRR exact recovery): "
            f"got {resolution_acc['hand']}")

        print(f"[self-test] PASS: real tokenizer/vocab/cooc/ppmi/codebook/ridge/partial-row builders + "
              f"run_dfeat_point + REAL FHRR single-edge storage/recall + score_sentences all exercised. "
              f"toy hand_resolution={resolution_acc['hand']:.3f} mechanics_sim={sim:.4f} "
              f"cardinality/finite-value guards held.", flush=True)
    finally:
        N_CODE = orig_n_code


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, SMOKE_CFG, DFEAT_CURVE_SMOKE, SEEDS, K_DRAWS_SMOKE, run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, FULL_CFG, DFEAT_CURVE_FULL, SEEDS, K_DRAWS_FULL, run_mode="full")
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
