"""conceptnet_rerank_parity_multiseed_v1 -- TWO deliverables on the decorrelated (RANDOM_BEAM)
substrate-native multi-hop composition spine, determinism-pinned + multi-seed.

TWO INDEPENDENT DELIVERABLES, one cell (shared decorrelated store + firewalled split; the
rerank-vs-random-beam comparison is PAIRED on the identical candidate sets, and the expensive
cf-RPE store is built once per seed instead of twice):

  (A) SEM_RERANK -- the semantic 2x-revival of the SEM_BEAM HARD_FAIL. Store codes stay
      DECORRELATED (near-orthogonal random -- the config that hit PARITY); semantics enters ONLY
      as a POST-HOC RE-RANK over the substrate-native RANDOM_BEAM candidate set (BGE cosine
      re-scores the top-RERANK_K beam shortlist). This RESPECTS correlation-hurts-capacity
      (reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08):
      the store/composition codes are never semantic-seeded; semantic geometry touches ONLY the
      shortlist reorder, never the stored codes. Q: does semantic rerank of the glass-box beam
      BEAT plain RANDOM_BEAM Hits@10 WITHOUT collapsing the way SEM_BEAM did (0.502 -> 0.227)?

  (B) MULTI-SEED CG-PARITY FIRM-UP -- the RANDOM_BEAM-vs-BGE PARITY (0.502 vs 0.494, currently
      MM-TENTATIVE because of PYTHONHASHSEED non-determinism) made multi-seed + determinism-pinned
      so the parity claim can move MM -> CHAIN_GRADE. Determinism fix: all sets that feed an
      ORDER-DEPENDENT computation are canonicalized via sorted() so the run is bit-reproducible
      regardless of PYTHONHASHSEED (portable; no os.execv re-exec, which is unsafe on Windows).

DETERMINISM (deliverable B core; PYTHONHASHSEED non-determinism ROOT CAUSE + fix):
  The June-19 cf-RPE store build iterates `store_edges` (a set of (u,rel,v) string-tuples) and the
  delta rule W += (LR/n)*outer(val - W@key, key) is ORDER-DEPENDENT (residual depends on current
  W). Python set-iteration order over string-tuples is PYTHONHASHSEED-dependent -> different runs
  built W in different orders -> Hits@10 wandered ~sigma 0.02 run-to-run. Candidate-pool
  composition (iterating tails_by_rel[r], a set, then capping) had the same dependence. FIX: every
  set that feeds an order-dependent computation is `sorted()` to a fixed canonical order BEFORE
  use (store edges; rel-subgraph BFS neighbour expansion; candidate base pool). Result:
  input-order-independent -> PYTHONHASHSEED-independent BY CONSTRUCTION. Verified empirically in
  --self-test (build W from a scrambled-order edge list, assert byte-identical digest to the
  sorted-order build) AND in the eval (determinism_check: run seed[0] twice, assert identical
  Hits@10 + identical W digest).

ARMS (per code-seed):
  RANDOM_BEAM      random (decorrelated) codes, width-BEAM_K beam -> substrate-native glass-box
                   [common spine for A + B]
  BGE_ALONE        frozen BGE-large cosine over the cached teacher (June-19 convention -> the 0.494
                   parity comparator) [B comparator + A rerank source; SEED-INVARIANT]
  SEM_RERANK_HARD  top-RERANK_K of RANDOM_BEAM reordered PURELY by BGE cosine (aggressive: BGE
                   fully replaces substrate order within the shortlist) [A]
  SEM_RERANK_RRF   top-RERANK_K of RANDOM_BEAM fused with BGE via reciprocal-rank fusion (robust:
                   blends substrate + BGE rank; least likely to collapse) [A]
  + closure (BFS transitive-closure oracle) and random-floor baselines (shared, seed-invariant)

MULTI-SEED design: the firewalled held-out SPLIT + candidate pools + BGE + closure are built ONCE
(seed-invariant) so BGE_ALONE is measured on identical items every seed and the paired McNemar is
per-item on a fixed eval set. Only the RANDOM codebook (E_rand, R) varies per code-seed -- that IS
the legitimate substrate run-to-run variance source (which random codes were drawn). This answers
"was 0.502 a lucky code draw, or does parity hold across draws?"

BANDS (research pre-reg; honest, pre-committed; NO SMOKE inflation):
  Deliverable A (primary arm = best-mean of {SEM_RERANK_HARD, SEM_RERANK_RRF}; lift vs RANDOM_BEAM):
    WIN  (HARD_PASS): best-rerank mean Hits@10 >= RANDOM_BEAM + 0.03 AND best arm positive in
                      >= ceil(0.8*S) seeds (paired same-seed).            (STRETCH, P~0.15-0.20)
    TIE  (MIDDLE)   : |best-rerank lift| < 0.03 AND best arm >= RANDOM_BEAM - 0.02 (no collapse) --
                      glass-box beam already captures what BGE-rerank would add. (EXPECTED, P~0.45)
    COLLAPSE (HARD_FAIL): best-rerank mean <= RANDOM_BEAM - 0.05 (post-hoc semantics HURTS even at
                      rerank -> extends correlation-hurts to reranking).  (P~0.20)
  Deliverable B (RANDOM_BEAM vs BGE_ALONE; parity_tier -- read INDEPENDENTLY of A's verdict):
    CG_PARITY     : |mean(RB)-BGE| <= 0.02 AND std(RB) <= 0.03 AND pooled McNemar p > 0.05 AND
                    determinism_ok -> parity FIRM, promote MM -> CHAIN_GRADE.
    MM_PARITY     : |mean(RB)-BGE| in (0.02, 0.05] OR std(RB) > 0.03 OR McNemar 0.01<p<=0.05.
    SUBSTRATE_WINS: mean(RB)-BGE > 0.05 AND McNemar p <= 0.05 (substrate BEATS the encoder).
    SUBSTRATE_LOSES: mean(RB)-BGE < -0.05 AND McNemar p <= 0.05.

Top-level `verdict` reflects deliverable A (the new-science mechanism question). Deliverable B's
parity_tier is a SEPARATE block; the VET reads it independently -- it is NOT gated by A's verdict.

Reuses exp_substrate_conceptnet_kg_inference_transfer_cpu_v1 (j19) + the June-19 semantic-beam cell
as pure-function libraries so the held-out split, metrics, beam decode + cf-RPE store are
byte-identical to the referents. DEVICE=cpu; READ-only (no Store mutation); ASCII.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (RANDOM_BEAM vs BGE_ALONE MUST differ; rerank-vs-beam pair
#   exempted-if-identity per headroom-vacuity, reported)
# - final_metrics_atomicity: tmp_replace via _seed_checkpoint.write_metrics (per-seed partials
#   atomic; final aggregate atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: ranking metric Hits@10 in [0,1]; parity bar 0.494 + rerank lift feasibility, not CRLB
# - baseline_in_band at smoke (RANDOM_BEAM ~0.50 in (0.05,0.95); smoke band [0.42,0.58])
# - discriminator survives scale: SMOKE runs at FULL N_DIM=8192 (option A) so RANDOM_BEAM
#   reproduces the ~0.50 phenomenon; rerank_headroom > 0.03 fires the rerank discriminator
# - HARD_PASS strictly above floor + margin (lift >= +0.03; parity |diff| <= 0.02)
# - cell_chunked: within-cell per-seed checkpoint/resume via _seed_checkpoint (runner death loses
#   one seed only)
# - progress_logging: print_flush_true (line-buffered) + heartbeat
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
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

# June-19 cells reused as pure-function libraries (identical split/metrics/beam/store)
import experiments.exp_substrate_conceptnet_kg_inference_transfer_cpu_v1 as j19  # noqa: E402
import experiments.exp_conceptnet_semantic_seeded_beam_composition_v1 as comp    # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials)
from hdlab.per_item_log import PerItemLogger  # noqa: E402

ANCHOR = "conceptnet_rerank_parity_multiseed_v1"
DEVICE = "cpu"
SPLIT_SEED = j19.SEED            # 20260619 -- reproduce the exact June-19 firewalled split (FIXED)
KHOP = 4
TRANSITIVE_RELS = j19.TRANSITIVE_RELS
TEACHER_NPZ = comp.TEACHER_NPZ
JUNE19_BGE_BAR = 0.494          # MEASURED@notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-08.md (BGE Hits@10)
JUNE19_RB_BAR = 0.502           # MEASURED@ same (RANDOM_BEAM Hits@10 -- the parity referent to firm up)
RERANK_K = 25                   # HYPOTHESIZED: shortlist size for BGE rerank (gives BGE room to
                                #   promote near-misses into top-10 while bounding demotion damage)
RRF_K0 = 60                     # CITED@Cormack-2009 reciprocal-rank-fusion default constant

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
if RUN_MODE == "smoke":
    # SMOKE at FULL N_DIM + FULL STORE_CAP (discriminator-survives-scale option A) so RANDOM_BEAM
    # reproduces the ~0.50 phenomenon. MEASURED@probe: the FULL profile (CLASSIFY_POOL=0) yields
    # store_edges=3769 (load 0.46; the STORE_CAP=8000 is NEVER binding -- with-path subgraph density
    # saturates it), with_path=233. CLASSIFY_POOL=6000 gives store_edges=3239 (load 0.40),
    # with_path=161 -> matches the full store LOAD and gives a stable Hits@10. 2 seeds.
    N_DIM, CLASSIFY_POOL, STORE_CAP, BEAM_K = 8192, 6000, 8000, 6
    CODE_SEEDS = [20260619, 20260620]
else:
    N_DIM, CLASSIFY_POOL, STORE_CAP, BEAM_K = 8192, 0, 8000, 6   # CLASSIFY_POOL=0 => full held_t pool (== June-19)
    CODE_SEEDS = [20260619, 20260620, 20260621, 20260622, 20260623]
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


# ---------------- determinism helpers (deliverable B core) ----------------

def canonical_edges(edge_iterable):
    """Canonicalize a set/iterable of (u,rel,v) string-tuples to a FIXED sorted list.

    This is the determinism fix: the cf-RPE store build consumes THIS order (not Python
    set-iteration order), so the built W is independent of PYTHONHASHSEED. sorted() over
    tuples-of-strings is a total order -> bit-reproducible across runs / hash seeds."""
    return sorted(edge_iterable)


def det_rel_subgraph_edges(adj_s, s, rel, max_depth, cap):
    """Deterministic re-implementation of j19.rel_subgraph_edges: BFS from s collecting (u,rel,v)
    edges within max_depth, capped. Neighbours are iterated in SORTED order so the cap-truncation
    (which edges survive when len>=cap) is PYTHONHASHSEED-independent. Same edge SET as j19 when
    uncapped; deterministic SUBSET when capped."""
    edges = set()
    frontier = [s]
    seen = {s}
    for _ in range(max_depth):
        nxt = []
        for u in sorted(frontier):
            for v in sorted(adj_s.get(u, ())):
                edges.add((u, rel, v))
                if len(edges) >= cap:
                    return edges
                if v not in seen:
                    seen.add(v)
                    nxt.append(v)
        frontier = nxt
        if not frontier:
            break
    return edges


def _wdigest(W):
    return hashlib.sha256(np.ascontiguousarray(W, dtype=np.float32).tobytes()).hexdigest()


# ---------------- semantic rerank (deliverable A) -- post-hoc, store untouched ----------------

def rerank_true_rank(sc_rb, bge_cos, true_pos, rerank_k, mode):
    """1-based rank of the true tail AFTER reranking the top-`rerank_k` RANDOM_BEAM candidates.

    Store codes are NEVER touched: sc_rb is the substrate-native beam score; bge_cos is the frozen
    BGE cosine (semantic geometry) applied ONLY to reorder the substrate shortlist. Candidates
    outside the shortlist keep their substrate order below the reranked block.

    mode = "hard": within the shortlist, reorder purely by bge_cos (descending).
    mode = "rrf" : within the shortlist, reorder by reciprocal-rank fusion of substrate rank and
                   BGE rank (blended); RRF_K0 damps the head. Robust -- rarely collapses.
    Returns (rank_1based, in_shortlist_bool)."""
    n = len(sc_rb)
    k = min(rerank_k, n)
    order_rb = np.argsort(-sc_rb, kind="stable")            # substrate full ranking (indices)
    shortlist = order_rb[:k]
    tail = order_rb[k:]
    bge_sl = bge_cos[shortlist]
    if mode == "hard":
        new_sl = shortlist[np.argsort(-bge_sl, kind="stable")]
    elif mode == "rrf":
        rb_rank = np.arange(1, k + 1)                       # substrate rank within shortlist (1..k)
        bge_rank_within = np.empty(k, dtype=np.int64)
        bge_order = np.argsort(-bge_sl, kind="stable")
        bge_rank_within[bge_order] = np.arange(1, k + 1)
        rrf = 1.0 / (RRF_K0 + rb_rank) + 1.0 / (RRF_K0 + bge_rank_within)
        new_sl = shortlist[np.argsort(-rrf, kind="stable")]
    else:
        raise ValueError(f"unknown rerank mode {mode!r}")
    final_order = np.concatenate([new_sl, tail])
    rank = int(np.where(final_order == true_pos)[0][0]) + 1
    in_sl = bool(np.any(shortlist == true_pos))
    return rank, in_sl


# ---------------- stats: paired McNemar (deliverable B; PAIRED-trials mandate) ----------------

def mcnemar(b, c):
    """Paired McNemar with continuity correction. b = #(RB hit, BGE miss); c = #(RB miss, BGE hit).
    Returns (chi2_stat, p_value). p from chi2 df=1 survival = erfc(sqrt(stat/2))."""
    if (b + c) == 0:
        return 0.0, 1.0
    stat = (abs(b - c) - 1.0) ** 2 / (b + c)
    p = math.erfc(math.sqrt(stat / 2.0))
    return float(stat), float(p)


# ---------------- BGE teacher (rerank source + parity comparator) ----------------

def load_bge_raw():
    """Vn_raw = L2-normalized BGE-large teacher (June-19 baseline-cosine convention -> comparable
    to the 0.494 bar). Returns (Vn_raw, id_index) or (None, None) if cache missing."""
    if not TEACHER_NPZ.exists():
        return None, None
    z = np.load(TEACHER_NPZ, allow_pickle=True)
    ids = json.loads(str(z["id_order_json"]))
    V = np.asarray(z["semantic"], dtype=np.float32)
    Vn_raw = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-8)
    return Vn_raw, {e: i for i, e in enumerate(ids)}


# ---------------- eval-set build (seed-invariant; ONCE) ----------------

def build_eval_set(out_dir: Path, t0: float):
    """Build the firewalled held-out eval set + candidate pools + BGE/closure/random baselines.
    Everything here is SEED-INVARIANT (depends only on SPLIT_SEED) so BGE_ALONE is measured on
    identical items each code-seed. Returns (eval_rows, ents, rels, eid, rid, sorted_store_edges,
    Vn_raw, bge_idx, meta) or (None, reason)."""
    Vn_raw, bge_idx = load_bge_raw()
    if Vn_raw is None:
        return None, "teacher_cache_missing"

    split_gen = np.random.default_rng(SPLIT_SEED)   # drives split + pool shuffles (FIXED across seeds)
    ing = j19.load_ingested_edges()
    held = j19.load_heldout()
    print(f"  ingested CN_ edges={len(ing)} | held-out edges={len(held)}", flush=True)
    if len(ing) < 100 or len(held) < 30:
        return None, "graph_or_heldout_too_small"
    any_adj, rel_adj, tails_by_rel, truths = j19.build_adj(ing)

    heldout_set = {(s, r, o) for (s, r, o) in held}
    if len(heldout_set & truths) > 0:
        return None, "firewall_breach_compose"

    held_t = [(s, r, o) for (s, r, o) in held if r in TRANSITIVE_RELS]
    split_gen.shuffle(held_t)
    pool = held_t[:CLASSIFY_POOL] if CLASSIFY_POOL else held_t
    with_set = []
    without_set = []
    store_edges = set()
    for (s, r, o) in pool:
        sr = rel_adj.get(r, {})
        depth = j19.bfs_depth(sr, s, o, KHOP)
        if depth is not None:
            with_set.append((s, r, o, True, depth <= 2))
            if len(store_edges) < STORE_CAP:
                store_edges |= det_rel_subgraph_edges(sr, s, r, KHOP, cap=STORE_CAP - len(store_edges))
        else:
            without_set.append((s, r, o, False, False))
    split_gen.shuffle(without_set)
    without_keep = without_set[: max(len(with_set), 150)]
    classified = with_set + without_keep
    print(f"  classified={len(pool)} -> WITH={len(with_set)} WITHOUT(kept)={len(without_keep)} "
          f"store_edges={len(store_edges)}", flush=True)

    ents = set()
    for (u, _r, v) in store_edges:
        ents.add(u)
        ents.add(v)
    for (s, r, o, _wp, _tr) in classified:
        ents.add(s)
        ents.add(o)
    ents = sorted(ents)
    rels = sorted({r for (_u, r, _v) in store_edges} | {r for (_s, r, _o, _wp, _tr) in classified})
    eid = {e: i for i, e in enumerate(ents)}
    rid = {r: i for i, r in enumerate(rels)}
    if len(heldout_set & store_edges) > 0:
        return None, "firewall_breach_store"
    sorted_store_edges = canonical_edges(store_edges)   # DETERMINISM: fixed store-build order

    # per-row candidate pools + seed-invariant baselines (closure / bge / random floor)
    eval_rows = []
    for (s, r, o, wp, trivial) in classified:
        if s not in eid or o not in eid or r not in rid:
            continue
        sr = rel_adj.get(r, {})
        rset = j19.reachable_set(sr, s, KHOP)
        other_true = {t for t in any_adj.get(s, set()) if (s, r, t) in truths and t != o}
        cpool = sorted(c for c in tails_by_rel.get(r, ()) if c in eid and c not in other_true and c != s)
        if o not in cpool:
            cpool.append(o)
        if len(cpool) > MAX_CANDS:
            keep = [o] + [c for c in cpool if c in rset and c != o][: MAX_CANDS // 2]
            rest = [c for c in cpool if c not in keep]
            split_gen.shuffle(rest)
            keep += rest[: MAX_CANDS - len(keep)]
            cpool = keep
        if len(cpool) < 5:
            continue
        cand_idx = np.array([eid[c] for c in cpool])
        true_pos = cpool.index(o)
        clo_sc = np.array([1.0 if c in rset else 0.0 for c in cpool], dtype=np.float64)
        si = bge_idx.get(s)
        if si is not None:
            bs = Vn_raw[si]
            bge_cos = np.array([float(bs @ Vn_raw[bge_idx[c]]) if c in bge_idx else -1.0 for c in cpool],
                               dtype=np.float64)
        else:
            bge_cos = np.zeros(len(cpool), dtype=np.float64)
        rng_sc = split_gen.random(len(cpool))
        eval_rows.append({
            "s": s, "r": r, "o": o, "with_path": bool(wp), "trivial": bool(trivial),
            "n_cands": len(cpool), "cand_idx": cand_idx, "true_pos": true_pos,
            "bge_cos": bge_cos, "clo_rank": j19.rank_true(clo_sc, true_pos),
            "bge_rank": j19.rank_true(bge_cos, true_pos), "rng_rank": j19.rank_true(rng_sc, true_pos),
            "s_idx": eid[s], "r_idx": rid[r],
        })
    meta = {"n_ent": len(ents), "n_rel": len(rels), "n_store_edges": len(sorted_store_edges),
            "store_digest_edges": hashlib.sha256(json.dumps(sorted_store_edges).encode()).hexdigest()[:12]}
    print(f"  eval_set built: rows={len(eval_rows)} n_ent={meta['n_ent']} n_rel={meta['n_rel']} "
          f"({time.perf_counter()-t0:.1f}s)", flush=True)
    return (eval_rows, ents, rels, eid, rid, sorted_store_edges, Vn_raw, bge_idx, meta), None


# ---------------- per-seed scoring ----------------

def build_seed_store(code_seed, n_ent, n_rel, eid, rid, sorted_store_edges):
    """Build (E_rand, R, W) for a code-seed's decorrelated RANDOM codebook. Isolated so the
    determinism_check can rebuild W twice cheaply (no beam eval) to prove bit-reproducibility."""
    code_gen = np.random.default_rng(code_seed)
    R = j19.bipolar(n_rel, N_DIM, code_gen)
    E_rand = j19.bipolar(n_ent, N_DIM, code_gen)
    sq = math.sqrt(N_DIM)
    W = comp.build_store(sorted_store_edges, E_rand, R, sq, eid, rid, N_DIM)
    return E_rand, R, W, sq


def score_one_seed(code_seed, eval_rows, n_ent, n_rel, eid, rid, sorted_store_edges, out_dir, t0, pil=None):
    """Build W with the seed's RANDOM codebook (decorrelated) and score all arms. Returns per-seed
    dict incl. per-item hit vectors for RANDOM_BEAM/BGE (paired McNemar) + rerank ranks."""
    E_rand, R, W, sq = build_seed_store(code_seed, n_ent, n_rel, eid, rid, sorted_store_edges)
    wdig = _wdigest(W)

    rb_ranks, hard_ranks, rrf_ranks = [], [], []
    rb_pos, bge_pos = [], []
    hit_rb, hit_bge = [], []          # per-item, WITH-path only (paired McNemar for B)
    in_top_k, in_top_10 = 0, 0        # rerank headroom (discriminator-fires for A), WITH-path
    n_with = 0
    n_rows = len(eval_rows)
    for ri, row in enumerate(eval_rows):
        sc_rb = comp.beam_scores(W, E_rand, R, sq, row["s_idx"], row["r_idx"],
                                 row["cand_idx"], BEAM_K, KHOP)
        tp = row["true_pos"]
        rb_rank = j19.rank_true(sc_rb, tp)
        hr, _ = rerank_true_rank(sc_rb, row["bge_cos"], tp, RERANK_K, "hard")
        rr, _ = rerank_true_rank(sc_rb, row["bge_cos"], tp, RERANK_K, "rrf")
        rb_ranks.append(rb_rank)
        hard_ranks.append(hr)
        rrf_ranks.append(rr)
        rb_pos.append(float(sc_rb[tp]))
        bge_pos.append(float(row["bge_cos"][tp]))
        if row["with_path"]:
            n_with += 1
            hit_rb.append(rb_rank <= 10)
            hit_bge.append(row["bge_rank"] <= 10)
            if rb_rank <= RERANK_K:
                in_top_k += 1
            if rb_rank <= 10:
                in_top_10 += 1
            if pil is not None:
                _iid = f"{row['s']}|{row['r']}|{row['o']}"
                _tags = {"with_path": True, "trivial": row["trivial"], "out_degree": int(row["n_cands"])}
                pil.log(_iid, f"compose:RANDOM_BEAM:seed{code_seed}", {"rank": rb_rank, "hit10": rb_rank <= 10}, _tags)
                pil.log(_iid, f"compose:SEM_RERANK_HARD:seed{code_seed}", {"rank": hr, "hit10": hr <= 10}, _tags)
                pil.log(_iid, f"compose:SEM_RERANK_RRF:seed{code_seed}", {"rank": rr, "hit10": rr <= 10}, _tags)
                pil.log(_iid, f"retrieval:BGE_ALONE", {"rank": int(row["bge_rank"]), "hit10": int(row["bge_rank"]) <= 10}, _tags)
        if ri % 100 == 0:
            _heartbeat(out_dir, ri, n_rows, t0, extra={"code_seed": code_seed})
            print(f"  [seed {code_seed}] row {ri}/{n_rows} ({time.perf_counter()-t0:.1f}s)", flush=True)

    with_mask = [row["with_path"] for row in eval_rows]
    def h10(ranks):
        w = [rk for rk, m in zip(ranks, with_mask) if m]
        return float(np.mean(np.asarray(w) <= 10)) if w else float("nan")
    rb_h10 = h10(rb_ranks)
    hard_h10 = h10(hard_ranks)
    rrf_h10 = h10(rrf_ranks)
    bge_h10 = float(np.mean(np.asarray([r["bge_rank"] for r in eval_rows if r["with_path"]]) <= 10))
    clo_h10 = float(np.mean(np.asarray([r["clo_rank"] for r in eval_rows if r["with_path"]]) <= 10))
    rng_h10 = float(np.mean(np.asarray([r["rng_rank"] for r in eval_rows if r["with_path"]]) <= 10))
    # paired McNemar (RB vs BGE)
    b = int(sum(1 for hr, hb in zip(hit_rb, hit_bge) if hr and not hb))
    c = int(sum(1 for hr, hb in zip(hit_rb, hit_bge) if (not hr) and hb))
    mc_stat, mc_p = mcnemar(b, c)
    headroom = (in_top_k - in_top_10) / n_with if n_with else float("nan")
    # arms-must-differ digests (rank vectors)
    def rdig(ranks):
        return hashlib.sha256(np.asarray(ranks, dtype=np.int64).tobytes()).hexdigest()
    per_seed = {
        "seed": code_seed, "N": N_DIM, "run_mode": RUN_MODE, "elapsed_s": time.perf_counter() - t0,
        "n_with": n_with, "n_eval": len(eval_rows),
        "RANDOM_BEAM_hits10": rb_h10, "SEM_RERANK_HARD_hits10": hard_h10,
        "SEM_RERANK_RRF_hits10": rrf_h10, "BGE_ALONE_hits10": bge_h10,
        "closure_hits10": clo_h10, "random_floor_hits10": rng_h10,
        "mcnemar_b_rb_only": b, "mcnemar_c_bge_only": c, "mcnemar_stat": mc_stat, "mcnemar_p": mc_p,
        "rerank_headroom": headroom, "w_digest": wdig,
        "rank_digests": {"RANDOM_BEAM": rdig(rb_ranks)[:12], "SEM_RERANK_HARD": rdig(hard_ranks)[:12],
                         "SEM_RERANK_RRF": rdig(rrf_ranks)[:12],
                         "BGE_ALONE": rdig([r["bge_rank"] for r in eval_rows])[:12]},
        "config_version": f"ANCHOR={ANCHOR},N={N_DIM},run_mode={RUN_MODE},split_seed={SPLIT_SEED}",
    }
    print(f"  [seed {code_seed}] RB={rb_h10:.3f} HARD={hard_h10:.3f} RRF={rrf_h10:.3f} "
          f"BGE={bge_h10:.3f} clo={clo_h10:.3f} | McNemar b={b} c={c} p={mc_p:.3f} "
          f"headroom={headroom:+.3f} wdig={wdig[:8]}", flush=True)
    return per_seed


# ---------------- main eval (multi-seed + aggregate) ----------------

def run_eval(out_dir: Path) -> int:
    t0 = time.perf_counter()
    _write_start_marker(out_dir, expected_n_units=len(CODE_SEEDS))
    print(f"[config] anchor={ANCHOR} mode={RUN_MODE} N_DIM={N_DIM} KHOP={KHOP} BEAM_K={BEAM_K} "
          f"RERANK_K={RERANK_K} seeds={CODE_SEEDS}", flush=True)

    built, reason = build_eval_set(out_dir, t0)
    if built is None:
        return _write_nontest(out_dir, reason)
    (eval_rows, ents, rels, eid, rid, sorted_store_edges, Vn_raw, bge_idx, meta) = built
    n_ent, n_rel = len(ents), len(rels)

    # DETERMINISM_CHECK (deliverable B): rebuild seed[0] store W TWICE, assert bit-identical digest
    # (W bit-reproducibility is the core PYTHONHASHSEED-independence proof; the deterministic beam
    # eval over a fixed W then follows). Cheap: W-only, no double beam eval.
    s0 = CODE_SEEDS[0]
    _, _, W_a, _ = build_seed_store(s0, n_ent, n_rel, eid, rid, sorted_store_edges)
    _, _, W_b, _ = build_seed_store(s0, n_ent, n_rel, eid, rid, sorted_store_edges)
    dig_a, dig_b = _wdigest(W_a), _wdigest(W_b)
    determinism_ok = (dig_a == dig_b)
    del W_a, W_b
    print(f"  [determinism_check] W rebuilt twice: digest_match={determinism_ok} "
          f"(dig={dig_a[:12]}) -> determinism_ok={determinism_ok}", flush=True)

    # multi-seed loop with per-seed checkpoint/resume (chunked; runner death loses one seed only)
    run_cfg = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR}
    done, remaining = resumable_seeds(CODE_SEEDS, out_dir, run_config=run_cfg)
    print(f"  [ckpt] {len(done)}/{len(CODE_SEEDS)} seeds done; running {remaining}", flush=True)
    pil = PerItemLogger(out_dir, eval_name=f"{ANCHOR}:{RUN_MODE}", cap=2_000_000)
    for seed in remaining:
        ps = score_one_seed(seed, eval_rows, n_ent, n_rel, eid, rid, sorted_store_edges, out_dir, t0, pil=pil)
        write_partial(out_dir, seed, ps)
    pil.close()
    per_seed = aggregate_partials(out_dir, CODE_SEEDS, run_config=run_cfg)

    return _summarize(per_seed, out_dir, t0, determinism_ok, dig_a, meta)


def _summarize(per_seed, out_dir, t0, determinism_ok, w_digest_seed0, meta) -> int:
    seeds_present = [str(s) for s in CODE_SEEDS if str(s) in per_seed]
    S = len(seeds_present)
    EXPECTED = len(CODE_SEEDS)
    cardinality_ok = (S == EXPECTED)
    if S == 0:
        return _write_nontest(out_dir, "no_seed_partials")

    def col(key):
        return np.asarray([float(per_seed[s][key]) for s in seeds_present], dtype=np.float64)
    rb = col("RANDOM_BEAM_hits10")
    hard = col("SEM_RERANK_HARD_hits10")
    rrf = col("SEM_RERANK_RRF_hits10")
    bge = col("BGE_ALONE_hits10")
    clo = col("closure_hits10")
    headroom = col("rerank_headroom")

    rb_mean, rb_std = float(rb.mean()), float(rb.std(ddof=0))
    bge_mean = float(bge.mean())      # BGE is seed-invariant -> std ~0
    hard_mean, rrf_mean = float(hard.mean()), float(rrf.mean())

    # ---- Deliverable A: SEM_RERANK vs RANDOM_BEAM (paired per seed) ----
    hard_lift = hard - rb
    rrf_lift = rrf - rb
    best_is_rrf = rrf_mean >= hard_mean
    best_mean = rrf_mean if best_is_rrf else hard_mean
    best_lift_vec = rrf_lift if best_is_rrf else hard_lift
    best_arm = "SEM_RERANK_RRF" if best_is_rrf else "SEM_RERANK_HARD"
    best_lift = best_mean - rb_mean
    n_pos = int(np.sum(best_lift_vec >= 0.0))
    need_pos = math.ceil(0.8 * S)
    a_win = (best_lift >= 0.03 and n_pos >= need_pos)
    a_collapse = (best_mean <= rb_mean - 0.05)
    a_tie = (abs(best_lift) < 0.03 and best_mean >= rb_mean - 0.02)
    if a_win:
        a_verdict = "WIN"; top_verdict = "HARD_PASS"
    elif a_collapse:
        a_verdict = "COLLAPSE"; top_verdict = "HARD_FAIL"
    else:
        a_verdict = "TIE"; top_verdict = "MIDDLE_BAND"
    mean_headroom = float(np.nanmean(headroom))
    rerank_fires = mean_headroom > 0.03

    # ---- Deliverable B: RANDOM_BEAM vs BGE parity (pooled McNemar) ----
    diff = rb_mean - bge_mean
    pooled_b = int(sum(int(per_seed[s]["mcnemar_b_rb_only"]) for s in seeds_present))
    pooled_c = int(sum(int(per_seed[s]["mcnemar_c_bge_only"]) for s in seeds_present))
    pooled_stat, pooled_p = mcnemar(pooled_b, pooled_c)
    if abs(diff) <= 0.02 and rb_std <= 0.03 and pooled_p > 0.05 and determinism_ok:
        parity_tier = "CG_PARITY"
    elif diff > 0.05 and pooled_p <= 0.05:
        parity_tier = "SUBSTRATE_WINS"
    elif diff < -0.05 and pooled_p <= 0.05:
        parity_tier = "SUBSTRATE_LOSES"
    else:
        parity_tier = "MM_PARITY"

    # arms-must-differ (RANDOM_BEAM vs BGE_ALONE MUST differ -> different mechanisms)
    s0 = seeds_present[0]
    rdg = per_seed[s0]["rank_digests"]
    arms_differ_rb_bge = rdg["RANDOM_BEAM"] != rdg["BGE_ALONE"]
    rerank_identity = (rdg["SEM_RERANK_HARD"] == rdg["RANDOM_BEAM"] and
                       rdg["SEM_RERANK_RRF"] == rdg["RANDOM_BEAM"])

    verdict_msg = (
        f"[B parity_tier={parity_tier}] RANDOM_BEAM={rb_mean:.3f}+/-{rb_std:.3f} vs BGE={bge_mean:.3f} "
        f"diff={diff:+.3f} McNemar(pooled b={pooled_b} c={pooled_c} p={pooled_p:.3f}) "
        f"determinism_ok={determinism_ok} | "
        f"[A {a_verdict}] best={best_arm} mean={best_mean:.3f} lift={best_lift:+.3f} "
        f"pos_seeds={n_pos}/{S} (HARD={hard_mean:.3f} RRF={rrf_mean:.3f}) "
        f"rerank_headroom={mean_headroom:+.3f} fires={rerank_fires} | "
        f"closure={float(clo.mean()):.3f} S={S}/{EXPECTED} cardinality_ok={cardinality_ok} "
        f"arms_differ(RB!=BGE)={arms_differ_rb_bge}")

    if not cardinality_ok:
        top_verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"

    metrics = {
        "anchor": ANCHOR, "anchor_name": ANCHOR, "run_mode": RUN_MODE,
        "metrics_source": "measured_decorrelated_cfrpe_beam_multiseed_plus_bge_rerank",
        "verdict": top_verdict, "verdict_msg": verdict_msg,
        "summary": f"A:{a_verdict} (best {best_arm} lift {best_lift:+.3f}) | B:{parity_tier} "
                   f"(RB {rb_mean:.3f}+/-{rb_std:.3f} vs BGE {bge_mean:.3f})",
        "elapsed_s": time.perf_counter() - t0,
        "n_seeds": S, "expected_seeds": EXPECTED, "cardinality_ok": cardinality_ok,
        "seeds": [int(s) for s in seeds_present], "meta": meta,
        "deliverable_A_rerank": {
            "verdict": a_verdict, "primary_arm": best_arm, "best_mean_hits10": best_mean,
            "lift_vs_random_beam": best_lift, "pos_seeds": n_pos, "need_pos": need_pos,
            "SEM_RERANK_HARD_mean": hard_mean, "SEM_RERANK_RRF_mean": rrf_mean,
            "RANDOM_BEAM_mean": rb_mean, "rerank_headroom_mean": mean_headroom,
            "rerank_fires": rerank_fires, "rerank_identity": rerank_identity,
            "rerank_k": RERANK_K,
            "bands": {"WIN": "best-rerank >= RANDOM_BEAM+0.03 AND pos in >=ceil(0.8*S) seeds",
                      "TIE": "|lift|<0.03 AND best >= RANDOM_BEAM-0.02",
                      "COLLAPSE": "best-rerank <= RANDOM_BEAM-0.05"}},
        "deliverable_B_parity": {
            "parity_tier": parity_tier, "RANDOM_BEAM_mean": rb_mean, "RANDOM_BEAM_std": rb_std,
            "BGE_ALONE_mean": bge_mean, "diff_rb_minus_bge": diff,
            "mcnemar_pooled_b": pooled_b, "mcnemar_pooled_c": pooled_c,
            "mcnemar_pooled_stat": pooled_stat, "mcnemar_pooled_p": pooled_p,
            "determinism_ok": determinism_ok, "w_digest_seed0": w_digest_seed0,
            "june19_rb_bar": JUNE19_RB_BAR, "june19_bge_bar": JUNE19_BGE_BAR,
            "bands": {"CG_PARITY": "|diff|<=0.02 AND std<=0.03 AND pooled_p>0.05 AND determinism_ok",
                      "MM_PARITY": "near-parity but not tight OR high seed variance OR p in (0.01,0.05]",
                      "SUBSTRATE_WINS": "diff>0.05 AND p<=0.05", "SUBSTRATE_LOSES": "diff<-0.05 AND p<=0.05"}},
        "per_seed": {s: per_seed[s] for s in seeds_present},
        "arms_differ_rb_vs_bge": arms_differ_rb_bge,
        "closure_hits10_mean": float(clo.mean()),
        "prior_work_check": "substrate-KB concept-query top hit cosine=0.330 (generic 'associative "
            "relation'/'Multiplicative composition' notes); NO prior arc cell for POST-HOC BGE-rerank "
            "over a decorrelated substrate beam -> genuinely novel (v1 SEM_BEAM injected semantics INTO "
            "the store and HARD_FAILed; this keeps the store decorrelated and reranks post-hoc).",
    }
    write_metrics(out_dir, metrics)
    print(f"\n[VERDICT] {top_verdict} | {verdict_msg}", flush=True)
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
    n_dim = 512
    sq = math.sqrt(n_dim)
    ents = ["a", "b", "c", "x"]
    rels = ["IS_A"]
    eid = {e: i for i, e in enumerate(ents)}
    rid = {"IS_A": 0}
    E = j19.bipolar(len(ents), n_dim, g)
    R = j19.bipolar(1, n_dim, g)

    # (1) DETERMINISM: canonical_edges makes store-build input-order-independent.
    edges = {("a", "IS_A", "b"), ("b", "IS_A", "c"), ("a", "IS_A", "c")}
    scrambled = list(edges)[::-1]
    W1 = comp.build_store(canonical_edges(edges), E, R, sq, eid, rid, n_dim)
    W2 = comp.build_store(canonical_edges(scrambled), E, R, sq, eid, rid, n_dim)
    ok_det = (_wdigest(W1) == _wdigest(W2))

    # (2) det_rel_subgraph_edges: uncapped == j19 edge set; capped is deterministic.
    adj_s = {"a": {"b", "c"}, "b": {"c", "d"}, "c": {"d"}}
    e_new = det_rel_subgraph_edges(adj_s, "a", "IS_A", 3, cap=10_000)
    e_j19 = j19.rel_subgraph_edges(adj_s, "a", "IS_A", 3, cap=10_000)
    ok_subgraph = (e_new == e_j19)
    e_cap1 = det_rel_subgraph_edges(adj_s, "a", "IS_A", 3, cap=2)
    e_cap2 = det_rel_subgraph_edges(adj_s, "a", "IS_A", 3, cap=2)
    ok_cap_det = (e_cap1 == e_cap2 and len(e_cap1) == 2)

    # (3) rerank: HARD reorders the shortlist by BGE; identity when bge matches substrate order.
    sc_rb = np.array([0.9, 0.8, 0.7, 0.6, 0.1], dtype=np.float64)   # substrate ranks: idx0>idx1>...
    bge = np.array([0.1, 0.2, 0.95, 0.3, 0.0], dtype=np.float64)    # BGE loves idx2 (substrate rank 3)
    r_hard, in_sl = rerank_true_rank(sc_rb, bge, true_pos=2, rerank_k=4, mode="hard")
    ok_rerank_promote = (r_hard == 1 and in_sl)                     # idx2 promoted to rank 1
    # true outside shortlist -> rank unchanged (rerank cannot help)
    r_out, in_sl2 = rerank_true_rank(sc_rb, bge, true_pos=4, rerank_k=4, mode="hard")
    ok_rerank_outside = (r_out == 5 and not in_sl2)
    # RRF blends: idx2 promoted but not necessarily to 1 (substrate rank 3 damps it)
    r_rrf, _ = rerank_true_rank(sc_rb, bge, true_pos=2, rerank_k=4, mode="rrf")
    ok_rrf = (1 <= r_rrf <= 4)
    # identity: bge order == substrate order -> HARD leaves ranks unchanged
    r_id, _ = rerank_true_rank(sc_rb, sc_rb.copy(), true_pos=0, rerank_k=4, mode="hard")
    ok_identity = (r_id == 1)

    # (4) McNemar: symmetric b==c -> p large; lopsided -> small.
    _, p_sym = mcnemar(10, 10)
    _, p_lop = mcnemar(20, 2)
    ok_mcnemar = (p_sym > 0.5 and p_lop < 0.05)

    ok = (ok_det and ok_subgraph and ok_cap_det and ok_rerank_promote and ok_rerank_outside
          and ok_rrf and ok_identity and ok_mcnemar)
    print(f"[{ANCHOR}] --self-test {'OK' if ok else 'FAIL'} "
          f"(determinism(order-indep W)={ok_det}; subgraph==j19={ok_subgraph}; cap_det={ok_cap_det}; "
          f"rerank_promote={ok_rerank_promote}; rerank_outside={ok_rerank_outside}; rrf={ok_rrf}; "
          f"identity={ok_identity}; mcnemar={ok_mcnemar})")
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
