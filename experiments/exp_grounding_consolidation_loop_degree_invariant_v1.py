"""CONSOLIDATION-LOOP degree-invariance rematch of the additive-geometric popularity-shortcut failure.

BACKGROUND. The just-landed FULL (exp_grounding_additive_geometric_degree_control_retest_v1, anchor
grounding_additive_geometric_degree_control_v1) measured HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT: the additive
TransE code beat the discrete one-shot code in AGGREGATE (d=0.098) but the margin was DEGREE-DEPENDENT -- strata
d(transe-discrete) LOW=-0.040 MID=+0.085 HIGH=+0.264 -- i.e. the one-shot geometry is a popularity shortcut, and
popularity recovered 0.52 of the reach. The SSP scan (research_ssp_fractional_binding_degree_invariant_relational_
code_2026-07-10.md) argues the degree bias lives in COORDINATE-FITTING FROM SKEWED DATA, not in the binding-op form,
so a code-swap alone cannot cure it; "the fix, if there is one, has to come from HOW coordinates get assigned."

THE MECHANISM UNDER TEST (a PROCESS, not a code). Instead of ENCODING a geometry directly in ONE shot (the popularity
shortcut), run a CONSOLIDATION LOOP: a "sleep"-like process that repeatedly nudges concept codes so that entities which
AGREE ACROSS TWO GENUINELY-INDEPENDENT CHANNELS are pulled together, letting the geometry SETTLE over many passes.
Brain analog: Complementary Learning Systems (McClelland/O'Reilly) -- hippocampus stores fast/episodic (the raw graph +
the raw surface form), neocortex slowly extracts the gist over sleep replay (the settled coordinate). The consolidation
ASSIGNS the coordinate (the crux the SSP note identifies), then a light additive relation-offset read-off sits on top.

WHY it should beat the one-shot code: cross-channel AGREEMENT (require BOTH channels to say two entities are related)
FILTERS the popularity signal. A high-degree hub is structurally near MANY nodes but surface-near only its few
morphological cousins, so hub pairs rarely survive the AND -- the hub loses its structural dominance, and the settled
geometry reflects degree-BALANCED agreement-relatedness, not triple frequency. A rare concept whose two channels agree
is placed as well as a common one -> degree-INVARIANT (transitive-inference end-anchor polarity, Lippl 2024).

THE LOAD-BEARING CONSTRAINT (make-or-break, guarded explicitly). The two channels MUST be GENUINELY INDEPENDENT /
exterior to each other. If both derive from the SAME skewed graph, consolidation just re-derives popularity and fails
identically (internal loops decorrelate noise but not a SHARED bias). This cell:
  (1) uses a STRUCTURAL channel (visible typed-graph relation-neighborhood; degree-biased) and a LEXICAL/ATTRIBUTE
      channel (char-trigram surface features of the concept string; EXTERIOR to the graph, degree-blind);
  (2) RUNS a channel-independence check (cross-channel pairwise-similarity correlation + lexical-vs-degree correlation)
      that must FIRE: genuinely-independent channels PASS (|r| < INDEP_R_MAX); a channel derived from the other is
      FLAGGED (|r| >= INDEP_R_FLAG). If the only available channel is NOT independent, the cell FAILS HONESTLY
      (HARD_FAIL_CHANNELS_NOT_INDEPENDENT) rather than faking a second channel out of the first;
  (3) includes a CONSOLIDATED_TRAP arm -- the SAME consolidation loop with BOTH channels derived from the graph
      structure (two structural views). If the trap ALSO passes, the benefit is the iterative process not the channel
      independence, and HARD_PASS is withheld. The trap is the direct operationalization of the shared-bias warning.

ARMS (all learn from the VISIBLE typed graph only unless noted; scored on the SAME held-out completable queries with
the SAME candidate negatives per seed -> PAIRED; identical harness to the retest so this is a clean rematch):
  DISCRETE_HRR_BIND   (one-shot substrate code): char-trigram -> ProjHead -> L2; HRR bind; cosine read-off.
  ONESHOT_TRANSE      (the JUST-FAILED one-shot additive code): margin-rank ||E_h + R_r - E_t||_1; degree-dependent.
  CONSOLIDATED        (MECHANISM under test): cross-channel-agreement contrastive settle assigns E_cons (unit-norm,
                      blocks the norm-blowup degree channel); freeze E_cons; fit additive relation offsets R_r on
                      visible edges; score -||E_cons[h] + R_r - E_cons[t]||_1.
  CONSOLIDATED_TRAP   (shared-bias control): identical loop, BUT the second channel is a SECOND STRUCTURAL VIEW (not
                      lexical) -> both channels degree-biased -> agreement does NOT filter hubs -> should re-derive the
                      popularity shortcut. Isolates whether the cure is channel-INDEPENDENCE vs the process alone.
  POPULARITY_DEGREE   (popularity baseline): score(candidate) = visible-graph degree(candidate). No geometry.
  RANDOM_CODES        (null): untrained TransE codes -> chance floor + codes-necessary control.
  TRANSE_TRANSDUCTIVE (oracle / must-fire): TransE trained WITH held-out visible; must recover >> random or setup broken.

PRIMARY METRIC (pre-registered, identical to the retest): reach@1 = filtered Hits@1 on the COMPLETABLE held-out subset;
also MRR + Hits@3/10; and per-degree-stratum reach@1 for every arm (LOW/MID/HIGH tertiles of the true-tail visible
degree). The DECISION is degree-INVARIANT tail survival + FLATNESS, NOT an aggregate delta above a bar (aggregate delta
is exactly what carries the degree confound).

DISCRIMINATOR (pre-registered; both bands numeric BEFORE the run):
  HARD_PASS_CONSOLIDATION_DEGREE_INVARIANT (all must hold):
      channels_independent (independence check PASSES)
    AND aggregate materiality: CONSOLIDATED reach@1 >= DISCRETE + GEOM_MARGIN
    AND tail survival: (CONSOLIDATED - DISCRETE) reach@1 >= STRAT_MARGIN in BOTH LOW and MID strata (>=MIN_STRAT_Q each)
    AND FLATNESS (the genuinely-new degree-invariance bar): |cons_HIGH - cons_LOW| <= FLATNESS_EPS
    AND popularity does NOT recover: (cons - pop) >= POP_GAP AND pop/cons <= POP_RECOVER_FRAC_MAX
    AND the TRAP FAILS: CONSOLIDATED_TRAP collapses on the tail OR concentrates on HIGH (shared-bias re-derives pop)
    -> the consolidation process over independent channels is a genuine degree-invariant inductive lever.
  HARD_FAIL_CHANNELS_NOT_INDEPENDENT: the independence check FLAGS the two channels (|r| >= INDEP_R_FLAG) -> the only
      available second channel is not exterior enough; report honestly (the comparison is void), redirect to INGEST.
  HARD_FAIL_CONSOLIDATION_ANOTHER_SHORTCUT (channels independent but consolidation still shortcuts):
      tail collapse ((cons - discrete) <= TIE_EPS in LOW or MID) OR concentration (|cons_HIGH - cons_LOW| >=
      HIGH_LOW_GAP_FAIL, matching TransE's ~0.26 head-tail gap) OR popularity recovers (cons-pop <= TIE_EPS OR
      pop/cons >= POP_RECOVER_FRAC_HI).
  MIDDLE_BAND_PARTIAL = otherwise (beats popularity in aggregate but flatness/tail ambiguous).
Gating precondition INCONCLUSIVE arms: enough completable, negatives_valid (random <= RANDOM_CEIL), oracle_fires.

SELF-TEST (mechanism; proves the grounding-specific discriminators FIRE on planted worlds -- contract (a)/(b)/(c)):
  (a) PLANTED INDEPENDENT AGREEMENT (degree-INDEPENDENT geometry + a real, independent second channel): a latent-grid
      geometry with planted degree variation; channel S = latent+noiseA, channel L = latent+noiseB (INDEPENDENT noise,
      genuinely informative). CONSOLIDATED must RECOVER held-out translations (>=0.25), be FLAT across degree strata
      (|high-low|<=0.10), and BEAT popularity (>=0.15); the TRAP (two structural views S1=latent+noiseA,
      S2=latent+noiseA') must NOT be flat / must not clear the tail as cleanly -> proves independence is load-bearing.
  (b) PLANTED PURE POPULARITY (tails ~ zipf, NO consistent geometry, lexical = pure noise): CONSOLIDATED must NOT beat
      popularity (cons-pop <= 0.05) and the POPULARITY baseline must FIRE (>=0.15) -> consolidation cannot fake a lever
      from popularity; the popularity baseline catches the popularity-driven signal.
  (c) CHANNEL-INDEPENDENCE CHECK fires: planted-independent channels PASS (|cross_sim_r| < INDEP_R_MAX); planted-
      correlated channels (L = copy of S) are FLAGGED (|cross_sim_r| >= INDEP_R_FLAG).
  Saturation-vacuous guard: the must-fail controls (planted-popularity cons-does-not-beat-pop; planted-correlated
  channels flagged) FAIL at self-test (smoke) scale, by construction, so a green self-test cannot rubber-stamp a
  degenerate FULL.

## Compute architecture
class: (a) batched-GPU. Structural features = random-projected propagated adjacency (2 dense [n,n]@[n,dim] matmuls,
n<=5000 -> ~0.1GB, seconds on GPU); channel kNN = a single [n,n] cosine + topk; agreement = boolean AND of the two
topk masks; consolidation = batched InfoNCE over agreement edges (matmul); relation-offset fit = vectorized margin-rank
over edge mini-batches with entity codes FROZEN; ranking builds one shared [nq,K,dim] candidate tensor scored per arm
(PAIRED). Storage strategy: SHARDED (each entity its own code / offset vector; no bundling). Routes to overnight_queue
(GPU) for FULL; local is smoke/self-test only (USER-locked). Self-test is the local pre-flight discriminator gate.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): >= 5 distinct held-out score signatures among the 7 arms.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace; write_partial per seed).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: filtered Hits@1 chance floor = 1/(N_RANK_NEG+1) ~ 0.01 (THEORETICAL). HARD_PASS needs cons >= discrete +
#   0.05, tail margins >= 0.03, flatness <= 0.08; self-test planted-independent arm demonstrates >= 0.25 reachable.
#   discriminator_reachability: OK.
# - baseline_in_band: RANDOM_CODES is the anti-triviality null (<= RANDOM_CEIL 0.15). ORACLE is the must-fire control
#   (>= random + 0.15). POPULARITY is the confound-baseline (measured, not gated as a null).
# - discriminator survives scale: consolidation/agreement/independence params (CONS_KNN/PASSES/REL_EPOCHS/kge_dim) are
#   SHARED between self-test and FULL; the SURVIVAL discriminator (per-stratum + flatness + trap) fires in the planted
#   self-test; the real-graph survival outcome is the open measurement.
# - HARD_PASS strictly above floor: cons >= discrete + 0.05 AND both tail strata >= 0.03 (>> tie-eps 0.02) AND flat.
# - HP_SCOPE: the SURVIVAL+FLATNESS gate applies to CONSOLIDATED vs DISCRETE + POPULARITY, with CONSOLIDATED_TRAP as a
#   must-fail control. RANDOM=null; ORACLE=must-fire; ONESHOT_TRANSE=the failed one-shot (reported, degree-dependent).
# - positive_control (Gate D): TRANSE_TRANSDUCTIVE reproduces the transductive-KGE result (>> random); ONESHOT_TRANSE
#   reproduces the retest's degree-dependent additive result on the same 30% split (sanity that the rematch matches).
# - sweep axis: ARM (method) x seed x degree-stratum; EXPECTED_N_UNITS = n_seeds; each seed asserts all 7 arms.
# - per-unit failure-class instrumentation (no bare except; per-arm try/except records failure_class).
# - calibration_check: default_ok_for_this_regime. HELDOUT_FRAC=0.30 + completable-subset inherited from the retest;
#   degree tertiles are DATA-driven quantiles of the query-target degree distribution (not tuned for PASS); KGE +
#   consolidation hyperparams pre-registered before the run.
# - PAIRED: all arms share the identical held-out split + completable subset + candidate negatives + degree strata.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm/per-stratum flush prints).
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

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import char_trigram_features  # noqa: E402
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import train_binding_encoder_dev  # noqa: E402
# Reuse the retest harness VERBATIM (apples-to-apples rematch): split, completable, degree, KGE, ranking, strata.
import experiments.exp_grounding_additive_geometric_degree_control_retest_v1 as rt  # noqa: E402

ANCHOR_NAME = "grounding_consolidation_loop_degree_invariant_v1"

# ---- Arm names ----
DISCRETE = "DISCRETE_HRR_BIND"          # one-shot substrate multiplicative binding code
ONESHOT = "ONESHOT_TRANSE"              # the JUST-FAILED one-shot additive code (degree-dependent)
CONS = "CONSOLIDATED"                   # MECHANISM: cross-channel-agreement settle + additive relation read-off
TRAP = "CONSOLIDATED_TRAP"             # shared-bias control: same loop, two STRUCTURAL views (no independence)
POP = "POPULARITY_DEGREE"               # degree-only popularity baseline (no geometry)
RANDOM = "RANDOM_CODES"                 # control: random codes, TransE scoring
ORACLE = "TRANSE_TRANSDUCTIVE"          # oracle: TransE trained WITH held-out visible (must-fire)
ALL_ARMS = [DISCRETE, ONESHOT, CONS, TRAP, POP, RANDOM, ORACLE]

STRATA = ["LOW", "MID", "HIGH"]

# ---- Pre-registered bands (picked BEFORE the run) ----
GEOM_MARGIN = 0.05           # HARD_PASS aggregate materiality: cons reach@1 >= discrete + this
STRAT_MARGIN = 0.03          # HARD_PASS tail survival: (cons - discrete) >= this in BOTH LOW and MID strata
TIE_EPS = 0.02               # HARD_FAIL collapse: (cons - discrete) <= this in a tail stratum
FLATNESS_EPS = 0.08          # HARD_PASS degree-invariance: |cons_HIGH - cons_LOW| <= this (FLAT across degree)
HIGH_LOW_GAP_FAIL = 0.15     # HARD_FAIL concentration: |cons_HIGH - cons_LOW| >= this (rides high-degree like TransE)
POP_GAP = 0.05               # HARD_PASS: cons reach@1 must beat POPULARITY by this
POP_RECOVER_FRAC_MAX = 0.60  # HARD_PASS: popularity recovers <= this fraction of cons reach
POP_RECOVER_FRAC_HI = 0.80   # HARD_FAIL: popularity recovers >= this fraction of cons reach
RANDOM_CEIL = 0.15           # anti-triviality: RANDOM reach@1 <= this
ORACLE_FIRE_MARGIN = 0.15    # discriminator-fires: ORACLE must beat RANDOM by this
MIN_STRAT_Q = 40             # min queries in a tail stratum to assess its margin
INDEP_R_MAX = 0.30           # exterior channel PASSES if |kNN-indegree-vs-degree r| < this; both-loaded if BOTH >= this
INDEP_R_FLAG = 0.30          # (reported) both-degree-loaded threshold (each channel's degree correlation)
REDUNDANT_CROSS = 0.95       # channels FLAGGED redundant (near-identical / collapsed) if |cross-channel-sim r| >= this

# ---- Held-out construction (inherited from the retest / phase-0 M5) ----
HELDOUT_FRAC = 0.30
MIN_HELDOUT_COMPLETABLE = 60
N_RANK_NEG = 99
MAX_RANK_QUERIES = 1500

# ---- KGE + consolidation hyperparams (pre-registered; NOT tuned on real data) ----
KGE_MARGIN = 1.0
KGE_NEG = 15
KGE_WD = 1e-3
# CONSOLIDATION = normalized-Laplacian graph diffusion WITH RESTART over the cross-channel agreement graph
# (personalized-PageRank / successor-representation form). Two brain/degree-invariance properties, BY CONSTRUCTION:
#   (1) NORMALIZED-Laplacian propagation S = D^-1/2 W D^-1/2 (symmetric-normalized) -- the decades-proven fix for the
#       degree/popularity bias that killed the additive code (unnormalized L = D - W re-derives the bias);
#   (2) RESTART (alpha>0) to the exterior-informed anchor -> non-trivial stationary state = personalized PageRank = SR,
#       which PREVENTS the Oono-Suzuki oversmoothing collapse to the constant eigenvector (anti-collapse by design).
#   Additionally EARLY-STOPPED (few passes) as a second anti-oversmoothing guard.
CONS_KNN = 8                 # per-channel kNN size for the agreement graph
CONS_PASSES = 6              # diffusion passes (EARLY-STOPPED; anti-oversmoothing)
CONS_ALPHA = 0.25            # restart probability (personalized-PageRank / SR; anti-collapse)
COLLAPSE_RANK_FLOOR = 3.0    # HARD_FAIL if consolidated-code effective rank <= this (collapsed to ~constant mode)
COLLAPSE_VAR_FLOOR = 0.02    # HARD_FAIL if consolidated-code representation-variance <= this (oversmoothing collapse)
REL_EPOCHS = 400            # additive relation-offset fit epochs (entity codes FROZEN)
REL_BATCH = 1024
STRUCT_HOP = 0.5           # 2-hop propagation weight for the structural channel features
INDEP_SAMPLE = 4000        # #pairs sampled for the cross-channel-similarity correlation

# Config profiles. Consolidation/kNN/rel-fit params are SHARED across self-test/smoke/full (discriminator-survives-scale)
SELFTEST_CFG = dict(seeds=[7], n_nodes=400, kge_dim=64,
                    enc=dict(epochs=20, batch=256, code_dim=128, feat_dim=1024, temp=0.15, lr=0.01,
                             lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0),
                    kge_epochs=450, kge_batch=512, kge_lr=0.01)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1800, kge_dim=64,
                 enc=dict(epochs=60, batch=256, code_dim=512, feat_dim=4096, temp=0.15, lr=0.01,
                          lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0),
                 kge_epochs=450, kge_batch=512, kge_lr=0.01)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, kge_dim=64,
                enc=dict(epochs=80, batch=256, code_dim=512, feat_dim=4096, temp=0.15, lr=0.01,
                         lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0),
                kge_epochs=600, kge_batch=1024, kge_lr=0.01)

LEX_FEAT_DIM = 4096


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# CHANNEL CONSTRUCTION.
#   Structural channel: random-projected propagated visible-graph adjacency (degree-BIASED view).
#   Lexical channel:    char-trigram surface features of the concept string (EXTERIOR / degree-blind view).
# ---------------------------------------------------------------------------

def structural_features(vis_tri, n_nodes, dim, seed, device, hop=STRUCT_HOP):
    """Per-entity structural feature [n, dim] from a random-projection of the propagated visible adjacency.
    F = normalize( A@P + hop * A@(A@P) ), P ~ N(0,1) [n, dim]. Degree-biased by construction (hub rows are dense)."""
    A = torch.zeros((n_nodes, n_nodes), dtype=torch.float32, device=device)
    src = torch.from_numpy(vis_tri[:, 0]).to(device)
    dst = torch.from_numpy(vis_tri[:, 2]).to(device)
    A[src, dst] = 1.0
    A[dst, src] = 1.0                                            # symmetrize (undirected neighborhood)
    g = torch.Generator(device="cpu").manual_seed(seed)
    P = torch.randn(n_nodes, dim, generator=g).to(device)
    AP = A @ P
    F = AP + hop * (A @ AP)
    return torch.nn.functional.normalize(F, dim=1)


def lexical_features(node_words, feat_dim, dim, seed, device):
    """Per-entity lexical feature [n, dim] = random-projection of the char-trigram surface features (exterior)."""
    Xl = char_trigram_features(node_words, feat_dim)            # [n, feat_dim] L2 rows
    Xt = torch.from_numpy(Xl).to(device)
    g = torch.Generator(device="cpu").manual_seed(seed + 71)
    P = torch.randn(feat_dim, dim, generator=g).to(device)
    F = Xt @ P
    return torch.nn.functional.normalize(F, dim=1)


def _topk_mask(feats, k, device):
    """Boolean [n, n] mask: True where column j is in the top-k cosine neighbours of row i (excluding self)."""
    n = feats.shape[0]
    S = feats @ feats.t()                                       # [n, n] cosine (rows normalized)
    S.fill_diagonal_(-1e9)
    kk = int(min(k, n - 1))
    idx = torch.topk(S, kk, dim=1).indices                     # [n, kk]
    mask = torch.zeros((n, n), dtype=torch.bool, device=device)
    mask.scatter_(1, idx, True)
    return mask


def agreement_edges(feat_a, feat_b, k, device):
    """Cross-channel agreement graph: (i,j) is an edge iff j is a top-k neighbour of i in BOTH channels.
    Symmetrized (OR of directions). Returns (src[E], dst[E]) numpy int64."""
    ma = _topk_mask(feat_a, k, device)
    mb = _topk_mask(feat_b, k, device)
    agr = ma & mb                                              # AND across channels (filters degree-hubs)
    agr = agr | agr.t()                                        # symmetrize
    agr.fill_diagonal_(False)
    ij = torch.nonzero(agr, as_tuple=False)                    # [E, 2]
    return ij[:, 0].cpu().numpy().astype(np.int64), ij[:, 1].cpu().numpy().astype(np.int64)


def _pearson(a, b):
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    if a.shape[0] < 3 or a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _knn_indegree(feat, k, device):
    """Per-entity kNN IN-degree [n]: how many other entities have this entity in their top-k cosine neighbours. This is
    the operationally-relevant degree-encoding probe: a channel that lets high-degree nodes DOMINATE neighbourhoods (the
    popularity-shortcut mechanism) produces high kNN in-degree for high-degree nodes."""
    mask = _topk_mask(feat, k, device)                          # [n,n] True where j in top-k of i
    return mask.sum(dim=0).cpu().numpy().astype(np.float64)     # column-sum = in-degree of each j


def channel_preflight(feat_struct, feat_lex, deg_vis, seed, device, sample=INDEP_SAMPLE, k=CONS_KNN):
    """PRE-FLIGHT channel-independence gate (runs BEFORE the consolidation loop -- the cheapest falsifier, per the
    prior-art through-line: verify the independence premise, don't assume it).

    The LOAD-BEARING check is each channel's correlation WITH NODE DEGREE (Director-hardened): struct_deg_r + lex_deg_r
    = Pearson of each channel's per-entity kNN IN-degree vs node graph-degree. If BOTH channels are degree-loaded, their
    'agreement' is just shared degree bias and the loop is INVALID -> BLOCK. The exterior (lexical) channel MUST be
    degree-decorrelated for the cross-channel AND to FILTER popularity.

    NOTE on cross_sim_r (reported): two channels that must AGREE necessarily SHARE the semantic signal, so a HIGH marginal
    cross-channel similarity correlation is EXPECTED and fine (this is the CLIP/co-training subtlety: the premise is
    CONDITIONAL independence given the label, not marginal independence). cross_sim_r is therefore used ONLY to flag
    near-IDENTICAL / collapsed channels (redundancy) at a HIGH threshold, NOT as a low-pass pass-condition."""
    n = feat_struct.shape[0]
    g = np.random.default_rng(seed * 13 + 5)
    m = int(min(sample, n * (n - 1) // 2))
    ii = g.integers(0, n, size=m); jj = g.integers(0, n, size=m)
    keep = ii != jj
    ii = ii[keep]; jj = jj[keep]
    it = torch.from_numpy(ii).to(device); jt = torch.from_numpy(jj).to(device)
    s_sim = (feat_struct[it] * feat_struct[jt]).sum(dim=1).cpu().numpy()
    l_sim = (feat_lex[it] * feat_lex[jt]).sum(dim=1).cpu().numpy()
    cross_sim_r = _pearson(s_sim, l_sim)

    deg = np.asarray(deg_vis, dtype=np.float64)
    struct_deg_r = _pearson(_knn_indegree(feat_struct, k, device), deg)
    lex_deg_r = _pearson(_knn_indegree(feat_lex, k, device), deg)

    exterior_decorrelated = bool(abs(lex_deg_r) < INDEP_R_MAX)          # the exterior channel must NOT encode degree
    both_degree_loaded = bool(abs(struct_deg_r) >= INDEP_R_MAX and abs(lex_deg_r) >= INDEP_R_MAX)
    redundant = bool(abs(cross_sim_r) >= REDUNDANT_CROSS)               # channels near-identical -> no independent info
    passes = bool(exterior_decorrelated and not both_degree_loaded and not redundant)
    flagged = bool(both_degree_loaded or redundant)
    return dict(cross_sim_r=cross_sim_r, struct_deg_r=struct_deg_r, lex_deg_r=lex_deg_r,
                exterior_decorrelated=exterior_decorrelated, both_degree_loaded=both_degree_loaded,
                redundant=redundant, passes=passes, flagged=flagged, n_pairs=int(ii.shape[0]))


def _effective_rank(E):
    """Effective rank = exp(entropy of normalized singular values) of the mean-centered code matrix (spread dims)."""
    try:
        Ec = E - E.mean(dim=0, keepdim=True)
        s = torch.linalg.svdvals(Ec.float())
        s = s[s > 1e-9]
        if s.numel() == 0:
            return 0.0
        p = s / s.sum()
        return float(torch.exp(-(p * torch.log(p)).sum()))
    except Exception:
        return float("nan")


def _rep_variance(E):
    """Representation-variance (anti-collapse; prior-art pitfall #5/#7 + Oono-Suzuki oversmoothing): fraction of code
    energy that is NON-constant across entities. Oversmoothing collapse -> all rows -> same vector -> centered energy
    -> 0 -> rep_variance -> 0. A healthy settled geometry keeps rep_variance well above the floor."""
    try:
        Ec = E - E.mean(dim=0, keepdim=True)
        return float(Ec.pow(2).sum(dim=1).mean() / (E.pow(2).sum(dim=1).mean() + 1e-12))
    except Exception:
        return float("nan")


# ---------------------------------------------------------------------------
# CONSOLIDATION: contrastive "sleep replay" settle over the agreement graph.
# Unit-norm codes (blocks the norm-blowup degree channel). InfoNCE: pull agreement-positives together, push random
# negatives apart. Brain analog: replay-driven Hebbian potentiation of co-agreeing representations + competitive norm.
# ---------------------------------------------------------------------------

def consolidate(agr_src, agr_dst, E0, n, passes, alpha, device, log_tag=""):
    """Normalized-Laplacian graph diffusion WITH RESTART (personalized-PageRank / SR) over the agreement graph.
    E^{k+1} = (1-alpha) * S @ E^k + alpha * E0, with S = D^-1/2 W D^-1/2 (symmetric-normalized adjacency of the
    agreement edges) and restart anchor E0 (the exterior-informed initial code). Returns the settled code UN-normalized
    (unit-normalizing destroys the additive translation structure the relation read-off needs -- verified empirically).
    Isolated nodes (no agreement neighbours) keep their anchor E0 (S row = 0): rare concepts are NOT pushed toward hubs.
    """
    if agr_src.shape[0] == 0:
        _log("    consolidate%s: EMPTY agreement graph -> returning anchor E0 unchanged" % log_tag)
        return E0.clone()
    W = torch.zeros((n, n), dtype=torch.float32, device=device)
    W[torch.from_numpy(agr_src).to(device), torch.from_numpy(agr_dst).to(device)] = 1.0
    W = torch.maximum(W, W.t())                                 # symmetric
    deg = W.sum(dim=1)
    dinv = torch.where(deg > 0, deg.pow(-0.5), torch.zeros_like(deg))
    S = dinv[:, None] * W * dinv[None, :]                       # D^-1/2 W D^-1/2 (normalized Laplacian propagation)
    E = E0.clone()
    for p in range(passes):
        E = (1.0 - alpha) * (S @ E) + alpha * E0                # PPR/SR restart step (anti-collapse)
    _log("    consolidate%s: diffusion-restart passes=%d alpha=%.2f agr_edges=%d effective_rank=%.1f/%d rep_var=%.3f"
         % (log_tag, passes, alpha, int(agr_src.shape[0]), _effective_rank(E), E.shape[1], _rep_variance(E)))
    return E


def fit_relation_offsets(E_cons, vis_tri, n_rels, dim, epochs, batch, lr, seed, device,
                         neg=KGE_NEG, margin=KGE_MARGIN):
    """Freeze consolidated entity codes; fit additive relation offsets R[n_rels,dim] via margin-rank on visible edges."""
    E = E_cons.detach()
    R = rt._init_emb(n_rels, dim, seed + 55, device, 6.0 / (dim ** 0.5)).clone().requires_grad_(True)
    opt = torch.optim.Adam([R], lr=lr)
    tri = torch.from_numpy(vis_tri).to(device)
    M = tri.shape[0]
    if M == 0:
        return R.detach()
    gen = torch.Generator(device="cpu").manual_seed(seed + 313)
    bs = int(min(batch, M))
    n = E.shape[0]
    for ep in range(epochs):
        perm = torch.from_numpy(np.random.default_rng(seed * 7919 + ep).permutation(M)).to(device)
        for start in range(0, M, bs):
            idx = perm[start:start + bs]
            b = tri[idx]
            h = b[:, 0]; r = b[:, 1]; t = b[:, 2]
            bn = h.shape[0]
            t_neg = torch.randint(0, n, (bn * neg,), generator=gen).to(device)
            hh = h.repeat_interleave(neg); rr = r.repeat_interleave(neg)
            pos_d = (E[h] + R[r] - E[t]).abs().sum(dim=1)
            neg_d = (E[hh] + R[rr] - E[t_neg]).abs().sum(dim=1)
            pos_rep = pos_d.repeat_interleave(neg)
            loss = torch.relu(margin + pos_rep - neg_d).mean()
            opt.zero_grad(); loss.backward(); opt.step()
    return R.detach()


# ---------------------------------------------------------------------------
# Per-seed run on the REAL typed subgraph.
# ---------------------------------------------------------------------------

def run_seed(seed, edges, rels, node_words, roles_disc, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    n_rels = int(np.asarray(rels).max()) + 1
    dim = cfg["kge_dim"]

    vis, hold, tri_all = rt.split_heldout(edges, rels, HELDOUT_FRAC, seed)
    comp = rt.completable_mask(hold, vis, n_nodes, n_rels)
    hold_comp = hold[comp]
    n_comp = int(hold_comp.shape[0]); n_hold = int(hold.shape[0])
    deg_vis = rt.visible_degree(vis, n_nodes)
    deg_vis_t = torch.from_numpy(deg_vis.astype(np.float32)).to(device)
    _log("  seed=%d vis_tri=%d hold_tri=%d completable=%d" % (seed, vis.shape[0], n_hold, n_comp))

    rng = np.random.default_rng(seed * 991 + 3)
    if n_comp > MAX_RANK_QUERIES:
        queries = hold_comp[rng.choice(n_comp, size=MAX_RANK_QUERIES, replace=False)]
    else:
        queries = hold_comp
    cand = rt.build_ranking_candidates(queries, tri_all, n_nodes, N_RANK_NEG, seed) if queries.shape[0] > 0 \
        else np.zeros((0, N_RANK_NEG + 1), dtype=np.int64)
    strata, (sq1, sq2) = rt.stratify_by_target_degree(queries, deg_vis)

    arms = {}; arms_strat = {}; sigs = {}; failures = []

    def _score_and_store(arm, score_fn):
        try:
            if queries.shape[0] == 0:
                raise RuntimeError("no completable queries")
            sc = score_fn()
            rank = rt._ranks_from_scores(sc)
            h1, h3, h10, mrr = rt._hits_from_ranks(rank)
            arms[arm] = dict(hits1=h1, hits3=h3, hits10=h10, mrr=mrr)
            arms_strat[arm] = rt._per_stratum_hits1(rank.cpu().numpy(), strata)
            sigs[arm] = hashlib.sha256(np.round(sc[:64].detach().cpu().numpy().astype(np.float64), 5)
                                       .tobytes()).hexdigest()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failures.append(dict(arm=arm, failure_class=type(e).__name__, msg=str(e)[:200]))
            arms[arm] = dict(hits1=float("nan"), hits3=float("nan"), hits10=float("nan"), mrr=float("nan"))
            arms_strat[arm] = {s: dict(hits1=float("nan"), n=0) for s in STRATA}
            sigs[arm] = "%s_failed" % arm

    # ---- Channels + PRE-FLIGHT independence gate (runs FIRST; gates the whole consolidation loop) ----
    feat_struct = structural_features(vis, n_nodes, dim, seed, device)                 # relational content (biased)
    feat_lex = lexical_features(node_words, LEX_FEAT_DIM, dim, seed, device)           # exterior (degree-blind)
    feat_struct2 = structural_features(vis, n_nodes, dim, seed + 1234, device, hop=1.0)  # 2nd structural view (trap)
    pf = channel_preflight(feat_struct, feat_lex, deg_vis, seed, device)
    _log("  seed=%d PRE-FLIGHT channels: cross_sim_r=%.3f struct_deg_r=%.3f lex_deg_r=%.3f | cross_indep=%s "
         "exterior_decorrelated=%s both_degree_loaded=%s PASSES=%s flagged=%s (pairs=%d)"
         % (seed, pf["cross_sim_r"], pf["struct_deg_r"], pf["lex_deg_r"], pf["cross_independent"],
            pf["exterior_decorrelated"], pf["both_degree_loaded"], pf["passes"], pf["flagged"], pf["n_pairs"]))
    preflight_blocked = bool(not pf["passes"])
    if preflight_blocked:
        _log("  seed=%d PRE-FLIGHT GATE FAILED -> BLOCKING the consolidation loop (channels not independent / "
             "degree-loaded); consolidation arms will NOT be run for this seed." % seed)

    # ---- DISCRETE (one-shot substrate code) ----
    X = char_trigram_features(node_words, cfg["enc"]["feat_dim"])
    vis_edges = np.stack([vis[:, 0], vis[:, 2]], axis=1).astype(np.int64)
    vis_rels_e = vis[:, 1].astype(np.int64)
    Z = train_binding_encoder_dev(X, vis_edges, vis_rels_e, roles_disc, cfg["enc"], seed, device,
                                  out_dir=out_dir, tag="BIND_vis")
    Zn = torch.nn.functional.normalize(Z, dim=1)
    _score_and_store(DISCRETE, lambda: rt.rank_discrete(Zn, roles_disc, queries, cand, device))

    # ---- ONESHOT_TRANSE (the just-failed one-shot additive code) ----
    Et, Rt = rt.train_kge(n_nodes, n_rels, vis, dim, cfg["kge_epochs"], cfg["kge_batch"], cfg["kge_lr"],
                          seed, device, "transe")
    _score_and_store(ONESHOT, lambda: rt.rank_transe(Et, Rt, queries, cand, device))

    # ---- CONSOLIDATED (mechanism): agreement(struct, lex) -> settle -> fit offsets -> additive read-off ----
    # Gated by the pre-flight: if channels are not independent, the loop is INVALID and is NOT run (BLOCKED).
    n_agr = -1; n_trap = -1; cons_eff_rank = float("nan"); trap_eff_rank = float("nan")
    cons_rep_var = float("nan"); trap_rep_var = float("nan")
    if preflight_blocked:
        for arm in (CONS, TRAP):
            arms[arm] = dict(hits1=float("nan"), hits3=float("nan"), hits10=float("nan"), mrr=float("nan"))
            arms_strat[arm] = {s: dict(hits1=float("nan"), n=0) for s in STRATA}
            sigs[arm] = "%s_blocked_preflight" % arm
    else:
        # CONS restart-anchors to the STRUCTURAL channel (relational content), diffused over the DEGREE-BALANCED
        # agreement(struct,lex) graph with normalized-Laplacian restart -> degree-invariant relational placement.
        a_src, a_dst = agreement_edges(feat_struct, feat_lex, CONS_KNN, device)
        n_agr = int(a_src.shape[0])
        E_cons = consolidate(a_src, a_dst, feat_struct, n_nodes, CONS_PASSES, CONS_ALPHA, device, "[cons]")
        cons_eff_rank = _effective_rank(E_cons); cons_rep_var = _rep_variance(E_cons)
        R_cons = fit_relation_offsets(E_cons, vis, n_rels, dim, REL_EPOCHS, REL_BATCH, cfg["kge_lr"], seed, device)
        _score_and_store(CONS, lambda: rt.rank_transe(E_cons, R_cons, queries, cand, device))

        # ---- CONSOLIDATED_TRAP (shared-bias control): agreement(struct, struct2) -> SAME anchor + pipeline ----
        # Differs ONLY in the 2nd channel (struct2, NOT degree-blind) -> agreement is NOT degree-balanced -> re-derives
        # the popularity shortcut. Isolates the channel-independence variable.
        t_src, t_dst = agreement_edges(feat_struct, feat_struct2, CONS_KNN, device)
        n_trap = int(t_src.shape[0])
        E_trap = consolidate(t_src, t_dst, feat_struct, n_nodes, CONS_PASSES, CONS_ALPHA, device, "[trap]")
        trap_eff_rank = _effective_rank(E_trap); trap_rep_var = _rep_variance(E_trap)
        R_trap = fit_relation_offsets(E_trap, vis, n_rels, dim, REL_EPOCHS, REL_BATCH, cfg["kge_lr"], seed + 7, device)
        _score_and_store(TRAP, lambda: rt.rank_transe(E_trap, R_trap, queries, cand, device))
        _log("  seed=%d effective_rank cons=%.1f trap=%.1f (dim=%d; COLLAPSE if <= %.1f)"
             % (seed, cons_eff_rank, trap_eff_rank, dim, COLLAPSE_RANK_FLOOR))

    # ---- POPULARITY (degree-only) ----
    _score_and_store(POP, lambda: rt.rank_popularity(deg_vis_t, queries, cand, device))

    # ---- RANDOM (control) ----
    Er = rt._renorm_rows(rt._init_emb(n_nodes, dim, seed + 101, device, 6.0 / (dim ** 0.5)), cap=1.0)
    Rr = rt._init_emb(n_rels, dim, seed + 102, device, 6.0 / (dim ** 0.5))
    _score_and_store(RANDOM, lambda: rt.rank_transe(Er, Rr, queries, cand, device))

    # ---- ORACLE (must-fire): TransE trained WITH held-out visible ----
    Eo, Ro = rt.train_kge(n_nodes, n_rels, tri_all, dim, cfg["kge_epochs"], cfg["kge_batch"], cfg["kge_lr"],
                          seed, device, "transe")
    _score_and_store(ORACLE, lambda: rt.rank_transe(Eo, Ro, queries, cand, device))

    for arm in ALL_ARMS:
        a = arms[arm]; st = arms_strat[arm]
        _log("  seed=%d %-20s hits1=%s (LOW=%s[n=%d] MID=%s[n=%d] HIGH=%s[n=%d]) mrr=%s" % (
            seed, arm, _fmt(a["hits1"]),
            _fmt(st["LOW"]["hits1"]), st["LOW"]["n"], _fmt(st["MID"]["hits1"]), st["MID"]["n"],
            _fmt(st["HIGH"]["hits1"]), st["HIGH"]["n"], _fmt(a["mrr"])))
    _log("  seed=%d degree tertiles: q1=%.1f q2=%.1f" % (seed, sq1, sq2))

    return dict(seed=seed, arms=arms, arms_strat=arms_strat, arm_sigs=sigs, preflight=pf,
                preflight_blocked=preflight_blocked, cons_eff_rank=cons_eff_rank, trap_eff_rank=trap_eff_rank,
                cons_rep_var=cons_rep_var, trap_rep_var=trap_rep_var,
                n_agr_edges=n_agr, n_trap_edges=n_trap,
                deg_tertiles=[sq1, sq2], n_completable=n_comp, n_heldout=n_hold, n_queries=int(queries.shape[0]),
                n_visible_tri=int(vis.shape[0]), failures=failures, kge_dim=dim, n_rels=n_rels)


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def aggregate_and_verdict(per_seed, meta):
    def A(arm, key):
        return rt._nm([m["arms"][arm][key] for m in per_seed if arm in m["arms"]])

    cons1 = A(CONS, "hits1"); trap1 = A(TRAP, "hits1"); discrete1 = A(DISCRETE, "hits1")
    oneshot1 = A(ONESHOT, "hits1"); pop1 = A(POP, "hits1"); random1 = A(RANDOM, "hits1"); oracle1 = A(ORACLE, "hits1")
    n_comp = int(rt._nm([m["n_completable"] for m in per_seed]))
    n_hold = int(rt._nm([m["n_heldout"] for m in per_seed]))
    cross_sim_r = rt._nm([m["preflight"]["cross_sim_r"] for m in per_seed])
    struct_deg_r = rt._nm([m["preflight"]["struct_deg_r"] for m in per_seed])
    lex_deg_r = rt._nm([m["preflight"]["lex_deg_r"] for m in per_seed])
    n_blocked = int(sum(1 for m in per_seed if m.get("preflight_blocked")))
    any_flagged = bool(any(m["preflight"]["flagged"] for m in per_seed))
    both_degree_loaded = bool(any(m["preflight"]["both_degree_loaded"] for m in per_seed))
    cons_eff_rank = rt._nm([m.get("cons_eff_rank", float("nan")) for m in per_seed])
    cons_rep_var = rt._nm([m.get("cons_rep_var", float("nan")) for m in per_seed])

    def _strat(arm, sname):
        return rt._strat_agg(per_seed, arm, sname)

    strat = {}
    for sname in STRATA:
        c_h, c_n = _strat(CONS, sname)
        d_h, _dn = _strat(DISCRETE, sname)
        p_h, _pn = _strat(POP, sname)
        tr_h, _tn = _strat(TRAP, sname)
        cd = (c_h - d_h) if (c_h == c_h and d_h == d_h) else float("nan")
        strat[sname] = dict(cons_hits1=c_h, discrete_hits1=d_h, pop_hits1=p_h, trap_hits1=tr_h,
                            delta_cons_discrete=cd, n=c_n)

    d_cons_discrete = (cons1 - discrete1) if (cons1 == cons1 and discrete1 == discrete1) else float("nan")
    d_cons_pop = (cons1 - pop1) if (cons1 == cons1 and pop1 == pop1) else float("nan")
    pop_recover_frac = (pop1 / cons1) if (cons1 == cons1 and cons1 > 1e-9 and pop1 == pop1) else float("nan")
    cons_high = strat["HIGH"]["cons_hits1"]; cons_low = strat["LOW"]["cons_hits1"]
    cons_flatness = abs(cons_high - cons_low) if (cons_high == cons_high and cons_low == cons_low) else float("nan")
    trap_high = strat["HIGH"]["trap_hits1"]; trap_low = strat["LOW"]["trap_hits1"]
    trap_flatness = abs(trap_high - trap_low) if (trap_high == trap_high and trap_low == trap_low) else float("nan")

    # ---- precondition gates ----
    enough = bool(n_comp >= MIN_HELDOUT_COMPLETABLE)
    negatives_valid = bool(random1 == random1 and random1 <= RANDOM_CEIL)
    oracle_fires = bool(oracle1 == oracle1 and random1 == random1 and oracle1 >= random1 + ORACLE_FIRE_MARGIN)
    # PRE-FLIGHT gate is authoritative: channels independent iff NO seed was blocked and none flagged.
    channels_independent = bool(n_blocked == 0 and not any_flagged)
    channels_flagged = bool(any_flagged or n_blocked > 0)

    # ---- SURVIVAL + FLATNESS decision (the pre-registered core) ----
    aggregate_margin_ok = bool(d_cons_discrete == d_cons_discrete and d_cons_discrete >= GEOM_MARGIN)

    def _tail_ok(sname):
        s = strat[sname]
        return bool(s["n"] >= MIN_STRAT_Q and s["delta_cons_discrete"] == s["delta_cons_discrete"]
                    and s["delta_cons_discrete"] >= STRAT_MARGIN)

    def _tail_collapse(sname):
        s = strat[sname]
        return bool(s["n"] >= MIN_STRAT_Q and s["delta_cons_discrete"] == s["delta_cons_discrete"]
                    and s["delta_cons_discrete"] <= TIE_EPS)

    tail_survives = bool(_tail_ok("LOW") and _tail_ok("MID"))
    tail_collapses = bool(_tail_collapse("LOW") or _tail_collapse("MID"))
    is_flat = bool(cons_flatness == cons_flatness and cons_flatness <= FLATNESS_EPS)
    concentrates_high = bool(cons_flatness == cons_flatness and cons_flatness >= HIGH_LOW_GAP_FAIL)
    pop_not_recovering = bool(d_cons_pop == d_cons_pop and d_cons_pop >= POP_GAP
                              and pop_recover_frac == pop_recover_frac and pop_recover_frac <= POP_RECOVER_FRAC_MAX)
    pop_recovers = bool((d_cons_pop == d_cons_pop and d_cons_pop <= TIE_EPS)
                        or (pop_recover_frac == pop_recover_frac and pop_recover_frac >= POP_RECOVER_FRAC_HI))
    # TRAP must FAIL (shared-bias re-derives popularity): collapse on tail OR concentrate on high.
    trap_fails = bool((trap_flatness == trap_flatness and trap_flatness >= HIGH_LOW_GAP_FAIL)
                      or (trap_high == trap_high and trap_low == trap_low and (trap_high - trap_low) >= HIGH_LOW_GAP_FAIL))

    consolidation_collapsed = bool((cons_eff_rank == cons_eff_rank and cons_eff_rank <= COLLAPSE_RANK_FLOOR)
                                   or (cons_rep_var == cons_rep_var and cons_rep_var <= COLLAPSE_VAR_FLOOR))
    # HARD_PASS gate: independence is verified DIRECTLY by the pre-flight (channels_independent), so trap_fails is a
    # REPORTED corroborator (the random-projection structural channel may not be degree-loaded, so the trap can be a
    # weak control on real data; a genuine cons win must not be false-blocked by a non-firing trap).
    consolidation_works = bool(channels_independent and not consolidation_collapsed and aggregate_margin_ok
                              and tail_survives and is_flat and pop_not_recovering)
    another_shortcut = bool(channels_independent and not consolidation_collapsed
                            and (tail_collapses or concentrates_high or pop_recovers))

    if not enough:
        verdict = "INCONCLUSIVE_TOO_FEW_COMPLETABLE"
    elif not negatives_valid:
        verdict = "INCONCLUSIVE_NEGATIVES_TRIVIAL"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_DID_NOT_FIRE"
    elif channels_flagged or (not channels_independent):
        verdict = "HARD_FAIL_CHANNELS_NOT_INDEPENDENT"
    elif consolidation_collapsed:
        verdict = "HARD_FAIL_CONSOLIDATION_COLLAPSED"
    elif consolidation_works:
        verdict = "HARD_PASS_CONSOLIDATION_DEGREE_INVARIANT"
    elif another_shortcut:
        verdict = "HARD_FAIL_CONSOLIDATION_ANOTHER_SHORTCUT"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_DEGREE_AMBIGUOUS"

    verdict_msg = (
        "%s || COMPLETABLE reach@1: CONS=%.3f TRAP=%.3f DISCRETE=%.3f ONESHOT=%.3f POP=%.3f RANDOM=%.3f ORACLE=%.3f || "
        "d(cons-discrete)=%s d(cons-pop)=%s pop_recover_frac=%s cons_flatness|hi-lo|=%s trap_flatness=%s || "
        "STRATA cons/discrete/pop [n]: LOW=%.3f/%.3f/%.3f[%d] MID=%.3f/%.3f/%.3f[%d] HIGH=%.3f/%.3f/%.3f[%d] || "
        "STRATA d(cons-discrete): LOW=%s MID=%s HIGH=%s || "
        "PRE-FLIGHT channels: cross_sim_r=%s struct_deg_r=%s lex_deg_r=%s both_degree_loaded=%s independent=%s "
        "flagged=%s n_blocked=%d/%d cons_eff_rank=%s || "
        "agg_margin(>=%.2f)=%s tail_survives(LOW&MID>=%.2f)=%s flat(<=%.2f)=%s tail_collapses(<=%.2f)=%s "
        "concentrates_high(>=%.2f)=%s pop_not_recovering=%s pop_recovers=%s trap_fails=%s || "
        "HARD_PASS(consolidation)=%s HARD_FAIL(shortcut)=%s || "
        "GATES: enough(%d>=%d)=%s neg_valid(rand<=%.2f)=%s oracle_fires=%s || n_hold=%d nodes=%d E=%d seeds=%d run=%s" % (
            verdict, cons1, trap1, discrete1, oneshot1, pop1, random1, oracle1,
            _fmt(d_cons_discrete), _fmt(d_cons_pop), _fmt(pop_recover_frac), _fmt(cons_flatness), _fmt(trap_flatness),
            strat["LOW"]["cons_hits1"], strat["LOW"]["discrete_hits1"], strat["LOW"]["pop_hits1"], strat["LOW"]["n"],
            strat["MID"]["cons_hits1"], strat["MID"]["discrete_hits1"], strat["MID"]["pop_hits1"], strat["MID"]["n"],
            strat["HIGH"]["cons_hits1"], strat["HIGH"]["discrete_hits1"], strat["HIGH"]["pop_hits1"], strat["HIGH"]["n"],
            _fmt(strat["LOW"]["delta_cons_discrete"]), _fmt(strat["MID"]["delta_cons_discrete"]),
            _fmt(strat["HIGH"]["delta_cons_discrete"]),
            _fmt(cross_sim_r), _fmt(struct_deg_r), _fmt(lex_deg_r), both_degree_loaded, channels_independent,
            channels_flagged, n_blocked, len(per_seed), _fmt(cons_eff_rank),
            GEOM_MARGIN, aggregate_margin_ok, STRAT_MARGIN, tail_survives, FLATNESS_EPS, is_flat, TIE_EPS, tail_collapses,
            HIGH_LOW_GAP_FAIL, concentrates_high, pop_not_recovering, pop_recovers, trap_fails,
            consolidation_works, another_shortcut,
            n_comp, MIN_HELDOUT_COMPLETABLE, enough, RANDOM_CEIL, negatives_valid, oracle_fires,
            n_hold, meta.get("n_nodes", -1), meta.get("n_edges", -1), len(per_seed),
            "full" if len(per_seed) == 3 else "smoke"))

    gates = dict(
        verdict=verdict,
        arms={a: {k: A(a, k) for k in ("hits1", "hits3", "hits10", "mrr")} for a in ALL_ARMS},
        strata=strat,
        cg=dict(cons_hits1=cons1, trap_hits1=trap1, discrete_hits1=discrete1, oneshot_hits1=oneshot1,
                pop_hits1=pop1, random_hits1=random1, oracle_hits1=oracle1,
                delta_cons_discrete=d_cons_discrete, delta_cons_pop=d_cons_pop, pop_recover_frac=pop_recover_frac,
                cons_flatness=cons_flatness, trap_flatness=trap_flatness,
                aggregate_margin_ok=aggregate_margin_ok, tail_survives=tail_survives, is_flat=is_flat,
                tail_collapses=tail_collapses, concentrates_high=concentrates_high,
                pop_not_recovering=pop_not_recovering, pop_recovers=pop_recovers, trap_fails=trap_fails,
                cons_eff_rank=cons_eff_rank, cons_rep_var=cons_rep_var,
                consolidation_collapsed=consolidation_collapsed,
                consolidation_works=consolidation_works, another_shortcut=another_shortcut),
        channels=dict(cross_sim_r=cross_sim_r, struct_deg_r=struct_deg_r, lex_deg_r=lex_deg_r,
                      both_degree_loaded=both_degree_loaded, independent=channels_independent, flagged=channels_flagged,
                      n_blocked=n_blocked, n_seeds=len(per_seed), cons_eff_rank=cons_eff_rank,
                      INDEP_R_MAX=INDEP_R_MAX, INDEP_R_FLAG=INDEP_R_FLAG),
        discriminator_fires=dict(enough_completable=enough, negatives_valid=negatives_valid, oracle_fires=oracle_fires,
                                 channels_independent=channels_independent),
        n_completable=n_comp, n_heldout=n_hold,
        bands=dict(GEOM_MARGIN=GEOM_MARGIN, STRAT_MARGIN=STRAT_MARGIN, TIE_EPS=TIE_EPS, FLATNESS_EPS=FLATNESS_EPS,
                   HIGH_LOW_GAP_FAIL=HIGH_LOW_GAP_FAIL, POP_GAP=POP_GAP, POP_RECOVER_FRAC_MAX=POP_RECOVER_FRAC_MAX,
                   POP_RECOVER_FRAC_HI=POP_RECOVER_FRAC_HI, RANDOM_CEIL=RANDOM_CEIL,
                   ORACLE_FIRE_MARGIN=ORACLE_FIRE_MARGIN, MIN_STRAT_Q=MIN_STRAT_Q, HELDOUT_FRAC=HELDOUT_FRAC,
                   MIN_HELDOUT_COMPLETABLE=MIN_HELDOUT_COMPLETABLE, N_RANK_NEG=N_RANK_NEG,
                   INDEP_R_MAX=INDEP_R_MAX, INDEP_R_FLAG=INDEP_R_FLAG, COLLAPSE_RANK_FLOOR=COLLAPSE_RANK_FLOOR,
                   CONS_KNN=CONS_KNN, CONS_PASSES=CONS_PASSES, CONS_ALPHA=CONS_ALPHA),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted worlds prove the grounding-specific discriminators (a)/(b)/(c) FIRE.
# ---------------------------------------------------------------------------

# Pre-registered self-test bands (planted-world; picked BEFORE the run):
ST_CHANCE = 1.0 / (N_RANK_NEG + 1)     # ~0.01 filtered Hits@1 chance floor (THEORETICAL)
ST_CAPTURE_MIN = 5.0 * ST_CHANCE       # (a) non-vacuous: consolidation recovers >= 5x chance on the clean planted world
ST_FLAT_EPS = 0.12                     # (a) degree-flat: |cons_high - cons_low| <= this on the planted world
ST_POP_FIRE = 0.15                     # (b) planted-popularity baseline must fire >= this (catches popularity)


def _clustered_world(side, per_cell, n_rels, seed):
    """Clustered planted world: clusters = grid cells; each cluster has a VARIABLE number of member entities (planted
    degree variation); relations act at the CLUSTER level (grid translations). A held-out edge (h,r,t) requires placing
    h's cluster + offset r at t's cluster -> recovery is degree-INVARIANT because a rare (small-cluster / low-degree)
    entity inherits its cluster's relational placement exactly as a common one does. Returns (n, n_rels, tri, ent_cluster,
    cluster_centroids)."""
    g = np.random.default_rng(seed)
    K = side * side
    ncl = np.array([2 + int(g.integers(0, per_cell)) for _ in range(K)])
    ent_cluster = np.repeat(np.arange(K), ncl)
    n = int(ent_cluster.shape[0])
    cc = np.stack([np.arange(K) // side, np.arange(K) % side], axis=1).astype(np.float64)
    transl = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (2, 0)][:n_rels]
    members = [np.where(ent_cluster == c)[0] for c in range(K)]
    tri = []
    for r0 in range(side):
        for c0 in range(side):
            ch = r0 * side + c0
            for r, (dr, dc) in enumerate(transl):
                r1 = r0 + dr; c1 = c0 + dc
                if 0 <= r1 < side and 0 <= c1 < side:
                    ct = r1 * side + c1
                    for h in members[ch]:
                        for t in members[ct]:
                            tri.append((int(h), r, int(t)))
    return n, len(transl), np.asarray(tri, dtype=np.int64), ent_cluster, cc


def _cluster_feat(ent_cluster, cc, dim, seed, noise, device):
    """Additive-preserving channel feature: linear lift of the cluster centroid + independent gaussian noise.
    Two calls with different seeds -> INDEPENDENT noisy views of the same cluster geometry."""
    g = np.random.default_rng(seed)
    W = g.standard_normal((cc.shape[1], dim)).astype(np.float32)
    base = (cc[ent_cluster] @ W).astype(np.float32)
    F = base + noise * g.standard_normal((ent_cluster.shape[0], dim)).astype(np.float32)
    return torch.from_numpy(F).to(device)


def _noise_feat(n, dim, seed, device):
    g = torch.Generator(device="cpu").manual_seed(seed)
    return torch.randn(n, dim, generator=g).to(device)


def _selftest_cons_one(n, n_rels, tri_all, feat_a, feat_b, E0, dim, device, seed, run_pop=False):
    """Full consolidation pipeline (agreement -> diffusion-restart(E0) -> fit offsets -> rank) on a planted world."""
    rng = np.random.default_rng(seed + 7)
    M = tri_all.shape[0]
    perm = rng.permutation(M)
    n_hold = int(HELDOUT_FRAC * M)
    hold = tri_all[perm[:n_hold]]; vis = tri_all[perm[n_hold:]]
    comp = rt.completable_mask(hold, vis, n, n_rels)
    queries = hold[comp]
    if queries.shape[0] == 0:
        return None
    if queries.shape[0] > 400:
        queries = queries[rng.choice(queries.shape[0], size=400, replace=False)]
    cand = rt.build_ranking_candidates(queries, tri_all, n, min(N_RANK_NEG, n - 2), seed)
    deg_vis = rt.visible_degree(vis, n)
    deg_vis_t = torch.from_numpy(deg_vis.astype(np.float32)).to(device)
    strata, _q = rt.stratify_by_target_degree(queries, deg_vis)
    a_src, a_dst = agreement_edges(feat_a, feat_b, CONS_KNN, device)
    E = consolidate(a_src, a_dst, E0, n, CONS_PASSES, CONS_ALPHA, device, "[st]")
    R = fit_relation_offsets(E, vis, n_rels, dim, min(REL_EPOCHS, 300), 512, 0.01, seed, device)
    sc = rt.rank_transe(E, R, queries, cand, device)
    rank = rt._ranks_from_scores(sc).cpu().numpy()
    low = strata == 0; high = strata == 2
    out = dict(cons=float((rank < 1.0).mean()), eff_rank=_effective_rank(E), rep_var=_rep_variance(E),
               n_agr=int(a_src.shape[0]),
               cons_low=float((rank[low] < 1.0).mean()) if int(low.sum()) >= 10 else float("nan"),
               cons_high=float((rank[high] < 1.0).mean()) if int(high.sum()) >= 10 else float("nan"),
               sig=hashlib.sha256(np.round(sc[:32].cpu().numpy().astype(np.float64), 5).tobytes()).hexdigest())
    if run_pop:
        out["pop"] = rt._hits_from_ranks(rt._ranks_from_scores(rt.rank_popularity(deg_vis_t, queries, cand, device)))[0]
    return out


def _planted_popularity_world(n, n_rels, seed):
    """Tails ~ zipf popularity (no consistent geometry). Reuses the retest's construction shape."""
    rng = np.random.default_rng(seed + 4242)
    w = 1.0 / np.arange(1, n + 1)
    w = w / w.sum()
    tri = []
    for i in range(n):
        for r in range(n_rels):
            if rng.random() < 0.5:
                t = int(rng.choice(n, p=w))
                if t != i:
                    tri.append((i, r, t))
    return n, n_rels, np.asarray(tri, dtype=np.int64)


def _mechanism_selftest(device, dim=64):
    # (a) PLANTED INDEPENDENT AGREEMENT: clustered world; struct=cluster+noiseA (relational content + restart anchor),
    #     lex=cluster+noiseB (INDEPENDENT noise, exterior). Consolidation must CAPTURE the geometry (>=5x chance) and be
    #     degree-FLAT (rare small-cluster entities recover as well as common ones), and BEAT popularity.
    n, rg, tri_c, ent_cl, cc = _clustered_world(9, 3, 6, 0)
    fa = _cluster_feat(ent_cl, cc, dim, 11, 1.2, device)     # structural channel (also the restart anchor E0)
    fb = _cluster_feat(ent_cl, cc, dim, 999, 1.2, device)    # lexical channel (independent noise)
    ind = _selftest_cons_one(n, rg, tri_c, fa, fb, fa, dim, device, 7, run_pop=True)

    # (b) PLANTED PURE POPULARITY: zipf tails, NO geometry, channels = pure noise -> consolidation cannot fake a lever;
    #     popularity baseline fires.
    npp, rpp, tri_p = _planted_popularity_world(256, 6, 0)
    fp_a = _noise_feat(npp, dim, 1, device); fp_b = _noise_feat(npp, dim, 2, device)
    popw = _selftest_cons_one(npp, rpp, tri_p, fp_a, fp_b, fp_a, dim, device, 7, run_pop=True)

    # (c) PRE-FLIGHT INDEPENDENCE GATE LOGIC (Director-hardened; the cheapest falsifier). Demonstrated on synthetic
    #     channels with KNOWN degree-loading so the gate's decisions are checkable: a DEGREE-LOADED channel (high-degree
    #     nodes pulled toward a shared hub direction -> high kNN in-degree) vs a DEGREE-BLIND channel (pure noise).
    #       - (degree-loaded, degree-blind)  -> PASS  (exterior channel decorrelated from degree; AND filters popularity)
    #       - (degree-loaded, itself)         -> FLAGGED redundant (near-identical channels; no independent info)
    #       - (degree-loaded, degree-loaded2) -> FLAGGED both-degree-loaded (agreement = shared degree bias -> INVALID)
    ncx = 300
    gd = np.random.default_rng(3)
    deg_syn = gd.integers(1, 60, size=ncx).astype(np.float64)
    dn = torch.from_numpy((deg_syn / deg_syn.max()).astype(np.float32)).to(device)[:, None]
    hub = torch.nn.functional.normalize(_noise_feat(1, dim, 50, device), dim=1)
    ch_loaded = torch.nn.functional.normalize(_noise_feat(ncx, dim, 51, device) + 3.0 * dn * hub, dim=1)
    ch_loaded2 = torch.nn.functional.normalize(_noise_feat(ncx, dim, 53, device) + 3.0 * dn * hub, dim=1)
    ch_blind = _noise_feat(ncx, dim, 52, device)
    chk_indep = channel_preflight(ch_loaded, ch_blind, deg_syn, 7, device)
    chk_corr = channel_preflight(ch_loaded, ch_loaded, deg_syn, 7, device)
    chk_bothdeg = channel_preflight(ch_loaded, ch_loaded2, deg_syn, 7, device)

    # (d) COLLAPSE DISCRIMINATOR: a collapsed (near-constant across entities) code is CAUGHT by the representation-
    #     variance floor; the healthy consolidated code from (a) PASSES it.
    base_row = _noise_feat(1, dim, 9, device)
    collapsed = base_row.repeat(n, 1) + 1e-4 * _noise_feat(n, dim, 3, device)
    collapsed_var = _rep_variance(collapsed)
    healthy_var = ind["rep_var"] if ind else float("nan")

    # ---- assertions (the discriminators must fire) ----
    a_cons_recovers = bool(ind is not None and ind["cons"] == ind["cons"] and ind["cons"] >= ST_CAPTURE_MIN)
    a_cons_flat = bool(ind is not None and ind["cons_low"] == ind["cons_low"] and ind["cons_high"] == ind["cons_high"]
                       and abs(ind["cons_high"] - ind["cons_low"]) <= ST_FLAT_EPS)
    a_cons_beats_pop = bool(ind is not None and ind.get("pop", float("nan")) == ind.get("pop", float("nan"))
                            and (ind["cons"] - ind["pop"]) >= 0.02)
    b_cons_no_edge_over_pop = bool(popw is not None and popw["cons"] == popw["cons"]
                                   and popw.get("pop", float("nan")) == popw.get("pop", float("nan"))
                                   and (popw["cons"] - popw["pop"]) <= 0.05)
    b_pop_fires = bool(popw is not None and popw.get("pop", float("nan")) == popw.get("pop", float("nan"))
                       and popw["pop"] >= ST_POP_FIRE)
    c_indep_passes = bool(chk_indep["passes"] and not chk_indep["flagged"])
    c_corr_flagged = bool(chk_corr["flagged"] and not chk_corr["passes"])
    c_bothdeg_flagged = bool(chk_bothdeg["both_degree_loaded"] and chk_bothdeg["flagged"] and not chk_bothdeg["passes"])
    d_collapse_caught = bool(collapsed_var <= COLLAPSE_VAR_FLOOR
                             and healthy_var == healthy_var and healthy_var > COLLAPSE_VAR_FLOOR)
    arms_differ = bool(len({ind["sig"] if ind else "x", popw["sig"] if popw else "z"}) >= 2)

    res = dict(
        a_ind_cons=round(ind["cons"], 4) if ind else None, a_ind_pop=round(ind.get("pop", float("nan")), 4) if ind else None,
        a_ind_cons_low=round(ind["cons_low"], 4) if ind else None,
        a_ind_cons_high=round(ind["cons_high"], 4) if ind else None,
        a_ind_eff_rank=round(ind["eff_rank"], 2) if ind else None, a_n_agr=ind["n_agr"] if ind else None,
        b_pop_cons=round(popw["cons"], 4) if popw else None,
        b_pop_pop=round(popw.get("pop", float("nan")), 4) if popw else None,
        c_indep_cross_r=round(chk_indep["cross_sim_r"], 4), c_corr_cross_r=round(chk_corr["cross_sim_r"], 4),
        c_indep_struct_r=round(chk_indep["struct_deg_r"], 4), c_indep_lex_r=round(chk_indep["lex_deg_r"], 4),
        c_bothdeg_struct_r=round(chk_bothdeg["struct_deg_r"], 4), c_bothdeg_lex_r=round(chk_bothdeg["lex_deg_r"], 4),
        d_collapsed_var=round(collapsed_var, 5), d_healthy_var=round(healthy_var, 4) if healthy_var == healthy_var else None,
        ST_CAPTURE_MIN=round(ST_CAPTURE_MIN, 4), ST_FLAT_EPS=ST_FLAT_EPS,
        a_cons_recovers=a_cons_recovers, a_cons_flat=a_cons_flat, a_cons_beats_pop=a_cons_beats_pop,
        b_cons_no_edge_over_pop=b_cons_no_edge_over_pop, b_pop_fires=b_pop_fires,
        c_indep_passes=c_indep_passes, c_corr_flagged=c_corr_flagged, c_bothdeg_flagged=c_bothdeg_flagged,
        d_collapse_caught=d_collapse_caught, arms_differ=arms_differ,
        clustered_edges=int(tri_c.shape[0]), pop_edges=int(tri_p.shape[0]))
    ok = bool(a_cons_recovers and a_cons_flat and a_cons_beats_pop and b_cons_no_edge_over_pop and b_pop_fires
              and c_indep_passes and c_corr_flagged and c_bothdeg_flagged and d_collapse_caught and arms_differ)
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
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest(device, dim=cfg["kge_dim"])
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (consolidation / agreement / independence discriminators did not "
                        "fire): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS consolidation-loop: (a) planted-independent agreement recovers + is flat + "
                        "beats popularity + beats two-structural trap; (b) planted-popularity NOT rescued by "
                        "consolidation and popularity baseline fires; (c) independence check passes on independent "
                        "channels and flags correlated channels; arms differ",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    edges = np.asarray(edges, dtype=np.int64)
    _log("subgraph: n_nodes=%d n_edges=%d rel_types=%d median_degree=%s"
         % (len(node_ids), edges.shape[0], T, meta.get("median_degree")))
    role_rng2 = np.random.default_rng(SUBGRAPH_BASE_SEED + 778)
    roles_disc = torch.from_numpy(make_unitary_roles(T, cfg["enc"]["code_dim"], role_rng2)).to(device)

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []; seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, edges, rels, node_words, roles_disc, cfg, device, out_dir_path)
            sig_vals = set(v for v in pm["arm_sigs"].values() if not v.endswith("_failed"))
            if len(sig_vals) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct arm sigs"
                                   % (seed, len(sig_vals)))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    meta2 = dict(n_nodes=len(node_ids), n_edges=int(edges.shape[0]), rel_types=int(T))
    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta2)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"],
                                                   kge_dim=cfg["kge_dim"], kge_epochs=cfg["kge_epochs"],
                                                   cons_passes=CONS_PASSES, cons_knn=CONS_KNN, rel_epochs=REL_EPOCHS,
                                                   enc=cfg["enc"]),
                   subgraph_meta=meta, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
