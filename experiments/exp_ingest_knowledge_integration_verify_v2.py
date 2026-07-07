"""exp_ingest_knowledge_integration_verify_v2 -- gate-D hardening re-gate (ingest INTEGRITY).

Amends v1's encoder-only lexical-leak control (gate-D) in two independent ways, leaving every
structural arm (A ingest / B shuffled-hop / C scrambled-KB / C2 no-ingest / R known-item / L
one-hop) UNCHANGED. This is the ingest-INTEGRITY gate that must clear before any 970K scale.

Why: v1 FULL passed gate-D only on the MEAN (D=0.148 < 0.15 ceiling) while 2 of 3 seeds
individually EXCEEDED 0.15 (per-seed [0.130, 0.157, 0.157] MEASURED@v1 FULL). A mean that masks
2/3 seeds over the line is a Goodhart signature with zero scale headroom, and the leak GREW
smoke->full. Two fixes (both cheap, independent):

  Fix 1 (per-seed gate): gate on max-over-seeds of the hardened gate-D, NOT the mean. Report
         per-seed + max. Removes the mean-masking hole.
  Fix 2 (stronger anti-lexical pool): the v1 leak-check drew the encoder-only candidate pool from
         RANDOM nodes, so the name-NN arm only had to beat lexically UNRELATED names -- an easy bar
         that understates the true name-shortcut. Harden it: build the distractor pool from the
         answer entity o's NEAREST LEXICAL NEIGHBORS (char-trigram Jaccard on the entity name), so
         the arm must distinguish the true answer from names that LOOK alike. Pool size matches the
         v1 negative count (o + 199 distractors = 200) so the chance rate is unchanged; only the
         DIFFICULTY changes. This is the ConceptNet entity-name analog of Test-0's near-duplicate
         lexical-shortcut surface (Jaccard-0.96 doc chunks + WordNet polysemy): the harder
         distractors are drawn from lexical neighbors at the base rate.

Three D variants are computed in the SAME run:
  D_hard    hardened gate-D: pool = {o} + 199 lexical-neighbors of o; ranked by name-sim to s.
            THE GATED metric (per-seed max).
  D_random  v1 semantics: pool = {o} + 199 RANDOM nodes; same unbiased scoring. Same-run
            continuity comparison (reproduces the v1 0.148-ish leak; the "leak grew" reference).
  D_hardscr firing control: same hard pool, but the QUERY SOURCE name is replaced by a random
            node's name (name->code map shuffled on the source side). If D_hard measures a genuine
            s->o lexical shortcut (not a pool-construction artifact), D_hardscr MUST collapse to
            chance (~1/200 = 0.005).

Unbiased tie-break: pools are SHUFFLED before argmax and the answer's shuffled position is scored,
so lexically-identical lookalikes (common in the hard pool) do NOT bias the answer by its list
index. (v1 scored argmax==0 with the answer at index 0, which inflates on ties.)

Strategic read (Director + USER, 2026-07-07): if A holds while D_hard DROPS on the harder pool, the
A-D gap WIDENS => a STRONGER non-vacuousness proof than the v1 0.85 bound (good case). If D_hard
stays high, the ~15% name-shortcuttable fraction is genuinely real and we report the honest bounded
number. Either way we learn the TRUE value, not a mean-masked pass. re-encode HELD (committed
ConceptNet, zero new ingest, zero encoder forward calls); CPU-only graph adjacency + char-trigram.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on A/B/C + D-hashes)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: exact graph reachability + argmax over a bounded name-similarity pool; no continuous
#     noise floor (declared in prereg)
# - baseline_in_band: EXEMPTED -- null arms DESIGNED to sit at floor; discriminator is the GAP
# - discriminator survives scale: smoke loads the FULL committed graph (~142k nodes) and computes
#     lexical neighbors over the FULL node set; only the probe COUNT is reduced -> the leak fires at
#     true corpus scale in smoke (multi-seed smoke observes per-seed spread before FULL)
# - all numbers in comments/prereg tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
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

ANCHOR_NAME = "ingest_knowledge_integration_verify_v2"
CONCEPT_DIR = REPO / "data" / "substrate_index" / "concept"
ATOMS_PATH = CONCEPT_DIR / "atoms.jsonl"
RELATIONS_PATH = CONCEPT_DIR / "relations.jsonl"

# ---- Pre-reg bands (locked) ---------------------------------------------------------------
GAP_REAL_VS_SCRAMBLED = 0.50   # D1: A - C >= this
GAP_FIRING = 0.50              # D2: A - B >= this
SHUFFLE_CEIL = 0.15            # D2: B <= this
NOINGEST_CEIL = 0.05           # D3: C2 <= this
LEAK_CEIL = 0.15               # D4: hardened gate-D HARD-PASS ceiling (max-over-seeds < this)
LEAK_HARD_FAIL = 0.17          # D4: any seed >= this -> HARD_FAIL_LEXICAL_LEAK
ADDRESS_FLOOR = 0.98           # D5: R >= this
LOOKUP_CEIL = 0.05             # D6: L <= this
INGEST_FLOOR = 0.90            # D6: A >= this
A_HARD_FAIL = 0.50             # HARD_FAIL if A below this
R_HARD_FAIL = 0.80             # HARD_FAIL if R below this
FIRING_CEIL = 0.02             # firing control: D_hardscr must collapse to <= this (~4x chance 0.005)

# v1 FULL measured max-over-seeds of the RANDOM-pool leak (the "current FULL" reference).
# MEASURED@d:/AI/hd-instrument/data/exp_ingest_knowledge_integration_verify_v1/metrics.json
#   per_seed[*].D_encoder_only_nameNN = [0.1300, 0.1567, 0.1567] -> max 0.1567
CURRENT_FULL_MAX_D_RANDOM = 0.1567

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
    # Multi-seed smoke: this cell's WHOLE POINT is per-seed behavior, so smoke runs all 3 FULL
    # seeds at reduced chains to observe the per-seed max-gate spread before FULL (multi-seed
    # smoke-gate discipline for leak/contamination-style continuous-score discriminators).
    SEEDS = [7, 13, 23]
    N_CHAINS = 100
    N_KNOWN = 400
else:  # full
    SEEDS = [7, 13, 23]
    N_CHAINS = 300
    N_KNOWN = 2000

N_POOL = 200  # encoder-only leak-check pool size ({o} + 199 distractors); chance = 1/200 = 0.005

CONFIG_VERSION = (
    "ingest-integration-verify-v2 gate-D HARDENED: per-seed-max gate + name-similar (lexical-NN) "
    "distractor pool + shuffled-source firing-control; structural arms A/B/C/C2/R/L unchanged; "
    "mode=%s chains=%d known=%d pool=%d bands[D1>=%.2f D2>=%.2f/B<=%.2f D3<=%.2f "
    "D4:maxD<%.2f/failD>=%.2f/fire<=%.3f D5>=%.2f D6:L<=%.2f/A>=%.2f]"
    % (RUN_MODE, N_CHAINS, N_KNOWN, N_POOL, GAP_REAL_VS_SCRAMBLED, GAP_FIRING, SHUFFLE_CEIL,
       NOINGEST_CEIL, LEAK_CEIL, LEAK_HARD_FAIL, FIRING_CEIL, ADDRESS_FLOOR, LOOKUP_CEIL,
       INGEST_FLOOR)
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


# ---- lexical nearest-neighbor pool (Fix 2) -------------------------------------------------
def build_tri_index(nodes, node_tris):
    """Inverted index trigram -> np.array(node_idx). Built once over the FULL node set."""
    tri2nodes = defaultdict(list)
    for idx, nid in enumerate(nodes):
        for t in node_tris[nid]:
            tri2nodes[t].append(idx)
    tri2nodes = {t: np.asarray(v, dtype=np.int64) for t, v in tri2nodes.items()}
    node_tri_len = np.asarray([len(node_tris[nid]) for nid in nodes], dtype=np.int64)
    return tri2nodes, node_tri_len


def lex_neighbors(tri_o, len_o, tri2nodes, node_tri_len, counts_buf, k, exclude_idx):
    """Top-k node indices by char-trigram Jaccard to a query trigram-set, via the inverted index.
    counts_buf: reusable int32 zero buffer sized len(nodes); reset to 0 for touched entries here."""
    touched = []
    for t in tri_o:
        arr = tri2nodes.get(t)
        if arr is not None:
            counts_buf[arr] += 1
            touched.append(arr)
    if not touched:
        return np.empty(0, dtype=np.int64)
    cand = np.unique(np.concatenate(touched))
    inter = counts_buf[cand].astype(np.float64)
    counts_buf[cand] = 0  # reset only touched entries (keep buffer zeroed for next call)
    denom = float(len_o) + node_tri_len[cand].astype(np.float64) - inter
    jac = np.where(denom > 0, inter / denom, 0.0)
    if exclude_idx:
        keep = ~np.isin(cand, np.asarray(list(exclude_idx), dtype=np.int64))
        cand = cand[keep]
        jac = jac[keep]
    if cand.size == 0:
        return np.empty(0, dtype=np.int64)
    if cand.size <= k:
        return cand[np.argsort(-jac)]
    part = np.argpartition(-jac, k)[:k]
    return cand[part[np.argsort(-jac[part])]]


def _pool_hit(sim_query_tris, pool_ids, o_pos, node_tris):
    """1 if the pool member most name-similar to sim_query_tris is the answer (at o_pos)."""
    sims = np.asarray([_name_sim(sim_query_tris, node_tris[c]) for c in pool_ids])
    return 1 if int(np.argmax(sims)) == o_pos else 0


# ---- self-test: toy graph + concrete hard-pool / firing-control assertions ------------------
def _selftest():
    # (a) structural machinery: 2-hop composes; held-out; shuffle + scramble behave.
    real = defaultdict(set)
    real[("a", "R1")] = {"b", "c"}
    real[("b", "R2")] = {"d"}
    real[("c", "R2")] = {"e"}
    real_any = defaultdict(set)
    for (s, _), tgts in real.items():
        real_any[s] |= tgts
    composed = set()
    for x in real[("a", "R1")]:
        composed |= real[(x, "R2")]
    assert "d" in composed, "selftest: 2-hop composition must reach d"
    assert "d" not in real_any["a"], "selftest: chain must be held-out (not 1-hop lookup)"

    # (b) HARD POOL is harder than RANDOM POOL (Fix 2, concrete case).
    #   s and o share the token 'quartz'. RANDOM distractors are lexically unrelated -> o wins.
    #   HARD distractor 'quartz_clocking' shares 'quartz'+'clock' with s (MORE than o does) -> the
    #   lookalike wins, so the hardened arm does NOT shortcut to o here.
    s_name = "CN_quartz_clock"
    o_name = "CN_quartz_ring"
    tri_s = _trigrams(s_name)
    node_tris = {
        o_name: _trigrams(o_name),
        "CN_wooden_chair": _trigrams("CN_wooden_chair"),
        "CN_metal_spoon": _trigrams("CN_metal_spoon"),
        "CN_quartz_clocking": _trigrams("CN_quartz_clocking"),
    }
    rnd_pool = [o_name, "CN_wooden_chair", "CN_metal_spoon"]
    hard_pool = [o_name, "CN_quartz_clocking", "CN_wooden_chair"]
    hit_rnd = _pool_hit(tri_s, rnd_pool, 0, node_tris)
    hit_hard = _pool_hit(tri_s, hard_pool, 0, node_tris)
    assert hit_rnd == 1, "selftest: answer must win the RANDOM pool (o closer to s than junk)"
    assert hit_hard == 0, ("selftest: hardened pool must defeat the name-shortcut when a lookalike "
                           "is closer to s than the answer (got hit_hard=1)")

    # (c) FIRING CONTROL collapses to chance under a total-tie pool + shuffled source.
    #   Pool = answer + (K-1) lookalikes with IDENTICAL trigram sets; every random source has sim=0
    #   to all -> full tie -> shuffle+argmax is uniform over K -> hit-rate ~ 1/K, NOT biased to o.
    K = 50
    ident = _trigrams("CN_zzq_ident_token")   # all pool members share this exact name -> equal sim
    unrelated = _trigrams("CN_xxvv_unrelated")  # a source lexically disjoint from the pool
    ntris = {("P%d" % j): ident for j in range(K)}
    rng = np.random.default_rng(999)
    hits = 0
    T = 4000
    for _ in range(T):
        pool = ["P%d" % j for j in range(K)]
        order = rng.permutation(K)
        pool = [pool[j] for j in order]
        o_pos = int(np.where(order == 0)[0][0])  # original answer P0 landed here after shuffle
        hits += _pool_hit(unrelated, pool, o_pos, ntris)
    rate = hits / T
    chance = 1.0 / K
    assert abs(rate - chance) < 0.010, (
        "selftest: firing control must collapse to chance %.3f, got %.3f (tie-break biased?)"
        % (chance, rate))

    print("[selftest] PASS: 2-hop composes + held-out; RANDOM pool leaks(1) but HARD pool "
          "defeats(0) the name-shortcut; firing control collapses to chance %.3f (measured %.3f)"
          % (chance, rate), flush=True)


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
    derived = len({(r0, r1, r2) for (r0, r1, r2) in triples if r1 == "USES"})
    return n_atoms, len(triples), derived, n_uses


# ---- adjacency extraction from the LIVE store ----------------------------------------------
def build_adjacency(store):
    real_out = defaultdict(set)
    real_any = defaultdict(set)
    per_rel_edges = defaultdict(list)
    for (src, rt, tgt) in store.iter_relations():
        rel_str = rt.value
        real_out[(src, rel_str)].add(tgt)
        real_any[src].add(tgt)
        per_rel_edges[rel_str].append((src, tgt))
    nodes = list(store.all_atom_ids())
    return real_out, real_any, per_rel_edges, nodes


def build_scrambled(per_rel_edges, rng):
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
    keys = [k for k, v in real_out.items() if v]
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
        if o in real_any[s]:
            continue
        chains.append((s, p1, x, p2, o))
    return chains


def compose_2hop(adj, s, p1, p2, o):
    frontier = adj.get((s, p1), set())
    for x in frontier:
        if o in adj.get((x, p2), set()):
            return 1
    return 0


def run_seed(seed, store, real_out, real_any, per_rel_edges, nodes, node_index, rel_types,
             node_tris, tri2nodes, node_tri_len, consistency_checked):
    rng = np.random.default_rng(seed)
    from backend.substrate_index.schema import RelationType

    chains = sample_chains(real_out, real_any, rng, N_CHAINS)
    n = len(chains)
    if n == 0:
        return {"seed": seed, "n_chains": 0, "error": "no_chains_sampled"}

    scr = build_scrambled(per_rel_edges, np.random.default_rng(seed + 1000))
    empty = defaultdict(set)
    counts_buf = np.zeros(len(nodes), dtype=np.int32)  # reusable NN accumulator (kept zeroed)

    hit_A = np.zeros(n, dtype=np.int8)
    hit_B = np.zeros(n, dtype=np.int8)
    hit_C = np.zeros(n, dtype=np.int8)
    hit_C2 = np.zeros(n, dtype=np.int8)
    hit_L = np.zeros(n, dtype=np.int8)
    hit_Dhard = np.zeros(n, dtype=np.int8)    # hardened gate-D (lexical-NN pool) -- THE GATED metric
    hit_Drand = np.zeros(n, dtype=np.int8)    # v1 semantics (random pool), same-run continuity
    hit_Dscr = np.zeros(n, dtype=np.int8)     # firing control (hard pool, shuffled source)
    n_lex_avail = np.zeros(n, dtype=np.int32)  # #lexical neighbors found (<199 => padded random)

    n_nodes = len(nodes)
    for i, (s, p1, x, p2, o) in enumerate(chains):
        hit_A[i] = compose_2hop(real_out, s, p1, p2, o)
        p2s = p2
        while p2s == p2 and len(rel_types) > 1:
            p2s = rel_types[int(rng.integers(0, len(rel_types)))]
        hit_B[i] = compose_2hop(real_out, s, p1, p2s, o)
        hit_C[i] = compose_2hop(scr, s, p1, p2, o)
        hit_C2[i] = compose_2hop(empty, s, p1, p2, o)
        hit_L[i] = 1 if o in real_any[s] else 0

        si = node_index[s]
        oi = node_index[o]
        tri_s = node_tris[s]
        tri_o = node_tris[o]

        # --- Fix 2: hardened lexical-neighbor pool for o ---
        neigh = lex_neighbors(tri_o, len(tri_o), tri2nodes, node_tri_len, counts_buf,
                              N_POOL - 1, {si, oi})
        n_lex_avail[i] = int(neigh.size)
        hard_ids = [o]
        seen = {oi, si}
        for idx in neigh.tolist():
            if len(hard_ids) >= N_POOL:
                break
            if idx in seen:
                continue
            hard_ids.append(nodes[idx])
            seen.add(idx)
        while len(hard_ids) < N_POOL:  # pad with random if <199 lexical neighbors exist
            ridx = int(rng.integers(0, n_nodes))
            if ridx in seen:
                continue
            hard_ids.append(nodes[ridx])
            seen.add(ridx)

        # --- v1 random pool (same-run continuity) ---
        rand_ids = [o]
        rseen = {oi, si}
        while len(rand_ids) < N_POOL:
            ridx = int(rng.integers(0, n_nodes))
            if ridx in rseen:
                continue
            rand_ids.append(nodes[ridx])
            rseen.add(ridx)

        # Unbiased tie-break: shuffle each pool, score the answer's shuffled position.
        hp = np.asarray(hard_ids, dtype=object)
        ord_h = rng.permutation(N_POOL)
        hp = hp[ord_h]
        o_pos_h = int(np.where(ord_h == 0)[0][0])  # answer was at index 0 pre-shuffle
        hit_Dhard[i] = _pool_hit(tri_s, list(hp), o_pos_h, node_tris)

        # firing control: replace source name with a random node's name (name->code map shuffled).
        s_scr = si
        while s_scr == si or s_scr == oi:
            s_scr = int(rng.integers(0, n_nodes))
        hit_Dscr[i] = _pool_hit(node_tris[nodes[s_scr]], list(hp), o_pos_h, node_tris)

        rp = np.asarray(rand_ids, dtype=object)
        ord_r = rng.permutation(N_POOL)
        rp = rp[ord_r]
        o_pos_r = int(np.where(ord_r == 0)[0][0])
        hit_Drand[i] = _pool_hit(tri_s, list(rp), o_pos_r, node_tris)

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
        "D_hard_lexNN": float(hit_Dhard.mean()),            # GATED gate-D (per-seed)
        "D_random_pool": float(hit_Drand.mean()),           # v1 continuity
        "D_hard_scrambled_src": float(hit_Dscr.mean()),     # firing control
        "L_one_hop_direct": float(hit_L.mean()),
        "R_known_item_1hop_recall": float(R),
        "mean_lex_neighbors_available": float(n_lex_avail.mean()),
        "known_item_probes": int(rk_tot),
        "adjacency_matches_live_out_neighbors": bool(consistency_ok),
        "arm_hashes": {
            "A": hashlib.sha256(hit_A.tobytes()).hexdigest()[:16],
            "B": hashlib.sha256(hit_B.tobytes()).hexdigest()[:16],
            "C": hashlib.sha256(hit_C.tobytes()).hexdigest()[:16],
            "Dhard": hashlib.sha256(hit_Dhard.tobytes()).hexdigest()[:16],
            "Drand": hashlib.sha256(hit_Drand.tobytes()).hexdigest()[:16],
            "Dscr": hashlib.sha256(hit_Dscr.tobytes()).hexdigest()[:16],
        },
        "config_version": CONFIG_VERSION, "run_mode": RUN_MODE,
    }


def verdict(per_seed, disk):
    ok_seeds = [p for p in per_seed if p.get("n_chains", 0) > 0]
    if not ok_seeds:
        return "HARD_FAIL", "HARD_FAIL: no chains sampled on any seed."

    def m(k):
        return float(np.mean([p[k] for p in ok_seeds]))

    def mx(k):
        return float(np.max([p[k] for p in ok_seeds]))

    A = m("A_ingest_2hop"); B = m("B_shuffled_2ndhop"); C = m("C_scrambled_kb")
    C2 = m("C2_no_ingest"); L = m("L_one_hop_direct"); R = m("R_known_item_1hop_recall")
    Dhard_seeds = [p["D_hard_lexNN"] for p in ok_seeds]
    Dhard_max = mx("D_hard_lexNN"); Dhard_mean = m("D_hard_lexNN")
    Drand_max = mx("D_random_pool"); Drand_mean = m("D_random_pool")
    fire = m("D_hard_scrambled_src"); fire_max = mx("D_hard_scrambled_src")

    d_atoms, d_triples, d_derived = disk["disk_atoms"], disk["disk_distinct_triples"], \
        disk["disk_derived"]
    completeness_ok = (disk["loaded_atoms"] == d_atoms and
                       disk["loaded_relations"] == d_triples + d_derived)
    consistency_ok = all(p.get("adjacency_matches_live_out_neighbors", False) for p in ok_seeds)

    gap_scr = A - C
    gap_fire = A - B
    gap_ad = A - Dhard_max  # honest non-vacuousness gap on the HARDER pool (worst-seed)

    D1 = gap_scr >= GAP_REAL_VS_SCRAMBLED
    D2 = (gap_fire >= GAP_FIRING) and (B <= SHUFFLE_CEIL)
    D3 = C2 <= NOINGEST_CEIL
    D5 = R >= ADDRESS_FLOOR
    D6 = (L <= LOOKUP_CEIL) and (A >= INGEST_FLOOR)
    D7 = completeness_ok and consistency_ok

    # Hardened gate-D (Fix 1 per-seed + Fix 2 hard pool), with firing control.
    firing_ok = fire <= FIRING_CEIL
    leak_grew = Dhard_max > CURRENT_FULL_MAX_D_RANDOM
    any_seed_fail = any(d >= LEAK_HARD_FAIL for d in Dhard_seeds)
    D4_hardpass = (Dhard_max < LEAK_CEIL) and firing_ok
    D4_hardfail = firing_ok and (any_seed_fail or leak_grew)

    summ = (
        "A=%.3f B=%.3f C=%.3f C2=%.3f L=%.3f R=%.3f | "
        "D_hard per-seed=%s max=%.4f mean=%.4f | D_random max=%.4f mean=%.4f | "
        "firing(scrambled-src) mean=%.4f max=%.4f (<=%.3f:%s) | "
        "gap_real-vs-scrambled=%.3f(>=%.2f:%s) gap_firing=%.3f/B<=%.2f(%s) noingest<=%.2f(%s) "
        "recall>=%.2f(%s) notlookup L<=%.2f/A>=%.2f(%s) | A-D_hard(worst)=%.3f | "
        "v1_ref_max_D_random=%.4f leak_grew=%s | completeness(atoms %d/%d rel %d/%d+%d)=%s consist=%s"
        % (A, B, C, C2, L, R,
           ["%.4f" % d for d in Dhard_seeds], Dhard_max, Dhard_mean, Drand_max, Drand_mean,
           fire, fire_max, FIRING_CEIL, firing_ok,
           gap_scr, GAP_REAL_VS_SCRAMBLED, D1, gap_fire, SHUFFLE_CEIL, D2, NOINGEST_CEIL, D3,
           ADDRESS_FLOOR, D5, LOOKUP_CEIL, INGEST_FLOOR, D6, gap_ad, CURRENT_FULL_MAX_D_RANDOM,
           leak_grew, disk["loaded_atoms"], d_atoms, disk["loaded_relations"], d_triples,
           d_derived, completeness_ok, consistency_ok)
    )

    # HARD_FAIL: plumbing broken.
    if A < A_HARD_FAIL:
        return "HARD_FAIL", "HARD_FAIL: ingest-arm 2-hop below floor. " + summ
    if R < R_HARD_FAIL:
        return "HARD_FAIL", "HARD_FAIL: known-item recall below floor (addressability broken). " + summ
    if not completeness_ok:
        return "HARD_FAIL", "HARD_FAIL: completeness breach (silent truncation). " + summ

    # VACUOUS: a structural control failed to fire OR the firing control did not collapse.
    vac = []
    if not D1:
        vac.append("scrambled-KB null did NOT collapse")
    if C2 > NOINGEST_CEIL:
        vac.append("no-ingest baseline did NOT fail")
    if not (gap_fire >= GAP_FIRING and B <= SHUFFLE_CEIL):
        vac.append("shuffled-2nd-hop firing control did NOT collapse")
    if not firing_ok:
        vac.append("hardened gate-D FIRING CONTROL did NOT collapse to chance (scrambled-source "
                   "mean=%.4f > %.3f) -> the hard pool may carry a NON-lexical artifact; D_hard "
                   "cannot be trusted" % (fire, FIRING_CEIL))
    if vac:
        return ("VACUOUS_NON_DISCRIMINATING",
                "VACUOUS_NON_DISCRIMINATING (NOT a pass): " + "; ".join(vac) + ". " + summ)

    # Hardened gate-D outcome (firing control has already passed here).
    if D4_hardfail:
        why = []
        if any_seed_fail:
            why.append("a seed D_hard >= %.2f" % LEAK_HARD_FAIL)
        if leak_grew:
            why.append("max D_hard %.4f > current-FULL random-pool max %.4f (leak did not shrink "
                       "on the harder pool)" % (Dhard_max, CURRENT_FULL_MAX_D_RANDOM))
        msg = ("HARD_FAIL_LEXICAL_LEAK: the name-shortcuttable fraction is REAL at scale (%s). "
               "Core integration is still CHAIN_GRADE (A-C=%.3f) but the honest leak bound has no "
               "scale headroom; a relation-only readout path is needed before naive 970K scale. "
               % ("; ".join(why), gap_scr)) + summ
        return "HARD_FAIL_LEXICAL_LEAK", msg

    if D4_hardpass and D1 and D2 and D3 and D5 and D6 and D7:
        msg = ("HARD_PASS: hardened per-seed gate-D holds on the name-similar pool (max D_hard "
               "%.4f < %.2f, EVERY seed), firing control collapses to chance, and the A-D gap "
               "WIDENS on the harder pool (worst-seed A-D=%.3f). Substrate INTEGRATES + QUERIES "
               "ingested ConceptNet via the live structural path; the ~%.0f%% name-shortcut bound "
               "is TIGHTER than v1. " % (Dhard_max, LEAK_CEIL, gap_ad, 100 * Dhard_max)) + summ
        return "HARD_PASS", msg

    # 0.15 <= max D_hard < 0.17 and did not grow: honest bounded non-vacuousness (not a clean pass).
    msg = ("MIDDLE_BAND: hardened per-seed gate-D is in the honest-bounded band (max D_hard %.4f "
           "in [%.2f, %.2f), did not grow vs current FULL). The name-shortcuttable fraction ~%.0f%% "
           "is a REAL bounded number: non-vacuousness ~%.2f is the honest ceiling at this scale, "
           "not a mean-masked pass. " % (Dhard_max, LEAK_CEIL, LEAK_HARD_FAIL, 100 * Dhard_max,
                                         1.0 - Dhard_max)) + summ
    return "MIDDLE_BAND", msg


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

    d_atoms, d_triples, d_derived, d_uses = _disk_counts()
    print("[disk] atoms=%d distinct_triples=%d derived_has_users=%d uses=%d"
          % (d_atoms, d_triples, d_derived, d_uses), flush=True)

    tL = time.time()
    from backend.substrate_index.store import Store
    store = Store(CONCEPT_DIR)
    loaded_atoms = len(store.all_atom_ids())
    loaded_relations = len(store._all_relations)
    print("[live-store] loaded atoms=%d relations=%d in %.1fs" %
          (loaded_atoms, loaded_relations, time.time() - tL), flush=True)

    real_out, real_any, per_rel_edges, nodes = build_adjacency(store)
    rel_types = sorted(per_rel_edges.keys())
    node_index = {nid: i for i, nid in enumerate(nodes)}
    node_tris = {nid: _trigrams(nid) for nid in nodes}
    tI = time.time()
    tri2nodes, node_tri_len = build_tri_index(nodes, node_tris)
    print("[adjacency] rel_types=%d keyed_pairs=%d nodes=%d | tri_index=%d trigrams in %.1fs" %
          (len(rel_types), len(real_out), len(nodes), len(tri2nodes), time.time() - tI), flush=True)

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
        rec = run_seed(s, store, real_out, real_any, per_rel_edges, nodes, node_index, rel_types,
                       node_tris, tri2nodes, node_tri_len, consistency_checked)
        tmp = out_dir / (pf.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        os.replace(tmp, pf)
        per_seed.append(rec)
        print("  [seed=%d] A=%.3f B=%.3f C=%.3f C2=%.3f Dhard=%.4f Drand=%.4f Dscr=%.4f L=%.3f "
              "R=%.3f lexNN_avail=%.1f (n=%d, %.1fs)" % (
            s, rec.get("A_ingest_2hop", -1), rec.get("B_shuffled_2ndhop", -1),
            rec.get("C_scrambled_kb", -1), rec.get("C2_no_ingest", -1),
            rec.get("D_hard_lexNN", -1), rec.get("D_random_pool", -1),
            rec.get("D_hard_scrambled_src", -1), rec.get("L_one_hop_direct", -1),
            rec.get("R_known_item_1hop_recall", -1), rec.get("mean_lex_neighbors_available", -1),
            rec.get("n_chains", 0), time.time() - ts), flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF): ingest vs nulls vs the 3 D-variants must not be bit-identical.
    arms_differ_verified = True
    for p in per_seed:
        h = p.get("arm_hashes", {})
        if h and (h.get("A") == h.get("B") == h.get("C")):
            arms_differ_verified = False
        # the hardened D must differ from the random-pool D (else Fix 2 did nothing).
        if h and h.get("Dhard") == h.get("Drand") and p.get("D_hard_lexNN") == p.get("D_random_pool"):
            # allow identical ONLY if both are exactly 0 (degenerate tiny-n); else flag.
            if p.get("D_hard_lexNN", -1) not in (0.0,):
                arms_differ_verified = False
    if not arms_differ_verified:
        raise AssertionError("META_RULE_AF VIOLATION: arm hit-vectors bit-identical (structural "
                             "arms collapsed OR hardened-D == random-D; Fix 2 not exercised)")

    v, vmsg = verdict(per_seed, disk)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "config_version": CONFIG_VERSION,
        "elapsed_s": round(time.time() - t0, 1), "arms_differ_verified": arms_differ_verified,
        "disk_completeness": disk, "per_seed": per_seed,
        "gate_d_hardening": {
            "fix1_per_seed_max_gate": True, "fix2_lexical_neighbor_pool": True,
            "leak_ceil": LEAK_CEIL, "leak_hard_fail": LEAK_HARD_FAIL, "firing_ceil": FIRING_CEIL,
            "current_full_max_d_random_ref": CURRENT_FULL_MAX_D_RANDOM,
            "d_hard_max_over_seeds": (float(np.max([p["D_hard_lexNN"] for p in per_seed
                                                    if p.get("n_chains", 0) > 0]))
                                      if any(p.get("n_chains", 0) > 0 for p in per_seed) else None),
        },
        "DESIGN_NOTE": ("v2 gate-D hardening (ingest INTEGRITY gate before 970K scale): Fix1 per-seed "
                        "max gate (no mean masking); Fix2 name-similar lexical-neighbor distractor "
                        "pool + shuffled-source firing control; structural arms A/B/C/C2/R/L "
                        "UNCHANGED from v1. PROOF is the A-D gap on the HARDER pool."),
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
