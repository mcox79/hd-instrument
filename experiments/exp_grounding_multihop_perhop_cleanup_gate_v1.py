"""Stage-4 reader: does a PER-HOP CLEANUP GATE inserted BETWEEN hops of a learned-code multi-hop retrieval
chain recover functional reach 2-3 -- where the Stage-3 chain (no cleanup) collapsed to reach 1 by learned-code
crosstalk at graph scale?

This is the revival of the VET-confirmed Stage-3 HARD_FAIL negative. The Stage-3 diagnosis (director backup
2026-07-08; sharpened HF): reach>=2 chaining on REAL learned (semantically-correlated) codes is walled by
LEARNED-CODE CROSSTALK / cleanup at graph scale, NOT the bind operator (block-code binding v1 already ruled the
operator out). The brain-grounding drill (notes/research_learned_code_crosstalk_cleanup_decorrelation_at_scale_
5x_2026-07-09.md) converged -- across hippocampal DG/CA3/CA1, cerebellar expansion, and VSA/resonator theory --
on ONE mechanism SHAPE: a repeated, LOCAL, per-hop re-sparsification + comparator/novelty gate between every
step, built to strip only INCIDENTAL redundancy while PRESERVING genuine semantic correlation (never global
orthogonalization). This cell inserts exactly that gate into the chain and tests reach recovery.

HONEST CEILING (pre-registered from the drill): target recovering REACH 2-3, NOT reach>=4-5. The brain does not
beat the correlated-crosstalk limit; it pushes the threshold back and keeps chains short (transitive inference
reliable to ~4-7 items with the full DG/CA3/CA1/theta machinery). HARD_PASS = material reach-2-3 recovery over
the no-cleanup baseline. HARD_FAIL = no material recovery (crosstalk floor is fundamental at our correlation
level -> next mechanism is hierarchical chunking / landmark-hub, not more cleanup). Both are gold.

ARMS (paired: identical planted chains + identical learned codes + identical seeds across all 4 arms):
  A NO_CLEANUP     : the Stage-3 chain. Raw HRR accumulation carried forward each hop (no per-hop cleanup);
                     a single global cleanup only at readout. MUST-FAIL / reference control: crosstalk
                     accumulates across hops -> collapse at reach>=2 (anti-saturation gate: MUST fail at smoke).
  B PLAIN_CLEANUP  : per-hop top-1 snap to the nearest codebook node code (generic cleanup, NO re-separation,
                     NO residual). Candidate mechanism (simplest per-hop cleanup) AND the attribution control
                     for the two sophisticated gates.
  C DG_RESEP       : Candidate 1 -- per-hop cleanup whose argmax-snap is computed in a fresh FIXED-random
                     sparse-expansion + k-WTA sketch space (granule-cell / DG pattern-separation re-encoding).
                     The chain snaps on RE-SEPARATED codes, reducing wrong-neighbour errors from correlation.
  D CA1_RESIDUAL   : Candidate 2 -- per-hop comparator/novelty gate. Forward only the UNPREDICTED component:
                     remove the incoming-cue-parallel ("already-explained") direction before the snap (CA1
                     novelty-detector / predictive-coding explaining-away). Its known failure mode (drill):
                     OVER-suppression of real signal -> can make fidelity WORSE (pre-registered HARD_FAIL dir).

DISCRIMINATOR: fidelity@d = hit@K (true node at hop d in top-K of the arm's readout score against the codebook),
measured along the SAME planted true typed L-hop paths for every arm; the chain commits top-1 each hop for the
cleanup arms (compounding), and carries the raw accumulated vector for NO_CLEANUP. Central question: does per-
hop cleanup (any of B/C/D) recover reach-2-3 fidelity materially over NO_CLEANUP on real correlated codes?

HONESTY: REAL-substrate multi-hop grounded retrieval on LEARNED codes. NOT language understanding. Codes are
the CG'd teacher-free relational encoder's semantically-correlated learned codes over the REAL ConceptNet
subgraph. Teacher-free, ASCII-only. Reuses ProjHead / info_nce / vicreg / char_trigram_features / the typed
subgraph loader / unitary HRR roles / crosstalk_floor; the numeric core (encoder + chain + cleanup gates) is
device-aware torch (cuda if available, else cpu) so the matmul-heavy codebook cleanup + DG sketch run on GPU.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash the 4 arms' fidelity-vs-depth curves).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: hit@K chance floor = K / n_nodes (~0.006 at n=5000, K=10); HARD_PASS usable floor 0.30 >> chance and
#   reachable in principle; the anti-saturation requirement is that NO_CLEANUP@reach2 COLLAPSES to <= 0.40 at
#   the smoke scale (verified empirically, not a closed-form estimator floor). crlb_n/a for the recovery gain.
# - baseline_in_band at smoke: NO_CLEANUP@1 >= 0.30 (single hop works; a genuine cap; MEASURED hit@10 ~0.44 at
#   smoke) AND NO_CLEANUP@2 collapses (<= 0.40 abs AND <= 0.50*@1). If it does not collapse ->
#   INCONCLUSIVE_BASELINE_DID_NOT_FAIL (re-spec). Bands are RELATIVE to the measured single-hop cap.
# - discriminator survives scale: the SATURATION-VACUOUS guard IS the must-fail control failing AT smoke scale;
#   SMOKE exercises the SAME 4 arms / same code path as FULL (only n_nodes/epochs/seeds/n_chains scale).
# - HARD_PASS strictly above floor: reach-2 gain >= 0.10 absolute over baseline is a clear categorical margin,
#   AND the gain must persist to reach-3 (>= 0.05) so a reach-2-only fluke is MIDDLE_BAND not HARD_PASS.
# - HP_SCOPE: recovery gates apply to the CANDIDATE arms {PLAIN_CLEANUP, DG_RESEP, CA1_RESIDUAL}; NO_CLEANUP is
#   the must-fail reference control (NOT expected to pass; must FAIL for the discriminator to be valid).
# - sweep axis: hop depth d in {1,2,3,4}; cardinality EXPECTED_N_UNITS = n_seeds; each seed asserted to produce
#   all 4 arms x all depths (arm/depth-cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (baseline-collapse gate recomputed empirically per run;
#   codebook-size-aware crosstalk floor sqrt(2 ln n / d); paired per-chain hits so the delta is paired).
# - PAIRED trials (arm-comparison discriminator): all arms share the identical planted chains + codes + seeds.
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
    ProjHead,
    vicreg_repulsion,
    build_adjlist,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    SUBGRAPH_BASE_SEED,
)
# Reuse the typed-subgraph loader, unitary HRR roles, and the codebook-size-aware crosstalk floor VERBATIM.
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
    crosstalk_floor,
)

ANCHOR_NAME = "grounding_multihop_perhop_cleanup_gate_v1"

# ---------------------------------------------------------------------------
# Device (cuda if available else cpu). The runner does NOT pass argv, so default sensibly per node:
# GPU node -> cuda (genuine GPU use for the matmul-heavy codebook cleanup + DG sketch); laptop smoke -> cpu.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    if arg_device == "cpu":
        return torch.device("cpu")
    if arg_device == "cuda":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")   # auto


# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME 4 arms / same code path as FULL; only scale differs)
# ---------------------------------------------------------------------------

HIT_K = 10                    # fidelity = hit@K (true node in top-K of the arm's readout score)
MAX_REACH = 4                 # measure fidelity through reach 4 (decay slope); PASS bar is reach 2-3 only
DG_ACTIVE_FRAC = 0.05         # DG sketch k-WTA active fraction (granule-cell sparse re-encoding)

SELFTEST_CFG = dict(
    seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    dg_dim=1024, n_chains=200, cos_floor_c=1.1,
)

SMOKE_CFG = dict(
    seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, code_dim=128, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    dg_dim=4096, n_chains=500, cos_floor_c=1.1,
)

FULL_CFG = dict(
    seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=256, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    dg_dim=8192, n_chains=1200, cos_floor_c=1.1,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run; anchored to the drill's REACH-2-3 honest ceiling)
# ---------------------------------------------------------------------------
# Bands are RELATIVE to the measured single-hop cap (NO_CLEANUP@1), per the drill's honest ceiling: "recover
# reach-2 to a usable working fidelity ~ within 15% of reach-1", NOT an absolute fidelity that ignores the
# encoder's single-hop ceiling. Smoke MEASURED the real single-hop cap at hit@10 ~ 0.44 (n=1525, code_dim=128,
# 60ep); an absolute 0.30 floor would be near-unreachable given hop1~0.44, so HARD_PASS uses RECOVER_FRAC*hop1.
HOP1_MIN = 0.30            # NO_CLEANUP@1 must clear this (single-hop cap present; >> chance ~0.007). MEASURED 0.44.
BASE_COLLAPSE_ABS = 0.40   # anti-saturation: NO_CLEANUP@2 must be <= this AND ...
BASE_COLLAPSE_FRAC = 0.50  # ... <= this fraction of NO_CLEANUP@1 (must-fail control lost >=half its reach). Smoke ~0.09x.
GAIN2_HP = 0.10            # HARD_PASS: candidate@2 - NO_CLEANUP@2 >= this absolute (material reach-2 recovery)
RECOVER_FRAC = 0.50        # HARD_PASS: candidate@2 >= this * candidate@1 (reach-2 keeps >=half the single-hop cap)
PERSIST3_HP = 0.05         # HARD_PASS: candidate@3 - NO_CLEANUP@3 >= this (reach-2 gain persists to reach 3)
MATERIAL_MIN = 0.05        # HARD_FAIL if NO candidate beats NO_CLEANUP@2 by >= this (crosstalk floor fundamental)
NOVELTY_LAMBDA = 0.50      # CA1 residual gain: forward pred - LAMBDA*cue_parallel (SOFT explaining-away; full
                           # removal LAMBDA=1.0 over-suppresses and destroyed hop-1 on real codes at smoke).

# Arm names
NO_CLEANUP = "NO_CLEANUP"
PLAIN_CLEANUP = "PLAIN_CLEANUP"
DG_RESEP = "DG_RESEP"
CA1_RESIDUAL = "CA1_RESIDUAL"
ARMS = [NO_CLEANUP, PLAIN_CLEANUP, DG_RESEP, CA1_RESIDUAL]
CANDIDATE_ARMS = [PLAIN_CLEANUP, DG_RESEP, CA1_RESIDUAL]   # HP_SCOPE: recovery gates apply to these


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
# Device-aware numeric primitives (torch; run on cuda when available)
# ---------------------------------------------------------------------------

def _l2t(x, eps=1e-8):
    return x / (x.norm(dim=1, keepdim=True) + eps)


def _info_nce_dev(za, zp, temp, device):
    """Symmetric InfoNCE (device-aware labels)."""
    za = _l2t(za)
    zp = _l2t(zp)
    logits = (za @ zp.t()) / temp
    labels = torch.arange(za.shape[0], device=device)
    return 0.5 * (torch.nn.functional.cross_entropy(logits, labels)
                  + torch.nn.functional.cross_entropy(logits.t(), labels))


def _hrr_bind_t(role, z):
    """Per-row HRR circular convolution: role,z [B, d] -> [B, d] (norm-preserving with unitary roles)."""
    d = z.shape[1]
    return torch.fft.irfft(torch.fft.rfft(role, dim=1) * torch.fft.rfft(z, dim=1), n=d, dim=1)


def _sketch(x, R, m):
    """DG granule-cell sparse re-encoding: fixed random expansion x@R then per-row top-m k-WTA, L2-normed.
    The k-WTA nonlinearity (not the linear projection, which preserves inner products by JL) is what
    DECORRELATES / pattern-separates correlated codes. x [B, d] -> [B, dg] sparse."""
    p = x @ R                                            # [B, dg]
    idx = p.abs().topk(m, dim=1).indices                # top-m by magnitude
    out = torch.zeros_like(p)
    out.scatter_(1, idx, p.gather(1, idx))
    return _l2t(out)


# ---------------------------------------------------------------------------
# Binding-structured encoder (device-aware, self-contained; reuses ProjHead + vicreg CG'd primitives).
# Base neighbour InfoNCE + VICReg + typed-binding-consistency InfoNCE (bind(role_r, z_i) lands on r-neighbour).
# Produces the REAL, semantically-correlated learned codes the chain runs over.
# ---------------------------------------------------------------------------

def train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=None, tag="BIND"):
    torch.manual_seed(seed)
    np.random.seed(seed)
    feat_dim = X.shape[1]
    Xt = torch.from_numpy(X).to(device)
    model = ProjHead(feat_dim, cfg["code_dim"]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
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
        flip = rng.random(bs) < 0.5
        ai = np.where(flip, e_b[eidx], e_a[eidx])
        pi = np.where(flip, e_a[eidx], e_b[eidx])
        ri = e_r[eidx]
        ha = model(Xt[torch.from_numpy(ai).to(device)])
        hp = model(Xt[torch.from_numpy(pi).to(device)])
        loss = _info_nce_dev(ha, hp, cfg["temp"], device) + vicreg_repulsion(
            torch.cat([ha, hp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
        za = _l2t(ha)
        bound = _hrr_bind_t(roles_t[torch.from_numpy(ri).to(device)], za)
        loss = loss + cfg["lambda_bind"] * _info_nce_dev(bound, hp, cfg["temp"], device)
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
        emb = _l2t(model(Xt))
    return emb.detach()    # [n, code_dim] on device, L2-normalized correlated learned codes


# ---------------------------------------------------------------------------
# Planted true typed L-hop paths over the REAL subgraph (directed typed multigraph; both orientations
# of each undirected typed edge are traversable under that relation role).
# ---------------------------------------------------------------------------

def build_typed_diradj(edges, rels, n_nodes):
    """dir_adj[u] = list of (v, r): u --r--> v is traversable (both orientations of each typed undirected edge)."""
    dir_adj = [[] for _ in range(n_nodes)]
    for (a, b), r in zip(edges, rels):
        a = int(a); b = int(b); r = int(r)
        if a == b:
            continue
        dir_adj[a].append((b, r))
        dir_adj[b].append((a, r))
    return dir_adj


def sample_chains(dir_adj, n_chains, L, rng):
    """Sample n_chains simple (no-revisit) length-L typed paths. Returns start [C], targets [L][C], role_ids
    [L][C] as int64 numpy. Random-walk from random starts with sufficient degree; restart on dead-ends."""
    starts = []
    tgt = [[] for _ in range(L)]
    rid = [[] for _ in range(L)]
    n = len(dir_adj)
    cands = [u for u in range(n) if len(dir_adj[u]) > 0]
    if not cands:
        raise RuntimeError("PLANT_FAIL: no nodes with typed out-edges")
    tries = 0
    max_tries = n_chains * 200 + 10000
    while len(starts) < n_chains and tries < max_tries:
        tries += 1
        u0 = int(rng.choice(cands))
        path = [u0]
        rels_path = []
        visited = {u0}
        ok = True
        cur = u0
        for _h in range(L):
            nbrs = [(v, r) for (v, r) in dir_adj[cur] if v not in visited]
            if not nbrs:
                ok = False
                break
            v, r = nbrs[int(rng.integers(0, len(nbrs)))]
            path.append(v)
            rels_path.append(r)
            visited.add(v)
            cur = v
        if not ok:
            continue
        starts.append(u0)
        for h in range(L):
            tgt[h].append(path[h + 1])
            rid[h].append(rels_path[h])
    C = len(starts)
    if C < max(8, n_chains // 5):
        raise RuntimeError("PLANT_FAIL: only %d/%d length-%d chains found (graph too sparse)" % (C, n_chains, L))
    return (np.asarray(starts, dtype=np.int64),
            [np.asarray(t, dtype=np.int64) for t in tgt],
            [np.asarray(r, dtype=np.int64) for r in rid])


# ---------------------------------------------------------------------------
# Chain retrieval with a per-hop cleanup gate (the core discriminator). All arms paired on identical chains.
# ---------------------------------------------------------------------------

def _hit_at_k(scores, targets, k):
    """scores [C, n] readout vs codebook; targets [C]. Returns per-chain bool hit@k (target in top-k)."""
    topk = scores.topk(k, dim=1).indices                       # [C, k]
    return (topk == targets[:, None]).any(dim=1)               # [C] bool


def run_chain_arm(arm, Z, Zsk, R, m, roles_t, start, targets, role_ids, k, device):
    """Run one arm's chain. Returns fid[d] (d=1..L) float and a per-chain-hit signature for arms-differ.
    Z [n, d] codes; Zsk [n, dg] DG sketches of codes; roles_t [T, d]; targets/role_ids per hop [L][C]."""
    L = len(targets)
    n = Z.shape[0]
    C = start.shape[0]
    Zt = Z                                                     # [n, d] (already L2-normed on device)
    cue = Z[torch.from_numpy(start).to(device)].clone()       # [C, d] start codes
    fid = {}
    hit_sig = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]   # [C, d]
        pred = _hrr_bind_t(role, cue)                              # [C, d] hop bind
        tgt = torch.from_numpy(targets[h]).to(device)             # [C]
        if arm == NO_CLEANUP:
            # raw accumulation carried forward; global cleanup only at readout (the Stage-3 chain)
            score = _l2t(pred) @ Zt.t()                            # [C, n]
            hits = _hit_at_k(score, tgt, k)
            cue = pred                                            # NO per-hop cleanup: crosstalk accumulates
        elif arm == PLAIN_CLEANUP:
            score = _l2t(pred) @ Zt.t()
            hits = _hit_at_k(score, tgt, k)
            est = score.argmax(dim=1)                            # top-1 commit
            cue = Zt[est]                                        # snap to clean codebook node code
        elif arm == DG_RESEP:
            sp = _sketch(pred, R, m)                             # re-separate in DG sparse-expansion space
            score = sp @ Zsk.t()                                # [C, n] readout in sketch space
            hits = _hit_at_k(score, tgt, k)
            est = score.argmax(dim=1)
            cue = Zt[est]                                        # carry the clean node code forward
        elif arm == CA1_RESIDUAL:
            cue_hat = _l2t(cue)
            proj = (pred * cue_hat).sum(dim=1, keepdim=True) * cue_hat   # cue-parallel "already-explained" part
            nov = pred - NOVELTY_LAMBDA * proj                  # forward the novel component (SOFT explaining-away)
            score = _l2t(nov) @ Zt.t()
            hits = _hit_at_k(score, tgt, k)
            est = score.argmax(dim=1)
            cue = Zt[est]
        else:
            raise ValueError("unknown arm %r" % arm)
        fid[h + 1] = float(hits.float().mean().item())
        hit_sig.append(hits.detach().to("cpu").numpy().astype(np.uint8))
    sig = hashlib.sha256(np.concatenate(hit_sig).tobytes()).hexdigest()
    return fid, sig


# ---------------------------------------------------------------------------
# Per-model-seed run: all 4 arms on the identical planted chains + codes
# ---------------------------------------------------------------------------

def run_seed(seed, X, edges, rels, dir_adj, roles_t, cfg, device, out_dir=None):
    n_nodes = X.shape[0]
    d = cfg["code_dim"]
    dg = cfg["dg_dim"]
    m = max(1, int(round(DG_ACTIVE_FRAC * dg)))

    # learned correlated codes
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()

    # fixed random DG expansion + code sketches (granule-cell re-encoding basis)
    g = torch.Generator(device="cpu").manual_seed(seed + 4242)
    R = (torch.randn(d, dg, generator=g) / np.sqrt(d)).to(device)          # [d, dg]
    Zsk = _sketch(Z, R, m)                                                 # [n, dg] sparse code sketches
    sketch_active = float((Zsk != 0).float().mean().item())

    # planted true typed L-hop chains (SAME for every arm -> paired)
    chain_rng = np.random.default_rng(seed + 909)
    start, targets, role_ids = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, chain_rng)
    n_chains_got = int(start.shape[0])

    arms = {}
    sigs = {}
    for arm in ARMS:
        fid, sig = run_chain_arm(arm, Z, Zsk, R, m, roles_t, start, targets, role_ids, HIT_K, device)
        arms[arm] = dict(fid=fid)
        sigs[arm] = sig
        _log("  seed=%d %-14s fid@[1..%d]=%s" % (
            seed, arm, MAX_REACH, {dd: round(fid[dd], 3) for dd in range(1, MAX_REACH + 1)}))

    # ARMS-MUST-DIFFER: per-chain hit signatures must not be bit-identical across arms
    uniq = len(set(sigs.values()))
    if uniq < 2:
        _log("  [warn] seed=%d all arm hit-signatures identical -- arms may not differ" % seed)

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig,
                n_chains=n_chains_got, sketch_active=sketch_active, dg_active_m=m)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _decay_slope(fid):
    """Linear-fit slope of fidelity across d=1..MAX_REACH (more negative = steeper crosstalk decay)."""
    ds = np.array([d for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    ys = np.array([fid[d] for d in range(1, MAX_REACH + 1)], dtype=np.float64)
    if np.any(ys != ys):
        return float("nan")
    A = np.vstack([ds, np.ones_like(ds)]).T
    slope = float(np.linalg.lstsq(A, ys, rcond=None)[0][0])
    return slope


def aggregate_and_verdict(per_seed, subgraph_meta, cfg):
    # mean fidelity per arm per depth over seeds
    fid = {a: {d: _nanmean([m["arms"][a]["fid"][d] for m in per_seed]) for d in range(1, MAX_REACH + 1)}
           for a in ARMS}
    slope = {a: _decay_slope(fid[a]) for a in ARMS}

    base1 = fid[NO_CLEANUP][1]
    base2 = fid[NO_CLEANUP][2]
    base3 = fid[NO_CLEANUP][3]

    hop1_ok = (base1 == base1) and (base1 >= HOP1_MIN)
    baseline_collapses = (base2 == base2 and base1 == base1
                          and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * base1)

    # per-candidate recovery evaluation (paired means over identical chains/seeds). HARD_PASS is RELATIVE to
    # each candidate's OWN single-hop cap (RECOVER_FRAC*cand@1) per the drill's reach-2-within-15%-of-reach-1
    # ceiling, AND an absolute margin over the collapsed baseline, AND persistence to reach 3.
    cand_eval = {}
    for a in CANDIDATE_ARMS:
        c1 = fid[a][1]
        c2 = fid[a][2]
        c3 = fid[a][3]
        gain2 = (c2 - base2) if (c2 == c2 and base2 == base2) else float("nan")
        gain3 = (c3 - base3) if (c3 == c3 and base3 == base3) else float("nan")
        recover_floor = (RECOVER_FRAC * c1) if c1 == c1 else float("nan")
        hp = bool(gain2 == gain2 and gain2 >= GAIN2_HP
                  and c2 == c2 and recover_floor == recover_floor and c2 >= recover_floor
                  and gain3 == gain3 and gain3 >= PERSIST3_HP)
        cand_eval[a] = dict(fid1=c1, fid2=c2, fid3=c3, gain2=gain2, gain3=gain3,
                            recover_floor=recover_floor, hard_pass=hp)

    hp_arms = [a for a in CANDIDATE_ARMS if cand_eval[a]["hard_pass"]]
    best_gain2 = max([cand_eval[a]["gain2"] for a in CANDIDATE_ARMS
                      if cand_eval[a]["gain2"] == cand_eval[a]["gain2"]], default=float("nan"))
    best_cand = max(CANDIDATE_ARMS,
                    key=lambda a: (cand_eval[a]["gain2"] if cand_eval[a]["gain2"] == cand_eval[a]["gain2"]
                                   else -1e9))
    any_material = bool(best_gain2 == best_gain2 and best_gain2 >= MATERIAL_MIN)

    if not hop1_ok:
        verdict = "INCONCLUSIVE_RECOVERY_FAILED"          # single-hop broken -> chain unattributable
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"    # saturation-vacuous; must-fail control did not fail
    elif len(hp_arms) > 0:
        verdict = "HARD_PASS"                             # per-hop cleanup recovers reach 2-3 materially
    elif not any_material:
        verdict = "HARD_FAIL_CROSSTALK_FLOOR_FUNDAMENTAL"  # no cleanup variant helps at this correlation level
    else:
        verdict = "MIDDLE_BAND"                           # partial gain (0.05-0.10) or reach-2-only (no persist)

    verdict_msg = (
        "%s || NO_CLEANUP fid@1=%.3f(hop1_ok=%s cap) @2=%.3f(collapses=%s) @3=%.3f @4=%.3f slope=%.3f || "
        "PLAIN @2=%.3f(gain2=%s) DG_RESEP @2=%.3f(gain2=%s) CA1_RESIDUAL @2=%.3f(gain2=%s) || "
        "best_cand=%s best_gain2=%s hp_arms=%s any_material(>=%.2f)=%s || bands: HOP1>=%.2f BASE_COLLAPSE<=%.2f&<=%.2fx@1 "
        "GAIN2_HP>=%.2f RECOVER>=%.2fx(cand@1) PERSIST3>=%.2f || n=%d E=%d rel_types=%d seeds=%d n_chains~%d hit@K=%d" % (
            verdict, base1, hop1_ok, base2, baseline_collapses, base3, fid[NO_CLEANUP][4], slope[NO_CLEANUP],
            fid[PLAIN_CLEANUP][2], _fmt(cand_eval[PLAIN_CLEANUP]["gain2"]),
            fid[DG_RESEP][2], _fmt(cand_eval[DG_RESEP]["gain2"]),
            fid[CA1_RESIDUAL][2], _fmt(cand_eval[CA1_RESIDUAL]["gain2"]),
            best_cand, _fmt(best_gain2), hp_arms, MATERIAL_MIN, any_material,
            HOP1_MIN, BASE_COLLAPSE_ABS, BASE_COLLAPSE_FRAC, GAIN2_HP, RECOVER_FRAC, PERSIST3_HP,
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed), int(_nanmean([m["n_chains"] for m in per_seed])), HIT_K))

    gates = dict(
        verdict=verdict, fid_mean=fid, decay_slope=slope,
        base_fid1=base1, base_fid2=base2, base_fid3=base3,
        hop1_ok=bool(hop1_ok), baseline_collapses=bool(baseline_collapses),
        candidate_eval=cand_eval, hp_arms=hp_arms, best_candidate=best_cand,
        best_gain2=best_gain2, any_material=bool(any_material),
        bands=dict(HOP1_MIN=HOP1_MIN, BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS,
                   BASE_COLLAPSE_FRAC=BASE_COLLAPSE_FRAC, GAIN2_HP=GAIN2_HP,
                   RECOVER_FRAC=RECOVER_FRAC, PERSIST3_HP=PERSIST3_HP, MATERIAL_MIN=MATERIAL_MIN,
                   NOVELTY_LAMBDA=NOVELTY_LAMBDA, HIT_K=HIT_K, MAX_REACH=MAX_REACH,
                   DG_ACTIVE_FRAC=DG_ACTIVE_FRAC),
    )
    return verdict, verdict_msg, gates


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


# ---------------------------------------------------------------------------
# Discriminator / mechanism self-test (ALWAYS runs, CPU)
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    """On PLANTED correlated codes with a real typed chain, prove: (0) the chain machinery works (NO_CLEANUP
    hop-1 fidelity high); (1) the must-fail control genuinely FAILS at reach>=2 (NO_CLEANUP@2 collapses well
    below @1) -- the discriminator is NOT saturation-vacuous / is telemetry-sensitive; (2) at least one per-hop
    cleanup variant recovers reach-2 over NO_CLEANUP (the metric CAN separate); (3) the 4 arms differ (distinct
    per-chain hit signatures); (4) the DG sketch DECORRELATES (mean |cos| among sketches < among raw codes on
    correlated codes); (5) the CA1 residual genuinely removes the cue-parallel component (cos(nov, cue) ~ 0)."""
    device = torch.device("cpu")
    rng = np.random.default_rng(0)
    d = 128
    dg = 1024
    m = max(1, int(round(DG_ACTIVE_FRAC * dg)))
    T = 4
    n = 1200
    roles_np = make_unitary_roles(T, d, rng)
    roles_t = torch.from_numpy(roles_np).to(device)

    # planted CORRELATED codebook + a recoverable typed chain. Unit-normalized components so the BIND term
    # (weight 1.0) dominates hop-1 recovery, while a shared per-cluster component (0.30) injects the semantic
    # correlation that makes raw accumulation (NO_CLEANUP) collapse past reach 1 and lets snapping (PLAIN) reset
    # it. Z[v] = normalize(bind(role_r, Z[u]) + 0.30*base_cluster(v) + 0.20*noise_v) along a Hamiltonian walk.
    n_clusters = 40
    per = n // n_clusters
    base = rng.standard_normal((n_clusters, d)).astype(np.float32)
    base_u = base / (np.linalg.norm(base, axis=1, keepdims=True) + 1e-8)
    base_ut = torch.from_numpy(base_u.astype(np.float32)).to(device)
    # forward-only adjacency: bind(role_r, Z[u]) ~ Z[v] holds only in the planted (forward) direction, since
    # HRR bind is not symmetric. (In the REAL run the encoder is trained with random edge-flip, so binding is
    # symmetric there and the real dir_adj carries both orientations; the self-test controls its own planting.)
    dir_adj = [[] for _ in range(n)]
    order = rng.permutation(n)
    Z2 = torch.zeros(n, d, device=device)
    u0 = int(order[0])
    Z2[u0] = _l2t((base_ut[u0 // per] + 0.20 * torch.randn(d))[None, :])[0]
    for k in range(1, n):
        u = int(order[k - 1]); v = int(order[k]); r = int(rng.integers(0, T))
        pred = _l2t(_hrr_bind_t(roles_t[r:r + 1], _l2t(Z2[u:u + 1])))[0]
        nz = _l2t(torch.randn(1, d))[0]
        Z2[v] = _l2t((pred + 0.50 * base_ut[v // per] + 1.60 * nz)[None, :])[0]
        dir_adj[u].append((v, r))          # forward only (planted recoverable direction)
    Z = _l2t(Z2)

    R = (torch.randn(d, dg) / np.sqrt(d)).to(device)
    Zsk = _sketch(Z, R, m)

    cfg = dict(code_dim=d, dg_dim=dg, n_chains=150)
    start, targets, role_ids = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, np.random.default_rng(1))

    fid = {}
    sigs = {}
    for arm in ARMS:
        f, s = run_chain_arm(arm, Z, Zsk, R, m, roles_t, start, targets, role_ids, HIT_K, device)
        fid[arm] = f
        sigs[arm] = s

    # Machinery-feasibility gates: with unitary roles + hit@K, raw HRR accumulation is robust on cleanly-
    # planted near-orthogonal codes at reach 2 (collapse is a deeper phenomenon here); assert the discriminator
    # fires at the DEEPEST reach (where accumulation guarantees separation). The reach-2 anti-saturation gate is
    # enforced on the REAL correlated codes at smoke (baseline_collapses in aggregate_and_verdict), not here.
    R_ = MAX_REACH
    hop1_high = bool(fid[NO_CLEANUP][1] >= 0.55)
    baseline_fails = bool(fid[NO_CLEANUP][R_] <= 0.70 * fid[NO_CLEANUP][1])
    best_cand_gain_deep = max(fid[a][R_] - fid[NO_CLEANUP][R_] for a in CANDIDATE_ARMS)
    metric_separates = bool(best_cand_gain_deep >= 0.05)
    arms_differ = bool(len(set(sigs.values())) >= 2)

    # DG sketch decorrelates on correlated codes
    def _mean_abs_offdiag_cos(M):
        Mn = _l2t(M)
        s = 200
        idx = torch.from_numpy(np.random.default_rng(3).choice(M.shape[0], size=s, replace=False))
        sub = Mn[idx]
        cc = (sub @ sub.t()).abs()
        off = cc - torch.diag(torch.diag(cc))
        return float(off.sum().item() / (s * (s - 1)))
    cos_raw = _mean_abs_offdiag_cos(Z)
    cos_sk = _mean_abs_offdiag_cos(Zsk)
    sketch_decorrelates = bool(cos_sk < cos_raw)

    # CA1 residual removes cue-parallel component
    cue = Z[torch.from_numpy(start[:64]).to(device)]
    role = roles_t[torch.from_numpy(role_ids[0][:64]).to(device)]
    pred = _hrr_bind_t(role, cue)
    cue_hat = _l2t(cue)
    proj = (pred * cue_hat).sum(dim=1, keepdim=True) * cue_hat
    nov = pred - NOVELTY_LAMBDA * proj
    pred_cos = float((_l2t(pred) * cue_hat).sum(dim=1).abs().mean().item())
    resid_cos = float((_l2t(nov) * cue_hat).sum(dim=1).abs().mean().item())
    residual_reduces_cue = bool(resid_cos < pred_cos)   # soft explaining-away reduces cue-parallel alignment

    res = dict(
        fid_no_cleanup={dd: round(fid[NO_CLEANUP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        fid_plain={dd: round(fid[PLAIN_CLEANUP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        fid_dg={dd: round(fid[DG_RESEP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        fid_ca1={dd: round(fid[CA1_RESIDUAL][dd], 4) for dd in range(1, MAX_REACH + 1)},
        hop1_high=hop1_high, baseline_fails=baseline_fails, best_cand_gain_deep=float(best_cand_gain_deep),
        metric_separates=metric_separates, arms_differ=arms_differ,
        cos_raw=cos_raw, cos_sketch=cos_sk, sketch_decorrelates=sketch_decorrelates,
        resid_pred_cos=pred_cos, resid_cue_cos=resid_cos, residual_reduces_cue=residual_reduces_cue,
    )
    ok = bool(hop1_high and baseline_fails and metric_separates and arms_differ
              and sketch_decorrelates and residual_reduces_cue)
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
            verdict_msg="MECHANISM_SELFTEST_FAILED (hop1/baseline_fails/separates/arms_differ/sketch/residual): %s"
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

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_np = make_unitary_roles(T, cfg["code_dim"], role_rng)
    roles_t = torch.from_numpy(roles_np).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS per-hop cleanup gate chain machinery: NO_CLEANUP collapses at reach>=2 "
                        "(must-fail control fires), a cleanup variant separates, arms differ, DG sketch "
                        "decorrelates, CA1 residual orthogonalizes; typed subgraph + roles exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, X, edges, rels, dir_adj, roles_t, cfg, device, out_dir=out_dir_path)
            # arm/depth cardinality: every arm x every depth present
            for a in ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1) if dd not in pm["arms"][a]["fid"]]
                if a not in pm["arms"] or missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            if len(set(pm["arm_sigs"].values())) < 2:
                _log("  [warn] arm hit-signatures collapsed to <2 distinct (seed=%d)" % seed)
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
