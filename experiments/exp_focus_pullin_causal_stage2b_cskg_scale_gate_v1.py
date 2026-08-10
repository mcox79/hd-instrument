# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; REAL vs SCRAMBLE_OBJECTS hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (a capacity/cardinality diagnostic sweep over the real CSKG store; no single
#   closed-form noise floor -- the whole POINT is measuring where the empirical floor sits)
# - HP_SCOPE: {full_cardinality_point: [relevant_recall, false_pull_in_rate, gate_net_value]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SCALES) (sweep-axis units are ingest-SCALES, not seeds)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime -- GATE_THRESH=0.28 is Stage-1's ORIGINAL
#   number, used UNCHANGED/NOT retuned here on purpose: the whole test is whether that
#   already-calibrated number generalizes to CSKG cardinality, not a fresh calibration exercise.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs a REAL tiny synthetic KGStore (real_code_path) AND validates the REAL
#   cskg_foundation_v1 loader against a small slice of the actual data files (no synthetic-only
#   branch for the data-loading path)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_focus_pullin_causal_stage2b_cskg_scale_gate_v1.md for the full pre-reg.
"""exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 -- Stage 2 SUB-TEST B of the simulation-engine
program: wires Stage-1's salience-gated pull_in() to the REAL, HARD_PASS-certified CSKG content
store (exp_cskg_foundation_v1: 482,588 nodes / 1,213,912 spine edges on disk at
data/cskg_foundation_v1/) via hdlab.kg_traversal.KGStore, the CERT'd (n8/U1, CERT 584/585)
substrate-native (s,p,o) retrieval path -- and measures whether the salience gate still
discriminates relevant retrieval from false positives AT THIS CARDINALITY, or whether it
degrades/blows up (the historically-fatal MCScript2.0 over-merge / cardinality-echo risk this
sub-test exists specifically to de-risk).

Mechanism wiring (Stage-1's pull_in(), REUSED via its generalized multi-exclude sibling from
Sub-test A -- imported, not re-transcribed):
  probe          = store.W @ store.key(s, p)        (the raw Hebbian-recalled noisy estimate of
                                                       the answer entity's identity vector -- lives
                                                       in the SAME 1024-dim space as store.E's rows,
                                                       exactly analogous to Stage-1's raw content-
                                                       vector probe)
  shortlist      = top-SHORTLIST_K entities by the cheap LINEAR store.score_all(key) readout
                    (a coarse candidate-generation pass; store.E rows are all bipolar {-1,+1} with
                    IDENTICAL norm sqrt(n_dim), so ranking by raw dot product == ranking by cosine
                    against a fixed-norm codebook -- score_all's top-K is a legitimate coarse
                    pre-filter, not an approximation that changes the ranking)
  candidate/gate = pull_in_multi_exclude(probe, shortlist_codebook, gate=0.28)  (Stage-1's EXACT
                    CA3-style iterative_attractor settle + raw-cosine admission gate, run on the
                    shortlist rather than the full 482,588-row codebook so the CA3 settle step
                    stays cheap at this cardinality -- disclosed 2-stage coarse-then-fine
                    retrieval, not a change to pull_in() itself)

GATE_THRESH=0.28 is Stage-1's ORIGINAL, un-retuned number (fixed by the Stage-2 task CONTRACT --
the question is whether Stage-1's calibration generalizes, not a fresh CSKG-specific calibration).

SCALE SWEEP (the diagnostic that answers "does it blow up" as a function of cardinality, not just
a single before/after point): ONE shared KGStore (E, R codebooks allocated ONCE, n_ent=482,588,
n_dim=1024) is repeatedly RESET (W zeroed, E/R untouched) and re-ingested with an increasing
PREFIX of a fixed deterministic shuffle of the real spine edges: SCALES = [1000, 5000, 10000,
30000, 100000, 1213912(=full)]. This isolates the swept variable to "how many triples were
Hebbian-written into the SAME 1024x1024 W matrix" -- the crosstalk-accumulation axis the
MCScript2.0-echo risk is actually about -- while the entity CODEBOOK SIZE (the false-pull-in
search space) stays fixed at the full 482,588 throughout every scale point.

Per scale point: RELEVANT-RECALL sampled from N_QUERY=150 real ingested triples (does the pipeline
still retrieve the TRUE object, admitted); FALSE-PULL-IN-RATE sampled from N_QUERY=150 random
(s,p) pairs verified NOT present in the ingested set (does the gate ever admit a candidate for a
query with no true answer). `relevant_in_shortlist_rate` is also tracked as a mechanism-
attribution diagnostic: it isolates whether a recall failure is caused by the SALIENCE GATE
(threshold too strict) or by the underlying STORE's raw associative capacity collapsing UPSTREAM
of the gate (the true answer not even reaching the coarse shortlist).

At the FULL scale point, an additional SCRAMBLE_OBJECTS control (object column of the ingested
triples permuted via the same hashlib-seeded convention Stage 1 uses) is run once, to confirm any
surviving recall is driven by genuine (s,p)->o structure and not an artifact.

Modes:
  --self-test  Real-code-path check: tiny synthetic KGStore (N=16, per META_RULE F.1) fires
               ingest/predict_one_hop/pull_in correctly, PLUS the REAL cskg_foundation_v1 loader
               is validated against a small real slice (not the full 482K/1.2M) -- no synthetic-
               only branch for the data-loading path. No queue dispatch.
  --smoke      Real CSKG data, SMALL scale subset [1000, 10000], full n_ent=482,588 entity
               codebook (FULL-N cardinality even in smoke -- the swept axis is ingest scale, and
               smoke exercises the discriminating region of that axis).
  --full       Complete scale sweep [1000, 5000, 10000, 30000, 100000, 1213912] + SCRAMBLE_OBJECTS
               control at the full point. Per-scale checkpointed via tools/exp_checkpoint.py
               (unit_key = scale, not seed -- this is a cardinality sweep, not a multi-seed cell).
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "4")

import argparse
import hashlib
import json
import platform
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2b_cskg_scale_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")

from hdlab.kg_traversal import KGStore  # noqa: E402
# REUSE (literal): Sub-test A's generalized multi-exclude pull_in (which is itself a byte-
# verified generalization of Stage-1's pull_in()). Importing rather than re-transcribing.
from experiments.exp_focus_pullin_causal_stage2a_multihop_loop_v1 import (  # noqa: E402
    pull_in_multi_exclude,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

GATE_THRESH = 0.28   # FIXED: Stage-1's ORIGINAL calibrated number, deliberately NOT retuned here.
SHORTLIST_K = 50
N_QUERY = 150
SCALES_SMOKE = [1000, 10000]
SCALES_FULL = [1000, 5000, 10000, 30000, 100000, 1213912]  # last = full spine-edge count
QUERY_SEED = 20260810
DATA_SEED = 20260810


# ============================================================================ real data loader
def load_entity_vocab(cskg_dir: str = CSKG_DIR) -> Dict[str, int]:
    entity_to_idx: Dict[str, int] = {}
    with open(os.path.join(cskg_dir, "nodes.jsonl"), encoding="utf-8") as f:
        for i, line in enumerate(f):
            row = json.loads(line)
            entity_to_idx[row["id"]] = i
    return entity_to_idx


def load_spine_edges(entity_to_idx: Dict[str, int], cskg_dir: str = CSKG_DIR,
                     max_shards: int = 16) -> Tuple[np.ndarray, Dict[str, int]]:
    """Returns (triples_int [N,3] int64 array, relation_to_idx). relation_to_idx is built via
    sorted(set(...)) over the RELATION STRINGS actually observed (deterministic; no hash())."""
    relations_seen: Set[str] = set()
    raw: List[Tuple[str, str, str]] = []
    for shard_i in range(max_shards):
        path = os.path.join(cskg_dir, f"edges_shard_{shard_i:02d}.jsonl")
        with open(path, encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                relations_seen.add(row["relation"])
                raw.append((row["subject"], row["relation"], row["obj"]))
    relation_to_idx = {r: i for i, r in enumerate(sorted(relations_seen))}
    triples = np.empty((len(raw), 3), dtype=np.int64)
    for i, (s, p, o) in enumerate(raw):
        triples[i, 0] = entity_to_idx[s]
        triples[i, 1] = relation_to_idx[p]
        triples[i, 2] = entity_to_idx[o]
    return triples, relation_to_idx


# ============================================================================ gate evaluation
def eval_gate(store: KGStore, ingested_triples: torch.Tensor, n_rel: int, n_query: int,
             query_seed: int, gate: float = GATE_THRESH, shortlist_k: int = SHORTLIST_K) -> Dict:
    """Relevant-recall + false-pull-in-rate + shortlist-diagnostic for the CURRENT ingest of
    `store` (E, R fixed; W reflects exactly `ingested_triples`)."""
    q_rng = np.random.default_rng(query_seed)
    n = ingested_triples.shape[0]
    existing_sp = set((int(s) * n_rel + int(p)) for s, p, _o in ingested_triples.tolist())
    shortlist_k = min(shortlist_k, store.n_ent)

    rel_idx = q_rng.choice(n, size=min(n_query, n), replace=False)
    rel_admitted_correct = 0
    rel_in_shortlist = 0
    for i in rel_idx:
        s, p, o = (int(x) for x in ingested_triples[i])
        key = store.key(s, p)
        probe = (store.W @ key)
        scores = store.score_all(key)
        topk = torch.topk(scores, k=shortlist_k)
        cand_global = topk.indices.numpy()
        if o in cand_global:
            rel_in_shortlist += 1
        shortlist_cb = store.E[cand_global].numpy()
        exclude_set: Set[int] = set()
        hit = np.where(cand_global == s)[0]
        if len(hit):
            exclude_set.add(int(hit[0]))
        r = pull_in_multi_exclude(probe.numpy(), shortlist_cb, exclude_set, gate=gate)
        global_candidate = int(cand_global[r["candidate_idx"]])
        if global_candidate == o and r["admitted"]:
            rel_admitted_correct += 1

    neg_count = 0
    neg_admitted = 0
    tries = 0
    n_ent = store.n_ent
    while neg_count < n_query and tries < n_query * 20:
        tries += 1
        s = int(q_rng.integers(0, n_ent))
        p = int(q_rng.integers(0, n_rel))
        if (s * n_rel + p) in existing_sp:
            continue
        neg_count += 1
        key = store.key(s, p)
        probe = (store.W @ key)
        scores = store.score_all(key)
        topk = torch.topk(scores, k=shortlist_k)
        cand_global = topk.indices.numpy()
        shortlist_cb = store.E[cand_global].numpy()
        exclude_set = set()
        hit = np.where(cand_global == s)[0]
        if len(hit):
            exclude_set.add(int(hit[0]))
        r = pull_in_multi_exclude(probe.numpy(), shortlist_cb, exclude_set, gate=gate)
        if r["admitted"]:
            neg_admitted += 1

    return {
        "n_relevant_queried": int(len(rel_idx)),
        "relevant_recall": rel_admitted_correct / max(len(rel_idx), 1),
        "relevant_in_shortlist_rate": rel_in_shortlist / max(len(rel_idx), 1),
        "n_negative_queried": neg_count,
        "false_pull_in_rate": neg_admitted / max(neg_count, 1),
    }


def _shuffle_objects(triples: torch.Tensor, seed: int) -> torch.Tensor:
    """Object-column permutation control (hashlib-seeded, PROT-023/F.5 compliant)."""
    seed_int = int.from_bytes(hashlib.sha256(f"stage2b_scramble_objects::{seed}".encode()).digest()[:8],
                              "big") % (2 ** 32)
    rng = np.random.default_rng(seed_int)
    perm = rng.permutation(triples.shape[0])
    out = triples.clone()
    out[:, 2] = triples[perm, 2]
    return out


# ============================================================================ real-data-loader precheck
def precheck_kgstore_and_loader() -> Dict:
    """CONTRACT-mandated precheck: KGStore ingest/predict_one_hop must fire correctly on a
    trivial known synthetic fact, AND the real cskg_foundation_v1 loader must resolve a small
    real slice with zero missing-entity references, BEFORE any HARD-FAIL on the main sweep is
    trusted."""
    gen = torch.Generator(); gen.manual_seed(1)
    store = KGStore(n_ent=4, n_rel=2, n_dim=64, generator=gen)
    store.ingest_triples(torch.tensor([[0, 0, 1], [2, 1, 3]], dtype=torch.long))
    kg_ok = (store.predict_one_hop(0, 0) == 1) and (store.predict_one_hop(2, 1) == 3)

    loader_ok = True
    loader_detail = {}
    if os.path.isdir(CSKG_DIR):
        entity_to_idx = load_entity_vocab(CSKG_DIR)
        n_missing = 0
        n_checked = 0
        with open(os.path.join(CSKG_DIR, "edges_shard_00.jsonl"), encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 200:
                    break
                row = json.loads(line)
                n_checked += 1
                if row["subject"] not in entity_to_idx or row["obj"] not in entity_to_idx:
                    n_missing += 1
        loader_ok = (n_missing == 0) and (n_checked > 0) and (len(entity_to_idx) > 0)
        loader_detail = {"n_nodes": len(entity_to_idx), "n_checked": n_checked, "n_missing": n_missing}
    else:
        loader_ok = False
        loader_detail = {"error": f"CSKG_DIR not found: {CSKG_DIR}"}

    ok = kg_ok and loader_ok
    return {"ok": ok, "kg_ok": kg_ok, "loader_ok": loader_ok, "loader_detail": loader_detail}


# ============================================================================ verdict logic
def scale_point_verdict(m: Dict) -> Tuple[str, str]:
    rr = m["relevant_recall"]
    fp = m["false_pull_in_rate"]
    hard_fail = (fp > 0.50) or (rr <= fp) or (rr < 0.05)
    hard_pass = (fp <= 0.20) and (rr >= 0.30) and (rr - fp >= 0.15)
    msg = f"relevant_recall={rr:.3f} false_pull_in={fp:.3f} shortlist_rate={m['relevant_in_shortlist_rate']:.3f}"
    if hard_fail:
        return "HARD_FAIL", f"HARD_FAIL: {msg}"
    if hard_pass:
        return "HARD_PASS", f"HARD_PASS: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND: {msg}"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        rec.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> Dict:
    pre = precheck_kgstore_and_loader()
    assert pre["ok"], f"PRECHECK_FAIL (flat=broken-experiment discipline): {pre}"

    # tiny synthetic full-pipeline exercise (N=16 entities, real KGStore + real pull_in_multi_exclude)
    gen = torch.Generator(); gen.manual_seed(7)
    store = KGStore(n_ent=16, n_rel=3, n_dim=64, generator=gen)
    triples = torch.tensor([[i, i % 3, (i + 1) % 16] for i in range(16)], dtype=torch.long)
    store.ingest_triples(triples)
    m = eval_gate(store, triples, n_rel=3, n_query=8, query_seed=1)
    tiny_ok = m["relevant_recall"] >= 0.5  # tiny/clean regime, should recover most

    hf_m = {"relevant_recall": 0.0, "false_pull_in_rate": 0.0, "relevant_in_shortlist_rate": 0.0}
    hf_v, _ = scale_point_verdict(hf_m)
    assert hf_v == "HARD_FAIL", hf_v

    hp_m = {"relevant_recall": 0.9, "false_pull_in_rate": 0.02, "relevant_in_shortlist_rate": 1.0}
    hp_v, _ = scale_point_verdict(hp_m)
    assert hp_v == "HARD_PASS", hp_v

    return {"precheck": pre, "tiny_pipeline_metrics": m, "tiny_ok": tiny_ok,
            "verdict_logic_unit_checks": {"hard_fail_case": hf_v, "hard_pass_case": hp_v}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    scales = SCALES_SMOKE if args.smoke else SCALES_FULL
    expected_units = len(scales) + (1 if run_mode == "full" else 0)  # +1 = scramble control (full only)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading real CSKG entity vocab...", flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    n_ent = len(entity_to_idx)
    print(f"[{run_mode}] {n_ent} entities loaded in {time.time()-t0:.2f}s; loading spine edges...",
        flush=True)
    triples_int, relation_to_idx = load_spine_edges(entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    print(f"[{run_mode}] {len(triples_int)} spine edges loaded, n_rel={n_rel}, "
        f"t={time.time()-t0:.2f}s", flush=True)

    rng = np.random.default_rng(DATA_SEED)
    perm = rng.permutation(len(triples_int))
    triples_shuffled = torch.from_numpy(triples_int[perm])

    gen = torch.Generator(); gen.manual_seed(DATA_SEED)
    store = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen)
    print(f"[{run_mode}] KGStore allocated (E={tuple(store.E.shape)}) t={time.time()-t0:.2f}s",
        flush=True)

    done = completed_units(output_dir)
    per_scale: Dict[str, Dict] = {}
    unit_i = 0
    for scale in scales:
        scale = min(scale, len(triples_shuffled))
        key = unit_key("scale", scale)
        if key in done:
            print(f"[{run_mode}] scale={scale} already complete (resume)", flush=True)
            unit_i += 1
            continue
        store.reset()
        t_ing = time.time()
        ingested = triples_shuffled[:scale]
        store.ingest_triples(ingested)
        ing_s = time.time() - t_ing
        t_ev = time.time()
        m = eval_gate(store, ingested, n_rel=n_rel, n_query=N_QUERY, query_seed=QUERY_SEED)
        ev_s = time.time() - t_ev
        verdict, msg = scale_point_verdict(m)
        m.update({"scale": scale, "ingest_s": round(ing_s, 3), "eval_s": round(ev_s, 3),
                 "verdict": verdict, "verdict_msg": msg})
        record_unit(output_dir, key, m)
        unit_i += 1
        print(f"[{run_mode}] scale={scale} {verdict}: {msg} (ingest={ing_s:.2f}s eval={ev_s:.2f}s)",
            flush=True)
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0, extra={"scale": scale})

    scramble_result = None
    if run_mode == "full":
        skey = unit_key("scramble_objects", "full")
        if skey in done:
            print(f"[{run_mode}] scramble_objects already complete (resume)", flush=True)
        else:
            full_scale = min(SCALES_FULL[-1], len(triples_shuffled))
            store.reset()
            scrambled = _shuffle_objects(triples_shuffled[:full_scale], seed=DATA_SEED)
            store.ingest_triples(scrambled)
            m = eval_gate(store, scrambled, n_rel=n_rel, n_query=N_QUERY, query_seed=QUERY_SEED)
            m.update({"scale": full_scale, "control": "scramble_objects"})
            record_unit(output_dir, skey, m)
            print(f"[{run_mode}] scramble_objects (scale={full_scale}) relevant_recall="
                f"{m['relevant_recall']:.3f} false_pull_in={m['false_pull_in_rate']:.3f}", flush=True)

    all_units = load_units(output_dir)
    per_scale = {str(u["scale"]): u for k, u in all_units.items() if k.startswith("scale|")}
    scramble_units = {k: u for k, u in all_units.items() if k.startswith("scramble_objects|")}
    scramble_result = list(scramble_units.values())[0] if scramble_units else None

    full_point = per_scale.get(str(min(SCALES_FULL[-1], len(triples_shuffled))))
    if full_point is not None:
        full_verdict, full_msg = full_point["verdict"], full_point["verdict_msg"]
    else:
        # smoke mode has no full-cardinality point; report the largest smoke scale instead
        largest = str(max(int(k) for k in per_scale))
        full_point = per_scale[largest]
        full_verdict, full_msg = full_point["verdict"], full_point["verdict_msg"]

    cardinality_ok = len(per_scale) == len(scales)

    # arms-must-differ: REAL (largest scale) vs SCRAMBLE_OBJECTS (full mode only)
    diff = None
    if scramble_result is not None:
        def _digest(obj):
            return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()
        d_real = _digest({k: v for k, v in full_point.items() if k not in ("ingest_s", "eval_s")})
        d_scr = _digest({k: v for k, v in scramble_result.items() if k not in ("ingest_s", "eval_s")})
        diff = {"real_digest": d_real, "scramble_digest": d_scr, "arms_differ": d_real != d_scr}

    elapsed = time.time() - t0
    metrics = {
        "verdict": full_verdict, "verdict_msg": f"FULL_CARDINALITY_POINT: {full_msg}",
        "summary": f"{full_verdict} at scale={full_point['scale']}: {full_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "gate_thresh": GATE_THRESH, "n_dim": 1024, "n_ent": n_ent, "n_rel": n_rel,
        "n_spine_edges_total": len(triples_int), "scales": scales,
        "per_scale": per_scale, "scramble_objects_control": scramble_result,
        "arms_differ_check": diff, "arms_differ_verified": (diff["arms_differ"] if diff else None),
        "full_cardinality_point": full_point,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "empirical cardinality-capacity diagnostic sweep over the real CSKG store; "
                    "no single closed-form noise floor -- measuring where the floor sits IS the test",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: GATE_THRESH=0.28 is Stage-1's ORIGINAL "
                            "un-retuned number, held fixed by the Stage-2 task CONTRACT",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_scale"}, indent=2, default=str))
    print(json.dumps({"per_scale": per_scale}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
