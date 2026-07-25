"""bge_finemeaning_wall_probe_v1 -- is the fine-content discrimination signal PRESENT in text (reachable
by a strong text encoder) vs absent from raw co-occurrence, on the SAME real WorldTree wall task?

FRAMING (Director re-scope 2026-07-25): BGE-large is a DIAGNOSTIC CEILING, NOT a candidate encoder to
adopt/distill (a borrowed vector is exactly the shortcut we reject). The BGE number answers ONE routing
question for our OWN grounding build: does the fine-discrimination signal EXIST in text via relational/
contrastive supervision (BGE) vs raw co-occurrence (GloVe) vs substrate-native char-overlap (char_trigram)?
That is a routing FACT about where to aim OUR grounding, nothing more. No verdict here recommends adopting
BGE.

WALL (VET-confirmed, skunkworks abda1634 / seq 29558): over frozen GloVe the substrate cannot tell the
CORRECT fine content from a lexically-similar-but-WRONG alternative. On the WorldTree fine-content task the
GloVe learned front-end is MEMORIZATION -- held-out-to-NEW-concepts acc ~0.106 (BELOW chance ~0.167),
in-vocab ~0.324. BUT the substrate's concept encoder is DISTILLED from a much stronger meaning source:
BGE-large (teacher glob bge_large_v2_name_*.npz; underlying model BAAI/bge-large-en-v1.5, 1024d). Nobody
has tested whether BGE-large ITSELF clears this wall. That is the untested base ingredient and it decides
the whole meaning path.

QUESTION (one variable = the representation; the meaning SOURCE): does BGE-large have the generalizable
fine-meaning structure that frozen GloVe lacks, on the SAME wall task? We test BGE DIRECTLY (encode the
WorldTree concept/value strings with the BGE model) -- NOT the distilled student encoder (that is a later
step).

DESIGN (reuses the GloVe harness exp_learned_meaning_frontend_realslice_v1: parse_tables, task/candidate
construction, held-out-to-NEW-concepts split, readouts, discriminate, Wilson CI; swaps ONLY the encoder):
  Shared item set = the GloVe-in-vocab items (concept + gold encodable by GloVe) -- IDENTICAL items the
  GloVe cell ran on. Per-relation value pool = GloVe-in-vocab values (IDENTICAL pool for both reps).
  ONE VARIABLE = representation, scored on IDENTICAL candidate sets. Two distractor constructions from the
  identical pool (fairness / can-fail, contract):
    GLOVE-NATIVE  distractors = nearest-K wrong values by GLOVE cosine   (the ORIGINAL wall; rigged for GloVe)
    BGE-NATIVE    distractors = nearest-K wrong values by BGE   cosine   (honest-HARDEST for BGE; can-fail)
  PRIMARY DISCRIMINATOR (contract): ZERO-FIT cosine on the BGE-NATIVE candidate sets, BGE vs GloVe vs
  chance -- memorization-proof (no fitting -> no held-out split needed; the number IS generalizable), and
  BGE-native distractors keep BGE HONEST (GloVe-near != BGE-near, so GloVe-native would be trivially easy
  for BGE). Same-candidate-set BGE-vs-GloVe isolates representation perfectly.
  SECONDARY (reported, NOT the primary): learned-linear-over-BGE with the SAME held-out-to-NEW-concepts
  protocol the GloVe cell used (does learning add on top / generalize to new concepts).

ARMS (identical items/candidates; only encoder + readout differ):
  ZF-CHARTRI score(c,v) = cos( trigram(c), trigram(v) )                     [zero-fit; SUBSTRATE-NATIVE floor]
  ZF-GLOVE   score(c,v) = cos( glove(c) , glove(v) )                        [zero-fit; raw co-occurrence]
  ZF-BGE     score(c,v) = cos( bge(c)   , bge(v)   )                        [zero-fit; text-signal CEILING]
  LIN-GLOVE  converged ridge readout over glove(c)+onehot(r) -> glove(v)    [learned; in-vocab + held-out]
  LIN-BGE    converged ridge readout over bge(c)+onehot(r)   -> bge(v)      [learned; in-vocab + held-out]
char_trigram (hdlab/char_trigram_encoder) = OUR OWN substrate-native, deterministic, zero-fit encoder -- a
cheap native baseline showing where the substrate sits on the same wall (NOT composed/concept encoders,
which need corpus fitting = a separate build). Both distractor constructions x each encoder = the zero-fit
table (cross terms reported: BGE on GloVe-native = inflated; GloVe/char_trigram on BGE-native = same-set
head-to-head).

TIERS: COARSE = KINDOF; FINE = the distinctive-content relations (the wall). Gate on FINE.

GATES (design-gate): real baseline (GloVe frozen, the wall) / can-fail (BGE-native = hardest-for-BGE hard
distractors; BGE genuinely CAN fail near chance) / difficulty-on (report mean BGE cos(gold,distractor);
BGE must not saturate) / one-variable (identical items+candidates; only encoder). No memorization confound
(zero-fit). Learned arm: no-leak held-out concepts + shuffled-target control.

VERDICT (a priori; PRIMARY = zero-fit, BGE-NATIVE candidate sets, same-set BGE-vs-GloVe-vs-chance). The
labels describe WHERE THE SIGNAL LIVES, not what encoder to adopt:
  BGE-CLEARS-WALL = BGE zero-fit FINE (bge-native) CI-lower > chance AND (BGE - chance) >= CLEAR_OVER_CHANCE
                    AND (BGE - GloVe_same_set) >= MARGIN_OVER_GLOVE -> the fine-discrimination signal DOES
                    exist in text and is reachable by relational/contrastive supervision (BGE), where raw
                    co-occurrence (GloVe) and substrate-native char-overlap cannot reach it. ROUTING FACT:
                    aim OUR grounding build at that signal (relational supervision) -- do NOT adopt/distill
                    BGE (borrowed vector = the shortcut we reject).
  BGE-ALSO-THIN   = (BGE - chance) < THIN_OVER_CHANCE OR BGE CI-lower <= chance -> even a strong text
                    encoder's RAW cosine cannot separate fine content from its own nearest wrong values ->
                    the signal is NOT cheaply present in text similarity; the wall is DEEPER than any
                    off-the-shelf embedder -> grounding/structure required, not better text embeddings.
  MIDDLE          = BGE materially above chance but not to the CLEAR bar -> partial fine signal in text.
  INVALID         = BGE-native distractors not actually near (selection broke) OR BGE fine saturates (task
                    too easy) OR too few fine eval items (noise floor).

Contract: INLINE-LOCAL foreground-to-completion (GloVe + BGE model large/git-ignored -> not remote-portable);
NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted iteration, BGE
eval-mode CPU deterministic); repo .venv; HF offline. BGE encodings disk-cached (string->vec) for fast
iteration. agent-reported VET-PENDING (skunkworks owns landed-VET; this cell banks NO atoms).

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics ; heartbeat
# - real_code_path: self_test parses REAL table + encodes REAL strings with BGE + builds REAL shared env +
#   real zero-fit + real converged-linear at tiny scale AND a PLANTED env asserting zero-fit cosine
#   discriminates when structure is planted (acc~1) and collapses to chance when destroyed
# - arms_differ: zf-glove vs zf-bge vs lin-bge scores differ; bge-native vs glove-native candidate sets differ
# - no-leak: learned held-out concepts NEVER in any training triple; shuffled guards learned marginal shortcut
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; BGE eval-mode
# - baseline_in_band: GloVe frozen fine checked near-chance-not-saturated at smoke; BGE not saturated
# - discriminator_fires: zero-fit is SCALE-INVARIANT (no training) -> smoke mirrors full at smaller N (CI);
#   the BGE-vs-GloVe direction must show at smoke
# - difficulty_on: BGE-native nearest hard distractors; report mean bge cos(gold,distractor)
# - storage = no_composition (self-contained probe; fixed-VSA selection stage UNCHANGED)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import math
import argparse
import platform
import traceback
from collections import defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# reuse the GloVe harness (task construction + readouts + eval), swap ONLY the encoder ----------------
from experiments.exp_learned_meaning_frontend_realslice_v1 import (  # noqa: E402
    parse_tables, CURATED_TABLES, COARSE_RELS, RELATIONS, REL_IDX, NREL,
    _clean, _l2, _l2_rows, wilson_ci, meaning_vec, HELDOUT_CONCEPT_FRAC, K_DISTRACT,
    WEIGHT_DECAY, discriminate, learned_reps, frozen_reps, fit_converged_linear,
    _load_glove, _load_wordnet, SemanticHDEncoder, PRETRAIN_DIM)
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402

ANCHOR_NAME = "bge_finemeaning_wall_probe_v1"
SEED = 20260725
BGE_MODEL = "BAAI/bge-large-en-v1.5"
BGE_DIM = 1024
TRIGRAM_DIM = 4096       # substrate-native char-trigram HD dim (default)

# ---------------------------------------------------------------------------
# pre-registered bands (a priori; NOT tuned for PASS)
# ---------------------------------------------------------------------------
CLEAR_OVER_CHANCE = 0.15   # BGE zero-fit fine (bge-native) - chance >= this (with CI-lower > chance) -> clears
MARGIN_OVER_GLOVE = 0.10   # BGE zero-fit fine - GloVe zero-fit fine (SAME bge-native candidate set) >= this
THIN_OVER_CHANCE = 0.05    # BGE zero-fit fine - chance < this -> BGE-ALSO-THIN (not materially above chance)
FROZEN_SAT = 0.85          # BGE zero-fit fine >= this -> task too easy -> INVALID (distractors not hard)
DIST_NEAR_MIN = 0.30       # BGE-native mean cos(gold,distractor) < this -> distractors not near -> INVALID
MIN_EVAL_FINE = 60         # < this many fine eval items -> INVALID (noise floor breach)

_T0 = [0.0]
_BGE = [None]


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    from datetime import datetime, timezone
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    from datetime import datetime, timezone
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    from datetime import datetime, timezone
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# BGE encoder (real meaning source) + string->vec disk cache
# ---------------------------------------------------------------------------
def _get_bge():
    if _BGE[0] is None:
        from sentence_transformers import SentenceTransformer
        _BGE[0] = SentenceTransformer(BGE_MODEL, device="cpu")
        _BGE[0].eval()
    return _BGE[0]


def _cache_path():
    return os.path.join(_out_dir(), "bge_string_cache.npz")


def _load_str_cache():
    p = _cache_path()
    if not os.path.exists(p):
        return {}
    z = np.load(p, allow_pickle=True)
    keys = [str(k) for k in z["keys"].tolist()]
    vecs = z["vecs"]
    return {k: vecs[i] for i, k in enumerate(keys)}


def _save_str_cache(cache):
    keys = sorted(cache.keys())
    vecs = np.stack([cache[k] for k in keys], axis=0).astype(np.float32) if keys else np.zeros((0, BGE_DIM), np.float32)
    tmp = _cache_path() + ".tmp"
    with open(tmp, "wb") as fh:   # explicit handle: np.savez appends .npz to a str path, not to a handle
        np.savez(fh, keys=np.array(keys, dtype=object), vecs=vecs)
    os.replace(tmp, _cache_path())


def bge_encode(strings, output_dir, use_cache=True):
    """Return dict string -> L2-normalized 1024d BGE vector. Disk-cached (string->vec) for fast iteration.
    Symmetric plain encoding (no query instruction) -- concept and value encoded identically (fair)."""
    strings = sorted(set(strings))
    cache = _load_str_cache() if use_cache else {}
    missing = [s for s in strings if s not in cache]
    if missing:
        _heartbeat(output_dir, "bge_encode", {"n_total": len(strings), "n_missing": len(missing)})
        model = _get_bge()
        E = model.encode(missing, normalize_embeddings=True, batch_size=64,
                         show_progress_bar=False, convert_to_numpy=True)
        E = np.asarray(E, dtype=np.float32)
        for i, s in enumerate(missing):
            cache[s] = E[i]
        if use_cache:
            _save_str_cache(cache)
    return {s: cache[s] for s in strings}


# ---------------------------------------------------------------------------
# shared environment: identical items across reps; two distractor constructions
# ---------------------------------------------------------------------------
def _nearest_distractors(gold_str, pool_strs, vmat, vidx_pool, gold_excl, k):
    """Nearest-k pool values to gold_str by cosine in the given (L2) vmat, excluding gold(s). Returns strings."""
    gi = vidx_pool[gold_str]
    sims = vmat @ vmat[gi]
    order = np.argsort(-sims)
    out = []
    for j in order.tolist():
        cand = pool_strs[j]
        if cand == gold_str or cand in gold_excl:
            continue
        out.append(cand)
        if len(out) >= k:
            break
    return out


def build_shared_environment(glove_enc, triples, kindof_cap, seed, output_dir, use_bge_cache=True):
    """Encode concepts+values with BOTH GloVe and BGE. Shared item set = GloVe-in-vocab items (identical to
    the GloVe cell). Per-relation value pool = GloVe-in-vocab values (identical pool for both reps). Build,
    per item, GLOVE-NATIVE and BGE-NATIVE nearest-K distractor candidate sets from the identical pool.
    Split concepts train/held-out (same frac/seed discipline as the GloVe harness)."""
    # optional KINDOF cap for balance/speed (deterministic subsample) -- mirrors harness
    by_rel = defaultdict(list)
    for (c, r, v) in triples:
        by_rel[r].append((c, r, v))
    rng = np.random.default_rng(seed + 101)
    kept = []
    for r in sorted(by_rel.keys()):
        lst = sorted(by_rel[r])
        if r in COARSE_RELS and kindof_cap and len(lst) > kindof_cap:
            idx = np.sort(rng.permutation(len(lst))[:kindof_cap])
            lst = [lst[i] for i in idx.tolist()]
        kept.extend(lst)
    kept = sorted(set(kept))

    concepts = sorted({c for (c, r, v) in kept})
    values = sorted({v for (c, r, v) in kept})
    _heartbeat(output_dir, "encode_concepts", {"n_concept": len(concepts), "n_value": len(values)})

    # GloVe encode (defines the shared in-vocab set; drops OOV -- IDENTICAL to the GloVe cell)
    g_cvec = {c: meaning_vec(glove_enc, c) for c in concepts}
    g_cvec = {c: v for c, v in g_cvec.items() if v is not None}
    g_vvec = {v: meaning_vec(glove_enc, v) for v in values}
    g_vvec = {v: mv for v, mv in g_vvec.items() if mv is not None}

    triples_iv = [(c, r, v) for (c, r, v) in kept if c in g_cvec and v in g_vvec]
    dropped = len(kept) - len(triples_iv)

    conc_iv = sorted({c for (c, r, v) in triples_iv})
    val_iv = sorted({v for (c, r, v) in triples_iv})

    # BGE encode the SAME shared strings (full coverage)
    bge = bge_encode(conc_iv + val_iv, output_dir, use_cache=use_bge_cache)
    b_cvec = {c: bge[c] for c in conc_iv}
    b_vvec = {v: bge[v] for v in val_iv}

    # char_trigram (substrate-native) encode the SAME shared strings (full coverage; L2-normalized)
    _heartbeat(output_dir, "encode_char_trigram", {"n_str": len(conc_iv) + len(val_iv)})
    tri_enc = CharTrigramEncoder(n_dim=TRIGRAM_DIM)
    t_cvec = {c: _l2(tri_enc.encode(c)) for c in conc_iv}
    t_vvec = {v: _l2(tri_enc.encode(v)) for v in val_iv}

    # shared indices (identical for all reps)
    cidx = {c: i for i, c in enumerate(conc_iv)}
    vidx = {v: i for i, v in enumerate(val_iv)}
    concept_vecs_glove = np.stack([g_cvec[c] for c in conc_iv], axis=0).astype(np.float32)
    concept_vecs_bge = np.stack([b_cvec[c] for c in conc_iv], axis=0).astype(np.float32)
    concept_vecs_trigram = np.stack([t_cvec[c] for c in conc_iv], axis=0).astype(np.float32)
    value_vecs_glove = np.stack([g_vvec[v] for v in val_iv], axis=0).astype(np.float32)
    value_vecs_bge = np.stack([b_vvec[v] for v in val_iv], axis=0).astype(np.float32)
    value_vecs_trigram = np.stack([t_vvec[v] for v in val_iv], axis=0).astype(np.float32)

    # per-relation value pool (GloVe-in-vocab values that appear as gold for that relation) -- identical pool
    pool = defaultdict(list)
    for (c, r, v) in triples_iv:
        pool[r].append(v)
    pool = {r: sorted(set(vs)) for r, vs in pool.items()}
    pool_gmat = {r: (np.stack([g_vvec[v] for v in pool[r]], axis=0), {v: i for i, v in enumerate(pool[r])}) for r in pool}
    pool_bmat = {r: (np.stack([b_vvec[v] for v in pool[r]], axis=0), {v: i for i, v in enumerate(pool[r])}) for r in pool}

    gold_by_cr = defaultdict(set)
    for (c, r, v) in triples_iv:
        gold_by_cr[(c, r)].add(v)

    # concept train/held-out split (same frac + rng discipline as harness)
    rng2 = np.random.default_rng(seed + 202)
    perm = rng2.permutation(len(conc_iv))
    n_hold = int(round(HELDOUT_CONCEPT_FRAC * len(conc_iv)))
    held_concepts = {conc_iv[i] for i in perm[:n_hold].tolist()}

    items = []
    g_dist_cos, b_dist_cos = [], []
    for (c, r, v) in triples_iv:
        p = pool[r]
        if len(p) < 2:
            continue
        excl = gold_by_cr[(c, r)]
        gmat, gpix = pool_gmat[r]
        bmat, bpix = pool_bmat[r]
        gdist = _nearest_distractors(v, p, gmat, gpix, excl, K_DISTRACT)
        bdist = _nearest_distractors(v, p, bmat, bpix, excl, K_DISTRACT)
        if not gdist or not bdist:
            continue
        gv_g, gv_b = g_vvec[v], b_vvec[v]
        g_dist_cos.append(float(np.mean([g_vvec[d] @ gv_g for d in gdist])))
        b_dist_cos.append(float(np.mean([b_vvec[d] @ gv_b for d in bdist])))
        items.append({
            "c_i": cidx[c], "r_i": REL_IDX[r], "gold_vi": vidx[v],
            "cand_vi_glove": [vidx[v]] + [vidx[d] for d in gdist],
            "cand_vi_bge": [vidx[v]] + [vidx[d] for d in bdist],
            "tier": ("coarse" if r in COARSE_RELS else "fine"),
            "concept": c, "relation": r, "gold": v, "held": (c in held_concepts),
        })

    env = {
        "concept_vecs_glove": concept_vecs_glove, "concept_vecs_bge": concept_vecs_bge,
        "concept_vecs_trigram": concept_vecs_trigram,
        "value_vecs_glove": value_vecs_glove, "value_vecs_bge": value_vecs_bge,
        "value_vecs_trigram": value_vecs_trigram,
        "conc_iv": conc_iv, "val_iv": val_iv, "cidx": cidx, "vidx": vidx,
        "items": items, "held_concepts": sorted(held_concepts),
        "n_triples_parsed": len(kept), "n_triples_invocab": len(triples_iv), "dropped_glove_oov": dropped,
        "pool_sizes": {r: len(pool[r]) for r in sorted(pool.keys())},
        "glove_native_mean_distractor_cos": round(float(np.mean(g_dist_cos)), 4) if g_dist_cos else None,
        "bge_native_mean_distractor_cos": round(float(np.mean(b_dist_cos)), 4) if b_dist_cos else None,
    }
    return env


# ---------------------------------------------------------------------------
# eval helpers (thin views over the harness discriminate/readouts)
# ---------------------------------------------------------------------------
def _cand_arrays(items, cand_key):
    W = K_DISTRACT + 1
    n = len(items)
    C = np.zeros((n, W), dtype=np.int64)
    mask = np.zeros((n, W), dtype=bool)
    gold = np.array([it["gold_vi"] for it in items], dtype=np.int64)
    for i, it in enumerate(items):
        cv = it[cand_key]
        C[i, :len(cv)] = cv
        mask[i, :len(cv)] = True
    return C, mask, gold


def _view(env, rep):
    """A minimal env-view exposing concept_vecs/value_vecs for the given rep, so harness fns work unchanged."""
    return {"concept_vecs": env["concept_vecs_" + rep], "value_vecs": env["value_vecs_" + rep]}


def zero_fit_fine(env, items, rep, cand_key):
    """Zero-fit cosine discrimination (frozen concept-vs-value). Returns per-tier dict for the item set."""
    view = _view(env, rep)
    C, mask, gold = _cand_arrays(items, cand_key)
    reps = frozen_reps(view, items)
    return discriminate(view, items, reps, C, mask, gold)


def learned_fine(env, train_items, eval_items, rep, cand_key, shuffle_seed=None):
    """Converged-ridge learned-linear over rep(concept)+onehot(rel) -> rep(value); eval on eval_items."""
    view = _view(env, rep)
    ro = fit_converged_linear(view, train_items, WEIGHT_DECAY, shuffle_seed=shuffle_seed)
    C, mask, gold = _cand_arrays(eval_items, cand_key)
    reps = learned_reps(view, eval_items, ro)
    return discriminate(view, eval_items, reps, C, mask, gold)


def _fine(res):
    return res["per_tier"].get("fine", {}).get("acc")


def _fine_ci(res):
    return res["per_tier"].get("fine", {}).get("ci")


def _fine_n(res):
    return res["per_tier"].get("fine", {}).get("n")


def _coarse(res):
    return res["per_tier"].get("coarse", {}).get("acc")


# ---------------------------------------------------------------------------
# self-test: planted zero-fit env + real BGE code path
# ---------------------------------------------------------------------------
def _planted_zero_fit(nd=64):
    """Planted: value vectors random; concept vector = its OWN gold value vector + small noise -> gold is the
    NEAREST value by cosine -> zero-fit fine acc ~1. Then DESTROY structure (concept = unrelated random) ->
    zero-fit collapses to ~chance. Proves the zero-fit discriminator can-fire AND can-fail."""
    rng = np.random.default_rng(31)
    n_val, W = 80, K_DISTRACT + 1   # larger N so the destroyed arm's empirical acc is tight near chance
    value_vecs = _l2_rows(rng.standard_normal((n_val, nd)).astype(np.float32))
    n_c = 50
    # structured concepts: concept i = value i + noise
    struct = _l2_rows(value_vecs[:n_c] + 0.05 * rng.standard_normal((n_c, nd)).astype(np.float32))
    # destroyed concepts: independent random
    destroyed = _l2_rows(rng.standard_normal((n_c, nd)).astype(np.float32))
    items = []
    for i in range(n_c):
        distract = [j for j in range(n_val) if j != i][:K_DISTRACT]
        items.append({"c_i": i, "r_i": 0, "gold_vi": i, "cand_vi_bge": [i] + distract,
                      "tier": "fine", "concept": f"c{i}", "relation": "R0", "gold": f"v{i}", "held": False})
    C, mask, gold = _cand_arrays(items, "cand_vi_bge")
    env_s = {"concept_vecs": struct, "value_vecs": value_vecs}
    env_d = {"concept_vecs": destroyed, "value_vecs": value_vecs}
    acc_s = discriminate(env_s, items, frozen_reps(env_s, items), C, mask, gold)["acc"]
    acc_d = discriminate(env_d, items, frozen_reps(env_d, items), C, mask, gold)["acc"]
    assert acc_s >= 0.9, f"planted: structured zero-fit did not fire (acc={acc_s})"
    assert acc_d <= 0.5, f"planted: destroyed zero-fit did not collapse (acc={acc_d})"
    return {"structured": acc_s, "destroyed": acc_d}


def self_test():
    print("[self-test] planted zero-fit: structured->~1, destroyed->~chance ...", flush=True)
    planted = _planted_zero_fit()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] REAL path: parse 2 tables + GloVe + BGE encode + shared env + zero-fit + converged-lin ...",
          flush=True)
    output_dir = _out_dir()
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=True, kv=kv)
    tiny = parse_tables((("MADEOF", 2, 6), ("HABITAT", 3, 5)))
    env = build_shared_environment(enc, tiny, kindof_cap=0, seed=SEED, output_dir=output_dir)
    items = env["items"]
    assert len(items) >= 20, f"real: too few items ({len(items)})"
    # BGE dim check
    assert env["concept_vecs_bge"].shape[1] == BGE_DIM, "real: BGE dim mismatch"
    # zero-fit both reps, both distractor constructions
    zf_g_gn = zero_fit_fine(env, items, "glove", "cand_vi_glove")
    zf_b_bn = zero_fit_fine(env, items, "bge", "cand_vi_bge")
    zf_b_gn = zero_fit_fine(env, items, "bge", "cand_vi_glove")
    zf_t_bn = zero_fit_fine(env, items, "trigram", "cand_vi_bge")
    assert env["concept_vecs_trigram"].shape[1] == TRIGRAM_DIM, "real: trigram dim mismatch"
    assert _fine(zf_t_bn) is not None, "real: char_trigram zero-fit fine None"
    # arms differ
    assert not np.allclose(env["concept_vecs_glove"][:1].shape, env["concept_vecs_bge"][:1].shape) or \
        env["concept_vecs_glove"].shape[1] != env["concept_vecs_bge"].shape[1], "real: reps same dim (unexpected)"
    assert (_fine(zf_b_bn) != _fine(zf_g_gn)) or (_fine(zf_b_bn) != _fine(zf_b_gn)), "real: arms identical (suspicious)"
    # learned converged path (in-vocab) both reps
    train_items = [it for it in items if not it["held"]]
    lin_b = learned_fine(env, train_items, train_items, "bge", "cand_vi_bge")
    lin_g = learned_fine(env, train_items, train_items, "glove", "cand_vi_glove")
    assert _fine(lin_b) is not None and _fine(lin_g) is not None, "real: learned fine None"
    # determinism (BGE cache + closed-form both deterministic)
    zf_b_bn2 = zero_fit_fine(env, items, "bge", "cand_vi_bge")
    assert _fine(zf_b_bn) == _fine(zf_b_bn2), "real: zero-fit non-deterministic"
    print(f"[self-test]   real: n_items={len(items)} zf_glove_gn_fine={_fine(zf_g_gn)} zf_bge_bn_fine={_fine(zf_b_bn)} "
          f"zf_bge_gn_fine={_fine(zf_b_gn)} zf_trigram_bn_fine={_fine(zf_t_bn)} lin_bge_iv={_fine(lin_b)} lin_glove_iv={_fine(lin_g)} "
          f"bge_native_dcos={env['bge_native_mean_distractor_cos']} glove_native_dcos={env['glove_native_mean_distractor_cos']} "
          f"dropped_glove_oov={env['dropped_glove_oov']}", flush=True)
    print("[self-test] PASS (planted zero-fit fires+fails; real GloVe+BGE parse/encode/eval; determinism; arms differ)",
          flush=True)
    return True


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"tables": (("KINDOF", 1, 4), ("MADEOF", 2, 6), ("CONTAINS", 2, 6), ("SOURCEOF", 2, 7),
                           ("PROP-RESOURCES-RENEWABLE", 0, 4)),
                "kindof_cap": 150}
    return {"tables": CURATED_TABLES, "kindof_cap": 700}


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _verdict(bge_zf_fine_bn, glove_zf_fine_bn_sameset, glove_zf_fine_gn, chance_bn, bge_ci_lo,
            bge_native_dcos, n_eval_fine):
    lift_chance = round(bge_zf_fine_bn - chance_bn, 4) if bge_zf_fine_bn is not None else None
    margin_glove = round(bge_zf_fine_bn - glove_zf_fine_bn_sameset, 4) \
        if (bge_zf_fine_bn is not None and glove_zf_fine_bn_sameset is not None) else None
    ci_lo_pos = (bge_ci_lo is not None and bge_ci_lo > chance_bn)
    extra = {"bge_zf_fine_lift_over_chance": lift_chance, "bge_zf_fine_margin_over_glove_sameset": margin_glove,
             "bge_ci_lower_above_chance": bool(ci_lo_pos), "chance_bge_native": chance_bn,
             "glove_zf_fine_original_wall": glove_zf_fine_gn}

    if n_eval_fine < MIN_EVAL_FINE:
        return "INVALID", f"only {n_eval_fine} fine eval items (< {MIN_EVAL_FINE}) -- noise-floor breach", extra
    if bge_native_dcos is not None and bge_native_dcos < DIST_NEAR_MIN:
        return "INVALID", (f"BGE-native mean cos(gold,distractor)={bge_native_dcos} < {DIST_NEAR_MIN}: distractors "
                           f"not actually near in BGE space -- can-fail broken, inspect selection"), extra
    if bge_zf_fine_bn is not None and bge_zf_fine_bn >= FROZEN_SAT:
        return "INVALID", (f"BGE zero-fit fine={bge_zf_fine_bn} >= {FROZEN_SAT}: task too easy -- BGE-native "
                           f"distractors not hard enough"), extra
    if lift_chance is not None and lift_chance >= CLEAR_OVER_CHANCE and ci_lo_pos and \
            margin_glove is not None and margin_glove >= MARGIN_OVER_GLOVE:
        return "BGE-CLEARS-WALL", (f"BGE zero-fit FINE (bge-native distractors)={bge_zf_fine_bn} clears chance="
                                   f"{chance_bn} by {lift_chance}>={CLEAR_OVER_CHANCE} (CI-lower>{chance_bn}) AND beats "
                                   f"GloVe (same candidate set)={glove_zf_fine_bn_sameset} by {margin_glove}>="
                                   f"{MARGIN_OVER_GLOVE}: the fine-discrimination signal DOES exist in text and is "
                                   f"reachable by relational/contrastive supervision (BGE) where raw co-occurrence (GloVe) "
                                   f"cannot -- memorization-proof zero-fit. ROUTING FACT for OUR grounding build: aim at "
                                   f"that relational signal; BGE is a DIAGNOSTIC CEILING, NOT an encoder to adopt/distill"), extra
    if lift_chance is not None and lift_chance < THIN_OVER_CHANCE or not ci_lo_pos:
        return "BGE-ALSO-THIN", (f"BGE zero-fit FINE (bge-native)={bge_zf_fine_bn} is NOT materially above chance="
                                 f"{chance_bn} (lift={lift_chance}<{THIN_OVER_CHANCE} or CI-lower<=chance): even a strong "
                                 f"text encoder's RAW cosine cannot separate fine content from its OWN nearest wrong "
                                 f"values -> the signal is NOT cheaply present in text similarity; the wall is DEEPER than "
                                 f"any off-the-shelf embedder -> OUR grounding build needs structure/grounding, not text "
                                 f"embeddings"), extra
    return "MIDDLE", (f"BGE zero-fit FINE (bge-native)={bge_zf_fine_bn} is materially above chance={chance_bn} "
                      f"(lift={lift_chance}) but not to the CLEAR bar (need lift>={CLEAR_OVER_CHANCE} + margin-over-GloVe>="
                      f"{MARGIN_OVER_GLOVE}; got margin={margin_glove}): PARTIAL fine signal in text -- stronger than raw "
                      f"co-occurrence but grounding/structure still indicated for the rest; BGE is a DIAGNOSTIC, not to adopt"), extra


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def run(mode, output_dir):
    from datetime import datetime, timezone
    cfg = _config(mode)
    _heartbeat(output_dir, "parse_tables")
    triples = parse_tables(cfg["tables"])
    _heartbeat(output_dir, "load_glove", {"n_triples": len(triples)})
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "build_shared_environment")
    env = build_shared_environment(enc, triples, cfg["kindof_cap"], SEED, output_dir)
    items = env["items"]
    fine_items = [it for it in items if it["tier"] == "fine"]
    train_items = [it for it in items if not it["held"]]
    held_items = [it for it in items if it["held"]]
    n_eval_fine = len(fine_items)
    print(f"[env] triples_parsed={env['n_triples_parsed']} invocab={env['n_triples_invocab']} "
          f"dropped_glove_oov={env['dropped_glove_oov']} items={len(items)} fine={n_eval_fine} "
          f"train={len(train_items)} held={len(held_items)}", flush=True)
    print(f"[env] pool_sizes={env['pool_sizes']} bge_native_dcos={env['bge_native_mean_distractor_cos']} "
          f"glove_native_dcos={env['glove_native_mean_distractor_cos']}", flush=True)

    # chance per candidate-set construction (fine items)
    chance_bn = round(float(np.mean([1.0 / len(it["cand_vi_bge"]) for it in fine_items])), 4) if fine_items else None
    chance_gn = round(float(np.mean([1.0 / len(it["cand_vi_glove"]) for it in fine_items])), 4) if fine_items else None

    # ---- ZERO-FIT 2x2 matrix (encoder x distractor-construction) over ALL shared fine items ----
    _heartbeat(output_dir, "zero_fit_matrix")
    # PRIMARY: bge-native candidate sets, both encoders (same-candidate-set head-to-head)
    zf_bge_bn = zero_fit_fine(env, items, "bge", "cand_vi_bge")
    zf_glove_bn = zero_fit_fine(env, items, "glove", "cand_vi_bge")
    # ORIGINAL WALL + inflation cross term: glove-native candidate sets, both encoders
    zf_glove_gn = zero_fit_fine(env, items, "glove", "cand_vi_glove")
    zf_bge_gn = zero_fit_fine(env, items, "bge", "cand_vi_glove")
    # SUBSTRATE-NATIVE floor: char_trigram on BOTH candidate constructions
    zf_tri_bn = zero_fit_fine(env, items, "trigram", "cand_vi_bge")
    zf_tri_gn = zero_fit_fine(env, items, "trigram", "cand_vi_glove")

    bge_zf_fine_bn = _fine(zf_bge_bn)
    bge_zf_fine_bn_ci = _fine_ci(zf_bge_bn)
    bge_ci_lo = bge_zf_fine_bn_ci[0] if bge_zf_fine_bn_ci else None
    glove_zf_fine_bn = _fine(zf_glove_bn)
    glove_zf_fine_gn = _fine(zf_glove_gn)
    bge_zf_fine_gn = _fine(zf_bge_gn)
    print(f"[zero-fit] BGE-native cands:  BGE_fine={bge_zf_fine_bn} (ci={bge_zf_fine_bn_ci}) "
          f"GloVe_fine={glove_zf_fine_bn} chance={chance_bn}", flush=True)
    print(f"[zero-fit] GloVe-native cands: GloVe_fine={glove_zf_fine_gn} (ORIGINAL WALL) BGE_fine={bge_zf_fine_gn} "
          f"(inflated) chance={chance_gn}", flush=True)
    print(f"[zero-fit] char_trigram (substrate-native): bge_native={_fine(zf_tri_bn)} glove_native={_fine(zf_tri_gn)}",
          flush=True)
    print(f"[zero-fit] coarse: BGE_bn={_coarse(zf_bge_bn)} GloVe_gn={_coarse(zf_glove_gn)} tri_bn={_coarse(zf_tri_bn)}",
          flush=True)

    # ---- SECONDARY: learned-linear (converged ridge) held-out-to-NEW-concepts + in-vocab (both reps) ----
    _heartbeat(output_dir, "learned_linear")
    lin_bge_iv = learned_fine(env, train_items, train_items, "bge", "cand_vi_bge")
    lin_bge_ho = learned_fine(env, train_items, held_items, "bge", "cand_vi_bge") if held_items else {"per_tier": {}}
    lin_glove_iv = learned_fine(env, train_items, train_items, "glove", "cand_vi_glove")
    lin_glove_ho = learned_fine(env, train_items, held_items, "glove", "cand_vi_glove") if held_items else {"per_tier": {}}
    # shuffled-target control on the learned BGE arm (train permuted, eval TRUE, in-vocab)
    lin_bge_iv_shuf = learned_fine(env, train_items, train_items, "bge", "cand_vi_bge", shuffle_seed=SEED + 9090)
    print(f"[learned] BGE  in-vocab={_fine(lin_bge_iv)} held-out={_fine(lin_bge_ho)} shuffled_iv={_fine(lin_bge_iv_shuf)}",
          flush=True)
    print(f"[learned] GloVe in-vocab={_fine(lin_glove_iv)} held-out={_fine(lin_glove_ho)}", flush=True)

    # ---- verdict (PRIMARY = zero-fit, bge-native, same-candidate-set BGE vs GloVe vs chance) ----
    bge_sat = (bge_zf_fine_bn is not None and bge_zf_fine_bn >= FROZEN_SAT)
    verdict, vmsg, gx = _verdict(bge_zf_fine_bn, glove_zf_fine_bn, glove_zf_fine_gn, chance_bn, bge_ci_lo,
                                 env["bge_native_mean_distractor_cos"], n_eval_fine)

    arms_differ = not (bge_zf_fine_bn is not None and glove_zf_fine_bn is not None
                       and abs(bge_zf_fine_bn - glove_zf_fine_bn) < 1e-9
                       and abs(bge_zf_fine_bn - (bge_zf_fine_gn or -1)) < 1e-9)

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": f"{verdict}: {vmsg}",
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME, "seed": SEED,
        "bge_model": BGE_MODEL, "bge_dim": BGE_DIM,
        "one_variable": "the representation / meaning SOURCE (frozen GloVe 300d vs BGE-large 1024d); identical items + identical candidate sets",
        "primary_metric": "ZERO-FIT cosine FINE-tier discrimination on BGE-NATIVE candidate sets, BGE vs GloVe vs chance (memorization-proof)",
        # scale / coverage / difficulty-on
        "n_triples_parsed": env["n_triples_parsed"], "n_triples_invocab_shared": env["n_triples_invocab"],
        "dropped_glove_oov": env["dropped_glove_oov"], "n_items": len(items),
        "n_eval_fine": n_eval_fine, "n_heldout_items": len(held_items), "n_heldout_concepts": len(env["held_concepts"]),
        "bge_coverage_note": "BGE encodes ALL shared strings (no OOV); shared item set = GloVe-in-vocab items (identical to the GloVe cell); coverage of shared items by BGE = 100%",
        "pool_sizes": env["pool_sizes"], "K_distract": K_DISTRACT,
        "chance_bge_native": chance_bn, "chance_glove_native": chance_gn,
        "bge_native_mean_distractor_cos": env["bge_native_mean_distractor_cos"],
        "glove_native_mean_distractor_cos": env["glove_native_mean_distractor_cos"],
        # PRIMARY: zero-fit 2x2 (encoder x distractor-construction), FINE tier
        "zf_bge_fine__bge_native": bge_zf_fine_bn, "zf_bge_fine__bge_native_ci": bge_zf_fine_bn_ci,
        "zf_glove_fine__bge_native": glove_zf_fine_bn,          # same candidate set head-to-head
        "zf_glove_fine__glove_native": glove_zf_fine_gn,        # ORIGINAL WALL (frozen GloVe on its own hard distractors)
        "zf_bge_fine__glove_native": bge_zf_fine_gn,            # inflated cross term (GloVe-near != BGE-near)
        "zf_char_trigram_fine__bge_native": _fine(zf_tri_bn),   # SUBSTRATE-NATIVE floor (same-set head-to-head)
        "zf_char_trigram_fine__glove_native": _fine(zf_tri_gn),
        "zf_bge_coarse__bge_native": _coarse(zf_bge_bn), "zf_glove_coarse__glove_native": _coarse(zf_glove_gn),
        "zf_char_trigram_coarse__bge_native": _coarse(zf_tri_bn),
        "bge_zf_fine_lift_over_chance": gx["bge_zf_fine_lift_over_chance"],
        "bge_zf_fine_margin_over_glove_sameset": gx["bge_zf_fine_margin_over_glove_sameset"],
        "bge_ci_lower_above_chance": gx["bge_ci_lower_above_chance"],
        # SECONDARY: learned-linear (converged ridge) -- reported, NOT the primary gate
        "learned_bge_fine_invocab": _fine(lin_bge_iv), "learned_bge_fine_invocab_ci": _fine_ci(lin_bge_iv),
        "learned_bge_fine_heldout": _fine(lin_bge_ho), "learned_bge_fine_heldout_ci": _fine_ci(lin_bge_ho),
        "learned_bge_fine_invocab_shuffled_control": _fine(lin_bge_iv_shuf),
        "learned_glove_fine_invocab": _fine(lin_glove_iv), "learned_glove_fine_heldout": _fine(lin_glove_ho),
        "learned_note": "GloVe learned reproduces the wall (in-vocab~memorization, held-out~chance); BGE learned held-out tests whether learning ADDS generalizable structure on top of the meaning source",
        # controls / integrity
        "arms_differ_verified": bool(arms_differ),
        "bands": {"CLEAR_OVER_CHANCE": CLEAR_OVER_CHANCE, "MARGIN_OVER_GLOVE": MARGIN_OVER_GLOVE,
                  "THIN_OVER_CHANCE": THIN_OVER_CHANCE, "FROZEN_SAT": FROZEN_SAT,
                  "DIST_NEAR_MIN": DIST_NEAR_MIN, "MIN_EVAL_FINE": MIN_EVAL_FINE},
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_sorted_bge_eval_mode",
        "storage": "no_composition_selfcontained_probe",
        "difficulty_on": f"BGE-native nearest hard distractors; mean bge cos(gold,distractor)={env['bge_native_mean_distractor_cos']}",
        "contract": "INLINE-LOCAL foreground-to-completion; no push/remote-persist; HF offline; VET-PENDING (skunkworks owns landed-VET)",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[gates] {gx}", flush=True)
    print(f"[one-line] fine-signal-in-text probe (BGE=diagnostic ceiling, NOT to adopt): zero-fit BGE-cosine "
          f"{bge_zf_fine_bn} vs GloVe {glove_zf_fine_bn} vs char_trigram {_fine(zf_tri_bn)} vs chance {chance_bn} "
          f"(BGE-native distractors); held-out learned-linear BGE {_fine(lin_bge_ho)}; verdict {verdict}", flush=True)
    return metrics


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    _T0[0] = time.perf_counter()
    output_dir = _out_dir()

    if args.self_test:
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    _write_start_marker(output_dir, mode)
    run(mode, output_dir)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir_top = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir_top, e)
        raise
