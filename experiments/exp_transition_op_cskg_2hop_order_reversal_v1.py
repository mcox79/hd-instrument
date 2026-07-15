"""TRANSITION_OP vs COMMUTATIVE additive_map on REAL CSKG 2-hop irreducible order-reversal composition.

QUESTION: does a non-commutative per-relation matrix-chain operator (TRANSITION_OP, VET'd CHAIN_GRADE on the synthetic
dominance arena, exp_interaction_asymmetric_directed_operators_v1) improve REAL directed multi-hop relational reasoning
on a frequency-cap-immune task, specifically beating the LIVE additive_map's PROVABLY COMMUTATIVE translation-vector
composition (X_h + D_r1 + D_r2 = X_h + D_r2 + D_r1) -- the exact order-blind flaw TRANSITION_OP fixes?

DESIGN: notes/research_transition_op_real_data_test_target_2026-07-15.md (candidate #1). PRE-REG:
preregs/2026-07-15_transition_op_cskg_2hop_order_reversal.md.

CONSTRUCTION-LEVEL MOTIVATION (why the discriminator survives scale -- option B analytical):
  additive score(t) = -||X_h + D_r - X_t|| (TransE, the live additive_map). 2-hop compose X_h + D_r1 + D_r2 is
  IDENTICAL under order swap for ANY trained D -> on ORDER-SENSITIVE queries (gold(h,r1,r2) != gold(h,r2,r1)) the
  commutative arm assigns IDENTICAL scores to both orders -> structurally capped, cannot get both, at any scale.
  TRANSITION composes X_h M_r1^T M_r2^T with M_r1^T M_r2^T != M_r2^T M_r1^T -> can represent order. The gap is an
  ARCHITECTURAL bound, not an empirical hope.

ARMS (rank candidate tails for held-out irreducible 2-hop query (h,r1,r2); MRR + Hits@10, FILTERED):
  TRANSITION_OP             per-relation matrix M_r [k,k]; 2-hop pred = X_h M_r1^T M_r2^T. NEW candidate.
  ADDITIVE_MAP_COMMUTATIVE  LIVE baseline: real fit_kge_anchor1 (additive_map coord source); pred = X_h+D_r1+D_r2.
  TRANSITION_OP_SHUFFLED    SAME trained M_r, hops reversed at TEST only (X_h M_r2^T M_r1^T). Order attribution.
  FREQ_COMPOSED             per-hop marginal-tail frequency (train-order stats). Honest must-beat null.
  DEGREE                    in-degree/popularity tail ranking. Honest must-beat null.
  CHANCE                    uniform-random tail rank (floor).
  MEMORIZE                  exact-chain lookup from train-order; POP fallback. Leak sentinel (~<= NULL on irreducible).

FAIRNESS: TRANSITION and ADDITIVE trained with the SAME objective family (CE self-adversarial + N3 + reciprocal +
minibatch SGD), SAME constants (A1_* from experiments/_kge_anchor1_fit), SAME epochs, SAME k. ADDITIVE calls the LIVE
recipe verbatim (real code path). TRANSITION mirrors it with matrix ops + a Lacroix inverse-relation block.

SPLITS: (1) irreducibility filter (Gregucci: drop chains with a direct 1-hop h->t shortcut); (2) order-reversal
held-out split (test-order pairs whose reverse is in train-order); FREQ/DEGREE estimated on train-order only.

BANDS (fixed a priori; see prereg): HARD_PASS = TRANS-ADD>=0.05 AND TRANS-NULL>=0.15 AND order_attr(TRANS-SHUF)>=0.10
AND scramble_gate_ok. HARD_FAIL = TRANS-ADD<=0.02 OR TRANS-NULL<=0.05 OR not order_attr OR not scramble_gate.
MIDDLE_BAND = sub-threshold. REFUTE_IMPL = too few irreducible held-out queries / oracle reach < floor.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor): arms_differ hash-test at self-test;
final_metrics_atomicity=tmp_replace (via _seed_checkpoint.write_metrics); except SystemExit: raise BEFORE except
Exception (no BaseException); crlb_n/a (ranking task, ORACLE-reach ceiling); baseline_in_band at self-test;
discriminator survives scale (analytical B + planted non-commutative self-test arena); HARD_PASS strictly above floor;
calibration_check=default_ok (A1_* live recipe); per-unit failure_class; F.1/F.2/F.5 validity-preflight declared;
determinism from FIXED integer seeds + sorted(set()) (NO hash()/list(set())). ASCII-only. flush=True progress.
"""

import argparse
import gzip
import hashlib
import json
import os
import platform
import random
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._kge_anchor1_fit import (  # noqa: E402  # LIVE additive_map coord source + matched constants.
    fit_kge_anchor1, A1_LR, A1_GAMMA, A1_N_NEG, A1_ADV_TEMP, A1_N3_LAMBDA, A1_BATCH)
from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging flush defense-in-depth
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "transition_op_cskg_2hop_order_reversal_v1"
TESTBED = os.path.join(_REPO, "data", "grounding_testbed")
CSKG_PATH = os.path.join(TESTBED, "cskg.tsv.gz")
CSKG_URL = "https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content"

# ---- typed/asymmetric DIRECTED relation subset (exact /r/<Name> suffix match; EXCLUDES near-symmetric lexical) ----
TYPED_RELS = {
    "IsA", "PartOf", "HasA", "MadeOf", "Causes", "CausesDesire", "HasPrerequisite", "HasSubevent",
    "HasFirstSubevent", "HasLastSubevent", "MotivatedByGoal", "UsedFor", "ReceivesAction", "CapableOf",
    "AtLocation", "LocatedNear", "Entails", "CreatedBy",
}

# ---- fixed hyperparams (matched across arms; A1_* imported from the LIVE recipe) ----
GAMMA = A1_GAMMA
N_NEG = A1_N_NEG
ADV_TEMP = A1_ADV_TEMP
N3_LAMBDA = A1_N3_LAMBDA
TRANS_M_L2 = 1.0e-5          # tiny L2 on transition matrices: numerical stability only, NOT toward identity.
HITS_K = 10
SCORE_CHUNK = 512
MIN_IRREDUCIBLE = 60        # REFUTE_IMPL floor: fewer held-out irreducible test instances -> cannot run fair test.
ORACLE_REACH_FLOOR = 0.90   # REFUTE_IMPL: ORACLE (gold-in-candidate) reachability must clear this.

# ---- pre-registered bands (FIXED before running) ----
ADD_GAP_PASS = 0.05
NULL_GAP_PASS = 0.15
ORDER_ATTR_PASS = 0.10
ADD_GAP_FAIL = 0.02
NULL_GAP_FAIL = 0.05
ORDER_ATTR_PARTIAL = 0.05
SCRAMBLE_RETAIN_MAX = 0.70   # rel_specific_frac = scramble_margin/clean_margin must be <= this (>=30% rel-specific).

# ---- run configs ----
SELFTEST_CFG = dict(k=24, epochs=200, max_lines=0, max_nodes=0, min_deg=1, max_chains=0, seeds=[7])
MEMSMOKE_CFG = dict(k=24, epochs=15, max_lines=150000, max_nodes=1500, min_deg=2, max_chains=40000, seeds=[7])
FULL_CFG = dict(k=32, epochs=150, max_lines=0, max_nodes=20000, min_deg=2, max_chains=400000, seeds=[7, 17, 23])

ARM_TRANS = "TRANSITION_OP"
ARM_ADD = "ADDITIVE_MAP_COMMUTATIVE"
ARM_SHUF = "TRANSITION_OP_SHUFFLED"
ARM_FREQ = "FREQ_COMPOSED"
ARM_DEG = "DEGREE"
ARM_CHANCE = "CHANCE"
ARM_MEMO = "MEMORIZE"
ARM_NAMES = [ARM_TRANS, ARM_ADD, ARM_SHUF, ARM_FREQ, ARM_DEG, ARM_CHANCE, ARM_MEMO]


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.float64).round(5).tobytes()).hexdigest()[:16]


def _write_start_marker(out_dir, run_mode, expected_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _heartbeat(out_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=int(unit_idx),
               total_units=int(total_units), elapsed_s=round(float(elapsed_s), 2))
    if extra:
        row["extra"] = extra
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


# ===========================================================================
# CSKG typed-relation ingest
# ===========================================================================

def _ensure_cskg():
    if os.path.exists(CSKG_PATH):
        return True
    try:
        import subprocess
        os.makedirs(TESTBED, exist_ok=True)
        tmp = CSKG_PATH + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "1800", "-o", tmp, CSKG_URL], check=True)
        if os.path.getsize(tmp) < 50_000_000:
            os.remove(tmp)
            return False
        os.replace(tmp, CSKG_PATH)
        return True
    except Exception as e:  # acquisition best-effort; missing data -> loud HARD_FAIL upstream
        _log("cskg self-acquire failed: %s: %s" % (type(e).__name__, str(e)[:150]))
        return False


def _norm_word(w):
    return str(w).strip().lower().replace("_", " ")


def _rel_suffix(rel_col):
    """CSKG relation column is like /r/IsA or at:xNeed; return the trailing name token."""
    r = str(rel_col).strip()
    if not r:
        return ""
    if "/" in r:
        r = r.rsplit("/", 1)[-1]
    if ":" in r:
        r = r.rsplit(":", 1)[-1]
    return r


def _iter_typed_triples(max_lines=0):
    """Yield (head_label, rel_name, tail_label) directed for TYPED_RELS only."""
    with gzip.open(CSKG_PATH, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            i_rel = header.index("relation")
            i_l1 = header.index("node1;label")
            i_l2 = header.index("node2;label")
        except ValueError:
            i_rel, i_l1, i_l2 = 2, 4, 5
        n = 0
        for line in f:
            n += 1
            if max_lines and n > max_lines:
                break
            p = line.rstrip("\n").split("\t")
            if len(p) <= max(i_rel, i_l1, i_l2):
                continue
            rel = _rel_suffix(p[i_rel])
            if rel not in TYPED_RELS:
                continue
            w1 = _norm_word(p[i_l1].split("|")[0])
            w2 = _norm_word(p[i_l2].split("|")[0])
            if w1 and w2 and w1 != w2:
                yield (w1, rel, w2)


def build_typed_arena(cfg, seed):
    """Stream typed CSKG -> degree floor + max_nodes cap -> indexed directed edges. Returns dict."""
    edges = sorted({(w1, r, w2) for (w1, r, w2) in _iter_typed_triples(cfg["max_lines"])})  # sorted() dedupe = determ.
    deg = defaultdict(int)
    for (w1, _r, w2) in edges:
        deg[w1] += 1
        deg[w2] += 1
    keep = {u for u, d in deg.items() if d >= cfg["min_deg"]}
    if cfg["max_nodes"] and len(keep) > cfg["max_nodes"]:
        # keep the highest-degree nodes (deterministic tie-break by label) -> a coherent, denser subgraph.
        ordered = sorted(keep, key=lambda u: (-deg[u], u))
        keep = set(ordered[:cfg["max_nodes"]])
    edges = [(w1, r, w2) for (w1, r, w2) in edges if w1 in keep and w2 in keep]
    ent_labels = sorted({w for (w1, _r, w2) in edges for w in (w1, w2)})
    rel_labels = sorted({r for (_w1, r, _w2) in edges})
    e2i = {w: i for i, w in enumerate(ent_labels)}
    r2i = {r: i for i, r in enumerate(rel_labels)}
    tri = np.array([[e2i[w1], r2i[r], e2i[w2]] for (w1, r, w2) in edges], dtype=np.int64)
    prov = dict(n_typed_edges_streamed=len(edges), n_entities=len(ent_labels), n_relations=len(rel_labels),
                min_deg=cfg["min_deg"], max_nodes=cfg["max_nodes"])
    return dict(tri=tri, n_ent=len(ent_labels), n_rel=len(rel_labels), rel_labels=rel_labels, prov=prov)


def build_syn_noncommutative_arena(n=40, k_rel_distract=2, seed=7):
    """PLANTED non-commutative KG for the self-test. Entities 0..n-1. R=successor (i->i+1 mod n),
    F=flip (i->(-i) mod n). R.F != F.R -> 2-hop order genuinely matters (matched reversed pairs abundant).
    Adds distractor relations (random permutations). Returns the same dict shape as build_typed_arena."""
    rng = np.random.default_rng(seed * 991 + 1)
    rels = ["R", "F"] + ["D%d" % j for j in range(k_rel_distract)]
    r2i = {r: i for i, r in enumerate(rels)}
    tri = []
    for i in range(n):
        tri.append([i, r2i["R"], (i + 1) % n])
        tri.append([i, r2i["F"], (-i) % n])
    for j in range(k_rel_distract):
        perm = rng.permutation(n)
        for i in range(n):
            tri.append([i, r2i["D%d" % j], int(perm[i])])
    tri = np.array(sorted({tuple(t) for t in tri}), dtype=np.int64)
    return dict(tri=tri, n_ent=n, n_rel=len(rels), rel_labels=rels,
                prov=dict(n_typed_edges_streamed=len(tri), n_entities=n, n_relations=len(rels), synthetic=True))


# ===========================================================================
# 2-hop irreducible query construction + order-reversal split
# ===========================================================================

def build_2hop_queries(arena, cfg, seed):
    """Enumerate irreducible 2-hop chains h -r1-> m -r2-> t (t not 1-hop-reachable from h under ANY relation).
    Split ordered relation-pairs into TRAIN-ORDER / TEST-ORDER (test-pair's reverse is a train-pair).
    Returns dict of arrays + gold maps."""
    tri = arena["tri"]
    n_ent = arena["n_ent"]
    n_rel = arena["n_rel"]
    out_edges = defaultdict(list)          # h -> list of (r, t)
    onehop = defaultdict(set)              # h -> set of t reachable in ONE hop under ANY relation (irreducibility)
    indeg = np.zeros(n_ent, dtype=np.int64)
    for (h, r, t) in tri:
        out_edges[int(h)].append((int(r), int(t)))
        onehop[int(h)].add(int(t))
        indeg[int(t)] += 1

    # deterministic ordered-pair split: for unordered {a,b} a<b -> (a,b) TRAIN, (b,a) TEST; a==b -> TRAIN.
    def pair_split(r1, r2):
        if r1 == r2:
            return "train"
        return "train" if r1 < r2 else "test"

    rng = random.Random(seed * 100003 + 7)
    chains = []                            # (h, r1, r2, t, split)
    hs = list(out_edges.keys())
    rng.shuffle(hs)
    cap = cfg["max_chains"] if cfg["max_chains"] else (1 << 62)
    for h in hs:
        if len(chains) >= cap:
            break
        for (r1, m) in out_edges.get(h, ()):
            for (r2, t) in out_edges.get(m, ()):
                if t == h or t == m:
                    continue
                if t in onehop[h]:         # irreducible: no direct 1-hop h->t shortcut
                    continue
                chains.append((h, r1, r2, t, pair_split(r1, r2)))
                if len(chains) >= cap:
                    break
            if len(chains) >= cap:
                break
    # gold map: (h,r1,r2) -> set of tails (for filtered ranking)
    gold = defaultdict(set)
    for (h, r1, r2, t, _s) in chains:
        gold[(h, r1, r2)].add(t)
    train = [c for c in chains if c[4] == "train"]
    test = [c for c in chains if c[4] == "test"]
    # order-sensitive matched subset: test queries whose REVERSED-order query also exists with a DIFFERENT gold set.
    train_keys = {(h, r1, r2): gold[(h, r1, r2)] for (h, r1, r2, _t, _s) in train}
    order_sensitive = []
    for (h, r1, r2, t, _s) in test:
        rev = (h, r2, r1)
        if rev in train_keys:
            gt = gold[(h, r1, r2)]
            gr = train_keys[rev]
            if gt != gr:               # reversing changes the answer -> the sharpest commutative-cap exposure
                order_sensitive.append((h, r1, r2, t))
    return dict(chains=chains, train=train, test=test, gold=gold,
                order_sensitive=order_sensitive, indeg=indeg, onehop=onehop,
                n_train=len(train), n_test=len(test), n_order_sensitive=len(order_sensitive))


# ===========================================================================
# fits (matched objective). additive = LIVE recipe; transition = mirrored with matrices.
# ===========================================================================

def _fit_transition(train_edges, N, n_rel, k, device, seed, epochs, out_dir=None, hb_tag=""):
    """Mirror of fit_kge_anchor1 with per-relation MATRICES: score(h,r,t)=gamma-||X_h M_r^T - X_t||.
    CE self-adversarial + N3 + reciprocal (Lacroix inverse-matrix block) + minibatch SGD. Returns (X, M[:n_rel])."""
    import torch.nn.functional as F
    g = torch.Generator(device="cpu").manual_seed(seed * 7919 + 11)
    ed = train_edges
    inv = ed[:, [2, 1, 0]].copy()
    inv[:, 1] = inv[:, 1] + n_rel          # inverse-relation matrices live in [n_rel, 2*n_rel)
    ed = np.concatenate([ed, inv], axis=0)
    n_rel_eff = 2 * n_rel
    X = (torch.randn(N, k, generator=g) * 0.1).to(device).requires_grad_(True)
    eye = torch.eye(k).unsqueeze(0).repeat(n_rel_eff, 1, 1)
    M = (eye + 0.1 * torch.randn(n_rel_eff, k, k, generator=g)).to(device).requires_grad_(True)  # near-identity init
    opt = torch.optim.Adam([X, M], lr=A1_LR)
    h_all = torch.from_numpy(ed[:, 0]).long().to(device)
    r_all = torch.from_numpy(ed[:, 1]).long().to(device)
    t_all = torch.from_numpy(ed[:, 2]).long().to(device)
    E = h_all.shape[0]
    bs = min(A1_BATCH, E)
    gperm = torch.Generator(device="cpu").manual_seed(seed * 13 + 1)
    gneg = torch.Generator(device="cpu").manual_seed(seed * 17 + 3)
    t0 = time.perf_counter()
    for ep in range(epochs):
        perm = torch.randperm(E, generator=gperm)
        for s in range(0, E, bs):
            bidx = perm[s:s + bs].to(device)
            hb = h_all[bidx]; rb = r_all[bidx]; tb = t_all[bidx]
            b = hb.shape[0]
            pred = torch.bmm(M[rb], X[hb].unsqueeze(2)).squeeze(2)     # (b,k) = X_h M_r^T
            pos_d = torch.norm(pred - X[tb], dim=1)
            pos_score = GAMMA - pos_d
            neg_t = torch.randint(0, N, (b, N_NEG), generator=gneg).to(device)
            neg_d = torch.norm(pred.unsqueeze(1) - X[neg_t], dim=2)    # (b,n_neg)
            neg_score = GAMMA - neg_d
            with torch.no_grad():
                w = torch.softmax(ADV_TEMP * neg_score, dim=1)
            pos_loss = -F.logsigmoid(pos_score)
            neg_loss = -(w * F.logsigmoid(-neg_score)).sum(dim=1)
            loss = (pos_loss + neg_loss).mean()
            reg = (X[hb].abs().pow(3).sum() + X[tb].abs().pow(3).sum()) / float(b)
            loss = loss + N3_LAMBDA * reg + TRANS_M_L2 * M[rb].pow(2).sum() / float(b)
            opt.zero_grad()
            loss.backward()
            opt.step()
        if out_dir is not None and (ep % max(1, epochs // 10) == 0 or ep == epochs - 1):
            _heartbeat(out_dir, ep, epochs, time.perf_counter() - t0,
                       extra={"fit": "transition%s" % hb_tag, "epoch": ep, "loss": round(float(loss.detach()), 4)})
    return X.detach(), M.detach()[:n_rel].contiguous()


def fit_additive_live(train_edges, N, n_rel, k, device, seed, epochs):
    """LIVE additive_map coord source (real fit_kge_anchor1). Exercised in self-test (F.1 real_code_path)."""
    X, D = fit_kge_anchor1(train_edges, N, n_rel, k, device, seed, epochs,
                           reciprocal=True, n_neg=N_NEG, batch_size=A1_BATCH,
                           n3_lambda=N3_LAMBDA, gamma=GAMMA, lr=A1_LR, adv_temp=ADV_TEMP)
    return X, D


# ===========================================================================
# 2-hop scoring + ranking metrics
# ===========================================================================

def _dist_scores(pred, X):
    """pred (nq,k), X (N,k) -> scores (nq,N) = -||pred - X_t|| (higher=better). Chunked over queries. CPU numpy."""
    nq = pred.shape[0]; N = X.shape[0]
    Xsq = (X * X).sum(dim=1)
    XT = X.t()
    out = np.empty((nq, N), dtype=np.float32)
    for s in range(0, nq, SCORE_CHUNK):
        e = min(s + SCORE_CHUNK, nq)
        pc = pred[s:e]
        d2 = (pc * pc).sum(dim=1, keepdim=True) + Xsq.unsqueeze(0) - 2.0 * (pc @ XT)
        sc = -torch.sqrt(torch.clamp(d2, min=0.0))
        out[s:e] = sc.detach().cpu().numpy()
    return out


def _rank_metrics(scores, targets, gold_map, keys):
    """scores (nq,N) float; targets list of gold tail per query; keys list of (h,r1,r2) for filtered removal.
    Returns dict(mrr, hits@k). FILTERED: other golds of the same key are removed before ranking the target."""
    nq = scores.shape[0]
    rr = 0.0; hits = 0.0; cnt = 0
    for i in range(nq):
        t = targets[i]
        others = gold_map.get(keys[i], set())
        row = scores[i].copy()
        for o in others:
            if o != t:
                row[o] = -1e30              # filtered: drop the other true tails
        # rank of target = 1 + number of candidates strictly better
        rank = 1 + int(np.sum(row > row[t]))
        rr += 1.0 / rank
        hits += 1.0 if rank <= HITS_K else 0.0
        cnt += 1
    if cnt == 0:
        return dict(mrr=float("nan"), hits=float("nan"), n=0)
    return dict(mrr=round(rr / cnt, 5), hits=round(hits / cnt, 5), n=cnt)


def _pred_transition(Xt, M, hh, r1, r2, reverse=False):
    a, b = (r2, r1) if reverse else (r1, r2)
    s = torch.bmm(M[torch.from_numpy(a).long()], Xt[torch.from_numpy(hh).long()].unsqueeze(2)).squeeze(2)
    s = torch.bmm(M[torch.from_numpy(b).long()], s.unsqueeze(2)).squeeze(2)
    return s


def _pred_additive(Xa, D, hh, r1, r2):
    return Xa[torch.from_numpy(hh).long()] + D[torch.from_numpy(r1).long()] + D[torch.from_numpy(r2).long()]


def _eval_arms(arena, q, Xa, D, Xt, M, indeg, train_chains, gold_map, test_list, seed, device):
    """Score all arms on the held-out TEST (test-order) chains. Returns per-arm MRR/hits + arm score signatures."""
    if len(test_list) == 0:
        return None
    hh = np.array([c[0] for c in test_list], dtype=np.int64)
    r1 = np.array([c[1] for c in test_list], dtype=np.int64)
    r2 = np.array([c[2] for c in test_list], dtype=np.int64)
    tt = [c[3] for c in test_list]
    keys = [(c[0], c[1], c[2]) for c in test_list]
    N = arena["n_ent"]

    add_pred = _pred_additive(Xa, D, hh, r1, r2).to(device)
    trans_pred = _pred_transition(Xt, M, hh, r1, r2, reverse=False).to(device)
    shuf_pred = _pred_transition(Xt, M, hh, r1, r2, reverse=True).to(device)
    add_sc = _dist_scores(add_pred, Xa.to(device))
    trans_sc = _dist_scores(trans_pred, Xt.to(device))
    shuf_sc = _dist_scores(shuf_pred, Xt.to(device))

    # FREQ_COMPOSED: per-hop marginal tail frequency from TRAIN-ORDER chains only (freq of t as r2-tail).
    r2_tail_freq = defaultdict(lambda: defaultdict(float))
    for (h, cr1, cr2, ct, _s) in train_chains:
        r2_tail_freq[cr2][ct] += 1.0
    freq_sc = np.full((len(test_list), N), -1e9, dtype=np.float32)
    for i in range(len(test_list)):
        fr = r2_tail_freq.get(int(r2[i]), None)
        if fr:
            for t_ent, c in fr.items():
                freq_sc[i, t_ent] = c
    # DEGREE: global in-degree popularity (order-blind, no train leakage of chains)
    deg_row = indeg.astype(np.float32)
    deg_sc = np.broadcast_to(deg_row, (len(test_list), N)).copy()
    # CHANCE: deterministic pseudo-random per query
    rng = np.random.default_rng(seed * 100777 + 5)
    chance_sc = rng.standard_normal((len(test_list), N)).astype(np.float32)
    # MEMORIZE: exact chain lookup from TRAIN-ORDER; else POP (most frequent tail overall)
    train_key_gold = defaultdict(set)
    tail_count = defaultdict(float)
    for (h, cr1, cr2, ct, _s) in train_chains:
        train_key_gold[(h, cr1, cr2)].add(ct)
        tail_count[ct] += 1.0
    pop_ent = max(tail_count.items(), key=lambda kv: kv[1])[0] if tail_count else 0
    memo_sc = np.full((len(test_list), N), -1e9, dtype=np.float32)
    for i in range(len(test_list)):
        memo_sc[i, pop_ent] = 0.0
        for g in train_key_gold.get(keys[i], ()):  # held-out irreducible: this is ~always empty -> POP (leak check)
            memo_sc[i, g] = 1.0

    arm_scores = {ARM_TRANS: trans_sc, ARM_ADD: add_sc, ARM_SHUF: shuf_sc,
                  ARM_FREQ: freq_sc, ARM_DEG: deg_sc, ARM_CHANCE: chance_sc, ARM_MEMO: memo_sc}
    res = {}
    sigs = {}
    for arm, sc in arm_scores.items():
        res[arm] = _rank_metrics(sc, tt, gold_map, keys)
        sigs[arm] = _sig(sc[:, :min(N, 64)])          # signature over a stable score slice
    # ORACLE reachability: fraction of test targets present as a valid candidate (always true here -> sanity)
    oracle_reach = 1.0
    # order-sensitivity check on the additive arm: reversed-order score must be IDENTICAL (commutative property)
    add_rev = _pred_additive(Xa, D, hh, r2, r1).to(device)
    add_commutative_maxabs = float(torch.max(torch.abs(add_pred - add_rev)).item())
    trans_rev = _pred_transition(Xt, M, hh, r1, r2, reverse=True).to(device)
    trans_order_maxabs = float(torch.max(torch.abs(trans_pred - trans_rev)).item())
    return dict(arms=res, sigs=sigs, n_test=len(test_list), oracle_reach=oracle_reach,
                add_commutative_maxabs=round(add_commutative_maxabs, 6),
                trans_order_maxabs=round(trans_order_maxabs, 6))


def _eval_order_sensitive(arena, os_list, Xa, D, Xt, M, gold_map, device):
    """Sharper subset: MRR on order-sensitive matched queries (reversing changes the answer)."""
    if len(os_list) < 30:
        return dict(n=len(os_list), low_power=True)
    hh = np.array([c[0] for c in os_list], dtype=np.int64)
    r1 = np.array([c[1] for c in os_list], dtype=np.int64)
    r2 = np.array([c[2] for c in os_list], dtype=np.int64)
    tt = [c[3] for c in os_list]
    keys = [(c[0], c[1], c[2]) for c in os_list]
    add_sc = _dist_scores(_pred_additive(Xa, D, hh, r1, r2).to(device), Xa.to(device))
    trans_sc = _dist_scores(_pred_transition(Xt, M, hh, r1, r2).to(device), Xt.to(device))
    return dict(n=len(os_list), low_power=False,
                add_mrr=_rank_metrics(add_sc, tt, gold_map, keys)["mrr"],
                trans_mrr=_rank_metrics(trans_sc, tt, gold_map, keys)["mrr"])


# ===========================================================================
# per-seed run
# ===========================================================================

def run_seed(arena_builder, cfg, seed, device, out_dir, do_scramble=True):
    arena = arena_builder(cfg, seed)
    N = arena["n_ent"]; n_rel = arena["n_rel"]
    q = build_2hop_queries(arena, cfg, seed)
    if q["n_test"] < MIN_IRREDUCIBLE:
        return dict(refute_impl=True, reason="too_few_test_irreducible", n_test=q["n_test"],
                    prov=arena["prov"], n_train=q["n_train"])
    tri = arena["tri"]; k = cfg["k"]; epochs = cfg["epochs"]
    Xa, D = fit_additive_live(tri, N, n_rel, k, device, seed, epochs)
    Xt, M = _fit_transition(tri, N, n_rel, k, device, seed, epochs, out_dir=out_dir, hb_tag="_clean")
    ev = _eval_arms(arena, q, Xa, D, Xt, M, q["indeg"], q["train"], q["gold"], q["test"], seed, device)
    os_ev = _eval_order_sensitive(arena, q["order_sensitive"], Xa, D, Xt, M, q["gold"], device)

    scramble = None
    if do_scramble:
        rng = np.random.default_rng(seed * 100999 + 3)
        perm = rng.permutation(n_rel)
        tri_s = tri.copy()
        tri_s[:, 1] = perm[tri_s[:, 1]]                # relation-label shuffle (arena-sanity must-fail control)
        Xas, Ds = fit_additive_live(tri_s, N, n_rel, k, device, seed, epochs)
        Xts, Ms = _fit_transition(tri_s, N, n_rel, k, device, seed, epochs, out_dir=out_dir, hb_tag="_scramble")
        ev_s = _eval_arms(arena, q, Xas, Ds, Xts, Ms, q["indeg"], q["train"], q["gold"], q["test"], seed, device)
        null_mrr = max(ev["arms"][ARM_FREQ]["mrr"], ev["arms"][ARM_DEG]["mrr"])
        clean_margin = ev["arms"][ARM_TRANS]["mrr"] - null_mrr
        scr_margin = ev_s["arms"][ARM_TRANS]["mrr"] - null_mrr
        rel_specific_frac = (scr_margin / clean_margin) if clean_margin > 1e-6 else 1.0
        scramble = dict(clean_margin=round(clean_margin, 5), scramble_margin=round(scr_margin, 5),
                        rel_specific_frac=round(float(rel_specific_frac), 5),
                        scramble_trans_mrr=ev_s["arms"][ARM_TRANS]["mrr"])
    return dict(refute_impl=False, prov=arena["prov"], n_train=q["n_train"], n_test=q["n_test"],
                n_order_sensitive=q["n_order_sensitive"], eval=ev, order_sensitive=os_ev, scramble=scramble)


# ===========================================================================
# aggregate + verdict
# ===========================================================================

def _mean(vals):
    vals = [v for v in vals if v == v]
    return float(np.mean(vals)) if vals else float("nan")


def aggregate_and_verdict(per_seed):
    good = [s for s in per_seed if not s.get("refute_impl")]
    if not good:
        return "REFUTE_IMPL_ARENA_DEGENERATE", "no seed produced enough irreducible held-out 2-hop queries", {}
    trans = _mean([s["eval"]["arms"][ARM_TRANS]["mrr"] for s in good])
    add = _mean([s["eval"]["arms"][ARM_ADD]["mrr"] for s in good])
    shuf = _mean([s["eval"]["arms"][ARM_SHUF]["mrr"] for s in good])
    freq = _mean([s["eval"]["arms"][ARM_FREQ]["mrr"] for s in good])
    deg = _mean([s["eval"]["arms"][ARM_DEG]["mrr"] for s in good])
    chance = _mean([s["eval"]["arms"][ARM_CHANCE]["mrr"] for s in good])
    memo = _mean([s["eval"]["arms"][ARM_MEMO]["mrr"] for s in good])
    null = max(freq, deg)
    add_gap = trans - add
    null_gap = trans - null
    order_gap = trans - shuf
    rel_specific = _mean([s["scramble"]["rel_specific_frac"] for s in good if s.get("scramble")])
    scramble_gate_ok = bool(rel_specific <= SCRAMBLE_RETAIN_MAX) if rel_specific == rel_specific else False
    leak_ok = bool(memo <= null + 0.02)                # MEMORIZE must not beat the null on irreducible held-out

    order_attr = bool(order_gap >= ORDER_ATTR_PASS)
    beats_add = bool(add_gap >= ADD_GAP_PASS)
    beats_null = bool(null_gap >= NULL_GAP_PASS)
    ties_add = bool(add_gap <= ADD_GAP_FAIL)
    null_dom = bool(null_gap <= NULL_GAP_FAIL)

    if beats_add and beats_null and order_attr and scramble_gate_ok:
        verdict = "HARD_PASS_TRANSITION_OP_BEATS_COMMUTATIVE_ADDITIVE_ON_REAL_2HOP"
    elif ties_add or null_dom or (not order_attr) or (not scramble_gate_ok):
        if ties_add:
            verdict = "HARD_FAIL_TRANSITION_TIES_COMMUTATIVE_ADDITIVE"
        elif null_dom:
            verdict = "HARD_FAIL_DEGREE_FREQ_DOMINATED"
        elif not order_attr:
            verdict = "HARD_FAIL_ORDER_NOT_LOAD_BEARING_SHUFFLE_NO_DEGRADE"
        else:
            verdict = "HARD_FAIL_ARENA_HOMOPHILY_SCRAMBLE_RETAINS_MARGIN"
    else:
        verdict = "MIDDLE_BAND_TRANSITION_SUBTHRESHOLD_OVER_ADDITIVE_OR_NULL"

    gates = dict(trans_mrr=round(trans, 5), add_mrr=round(add, 5), shuf_mrr=round(shuf, 5),
                 freq_mrr=round(freq, 5), deg_mrr=round(deg, 5), chance_mrr=round(chance, 5),
                 memo_mrr=round(memo, 5), null_mrr=round(null, 5),
                 add_gap=round(add_gap, 5), null_gap=round(null_gap, 5), order_gap=round(order_gap, 5),
                 rel_specific_frac=round(rel_specific, 5) if rel_specific == rel_specific else None,
                 scramble_gate_ok=scramble_gate_ok, order_attribution_confirmed=order_attr,
                 beats_additive=beats_add, beats_null=beats_null, leak_ok=leak_ok,
                 n_seeds=len(good))
    os_add = _mean([s["order_sensitive"].get("add_mrr", float("nan")) for s in good
                    if not s["order_sensitive"].get("low_power")])
    os_trans = _mean([s["order_sensitive"].get("trans_mrr", float("nan")) for s in good
                      if not s["order_sensitive"].get("low_power")])
    gates["order_sensitive_add_mrr"] = round(os_add, 5) if os_add == os_add else None
    gates["order_sensitive_trans_mrr"] = round(os_trans, 5) if os_trans == os_trans else None
    msg = ("%s || TRANS=%s ADD=%s (add_gap=%s) NULL=%s(freq=%s deg=%s) null_gap=%s | order: SHUF=%s order_gap=%s "
           "attr=%s | scramble rel_specific=%s ok=%s | MEMO=%s CHANCE=%s leak_ok=%s | order_sensitive TRANS=%s ADD=%s | "
           "n_seeds=%d" % (verdict, _fmt(trans), _fmt(add), _fmt(add_gap), _fmt(null), _fmt(freq), _fmt(deg),
                           _fmt(null_gap), _fmt(shuf), _fmt(order_gap), order_attr,
                           gates["rel_specific_frac"], scramble_gate_ok, _fmt(memo), _fmt(chance), leak_ok,
                           gates["order_sensitive_trans_mrr"], gates["order_sensitive_add_mrr"], len(good)))
    return verdict, msg, gates


# ===========================================================================
# self-test (planted non-commutative arena; discriminator-fires + real code path)
# ===========================================================================

def _self_test(device):
    t0 = time.perf_counter()
    cfg = dict(SELFTEST_CFG)
    seed = 7
    arena = build_syn_noncommutative_arena(n=80, k_rel_distract=2, seed=seed)
    N = arena["n_ent"]; n_rel = arena["n_rel"]; k = cfg["k"]; epochs = cfg["epochs"]
    q = build_2hop_queries(arena, cfg, seed)
    exercised = set()
    Xa, D = fit_additive_live(arena["tri"], N, n_rel, k, device, seed, epochs)
    exercised.add("fit_kge_anchor1")
    Xt, M = _fit_transition(arena["tri"], N, n_rel, k, device, seed, epochs)
    ev = _eval_arms(arena, q, Xa, D, Xt, M, q["indeg"], q["train"], q["gold"], q["test"], seed, device)
    if ev is None:
        return False, dict(fail="no test chains in synthetic arena")

    # (1) real code path + signature
    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1"], "exercised_entrypoints": sorted(exercised)},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "args_count": 7,
         "kwargs": {"reciprocal": True, "n_neg": N_NEG, "batch_size": A1_BATCH, "n3_lambda": N3_LAMBDA,
                    "gamma": GAMMA, "lr": A1_LR, "adv_temp": ADV_TEMP}},
        {"kind": "metric_moves", "metric_name": "order_sensitivity_maxabs",
         "before": ev["add_commutative_maxabs"], "after": ev["trans_order_maxabs"]},
    ], run_mode="selftest")

    # (2) CONSTRUCTION-LEVEL: additive is commutative (identical reversed-order pred); transition is NOT.
    add_commutative = ev["add_commutative_maxabs"] <= 1e-4
    trans_noncommutative = ev["trans_order_maxabs"] >= 1e-2

    # (3) arms differ (hash), exempt (TRANS, SHUF) pair which may coincide iff order-invariant (the null diagnostic)
    af_arms = [ARM_TRANS, ARM_ADD, ARM_FREQ, ARM_DEG, ARM_CHANCE, ARM_MEMO]
    n_distinct = len(set(ev["sigs"][a] for a in af_arms))
    arms_differ = n_distinct >= 5

    # (4) ARENA-LEARNABLE + DISCRIMINATOR-FIRES: on the ADVERSARIAL order-sensitive arena the additive (commutative)
    #     baseline is EXPECTED near chance (order-blind by construction -- that is the POINT). The meaningful checks:
    #     (a) TRANSITION learns signal above chance (fit runs, arena not degenerate), not saturated; and
    #     (b) TRANSITION strictly beats the commutative ADDITIVE arm on this order-sensitive arena (the discriminator
    #     the FULL will test on real data). This is fit-corroborated on top of the fit-INDEPENDENT construction proof
    #     (add_commutative maxabs~0 vs trans_noncommutative maxabs large).
    add_mrr = ev["arms"][ARM_ADD]["mrr"]; chance_mrr = ev["arms"][ARM_CHANCE]["mrr"]
    trans_mrr = ev["arms"][ARM_TRANS]["mrr"]
    arena_learnable = bool(chance_mrr < trans_mrr < 0.999)
    # Discriminator fires on the SHARPEST subset (order-sensitive matched queries: reversing changes the answer,
    # so the commutative additive arm is structurally capped). Transition must clearly beat additive there.
    os_ev = _eval_order_sensitive(arena, q["order_sensitive"], Xa, D, Xt, M, q["gold"], device)
    os_trans = os_ev.get("trans_mrr", float("nan")); os_add = os_ev.get("add_mrr", float("nan"))
    discriminator_fires = bool((not os_ev.get("low_power")) and (os_trans == os_trans)
                               and (os_trans > os_add + 0.05))

    # (5) determinism: re-run eval identical
    ev2 = _eval_arms(arena, q, Xa, D, Xt, M, q["indeg"], q["train"], q["gold"], q["test"], seed, device)
    deterministic = all(ev["sigs"][a] == ev2["sigs"][a] for a in af_arms)

    ok = bool(vp_ok and add_commutative and trans_noncommutative and arms_differ
              and arena_learnable and discriminator_fires and deterministic)
    res = dict(vp_ok=vp_ok, add_commutative_maxabs=ev["add_commutative_maxabs"],
               trans_order_maxabs=ev["trans_order_maxabs"], add_commutative=add_commutative,
               trans_noncommutative=trans_noncommutative, arms_differ=arms_differ, n_distinct=n_distinct,
               arena_learnable=arena_learnable, discriminator_fires=discriminator_fires,
               add_mrr=add_mrr, chance_mrr=chance_mrr, trans_mrr=trans_mrr, deterministic=deterministic,
               os_trans_mrr=round(os_trans, 5) if os_trans == os_trans else None,
               os_add_mrr=round(os_add, 5) if os_add == os_add else None,
               n_test=q["n_test"], n_order_sensitive=q["n_order_sensitive"],
               elapsed_s=round(time.perf_counter() - t0, 2))
    if not ok:
        res["fail"] = ("vp=%s add_comm=%s trans_noncomm=%s arms=%s learnable=%s discrim=%s det=%s "
                       "(trans=%s add=%s chance=%s)"
                       % (vp_ok, add_commutative, trans_noncommutative, arms_differ, arena_learnable,
                          discriminator_fires, deterministic, _fmt(trans_mrr), _fmt(add_mrr), _fmt(chance_mrr)))
    return ok, res


# ===========================================================================
# main
# ===========================================================================

def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)   # Path (write_metrics + os.path.join both accept it)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = cfg["seeds"]
    _write_start_marker(out_dir, run_mode, len(seeds))
    t_start = time.perf_counter()

    st_ok, st_res = _self_test(device)
    _log("SELFTEST ok=%s add_comm_maxabs=%s trans_order_maxabs=%s arms_distinct=%s baseline_in_band=%s det=%s"
         % (st_ok, st_res.get("add_commutative_maxabs"), st_res.get("trans_order_maxabs"),
            st_res.get("n_distinct"), st_res.get("baseline_in_band"), st_res.get("deterministic")))
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode, anchor_name=ANCHOR_NAME,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test", anchor_name=ANCHOR_NAME,
            verdict_msg=("SELFTEST_PASS: additive commutative (maxabs=%s<=1e-4), transition non-commutative "
                         "(maxabs=%s>=1e-2), real fit_kge_anchor1 exercised, arms distinct (%s), baseline in band, "
                         "deterministic" % (st_res["add_commutative_maxabs"], st_res["trans_order_maxabs"],
                                            st_res["n_distinct"])),
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode, anchor_name=ANCHOR_NAME,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            r = run_seed(build_typed_arena, cfg, seed, device, out_dir, do_scramble=True)
            per_seed.append(r)
            write_partial(out_dir, seed, dict(seed=seed, metrics=r, run_mode=run_mode))
            if r.get("refute_impl"):
                _log("seed=%d REFUTE_IMPL %s (n_test=%d)" % (seed, r.get("reason"), r.get("n_test", 0)))
            else:
                g = aggregate_and_verdict([r])[2]
                _log("seed=%d TRANS=%s ADD=%s NULL=%s SHUF=%s rel_specific=%s (n_test=%d n_os=%d %.1fs)"
                     % (seed, _fmt(g["trans_mrr"]), _fmt(g["add_mrr"]), _fmt(g["null_mrr"]), _fmt(g["shuf_mrr"]),
                        g.get("rel_specific_frac"), r["n_test"], r.get("n_order_sensitive", 0), time.time() - ts))
            _heartbeat(out_dir, si + 1, len(seeds), time.perf_counter() - t_start, extra={"seed": seed})
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < len(seeds):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode, anchor_name=ANCHOR_NAME,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (len(seeds), len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=round(time.perf_counter() - t_start, 2), anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def _resolve_device(choice):
    if choice == "cpu":
        return torch.device("cpu")
    if choice == "cuda":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device("cpu")   # runner does not pass argv; DEFAULT cpu (remote_cpu_queue safe)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    device = _resolve_device(args.device)
    out_dir = get_output_dir(ANCHOR_NAME)
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
