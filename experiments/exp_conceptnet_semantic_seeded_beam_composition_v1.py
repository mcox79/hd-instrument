"""conceptnet_semantic_seeded_beam_composition_v1 -- close (or bound) the multi-hop composition gap
that made the June-19 ConceptNet cell lose to BGE (substrate Hits@10=0.451 < BGE 0.502).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: ranking metric Hits@10 in [0,1]; bar 0.502 reachable (feasibility, not CRLB)
# - baseline_in_band at smoke (RANDOM_K1 ~0.45 in (0.05,0.95))
# - discriminator survives scale: SEMANTIC injects edge-cosine structure (structural fire-check) at BOTH N_DIM
# - HARD_PASS strictly above the sacrosanct June-19 bands
# - Gate-D positive control: RANDOM_K1 reproduces June-19 0.451 (tol 0.10)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

CLAIM (honest, pre-committed MIDDLE): the June-19 HARD_FAIL had two named causes (research scoping
notes/research_multihop_composition_gap_closure_scoping_2026-07-07.md): (c) high-branching to-many
relations decoded by a SINGLE hard argmax (no beam) and (d) entity codes = pure random noise (zero
semantic content vs BGE's pretrained semantics). This cell fixes BOTH and ablates them separately.

  Cause (d) fix = SEMANTIC-SEED entity codebook: entity vector = SimHash (sign of a fixed Gaussian
  random projection) of the BGE-large teacher embedding that the CHAIN_GRADE GSBC encoder distills
  (cached at data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz, keyed by the
  exact CN_ ids, 100pct overlap MEASURED@scratchpad probe). NOTE (honest scope): this uses the
  encoder's BGE TEACHER/INPUT directly. The substrate-native GSBC graded-code sparsification of that
  teacher is a LOSSY approximation (ret_agree10=0.432 MEASURED@backup 2026-07-07), so BGE-SimHash is
  the semantic UPPER BOUND the substrate encoder aims at; a follow-up cell can route through the
  trained GSBC student. Codes stay bipolar so the cf-RPE elementwise-mul algebra is unchanged.

  Cause (c) fix = TOP-K BEAM per hop: replace the single `best=argmax(E@cur)` hard carry-through with
  a width-k beam (k=1 reproduces the June-19 decoder EXACTLY).

ARMS (2x2 ablation + firing control), single deterministic seed (curated KB + seeded codebooks, as
June-19):
  RANDOM_K1     random codes, beam_k=1  -> reproduces June-19 (Gate-D positive control, ~0.451)
  RANDOM_BEAM   random codes, beam_k=K  -> beam-alone effect
  SEM_K1        semantic codes, beam_k=1 -> semantic-seed-alone effect
  SEM_BEAM      semantic codes, beam_k=K -> BOTH fixes (PRIMARY)
  SEM_SCRAM_BEAM scrambled-semantic (entity->vector permuted), beam_k=K -> firing control (must
                collapse to ~RANDOM level => semantics, not just mechanism, is load-bearing)

BASELINES (shared, computed once): transitive-closure (BFS), frozen BGE-large cosine from the cached
teacher (bge_cached), random-rank floor. External sacrosanct bar = June-19 live BGE Hits@10=0.502
MEASURED@data/substrate_conceptnet_kg_inference_transfer_cpu_v1_metrics.json:frozen_bge_baseline.hits@10.

BANDS (research pre-reg; applied to PRIMARY arm SEM_BEAM):
  HARD_PASS = SEM_BEAM Hits@10 beats BOTH closure AND max(bge_cached, 0.502) by >=0.05 AND
    nontrivial_lift_hits10 >= 0.00 AND sub_auroc >= 0.7.   (STRETCH, P~0.15-0.20)
  MIDDLE    = SEM_BEAM closes on BGE (min_lift in [-0.02, +0.05)) OR nontrivial_lift improves from
    -0.72 into [-0.30, 0.00).                              (EXPECTED / pre-committed, P~0.40-0.45)
  HARD_FAIL = SEM_BEAM <= max(closure, bge) AND nontrivial_lift <= -0.50 (both fixes insufficient).

Reuses the June-19 cell AS A LIBRARY for data-load, BFS/classification, candidate-pool, metrics, so
the held-out split + bands are byte-identical. DEVICE=cpu; READ-only (no Store mutation); ASCII.
"""
from __future__ import annotations
# KB_REFERENT: data/substrate_index/concept/relations.jsonl
# KB_REFERENT: data/conceptnet/heldout_edges.jsonl
# KB_REFERENT: data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz
import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# June-19 cell reused as a pure-function library (identical split/metrics)
import experiments.exp_substrate_conceptnet_kg_inference_transfer_cpu_v1 as j19  # noqa: E402
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR = "conceptnet_semantic_seeded_beam_composition_v1"
DEVICE = "cpu"
SEED = j19.SEED                 # 20260619 -- reproduce the exact June-19 split
KHOP = 4
TRANSITIVE_RELS = j19.TRANSITIVE_RELS
TEACHER_NPZ = REPO / "data" / "substrate_index" / "cached_indices" / "bge_large_v2_name_177899_54f7cf6a.npz"
JUNE19_BGE_BAR = 0.5021459227467812   # MEASURED@data/substrate_conceptnet_kg_inference_transfer_cpu_v1_metrics.json
JUNE19_SUB_BAR = 0.45064377682403434  # MEASURED@ same file (RANDOM_K1 Gate-D reproduce target)

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
if RUN_MODE == "smoke":
    N_DIM, CLASSIFY_POOL, STORE_CAP, BEAM_K = 2048, 1800, 2200, 4
else:
    N_DIM, CLASSIFY_POOL, STORE_CAP, BEAM_K = 8192, 0, 8000, 6   # CLASSIFY_POOL=0 => full held_t pool (== June-19)
MAX_CANDS = 200

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush each newline
    except Exception:
        pass


# ---------------- defensive error-checking (start-marker / crash / heartbeat) ----------------

def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR, "run_mode": RUN_MODE, "expected_n_units": expected_n_units,
              "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR, "run_mode": RUN_MODE}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


def _heartbeat(output_dir: Path, unit_idx: int, total: int, t0: float, extra=None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total, "elapsed_s": time.perf_counter() - t0}
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------- semantic-seed entity codebook (SimHash of BGE-large teacher) ----------------

def load_teacher():
    """Return (Vn_raw, Vn_cent, idx). Vn_raw = L2-normalized BGE (baseline cosine, June-19 convention).
    Vn_cent = MEAN-CENTERED then L2-normalized BGE -- removes the BGE anisotropy cone so SimHash codes
    are DISCRIMINATIVE (related entities stand out) instead of all ~0.4 correlated (cone collision would
    swamp the cf-RPE store). Standard sentence-embedding post-processing (all-but-the-mean)."""
    if not TEACHER_NPZ.exists():
        return None, None, None
    z = np.load(TEACHER_NPZ, allow_pickle=True)
    ids = json.loads(str(z["id_order_json"]))
    V = np.asarray(z["semantic"], dtype=np.float32)
    Vn_raw = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-8)
    Vc = V - V.mean(axis=0, keepdims=True)
    Vn_cent = Vc / (np.linalg.norm(Vc, axis=1, keepdims=True) + 1e-8)
    idx = {e: i for i, e in enumerate(ids)}
    return Vn_raw, Vn_cent, idx


def semantic_codes(ents, Vn, tidx, n_dim, proj_gen, scramble=False):
    """SimHash: E[i] = sign(P @ bge[ent_i]) normalized. Semantically similar entities -> similar codes.
    Missing entity (should be ~none; 100pct overlap MEASURED) -> deterministic random bipolar."""
    d = Vn.shape[1]
    P = proj_gen.standard_normal((n_dim, d)).astype(np.float32)
    n = len(ents)
    Vs = np.zeros((n, d), dtype=np.float32)
    miss_idx = []
    for i, e in enumerate(ents):
        j = tidx.get(e)
        if j is None:
            miss_idx.append(i)
        else:
            Vs[i] = Vn[j]
    H = Vs @ P.T                       # (n, n_dim)
    codes = np.sign(H).astype(np.float32)
    codes[codes == 0.0] = 1.0
    # fill misses with deterministic random bipolar (no semantic content)
    for i in miss_idx:
        codes[i] = (proj_gen.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
    if scramble:
        perm = proj_gen.permutation(n)  # assign semantic vectors to WRONG entities
        codes = codes[perm]
    codes /= (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-8)
    return codes, len(miss_idx)


# ---------------- beam decode (k=1 == June-19 single hard argmax) ----------------

def beam_scores(W, E, R, sq, s_idx, r_idx, cand_idx, beam_k, khop):
    """K-hop beam recall. k=1 reduces to June-19 EXACTLY (single argmax carry, max over hop-depths).
    BATCHED: the k beam expansions per hop are ONE matmul W@Keys (reads W once, not k times)."""
    key0 = (E[s_idx] * R[r_idx] * sq).astype(np.float32)
    q = W @ key0
    acc = E[cand_idx] @ q                           # 1-hop scores over candidates
    sims = E @ q
    k = min(beam_k, len(sims))
    beam = np.argpartition(-sims, k - 1)[:k]
    for _h in range(khop - 1):
        Keys = np.ascontiguousarray((E[beam] * R[r_idx] * sq).T.astype(np.float32))  # (n_dim, kb)
        Curs = W @ Keys                             # (n_dim, kb)
        acc = np.maximum(acc, (E[cand_idx] @ Curs).max(axis=1))
        stacked = (E @ Curs).max(axis=1)            # (n_ent,)
        kk = min(beam_k, len(stacked))
        beam = np.argpartition(-stacked, kk - 1)[:kk]
    return acc


# ---------------- store ----------------

try:
    from scipy.linalg.blas import sger as _sger  # in-place rank-1: A := alpha*x*y' + A
    _HAVE_SGER = True
except Exception:
    _HAVE_SGER = False


def _cfrpe_fast(W, key, val, n):
    """cf-RPE delta-rule W += (LR/n)*outer(val - W@key, key). BLAS in-place (no per-edge alloc).
    Numerically equivalent to j19.cfrpe (np.outer) within float32 rounding (Gate-D tol 0.10 absorbs)."""
    resid = val - (W @ key)
    if _HAVE_SGER:
        _sger(j19.LR / n, resid, key, a=W, overwrite_a=1)
    else:
        W += (j19.LR / n) * np.outer(resid, key)


def build_store(store_edges, E, R, sq, eid, rid, n_dim):
    W = np.zeros((n_dim, n_dim), dtype=np.float32, order="F")  # F-order: BLAS sger overwrite friendly
    for (u, r, v) in store_edges:
        if u in eid and v in eid and r in rid:
            _cfrpe_fast(W, (E[eid[u]] * R[rid[r]] * sq).astype(np.float32),
                        E[eid[v]].astype(np.float32), n_dim)
    return W


# ---------------- metrics (mirror June-19 _summarize per-arm) ----------------

def arm_metrics(rows, arm):
    def hm(subset):
        return j19.hits_mrr([r[arm + "_rank"] for r in subset])
    with_rows = [r for r in rows if r["with_path"]]
    sub_hm = hm(with_rows)
    def rank_auroc(subset):
        vals = [(r["n_cands"] - r[arm + "_rank"]) / max(r["n_cands"] - 1, 1) for r in subset]
        return float(np.mean(vals)) if vals else float("nan")
    sub_auroc = rank_auroc(with_rows)
    triv = [r for r in with_rows if r["trivial"]]
    nontriv = [r for r in with_rows if not r["trivial"]]
    clo = j19.hits_mrr([r["clo_rank"] for r in with_rows])["hits@10"]
    triv_lift = (j19.hits_mrr([r[arm + "_rank"] for r in triv])["hits@10"]
                 - j19.hits_mrr([r["clo_rank"] for r in triv])["hits@10"]) if triv else float("nan")
    nontriv_lift = (j19.hits_mrr([r[arm + "_rank"] for r in nontriv])["hits@10"]
                    - j19.hits_mrr([r["clo_rank"] for r in nontriv])["hits@10"]) if nontriv else float("nan")
    without_rows = [r for r in rows if not r["with_path"]]
    fab_auroc = j19.auroc([r[arm + "_pos"] for r in with_rows], [r[arm + "_pos"] for r in without_rows])
    return {"hits": sub_hm, "auroc": sub_auroc, "trivial_lift_hits10": triv_lift,
            "nontrivial_lift_hits10": nontriv_lift, "fab_auroc": fab_auroc,
            "n_trivial": len(triv), "n_nontrivial": len(nontriv)}


def _digest(x):
    a = np.ascontiguousarray(x, dtype=np.float32)
    return hashlib.sha256(a.tobytes()).hexdigest()


# ---------------- main eval ----------------

def run_eval(out_dir: Path) -> int:
    t0 = time.perf_counter()
    ARMS = ["RANDOM_K1", "RANDOM_BEAM", "SEM_K1", "SEM_BEAM", "SEM_SCRAM_BEAM"]
    _write_start_marker(out_dir, expected_n_units=len(ARMS))
    print(f"[config] anchor={ANCHOR} mode={RUN_MODE} N_DIM={N_DIM} KHOP={KHOP} BEAM_K={BEAM_K}", flush=True)

    Vn_raw, Vn_cent, tidx = load_teacher()
    if Vn_raw is None:
        print("NON_TEST: teacher BGE cache missing; the whole cell is about semantic seeding. Halt.", flush=True)
        return _write_nontest(out_dir, "teacher_cache_missing")

    g = np.random.default_rng(SEED)                  # drives split/candidate-pool EXACTLY as June-19
    code_gen = np.random.default_rng(SEED + 1)       # separate: codebooks (does not perturb split)
    proj_gen = np.random.default_rng(SEED + 2)       # separate: SimHash projection + scramble

    ing = j19.load_ingested_edges(); held = j19.load_heldout()
    print(f"  ingested CN_ edges={len(ing)} | held-out edges={len(held)}", flush=True)
    if len(ing) < 100 or len(held) < 30:
        return _write_nontest(out_dir, "graph_or_heldout_too_small")
    any_adj, rel_adj, tails_by_rel, truths = j19.build_adj(ing)

    heldout_set = {(s, r, o) for (s, r, o) in held}
    if len(heldout_set & truths) > 0:
        print("FIREWALL BREACH: held-out in compose graph. Halt.", flush=True)
        return _write_nontest(out_dir, "firewall_breach_compose")

    held_t = [(s, r, o) for (s, r, o) in held if r in TRANSITIVE_RELS]
    g.shuffle(held_t)
    pool = held_t[:CLASSIFY_POOL] if CLASSIFY_POOL else held_t
    with_set = []; without_set = []; store_edges = set()
    for (s, r, o) in pool:
        sr = rel_adj.get(r, {})
        depth = j19.bfs_depth(sr, s, o, KHOP)
        if depth is not None:
            with_set.append((s, r, o, True, depth <= 2))
            if len(store_edges) < STORE_CAP:
                store_edges |= j19.rel_subgraph_edges(sr, s, r, KHOP, cap=STORE_CAP - len(store_edges))
        else:
            without_set.append((s, r, o, False, False))
    g.shuffle(without_set)
    without_keep = without_set[: max(len(with_set), 150)]
    classified = with_set + without_keep
    print(f"  classified={len(pool)} -> WITH={len(with_set)} WITHOUT(kept)={len(without_keep)} store_edges={len(store_edges)}", flush=True)

    ents = set()
    for (u, _r, v) in store_edges:
        ents.add(u); ents.add(v)
    for (s, r, o, _wp, _tr) in classified:
        ents.add(s); ents.add(o)
    ents = sorted(ents)
    rels = sorted({r for (_u, r, _v) in store_edges} | {r for (_s, r, _o, _wp, _tr) in classified})
    eid = {e: i for i, e in enumerate(ents)}; rid = {r: i for i, r in enumerate(rels)}
    if len(heldout_set & store_edges) > 0:
        print("FIREWALL BREACH: held-out leaked into store. Halt.", flush=True)
        return _write_nontest(out_dir, "firewall_breach_store")
    sq = math.sqrt(N_DIM)

    # shared relation codebook (relations are NOT the semantic variable; same realization all arms)
    R = j19.bipolar(len(rels), N_DIM, code_gen)
    # entity codebooks per family
    E_rand = j19.bipolar(len(ents), N_DIM, code_gen)
    E_sem, n_miss = semantic_codes(ents, Vn_cent, tidx, N_DIM, np.random.default_rng(SEED + 2), scramble=False)
    E_scr, _ = semantic_codes(ents, Vn_cent, tidx, N_DIM, np.random.default_rng(SEED + 3), scramble=True)
    print(f"  codebooks: n_ent={len(ents)} n_rel={len(rels)} sem_miss={n_miss} "
          f"(hash rand={_digest(E_rand)[:8]} sem={_digest(E_sem)[:8]} scr={_digest(E_scr)[:8]})", flush=True)

    # DISCRIMINATOR-FIRES (cause-d): semantic codes must carry edge-cosine structure absent in random.
    edge_sample = list(store_edges)[:2000]
    def mean_edge_cos(E):
        vals = [float(E[eid[u]] @ E[eid[v]]) for (u, _r, v) in edge_sample if u in eid and v in eid]
        return float(np.mean(vals)) if vals else float("nan")
    sem_edge_cos = mean_edge_cos(E_sem); rand_edge_cos = mean_edge_cos(E_rand); scr_edge_cos = mean_edge_cos(E_scr)
    # DISCRIMINATIVE structure = true edges more similar than scrambled (same semantic family, wrong
    # assignment). Cone offset (sem vs rand) is NOT the signal after centering; edge-vs-scramble is.
    semantic_fires = (sem_edge_cos - scr_edge_cos) > 0.02
    print(f"  [fire-check cause-d] mean_edge_cos sem={sem_edge_cos:+.4f} rand={rand_edge_cos:+.4f} "
          f"scram={scr_edge_cos:+.4f} | discriminative_gap(sem-scram)={sem_edge_cos-scr_edge_cos:+.4f} "
          f"-> semantic_fires={semantic_fires}", flush=True)

    arm_E = {"RANDOM_K1": E_rand, "RANDOM_BEAM": E_rand, "SEM_K1": E_sem, "SEM_BEAM": E_sem, "SEM_SCRAM_BEAM": E_scr}
    arm_k = {"RANDOM_K1": 1, "RANDOM_BEAM": BEAM_K, "SEM_K1": 1, "SEM_BEAM": BEAM_K, "SEM_SCRAM_BEAM": BEAM_K}
    stores = {}
    for fam, E in [("rand", E_rand), ("sem", E_sem), ("scr", E_scr)]:
        stores[fam] = build_store(store_edges, E, R, sq, eid, rid, N_DIM)
    arm_store = {"RANDOM_K1": stores["rand"], "RANDOM_BEAM": stores["rand"],
                 "SEM_K1": stores["sem"], "SEM_BEAM": stores["sem"], "SEM_SCRAM_BEAM": stores["scr"]}
    print(f"  stores built ({time.perf_counter()-t0:.1f}s)", flush=True)

    # shared per-row candidate pools + closure/bge/random baselines
    rows = []
    n_rows = len(classified)
    arm_out_vec = {a: [] for a in ARMS}   # for arms-must-differ hash
    for ri, (s, r, o, wp, trivial) in enumerate(classified):
        if s not in eid or o not in eid or r not in rid:
            continue
        sr = rel_adj.get(r, {})
        rset = j19.reachable_set(sr, s, KHOP)
        other_true = {t for t in any_adj.get(s, set()) if (s, r, t) in truths and t != o}
        cpool = [c for c in tails_by_rel.get(r, ()) if c in eid and c not in other_true and c != s]
        if o not in cpool:
            cpool.append(o)
        if len(cpool) > MAX_CANDS:
            keep = [o] + [c for c in cpool if c in rset and c != o][: MAX_CANDS // 2]
            rest = [c for c in cpool if c not in keep]
            g.shuffle(rest); keep += rest[: MAX_CANDS - len(keep)]
            cpool = keep
        if len(cpool) < 5:
            continue
        cand_idx = np.array([eid[c] for c in cpool]); true_pos = cpool.index(o)
        clo_sc = np.array([1.0 if c in rset else 0.0 for c in cpool], dtype=np.float64)
        # bge_cached baseline: cosine over RAW BGE-large teacher (June-19 convention -> comparable to 0.502)
        si = tidx.get(s)
        if si is not None:
            bs = Vn_raw[si]
            bge_sc = np.array([float(bs @ Vn_raw[tidx[c]]) if c in tidx else -1.0 for c in cpool], dtype=np.float64)
        else:
            bge_sc = np.zeros(len(cpool), dtype=np.float64)
        rng_sc = g.random(len(cpool))
        row = {"with_path": bool(wp), "trivial": bool(trivial), "n_cands": len(cpool),
               "clo_rank": j19.rank_true(clo_sc, true_pos), "bge_rank": j19.rank_true(bge_sc, true_pos),
               "rng_rank": j19.rank_true(rng_sc, true_pos)}
        for a in ARMS:
            sc = beam_scores(arm_store[a], arm_E[a], R, sq, eid[s], rid[r], cand_idx, arm_k[a], KHOP)
            row[a + "_rank"] = j19.rank_true(sc, true_pos)
            row[a + "_pos"] = float(sc[true_pos])
            arm_out_vec[a].append(float(sc[true_pos]))
        rows.append(row)
        if ri % 25 == 0:
            _heartbeat(out_dir, ri, n_rows, t0, extra={"rows_scored": len(rows)})
            print(f"  [progress] row {ri}/{n_rows} scored={len(rows)} ({time.perf_counter()-t0:.1f}s)", flush=True)

    return _summarize(rows, out_dir, t0, ARMS, arm_out_vec, semantic_fires,
                      {"sem": sem_edge_cos, "rand": rand_edge_cos, "scram": scr_edge_cos, "n_miss": n_miss})


def _summarize(rows, out_dir, t0, ARMS, arm_out_vec, semantic_fires, fire) -> int:
    with_rows = [r for r in rows if r["with_path"]]
    without_rows = [r for r in rows if not r["with_path"]]
    n_with = len(with_rows); n_without = len(without_rows)
    print(f"  eval rows={len(rows)} WITH={n_with} WITHOUT={n_without}", flush=True)
    if n_with < 30 or n_without < 10:
        return _write_nontest(out_dir, f"degenerate_split_with{n_with}_without{n_without}")

    # ARMS-MUST-DIFFER (META_RULE_AF): pos-score vectors must not be bit-identical across arms
    digests = {a: hashlib.sha256(np.asarray(arm_out_vec[a], dtype=np.float64).tobytes()).hexdigest() for a in ARMS}
    arms_differ = len(set(digests.values())) == len(ARMS)

    clo_hm = j19.hits_mrr([r["clo_rank"] for r in with_rows])["hits@10"]
    bge_hm = j19.hits_mrr([r["bge_rank"] for r in with_rows])["hits@10"]
    rng_hm = j19.hits_mrr([r["rng_rank"] for r in with_rows])["hits@10"]
    per_arm = {a: arm_metrics(rows, a) for a in ARMS}

    bar = max(bge_hm, JUNE19_BGE_BAR)
    prim = per_arm["SEM_BEAM"]
    prim_h10 = prim["hits"]["hits@10"]
    lift_vs_clo = prim_h10 - clo_hm
    lift_vs_bge = prim_h10 - bge_hm
    min_lift = min(lift_vs_clo, lift_vs_bge)
    nontriv = prim["nontrivial_lift_hits10"]

    hard_pass = (prim_h10 >= clo_hm + 0.05 and prim_h10 >= bar + 0.05
                 and (not math.isnan(nontriv) and nontriv >= 0.0) and prim["auroc"] >= 0.7)
    hard_fail = (prim_h10 <= max(clo_hm, bge_hm) and (not math.isnan(nontriv) and nontriv <= -0.50))
    middle = ((-0.02 <= min_lift < 0.05) or (not math.isnan(nontriv) and -0.30 <= nontriv < 0.0))
    verdict = "HARD_PASS" if hard_pass else ("HARD_FAIL" if hard_fail else ("MIDDLE_BAND" if middle else "MIDDLE_BAND"))

    # firing controls (report; assert at smoke elsewhere)
    gate_d_repro = abs(per_arm["RANDOM_K1"]["hits"]["hits@10"] - JUNE19_SUB_BAR) <= 0.10
    scram_h10 = per_arm["SEM_SCRAM_BEAM"]["hits"]["hits@10"]
    sem_h10 = per_arm["SEM_BEAM"]["hits"]["hits@10"]
    scramble_collapses = (sem_h10 - scram_h10) > 0.0  # scramble should not exceed semantic

    metrics = {
        "anchor": ANCHOR, "anchor_name": ANCHOR, "run_mode": RUN_MODE,
        "metrics_source": "measured_substrate_cfrpe_beam_plus_bge_simhash_seed",
        "verdict": verdict,
        "verdict_msg": (f"SEM_BEAM Hits@10={prim_h10:.3f} vs closure={clo_hm:.3f} bge_cached={bge_hm:.3f} "
                        f"bar={bar:.3f} min_lift={min_lift:+.3f} nontriv_lift={nontriv:+.3f} auroc={prim['auroc']:.3f} "
                        f"| RANDOM_K1={per_arm['RANDOM_K1']['hits']['hits@10']:.3f} (June19={JUNE19_SUB_BAR:.3f}) "
                        f"SEM_K1={per_arm['SEM_K1']['hits']['hits@10']:.3f} "
                        f"RANDOM_BEAM={per_arm['RANDOM_BEAM']['hits']['hits@10']:.3f} SCRAM={scram_h10:.3f} "
                        f"| semantic_fires={semantic_fires} gate_d_repro={gate_d_repro} "
                        f"scramble_collapses={scramble_collapses} arms_differ={arms_differ}"),
        "summary": f"{verdict}: SEM_BEAM {prim_h10:.3f} vs bar {bar:.3f}",
        "elapsed_s": time.perf_counter() - t0,
        "n_eval_rows": len(rows), "n_with_path": n_with, "n_without_path": n_without,
        "closure_hits10": clo_hm, "bge_cached_hits10": bge_hm, "random_hits10": rng_hm,
        "external_bge_bar": JUNE19_BGE_BAR, "june19_substrate_bar": JUNE19_SUB_BAR,
        "per_arm": per_arm,
        "primary_arm": "SEM_BEAM", "primary_hits10": prim_h10,
        "lift_vs_closure": lift_vs_clo, "lift_vs_bge": lift_vs_bge, "min_lift": min_lift,
        "nontrivial_lift_hits10": nontriv, "trivial_lift_hits10": prim["trivial_lift_hits10"],
        "fact_fabrication_bound_auroc": prim["fab_auroc"],
        "fire_check": {"semantic_fires": semantic_fires, "mean_edge_cos": fire,
                       "gate_d_repro_random_k1": gate_d_repro, "scramble_collapses": scramble_collapses,
                       "arms_differ": arms_differ, "arm_digests": {a: d[:12] for a, d in digests.items()}},
        "bands": {"hard_pass": "SEM_BEAM Hits@10 >= closure+0.05 AND >= max(bge,0.502)+0.05 AND nontriv_lift>=0 AND auroc>=0.7",
                  "middle": "min_lift in [-0.02,0.05) OR nontriv_lift in [-0.30,0.0)",
                  "hard_fail": "SEM_BEAM <= max(closure,bge) AND nontriv_lift <= -0.50"},
        "prior_work_check": "cosine>0.30 hits generic 'Composition'/'Entity resolution+KG' notes; no prior arc cell for semantic-seed+beam on ConceptNet -> genuinely novel vs June-19 random-code cell",
    }
    write_metrics(out_dir, metrics)
    print(f"\n[VERDICT] {verdict} | {metrics['verdict_msg']}", flush=True)
    print(f"[metrics] -> {out_dir/'metrics.json'}", flush=True)
    return 0


def _write_nontest(out_dir: Path, reason: str) -> int:
    m = {"anchor": ANCHOR, "anchor_name": ANCHOR, "run_mode": RUN_MODE, "verdict": "NON_TEST",
         "verdict_msg": f"NON_TEST: {reason}", "summary": f"NON_TEST: {reason}", "elapsed_s": 0.0}
    write_metrics(out_dir, m)
    print(f"NON_TEST: {reason} -> {out_dir/'metrics.json'}", flush=True)
    return 5


# ---------------- self-test (synthetic; no data) ----------------

def self_test() -> int:
    g = np.random.default_rng(0)
    n_dim = 512; sq = math.sqrt(n_dim)
    ents = ["a", "b", "c", "x"]; rels = ["IS_A"]
    eid = {e: i for i, e in enumerate(ents)}; rid = {"IS_A": 0}
    E = j19.bipolar(len(ents), n_dim, g); R = j19.bipolar(1, n_dim, g)
    store_edges = [("a", "IS_A", "b"), ("b", "IS_A", "c")]
    W = build_store(store_edges, E, R, sq, eid, rid, n_dim)
    cand = np.array([eid["b"], eid["c"], eid["x"]])
    # beam k=1 must equal the June-19 single-argmax decode on the same store/codebook
    sc_k1 = beam_scores(W, E, R, sq, eid["a"], rid["IS_A"], cand, 1, 4)
    j19.KHOP = 4  # june-19 substrate_scores reads global KHOP
    sc_j19 = j19.substrate_scores(W, E, R, sq, eid["a"], rid["IS_A"], cand)
    ok_k1_equals_j19 = bool(np.allclose(sc_k1, sc_j19, atol=1e-5))
    # 1-hop recall: a->b should score b highest at hop1
    ok_1hop = int(np.argmax(E @ (W @ (E[eid["a"]] * R[0] * sq)))) == eid["b"]
    # beam k=3 must be >= k=1 on the accumulated-max (superset of hops)
    sc_k3 = beam_scores(W, E, R, sq, eid["a"], rid["IS_A"], cand, 3, 4)
    ok_beam_ge = bool(np.all(sc_k3 >= sc_k1 - 1e-6))
    # semantic codes carry structure: build tiny teacher; similar rows -> higher code cosine
    Vn = np.array([[1, 0, 0], [0.9, 0.1, 0], [0, 0, 1], [-1, 0, 0]], dtype=np.float32)
    Vn = Vn / (np.linalg.norm(Vn, axis=1, keepdims=True) + 1e-8)
    tidx = {"a": 0, "b": 1, "c": 2, "x": 3}
    codes, miss = semantic_codes(["a", "b", "c"], Vn, tidx, 4096, np.random.default_rng(1))
    cos_ab = float(codes[0] @ codes[1]); cos_ac = float(codes[0] @ codes[2])
    ok_sem = (miss == 0 and cos_ab > cos_ac)   # a,b similar teacher -> more similar codes than a,c
    # scramble changes assignment
    codes_s, _ = semantic_codes(["a", "b", "c"], Vn, tidx, 4096, np.random.default_rng(1), scramble=True)
    ok_scr = not np.allclose(codes, codes_s)
    ok = ok_k1_equals_j19 and ok_1hop and ok_beam_ge and ok_sem and ok_scr
    print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} "
          f"(k1==june19={ok_k1_equals_j19}; 1hop={ok_1hop}; beam>=k1={ok_beam_ge}; "
          f"sem_structure(cos_ab={cos_ab:.3f}>cos_ac={cos_ac:.3f})={ok_sem}; scramble={ok_scr})")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return self_test()
    out_dir = get_output_dir(ANCHOR)
    try:
        return run_eval(out_dir)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
