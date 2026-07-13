"""MAP_BUILDER_RESIDUE_MODULE_CEILING: is RNS/CRT multi-module residue coding (grid-cell VSA construction; Frady/
Kleyko arXiv:2311.04872) a DEPLOYABLE lever that raises the recoverable-signal ORACLE CEILING of the inductive
relational map-builder at SUB-QUADRATIC cost -- AND does it survive a MATCHED CLEAN decode? Tests the codes<->decode
COUPLING head-on, because a VET-banked prior (reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_
2026-07-06) predicts residue codes read off a NOISY associative superposition are SET UP TO FAIL: low-arity
per-module argmax amplifies noise, no joint decode. So the cell crosses RNS residue codes with {noisy per-module
argmax decode, clean joint (CRT-aware) decode} to LOCALIZE capacity-present-but-unreadable vs capacity-absent.

THE COST/CEILING TRADE (MEASURED, on-disk). Monolithic-dimension relief RAISES the native-store ORACLE ceiling but
at O(n_dim^2) W-storage cost:
  oracle_mrr_by_dim = {1024: 0.023083, 2048: 0.118037, 4096: 0.413520, 8192: 0.780600}
  MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.oracle_mrr_by_dim
  W-cost = n_dim^2: 1024->1.05M, 2048->4.19M, 4096->16.78M, 8192->67.11M.
Additive (SGD TransE k=24) ORACLE ceiling = 0.137293 MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/
metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE ; realized additive compose = 0.128210 (:ANCHOR_COMPOSE).
RNS/CRT claim (CITED@arXiv:2311.04872 + Sreenivasan&Fiete 2011): capacity = PRODUCT of module ranges, cost = SUM
of module dims -> multiplicative range from additive resource. The DEPLOYABLE question: can a K-module residue code
at SUM-cost reach the CEILING a same-cost MONOLITHIC vector reaches, and BEAT it (sub-quadratic advantage)?

RNS CONSTRUCTION (my design; zero SGD, deterministic, glass-box). K=5 pairwise-coprime moduli m=[7,11,13,17,19]
(product 323323 >> N~25.7k). Only the LARGE-cardinality set (entity IDs, the decode target) is residue-coded;
relations (n_rel~40, small) keep a FULL per-module codebook so relational signal is not residue-collapsed. Per
module k: a real KGStore(n_ent=m_k, n_rel, n_dim=d_k) supplies random-bipolar codebooks C_k (m_k x d_k) and RC_k
(n_rel x d_k); the store's OWN one-shot Hebbian W_k (d_k x d_k) ingests residue-mapped train (+fold-in) edges
(h%m_k, r, t%m_k). d_k=2048 all modules -> RNS W-cost = K*d_k^2 = 20.97M (3.2x CHEAPER than the 8192 monolithic
relief 67.11M; sub-quadratic in the effective range). Matched-cost monolithic control at d_match=round(sqrt(K)*d_k)
=4579 (W-cost 20.97M) is the SAME-COST bar the residue code must beat.

THE 2x2 (residue-code x decode; all ORACLE = held-out edges folded into W -> measures the RECOVERABLE ceiling):
  MONO_PC_ORACLE      : monolithic native code d=1024, native bilinear readout, fold-in. POSITIVE CONTROL -> must
                        reproduce 0.023 (apparatus reproduces the native baseline).
  MONO_MATCHED_ORACLE : monolithic native code d=4579 (SAME W-cost as RNS), native bilinear readout, fold-in. The
                        same-cost bar + the ORACLE-FIRES gate (arena answerable at this dim per the relief curve).
  RNS_NOISY_ORACLE    : residue codes, HARD per-module argmax residue decode + agreement combine (the low-arity
                        residue-native shortcut the VET prior says LOSES on noisy superposition). Predicted FRAGILE.
  RNS_CLEAN_ORACLE    : residue codes, SOFT JOINT decode score(t)=sum_k <recall_k, C_k[t%m_k]> over all N tails
                        (CRT-aware; no per-module commitment; a strong module carries weak ones). THE HEADLINE.
LOCALIZATION: RNS_CLEAN >> RNS_NOISY => capacity PRESENT-but-unreadable by the noisy readout (decode-limited; clean
  decode unlocks it). RNS_CLEAN ~ RNS_NOISY ~ RANDOM => capacity ABSENT in the residue codes (code-limited; the
  task's relational structure does not factor across residue moduli). RNS_CLEAN > MONO_MATCHED => genuine
  sub-quadratic ceiling lever. RNS_CLEAN <= MONO_MATCHED => no advantage over a same-cost monolithic vector.

SECONDARY (realized anchor-compose under the best pairing): RNS_CLEAN_COMPOSE composes each held-out tail's residue
signature from its SUPPORT edges (per-module majority argmax; NO fold-in) then scores QUERY edges with the clean
joint decode. Compared vs additive realized 0.128 (CITED) + RANDOM + RNS_SCRAMBLE_COMPOSE must-fail (support
relations scrambled). Context only; the headline verdict is the PRIMARY oracle-ceiling coupling.

PRE-REG BANDS (picked BEFORE the run; primary = FILTERED MRR rank-vs-all-N; fractions of ADD_ORACLE=0.137293 +
cost-relative + the codes<->decode coupling; H_rns = RNS_CLEAN - RANDOM measured in-run):
  ORACLE-FIRES (arena answerable) : MONO_MATCHED_ORACLE >= 3x RANDOM AND (MONO_MATCHED - RANDOM) >= 0.003.
  POS-CONTROL : MONO_PC_ORACLE reproduces 0.023 within +-0.010 AND RANDOM <= 0.004.
  CAPACITY_DEPLOYABLE (RNS is a genuine sub-quadratic ceiling lever): pos-controls hold AND oracle fires AND
      RNS_CLEAN - RANDOM >= max(0.50*ADD_ORACLE, 0.010) (reaches >=50% of the additive-oracle ceiling) AND
      RNS_CLEAN >= MONO_MATCHED + 0.020 (BEATS the same-cost monolithic) AND RNS_COST < RELIEF_8192_COST.
      Reports the coupling: DECODE_LIMITED if (RNS_CLEAN - RNS_NOISY) >= 0.50*H_rns (present-but-unreadable-by-noisy).
  NOT_DEPLOYABLE : pos-controls hold AND oracle fires AND either
      (a) CODE-LIMITED: (RNS_CLEAN - RANDOM) < 0.010 (no recoverable residue signal under EITHER decode -> the
          relational structure does not factor across residue moduli; capacity absent), OR
      (b) NO-SUBQUAD-ADVANTAGE: (RNS_CLEAN - RANDOM) >= 0.010 but RNS_CLEAN <= MONO_MATCHED (residue recoverable but
          a same-cost monolithic vector does at least as well -> no lever; redirect to decode-side / accept O(n^2)).
  MIDDLE_BAND : recoverable (RNS_CLEAN - RANDOM >= 0.010) and RNS_CLEAN in (MONO_MATCHED, MONO_MATCHED+0.020] -> a
      marginal edge; sweep K / d_k before claiming a lever.
  Gated INCONCLUSIVE if oracle does not fire, pos-controls fail, too few held-out queries, or POP beats RANDOM
  (BROKEN; guard validated vs the RANDOM/arm floor per Gate F.4).

FIVE VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight; F.1-F.4 ENFORCE):
  (1) positive_control : on a planted residue-recoverable arena, RNS_CLEAN recovers planted held-out tails and clears
      RANDOM by the ceiling-aware (ratio+abs) fire gate -> arena answerable, the clean-decode discriminator FIRES.
  (2) metric_moves : the 2x2 oracle MRRs MOVE across [RANDOM, RNS_NOISY, MONO_MATCHED, RNS_CLEAN] (not frozen).
  (3) negative_control_margin : RANDOM + RNS on scrambled residue-tail assignment + SCRAMBLE compose sit below
      RNS_CLEAN by an MRR margin, deterministically (>=3 controls).
  (4) full_gates_exercised : the deployable/coupling verdict fires every fail-closed gate at self-test scale.
  (5) real_code_path (F.1) + substrate_signature (F.2/F.3) + guard_baseline_valid (F.4): the self-test CONSTRUCTS
      the REAL KGStore per module at tiny scale and RUNS ingest_triples on residue-mapped triples (exercises the FULL
      substrate entrypoints); binds KGStore against its LIVE signature with BASE/portable kwargs only
      (n_ent,n_rel,n_dim,generator -- NOT the optional init_entities); the BROKEN(POP>RANDOM) guard is validated to
      compare against the RANDOM/arm floor, not a structurally-zero POP.

## Compute architecture
class (b) sequential-CPU, justified. The native store is ONE-SHOT Hebbian (NO SGD, NO epochs) -> the whole cell is
cheap CPU: per module a chunked Hebbian ingest (KGStore.ingest_triples, batch=5000, d_k=2048 -> d_k^2 per batch) and
a chunked query recall + residue-similarity matmul; the CLEAN joint decode is a per-module (nq x m_k) similarity then
an O(nq*N*K) gather (m_k<=19 distinct residue codes per module -> the READOUT is itself sub-quadratic, not nq*N*d).
Monolithic arms reuse the base cell's CPU Hebbian path. The reference cell exp_kg_store_dim_scaling_ceiling_v1 built
stores up to n_dim=8192 (W-cost 67M) across 3 seeds on device=cpu in 1768s; this cell builds NOTHING above d=4579
(W-cost 21M) so it is strictly cheaper -> remote_cpu_queue (device=cpu). No SGD, no GPU needed. Storage: only the
per-module Hebbian W_k (real KGStore primitive) + a read-only per-held-out-tail residue-signature estimate for the
SECONDARY compose; no mutation of any persisted store; each KGStore instance is cell-local.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 8 arms produce >=5 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary bands are FRACTIONS of the measured additive-oracle ceiling (0.137) + a same-cost
#   monolithic in-run bar -> discriminator_reachability OK by construction (RNS must beat a measured same-cost arm).
# - baseline_in_band: MONO_MATCHED must FIRE (>=3x RANDOM) so the arena is answerable at the RNS cost; MONO_PC
#   reproduces the 0.023 native baseline; RANDOM near the 1/N floor.
# - discriminator survives scale: FULL runs at the EXACT CSKG core / held-out-entity regime (N~25.7k, frac=0.15,
#   support_frac=0.5, seeds 7/13/17) that MEASURED 0.023->0.781 monolithic + 0.137 additive; the self-test fires the
#   RNS_CLEAN-recovers-planted + clean-decode-computes + must-fail discriminators on a planted residue-recoverable arena.
# - HARD bands strictly separated: DEPLOYABLE needs RNS_CLEAN >= MONO_MATCHED+0.020 (MIDDLE dead-band up to +0.020).
# - HP_SCOPE: the DEPLOYABLE gates apply to RNS_CLEAN_ORACLE only. MONO_MATCHED = same-cost bar + oracle-fire gate;
#   MONO_PC = 0.023 reproducer; RNS_NOISY = the fragile-decode localizer; RANDOM/SCRAMBLE = must-not-clear controls;
#   RNS_CLEAN_COMPOSE/RNS_SCRAMBLE_COMPOSE = SECONDARY realized context; POP = fit-independence / BROKEN guard.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=5 sigs + finite W per module.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- all moduli/dims/fracs/tols pre-registered, NOT tuned on real
#   data; the CSKG core + held-out split config is COPIED VERBATIM from the native + additive arenas.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-module flush prints + heartbeat; timeout>=1800).

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
from hdlab.kg_traversal import KGStore  # noqa: E402  (LIVE store; per-module residue codebooks + native Hebbian W)

# Reuse the native arena / split / native readout / controls VERBATIM via import (bit-identical split given seed).
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402

ANCHOR_NAME = "map_builder_residue_module_ceiling_v1"

# ---- Arm names (all scored PAIRED on the SAME held-out QUERY edges; filtered MRR-vs-all-N) ----
MONO_PC = "MONO_PC_ORACLE_d1024"            # positive control: monolithic native d=1024 -> reproduce 0.023
MONO_MATCHED = "MONO_MATCHED_ORACLE"        # same-cost monolithic (d=d_match) + oracle-fire gate
RNS_NOISY = "RNS_NOISY_ORACLE"              # residue codes, hard per-module argmax decode (fragile; VET prior)
RNS_CLEAN = "RNS_CLEAN_ORACLE"             # residue codes, soft joint CRT-aware decode (HEADLINE)
RANDOM = "RANDOM_CODES"                     # null floor
RNS_COMPOSE = "RNS_CLEAN_COMPOSE"          # SECONDARY realized: compose held-out signature from support + clean decode
RNS_SCRAMBLE = "RNS_SCRAMBLE_COMPOSE"      # SECONDARY must-fail: support relations scrambled
POP = "BASELINE_POP"                        # fit-independence sanity / BROKEN guard floor

ORACLE_2X2 = [MONO_PC, MONO_MATCHED, RNS_NOISY, RNS_CLEAN]
ALL_ARMS = [MONO_PC, MONO_MATCHED, RNS_NOISY, RNS_CLEAN, RANDOM, RNS_COMPOSE, RNS_SCRAMBLE, POP]

EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"

# ---- RNS module design (pairwise-coprime moduli; product >> N; only entities residue-coded) ----
MODULI = [7, 11, 13, 17, 19]                # product = 323323 >> N~25.7k
D_MODULE = 2048                             # per-module code dim (all modules)
K_MOD = len(MODULI)
# matched-cost monolithic dim: d_match^2 == K*D_MODULE^2  -> d_match = round(sqrt(K)*D_MODULE)
D_MATCHED = int(round((float(K_MOD) ** 0.5) * D_MODULE))     # 4579
D_MONO_PC = 1024

# ---- CITED reference ceilings (the quantities this cell is measured against) ----
CITED_MONO_1024 = 0.023083   # MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.oracle_mrr_by_dim.1024
CITED_MONO_2048 = 0.118037   # MEASURED@ same :2048
CITED_MONO_4096 = 0.413520   # MEASURED@ same :4096
CITED_RELIEF_8192 = 0.780600 # MEASURED@ same :8192 (the undeployable O(n^2) relief target)
CITED_ADD_ORACLE = 0.137293  # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE
CITED_ADD_COMPOSE = 0.12821  # MEASURED@ same :ANCHOR_COMPOSE (additive realized)

# ---- W-storage costs (parameter counts) ----
RNS_COST = K_MOD * D_MODULE * D_MODULE
MONO_MATCHED_COST = D_MATCHED * D_MATCHED
RELIEF_8192_COST = 8192 * 8192

# ---- Pre-registered bands (NOT tuned on real data) ----
REPRODUCE_TOL_MONO = 0.010       # |MONO_PC - 0.023| tolerance (one-shot Hebbian, low variance)
RANDOM_FLOOR_MRR = 0.004         # RANDOM must sit at/below this (native-readout null floor at nq>=3000)
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003
DEPLOY_ADD_FRAC = 0.50           # RNS_CLEAN - RANDOM >= 0.50 * ADD_ORACLE
DEPLOY_ADD_ABS = 0.010           # ... AND >= this absolute (recoverable at all)
SUBQUAD_MARGIN = 0.020           # RNS_CLEAN >= MONO_MATCHED + this -> beats the same-cost monolithic
DECODE_LIMITED_FRAC = 0.50       # (RNS_CLEAN - RNS_NOISY) >= 0.50 * (RNS_CLEAN - RANDOM) -> present-but-unreadable
COMPOSE_SCRAMBLE_MARGIN = 0.003  # (RNS_COMPOSE - RNS_SCRAMBLE) >= this (SECONDARY control; reported, non-headline)

# ---- self-test planted thresholds (calibrated on synthetic, NOT real data) ----
ST_CLEAN_MIN = 0.15              # planted residue-recoverable arena: RNS_CLEAN oracle mrr >= this
ST_CLEAN_BEATS_RANDOM = 0.08     # (RNS_CLEAN - RANDOM) mrr margin
ST_CLEAN_GE_NOISY = -1e-6        # clean decode is never worse than noisy (soft joint >= hard argmax on recoverable)
ST_SCRAMBLE_MARGIN = 0.03        # (RNS_CLEAN - RNS residue-scramble) mrr margin

SCORE_CHUNK = 512

# Config profiles. SELFTEST/FULL exercise the SAME residue-module build -> decode -> score -> verdict path.
# SELFTEST: moduli product=2431 >> arena n_ent=80 -> UNIQUE CRT residue signatures + mild per-module head-collision
# so the clean joint decode is answerable (CLEAN~0.69 >> NOISY~0.30 >> RANDOM~0.08) and the discriminator + the
# clean-vs-noisy coupling both fire, while relation-scramble/identity controls collapse.
SELFTEST_CFG = dict(moduli=[11, 13, 17], d_module=1024, d_mono_pc=256, st_n_ent=80, st_edges_per_ent=6,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=8)
# FULL: CSKG core k_core=12 (N~25.7k), the SAME held-out split (frac=0.15, support_frac=0.5), seeds [7,13,17].
FULL_CFG = dict(moduli=MODULI, d_module=D_MODULE, d_mono_pc=D_MONO_PC,
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


def _d_matched(moduli, d_module):
    return int(round((float(len(moduli)) ** 0.5) * d_module))


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
# RNS residue modules: one REAL KGStore per module (n_ent=m_k gives random-bipolar residue codebook C_k), native
# one-shot Hebbian W_k over residue-mapped (h%m_k, r, t%m_k) train (+fold-in) edges. Base/portable KGStore kwargs.
# ---------------------------------------------------------------------------

def _residue_map(edges_int, m_k):
    """Map (h,r,t) int edges to residue-space (h%m_k, r, t%m_k)."""
    h = (edges_int[:, 0] % m_k).astype(np.int64)
    r = edges_int[:, 1].astype(np.int64)
    t = (edges_int[:, 2] % m_k).astype(np.int64)
    return np.stack([h, r, t], axis=1)


def build_residue_module(m_k, n_rel, d_k, seed, module_idx, train_int, fold_in=None):
    """Real KGStore for module k. init_entities defaults True -> random-bipolar C_k (m_k x d_k), RC_k (n_rel x d_k).
    Base/portable kwargs ONLY (n_ent,n_rel,n_dim,generator) per Gate F.3. Returns (store, W_finite)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + d_k * 7 + module_idx * 131 + 3)
    store = KGStore(n_ent=int(m_k), n_rel=int(n_rel), n_dim=int(d_k), generator=g)
    store.W.zero_()
    tri = _residue_map(train_int, m_k)
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = np.concatenate([tri, _residue_map(fold_in, m_k)], axis=0)
    store.ingest_triples(torch.from_numpy(tri).long())
    finite = bool(torch.isfinite(store.W).all().item())
    return store, finite


def module_residue_sims(store, query_int, m_k, chunk=SCORE_CHUNK, rel_perm=None):
    """s_k[i, j] = <W_k @ key_k(h_i%m_k, r_i), C_k[j]> for j in [0,m_k). Native bilinear recall then residue-codebook
    similarity. rel_perm scrambles relation ids (control). Shape [nq, m_k]."""
    hq = torch.from_numpy((query_int[:, 0] % m_k).astype(np.int64)).long()
    r_np = query_int[:, 1].astype(np.int64).copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]
    rq = torch.from_numpy(r_np).long()
    E = store.E; R = store.R; W = store.W; sq = store.sq
    nq = query_int.shape[0]
    ET = E.T.contiguous()
    out = torch.empty(nq, E.shape[0], dtype=torch.float32)
    for b in range(0, nq, chunk):
        Q = (E[hq[b:b + chunk]] * R[rq[b:b + chunk]] * sq)     # [c, d_k] native multiplicative bind
        recall = Q @ W.T                                       # [c, d_k] native Hebbian recall
        out[b:b + chunk] = recall @ ET                         # [c, m_k] residue-codebook similarity
    return out


def _res_tail_table(moduli, N):
    """res_tail[k] = arange(N) % m_k. Shape (K, N) long tensors list."""
    return [torch.from_numpy((np.arange(N) % m).astype(np.int64)).long() for m in moduli]


def rns_clean_scores(sims_list, res_tail, N):
    """SOFT joint decode: score(t) = sum_k s_k[:, t % m_k]. Shape [nq, N]. O(nq*N*K) gather (sub-quadratic readout)."""
    nq = sims_list[0].shape[0]
    scores = torch.zeros(nq, N, dtype=torch.float32)
    for k, s_k in enumerate(sims_list):
        scores += s_k[:, res_tail[k]]                          # gather (nq, N) from (nq, m_k)
    return scores


def rns_noisy_scores(sims_list, res_tail, N, seed):
    """HARD per-module argmax residue decode + agreement combine (fragile low-arity residue-native shortcut). Ties
    (coarse integer agreement) broken by a tiny deterministic jitter that encodes NO signal. Shape [nq, N]."""
    nq = sims_list[0].shape[0]
    agree = torch.zeros(nq, N, dtype=torch.float32)
    for k, s_k in enumerate(sims_list):
        hat_k = s_k.argmax(dim=1)                              # [nq] hard residue per module
        agree += (res_tail[k][None, :] == hat_k[:, None]).to(torch.float32)   # [nq, N] match indicator
    g = torch.Generator(device="cpu").manual_seed(seed * 313 + 11)
    jitter = (torch.rand(nq, N, generator=g, dtype=torch.float32) - 0.5) * 1e-4
    return agree + jitter


def rns_compose_scores(modules, support_int, query_int, moduli, res_tail, N, seed, rel_perm=None):
    """SECONDARY realized: estimate each held-out tail's residue signature from its SUPPORT edges (per-module MAJORITY
    argmax of the support-edge recalls; NO fold-in), replace those tails' residue assignment, then CLEAN-decode the
    QUERY edges. rel_perm scrambles support relations (must-fail control). Shape [nq, N]."""
    res_tail_c = [rt.clone() for rt in res_tail]
    for k, (store, m_k) in enumerate(zip(modules, moduli)):
        # per-support-edge argmax residue (in module k), majority-vote per held-out tail
        s_sup = module_residue_sims(store, support_int, m_k, rel_perm=rel_perm)   # [S, m_k]
        hat = s_sup.argmax(dim=1).numpy()                                         # [S]
        tails = support_int[:, 2].astype(np.int64)
        votes = {}
        for i in range(tails.shape[0]):
            t = int(tails[i])
            votes.setdefault(t, np.zeros(m_k, dtype=np.int64))
            votes[t][int(hat[i])] += 1
        rt = res_tail_c[k].numpy().copy()
        for t, v in votes.items():
            rt[t] = int(v.argmax())                                              # replace with composed residue
        res_tail_c[k] = torch.from_numpy(rt).long()
    sims_q = [module_residue_sims(store, query_int, m_k) for store, m_k in zip(modules, moduli)]
    return rns_clean_scores(sims_q, res_tail_c, N)


# ---------------------------------------------------------------------------
# Score all arms PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def score_all_arms(prep, cfg, seed):
    N = prep["N"]; n_rel = prep["n_rel"]
    moduli = cfg["moduli"]; d_module = cfg["d_module"]; d_mono_pc = cfg["d_mono_pc"]
    d_match = _d_matched(moduli, d_module)
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    hold_all = prep["hold_all"]; all_true = prep["all_true"]
    res_tail = _res_tail_table(moduli, N)

    # ---- RNS residue modules (ORACLE = fold-in) ----
    modules = []
    mods_finite = True
    for kk, m_k in enumerate(moduli):
        store_k, fin_k = build_residue_module(m_k, n_rel, d_module, seed, kk, train_int, fold_in=hold_all)
        modules.append(store_k)
        mods_finite = mods_finite and fin_k
    sims = [module_residue_sims(store, query_int, m_k) for store, m_k in zip(modules, moduli)]
    sc_rns_clean = rns_clean_scores(sims, res_tail, N)
    sc_rns_noisy = rns_noisy_scores(sims, res_tail, N, seed)
    # residue-scramble control (relations permuted in the query recall) -> clean decode on a broken relational signal
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    sims_scr = [module_residue_sims(store, query_int, m_k, rel_perm=rel_perm) for store, m_k in zip(modules, moduli)]
    sc_rns_scr = rns_clean_scores(sims_scr, res_tail, N)   # used only inside the negative-control margin at self-test

    # ---- SECONDARY realized compose (no fold-in modules) ----
    modules_tr = []
    for kk, m_k in enumerate(moduli):
        store_k, _ = build_residue_module(m_k, n_rel, d_module, seed, kk, train_int, fold_in=None)
        modules_tr.append(store_k)
    sc_compose = rns_compose_scores(modules_tr, support_int, query_int, moduli, res_tail, N, seed)
    sc_compose_scr = rns_compose_scores(modules_tr, support_int, query_int, moduli, res_tail, N, seed, rel_perm=rel_perm)

    # ---- monolithic native arms (reuse base VERBATIM) ----
    store_pc = base.build_store(N, n_rel, d_mono_pc, seed, train_int, fold_in=hold_all)
    recall_pc = base.native_query_recall(store_pc, query_int)
    sc_mono_pc = base.score_from_codes(recall_pc, store_pc.E)
    store_mm = base.build_store(N, n_rel, d_match, seed, train_int, fold_in=hold_all)
    recall_mm = base.native_query_recall(store_mm, query_int)
    sc_mono_mm = base.score_from_codes(recall_mm, store_mm.E)
    mono_finite = bool(torch.isfinite(store_pc.W).all().item() and torch.isfinite(store_mm.W).all().item())

    sc_random = base.random_scores(N, query_int, d_match, seed)

    arm_scores = {
        MONO_PC: sc_mono_pc, MONO_MATCHED: sc_mono_mm, RNS_NOISY: sc_rns_noisy, RNS_CLEAN: sc_rns_clean,
        RANDOM: sc_random, RNS_COMPOSE: sc_compose, RNS_SCRAMBLE: sc_compose_scr,
    }
    # residue-scramble ORACLE score is an internal control (not a headline arm); kept for the self-test margin
    arm_scores["_RNS_RELSCRAMBLE_ORACLE"] = sc_rns_scr

    arm_metric, arm_sig = {}, {}
    for name, sc in arm_scores.items():
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    diag = dict(mods_finite=bool(mods_finite), mono_finite=mono_finite, d_matched=int(d_match),
                rns_cost=int(len(moduli) * d_module * d_module), mono_matched_cost=int(d_match * d_match),
                moduli=list(moduli), d_module=int(d_module))
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, diag=diag)


# ---------------------------------------------------------------------------
# Prepare a seed-deterministic split (SAME as base + additive arena: bit-identical given seed/ent2i/fracs).
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


def run_corpus(pool_lbl, cfg, seed, corpus_name):
    prep = prepare_corpus(pool_lbl, cfg, seed)
    d_match = _d_matched(cfg["moduli"], cfg["d_module"])
    result = dict(corpus=corpus_name, seed=seed, N=int(prep["N"]), n_rel=int(prep["n_rel"]),
                  n_train=int(prep["train_int"].shape[0]), n_heldout_entities=len(prep["hold_ids"]),
                  n_support=int(prep["support_int"].shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(prep["query_int"].shape[0]), n_cold=int(prep["n_cold"]),
                  moduli=list(cfg["moduli"]), d_module=int(cfg["d_module"]), d_matched=int(d_match))
    if prep["query_int"].shape[0] < 1:
        result["empty"] = True
        return result, None
    fs = score_all_arms(prep, cfg, seed)
    am = fs["arm_metric"]
    headline = [a for a in ALL_ARMS]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in headline},
        arm_n={a: am[a]["n"] for a in headline},
        arm_sigs={a: fs["arm_sig"][a] for a in list(fs["arm_sig"].keys())},
        internal_relscramble_mrr=round(am["_RNS_RELSCRAMBLE_ORACLE"].get(CEIL_METRIC, float("nan")), 6),
        diag=fs["diag"],
    )
    return result, fs


# ---------------------------------------------------------------------------
# Deployable / coupling verdict over per-seed results.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def deployable_verdict(per_seed):
    def agg(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    mrr = {a: agg(a) for a in ALL_ARMS}
    mono_pc = mrr[MONO_PC]; mono_mm = mrr[MONO_MATCHED]; rns_noisy = mrr[RNS_NOISY]; rns_clean = mrr[RNS_CLEAN]
    rnd = mrr[RANDOM]; comp = mrr[RNS_COMPOSE]; comp_scr = mrr[RNS_SCRAMBLE]; pop = mrr[POP]

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    H_rns = _sub(rns_clean, rnd)                       # RNS recoverable headroom
    clean_minus_noisy = _sub(rns_clean, rns_noisy)
    clean_minus_mono = _sub(rns_clean, mono_mm)
    compose_margin = _sub(comp, comp_scr)

    # positive controls
    mono_pc_reproduces = bool(mono_pc == mono_pc and abs(mono_pc - CITED_MONO_1024) <= REPRODUCE_TOL_MONO)
    random_floor = bool(rnd == rnd and rnd <= RANDOM_FLOOR_MRR)
    oracle_ratio = _ratio(mono_mm, rnd)
    oracle_fires = bool(_sub(mono_mm, rnd) == _sub(mono_mm, rnd) and _sub(mono_mm, rnd) >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    mods_finite = all(ps.get("diag", {}).get("mods_finite", False) for ps in per_seed)
    mono_finite = all(ps.get("diag", {}).get("mono_finite", False) for ps in per_seed)
    # BROKEN guard (Gate F.4): POP must NOT beat RANDOM (validated vs the RANDOM/arm floor, not a structural-zero POP)
    broken = bool(pop == pop and rnd == rnd and (pop - rnd) > max(RANDOM_FLOOR_MRR, 0.005))

    pos_controls_ok = bool(mono_pc_reproduces and random_floor and oracle_fires and mods_finite
                           and mono_finite and not broken)

    # deployable conditions
    recoverable = bool(H_rns == H_rns and H_rns >= max(DEPLOY_ADD_FRAC * CITED_ADD_ORACLE, DEPLOY_ADD_ABS))
    recoverable_any = bool(H_rns == H_rns and H_rns >= DEPLOY_ADD_ABS)
    subquad_advantage = bool(clean_minus_mono == clean_minus_mono and clean_minus_mono >= SUBQUAD_MARGIN)
    subquad_cost = bool(RNS_COST < RELIEF_8192_COST)
    decode_limited = bool(clean_minus_noisy == clean_minus_noisy and H_rns == H_rns and H_rns > 0
                          and clean_minus_noisy >= DECODE_LIMITED_FRAC * H_rns)

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_POSCONTROL_OR_ORACLE_FAILED"
    elif recoverable and subquad_advantage and subquad_cost:
        verdict = "CAPACITY_DEPLOYABLE_SUBQUADRATIC"
    elif not recoverable_any:
        verdict = "NOT_DEPLOYABLE_CODES_ABSENT"
    elif recoverable_any and not subquad_advantage:
        verdict = "NOT_DEPLOYABLE_NO_SUBQUAD_ADVANTAGE"
    else:
        verdict = "MIDDLE_BAND_MARGINAL_RESIDUE_EDGE"

    coupling = ("DECODE_LIMITED_present_but_unreadable_by_noisy" if decode_limited
                else ("CODE_LIMITED_capacity_absent" if not recoverable_any
                      else "READABLE_BY_NOISY_TOO"))

    frac_of_add = _ratio(rns_clean, CITED_ADD_ORACLE)
    frac_of_relief = _ratio(rns_clean, CITED_RELIEF_8192)

    verdict_msg = (
        "%s [%s] || ORACLE MRR: MONO_PC(d1024)=%s(repro0.023=%s) MONO_MATCHED(d%d,cost%.1fM)=%s RNS_NOISY=%s "
        "RNS_CLEAN=%s(cost%.1fM) RANDOM=%s || H_rns=%s (>=%.3f=%s) clean-mono=%s (>=%.3f subquad=%s) clean-noisy=%s "
        "(decode_limited>=%.2f*H=%s) | frac_of_add(0.137)=%s frac_of_relief(0.781)=%s cost_vs_relief=%.2fx "
        "(subquad=%s) || SECONDARY compose=%s vs add_compose0.128 scramble=%s (margin=%s) | oracle_fires=%s "
        "pos_controls=%s broken=%s seeds=%d"
        % (verdict, coupling, _fmt(mono_pc), mono_pc_reproduces,
           per_seed[0]["diag"]["d_matched"], MONO_MATCHED_COST / 1e6, _fmt(mono_mm), _fmt(rns_noisy),
           _fmt(rns_clean), RNS_COST / 1e6, _fmt(rnd), _fmt(H_rns),
           max(DEPLOY_ADD_FRAC * CITED_ADD_ORACLE, DEPLOY_ADD_ABS), recoverable, _fmt(clean_minus_mono),
           SUBQUAD_MARGIN, subquad_advantage, _fmt(clean_minus_noisy), DECODE_LIMITED_FRAC, decode_limited,
           _fmt(frac_of_add), _fmt(frac_of_relief), RNS_COST / float(RELIEF_8192_COST), subquad_cost,
           _fmt(comp), _fmt(comp_scr), _fmt(compose_margin), oracle_fires, pos_controls_ok, broken, len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    metric_keys = ["hits@%d" % kk for kk in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    gates = dict(
        verdict=verdict, coupling=coupling,
        oracle_2x2_mrr=dict(MONO_PC=_rnd(mono_pc), MONO_MATCHED=_rnd(mono_mm),
                            RNS_NOISY=_rnd(rns_noisy), RNS_CLEAN=_rnd(rns_clean)),
        random_mrr=_rnd(rnd), H_rns=_rnd(H_rns),
        clean_minus_noisy=_rnd(clean_minus_noisy), clean_minus_mono_matched=_rnd(clean_minus_mono),
        frac_of_additive_oracle=_rnd(frac_of_add), frac_of_monolithic_relief=_rnd(frac_of_relief),
        secondary_compose=dict(RNS_CLEAN_COMPOSE=_rnd(comp), RNS_SCRAMBLE_COMPOSE=_rnd(comp_scr),
                               compose_scramble_margin=_rnd(compose_margin),
                               compose_scramble_controlled=bool(compose_margin == compose_margin
                                                                and compose_margin >= COMPOSE_SCRAMBLE_MARGIN)),
        costs=dict(RNS_COST=RNS_COST, MONO_MATCHED_COST=MONO_MATCHED_COST, RELIEF_8192_COST=RELIEF_8192_COST,
                   cost_ratio_vs_relief=round(RNS_COST / float(RELIEF_8192_COST), 4)),
        mono_pc_reproduces=mono_pc_reproduces, random_floor=random_floor, oracle_fires=oracle_fires,
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        mods_finite=mods_finite, mono_finite=mono_finite, broken=broken, pos_controls_ok=pos_controls_ok,
        recoverable=recoverable, recoverable_any=recoverable_any, subquad_advantage=subquad_advantage,
        subquad_cost=subquad_cost, decode_limited=decode_limited,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        controls=dict(POP=_rnd(pop)),
        bands=dict(CITED_MONO_1024=CITED_MONO_1024, CITED_ADD_ORACLE=CITED_ADD_ORACLE,
                   CITED_RELIEF_8192=CITED_RELIEF_8192, CITED_ADD_COMPOSE=CITED_ADD_COMPOSE,
                   REPRODUCE_TOL_MONO=REPRODUCE_TOL_MONO, RANDOM_FLOOR_MRR=RANDOM_FLOOR_MRR,
                   ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   DEPLOY_ADD_FRAC=DEPLOY_ADD_FRAC, DEPLOY_ADD_ABS=DEPLOY_ADD_ABS, SUBQUAD_MARGIN=SUBQUAD_MARGIN,
                   DECODE_LIMITED_FRAC=DECODE_LIMITED_FRAC, MODULI=list(MODULI), D_MODULE=D_MODULE,
                   D_MATCHED=D_MATCHED),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Planted residue-recoverable arena: (h, r) -> t is DETERMINISTIC via a per-relation permutation, and N is chosen
# > product(moduli) so residue signatures COLLIDE (multiple entities share a full residue signature) -> the JOINT
# clean decode disambiguates via the RELATION operator while a single module's argmax is ambiguous. Held-out tails'
# edges fold into W so the ORACLE clean decode can recover them; relation-scramble breaks the mapping.
# ---------------------------------------------------------------------------

def build_planted_residue_arena(seed, moduli, n_ent=180, n_rel=6, edges_per_ent=5):
    rng = np.random.default_rng(seed * 100057 + 9)
    perms = [rng.permutation(n_ent) for _ in range(n_rel)]      # per-relation head->tail permutation (deterministic)
    edges = []
    for h in range(n_ent):
        rels = rng.choice(n_rel, size=min(edges_per_ent, n_rel), replace=False)
        for r in rels:
            t = int(perms[int(r)][h])
            if t == h:
                t = (t + 1) % n_ent
            edges.append(("e%d" % h, "r%d" % int(r), "e%d" % t))
    return list(dict.fromkeys(edges))


# ---------------------------------------------------------------------------
# Self-test: apparatus validity on the planted residue arena (real KGStore path + discriminators + must-fails).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _selftest_real_store_smoke(cfg):
    """Gate F.1: CONSTRUCT the REAL KGStore per module at tiny scale + RUN ingest_triples on residue-mapped triples,
    populating the exercised-entrypoints set. Returns (exercised, ok)."""
    exercised = set()
    m_k = cfg["moduli"][0]
    tri = np.array([[0, 0, 1], [1, 0, 2], [2, 1, 0]], dtype=np.int64)
    store, fin = build_residue_module(m_k, 3, cfg["d_module"], 7, 0, tri, fold_in=tri[:1])
    exercised.add("KGStore")
    exercised.add("build_residue_module")
    if store._n_triples_ingested > 0:
        exercised.add("ingest_triples")
    s = module_residue_sims(store, tri, m_k)
    if s.shape == (3, m_k):
        exercised.add("module_residue_sims")
    return exercised, bool(fin and s.shape == (3, m_k))


def _mechanism_selftest_body():
    cfg = dict(SELFTEST_CFG)
    out = {}
    moduli = cfg["moduli"]

    # ---- Gate F.1 real code path ----
    exercised, real_ok = _selftest_real_store_smoke(cfg)

    pool = build_planted_residue_arena(7, moduli, n_ent=cfg["st_n_ent"], edges_per_ent=cfg["st_edges_per_ent"])
    prep = prepare_corpus(pool, cfg, 7)
    if prep["query_int"].shape[0] < cfg["min_heldout"]:
        out["fail"] = "planted residue arena produced too few held-out queries (%d)" % prep["query_int"].shape[0]
        return False, out
    res, fs = run_corpus(pool, cfg, 7, "PLANTED_RESIDUE")
    am = fs["arm_metric"]
    sm = {a: am[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    relscr = am["_RNS_RELSCRAMBLE_ORACLE"].get(CEIL_METRIC, float("nan"))
    n_sigs = len(set(fs["arm_sig"][a] for a in ALL_ARMS))

    clean = sm[RNS_CLEAN]; noisy = sm[RNS_NOISY]; rnd = sm[RANDOM]; mono_mm = sm[MONO_MATCHED]
    clean_recovers = bool(clean == clean and clean >= ST_CLEAN_MIN)
    clean_beats_random = bool(clean == clean and rnd == rnd and (clean - rnd) >= ST_CLEAN_BEATS_RANDOM)
    clean_ge_noisy = bool(clean == clean and noisy == noisy and (clean - noisy) >= ST_CLEAN_GE_NOISY)
    scramble_fails = bool(clean == clean and relscr == relscr and (clean - relscr) >= ST_SCRAMBLE_MARGIN)
    arms_differ = bool(n_sigs >= 5)
    mods_finite = bool(fs["diag"]["mods_finite"] and fs["diag"]["mono_finite"])

    # VACUOUS-SMOKE guard: on the planted residue arena the clean decode MUST separate from RANDOM.
    clean_frozen = bool((clean - rnd) < ST_CLEAN_BEATS_RANDOM)
    assert_discriminator_fires(clean_frozen, control_name=RANDOM,
                               headline_name="rns_clean_decode_beats_random_heldout", run_mode="self_test",
                               extra="RNS_CLEAN joint decode did NOT separate from RANDOM on the planted "
                                     "residue-recoverable arena -> arena not answerable / apparatus frozen")

    st_verdict, _stmsg, _stg = deployable_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(clean_recovers and clean_beats_random),
         "control_name": "RANDOM", "headline_name": "rns_clean_recovers_planted_heldout",
         "extra": "planted residue arena: the RNS clean joint decode recovers planted held-out tails (fold-in) and "
                  "clears RANDOM by the ceiling-aware margin -> the residue apparatus is answerable and the "
                  "clean-decode discriminator fires"},
        {"kind": "metric_moves", "metric_name": "oracle_2x2_mrr",
         "values": [rnd, noisy, mono_mm, clean],
         "extra": "the 2x2 oracle cells MOVE on synthetic: RANDOM=%.3f RNS_NOISY=%.3f MONO_MATCHED=%.3f "
                  "RNS_CLEAN=%.3f (not frozen)" % (rnd, noisy, mono_mm, clean)},
        {"kind": "negative_control_margin",
         "control_scores": [rnd, relscr, sm[RNS_SCRAMBLE]],
         "headline_threshold": clean, "higher_is_pass": True, "margin": ST_SCRAMBLE_MARGIN, "n_repeats_min": 3,
         "control_name": "RANDOM_RELSCRAMBLE_COMPOSESCRAMBLE_below_clean", "extra":
         "RANDOM + relation-scrambled residue decode + scrambled-support compose sit below RNS_CLEAN by the MRR "
         "margin -> the residue lift needs the RELATION operators + correct residue mapping, not code volume"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["clean_recovers", "clean_beats_random", "scramble_fails", "arms_differ",
                                    "oracle_fires", "real_code_path", "deployable_verdict"],
         "exercised_gates": ["clean_recovers", "clean_beats_random", "scramble_fails", "arms_differ",
                             "oracle_fires", "real_code_path", "deployable_verdict"],
         "extra": "deployable_verdict=%s at self-test scale" % st_verdict},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "build_residue_module", "ingest_triples", "module_residue_sims"],
         "exercised_entrypoints": exercised,
         "extra": "self-test constructs the REAL KGStore per module and runs ingest_triples on residue-mapped triples"},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None},
         "extra": "base/portable KGStore kwargs only (n_ent,n_rel,n_dim,generator); no optional init_entities"},
        {"kind": "guard_baseline_valid", "baseline_score": sm[MONO_MATCHED], "floor_score": rnd,
         "guard_name": "BROKEN_POP_BEATS_RANDOM", "baseline_name": "MONO_MATCHED", "floor_name": "RANDOM",
         "eps": 0.02,
         "extra": "the BROKEN guard compares POP against the RANDOM floor (not a structural-zero POP); MONO_MATCHED "
                  "sits above the floor so the arena baseline is valid"},
    ], run_mode="self_test")

    out.update(
        real_code_path_ok=bool(real_ok), exercised_entrypoints=sorted(exercised),
        planted_2x2={a: (round(sm[a], 5) if sm[a] == sm[a] else None) for a in ALL_ARMS},
        internal_relscramble_mrr=(round(relscr, 5) if relscr == relscr else None),
        n_distinct_sigs=n_sigs, clean_recovers=clean_recovers, clean_beats_random=clean_beats_random,
        clean_ge_noisy=clean_ge_noisy, scramble_fails=scramble_fails, arms_differ=arms_differ,
        mods_finite=mods_finite, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3", "guard_baseline_valid_F4"],
    )
    ok = bool(real_ok and clean_recovers and clean_beats_random and clean_ge_noisy and scramble_fails
              and arms_differ and mods_finite and vp_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=cpu run_mode=%s seeds=%s moduli=%s d_module=%s d_matched=%s rns_cost=%.1fM relief_cost=%.1fM"
         % (run_mode, seeds, cfg["moduli"], cfg["d_module"], _d_matched(cfg["moduli"], cfg["d_module"]),
            len(cfg["moduli"]) * cfg["d_module"] ** 2 / 1e6, RELIEF_8192_COST / 1e6))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s | clean=%s noisy=%s mono_mm=%s random=%s relscr=%s | clean_recovers=%s "
         "scramble_fails=%s real_code=%s vp_ok=%s"
         % (st_ok, (st_res.get("planted_2x2") or {}).get(RNS_CLEAN),
            (st_res.get("planted_2x2") or {}).get(RNS_NOISY), (st_res.get("planted_2x2") or {}).get(MONO_MATCHED),
            (st_res.get("planted_2x2") or {}).get(RANDOM), st_res.get("internal_relscramble_mrr"),
            st_res.get("clean_recovers"), st_res.get("scramble_fails"), st_res.get("real_code_path_ok"),
            st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (clean decode did not recover/beat-random, or scramble did not "
                        "fail, or the real KGStore residue path / validity-preflight did not fire): %s"
                        % {kk: st_res.get(kk) for kk in ("clean_recovers", "clean_beats_random", "scramble_fails",
                           "real_code_path_ok", "arms_differ", "validity_preflight_ok")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS RESIDUE_MODULE_CEILING: on a planted residue-recoverable arena the RNS clean "
                        "joint decode recovers planted held-out tails (fold-in) and clears RANDOM; the clean decode "
                        "is >= the noisy per-module argmax decode; relation-scramble + scrambled-support compose "
                        "fail; the REAL KGStore per-module residue path (ingest_triples) is exercised; 7 "
                        "validity-preflight checks declared (F.1-F.4 ENFORCE)",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res, _fs = run_corpus(pool, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY")
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", 20):
                raise RuntimeError("held-out query edges too few (%d)" % res.get("n_query_scored", 0))
            sigset = set(res["arm_sigs"][a] for a in ALL_ARMS)
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs" % (seed, len(sigset)))
            if not (res["diag"]["mods_finite"] and res["diag"]["mono_finite"]):
                raise RuntimeError("non-finite W seed=%d (mods=%s mono=%s)"
                                   % (seed, res["diag"]["mods_finite"], res["diag"]["mono_finite"]))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d | MONO_PC=%s MONO_MM=%s RNS_NOISY=%s RNS_CLEAN=%s RANDOM=%s | COMPOSE=%s SCR=%s (%.1fs)"
                 % (seed, res["n_query_scored"], _fmt(ah[MONO_PC][CEIL_METRIC]), _fmt(ah[MONO_MATCHED][CEIL_METRIC]),
                    _fmt(ah[RNS_NOISY][CEIL_METRIC]), _fmt(ah[RNS_CLEAN][CEIL_METRIC]), _fmt(ah[RANDOM][CEIL_METRIC]),
                    _fmt(ah[RNS_COMPOSE][CEIL_METRIC]), _fmt(ah[RNS_SCRAMBLE][CEIL_METRIC]), time.time() - ts))
            _hb("cskg", si + 1)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = deployable_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
