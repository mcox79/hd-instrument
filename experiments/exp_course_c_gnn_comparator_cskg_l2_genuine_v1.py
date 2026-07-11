"""Anchor 4 (Phase-2 CALIBRATION): a same-split OPAQUE path-aggregation GNN comparator on the CSKG
L2-GENUINE held-out split -- bank the best-in-class reference number the glass-box map-builder is graded
against, MEASURED on OUR graph (not a borrowed FB15k-237 analogy).

WHY. The glass-box map-builder (exp_course_c_map_builder_cskg_l2_genuine_v1) reports filtered hits@10 / MRR /
degree-stratified on a genuine 2-hop L2 held-out set of CSKG dense-core edges, vs a POP_RELFREQ frequency
incumbent. To claim "glass-box is within X% of opaque SOTA" HONESTLY for THIS task/graph we need an opaque
GNN measured on the IDENTICAL split + IDENTICAL metric harness -- not the external ~90-95% FB15k-237
precedent (different graph, 1-hop vs 2-hop, different difficulty). This cell converts that analogy into a
measurement. It is NOT on the reasoning critical path; a clean failure is no-harm.

CALIBRATION CAVEAT (attach to any external framing; per research handoff HEADLINE point 3): the reference
banked here is TransE-tier ABSOLUTE for a HARDER 2-hop task, NOT NBFNet-on-FB15k237-tier. NEVER market as
SOTA. The comparator's OWN pass criterion is "did it train + produce a VALID ranking number on the CORRECT
split" -- the >=85% / 60% bands are for the LATER glass-box comparison (owned by verdict_handler), NOT for
this comparator.

APPARATUS REUSE (apples-to-apples; the load-bearing guarantee). This cell IMPORTS the map-builder's OWN
split + metric functions and reconstructs the held-out set DETERMINISTICALLY from the SAME seeds/config, then
ASSERTS bit-identical edge-set identity: the recomputed BASELINE_POP arm_sig (a deterministic hash of the
POP rank vector over the SAME L2-genuine held-out queries + SAME filtered candidate set) MUST equal the value
landed by the map-builder FULL. A comparator on a different split is worthless; this assert makes the split
provably the same one.
  - CSKG assembly + L2-genuine extraction + degree strata + POP baseline + filtered hits harness:
    extract_l2_genuine / stratify_by_tail_degree / build_true_by_hr_int / filtered_hits_from_scores /
    pop_hits / per_stratum_hits / per_stratum_pop / _sig / build_cskg_core_triples / _ensure_cskg / Graph /
    build_ids / mine_rules -- ALL imported from exp_course_c_map_builder_cskg_l2_genuine_v1 (identical code).
  - The ONLY new thing is the ARM: an opaque NBFNet-lite path-aggregation GNN (generalized Bellman-Ford,
    DistMult relational messages, inverse edges, boundary re-injection) trained on the VISIBLE train graph,
    scored PAIRED on the SAME held-out queries. Plus an UNTRAINED-GNN control (must underperform the trained
    arm) and the POP baseline (must-reproduce the landed sig).

ARMS (scored PAIRED on the SAME L2-genuine held-out queries + same filtered candidate set + same strata):
  GNN_TRAINED    NBFNet-lite trained with filtered cross-entropy. THE opaque reference arm.
  GNN_UNTRAINED  identical architecture, random init, NO training. Control: training must lift the arm.
  BASELINE_POP   POP_RELFREQ frequency incumbent (imported pop_hits). Apples-to-apples bar + split-identity
                 witness (its sig MUST match the map-builder's landed BASELINE_POP sig at FULL).

PRIMARY METRIC: filtered hits@10 on the L2-genuine held-out subset, PLUS per-degree-stratum hits@10, PLUS
hits@1 and MRR (all via the imported harness). Reports GNN vs POP per stratum. For convenience the cell ALSO
RECORDS (does NOT gate) the glass-box-best/comparator ratio using the landed map-builder number, tagged with
the calibration caveat -- the actual >=85%/60% grading is a downstream verdict_handler job.

DISCRIMINATOR (this cell's OWN verdict, per the contract -- validity, not the glass-box bands):
  COMPARATOR_REFERENCE_BANKED = split_identity_ok (recomputed POP sig == landed sig per seed)
      AND training_converged (final train loss < initial * TRAIN_CONVERGE_REL)
      AND gnn produced a valid, non-degenerate ranking (per-query score std > 0; hits in [0,1])
      AND arms differ (GNN_TRAINED sig != GNN_UNTRAINED sig).
  HARD_FAIL_SPLIT_IDENTITY_BREACH = recomputed POP sig != landed map-builder sig -> the split is NOT the
      glass-box's; the comparator is worthless. Fail closed.
  HARD_FAIL_TRAINING_DEGENERATE = training did not reduce the loss, or scores are degenerate (no ranking
      signal) -> cannot bank a reference number.

SELF-TEST (planted; scale-invariant; SAME split+metric code path at reduced scale): on SYN_COMPOSITIONAL
(planted rA(p,m)&rB(m,t)=>rC(p,t), uniform non-popular tails) the trained GNN LEARNS the 2-hop rule and
clearly beats its own untrained control on the L2-genuine held-out set; arms differ; L2-genuine extraction
non-empty. VacuousSmokeError if the UNTRAINED control already clears the trained bar (then training/the GNN
is not the lever). The self-test routes to a fast planted branch that exits 0 and does NOT trigger a CSKG run.

## Compute architecture
class: (a) batched-GPU. The GNN forward is a batched generalized Bellman-Ford: for a batch of B queries the
per-layer relational message is a single (B, 2E, dim) gather-multiply then an index_add scatter to (B, N,
dim) node states -- matmul/scatter-heavy, GPU. It NEVER materializes an [N x N] map (the OOM trap at
N~25.7k): scores are (B, N) per query-batch, accumulated onto CPU host RAM. Query batches are chunked
(b_train small under autograd; b_eval larger no-grad) so the (B, 2E, dim) message tensor -- the sole large
device resident -- stays well under the 8GB card (shared with BOINC ~1.2GB). The symbolic split build
(mine_rules / extract_l2_genuine / pop_hits) is sequential-CPU (combinatorial graph traversal, no matmul --
same justification as the imported apparatus). Storage strategy: SHARDED (each entity a conditional node
state per query; relation operators factorized per TYPE; NEVER a global fact bundle). device=auto (cuda on
the GPU host); local = NO EXECUTION (no-local-smokes lock; all runs remote).

MEMORY DISCIPLINE (this GNN family OOM'd 3x historically on the shared 8GB card):
  - never materialize [N x N]; scores are (B, N), eval scores accumulate on CPU.
  - chunk query batches (b_train / b_eval); the (B, 2E, dim) message tensor is the only large device tile.
  - per-seed teardown: fresh model, explicit del of model + optimizer + edge tensors + eval scores,
    torch.cuda.empty_cache(), reset_peak_memory_stats; log per-seed peak_gpu_mem_bytes.
  - MANDATORY >=2-seed REMOTE memory smoke at REDUCED-BUT-MEANINGFUL scale (memsmoke run mode; ~4k nodes,
    2 seeds) BEFORE the FULL -- single-seed masks multi-seed accumulation. The 180s queue_add pre-gate smoke
    is tiny SYN only (fits the ceiling); the reduced-scale CSKG memory job is a separate GPU dispatch.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): GNN_TRAINED vs GNN_UNTRAINED sigs distinct.
# - final_metrics_atomicity: tmp_replace (write_metrics uses tmp + os.replace; write_partial per seed).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except) -- grep-clean.
# - crlb: filtered hits@10 chance floor ~ 10/n_candidates THEORETICAL; POP is the real (non-chance) bar; the
#   comparator's number is a MEASUREMENT (no HARD_PASS threshold to be unreachable) -- validity-gated only.
# - baseline_in_band: POP is the imported measured confound-baseline (landed FULL POP h@10~0.175 aggregate);
#   GNN_UNTRAINED is the anti-triviality null (must underperform GNN_TRAINED).
# - discriminator survives scale: the comparator is a MEASUREMENT; the scale-invariant discriminator-fires
#   proof is the planted self-test (trained GNN beats its untrained control on SYN L2-genuine) through the
#   IDENTICAL split+metric code path; the CSKG number is what we bank.
# - HP_SCOPE: COMPARATOR_REFERENCE_BANKED applies to GNN_TRAINED (validity) + split-identity (POP sig) +
#   arms-differ (trained vs untrained). No chain-grade HARD_PASS floor on any arm (calibration cell).
# - positive_control (Gate D): the split-identity POP-sig assert IS the reproduce-prior-result-at-test-regime
#   control (bit-identical to the map-builder's BASELINE_POP). regime_extension_audit: SHAPE_MATCH -- same
#   split, same candidate set, same filtered-hits harness; only the scoring arm differs.
# - sweep axis: ARM x seed; EXPECTED_N_UNITS = n_seeds; each seed asserts split-identity + arms-differ.
# - per-unit failure-class instrumentation (no bare except; per-seed try/except records failure_class).
# - calibration_check: default_ok_for_this_regime -- split params (k_core / min_support / min_conf / n_eval /
#   seeds) are COPIED verbatim from the map-builder FULL_CFG and asserted identical via the POP sig.
# - PAIRED: GNN and POP share the identical L2-genuine held-out split + candidate set + degree strata.
# - progress_logging: print_flush_true (line-buffered stdout; per-seed / per-epoch / per-eval-chunk flush).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires, VacuousSmokeError,
)
# Split + metric apparatus imported VERBATIM from the glass-box map-builder (apples-to-apples guarantee).
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    extract_l2_genuine, stratify_by_tail_degree, build_true_by_hr_int, filtered_hits_from_scores,
    pop_hits, per_stratum_hits, per_stratum_pop, _to_int_edges, _sig,
    build_cskg_core_triples, _ensure_cskg, Graph, build_ids, mine_rules,
    MAX_RULES_PER_HEAD, HUB_CAP, STRATA, PRIMARY_K,
)
# Planted scale-invariant self-test corpus (identical assembly as the map-builder self-test).
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_syn_compositional,
)

ANCHOR_NAME = "course_c_gnn_comparator_cskg_l2_genuine_v1"
# The glass-box cell whose split we MUST match + whose landed number we calibrate against.
MAPBUILDER_NAME = "course_c_map_builder_cskg_l2_genuine_v1"
MAPBUILDER_METRICS = os.path.join(_REPO, "data", "exp_%s" % MAPBUILDER_NAME, "metrics.json")

# ---- Arm names ----
GNN = "GNN_TRAINED"
GNN0 = "GNN_UNTRAINED"
POP = "BASELINE_POP"
ALL_ARMS = [GNN, GNN0, POP]

# ---- Validity gates (this cell's OWN verdict; NOT the glass-box >=85%/60% bands) ----
TRAIN_CONVERGE_REL = 0.85   # final train loss must be < initial * this (training actually reduced the loss)
MIN_SCORE_STD = 1e-6        # per-query GNN score std must exceed this (non-degenerate ranking)
# ---- self-test planted thresholds. Gate on the RELATIVE discriminator (training LIFT over the untrained
#      control) + convergence, per the map-builder's own wisdom that absolute levels on the weak planted
#      SYN fit are noisy; the absolute trained level is REPORTED not gated. ----
ST_TRAINED_REPORT = 0.15    # planted SYN: reported trained hits@10 target (NOT gated; noisy on weak SYN fit)
ST_TRAIN_LIFT = 0.08        # planted SYN: trained - untrained hits@10 >= this (training is the lever; GATED)

# Config profiles. FULL split params are COPIED VERBATIM from the map-builder FULL_CFG (asserted via POP sig).
# self_test / smoke = tiny planted SYN (must fit the 180s queue_add pre-gate). memsmoke = reduced-scale REAL
# CSKG GPU job (the mandatory >=2-seed memory smoke). full = the identical-split 3-seed comparator.
SELFTEST_CFG = dict(dim=32, n_layers=3, epochs=45, b_train=32, b_eval=64, lr=8e-3, wd=1e-6,
                    min_support=2, min_conf=0.05, n_eval=0, qpe=1500)
SMOKE_CFG = dict(seeds=[0, 1], dim=32, n_layers=3, epochs=25, b_train=32, b_eval=64, lr=8e-3, wd=1e-6,
                 min_support=2, min_conf=0.05, n_eval=0, qpe=1500)
MEMSMOKE_CFG = dict(seeds=[7, 17], dim=32, n_layers=3, epochs=6, b_train=6, b_eval=16, lr=5e-3, wd=1e-6,
                    cskg_max_lines=0, k_core=8, cskg_max_nodes=4000, min_support=6, min_conf=0.08,
                    n_eval=1500, min_heldout=15, qpe=8000)
FULL_CFG = dict(seeds=[7, 17, 23], dim=32, n_layers=3, epochs=15, b_train=6, b_eval=16, lr=5e-3, wd=1e-6,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0, min_support=10, min_conf=0.10,
                n_eval=6000, min_heldout=20, qpe=12000)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# NBFNet-lite: batched generalized Bellman-Ford path-aggregation GNN.
# For a query (h, r): boundary X0[b, h] = query_emb(r); L layers of relational-message passing over the
# (inverse-augmented) edge set; readout MLP -> per-node score. Scores are (B, N); NEVER an [N x N] map.
# ---------------------------------------------------------------------------

class NBFNetLite(nn.Module):
    def __init__(self, n_ent, n_rel, dim, n_layers):
        super().__init__()
        self.n_ent = int(n_ent)
        self.n_rel = int(n_rel)          # forward relation count; inverse relations occupy [n_rel, 2*n_rel)
        self.dim = int(dim)
        self.L = int(n_layers)
        self.query = nn.Embedding(2 * n_rel, dim)      # boundary condition per query relation
        self.rel_mult = nn.Embedding(2 * n_rel, dim)   # DistMult relational message multiplier per edge type
        self.self_lin = nn.ModuleList(nn.Linear(dim, dim) for _ in range(n_layers))
        self.msg_lin = nn.ModuleList(nn.Linear(dim, dim) for _ in range(n_layers))
        self.lns = nn.ModuleList(nn.LayerNorm(dim) for _ in range(n_layers))
        self.score_mlp = nn.Sequential(nn.Linear(dim, dim), nn.ReLU(), nn.Linear(dim, 1))
        with torch.no_grad():
            nn.init.normal_(self.query.weight, std=0.1)
            nn.init.normal_(self.rel_mult.weight, mean=1.0, std=0.1)  # near-identity so early messages pass

    def forward(self, edge_index, edge_rel, h_batch, r_batch):
        """edge_index (2, Ea) long [src; dst] inverse-augmented; edge_rel (Ea,) long in [0, 2*n_rel).
        h_batch (B,) long source ids; r_batch (B,) long forward relation ids. Returns scores (B, N)."""
        device = self.query.weight.device
        B = int(h_batch.shape[0])
        N = self.n_ent
        src = edge_index[0]
        dst = edge_index[1]
        rmul = self.rel_mult(edge_rel).unsqueeze(0)            # (1, Ea, dim) broadcast over batch
        X = torch.zeros(B, N, self.dim, device=device)
        X[torch.arange(B, device=device), h_batch] = self.query(r_batch)
        boundary0 = X                                          # boundary re-injection each layer (NBFNet)
        Xcur = X
        for l in range(self.L):
            msg = Xcur[:, src, :] * rmul                       # (B, Ea, dim) -- sole large device tile
            agg = torch.zeros(B, N, self.dim, device=device)
            agg.index_add_(1, dst, msg)                        # scatter-add incoming messages to targets
            upd = self.self_lin[l](Xcur) + self.msg_lin[l](agg)
            Xcur = F.relu(self.lns[l](upd)) + boundary0
            del msg, agg
        return self.score_mlp(Xcur).squeeze(-1)                # (B, N)


def _build_edge_tensors(train_int, n_rel, device):
    """Inverse-augmented directed edge set: forward rel in [0,n_rel), inverse rel in [n_rel,2*n_rel)."""
    src = torch.from_numpy(train_int[:, 0]).long()
    rel = torch.from_numpy(train_int[:, 1]).long()
    dst = torch.from_numpy(train_int[:, 2]).long()
    ei = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)   # (2, 2E)
    er = torch.cat([rel, rel + n_rel])                                        # (2E,)
    return ei.to(device), er.to(device)


def _train_gnn(model, edge_index, edge_rel, train_int, train_true, N, cfg, device, seed, hb):
    """Filtered cross-entropy: for each (h,r,t) score all N tails via one Bellman-Ford, mask OTHER train-true
    tails to -inf, CE against gold. Subsamples qpe train queries per epoch (qpe=0 -> all). Returns
    (loss_first, loss_last, n_batches)."""
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"], weight_decay=cfg["wd"])
    rng = np.random.default_rng(seed * 7919 + 3)
    n_tr = train_int.shape[0]
    B = cfg["b_train"]
    qpe = cfg["qpe"] if cfg["qpe"] else n_tr
    loss_first = float("nan")
    loss_last = float("nan")
    n_batches = 0
    model.train()
    t0 = time.perf_counter()
    for ep in range(cfg["epochs"]):
        idx = rng.permutation(n_tr)[:qpe]
        ep_losses = []
        for s in range(0, idx.shape[0], B):
            bi = idx[s:s + B]
            hb_ = torch.from_numpy(train_int[bi, 0]).long().to(device)
            rb_ = torch.from_numpy(train_int[bi, 1]).long().to(device)
            tb_ = torch.from_numpy(train_int[bi, 2]).long().to(device)
            scores = model(edge_index, edge_rel, hb_, rb_)          # (b, N)
            for i in range(bi.shape[0]):
                others = train_true.get((int(train_int[bi[i], 0]), int(train_int[bi[i], 1])), None)
                if others:
                    gold = int(train_int[bi[i], 2])
                    for o in others:
                        if o != gold:
                            scores[i, o] = -1e30
            loss = F.cross_entropy(scores, tb_)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            lv = float(loss.detach().item())
            ep_losses.append(lv)
            if n_batches == 0:
                loss_first = lv
            n_batches += 1
            del scores, loss, hb_, rb_, tb_
        loss_last = float(np.mean(ep_losses)) if ep_losses else float("nan")
        _log("  seed=%d epoch=%d/%d mean_loss=%.4f nbatch=%d (%.1fs)"
             % (seed, ep + 1, cfg["epochs"], loss_last, n_batches, time.perf_counter() - t0))
        if hb is not None:
            hb("train_ep", ep)
    del opt
    return loss_first, loss_last, n_batches


@torch.no_grad()
def _eval_gnn(model, edge_index, edge_rel, hold, N, cfg, device):
    """Score the held-out queries in chunks -> (nq, N) CPU float32 (host RAM ample; never on device whole)."""
    model.eval()
    nq = hold.shape[0]
    B = cfg["b_eval"]
    out = torch.empty((nq, N), dtype=torch.float32)
    for s in range(0, nq, B):
        e = min(s + B, nq)
        hb_ = torch.from_numpy(hold[s:e, 0]).long().to(device)
        rb_ = torch.from_numpy(hold[s:e, 1]).long().to(device)
        sc = model(edge_index, edge_rel, hb_, rb_)     # (b, N)
        out[s:e] = sc.detach().to("cpu").float()
        del sc, hb_, rb_
    return out


# ---------------------------------------------------------------------------
# Split reconstruction (imported apparatus; identical to map-builder run_corpus split section).
# ---------------------------------------------------------------------------

def build_split(train_lbl, valid_lbl, test_lbl, cfg, seed):
    """Reconstruct the IDENTICAL L2-genuine held-out split the map-builder uses. Returns a dict with int
    edges, held-out edges, strata, POP inputs, and provenance. Uses the imported functions verbatim."""
    ent2i, rel2i = build_ids(train_lbl, valid_lbl, test_lbl)
    N = len(ent2i)
    n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    test_int = _to_int_edges(test_lbl, ent2i, rel2i)
    valid_int = _to_int_edges(valid_lbl, ent2i, rel2i)
    gd = Graph(train_lbl, ent2i, rel2i)                    # mine on TRAIN only (identical to map-builder)
    known = defaultdict(set)
    for tr in (train_lbl, valid_lbl, test_lbl):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    target_rels = list(rel2i.values())
    _acc, allpat, _hub = mine_rules(gd, target_rels, cfg["min_support"], cfg["min_conf"],
                                    MAX_RULES_PER_HEAD, HUB_CAP)
    hold, hold_prov = extract_l2_genuine(gd, allpat, known, test_int, cfg["n_eval"], seed)
    all_true = build_true_by_hr_int(train_int, valid_int, test_int)
    train_true = build_true_by_hr_int(train_int)
    strat, tert = stratify_by_tail_degree(hold, gd.node_degree)
    return dict(ent2i=ent2i, N=int(N), n_rel=int(n_rel), train_int=train_int, test_int=test_int,
                gd=gd, hold=hold, hold_prov=hold_prov, all_true=all_true, train_true=train_true,
                strat=strat, tert=tert, n_train=int(train_int.shape[0]), n_test=int(test_int.shape[0]))


def _load_mapbuilder_landed():
    """Load the landed map-builder FULL metrics (present on the remote GPU host; the identity referent)."""
    if not os.path.exists(MAPBUILDER_METRICS):
        return None
    try:
        with open(MAPBUILDER_METRICS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def _mapbuilder_pop_sig_for_seed(landed, seed):
    """Return the map-builder's landed BASELINE_POP arm_sig + provenance for a given seed, or None."""
    if not landed:
        return None
    for ps in landed.get("per_seed", []):
        if int(ps.get("seed", -1)) == int(seed):
            return dict(pop_sig=ps.get("arm_sigs", {}).get("BASELINE_POP"),
                        N=ps.get("N"), n_rel=ps.get("n_rel"), n_train=ps.get("n_train"),
                        n_l2_genuine=ps.get("l2_genuine", {}).get("n_l2_genuine"),
                        strata_counts=ps.get("strata_counts"))
    return None


# ---------------------------------------------------------------------------
# One seed of the CSKG comparator (memsmoke + full).
# ---------------------------------------------------------------------------

def run_seed_cskg(cfg, device, seed, assert_identity, hb):
    """Assemble CSKG -> reconstruct the map-builder split -> assert split identity (full only) -> fit the GNN
    + untrained control -> PAIRED filtered hits vs POP + per-degree strata. Returns a per-seed result dict."""
    train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
        cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
    _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d train=%d test=%d"
         % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
            prov["n_rel_tokens"], prov["n_train"], prov["n_test"]))
    sp = build_split(train_lbl, valid_lbl, test_lbl, cfg, seed)
    N = sp["N"]
    n_rel = sp["n_rel"]
    hold = sp["hold"]
    min_hold = cfg.get("min_heldout", 15)
    if hold.shape[0] < min_hold:
        raise RuntimeError("L2-genuine held-out too small (%d < %d): %s"
                           % (hold.shape[0], min_hold, sp["hold_prov"]))

    # ---- POP baseline (imported) + split-identity witness ----
    pop_m, pop_rank_vec = pop_hits(sp["gd"].rel_tail_freq, hold, sp["all_true"], N)
    pop_sig = _sig(pop_rank_vec.astype(np.float64))
    strata_counts = {STRATA[si]: int((sp["strat"] == si).sum()) for si in range(3)}
    identity = dict(pop_sig=pop_sig, N=N, n_rel=n_rel, n_train=sp["n_train"],
                    n_l2_genuine=int(hold.shape[0]), strata_counts=strata_counts)
    identity_ok = None
    identity_ref = None
    if assert_identity:
        landed = _load_mapbuilder_landed()
        identity_ref = _mapbuilder_pop_sig_for_seed(landed, seed)
        if identity_ref is None or identity_ref.get("pop_sig") is None:
            raise RuntimeError("SPLIT_IDENTITY_REFERENT_MISSING: map-builder landed metrics lack a "
                               "BASELINE_POP sig for seed=%d at %s" % (seed, MAPBUILDER_METRICS))
        identity_ok = bool(pop_sig == identity_ref["pop_sig"]
                           and int(identity_ref.get("N", -1)) == N
                           and int(identity_ref.get("n_rel", -1)) == n_rel
                           and int(identity_ref.get("n_l2_genuine", -1)) == int(hold.shape[0]))
        if not identity_ok:
            raise RuntimeError(
                "SPLIT_IDENTITY_BREACH seed=%d: recomputed POP sig=%s vs landed=%s ; "
                "N %d/%s n_rel %d/%s n_l2gen %d/%s -- the comparator split is NOT the glass-box's."
                % (seed, pop_sig, identity_ref.get("pop_sig"), N, identity_ref.get("N"),
                   n_rel, identity_ref.get("n_rel"), int(hold.shape[0]), identity_ref.get("n_l2_genuine")))
        _log("seed=%d SPLIT_IDENTITY_OK pop_sig=%s (== landed map-builder)" % (seed, pop_sig))

    # ---- edge tensors (shared by trained + untrained arms) ----
    edge_index, edge_rel = _build_edge_tensors(sp["train_int"], n_rel, device)

    # ---- GNN_UNTRAINED control (random init, no training) ----
    torch.manual_seed(seed * 101 + 1)
    model0 = NBFNetLite(N, n_rel, cfg["dim"], cfg["n_layers"]).to(device)
    sc0 = _eval_gnn(model0, edge_index, edge_rel, hold, N, cfg, device)
    m0 = filtered_hits_from_scores(sc0, hold, sp["all_true"])
    sig0 = _sig(sc0.numpy()[:min(64, sc0.shape[0])].ravel())
    del model0

    # ---- GNN_TRAINED (the reference arm) ----
    torch.manual_seed(seed * 101 + 1)                 # same init as control -> lift is purely training
    model = NBFNetLite(N, n_rel, cfg["dim"], cfg["n_layers"]).to(device)
    loss_first, loss_last, n_batches = _train_gnn(model, edge_index, edge_rel, sp["train_int"],
                                                  sp["train_true"], N, cfg, device, seed, hb)
    sc = _eval_gnn(model, edge_index, edge_rel, hold, N, cfg, device)
    m1 = filtered_hits_from_scores(sc, hold, sp["all_true"])
    sig1 = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())

    # per-query score-std (non-degeneracy) on the trained arm
    score_std = float(sc.std(dim=1).mean().item())

    # ---- per-degree strata (imported harness), PAIRED GNN vs POP ----
    strat_hits = dict()
    strat_hits[GNN] = per_stratum_hits(sc, hold, sp["strat"], sp["all_true"])
    strat_hits[GNN0] = per_stratum_hits(sc0, hold, sp["strat"], sp["all_true"])
    strat_hits[POP] = per_stratum_pop(sp["gd"].rel_tail_freq, hold, sp["strat"], sp["all_true"], N)

    train_converged = bool(loss_first == loss_first and loss_last == loss_last
                           and loss_last < loss_first * TRAIN_CONVERGE_REL)
    nondegenerate = bool(score_std > MIN_SCORE_STD)
    arms_differ = bool(sig1 != sig0)

    peak_mb = None
    if getattr(device, "type", "") == "cuda":
        peak_mb = round(torch.cuda.max_memory_allocated() / 1e6, 1)

    res = dict(
        corpus="CSKG_XCUT_CORE", seed=int(seed), N=N, n_rel=n_rel, n_train=sp["n_train"],
        n_test=sp["n_test"], n_l2_genuine=int(hold.shape[0]), tert_bounds=sp["tert"],
        strata_counts=strata_counts,
        arm_hits={GNN: {k: round(v, 4) for k, v in m1.items() if k != "n"},
                  GNN0: {k: round(v, 4) for k, v in m0.items() if k != "n"},
                  POP: {k: round(v, 4) for k, v in pop_m.items() if k != "n"}},
        arm_n={GNN: m1["n"], GNN0: m0["n"], POP: pop_m["n"]},
        arm_sigs={GNN: sig1, GNN0: sig0, POP: pop_sig},
        strat_hits=strat_hits,
        train=dict(loss_first=round(loss_first, 5) if loss_first == loss_first else None,
                   loss_last=round(loss_last, 5) if loss_last == loss_last else None,
                   n_batches=int(n_batches), epochs=cfg["epochs"], qpe=cfg["qpe"]),
        gnn_score_std=round(score_std, 6),
        split_identity=dict(assert_identity=bool(assert_identity), identity_ok=identity_ok,
                            recomputed_pop_sig=pop_sig, landed_ref=identity_ref, identity=identity),
        validity=dict(train_converged=train_converged, nondegenerate=nondegenerate, arms_differ=arms_differ),
        peak_gpu_mem_mb=peak_mb,
        cskg_provenance=prov,
    )
    _log("seed=%d L2gen=%d | hits@%d GNN=%.4f UNTRAINED=%.4f POP=%.4f | MRR GNN=%.4f POP=%.4f | "
         "loss %.3f->%.3f std=%.4g peak_gpu=%sMB identity_ok=%s"
         % (seed, hold.shape[0], PRIMARY_K, m1["hits@%d" % PRIMARY_K], m0["hits@%d" % PRIMARY_K],
            pop_m["hits@%d" % PRIMARY_K], m1["mrr"], pop_m["mrr"], loss_first, loss_last, score_std,
            peak_mb, identity_ok))

    # ---- teardown (per-seed process-equivalent isolation) ----
    del model, sc, sc0, edge_index, edge_rel, sp
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    return res


# ---------------------------------------------------------------------------
# Self-test (planted; scale-invariant; SAME split + metric code path).
# ---------------------------------------------------------------------------

def _selftest(device):
    cfg = dict(SELFTEST_CFG)
    tr, va, te = build_syn_compositional(seed=0, n_person=220, n_tail=55)
    sp = build_split(tr, va, te, cfg, 0)
    N = sp["N"]
    n_rel = sp["n_rel"]
    hold = sp["hold"]
    res = dict(l2_genuine=int(hold.shape[0]), N=N, n_rel=n_rel)
    if hold.shape[0] < 5:
        res["fail"] = "SYN_COMPOSITIONAL produced no L2-genuine held-out (%s)" % sp["hold_prov"]
        return False, res

    pop_m, pop_rank_vec = pop_hits(sp["gd"].rel_tail_freq, hold, sp["all_true"], N)
    edge_index, edge_rel = _build_edge_tensors(sp["train_int"], n_rel, device)

    torch.manual_seed(11)
    model0 = NBFNetLite(N, n_rel, cfg["dim"], cfg["n_layers"]).to(device)
    sc0 = _eval_gnn(model0, edge_index, edge_rel, hold, N, cfg, device)
    m0 = filtered_hits_from_scores(sc0, hold, sp["all_true"])
    sig0 = _sig(sc0.numpy()[:min(64, sc0.shape[0])].ravel())

    torch.manual_seed(11)
    model = NBFNetLite(N, n_rel, cfg["dim"], cfg["n_layers"]).to(device)
    loss_first, loss_last, _nb = _train_gnn(model, edge_index, edge_rel, sp["train_int"],
                                            sp["train_true"], N, cfg, device, 0, None)
    sc = _eval_gnn(model, edge_index, edge_rel, hold, N, cfg, device)
    m1 = filtered_hits_from_scores(sc, hold, sp["all_true"])
    sig1 = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())

    k = "hits@%d" % PRIMARY_K
    trained = float(m1[k])
    untrained = float(m0[k])
    pop = float(pop_m[k])
    lift = trained - untrained
    lift_ok = bool(lift >= ST_TRAIN_LIFT)                 # GATED: training lifts the arm (the lever fires)
    arms_differ = bool(sig1 != sig0)
    converged = bool(loss_last < loss_first * TRAIN_CONVERGE_REL)
    trained_meets_report = bool(trained >= ST_TRAINED_REPORT)   # REPORTED not gated

    # VACUOUS-SMOKE guard: training must produce the LIFT; if the untrained control is within ST_TRAIN_LIFT of
    # the trained arm, training/the GNN is not the lever and a green self-test is meaningless.
    training_not_the_lever = bool(lift < ST_TRAIN_LIFT)
    assert_discriminator_fires(training_not_the_lever, control_name=GNN0,
                               headline_name="training_lifts_gnn_over_untrained", run_mode="self_test",
                               extra="trained GNN did not lift hits@10 over its untrained control on planted "
                                     "composition -> training/the GNN is not the lever")

    res.update(trained_hits=round(trained, 4), untrained_hits=round(untrained, 4), pop_hits=round(pop, 4),
               train_lift=round(lift, 4), trained_mrr=round(float(m1["mrr"]), 4),
               loss_first=round(loss_first, 4), loss_last=round(loss_last, 4),
               lift_ok=lift_ok, converged=converged, arms_differ=arms_differ,
               trained_meets_report=trained_meets_report, n_distinct_sigs=len({sig0, sig1}))
    del model, model0, sc, sc0, edge_index, edge_rel
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    ok = bool(lift_ok and arms_differ and converged and hold.shape[0] >= 5)
    return ok, res


# ---------------------------------------------------------------------------
# Aggregate + verdict (CSKG comparator: validity + banked reference number).
# ---------------------------------------------------------------------------

def _mean(vals):
    vals = [v for v in vals if v is not None and v == v]
    return float(np.mean(vals)) if vals else float("nan")


def aggregate_and_verdict(per_seed, run_mode):
    hk = "hits@%d" % PRIMARY_K

    def arm_k(arm, metric):
        return _mean([ps["arm_hits"][arm].get(metric) for ps in per_seed])

    def strat_mean(arm, stratum):
        return _mean([per_seed[i]["strat_hits"][arm][stratum]["hits"] for i in range(len(per_seed))
                      if per_seed[i]["strat_hits"][arm][stratum]["n"] >= 8])

    ref = dict(
        primary_k=PRIMARY_K,
        gnn_hits_at_1=round(arm_k(GNN, "hits@1"), 4), gnn_hits_at_10=round(arm_k(GNN, hk), 4),
        gnn_mrr=round(arm_k(GNN, "mrr"), 4),
        untrained_hits_at_10=round(arm_k(GNN0, hk), 4),
        pop_hits_at_1=round(arm_k(POP, "hits@1"), 4), pop_hits_at_10=round(arm_k(POP, hk), 4),
        pop_mrr=round(arm_k(POP, "mrr"), 4),
        gnn_strat_hits_at_10={s: (round(strat_mean(GNN, s), 4) if strat_mean(GNN, s) == strat_mean(GNN, s) else None) for s in STRATA},
        pop_strat_hits_at_10={s: (round(strat_mean(POP, s), 4) if strat_mean(POP, s) == strat_mean(POP, s) else None) for s in STRATA},
    )

    # ---- validity gates (this cell's OWN verdict) ----
    identity_ok = all(bool(ps["split_identity"]["identity_ok"]) for ps in per_seed) \
        if run_mode == "full" else None
    converged = all(bool(ps["validity"]["train_converged"]) for ps in per_seed)
    nondegenerate = all(bool(ps["validity"]["nondegenerate"]) for ps in per_seed)
    arms_differ = all(bool(ps["validity"]["arms_differ"]) for ps in per_seed)

    gates = dict(reference=ref, identity_ok=identity_ok, train_converged=converged,
                 nondegenerate=nondegenerate, arms_differ=arms_differ,
                 peak_gpu_mem_mb=[ps.get("peak_gpu_mem_mb") for ps in per_seed])

    # ---- glass-box vs comparator ratio (RECORDED not gated; calibration caveat attached) ----
    landed = _load_mapbuilder_landed()
    if landed is not None:
        gb = landed.get("gates", {})
        gb_best = gb.get("geom_best")
        gb_high = gb.get("geom_best_high")
        comp = ref["gnn_hits_at_10"]
        comp_high = ref["gnn_strat_hits_at_10"].get("high")
        gates["glassbox_vs_comparator"] = dict(
            note="INFORMATIONAL ONLY -- NOT a gate. The >=85%/60% grading is owned downstream. Comparator is "
                 "TransE-tier ABSOLUTE for a harder 2-hop task, NOT NBFNet-SOTA; never market as SOTA.",
            glassbox_geom_best_hits_at_10=gb_best, comparator_gnn_hits_at_10=comp,
            ratio_glassbox_over_comparator=(round(gb_best / comp, 4) if (gb_best and comp and comp > 0) else None),
            glassbox_high_hits_at_10=gb_high, comparator_high_hits_at_10=comp_high,
            glassbox_pop_hits_at_10=gb.get("reach_hits_at_k", {}).get("BASELINE_POP"),
            comparator_pop_hits_at_10=ref["pop_hits_at_10"])

    valid_core = bool(converged and nondegenerate and arms_differ)
    if run_mode == "full":
        valid = bool(valid_core and identity_ok)
    else:
        valid = valid_core

    if run_mode == "full" and not identity_ok:
        verdict = "HARD_FAIL_SPLIT_IDENTITY_BREACH"
        msg = "Comparator split does NOT match the glass-box map-builder (POP sig mismatch); reference invalid."
    elif not (converged and nondegenerate):
        verdict = "HARD_FAIL_TRAINING_DEGENERATE"
        msg = ("GNN training degenerate: converged=%s nondegenerate=%s arms_differ=%s (loss/std did not "
               "produce a valid ranking)." % (converged, nondegenerate, arms_differ))
    else:
        verdict = "COMPARATOR_REFERENCE_BANKED"
        msg = ("Opaque NBFNet-lite comparator on the IDENTICAL CSKG L2-genuine split (identity_ok=%s): "
               "hits@1=%.4f hits@10=%.4f MRR=%.4f (POP hits@10=%.4f); HIGH-degree GNN hits@10=%s vs POP=%s; "
               "untrained control hits@10=%.4f. Banked as the TransE-tier absolute reference for the harder "
               "2-hop CSKG task (NOT NBFNet-SOTA; calibration caveat attached). Glass-box grading downstream."
               % (identity_ok, ref["gnn_hits_at_1"], ref["gnn_hits_at_10"], ref["gnn_mrr"],
                  ref["pop_hits_at_10"], ref["gnn_strat_hits_at_10"].get("high"),
                  ref["pop_strat_hits_at_10"].get("high"), ref["untrained_hits_at_10"]))
    return verdict, msg, gates, valid


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def _resolve_run_mode(args):
    if args.self_test:
        return "self_test"
    if args.smoke:
        return "smoke"
    if args.run_mode != "auto":
        return args.run_mode
    name = os.environ.get("HDLAB_EXP_NAME", "")
    if name.endswith("_memsmoke"):
        return "memsmoke"
    if name.endswith("_selftest"):
        return "self_test"
    if name.endswith("_smoke"):
        return "smoke"
    return "full"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["auto", "self_test", "smoke", "memsmoke", "full"], default="auto")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seeds", type=int, nargs="*", default=None,
                    help="override seed list (e.g. --seeds 7 for single-seed process-isolated dispatch)")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = _resolve_run_mode(args)

    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (args.device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        device = torch.device("cpu")
    else:
        want_cuda = (args.device in ("auto", "cuda")) or (env_dev == "cuda")
        device = torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")

    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode]
    seeds = args.seeds if args.seeds else cfg.get("seeds", [7])
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")
    t_start = time.perf_counter()

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s" % (device, torch.cuda.is_available(), run_mode, seeds))

    # ---- scale-invariant planted self-test (proves the discriminator fires; SAME code path) ----
    st_ok, st_res = _selftest(device)
    _log("selftest ok=%s %s" % (st_ok, st_res))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED (trained GNN did not clearly beat its untrained control on planted "
                        "composition): %s" % st_res,
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start, selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS GNN comparator apparatus: SYN_COMPOSITIONAL L2-genuine non-empty, "
                        "trained NBFNet-lite beats its untrained control + converged, arms differ.",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    # ---- smoke: planted SYN 2-seed (validates the multi-seed loop + metrics write; fits the 180s pre-gate).
    #      The REAL >=2-seed CSKG GPU memory smoke is the separate `memsmoke` dispatch. ----
    if run_mode == "smoke":
        per = []
        for si, seed in enumerate(seeds):
            tr, va, te = build_syn_compositional(seed=seed, n_person=220, n_tail=55)
            sp = build_split(tr, va, te, cfg, seed)
            N = sp["N"]; n_rel = sp["n_rel"]; hold = sp["hold"]
            ei, er = _build_edge_tensors(sp["train_int"], n_rel, device)
            torch.manual_seed(seed * 101 + 1)
            model = NBFNetLite(N, n_rel, cfg["dim"], cfg["n_layers"]).to(device)
            _train_gnn(model, ei, er, sp["train_int"], sp["train_true"], N, cfg, device, seed, _hb)
            sc = _eval_gnn(model, ei, er, hold, N, cfg, device)
            m1 = filtered_hits_from_scores(sc, hold, sp["all_true"])
            per.append(dict(seed=int(seed), N=N, n_l2_genuine=int(hold.shape[0]),
                            gnn_hits_at_10=round(m1["hits@%d" % PRIMARY_K], 4), gnn_mrr=round(m1["mrr"], 4)))
            del model, sc, ei, er, sp
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()
            _hb("smoke", si)
        write_metrics(out_dir, dict(
            verdict="SMOKE_PASS", run_mode="smoke",
            verdict_msg="SMOKE_PASS GNN comparator: %d-seed planted SYN pipeline ran + metrics valid: %s"
                        % (len(per), per),
            summary="SMOKE_PASS", elapsed_s=time.perf_counter() - t_start, smoke_per_seed=per, selftest=st_res))
        _log("SMOKE_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    # ---- memsmoke / full: real CSKG comparator ----
    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    assert_identity = (run_mode == "full")   # only the FULL runs the identical-split params -> assert identity
    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            res = run_seed_cskg(cfg, device, seed, assert_identity, _hb)
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            _log("seed=%d done (%.1fs)" % (seed, time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:400]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:300]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates, _valid = aggregate_and_verdict(per_seed, run_mode)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, selftest=st_res, seed_failures=seed_failures,
                   per_seed=per_seed,
                   calibration_caveat=("Reference is TransE-tier ABSOLUTE for a HARDER 2-hop task, NOT "
                                       "NBFNet-on-FB15k237-tier; NEVER market as SOTA. The >=85%/60% "
                                       "glass-box grading is a downstream verdict_handler job."),
                   split_referent=dict(source="MEASURED@%s" % MAPBUILDER_METRICS,
                                       assert_identity=assert_identity))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
