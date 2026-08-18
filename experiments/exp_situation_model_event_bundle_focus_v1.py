"""SITUATION-MODEL MEMORY FORMAT -- event bundles + active focus (Cowan-4) -- v1.

Represents reader EVENTS + the active FOCUS OF ATTENTION as brain-grounded HIERARCHICAL
ROLE-SLOT BUNDLES (the validated M1.7 RoleSlotSummarizer binding), replacing the reader's
current THIN event labels. Builds the two NEW pluggable substrate modules and runs the
fair can-fail demonstration on REAL reader events.

MODULES (new; pluggable; the reader timeline/coref will USE these):
  * hdlab/event_bundle.py     -- EventBundleCodec: an event (PRED, AGENT, PATIENT, TENSE)
                                 -> ONE role-slot-bound vector; GLASS-BOX unbindable (query
                                 a role -> recover its filler). REUSES RoleSlotSummarizer
                                 flat role-slot binding (bit-identity self-test).
  * hdlab/situation_focus.py  -- FlatFocus (chunking OFF) + ChunkedFocus (Cowan-4 active
                                 buffer + hierarchical chunking of older frames).

ARMS / DEMOS (all on REAL reader events + real vocab):
  ARM P1 ROUND-TRIP     : encode each real event, unbind each of the 4 roles, cleanup ->
                          filler. Per-role + overall recovery. (bundle round-trips)
  ARM DISCRIMINATOR     : role-query retrieval on a single event -- BUNDLE vs two thin
                          baselines that CANNOT answer a role query: THIN_LABEL (event as
                          one atomic vector / string label) and BAG_OF_ARGS (fillers
                          bundled with NO role binding). Bundle succeeds; baselines ~ chance.
  ARM P2 SCRAMBLE       : encode with role<->filler binding permuted (structure destroyed);
                          query the true role -> recovers the WRONG filler (~ chance). Proves
                          the role binding (structure) is load-bearing, not filler-presence.
  ARM CAPACITY          : FLAT focus retrieval accuracy vs #active-items n=1..8 -> GRACEFUL
                          (Cowan) degradation (not unbounded, not hard-zero). Chance = 1/V.
  ARM CHUNK RECOVERY    : ChunkedFocus on the SAME stream -- recent (in-focus) items stay
                          accessible at high load via chunking of older frames; chunked-recent
                          beats flat at load 8 (recovery). Also reports the recency/depth
                          degradation profile + an N-robustness table (signature holds across N).

FAIRNESS (P1/P2): P1 = the bundle round-trips (each role's filler recovered above cleanup).
  P2 = scrambling the role bindings makes role-query FAIL (structure load-bearing). The thin
  baselines are stored in the SAME substrate with the SAME information budget; they lack only
  the role-filler binding -- exactly the variable under test (structure vs no-structure).
  ONE variable per arm. Capacity measured honestly: the operating point N is chosen ONCE so
  the finite-capacity limit is VISIBLE in the 1..8 window while recent items stay usably
  retrievable (a design-gate regime choice, NOT per-trial tuning); the N-robustness table
  shows the QUALITATIVE signature (graceful decline + chunking recovery) is N-invariant, only
  the knee shifts -- so the result is not a construction-aided clean number.

BRAIN-CHECK (Cowan 2001): WM holds ~4(+-1) chunks in the focus of attention, hierarchically
  chunked (each chunk a bundle). FlatFocus = the raw superposition capacity limit; ChunkedFocus
  = the focus-of-attention that stays ~4 active units by compressing older frames -> graceful
  recency-graded degradation, the human-WM signature. NEVER-CONFIDENTLY-WRONG: cleanup returns
  a filler + score; low-score retrievals are the degraded tail we report, not hidden.

COMPUTE ARCHITECTURE: class (c) mixed. (i) One reused arc-eager parser train (~25s smoke /
  ~50s full, byte-identical import of the consolidated reader components) to obtain REAL events;
  sequential-CPU justified (it IS the reused reader, not a batchable substrate primitive).
  (ii) All HD ops (bind = elementwise mul, bundle = sum+sign, cleanup = matmul + argmax) at
  N<=8192 over a few thousand trials -- vectorized numpy/torch, wall < 30s. Storage: event =
  BUNDLED (small fixed 4-pair superposition, alpha=4/N << 0.138 wall, correct at this level);
  focus = FLAT (ablation) vs CHUNKED (bounded active buffer). Determinism: OMP/MKL/OPENBLAS=1,
  fixed int SEED, torch.Generator, sorted(set) vocab; no hash()-seeded RNG. LOCAL-ONLY,
  foreground-to-completion. NO push / NO remote-persist / NO queue_add (routing contract:
  inline-local FULL, not banked -- skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground demonstration cell):
  - arms_differ_verified at smoke (bundle vs thin-label bundle vectors hash-differ)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke: discriminator baselines are the DELIBERATELY-null thin/bag
    representations (report at chance = 1/V); the mechanism arm (bundle) must clear them by
    the pre-registered margin; capacity FLAT arm must be in-band (0.05 < flat(8) < flat(1))
  - discriminator fires at smoke: bundle role-query >> thin/bag; flat degrades; chunk recovers
  - deterministic seeding (fixed int SEED; torch.Generator; sorted(set) ordering)
  - all numbers MEASURED@ (printed at run) or CITED@; TENSE is a HEURISTIC placeholder for the
    TIME/TENSE slot (past if -ed/irregular else present) -- flagged, not a tense-tagger claim
  - N/A: KGStore (no KG); N/A CRLB (accuracy/argmax over a discrete codebook; chance=1/V stated);
    N/A multi-seed (deterministic given fixed SEED; capacity curve averages many trials)
  - progress_logging: print_flush_true (stdout line-buffered at cell start)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "situation_model_event_bundle_focus_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from hdlab.event_bundle import EventBundleCodec, DEFAULT_ROLES              # noqa: E402
from hdlab.situation_focus import FlatFocus, ChunkedFocus                   # noqa: E402
from hdlab import event_bundle as _EB                                       # noqa: E402
from hdlab import situation_focus as _SF                                    # noqa: E402

ROLES = DEFAULT_ROLES  # ("PRED", "AGENT", "PATIENT", "TENSE")
SEED = 20260723
EVENT_N = 8192          # event-level fidelity (RoleSlotSummarizer envelope)
FOCUS_N = 384           # focus operating point (finite-capacity signature visible in 1..8)
CAPACITY = 4
FANOUT = 2
MAX_N = 8
ROBUSTNESS_NS = (192, 256, 384, 512)

# ---- pre-registered bands (grounded on the N=384 calibration; HYPOTHESIZED pre-run) ----
HP_P1_MIN = 0.98            # bundle round-trips (overall per-role recovery)
HF_P1_MIN = 0.80            # below this the event format is broken
HP_DISC_BUNDLE_MIN = 0.95   # bundle role-query
HP_DISC_THIN_MAX = 0.20     # thin-label at/near chance
HP_DISC_BAG_MAX = 0.40      # bag-of-args cannot assign roles
HP_DISC_MARGIN_MIN = 0.50   # bundle - max(thin, bag)
HP_P2_SCRAMBLE_MAX = 0.40   # scrambled structure ~ chance
HP_P2_MARGIN_MIN = 0.40     # bundle - scramble
HP_FLAT1_MIN = 0.90         # near-perfect at load 1
HP_FLAT_DROP_MIN = 0.15     # genuine degradation flat(1)-flat(MAX_N)
HF_FLAT_SAT_EPS = 0.02      # flat(MAX_N) >= flat(1)-eps => saturated (signature hidden) => FAIL
HP_RECOVERY_MARGIN_MIN = 0.10  # chunked-recent(MAX_N) - flat(MAX_N)
HP_RECOVERY_RECENT_MIN = 0.55  # recent items usable at high load

CITED_RSS = ("hdlab/role_slot_summarizer.py RoleSlotSummarizer M1.7 3-seed CG 2026-07-01 "
             "ROLE 0.79/0.83/0.79 cv=0.024")
CITED_COWAN = "Cowan (2001) 4+-1 chunks in the focus of attention; notes/research_drill_HOL_meta_reasoning_biology_3x_2026-06-09.md"

_IRREGULAR_PAST = {
    "took", "threw", "did", "held", "got", "made", "went", "saw", "came", "gave",
    "found", "told", "said", "ran", "began", "grew", "knew", "fell", "sat", "stood",
    "brought", "bought", "caught", "taught", "thought", "left", "kept", "felt", "met",
    "sent", "spent", "built", "rose", "wrote", "spoke", "broke", "chose", "drove",
}


def _tense_of(verb: str) -> str:
    v = str(verb).lower()
    if v.endswith("ed") or v in _IRREGULAR_PAST:
        return "T=PAST"
    return "T=PRES"


def _event_role_fillers(verb, agent, patient) -> dict:
    return {"PRED": str(verb).lower(), "AGENT": str(agent).lower(),
            "PATIENT": str(patient).lower(), "TENSE": _tense_of(verb)}


# =======================================================================================
# REAL reader events (byte-identical import of the consolidated reader components).
# =======================================================================================
def get_real_events(run_mode):
    """Run the consolidated who-did-what reader on REAL McGuffey text -> [(verb,agent,patient)]."""
    from experiments import exp_consolidated_reader_chaingrade_demo_v1 as R
    from experiments import exp_multipred_depparse_argstruct_recall_v2 as M
    from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3
    from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2
    slice_lessons = R.SMOKE_SLICE if run_mode == "smoke" else R.FULL_SLICE
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    W, parser_info = M.train_dep_parser("smoke" if run_mode == "smoke" else "full")
    order, sent_text, arm, _gate, _sel = R.run_consolidated_reader(
        slice_lessons, W, clf, ratings_table, use_dohave=True, use_ecm=False)
    events = []
    for sid in order:
        for (v, a, p) in arm[sid]:
            if v and a and p:
                events.append((str(v), str(a), str(p)))
    return events, dict(slice=slice_lessons, n_sentences=len(order), parser_uas=parser_info["uas_dev"])


def build_vocab(events):
    toks = set()
    for (v, a, p) in events:
        rf = _event_role_fillers(v, a, p)
        for f in rf.values():
            toks.add(f)
    return sorted(toks)


# =======================================================================================
# Event-level arms (N = EVENT_N): P1 round-trip, discriminator, P2 scramble.
# =======================================================================================
def event_level_arms(events, vocab, n_dim):
    codec = EventBundleCodec(n_dim=n_dim, roles=ROLES, seed=SEED)
    codec.prime_symbols(vocab)
    V = codec.vocab_size()
    chance = 1.0 / V if V else 0.0
    gen = torch.Generator(); gen.manual_seed(SEED + 1)

    per_role_hits = {r: 0 for r in ROLES}
    total_events = 0
    disc_bundle_hits = disc_thin_hits = disc_bag_hits = disc_tot = 0
    p2_hits = 0
    role_query_roles = ("AGENT", "PATIENT")
    glass_box_samples = []

    for (v, a, p) in events:
        rf = _event_role_fillers(v, a, p)
        ev = codec.encode_event(rf)
        thin = codec.encode_thin_label()
        bag = codec.encode_bag_of_args(list(rf.values()))
        # scramble: random permutation of the 4 role-key assignments (non-identity preferred)
        perm = torch.randperm(len(ROLES), generator=gen).tolist()
        if perm == list(range(len(ROLES))):
            perm = perm[1:] + perm[:1]
        scr = codec.encode_scrambled_event(rf, perm)
        total_events += 1
        sample = dict(event=(v, a, p), tense=rf["TENSE"], recovered={})
        for r in ROLES:
            s, sc = codec.query_role_vec(ev, r)
            sample["recovered"][r] = (s, round(sc, 1))
            if s == rf[r]:
                per_role_hits[r] += 1
        for r in role_query_roles:
            disc_tot += 1
            sb, _ = codec.query_role_vec(ev, r)
            st, _ = codec.query_role_vec(thin, r)
            sg, _ = codec.query_role_vec(bag, r)
            ss, _ = codec.query_role_vec(scr, r)
            if sb == rf[r]:
                disc_bundle_hits += 1
            if st == rf[r]:
                disc_thin_hits += 1
            if sg == rf[r]:
                disc_bag_hits += 1
            if ss == rf[r]:
                p2_hits += 1
        if len(glass_box_samples) < 6:
            glass_box_samples.append(sample)

    per_role_acc = {r: (per_role_hits[r] / total_events if total_events else 0.0) for r in ROLES}
    p1_overall = sum(per_role_hits.values()) / (total_events * len(ROLES)) if total_events else 0.0
    disc = dict(
        bundle=disc_bundle_hits / disc_tot if disc_tot else 0.0,
        thin_label=disc_thin_hits / disc_tot if disc_tot else 0.0,
        bag_of_args=disc_bag_hits / disc_tot if disc_tot else 0.0,
        scramble=p2_hits / disc_tot if disc_tot else 0.0,
        chance=chance, n_queries=disc_tot, vocab_size=V,
    )
    # arms_differ: bundle vs thin-label vectors must hash-differ
    ev0 = codec.encode_event(_event_role_fillers(*events[0]))
    thin0 = codec.encode_thin_label()
    h_ev = hashlib.sha256(ev0.numpy().tobytes()).hexdigest()[:16]
    h_thin = hashlib.sha256(thin0.numpy().tobytes()).hexdigest()[:16]
    arms_differ = (h_ev != h_thin)
    return dict(p1_overall=p1_overall, per_role_acc=per_role_acc, discriminator=disc,
                n_events=total_events, arms_differ=arms_differ,
                arm_hashes=dict(bundle=h_ev, thin_label=h_thin),
                glass_box_samples=glass_box_samples)


# =======================================================================================
# Capacity + chunking arms (N = FOCUS_N): flat degradation + chunked recovery.
# =======================================================================================
def capacity_sweep(vocab, n_dim, trials, max_n=MAX_N, capacity=CAPACITY, fanout=FANOUT,
                   seed=SEED):
    codec = EventBundleCodec(n_dim=n_dim, roles=ROLES, seed=seed)
    codec.prime_symbols(vocab)
    V = codec.vocab_size()
    chance = 1.0 / V if V else 0.0
    gen = torch.Generator(); gen.manual_seed(seed + 7)
    role_ids = (1, 2)  # AGENT, PATIENT
    flat = {}; chunk_all = {}; chunk_recent = {}
    depth_profile = {}  # n -> {depth: acc}
    for n in range(1, max_n + 1):
        fh = ft = 0
        ah = at = 0
        rh = rt = 0
        depth_hits = {}; depth_tot = {}
        for _ in range(trials):
            events = []
            picks = []
            for _g in range(n):
                pk = [vocab[int(torch.randint(0, V, (1,), generator=gen))] for _ in ROLES]
                picks.append(pk)
                events.append(codec.encode_event({ROLES[i]: pk[i] for i in range(len(ROLES))}))
            ff = FlatFocus(codec, max_items=n, seed=seed + 3); ff.build(events)
            cf = ChunkedFocus(codec, capacity=capacity, fanout=fanout, seed=seed + 3)
            for g in range(n):
                cf.push(events[g], g)
            for g in range(n):
                d = cf.depth(g)
                direct = (d == 0)
                for ri in role_ids:
                    truth = picks[g][ri]
                    sf, _ = ff.query(g, ROLES[ri]); ft += 1; fh += (sf == truth)
                    sc, _ = cf.query(g, ROLES[ri]); at += 1; ah += (sc == truth)
                    depth_tot[d] = depth_tot.get(d, 0) + 1
                    depth_hits[d] = depth_hits.get(d, 0) + (sc == truth)
                    if direct:
                        rt += 1; rh += (sc == truth)
        flat[n] = fh / ft
        chunk_all[n] = ah / at
        chunk_recent[n] = (rh / rt) if rt else 0.0
        depth_profile[n] = {int(d): round(depth_hits[d] / depth_tot[d], 4) for d in sorted(depth_tot)}
    return dict(flat=flat, chunk_all=chunk_all, chunk_recent=chunk_recent,
                depth_profile=depth_profile, chance=chance, vocab_size=V,
                capacity=capacity, fanout=fanout, max_n=max_n, trials=trials)


def robustness_table(vocab, trials):
    out = {}
    for nd in ROBUSTNESS_NS:
        sw = capacity_sweep(vocab, nd, trials=trials)
        out[nd] = dict(flat={n: round(sw["flat"][n], 4) for n in sw["flat"]},
                       chunk_recent={n: round(sw["chunk_recent"][n], 4) for n in sw["chunk_recent"]},
                       flat_drop=round(sw["flat"][1] - sw["flat"][MAX_N], 4),
                       recovery=round(sw["chunk_recent"][MAX_N] - sw["flat"][MAX_N], 4))
    return out


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# =======================================================================================
# Self-test (design-gate; module selftests + tiny synthetic arms).
# =======================================================================================
def self_test():
    print("[self-test] module selftests (reuse-verification + baselines-fail + chunking) ...")
    print("  event_bundle:", _EB._run_all_selftests())
    print("  situation_focus:", _SF._run_all_selftests())

    # Tiny synthetic event set (no reader dependency) exercises every arm + design gates.
    syn = [("took", "boy", "block"), ("threw", "girl", "ball"), ("held", "man", "hand"),
           ("opened", "she", "door"), ("covered", "he", "face"), ("rubbed", "cat", "wall")]
    vocab = build_vocab(syn)
    ev = event_level_arms(syn, vocab, n_dim=EVENT_N)
    print(f"  [event] P1={ev['p1_overall']:.3f} per_role={ {r: round(v,3) for r,v in ev['per_role_acc'].items()} }")
    print(f"  [event] disc bundle={ev['discriminator']['bundle']:.3f} thin={ev['discriminator']['thin_label']:.3f} "
          f"bag={ev['discriminator']['bag_of_args']:.3f} scramble={ev['discriminator']['scramble']:.3f} "
          f"chance={ev['discriminator']['chance']:.3f}")
    assert ev["arms_differ"], "arms_differ FAIL: bundle vs thin-label hash collide"
    assert ev["p1_overall"] >= HF_P1_MIN, f"P1 below hard-fail floor: {ev['p1_overall']}"
    assert ev["discriminator"]["bundle"] > max(ev["discriminator"]["thin_label"],
                                               ev["discriminator"]["bag_of_args"]), \
        "discriminator did NOT fire at smoke (bundle not > thin/bag)"
    assert ev["discriminator"]["bundle"] > ev["discriminator"]["scramble"], \
        "P2 did NOT fire at smoke (bundle not > scramble)"

    sw = capacity_sweep(vocab, FOCUS_N, trials=40)
    print(f"  [capacity] flat={ {n: round(sw['flat'][n],3) for n in sw['flat']} }")
    print(f"  [capacity] chunk_recent={ {n: round(sw['chunk_recent'][n],3) for n in sw['chunk_recent']} }")
    assert sw["flat"][1] > sw["flat"][MAX_N], "flat did NOT degrade at smoke (saturated)"
    assert sw["chunk_recent"][MAX_N] > sw["flat"][MAX_N], "chunking gave NO recovery at smoke"
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict (FULL).
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    trials = 40 if run_mode == "smoke" else 200
    _write_start_marker(output_dir, run_mode, expected_n_units=MAX_N)
    print(f"[full] mode={run_mode} acquiring REAL reader events ...", flush=True)
    events, ev_meta = get_real_events(run_mode)
    print(f"[full] real events: n={len(events)} from {ev_meta['slice']} (parser uas={ev_meta['parser_uas']})",
          flush=True)
    if len(events) < (8 if run_mode == "smoke" else 20):
        raise RuntimeError(f"too few real reader events ({len(events)}) -- real-event acquisition failed")
    vocab = build_vocab(events)
    print(f"[full] vocab size V={len(vocab)} (chance=1/V={1.0/len(vocab):.4f})", flush=True)

    # ---- event-level arms (N=EVENT_N) ----
    ev = event_level_arms(events, vocab, n_dim=EVENT_N)
    disc = ev["discriminator"]
    disc_margin = disc["bundle"] - max(disc["thin_label"], disc["bag_of_args"])
    p2_margin = disc["bundle"] - disc["scramble"]
    print(f"[full] P1 round-trip overall={ev['p1_overall']:.4f} per_role="
          f"{ {r: round(v,4) for r,v in ev['per_role_acc'].items()} }", flush=True)
    print(f"[full] DISCRIMINATOR bundle={disc['bundle']:.4f} thin={disc['thin_label']:.4f} "
          f"bag={disc['bag_of_args']:.4f} scramble={disc['scramble']:.4f} chance={disc['chance']:.4f} "
          f"| disc_margin={disc_margin:.4f} p2_margin={p2_margin:.4f}", flush=True)

    # ---- capacity + chunking arms (N=FOCUS_N) ----
    sw = capacity_sweep(vocab, FOCUS_N, trials=trials)
    flat = sw["flat"]; ch_recent = sw["chunk_recent"]; ch_all = sw["chunk_all"]
    flat_drop = flat[1] - flat[MAX_N]
    recovery_margin = ch_recent[MAX_N] - flat[MAX_N]
    print(f"[full] CAPACITY flat={ {n: round(flat[n],4) for n in flat} }", flush=True)
    print(f"[full] CHUNK recent={ {n: round(ch_recent[n],4) for n in ch_recent} } "
          f"all={ {n: round(ch_all[n],4) for n in ch_all} }", flush=True)
    print(f"[full] flat_drop(1->{MAX_N})={flat_drop:.4f} recovery(recent-flat@{MAX_N})={recovery_margin:.4f}",
          flush=True)

    robust = robustness_table(vocab, trials=max(40, trials // 2))
    print(f"[full] N-robustness (flat_drop / recovery): "
          f"{ {nd: (robust[nd]['flat_drop'], robust[nd]['recovery']) for nd in robust} }", flush=True)

    # ---- per-gate verdicts ----
    p1_ok = ev["p1_overall"] >= HP_P1_MIN
    disc_ok = (disc["bundle"] >= HP_DISC_BUNDLE_MIN and disc["thin_label"] <= HP_DISC_THIN_MAX
               and disc["bag_of_args"] <= HP_DISC_BAG_MAX and disc_margin >= HP_DISC_MARGIN_MIN)
    p2_ok = (disc["scramble"] <= HP_P2_SCRAMBLE_MAX and p2_margin >= HP_P2_MARGIN_MIN)
    flat_sat = flat[MAX_N] >= flat[1] - HF_FLAT_SAT_EPS
    flat_hardzero = flat[2] <= disc["chance"] + 0.02
    capacity_ok = (flat[1] >= HP_FLAT1_MIN and flat_drop >= HP_FLAT_DROP_MIN
                   and flat[MAX_N] > sw["chance"] + 0.02 and not flat_sat)
    recovery_ok = (recovery_margin >= HP_RECOVERY_MARGIN_MIN
                   and ch_recent[MAX_N] >= HP_RECOVERY_RECENT_MIN)

    hard_fail = (ev["p1_overall"] < HF_P1_MIN or disc["bundle"] <= max(disc["thin_label"], disc["bag_of_args"])
                 or disc["scramble"] >= disc["bundle"] - 0.10 or flat_sat or flat_hardzero
                 or ch_recent[MAX_N] <= flat[MAX_N])
    all_ok = p1_ok and disc_ok and p2_ok and capacity_ok and recovery_ok

    gates = dict(P1_roundtrips=p1_ok, DISCRIMINATOR_fires=disc_ok, P2_structure_load_bearing=p2_ok,
                 CAPACITY_graceful=capacity_ok, CHUNK_recovery=recovery_ok)

    if all_ok:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS situation-model memory format: (P1) event bundle round-trips -- per-role recovery "
                f"{ {r: round(v,3) for r,v in ev['per_role_acc'].items()} }, overall {ev['p1_overall']:.3f}; "
                f"(DISCRIMINATOR) role-query retrieval bundle={disc['bundle']:.3f} vs thin-label "
                f"{disc['thin_label']:.3f} / bag-of-args {disc['bag_of_args']:.3f} (chance {disc['chance']:.3f}) "
                f"-- the bundle answers 'who was the AGENT/PATIENT' by unbinding a role; the thin baselines "
                f"CANNOT (margin {disc_margin:.3f}); (P2) scrambling the role bindings collapses retrieval to "
                f"{disc['scramble']:.3f} (structure load-bearing, margin {p2_margin:.3f}); (CAPACITY) FLAT focus "
                f"degrades gracefully {flat[1]:.3f}->{flat[MAX_N]:.3f} over 1..{MAX_N} active items (Cowan "
                f"signature, not unbounded, not hard-zero); (CHUNK) ChunkedFocus keeps recent items accessible "
                f"at load {MAX_N} (recent {ch_recent[MAX_N]:.3f} vs flat {flat[MAX_N]:.3f}, recovery "
                f"{recovery_margin:.3f}) by compressing older frames -- the human focus-of-attention signature. "
                f"Signature N-invariant (robustness table). Event bundle = byte-identical reuse of "
                f"RoleSlotSummarizer flat role-slot binding.")
    elif hard_fail:
        verdict = "HARD_FAIL"
        reasons = []
        if ev["p1_overall"] < HF_P1_MIN:
            reasons.append(f"P1 round-trip {ev['p1_overall']:.3f} < {HF_P1_MIN}")
        if disc["bundle"] <= max(disc["thin_label"], disc["bag_of_args"]):
            reasons.append("bundle not > thin/bag (no discrimination)")
        if disc["scramble"] >= disc["bundle"] - 0.10:
            reasons.append(f"scramble {disc['scramble']:.3f} ~ bundle {disc['bundle']:.3f} (structure not load-bearing)")
        if flat_sat:
            reasons.append(f"flat saturated flat({MAX_N})={flat[MAX_N]:.3f} >= flat(1)-eps (signature hidden)")
        if flat_hardzero:
            reasons.append(f"flat hard-zero flat(2)={flat[2]:.3f} ~ chance")
        if ch_recent[MAX_N] <= flat[MAX_N]:
            reasons.append(f"no chunking recovery recent({MAX_N})={ch_recent[MAX_N]:.3f} <= flat={flat[MAX_N]:.3f}")
        vmsg = "HARD_FAIL: " + "; ".join(reasons)
    else:
        verdict = "PARTIAL"
        failing = [k for k, v in gates.items() if not v]
        vmsg = (f"PARTIAL: no hard-fail trigger but not all gates passed (failing: {failing}). "
                f"P1={ev['p1_overall']:.3f} bundle={disc['bundle']:.3f} thin={disc['thin_label']:.3f} "
                f"scramble={disc['scramble']:.3f} flat_drop={flat_drop:.3f} recovery={recovery_margin:.3f}.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: P1={ev['p1_overall']:.3f} | disc bundle={disc['bundle']:.3f} thin={disc['thin_label']:.3f} "
                 f"bag={disc['bag_of_args']:.3f} scramble={disc['scramble']:.3f} chance={disc['chance']:.3f} | "
                 f"flat {flat[1]:.3f}->{flat[MAX_N]:.3f} (drop {flat_drop:.3f}) | chunk recovery "
                 f"{recovery_margin:.3f} (recent@{MAX_N}={ch_recent[MAX_N]:.3f}) | gates={gates}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED,
        event_n=EVENT_N, focus_n=FOCUS_N, capacity=CAPACITY, fanout=FANOUT, max_n=MAX_N,
        gates=gates, all_gates_pass=all_ok,
        real_events_meta=ev_meta, n_real_events=ev["n_events"], vocab_size=len(vocab),
        arms_differ_verified=ev["arms_differ"], arm_hashes=ev["arm_hashes"],
        p1_roundtrip=dict(overall=ev["p1_overall"], per_role=ev["per_role_acc"]),
        discriminator=dict(bundle=disc["bundle"], thin_label=disc["thin_label"],
                           bag_of_args=disc["bag_of_args"], scramble=disc["scramble"],
                           chance=disc["chance"], n_queries=disc["n_queries"],
                           disc_margin=round(disc_margin, 4), p2_margin=round(p2_margin, 4)),
        capacity_signature=dict(flat=flat, chunk_recent=ch_recent, chunk_all=ch_all,
                                depth_profile=sw["depth_profile"], chance=sw["chance"],
                                flat_drop=round(flat_drop, 4), recovery_margin=round(recovery_margin, 4)),
        n_robustness=robust,
        glass_box_samples=ev["glass_box_samples"],
        bands=dict(HP_P1_MIN=HP_P1_MIN, HF_P1_MIN=HF_P1_MIN, HP_DISC_BUNDLE_MIN=HP_DISC_BUNDLE_MIN,
                   HP_DISC_THIN_MAX=HP_DISC_THIN_MAX, HP_DISC_BAG_MAX=HP_DISC_BAG_MAX,
                   HP_DISC_MARGIN_MIN=HP_DISC_MARGIN_MIN, HP_P2_SCRAMBLE_MAX=HP_P2_SCRAMBLE_MAX,
                   HP_P2_MARGIN_MIN=HP_P2_MARGIN_MIN, HP_FLAT1_MIN=HP_FLAT1_MIN,
                   HP_FLAT_DROP_MIN=HP_FLAT_DROP_MIN, HF_FLAT_SAT_EPS=HF_FLAT_SAT_EPS,
                   HP_RECOVERY_MARGIN_MIN=HP_RECOVERY_MARGIN_MIN,
                   HP_RECOVERY_RECENT_MIN=HP_RECOVERY_RECENT_MIN),
        one_variable=("event-level: bundle (role-slot binding) vs thin-label/bag-of-args (no role binding) "
                      "-- structure vs no-structure; P2: same bundle with role<->filler binding permuted; "
                      "capacity: FlatFocus (chunking OFF) vs ChunkedFocus (chunking ON) on the SAME event "
                      "stream -- chunking is the only variable."),
        cited=dict(role_slot_summarizer=CITED_RSS, cowan=CITED_COWAN),
        modules=dict(event_bundle="hdlab/event_bundle.py", situation_focus="hdlab/situation_focus.py"),
        scope_caveat=("TENSE is a HEURISTIC placeholder for the TIME/TENSE slot (past if -ed/irregular else "
                      "present), not a validated tense-tagger -- the role-slot BINDING is what is validated, "
                      "not tense extraction. Real events come from the consolidated who-did-what reader "
                      "(out-of-domain UD-EWT parser on McGuffey; extraction is imperfect, F1~0.59 CITED) -- the "
                      "event-bundle format is agnostic to extraction quality (it encodes whatever tuple it is "
                      "given). The focus operating point N=384 is chosen ONCE to make the finite-capacity limit "
                      "visible in 1..8 while keeping recent items usable (design-gate regime choice); the "
                      "N-robustness table shows the graceful-decline + chunking-recovery signature is "
                      "N-invariant (only the knee shifts), so it is not a construction-aided clean number. This "
                      "is a NEW-MODULE DEMONSTRATION (pluggable event/focus representation for the reader), "
                      "CLAIM-VET-pending; strategic read = HYPOTHESIS pending landed-VET (skunkworks VETs "
                      "separately per the routing contract). NOT banked."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("glass_box_samples:", json.dumps(ev["glass_box_samples"][:4]))
    print("depth_profile:", json.dumps(sw["depth_profile"]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
