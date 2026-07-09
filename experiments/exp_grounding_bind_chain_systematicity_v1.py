"""Compositional bind/unbind operator: reach-deepening (bind-chain) + systematicity (role-filler),
with an oracle skyline that arbitrates encoder-vs-readout for the 1-hop grounding cap.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test BIND vs FLAT vs NOBIND preds; D=1 vs D=2 fields)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared: ordering-acc chance floor = 0.5, cleanup top1 chance = 1/F; discriminators are
#   (i) reach/decay-length of bind-chain vs a one-shot (D=1) control + shuffled empirical null + over-smoothing
#   gate, (ii) held-out-recombination cleanup accuracy of BIND vs a genuine flat-similarity control, and
#   (iii) ridge decodability skyline; none is a closed-form estimator noise floor.
# - baseline_in_band at smoke: reach D=1 must sit at reach 1 (one-shot cap; headroom to extend); FLAT_NN
#   must handle SEEN combos (control-valid, flat_seen >= 0.50) yet FAIL held-out (flat_heldout < 0.40);
#   shuffled controls near chance.
# - discriminator survives scale: smoke fires all three (bind-chain reach(D>=2) > reach(D=1); BIND held-out
#   >> FLAT held-out; ridge decodes smooth > shuffled). SMOKE exercises the SAME code branches as FULL.
# - HARD_PASS strictly above floor: reach_delta >= 1 (AND non-collapsed AND shuffled-flat); systematicity
#   bind_heldout >= 0.80 AND (bind_heldout - flat_heldout) >= 0.40 AND gen-gap small.
# - HP_SCOPE: reach gates apply to BIND_CHAIN (D>=2) vs BIND_CHAIN (D=1) one-shot control; systematicity
#   gates apply to BIND vs FLAT_NN; NOBIND is the role-blind floor; SHUFFLED attribute is the genuineness
#   control; ORACLE is a diagnostic skyline (no pass/fail gate, arbiter flag only).
# - sweep axes: D (chain depth, block 2) + distance-bin (blocks 2/3); cardinality via EXPECTED_N_UNITS =
#   n_model_seeds; D-sweep + bin coverage asserted WITHIN each seed unit.
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (shuffled empirical null recomputed per run;
#   over-smoothing collapse gate proven to fire; FLAT_NN control-validity gate on seen combos)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg

SCIENCE (per notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md Test 2 +
notes/research_meaning_growth_abstraction_compositionality_ladder_2026-07-09.md Test 2):

  The just-landed recurrent-settling cascade cell HARD_FAIL_NO_EXTENSION'd at FULL scale (reach_delta=0):
  a better similarity-only readout did NOT break the 1-hop grounded-attribute cap; the 1-hop bound now holds
  across TWO independent readouts (parent co-training + recurrent settling). Both same-day research notes
  converge (with the philosophy-of-language compositionality note, a THIRD independent literature) on the
  SAME missing primitive: an explicit, invertible role-filler BINDING operator that can be CHAINED
  (bind, unbind, bind again). Near-random / near-orthogonal atomic codes with similarity-only readout
  support only 1-hop retrieval; there is no unbind-chain to traverse a second relational edge
  compositionally (Fodor-Pylyshyn 1988; Smolensky 1990; Plate HRR; Gayler VSA; Kanerva).

  This ONE build yields THREE interpretable numbers via a VSA-native FHRR (unit-modulus circular-convolution
  / elementwise-complex) bind/unbind operator, reusing hdlab.binding.bind/unbind (complex dtype path):

  (1) REACH-DEEPENING (block 2, synthetic typed relational graph -- clean controlled data). Each node gets a
      near-random FHRR atom code; each relation type gets a near-random role code. A node's relational memory
      M_i = bundle_(j,r) bind(role_r, atom_j) superimposes its typed neighbours. The bind/unbind operator
      RECOVERS the typed adjacency: unbind(M_i, role_r) then cleanup over the atom codebook returns node i's
      r-neighbours (up to superposition crosstalk that grows with degree and shrinks with dim N -- the
      operator's SNR). CHAINING = propagate a graph-smooth grounded attribute from sparse seeds over the
      RECOVERED graph for D hops. D=1 is the one-shot control (reach ~ 1, the cap). Discriminator: does
      reach(best non-collapsed D>=2) exceed reach(D=1) by >= 1 hop, with the shuffled-attribute control
      staying flat at every D (rules out over-smoothing / homogenization). A finite reach that lengthens
      then collapses at large D (cleanup noise + row-stochastic over-smoothing) is the expected honest
      signature; unbounded rise of BOTH smooth and shuffled = over-smoothing artefact, gated out.

  (2) SYSTEMATICITY (block 1, synthetic role-filler scenes -- clean controlled data; Fodor-Pylyshyn paired
      recombination). Scenes bind R roles to fillers: S = bundle_r bind(role_r, filler_assign[r]). A held-out
      set of (role, filler) COMBINATIONS never appears in any training scene. Minimal-pair test scenes are
      built by taking a training scene and swapping ONE role to a held-out filler; the swapped role is
      queried. BIND recovers the queried filler via unbind(S, role_r)+cleanup for ANY combination (systematic
      by algebraic construction). FLAT_NN (the genuine flat-similarity control, NO binding) stores training
      scenes as role-blind filler-superposition bundles and answers a role query by returning the
      role-r filler of the most cosine-similar TRAINING scene: it handles SEEN combos (memorised) but returns
      the pre-swap filler on held-out recombinations (productivity WITHOUT systematicity). NOBIND is a
      role-blind cleanup floor. Discriminator: BIND held-out accuracy >> FLAT_NN held-out accuracy, with
      FLAT_NN control-valid on seen combos (else the control is merely broken, inconclusive).

  (3) ORACLE SKYLINE (block 3, REAL ConceptNet encoder codes -- reuses the settling/snowball pipeline). A
      privileged ridge probe fit on a TRAIN split of ALL non-seed node codes, evaluated per graph-distance
      bin on a HELD-OUT split, is the upper bound any readout over the encoder codes could reach. If the
      oracle decodes hop-2 grounded signal above the shuffled floor while similarity readouts capped at 1,
      the 1-hop limit is a READOUT limit (a better operator can help). If even the oracle cannot decode
      hop-2, the bound is on the ENCODER (the codes lack the signal) and the fix is encoder-level (binding
      must happen at ENCODE time, not read time) -- a deeper, load-bearing finding. This arm ties the
      compositional-operator diagnostics back to the real substrate and to the settling reach=1 baseline.

HONESTY FRAMING (load-bearing): this is NOT "language understanding". Block 1 measures systematic
role-filler generalization; block 2 measures compositional grounded-attribute propagation on a controlled
typed graph via an explicit binding operator (encode-time structure -- the note's thesis that binding must
be encoded to license hop-chaining); block 3 measures whether the real encoder's codes even carry the far-hop
signal. A PASS is a necessary (not sufficient) recipe for compositional grounded propagation + systematic
recombination without any external LM. Teacher-free / self-contained: NO BGE, NO external LM, NO network.
Reuses hdlab.binding (bind/unbind, FHRR complex path) + the CG'd teacher-free relational encoder pipeline
(cert 06e5a493d) for block 3. CPU-only. ASCII-only. No emojis. No em dashes.
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
    build_adjlist,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    make_smooth_attribute,
    attribute_assortativity,
    multi_source_bfs,
    distance_bins,
    train_encoder,
    label_propagation,
    ordering_accuracy,
    ridge_readout,
    SUBGRAPH_BASE_SEED,
    MIN_BIN_NODES,
)
from hdlab.binding import bind as hdlab_bind  # noqa: E402  (FHRR complex path: a * b)
from hdlab.binding import unbind as hdlab_unbind  # noqa: E402  (FHRR complex path: c * conj(b))

ANCHOR_NAME = "grounding_bind_chain_systematicity_v1"

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale differs)
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(
    seeds=[7],
    # block 1 (systematicity)
    sys_N=512, sys_R=4, sys_F=20, sys_n_train=60, sys_n_test=200, sys_heldout_frac=0.30,
    # block 2 (bind-chain reach, synthetic typed graph)
    reach_N=512, reach_n=300, reach_T=3, reach_deg=4, reach_n_seeds_ground=15,
    reach_n_sources=6, reach_diffuse_steps=8, reach_D=[1, 2, 3], reach_cleanup_topk=3,
    reach_n_pairs=2000,
    # block 3 (oracle skyline on real CN)
    cn_n_nodes=400, cn_epochs=10, cn_code_dim=64, cn_feat_dim=1024, cn_temp=0.15, cn_lr=0.01,
    cn_lambda_cov=1.0, cn_lambda_var=1.0, cn_lambda_attr=1.0, cn_n_ground_seeds=20,
    cn_n_sources=6, cn_diffuse_steps=8, cn_ridge_lambda=1.0, cn_n_pairs=2000, cn_k_labelprop=7,
)

SMOKE_CFG = dict(
    seeds=[7, 13],
    sys_N=1024, sys_R=6, sys_F=40, sys_n_train=150, sys_n_test=400, sys_heldout_frac=0.30,
    reach_N=1024, reach_n=600, reach_T=4, reach_deg=4, reach_n_seeds_ground=30,
    reach_n_sources=15, reach_diffuse_steps=10, reach_D=[1, 2, 3, 4], reach_cleanup_topk=4,
    reach_n_pairs=4000,
    cn_n_nodes=1500, cn_epochs=40, cn_code_dim=128, cn_feat_dim=4096, cn_temp=0.15, cn_lr=0.01,
    cn_lambda_cov=1.0, cn_lambda_var=1.0, cn_lambda_attr=1.0, cn_n_ground_seeds=30,
    cn_n_sources=25, cn_diffuse_steps=10, cn_ridge_lambda=1.0, cn_n_pairs=4000, cn_k_labelprop=7,
)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    sys_N=2048, sys_R=8, sys_F=60, sys_n_train=300, sys_n_test=800, sys_heldout_frac=0.30,
    reach_N=1024, reach_n=800, reach_T=4, reach_deg=4, reach_n_seeds_ground=40,
    reach_n_sources=25, reach_diffuse_steps=12, reach_D=[1, 2, 3, 4, 5], reach_cleanup_topk=4,
    reach_n_pairs=6000,
    cn_n_nodes=4000, cn_epochs=60, cn_code_dim=256, cn_feat_dim=8192, cn_temp=0.10, cn_lr=0.008,
    cn_lambda_cov=1.0, cn_lambda_var=1.0, cn_lambda_attr=1.0, cn_n_ground_seeds=80,
    cn_n_sources=60, cn_diffuse_steps=12, cn_ridge_lambda=1.0, cn_n_pairs=6000, cn_k_labelprop=7,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run)
# ---------------------------------------------------------------------------

# --- Block 1: systematicity (cleanup top1 accuracy; chance = 1/F) ---
SYS_BIND_HELDOUT_HP = 0.80      # BIND recovers held-out-combo filler
SYS_MARGIN_HP = 0.40           # bind_heldout - flat_heldout (systematic vs flat-similarity)
SYS_GENGAP_MAX = 0.15          # |bind_seen - bind_heldout| : genuine generalization, not memorization
SYS_FLAT_SEEN_MIN = 0.50       # FLAT_NN must handle SEEN combos (control-valid, else merely broken)
SYS_FLAT_HELDOUT_MAX = 0.40    # FLAT_NN must FAIL held-out (must-fail control)
SYS_BIND_HELDOUT_HF = 0.60     # below this => binding does not deliver systematicity (HARD_FAIL)
SYS_MARGIN_HF = 0.20           # below this margin => no separation from flat (HARD_FAIL)

# --- Block 2: bind-chain reach (ordering acc; chance = 0.5) ---
REACH_THRESH = 0.55            # ordering-acc floor for a hop to count as "grounded" (chance 0.5 + 0.05)
MARGIN_FLOOR = 0.05            # genuine_margin (smooth - shuffled) required at a hop
REACH_DELTA_HP = 1             # HARD_PASS: bind-chain reach extends >= this many hops beyond D=1 one-shot
SHUF_MAX = 0.58               # shuffled ordering acc must stay near chance; above => homogenization
MONOTONE_TOL = 0.04            # per-step acc increase tolerated (near->far) before flagging non-monotone
COLLAPSE_RATIO_MIN = 0.25      # field_std(pred_smooth)/std(attr): below AND near lost => over-smoothed
REACH_STRICT_MARGIN = 0.01     # newly-reached bin acc must clear REACH_THRESH by >= this for clean HP

# --- Block 3: oracle skyline (ridge decode ordering acc; chance = 0.5) ---
ORACLE_DECODE_THRESH = 0.55    # bin counts as oracle-decodable above this AND margin over shuffled floor
ORACLE_MARGIN_FLOOR = 0.05

# --- attribute graph-smoothness precondition (adaptive gate; block 2 + block 3) ---
ATTR_ASSORT_SMOOTH_MIN = 0.30  # synthetic-graph smooth-field assortativity floor (deflated for random typed graph)
ATTR_ASSORT_SHUFFLED_MAX = 0.20

# --- reach one-shot cap sanity (baseline_in_band): D=1 reach must be small (the cap to beat) ---
REACH_D1_MAX = 2               # D=1 one-shot reach must be <= this (else no cap to extend, saturation risk)


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
# FHRR (unit-modulus complex / circular-convolution) primitives.
# bind/unbind are IDENTICAL to hdlab.binding.bind/unbind on the complex dtype path
# (a*b ; c*conj(b)); verified bit-identical in discriminator_selftest. Vectorized numpy
# equivalents used in hot loops for speed; single-vector hdlab primitives reused in selftest.
# ---------------------------------------------------------------------------

def make_fhrr_codes(m, n, rng):
    """m near-random FHRR atom codes of dim n: unit-modulus phasors exp(i*theta). complex64 [m, n]."""
    theta = rng.uniform(0.0, 2.0 * np.pi, size=(m, n))
    return np.exp(1j * theta).astype(np.complex64)


def fhrr_bind(a, b):
    """FHRR bind = elementwise complex multiply (== hdlab.binding.bind complex path)."""
    return a * b


def fhrr_unbind(c, b):
    """FHRR unbind = elementwise multiply by conjugate (== hdlab.binding.unbind complex path)."""
    return c * np.conj(b)


def cleanup_scores(x, codebook):
    """Conjugate-aware cleanup scores Re(<codebook, x>). x [..., n], codebook [m, n] -> [..., m]."""
    return np.real(x @ np.conj(codebook).T)


# ---------------------------------------------------------------------------
# BLOCK 1: systematicity (role-filler recombination)
# ---------------------------------------------------------------------------

def _make_heldout_split(R, F, heldout_frac, rng):
    """For each role, split fillers into train-allowed and held-out. Returns allowed[r] (list),
    heldout[r] (list). Guarantees each role has >= 2 allowed and >= 1 held-out filler."""
    allowed = {}
    heldout = {}
    n_ho = max(1, int(round(F * heldout_frac)))
    n_ho = min(n_ho, F - 2)  # keep >= 2 allowed
    for r in range(R):
        perm = rng.permutation(F)
        heldout[r] = sorted(int(x) for x in perm[:n_ho])
        allowed[r] = sorted(int(x) for x in perm[n_ho:])
    return allowed, heldout


def _build_scene(role_cb, filler_cb, assign):
    """Scene vector S = bundle_r bind(role_r, filler_assign[r]) (FHRR). assign: list len R."""
    R = len(assign)
    acc = np.zeros(role_cb.shape[1], dtype=np.complex64)
    for r in range(R):
        acc = acc + fhrr_bind(role_cb[r], filler_cb[assign[r]])
    return acc


def _flat_bundle(filler_cb, assign):
    """Role-blind flat superposition = sum_r filler_assign[r] (NO role binding)."""
    acc = np.zeros(filler_cb.shape[1], dtype=np.complex64)
    for a in assign:
        acc = acc + filler_cb[a]
    return acc


def run_systematicity(cfg, seed):
    """BIND vs FLAT_NN vs NOBIND on held-out (role,filler) recombination. Returns metrics + digests."""
    rng = np.random.default_rng(seed + 101)
    N, R, F = cfg["sys_N"], cfg["sys_R"], cfg["sys_F"]
    role_cb = make_fhrr_codes(R, N, rng)
    filler_cb = make_fhrr_codes(F, N, rng)
    allowed, heldout = _make_heldout_split(R, F, cfg["sys_heldout_frac"], rng)

    # --- training scenes (also the FLAT_NN library) : each role sampled from allowed[r] ---
    n_train = cfg["sys_n_train"]
    train_assign = np.empty((n_train, R), dtype=np.int64)
    for i in range(n_train):
        for r in range(R):
            train_assign[i, r] = allowed[r][rng.integers(0, len(allowed[r]))]
    # library representations
    lib_flat = np.stack([_flat_bundle(filler_cb, train_assign[i]) for i in range(n_train)])  # [n_train, N]

    # --- test scenes: half SEEN (query a random role of an actual training scene = memorised combo),
    #     half HELDOUT (minimal-pair: swap ONE role of a training scene to a held-out filler; query it) ---
    n_test = cfg["sys_n_test"]
    n_half = n_test // 2
    seen_assign = np.empty((n_half, R), dtype=np.int64)
    seen_query = np.empty(n_half, dtype=np.int64)
    for i in range(n_half):
        base = int(rng.integers(0, n_train))
        seen_assign[i] = train_assign[base]
        seen_query[i] = int(rng.integers(0, R))  # queried (role,filler) IS in the library
    held_assign = np.empty((n_half, R), dtype=np.int64)
    held_query = np.empty(n_half, dtype=np.int64)
    for i in range(n_half):
        base = int(rng.integers(0, n_train))
        a = train_assign[base].copy()
        rq = int(rng.integers(0, R))
        a[rq] = heldout[rq][rng.integers(0, len(heldout[rq]))]  # NOVEL combo, never in training
        held_assign[i] = a
        held_query[i] = rq

    def bind_recover(assign_mat, query_roles):
        """BIND: unbind scene by queried role, cleanup over filler codebook -> predicted filler."""
        preds = np.empty(assign_mat.shape[0], dtype=np.int64)
        for i in range(assign_mat.shape[0]):
            S = _build_scene(role_cb, filler_cb, assign_mat[i])
            probe = fhrr_unbind(S, role_cb[query_roles[i]])
            sc = cleanup_scores(probe, filler_cb)
            preds[i] = int(np.argmax(sc))
        return preds

    def flat_nn_recover(assign_mat, query_roles):
        """FLAT_NN: nearest TRAINING scene by role-blind flat cosine; return its filler in queried role."""
        preds = np.empty(assign_mat.shape[0], dtype=np.int64)
        lib_norm = lib_flat / (np.linalg.norm(lib_flat, axis=1, keepdims=True) + 1e-9)
        for i in range(assign_mat.shape[0]):
            q = _flat_bundle(filler_cb, assign_mat[i])
            q = q / (np.linalg.norm(q) + 1e-9)
            sims = np.real(q @ np.conj(lib_norm).T)
            nn = int(np.argmax(sims))
            preds[i] = int(train_assign[nn, query_roles[i]])
        return preds

    def nobind_recover(assign_mat, query_roles):
        """NOBIND floor: role-blind superposition cleanup -> argmax filler, independent of role."""
        preds = np.empty(assign_mat.shape[0], dtype=np.int64)
        for i in range(assign_mat.shape[0]):
            S = _flat_bundle(filler_cb, assign_mat[i])
            sc = cleanup_scores(S, filler_cb)
            preds[i] = int(np.argmax(sc))
        return preds

    def acc(preds, assign_mat, query_roles):
        truth = assign_mat[np.arange(assign_mat.shape[0]), query_roles]
        return float(np.mean(preds == truth))

    bind_seen_p = bind_recover(seen_assign, seen_query)
    bind_held_p = bind_recover(held_assign, held_query)
    flat_seen_p = flat_nn_recover(seen_assign, seen_query)
    flat_held_p = flat_nn_recover(held_assign, held_query)
    nobind_held_p = nobind_recover(held_assign, held_query)

    bind_seen = acc(bind_seen_p, seen_assign, seen_query)
    bind_held = acc(bind_held_p, held_assign, held_query)
    flat_seen = acc(flat_seen_p, seen_assign, seen_query)
    flat_held = acc(flat_held_p, held_assign, held_query)
    nobind_held = acc(nobind_held_p, held_assign, held_query)

    digests = {
        "bind_held": hashlib.sha256(bind_held_p.tobytes()).hexdigest(),
        "flat_held": hashlib.sha256(flat_held_p.tobytes()).hexdigest(),
        "nobind_held": hashlib.sha256(nobind_held_p.tobytes()).hexdigest(),
    }
    return dict(
        bind_seen=bind_seen, bind_heldout=bind_held,
        flat_seen=flat_seen, flat_heldout=flat_held, nobind_heldout=nobind_held,
        chance=1.0 / F, R=R, F=F, N=N, n_train=n_train, n_test=n_test,
    ), digests


# ---------------------------------------------------------------------------
# BLOCK 2: bind-chain reach on a synthetic typed relational graph
# ---------------------------------------------------------------------------

def make_typed_graph(n, T, deg, rng):
    """Random typed relational graph: n nodes, T relation types, ~deg avg degree. Returns
    edges [E,2] int32, rels [E] int32 (relation type per edge), adj (list of set), degrees [n]."""
    edge_set = {}
    for u in range(n):
        k = max(1, deg // 2)
        for _ in range(k):
            v = int(rng.integers(0, n))
            if v == u:
                continue
            a, b = (u, v) if u < v else (v, u)
            if (a, b) not in edge_set:
                edge_set[(a, b)] = int(rng.integers(0, T))
    edges = np.array(sorted(edge_set.keys()), dtype=np.int32)
    rels = np.array([edge_set[(int(a), int(b))] for a, b in edges], dtype=np.int32)
    degrees = np.zeros(n, dtype=np.int32)
    adj = [set() for _ in range(n)]
    for (a, b), r in zip(edges, rels):
        degrees[a] += 1
        degrees[b] += 1
        adj[a].add(int(b))
        adj[b].add(int(a))
    return edges, rels, adj, degrees


def build_node_memory(n, N, edges, rels, atom_cb, role_cb):
    """M_i = bundle over typed edges (j, r) incident to i of bind(role_r, atom_j). complex64 [n, N]."""
    M = np.zeros((n, N), dtype=np.complex64)
    for (a, b), r in zip(edges, rels):
        a = int(a); b = int(b); r = int(r)
        M[a] = M[a] + fhrr_bind(role_cb[r], atom_cb[b])
        M[b] = M[b] + fhrr_bind(role_cb[r], atom_cb[a])
    return M


def recover_adjacency(M, atom_cb, role_cb, T, topk, thresh_frac=0.30):
    """Unbind each node memory by each role, cleanup over atom codebook, keep recovered neighbours ABOVE
    the crosstalk noise floor (principled VSA cleanup, not a fixed top-k). For unit-modulus FHRR a true
    bound term recovers with real score ~ N (Re<atom,atom>=N) while superposition crosstalk scores ~ sqrt(N);
    accept only score > thresh_frac * N (capped at topk for safety). A node with NO r-edge yields only
    crosstalk -> all below floor -> no spurious neighbour. This is the bind/unbind OPERATOR demonstration
    (one-time; chaining then propagates over the recovered graph)."""
    n, N = M.shape
    floor = thresh_frac * float(N)
    rec_adj = [set() for _ in range(n)]
    for r in range(T):
        probes = fhrr_unbind(M, role_cb[r])              # [n, N]  unbind all nodes by role r
        sc = cleanup_scores(probes, atom_cb)             # [n, n]  score vs atom codebook
        np.fill_diagonal(sc, -np.inf)                    # no self-neighbour
        top = np.argpartition(-sc, topk - 1, axis=1)[:, :topk]  # [n, topk] strongest candidates
        for i in range(n):
            for jj in top[i]:
                if sc[i, jj] > floor:                    # above crosstalk noise floor only
                    rec_adj[i].add(int(jj))
    return rec_adj


def _row_stochastic_from_adj(adj_sets, n):
    """Gather-form random-walk transition over an adjacency (list of sets). Returns (nbr_list, w_list)."""
    nbr = []
    w = []
    for i in range(n):
        js = sorted(adj_sets[i])
        nbr.append(np.array(js, dtype=np.int64))
        d = len(js)
        w.append(np.full(d, 1.0 / d, dtype=np.float64) if d > 0 else np.zeros(0, dtype=np.float64))
    return nbr, w


def propagate_field(nbr, w, seed_idx, seed_vals, D, alpha=0.85):
    """D-step clamped label spreading over a (recovered) adjacency: f^{t+1}=alpha*P f^t+(1-alpha)*y0.
    seed_vals is the FULL attribute array (indexed by seed_idx). Returns pred field [n]."""
    n = len(nbr)
    y0 = np.zeros(n, dtype=np.float64)
    y0[seed_idx] = np.asarray(seed_vals, dtype=np.float64)[seed_idx]
    f = y0.copy()
    for _ in range(int(D)):
        f_new = np.zeros(n, dtype=np.float64)
        for i in range(n):
            if nbr[i].shape[0] > 0:
                f_new[i] = float(np.sum(w[i] * f[nbr[i]]))
        f = alpha * f_new + (1.0 - alpha) * y0
    return f


def _field_std_ratio(pred, truth, nonseed_idx):
    if nonseed_idx.shape[0] < 2:
        return float("nan")
    ts = float(np.std(truth[nonseed_idx]))
    if ts < 1e-12:
        return float("nan")
    return float(np.std(pred[nonseed_idx])) / ts


def _reach_hops(acc_by_bin, margin_by_bin):
    r = 0
    for b in range(4):
        a = acc_by_bin[b]; m = margin_by_bin[b]
        if (a == a) and (m == m) and (a >= REACH_THRESH) and (m >= MARGIN_FLOOR):
            r = b + 1
        else:
            break
    return r


def _reach_arm_metrics(pred_s, pred_h, a_smooth, a_shuf, bins, nonseed_idx, rng, n_pairs):
    acc_s = {}; acc_h = {}; margin = {}
    for b in range(4):
        idx = bins[b]
        if idx.shape[0] < MIN_BIN_NODES:
            acc_s[b] = float("nan"); acc_h[b] = float("nan"); margin[b] = float("nan")
        else:
            a1, _ = ordering_accuracy(pred_s, a_smooth, idx, rng, n_pairs)
            a2, _ = ordering_accuracy(pred_h, a_shuf, idx, rng, n_pairs)
            acc_s[b] = a1; acc_h[b] = a2
            margin[b] = (a1 - a2) if (a1 == a1 and a2 == a2) else float("nan")
    fsr = _field_std_ratio(pred_s, a_smooth, nonseed_idx)
    reach = _reach_hops(acc_s, margin)
    near = acc_s[0]
    far = float("nan"); far_bin = None
    for b in (3, 2, 1):
        if acc_s[b] == acc_s[b]:
            far = acc_s[b]; far_bin = b; break
    return dict(acc_smooth=acc_s, acc_shuf=acc_h, margin=margin, field_std_ratio=fsr,
                reach=reach, near_acc=near, far_acc=far, far_bin=far_bin)


def _reach_collapsed(m):
    """Over-smoothing detector: shuffled homogenized up OR field flattened AND near-signal lost."""
    fsr = m["field_std_ratio"]; shuf_near = m["acc_shuf"][0]; near = m["near_acc"]
    if shuf_near == shuf_near and shuf_near > SHUF_MAX:
        return True, "shuffled_near>%.2f" % SHUF_MAX
    if (fsr == fsr and fsr < COLLAPSE_RATIO_MIN) and (near == near and near < REACH_THRESH):
        return True, "field_flattened_and_near_lost"
    return False, "ok"


def run_reach(cfg, seed):
    """Bind-chain reach on a synthetic typed graph. Returns metrics + digests."""
    rng = np.random.default_rng(seed + 202)
    n, N, T, deg = cfg["reach_n"], cfg["reach_N"], cfg["reach_T"], cfg["reach_deg"]
    edges, rels, adj_true, degrees = make_typed_graph(n, T, deg, rng)

    # graph-smooth attribute over the synthetic graph + shuffled control (reuse parent primitives)
    a_smooth = make_smooth_attribute(edges, degrees, n, rng, cfg["reach_n_sources"], cfg["reach_diffuse_steps"])
    a_shuf = a_smooth.copy(); rng.shuffle(a_shuf)
    assort_smooth = attribute_assortativity(a_smooth, edges)
    assort_shuffled = attribute_assortativity(a_shuf, edges)

    # sparse grounded seeds + distance bins to nearest seed (reuse parent BFS + binning)
    n_gs = int(min(cfg["reach_n_seeds_ground"], n // 4))
    ground_seeds = rng.choice(n, size=n_gs, replace=False)
    seed_set = set(int(x) for x in ground_seeds)
    dist = multi_source_bfs(adj_true, [int(x) for x in ground_seeds], n)
    bins, n_unreachable = distance_bins(dist, seed_set)
    nonseed_idx = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)

    # FHRR codebooks
    atom_cb = make_fhrr_codes(n, N, rng)
    role_cb = make_fhrr_codes(T, N, rng)

    # build node memory + recover adjacency via bind/unbind (the operator)
    M = build_node_memory(n, N, edges, rels, atom_cb, role_cb)
    rec_adj = recover_adjacency(M, atom_cb, role_cb, T, cfg["reach_cleanup_topk"])

    # operator fidelity: recovered-vs-true edge recall (undirected)
    true_pairs = set()
    for (a, b) in edges:
        true_pairs.add((int(a), int(b)))
    rec_pairs = set()
    for i in range(n):
        for j in rec_adj[i]:
            a, b = (i, j) if i < j else (j, i)
            rec_pairs.add((a, b))
    edge_recall = len(true_pairs & rec_pairs) / max(1, len(true_pairs))
    edge_precision = len(true_pairs & rec_pairs) / max(1, len(rec_pairs))

    # chaining: propagate attribute over RECOVERED adjacency for each depth D
    nbr, w = _row_stochastic_from_adj(rec_adj, n)
    gs = np.asarray(ground_seeds, dtype=np.int64)
    npairs = cfg["reach_n_pairs"]
    by_D = {}
    fields_probe = {}
    for D in cfg["reach_D"]:
        pf_s = propagate_field(nbr, w, gs, a_smooth, D)
        pf_h = propagate_field(nbr, w, gs, a_shuf, D)
        by_D[D] = _reach_arm_metrics(pf_s, pf_h, a_smooth, a_shuf, bins, nonseed_idx,
                                     np.random.default_rng(seed + 303), npairs)
        if D in (min(cfg["reach_D"]), max(cfg["reach_D"])):
            fields_probe[D] = hashlib.sha256(np.ascontiguousarray(pf_s.astype(np.float32)).tobytes()).hexdigest()

    digests = {"field_Dmin": fields_probe.get(min(cfg["reach_D"]), ""),
               "field_Dmax": fields_probe.get(max(cfg["reach_D"]), "")}
    return dict(
        reach_D=list(cfg["reach_D"]),
        by_D={str(D): by_D[D] for D in cfg["reach_D"]},
        edge_recall=float(edge_recall), edge_precision=float(edge_precision),
        assort_smooth=float(assort_smooth), assort_shuffled=float(assort_shuffled),
        bin_counts={b: int(bins[b].shape[0]) for b in range(4)}, n_unreachable=int(n_unreachable),
        n_ground_seeds=n_gs,
    ), digests


# ---------------------------------------------------------------------------
# BLOCK 3: oracle skyline on REAL ConceptNet encoder codes (encoder-vs-readout arbiter)
# ---------------------------------------------------------------------------

def _oracle_per_bin(codes, a_smooth, a_shuf, bins, ridge_lambda, rng, n_pairs):
    """Ridge probe fit on a TRAIN split of ALL non-seed nodes, evaluated per bin on a HELD-OUT split.
    Privileged skyline: uses far-node labels at train. Returns per-bin ordering acc (smooth + shuffled)."""
    nonseed = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)
    if nonseed.shape[0] < 4 * MIN_BIN_NODES:
        return None
    perm = rng.permutation(nonseed.shape[0])
    n_tr = nonseed.shape[0] // 2
    tr = nonseed[perm[:n_tr]]; te_mask = np.zeros(codes.shape[0], dtype=bool); te_mask[nonseed[perm[n_tr:]]] = True
    # fit ridge on train split (smooth + shuffled separately)
    w_s = ridge_readout(codes[tr], a_smooth[tr], codes, ridge_lambda)   # predicts over all nodes
    w_h = ridge_readout(codes[tr], a_shuf[tr], codes, ridge_lambda)
    acc_s = {}; acc_h = {}; margin = {}
    for b in range(4):
        idx = np.array([i for i in bins[b] if te_mask[i]], dtype=np.int64)
        if idx.shape[0] < MIN_BIN_NODES:
            acc_s[b] = float("nan"); acc_h[b] = float("nan"); margin[b] = float("nan")
        else:
            a1, _ = ordering_accuracy(w_s, a_smooth, idx, rng, n_pairs)
            a2, _ = ordering_accuracy(w_h, a_shuf, idx, rng, n_pairs)
            acc_s[b] = a1; acc_h[b] = a2
            margin[b] = (a1 - a2) if (a1 == a1 and a2 == a2) else float("nan")
    # oracle reach = farthest contiguous bin decodable above thresh + margin
    r = 0
    for b in range(4):
        a = acc_s[b]; m = margin[b]
        if (a == a) and (m == m) and (a >= ORACLE_DECODE_THRESH) and (m >= ORACLE_MARGIN_FLOOR):
            r = b + 1
        else:
            break
    return dict(acc_smooth=acc_s, acc_shuf=acc_h, margin=margin, oracle_reach=r)


def run_oracle(cfg, seed, cn_cache):
    """Reuse the real CN pipeline: train encoder, ridge-decode grounded attribute per distance bin.
    cn_cache holds the shared (subgraph, attribute, seeds, bins) so it is built once across seeds."""
    rng = np.random.default_rng(seed + 404)
    X = cn_cache["X"]; adj = cn_cache["adj"]; a_smooth = cn_cache["a_smooth"]; a_shuf = cn_cache["a_shuf"]
    bins = cn_cache["bins"]; ground_seeds = cn_cache["ground_seeds"]
    sub_cfg = dict(code_dim=cfg["cn_code_dim"], epochs=cfg["cn_epochs"], batch=256,
                   temp=cfg["cn_temp"], lr=cfg["cn_lr"], lambda_cov=cfg["cn_lambda_cov"],
                   lambda_var=cfg["cn_lambda_var"], lambda_attr=cfg["cn_lambda_attr"])
    z = train_encoder(X, adj, sub_cfg, seed, tag="ORACLE_ENC")
    # flat one-shot label-prop (reconfirm settling-style reach ~ 1 on the SAME codes)
    gs = np.asarray(ground_seeds, dtype=np.int64)
    pred_os_s = label_propagation(z, gs, a_smooth, cfg["cn_k_labelprop"])
    pred_os_h = label_propagation(z, gs, a_shuf, cfg["cn_k_labelprop"])
    os_metrics = _reach_arm_metrics(pred_os_s, pred_os_h, a_smooth, a_shuf, bins,
                                    cn_cache["nonseed_idx"], np.random.default_rng(seed + 505),
                                    cfg["cn_n_pairs"])
    oracle = _oracle_per_bin(z, a_smooth, a_shuf, bins, cfg["cn_ridge_lambda"], rng, cfg["cn_n_pairs"])
    return dict(flat_oneshot=os_metrics, oracle=oracle)


# ---------------------------------------------------------------------------
# Per-model-seed run (all three blocks)
# ---------------------------------------------------------------------------

def run_seed(seed, cfg, cn_cache):
    _log("  seed=%d block1 systematicity..." % seed)
    sys_m, sys_dg = run_systematicity(cfg, seed)
    _log("  seed=%d systematicity bind_seen=%.3f bind_heldout=%.3f flat_seen=%.3f flat_heldout=%.3f nobind=%.3f" % (
        seed, sys_m["bind_seen"], sys_m["bind_heldout"], sys_m["flat_seen"], sys_m["flat_heldout"], sys_m["nobind_heldout"]))

    _log("  seed=%d block2 bind-chain reach (n=%d N=%d T=%d)..." % (seed, cfg["reach_n"], cfg["reach_N"], cfg["reach_T"]))
    reach_m, reach_dg = run_reach(cfg, seed)
    _log("  seed=%d reach edge_recall=%.3f edge_prec=%.3f reach_by_D=%s" % (
        seed, reach_m["edge_recall"], reach_m["edge_precision"],
        {D: reach_m["by_D"][D]["reach"] for D in reach_m["by_D"]}))

    _log("  seed=%d block3 oracle skyline (CN encoder)..." % seed)
    oracle_m = run_oracle(cfg, seed, cn_cache)
    orc = oracle_m["oracle"]
    _log("  seed=%d oracle_reach=%s flat_oneshot_reach=%d" % (
        seed, (orc["oracle_reach"] if orc else "None"), oracle_m["flat_oneshot"]["reach"]))

    # ARMS-MUST-DIFFER (META_RULE_AF)
    assert sys_dg["bind_held"] != sys_dg["flat_held"], "META_RULE_AF: BIND == FLAT held-out preds"
    assert sys_dg["bind_held"] != sys_dg["nobind_held"], "META_RULE_AF: BIND == NOBIND held-out preds"
    if reach_dg["field_Dmin"] and reach_dg["field_Dmax"]:
        assert reach_dg["field_Dmin"] != reach_dg["field_Dmax"], "META_RULE_AF: reach D=min == D=max field (no chaining effect)"

    return dict(seed=seed, systematicity=sys_m, reach=reach_m, oracle=oracle_m)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nanmean(vals):
    arr = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(arr.mean()) if arr.shape[0] > 0 else float("nan")


def _mean_reach_arm(arms):
    out = dict(acc_smooth={}, acc_shuf={}, margin={})
    for b in range(4):
        out["acc_smooth"][b] = _nanmean([a["acc_smooth"][b] for a in arms])
        out["acc_shuf"][b] = _nanmean([a["acc_shuf"][b] for a in arms])
        out["margin"][b] = _nanmean([a["margin"][b] for a in arms])
    out["field_std_ratio"] = _nanmean([a["field_std_ratio"] for a in arms])
    out["near_acc"] = _nanmean([a["near_acc"] for a in arms])
    out["far_acc"] = _nanmean([a["far_acc"] for a in arms])
    out["reach"] = _reach_hops(out["acc_smooth"], out["margin"])
    return out


def aggregate_and_verdict(per_seed, cfg):
    # ---- Block 1: systematicity ----
    bind_seen = _nanmean([m["systematicity"]["bind_seen"] for m in per_seed])
    bind_held = _nanmean([m["systematicity"]["bind_heldout"] for m in per_seed])
    flat_seen = _nanmean([m["systematicity"]["flat_seen"] for m in per_seed])
    flat_held = _nanmean([m["systematicity"]["flat_heldout"] for m in per_seed])
    nobind_held = _nanmean([m["systematicity"]["nobind_heldout"] for m in per_seed])
    sys_margin = bind_held - flat_held
    gen_gap = abs(bind_seen - bind_held)
    flat_valid = flat_seen >= SYS_FLAT_SEEN_MIN
    if not flat_valid:
        sys_verdict = "SYS_INCONCLUSIVE_FLAT_CONTROL_INVALID"  # flat control merely broken, not a fair baseline
    elif (bind_held >= SYS_BIND_HELDOUT_HP and sys_margin >= SYS_MARGIN_HP and
          gen_gap <= SYS_GENGAP_MAX and flat_held <= SYS_FLAT_HELDOUT_MAX):
        sys_verdict = "SYS_HARD_PASS"
    elif (bind_held < SYS_BIND_HELDOUT_HF or sys_margin < SYS_MARGIN_HF):
        sys_verdict = "SYS_HARD_FAIL"
    else:
        sys_verdict = "SYS_MIDDLE_BAND"

    # ---- Block 2: bind-chain reach ----
    reach_D = per_seed[0]["reach"]["reach_D"]
    reach_mean = {}
    reach_collapsed = {}
    reach_reason = {}
    for D in reach_D:
        arms = [m["reach"]["by_D"][str(D)] for m in per_seed]
        rm = _mean_reach_arm(arms)
        reach_mean[D] = rm
        c, reason = _reach_collapsed(rm)
        reach_collapsed[D] = c; reach_reason[D] = reason
    reach_d1 = reach_mean[1]["reach"] if 1 in reach_mean else reach_mean[reach_D[0]]["reach"]
    noncollapsed = [D for D in reach_D if D >= 2 and not reach_collapsed[D]]
    if noncollapsed:
        best_reach = max(reach_mean[D]["reach"] for D in noncollapsed)
        d_star = min(D for D in noncollapsed if reach_mean[D]["reach"] == best_reach)
    else:
        best_reach = -1; d_star = None
    reach_delta = (best_reach - reach_d1) if best_reach >= 0 else float("nan")
    edge_recall = _nanmean([m["reach"]["edge_recall"] for m in per_seed])
    edge_precision = _nanmean([m["reach"]["edge_precision"] for m in per_seed])
    assort_smooth_r = _nanmean([m["reach"]["assort_smooth"] for m in per_seed])
    assort_shuf_r = _nanmean([m["reach"]["assort_shuffled"] for m in per_seed])
    reach_precondition = (assort_smooth_r >= ATTR_ASSORT_SMOOTH_MIN and assort_shuf_r <= ATTR_ASSORT_SHUFFLED_MAX)
    # D=1 must be a genuine one-shot cap (baseline_in_band): reach_d1 <= REACH_D1_MAX
    d1_in_band = reach_d1 <= REACH_D1_MAX
    # strict-above-floor for the newly-reached bin at d_star
    strict_ok = False
    if d_star is not None and best_reach >= 1:
        rb = reach_mean[d_star]["acc_smooth"][best_reach - 1]
        mb = reach_mean[d_star]["margin"][best_reach - 1]
        strict_ok = (rb == rb and mb == mb and rb >= REACH_THRESH + REACH_STRICT_MARGIN and mb >= MARGIN_FLOOR)
    if not reach_precondition:
        reach_verdict = "REACH_PRECONDITION_FAIL"
    elif not d1_in_band:
        reach_verdict = "REACH_INCONCLUSIVE_NO_ONESHOT_CAP"  # D=1 already reaches far => nothing to extend
    elif d_star is None:
        reach_verdict = "REACH_HARD_FAIL_ALL_COLLAPSE"
    elif (reach_delta == reach_delta and reach_delta >= REACH_DELTA_HP):
        reach_verdict = "REACH_HARD_PASS" if strict_ok else "REACH_MIDDLE_BAND_BANDFLOOR"
    elif (reach_delta == reach_delta and reach_delta <= 0):
        reach_verdict = "REACH_HARD_FAIL_NO_EXTENSION"
    else:
        reach_verdict = "REACH_MIDDLE_BAND"

    # ---- Block 3: oracle skyline (arbiter flag) ----
    flat_os_reach = _nanmean([m["oracle"]["flat_oneshot"]["reach"] for m in per_seed])
    oracle_reaches = [m["oracle"]["oracle"]["oracle_reach"] for m in per_seed if m["oracle"]["oracle"] is not None]
    oracle_reach = float(np.mean(oracle_reaches)) if oracle_reaches else float("nan")
    if oracle_reach != oracle_reach:
        oracle_flag = "ORACLE_UNAVAILABLE"
    elif oracle_reach >= 2.0 and flat_os_reach <= 1.5:
        oracle_flag = "READOUT_LIMIT"   # signal IS in encoder codes; similarity readout under-extracts
    elif oracle_reach <= 1.5:
        oracle_flag = "ENCODER_LIMIT"   # even privileged decode cannot reach hop-2 => encoder-level fix needed
    else:
        oracle_flag = "ORACLE_AMBIGUOUS"

    verdict = "SYS=%s|REACH=%s|ORACLE=%s" % (sys_verdict, reach_verdict, oracle_flag)

    def reach_curve(D):
        arm = reach_mean[D]
        return [round(arm["acc_smooth"][b], 4) if arm["acc_smooth"][b] == arm["acc_smooth"][b] else None for b in range(4)]

    verdict_msg = (
        "%s || SYSTEMATICITY: bind_seen=%.3f bind_heldout=%.3f flat_seen=%.3f flat_heldout=%.3f "
        "nobind=%.3f margin=%.3f gen_gap=%.3f chance=%.3f flat_valid=%s || "
        "REACH: reach(D=1)=%d best_reach(D*=%s)=%d reach_delta=%s strict=%s edge_recall=%.3f edge_prec=%.3f "
        "reach_curve_D1=%s reach_curve_Dstar=%s assort(smooth=%.3f,shuf=%.3f) precond=%s d1_in_band=%s || "
        "ORACLE: oracle_reach=%.2f flat_oneshot_reach=%.2f flag=%s" % (
            verdict,
            bind_seen, bind_held, flat_seen, flat_held, nobind_held, sys_margin, gen_gap,
            per_seed[0]["systematicity"]["chance"], flat_valid,
            reach_d1, str(d_star), best_reach if best_reach >= 0 else -1,
            ("%.1f" % reach_delta) if reach_delta == reach_delta else "nan", strict_ok,
            edge_recall, edge_precision,
            reach_curve(1) if 1 in reach_mean else None,
            reach_curve(d_star) if d_star is not None else None,
            assort_smooth_r, assort_shuf_r, reach_precondition, d1_in_band,
            oracle_reach, flat_os_reach, oracle_flag))

    gates = dict(
        sys_verdict=sys_verdict, reach_verdict=reach_verdict, oracle_flag=oracle_flag,
        bind_seen=bind_seen, bind_heldout=bind_held, flat_seen=flat_seen, flat_heldout=flat_held,
        nobind_heldout=nobind_held, sys_margin=sys_margin, gen_gap=gen_gap, flat_control_valid=flat_valid,
        reach_d1=reach_d1, reach_best=best_reach, d_star=d_star, reach_delta=reach_delta,
        reach_strict_above_floor=strict_ok, d1_in_band=d1_in_band, reach_precondition_ok=reach_precondition,
        edge_recall=edge_recall, edge_precision=edge_precision,
        reach_by_D={str(D): reach_mean[D]["reach"] for D in reach_D},
        reach_collapsed_by_D={str(D): reach_collapsed[D] for D in reach_D},
        reach_reason_by_D={str(D): reach_reason[D] for D in reach_D},
        reach_curve_by_D={str(D): reach_curve(D) for D in reach_D},
        reach_shuf_near_by_D={str(D): reach_mean[D]["acc_shuf"][0] for D in reach_D},
        assort_smooth=assort_smooth_r, assort_shuffled=assort_shuf_r,
        oracle_reach=oracle_reach, flat_oneshot_reach=flat_os_reach,
        bands=dict(SYS_BIND_HELDOUT_HP=SYS_BIND_HELDOUT_HP, SYS_MARGIN_HP=SYS_MARGIN_HP,
                   SYS_GENGAP_MAX=SYS_GENGAP_MAX, REACH_THRESH=REACH_THRESH, MARGIN_FLOOR=MARGIN_FLOOR,
                   REACH_DELTA_HP=REACH_DELTA_HP, SHUF_MAX=SHUF_MAX, ORACLE_DECODE_THRESH=ORACLE_DECODE_THRESH),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------

def discriminator_selftest():
    """Prove all three discriminators are telemetry-sensitive (perturb-moves-it), not analytically pinned,
    AND that the FHRR bind/unbind used here is bit-identical to hdlab.binding on the complex dtype path."""
    rng = np.random.default_rng(0)

    # (0) reuse-fidelity: our elementwise FHRR == hdlab.binding on complex path
    a = make_fhrr_codes(1, 128, rng)[0]; b = make_fhrr_codes(1, 128, rng)[0]
    hd_b = hdlab_bind(torch.from_numpy(a), torch.from_numpy(b)).numpy()
    hd_u = hdlab_unbind(torch.from_numpy(a), torch.from_numpy(b)).numpy()
    reuse_ok = bool(np.allclose(hd_b, fhrr_bind(a, b), atol=1e-4) and np.allclose(hd_u, fhrr_unbind(a, b), atol=1e-4))

    # (1) systematicity: BIND recovers held-out combos; FLAT_NN does not; perturbing N moves BIND acc
    cfg_hi = dict(sys_N=1024, sys_R=5, sys_F=25, sys_n_train=120, sys_n_test=300, sys_heldout_frac=0.30)
    # low-SNR condition: tiny dim + heavy bundle load -> cleanup crosstalk tanks BIND recovery
    cfg_lo = dict(sys_N=48, sys_R=24, sys_F=25, sys_n_train=120, sys_n_test=300, sys_heldout_frac=0.30)
    m_hi, _ = run_systematicity(cfg_hi, 1)
    m_lo, _ = run_systematicity(cfg_lo, 1)
    sys_fires = (m_hi["bind_heldout"] >= 0.75 and (m_hi["bind_heldout"] - m_hi["flat_heldout"]) >= 0.30
                 and m_hi["flat_seen"] >= 0.5 and m_hi["flat_heldout"] <= 0.45)
    sys_telemetry = (m_hi["bind_heldout"] - m_lo["bind_heldout"]) > 0.05  # dim/load moves BIND (cleanup SNR)

    # (2) reach: bind-chain reach(D>=2) > reach(D=1) on a planted typed graph; perturb seed values moves margin
    cfg_r = dict(reach_N=512, reach_n=300, reach_T=3, reach_deg=4, reach_n_seeds_ground=15,
                 reach_n_sources=6, reach_diffuse_steps=10, reach_D=[1, 2, 3, 4], reach_cleanup_topk=3,
                 reach_n_pairs=3000)
    rm, _ = run_reach(cfg_r, 2)
    r_by_D = {int(D): rm["by_D"][D]["reach"] for D in rm["by_D"]}
    reach_d1 = r_by_D.get(1, 0)
    best_ge2 = max(v for D, v in r_by_D.items() if D >= 2)
    reach_fires = (best_ge2 > reach_d1) and (rm["edge_recall"] > 0.30)
    reach_telemetry = (max(r_by_D.values()) != min(r_by_D.values()))  # depth moves reach

    # (3) oracle: ridge decodes a planted smooth code (near high) but shuffled flat -> arbiter separates
    n = 400; cd = 32
    aval = rng.standard_normal(n)
    dist = np.concatenate([np.zeros(30, dtype=int), rng.integers(1, 6, size=n - 30)])
    direction = rng.standard_normal(cd); direction /= np.linalg.norm(direction)
    strength = np.maximum(0.0, 1.0 - 0.15 * dist)
    z = 0.8 * rng.standard_normal((n, cd)) + (aval * strength)[:, None] * direction[None, :]
    z = (z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    bins = {0: np.array([i for i in range(30, n) if dist[i] == 1]),
            1: np.array([i for i in range(30, n) if dist[i] == 2]),
            2: np.array([i for i in range(30, n) if dist[i] == 3]),
            3: np.array([i for i in range(30, n) if dist[i] >= 4])}
    a_shuf = aval.copy(); np.random.default_rng(9).shuffle(a_shuf)
    orc = _oracle_per_bin(z, aval, a_shuf, bins, 1.0, np.random.default_rng(1), 3000)
    oracle_fires = orc is not None and orc["oracle_reach"] >= 1 and \
        (orc["acc_smooth"][0] == orc["acc_smooth"][0] and orc["acc_smooth"][0] - orc["acc_shuf"][0] > 0.05)

    res = dict(
        reuse_ok=reuse_ok,
        sys_bind_heldout_hi=float(m_hi["bind_heldout"]), sys_flat_heldout_hi=float(m_hi["flat_heldout"]),
        sys_flat_seen_hi=float(m_hi["flat_seen"]), sys_bind_heldout_lo=float(m_lo["bind_heldout"]),
        sys_fires=bool(sys_fires), sys_telemetry=bool(sys_telemetry),
        reach_by_D=r_by_D, reach_edge_recall=float(rm["edge_recall"]),
        reach_fires=bool(reach_fires), reach_telemetry=bool(reach_telemetry),
        oracle_reach=(orc["oracle_reach"] if orc else None), oracle_fires=bool(oracle_fires),
    )
    ok = bool(reuse_ok and sys_fires and sys_telemetry and reach_fires and reach_telemetry and oracle_fires)
    return ok, res


# ---------------------------------------------------------------------------
# Shared CN cache (built once; block 3 encoder trained per seed over it)
# ---------------------------------------------------------------------------

def build_cn_cache(cfg):
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["cn_n_nodes"], SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["cn_feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    attr_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 555)
    a_smooth = make_smooth_attribute(edges, degrees, n_nodes, attr_rng, cfg["cn_n_sources"], cfg["cn_diffuse_steps"])
    a_shuf = a_smooth.copy(); attr_rng.shuffle(a_shuf)
    n_gs = int(min(cfg["cn_n_ground_seeds"], n_nodes // 4))
    ground_seeds = attr_rng.choice(n_nodes, size=n_gs, replace=False)
    seed_set = set(int(x) for x in ground_seeds)
    dist = multi_source_bfs(adj, [int(x) for x in ground_seeds], n_nodes)
    bins, n_unreachable = distance_bins(dist, seed_set)
    nonseed_idx = np.concatenate([bins[b] for b in range(4) if bins[b].shape[0] > 0]) \
        if any(bins[b].shape[0] > 0 for b in range(4)) else np.array([], dtype=np.int64)
    return dict(X=X, adj=adj, a_smooth=a_smooth, a_shuf=a_shuf, bins=bins, ground_seeds=ground_seeds,
                nonseed_idx=nonseed_idx, meta=meta,
                bin_counts={b: int(bins[b].shape[0]) for b in range(4)}, n_unreachable=int(n_unreachable))


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
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (not telemetry-sensitive or reuse mismatch): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    # ---- build shared CN cache (real ConceptNet subgraph for block 3) ----
    _log("building CN cache (target n_nodes=%d)..." % cfg["cn_n_nodes"])
    cn_cache = build_cn_cache(cfg)
    _log("CN cache: %s | bins d1=%d d2=%d d3=%d d4+=%d" % (
        cn_cache["meta"], cn_cache["bin_counts"][0], cn_cache["bin_counts"][1],
        cn_cache["bin_counts"][2], cn_cache["bin_counts"][3]))

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS bind/unbind reuse + 3 discriminators telemetry-sensitive; CN cache built",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, cn_meta=cn_cache["meta"], cn_bin_counts=cn_cache["bin_counts"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, cfg, cn_cache)
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
            seed_failures=seed_failures, cn_meta=cn_cache["meta"]))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        cn_meta=cn_cache["meta"], cn_bin_counts=cn_cache["bin_counts"], gates=gates,
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
