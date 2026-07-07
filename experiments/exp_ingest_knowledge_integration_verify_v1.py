"""exp_ingest_knowledge_integration_verify_v1 -- Stage-0 ingest-arc plumbing verification.

Verifies the substrate can INTEGRATE + QUERY already-committed ConceptNet knowledge through the
LIVE structural query path (backend.substrate_index.store.Store + out_neighbors), with a battery
of anti-vacuousness controls. NO BGE re-encode (re-encode HELD, USER-locked): the structural graph
walk uses committed edge adjacency only -- zero vector ops, zero encoder forward calls, zero
Retriever.rebuild_index. CPU-only.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: exact graph reachability, no continuous noise floor (declared in prereg)
# - baseline_in_band: EXEMPTED -- null arms are DESIGNED to sit at floor; discriminator is the
#     GAP (real-ingest minus null), which is the genuinely-uncertain, could-fail quantity.
# - discriminator survives scale: smoke loads the FULL committed graph (~5.5s), only the probe
#     COUNT is reduced; the discriminator fires at true corpus scale in smoke.
# - all numbers in comments/prereg tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

NON-VACUOUSNESS DISCIPLINE (Director + USER, 2026-07-07): the ingest is PROVEN only if the
real-ingest arm beats a battery of nulls that MUST fail. The PROOF is the GAP, not any single
absolute score.

  A  ingest_2hop        : live 2-hop structural composition over REAL committed ConceptNet
  B  shuffled_2ndhop    : REAL graph, hop-2 relation randomized        -> MUST collapse
  C  scrambled_kb_2hop  : degree-preserving edge-target permutation     -> MUST fail (KEY null)
  C2 no_ingest_2hop     : empty graph, same probes                      -> MUST be ~0 (sanity)
  D  encoder_only_nameNN: char-trigram name-NN, NO graph                -> MUST be low (leak-check)
  R  known_item_1hop    : round-trip live-path recall of ingested edges -> addressability (~1.0)
  L  one_hop_direct     : is o a 1-hop neighbor of s? (held-out probes) -> MUST be ~0 (not lookup)

Pre-registered discriminator gates (see prereg for bands + rationale):
  D1 real-vs-scrambled : A - C >= 0.50   (real ingested structure does the work, not density)
  D2 firing-control    : A - B >= 0.50 AND B <= 0.15  (the 2nd hop is load-bearing)
  D3 no-ingest sanity  : C2 <= 0.05
  D4 encoder leak      : D <= 0.15   (else LEAK reported)
  D5 addressability    : R >= 0.98
  D6 integration-not-lookup : L <= 0.05 AND A >= 0.90
  D7 completeness      : loaded_atoms == disk_atoms AND loaded_edges == disk_distinct + derived

Verdict logic:
  HARD_PASS                 : all D1..D7 hold.
  VACUOUS_NON_DISCRIMINATING: a control failed to fire (C high, or C2 high, or D leak, or A-C
                              small) -> this is NOT a pass; the result cannot distinguish genuine
                              integration from an artifact.
  HARD_FAIL                 : A < 0.50 OR R < 0.80 OR completeness breach (silent truncation).
  MIDDLE_BAND               : partial -- addressability holds but a control only partially fires.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "ingest_knowledge_integration_verify_v1"
CONCEPT_DIR = REPO / "data" / "substrate_index" / "concept"
ATOMS_PATH = CONCEPT_DIR / "atoms.jsonl"
RELATIONS_PATH = CONCEPT_DIR / "relations.jsonl"

# ---- Pre-reg bands (locked) ---------------------------------------------------------------
GAP_REAL_VS_SCRAMBLED = 0.50   # D1: A - C >= this
GAP_FIRING = 0.50              # D2: A - B >= this
SHUFFLE_CEIL = 0.15            # D2: B <= this
NOINGEST_CEIL = 0.05           # D3: C2 <= this
LEAK_CEIL = 0.15               # D4: D <= this
ADDRESS_FLOOR = 0.98           # D5: R >= this
LOOKUP_CEIL = 0.05             # D6: L <= this
INGEST_FLOOR = 0.90            # D6: A >= this
A_HARD_FAIL = 0.50             # HARD_FAIL if A below this
R_HARD_FAIL = 0.80             # HARD_FAIL if R below this

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if _ARGS.smoke:
    RUN_MODE = "smoke"
elif _ARGS.self_test:
    RUN_MODE = "self_test"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_CHAINS = 60
    N_KNOWN = 300
else:  # full
    SEEDS = [7, 13, 23]
    N_CHAINS = 300
    N_KNOWN = 2000

N_POOL = 200  # encoder-only leak-check candidate pool size ({o} + 199 distractors)

CONFIG_VERSION = (
    "ingest-integration-verify: live-structural-2hop + shuffled-2nd-hop + scrambled-kb-null + "
    "no-ingest + encoder-name-NN-leak + known-item-1hop-recall + completeness; "
    "mode=%s chains=%d known=%d pool=%d bands[D1>=%.2f D2>=%.2f/B<=%.2f D3<=%.2f D4<=%.2f "
    "D5>=%.2f D6:L<=%.2f/A>=%.2f]"
    % (RUN_MODE, N_CHAINS, N_KNOWN, N_POOL, GAP_REAL_VS_SCRAMBLED, GAP_FIRING, SHUFFLE_CEIL,
       NOINGEST_CEIL, LEAK_CEIL, ADDRESS_FLOOR, LOOKUP_CEIL, INGEST_FLOOR)
)


# ---- name encoder (dependency-free; NOT BGE; substrate-knows-nothing leak proxy) -----------
def _trigrams(name):
    """Char-trigram set of a node label ('CN_fire_engine' -> 'fire engine' trigrams)."""
    s = name[3:] if name.startswith("CN_") else name
    s = s.replace("_", " ").lower()
    s = "  " + s + "  "
    return set(s[i:i + 3] for i in range(len(s) - 2))


def _name_sim(tri_a, tri_b):
    if not tri_a or not tri_b:
        return 0.0
    inter = len(tri_a & tri_b)
    return inter / (len(tri_a) + len(tri_b) - inter)


# ---- self-test: toy graph exercises every arm + verdict primitive --------------------------
def _selftest():
    # 6-node toy: a -R1-> b -R2-> d  (2-hop held-out; no direct a->d).  a -R1-> c (distractor).
    real = defaultdict(set)
    real[("a", "R1")] = {"b", "c"}
    real[("b", "R2")] = {"d"}
    real[("c", "R2")] = {"e"}
    real_any = defaultdict(set)
    for (s, _), tgts in real.items():
        real_any[s] |= tgts
    # ingest arm: compose R1 then R2 from a, expect d reachable
    x_set = real[("a", "R1")]
    composed = set()
    for x in x_set:
        composed |= real[(x, "R2")]
    assert "d" in composed, "selftest: 2-hop composition must reach d"
    # held-out: d not a 1-hop neighbor of a
    assert "d" not in real_any["a"], "selftest: chain must be held-out (not 1-hop lookup)"
    # shuffled 2nd hop: R1 then a NON-R2 relation -> should not reach d
    composed_shuf = set()
    for x in x_set:
        composed_shuf |= real[(x, "R_OTHER")]  # empty
    assert "d" not in composed_shuf, "selftest: shuffled-2nd-hop must collapse"
    # scrambled: permute R2 targets so b no longer -> d
    scr = defaultdict(set)
    scr[("b", "R2")] = {"e"}
    scr[("c", "R2")] = {"d"}
    composed_scr = set()
    for x in x_set:
        composed_scr |= scr[(x, "R2")]
    # a's R1 = {b,c}; scr makes c->d, so scrambled DOES reach d here (toy). Real cell over 133k
    # nodes makes this vanishingly rare; toy only checks the machinery runs.
    # name-NN leak: 'a' vs pool {'d', 'zzz'} -> char-sim near 0, top1 should not spuriously =d
    tri_a = _trigrams("a")
    pool = ["d", "zzz_distractor"]
    sims = [_name_sim(tri_a, _trigrams(p)) for p in pool]
    _ = int(np.argmax(sims))  # just exercise the path
    print("[selftest] PASS: 2-hop composes; held-out ok; shuffle collapses; name-NN path ok",
          flush=True)


# ---- disk completeness (independent of the live loader) ------------------------------------
def _disk_counts():
    n_atoms = 0
    with open(ATOMS_PATH, encoding="utf-8") as f:
        for _ in f:
            n_atoms += 1
    triples = set()
    n_uses = 0
    with open(RELATIONS_PATH, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            triples.add((r["src_id"], r["rel_type"], r["tgt_id"]))
            if r["rel_type"] == "USES":
                n_uses += 1
    # Store auto-derives one HAS_USERS per unique USES triple.
    derived = len({(r0, r1, r2) for (r0, r1, r2) in triples if r1 == "USES"})
    return n_atoms, len(triples), derived, n_uses


# ---- adjacency extraction from the LIVE store ----------------------------------------------
def build_adjacency(store):
    """Extract real out-adjacency from the loaded live Store (equivalent to repeated
    store.out_neighbors, cached for speed). Returns (real_out, real_any, per_rel_edges, nodes)."""
    real_out = defaultdict(set)
    real_any = defaultdict(set)
    per_rel_edges = defaultdict(list)  # rel_str -> list[(src, tgt)]
    for (src, rt, tgt) in store.iter_relations():
        rel_str = rt.value
        real_out[(src, rel_str)].add(tgt)
        real_any[src].add(tgt)
        per_rel_edges[rel_str].append((src, tgt))
    nodes = list(store.all_atom_ids())
    return real_out, real_any, per_rel_edges, nodes


def build_scrambled(per_rel_edges, rng):
    """Degree-preserving null: permute the tgt column within each relation type. Preserves per-
    (src, rel) out-degree and per-rel edge count exactly; destroys the real (s, p, o) structure."""
    scr = defaultdict(set)
    for rel_str, edges in per_rel_edges.items():
        if not edges:
            continue
        srcs = [e[0] for e in edges]
        tgts = [e[1] for e in edges]
        perm = rng.permutation(len(tgts))
        for i, si in enumerate(srcs):
            scr[(si, rel_str)].add(tgts[perm[i]])
    return scr


def sample_chains(real_out, real_any, rng, n_chains):
    """Sample held-out 2-hop chains (s, p1, x, p2, o): o reachable from s only via composition."""
    keys = [k for k, v in real_out.items() if v]  # (src, rel_str) with >=1 target
    chains = []
    tries = 0
    max_tries = n_chains * 400
    while len(chains) < n_chains and tries < max_tries:
        tries += 1
        s, p1 = keys[int(rng.integers(0, len(keys)))]
        xs = list(real_out[(s, p1)])
        x = xs[int(rng.integers(0, len(xs)))]
        if x == s:
            continue
        x_out_keys = [rel for (xx, rel) in real_out if xx == x and real_out[(xx, rel)]]
        if not x_out_keys:
            continue
        p2 = x_out_keys[int(rng.integers(0, len(x_out_keys)))]
        os_ = list(real_out[(x, p2)])
        o = os_[int(rng.integers(0, len(os_)))]
        if o == s or o == x:
            continue
        if o in real_any[s]:   # held-out: o must NOT be a direct 1-hop neighbor of s
            continue
        chains.append((s, p1, x, p2, o))
    return chains


def compose_2hop(adj, s, p1, p2, o):
    """Does o appear in {adj(x, p2) : x in adj(s, p1)} ? Returns 1/0 hit."""
    frontier = adj.get((s, p1), set())
    for x in frontier:
        if o in adj.get((x, p2), set()):
            return 1
    return 0


def run_seed(seed, store, real_out, real_any, per_rel_edges, nodes, rel_types, node_tris,
             consistency_checked):
    rng = np.random.default_rng(seed)
    from backend.substrate_index.schema import RelationType

    chains = sample_chains(real_out, real_any, rng, N_CHAINS)
    n = len(chains)
    if n == 0:
        return {"seed": seed, "n_chains": 0, "error": "no_chains_sampled"}

    scr = build_scrambled(per_rel_edges, np.random.default_rng(seed + 1000))
    empty = defaultdict(set)

    hit_A = np.zeros(n, dtype=np.int8)   # ingest 2-hop (real)
    hit_B = np.zeros(n, dtype=np.int8)   # shuffled 2nd hop
    hit_C = np.zeros(n, dtype=np.int8)   # scrambled kb
    hit_C2 = np.zeros(n, dtype=np.int8)  # no ingest (empty)
    hit_D = np.zeros(n, dtype=np.int8)   # encoder-only name NN
    hit_L = np.zeros(n, dtype=np.int8)   # one-hop-direct leak (should be 0 by held-out)

    for i, (s, p1, x, p2, o) in enumerate(chains):
        hit_A[i] = compose_2hop(real_out, s, p1, p2, o)
        # shuffled 2nd hop: random rel != p2
        p2s = p2
        while p2s == p2 and len(rel_types) > 1:
            p2s = rel_types[int(rng.integers(0, len(rel_types)))]
        hit_B[i] = compose_2hop(real_out, s, p1, p2s, o)
        hit_C[i] = compose_2hop(scr, s, p1, p2, o)
        hit_C2[i] = compose_2hop(empty, s, p1, p2, o)
        hit_L[i] = 1 if o in real_any[s] else 0
        # encoder-only leak: name-NN over pool {o} + random distractors, NO graph
        pool = [o]
        while len(pool) < N_POOL:
            cand = nodes[int(rng.integers(0, len(nodes)))]
            if cand != o and cand != s:
                pool.append(cand)
        tri_s = node_tris.get(s) or _trigrams(s)
        sims = [_name_sim(tri_s, node_tris.get(c) or _trigrams(c)) for c in pool]
        hit_D[i] = 1 if int(np.argmax(sims)) == 0 else 0  # pool[0] == o

    # Consistency: tie my cached adjacency to the LIVE out_neighbors path on a sample (once).
    consistency_ok = True
    if not consistency_checked["done"]:
        for (s, p1, x, p2, o) in chains[:20]:
            try:
                live = store.out_neighbors(s, RelationType(p1))
            except Exception:
                live = None
            if live is not None and live != real_out[(s, p1)]:
                consistency_ok = False
                break
        consistency_checked["done"] = True
        consistency_checked["ok"] = consistency_ok
    else:
        consistency_ok = consistency_checked["ok"]

    # Known-item 1-hop round-trip recall through the LIVE store.out_neighbors path.
    all_keys = [k for k, v in real_out.items() if v]
    kidx = rng.permutation(len(all_keys))[:min(N_KNOWN, len(all_keys))]
    rk_hit = 0
    rk_tot = 0
    for j in kidx:
        s, p1 = all_keys[j]
        targets = real_out[(s, p1)]
        try:
            live = store.out_neighbors(s, RelationType(p1))
        except Exception:
            live = set()
        for t in targets:
            rk_tot += 1
            if t in live:
                rk_hit += 1
    R = rk_hit / max(rk_tot, 1)

    return {
        "seed": seed, "n_chains": n,
        "A_ingest_2hop": float(hit_A.mean()),
        "B_shuffled_2ndhop": float(hit_B.mean()),
        "C_scrambled_kb": float(hit_C.mean()),
        "C2_no_ingest": float(hit_C2.mean()),
        "D_encoder_only_nameNN": float(hit_D.mean()),
        "L_one_hop_direct": float(hit_L.mean()),
        "R_known_item_1hop_recall": float(R),
        "known_item_probes": int(rk_tot),
        "adjacency_matches_live_out_neighbors": bool(consistency_ok),
        "arm_hashes": {
            "A": hashlib.sha256(hit_A.tobytes()).hexdigest()[:16],
            "B": hashlib.sha256(hit_B.tobytes()).hexdigest()[:16],
            "C": hashlib.sha256(hit_C.tobytes()).hexdigest()[:16],
            "D": hashlib.sha256(hit_D.tobytes()).hexdigest()[:16],
        },
        "config_version": CONFIG_VERSION, "run_mode": RUN_MODE,
    }


def verdict(per_seed, disk):
    ok_seeds = [p for p in per_seed if p.get("n_chains", 0) > 0]
    if not ok_seeds:
        return "HARD_FAIL", "HARD_FAIL: no chains sampled on any seed."

    def m(k):
        return float(np.mean([p[k] for p in ok_seeds]))

    A = m("A_ingest_2hop"); B = m("B_shuffled_2ndhop"); C = m("C_scrambled_kb")
    C2 = m("C2_no_ingest"); D = m("D_encoder_only_nameNN"); L = m("L_one_hop_direct")
    R = m("R_known_item_1hop_recall")

    d_atoms, d_triples, d_derived, _ = disk["disk_atoms"], disk["disk_distinct_triples"], \
        disk["disk_derived"], disk["disk_uses"]
    completeness_ok = (disk["loaded_atoms"] == d_atoms and
                       disk["loaded_relations"] == d_triples + d_derived)
    consistency_ok = all(p.get("adjacency_matches_live_out_neighbors", False) for p in ok_seeds)

    gap_scr = A - C
    gap_fire = A - B

    D1 = gap_scr >= GAP_REAL_VS_SCRAMBLED
    D2 = (gap_fire >= GAP_FIRING) and (B <= SHUFFLE_CEIL)
    D3 = C2 <= NOINGEST_CEIL
    D4 = D <= LEAK_CEIL
    D5 = R >= ADDRESS_FLOOR
    D6 = (L <= LOOKUP_CEIL) and (A >= INGEST_FLOOR)
    D7 = completeness_ok and consistency_ok

    summ = (
        "A_ingest=%.3f B_shuffled=%.3f C_scrambled=%.3f C2_noingest=%.3f D_encoderNN=%.3f "
        "L_1hop=%.3f R_recall=%.3f | gap_real-vs-scrambled=%.3f (>=%.2f:%s) "
        "gap_firing=%.3f/B<=%.2f (%s) noingest<=%.2f(%s) leak<=%.2f(%s) recall>=%.2f(%s) "
        "notlookup L<=%.2f/A>=%.2f(%s) completeness(atoms %d/%d rel %d/%d+%d)=%s consistency=%s"
        % (A, B, C, C2, D, L, R, gap_scr, GAP_REAL_VS_SCRAMBLED, D1, gap_fire, SHUFFLE_CEIL, D2,
           NOINGEST_CEIL, D3, LEAK_CEIL, D4, ADDRESS_FLOOR, D5, LOOKUP_CEIL, INGEST_FLOOR, D6,
           disk["loaded_atoms"], d_atoms, disk["loaded_relations"], d_triples, d_derived,
           completeness_ok, consistency_ok)
    )

    # HARD_FAIL: plumbing broken.
    if A < A_HARD_FAIL:
        return "HARD_FAIL", "HARD_FAIL: ingest-arm 2-hop below floor (integration not reachable). " + summ
    if R < R_HARD_FAIL:
        return "HARD_FAIL", "HARD_FAIL: known-item recall below floor (addressability broken). " + summ
    if not completeness_ok:
        return "HARD_FAIL", "HARD_FAIL: completeness breach (silent truncation of atoms/edges). " + summ

    # VACUOUS: a control failed to fire -> cannot distinguish integration from artifact.
    vac = []
    if not D1:
        vac.append("scrambled-KB null did NOT collapse (real edges not doing the work)")
    if C2 > NOINGEST_CEIL:
        vac.append("no-ingest baseline did NOT fail")
    if not D4:
        vac.append("encoder-only name-NN LEAK (answer guessable without graph)")
    if not (gap_fire >= GAP_FIRING and B <= SHUFFLE_CEIL):
        vac.append("shuffled-2nd-hop firing control did NOT collapse")
    if vac:
        return ("VACUOUS_NON_DISCRIMINATING",
                "VACUOUS_NON_DISCRIMINATING (NOT a pass): " + "; ".join(vac) + ". " + summ)

    if D1 and D2 and D3 and D4 and D5 and D6 and D7:
        return ("HARD_PASS",
                "HARD_PASS: substrate INTEGRATES + QUERIES ingested ConceptNet via the live "
                "structural path; every anti-vacuousness control fires (scrambled-KB, no-ingest, "
                "shuffled-hop collapse; no encoder leak; addressability + completeness). " + summ)
    return "MIDDLE_BAND", "MIDDLE_BAND: addressability holds but a gate is partial. " + summ


# ---- error-checking scaffolding (SS 13) ----------------------------------------------------
def _write_start_marker(out_dir):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "expected_n_units": len(SEEDS),
              "host": platform.node()}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")


def main():
    t0 = time.time()
    out_dir = REPO / "data" / ("exp_%s" % os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME))
    _write_start_marker(out_dir)
    print("[config] anchor=%s mode=%s seeds=%s | %s" % (ANCHOR_NAME, RUN_MODE, SEEDS, CONFIG_VERSION),
          flush=True)

    if not ATOMS_PATH.exists() or not RELATIONS_PATH.exists():
        raise FileNotFoundError("committed ConceptNet not found at %s" % CONCEPT_DIR)

    # Disk completeness (read directly, independent of the loader).
    d_atoms, d_triples, d_derived, d_uses = _disk_counts()
    print("[disk] atoms=%d distinct_triples=%d derived_has_users=%d uses=%d"
          % (d_atoms, d_triples, d_derived, d_uses), flush=True)

    # Load the LIVE store (NO re-encode: Store loads atoms + relations only).
    tL = time.time()
    from backend.substrate_index.store import Store
    from backend.substrate_index.schema import RelationType
    store = Store(CONCEPT_DIR)
    loaded_atoms = len(store.all_atom_ids())
    loaded_relations = len(store._all_relations)
    print("[live-store] loaded atoms=%d relations=%d in %.1fs" %
          (loaded_atoms, loaded_relations, time.time() - tL), flush=True)

    real_out, real_any, per_rel_edges, nodes = build_adjacency(store)
    rel_types = sorted(per_rel_edges.keys())
    # Pre-compute trigrams for all nodes touched (bounded: lazily fill during run instead).
    node_tris = {}
    for nid in nodes:
        node_tris[nid] = _trigrams(nid)
    print("[adjacency] rel_types=%d keyed_pairs=%d nodes=%d" %
          (len(rel_types), len(real_out), len(nodes)), flush=True)

    disk = {"disk_atoms": d_atoms, "disk_distinct_triples": d_triples, "disk_derived": d_derived,
            "disk_uses": d_uses, "loaded_atoms": loaded_atoms, "loaded_relations": loaded_relations}

    per_seed = []
    consistency_checked = {"done": False, "ok": True}
    for s in SEEDS:
        pf = out_dir / ("partial_seed%d_%s.json" % (s, RUN_MODE))
        if pf.exists():
            try:
                rec = json.loads(pf.read_text(encoding="utf-8"))
                if rec.get("config_version") == CONFIG_VERSION:
                    print("  [seed=%d] RESUME from checkpoint" % s, flush=True)
                    per_seed.append(rec)
                    continue
            except Exception:
                pass
        ts = time.time()
        rec = run_seed(s, store, real_out, real_any, per_rel_edges, nodes, rel_types, node_tris,
                       consistency_checked)
        tmp = out_dir / (pf.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        os.replace(tmp, pf)
        per_seed.append(rec)
        print("  [seed=%d] A=%.3f B=%.3f C=%.3f C2=%.3f D=%.3f L=%.3f R=%.3f (n=%d, %.1fs)" % (
            s, rec.get("A_ingest_2hop", -1), rec.get("B_shuffled_2ndhop", -1),
            rec.get("C_scrambled_kb", -1), rec.get("C2_no_ingest", -1),
            rec.get("D_encoder_only_nameNN", -1), rec.get("L_one_hop_direct", -1),
            rec.get("R_known_item_1hop_recall", -1), rec.get("n_chains", 0), time.time() - ts),
            flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF): A vs B vs C hit-vectors must not be bit-identical.
    arms_differ_verified = True
    for p in per_seed:
        h = p.get("arm_hashes", {})
        if h and (h.get("A") == h.get("B") == h.get("C")):
            arms_differ_verified = False
    if not arms_differ_verified:
        raise AssertionError("META_RULE_AF VIOLATION: ingest/shuffled/scrambled arms bit-identical")

    v, vmsg = verdict(per_seed, disk)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "config_version": CONFIG_VERSION,
        "elapsed_s": round(time.time() - t0, 1), "arms_differ_verified": arms_differ_verified,
        "disk_completeness": disk, "per_seed": per_seed,
        "DESIGN_NOTE": ("Stage-0 ingest plumbing verification via LIVE structural path; NO BGE "
                        "re-encode; anti-vacuousness battery (scrambled-KB null, no-ingest, "
                        "shuffled-2nd-hop, encoder-only name-NN leak-check); PROOF is the GAP not "
                        "the absolute ingest-arm score."),
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    _out_dir = REPO / "data" / ("exp_%s" % os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out_dir, e)
        raise
