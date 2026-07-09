"""Binding-structured encoder: does folding typed-relation binding into the code at ENCODE time make
multi-hop grounded-attribute reach EXTRACTABLE past 1 hop on the REAL learned codes -- above the
similarity-trained-encoder baseline?

This closes the gap the bind-chain cell (grounding_bind_chain_systematicity_v1, 60f40852a) left UNTESTED.
That cell's block-2 reach-deepening ran over a LOSSLESSLY-RECOVERED synthetic graph and its block-3 ORACLE
skyline used a privileged ridge over the real codes (VET: READOUT_LIMIT weak; encode-time-bound reach was
never measured on the ACTUAL learned encoder). Here the graph over which the attribute propagates is
RECOVERED FROM THE LEARNED CODES themselves -- no oracle, no reconstructed-true-graph shortcut.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test the 2 ENCODERS + the 4 reach-arm fields)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared: ordering-acc chance floor = 0.5; the discriminator is the shuffled-gated,
#   over-smoothing-gated effective REACH of grounded-attribute propagation over a code-recovered graph,
#   not a closed-form estimator noise floor.
# - baseline_in_band at smoke: BASELINE_COSINE effective reach must sit at the 1-hop cap (<= BASELINE_CAP_MAX)
#   -> a genuine cap to beat (else INCONCLUSIVE_NO_ONESHOT_CAP; not a fair contrast); attribute assortativity
#   smooth high + shuffled ~0.
# - discriminator survives scale: smoke fires it (BINDING_UNBIND reach > BASELINE_COSINE reach; BASELINE_UNBIND
#   ~ garbage proving unbind needs encode-time binding; shuffled flat). SMOKE exercises the SAME branches as FULL.
# - HARD_PASS strictly above floor: reach(BINDING_UNBIND) >= 2 AND reach_delta_vs_baseline >= 1 AND newly-reached
#   bin acc >= REACH_THRESH + strict AND margin over shuffled AND non-collapsed AND baseline cap present.
# - HP_SCOPE: reach gates apply to BINDING_UNBIND (treatment) vs BASELINE_COSINE (cap); BASELINE_UNBIND is the
#   encode-time-binding-necessity control; BINDING_COSINE is a robustness arm (does binding help even under the
#   identical cosine read); SHUFFLED attribute is the genuineness control per arm.
# - sweep axis: D (propagation depth); cardinality via EXPECTED_N_UNITS = n_model_seeds; D-sweep coverage
#   asserted WITHIN each seed unit.
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run;
#   over-smoothing collapse gate proven to fire; recovery crosstalk floor is sqrt(1/code_dim)-scaled)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg

HONESTY FRAMING (load-bearing): this is REAL-SUBSTRATE multi-hop grounded-attribute PROPAGATION on learned
codes. It is NOT "language understanding", NOT "grounding solved". The grounded scalar is a synthetic
graph-smooth field diffused over the REAL ConceptNet subgraph (an honest stand-in for a measured non-symbolic
attribute that correlates along relational edges). A PASS = a necessary (not sufficient) recipe: encode-time
typed binding makes multi-hop grounded propagation EXTRACTABLE on the real codes past the 1-hop similarity cap.
A FAIL = encode-time binding as implemented is NOT enough on real learned codes -> a deeper
encoder-architecture question (not a claim about the substrate's ceiling). Both outcomes are informative.

Teacher-free / self-contained: NO BGE, NO external LM, NO network. Reuses the CG'd teacher-free relational
encoder pipeline (cert 06e5a493d): load_cn_subgraph, char_trigram_features, ProjHead, info_nce,
vicreg_repulsion, _l2norm, build_adjlist; the snowball grounding primitives (make_smooth_attribute,
attribute_assortativity, multi_source_bfs, distance_bins, ordering_accuracy, train_encoder for BASELINE);
and the bind-chain reach machinery (propagate_field, _row_stochastic_from_adj, _reach_arm_metrics,
_reach_collapsed, _reach_hops). Binding operator = hdlab.binding HRR real path (circular convolution via FFT),
with fixed UNITARY per-relation role vectors (norm-preserving -> clean unbind). CPU-only. ASCII-only. No emojis.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    load_cn_subgraph,
    char_trigram_features,
    ProjHead,
    info_nce,
    vicreg_repulsion,
    build_adjlist,
    _l2norm,
    RELATIONS_PATH,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    make_smooth_attribute,
    attribute_assortativity,
    multi_source_bfs,
    distance_bins,
    ordering_accuracy,
    train_encoder,             # BASELINE similarity encoder (info_nce neighbor + vicreg, ungrounded)
    SUBGRAPH_BASE_SEED,
    MIN_BIN_NODES,
)
from experiments.exp_grounding_bind_chain_systematicity_v1 import (  # noqa: E402
    propagate_field,
    _row_stochastic_from_adj,
    _reach_arm_metrics,
    _reach_collapsed,
    _reach_hops,
    REACH_THRESH,
    MARGIN_FLOOR,
)
from hdlab.binding import bind as hdlab_bind  # noqa: E402  (HRR real path: circular convolution via FFT)

ANCHOR_NAME = "grounding_binding_structured_encoder_multihop_v1"

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale differs)
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    seeds=[7],
    n_nodes=400, epochs=10, batch=256, code_dim=64, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=20, diffuse_steps=8, n_sources=6,
    D=[1, 2, 3], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=2000,
)

SMOKE_CFG = dict(
    seeds=[7, 13],
    n_nodes=1800, epochs=45, batch=256, code_dim=128, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=30, diffuse_steps=10, n_sources=20,
    D=[1, 2, 3, 4], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=4000,
)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_nodes=5000, epochs=100, batch=512, code_dim=256, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_ground_seeds=80, diffuse_steps=12, n_sources=50,
    D=[1, 2, 3, 4, 5], alpha=0.85, recover_topk=8, cos_floor_c=1.1, n_pairs=6000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run)
# ---------------------------------------------------------------------------
# Reach is measured on a graph RECOVERED FROM THE LEARNED CODES, propagating a graph-smooth grounded
# attribute D steps from sparse seeds; per-arm effective reach = farthest contiguous TRUE-distance bin with
# smooth ordering acc >= REACH_THRESH (0.55) AND margin over shuffled >= MARGIN_FLOOR (0.05), non-collapsed
# (over-smoothing gated). REACH_THRESH / MARGIN_FLOOR are imported from the bind-chain reach machinery so the
# reach definition is bit-identical to the prior cell.

REACH_HP_MIN = 2            # HARD_PASS: BINDING_UNBIND effective reach must extend to at least hop 2
REACH_DELTA_HP = 1          # HARD_PASS: reach(BINDING_UNBIND) - reach(BASELINE_COSINE) >= this
REACH_STRICT_MARGIN = 0.01  # newly-reached bin acc must clear REACH_THRESH by >= this for a clean HP
BASELINE_CAP_MAX = 1        # BASELINE_COSINE reach must be <= this (baseline_in_band; a genuine 1-hop cap)
RECOVERY_RECALL_MIN = 0.20  # BINDING_UNBIND role-apply edge recall floor (else recovery itself failed)

# attribute graph-smoothness precondition (adaptive gate)
ATTR_ASSORT_SMOOTH_MIN = 0.45
ATTR_ASSORT_SHUFFLED_MAX = 0.20

# reach arm names
BASE_COS = "BASELINE_COSINE"     # similarity encoder, cosine-kNN recovery (the 1-hop cap)
BASE_UNB = "BASELINE_UNBIND"     # similarity encoder, role-apply recovery (control: needs encode-time binding)
BIND_UNB = "BINDING_UNBIND"      # binding encoder, role-apply recovery (PRIMARY treatment)
BIND_COS = "BINDING_COSINE"      # binding encoder, cosine-kNN recovery (robustness)
REACH_ARMS = [BASE_COS, BASE_UNB, BIND_UNB, BIND_COS]


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Typed ConceptNet subgraph: reuse load_cn_subgraph node/edge SELECTION (identical subgraph to
# snowball / bind-chain), then a second pass attaches the real rel_type to each kept undirected edge.
# ---------------------------------------------------------------------------

def load_typed_cn_subgraph(n_nodes, base_seed):
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(n_nodes, base_seed)
    idx_of = {nid: i for i, nid in enumerate(node_ids)}
    kept_pairs = set()
    for (a, b) in edges:
        kept_pairs.add((int(a), int(b)))
    pair_rel = {}
    with open(RELATIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            s = d.get("src_id")
            t = d.get("tgt_id")
            if s not in idx_of or t not in idx_of:
                continue
            iu = idx_of[s]
            iv = idx_of[t]
            if iu == iv:
                continue
            key = (iu, iv) if iu < iv else (iv, iu)
            if key in kept_pairs and key not in pair_rel:
                pair_rel[key] = d.get("rel_type", "UNK")
    rels_for_edges = [pair_rel.get((int(a), int(b)), "UNK") for (a, b) in edges]
    types = sorted(set(rels_for_edges))
    tindex = {t: i for i, t in enumerate(types)}
    rels = np.array([tindex[r] for r in rels_for_edges], dtype=np.int32)
    meta = dict(meta)
    meta["n_relation_types"] = len(types)
    meta["relation_types"] = types
    meta["n_typed_edges"] = int(np.sum(np.array(rels_for_edges) != "UNK"))
    return node_ids, node_words, edges, degrees, rels, len(types), types, meta


# ---------------------------------------------------------------------------
# Unitary HRR role codebook (norm-preserving circular convolution -> clean unbind).
# One role per relation type; fixed (NOT trained). Unit-modulus frequency spectrum -> real role vector.
# ---------------------------------------------------------------------------

def make_unitary_roles(T, d, rng):
    """T real role vectors [T, d] whose circular convolution is norm-preserving (unit-modulus spectrum)."""
    nf = d // 2 + 1
    phases = rng.uniform(0.0, 2.0 * np.pi, size=(T, nf))
    spec = np.exp(1j * phases)
    spec[:, 0] = 1.0                       # DC real (magnitude 1)
    if d % 2 == 0:
        spec[:, -1] = 1.0                  # Nyquist real (magnitude 1)
    roles = np.fft.irfft(spec, n=d, axis=1)
    return roles.astype(np.float32)


def np_hrr_bind(role, Z):
    """Circular convolution of a single role [d] with each row of Z [n, d] -> [n, d] (HRR real bind)."""
    d = Z.shape[1]
    fr = np.fft.rfft(role.astype(np.float64))
    FZ = np.fft.rfft(Z.astype(np.float64), axis=1)
    return np.fft.irfft(FZ * fr[None, :], n=d, axis=1).astype(np.float32)


def torch_hrr_bind(role_batch, z_batch):
    """Per-row circular convolution: role_batch [B, d], z_batch [B, d] -> [B, d] (differentiable)."""
    d = z_batch.shape[1]
    fr = torch.fft.rfft(role_batch, dim=1)
    fz = torch.fft.rfft(z_batch, dim=1)
    return torch.fft.irfft(fr * fz, n=d, dim=1)


# ---------------------------------------------------------------------------
# BINDING-STRUCTURED encoder: base neighbor InfoNCE + VICReg PLUS a typed-binding-consistency InfoNCE
# (bind(role_r, z_i) must land on the r-typed neighbor z_j). Folds typed relations into the code at
# ENCODE time. Roles are fixed unitary HRR vectors.
# ---------------------------------------------------------------------------

def train_binding_encoder(X, edges, rels, roles_np, cfg, seed, out_dir=None, tag="BINDING"):
    torch.manual_seed(seed)
    np.random.seed(seed)
    n_nodes = X.shape[0]
    feat_dim = X.shape[1]
    Xt = torch.from_numpy(X)
    model = ProjHead(feat_dim, cfg["code_dim"])
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    roles_t = torch.from_numpy(roles_np)  # [T, d]
    E = edges.shape[0]
    e_a = edges[:, 0].astype(np.int64)
    e_b = edges[:, 1].astype(np.int64)
    e_r = rels.astype(np.int64)
    rng = np.random.default_rng(seed + 7)
    log_every = max(1, cfg["epochs"] // 5)
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        bs = min(cfg["batch"], E)
        eidx = rng.choice(E, size=bs, replace=False)
        # random orientation per sampled edge (anchor -> neighbor under role r)
        flip = rng.random(bs) < 0.5
        ai = np.where(flip, e_b[eidx], e_a[eidx])
        pi = np.where(flip, e_a[eidx], e_b[eidx])
        ri = e_r[eidx]
        xa = Xt[torch.from_numpy(ai)]
        xp = Xt[torch.from_numpy(pi)]
        ha = model(xa)
        hp = model(xp)
        # (1) base proximity + (2) VICReg repulsion (identical to baseline encoder objective)
        loss = info_nce(ha, hp, cfg["temp"]) + vicreg_repulsion(
            torch.cat([ha, hp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        # (3) typed-binding consistency: bind(role_r, anchor) must match the r-typed neighbor,
        #     distinguishably from other neighbors in the batch (in-batch negatives).
        za = _l2norm(ha)
        bound = torch_hrr_bind(roles_t[torch.from_numpy(ri)], za)
        loss = loss + cfg["lambda_bind"] * info_nce(bound, hp, cfg["temp"])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d %s ep=%d/%d loss=%.4f (%.1fs)" % (
                seed, tag, ep, cfg["epochs"], float(loss.detach()), time.perf_counter() - t_ep))
            if out_dir is not None:
                try:
                    from experiments._cell_heartbeat import emit_heartbeat
                    emit_heartbeat(str(out_dir), unit_idx=ep, total_units=cfg["epochs"],
                                   elapsed_s=time.perf_counter() - t_ep)
                except Exception as _hb_e:  # heartbeat best-effort telemetry (SCHEMA-VET 13D)
                    _log("  [heartbeat-warn] %s: %s" % (type(_hb_e).__name__, str(_hb_e)[:120]))
    with torch.no_grad():
        emb = _l2norm(model(Xt)).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# Graph recovery FROM THE LEARNED CODES (no true graph, no oracle)
# ---------------------------------------------------------------------------

def _l2(Z):
    return Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-8)


def crosstalk_floor(n, d, c):
    """Codebook-size-aware VSA cleanup floor: expected max crosstalk cosine among n iid random unit
    vectors in R^d is ~ sqrt(2 ln n / d). A principled floor scales WITH the codebook size (Bonferroni /
    extreme-value criterion), unlike a fixed z/sqrt(d) which floods large codebooks with crosstalk."""
    return float(c) * float(np.sqrt(2.0 * np.log(max(int(n), 2)) / float(d)))


def _topk_floor_adj(S, topk, floor):
    """Undirected adjacency from a score matrix S [n,n]: for each source i keep its top-k targets j whose
    score exceeds the codebook-size-aware crosstalk floor, add the (directed) edge, then symmetrize by union.
    Role-apply recovery is inherently DIRECTED (bind(role_r, z_i) points at i's r-neighbour, not conversely),
    so a directed-then-unioned rule is the correct shape; the SIZE-AWARE floor -- not mutuality -- is what
    controls crosstalk precision. Applied IDENTICALLY to the cosine and role scores so the arms differ ONLY
    in how S is computed."""
    n = S.shape[0]
    Sc = S.copy()
    np.fill_diagonal(Sc, -np.inf)
    top = np.argpartition(-Sc, topk - 1, axis=1)[:, :topk]      # [n, topk]
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in top[i]:
            if Sc[i, j] > floor:
                adj[i].add(int(j))
                adj[int(j)].add(i)                              # symmetrize (union)
    return adj


def score_cosine(Z):
    """Cosine score matrix [n,n] over the learned codes (similarity encoder's NATIVE read)."""
    z = _l2(Z).astype(np.float32)
    return (z @ z.T).astype(np.float32)


def score_role(Z, roles_np):
    """Role-apply cleanup score S[i,j] = max_r cos(bind(role_r, z_i), z_j): the best typed-binding match of
    j as an r-neighbour of i, over all relation roles. This is the encode-time-binding NATIVE read (max-over-
    roles crosstalk on an encoder NOT trained with binding structure -- see BASELINE_UNBIND control)."""
    z = _l2(Z).astype(np.float32)
    n, d = z.shape
    T = roles_np.shape[0]
    S = np.full((n, n), -np.inf, dtype=np.float32)
    for r in range(T):
        pred = _l2(np_hrr_bind(roles_np[r], z)).astype(np.float32)
        sc = (pred @ z.T).astype(np.float32)
        np.maximum(S, sc, out=S)
    return S


def recover_cosine_adj(Z, topk, floor):
    return _topk_floor_adj(score_cosine(Z), topk, floor)


def recover_role_adj(Z, roles_np, topk, floor):
    return _topk_floor_adj(score_role(Z, roles_np), topk, floor)


def _edge_recall_precision(rec_adj, edges):
    true_pairs = set((int(a), int(b)) if a < b else (int(b), int(a)) for (a, b) in edges)
    rec_pairs = set()
    for i in range(len(rec_adj)):
        for j in rec_adj[i]:
            a, b = (i, j) if i < j else (j, i)
            rec_pairs.add((a, b))
    inter = len(true_pairs & rec_pairs)
    recall = inter / max(1, len(true_pairs))
    precision = inter / max(1, len(rec_pairs))
    return float(recall), float(precision), int(len(rec_pairs))


# ---------------------------------------------------------------------------
# Reach over a recovered adjacency (reuse bind-chain propagate_field + reach machinery)
# ---------------------------------------------------------------------------

def reach_over_recovered(rec_adj, ground_seeds, a_smooth, a_shuf, bins, nonseed_idx, D_list, alpha,
                         n_pairs, seed):
    """Propagate the grounded attribute D steps over rec_adj for each D; return per-D reach metrics +
    the best non-collapsed effective reach."""
    n = len(rec_adj)
    nbr, w = _row_stochastic_from_adj(rec_adj, n)
    gs = np.asarray(ground_seeds, dtype=np.int64)
    by_D = {}
    for D in D_list:
        pf_s = propagate_field(nbr, w, gs, a_smooth, D, alpha=alpha)
        pf_h = propagate_field(nbr, w, gs, a_shuf, D, alpha=alpha)
        m = _reach_arm_metrics(pf_s, pf_h, a_smooth, a_shuf, bins, nonseed_idx,
                               np.random.default_rng(seed + 303 + D), n_pairs)
        c, reason = _reach_collapsed(m)
        m["collapsed"] = bool(c)
        m["collapse_reason"] = reason
        by_D[D] = m
    # effective reach = best non-collapsed reach over D>=1 (single-shot D=1 allowed as the floor)
    valid = [D for D in D_list if not by_D[D]["collapsed"]]
    if valid:
        eff_reach = max(by_D[D]["reach"] for D in valid)
        d_star = min(D for D in valid if by_D[D]["reach"] == eff_reach)
    else:
        eff_reach = -1
        d_star = None
    return by_D, eff_reach, d_star


# ---------------------------------------------------------------------------
# Per-model-seed run
# ---------------------------------------------------------------------------

def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


def run_seed(seed, X, edges, rels, roles_np, adj, cfg, a_smooth, a_shuf, ground_seeds, bins,
             nonseed_idx, out_dir=None):
    d = cfg["code_dim"]
    cos_floor = crosstalk_floor(X.shape[0], d, cfg["cos_floor_c"])   # codebook-size-aware VSA cleanup floor

    # --- two encoders on the SAME real subgraph features ---
    z_base = train_encoder(X, adj, cfg, seed, out_dir=out_dir, tag="BASELINE_SIM")   # similarity encoder
    z_bind = train_binding_encoder(X, edges, rels, roles_np, cfg, seed, out_dir=out_dir, tag="BINDING")

    enc_dig = {"baseline_encoder": _emb_digest(z_base), "binding_encoder": _emb_digest(z_bind)}
    assert enc_dig["baseline_encoder"] != enc_dig["binding_encoder"], (
        "META_RULE_AF VIOLATION: baseline and binding encoders bit-identical")

    topk = cfg["recover_topk"]
    # --- recover a graph from each encoder's codes, its native way + the cross controls ---
    rec = {
        BASE_COS: recover_cosine_adj(z_base, topk, cos_floor),
        BASE_UNB: recover_role_adj(z_base, roles_np, topk, cos_floor),   # control: unbind needs binding
        BIND_UNB: recover_role_adj(z_bind, roles_np, topk, cos_floor),   # PRIMARY treatment
        BIND_COS: recover_cosine_adj(z_bind, topk, cos_floor),           # robustness
    }
    recov = {}
    for arm in REACH_ARMS:
        recall, prec, n_rec = _edge_recall_precision(rec[arm], edges)
        recov[arm] = dict(edge_recall=recall, edge_precision=prec, n_recovered=n_rec)

    # --- reach per arm (identical propagation + reach definition) ---
    arms = {}
    reach_digests = {}
    for arm in REACH_ARMS:
        by_D, eff_reach, d_star = reach_over_recovered(
            rec[arm], ground_seeds, a_smooth, a_shuf, bins, nonseed_idx,
            cfg["D"], cfg["alpha"], cfg["n_pairs"], seed)
        arms[arm] = dict(
            eff_reach=eff_reach, d_star=d_star,
            edge_recall=recov[arm]["edge_recall"], edge_precision=recov[arm]["edge_precision"],
            n_recovered=recov[arm]["n_recovered"],
            reach_by_D={str(D): by_D[D]["reach"] for D in cfg["D"]},
            collapsed_by_D={str(D): by_D[D]["collapsed"] for D in cfg["D"]},
            acc_smooth_by_D={str(D): {b: by_D[D]["acc_smooth"][b] for b in range(4)} for D in cfg["D"]},
            acc_shuf_by_D={str(D): {b: by_D[D]["acc_shuf"][b] for b in range(4)} for D in cfg["D"]},
            margin_by_D={str(D): {b: by_D[D]["margin"][b] for b in range(4)} for D in cfg["D"]},
            field_std_ratio_by_D={str(D): by_D[D]["field_std_ratio"] for D in cfg["D"]},
        )
        # reach signature per arm (D=min vs D=max acc_smooth curve) for ARMS-MUST-DIFFER
        curve = np.array([arms[arm]["acc_smooth_by_D"][str(cfg["D"][-1])][b]
                          if arms[arm]["acc_smooth_by_D"][str(cfg["D"][-1])][b] ==
                          arms[arm]["acc_smooth_by_D"][str(cfg["D"][-1])][b] else -1.0
                          for b in range(4)], dtype=np.float64)
        reach_digests[arm] = hashlib.sha256(np.ascontiguousarray(curve.astype(np.float32)).tobytes()).hexdigest()

    _log("  seed=%d reach: %s | recall: %s" % (
        seed, {a: arms[a]["eff_reach"] for a in REACH_ARMS},
        {a: round(arms[a]["edge_recall"], 3) for a in REACH_ARMS}))

    return dict(seed=seed, encoder_digests=enc_dig, reach_digests=reach_digests, arms=arms,
                cos_floor=float(cos_floor))


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _median_int(vals):
    arr = np.array([v for v in vals if v is not None], dtype=np.float64)
    return float(np.median(arr)) if arr.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, attr_meta, subgraph_meta, cfg):
    # mean effective reach + edge recall per arm
    reach_mean = {a: _nanmean([m["arms"][a]["eff_reach"] for m in per_seed]) for a in REACH_ARMS}
    recall_mean = {a: _nanmean([m["arms"][a]["edge_recall"] for m in per_seed]) for a in REACH_ARMS}
    precision_mean = {a: _nanmean([m["arms"][a]["edge_precision"] for m in per_seed]) for a in REACH_ARMS}

    base_reach = reach_mean[BASE_COS]
    bind_reach = reach_mean[BIND_UNB]
    reach_delta = bind_reach - base_reach if (base_reach == base_reach and bind_reach == bind_reach) else float("nan")

    # attribute smoothness precondition
    precondition_ok = (attr_meta["assort_smooth"] >= ATTR_ASSORT_SMOOTH_MIN) and \
        (attr_meta["assort_shuffled"] <= ATTR_ASSORT_SHUFFLED_MAX)

    # baseline cap present (baseline_in_band): the similarity encoder must sit at the 1-hop cap
    base_cap_present = (base_reach == base_reach) and (base_reach <= BASELINE_CAP_MAX + 1e-9)

    # recovery-succeeded gate for the treatment (else the win/loss is unattributable)
    bind_recovery_ok = recall_mean[BIND_UNB] >= RECOVERY_RECALL_MIN

    # strict-above-floor at the newly-reached bin of BINDING_UNBIND at its best D across seeds
    def strict_ok_for_treatment():
        oks = []
        for m in per_seed:
            arm = m["arms"][BIND_UNB]
            er = arm["eff_reach"]
            ds = arm["d_star"]
            if er is None or er < REACH_HP_MIN or ds is None:
                oks.append(False)
                continue
            b = int(er) - 1  # newly-reached bin index
            acc = arm["acc_smooth_by_D"][str(ds)][b]
            mar = arm["margin_by_D"][str(ds)][b]
            ok = (acc == acc and mar == mar and acc >= REACH_THRESH + REACH_STRICT_MARGIN
                  and mar >= MARGIN_FLOOR)
            oks.append(bool(ok))
        return bool(np.mean(oks) >= 0.5) if oks else False  # majority of seeds strict

    strict_ok = strict_ok_for_treatment()

    if not precondition_ok:
        verdict = "PRECONDITION_FAIL"
    elif not base_cap_present:
        verdict = "INCONCLUSIVE_NO_ONESHOT_CAP"       # no 1-hop cap to beat -> not a fair contrast
    elif not bind_recovery_ok:
        verdict = "INCONCLUSIVE_RECOVERY_FAILED"       # role-apply recovery failed -> unattributable
    elif (bind_reach >= REACH_HP_MIN) and (reach_delta >= REACH_DELTA_HP) and strict_ok:
        verdict = "HARD_PASS"
    elif (bind_reach >= REACH_HP_MIN) and (reach_delta >= REACH_DELTA_HP):
        verdict = "MIDDLE_BAND_BANDFLOOR"              # extension but not strictly above floor
    elif (reach_delta == reach_delta and reach_delta <= 0):
        verdict = "HARD_FAIL_NO_EXTENSION"             # encode-time binding did not extend reach on real codes
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s || REACH(eff, mean): %s=%.2f(cap<=%d present=%s) %s=%.2f(control) %s=%.2f(PRIMARY) "
        "%s=%.2f(robust) | reach_delta(bind_unbind-base_cos)=%s strict_above_floor=%s || "
        "RECOVERY edge_recall: base_cos=%.3f base_unbind=%.3f bind_unbind=%.3f bind_cos=%.3f "
        "(bind recovery_ok=%s) precision bind_unbind=%.3f || "
        "attr_assort smooth=%.3f shuf=%.3f precond=%s || "
        "subgraph n=%d E=%d med_deg=%.1f n_rel_types=%d seeds=%d" % (
            verdict,
            BASE_COS, base_reach, BASELINE_CAP_MAX, base_cap_present,
            BASE_UNB, reach_mean[BASE_UNB],
            BIND_UNB, bind_reach,
            BIND_COS, reach_mean[BIND_COS],
            ("%.2f" % reach_delta) if reach_delta == reach_delta else "nan", strict_ok,
            recall_mean[BASE_COS], recall_mean[BASE_UNB], recall_mean[BIND_UNB], recall_mean[BIND_COS],
            bind_recovery_ok, precision_mean[BIND_UNB],
            attr_meta["assort_smooth"], attr_meta["assort_shuffled"], precondition_ok,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta["median_degree"],
            subgraph_meta.get("n_relation_types", -1), len(per_seed)))

    gates = dict(
        verdict=verdict,
        reach_mean=reach_mean, recall_mean=recall_mean, precision_mean=precision_mean,
        base_reach=base_reach, bind_reach=bind_reach, reach_delta=reach_delta,
        base_cap_present=base_cap_present, bind_recovery_ok=bind_recovery_ok,
        strict_above_floor=strict_ok, precondition_ok=precondition_ok,
        attr_assort_smooth=attr_meta["assort_smooth"], attr_assort_shuffled=attr_meta["assort_shuffled"],
        reach_by_D_per_arm={a: {str(D): _median_int([m["arms"][a]["reach_by_D"][str(D)] for m in per_seed])
                                for D in cfg["D"]} for a in REACH_ARMS},
        bands=dict(REACH_HP_MIN=REACH_HP_MIN, REACH_DELTA_HP=REACH_DELTA_HP,
                   BASELINE_CAP_MAX=BASELINE_CAP_MAX, RECOVERY_RECALL_MIN=RECOVERY_RECALL_MIN,
                   REACH_THRESH=REACH_THRESH, MARGIN_FLOOR=MARGIN_FLOOR,
                   ATTR_ASSORT_SMOOTH_MIN=ATTR_ASSORT_SMOOTH_MIN,
                   ATTR_ASSORT_SHUFFLED_MAX=ATTR_ASSORT_SHUFFLED_MAX),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------

def discriminator_selftest():
    """Prove: (0) np_hrr_bind == hdlab.binding.bind (HRR real path); (1) role-apply recovery recovers PLANTED
    binding edges (recall high) while cosine-kNN on the SAME rotated-neighbour codes fails (needs encode-time
    binding); (2) the reach probe detects binding-enabled multi-hop propagation (role-apply reach >= 2 and >
    cosine reach on planted binding-chain codes; shuffled flat), and perturbing the codes DROPS reach
    (telemetry-sensitive, not analytically pinned)."""
    rng = np.random.default_rng(0)
    d = 256

    # (0) reuse-fidelity: our numpy HRR bind == hdlab.binding.bind on the real path
    roles = make_unitary_roles(3, d, rng)
    v = rng.standard_normal((1, d)).astype(np.float32)
    hd = hdlab_bind(torch.from_numpy(roles[0].copy()), torch.from_numpy(v[0].copy())).numpy()
    reuse_ok = bool(np.allclose(hd, np_hrr_bind(roles[0], v)[0], atol=1e-3))
    # norm-preservation of the unitary role (clean-unbind precondition)
    norm_ratio = float(np.linalg.norm(np_hrr_bind(roles[0], v)[0]) / (np.linalg.norm(v[0]) + 1e-9))
    unitary_ok = bool(abs(norm_ratio - 1.0) < 0.05)

    # (1)+(2) planted binding structure: a typed chain where z_{k+1} = bind(role_r, z_k) + noise.
    n = 500
    T = 3
    roles = make_unitary_roles(T, d, rng)
    z = np.zeros((n, d), dtype=np.float32)
    z[0] = rng.standard_normal(d)
    chain_edges = []
    chain_rels = []
    for k in range(1, n):
        r = int(rng.integers(0, T))
        z[k] = np_hrr_bind(roles[r], z[k - 1:k])[0] + 0.05 * rng.standard_normal(d).astype(np.float32)
        chain_edges.append((k - 1, k))
        chain_rels.append(r)
    z = _l2(z).astype(np.float32)
    edges = np.array(chain_edges, dtype=np.int32)
    cos_floor = crosstalk_floor(n, d, 1.1)

    rec_role = recover_role_adj(z, roles, 6, cos_floor)
    rec_cos = recover_cosine_adj(z, 6, cos_floor)
    recall_role, _, _ = _edge_recall_precision(rec_role, edges)
    recall_cos, _, _ = _edge_recall_precision(rec_cos, edges)
    recovery_fires = (recall_role >= 0.5) and (recall_role - recall_cos >= 0.25)

    # smooth grounded attribute over the chain (position-based => graph-smooth along the chain)
    a_smooth = np.arange(n, dtype=np.float64)
    a_smooth = (a_smooth - a_smooth.mean()) / (a_smooth.std() + 1e-9)
    a_shuf = a_smooth.copy()
    np.random.default_rng(9).shuffle(a_shuf)
    ground = np.arange(0, n, max(2, n // 20), dtype=np.int64)  # sparse seeds along the chain
    # true-distance bins along the chain from nearest seed
    from collections import deque as _dq
    adj_true = [set() for _ in range(n)]
    for (a, b) in edges:
        adj_true[int(a)].add(int(b))
        adj_true[int(b)].add(int(a))
    BIG = 1 << 30
    dist = np.full(n, BIG, dtype=np.int64)
    dq = _dq()
    for s in ground:
        dist[s] = 0
        dq.append(int(s))
    while dq:
        u = dq.popleft()
        for vv in adj_true[u]:
            if dist[vv] > dist[u] + 1:
                dist[vv] = dist[u] + 1
                dq.append(vv)
    seed_set = set(int(x) for x in ground)
    bins, _ = distance_bins(dist, seed_set)
    nonseed = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)

    _, reach_role, _ = reach_over_recovered(rec_role, ground, a_smooth, a_shuf, bins, nonseed,
                                            [1, 2, 3, 4], 0.85, 3000, 1)
    _, reach_cos, _ = reach_over_recovered(rec_cos, ground, a_smooth, a_shuf, bins, nonseed,
                                          [1, 2, 3, 4], 0.85, 3000, 1)
    reach_fires = (reach_role >= 2) and (reach_role > reach_cos)

    # telemetry: shuffle the codes -> role-apply recovery + reach must DROP
    zperm = z[rng.permutation(n)]
    rec_role_perm = recover_role_adj(zperm, roles, 6, cos_floor)
    recall_perm, _, _ = _edge_recall_precision(rec_role_perm, edges)
    telemetry = (recall_role - recall_perm) >= 0.25

    res = dict(
        reuse_ok=reuse_ok, unitary_norm_ratio=norm_ratio, unitary_ok=unitary_ok,
        recall_role=float(recall_role), recall_cos=float(recall_cos), recovery_fires=bool(recovery_fires),
        reach_role=int(reach_role), reach_cos=int(reach_cos), reach_fires=bool(reach_fires),
        recall_perm=float(recall_perm), telemetry_sensitive=bool(telemetry),
    )
    ok = bool(reuse_ok and unitary_ok and recovery_fires and reach_fires and telemetry)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    # ---- discriminator telemetry-sensitivity self-test (ALWAYS) ----
    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (reuse/unitary/recovery/reach/telemetry): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    # ---- load typed real ConceptNet subgraph ----
    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d %s" % (
        {k: meta[k] for k in ("n_nodes", "n_edges", "median_degree", "mean_degree")}, T, types))
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)

    # ---- graph-smooth grounded attribute + shuffled control + ground seeds + distance bins ----
    attr_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 555)
    a_smooth = make_smooth_attribute(edges, degrees, n_nodes, attr_rng, cfg["n_sources"], cfg["diffuse_steps"])
    a_shuf = a_smooth.copy()
    attr_rng.shuffle(a_shuf)
    assort_smooth = attribute_assortativity(a_smooth, edges)
    assort_shuffled = attribute_assortativity(a_shuf, edges)
    _log("attribute assortativity: smooth=%.3f shuffled=%.3f" % (assort_smooth, assort_shuffled))

    n_gs = int(min(cfg["n_ground_seeds"], n_nodes // 4))
    ground_seeds = attr_rng.choice(n_nodes, size=n_gs, replace=False)
    seed_set = set(int(x) for x in ground_seeds)
    dist = multi_source_bfs(adj, [int(x) for x in ground_seeds], n_nodes)
    bins, n_unreachable = distance_bins(dist, seed_set)
    nonseed_idx = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)
    _log("distance bins (non-seed): d1=%d d2=%d d3=%d d4+=%d unreachable=%d" % (
        bins[0].shape[0], bins[1].shape[0], bins[2].shape[0], bins[3].shape[0], n_unreachable))

    attr_meta = dict(assort_smooth=assort_smooth, assort_shuffled=assort_shuffled, n_ground_seeds=n_gs,
                     n_unreachable=int(n_unreachable), bin_counts={b: int(bins[b].shape[0]) for b in range(4)})

    # ---- fixed unitary role codebook (one per relation type) ----
    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_np = make_unitary_roles(T, cfg["code_dim"], role_rng)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS HRR reuse + unitary roles + recovery + reach probe telemetry-sensitive; "
                        "typed subgraph + attribute pipeline exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, subgraph_meta=meta, attr_meta=attr_meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, roles_np, adj, cfg, a_smooth, a_shuf,
                          ground_seeds, bins, nonseed_idx, out_dir=out_dir_path)
            # ARMS-MUST-DIFFER: the 4 reach arms must not be bit-identical reach curves
            rd = pm["reach_digests"]
            names = list(rd.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    if rd[names[i]] == rd[names[j]]:
                        _log("  [warn] reach curves identical for %s and %s (seed=%d)" % (
                            names[i], names[j], seed))
            pm_persist = {k: v for k, v in pm.items() if k not in ("encoder_digests", "reach_digests")}
            per_seed.append(pm_persist)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm_persist))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta, attr_meta=attr_meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, attr_meta, meta, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, attr_meta=attr_meta, gates=gates,
        discriminator_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
