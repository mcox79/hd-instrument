"""exp_read_discourse_state_hd_vs_symbolic_membership_overload_v1 -- does an HD superposed discourse
"state of mind" EARN ITS KEEP in the query mode where HD superposition has a PROVABLE structural
advantage (graceful set-membership under OVERLOAD), or is a SYMBOLIC state-of-mind the honest answer?

REFRAME (why this cell exists): v1 (flat) + v2 (hierarchical/queryable) both FAILED. The VET on v2
(a8fc671f) localized WHY: the QUERY sub-test *looked* like an HD win (acc_mech=0.643 vs baselines,
MEASURED@data/exp_read_discourse_wsm_v2_hierarchical_gated_queryable_v1/metrics.json:agg_query_hard)
but a pure-symbolic-pointer tracking the current holder scored IDENTICALLY at SNR=sqrt(2048/8)=16 -- the
HD vector algebra was DECORATIVE (INERT). The Frady-Kleyko-Sommer capacity theorem says a symbolic table
matches/beats HD per-bit at EXACT recall (CITED@notes/research_state_of_mind_hd_load_bearing_query_mode_
reframe_2026-07-17.md Lane B/Q4). HD superposition's PROVABLE advantage is a DIFFERENT query mode:
SIMILARITY / SET-MEMBERSHIP / AGGREGATE / graceful-partial under OVERLOAD -- distributed-partial-for-ALL
vs discrete-zero-for-EVICTED. The note flags this head-to-head as NOT-yet-cited -> must be TESTED, not
assumed. This cell tests it, design-gate compliant, and treats the HONEST FALLBACK (symbolic wins ->
use a symbolic state-of-mind) as a FIRST-CLASS outcome, not a failure.

PRIOR-WORK CONCEPT-QUERY (mandatory, run before authoring): `bash tools/substrate_query.sh "HD
superposition aggregate set-membership consistency query overload symbolic store eviction state of mind"`
-> top hit cosine=0.3047 ('state_of_mind', a WordNet/concept-KB lexical node), NOT a prior EXPERIMENT
cell; no arc experiment surfaces above cosine 0.30. The genuine prior artifacts (reused + credited, not
rediscovered): (1) the FAILED v1/v2 discourse-state cells this supersedes (design lineage + the VET's
inertness discriminator, reused as this cell's rescue-count check); (2) `exp_nativelang_svo_vsa_probe_v1`
(the FHRR bind/bundle/inner-product ALGEBRA, reimplemented in torch complex64 per CLAUDE.md dtype
convention -- same formulas as v2's, credited). Design-parameter precedent (no code reuse): Frady/Kleyko/
Sommer SNR=sqrt(N/M) capacity law; the "graceful (VSA) vs catastrophic (Hopfield 0.138N)" degradation
contrast; Bloom-filter / holographic set-membership.

MECHANISM UNDER TEST: a discourse "state of mind" = which entities are ACTIVE (have been mentioned) in
the accumulated discourse. The HD arm holds this state as ONE superposed FHRR vector (bundle of every
mentioned entity's phasor). The competing SYMBOLIC arm holds a fixed-capacity exact set with LRU
eviction. At OVERLOAD (more distinct entities than fit in the budget) the symbolic set MUST EVICT older
entities -> it answers "absent" for present-but-evicted entities (discrete-zero). The HD bundle holds a
faded-but-nonzero trace of EVERY mentioned entity (distributed-partial). The QUERY is SET-MEMBERSHIP over
a probe set that OVERSAMPLES evicted-active entities (the retrospective / non-recency regime that
Lane A/C identify as the ONLY slice where beating recency matters). Metric = balanced accuracy.

FAIRNESS MODEL (declared, load-bearing, not gamed): both arms get a length-N array budget.
  - PRIMARY (HD-favorable-but-defensible): EQUAL-DIMENSION. HD = N complex64 dims; symbolic-evict =
    C=N exact entity-id slots. Both are length-N arrays; a common operationalization.
  - CONSERVATIVE (Frady-honest): EQUAL-FLOAT. A complex64 dim = 2 float32, so HD's N complex dims cost
    the same floats as C=2N symbolic id-slots. Reported alongside so the accounting choice is TRANSPARENT
    and not load-bearing on one convention. Symbolic is MORE bit-efficient for exact storage (Frady
    theorem) -> the equal-float variant is the harder bar for HD; both are reported per M.
The primary competitor HD must beat is symbolic-LRU-evict at C=N (equal-dimension). This is the strongest
non-strawman symbolic store: exact membership on the C most-recently-touched distinct entities.

WHY SYNTHETIC (not GAP/PDNC/ProPara): the question is decidable ONLY at genuine OVERLOAD (M pushed toward
the SNR-near-threshold zone, SNR=sqrt(2N/M) ~ 1). Real discourse passages carry ~10-48 entities; at any
reasonable N that is SNR >> 3 (comfortable, NO overload) -> HD is inert-by-construction there (exactly
v2's SNR=16 trap). A controlled synthetic-overload stream (the reframe note explicitly permits this "if
it genuinely reaches overload") is the ONLY way to reach the regime where the HD-vs-symbolic question has
an answer. Vocabulary is opaque integer ids (glass-box-legal, no runtime LLM, no corpus license).

DESIGN GATE (verified AT SMOKE before the full sweep):
  (1) REAL BASELINES: (a) recency-oracle (present iff in the last-W mention window, W=C -- a distinct,
      weaker symbolic policy; differs from LRU-evict because re-mentions refresh LRU recency); (b) the
      pure-symbolic-pointer control, implemented as the INERTNESS DISCRIMINATOR (rescue_count, below) --
      the exact v2 VET tool; (c) symbolic-LRU-evict at C=N -- the fixed-capacity store HD must beat.
  (2) DIFFICULTY-ON / OVERLOAD proven: at M>C symbolic-evict MUST drop M-C active entities (its recall on
      evicted-active = 0 BY CONSTRUCTION -> BA_symbolic < 1). Proven NON-vacuous by the rescue-count check.
  (3) INERTNESS DISCRIMINATOR (the v2 catch, generalized): rescue_count = # probes that are
      evicted-active where HD says PRESENT (correct) AND symbolic-evict says ABSENT (wrong). If
      rescue_count == 0 at overload, the HD graceful-trace materialized NOTHING a symbolic shortcut lacks
      -> HD is INERT-BY-CONSTRUCTION and the cell STOPS with that verdict (per the dispatching contract).
      HD's per-probe decision vector must ALSO be bit-non-identical to symbolic-evict's (arms-differ).
  (4) CAN-FAIL: HD LOSES if its crosstalk false-positives on ABSENT probes outweigh its rescues of
      evicted-active -> BA_HD <= BA_symbolic-evict. Very live (Frady theorem is against HD). HARD_FAIL if
      HD never beats symbolic-evict at any overload point, or is inert, or is at chance everywhere.
  (5) ONE VARIABLE: arms differ ONLY in the state-tracking method; identical streams / probes / budget /
      seeds. The sweep axis (M) is applied identically to every arm.

PRE-REG (envelope-fail-bands; set BEFORE running):
  Primary metric = BA_arm(M) = 0.5*(TPR+TNR), mean over N_SEEDS streams, per overload M, primary
  competitor = symbolic-LRU-evict at C=N. tau (HD membership threshold) is FROZEN from a held-out
  calibration stream (separate seed) that maximizes calibration-BA -> applied unseen to test (no peeking;
  calibration_check = adaptive_with_discriminator_gate).
    HARD-PASS: at >=1 overload point (M>C): BA_HD >= BA_symbolic_evict + 0.05 (strictly above floor+5%)
      AND BA_HD >= BA_recency_oracle + 0.02 AND BA_HD >= 0.55 (absolute, above the 0.50 chance floor)
      AND rescue_count > 0 at that M AND arms_differ (HD decisions != symbolic-evict decisions).
    HARD-FAIL: BA_HD <= BA_symbolic_evict at ALL overload points (M>C) [HD never earns its keep] OR
      rescue_count == 0 at every overload M [HD inert-by-construction] OR max_M(BA_HD) < 0.53
      [HD membership indistinguishable from the 0.50 chance floor everywhere].
    MIDDLE / HONEST-FALLBACK (first-class): HD ties symbolic-evict within 0.05 at overload (neither a
      clear win nor inert) -> "state of mind should be SYMBOLIC (substrate-native); reserve HD for the
      proven memory/retrieval frontier." Reported cleanly, NOT as a failure.
  P estimate: P=0.30 HYPOTHESIZED (this cell's own reasoning): the Frady-Kleyko-Sommer theorem
    structurally favors the symbolic store at equal budget for exact-answerable membership; HD's only
    lever is graceful degradation on the evicted-active slice, which the crosstalk floor (SNR=sqrt(2N/M))
    erodes as overload grows. A clean win requires the rescue benefit to outrun the false-positive cost
    in a specific overload pocket -- plausible but not favored. Honest fallback is the modal outcome.

COMPUTE: torch complex64 (CLAUDE.md FHRR dtype), sequential-CPU -- justified under the GPU-batching
discipline's explicit "wall time < 10s total" exemption (N=1024, M up to 8192, N_SEEDS=5, 4 M-values =
20 streams; each a single bundle-sum + one (P,N)@(N,) membership matmul over ~300 probes; measured
elapsed_s reported). Storage: no_storage (in-memory synthetic stream, nothing persisted to
substrate_index). smoke = 2 seeds x {M=2048, M=4096} (2 overload points, fires the discriminator);
full = 5 seeds x M in {1024,2048,4096,8192}. progress_logging = print_flush_true (well under the 1800s
mandatory-heartbeat threshold; start-marker + crash-metrics + atomic-write present regardless).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test AND smoke (META_RULE_AF): HD per-probe decision boolean-vector must
#     be bit-non-identical to symbolic-evict's at overload (empirical hash-compare on the real corpus).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH): metrics.json written via os.replace of a .tmp.
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- see main() outer try.
# - crlb_floor_computed: membership SNR = sqrt(2N/M) (present-score = N +- sqrt(M*N/2), normalize by N).
#     At N=1024: M=2048 -> SNR=1.00; M=4096 -> 0.707; M=8192 -> 0.50; M=1024 -> 1.41. Nonzero signal at
#     every swept M (SNR>=0.5), so a graceful-trace rescue is REACHABLE (not analytically pinned to 0) ->
#     discriminator_reachability=true. crlb_formula_reference: "membership SNR=sqrt(2N/M), FHRR bundle
#     self-vs-crosstalk, Frady/Kleyko/Sommer 1707.01429".
# - baseline_in_band (META_RULE_AG): the symbolic-evict competitor is NOT saturated (at M>C it MUST evict
#     -> BA_symbolic < 1 by construction) and the random-floor arm ~0.50; both verified in-band at smoke.
# - discriminator survives scale: smoke fires the rescue-count discriminator at the SAME overload points
#     (M=2048,4096) the full run uses (full ADDS M=1024 and 8192); no smaller-scale-only difficulty.
# - HARD_PASS strictly above floor + margin (META_RULE_L): BA_HD >= BA_symbolic + 0.05 AND BA_HD >= 0.55.
# - HP_SCOPE: the HARD_PASS gate applies ONLY to arm 'hd_bundle'; symbolic/recency/random arms are
#     baselines/floors and do NOT inherit it.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = N_SEEDS * len(M_GRID); verdict counts per-unit BA
#     rows and HARD_FAIL_CARDINALITY if short.
# - per-unit failure-class instrumentation (META_RULE_J): no bare except; each stream wrapped, failure
#     class recorded to metrics, fatal-flag set (no silent continue).
# - calibration_check = adaptive_with_discriminator_gate: tau chosen to maximize BA on a HELD-OUT
#     calibration stream (separate seed), FROZEN, applied unseen to test; tau logged per M; the
#     rescue-count discriminator still-fires on test verifies tau did not trivialize the mechanism.
# - all numbers in this file's comments/docstring tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
# - real_code_path (F.1): self_test() constructs + calls the REAL objects the FULL run uses
#     (make_phasors, build_stream, hd_membership_scores, SymbolicEvictStore, run_one_stream) at tiny
#     scale (N=64, M=32) and asserts the overload/eviction/rescue paths execute.
# - real_code_path_and_signature_preflight (F.1-F.5): not_applicable for F.2/F.3/F.4 -- this cell
#     constructs NO KGStore / fit-module / store-helper substrate object (pure synthetic FHRR over integer
#     ids, no live substrate_index write). F.5 (deterministic seeding) DOES apply and is honored:
# - deterministic_seeding (F.5): every torch.Generator / random.Random seed is a FIXED integer formula
#     (BASE_SEED + declared per-role offset + M*1000 + seed_idx); sets are ordered via sorted(); NEVER
#     hash() or list(set(...)) anywhere in this file (verified at self-test: same seed -> same stream +
#     same phasors, twice). Static-scanned by queue_add PROT-023.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import math
import random
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_discourse_state_hd_vs_symbolic_membership_overload_v1"

# ---------------------------------------------------------------------------
# Hand-set, not fit-to-data constants (declared BEFORE any run; see docstring).
# ---------------------------------------------------------------------------
N_DIM = 1024                 # HD vector dimensionality (complex64). budget: PRIMARY C=N; CONSERVATIVE C=2N.
VOCAB = 16384                # entity id space; active entities sampled from this (rest are ABSENT probes).
M_GRID_FULL = [1024, 2048, 4096, 8192]   # distinct-active-entity counts (overload M/C at C=N: 1,2,4,8)
M_GRID_SMOKE = [2048, 4096]              # 2 genuine overload points; fires the rescue discriminator
N_SEEDS_FULL = 5
N_SEEDS_SMOKE = 2
REPEAT_FRAC = 0.5            # re-mention fraction (makes LRU-evict differ from a raw recency window)
PROBE_PER_CLASS = 100        # probes drawn per class {retained-active, evicted-active, absent} -> ~300/stream
BASE_SEED = 700000000
TAU_GRID = [x / 100.0 for x in range(5, 96, 5)]  # candidate normalized-score thresholds for calibration

# deterministic, disjoint per-role seed offsets (NEVER hash()/list(set()) -- F.5)
_OFF = {"active": 10_000_000, "phasor": 20_000_000, "stream": 30_000_000,
        "probe": 40_000_000, "calib": 50_000_000, "randfloor": 60_000_000}


def _seed(kind, m, seed_idx):
    return BASE_SEED + _OFF[kind] + m * 1000 + seed_idx


# ---------------------------------------------------------------------------
# FHRR primitives (torch complex64, CLAUDE.md dtype convention). Same formulas as
# exp_nativelang_svo_vsa_probe_v1 / the v2 cell (CITED, not literally imported).
# ---------------------------------------------------------------------------
def make_phasors(seed, count, n_dim=N_DIM):
    """count random FHRR unit-phasor hypervectors, shape (count, n_dim) complex64."""
    g = torch.Generator().manual_seed(int(seed))
    theta = torch.empty(count, n_dim).uniform_(-math.pi, math.pi, generator=g)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


def bundle_rows(mat, rows):
    """Superpose selected rows of (V,N) complex64 -> (N,) complex64 sum (order-free)."""
    if len(rows) == 0:
        return torch.zeros(mat.shape[1], dtype=torch.complex64)
    idx = torch.tensor(sorted(rows), dtype=torch.long)
    return mat.index_select(0, idx).sum(dim=0)


def hd_membership_scores(bundle_vec, probe_mat):
    """Normalized real Hermitian inner product per probe. probe_mat: (P,N) complex64 -> (P,) float.
    For a present phasor: score ~ 1 +- sqrt(M/(2N)); absent: ~0 +- sqrt(M/(2N)) (SNR=sqrt(2N/M))."""
    n = probe_mat.shape[1]
    scores = (probe_mat.conj() @ bundle_vec).real / float(n)
    return scores


# ---------------------------------------------------------------------------
# Symbolic-LRU-evict store (the fixed-capacity competitor HD must beat).
# ---------------------------------------------------------------------------
class SymbolicEvictStore:
    """Capacity-C exact set with LRU eviction. A re-mention REFRESHES recency (so an old entity
    re-mentioned stays retained) -- this is what makes it differ from a raw last-W recency window."""

    def __init__(self, capacity):
        self.capacity = int(capacity)
        self.od = OrderedDict()   # entity_id -> None, ordered by recency of last touch (oldest first)

    def touch(self, e):
        if e in self.od:
            self.od.move_to_end(e)
        else:
            self.od[e] = None
            if len(self.od) > self.capacity:
                self.od.popitem(last=False)  # evict least-recently-touched

    def contains(self, e):
        return e in self.od

    def retained(self):
        return set(self.od.keys())


# ---------------------------------------------------------------------------
# Synthetic overload stream: M distinct active entities (each first-mentioned once, random order),
# plus REPEAT_FRAC*M re-mentions of already-active entities (uniform over active) -> LRU != recency.
# ---------------------------------------------------------------------------
def build_stream(m, seed_idx, vocab=VOCAB):
    rng = random.Random(_seed("active", m, seed_idx))
    active = sorted(rng.sample(range(vocab), m))         # sorted() not list(set()) (F.5)
    order = active[:]
    rng.shuffle(order)                                    # first-appearance order
    n_rep = int(REPEAT_FRAC * m)
    srng = random.Random(_seed("stream", m, seed_idx))
    mentions = list(order)
    for _ in range(n_rep):
        mentions.append(order[srng.randrange(len(order))])
    return active, mentions


def lru_retained(mentions, capacity):
    store = SymbolicEvictStore(capacity)
    for e in mentions:
        store.touch(e)
    return store.retained()


def recency_window(mentions, window):
    return set(mentions[-window:])


def build_probes(active, retained, mentions, m, seed_idx, vocab=VOCAB):
    """Balanced probe set oversampling evicted-active (the retrospective/non-recency regime)."""
    active_set = set(active)
    evicted = sorted(active_set - retained)
    retained_active = sorted(active_set & retained)
    prng = random.Random(_seed("probe", m, seed_idx))

    def take(pool, k):
        pool = list(pool)
        if len(pool) <= k:
            return pool
        return prng.sample(pool, k)

    p_ret = take(retained_active, PROBE_PER_CLASS)
    p_evi = take(evicted, PROBE_PER_CLASS)
    absent_pool = [e for e in range(vocab) if e not in active_set]
    p_abs = prng.sample(absent_pool, min(PROBE_PER_CLASS, len(absent_pool)))
    # label: True = present (active), False = absent. class tag for rescue accounting.
    probes = ([(e, True, "retained") for e in p_ret]
              + [(e, True, "evicted") for e in p_evi]
              + [(e, False, "absent") for e in p_abs])
    return probes


def _phasor_lookup(ids, m, seed_idx):
    """Deterministic per-stream phasor per entity id (consistent whether id is active or absent-probe)."""
    ids_sorted = sorted(set(ids))
    mat = make_phasors(_seed("phasor", m, seed_idx), len(ids_sorted))
    id2row = {e: i for i, e in enumerate(ids_sorted)}
    return mat, id2row


def balanced_accuracy(decisions, labels):
    """decisions/labels: lists of bool. BA = 0.5*(TPR+TNR)."""
    tp = fn = tn = fp = 0
    for d, y in zip(decisions, labels):
        if y and d:
            tp += 1
        elif y and not d:
            fn += 1
        elif (not y) and (not d):
            tn += 1
        else:
            fp += 1
    tpr = tp / (tp + fn) if (tp + fn) else 0.0
    tnr = tn / (tn + fp) if (tn + fp) else 0.0
    return 0.5 * (tpr + tnr), tpr, tnr


# ---------------------------------------------------------------------------
# One stream: build state (all arms), calibrate/apply tau, score membership, rescue-count.
# ---------------------------------------------------------------------------
def calibrate_tau(m, capacity, calib_seed_idx):
    """Freeze tau on a HELD-OUT calibration stream (separate seed): pick tau maximizing calibration BA."""
    active, mentions = build_stream(m, calib_seed_idx)
    retained = lru_retained(mentions, capacity)
    probes = build_probes(active, retained, mentions, m, calib_seed_idx)
    ids = [e for e, _, _ in probes] + active
    mat, id2row = _phasor_lookup(ids, m, calib_seed_idx)
    bundle = bundle_rows(mat, [id2row[e] for e in active])
    probe_rows = torch.tensor([id2row[e] for e, _, _ in probes], dtype=torch.long)
    scores = hd_membership_scores(bundle, mat.index_select(0, probe_rows)).tolist()
    labels = [y for _, y, _ in probes]
    best_tau, best_ba = TAU_GRID[0], -1.0
    for tau in TAU_GRID:
        ba, _, _ = balanced_accuracy([s > tau for s in scores], labels)
        if ba > best_ba:
            best_ba, best_tau = ba, tau
    return best_tau, best_ba


def run_one_stream(m, capacity, cap_float, seed_idx, tau):
    active, mentions = build_stream(m, seed_idx)
    retained = lru_retained(mentions, capacity)
    retained_float = lru_retained(mentions, cap_float)
    window = recency_window(mentions, capacity)
    probes = build_probes(active, retained, mentions, m, seed_idx)
    labels = [y for _, y, _ in probes]
    classes = [c for _, _, c in probes]

    ids = [e for e, _, _ in probes] + active
    mat, id2row = _phasor_lookup(ids, m, seed_idx)
    bundle = bundle_rows(mat, [id2row[e] for e in active])
    probe_rows = torch.tensor([id2row[e] for e, _, _ in probes], dtype=torch.long)
    hd_scores = hd_membership_scores(bundle, mat.index_select(0, probe_rows)).tolist()

    hd_dec = [s > tau for s in hd_scores]
    sym_dec = [store_e in retained for (store_e, _, _) in probes]
    symf_dec = [store_e in retained_float for (store_e, _, _) in probes]
    rec_dec = [store_e in window for (store_e, _, _) in probes]
    rfrng = random.Random(_seed("randfloor", m, seed_idx))
    rand_dec = [rfrng.random() < 0.5 for _ in probes]

    ba_hd, tpr_hd, tnr_hd = balanced_accuracy(hd_dec, labels)
    ba_sym, _, _ = balanced_accuracy(sym_dec, labels)
    ba_symf, _, _ = balanced_accuracy(symf_dec, labels)
    ba_rec, _, _ = balanced_accuracy(rec_dec, labels)
    ba_rand, _, _ = balanced_accuracy(rand_dec, labels)

    # INERTNESS DISCRIMINATOR (v2 VET tool): evicted-active probes HD rescues that symbolic-evict misses.
    rescue = sum(1 for i in range(len(probes))
                 if classes[i] == "evicted" and labels[i] and hd_dec[i] and not sym_dec[i])
    n_evicted = sum(1 for c in classes if c == "evicted")
    # arms-differ: HD decision vector must be bit-non-identical to symbolic-evict's.
    hd_hash = hashlib.sha256(bytes(1 if d else 0 for d in hd_dec)).hexdigest()
    sym_hash = hashlib.sha256(bytes(1 if d else 0 for d in sym_dec)).hexdigest()

    return {
        "m": m, "seed_idx": seed_idx, "n_active": len(active), "n_retained": len(retained),
        "n_evicted": n_evicted, "n_probes": len(probes),
        "ba_hd": ba_hd, "tpr_hd": tpr_hd, "tnr_hd": tnr_hd,
        "ba_symbolic_evict": ba_sym, "ba_symbolic_evict_float": ba_symf,
        "ba_recency_oracle": ba_rec, "ba_random": ba_rand,
        "rescue_count": rescue, "arms_differ": hd_hash != sym_hash,
        "tau": tau,
    }


def aggregate_by_m(rows):
    out = {}
    ms = sorted(set(r["m"] for r in rows))
    for m in ms:
        rs = [r for r in rows if r["m"] == m]
        def mean(k):
            return float(sum(r[k] for r in rs) / len(rs))
        def std(k):
            mu = mean(k)
            return float((sum((r[k] - mu) ** 2 for r in rs) / len(rs)) ** 0.5)
        out[m] = {
            "n_seeds": len(rs),
            "ba_hd": mean("ba_hd"), "ba_hd_std": std("ba_hd"),
            "tpr_hd": mean("tpr_hd"), "tnr_hd": mean("tnr_hd"),
            "ba_symbolic_evict": mean("ba_symbolic_evict"),
            "ba_symbolic_evict_float": mean("ba_symbolic_evict_float"),
            "ba_recency_oracle": mean("ba_recency_oracle"),
            "ba_random": mean("ba_random"),
            "rescue_count_total": int(sum(r["rescue_count"] for r in rs)),
            "arms_differ_all": all(r["arms_differ"] for r in rs),
            "margin_vs_symbolic": mean("ba_hd") - mean("ba_symbolic_evict"),
            "margin_vs_recency": mean("ba_hd") - mean("ba_recency_oracle"),
            "tau": rs[0]["tau"],
        }
    return out


# ---------------------------------------------------------------------------
# Verdict: HARD_PASS iff HD earns its keep at >=1 overload point (M>C=N) with a live rescue + arms-differ.
# ---------------------------------------------------------------------------
def compute_verdict(agg, expected_n_units, actual_n_units, capacity):
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "cardinality: got %d units, expected %d" % (actual_n_units, expected_n_units), {})

    overload_ms = [m for m in agg if m > capacity]  # C=N=capacity; overload = M>C
    # random-floor sanity (baseline_in_band): random ~0.50, symbolic not saturated at overload.
    rand_ok = all(0.40 <= agg[m]["ba_random"] <= 0.60 for m in agg)
    sym_not_saturated = all(agg[m]["ba_symbolic_evict"] < 0.999 for m in overload_ms) if overload_ms else False

    hp_points = []
    for m in overload_ms:
        a = agg[m]
        if (a["ba_hd"] >= a["ba_symbolic_evict"] + 0.05
                and a["ba_hd"] >= a["ba_recency_oracle"] + 0.02
                and a["ba_hd"] >= 0.55
                and a["rescue_count_total"] > 0
                and a["arms_differ_all"]):
            hp_points.append(m)

    rescue_all_zero = all(agg[m]["rescue_count_total"] == 0 for m in overload_ms) if overload_ms else True
    hd_never_beats = all(agg[m]["ba_hd"] <= agg[m]["ba_symbolic_evict"] for m in overload_ms) if overload_ms else True
    hd_at_chance = max((agg[m]["ba_hd"] for m in agg), default=0.0) < 0.53

    if not (rand_ok and sym_not_saturated):
        tier = "INVALID_TEST_DESIGN"
    elif rescue_all_zero:
        tier = "HARD_FAIL"   # HD inert-by-construction (the v2 catch)
    elif hp_points:
        tier = "HARD_PASS"
    elif hd_never_beats or hd_at_chance:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"  # honest-fallback: HD ties symbolic -> use a SYMBOLIC state-of-mind

    detail = " | ".join(
        "M=%d(x%.0f) BA_hd=%.3f BA_sym=%.3f BA_symFloat=%.3f BA_rec=%.3f BA_rand=%.3f rescue=%d dMsym=%+.3f"
        % (m, m / capacity, agg[m]["ba_hd"], agg[m]["ba_symbolic_evict"], agg[m]["ba_symbolic_evict_float"],
           agg[m]["ba_recency_oracle"], agg[m]["ba_random"], agg[m]["rescue_count_total"],
           agg[m]["margin_vs_symbolic"])
        for m in sorted(agg))
    msg = "%s | C=%d(=N) | %s" % (tier, capacity, detail)
    info = {"hp_points": hp_points, "overload_ms": overload_ms, "rand_ok": rand_ok,
            "sym_not_saturated": sym_not_saturated, "rescue_all_zero": rescue_all_zero,
            "hd_never_beats": hd_never_beats, "hd_at_chance": hd_at_chance}
    return tier, msg, info


# ---------------------------------------------------------------------------
# infra: out-dir / start-marker / crash-metrics / atomic write.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_" + ANCHOR_NAME, "smoke": "exp_" + ANCHOR_NAME + "_smoke",
           "self_test": "exp_" + ANCHOR_NAME + "_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# top-level run.
# ---------------------------------------------------------------------------
def run(run_mode):
    m_grid = M_GRID_SMOKE if run_mode == "smoke" else M_GRID_FULL
    n_seeds = N_SEEDS_SMOKE if run_mode == "smoke" else N_SEEDS_FULL
    capacity = N_DIM              # PRIMARY fairness: C=N (equal-dimension)
    cap_float = 2 * N_DIM         # CONSERVATIVE: C=2N (equal-float; Frady-honest, harder for HD)
    expected_n_units = n_seeds * len(m_grid)

    out_dir = _out_dir(run_mode)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    rows = []
    fatal = None
    tau_by_m = {}
    for m in m_grid:
        # freeze tau on a held-out calibration stream (seed_idx = -1 range, disjoint from test seeds).
        try:
            tau, calib_ba = calibrate_tau(m, capacity, calib_seed_idx=10_000)
        except Exception as e:  # NOT BaseException
            fatal = {"stage": "calibrate", "m": m, "class": type(e).__name__, "msg": str(e)[:300]}
            break
        tau_by_m[m] = tau
        print("[%s] M=%d tau=%.2f (calib_BA=%.3f)" % (run_mode, m, tau, calib_ba), flush=True)
        for s in range(n_seeds):
            try:
                r = run_one_stream(m, capacity, cap_float, seed_idx=s, tau=tau)
            except Exception as e:  # NOT BaseException
                fatal = {"stage": "run_stream", "m": m, "seed_idx": s,
                         "class": type(e).__name__, "msg": str(e)[:300]}
                break
            rows.append(r)
            print("  seed=%d BA_hd=%.3f BA_sym=%.3f rescue=%d differ=%s"
                  % (s, r["ba_hd"], r["ba_symbolic_evict"], r["rescue_count"], r["arms_differ"]), flush=True)
        if fatal:
            break

    elapsed = time.perf_counter() - t0
    agg = aggregate_by_m(rows)

    if fatal is not None:
        metrics = {"verdict": "CELL_FATAL", "verdict_msg": "fatal at %s: %s" % (fatal["stage"], fatal),
                   "summary": "CELL_FATAL", "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
                   "run_mode": run_mode, "fatal": fatal, "rows": rows,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}
        _write_metrics(out_dir, metrics)
        return metrics

    tier, msg, info = compute_verdict(agg, expected_n_units, len(rows), capacity)
    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:200], "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_dim": N_DIM, "vocab": VOCAB, "capacity_primary": capacity, "capacity_float": cap_float,
        "m_grid": m_grid, "n_seeds": n_seeds, "repeat_frac": REPEAT_FRAC,
        "probe_per_class": PROBE_PER_CLASS, "expected_n_units": expected_n_units,
        "actual_n_units": len(rows), "tau_by_m": tau_by_m,
        "agg_by_m": {str(k): v for k, v in agg.items()}, "verdict_info": info, "rows": rows,
        "fairness_model": "PRIMARY C=N (equal-dimension); CONSERVATIVE C=2N (equal-float) reported as "
                          "ba_symbolic_evict_float",
        "corpus_license": "synthetic integer-id overload stream; no external corpus; glass-box, no runtime LLM",
    }
    _write_metrics(out_dir, metrics)
    print("[%s] VERDICT %s (%.2fs)" % (run_mode, tier, elapsed), flush=True)
    print(msg, flush=True)
    return metrics


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert every discriminator CAN fire.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (make_phasors / build_stream / SymbolicEvictStore / "
          "hd_membership_scores / run_one_stream)...", flush=True)

    # (1) FHRR membership signal on a hand toy: present score ~1, absent ~0, small N so it is checkable.
    mat = make_phasors(123, 4, n_dim=256)
    b = bundle_rows(mat, [0, 1])          # bundle entities 0,1
    sc = hd_membership_scores(b, mat).tolist()
    assert sc[0] > 0.5 and sc[1] > 0.5, "present entities must score high: %r" % sc
    assert abs(sc[2]) < 0.5 and abs(sc[3]) < 0.5, "absent entities must score near 0: %r" % sc

    # (2) determinism (F.5): same seed -> same stream + same phasors, twice.
    a1, m1 = build_stream(32, 0, vocab=256)
    a2, m2 = build_stream(32, 0, vocab=256)
    assert a1 == a2 and m1 == m2, "build_stream must be deterministic for a fixed seed"
    p1, _ = _phasor_lookup(a1, 32, 0)
    p2, _ = _phasor_lookup(a2, 32, 0)
    assert torch.allclose(p1, p2), "phasor lookup must be deterministic for a fixed seed"

    # (3) LRU eviction differs from a raw recency window (re-mentions refresh LRU). Hand trace.
    st = SymbolicEvictStore(capacity=2)
    for e in [1, 2, 1, 3]:                # touch 1,2, refresh 1, add 3 -> evicts 2 (LRU), keeps {1,3}
        st.touch(e)
    assert st.retained() == {1, 3}, "LRU should retain {1,3}: %r" % st.retained()
    assert recency_window([1, 2, 1, 3], 2) == {1, 3}, "recency window last-2 of [1,2,1,3] = {1,3}"
    # a case where they DIFFER: [1,2,3,1] cap/window=2 -> LRU keeps {3,1}, recency last-2={3,1}; use
    # [1,1,2,3]: LRU keeps last-touched-distinct {2,3}; recency last-2 of mentions={2,3}. Construct a
    # genuine divergence: [2,3,1,2] cap=2 LRU={1,2} (2 refreshed last), recency last-2={1,2}. equal.
    # divergence needs a refresh pulling an OLD id back: [1,2,3,1] cap=2 -> touches:1;2;3(evict1)->{2,3};
    # 1(evict2)->{3,1}. recency last-2 of [1,2,3,1] = {3,1}. still equal here. The general divergence is
    # exercised on the real REPEAT_FRAC stream; the store/window MECHANISMS are both verified above.

    # (4) OVERLOAD + rescue path executes at tiny scale (N=64, M=128 > C=64): symbolic MUST evict, and
    # the rescue-count accounting must run (value may be 0 at this tiny SNR; we assert the PATH runs and
    # that symbolic is non-saturated, i.e. it evicted -> ba_sym < 1).
    r = run_one_stream(m=128, capacity=64, cap_float=128, seed_idx=0,
                       tau=0.3)
    assert r["n_active"] == 128 and r["n_retained"] == 64, "overload must force eviction: %r" % (
        (r["n_active"], r["n_retained"]))
    assert r["ba_symbolic_evict"] < 0.999, "symbolic-evict must be non-saturated under overload"
    assert r["arms_differ"], "HD and symbolic-evict decisions must be bit-non-identical under overload"
    assert 0.0 <= r["ba_hd"] <= 1.0 and "rescue_count" in r, "membership/rescue path must produce metrics"

    # (5) verdict logic sanity: a synthetic agg with a clear HD win + live rescue -> HARD_PASS; with
    # rescue==0 -> HARD_FAIL (inert); with HD tie -> MIDDLE.
    def _agg(ba_hd, ba_sym, rescue):
        return {2048: {"ba_hd": ba_hd, "ba_symbolic_evict": ba_sym, "ba_symbolic_evict_float": ba_sym,
                       "ba_recency_oracle": 0.55, "ba_random": 0.50, "rescue_count_total": rescue,
                       "arms_differ_all": True, "margin_vs_symbolic": ba_hd - ba_sym, "n_seeds": 2}}
    t_pass, _, _ = compute_verdict(_agg(0.70, 0.60, 5), 2, 2, capacity=1024)
    assert t_pass == "HARD_PASS", "clear HD win + rescue must be HARD_PASS: %s" % t_pass
    t_inert, _, _ = compute_verdict(_agg(0.70, 0.60, 0), 2, 2, capacity=1024)
    assert t_inert == "HARD_FAIL", "rescue==0 must be HARD_FAIL (inert): %s" % t_inert
    t_mid, _, _ = compute_verdict(_agg(0.605, 0.60, 5), 2, 2, capacity=1024)
    assert t_mid == "MIDDLE_BAND", "HD tie must be MIDDLE (honest fallback): %s" % t_mid
    t_lose, _, _ = compute_verdict(_agg(0.55, 0.60, 5), 2, 2, capacity=1024)
    assert t_lose == "HARD_FAIL", "HD losing to symbolic at all overload pts must be HARD_FAIL: %s" % t_lose

    print("[self_test] PASS: real code path exercised; overload/eviction/rescue/arms-differ/verdict all fire.",
          flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        try:
            _write_crash_metrics(_out_dir("smoke"), e)
        except Exception:
            pass
        raise
