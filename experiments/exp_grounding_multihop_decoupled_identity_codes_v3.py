"""Stage-5 reader WIN-CELL v3: DECOUPLED / NEAR-ORTHOGONAL IDENTITY CODES to crack the same-relation aliasing floor.

THESIS (VET-corrected continuation of exp_grounding_multihop_local_chain_index_v2, commit 8efbb57b7 =
HARD_FAIL_SEMANTIC_FLOOR): v2's LOCAL-neighborhood-scoping count-tax fix WORKS (LOCAL reach1=0.453 vs GLOBAL
0.088; 6x lift) but reveals the floor beneath: SAME-RELATION ALIASING. Among LOCAL hop-2 errors, aliasing_frac
=0.815 vs same-relation base_rate=0.491 (excess=0.324) -- same-relation sibling nodes have codes too similar to
disambiguate, AND that confusability EXCEEDS the graph's structural base rate: the codes ACTIVELY mislead toward
the wrong sibling beyond chance. It is NOT fundamental: the v2 self-test with CLEAN PLANTED separable codes gives
LOCAL=1.0 at all depths. The char-trigram+InfoNCE codes are the problem -- trigram features inject WORD-SURFACE
correlation, and same-relation siblings tend to be semantically similar, so the binding encoder places their
codes too close.

FIX UNDER TEST (relation-conditioned scoring was RULED OUT -- same-relation siblings SHARE the relation so
conditioning adds no discriminative info): attack the REPRESENTATION. Replace the semantically-correlated char-
trigram input features with NEAR-ORTHOGONAL IDENTITY features (random Gaussian per-node, pairwise cosine ~
1/sqrt(feat_dim)), decoupled from word semantics. The binding encoder then places each node's code freed from the
trigram-correlation constraint, so same-relation siblings separate by IDENTITY rather than being pulled together
by shared surface content (DG pattern-separation analog: decouple the decorrelated chain/identity layer from the
correlated retrieval-semantic layer). Everything else (LOCAL candidate scoping, chains, roles, seeds, dim) is
held IDENTICAL to v2 -- any gap is purely the CODE design (feature decoupling), a clean within-dim attribution.

ARMS (6; PAIRED: identical planted chains + identical roles + identical seeds + identical graph + identical dim
across ALL arms; ONLY the input features (=> learned codes) and the cleanup candidate set / scoring differ):
  1 NO_CLEANUP         : must-fail control. Z_sem, raw HRR accumulation, top-1 GLOBAL readout. MUST collapse @>=2.
  2 GLOBAL_SEMANTIC    : reference (reported, NOT gated). Z_sem, per-hop top-1 snap over the FULL codebook.
  3 LOCAL_SEMANTIC     : BASELINE floor (= v2 LOCAL_CLEANUP). Z_sem, LOCAL snap. alpha_id=0.0.
  4 LOCAL_PARTIAL      : dose midpoint. Z_partial (features = normalize(0.5*sem + 0.5*identity)), LOCAL snap.
  5 LOCAL_DECOUPLED    : THE WIN LEVER. Z_id (near-orthogonal identity features), LOCAL snap. alpha_id=1.0.
  6 LOCAL_DECOUPLED_DG : strongest identity form. Z_id + DG sparse-expansion (k-WTA) re-separation at scoring.

WIN_ARMS (HP_SCOPE): {LOCAL_DECOUPLED, LOCAL_DECOUPLED_DG}. DOSE arms (aliasing monotonicity / necessity-under-
ablation): [LOCAL_SEMANTIC(0.0), LOCAL_PARTIAL(0.5), LOCAL_DECOUPLED(1.0)].

METRIC (primary, gated): reach@d = TOP-1 COMMIT accuracy at hop d. local_aliasing_frac per LOCAL arm (mechanism
check: does decoupling reduce the excess toward the same-relation base rate?). hit@10 = SECONDARY (not gated).

WIN BAR (pre-registered BEFORE the run):
  HARD_PASS_DECOUPLED_WIN = a WIN_ARM reach2 >= 0.60 AND reach3 >= 0.35 AND aliasing reduced (excess_semantic -
                        excess_decoupled >= 0.10). Collision cracked at modest dim.
  HARD_FAIL_IDENTITY_NOT_LEVER = aliasing NOT reduced (excess drop < 0.10) AND best WIN_ARM reach2 < 0.15.
                        Identity separation is not the lever; the residual is a genuine floor.
  MIDDLE_BAND_PARTIAL = partial crossing (aliasing drops but reach short of WIN, OR reach lifts but misses band).

DISCRIMINATOR-SURVIVES-SCALE: the aliasing discriminator is GRAPH-STRUCTURAL (local neighborhood ~ mean_out_deg,
scale-independent). It fires at smoke on the real subgraph: NO_CLEANUP collapses @>=2; LOCAL_SEMANTIC aliasing
excess is high; the KEY mechanism gap (LOCAL_DECOUPLED excess < LOCAL_SEMANTIC excess) must show DIRECTIONALLY at
smoke. Smoke uses the SAME 6 arms / same code path as FULL; only scale differs.

HONESTY: REAL CG'd teacher-free relational learned codes over the REAL ConceptNet typed subgraph; top-1 commit
fidelity; NO language understanding claimed. Identity features are random near-orthogonal per-node vectors (no
word content) -- a legitimate representational choice (pattern-separation analog), NOT oracle-cheating: the
encoder must still LEARN bind(role_r, code[u]) -> code[v] over the real edges; wrong commits propagate to wrong
candidate sets. The LOCAL candidate restriction is legitimate for KG traversal (adjacency known at each step).
Teacher-free, ASCII-only, device-aware torch. Reuses Stage-4/5 VET-landed encoder/chain/LOCAL-scoping primitives
VERBATIM (calibration continuity + no drift).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; WIN arms use Z_id != Z_sem => distinct commit signatures;
#   LOCAL_DECOUPLED asserted != LOCAL_SEMANTIC != NO_CLEANUP).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000); LOCAL load 6.65/2048=0.0032 << resonator thresh
#   0.056 so the count-tax is NOT the constraint at this dim; the residual is code correlation (measured aliasing
#   excess, not a closed-form floor). crlb_n/a for the semantic-floor branch.
# - baseline_in_band: LOCAL_SEMANTIC@1 in (0.05, 0.95) at smoke (v2 MEASURED 0.453). NO_CLEANUP@2 collapses.
# - discriminator survives scale: aliasing lever is scale-independent (local neighborhood at all n); the
#   DECOUPLED-reduces-aliasing gap FIRES AT SMOKE (option A/C). Documented + asserted at smoke.
# - HARD_PASS strictly above floor: reach2>=0.60 AND reach3>=0.35 AND aliasing excess drop>=0.10 (all three).
# - HP_SCOPE: WIN gate applies ONLY to {LOCAL_DECOUPLED, LOCAL_DECOUPLED_DG}. NO_CLEANUP=must-fail; GLOBAL/LOCAL_
#   SEMANTIC/LOCAL_PARTIAL = reference/dose arms (reported, not WIN-gated).
# - sweep axis: identity_fraction alpha_id in {0.0,0.5,1.0}; hop depth d in {1..4}; EXPECTED_N_UNITS = n_seeds;
#   each seed asserted to produce all 6 arms x all depths (arm/depth cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (baseline-collapse + baseline-in-band + aliasing base
#   rate recomputed empirically per run; paired per-chain top-1 commits so all deltas are paired).
# - PAIRED trials (arm-comparison discriminator): all arms share identical chains + roles + seeds + graph + dim.
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
# Reuse the Stage-4/5 VET-landed primitives VERBATIM (calibration continuity + no drift).
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _l2t,
)

ANCHOR_NAME = "grounding_multihop_decoupled_identity_codes_v3"

HIT_K = 10            # SECONDARY diagnostic only (hit@K continuity); NOT gated
MAX_REACH = 4         # measure reach through 4; WIN bar is reach 2-3
RESONATOR_THRESH = 0.056   # CITED@arXiv:1906.11684 resonator D_f/N stability threshold

# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME 6 arms / same code path as FULL; only scale differs.
# dim is MODEST + IDENTICAL to v2 (2048 full) so any gap is purely the CODE design, not dimension.
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=200, chain_chunk=256, dg_dim=1024, dg_active_frac=0.05,
)

SMOKE_CFG = dict(
    seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, code_dim=512, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=500, chain_chunk=256, dg_dim=4096, dg_active_frac=0.05,
)

FULL_CFG = dict(
    seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=2048, feat_dim=8192,
    temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
    n_chains=1200, chain_chunk=256, dg_dim=8192, dg_active_frac=0.05,
)

# ---------------------------------------------------------------------------
# Pre-registered WIN bands (picked BEFORE the run). Metric = TOP-1 COMMIT accuracy.
# ---------------------------------------------------------------------------
HOP1_PRESENT = 0.08        # GLOBAL_SEMANTIC@1 must clear this (single-hop machinery works; >> chance ~0.0002)
BASE_IN_BAND_HI = 0.95     # LOCAL_SEMANTIC@1 must be < this (baseline in measurable band)
BASE_COLLAPSE_ABS = 0.10   # anti-saturation: NO_CLEANUP@2 <= this AND ...
BASE_COLLAPSE_FRAC = 0.50  # ... <= this fraction of NO_CLEANUP@1 (must-fail control lost >= half its reach)
WIN_REACH2 = 0.60          # WIN: best WIN_ARM reach-2 top-1 commit >= this
WIN_REACH3 = 0.35          # WIN: best WIN_ARM reach-3 top-1 commit >= this
ALIAS_DROP_MIN = 0.10      # MECHANISM: LOCAL_DECOUPLED excess must be >= this much BELOW LOCAL_SEMANTIC excess
FAIL_REACH2 = 0.15         # HARD_FAIL floor: best WIN_ARM reach2 < this (with no aliasing drop) => not the lever

# Arm names
NO_CLEANUP = "NO_CLEANUP"
GLOBAL_SEMANTIC = "GLOBAL_SEMANTIC"
LOCAL_SEMANTIC = "LOCAL_SEMANTIC"
LOCAL_PARTIAL = "LOCAL_PARTIAL"
LOCAL_DECOUPLED = "LOCAL_DECOUPLED"
LOCAL_DECOUPLED_DG = "LOCAL_DECOUPLED_DG"
ARMS = [NO_CLEANUP, GLOBAL_SEMANTIC, LOCAL_SEMANTIC, LOCAL_PARTIAL, LOCAL_DECOUPLED, LOCAL_DECOUPLED_DG]
WIN_ARMS = [LOCAL_DECOUPLED, LOCAL_DECOUPLED_DG]      # HP_SCOPE: WIN gate applies to these only
DOSE_ARMS = [LOCAL_SEMANTIC, LOCAL_PARTIAL, LOCAL_DECOUPLED]   # aliasing monotonicity (necessity/dose)
LOCAL_ARMS = [LOCAL_SEMANTIC, LOCAL_PARTIAL, LOCAL_DECOUPLED, LOCAL_DECOUPLED_DG]

# arm -> (encoder key, scoring mode). encoder key selects which learned codes Z the arm uses.
#   scoring mode: "raw_global" (NO_CLEANUP), "global" (global cleanup), "local" (local snap),
#                 "local_dg" (local snap in DG re-separated sketch space).
ARM_SPEC = {
    NO_CLEANUP:         ("sem", "raw_global"),
    GLOBAL_SEMANTIC:    ("sem", "global"),
    LOCAL_SEMANTIC:     ("sem", "local"),
    LOCAL_PARTIAL:      ("partial", "local"),
    LOCAL_DECOUPLED:    ("id", "local"),
    LOCAL_DECOUPLED_DG: ("id", "local_dg"),
}
ALPHA_ID = {"sem": 0.0, "partial": 0.5, "id": 1.0}   # identity fraction per encoder


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
# Feature builders. Semantic = char-trigram (correlated, word-surface). Identity = random near-orthogonal per
# node (decoupled from word content; pairwise cosine ~ 1/sqrt(feat_dim)). Partial = normalized convex mix.
# ---------------------------------------------------------------------------

def identity_features(n, feat_dim, seed):
    """Random near-orthogonal per-node identity features, L2-normalized rows. Shape [n, feat_dim]. No word
    content. Decoupled from surface semantics: two nodes' features are correlated only by chance (~1/sqrt(D))."""
    rng = np.random.default_rng(seed + 5150)
    X = rng.standard_normal((n, feat_dim)).astype(np.float32)
    X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def mixed_features(X_sem, X_id, alpha_id):
    """Convex mix of L2-normed semantic + identity features, renormalized. alpha_id in [0,1]."""
    X = (1.0 - alpha_id) * X_sem + alpha_id * X_id
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n == 0.0] = 1.0
    return (X / n).astype(np.float32)


def build_features(node_words, cfg, seed, encoder_key):
    """Return the input feature matrix [n, feat_dim] for the given encoder key (sem / partial / id)."""
    feat_dim = cfg["feat_dim"]
    X_sem = char_trigram_features(node_words, feat_dim)
    if encoder_key == "sem":
        return X_sem
    X_id = identity_features(len(node_words), feat_dim, seed)
    if encoder_key == "id":
        return X_id
    if encoder_key == "partial":
        return mixed_features(X_sem, X_id, ALPHA_ID["partial"])
    raise ValueError("unknown encoder_key %r" % encoder_key)


# ---------------------------------------------------------------------------
# DG granule-cell sparse re-encoding (k-WTA re-separation). The k-WTA nonlinearity (not the linear projection,
# which preserves inner products by JL) is what pattern-separates. x [B, d] -> [B, dg] sparse, L2-normed.
# ---------------------------------------------------------------------------

def _sketch(x, R, m):
    p = x @ R                                            # [B, dg]
    idx = p.abs().topk(m, dim=1).indices                # top-m by magnitude
    out = torch.zeros_like(p)
    out.scatter_(1, idx, p.gather(1, idx))
    return _l2t(out)


# ---------------------------------------------------------------------------
# Padded neighbor table for local-candidate scoring. Node index n_nodes is a DEAD sentinel (empty neighbor row).
# ---------------------------------------------------------------------------

def build_nbr_table(dir_adj, n_nodes, device):
    """Returns nbr_idx [n+1, Dmax] (node ids, padded n_nodes sentinel), nbr_rel [n+1, Dmax] (relation ids,
    padded -1), nbr_mask [n+1, Dmax] bool. Row n_nodes = all-padding dead sentinel."""
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


def _local_scores(pred_score_blk, cur_blk, Zscore_p, nbr_idx, nbr_mask):
    """Local candidate scoring for a block. pred_score_blk [B, ds] (already L2-ready + already sketched for dg),
    cur_blk [B] current-node ids, Zscore_p [n+1, ds] padded scoring codes (row n = 0).
    Returns (score [B, Dmax] with -inf at padding, cand [B, Dmax] node ids, mask [B, Dmax], cset_size [B])."""
    cand = nbr_idx[cur_blk]                       # [B, Dmax] node ids (sentinel n at padding)
    mask = nbr_mask[cur_blk]                       # [B, Dmax] bool
    Zc = Zscore_p[cand]                           # [B, Dmax, ds]
    p = _l2t(pred_score_blk)                       # [B, ds]
    s = torch.einsum("bd,bkd->bk", p, Zc)         # [B, Dmax]
    s = s.masked_fill(~mask, float("-inf"))
    cset_size = mask.sum(dim=1)                    # [B]
    return s, cand, mask, cset_size


# ---------------------------------------------------------------------------
# Chain retrieval per arm. All arms paired on identical chains. Metric = TOP-1 COMMIT accuracy.
# For local_dg the SCORING happens in the DG sketch space (pred sketched, candidates = Zsk_p); the carried cue
# is always the real code Z[committed] (only scoring uses sketches). For global/raw_global scoring is over Z.
# ---------------------------------------------------------------------------

def run_arm(arm, Z, Zp, Zsk_p, sk_R, sk_m, roles_t, nbr_idx, nbr_mask, start, targets, role_ids,
            device, chunk, n_nodes):
    """Returns reach[d] (top-1 commit acc), hit10[d] (secondary), per-chain top-1-commit signature (arms-differ),
    mean local candidate-set size (local arms only)."""
    _enc_key, mode = ARM_SPEC[arm]
    L = len(targets)
    C = start.shape[0]
    is_local = mode in ("local", "local_dg")
    is_dg = (mode == "local_dg")
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
            pred_score = _sketch(pred, sk_R, sk_m) if is_dg else pred     # sketch the query for dg re-separation
            Zscore_p = Zsk_p if is_dg else Zp
            for b0 in range(0, C, chunk):
                b1 = min(C, b0 + chunk)
                s, cand, mask, csz = _local_scores(pred_score[b0:b1], cur[b0:b1], Zscore_p, nbr_idx, nbr_mask)
                nonempty = mask.any(dim=1)                            # [b]
                loc_arg = s.argmax(dim=1)                             # [b] local index
                b_ids = torch.arange(b1 - b0, device=device)
                picked = cand[b_ids, loc_arg]                         # [b] node id of local argmax
                committed[b0:b1] = torch.where(nonempty, picked,
                                               torch.full_like(picked, n_nodes))
                kk = min(HIT_K, s.shape[1])
                topk = s.topk(kk, dim=1).indices                     # [b, kk] local indices
                topk_ids = torch.gather(cand, 1, topk)               # [b, kk] node ids
                hitk[b0:b1] = (topk_ids == tgt[b0:b1, None]).any(dim=1) & nonempty
                cset_sizes.append(csz.detach().to("cpu"))
            carry_ids = committed
        elif mode == "global":
            score = _l2t(pred) @ Z.t()                               # [C, n] global
            committed = score.argmax(dim=1)                          # top-1 global commit
            topk = score.topk(min(HIT_K, score.shape[1]), dim=1).indices
            hitk = (topk == tgt[:, None]).any(dim=1)
            carry_ids = committed
        elif mode == "raw_global":
            # handled by run_no_cleanup for correct raw-accumulation carry; run_arm only used for cleanup arms
            raise ValueError("raw_global handled by run_no_cleanup, not run_arm")
        else:
            raise ValueError("unknown mode %r for arm %r" % (mode, arm))

        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cur = carry_ids                                              # advance to committed node for next hop

    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    mean_cset = float(torch.cat(cset_sizes).float().mean().item()) if cset_sizes else float("nan")
    return reach, hit10, sig, mean_cset


def run_no_cleanup(Z, roles_t, start, targets, role_ids, device, n_nodes):
    """Explicit raw-accumulation control: cue starts at the true start code, each hop cue <- bind(role, cue) with
    NO snap; readout top-1 global argmax. Crosstalk compounds -> collapse at reach>=2 (anti-saturation)."""
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
# LOCAL hop-2 semantic-floor / aliasing decomposition PER ARM. Condition on hop-1 CORRECT (use the true
# midpoint), do the LOCAL cleanup for hop-2 with this arm's codes/scoring, and among the errors measure the
# fraction whose wrongly-picked neighbor is a SAME-RELATION sibling of the true edge. base_rate is graph-
# structural (arm-invariant); excess = aliasing_frac - base_rate is the CODE-induced confusability beyond chance.
# ---------------------------------------------------------------------------

def local_error_decomposition(arm, Z, Zp, Zsk_p, sk_R, sk_m, roles_t, nbr_idx, nbr_rel, nbr_mask,
                              start, targets, role_ids, device, n_nodes):
    if len(targets) < 2:
        return dict(n_hop2=0, n_err=0, n_alias=0, local_aliasing_frac=float("nan"),
                    same_rel_base_rate=float("nan"), aliasing_excess_over_base=float("nan"))
    _enc_key, mode = ARM_SPEC[arm]
    is_dg = (mode == "local_dg")
    C = start.shape[0]
    mid = torch.from_numpy(targets[0]).to(device)               # TRUE hop-1 midpoint (condition hop-1 correct)
    role2 = roles_t[torch.from_numpy(role_ids[1]).to(device)]
    true_r2 = torch.from_numpy(role_ids[1]).to(device)          # true relation of hop-2
    pred2 = _hrr_bind_t(role2, Z[mid])
    pred_score = _sketch(pred2, sk_R, sk_m) if is_dg else pred2
    Zscore_p = Zsk_p if is_dg else Zp
    tgt2 = torch.from_numpy(targets[1]).to(device)
    picked = torch.full((C,), n_nodes, dtype=torch.long, device=device)
    picked_rel = torch.full((C,), -1, dtype=torch.long, device=device)
    for b0 in range(0, C, 256):
        b1 = min(C, b0 + 256)
        s, cand, mask, _csz = _local_scores(pred_score[b0:b1], mid[b0:b1], Zscore_p, nbr_idx, nbr_mask)
        nonempty = mask.any(dim=1)
        la = s.argmax(dim=1)
        b_ids = torch.arange(b1 - b0, device=device)
        pid = cand[b_ids, la]
        prel = nbr_rel[mid[b0:b1]][b_ids, la]
        picked[b0:b1] = torch.where(nonempty, pid, torch.full_like(pid, n_nodes))
        picked_rel[b0:b1] = torch.where(nonempty, prel, torch.full_like(prel, -1))
    err = (picked != tgt2)
    alias = err & (picked_rel == true_r2)                       # wrong pick shares the SAME relation
    n_err = int(err.sum().item())
    n_alias = int(alias.sum().item())
    frac = (n_alias / n_err) if n_err > 0 else float("nan")
    same_rel_ct = ((nbr_rel[mid] == true_r2[:, None]) & nbr_mask[mid]).sum(dim=1).float()
    cand_ct = nbr_mask[mid].sum(dim=1).float().clamp(min=1.0)
    base_rate = float((same_rel_ct / cand_ct).mean().item())
    excess = (frac - base_rate) if (frac == frac) else float("nan")
    return dict(n_hop2=int(C), n_err=n_err, n_alias=n_alias, local_aliasing_frac=float(frac),
                same_rel_base_rate=base_rate, aliasing_excess_over_base=float(excess))


# ---------------------------------------------------------------------------
# D_f/N recompute diagnostic (continuity with v2)
# ---------------------------------------------------------------------------

def df_recompute(n_nodes, mean_out_deg, mean_cset, dim):
    g_df = float(n_nodes)
    l_df1 = float(mean_out_deg)
    return dict(
        global_D_f=g_df, global_dim_needed=g_df / RESONATOR_THRESH,
        local_D_f_1hop=l_df1, local_dim_needed_1hop=l_df1 / RESONATOR_THRESH,
        mean_out_degree=float(mean_out_deg), mean_local_cset_size=float(mean_cset),
        dim=int(dim), local_load_per_hop=float(mean_out_deg) / float(dim),
        collapse_factor=(g_df / l_df1) if l_df1 > 0 else float("nan"),
        resonator_thresh=RESONATOR_THRESH,
    )


# ---------------------------------------------------------------------------
# Per-model-seed run: 3 encoders (sem / partial / id) on identical features-per-key, then 6 arms on identical
# chains + roles + graph. All arms paired.
# ---------------------------------------------------------------------------

def _feat_orthogonality(X):
    """Mean |cos| off-diagonal over a random 200-node subsample (lower = more orthogonal)."""
    n = X.shape[0]
    s = min(200, n)
    idx = np.random.default_rng(3).choice(n, size=s, replace=False)
    sub = X[idx]
    sub = sub / (np.linalg.norm(sub, axis=1, keepdims=True) + 1e-8)
    cc = np.abs(sub @ sub.T)
    off = cc - np.diag(np.diag(cc))
    return float(off.sum() / (s * (s - 1)))


def run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask, mean_out_deg,
             cfg, device, out_dir=None):
    n_nodes = len(node_words)
    d = cfg["code_dim"]
    dg = cfg["dg_dim"]
    sk_m = max(1, int(round(cfg["dg_active_frac"] * dg)))

    # 3 encoders (one per unique feature set). Semantic serves NO_CLEANUP + GLOBAL + LOCAL_SEMANTIC.
    Zs = {}
    enc_digs = {}
    feat_ortho = {}
    for key in ("sem", "partial", "id"):
        X = build_features(node_words, cfg, seed, key)
        feat_ortho[key] = _feat_orthogonality(X)
        Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir,
                                      tag="BIND_%s" % key)
        Zs[key] = Z
        enc_digs[key] = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
        _log("  seed=%d encoder=%s feat_ortho=%.4f enc_dig=%s" % (seed, key, feat_ortho[key], enc_digs[key][:12]))

    # padded codes + DG sketches per encoder (sketch space for local_dg)
    g = torch.Generator(device="cpu").manual_seed(seed + 4242)
    sk_R = (torch.randn(d, dg, generator=g) / np.sqrt(d)).to(device)     # [d, dg] fixed random expansion
    Zp = {k: torch.cat([Zs[k], torch.zeros(1, d, device=device)], dim=0) for k in Zs}
    Zsk = {k: _sketch(Zs[k], sk_R, sk_m) for k in Zs}
    Zsk_p = {k: torch.cat([Zsk[k], torch.zeros(1, dg, device=device)], dim=0) for k in Zs}

    chain_rng = np.random.default_rng(seed + 909)
    start, targets, role_ids = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, chain_rng)
    n_chains_got = int(start.shape[0])
    chunk = cfg["chain_chunk"]

    arms = {}
    sigs = {}
    err_decomp = {}
    mean_cset = float("nan")
    for arm in ARMS:
        enc_key, mode = ARM_SPEC[arm]
        Z = Zs[enc_key]
        if mode == "raw_global":
            reach, hit10, sig = run_no_cleanup(Z, roles_t, start, targets, role_ids, device, n_nodes)
            mcs = float("nan")
        else:
            reach, hit10, sig, mcs = run_arm(arm, Z, Zp[enc_key], Zsk_p[enc_key], sk_R, sk_m, roles_t,
                                             nbr_idx, nbr_mask, start, targets, role_ids, device, chunk, n_nodes)
            if arm == LOCAL_SEMANTIC and mcs == mcs:
                mean_cset = mcs
        arms[arm] = dict(reach=reach, hit10=hit10, mean_cset=mcs, encoder=enc_key, mode=mode,
                         alpha_id=ALPHA_ID[enc_key])
        sigs[arm] = sig
        if arm in LOCAL_ARMS:
            err_decomp[arm] = local_error_decomposition(
                arm, Z, Zp[enc_key], Zsk_p[enc_key], sk_R, sk_m, roles_t, nbr_idx, nbr_rel, nbr_mask,
                start, targets, role_ids, device, n_nodes)
        _log("  seed=%d %-19s reach@[1..%d]=%s hit10@2=%.3f cset=%.2f alias_excess=%s" % (
            seed, arm, MAX_REACH, {dd: round(reach[dd], 3) for dd in range(1, MAX_REACH + 1)},
            hit10[2], mcs if mcs == mcs else -1.0,
            _fmt(err_decomp[arm]["aliasing_excess_over_base"]) if arm in err_decomp else "n/a"))

    df = df_recompute(n_nodes, mean_out_deg, mean_cset, d)

    if len(set(sigs.values())) < 2:
        _log("  [warn] seed=%d arm commit-signatures collapsed to <2 distinct" % seed)

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digests=enc_digs, feat_ortho=feat_ortho,
                n_chains=n_chains_got, code_dim=d, mean_local_cset=mean_cset,
                error_decomp=err_decomp, df_recompute=df)


# ---------------------------------------------------------------------------
# Aggregate + WIN verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _excess(per_seed, arm):
    return _nanmean([m["error_decomp"][arm]["aliasing_excess_over_base"]
                     for m in per_seed if arm in m["error_decomp"]])


def _alias_frac(per_seed, arm):
    return _nanmean([m["error_decomp"][arm]["local_aliasing_frac"]
                     for m in per_seed if arm in m["error_decomp"]])


def aggregate_and_verdict(per_seed, subgraph_meta, cfg):
    reach = {a: {d: _nanmean([m["arms"][a]["reach"][d] for m in per_seed]) for d in range(1, MAX_REACH + 1)}
             for a in ARMS}
    hit10 = {a: {d: _nanmean([m["arms"][a]["hit10"][d] for m in per_seed]) for d in range(1, MAX_REACH + 1)}
             for a in ARMS}

    base1 = reach[NO_CLEANUP][1]
    base2 = reach[NO_CLEANUP][2]
    glob1 = reach[GLOBAL_SEMANTIC][1]
    loc_sem1 = reach[LOCAL_SEMANTIC][1]

    hop1_present = (glob1 == glob1) and (glob1 >= HOP1_PRESENT)
    baseline_in_band = (loc_sem1 == loc_sem1) and (loc_sem1 < BASE_IN_BAND_HI) and (loc_sem1 > 0.05)
    baseline_collapses = (base2 == base2 and base1 == base1
                          and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))

    # aliasing excess per LOCAL arm (mean over seeds) + base rate (graph-structural, arm-invariant)
    excess = {a: _excess(per_seed, a) for a in LOCAL_ARMS}
    alias_frac = {a: _alias_frac(per_seed, a) for a in LOCAL_ARMS}
    base_rate = _nanmean([m["error_decomp"][LOCAL_SEMANTIC]["same_rel_base_rate"]
                          for m in per_seed if LOCAL_SEMANTIC in m["error_decomp"]])

    ex_sem = excess[LOCAL_SEMANTIC]
    ex_dec = excess[LOCAL_DECOUPLED]
    ex_dg = excess[LOCAL_DECOUPLED_DG]
    # best (largest) aliasing-excess DROP achieved by any WIN arm vs the semantic baseline
    drops = {a: (ex_sem - excess[a]) if (ex_sem == ex_sem and excess[a] == excess[a]) else float("nan")
             for a in WIN_ARMS}
    best_drop = max([drops[a] for a in WIN_ARMS if drops[a] == drops[a]], default=float("nan"))
    aliasing_reduced = bool(best_drop == best_drop and best_drop >= ALIAS_DROP_MIN)

    # dose-response monotonicity: excess(SEMANTIC 0.0) >= excess(PARTIAL 0.5) >= excess(DECOUPLED 1.0)
    dose_excess = [excess[LOCAL_SEMANTIC], excess[LOCAL_PARTIAL], excess[LOCAL_DECOUPLED]]
    dose_monotone = bool(all(dose_excess[i] == dose_excess[i] for i in range(3))
                         and dose_excess[0] >= dose_excess[1] - 1e-6
                         and dose_excess[1] >= dose_excess[2] - 1e-6)

    # WIN evaluation per WIN arm: reach2>=WIN_REACH2 AND reach3>=WIN_REACH3 AND that arm's aliasing dropped
    win_eval = {}
    for a in WIN_ARMS:
        r2 = reach[a][2]
        r3 = reach[a][3]
        dr = drops[a]
        alias_ok = bool(dr == dr and dr >= ALIAS_DROP_MIN)
        win = bool(r2 == r2 and r2 >= WIN_REACH2 and r3 == r3 and r3 >= WIN_REACH3 and alias_ok)
        win_eval[a] = dict(reach1=reach[a][1], reach2=r2, reach3=r3, alias_drop=dr, alias_ok=alias_ok, win=win)

    win_arms_pass = [a for a in WIN_ARMS if win_eval[a]["win"]]
    best_win = max(WIN_ARMS, key=lambda a: (win_eval[a]["reach2"] if win_eval[a]["reach2"] == win_eval[a]["reach2"]
                                            else -1e9))
    best_win_r2 = win_eval[best_win]["reach2"]

    # local lift over the semantic baseline (attribution: same dim/scoping, only the codes differ)
    local_lift2 = (reach[LOCAL_DECOUPLED][2] - reach[LOCAL_SEMANTIC][2]
                   if reach[LOCAL_DECOUPLED][2] == reach[LOCAL_DECOUPLED][2] else float("nan"))

    identity_not_lever = bool((not aliasing_reduced)
                              and best_win_r2 == best_win_r2 and best_win_r2 < FAIL_REACH2)

    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif len(win_arms_pass) > 0:
        verdict = "HARD_PASS_DECOUPLED_WIN"
    elif identity_not_lever:
        verdict = "HARD_FAIL_IDENTITY_NOT_LEVER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL"

    df = per_seed[0]["df_recompute"]

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f(hop1=%s) @2=%.3f(collapses=%s) || GLOBAL_SEM @1=%.3f @2=%.3f || "
        "LOCAL_SEM @1=%.3f(in_band=%s) @2=%.3f @3=%.3f ex=%s | LOCAL_PARTIAL @2=%.3f ex=%s | "
        "LOCAL_DECOUPLED @1=%.3f @2=%.3f @3=%.3f ex=%s drop=%s win=%s | "
        "LOCAL_DECOUPLED_DG @2=%.3f @3=%.3f ex=%s drop=%s win=%s || "
        "base_rate=%s aliasing_reduced(>=%.2f)=%s best_drop=%s dose_monotone=%s || "
        "best_win=%s best_win_r2=%.3f local_lift2(vs LOCAL_SEM)=%s win_arms=%s || "
        "df: global_dim_needed=%.0f local_dim_needed_1hop=%.1f collapse=%.0fx mean_cset=%.2f mean_out_deg=%.2f "
        "dim=%d local_load/hop=%.4f (thr=%.3f) || WIN bands: R2>=%.2f R3>=%.2f ALIAS_DROP>=%.2f (dim=%d MODEST) || "
        "n=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, hop1_present, base2, baseline_collapses, glob1, reach[GLOBAL_SEMANTIC][2],
            loc_sem1, baseline_in_band, reach[LOCAL_SEMANTIC][2], reach[LOCAL_SEMANTIC][3], _fmt(ex_sem),
            reach[LOCAL_PARTIAL][2], _fmt(excess[LOCAL_PARTIAL]),
            reach[LOCAL_DECOUPLED][1], reach[LOCAL_DECOUPLED][2], reach[LOCAL_DECOUPLED][3], _fmt(ex_dec),
            _fmt(drops[LOCAL_DECOUPLED]), win_eval[LOCAL_DECOUPLED]["win"],
            reach[LOCAL_DECOUPLED_DG][2], reach[LOCAL_DECOUPLED_DG][3], _fmt(ex_dg),
            _fmt(drops[LOCAL_DECOUPLED_DG]), win_eval[LOCAL_DECOUPLED_DG]["win"],
            _fmt(base_rate), ALIAS_DROP_MIN, aliasing_reduced, _fmt(best_drop), dose_monotone,
            best_win, best_win_r2, _fmt(local_lift2), win_arms_pass,
            df["global_dim_needed"], df["local_dim_needed_1hop"], df["collapse_factor"],
            df["mean_local_cset_size"], df["mean_out_degree"], df["dim"], df["local_load_per_hop"],
            RESONATOR_THRESH, WIN_REACH2, WIN_REACH3, ALIAS_DROP_MIN, cfg["code_dim"],
            subgraph_meta["n_nodes"], subgraph_meta["n_edges"], subgraph_meta.get("n_relation_types", -1),
            len(per_seed), "full" if len(cfg["seeds"]) == 3 else "smoke"))

    gates = dict(
        verdict=verdict, reach_mean=reach, hit10_mean=hit10,
        base_reach1=base1, base_reach2=base2, global_reach1=glob1, local_sem_reach1=loc_sem1,
        hop1_present=bool(hop1_present), baseline_in_band=bool(baseline_in_band),
        baseline_collapses=bool(baseline_collapses),
        aliasing_excess=excess, aliasing_frac=alias_frac, same_rel_base_rate=base_rate,
        aliasing_drops=drops, best_alias_drop=best_drop, aliasing_reduced=bool(aliasing_reduced),
        dose_excess=dict(sem=dose_excess[0], partial=dose_excess[1], decoupled=dose_excess[2]),
        dose_monotone=bool(dose_monotone),
        win_eval=win_eval, win_arms_pass=win_arms_pass, best_win=best_win, best_win_reach2=best_win_r2,
        local_lift2_vs_semantic=local_lift2, identity_not_lever=bool(identity_not_lever),
        df_recompute=df,
        bands=dict(HOP1_PRESENT=HOP1_PRESENT, BASE_IN_BAND_HI=BASE_IN_BAND_HI,
                   BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, BASE_COLLAPSE_FRAC=BASE_COLLAPSE_FRAC,
                   WIN_REACH2=WIN_REACH2, WIN_REACH3=WIN_REACH3, ALIAS_DROP_MIN=ALIAS_DROP_MIN,
                   FAIL_REACH2=FAIL_REACH2, HIT_K=HIT_K, MAX_REACH=MAX_REACH),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (ALWAYS runs, CPU). PLANTED separable codes + real local graph (the v2
# CLEAN-CODE POSITIVE CONTROL: LOCAL cleanup -> 1.0 -> the CEILING). Proves: (0) chain machinery works (hop-1
# high); (1) must-fail NO_CLEANUP collapses at reach>=2; (2) LOCAL cleanup beats GLOBAL at reach-2; (3) arms
# differ; (4) DG re-separation runs (local_dg path exercised); (5) identity features are MORE orthogonal than
# char-trigram features (the decoupling premise) on the real word list.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    rng = np.random.default_rng(0)
    d = 96
    dg = 512
    sk_m = max(1, int(round(0.05 * dg)))
    T = 4
    n = 3000
    roles_b = torch.from_numpy(make_unitary_roles(T, d, np.random.default_rng(11))).to(device)

    n_clusters = 40
    per = n // n_clusters
    base = rng.standard_normal((n_clusters, d)).astype(np.float32)
    base_u = base / (np.linalg.norm(base, axis=1, keepdims=True) + 1e-8)
    base_ut = torch.from_numpy(base_u.astype(np.float32)).to(device)
    dir_adj_planted = [[] for _ in range(n)]
    dir_adj_full = [[] for _ in range(n)]
    order = rng.permutation(n)
    Z2 = torch.zeros(n, d, device=device)
    u0 = int(order[0])
    Z2[u0] = _l2t((base_ut[u0 // per] + 0.20 * torch.randn(d))[None, :])[0]
    for k in range(1, n):
        u = int(order[k - 1]); v = int(order[k]); r = int(rng.integers(0, T))
        pred = _l2t(_hrr_bind_t(roles_b[r:r + 1], _l2t(Z2[u:u + 1])))[0]
        nz = _l2t(torch.randn(1, d))[0]
        Z2[v] = _l2t((pred + 0.30 * base_ut[v // per] + 1.95 * nz)[None, :])[0]
        dir_adj_planted[u].append((v, r))
        dir_adj_full[u].append((v, r))
    for u in range(n):
        for _ in range(int(rng.integers(2, 6))):
            w = int(rng.integers(0, n))
            if w != u:
                dir_adj_full[u].append((w, int(rng.integers(0, T))))
    Z = _l2t(Z2)
    Zp = torch.cat([Z, torch.zeros(1, d, device=device)], dim=0)
    sk_R = (torch.randn(d, dg) / np.sqrt(d)).to(device)
    Zsk = _sketch(Z, sk_R, sk_m)
    Zsk_p = torch.cat([Zsk, torch.zeros(1, dg, device=device)], dim=0)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj_full, n, device)

    start, targets, role_ids = sample_chains(dir_adj_planted, 200, MAX_REACH, np.random.default_rng(1))

    reach = {}
    sigs = {}
    r_no, _h, s_no = run_no_cleanup(Z, roles_b, start, targets, role_ids, device, n)
    reach[NO_CLEANUP] = r_no; sigs[NO_CLEANUP] = s_no
    # exercise global + local + local_dg scoring paths (planted separable codes -> LOCAL ~ 1.0 = the CEILING)
    for arm in [GLOBAL_SEMANTIC, LOCAL_SEMANTIC, LOCAL_DECOUPLED_DG]:
        r, _hh, s, _mcs = run_arm(arm, Z, Zp, Zsk_p, sk_R, sk_m, roles_b, nbr_idx, nbr_mask,
                                  start, targets, role_ids, device, 256, n)
        reach[arm] = r; sigs[arm] = s

    hop1_high = bool(reach[NO_CLEANUP][1] >= 0.40)
    baseline_fails = bool(reach[NO_CLEANUP][MAX_REACH] <= 0.60 * max(reach[NO_CLEANUP][1], 1e-9))
    local_beats_global2 = bool(reach[LOCAL_SEMANTIC][2] >= reach[GLOBAL_SEMANTIC][2] + 0.05)
    local_ceiling_high = bool(reach[LOCAL_SEMANTIC][2] >= 0.80)   # CLEAN-CODE POSITIVE CONTROL: LOCAL ~ ceiling
    dg_path_runs = bool(reach[LOCAL_DECOUPLED_DG][1] >= 0.40)     # DG re-separation scoring path exercised
    arms_differ = bool(len(set(sigs.values())) >= 2)

    # decoupling premise: identity features MORE orthogonal than char-trigram features on the real word list
    words = ["node_%d_%s" % (i, ["cat", "dog", "run", "blue", "tree"][i % 5]) for i in range(300)]
    X_sem = char_trigram_features(words, 1024)
    X_id = identity_features(len(words), 1024, 0)
    ortho_sem = _feat_orthogonality(X_sem)
    ortho_id = _feat_orthogonality(X_id)
    identity_more_orthogonal = bool(ortho_id < ortho_sem)

    res = dict(
        reach_no_cleanup={dd: round(reach[NO_CLEANUP][dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_global={dd: round(reach[GLOBAL_SEMANTIC][dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_local_ceiling={dd: round(reach[LOCAL_SEMANTIC][dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_local_dg={dd: round(reach[LOCAL_DECOUPLED_DG][dd], 4) for dd in range(1, MAX_REACH + 1)},
        hop1_high=hop1_high, baseline_fails=baseline_fails, local_beats_global2=local_beats_global2,
        local_ceiling_high=local_ceiling_high, dg_path_runs=dg_path_runs, arms_differ=arms_differ,
        ortho_sem=ortho_sem, ortho_id=ortho_id, identity_more_orthogonal=identity_more_orthogonal,
        Dmax=int(Dmax), mean_out_deg=round(mean_out_deg, 3),
    )
    ok = bool(hop1_high and baseline_fails and local_beats_global2 and local_ceiling_high
              and dg_path_runs and arms_differ and identity_more_orthogonal)
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
            verdict_msg="MECHANISM_SELFTEST_FAILED (hop1/baseline/local_beats_global/ceiling/dg/arms/ortho): %s"
                        % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    dir_adj = build_typed_diradj(edges, rels, n_nodes)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj, n_nodes, device)
    _log("nbr table: Dmax=%d mean_out_deg=%.3f" % (Dmax, mean_out_deg))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS decoupled-identity machinery: NO_CLEANUP collapses at reach>=2, LOCAL "
                        "cleanup beats GLOBAL + hits the CLEAN-CODE ceiling (~1.0), DG re-separation path runs, "
                        "arms differ, identity features more orthogonal than char-trigram; typed subgraph + nbr "
                        "table exercised",
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
            pm = run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask,
                          mean_out_deg, cfg, device, out_dir=out_dir_path)
            for a in ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1) if dd not in pm["arms"][a]["reach"]]
                if a not in pm["arms"] or missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # WIN arms must differ from LOCAL_SEMANTIC and NO_CLEANUP (META_RULE_AF, scoped)
            for a in WIN_ARMS:
                if pm["arm_sigs"][a] == pm["arm_sigs"][NO_CLEANUP]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s == NO_CLEANUP" % (seed, a))
                if pm["arm_sigs"][a] == pm["arm_sigs"][LOCAL_SEMANTIC]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s == LOCAL_SEMANTIC" % (seed, a))
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
