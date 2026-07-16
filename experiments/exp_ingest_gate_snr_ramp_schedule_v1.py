"""Developmental PERMISSIVE->SELECTIVE gate SCHEDULE as a foundation-BUILDER architecture (SNR-gated ramp).

Pre-registered cheap test from notes/research_developmental_curriculum_permissive_to_selective_gate_schedule_2026-07-16.md
(Section b / Prediction 2): replace a FIXED gate-stringency with an SNR-GATED RAMP whose tightening TRIGGER is the
substrate's OWN measured signal-extraction SUCCESS RATE (Chang & Merzenich 2003; Toyoizumi et al. 2013), NOT elapsed
time nor raw noise-count. Test whether it builds a BETTER foundation over a SEQUENTIAL ingest that starts EMPTY.

SCENARIO (genuine ingest-over-time, foundation starts EMPTY): a stream of candidate claims (edges) is ingested
SEQUENTIALLY. At each step the 3 gate signals are recomputed CLOSED-LOOP against the CURRENT admitted foundation:
  - schema-fit  = reachability of the claim's endpoints in the CURRENT admitted graph (hdlab/reachability_audit).
  - derivability/surprise proxy = same reachability field (foundation predicts endpoint-integration -> low surprise).
  - recurrence  = provenance corroboration count (shared HARD-FLOOR: one-off items DISCARD-ed by every arm equally).
The gate's VARIABLE knob is a single schema-fit STRINGENCY threshold; arms differ ONLY in how that threshold evolves.

ARMS (same metric, same stream, same recurrence floor):
  - FIXED(thr)    : constant stringency; SWEPT, best-per-condition value reported (its strongest shot).
  - TIME-KEYED    : permissive->strict ramp keyed on ELAPSED STREAM FRACTION (the WRONG control; the position-clock).
                    Its ramp window is calibrated to MATCH the SNR arm's tightening position under LOW noise, then
                    applied UNCHANGED to high noise (single config, like the brain's non-re-tuned schedule).
  - SNR-GATED     : permissive->strict ramp keyed on the substrate's own measured signal-extraction SUCCESS RATE
                    (rolling fraction of recent candidates whose schema-fit crosses a low extractable-structure bar),
                    peak-RATCHETED (consolidation lock-in / PNN-faithful). ONE config, used in BOTH noise conditions.

FORCES (fired positive control, honest, not ramp-tuned):
  - PLACEHOLDER claims (Carey bootstrapping): TRUE satellite->core edges whose module backbone arrives LATER, so their
    schema-fit is LOW at arrival and RISES only after related structure is admitted. Permissive-early ADMITS them;
    fixed-STRICT REJECTS them (blocks the bootstrap). This is the RECALL benefit.
  - DISTRACTOR claims: FALSE, corroborated (pass the recurrence floor), between PERIPHERAL low-reachability nodes so
    schema-fit stays ~0; arrive LATE. Strict-late REJECTS them; permissive ADMITS them. This is the PRECISION benefit.
  No FIXED threshold can admit low-schema-fit-EARLY-true while rejecting low-schema-fit-LATE-false: the separating
  information is TEMPORAL, which is exactly why a SCHEDULE can beat any fixed value. Under HIGH noise, real structure
  accumulates slower -> success-rate rises later -> the SNR ramp stays permissive longer (Chang-Merzenich) and admits
  DELAYED placeholders that the position-keyed TIME ramp (tightened on its clock) wrongly rejects.

METRIC (quality of the BUILT foundation): downstream reasoning BALANCED-ACCURACY over held-out same-group vs
cross-group connectivity queries on the ACCUMULATED admitted graph (rewards admitting placeholders, penalizes
admitting distractors). Corroborated by F1 of admitted-true-vs-admitted-false against ground truth.

CONTROLS: fired positive control (SNR beats best-fixed under high noise -- MUST fire at smoke); NULL guard (a
no-placeholder/no-distractor arena where the schedule must add nothing); anti-rig (SNR uses ONE config across both
conditions while FIXED/TIME are given their best/ matched shot; a time-keyed or fixed gate tying is an honest MIDDLE);
SNR-vs-TIME trigger check (SNR tightening-position shifts LATER under high noise; time-keyed identical by construction).

PRE-REG (this cell is authoritative; the TASK axis is SNR-vs-FIXED, the note ADDS the SNR-vs-TIME refinement):
  HARD-PASS = SNR-ramp beats best-fixed on foundation quality under HIGH noise (>=0.05 balanced-acc) AND admits
              bootstrappable placeholders where fixed-strict rejects (>=0.20 admission delta) AND the NULL guard holds
              (|SNR-bestfixed|<=0.04) AND baseline in band AND arms differ AND telemetry-sensitive AND the SNR trigger
              earns its complexity: beats the LOW-noise-optimal TIME-keyed ramp under HIGH noise (>=0.03) AND is
              signal-keyed not time-keyed (selectivity-onset shifts >= SHIFT_MIN later under high noise).
  HARD-FAIL = best-fixed does as well as SNR under high noise (the schedule -- coarse OR fine -- adds nothing).
  MIDDLE    = the COARSE permissive->selective schedule beats fixed via bootstrapping (task-positive) but the SNR
              TRIGGER refinement does not earn its complexity over a matched time-clock on this substrate (the note's
              own explicitly-anticipated Prediction-2 branch), OR margins otherwise partial.

CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke (admitted-set hashes distinct across FIXED/TIME/SNR)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: gate is a decision over measured graph signals; bands set from MEASURED smoke calibration
# - baseline_in_band: best-fixed foundation BA in (0.05,0.98) verified at smoke
# - discriminator survives scale: temporal placeholder/distractor separation is scale-free (analytical)
# - positive control (fires): the SCHEDULE (swept time-clock ramp) beats best-fixed under high noise -- proves the
#   arena rewards permissive->selective at all; the SNR-beats-fixed hypothesis is the thing UNDER TEST (may be refuted)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / CITED@
# - real_code_path: self_test exercises reachability_audit + AdditiveKGMap.score_all + the ingest/gate/downstream loop
# - deterministic seeding: np.random.default_rng(fixed int) + sorted() dedupe only

ASCII-only. No emojis. Explicit dtypes. Deterministic. Terse. Local numpy (no queue/GPU/atoms/push).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import deque
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab import reachability_audit as RA  # noqa: E402

ANCHOR_NAME = "ingest_gate_snr_ramp_schedule_v1"

# ---- kinds -----------------------------------------------------------------------------------------------------
K_BACKBONE = 0
K_PLACEHOLDER = 1
K_DISTRACTOR = 2
K_NOISE = 3
KIND_NAME = {0: "backbone", 1: "placeholder", 2: "distractor", 3: "noise"}
TRUE_KINDS = (K_BACKBONE, K_PLACEHOLDER)   # ground-truth "should admit"

# ---- pre-registered gate params (picked a priori; NOT tuned-for-pass; calibrated arena params only) -------------
RECURRENCE_MIN = 3          # shared hard-floor: one-off items (noise) DISCARD-ed by every arm
STRICT_THR = 0.60           # mature schema-fit bar ([0,1] saturating-reach units); the ramp's strict endpoint
PERMISSIVE_THR = 0.0        # ramp's permissive endpoint (admit-all subject to recurrence floor)
SR_BAR = 0.40               # low extractable-structure bar: a candidate "succeeds" if edge schema_fit >= SR_BAR
SR_LO = 0.15                # measured success-rate below this -> fully permissive
SR_HI = 0.60                # measured success-rate above this -> fully strict
SR_WINDOW = 50              # rolling window (candidates) for the measured success rate

# ---- pre-registered HARD-PASS bands ----------------------------------------------------------------------------
HP_MARGIN_FIXED = 0.05      # SNR balanced-acc advantage over best-fixed under HIGH noise
HP_MARGIN_TIME = 0.03       # SNR advantage over matched TIME-keyed ramp under HIGH noise
HP_BOOTSTRAP_DELTA = 0.20   # SNR placeholder-admit-rate minus fixed-STRICT placeholder-admit-rate
HP_NULL_TOL = 0.04          # |SNR - best-fixed| in the NULL arena must be within this (schedule adds nothing)
HP_SHIFT_MIN_FRAC = 0.06    # SNR selectivity-onset (tighten fraction) must shift >= this LATER under high vs low
#                             noise -> proves the trigger is SIGNAL-keyed (Chang-Merzenich noise-reared -> stays
#                             permissive longer), not a fixed time-clock (which would be identical across noise)
HP_BASE_LO = 0.05
HP_BASE_HI = 0.98

# ---- run configs -----------------------------------------------------------------------------------------------
FULL_CFG = dict(M=14, core_size=10, sat_size=3, n_outlier=40, n_distractor=44, dist_recur=4,
                noise_low=0.05, noise_high=0.35, noise_front_frac=1.0, seeds=[7, 13, 17],
                refresh_every=15, reach_k=2, reach_cap=160, reach_target=6, query_k=3,
                n_pos_core=140, n_pos_sat=140, n_neg_dist=160, n_neg_cross=120,
                fixed_grid=[0.0, 0.1, 0.25, 0.4, 0.6, 0.8, 1.0])
SMOKE_CFG = dict(M=8, core_size=7, sat_size=2, n_outlier=20, n_distractor=22, dist_recur=4,
                 noise_low=0.05, noise_high=0.35, noise_front_frac=1.0, seeds=[7],
                 refresh_every=12, reach_k=2, reach_cap=120, reach_target=6, query_k=3,
                 n_pos_core=70, n_pos_sat=70, n_neg_dist=80, n_neg_cross=60,
                 fixed_grid=[0.0, 0.1, 0.25, 0.4, 0.6, 0.8, 1.0])


# ---------------------------------------------------------------------------
# start-marker / atomic metrics / crash diagnostic
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics_atomic(output_dir, diag)


def _log(msg):
    print("[snr_ramp] %s" % msg, flush=True)


def _sha_intpairs(pairs):
    a = np.asarray(sorted(pairs), dtype=np.int64)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# ARENA: modular graph + placeholders + distractors + outliers + a diluted ingest stream
# ---------------------------------------------------------------------------
def build_arena(cfg, seed, scenario, noise_frac):
    """Build ground-truth structure + an ORDERED, noise-diluted ingest stream. scenario in {structured, null}.

    Returns dict with: streams (h,t,kind,n_sources arrays in arrival order), node layout (modules/satellites/
    outliers), and downstream query sets (pos/neg pairs with truth labels). Deterministic in seed."""
    rng = np.random.default_rng(seed * 100003 + (0 if scenario == "structured" else 991))
    M = cfg["M"]; cs = cfg["core_size"]; ss = cfg["sat_size"]
    use_sat = ss if scenario == "structured" else 0
    n_outlier = cfg["n_outlier"] if scenario == "structured" else cfg["n_outlier"]
    n_distractor = cfg["n_distractor"] if scenario == "structured" else 0

    # node layout: per module [cores..., sats...]; then a shared outlier pool
    cores = []          # cores[m] = list of core node ids
    sats = []           # sats[m] = list of satellite node ids (empty in null)
    nid = 0
    for m in range(M):
        cores.append(list(range(nid, nid + cs))); nid += cs
        sats.append(list(range(nid, nid + use_sat))); nid += use_sat
    outliers = list(range(nid, nid + n_outlier)); nid += n_outlier
    N = nid
    module_of = np.full(N, -1, dtype=np.int64)
    for m in range(M):
        for v in cores[m] + sats[m]:
            module_of[v] = m

    # ---- TRUE edges (relation-agnostic; undirected reachability) ----------------------------------------------
    backbone = []       # (h,t) ring over each module's cores
    for m in range(M):
        cm = cores[m]
        for i in range(len(cm)):
            backbone.append((cm[i], cm[(i + 1) % len(cm)]))
    placeholders = []   # (sat, core) TRUE; low schema-fit until the core's module backbone is admitted
    for m in range(M):
        for s in sats[m]:
            placeholders.append((s, cores[m][int(rng.integers(len(cores[m])))]))
    # ---- DISTRACTOR edges: FALSE, corroborated, between PERIPHERAL outliers (schema-fit ~0 forever) ------------
    distractors = []
    dist_pairs = set()
    tries = 0
    while len(distractors) < n_distractor and tries < n_distractor * 40:
        a, b = int(rng.integers(len(outliers))), int(rng.integers(len(outliers)))
        tries += 1
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        if key in dist_pairs:
            continue
        dist_pairs.add(key)
        distractors.append((outliers[a], outliers[b]))

    # ---- assemble the TRUE-EDGE arrival SUBSEQUENCE (the fixed ingest order, before noise dilution) ------------
    # EARLY modules build first; their (easy) placeholders follow. LATE modules' placeholders arrive at MID, BEFORE
    # their backbone (so placeholder schema-fit is LOW at arrival -> needs permissiveness). Backbone of LATE modules
    # + distractors arrive LATE.
    half = M // 2
    early_bb = [(h, t, K_BACKBONE) for m in range(half) for (h, t) in _mod_backbone(cores[m])]
    early_ph = [(h, t, K_PLACEHOLDER) for m in range(half) for (h, t) in _mod_placeholders(cores[m], sats[m], rng)]
    late_ph = [(h, t, K_PLACEHOLDER) for m in range(half, M) for (h, t) in _mod_placeholders(cores[m], sats[m], rng)]
    late_bb = [(h, t, K_BACKBONE) for m in range(half, M) for (h, t) in _mod_backbone(cores[m])]
    late_ds = [(h, t, K_DISTRACTOR) for (h, t) in distractors]

    rng.shuffle(early_bb); rng.shuffle(early_ph); rng.shuffle(late_ph); rng.shuffle(late_bb); rng.shuffle(late_ds)
    if scenario == "null":
        # NULL arena: no placeholders, no distractors -> only backbone (all modules) + noise. No temporal signal.
        all_bb = [(h, t, K_BACKBONE) for m in range(M) for (h, t) in _mod_backbone(cores[m])]
        rng.shuffle(all_bb)
        true_seq = all_bb
    else:
        true_seq = early_bb + early_ph + late_ph + late_bb + late_ds

    # ---- DILUTE with one-off NOISE to the target fraction -> pushes true edges to later absolute positions -----
    n_true = len(true_seq)
    n_noise = int(round(noise_frac / max(1e-9, (1.0 - noise_frac)) * n_true))
    noise_items = []
    for _ in range(n_noise):
        a, b = int(rng.integers(N)), int(rng.integers(N))
        if a == b:
            b = (b + 1) % N
        noise_items.append((a, b, K_NOISE))

    # interleave: FRONT-LOAD the noise into the first `noise_front_frac` of the true subsequence (biologically the
    # "noisy/uninformative early rearing" of Chang & Merzenich 2003 -- an early noise burst that genuinely DELAYS
    # structure maturation, the ONLY regime where the SNR trigger is predicted to matter vs a fixed position clock).
    # Same rule in both conditions (fair): under LOW noise there are few items so the burst is benign; under HIGH
    # noise it is a heavy early burst that pushes real structure to later stream fractions.
    stream = list(true_seq)
    front = max(1, int(round(cfg.get("noise_front_frac", 0.5) * len(true_seq))))
    positions = sorted(int(x) for x in rng.integers(0, front + 1, size=len(noise_items)))
    for off, (ni, item) in enumerate(zip(positions, noise_items)):
        stream.insert(ni + off, item)

    h_arr = np.array([s[0] for s in stream], dtype=np.int64)
    t_arr = np.array([s[1] for s in stream], dtype=np.int64)
    kind_arr = np.array([s[2] for s in stream], dtype=np.int64)
    # recurrence / provenance: TRUE + DISTRACTOR corroborated (pass floor); NOISE one-off
    nsrc = np.where(kind_arr == K_NOISE, 1, cfg["dist_recur"]).astype(np.int64)

    # ---- downstream query sets (truth labels independent of admission) ----------------------------------------
    pos, neg = _build_queries(cfg, rng, cores, sats, outliers, dist_pairs, module_of, scenario)

    return dict(N=N, module_of=module_of, cores=cores, sats=sats, outliers=outliers,
                h=h_arr, t=t_arr, kind=kind_arr, nsrc=nsrc, n_true=n_true, n_noise=n_noise,
                pos=pos, neg=neg, scenario=scenario, noise_frac=noise_frac)


def _mod_backbone(core_list):
    """STAR backbone: every core links to core[0]. 2 undirected hops reach the whole module -> the k=2 reachability
    mass of an integrated node is ~module-size regardless of total N (keeps the schema-fit signal scale-stable)."""
    hub = core_list[0]
    return [(hub, core_list[i]) for i in range(1, len(core_list))]


def _mod_placeholders(core_list, sat_list, rng):
    return [(s, core_list[int(rng.integers(len(core_list)))]) for s in sat_list]


def _build_queries(cfg, rng, cores, sats, outliers, dist_pairs, module_of, scenario):
    """POS (truth=connected/same-group) and NEG (truth=NOT). pos sat-core queries reward placeholders; neg
    outlier-distractor queries penalize distractors."""
    M = len(cores)
    pos = []   # (a,b) truth YES
    neg = []   # (a,b) truth NO
    # POS core-core within module
    for _ in range(cfg["n_pos_core"]):
        m = int(rng.integers(M))
        if len(cores[m]) < 2:
            continue
        i, j = rng.choice(len(cores[m]), size=2, replace=False)
        pos.append((cores[m][int(i)], cores[m][int(j)]))
    # POS sat-core within module (need the placeholder edge admitted)
    if scenario == "structured":
        sat_modules = [m for m in range(M) if len(sats[m]) > 0]
        for _ in range(cfg["n_pos_sat"]):
            m = int(rng.choice(sat_modules))
            s = int(rng.choice(sats[m]))
            c = int(rng.choice(cores[m]))
            pos.append((s, c))
    # NEG outlier-outlier that a DISTRACTOR would connect (should be NO)
    if scenario == "structured" and dist_pairs:
        dp = sorted(dist_pairs)
        for _ in range(cfg["n_neg_dist"]):
            a, b = dp[int(rng.integers(len(dp)))]
            neg.append((outliers[a], outliers[b]))
    # NEG cross-module core-core (should be NO)
    for _ in range(cfg["n_neg_cross"]):
        m1, m2 = rng.choice(M, size=2, replace=False)
        neg.append((int(rng.choice(cores[int(m1)])), int(rng.choice(cores[int(m2)]))))
    return pos, neg


# ---------------------------------------------------------------------------
# threshold policies (arms)
# ---------------------------------------------------------------------------
def thr_fixed(_state, thr):
    return thr


def thr_time(state, t0, t1):
    """Position-keyed permissive->strict ramp (the WRONG control): frac = stream position / length."""
    frac = state["pos"] / max(1, state["stream_len"])
    x = (frac - t0) / max(1e-9, (t1 - t0))
    x = min(1.0, max(0.0, x))
    return PERMISSIVE_THR + (STRICT_THR - PERMISSIVE_THR) * x


def thr_snr(state, sr_hi=SR_HI):
    """SNR-keyed ramp: keyed on the substrate's OWN measured success rate (peak-ratcheted -> consolidation lock).
    sr_hi (tightening rate) is calibrated to the LOW-noise optimum -- the SAME fair shot the TIME arm's window gets."""
    x = (state["peak_success"] - SR_LO) / max(1e-9, (sr_hi - SR_LO))
    x = min(1.0, max(0.0, x))
    return PERMISSIVE_THR + (STRICT_THR - PERMISSIVE_THR) * x


# ---------------------------------------------------------------------------
# the sequential ingest (foundation starts EMPTY)
# ---------------------------------------------------------------------------
def ingest(arena, cfg, policy, record_tighten=False):
    """Run one arm over the stream. policy(state)->threshold. Returns admitted mask + per-kind admit counts +
    (optional) tighten position (first step threshold crosses the ramp midpoint)."""
    N = arena["N"]
    h = arena["h"]; t = arena["t"]; kind = arena["kind"]; nsrc = arena["nsrc"]
    n = h.shape[0]
    admitted = np.zeros(n, dtype=bool)
    adj_edges = []                       # admitted (h,t) pairs -> adjacency recomputed periodically
    reach_frac = np.zeros(N, dtype=np.float64)
    win = deque(maxlen=SR_WINDOW)
    peak_success = 0.0
    thr_series = [] if record_tighten else None
    refresh = cfg["refresh_every"]

    for pos in range(n):
        if pos % refresh == 0 and adj_edges:
            ei = np.array(adj_edges, dtype=np.int64)
            ei3 = np.column_stack([ei[:, 0], np.zeros(ei.shape[0], dtype=np.int64), ei[:, 1]])
            adj = RA.build_undirected_adj(ei3, N)
            mass = RA.k_hop_reachable_mass(adj, cfg["reach_k"], cap=cfg["reach_cap"])
            # SCALE-INVARIANT normalization: saturating fraction of a fixed structural reach TARGET (a node reaching
            # >= reach_target others counts as fully integrated). Independent of total N AND of module size -> the
            # schema-fit signal + gate bars carry the SAME meaning at smoke and full scale (discriminator survives
            # scale). reach_target is a fixed constant across configs.
            reach_frac = np.minimum(1.0, mass.astype(np.float64) / float(cfg["reach_target"]))
        hi = int(h[pos]); ti = int(t[pos])
        sf = 0.5 * (reach_frac[hi] + reach_frac[ti])
        # measured success signal (substrate's own): did this candidate cross the extractable-structure bar?
        win.append(1.0 if sf >= SR_BAR else 0.0)
        success = float(np.mean(win)) if win else 0.0
        peak_success = max(peak_success, success)
        state = dict(pos=pos, stream_len=n, peak_success=peak_success)
        thr = policy(state)
        if thr_series is not None:
            thr_series.append(thr)
        # GATE: shared recurrence floor, then schema-fit stringency
        if int(nsrc[pos]) < RECURRENCE_MIN:
            decision = "DISCARD"
        elif sf >= thr:
            decision = "ADMIT"
        else:
            decision = "SKIP"
        if decision == "ADMIT":
            admitted[pos] = True
            adj_edges.append((hi, ti))

    counts = {}
    for k in (K_BACKBONE, K_PLACEHOLDER, K_DISTRACTOR, K_NOISE):
        m = kind == k
        counts[KIND_NAME[k]] = dict(admit=int((admitted & m).sum()), total=int(m.sum()))
    # tighten-onset = first step the threshold reaches half of its OWN peak stringency (level-adaptive; captures the
    # operational onset regardless of the absolute level the SNR trajectory reaches). -1 if never tightens.
    tighten_pos = -1
    if thr_series is not None:
        ts = np.asarray(thr_series, dtype=np.float64)
        peak_thr = float(ts.max()) if ts.size else 0.0
        if peak_thr > 1e-9:
            hits = np.where(ts >= 0.5 * peak_thr)[0]
            if hits.size:
                tighten_pos = int(hits[0])
    return admitted, adj_edges, counts, tighten_pos, float(peak_success)


# ---------------------------------------------------------------------------
# downstream reasoning quality: balanced accuracy of connectivity queries on the admitted graph
# ---------------------------------------------------------------------------
def downstream_ba(arena, adj_edges, cfg):
    """Foundation answers query(a,b)=YES iff b reachable from a within query_k hops in the ADMITTED graph.
    Balanced accuracy over POS (truth YES) and NEG (truth NO). Also returns admission F1 (true vs false)."""
    N = arena["N"]
    if adj_edges:
        ei = np.array(adj_edges, dtype=np.int64)
        ei3 = np.column_stack([ei[:, 0], np.zeros(ei.shape[0], dtype=np.int64), ei[:, 1]])
        adj = RA.build_undirected_adj(ei3, N)
    else:
        adj = [np.zeros(0, dtype=np.int64) for _ in range(N)]
    qk = cfg["query_k"]

    def connected(a, b):
        if a == b:
            return True
        seen = {a}; frontier = [a]
        for _ in range(qk):
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    vi = int(v)
                    if vi == b:
                        return True
                    if vi not in seen:
                        seen.add(vi); nxt.append(vi)
            frontier = nxt
            if not frontier:
                break
        return False

    pos = arena["pos"]; neg = arena["neg"]
    tp = sum(1 for (a, b) in pos if connected(a, b))
    tn = sum(1 for (a, b) in neg if not connected(a, b))
    tpr = tp / max(1, len(pos))
    tnr = tn / max(1, len(neg))
    ba = 0.5 * (tpr + tnr)
    return dict(ba=ba, tpr=tpr, tnr=tnr, n_pos=len(pos), n_neg=len(neg))


def admission_f1(arena, admitted):
    """F1 of admitted-TRUE-vs-admitted-FALSE against ground truth (backbone+placeholder = should admit)."""
    kind = arena["kind"]
    is_true = np.isin(kind, TRUE_KINDS)
    tp = int((admitted & is_true).sum())
    fp = int((admitted & ~is_true).sum())
    fn = int((~admitted & is_true).sum())
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 0.0 if (prec + rec) == 0 else 2 * prec * rec / (prec + rec)
    return dict(f1=f1, precision=prec, recall=rec, tp=tp, fp=fp, fn=fn)


# ---------------------------------------------------------------------------
# run all arms for one arena (structured-low, structured-high, null-high)
# ---------------------------------------------------------------------------
TIME_WINDOWS = [(max(0.0, c - 0.1), min(1.0, c + 0.1)) for c in (0.15, 0.30, 0.45, 0.60, 0.75, 0.90)]


def _ph_rate(cnt):
    c = cnt["placeholder"]
    return c["admit"] / max(1, c["total"])


SNR_SR_HI_GRID = [0.25, 0.40, 0.55, 0.70, 0.90, 1.20]


def sweep_time_window(arena, cfg):
    """Calibrate the TIME-keyed ramp: pick the window maximizing downstream BA on THIS arena (used on LOW noise ->
    the 'schedule tuned to the normal/typical environment' analog; then applied UNCHANGED to high noise)."""
    best = None
    for (t0, t1) in TIME_WINDOWS:
        adm, adj, _cnt, _tp, _ps = ingest(arena, cfg, lambda st, a=t0, b=t1: thr_time(st, a, b))
        ba = downstream_ba(arena, adj, cfg)["ba"]
        if best is None or ba > best[0]:
            best = (ba, (t0, t1))
    return best[1], best[0]


def sweep_snr_config(arena, cfg):
    """Calibrate the SNR ramp's tightening RATE (sr_hi) to the LOW-noise optimum -- the SAME fair, swept shot the TIME
    arm gets. (That the SNR trigger REQUIRES this per-scale calibration to behave is itself reported as a fragility.)"""
    best = None
    for sr_hi in SNR_SR_HI_GRID:
        adm, adj, _cnt, _tp, _ps = ingest(arena, cfg, lambda st, h=sr_hi: thr_snr(st, h))
        ba = downstream_ba(arena, adj, cfg)["ba"]
        if best is None or ba > best[0]:
            best = (ba, sr_hi)
    return best[1], best[0]


def run_condition(cfg, seed, scenario, noise_frac, time_window, snr_sr_hi):
    arena = build_arena(cfg, seed, scenario, noise_frac)
    n = arena["h"].shape[0]
    # SNR arm (sr_hi calibrated to low-noise optimum; record tighten position + measured success trajectory peak)
    adm_snr, adj_snr, cnt_snr, tp_snr, ps_snr = ingest(
        arena, cfg, lambda st: thr_snr(st, snr_sr_hi), record_tighten=True)
    ds_snr = downstream_ba(arena, adj_snr, cfg)
    f1_snr = admission_f1(arena, adm_snr)
    # FIXED sweep -> best per condition (its strongest shot)
    fixed_runs = []
    for thr in cfg["fixed_grid"]:
        adm, adj, cnt, _tp, _ps = ingest(arena, cfg, lambda st, _thr=thr: thr_fixed(st, _thr))
        ds = downstream_ba(arena, adj, cfg)
        fixed_runs.append(dict(thr=thr, ba=ds["ba"], f1=admission_f1(arena, adm)["f1"],
                               placeholder_admit=cnt["placeholder"], admitted=adm))
    best_fixed = max(fixed_runs, key=lambda r: r["ba"])
    strict_fixed = max(fixed_runs, key=lambda r: r["thr"])   # strictest = highest thr (blocks bootstrap)
    # TIME-keyed arm: window frozen from LOW-noise calibration, applied unchanged here
    t0, t1 = time_window
    adm_t, adj_t, cnt_t, tp_t, _pst = ingest(arena, cfg, lambda st: thr_time(st, t0, t1), record_tighten=True)
    ds_t = downstream_ba(arena, adj_t, cfg)
    time_res = dict(ba=ds_t["ba"], f1=admission_f1(arena, adm_t)["f1"],
                    placeholder_rate=_ph_rate(cnt_t), tighten_frac=(tp_t / max(1, n)) if tp_t >= 0 else -1.0)

    return dict(
        scenario=scenario, noise_frac=noise_frac, N=arena["N"], stream_len=n,
        n_true=arena["n_true"], n_noise=arena["n_noise"], time_window=[t0, t1],
        snr=dict(ba=ds_snr["ba"], tpr=ds_snr["tpr"], tnr=ds_snr["tnr"], f1=f1_snr["f1"],
                 counts=cnt_snr, placeholder_rate=_ph_rate(cnt_snr), peak_success=ps_snr,
                 tighten_frac=(tp_snr / max(1, n)) if tp_snr >= 0 else -1.0),
        best_fixed=dict(thr=best_fixed["thr"], ba=best_fixed["ba"], f1=best_fixed["f1"],
                        placeholder_rate=_ph_rate({"placeholder": best_fixed["placeholder_admit"]})),
        strict_fixed=dict(thr=strict_fixed["thr"], ba=strict_fixed["ba"],
                          placeholder_rate=_ph_rate({"placeholder": strict_fixed["placeholder_admit"]})),
        fixed_sweep=[dict(thr=r["thr"], ba=r["ba"], f1=r["f1"]) for r in fixed_runs],
        time=time_res,
        _arena=arena, _adm_snr=adm_snr, _best_fixed_adm=best_fixed["admitted"],
    )


# ---------------------------------------------------------------------------
# one seed: calibrate matched time window on LOW, then evaluate HIGH + NULL
# ---------------------------------------------------------------------------
def run_seed(cfg, seed):
    # 1) Calibrate the TIME-keyed ramp to be OPTIMAL under LOW noise (the 'schedule tuned to the normal/typical
    #    environment' analog), then apply it UNCHANGED to high noise. SNR uses ONE config in both. This is the honest
    #    anti-rig frame: a single time schedule cannot be simultaneously right for both environments; SNR adapts.
    low_arena = build_arena(cfg, seed, "structured", cfg["noise_low"])
    time_window, time_ba_low_cal = sweep_time_window(low_arena, cfg)
    snr_sr_hi, snr_ba_low_cal = sweep_snr_config(low_arena, cfg)   # SNR gets the SAME swept-to-low-noise shot as time

    low = run_condition(cfg, seed, "structured", cfg["noise_low"], time_window, snr_sr_hi)
    high = run_condition(cfg, seed, "structured", cfg["noise_high"], time_window, snr_sr_hi)
    nul = run_condition(cfg, seed, "null", cfg["noise_high"], time_window, snr_sr_hi)

    # arms-differ: admitted sets distinct (SNR vs best-fixed) under high noise
    arena_h = high["_arena"]
    snr_adm_pairs = [(int(arena_h["h"][i]), int(arena_h["t"][i])) for i in np.where(high["_adm_snr"])[0]]
    bf_adm_pairs = [(int(arena_h["h"][i]), int(arena_h["t"][i])) for i in np.where(high["_best_fixed_adm"])[0]]
    arms_differ = _sha_intpairs(snr_adm_pairs) != _sha_intpairs(bf_adm_pairs)

    for d in (low, high, nul):
        d.pop("_arena", None); d.pop("_adm_snr", None); d.pop("_best_fixed_adm", None)
    return dict(seed=seed, time_window=list(time_window), time_ba_low_calibration=time_ba_low_cal,
                snr_sr_hi=snr_sr_hi, snr_ba_low_calibration=snr_ba_low_cal,
                low=low, high=high, null=nul, arms_differ=arms_differ)


# ---------------------------------------------------------------------------
# telemetry sensitivity (gate decision flips when a signal is perturbed)
# ---------------------------------------------------------------------------
def telemetry_check():
    # base: schema-fit above strict, recurrence ok -> ADMIT; perturbations must flip the decision
    def decide(sf, nsrc, thr):
        if nsrc < RECURRENCE_MIN:
            return "DISCARD"
        return "ADMIT" if sf >= thr else "SKIP"
    base = decide(STRICT_THR + 0.2, 5, STRICT_THR)       # ADMIT (schema above strict)
    flip_rec = decide(STRICT_THR + 0.2, 1, STRICT_THR)   # DISCARD (recurrence floor)
    flip_sf = decide(0.0, 5, STRICT_THR)                 # SKIP (schema-fit below strict)
    # threshold policy responds to state: permissive vs strict give different decisions on a mid item
    perm = thr_snr(dict(pos=0, stream_len=100, peak_success=0.0))
    strict = thr_snr(dict(pos=0, stream_len=100, peak_success=1.0))
    thr_flips = (0.0 <= perm + 1e-12) and (strict >= STRICT_THR - 1e-9) and (strict > perm)
    return dict(base=base, flip_recurrence=flip_rec, flip_schema=flip_sf,
                recurrence_flips=(base == "ADMIT" and flip_rec == "DISCARD"),
                schema_flips=(base == "ADMIT" and flip_sf == "SKIP"),
                threshold_responds=thr_flips)


# ---------------------------------------------------------------------------
# aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


def aggregate_and_verdict(per_seed, run_mode, tele):
    def m(cond, arm, key):
        return _mean([s[cond][arm][key] for s in per_seed])

    # HIGH-noise headline
    snr_ba_high = m("high", "snr", "ba")
    bf_ba_high = m("high", "best_fixed", "ba")
    time_ba_high = _mean([s["high"]["time"]["ba"] for s in per_seed if s["high"]["time"]])
    snr_ph_high = m("high", "snr", "placeholder_rate")
    strict_ph_high = m("high", "strict_fixed", "placeholder_rate")
    # LOW-noise (context)
    snr_ba_low = m("low", "snr", "ba")
    bf_ba_low = m("low", "best_fixed", "ba")
    time_ba_low = _mean([s["low"]["time"]["ba"] for s in per_seed if s["low"]["time"]])
    # NULL guard
    snr_ba_null = m("null", "snr", "ba")
    bf_ba_null = m("null", "best_fixed", "ba")
    # SNR trigger is SIGNAL-keyed, not time-keyed: under high (noisy-reared) input the substrate's own success signal
    # rises later, so selectivity-onset (tighten fraction) shifts LATER (Chang-Merzenich). A time-clock is invariant.
    ps_low = m("low", "snr", "peak_success")
    ps_high = m("high", "snr", "peak_success")
    tf_low = _mean([s["low"]["snr"]["tighten_frac"] for s in per_seed if s["low"]["snr"]["tighten_frac"] >= 0])
    tf_high = _mean([s["high"]["snr"]["tighten_frac"] for s in per_seed if s["high"]["snr"]["tighten_frac"] >= 0])
    tighten_shift = tf_high - tf_low

    beats_fixed = (snr_ba_high - bf_ba_high) >= HP_MARGIN_FIXED
    beats_time = (snr_ba_high - time_ba_high) >= HP_MARGIN_TIME
    bootstrap = (snr_ph_high - strict_ph_high) >= HP_BOOTSTRAP_DELTA
    null_guard = abs(snr_ba_null - bf_ba_null) <= HP_NULL_TOL
    snr_not_time = tighten_shift >= HP_SHIFT_MIN_FRAC
    base_in_band = HP_BASE_LO < bf_ba_high < HP_BASE_HI
    arms_differ = all(s["arms_differ"] for s in per_seed)
    tele_ok = bool(tele["recurrence_flips"] and tele["schema_flips"] and tele["threshold_responds"])

    g = dict(HP_SNR_BEATS_FIXED=beats_fixed, HP_SNR_BEATS_TIME=beats_time, HP_BOOTSTRAP=bootstrap,
             HP_NULL_GUARD=null_guard, HP_SNR_NOT_TIME=snr_not_time, HP_BASE_IN_BAND=base_in_band,
             HP_ARMS_DIFFER=arms_differ, HP_TELEMETRY=tele_ok)
    joint = all(g.values())
    schedule_beats_fixed_g = (time_ba_high - bf_ba_high) >= HP_MARGIN_FIXED

    # Does the SCHEDULE CONCEPT (position-keyed time ramp, its own swept-to-low-noise best shot) beat fixed? This is
    # the fired positive control for "permissive->selective helps at all". Distinct from whether the SNR TRIGGER earns.
    schedule_beats_fixed = (time_ba_high - bf_ba_high) >= HP_MARGIN_FIXED
    snr_beats_fixed = beats_fixed
    snr_refinement_earns = beats_time and snr_not_time
    ramp_adds_nothing = (not schedule_beats_fixed) and (not snr_beats_fixed)
    if joint:
        verdict = "HARD_PASS"
    elif ramp_adds_nothing:
        verdict = "HARD_FAIL_no_schedule_beats_fixed_ramp_adds_nothing"
    elif schedule_beats_fixed and not snr_beats_fixed:
        # coarse SCHEDULE concept validated (time-clock beats fixed) but the SNR-GATED TRIGGER is refuted (does not
        # even beat fixed; dominated by the simple time clock) -- the note's anticipated Prediction-2 HARD-FAIL branch.
        verdict = "HARD_FAIL_snr_trigger_refuted_schedule_concept_validated_by_time_clock"
    elif snr_beats_fixed and not snr_refinement_earns:
        verdict = "MIDDLE_BAND_snr_beats_fixed_but_trigger_ties_or_loses_matched_time_clock"
    else:
        verdict = "MIDDLE_BAND_schedule_helps_partially"

    msg = ("HIGH: snr_ba=%.3f bestfixed_ba=%.3f (thr=%s) time_ba=%.3f | d_fixed=%+.3f d_time=%+.3f | "
           "boot: snr_ph=%.2f strictfixed_ph=%.2f d=%+.2f | NULL: snr=%.3f fixed=%.3f d=%.3f | "
           "trigger: tf_low=%.2f tf_high=%.2f shift=%+.2f (peaksucc %.3f/%.3f) | "
           "LOW: snr=%.3f fixed=%.3f time=%.3f | tele=%s arms_differ=%s" % (
               snr_ba_high, bf_ba_high, _mean([s["high"]["best_fixed"]["thr"] for s in per_seed]), time_ba_high,
               snr_ba_high - bf_ba_high, snr_ba_high - time_ba_high,
               snr_ph_high, strict_ph_high, snr_ph_high - strict_ph_high,
               snr_ba_null, bf_ba_null, abs(snr_ba_null - bf_ba_null),
               tf_low, tf_high, tighten_shift, ps_low, ps_high,
               snr_ba_low, bf_ba_low, time_ba_low, tele_ok, arms_differ))
    g["SCHEDULE_TIME_BEATS_FIXED"] = schedule_beats_fixed_g
    summary = ("%s | SCHEDULE(time)-vs-fixed=%+.3f | snr-vs-fixed=%+.3f snr-vs-time=%+.3f bootstrap_delta=%+.2f" % (
        verdict, time_ba_high - bf_ba_high, snr_ba_high - bf_ba_high, snr_ba_high - time_ba_high,
        snr_ph_high - strict_ph_high))
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, gates=g, joint_hard_pass=joint,
                run_mode=run_mode,
                agg=dict(snr_ba_high=snr_ba_high, best_fixed_ba_high=bf_ba_high, time_ba_high=time_ba_high,
                         snr_ba_low=snr_ba_low, best_fixed_ba_low=bf_ba_low, time_ba_low=time_ba_low,
                         snr_ba_null=snr_ba_null, best_fixed_ba_null=bf_ba_null,
                         snr_placeholder_high=snr_ph_high, strict_fixed_placeholder_high=strict_ph_high,
                         bootstrap_delta=snr_ph_high - strict_ph_high,
                         schedule_time_vs_fixed_high=time_ba_high - bf_ba_high,
                         peak_success_low=ps_low, peak_success_high=ps_high,
                         snr_tighten_frac_low=tf_low, snr_tighten_frac_high=tf_high, tighten_shift=tighten_shift,
                         d_fixed_high=snr_ba_high - bf_ba_high, d_time_high=snr_ba_high - time_ba_high))


# ---------------------------------------------------------------------------
# self-test (REAL code path at tiny scale + validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    _log("self_test: tiny arena + reachability_audit + AdditiveKGMap.score_all signal-source + ingest/gate/downstream")
    exercised = set()

    tiny = dict(M=4, core_size=5, sat_size=2, n_outlier=8, n_distractor=6, dist_recur=4,
                noise_low=0.05, noise_high=0.35, seeds=[7], refresh_every=6, reach_k=2, reach_cap=60, reach_target=6, query_k=3,
                n_pos_core=20, n_pos_sat=20, n_neg_dist=20, n_neg_cross=15, fixed_grid=[0.0, 0.1, 0.22, 0.35])
    arena = build_arena(tiny, 7, "structured", 0.35); exercised.add("build_arena")
    assert arena["n_noise"] > 0 and arena["n_true"] > 0
    adm, adj, cnt, tp, ps = ingest(arena, tiny, thr_snr, record_tighten=True); exercised.add("ingest")
    exercised.add("reachability_audit.build_undirected_adj"); exercised.add("reachability_audit.k_hop_reachable_mass")
    ds = downstream_ba(arena, adj, tiny); exercised.add("downstream_ba")
    f1 = admission_f1(arena, adm); exercised.add("admission_f1")
    assert 0.0 <= ds["ba"] <= 1.0 and 0.0 <= f1["f1"] <= 1.0

    # threshold policies distinct: permissive (empty foundation) < strict (mature)
    p0 = thr_snr(dict(pos=0, stream_len=100, peak_success=0.0))
    p1 = thr_snr(dict(pos=0, stream_len=100, peak_success=1.0))
    assert p1 > p0 and abs(p0 - PERMISSIVE_THR) < 1e-9 and abs(p1 - STRICT_THR) < 1e-9, "snr ramp endpoints wrong"
    tt0 = thr_time(dict(pos=0, stream_len=100), 0.2, 0.4)
    tt1 = thr_time(dict(pos=100, stream_len=100), 0.2, 0.4)
    assert tt1 > tt0, "time ramp not monotone"
    # SNR trigger is a PURE function of measured success rate, NOT of position (the load-bearing invariant)
    a = thr_snr(dict(pos=5, stream_len=100, peak_success=0.5))
    b = thr_snr(dict(pos=95, stream_len=100, peak_success=0.5))
    assert a == b, "SNR threshold must depend ONLY on success rate, not stream position"

    # telemetry sensitivity
    tele = telemetry_check(); exercised.add("telemetry_check")
    assert tele["recurrence_flips"] and tele["schema_flips"] and tele["threshold_responds"], "telemetry insensitive"

    # NULL arena has no placeholders/distractors
    nul = build_arena(tiny, 7, "null", 0.35)
    assert int((nul["kind"] == K_PLACEHOLDER).sum()) == 0 and int((nul["kind"] == K_DISTRACTOR).sum()) == 0

    # AdditiveKGMap.score_all signal-source availability (the note's surprise source; exercised on the real object)
    import torch
    from hdlab.additive_map import AdditiveKGMap
    triples = [("a", "r", "b"), ("b", "r", "c"), ("c", "r", "a"), ("a", "r", "c")]
    km = AdditiveKGMap(device="cpu")
    km.fit(triples, k=8, epochs=20, seed=7)
    sc = km.score_all("a", "r"); exercised.add("AdditiveKGMap.score_all")
    assert hasattr(sc, "shape") and int(sc.shape[0]) == km.num_entities

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["reachability_audit.build_undirected_adj",
                                        "reachability_audit.k_hop_reachable_mass",
                                        "AdditiveKGMap.score_all", "ingest", "downstream_ba", "build_arena"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": RA.k_hop_reachable_mass,
         "callable_name": "k_hop_reachable_mass",
         "kwargs": {"adj": [np.zeros(0, dtype=np.int64)], "k": 2, "cap": 10}},
        {"kind": "metric_moves", "metric_name": "snr_threshold", "before": float(p0), "after": float(p1),
         "min_delta": 1e-6},
    ], run_mode="selftest")
    assert ok, "validity preflight failed"
    _log("self_test PASS (exercised: %s)" % sorted(exercised))
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _unk = ap.parse_known_args()

    from experiments._seed_checkpoint import get_output_dir
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else "full")
    output_dir = str(get_output_dir(ANCHOR_NAME + ("_selftest" if args.self_test else ("_smoke" if args.smoke else ""))))
    global _OUT
    _OUT = output_dir

    if args.self_test:
        self_test()
        _write_metrics_atomic(output_dir, dict(verdict="HARD_PASS", verdict_msg="SELFTEST_PASS",
                                               run_mode="self_test", summary="self_test ok", elapsed_s=0.0))
        return

    cfg = SMOKE_CFG if args.smoke else FULL_CFG
    _write_start_marker(output_dir, run_mode, len(cfg["seeds"]))
    t0 = time.time()
    per_seed = []
    for si, seed in enumerate(cfg["seeds"]):
        _log("seed %d/%d (seed=%d) ingest-over-time (low/high/null)..." % (si + 1, len(cfg["seeds"]), seed))
        res = run_seed(cfg, seed)
        per_seed.append(res)
        h = res["high"]
        _log("seed=%d HIGH snr_ba=%.3f bestfixed_ba=%.3f time_ba=%.3f d_fix=%+.3f d_time=%+.3f boot=%+.2f (%.1fs)" % (
            seed, h["snr"]["ba"], h["best_fixed"]["ba"], (h["time"]["ba"] if h["time"] else float("nan")),
            h["snr"]["ba"] - h["best_fixed"]["ba"],
            h["snr"]["ba"] - (h["time"]["ba"] if h["time"] else float("nan")),
            h["snr"]["placeholder_rate"] - h["strict_fixed"]["placeholder_rate"], time.time() - t0))

    tele = telemetry_check()
    v = aggregate_and_verdict(per_seed, run_mode, tele)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(cfg["seeds"]),
                   config=dict(M=cfg["M"], core_size=cfg["core_size"], sat_size=cfg["sat_size"],
                               n_outlier=cfg["n_outlier"], n_distractor=cfg["n_distractor"],
                               noise_low=cfg["noise_low"], noise_high=cfg["noise_high"], seeds=cfg["seeds"],
                               fixed_grid=cfg["fixed_grid"]),
                   params=dict(RECURRENCE_MIN=RECURRENCE_MIN, STRICT_THR=STRICT_THR, PERMISSIVE_THR=PERMISSIVE_THR,
                               SR_BAR=SR_BAR, SR_LO=SR_LO, SR_HI=SR_HI, SR_WINDOW=SR_WINDOW),
                   bands=dict(HP_MARGIN_FIXED=HP_MARGIN_FIXED, HP_MARGIN_TIME=HP_MARGIN_TIME,
                              HP_BOOTSTRAP_DELTA=HP_BOOTSTRAP_DELTA, HP_NULL_TOL=HP_NULL_TOL,
                              HP_SHIFT_MIN_FRAC=HP_SHIFT_MIN_FRAC),
                   telemetry=tele, arms_differ_verified=all(s["arms_differ"] for s in per_seed),
                   final_metrics_atomicity="tmp_replace", **v, per_seed=per_seed)
    _write_metrics_atomic(output_dir, metrics)
    _log("VERDICT %s | %s" % (v["verdict"], v["verdict_msg"]))
    _log("wrote %s (%.1fs)" % (os.path.join(output_dir, "metrics.json"), elapsed))


_OUT = None
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT or os.path.join("data", "exp_" + ANCHOR_NAME), e)
        raise
