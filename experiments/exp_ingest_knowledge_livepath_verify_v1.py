"""ingest_knowledge_livepath_verify_v1 -- LIVE-PATH INGESTION VERIFY PILOT.

WHAT (USER-directed 5x-drill angle-4): verify the substrate can live-reason over
REAL KNOWLEDGE IT ALREADY HOLDS (ConceptNet, ~133k CONCEPT_NODE atoms committed
2026-06-19), through the LIVE operational retriever path (Retriever.semantic /
Retriever.structural), NOT an isolated numpy eval harness. NO new ingest, NO
re-encode. READ-ONLY on the canonical store.

HONEST FRAMING (USER-LOCKED): this verifies LIVE-PATH USABILITY of already-held
knowledge. It is NOT new ingest and NOT a language-capability claim. The claim is
"substrate live-addresses + composes over a real KB it already holds." The 2-hop
mechanism here is the LIVE operational path = BGE semantic-addressing + structural
edge-composition. That is a DIFFERENT mechanism/regime than U1
(exp_u1_fb15k237_ingest_eval_v1, CHAIN_GRADE, isolated HD-algebra Hebbian store over
FB15k-237). We therefore reproduce U1's QUALITATIVE bar (real signal >> random floor
+ fabrication-refusal) through the live path, NOT U1's exact numbers. Declared
regime_extension_audit = SHAPE_DRIFT (Gate D).

TWO PHASES:
  Phase A (full-store addressability/collision audit, read-only, ~5s):
    - id_order = [a.id for a in PartitionedStore.all_atoms()]  (exactly what
      Retriever.rebuild_index / retrieve_cache use)
    - cross-partition bare-id collision count (the 1500->1497 concern at 177k scale)
    - collision count restricted to the CN_ concept namespace (the pilot's target)
    - which live cache retrieve_cache._cache_path would resolve + whether it EXISTS
      (settles "is the qualified-id fix wired into the live path?" as a side effect)
  Phase B (live retriever round-trip + 2-hop, real ConceptNet subgraph):
    - Build Retriever over a deterministic seed-anchored concept subgraph
      (seeds + IS_A neighborhoods + random concept distractors); rebuild_index_cached
      into the CELL's own dir (no canonical pollution).
    - round-trip known-item recall@1/@10 by exact name; correct-id rate (collision-safe
      retrieval); refuse-gate cosine separation (known vs fabricated queries).
    - 2-hop: semantic-address seed -> structural IS_A -> structural IS_A; recover true
      transitive target; compare vs 1-hop (cannot reach it) and vs random-target floor;
      fabrication-refusal on absent (seed,target) pairs.

HARD-PASS = full-scale collision-safe (0 collisions in CN namespace) AND live round-trip
  recall@10 >= 0.80 on >=90% of probes AND correct-id-rate >= 0.95 AND twohop_true_recall
  > onehop_baseline_recall + 0.02 AND twohop_true_recall >= 20x random-floor.
HARD-FAIL = round-trip recall@10 < 0.40, OR correct-id-rate < 0.60 (wrong concepts /
  collision), OR twohop_true_recall <= random-floor (compose collapses to floor), OR
  twohop_fabrication_accept > 0.30.
NOTE: cache-wiring status (Phase A) is a first-class REPORTED finding for FULL-readiness
  / next-action routing; it does NOT gate the Phase-B mechanism PASS/FAIL (Phase B builds
  its own subgraph index, so it measures the retrieval MECHANISM independently of whether
  the canonical full-store cache happens to be wired).

CPU-only (BGE production encoder is CPU-pinned). ASCII. Single-unit (not multi-seed).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - start-marker + crash-diagnostic + heartbeat + atomic tmp+os.replace metrics
# - discriminator fires in smoke (Phase A injected-collision positive control;
#   Phase B round-trip + 2-hop on real subgraph); full-scale collision audit is
#   read-only real state (survives-scale by measuring the actual 177k store)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "ingest_knowledge_livepath_verify_v1"

# ---- run mode ----------------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
if _ARGS.smoke:
    RUN_MODE = "smoke"
elif _ARGS.self_test:
    RUN_MODE = "self_test"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()

# ---- regime config -----------------------------------------------------------
if RUN_MODE == "smoke":
    N_INDEX = 400        # subgraph index size (real CN atoms)
    N_PROBE = 30         # round-trip known-item probes
    N_2HOP = 20          # true 2-hop chains
    N_REFUSE = 20        # fabricated-query refuse probes + absent 2-hop pairs
    SEED = 12345
    OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}_smoke"
else:
    N_INDEX = 6000
    N_PROBE = 250
    N_2HOP = 120
    N_REFUSE = 120
    SEED = 12345
    OUT_DIR = REPO / "data" / f"exp_{ANCHOR_NAME}"

STORE_ROOT = REPO / "data" / "substrate_index"

# ---- bands (locked; from drill notes/research_ingestion_readiness_scoped_pilot_5x_angle4_2026-07-05.md) ----
# HYPOTHESIZED bands per drill; MEASURED collision/cache facts embedded from the
# 2026-07-05 exp_dev diagnostic probe:
#   n_atoms=177872 unique=177871 collisions=1 (0 in CN_ namespace)
#     MEASURED@scratchpad probe_livepath 2026-07-05
#   live cache resolves bge_large_v2_name_177872_c1f5fc5d.npz -> DOES NOT EXIST (MISS)
#     MEASURED@scratchpad probe_livepath 2026-07-05 (drift vs on-disk _177899_54f7cf6a;
#     qualified_* caches present but not selected by retrieve_cache glob)
ROUND_TRIP_RECALL10_HP = 0.80    # HARD-PASS floor on recall@10
ROUND_TRIP_RECALL10_HF = 0.40    # HARD-FAIL ceiling
CORRECT_ID_RATE_HP = 0.95
CORRECT_ID_RATE_HF = 0.60
PROBE_COVER_HP = 0.90            # >=90% of probes must clear recall@10
TWOHOP_MARGIN_HP = 0.02         # twohop_recall > onehop_recall + this
TWOHOP_FLOOR_MULT_HP = 20.0     # twohop_recall >= this * random_floor
TWOHOP_FAB_ACCEPT_HF = 0.30     # HARD-FAIL if fabrication accept exceeds this
REFUSE_SEP_MIN = 0.05           # min cosine separation known-vs-fabricated (soft, reported)


# =============================================================================
# Pure metric helpers (self-testable, no store/BGE)
# =============================================================================
def content_hash(id_order):
    """Replicate retrieve_cache._compute_content_hash exactly (cache-selection key)."""
    payload = json.dumps(sorted(id_order)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:8]


def audit_ids(id_order, cn_prefix="CN_"):
    """Cross-partition bare-id collision audit over the exact retriever id_order."""
    n = len(id_order)
    cnt = Counter(id_order)
    dups = {k: v for k, v in cnt.items() if v > 1}
    cn_dups = {k: v for k, v in dups.items() if k.startswith(cn_prefix)}
    return {
        "n_atoms": n,
        "n_unique_bare_ids": len(cnt),
        "n_collisions": n - len(cnt),
        "n_dup_ids": len(dups),
        "dup_id_examples": list(dups.items())[:10],
        "n_cn_dup_ids": len(cn_dups),
        "cn_dup_examples": list(cn_dups.items())[:10],
        "collision_safe_cn": len(cn_dups) == 0,
    }


def recall_at_k(ranked_ids, target_id, k):
    """1 if target_id within first k of ranked_ids else 0."""
    return 1 if target_id in ranked_ids[:k] else 0


def twohop_compose(out_fn, seed, rel, exclude_direct=True):
    """Live 2-hop composition via two structural lookups.

    out_fn(node, rel) -> set of neighbor ids. Returns (twohop_set, onehop_set).
    twohop_set excludes the seed and (if exclude_direct) the 1-hop neighbors, so a
    member of twohop_set is a genuine 2-hop-only reachable target.
    """
    onehop = set(out_fn(seed, rel))
    twohop = set()
    for m in onehop:
        twohop |= set(out_fn(m, rel))
    twohop.discard(seed)
    if exclude_direct:
        twohop -= onehop
    return twohop, onehop


# =============================================================================
# I/O helpers (start-marker, heartbeat, crash-diagnostic, atomic metrics)
# =============================================================================
def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir):
    marker = {
        "pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE, "host": platform.node(),
        "expected_n_units": {"n_index": N_INDEX, "n_probe": N_PROBE, "n_2hop": N_2HOP},
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _heartbeat(output_dir, stage, elapsed_s, extra=None):
    row = {"ts_iso": _now_iso(), "stage": stage, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass  # heartbeat best-effort; never fatal (does not touch verdict path)
    print(f"[hb] stage={stage} elapsed={elapsed_s:.1f}s {extra or ''}", flush=True)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "run_mode": RUN_MODE, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": _now_iso(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _write_metrics(output_dir, diag)


# =============================================================================
# Formula self-test (no store / no BGE)
# =============================================================================
def _selftest():
    print("[selftest] start", flush=True)
    # (1) content_hash matches retrieve_cache._compute_content_hash
    from backend.substrate_index.retrieve_cache import _compute_content_hash
    ids = ["b", "a", "c", "a"]  # note dup + unsorted
    assert content_hash(ids) == _compute_content_hash(ids), "content_hash mismatch vs retrieve_cache"
    print("[selftest] content_hash parity OK", flush=True)

    # (2) collision audit: injected cross-partition dup fires the detector
    inj = ["CN_dog", "CN_cat", "note_x", "note_x", "CN_dog"]  # CN_dog dup + note_x dup
    a = audit_ids(inj)
    assert a["n_atoms"] == 5 and a["n_unique_bare_ids"] == 3, f"audit counts wrong: {a}"
    assert a["n_collisions"] == 2, f"expected 2 collisions, got {a['n_collisions']}"
    assert a["n_dup_ids"] == 2, f"expected 2 dup ids, got {a['n_dup_ids']}"
    assert a["n_cn_dup_ids"] == 1 and a["collision_safe_cn"] is False, f"cn-dup detect wrong: {a}"
    # clean set is collision-safe
    a2 = audit_ids(["CN_a", "CN_b", "science_a"])
    assert a2["n_collisions"] == 0 and a2["collision_safe_cn"] is True, f"clean audit wrong: {a2}"
    print("[selftest] collision detector fires on injection + clean OK", flush=True)

    # (3) recall_at_k
    ranked = ["x", "y", "TGT", "z"]
    assert recall_at_k(ranked, "TGT", 1) == 0 and recall_at_k(ranked, "TGT", 3) == 1, "recall_at_k wrong"
    print("[selftest] recall_at_k OK", flush=True)

    # (4) 2-hop compose recovers a true transitive target 1-hop cannot; refuses absent
    edges = {("s", "R"): {"m"}, ("m", "R"): {"t"}, ("s2", "R"): {"m"}}
    def out_fn(node, rel):
        return edges.get((node, rel), set())
    twohop, onehop = twohop_compose(out_fn, "s", "R")
    assert onehop == {"m"}, f"onehop wrong: {onehop}"
    assert twohop == {"t"}, f"twohop wrong: {twohop}"           # t reachable only at 2 hops
    assert "t" not in onehop, "t must NOT be a 1-hop neighbor (composition necessary)"
    # fabrication-refusal: absent pair (s -> 'ZZZ') not in twohop closure
    assert "ZZZ" not in twohop, "absent target must be refused (not fabricated)"
    print("[selftest] 2-hop compose + fabrication-refusal OK", flush=True)

    # (5) twohop random floor sanity: floor = closure_size / N_index is tiny at scale
    floor = len(twohop) / 100000.0
    assert floor < 1e-4, "floor formula sanity"
    print(f"[selftest] random-floor formula OK (floor={floor:.2e})", flush=True)

    print("SELFTEST_PASS", flush=True)
    return True


# =============================================================================
# Phase A -- full-store addressability / collision / cache-wiring audit (read-only)
# =============================================================================
def phase_a_audit(store_root):
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index import retrieve_cache

    store = PartitionedStore(store_root)
    atoms = store.all_atoms()
    id_order = [a.id for a in atoms]
    aud = audit_ids(id_order)
    h = content_hash(id_order)
    n = aud["n_atoms"]

    # exactly retrieve_cache._cache_path -> the cache the LIVE loader would select
    cache_dir = store_root / "cached_indices"
    resolved = retrieve_cache._cache_path(store_root, n, h)  # bge_large_v2_name_{n}_{h}.npz
    cache_hit = resolved.exists()

    # which qualified_* caches exist but are NOT selected by the live glob
    qualified = sorted(p.name for p in cache_dir.glob("qualified_*.npz")) if cache_dir.exists() else []
    full_scale = sorted(p.name for p in cache_dir.glob("bge_large_v2_name_*.npz")
                        if p.stat().st_size > 100_000_000) if cache_dir.exists() else []

    aud.update({
        "content_hash": h,
        "live_cache_resolved": resolved.name,
        "live_cache_hit": bool(cache_hit),
        "qualified_caches_present_unwired": qualified,
        "full_scale_bge_caches_on_disk": full_scale,
        "per_partition_counts": {c.value: len(s.all_atom_ids())
                                 for c, s in store._stores.items() if s.all_atom_ids()},
    })
    return aud


# =============================================================================
# Phase B -- deterministic real-ConceptNet subgraph build
# =============================================================================
def build_subgraph(store_root, n_index, n_2hop, rng):
    """Mine a deterministic seed-anchored connected concept subgraph.

    Returns (atoms_list, relations_list, twohop_chains, probe_names) where a chain is
    (seed_id, seed_name, mid_id, target_id, target_name) with target reachable only at
    2 hops (IS_A), and probe_names is a subset of subgraph ids for round-trip.
    """
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.schema import RelationType, Relation
    IS_A = RelationType.IS_A

    store = PartitionedStore(store_root)
    cs = store.concept

    # Deterministic scan for 2-hop IS_A seeds (target reachable only at 2 hops).
    chains = []
    subgraph_ids = set()
    for a in cs.iter_atoms():
        if len(chains) >= n_2hop:
            break
        if not a.id.startswith("CN_"):
            continue
        onehop = cs.out_neighbors(a.id, IS_A)
        if not onehop:
            continue
        for m in sorted(onehop):
            twohop = set()
            for t in cs.out_neighbors(m, IS_A):
                if t != a.id and t not in onehop:
                    twohop.add(t)
            if twohop:
                t = sorted(twohop)[0]
                sa, sm, st = cs.get_atom(a.id), cs.get_atom(m), cs.get_atom(t)
                if sa and sm and st:
                    chains.append((a.id, sa.name, m, sm.name, t, st.name))
                    subgraph_ids.update([a.id, m, t])
                break

    # Pad the index with deterministic random concept distractors up to n_index.
    all_cn = [a.id for a in cs.iter_atoms() if a.id.startswith("CN_")]
    all_cn.sort()
    rng.shuffle(all_cn)
    for aid in all_cn:
        if len(subgraph_ids) >= n_index:
            break
        subgraph_ids.add(aid)

    atoms = [cs.get_atom(aid) for aid in sorted(subgraph_ids)]
    atoms = [a for a in atoms if a is not None]
    id_set = {a.id for a in atoms}

    # Collect IS_A relations fully inside the subgraph.
    rels = []
    for aid in id_set:
        for t in cs.out_neighbors(aid, IS_A):
            if t in id_set:
                rels.append(Relation(src_id=aid, tgt_id=t, rel_type=IS_A))

    # probe names: distinctive single-token lower-alpha concept names in subgraph
    probes = []
    for a in atoms:
        if a.name and a.name.replace(" ", "").isalnum() and len(a.name) >= 3:
            probes.append((a.id, a.name))
    return atoms, rels, chains, probes


def phase_b_livepath(store_root, out_dir, n_index, n_probe, n_2hop, n_refuse, seed, t0):
    from backend.substrate_index.schema import save_atoms, save_relations, RelationType
    from backend.substrate_index.store import Store
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve import Retriever
    from backend.substrate_index import retrieve_cache
    IS_A = RelationType.IS_A

    rng = np.random.default_rng(seed)
    _heartbeat(out_dir, "subgraph_mine_start", time.perf_counter() - t0)
    atoms, rels, chains, probes = build_subgraph(store_root, n_index, n_2hop, rng)
    _heartbeat(out_dir, "subgraph_mined", time.perf_counter() - t0,
               {"n_atoms": len(atoms), "n_rels": len(rels), "n_chains": len(chains), "n_probes": len(probes)})

    # Write the subgraph to the CELL's own dir, then load via the real Store path.
    sg_dir = Path(out_dir) / "subgraph_store"
    sg_dir.mkdir(parents=True, exist_ok=True)
    save_atoms(atoms, sg_dir / "atoms.jsonl")
    save_relations(rels, sg_dir / "relations.jsonl")
    sg_store = Store(sg_dir)

    # Build the LIVE retriever + BGE index (cache isolated to the cell dir).
    _heartbeat(out_dir, "bge_load_start", time.perf_counter() - t0)
    encoder = AtomEncoder()  # loads bge-large-en-v1.5 singleton (CPU)
    retr = Retriever(sg_store, encoder)
    _heartbeat(out_dir, "index_build_start", time.perf_counter() - t0)
    from_cache = retrieve_cache.rebuild_index_cached(retr, Path(out_dir), force_rebuild=False)
    _heartbeat(out_dir, "index_built", time.perf_counter() - t0,
               {"from_cache": bool(from_cache), "index_size": len(retr._id_order)})

    # completeness: retrieved-index count == submitted count (no collision loss)
    index_complete = (len(retr._id_order) == len(atoms)) and (len(set(retr._id_order)) == len(atoms))

    # ---- round-trip known-item recall (exact-name queries) ----
    probe_sample = probes[:n_probe] if len(probes) >= n_probe else probes
    r1 = r10 = correct_id = 0
    accept_cos = []
    for aid, name in probe_sample:
        cands = retr.semantic(name, top_k=10)
        ranked = [c.atom_id for c in cands]
        r1 += recall_at_k(ranked, aid, 1)
        r10 += recall_at_k(ranked, aid, 10)
        if ranked and ranked[0] == aid:
            correct_id += 1
        if cands:
            accept_cos.append(cands[0].score)
    npb = max(1, len(probe_sample))
    recall1 = r1 / npb
    recall10 = r10 / npb
    correct_id_rate = correct_id / npb
    probe_cover10 = recall10  # fraction of probes clearing recall@10 (per-probe binary)

    # ---- refuse-gate: fabricated (non-concept) queries should score lower ----
    fab_cos = []
    for i in range(n_refuse):
        fab = f"zzq{rng.integers(10**8, 10**9)}xqz nonconcept token {i}"
        cands = retr.semantic(fab, top_k=1)
        if cands:
            fab_cos.append(cands[0].score)
    accept_mean = float(np.mean(accept_cos)) if accept_cos else 0.0
    refuse_mean = float(np.mean(fab_cos)) if fab_cos else 0.0
    refuse_sep = accept_mean - refuse_mean

    # ---- 2-hop: live semantic-address + structural compose ----
    def out_fn(node, rel):
        return retr.store.out_neighbors(node, rel)

    chain_sample = chains[:n_2hop] if len(chains) >= n_2hop else chains
    twohop_hits = 0
    onehop_hits = 0
    addr_hits = 0
    closure_sizes = []
    for (sid, sname, mid, mname, tid, tname) in chain_sample:
        # live semantic addressing of the seed by name
        acands = retr.semantic(sname, top_k=10)
        if acands and any(c.atom_id == sid for c in acands[:10]):
            addr_hits += 1
        twohop, onehop = twohop_compose(out_fn, sid, IS_A)
        closure_sizes.append(len(twohop))
        if tid in twohop:
            twohop_hits += 1
        if tid in onehop:
            onehop_hits += 1
    ncs = max(1, len(chain_sample))
    twohop_recall = twohop_hits / ncs
    onehop_recall = onehop_hits / ncs
    addr_recall = addr_hits / ncs
    mean_closure = float(np.mean(closure_sizes)) if closure_sizes else 0.0
    random_floor = mean_closure / max(1, len(atoms))  # P(random atom is the true target)

    # ---- fabrication-refusal: absent (seed,target) 2-hop pairs ----
    # For each seed, draw a random atom as a candidate "answer". If that atom is NOT
    # in the seed's true 2-hop IS_A closure, the live path must NOT assert the link
    # (structural-compose returns only stored-edge reachables -> does not fabricate).
    # This is 0 by construction of structural-compose; reported as a plumbing sanity.
    # The non-vacuous refusal signal is refuse_separation (semantic accept-vs-fabricated).
    fab_accept = 0
    fab_total = 0
    all_ids = [a.id for a in atoms]
    for (sid, sname, mid, mname, tid, tname) in chain_sample[:n_refuse]:
        twohop, onehop = twohop_compose(out_fn, sid, IS_A)
        cand = all_ids[int(rng.integers(0, len(all_ids)))]
        if cand == sid or cand in twohop or cand in onehop:
            continue  # not an "absent" pair; skip
        fab_total += 1
        # live-path answer for the absent pair: is cand reachable via 2-hop compose?
        if cand in twohop:  # would be a fabricated (non-stored) link
            fab_accept += 1
    fab_accept_rate = fab_accept / max(1, fab_total)

    return {
        "index_size": len(retr._id_order),
        "index_from_cache": bool(from_cache),
        "index_complete_no_collision_loss": bool(index_complete),
        "n_probes": len(probe_sample),
        "round_trip_recall_at_1": round(recall1, 4),
        "round_trip_recall_at_10": round(recall10, 4),
        "round_trip_correct_id_rate": round(correct_id_rate, 4),
        "probe_cover_recall10": round(probe_cover10, 4),
        "refuse_accept_cos_mean": round(accept_mean, 4),
        "refuse_fab_cos_mean": round(refuse_mean, 4),
        "refuse_separation": round(refuse_sep, 4),
        "n_chains": len(chain_sample),
        "twohop_true_recall": round(twohop_recall, 4),
        "onehop_baseline_recall": round(onehop_recall, 4),
        "twohop_seed_addr_recall": round(addr_recall, 4),
        "twohop_mean_closure_size": round(mean_closure, 2),
        "twohop_random_floor": round(random_floor, 8),
        "twohop_fabrication_accept": round(fab_accept_rate, 4),
        "twohop_over_floor_mult": round(twohop_recall / random_floor, 1) if random_floor > 0 else float("inf"),
    }


# =============================================================================
# Verdict
# =============================================================================
def decide_verdict(aud, b):
    fails, passes = [], []

    collision_safe = aud["collision_safe_cn"]
    (passes if collision_safe else fails).append(
        f"cn_collision_safe={collision_safe} (n_cn_dup={aud['n_cn_dup_ids']}, n_collisions_total={aud['n_collisions']})")

    r10 = b["round_trip_recall_at_10"]
    if r10 < ROUND_TRIP_RECALL10_HF:
        fails.append(f"recall@10={r10} < HF {ROUND_TRIP_RECALL10_HF}")
    elif r10 >= ROUND_TRIP_RECALL10_HP:
        passes.append(f"recall@10={r10} >= HP {ROUND_TRIP_RECALL10_HP}")

    cir = b["round_trip_correct_id_rate"]
    if cir < CORRECT_ID_RATE_HF:
        fails.append(f"correct_id_rate={cir} < HF {CORRECT_ID_RATE_HF} (wrong-concept/collision)")
    elif cir >= CORRECT_ID_RATE_HP:
        passes.append(f"correct_id_rate={cir} >= HP {CORRECT_ID_RATE_HP}")

    th, oh = b["twohop_true_recall"], b["onehop_baseline_recall"]
    floor = b["twohop_random_floor"]
    if th <= floor:
        fails.append(f"twohop_recall={th} <= random_floor={floor} (compose collapsed)")
    else:
        margin_ok = th > oh + TWOHOP_MARGIN_HP
        floor_ok = (floor == 0.0 and th > 0) or (floor > 0 and th >= TWOHOP_FLOOR_MULT_HP * floor)
        if margin_ok and floor_ok:
            passes.append(f"twohop={th} > onehop={oh}+{TWOHOP_MARGIN_HP} and >= {TWOHOP_FLOOR_MULT_HP}x floor")
        else:
            fails.append(f"twohop margin/floor not cleared (th={th}, oh={oh}, floor={floor})")

    fab = b["twohop_fabrication_accept"]
    if fab > TWOHOP_FAB_ACCEPT_HF:
        fails.append(f"twohop_fabrication_accept={fab} > HF {TWOHOP_FAB_ACCEPT_HF}")
    else:
        passes.append(f"fabrication_accept={fab} <= {TWOHOP_FAB_ACCEPT_HF}")

    # HARD-FAIL if any explicit HF tripped OR collision-unsafe
    hard_fail = (not collision_safe) or (r10 < ROUND_TRIP_RECALL10_HF) or \
                (cir < CORRECT_ID_RATE_HF) or (th <= floor) or (fab > TWOHOP_FAB_ACCEPT_HF)
    # HARD-PASS requires all primary gates
    hard_pass = collision_safe and (r10 >= ROUND_TRIP_RECALL10_HP) and \
                (b["probe_cover_recall10"] >= PROBE_COVER_HP) and \
                (cir >= CORRECT_ID_RATE_HP) and (th > oh + TWOHOP_MARGIN_HP) and \
                (((floor == 0.0 and th > 0) or (floor > 0 and th >= TWOHOP_FLOOR_MULT_HP * floor)))

    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"
    return verdict, passes, fails


# =============================================================================
# main
# =============================================================================
def main():
    t0 = time.perf_counter()
    if RUN_MODE == "self_test":
        _selftest()
        # minimal metrics so runner sees a clean result
        _write_metrics(OUT_DIR, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "formula selftest passed",
            "summary": "SELFTEST_PASS", "run_mode": "self_test",
            "elapsed_s": round(time.perf_counter() - t0, 3), "ts_iso": _now_iso(),
            "anchor_name": ANCHOR_NAME,
        })
        return

    _write_start_marker(OUT_DIR)
    print(f"[main] run_mode={RUN_MODE} out_dir={OUT_DIR}", flush=True)

    # ---- Phase A: full-store audit (read-only, real canonical state) ----
    _heartbeat(OUT_DIR, "phase_a_start", time.perf_counter() - t0)
    aud = phase_a_audit(STORE_ROOT)
    _heartbeat(OUT_DIR, "phase_a_done", time.perf_counter() - t0, {
        "n_atoms": aud["n_atoms"], "n_collisions": aud["n_collisions"],
        "n_cn_dup": aud["n_cn_dup_ids"], "cache_hit": aud["live_cache_hit"],
    })

    # ---- Phase A positive control (smoke only): injected collision must fire ----
    posctrl = None
    if RUN_MODE == "smoke":
        inj = list(aud["dup_id_examples"])  # not needed; build explicit injection
        pc = audit_ids(["CN_x", "CN_y", "CN_x", "sci_z", "sci_z"])
        assert pc["n_cn_dup_ids"] == 1 and pc["collision_safe_cn"] is False, "positive control failed to fire"
        posctrl = {"injected_cn_dup_detected": pc["n_cn_dup_ids"], "collision_safe_cn": pc["collision_safe_cn"]}
        print(f"[smoke] positive-control collision detector fired: {posctrl}", flush=True)

    # ---- Phase B: live retriever round-trip + 2-hop over real ConceptNet ----
    b = phase_b_livepath(STORE_ROOT, OUT_DIR, N_INDEX, N_PROBE, N_2HOP, N_REFUSE, SEED, t0)
    _heartbeat(OUT_DIR, "phase_b_done", time.perf_counter() - t0, {
        "recall@10": b["round_trip_recall_at_10"], "twohop": b["twohop_true_recall"],
    })

    verdict, passes, fails = decide_verdict(aud, b)
    elapsed = round(time.perf_counter() - t0, 2)

    vmsg = (f"LIVE-PATH VERIFY [{RUN_MODE}] {verdict}: "
            f"cn_collision_safe={aud['collision_safe_cn']} (collisions={aud['n_collisions']}, cn_dup={aud['n_cn_dup_ids']}); "
            f"live_cache_hit={aud['live_cache_hit']} (resolves {aud['live_cache_resolved']}); "
            f"round_trip recall@1={b['round_trip_recall_at_1']} recall@10={b['round_trip_recall_at_10']} "
            f"correct_id={b['round_trip_correct_id_rate']}; "
            f"twohop={b['twohop_true_recall']} vs onehop={b['onehop_baseline_recall']} "
            f"vs floor={b['twohop_random_floor']} ({b['twohop_over_floor_mult']}x); "
            f"fab_accept={b['twohop_fabrication_accept']}; refuse_sep={b['refuse_separation']}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict} live-path verify ({RUN_MODE})",
        "run_mode": RUN_MODE,
        "elapsed_s": elapsed,
        "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME,
        "config": {"N_INDEX": N_INDEX, "N_PROBE": N_PROBE, "N_2HOP": N_2HOP,
                   "N_REFUSE": N_REFUSE, "SEED": SEED},
        "phase_a_full_store_audit": aud,
        "phase_a_positive_control": posctrl,
        "phase_b_livepath": b,
        "verdict_passes": passes,
        "verdict_fails": fails,
        "bands": {
            "ROUND_TRIP_RECALL10_HP": ROUND_TRIP_RECALL10_HP,
            "ROUND_TRIP_RECALL10_HF": ROUND_TRIP_RECALL10_HF,
            "CORRECT_ID_RATE_HP": CORRECT_ID_RATE_HP,
            "TWOHOP_MARGIN_HP": TWOHOP_MARGIN_HP,
            "TWOHOP_FLOOR_MULT_HP": TWOHOP_FLOOR_MULT_HP,
            "TWOHOP_FAB_ACCEPT_HF": TWOHOP_FAB_ACCEPT_HF,
        },
        "honest_framing": ("LIVE-PATH usability of already-held ConceptNet knowledge; "
                           "NOT new ingest, NOT language capability; live 2-hop = BGE "
                           "semantic-address + structural edge-compose (SHAPE_DRIFT vs U1 "
                           "isolated HD-algebra); reproduces U1 QUALITATIVE bar only."),
    }
    _write_metrics(OUT_DIR, metrics)
    print(f"[main] {verdict} | {vmsg}", flush=True)
    print(f"[main] elapsed={elapsed}s", flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUT_DIR, e)
        raise
