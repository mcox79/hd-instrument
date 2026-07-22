"""Perception-MEANING grounding VIABILITY PROBE: does a SHARDED (per-class) bind store recover the
grounding lift that the ADDITIVE-superposition store lost to cross-class crosstalk (atom 29438)?

ONE VARIABLE = the STORE STRUCTURE. Everything else (encoder front-ends raw/hog, data, split, words,
retrieval task) is REUSED VERBATIM from experiments.exp_reader_perception_meaning_grounding_v1 (GRD).

BASELINE to beat (atom 29438, disk): olivetti(40-class) ADDITIVE store i2w BLIND(raw)=0.317
AWARE(hog)=0.232 -> aware-blind=-0.085 (NO lift, hog slightly hurts), BUT hog shuffle-sensitivity
=0.188 vs raw=-0.030 (perception is REAL / content genuinely used through the bind).
  CITED@d:/AI/hd-instrument/data/exp_reader_perception_meaning_grounding_v1/metrics.json:
    primary_olivetti.arms.rung1_raw.i2w_clean=0.3166667
    primary_olivetti.arms.rung3_hog.i2w_clean=0.2316667
    verdict_detail.olivetti_gates.aware_over_blind=-0.085

THE HYPOTHESIS (recurring project theme): additive-superposition crosstalk is the same capacity
limit across grounding + settling + compgen; SHARDING is the recurring fix. The additive store sums
ALL train binds into ONE vector M = sum_i bind(word_c(i), code_i); grounding q = M * code_x argmax'd
over the word codebook picks up crosstalk from every OTHER class's binds. A PER-CLASS SHARDED store
keeps one vector M_c = sum_{i in class c} bind(word_c, code_i) per class and scores each shard
INDEPENDENTLY: pred = argmax_c cosine(word_c, M_c * code_x). This DROPS the off-diagonal c != w
crosstalk terms entirely (an inspectable per-class partition of the bind memory -- glass-box VSA,
NOT a neural module). If cross-class crosstalk was masking a real content-recognition lift, the
sharded store recovers it (aware beats blind). If sharding ALSO shows no lift, crosstalk was NOT the
limit -> implicates the encoder / perception step.

TWO STORE STRUCTURES x TWO ENCODER FRONT-ENDS = a 2x2. aware-over-blind measured under EACH store:
  additive : GRD.build_store / GRD.i2w_heldout / GRD.w2i_heldout  (VERBATIM; the 29438 baseline arm)
  sharded  : build_store_sharded / i2w_heldout_sharded / w2i_heldout_sharded (per-class partition)

PRE-REGISTERED BANDS (probe verdict on PRIMARY olivetti):
  POSITIVE CONTROL (Gate D, reproduce prior): the ADDITIVE arm must reproduce 29438's null direction
    -- additive aware_over_blind in [-0.135, -0.035] (cited -0.085 +/- 0.05) AND additive raw/hog
    absolute i2w within 0.06 of 0.317 / 0.232. If not, the store-comparison rail is broken -> RAIL_FAIL.
  HARD-PASS  SHARDED_RECOVERS_GROUNDING_LIFT: sharded aware_over_blind >= +0.05 (AWARE_OVER_BLIND_MIN)
    AND robust to controls -- sharded hog shuffle-sensitivity >= 0.15, sharded hog scramble-collapse
    >= 0.10, sharded raw shuffle-invariant (<= 0.12). Crosstalk WAS the limit; sharding is the fix.
  HARD-FAIL  SHARDING_NO_LIFT: sharded aware_over_blind <= 0.0. Crosstalk NOT the limit; the encoder
    / perception step is implicated (honest refutation of the crosstalk hypothesis for grounding).
  MIDDLE_BAND: 0.0 < sharded aware_over_blind < +0.05 (weak partial recovery, inconclusive).

CAN-FAIL is REAL: sharding may help raw as much as hog (both are nearest-class-shard scoring in code
space), leaving aware-blind <= 0 -> HARD-FAIL. The probe genuinely discriminates the two hypotheses.

DISCRIMINATOR-SURVIVES-SCALE (analytical, option B): additive cross-class crosstalk variance grows
with the number of OTHER-class binds ~ (n_classes-1)*k_train; sharding removes exactly those terms.
So the sharded-vs-additive gap GROWS with n_classes: the FULL 40-class olivetti regime is MORE
discriminating than the 8-class smoke, not less. If the mechanism differentiates at smoke it
differentiates at full. The additive positive-control null (-0.085) is a FULL-40-class property; the
smoke gate verifies the machinery + direction, FULL validates the reproduction + magnitude.

GLASS-BOX invariant: no external LLM, no learned-opaque operator. Sharded store = per-class partition
of the SAME bind/unbind VSA primitives. LOCAL ONLY: no push, no remote-persist, no atom banking.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (raw/hog codes bit-differ; additive vs sharded metrics differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: grounding = held-out retrieval vs chance + shuffle-sensitivity contrast + scramble
#             collapse + store-structure differential, not a scalar noise-floor cap
# - baseline_in_band: additive raw i2w in (chance, RAW_SAT_MAX); sharded arms checked not both >0.95
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - discriminator-fires: self_test synth localized-shape set has sharded hog grounding high, sharded
#             hog shuffle-sensitivity > sharded raw, scramble collapses, additive != sharded metrics
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging = print_flush_true (cell < 600s; flush anyway)
# - positive_control (Gate D): additive arm reproduces cited 29438 aware_over_blind=-0.085 at FULL
ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
import hashlib
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_perception_meaning_grounding_sharded_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse (VERBATIM) the perception-meaning grounding cell: encoder, split, words, additive store,
# additive retrieval, HOG front-end, loaders. ONLY the store STRUCTURE is added here.
import experiments.exp_reader_perception_meaning_grounding_v1 as GRD  # noqa: E402
import experiments.exp_reader_image_shape_recognition_hog_v1 as HG  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-22_reader_perception_meaning_grounding_sharded_v1.md) ----
CHANCE_EPS = 0.03
AWARE_OVER_BLIND_MIN = 0.05      # sharded hog_i2w - raw_i2w: the HARD-PASS lift threshold
SHUFFLE_SENS_MIN = 0.15          # sharded hog clean - hog shuffled: content-aware must still drop
SHUFFLE_INVARIANT_MAX = 0.12     # sharded raw clean - raw shuffled: content-blind noise floor
SCR_COLLAPSE_MIN = 0.10          # sharded hog clean - hog wordscramble: real association, not base-rate
STRONG_GROUND_MIN = 0.30
RAW_SAT_MAX = 0.95               # baseline_in_band: any store's raw/hog i2w >= this at FULL => sat flag
# Gate D positive-control (reproduce atom 29438 additive null at FULL 40-class olivetti)
ADD_AOB_CITED = -0.085           # CITED@.../exp_reader_perception_meaning_grounding_v1/metrics.json
ADD_AOB_TOL = 0.05               # additive aware_over_blind must land in [-0.135, -0.035]
ADD_RAW_CITED = 0.3166667        # CITED@...:primary_olivetti.arms.rung1_raw.i2w_clean
ADD_HOG_CITED = 0.2316667        # CITED@...:primary_olivetti.arms.rung3_hog.i2w_clean
ADD_ABS_TOL = 0.06

SEEDS = [0, 1, 2, 3, 4]
ARMS = ["rung1_raw", "rung3_hog"]     # content-blind baseline, content-aware
STORES = ["additive", "sharded"]      # THE single variable


# --------------------------------------------------------------------------------------
# defensive-error-checking template helpers
# --------------------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": anchor_name, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": anchor_name}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)


def _arms_must_differ(arms_outputs):
    digests = {}
    for name, out in arms_outputs.items():
        b = np.ascontiguousarray(out).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, b, digests[a]))
    return digests


# --------------------------------------------------------------------------------------
# SHARDED (per-class) store + per-shard retrieval  --  THE SINGLE VARIABLE
# --------------------------------------------------------------------------------------
def build_store_sharded(codes, labels, words, train_mask, label_map=None):
    """Per-class shard: M_c = sum_{train imgs in class c} bind(word[label_or_scramble(c)], code_i).
    Returns dict {class_id: shard_vector}. An inspectable per-class partition of the SAME additive
    bind memory (each class its own bundle vector) -- NOT a neural module. label_map permutes the
    class->word assignment for the base-rate scramble control (built with word[label_map[c]] but
    scored against word[c] -> collapses when scrambled)."""
    labels = np.asarray(labels)
    N = codes.shape[1]
    shards = {}
    for i in np.where(train_mask)[0]:
        c = int(labels[i])
        wc = c if label_map is None else int(label_map[c])
        if c not in shards:
            shards[c] = np.zeros(N, dtype=np.float32)
        shards[c] += words[wc].astype(np.float32) * codes[i]
    return shards


def i2w_heldout_sharded(shards, codes, labels, test_mask, words):
    """Ground each HELD-OUT image to its referent word via PER-SHARD scoring:
        pred = argmax_c cosine(word_c, M_c * code_x)
    Drops the off-diagonal (c != w) crosstalk terms the additive single-M scoring carries. Content
    recognition still drives it: M_c * x is aligned to word_c ONLY when x resembles class-c train codes."""
    labels = np.asarray(labels)
    Wn = words.astype(np.float32)
    Wn = Wn / (np.linalg.norm(Wn, axis=1, keepdims=True) + 1e-12)
    idx = np.where(test_mask)[0]
    if len(idx) == 0:
        return 0.0
    classes = sorted(shards.keys())
    hits = 0
    for i in idx:
        x = codes[i]
        best_c, best_s = -1, -np.inf
        for c in classes:
            qc = shards[c] * x
            qc = qc / (np.linalg.norm(qc) + 1e-12)
            s = float(Wn[c] @ qc)          # score shard c against ITS OWN referent word_c
            if s > best_s:
                best_s, best_c = s, c
        hits += int(best_c == labels[i])
    return hits / len(idx)


def w2i_heldout_sharded(shards, codes, labels, test_mask, words):
    """Ground each referent word to a HELD-OUT image among held-out distractors, per-shard:
        q = M_c * word_c ; top-1 held-out code by cosine shares class c? chance ~ 1/n_classes."""
    labels = np.asarray(labels)
    idx = np.where(test_mask)[0]
    if len(idx) == 0:
        return 0.0
    C = codes[idx]  # already normalized
    correct, present = 0, 0
    for c in sorted(shards.keys()):
        if not np.any(labels[idx] == c):
            continue
        present += 1
        q = shards[c] * words[c].astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-12)
        top = idx[int((C @ q).argmax())]
        correct += int(labels[top] == c)
    return correct / max(present, 1)


# --------------------------------------------------------------------------------------
# evaluate both stores x both encoders on one dataset (clean + global-pixel-shuffle + scramble)
# --------------------------------------------------------------------------------------
def eval_dataset_2store(grays, labels, p, N, seeds, k_train):
    labels = np.asarray(labels)
    n_classes = int(len(np.unique(labels)))
    chance = 1.0 / n_classes
    train_mask, test_mask = GRD.split_masks(labels, k_train)   # VERBATIM split
    per = {}                       # per[arm][store] = metrics dict
    example_codes = {}
    for arm in ARMS:
        store_acc = {st: defaultdict(list) for st in STORES}
        for s in seeds:
            words = GRD.random_words(n_classes, N, s)           # VERBATIM words
            scr_rng = np.random.default_rng(6000 + s)           # VERBATIM scramble seed
            label_map = scr_rng.permutation(n_classes)
            for cond, shuf in (("clean", False), ("shuf", True)):
                codes = GRD.encode_images(grays, arm, p, N, s, shuffle=shuf)  # VERBATIM encoder
                if arm not in example_codes and cond == "clean":
                    example_codes[arm] = codes
                # ADDITIVE store (the 29438 baseline arm) -- VERBATIM build + retrieval
                M = GRD.build_store(codes, labels, words, train_mask)
                store_acc["additive"]["i2w_" + cond].append(
                    GRD.i2w_heldout(M, codes, labels, test_mask, words))
                store_acc["additive"]["w2i_" + cond].append(
                    GRD.w2i_heldout(M, codes, labels, test_mask, words))
                # SHARDED store (the single variable)
                sh = build_store_sharded(codes, labels, words, train_mask)
                store_acc["sharded"]["i2w_" + cond].append(
                    i2w_heldout_sharded(sh, codes, labels, test_mask, words))
                store_acc["sharded"]["w2i_" + cond].append(
                    w2i_heldout_sharded(sh, codes, labels, test_mask, words))
                if cond == "clean":
                    Ms = GRD.build_store(codes, labels, words, train_mask, label_map=label_map)
                    store_acc["additive"]["i2w_scr"].append(
                        GRD.i2w_heldout(Ms, codes, labels, test_mask, words))
                    shs = build_store_sharded(codes, labels, words, train_mask, label_map=label_map)
                    store_acc["sharded"]["i2w_scr"].append(
                        i2w_heldout_sharded(shs, codes, labels, test_mask, words))
        for st in STORES:
            acc = store_acc[st]
            m = {k: float(np.mean(v)) for k, v in acc.items()}
            m["i2w_clean_std"] = float(np.std(acc["i2w_clean"]))
            m["shuffle_sensitivity"] = m["i2w_clean"] - m["i2w_shuf"]
            m["scramble_collapse"] = m["i2w_clean"] - m["i2w_scr"]
            m["n_seeds"] = len(seeds)
            per.setdefault(arm, {})[st] = m
    return {"n_img": len(labels), "n_classes": n_classes, "chance_i2w": chance,
            "n_train": int(train_mask.sum()), "n_test": int(test_mask.sum()),
            "arms": per}, example_codes


def _store_gates(ds, store):
    """Perception-meaning gates for ONE store structure on one dataset."""
    blind = ds["arms"]["rung1_raw"][store]
    aware = ds["arms"]["rung3_hog"][store]
    chance = ds["chance_i2w"]
    aob = aware["i2w_clean"] - blind["i2w_clean"]
    g = {
        "store": store, "chance_i2w": chance,
        "blind_i2w_clean": blind["i2w_clean"], "aware_i2w_clean": aware["i2w_clean"],
        "blind_i2w_shuf": blind["i2w_shuf"], "aware_i2w_shuf": aware["i2w_shuf"],
        "aware_over_blind": aob,
        "aware_shuffle_sensitivity": aware["shuffle_sensitivity"],
        "blind_shuffle_sensitivity": blind["shuffle_sensitivity"],
        "aware_scramble_collapse": aware["scramble_collapse"],
        "aware_lift_over_chance": aware["i2w_clean"] - chance,
        "blind_w2i_clean": blind["w2i_clean"], "aware_w2i_clean": aware["w2i_clean"],
        "shuffle_contrast_aware_minus_blind": aware["shuffle_sensitivity"] - blind["shuffle_sensitivity"],
    }
    g["gate_flags"] = {
        "over_blind_ok": bool(aob >= AWARE_OVER_BLIND_MIN),
        "aware_sens_ok": bool(aware["shuffle_sensitivity"] >= SHUFFLE_SENS_MIN),
        "blind_noisefloor_ok": bool(blind["shuffle_sensitivity"] <= SHUFFLE_INVARIANT_MAX),
        "scramble_ok": bool(aware["scramble_collapse"] >= SCR_COLLAPSE_MIN),
        "strong": bool(aware["i2w_clean"] >= STRONG_GROUND_MIN),
        "raw_saturated": bool(blind["i2w_clean"] >= RAW_SAT_MAX),
        "hog_saturated": bool(aware["i2w_clean"] >= RAW_SAT_MAX),
    }
    return g


def _probe_verdict(oli):
    """THE probe verdict on PRIMARY olivetti: does sharding recover the aware-over-blind lift?"""
    add = _store_gates(oli, "additive")
    shd = _store_gates(oli, "sharded")

    # Gate D positive control: additive arm must reproduce atom 29438's null at FULL 40-class.
    add_aob = add["aware_over_blind"]
    add_repro_aob = (ADD_AOB_CITED - ADD_AOB_TOL) <= add_aob <= (ADD_AOB_CITED + ADD_AOB_TOL)
    add_repro_raw = abs(add["blind_i2w_clean"] - ADD_RAW_CITED) <= ADD_ABS_TOL
    add_repro_hog = abs(add["aware_i2w_clean"] - ADD_HOG_CITED) <= ADD_ABS_TOL
    add_reproduced = bool(add_repro_aob and add_repro_raw and add_repro_hog)

    shd_aob = shd["aware_over_blind"]
    shd_f = shd["gate_flags"]
    controls_ok = bool(shd_f["aware_sens_ok"] and shd_f["blind_noisefloor_ok"] and shd_f["scramble_ok"])
    both_sat = bool(shd_f["raw_saturated"] and shd_f["hog_saturated"])

    if not add_reproduced:
        verdict = "RAIL_FAIL_ADDITIVE_NOT_REPRODUCED"
    elif both_sat:
        # both arms saturate under sharding -> can't compare lift (baseline out of band)
        verdict = "SHARDED_SATURATED_INCONCLUSIVE"
    elif shd_aob >= AWARE_OVER_BLIND_MIN and controls_ok:
        verdict = ("SHARDED_RECOVERS_GROUNDING_LIFT_STRONG"
                   if shd["gate_flags"]["strong"] else "SHARDED_RECOVERS_GROUNDING_LIFT")
    elif shd_aob <= 0.0:
        verdict = "SHARDING_NO_LIFT_CROSSTALK_NOT_THE_LIMIT"
    else:
        verdict = "MIDDLE_BAND_WEAK_PARTIAL_RECOVERY"

    detail = {
        "additive_gates": add, "sharded_gates": shd,
        "additive_reproduced_29438": add_reproduced,
        "additive_repro_checks": {"aob_ok": bool(add_repro_aob), "raw_ok": bool(add_repro_raw),
                                  "hog_ok": bool(add_repro_hog),
                                  "add_aob": add_aob, "cited_aob": ADD_AOB_CITED},
        "sharded_aware_over_blind": shd_aob,
        "additive_aware_over_blind": add_aob,
        "lift_recovery_delta_sharded_minus_additive": shd_aob - add_aob,
        "sharded_controls_ok": controls_ok,
        "verdict": verdict,
    }
    return verdict, detail


# --------------------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------------------
def self_test():
    N, Q = 3000, 9
    p = {"grid": 12, "grid_hog": 6, "n_orient": 9, "Q": Q}

    # 1. localized-shape synth (grossly-different classes): sharded hog grounds cross-instance, the
    #    class<->word scramble collapses it, additive and sharded metrics are NOT bit-identical.
    def synth_local(seed):
        r = np.random.default_rng(seed)
        grays, labels = [], []
        for ci in range(3):
            for _ in range(6):
                g = r.integers(200, 235, size=(48, 48)).astype(np.float32)
                dy, dx = int(r.integers(-2, 3)), int(r.integers(-2, 3))
                if ci == 0:
                    g[10 + dy:14 + dy, 6 + dx:42 + dx] = 25.0
                elif ci == 1:
                    g[6 + dy:42 + dy, 10 + dx:14 + dx] = 25.0
                else:
                    g[20 + dy:28 + dy, 20 + dx:28 + dx] = 25.0
                grays.append(np.clip(g, 0, 255).astype(np.float32)); labels.append(ci)
        return grays, labels
    sg, sl = synth_local(3)
    ds, ex = eval_dataset_2store(sg, sl, p, N, [0, 1], k_train=4)
    hog_sh = ds["arms"]["rung3_hog"]["sharded"]
    raw_sh = ds["arms"]["rung1_raw"]["sharded"]
    assert hog_sh["i2w_clean"] >= 0.90, "sharded hog cross-instance grounding failed (%.3f)" % hog_sh["i2w_clean"]
    assert hog_sh["scramble_collapse"] >= 0.30, ("sharded word-scramble must collapse grounding "
                                                 "(clean %.3f scr %.3f)" % (hog_sh["i2w_clean"], hog_sh["i2w_scr"]))
    assert hog_sh["w2i_clean"] >= 0.66, "sharded hog w2i held-out grounding failed (%.3f)" % hog_sh["w2i_clean"]
    assert raw_sh["shuffle_sensitivity"] <= 0.02, ("sharded raw must be ~shuffle-invariant (sens=%.3f)"
                                                   % raw_sh["shuffle_sensitivity"])

    # 1b. THE STORE VARIABLE FIRES (direct crosstalk micro-proof at the code level, no encoder): with
    #     MANY near-orthogonal classes, the additive single-M store carries cross-class crosstalk that
    #     degrades held-out grounding; the per-class sharded store drops those off-diagonal terms and
    #     grounds STRICTLY better. This is the exact mechanism the FULL 40-class olivetti run probes.
    def _crosstalk_case(Cn, k_tr, k_te, Nc, seed, noise=0.35):
        r = np.random.default_rng(seed)
        bases = (r.integers(0, 2, size=(Cn, Nc)) * 2 - 1).astype(np.float32)  # class prototypes
        codes, labels = [], []
        for c in range(Cn):
            for _ in range(k_tr + k_te):
                flip = (r.random(Nc) < noise)
                v = bases[c].copy(); v[flip] *= -1.0
                v = v / (np.linalg.norm(v) + 1e-12)
                codes.append(v.astype(np.float32)); labels.append(c)
        codes = np.stack(codes); labels = np.asarray(labels)
        tr = np.zeros(len(labels), bool); te = np.zeros(len(labels), bool)
        for c in range(Cn):
            idx = np.where(labels == c)[0]
            tr[idx[:k_tr]] = True; te[idx[k_tr:]] = True
        return codes, labels, tr, te
    cc, cl, ctr, cte = _crosstalk_case(Cn=16, k_tr=4, k_te=3, Nc=1024, seed=7)
    cw = (np.random.default_rng(11).integers(0, 2, size=(16, 1024)) * 2 - 1).astype(np.int8)
    Mx = GRD.build_store(cc, cl, cw, ctr)
    add_i2w = GRD.i2w_heldout(Mx, cc, cl, cte, cw)
    shx = build_store_sharded(cc, cl, cw, ctr)
    shd_i2w = i2w_heldout_sharded(shx, cc, cl, cte, cw)
    assert shd_i2w >= add_i2w + 0.05, ("store variable must fire: sharded must beat additive under "
                                       "cross-class crosstalk (sharded=%.3f additive=%.3f)" % (shd_i2w, add_i2w))
    assert shd_i2w >= 0.90, "sharded must ground the crosstalk case near-perfectly (%.3f)" % shd_i2w

    # 2. DISCRIMINATOR fires on LOCAL-structure classes (orientation): sharded hog collapses under a
    #    global pixel-shuffle (destroys HOG's spatial gradient locality) while sharded raw stays at its
    #    noise floor -> shuffle-sensitivity CONTRAST. Same discriminator the FULL run reports per store.
    def synth_orient(seed):
        r = np.random.default_rng(seed)
        thetas = [0.0, 45.0, 90.0]
        grays, labels = [], []
        for ci, th in enumerate(thetas):
            for _ in range(6):
                per = float(r.uniform(6.0, 10.0)); ph = float(r.uniform(0, 2 * np.pi))
                yy, xx = np.mgrid[0:48, 0:48].astype(np.float64)
                thr = np.deg2rad(th)
                coord = xx * np.cos(thr) + yy * np.sin(thr)
                g = 128.0 + 100.0 * np.sign(np.sin(2 * np.pi * coord / per + ph))
                g = g + r.normal(0, 8.0, size=(48, 48))
                grays.append(np.clip(g, 0, 255).astype(np.float32)); labels.append(ci)
        return grays, labels
    og, ol = synth_orient(2)
    dso, _ = eval_dataset_2store(og, ol, p, N, [0, 1], k_train=4)
    hog_o = dso["arms"]["rung3_hog"]["sharded"]; raw_o = dso["arms"]["rung1_raw"]["sharded"]
    assert hog_o["i2w_clean"] >= 0.80, "sharded hog must ground oriented textures (i2w=%.3f)" % hog_o["i2w_clean"]
    assert hog_o["shuffle_sensitivity"] >= 0.25, ("sharded hog grounding must collapse under global "
                                                  "pixel-shuffle (sens=%.3f)" % hog_o["shuffle_sensitivity"])
    assert raw_o["shuffle_sensitivity"] <= SHUFFLE_INVARIANT_MAX, (
        "sharded raw shuffle-sens must stay at noise floor (sens=%.3f > %.2f)"
        % (raw_o["shuffle_sensitivity"], SHUFFLE_INVARIANT_MAX))
    assert hog_o["shuffle_sensitivity"] >= raw_o["shuffle_sensitivity"] + 0.10, (
        "sharded hog must be MORE shuffle-sensitive than raw (hog=%.3f raw=%.3f)"
        % (hog_o["shuffle_sensitivity"], raw_o["shuffle_sensitivity"]))

    # 3. arms differ (raw vs hog codes bit-differ)
    _arms_must_differ({a: ex[a] for a in ex})

    # 4. no-nondeterministic-seeding static scan
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
            assert_no_nondeterministic_seeding(fh.read())
    except ImportError:
        pass

    print("[self_test] PASS: sharded xinstance-grounding(hog i2w=%.3f w2i=%.3f) scramble-collapses(%.3f) "
          "raw-invariant(%.3f); STORE-VARIABLE-FIRES crosstalk-case sharded=%.3f > additive=%.3f; "
          "DISCRIMINATOR(oriented) sharded hog-shuffle-sens=%.3f > raw=%.3f (hog i2w=%.3f), arms-differ"
          % (hog_sh["i2w_clean"], hog_sh["w2i_clean"], hog_sh["scramble_collapse"],
             raw_sh["shuffle_sensitivity"], shd_i2w, add_i2w,
             hog_o["shuffle_sensitivity"], raw_o["shuffle_sensitivity"], hog_o["i2w_clean"]), flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def run(mode="full"):
    t0 = time.perf_counter()
    if mode == "smoke":
        p = {"grid": 12, "grid_hog": 6, "n_orient": 9, "Q": 9}
        N, seeds = 3000, [0, 1]
        oli_sub, oli_ktrain = (8, 6), 4
        dig_sub, dig_ktrain = (8, 12), 8
    else:
        # FULL config replicates atom 29438 EXACTLY (so the additive arm reproduces its numbers).
        p = {"grid": 16, "grid_hog": 8, "n_orient": 9, "Q": 17}
        N, seeds = 8192, SEEDS
        oli_sub, oli_ktrain = None, 7           # olivetti 10/class -> 7 train, 3 held-out
        dig_sub, dig_ktrain = (10, 40), 30      # digits 40/class -> 30 train, 10 held-out

    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode,
                        expected_n_units=len(seeds) * len(ARMS) * len(STORES) * 2)

    grays_o, labels_o = HG.load_olivetti(subsample=oli_sub)
    print("[olivetti] n_img=%d n_classes=%d k_train=%d"
          % (len(grays_o), len(set(labels_o)), oli_ktrain), flush=True)
    olivetti, ex_codes = eval_dataset_2store(grays_o, labels_o, p, N, seeds, oli_ktrain)
    print("[olivetti] done ADD raw=%.3f hog=%.3f | SHD raw=%.3f hog=%.3f"
          % (olivetti["arms"]["rung1_raw"]["additive"]["i2w_clean"],
             olivetti["arms"]["rung3_hog"]["additive"]["i2w_clean"],
             olivetti["arms"]["rung1_raw"]["sharded"]["i2w_clean"],
             olivetti["arms"]["rung3_hog"]["sharded"]["i2w_clean"]), flush=True)

    grays_d, labels_d = HG.load_digits_up(per_class=40, up=32, subsample=dig_sub)
    print("[digits] n_img=%d n_classes=%d k_train=%d"
          % (len(grays_d), len(set(labels_d)), dig_ktrain), flush=True)
    digits, _ = eval_dataset_2store(grays_d, labels_d, p, N, seeds, dig_ktrain)
    print("[digits] done ADD raw=%.3f hog=%.3f | SHD raw=%.3f hog=%.3f"
          % (digits["arms"]["rung1_raw"]["additive"]["i2w_clean"],
             digits["arms"]["rung3_hog"]["additive"]["i2w_clean"],
             digits["arms"]["rung1_raw"]["sharded"]["i2w_clean"],
             digits["arms"]["rung3_hog"]["sharded"]["i2w_clean"]), flush=True)

    arm_digests = _arms_must_differ({a: ex_codes[a] for a in ex_codes})

    verdict, detail = _probe_verdict(olivetti)
    _, dig_detail = _probe_verdict(digits)

    add_g = detail["additive_gates"]; shd_g = detail["sharded_gates"]
    dig_add = dig_detail["additive_gates"]; dig_shd = dig_detail["sharded_gates"]
    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "SHARDED-vs-ADDITIVE grounding-store PROBE (does per-class sharding recover the perception-"
        "meaning lift lost to additive crosstalk, atom 29438?). PRIMARY olivetti(%d-class,chance=%.3f): "
        "ADDITIVE i2w raw=%.3f hog=%.3f (aware-blind=%.3f; 29438-repro=%s) || "
        "SHARDED i2w raw=%.3f hog=%.3f (aware-blind=%.3f) shuffsens raw=%.3f hog=%.3f scr_collapse(hog)"
        "=%.3f | recovery-delta(shd-add aob)=%.3f || SECONDARY digits(%d-class): SHARDED aware-blind=%.3f "
        "-> %s"
        % (olivetti["n_classes"], olivetti["chance_i2w"],
           add_g["blind_i2w_clean"], add_g["aware_i2w_clean"], add_g["aware_over_blind"],
           detail["additive_reproduced_29438"],
           shd_g["blind_i2w_clean"], shd_g["aware_i2w_clean"], shd_g["aware_over_blind"],
           shd_g["blind_shuffle_sensitivity"], shd_g["aware_shuffle_sensitivity"],
           shd_g["aware_scramble_collapse"], detail["lift_recovery_delta_sharded_minus_additive"],
           digits["n_classes"], dig_shd["aware_over_blind"], verdict))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "sharded-vs-additive grounding-store viability probe: %s" % verdict,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "run_mode": mode,
        "config": {"params": p, "N": N, "seeds": seeds, "cell_px": HG.CELL_PX, "arms": ARMS,
                   "stores": STORES, "shuffle_seed": GRD.SHUFFLE_SEED,
                   "olivetti_k_train": oli_ktrain, "digits_k_train": dig_ktrain,
                   "primary_dataset": "sklearn_fetch_olivetti_faces_64x64_40class",
                   "secondary_dataset": "sklearn_load_digits_8x8_upscaled32_10class",
                   "note_mcguffey": "NOT USED (USER: de-emphasize McGuffey; clean captioned corpus)"},
        "primary_olivetti": olivetti,
        "secondary_digits": digits,
        "chance": {"olivetti_i2w": olivetti["chance_i2w"], "digits_i2w": digits["chance_i2w"]},
        "probe_detail_olivetti": detail,
        "probe_detail_digits": dig_detail,
        "verdict_detail": {
            "headline_metric": "SHARDED store aware_over_blind (hog i2w - raw i2w) vs ADDITIVE store "
                               "aware_over_blind; does per-class sharding recover a grounding lift that "
                               "additive-superposition crosstalk masked?",
            "single_variable": "store structure (additive-superposition vs per-class sharded); encoder, "
                               "data, split, words, retrieval task held identical between the two stores",
            "hypothesis": "additive cross-class crosstalk is the same capacity limit as in settling / "
                          "compgen; sharding is the recurring fix -- tested here for grounding.",
            "olivetti_probe": detail, "digits_probe": dig_detail},
        "bands": {"CHANCE_EPS": CHANCE_EPS, "AWARE_OVER_BLIND_MIN": AWARE_OVER_BLIND_MIN,
                  "SHUFFLE_SENS_MIN": SHUFFLE_SENS_MIN, "SHUFFLE_INVARIANT_MAX": SHUFFLE_INVARIANT_MAX,
                  "SCR_COLLAPSE_MIN": SCR_COLLAPSE_MIN, "STRONG_GROUND_MIN": STRONG_GROUND_MIN,
                  "RAW_SAT_MAX": RAW_SAT_MAX, "ADD_AOB_CITED": ADD_AOB_CITED, "ADD_AOB_TOL": ADD_AOB_TOL,
                  "ADD_RAW_CITED": ADD_RAW_CITED, "ADD_HOG_CITED": ADD_HOG_CITED, "ADD_ABS_TOL": ADD_ABS_TOL},
        "must_fail_controls": {
            "global_pixel_shuffle": "ONE fixed permutation of the front-end input grid, same for every "
                                    "image; content-blind invariant, content-aware collapses = perception "
                                    "discriminator (carried over per store)",
            "word_scramble": "class<->word assignment permuted before building each store; grounding must "
                             "collapse to chance (base-rate control, carried over per store)",
            "additive_positive_control": "additive store must reproduce atom 29438 aware_over_blind=-0.085 "
                                         "at FULL 40-class olivetti (Gate D rail); else RAIL_FAIL"},
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": [
            "exp_reader_perception_meaning_grounding_v1 (GRD): encode_images / split_masks / "
            "random_words / build_store / i2w_heldout / w2i_heldout VERBATIM (additive baseline arm)",
            "exp_reader_image_shape_recognition_hog_v1 (HG): HOG front-end + loaders VERBATIM",
            "per-class sharded store M_c = sum bind(word_c, code) + per-shard argmax retrieval (added)"],
        "recipe_adopted": "ONE-VARIABLE store-structure probe: additive-superposition vs per-class "
                          "sharded bind store, same encoder/data/split/words/task; aware-over-blind "
                          "measured under each store; additive arm is the 29438 reproduction rail",
        "local_only": True, "banked": False,
    }
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    print(verdict_msg, flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(mode="smoke" if args.smoke else "full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
