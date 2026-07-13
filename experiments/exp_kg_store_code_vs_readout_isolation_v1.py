"""KG_STORE_CODE_VS_READOUT_ISOLATION: decompose the ~6x native-vs-additive ORACLE-CEILING gap into its two
un-separated factors -- CODE QUALITY vs READOUT MATH -- via a clean 2x2 factorial. Closes the biggest remaining
unknown in the nativize question: is the native store's low ceiling limited by its random-bipolar CODES, by its
bilinear-Hebbian READOUT, or both?

THE GAP (MEASURED, on-disk). Native store ORACLE ceiling (bilinear-Hebbian readout on fixed random-bipolar codes,
held-out folded in) = 0.023083 MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:
gates.heldout_mrr.ORACLE_FOLDIN. Additive fit ORACLE ceiling (direct-distance readout on learned k=24 TransE
coordinates) = 0.137293 MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.
ORACLE_ADDITIVE. Ratio ~5.9x. The WRITE RULE factor is CLOSED (kg_store_write_rule_decorrelated_ceiling_v1 =
HARD_FAIL_WRITE_RULE_NOT_THE_LEVER, pinv oracle 0.0240 ~= hebb oracle 0.0231; capacity saturation, NOT the lever;
this cell does NOT vary the write rule -- native arms use the store's default Hebbian ingest). DIMENSION is swept
separately (kg_store_dim_scaling_ceiling_v1). CODES vs READOUT is UN-ISOLATED -- this cell's job.

THE 2x2 (measure the ORACLE ceiling under each cell of {code source} x {readout}; all arms PAIRED on the SAME
held-out QUERY edges + filtered MRR-vs-all-N, so the four cells are directly comparable):
  NN_ORACLE = native codes  x native readout   : random-bipolar E/R + bilinear-Hebbian E@(W@key), hold folded in.
              REPRODUCE 0.023 (positive control). CITED@ above.
  AN_ORACLE = additive codes x native readout   : the LEARNED k=24 oracle coords (Xo,Do), BRIDGED to n_dim via a
              FIXED LINEAR random projection (additivity-preserving; documented below), used as the native store's
              E/R; hold folded into the store's Hebbian W; read back by the native bilinear readout. THE NOVEL ARM.
              RISES toward 0.137 => CODES were the native limiter (nativize needs richer/structured/learned codes;
              glass-box code-family is the next lever). FLAT ~0.02 (while BF_ADD confirms the codes ARE good under
              their own readout) => the native READOUT caps it (nativize needs a readout change).
  NA_ORACLE = native codes  x additive readout  : direct-distance -||E_h + R_r - E_t|| on the SAME random-bipolar
              codes that give 0.023 under the native readout. RISES => the READOUT was the limiter (direct-distance
              beats bilinear-Hebbian on identical codes). FLAT ~floor => the CODES cap it (random codes carry no
              additive geometry for ANY readout). Predicted floor.
  AA_ORACLE = additive codes x additive readout  : direct-distance on the learned oracle coords (Xo,Do). REPRODUCE
              0.137 (positive control / sanity). CITED@ above.

BRIDGE (my choice; glass-box, ZERO SGD). A FIXED random LINEAR projection P ~ N(0, 1/n_dim), shape (k, n_dim),
deterministic per seed. E_add = Xo @ P ; R_add = Do @ P (dense real, n_dim). LINEAR => the additive translation
structure is PRESERVED: E_add[h] + R_add[r] = (Xo[h] + Do[r]) @ P ~= Xo[t] @ P = E_add[t] (Johnson-Lindenstrauss:
a random linear projection preserves inner products / distances up to a small distortion). A sign/bipolar bridge
would DESTROY additivity (sign is nonlinear) and confound a FLAT AN_ORACLE. To remove that confound outright the
cell adds a BRIDGE-FIDELITY control:
  BF_ADD = additive codes x additive readout on the BRIDGED codes = additive_direct_scores(E_add, R_add) in n_dim.
  It MUST reproduce ~AA_ORACLE (the projection preserved the geometry). If BF_ADD is high (codes provably good under
  direct-distance) but AN_ORACLE is flat, the native READOUT is DEFINITIVELY the limiter -- not a broken bridge.

WHY the native readout accepts dense codes: KGStore's E/R/W/sq are plain tensors; the bilinear readout
E@(W@key), key=E[s]*R[p]*sqrt(n_dim), W += outer(E[o],key)/n_dim, is valid linear algebra for ANY real E/R (ranking
is scale-invariant). The cell OVERWRITES a local store instance's E/R with the bridged dense codes then runs the
STANDARD Hebbian ingest + the base cell's native readout VERBATIM. KGStore the class + the CERT-584/585 code paths
are NOT modified (same defaulted-off in-cell-instance discipline as the write-rule cell).

CONTEXT ARMS (not headline; cheap, add fidelity + weak-point context):
  AA_COMPOSE : additive REALIZED (compose held-out from support via mean(Xa+Da), direct distance). REPRODUCE 0.128
               (CITED@ anchor_compose ANCHOR_COMPOSE) -- proves the additive-readout wiring is faithful.
  NN_COMPOSE : native REALIZED (majority-sign bundle of Hebbian recall). CITED@ native cell NATIVE_ANCHOR_COMPOSE
               0.0140 -- context for the realized (not ceiling) gap.
  RANDOM / NATIVE_SCRAMBLE / IDENTITY_SHUFFLE : native-readout null + must-fail controls (reuse base VERBATIM).

PRE-REG ATTRIBUTION (picked BEFORE the run; primary = filtered MRR oracle ceilings; G = AA_ORACLE - NN_ORACLE, the
measured ceiling gap, ~0.114):
  Gate POS-CONTROLS (all required, else INCONCLUSIVE): NN_ORACLE reproduces 0.023 within REPRODUCE_TOL_NATIVE AND
    AA_ORACLE reproduces 0.137 within REPRODUCE_TOL_ADD AND RANDOM at floor AND native scramble+idshuf controlled
    AND BF_ADD >= BF_FIDELITY_FRAC * AA_ORACLE (the bridge preserved the geometry -> AN_ORACLE is interpretable).
  CODES_LIMITER : (AN_ORACLE - NN_ORACLE) >= CODES_RISE_FRAC * G  (the native readout carries the additive magnitude
                  once given good codes -> the CODES were the native path's dominant limiter).
  READOUT_LIMITER : (AN_ORACLE - NN_ORACLE) <= READOUT_FLAT_FRAC * G  (native readout stays near 0.02 despite good
                  codes that BF_ADD proves are good -> the bilinear-Hebbian READOUT FORMAT caps it).
  BOTH : READOUT_FLAT_FRAC*G < (AN_ORACLE - NN_ORACLE) < CODES_RISE_FRAC*G, OR NA_ORACLE also rises materially
                  ((NA_ORACLE - RANDOM) > READOUT_FLAT_FRAC * G -> the readout swap alone lifts even native codes).
  NA read-out (reported, sharpens BOTH): NA_ORACLE - RANDOM; predicted <= READOUT_FLAT_FRAC * G (direct-distance
                  alone does NOT rescue random codes -> the additive advantage is a CO-DESIGNED codes+readout
                  package, not a bolt-on readout).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : on synthetic, the additive readout recovers planted TransE structure (learned codes
                                >> RANDOM) AND the native ORACLE recovers the planted native-consistent arena.
  (2) metric_moves            : the four 2x2 oracle-cell MRRs MOVE across the synthetic arenas (not frozen).
  (3) negative_control_margin : RANDOM + native-scramble + NA-on-random-codes sit below the learned-code arms by an
                                MRR margin (deterministic, >=3 controls).
  (4) full_gates_exercised    : the attribution verdict fires every gate at self-test scale.

## Compute architecture
class (c) MIXED. The ADDITIVE fits (Xa/Da train-only + Xo/Do oracle fold-in) are minibatch-SGD (k=24, epochs=500,
n_neg=128) -> GPU-BATCHED (overnight_queue): matmul-heavy neg-scoring, the exact workload anchor_compose ran on GPU
(gpu1024); CPU would take hours (the additive coords are NOT persisted on disk -> a re-fit is required, so this is
NOT a zero-SGD cell and does NOT belong on remote_cpu). The NATIVE store (one-shot Hebbian ingest, bilinear readout)
+ the linear-projection bridge + all direct-distance scorings + split/POP graph ops run on CPU tensors (cheap;
1024x1024 W, chunked (nq,N) reads -- the base cell's own CPU path). Fits on cuda; native readout on cpu; codes moved
across the boundary once. 2 fits/seed x 3 seeds. Wall estimate < ~90min FULL on GPU. No mutation of KGStore or any
persisted store; the fit checkpoints are cell-owned + resumable.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): the 2x2 + control arms produce >=5 distinct score signatures.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary is a FRACTION-OF-THE-MEASURED-GAP attribution (AN_ORACLE-NN_ORACLE)/(AA-NN); bands
#   are fractions of the in-run measured ceiling gap G -> discriminator_reachability OK by construction.
# - baseline_in_band: NN_ORACLE reproduces 0.023 AND AA_ORACLE reproduces 0.137 (both positive controls fire);
#   RANDOM near the 1/N floor; BF_ADD proves the bridge before AN_ORACLE is interpreted.
# - discriminator survives scale: the FULL runs at n_dim=1024 / k=24 / N~25.7k = the EXACT regimes that MEASURED
#   0.023 and 0.137; the self-test fires the codes-matter (native + additive readout both respond to code quality)
#   + bridge-fidelity + NA-floor discriminators deterministically on planted arenas.
# - HARD/attribution bands strictly separated: CODES_RISE_FRAC=0.50 vs READOUT_FLAT_FRAC=0.20 (30% of G dead-band).
# - HP_SCOPE: the attribution gates apply to the AN_ORACLE / NA_ORACLE cross cells only; NN_ORACLE + AA_ORACLE are
#   positive-control reproducers (must reproduce landed); RANDOM/SCRAMBLE/IDSHUF = must-not-clear controls; BF_ADD =
#   bridge-fidelity gate; AA_COMPOSE/NN_COMPOSE = realized-path context.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=5 sigs + 2 finite fits.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- all fracs/tols pre-registered, NOT tuned on real data; the
#   additive fit config is COPIED VERBATIM from the confirmed anchor_compose FULL (k=24/epochs=500/n_neg=128).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-fit flush prints + heartbeat; timeout>=1800).

ASCII-only. No bare except; except SystemExit before except Exception.
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
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint  # noqa: E402
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_planted_transe_arena, build_anchor_compose_codes,
)
from hdlab.kg_traversal import KGStore  # noqa: E402  (LIVE store; E/R overwritten on a local instance only)

# Reuse the native arena / split / native readout / controls / verdict-helpers VERBATIM via import.
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402

ANCHOR_NAME = "kg_store_code_vs_readout_isolation_v1"

# ---- 2x2 + control arm names (all scored PAIRED on the SAME held-out QUERY edges; filtered MRR-vs-all-N) ----
NN_ORACLE = "NN_ORACLE_nativecode_nativeread"     # arm1: reproduce 0.023 (native codes, native readout, fold-in)
AN_ORACLE = "AN_ORACLE_addcode_nativeread"        # arm2: bridged learned codes, native readout (NOVEL headline)
NA_ORACLE = "NA_ORACLE_nativecode_addread"        # arm3: random codes, additive readout (NOVEL; predicted floor)
AA_ORACLE = "AA_ORACLE_addcode_addread"           # arm4: reproduce 0.137 (learned codes, additive readout)
BF_ADD = "BF_ADD_bridgefidelity"                  # bridge-fidelity: additive readout on bridged codes (~ AA_ORACLE)
AA_COMPOSE = "AA_COMPOSE_realized"                # additive realized (~0.128) positive control
NN_COMPOSE = "NN_COMPOSE_realized"                # native realized (~0.014) context
RANDOM = "RANDOM_CODES"                           # native-readout null (the floor bar)
SCRAMBLE = "NATIVE_SCRAMBLE"                      # must-fail (native readout, support relations scrambled)
IDSHUF = "IDENTITY_SHUFFLE"                       # must-fail (native readout, composed code -> wrong entity)
POP = "BASELINE_POP"                              # fit-independence sanity

ORACLE_2X2 = [NN_ORACLE, AN_ORACLE, NA_ORACLE, AA_ORACLE]
ALL_ARMS = [NN_ORACLE, AN_ORACLE, NA_ORACLE, AA_ORACLE, BF_ADD, AA_COMPOSE, NN_COMPOSE,
            RANDOM, SCRAMBLE, IDSHUF, POP]

EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"

# ---- CITED reference ceilings (the quantities this cell decomposes) ----
CITED_NN_ORACLE = 0.023083   # MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN
CITED_AA_ORACLE = 0.137293   # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE
CITED_AA_COMPOSE = 0.12821   # MEASURED@ same anchor_compose path :ANCHOR_COMPOSE
CITED_NN_COMPOSE = 0.013969  # MEASURED@ native cell :NATIVE_ANCHOR_COMPOSE

# ---- Pre-registered attribution bands (NOT tuned on real data) ----
REPRODUCE_TOL_NATIVE = 0.008     # |NN_ORACLE - 0.023| tolerance (one-shot Hebbian, low variance)
REPRODUCE_TOL_ADD = 0.030        # |AA_ORACLE - 0.137| tolerance (SGD re-fit; cross-device float variance wider)
CODES_RISE_FRAC = 0.50           # AN_ORACLE rises >= 50% of the gap G -> CODES were the limiter
READOUT_FLAT_FRAC = 0.20         # AN_ORACLE rises <= 20% of G -> READOUT caps it (dead-band between)
BF_FIDELITY_FRAC = 0.50          # BF_ADD >= 50% of AA_ORACLE -> the linear bridge preserved the additive geometry
RANDOM_FLOOR_MRR = 0.004         # RANDOM must sit at/below this (native-readout null floor at nq>=3000)

# ---- Bridge knobs ----
BRIDGE_STD_SCALE = True          # apply a single global scalar so bridged codes match the bipolar RMS (rank-invariant)

# ---- self-test planted thresholds (calibrated on synthetic, NOT real data) ----
ST_ADD_LEARNED_MIN = 0.15        # planted TransE: additive readout on LEARNED codes mrr >= this
ST_ADD_BEATS_RANDOM = 0.08       # (learned - RANDOM) mrr margin under the additive readout
ST_BF_FRAC = 0.50                # BF_ADD_synth >= this * AA_ORACLE_synth (bridge preserves geometry on synthetic)
ST_NA_FLOOR_EPS = 0.03           # NA_ORACLE_synth (random codes, additive readout) <= RANDOM + this (predicted floor)
ST_NATIVE_CODESENS_MARGIN = 0.02 # native readout: clean (near-orthogonal) codes ORACLE - random codes ORACLE >= this
ST_SCRAMBLE_MARGIN = 0.03        # additive readout: (learned - scramble) mrr >= this

SCORE_CHUNK = 512

# Config profiles.
# SELFTEST: small synthetic; additive fit small; native store small.
SELFTEST_CFG = dict(n_dim=256, k=8, epochs=150, n_neg=32, batch=2048, neg_chunk=16,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=8)
# FULL: n_dim=1024 (native default / CERT-584/585 regime) + k=24/epochs=500/n_neg=128 (anchor_compose FULL VERBATIM).
FULL_CFG = dict(n_dim=1024, k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=0.15, support_frac=0.5, cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=20, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


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
# BRIDGE: fixed LINEAR random projection of k-dim learned coords -> n_dim dense codes (additivity-preserving).
# ---------------------------------------------------------------------------

def make_projection(k, n_dim, seed):
    """P ~ N(0, 1/n_dim), shape (k, n_dim), deterministic. Linear => additive structure survives the bridge."""
    g = torch.Generator(device="cpu").manual_seed(seed * 90001 + 7)
    return (torch.randn(k, n_dim, generator=g, dtype=torch.float32) / float(np.sqrt(n_dim)))


def bridge_codes(X_cpu, D_cpu, P):
    """E_add = X @ P ; R_add = D @ P (dense real, n_dim). Optional single global RMS scalar (rank-invariant for the
    native readout; distance-preserving up to that scalar for the additive readout)."""
    E_add = (X_cpu @ P).contiguous()
    R_add = (D_cpu @ P).contiguous()
    if BRIDGE_STD_SCALE:
        # single global scalar so per-element RMS ~= 1 (bipolar convention); a scalar preserves additivity + ranking.
        rms = float(torch.sqrt((E_add * E_add).mean()).item())
        s = 1.0 / max(rms, 1e-8)
        E_add = (E_add * s).contiguous()
        R_add = (R_add * s).contiguous()
    return E_add, R_add


# ---------------------------------------------------------------------------
# Native store with INJECTED codes (E/R overwritten on a local instance) + standard Hebbian ingest.
# ---------------------------------------------------------------------------

def build_native_store_codes(N, n_rel, n_dim, seed, train_int, E_inject=None, R_inject=None, fold_in=None):
    """KGStore with FIXED bipolar E/R (base seed formula) OR injected dense E/R, + one-shot Hebbian W over
    train (+ optional fold_in). KGStore class untouched; only this instance's E/R/W are set."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + n_dim + 1)   # SAME formula as base.build_store
    store = KGStore(n_ent=N, n_rel=n_rel, n_dim=n_dim, generator=g)
    if E_inject is not None:
        store.E = E_inject.to(torch.float32).contiguous()
    if R_inject is not None:
        store.R = R_inject.to(torch.float32).contiguous()
    store.W.zero_()
    tri = torch.from_numpy(train_int).long()
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = torch.cat([tri, torch.from_numpy(fold_in).long()], dim=0)
    store.ingest_triples(tri)
    finite = bool(torch.isfinite(store.W).all().item())
    return store, finite


# ---------------------------------------------------------------------------
# Additive fit wrappers (train-only Xa/Da + oracle Xo/Do with hold folded in). GPU-batched.
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_additive(train_int, hold_all, N, n_rel, cfg, device, seed, ckpt_dir=None):
    """Return (Xa, Da) train-only and (Xo, Do) oracle (held-out folded in). SGD (k, epochs, n_neg from cfg)."""
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive", seed))
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    Xo, Do = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                             reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_oracle", seed))
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return Xa.detach(), Da.detach(), Xo.detach(), Do.detach()


# ---------------------------------------------------------------------------
# Score all arms PAIRED on the SAME held-out QUERY edges. Returns arm_metric/arm_sig/arm_scores + diagnostics.
# ---------------------------------------------------------------------------

def score_all_arms(prep, cfg, device, seed, ckpt_dir=None):
    N = prep["N"]; n_rel = prep["n_rel"]; n_dim = cfg["n_dim"]; k = cfg["k"]
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    hold_all = prep["hold_all"]; hold_ids = prep["hold_ids"]; all_true = prep["all_true"]

    # ---- additive fits (GPU) ----
    Xa, Da, Xo, Do = fit_additive(train_int, hold_all, N, n_rel, cfg, device, seed, ckpt_dir=ckpt_dir)
    Xo_cpu = Xo.to("cpu"); Do_cpu = Do.to("cpu")

    # ---- bridge learned ORACLE coords -> dense n_dim codes (additivity-preserving linear projection) ----
    P = make_projection(k, n_dim, seed)
    E_add, R_add = bridge_codes(Xo_cpu, Do_cpu, P)

    # ---- NATIVE-readout column ----
    # native codes (random bipolar): reuse base machinery for NN_ORACLE / NN_COMPOSE / RANDOM / SCRAMBLE / IDSHUF
    store_nat, fin_nat = build_native_store_codes(N, n_rel, n_dim, seed, train_int)
    store_nat_oracle, fin_nat_o = build_native_store_codes(N, n_rel, n_dim, seed, train_int, fold_in=hold_all)
    Ep_anchor, support_deg = base.native_compose_codes(store_nat, support_int, N)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Ep_scramble, _ = base.native_compose_codes(store_nat, support_int, N, rel_perm=rel_perm)
    Ep_idshuf = base.identity_shuffle_codes(store_nat.E, Ep_anchor, support_deg, hold_ids, seed)
    recall_nat = base.native_query_recall(store_nat, query_int)
    recall_nat_oracle = base.native_query_recall(store_nat_oracle, query_int)

    # bridged codes (additive-derived): native readout ORACLE fold-in = AN_ORACLE
    store_add, fin_add = build_native_store_codes(N, n_rel, n_dim, seed, train_int,
                                                  E_inject=E_add, R_inject=R_add, fold_in=hold_all)
    recall_add_oracle = base.native_query_recall(store_add, query_int)

    # ---- ADDITIVE-readout column ----
    # native random-bipolar codes fed to the additive (direct-distance) readout = NA_ORACLE (predicted floor)
    E_nat = store_nat.E; R_nat = store_nat.R   # fixed random bipolar rows (n_dim)
    # additive realized codes (compose held-out from support via mean(Xa+Da)) = AA_COMPOSE
    Xac, _sd = build_anchor_compose_codes(Xa.to(device), Da.to(device), support_int, device)

    arm_scores = {}
    arm_scores[NN_ORACLE] = base.score_from_codes(recall_nat_oracle, store_nat_oracle.E)   # native codes, native read, fold-in
    arm_scores[NN_COMPOSE] = base.score_from_codes(recall_nat, Ep_anchor)                   # native codes, native read, realized
    arm_scores[AN_ORACLE] = base.score_from_codes(recall_add_oracle, store_add.E)           # bridged codes, native read, fold-in
    arm_scores[SCRAMBLE] = base.score_from_codes(recall_nat, Ep_scramble)
    arm_scores[IDSHUF] = base.score_from_codes(recall_nat, Ep_idshuf)
    arm_scores[RANDOM] = base.random_scores(N, query_int, n_dim, seed)
    arm_scores[AA_ORACLE] = additive_direct_scores(Xo.to(device), Do.to(device), query_int, device, chunk=SCORE_CHUNK)
    arm_scores[AA_COMPOSE] = additive_direct_scores(Xac, Da.to(device), query_int, device, chunk=SCORE_CHUNK)
    arm_scores[NA_ORACLE] = additive_direct_scores(E_nat, R_nat, query_int, torch.device("cpu"), chunk=SCORE_CHUNK)
    arm_scores[BF_ADD] = additive_direct_scores(E_add, R_add, query_int, torch.device("cpu"), chunk=SCORE_CHUNK)

    arm_metric, arm_sig = {}, {}
    for name in [a for a in ALL_ARMS if a != POP]:
        sc = arm_scores[name]
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    diag = dict(
        fits_finite=bool(torch.isfinite(Xa).all().item() and torch.isfinite(Xo).all().item()),
        native_W_finite=bool(fin_nat and fin_nat_o), bridged_W_finite=bool(fin_add),
        bridge_rms=round(float(torch.sqrt((E_add * E_add).mean()).item()), 5),
        Xo_norm=round(float(torch.linalg.norm(Xo_cpu).item()), 4),
        w_add_hash=hashlib.sha256(store_add.W.numpy().tobytes()).hexdigest()[:16],
        w_nat_hash=hashlib.sha256(store_nat_oracle.W.numpy().tobytes()).hexdigest()[:16],
    )
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg, diag=diag)


# ---------------------------------------------------------------------------
# Prepare a seed-deterministic split (SAME as base + anchor_compose: bit-identical given seed/ent2i/fracs).
# ---------------------------------------------------------------------------

def prepare_corpus(pool_lbl, cfg, seed):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = base.build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)
    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    hold_all = np.concatenate([support_int, query_int], axis=0) if query_int.shape[0] else support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)
    return dict(ent2i=ent2i, rel2i=rel2i, N=N, n_rel=n_rel, train_int=train_int, support_int=support_int,
                query_int=query_int, hold_all=hold_all, hold_ids=hold_ids, n_cold=n_cold,
                n_query_total=n_query_total, gd=gd, all_true=all_true)


def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None):
    prep = prepare_corpus(pool_lbl, cfg, seed)
    result = dict(corpus=corpus_name, seed=seed, N=int(prep["N"]), n_rel=int(prep["n_rel"]),
                  n_train=int(prep["train_int"].shape[0]), n_heldout_entities=len(prep["hold_ids"]),
                  n_support=int(prep["support_int"].shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(prep["query_int"].shape[0]), n_cold=int(prep["n_cold"]),
                  n_dim=int(cfg["n_dim"]), k=int(cfg["k"]))
    if prep["query_int"].shape[0] < 1:
        result["empty"] = True
        return result, None
    fs = score_all_arms(prep, cfg, device, seed, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"], diag=fs["diag"],
    )
    return result, fs


# ---------------------------------------------------------------------------
# 2x2 attribution verdict over the per-seed results.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def attribution_verdict(per_seed):
    def agg(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    mrr = {a: agg(a) for a in ALL_ARMS}
    nn = mrr[NN_ORACLE]; an = mrr[AN_ORACLE]; na = mrr[NA_ORACLE]; aa = mrr[AA_ORACLE]
    bf = mrr[BF_ADD]; rnd = mrr[RANDOM]; scr = mrr[SCRAMBLE]; ids = mrr[IDSHUF]
    G = (aa - nn) if (aa == aa and nn == nn) else float("nan")

    an_rise = (an - nn) if (an == an and nn == nn) else float("nan")
    na_rise = (na - rnd) if (na == na and rnd == rnd) else float("nan")

    # positive-control gates
    nn_reproduces = bool(nn == nn and abs(nn - CITED_NN_ORACLE) <= REPRODUCE_TOL_NATIVE)
    aa_reproduces = bool(aa == aa and abs(aa - CITED_AA_ORACLE) <= REPRODUCE_TOL_ADD)
    random_floor = bool(rnd == rnd and rnd <= RANDOM_FLOOR_MRR)
    # scramble/idshuf must stay near the RANDOM floor (native readout must-fail controls)
    scr_ctrl = bool(scr == scr and rnd == rnd and (scr - rnd) <= READOUT_FLAT_FRAC * G) if G == G else False
    ids_ctrl = bool(ids == ids and rnd == rnd and (ids - rnd) <= READOUT_FLAT_FRAC * G) if G == G else False
    bridge_ok = bool(bf == bf and aa == aa and bf >= BF_FIDELITY_FRAC * aa)
    fits_finite = all(ps.get("diag", {}).get("fits_finite", False) for ps in per_seed)
    W_finite = all(ps.get("diag", {}).get("bridged_W_finite", False)
                   and ps.get("diag", {}).get("native_W_finite", False) for ps in per_seed)

    pos_controls_ok = bool(nn_reproduces and aa_reproduces and random_floor and scr_ctrl and ids_ctrl
                           and bridge_ok and fits_finite and W_finite and G == G and G > 0)

    codes_limiter = bool(an_rise == an_rise and G == G and an_rise >= CODES_RISE_FRAC * G)
    readout_flat = bool(an_rise == an_rise and G == G and an_rise <= READOUT_FLAT_FRAC * G)
    na_rises = bool(na_rise == na_rise and G == G and na_rise > READOUT_FLAT_FRAC * G)

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_POSCONTROL_OR_BRIDGE_FAILED"
    elif codes_limiter and not na_rises:
        verdict = "CODES_ARE_THE_LIMITER"
    elif readout_flat and bridge_ok and not na_rises:
        verdict = "READOUT_IS_THE_LIMITER"
    elif na_rises and readout_flat:
        verdict = "READOUT_IS_THE_LIMITER_NA_CONFIRMS"
    else:
        verdict = "BOTH_CODES_AND_READOUT_CONTRIBUTE"

    msg = ("%s || 2x2 ORACLE MRR: NN(natcode/natread)=%s AN(addcode/natread)=%s NA(natcode/addread)=%s "
           "AA(addcode/addread)=%s || G(gap)=%s AN_rise=%s (codes>=%.2f*G=%s flat<=%.2f*G=%s) NA_rise=%s "
           "(readout if >%.2f*G) || BF(bridge)=%s (>=%.2f*AA=%s) | reproduces NN(%.3f+-%.3f)=%s AA(%.3f+-%.3f)=%s "
           "| RANDOM=%s(floor<=%.3f=%s) SCR-RND=%s IDS-RND=%s(ctrl) | AA_COMPOSE=%s NN_COMPOSE=%s | pos_controls=%s"
           % (verdict, _fmt(nn), _fmt(an), _fmt(na), _fmt(aa), _fmt(G), _fmt(an_rise), CODES_RISE_FRAC,
              codes_limiter, READOUT_FLAT_FRAC, readout_flat, _fmt(na_rise), READOUT_FLAT_FRAC,
              _fmt(bf), BF_FIDELITY_FRAC, bridge_ok, CITED_NN_ORACLE, REPRODUCE_TOL_NATIVE, nn_reproduces,
              CITED_AA_ORACLE, REPRODUCE_TOL_ADD, aa_reproduces, _fmt(rnd), RANDOM_FLOOR_MRR, random_floor,
              _fmt(scr - rnd) if (scr == scr and rnd == rnd) else "nan",
              _fmt(ids - rnd) if (ids == ids and rnd == rnd) else "nan",
              _fmt(mrr[AA_COMPOSE]), _fmt(mrr[NN_COMPOSE]), pos_controls_ok))

    def _rnd(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    metric_keys = ["hits@%d" % kk for kk in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    gates = dict(
        verdict=verdict,
        oracle_2x2_mrr=dict(NN=_rnd(nn), AN=_rnd(an), NA=_rnd(na), AA=_rnd(aa)),
        gap_G=_rnd(G), an_rise=_rnd(an_rise), na_rise=_rnd(na_rise),
        bridge_fidelity_mrr=_rnd(bf), bridge_ok=bridge_ok,
        realized=dict(AA_COMPOSE=_rnd(mrr[AA_COMPOSE]), NN_COMPOSE=_rnd(mrr[NN_COMPOSE])),
        controls=dict(RANDOM=_rnd(rnd), SCRAMBLE=_rnd(scr), IDSHUF=_rnd(ids), POP=_rnd(mrr[POP])),
        nn_reproduces=nn_reproduces, aa_reproduces=aa_reproduces, random_floor=random_floor,
        scramble_controlled=scr_ctrl, idshuf_controlled=ids_ctrl, fits_finite=fits_finite, W_finite=W_finite,
        pos_controls_ok=pos_controls_ok, codes_limiter=codes_limiter, readout_flat=readout_flat, na_rises=na_rises,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        bands=dict(CITED_NN_ORACLE=CITED_NN_ORACLE, CITED_AA_ORACLE=CITED_AA_ORACLE, CITED_AA_COMPOSE=CITED_AA_COMPOSE,
                   REPRODUCE_TOL_NATIVE=REPRODUCE_TOL_NATIVE, REPRODUCE_TOL_ADD=REPRODUCE_TOL_ADD,
                   CODES_RISE_FRAC=CODES_RISE_FRAC, READOUT_FLAT_FRAC=READOUT_FLAT_FRAC,
                   BF_FIDELITY_FRAC=BF_FIDELITY_FRAC, RANDOM_FLOOR_MRR=RANDOM_FLOOR_MRR),
    )
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Self-test: apparatus validity on planted synthetic arenas (adversarial predicted separations + must-fails).
# ---------------------------------------------------------------------------

def mechanism_selftest(device):
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _native_codesens_probe(seed=7, n=256, load=2.0):   # M = load*n > n => interference regime (matches N>>n_dim)
    """Micro-probe: the native bilinear-Hebbian ORACLE readout must RESPOND to code quality at the INTERFERENCE
    regime (M > n, matching real data where N ~= 25.7k >> n_dim=1024). Random keys, fixed; compare RANDOM-bipolar
    target codes vs highly-CORRELATED target codes. Correlated codes COLLIDE in the correlation matrix W (per this
    substrate's own correlation-hurts-capacity finding) -> a LOWER fold-in oracle. A clear (random - correlated)
    margin proves the native-readout measurement is NOT frozen wrt code quality, so a FLAT/LOW AN_ORACLE on real
    data is a genuine signal, not an apparatus artifact."""
    M = int(load * n)
    g = torch.Generator(device="cpu").manual_seed(seed * 31 + 5)
    keys = (torch.randint(0, 2, (M, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    T_rand = (torch.randint(0, 2, (M, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    # correlated targets: shared common direction + weak per-item deviation, bipolarized (semantic-cluster proxy)
    common = (torch.randint(0, 2, (1, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    dev = torch.randn(M, n, generator=g)
    T_corr = torch.sign(2.0 * common + dev)
    T_corr[T_corr == 0] = 1.0

    def _oracle_mrr(T):
        W = (T.T @ keys) / n                                 # Hebbian store keyed by keys -> targets
        recall = keys @ W.T                                  # (M,n) recall of each stored target
        scores = recall @ T.T                                # (M,M) rank the true target among all targets
        ranks = []
        for i in range(M):
            row = scores[i]
            r = int((row > row[i]).sum().item()) + 1
            ranks.append(1.0 / r)
        return float(np.mean(ranks))

    return _oracle_mrr(T_rand), _oracle_mrr(T_corr)   # (random_codes_oracle, correlated_codes_oracle)


def _mechanism_selftest_body(device):
    cfg = dict(SELFTEST_CFG)
    out = {}

    # ---- ST-A: native-readout column apparatus + must-fails (reuse base's proven planted native arena) ----
    pool_nat = base.build_planted_native_arena(7)
    base_res = base.run_corpus(pool_nat, dict(base.SELFTEST_CFG), 7, "PLANTED_NATIVE", localize=False)
    bm = base_res.get("arm_hits", {})
    nat_oracle = bm.get(base.ORACLE, {}).get(CEIL_METRIC, float("nan"))
    nat_native = bm.get(base.NATIVE, {}).get(CEIL_METRIC, float("nan"))
    nat_random = bm.get(base.RANDOM, {}).get(CEIL_METRIC, float("nan"))
    nat_scr = bm.get(base.SCRAMBLE, {}).get(CEIL_METRIC, float("nan"))
    nat_ids = bm.get(base.IDSHUF, {}).get(CEIL_METRIC, float("nan"))
    native_oracle_fires = bool(nat_oracle == nat_oracle and nat_random == nat_random
                               and (nat_oracle - nat_random) >= 0.02 and nat_oracle >= 3.0 * max(nat_random, 1e-6))
    native_scramble_fails = bool(nat_native == nat_native and nat_scr == nat_scr
                                 and (nat_native - nat_scr) >= ST_SCRAMBLE_MARGIN)
    native_idshuf_fails = bool(nat_native == nat_native and nat_ids == nat_ids
                               and (nat_native - nat_ids) >= ST_SCRAMBLE_MARGIN)

    # ---- ST-B: native-readout code sensitivity (clean codes > random codes -> apparatus not frozen wrt codes) ----
    rand_code_oracle, corr_code_oracle = _native_codesens_probe(7)
    native_codes_matter = bool(rand_code_oracle == rand_code_oracle and corr_code_oracle == corr_code_oracle
                               and (rand_code_oracle - corr_code_oracle) >= ST_NATIVE_CODESENS_MARGIN)

    # ---- ST-C: additive-readout column + bridge fidelity + NA-floor on a planted TransE arena ----
    pool_add = build_planted_transe_arena(7)
    prep = prepare_corpus(pool_add, cfg, 7)
    if prep["query_int"].shape[0] < cfg["min_heldout"]:
        out["fail"] = "planted TransE arena produced too few held-out queries (%d)" % prep["query_int"].shape[0]
        return False, out
    fs = score_all_arms(prep, cfg, device, 7, ckpt_dir=None)
    am = fs["arm_metric"]
    sm = {a: am[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(fs["arm_sig"].values()))

    aa_learned = sm[AA_ORACLE]; rnd = sm[RANDOM]; bf = sm[BF_ADD]; na = sm[NA_ORACLE]
    an = sm[AN_ORACLE]; nn = sm[NN_ORACLE]; aac = sm[AA_COMPOSE]
    add_learned_recovers = bool(aa_learned == aa_learned and aa_learned >= ST_ADD_LEARNED_MIN)
    add_beats_random = bool(aa_learned == aa_learned and rnd == rnd and (aa_learned - rnd) >= ST_ADD_BEATS_RANDOM)
    bridge_preserves = bool(bf == bf and aa_learned == aa_learned and bf >= ST_BF_FRAC * aa_learned)
    na_at_floor = bool(na == na and rnd == rnd and (na - rnd) <= ST_NA_FLOOR_EPS)   # random codes, additive readout = floor
    arms_differ = bool(n_sigs >= 5)
    fits_finite = bool(fs["diag"]["fits_finite"] and fs["diag"]["bridged_W_finite"] and fs["diag"]["native_W_finite"])

    # VACUOUS-SMOKE guard: on the planted TransE arena the additive readout MUST separate learned from random.
    add_frozen = bool(add_beats_random is False)
    assert_discriminator_fires(add_frozen, control_name=RANDOM,
                               headline_name="additive_readout_learned_beats_random_synth", run_mode="self_test",
                               extra="on the planted TransE arena the additive readout did NOT separate learned "
                                     "codes from RANDOM -> arena not answerable / apparatus frozen")

    v_verdict, v_msg, v_gates = attribution_verdict(
        [{"arm_hits": {a: {CEIL_METRIC: sm[a]} for a in ALL_ARMS}, "diag": fs["diag"]}])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(add_learned_recovers and add_beats_random
                                                        and native_oracle_fires),
         "control_name": "ADD_LEARNED_AND_NATIVE_ORACLE", "headline_name": "both_readout_positive_controls_fire",
         "extra": "planted arenas: the additive readout recovers learned TransE codes (>>RANDOM) AND the native "
                  "bilinear-Hebbian ORACLE recovers the planted native-consistent arena -> BOTH readout columns of "
                  "the 2x2 are answerable and the attribution is well-posed"},
        {"kind": "metric_moves", "metric_name": "oracle_2x2_mrr",
         "values": [nn, an, na, aa_learned],
         "extra": "the four 2x2 oracle cells MOVE on synthetic: NN=%.3f AN=%.3f NA=%.3f AA=%.3f (not frozen)"
                  % (nn, an, na, aa_learned)},
        {"kind": "negative_control_margin",
         "control_scores": [rnd, na, sm[SCRAMBLE]],
         "headline_threshold": aa_learned, "higher_is_pass": True, "margin": ST_ADD_BEATS_RANDOM, "n_repeats_min": 3,
         "control_name": "RANDOM_NA_SCRAMBLE_below_learned_add", "extra":
         "RANDOM + native-codes-under-additive-readout + native-scramble sit below the learned-additive arm by the "
         "MRR margin -> the additive advantage needs LEARNED geometry, not just the readout"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "add_learned_recovers", "bridge_preserves", "na_at_floor",
                                    "native_oracle_fires", "native_codes_matter", "attribution_verdict"],
         "exercised_gates": ["arms_differ", "add_learned_recovers", "bridge_preserves", "na_at_floor",
                             "native_oracle_fires", "native_codes_matter", "attribution_verdict"],
         "extra": "attribution_verdict=%s at self-test scale" % v_verdict},
    ], run_mode="self_test")

    out.update(
        native_planted=dict(oracle=round(nat_oracle, 5) if nat_oracle == nat_oracle else None,
                            native=round(nat_native, 5) if nat_native == nat_native else None,
                            random=round(nat_random, 5) if nat_random == nat_random else None,
                            scramble=round(nat_scr, 5) if nat_scr == nat_scr else None,
                            idshuf=round(nat_ids, 5) if nat_ids == nat_ids else None),
        native_codesens=dict(rand_code_oracle=round(rand_code_oracle, 5), corr_code_oracle=round(corr_code_oracle, 5)),
        transe_planted={a: round(sm[a], 5) if sm[a] == sm[a] else None for a in ALL_ARMS},
        n_distinct_sigs=n_sigs,
        native_oracle_fires=native_oracle_fires, native_scramble_fails=native_scramble_fails,
        native_idshuf_fails=native_idshuf_fails, native_codes_matter=native_codes_matter,
        add_learned_recovers=add_learned_recovers, add_beats_random=add_beats_random,
        bridge_preserves=bridge_preserves, na_at_floor=na_at_floor, arms_differ=arms_differ,
        fits_finite=fits_finite, attribution_selftest_verdict=v_verdict,
        validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(native_oracle_fires and native_scramble_fails and native_idshuf_fails and native_codes_matter
              and add_learned_recovers and add_beats_random and bridge_preserves and na_at_floor
              and arms_differ and fits_finite)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _pick_device(arg):
    if arg == "cpu":
        return torch.device("cpu")
    if arg == "cuda":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")
    ckpt_dir = os.path.join(str(out_dir), "_fit_ckpts")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s run_mode=%s seeds=%s n_dim=%s k=%s epochs=%s"
         % (device, run_mode, seeds, cfg["n_dim"], cfg["k"], cfg.get("epochs")))

    st_ok, st_res = mechanism_selftest(device)
    _log("mechanism_selftest ok=%s | native_planted=%s codesens=%s transe(AA=%s AN=%s NA=%s NN=%s BF=%s) vp_ok=%s"
         % (st_ok, st_res.get("native_oracle_fires"), st_res.get("native_codes_matter"),
            (st_res.get("transe_planted") or {}).get(AA_ORACLE), (st_res.get("transe_planted") or {}).get(AN_ORACLE),
            (st_res.get("transe_planted") or {}).get(NA_ORACLE), (st_res.get("transe_planted") or {}).get(NN_ORACLE),
            (st_res.get("transe_planted") or {}).get(BF_ADD), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (a readout column, the bridge fidelity, the NA-floor, the native "
                        "code-sensitivity, or a must-fail did not fire on synthetic): %s"
                        % {kk: st_res.get(kk) for kk in ("native_oracle_fires", "native_codes_matter",
                           "add_beats_random", "bridge_preserves", "na_at_floor", "arms_differ")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS CODE_VS_READOUT_ISOLATION: on synthetic, BOTH readout columns respond to code "
                        "quality (additive readout: learned>>random; native bilinear-Hebbian ORACLE: clean codes>"
                        "random codes), the LINEAR bridge preserves the additive geometry (BF~=AA), random codes "
                        "under the additive readout sit at floor (NA~=random), and the native scramble/identity "
                        "must-fails fire; 4 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed = []
    unit_failures = []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res, fs = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", ckpt_dir=ckpt_dir)
            if res.get("empty"):
                raise RuntimeError("empty query set")
            if int(res["n_query_scored"]) < cfg.get("min_heldout", 20):
                raise RuntimeError("held-out query edges too few (%d)" % int(res["n_query_scored"]))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs" % (seed, len(sigset)))
            if not res["diag"]["fits_finite"]:
                raise RuntimeError("additive fit non-finite seed=%d" % seed)
            res["cskg_provenance"] = prov
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d | NN=%s AN=%s NA=%s AA=%s | BF=%s RANDOM=%s AA_COMP=%s NN_COMP=%s | (%.1fs)"
                 % (seed, res["n_query_scored"], _fmt(ah[NN_ORACLE][CEIL_METRIC]), _fmt(ah[AN_ORACLE][CEIL_METRIC]),
                    _fmt(ah[NA_ORACLE][CEIL_METRIC]), _fmt(ah[AA_ORACLE][CEIL_METRIC]), _fmt(ah[BF_ADD][CEIL_METRIC]),
                    _fmt(ah[RANDOM][CEIL_METRIC]), _fmt(ah[AA_COMPOSE][CEIL_METRIC]), _fmt(ah[NN_COMPOSE][CEIL_METRIC]),
                    time.time() - ts))
            _hb("cskg", si + 1)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = attribution_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(seeds), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, unit_failures=unit_failures,
                   per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    device = _pick_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
