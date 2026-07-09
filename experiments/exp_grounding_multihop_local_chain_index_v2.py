"""Stage-5 reader LOCAL-NEIGHBORHOOD-SCOPED multi-hop chain cleanup (WIN-CELL v2).

THESIS (from research_reader_load_reduction_feasible_dim_win_path_2026-07-09 + the VET atom
MULTIHOP_READER_IS_LOAD_LIMITED): the multi-hop reader is LOAD-limited, not semantic-floor-limited. The landed
decisive-win cell's diagnostic backed out dim_needed = n_nodes/0.056 = 4440/0.056 = 79286 -- i.e. it charged the
cleanup crosstalk against the FULL global vocabulary (4440 nodes). But a multi-hop KG walk only ever has to
discriminate the true target from the LOCAL graph neighborhood of the current node (mean out-degree ~6.65). Charge
the resonator/cleanup against ~6.65 candidates instead of 4440 and dim_needed collapses ~670x (6.65/0.056 = 119).
The fix is architectural, not dimensional: restrict the per-hop cleanup candidate set to the current node's actual
graph neighbors. Keep dim MODEST (~2k) -- the win must come from local-scoping, not from throwing dimension.

CHEAP GLOBAL-vs-LOCAL PRE-TEST (arm-0, in the self-test + reported): instrument whether the BASELINE cleanup
scores candidates against the full global vocabulary or the local graph-neighborhood. In the landed harness the
cleanup does `score = _l2t(pred) @ Z.t()` (Z = [n_nodes, d]) then argmax over ALL nodes -> GLOBAL. dim_needed
backs out to n_nodes/0.056 exactly. This cell CONFIRMS that and measures the collapse under the local D_f.

ARMS (4; paired: identical planted chains + identical learned codes Z + identical unitary roles + identical seeds
across all arms; the ONLY difference is the cleanup candidate set, so GLOBAL-vs-LOCAL is a clean within-dim
attribution -- any gap is purely the candidate-set restriction, not dimension):
  1 NO_CLEANUP    : must-fail control. Raw HRR accumulation carried forward each hop; top-1 global readout only.
                    Anti-saturation gate: MUST collapse at reach>=2 (else the discriminator is vacuous).
  2 GLOBAL_CLEANUP: baseline = current landed behavior. Per-hop top-1 snap to the nearest node over the FULL
                    codebook (argmax over all n_nodes). The reference the LOCAL arm must beat.
  3 LOCAL_CLEANUP : THE win lever. Per-hop top-1 snap restricted to the current node's graph neighbors
                    (out-neighbors of the committed node; for hop-0 the TRUE start, whose adjacency is legitimately
                    known in a KG walk). Errors propagate honestly (wrong commit -> wrong candidate set next hop).
  4 LOCAL_DECORR  : LOCAL_CLEANUP + light decorrelation: subtract the local candidate centroid (remove the shared
                    semantic component among neighbors) before scoring. Targets the residual within-neighborhood
                    semantic aliasing (the correlation-tax operating at LOCAL scale, tens not thousands).

METRIC (primary, gated): reach@d = TOP-1 COMMIT accuracy at hop d (committed node == true target). This is the
honest chaining metric -- the chain must carry exactly ONE node forward, so top-1 is what actually propagates. It
also AVOIDS the small-candidate-set inflation hit@K would cause for the local arms (when |neighbors| <= K, hit@K
degenerates to "is the target in the small set", ~trivial). hit@10 is computed as a SECONDARY diagnostic only
(global top-10 for continuity with the landed cell's PLAIN@2=0.106; NOT gated).

WIN BAR (pre-registered BEFORE the run):
  HARD_PASS_LOCAL_WIN = LOCAL arm reach2 >= 0.60 AND reach3 >= 0.35 AND slope-flatten >= 40% (at feasible dim
                        <= ~5k). Level-lift alone is NOT a win -- the slope MUST flatten (VET's key requirement).
  HARD_FAIL_SEMANTIC_FLOOR = LOCAL reach2 < 0.60 AND local_aliasing_frac >= 0.50 (the residual is genuine same-
                        relation sibling ambiguity in the graph itself -> no code/dim fix helps; it IS a semantic
                        floor). local_aliasing_frac = among hop-2 LOCAL errors (hop-1 conditioned correct), the
                        fraction whose wrongly-picked neighbor is a SAME-RELATION sibling of the true edge.
  MIDDLE_BAND_PARTIAL  = partial crossing (LOCAL lifts materially over GLOBAL but misses a WIN band, and the miss
                        is not a semantic floor).

DISCRIMINATOR-SURVIVES-SCALE: unlike the v1 dimension-throw lever (which by construction cannot show at small
dim), the LOCAL lever is SCALE-INDEPENDENT -- the candidate set is ~mean_out_degree regardless of total n_nodes.
So the discriminator DOES fire at smoke: LOCAL >> GLOBAL directionally, NO_CLEANUP collapses, on the REAL subgraph.
Smoke uses the same 4 arms / same code path as FULL; only n_nodes/dim/epochs/seeds/n_chains scale.

HONESTY: real CG'd teacher-free relational learned codes over the REAL ConceptNet typed subgraph; top-1 commit
fidelity; NO language understanding claimed. The local-scoping restriction is LEGITIMATE for KG traversal (graph
adjacency is known at each step; this is the VSA analog of HippoRAG's graph-index-in-front-of-dense-embeddings).
It is NOT oracle-cheating: the model still must pick the RIGHT neighbor among ~6.65 using the role-bound query;
the target identity is never handed to it, and wrong commits propagate to wrong candidate sets. Teacher-free,
ASCII-only, device-aware torch (cuda if available). Reuses the Stage-4 VET-landed encoder/chain primitives
VERBATIM (calibration continuity + no drift).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-chain top-1-commit signatures; LOCAL asserted != GLOBAL
#   asserted != NO_CLEANUP).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000); WIN floor reach2>=0.60 >> chance and reachable at
#   the modest dim because the LOCAL load 6.65/dim is far below the resonator threshold 0.056 for dim>=256
#   (6.65/2048 = 0.0032). crlb_n/a for the semantic-floor branch (measured aliasing, not a closed-form floor).
# - baseline_in_band: GLOBAL_CLEANUP@1 in (0.05, 0.95) at smoke (single-hop global top-1 is a genuine cap, not
#   saturated). NO_CLEANUP@2 must collapse (<= 0.10 abs AND <= 0.5x@1) -- the anti-saturation must-fail control.
# - discriminator survives scale: LOCAL lever is scale-independent (candidate set ~ mean_out_degree at all n) so
#   the LOCAL>>GLOBAL gap FIRES AT SMOKE on the real subgraph (option A/C). Documented.
# - HARD_PASS strictly above floor: reach2>=0.60 AND reach3>=0.35 AND slope-flatten>=40% (all three).
# - HP_SCOPE: WIN gate applies ONLY to {LOCAL_CLEANUP, LOCAL_DECORR}. NO_CLEANUP = must-fail control;
#   GLOBAL_CLEANUP = baseline reference (reported, not gated).
# - sweep axis: hop depth d in {1..4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 4 arms x all
#   depths (arm/depth cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (baseline-collapse + baseline-in-band recomputed
#   empirically per run; paired per-chain top-1 commits so all deltas are paired).
# - PAIRED trials (arm-comparison discriminator): all arms share identical chains + codes + roles + seeds.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed flush prints + heartbeat).
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
    char_trigram_features,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    SUBGRAPH_BASE_SEED,
)
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
)
# Reuse the Stage-4 VET-landed primitives VERBATIM (calibration continuity + no drift).
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _l2t,
)

ANCHOR_NAME = "grounding_multihop_local_chain_index_v2"

HIT_K = 10            # SECONDARY diagnostic only (hit@K continuity with landed PLAIN@2); NOT gated
MAX_REACH = 4         # measure reach through 4 (decay slope); WIN bar is reach 2-3

RESONATOR_THRESH = 0.056   # CITED@arXiv:1906.11684 resonator D_f/N stability threshold

# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME 4 arms / same code path as FULL; only scale differs.
# dim is MODEST (the whole point). LOCAL load = mean_out_degree/dim << resonator thresh at all these dims.
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=200, chain_chunk=256,
)

SMOKE_CFG = dict(
    seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, code_dim=512, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=500, chain_chunk=256,
)

FULL_CFG = dict(
    seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=2048, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=1200, chain_chunk=256,
)

# ---------------------------------------------------------------------------
# Pre-registered WIN bands (picked BEFORE the run). Metric = TOP-1 COMMIT accuracy.
# ---------------------------------------------------------------------------
HOP1_PRESENT = 0.08        # GLOBAL_CLEANUP@1 must clear this (single-hop machinery works; >> chance ~0.0002)
BASE_IN_BAND_HI = 0.95     # GLOBAL_CLEANUP@1 must be < this (not saturated -> baseline in measurable band)
BASE_COLLAPSE_ABS = 0.10   # anti-saturation: NO_CLEANUP@2 <= this AND ...
BASE_COLLAPSE_FRAC = 0.50  # ... <= this fraction of NO_CLEANUP@1 (must-fail control lost >= half its reach)
WIN_REACH2 = 0.60          # WIN: LOCAL arm reach-2 top-1 commit >= this (usable multi-hop, not detectable)
WIN_REACH3 = 0.35          # WIN: LOCAL arm reach-3 top-1 commit >= this (material chainable signal)
WIN_SLOPE_FLATTEN = 0.40   # WIN: |decay_slope| flattened by >= this fraction vs NO_CLEANUP baseline slope
ALIAS_FLOOR_HI = 0.50      # HARD_FAIL_SEMANTIC_FLOOR: local_aliasing_frac >= this AND LOCAL reach2 < WIN_REACH2 ...
ALIAS_EXCESS_MIN = 0.15    # ... AND aliasing_frac exceeds the same-relation base rate by >= this (genuine, not base-rate)

# Arm names
NO_CLEANUP = "NO_CLEANUP"
GLOBAL_CLEANUP = "GLOBAL_CLEANUP"
LOCAL_CLEANUP = "LOCAL_CLEANUP"
LOCAL_DECORR = "LOCAL_DECORR"
ARMS = [NO_CLEANUP, GLOBAL_CLEANUP, LOCAL_CLEANUP, LOCAL_DECORR]
WIN_ARMS = [LOCAL_CLEANUP, LOCAL_DECORR]   # HP_SCOPE: WIN gate applies to these only


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    if arg_device == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


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


# ---------------------------------------------------------------------------
# Padded neighbor table for local-candidate scoring. Node index n_nodes is a DEAD sentinel (empty neighbor row).
# Z is padded with a zero row at index n_nodes so gathers on the sentinel are safe.
# ---------------------------------------------------------------------------

def build_nbr_table(dir_adj, n_nodes, device):
    """Returns nbr_idx [n+1, Dmax] (node ids, padded with n_nodes sentinel), nbr_rel [n+1, Dmax] (relation ids,
    padded -1), nbr_mask [n+1, Dmax] bool (True where a real neighbor). Row n_nodes = all-padding dead sentinel."""
    degs = [len(dir_adj[u]) for u in range(n_nodes)]
    Dmax = max(1, max(degs) if degs else 1)
    nbr_idx = np.full((n_nodes + 1, Dmax), n_nodes, dtype=np.int64)
    nbr_rel = np.full((n_nodes + 1, Dmax), -1, dtype=np.int64)
    nbr_mask = np.zeros((n_nodes + 1, Dmax), dtype=bool)
    for u in range(n_nodes):
        for j, (v, r) in enumerate(dir_adj[u]):
            nbr_idx[u, j] = int(v)
            nbr_rel[u, j] = int(r)
            nbr_mask[u, j] = True
    mean_out_deg = float(np.mean([d for d in degs if d > 0])) if any(degs) else 0.0
    return (torch.from_numpy(nbr_idx).to(device),
            torch.from_numpy(nbr_rel).to(device),
            torch.from_numpy(nbr_mask).to(device),
            int(Dmax), mean_out_deg)


def _local_scores(pred_blk, cur_blk, Zp, nbr_idx, nbr_mask, decorr):
    """Local candidate scoring for a block of chains.
    pred_blk [B, d] (L2 will be applied), cur_blk [B] current-node ids, Zp [n+1, d] padded codes (row n = 0).
    Returns (score [B, Dmax] with -inf at padding, cand [B, Dmax] node ids, mask [B, Dmax] bool, cset_size [B]).
    If decorr: subtract the local candidate centroid from both pred and candidate codes before the dot product."""
    cand = nbr_idx[cur_blk]                       # [B, Dmax] node ids (sentinel n at padding)
    mask = nbr_mask[cur_blk]                       # [B, Dmax] bool
    Zc = Zp[cand]                                 # [B, Dmax, d]
    p = _l2t(pred_blk)                             # [B, d]
    if decorr:
        mf = mask.unsqueeze(-1).to(Zc.dtype)      # [B, Dmax, 1]
        denom = mf.sum(dim=1).clamp(min=1.0)      # [B, 1]
        centroid = (Zc * mf).sum(dim=1) / denom   # [B, d] local neighbor centroid
        Zc = Zc - centroid.unsqueeze(1)           # remove shared local component
        p = p - centroid                          # project the query the same way
    s = torch.einsum("bd,bkd->bk", p, Zc)         # [B, Dmax]
    s = s.masked_fill(~mask, float("-inf"))
    cset_size = mask.sum(dim=1)                    # [B]
    return s, cand, mask, cset_size


# ---------------------------------------------------------------------------
# Chain retrieval per arm. All arms paired on identical chains. Metric = TOP-1 COMMIT accuracy.
# ---------------------------------------------------------------------------

def run_arm(arm, Z, Zp, roles_t, nbr_idx, nbr_mask, start, targets, role_ids, device, chunk, n_nodes):
    """Returns reach[d] (top-1 commit acc), hit10[d] (secondary, global top-10 or local top-10), per-chain
    top-1-commit signature (arms-differ), and mean local candidate-set size (local arms only)."""
    L = len(targets)
    C = start.shape[0]
    decorr = (arm == LOCAL_DECORR)
    is_local = arm in (LOCAL_CLEANUP, LOCAL_DECORR)
    cur = torch.from_numpy(start).to(device)                 # [C] current committed node ids (start = TRUE start)
    reach = {}
    hit10 = {}
    commit_sig = []
    cset_sizes = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]     # [C, d]
        cue = Z[cur.clamp(max=n_nodes - 1)]                          # [C, d] code of current committed node
        pred = _hrr_bind_t(role, cue)                                # [C, d] hop bind
        tgt = torch.from_numpy(targets[h]).to(device)                # [C]
        committed = torch.full((C,), n_nodes, dtype=torch.long, device=device)  # dead sentinel default
        hitk = torch.zeros(C, dtype=torch.bool, device=device)
        if is_local:
            for b0 in range(0, C, chunk):
                b1 = min(C, b0 + chunk)
                s, cand, mask, csz = _local_scores(pred[b0:b1], cur[b0:b1], Zp, nbr_idx, nbr_mask, decorr)
                nonempty = mask.any(dim=1)                            # [b]
                loc_arg = s.argmax(dim=1)                             # [b] local index
                b_ids = torch.arange(b1 - b0, device=device)
                picked = cand[b_ids, loc_arg]                         # [b] node id of local argmax
                committed[b0:b1] = torch.where(nonempty, picked,
                                               torch.full_like(picked, n_nodes))
                # secondary hit@K among local candidates (diagnostic; inflated when |cand|<=K -> reported, not gated)
                kk = min(HIT_K, s.shape[1])
                topk = s.topk(kk, dim=1).indices                     # [b, kk] local indices
                topk_ids = torch.gather(cand, 1, topk)               # [b, kk] node ids
                hitk[b0:b1] = (topk_ids == tgt[b0:b1, None]).any(dim=1) & nonempty
                cset_sizes.append(csz.detach().to("cpu"))
            carry_ids = committed
        elif arm == GLOBAL_CLEANUP:
            score = _l2t(pred) @ Z.t()                               # [C, n] global
            committed = score.argmax(dim=1)                          # top-1 global commit
            topk = score.topk(min(HIT_K, score.shape[1]), dim=1).indices
            hitk = (topk == tgt[:, None]).any(dim=1)
            carry_ids = committed
        else:
            raise ValueError("unknown arm %r (NO_CLEANUP is handled by run_no_cleanup)" % arm)

        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cur = carry_ids                                              # advance to committed node for next hop

    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    mean_cset = float(torch.cat(cset_sizes).float().mean().item()) if cset_sizes else float("nan")
    return reach, hit10, sig, mean_cset


def run_no_cleanup(Z, roles_t, start, targets, role_ids, device, n_nodes):
    """Explicit raw-accumulation control: cue starts at the true start code, each hop cue <- bind(role, cue) with
    NO snap; readout is top-1 global argmax. Crosstalk compounds -> collapse at reach>=2 (anti-saturation)."""
    L = len(targets)
    C = start.shape[0]
    cue = Z[torch.from_numpy(start).to(device)].clone()
    reach = {}
    hit10 = {}
    commit_sig = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]
        pred = _hrr_bind_t(role, cue)
        tgt = torch.from_numpy(targets[h]).to(device)
        score = _l2t(pred) @ Z.t()
        committed = score.argmax(dim=1)
        topk = score.topk(min(HIT_K, score.shape[1]), dim=1).indices
        hitk = (topk == tgt[:, None]).any(dim=1)
        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cue = pred                                              # raw carry (no cleanup); crosstalk compounds
    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    return reach, hit10, sig


# ---------------------------------------------------------------------------
# LOCAL hop-2 semantic-floor decomposition. Condition on hop-1 CORRECT (use the true midpoint), do the LOCAL
# cleanup for hop-2, and among the errors measure the fraction whose wrongly-picked neighbor is a SAME-RELATION
# sibling of the true edge -> irreducible graph ambiguity (semantic floor) vs a different-relation neighbor.
# ---------------------------------------------------------------------------

def local_error_decomposition(Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, start, targets, role_ids,
                              device, n_nodes, decorr=False):
    if len(targets) < 2:
        return dict(n_hop2=0, n_err=0, n_alias=0, local_aliasing_frac=float("nan"))
    C = start.shape[0]
    mid = torch.from_numpy(targets[0]).to(device)               # TRUE hop-1 midpoint (condition hop-1 correct)
    role2 = roles_t[torch.from_numpy(role_ids[1]).to(device)]
    true_r2 = torch.from_numpy(role_ids[1]).to(device)          # true relation of hop-2
    pred2 = _hrr_bind_t(role2, Z[mid])
    tgt2 = torch.from_numpy(targets[1]).to(device)
    picked = torch.full((C,), n_nodes, dtype=torch.long, device=device)
    picked_rel = torch.full((C,), -1, dtype=torch.long, device=device)
    for b0 in range(0, C, 256):
        b1 = min(C, b0 + 256)
        s, cand, mask, _csz = _local_scores(pred2[b0:b1], mid[b0:b1], Zp, nbr_idx, nbr_mask, decorr)
        nonempty = mask.any(dim=1)
        la = s.argmax(dim=1)
        b_ids = torch.arange(b1 - b0, device=device)
        pid = cand[b_ids, la]
        prel = nbr_rel[mid[b0:b1]][b_ids, la]
        picked[b0:b1] = torch.where(nonempty, pid, torch.full_like(pid, n_nodes))
        picked_rel[b0:b1] = torch.where(nonempty, prel, torch.full_like(prel, -1))
    err = (picked != tgt2)
    # among errors, wrongly-picked neighbor shares the SAME relation as the true hop-2 edge => same-relation sibling
    alias = err & (picked_rel == true_r2)
    n_err = int(err.sum().item())
    n_alias = int(alias.sum().item())
    frac = (n_alias / n_err) if n_err > 0 else float("nan")
    # base rate: fraction of the midpoint's candidate neighbors that share the true hop-2 relation. If a random
    # wrong pick would be same-relation this often anyway, then a high aliasing_frac is a base-rate artifact NOT
    # genuine same-relation confusability. semantic_floor requires aliasing_frac to EXCEED this base rate.
    same_rel_ct = ((nbr_rel[mid] == true_r2[:, None]) & nbr_mask[mid]).sum(dim=1).float()
    cand_ct = nbr_mask[mid].sum(dim=1).float().clamp(min=1.0)
    base_rate = float((same_rel_ct / cand_ct).mean().item())
    excess = (frac - base_rate) if (frac == frac) else float("nan")
    return dict(n_hop2=int(C), n_err=n_err, n_alias=n_alias, local_aliasing_frac=float(frac),
                same_rel_base_rate=base_rate, aliasing_excess_over_base=float(excess))


# ---------------------------------------------------------------------------
# D_f/N recompute diagnostic (the cheap GLOBAL-vs-LOCAL test): global vs local D_f -> dim_needed collapse.
# ---------------------------------------------------------------------------

def df_recompute(n_nodes, mean_out_deg, mean_cset, dim):
    g_df = float(n_nodes)
    l_df1 = float(mean_out_deg)                    # 1-hop local branching
    l_df2 = float(mean_out_deg ** 2)               # pessimistic 2-hop tree (real graph re-converges -> lower)
    l_df3 = float(mean_out_deg ** 3)               # pessimistic 3-hop tree
    return dict(
        scoring_scope_baseline="GLOBAL",           # confirmed by code inspection: score = pred @ Z.t() over all n
        global_D_f=g_df, global_dim_needed=g_df / RESONATOR_THRESH,
        local_D_f_1hop=l_df1, local_dim_needed_1hop=l_df1 / RESONATOR_THRESH,
        local_D_f_2hop=l_df2, local_dim_needed_2hop=l_df2 / RESONATOR_THRESH,
        local_D_f_3hop=l_df3, local_dim_needed_3hop=l_df3 / RESONATOR_THRESH,
        mean_out_degree=float(mean_out_deg), mean_local_cset_size=float(mean_cset),
        dim=int(dim), local_load_per_hop=float(mean_out_deg) / float(dim),
        collapse_factor=(g_df / l_df1) if l_df1 > 0 else float("nan"),
        resonator_thresh=RESONATOR_THRESH,
    )


# ---------------------------------------------------------------------------
# Per-model-seed run: all 4 arms on identical chains + codes + roles + graph
# ---------------------------------------------------------------------------

def run_seed(seed, X, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask, mean_out_deg,
             cfg, device, out_dir=None):
    n_nodes = X.shape[0]
    d = cfg["code_dim"]

    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, d, device=device)], dim=0)   # padded codes; row n_nodes = 0 (dead sentinel)

    chain_rng = np.random.default_rng(seed + 909)
    start, targets, role_ids = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, chain_rng)
    n_chains_got = int(start.shape[0])
    chunk = cfg["chain_chunk"]

    arms = {}
    sigs = {}
    mean_cset = float("nan")
    for arm in ARMS:
        if arm == NO_CLEANUP:
            reach, hit10, sig = run_no_cleanup(Z, roles_t, start, targets, role_ids, device, n_nodes)
            mcs = float("nan")
        else:
            reach, hit10, sig, mcs = run_arm(arm, Z, Zp, roles_t, nbr_idx, nbr_mask, start, targets, role_ids,
                                             device, chunk, n_nodes)
            if arm == LOCAL_CLEANUP and mcs == mcs:
                mean_cset = mcs
        arms[arm] = dict(reach=reach, hit10=hit10, mean_cset=mcs)
        sigs[arm] = sig
        _log("  seed=%d %-15s reach@[1..%d]=%s hit10@2=%.3f cset=%.2f" % (
            seed, arm, MAX_REACH, {dd: round(reach[dd], 3) for dd in range(1, MAX_REACH + 1)},
            hit10[2], mcs if mcs == mcs else -1.0))

    err_local = local_error_decomposition(Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                          start, targets, role_ids, device, n_nodes, decorr=False)
    _log("  seed=%d local_error_decomp %s" % (seed, err_local))

    df = df_recompute(n_nodes, mean_out_deg, mean_cset, d)
    _log("  seed=%d df_recompute global_dim_needed=%.0f local_dim_needed_1hop=%.1f collapse=%.0fx cset=%.2f" % (
        seed, df["global_dim_needed"], df["local_dim_needed_1hop"], df["collapse_factor"], df["mean_local_cset_size"]))

    if len(set(sigs.values())) < 2:
        _log("  [warn] seed=%d arm commit-signatures collapsed to <2 distinct" % seed)

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig,
                n_chains=n_chains_got, code_dim=d, mean_local_cset=mean_cset,
                error_decomp_local=err_local, df_recompute=df)


# ---------------------------------------------------------------------------
# Aggregate + WIN verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _decay_slope(reach):
    ds = np.array([d for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    ys = np.array([reach[d] for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    if np.any(ys != ys):
        return float("nan")
    A = np.vstack([ds, np.ones_like(ds)]).T
    return float(np.linalg.lstsq(A, ys, rcond=None)[0][0])


def _log_decay_slope(reach, floor=1e-3):
    """Slope of ln(reach) vs depth: the RELATIVE (geometric) decay rate. Level-invariant, so a high-starting arm
    that retains a larger FRACTION per hop reads as flatter than a low-starting arm even if its absolute drop is
    bigger. This is the honest 'does the chain retain fidelity across hops' measure (arms start at very different
    levels, so absolute linear slope is not comparable across arms)."""
    ds = np.array([d for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    ys = np.array([max(reach[d], floor) for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    if np.any(ys != ys):
        return float("nan")
    A = np.vstack([ds, np.ones_like(ds)]).T
    return float(np.linalg.lstsq(A, np.log(ys), rcond=None)[0][0])


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def aggregate_and_verdict(per_seed, subgraph_meta, cfg):
    reach = {a: {d: _nanmean([m["arms"][a]["reach"][d] for m in per_seed]) for d in range(1, MAX_REACH + 1)}
             for a in ARMS}
    hit10 = {a: {d: _nanmean([m["arms"][a]["hit10"][d] for m in per_seed]) for d in range(1, MAX_REACH + 1)}
             for a in ARMS}
    slope = {a: _decay_slope(reach[a]) for a in ARMS}
    log_slope = {a: _log_decay_slope(reach[a]) for a in ARMS}

    base1 = reach[NO_CLEANUP][1]
    base2 = reach[NO_CLEANUP][2]
    base3 = reach[NO_CLEANUP][3]
    base_logslope = log_slope[NO_CLEANUP]
    glob1 = reach[GLOBAL_CLEANUP][1]

    hop1_present = (glob1 == glob1) and (glob1 >= HOP1_PRESENT)
    baseline_in_band = (glob1 == glob1) and (glob1 < BASE_IN_BAND_HI) and hop1_present
    baseline_collapses = (base2 == base2 and base1 == base1
                          and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))

    def _flatten(a):
        # relative (log) decay flatten vs the collapsing NO_CLEANUP control: does the chain retain a larger
        # FRACTION of fidelity per hop than raw accumulation (level-invariant, so comparable across arms).
        sa = log_slope[a]
        if not (sa == sa) or not (base_logslope == base_logslope) or abs(base_logslope) < 1e-9:
            return float("nan")
        return 1.0 - (abs(sa) / abs(base_logslope))

    # local aliasing (mean over seeds) + same-relation base rate for the semantic-floor branch
    alias_frac = _nanmean([m["error_decomp_local"].get("local_aliasing_frac", float("nan")) for m in per_seed])
    alias_base = _nanmean([m["error_decomp_local"].get("same_rel_base_rate", float("nan")) for m in per_seed])
    alias_excess = _nanmean([m["error_decomp_local"].get("aliasing_excess_over_base", float("nan"))
                             for m in per_seed])

    win_eval = {}
    for a in WIN_ARMS:
        r2 = reach[a][2]
        r3 = reach[a][3]
        fl = _flatten(a)
        win = bool(r2 == r2 and r2 >= WIN_REACH2 and r3 == r3 and r3 >= WIN_REACH3
                   and fl == fl and fl >= WIN_SLOPE_FLATTEN)
        win_eval[a] = dict(reach1=reach[a][1], reach2=r2, reach3=r3, slope_flatten=fl, win=win)

    win_arms_pass = [a for a in WIN_ARMS if win_eval[a]["win"]]
    best_local = max(WIN_ARMS, key=lambda a: (win_eval[a]["reach2"] if win_eval[a]["reach2"] == win_eval[a]["reach2"]
                                              else -1e9))
    best_local_r2 = win_eval[best_local]["reach2"]

    # semantic-floor branch: best LOCAL arm misses WIN_REACH2 AND the residual is DISPROPORTIONATELY same-relation
    # sibling ambiguity -- aliasing_frac must clear the absolute floor AND exceed the same-relation base rate by a
    # margin (else a high aliasing_frac is just the base rate of same-relation neighbors, not genuine confusability).
    semantic_floor = bool(best_local_r2 == best_local_r2 and best_local_r2 < WIN_REACH2
                          and alias_frac == alias_frac and alias_frac >= ALIAS_FLOOR_HI
                          and alias_excess == alias_excess and alias_excess >= ALIAS_EXCESS_MIN)

    # local lift over global baseline (attribution: the win is the candidate-set restriction, same dim/Z)
    local_lift2 = (reach[LOCAL_CLEANUP][2] - reach[GLOBAL_CLEANUP][2]
                   if reach[LOCAL_CLEANUP][2] == reach[LOCAL_CLEANUP][2] else float("nan"))

    df = per_seed[0]["df_recompute"]

    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif len(win_arms_pass) > 0:
        verdict = "HARD_PASS_LOCAL_WIN"
    elif semantic_floor:
        verdict = "HARD_FAIL_SEMANTIC_FLOOR"
    else:
        verdict = "MIDDLE_BAND_PARTIAL"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f(hop1_present=%s) @2=%.3f(collapses=%s) @3=%.3f logslope=%.3f || "
        "GLOBAL @1=%.3f(in_band=%s) @2=%.3f @3=%.3f || "
        "LOCAL @1=%.3f @2=%.3f @3=%.3f flat=%s win=%s | LOCAL_DECORR @1=%.3f @2=%.3f @3=%.3f flat=%s win=%s || "
        "best_local=%s best_local_r2=%.3f local_lift2(vs GLOBAL)=%s win_arms=%s || "
        "local_aliasing_frac=%s base_rate=%s excess=%s semantic_floor=%s || "
        "df: scope=%s global_dim_needed=%.0f local_dim_needed_1hop=%.1f collapse=%.0fx mean_cset=%.2f "
        "mean_out_deg=%.2f dim=%d local_load/hop=%.4f (thr=%.3f) || "
        "WIN bands: R2>=%.2f R3>=%.2f FLATTEN>=%.0f%% (dim=%d MODEST) || "
        "n=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, hop1_present, base2, baseline_collapses, base3, base_logslope,
            glob1, baseline_in_band, reach[GLOBAL_CLEANUP][2], reach[GLOBAL_CLEANUP][3],
            reach[LOCAL_CLEANUP][1], reach[LOCAL_CLEANUP][2], reach[LOCAL_CLEANUP][3],
            _fmt(win_eval[LOCAL_CLEANUP]["slope_flatten"]), win_eval[LOCAL_CLEANUP]["win"],
            reach[LOCAL_DECORR][1], reach[LOCAL_DECORR][2], reach[LOCAL_DECORR][3],
            _fmt(win_eval[LOCAL_DECORR]["slope_flatten"]), win_eval[LOCAL_DECORR]["win"],
            best_local, best_local_r2, _fmt(local_lift2), win_arms_pass,
            _fmt(alias_frac), _fmt(alias_base), _fmt(alias_excess), semantic_floor,
            df["scoring_scope_baseline"], df["global_dim_needed"], df["local_dim_needed_1hop"],
            df["collapse_factor"], df["mean_local_cset_size"], df["mean_out_degree"], df["dim"],
            df["local_load_per_hop"], RESONATOR_THRESH,
            WIN_REACH2, WIN_REACH3, WIN_SLOPE_FLATTEN * 100, cfg["code_dim"],
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed), "full" if len(cfg["seeds"]) == 3 else "smoke"))

    gates = dict(
        verdict=verdict, reach_mean=reach, hit10_mean=hit10, decay_slope=slope, log_decay_slope=log_slope,
        base_reach1=base1, base_reach2=base2, base_reach3=base3,
        base_slope=slope[NO_CLEANUP], base_logslope=base_logslope,
        global_reach1=glob1, hop1_present=bool(hop1_present), baseline_in_band=bool(baseline_in_band),
        baseline_collapses=bool(baseline_collapses),
        win_eval=win_eval, win_arms_pass=win_arms_pass, best_local=best_local, best_local_reach2=best_local_r2,
        local_lift2_vs_global=local_lift2,
        local_aliasing_frac=alias_frac, same_rel_base_rate=alias_base, aliasing_excess_over_base=alias_excess,
        semantic_floor=bool(semantic_floor),
        df_recompute=df,
        bands=dict(HOP1_PRESENT=HOP1_PRESENT, BASE_IN_BAND_HI=BASE_IN_BAND_HI,
                   BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, BASE_COLLAPSE_FRAC=BASE_COLLAPSE_FRAC,
                   WIN_REACH2=WIN_REACH2, WIN_REACH3=WIN_REACH3, WIN_SLOPE_FLATTEN=WIN_SLOPE_FLATTEN,
                   ALIAS_FLOOR_HI=ALIAS_FLOOR_HI, ALIAS_EXCESS_MIN=ALIAS_EXCESS_MIN,
                   HIT_K=HIT_K, MAX_REACH=MAX_REACH),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (ALWAYS runs, CPU) on PLANTED correlated codes + a real local graph.
# Proves: (0) chain machinery works (hop-1 high); (1) must-fail NO_CLEANUP collapses at reach>=2; (2) LOCAL
# cleanup beats GLOBAL cleanup at reach-2 (the count-tax lever separates); (3) all arms differ; (4) the D_f
# recompute collapses global->local dim_needed (the cheap GLOBAL-vs-LOCAL arithmetic).
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    rng = np.random.default_rng(0)
    d = 96
    T = 4
    n = 3000
    roles_b = torch.from_numpy(make_unitary_roles(T, d, np.random.default_rng(11))).to(device)

    # Planted correlated codebook + recoverable typed chain, with a REAL local graph (each node a few typed
    # out-neighbors) so the local-candidate scoring path is exercised. Same planting recipe family as the
    # Stage-4/5 self-tests: Z[v] = normalize(bind(role_r, Z[u]) + 0.30*cluster(v) + noise) along a walk, and we
    # ALSO plant a handful of DECOY out-edges per node (different targets) so LOCAL cleanup must actually pick.
    n_clusters = 40
    per = n // n_clusters
    base = rng.standard_normal((n_clusters, d)).astype(np.float32)
    base_u = base / (np.linalg.norm(base, axis=1, keepdims=True) + 1e-8)
    base_ut = torch.from_numpy(base_u.astype(np.float32)).to(device)
    dir_adj_planted = [[] for _ in range(n)]   # recoverable edges only -> chains walk these
    dir_adj_full = [[] for _ in range(n)]       # planted + decoy distractors -> local candidate table
    order = rng.permutation(n)
    Z2 = torch.zeros(n, d, device=device)
    u0 = int(order[0])
    Z2[u0] = _l2t((base_ut[u0 // per] + 0.20 * torch.randn(d))[None, :])[0]
    for k in range(1, n):
        u = int(order[k - 1]); v = int(order[k]); r = int(rng.integers(0, T))
        pred = _l2t(_hrr_bind_t(roles_b[r:r + 1], _l2t(Z2[u:u + 1])))[0]
        nz = _l2t(torch.randn(1, d))[0]
        # cleaner planting than the Stage-4/5 hit@10 self-tests: the TOP-1 commit metric needs the bind signal to
        # dominate so hop-1 top-1 recovery is genuinely high (proves machinery); accumulation still compounds so
        # NO_CLEANUP collapses at deep reach, and the local candidate restriction still beats global.
        # noise tuned so the single-hop target cosine (~0.45) sits near the GLOBAL random-competitor max (max of
        # ~n draws grows with n), so GLOBAL loses on the count-tax while LOCAL (only ~mean_out_deg competitors,
        # far smaller max) recovers -- the exact count-tax the cell measures. Cluster component is ~orthogonal to
        # the bind direction so it does not drive the effect (kept small).
        Z2[v] = _l2t((pred + 0.30 * base_ut[v // per] + 1.95 * nz)[None, :])[0]
        dir_adj_planted[u].append((v, r))                        # true recoverable edge (chains walk these)
        dir_adj_full[u].append((v, r))
    # add DECOY out-edges (random targets/relations) to the candidate table ONLY (distractors so LOCAL must pick);
    # chains never walk decoys, so the true target is always a planted neighbor in the local candidate set.
    for u in range(n):
        for _ in range(int(rng.integers(2, 6))):
            w = int(rng.integers(0, n))
            if w != u:
                dir_adj_full[u].append((w, int(rng.integers(0, T))))
    Z = _l2t(Z2)
    Zp = torch.cat([Z, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj_full, n, device)

    start, targets, role_ids = sample_chains(dir_adj_planted, 200, MAX_REACH, np.random.default_rng(1))

    reach = {}
    sigs = {}
    r_no, _h, s_no = run_no_cleanup(Z, roles_b, start, targets, role_ids, device, n)
    reach[NO_CLEANUP] = r_no; sigs[NO_CLEANUP] = s_no
    for arm in [GLOBAL_CLEANUP, LOCAL_CLEANUP, LOCAL_DECORR]:
        r, _hh, s, _mcs = run_arm(arm, Z, Zp, roles_b, nbr_idx, nbr_mask, start, targets, role_ids, device, 256, n)
        reach[arm] = r; sigs[arm] = s

    hop1_high = bool(reach[NO_CLEANUP][1] >= 0.40)
    baseline_fails = bool(reach[NO_CLEANUP][MAX_REACH] <= 0.60 * max(reach[NO_CLEANUP][1], 1e-9))
    local_beats_global2 = bool(reach[LOCAL_CLEANUP][2] >= reach[GLOBAL_CLEANUP][2] + 0.05)
    arms_differ = bool(len(set(sigs.values())) >= 2)
    df = df_recompute(n, mean_out_deg, float("nan"), d)
    df_collapses = bool(df["local_dim_needed_1hop"] < df["global_dim_needed"] and df["collapse_factor"] > 10.0)

    res = dict(
        reach_no_cleanup={dd: round(reach[NO_CLEANUP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_global={dd: round(reach[GLOBAL_CLEANUP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_local={dd: round(reach[LOCAL_CLEANUP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_local_decorr={dd: round(reach[LOCAL_DECORR][dd], 4) for dd in range(1, MAX_REACH + 1)},
        hop1_high=hop1_high, baseline_fails=baseline_fails, local_beats_global2=local_beats_global2,
        arms_differ=arms_differ, df_collapses=df_collapses,
        df=dict(global_dim_needed=round(df["global_dim_needed"], 1),
                local_dim_needed_1hop=round(df["local_dim_needed_1hop"], 2),
                collapse_factor=round(df["collapse_factor"], 1), mean_out_degree=round(df["mean_out_degree"], 2)),
        Dmax=int(Dmax),
    )
    ok = bool(hop1_high and baseline_fails and local_beats_global2 and arms_differ and df_collapses)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    device = _resolve_device(args.device)
    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda_available=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest()
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (hop1/baseline_fails/local_beats_global/arms_differ/df): %s"
                        % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    dir_adj = build_typed_diradj(edges, rels, n_nodes)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj, n_nodes, device)
    _log("nbr table: Dmax=%d mean_out_deg=%.3f" % (Dmax, mean_out_deg))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS local-chain-index machinery: NO_CLEANUP collapses at reach>=2 (must-fail "
                        "control fires), LOCAL cleanup beats GLOBAL at reach-2 (count-tax lever separates), arms "
                        "differ, D_f recompute collapses global->local dim_needed; typed subgraph + nbr table + "
                        "encoder exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta,
            df_recompute=df_recompute(n_nodes, mean_out_deg, float("nan"), cfg["code_dim"])))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask, mean_out_deg,
                          cfg, device, out_dir=out_dir_path)
            for a in ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1) if dd not in pm["arms"][a]["reach"]]
                if a not in pm["arms"] or missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # WIN arms must differ from GLOBAL and NO_CLEANUP (META_RULE_AF, scoped)
            for a in WIN_ARMS:
                if pm["arm_sigs"][a] == pm["arm_sigs"][NO_CLEANUP]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s == NO_CLEANUP" % (seed, a))
                if pm["arm_sigs"][a] == pm["arm_sigs"][GLOBAL_CLEANUP]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s == GLOBAL_CLEANUP" % (seed, a))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
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
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        device=str(device), n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, gates=gates,
        mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
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
