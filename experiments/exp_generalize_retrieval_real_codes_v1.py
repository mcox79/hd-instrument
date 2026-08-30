"""exp_generalize_retrieval_real_codes_v1 -- GENERALIZATION STRESS-TEST of the store/retrieval cluster.

SOLVER problem: stress_test_which_organ_wins_actually_generalize_on_held_out_text.

WHAT THIS RERUNS. The store/retrieval/binding cluster
  - content_addressable_retrieval_over_a_separated_store  (SEP_CA hit@1 0.99 vs FLAT, synthetic)
  - the_core_binding_operator_may_not_be_brain_faithful   (theta/CA3 beats flat superposition ~5x, synthetic)
  - resolve_retrieval_interference_among_similar_memories (context resolves interference, synthetic)
all share ONE headline claim: *a SEPARATED, content-addressable / CA3 store beats a FLAT superposition
read-out under load / partial cue.* Every one of them proved it on a SYNTHETIC population: a random
|V| codebook, engineered-orthogonal (rho=0) or engineered-graded codes, and a FIXED high load
(load=32..64 items per register). The organs THEMSELVES flag this ("an isolation win is not a
capability... must be measured on the live task"; "is the substrate's REAL context separable?").

The one time the SAME family was ever tested on real held-out text -- flat_store_destroys_the_code,
addressed storage hit@1 0.1399 vs a co-occurrence COUNTING floor 0.3242 on real SimpleWiki -- it LOST.

THE GENERALIZATION QUESTION (brain-foundational). The brain's CA3 content-addressable completion works
on REAL, correlated, low-load memories every day; the DG pattern-separation stage is what makes that
possible. But the *value* of a separated store over a flat sum depends on the OPERATING POINT: how many
competing memories share an address (load), and how confusable they are. A win measured at synthetic
load=32 tells you nothing about real narrative if real entities carry ~1 event each. So: recompute the
EXACT retrieval arms (imported verbatim from the content_addressable cell) on the REAL LitBank
who-did-what population -- real entities (gold coref clusters), real Zipfian verb fillers (same verb ->
same code, so "say"/"be" recur across entities = real confusability), at each entity's REAL event count
-- against the strongest REAL floor (per-entity verb COUNTING, the flat_store lesson), the info-free
twin LOSING, and a synthetic POSITIVE CONTROL proving the harness reproduces the organ's win.

PINNED-BY-EVIDENCE: generalization/systematicity is the standard (a competence that only fires on its
training exemplars is a lookup, not the brain's operation); CA3 completion + DG separation
(Leutgeb 2007, McHugh 2007, Nakazawa 2002). OUR-INVENTION-UNDER-TEST: the per-entity register framing
(matches register_completion_real_litbank), the load-bin strata, the FHRR code assignment.

ARMS (imported from exp_content_addressable_register_retrieval_v1 -- the SAME live retrieval code):
  FLAT        : one hdlab bundle of the entity's events; unbind by the degraded cue. The incumbent.
  SEP_CA      : separated slots + CA3 content-addressable match (the fragile win).
  SEP_CA_DG   : + hdlab.dg_pattern_separation on the keys (the brain build-across for correlated codes).
  COUNTING    : predict the entity's MOST-FREQUENT verb, ignoring the cue (the strong real floor).
  SHUFFLED_KEYS / RANDOM_ROUTE : info-free twins (must LOSE).
Scorer = filler (verb) recovery hit@1. Stratified by the entity's real event count. Paired bootstrap
over ENTITIES; CI half-width + null p95 reported. Floors recomputed per population. NO number crosses
populations. Real hdlab FHRR ops. NO external LLM. CPU. ASCII-only. Deterministic.

Run: .venv/Scripts/python.exe experiments/exp_generalize_retrieval_real_codes_v1.py --self-test
     ... --smoke     ... --full
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import json
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# The SAME live retrieval code the organ validated -- imported verbatim, not reimplemented.
from experiments import exp_content_addressable_register_retrieval_v1 as CAR  # noqa: E402
from hdlab import binding, bundling                                            # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec                    # noqa: E402

ANCHOR = "generalize_retrieval_real_codes_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
WDW_PATH = os.path.join(REPO, "data", "litbank", "who_did_what_events.json")

ROLE_IDS = {"SUBJECT": 0, "OBJECT": 1, "POSSESSIVE": 2, "OTHER": 3}
D_DEFAULT = 128
CA = {"temp": CAR.CA_TEMP, "steps": CAR.CA_STEPS, "alpha": CAR.CA_ALPHA}
DG = {"expand_mult": CAR.DG_EXPAND_MULT, "sparsity": CAR.DG_SPARSITY}
BINS = [(1, 1), (2, 3), (4, 8), (9, 16), (17, 63), (64, 100000)]
BIN_LABELS = ["1", "2-3", "4-8", "9-16", "17-63", "64+"]


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------------ real population
def load_entities():
    """Real LitBank who-did-what -> per-entity event lists. entity = (doc, gold cluster).
    event = (role_id, verb). Only mentions with a gov_verb (an action the entity is in)."""
    docs = json.load(open(WDW_PATH, encoding="utf-8"))
    ents = collections.OrderedDict()
    verb_ct = collections.Counter()
    for dd in docs:
        doc = dd["doc"]
        for m in dd["stream"]:
            v = m.get("gov_verb")
            if not v:
                continue
            r = ROLE_IDS.get(m.get("role"), 3)
            ents.setdefault((doc, int(m["gold"])), []).append((r, str(v)))
            verb_ct[str(v)] += 1
    return ents, verb_ct


def build_codebooks(verb_ct, d, gen_t, correlated=False, gen_np=None):
    """Global FHRR codebooks. filler code is keyed on the VERB STRING, so the same verb across different
    entities/events shares ONE code -- this is the REAL confusability (Zipfian "be"/"say" recur), the
    single most important way real fillers differ from a fresh-per-item random codebook.

    correlated=True: near-synonym verbs get CORRELATED codes (phase interpolation toward a shared base
    per frequency-rank cluster) -- a coarse stand-in for real verb-semantic similarity, the regime where
    DG pattern-separation is claimed to matter. Default False = distinct-orthogonal-per-verb."""
    role_vecs = [unit_phase_vec(d, gen_t) for _ in range(4)]
    idx_vecs = [unit_phase_vec(d, gen_t) for _ in range(512)]  # event-slot codes (max 260 real)
    verbs = [v for v, _ in verb_ct.most_common()]
    filler = {}
    if not correlated:
        for v in verbs:
            filler[v] = unit_phase_vec(d, gen_t)
    else:
        import math
        # cluster verbs into groups sharing a base phase; within-group codes correlated (rho=0.5).
        base = {}
        for gi in range(64):
            base[gi] = torch.rand(d, generator=gen_t) * (2 * math.pi)
        for i, v in enumerate(verbs):
            b = base[i % 64]
            jit = torch.rand(d, generator=gen_t) * (2 * math.pi)
            theta = 0.5 * jit + 0.5 * b
            filler[v] = torch.polar(torch.ones(d), theta).to(torch.complex64)
    return {"role_vecs": role_vecs, "idx_vecs": idx_vecs, "filler": filler,
            "verb_list": verbs, "verb_index": {v: i for i, v in enumerate(verbs)}}


def make_entity_pop(events, cb, d, gen_t):
    """Build a CAR-compatible `pop` for ONE entity's events (a per-entity situation register).
    Reuses the organ's item algebra EXACTLY: key=bind(entity,idx), val=bind(role,filler),
    item=bind(key,val). entity_vec is constant within the register (the address that varies is the
    event index). filler_vecs is the GLOBAL verb codebook restricted to the verbs present, so
    _decode_filler's argmax-over-|V| is over the real (confusable) vocabulary the entity draws from."""
    ent_vec = unit_phase_vec(d, gen_t)
    # restrict the decode vocabulary to verbs present for THIS entity (competitors = its own events;
    # this is the per-entity register the brain holds, not the whole lexicon) -- matches the organ's
    # |V|-way argmax with a real, confusable candidate set.
    present = []
    seen = {}
    for (r, v) in events:
        if v not in seen:
            seen[v] = len(present)
            present.append(v)
    filler_vecs = [cb["filler"][v] for v in present]
    items = []
    for j, (r, v) in enumerate(events):
        f = seen[v]
        key = binding.bind(ent_vec, cb["idx_vecs"][j])
        val = binding.bind(cb["role_vecs"][r], filler_vecs[f])
        item = binding.bind(key, val)
        items.append({"e": 0, "ev": j, "r": r, "f": f, "key": key, "val": val, "item": item})
    return {"role_vecs": cb["role_vecs"], "filler_vecs": filler_vecs, "idx_vecs": cb["idx_vecs"],
            "entity_vecs": [ent_vec], "items": items, "R": 4, "V": len(present), "K": 1,
            "E": len(events), "d": d}


def counting_pred(events):
    """The strong real floor: predict the entity's MOST FREQUENT verb for every event, ignoring the cue
    (co-occurrence counting, the flat_store_destroys_the_code lesson). Returns per-event correctness."""
    verbs = [v for (_, v) in events]
    maj = collections.Counter(verbs).most_common(1)[0][0]
    return [int(v == maj) for v in verbs]


# ------------------------------------------------------------------ per-entity scoring
def score_entity(events, cb, d, p, seed, use_dg=False):
    """Run FLAT / SEP_CA / (SEP_CA_DG) / twins + COUNTING on one entity register at partial cue p.
    Returns dict arm -> mean hit@1 over that entity's events (the bootstrap unit is the ENTITY)."""
    gen_t = torch.Generator().manual_seed(seed)
    gnp = np.random.default_rng(seed + 12345)
    pop = make_entity_pop(events, cb, d, gen_t)
    cues = CAR.make_cues(pop, p, gnp, cue_mode="fragment")
    out = {}
    out["FLAT"] = CAR.accuracy(CAR.arm_flat(pop, cues, clean_key=False), pop)
    out["SEP_CA"] = CAR.accuracy(CAR.arm_sep_ca(pop, cues, temp=CA["temp"], steps=CA["steps"],
                                                alpha=CA["alpha"]), pop)
    if use_dg:
        out["SEP_CA_DG"] = CAR.accuracy(CAR.arm_sep_ca(
            pop, cues, temp=CA["temp"], steps=CA["steps"], alpha=CA["alpha"], use_dg=True,
            dg_expand_mult=DG["expand_mult"], dg_sparsity=DG["sparsity"]), pop)
    out["SHUFFLED_KEYS"] = CAR.accuracy(CAR.arm_shuffled_keys(pop, cues, gnp), pop)
    out["RANDOM_ROUTE"] = CAR.accuracy(CAR.arm_random_route(pop, cues, gnp), pop)
    out["COUNTING"] = float(np.mean(counting_pred(events)))
    return out


def bootstrap_paired(per_ent, arm_a, arm_b, gen_np, n_boot=2000, weights=None):
    """Paired bootstrap over entities of (arm_a - arm_b). If `weights` given (one per entity), the
    bootstrap resamples entities PROPORTIONAL to the weight -- used to weight the pooled result by the
    REAL bin frequency so the aggregate reflects the true operating point, not the sampled mix."""
    a = np.array([e[arm_a] for e in per_ent], dtype=np.float64)
    b = np.array([e[arm_b] for e in per_ent], dtype=np.float64)
    n = len(a)
    if n == 0:
        return {"delta": float("nan"), "lo": float("nan"), "hi": float("nan"),
                "half_width": float("nan"), "null_p95": float("nan"), "band": "NA", "n": 0}
    diffs = a - b
    if weights is not None:
        w = np.asarray(weights, dtype=np.float64); w = w / w.sum()
        point = float(np.sum(diffs * w))
        idx = np.array([gen_np.choice(n, size=n, replace=True, p=w) for _ in range(n_boot)])
        boot = diffs[idx].mean(axis=1)
        null = np.array([np.abs(np.sum(diffs * gen_np.choice([-1.0, 1.0], size=n) * w)) for _ in range(n_boot)])
    else:
        point = float(diffs.mean())
        idx = np.array([gen_np.integers(0, n, size=n) for _ in range(n_boot)])
        boot = diffs[idx].mean(axis=1)
        null = np.array([np.abs((diffs * gen_np.choice([-1.0, 1.0], size=n)).mean()) for _ in range(n_boot)])
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    p95 = float(np.percentile(null, 95))
    band = "ABOVE" if lo > 0 and lo > p95 else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": point, "lo": lo, "hi": hi, "half_width": (hi - lo) / 2.0,
            "null_p95": p95, "band": band, "n": n}


def arm_means(per_ent, arms, gen_np, n_boot=2000):
    out = {}
    for a in arms:
        v = np.array([e[a] for e in per_ent if a in e], dtype=np.float64)
        if len(v) == 0:
            out[a] = {"mean": float("nan"), "n": 0}
            continue
        boot = np.array([gen_np.choice(v, size=len(v), replace=True).mean() for _ in range(n_boot)])
        out[a] = {"mean": float(v.mean()), "lo": float(np.percentile(boot, 2.5)),
                  "hi": float(np.percentile(boot, 97.5)), "n": len(v)}
    return out


# ------------------------------------------------------------------ synthetic positive control
def synthetic_positive_control(gen_boot):
    """Reproduce the organ's OWN win with the imported arms: synthetic load=32, rho=0, partial cue
    p=0.7 -> SEP_CA must beat FLAT CI-separated. Proves a NULL on real data is a generalization gap,
    not a broken harness."""
    per = []
    for seed in (101, 113, 127):
        res, pop = CAR.run_cell(128, 32, 0.0, 0.7, seed, 20)
        # convert the organ's per-trial arrays into per-"unit" records for our bootstrap
        for t in range(len(res["FLAT"]["trials"])):
            per.append({"FLAT": res["FLAT"]["trials"][t], "SEP_CA": res["SEP_CA"]["trials"][t]})
    d = bootstrap_paired(per, "SEP_CA", "FLAT", gen_boot)
    m = arm_means(per, ["FLAT", "SEP_CA"], gen_boot)
    return {"sep_ca": m["SEP_CA"], "flat": m["FLAT"], "sep_minus_flat": d}


# ------------------------------------------------------------------ driver
def run(mode="full", n_boot=2000):
    t0 = time.perf_counter()
    d = D_DEFAULT
    ents, verb_ct = load_entities()
    gen_t_cb = torch.Generator().manual_seed(20260830)
    cb = build_codebooks(verb_ct, d, gen_t_cb, correlated=False)

    # bucket entities by event count; record the REAL bin frequency BEFORE any capping.
    by_bin_all = {lbl: [] for lbl in BIN_LABELS}
    for (ekey, events) in ents.items():
        n = len(events)
        for (lo, hi), lbl in zip(BINS, BIN_LABELS):
            if lo <= n <= hi:
                by_bin_all[lbl].append((ekey, events)); break
    real_bin_count = {lbl: len(by_bin_all[lbl]) for lbl in BIN_LABELS}
    real_total = sum(real_bin_count.values())

    # caps: LOW bins are homogeneous (1-event is exactly 1.0) so a sample suffices; HIGH bins are the
    # interesting minority -> use ALL of them. Weighting restores the true operating point regardless.
    caps = {"1": 300, "2-3": 300, "4-8": 300, "9-16": 100000, "17-63": 100000, "64+": 100000}
    if mode == "smoke":
        caps = {l: 60 for l in BIN_LABELS}
    p_list = [0.0, 0.7] if mode == "full" else [0.7]

    rng_sample = np.random.default_rng(7)
    by_bin = {}
    for lbl in BIN_LABELS:
        lst = by_bin_all[lbl]
        if len(lst) > caps[lbl]:
            sel = rng_sample.choice(len(lst), size=caps[lbl], replace=False)
            by_bin[lbl] = [lst[i] for i in sel]
        else:
            by_bin[lbl] = lst

    _log("real bin freq: " + " ".join("%s=%d(%.1f%%)" % (l, real_bin_count[l], 100 * real_bin_count[l] / real_total)
                                       for l in BIN_LABELS))
    _log("sampled/bin: " + " ".join("%s=%d" % (l, len(by_bin[l])) for l in BIN_LABELS))
    gen_boot = np.random.default_rng(20260830)

    results = {"per_p": {}, "bin_labels": BIN_LABELS, "real_bin_count": real_bin_count, "real_total": real_total}
    for p in p_list:
        all_recs, all_w = [], []
        per_bin_out = {}
        for lbl in BIN_LABELS:
            recs = []
            use_dg = lbl in ("17-63", "64+")
            for si, (ekey, events) in enumerate(by_bin[lbl]):
                recs.append(score_entity(events, cb, d, p, seed=1000 + si, use_dg=use_dg))
            # weight each sampled entity by real_bin_count/n_sampled so the pool reflects reality
            w = real_bin_count[lbl] / max(1, len(recs))
            all_recs.extend(recs); all_w.extend([w] * len(recs))
            arms = ["FLAT", "SEP_CA", "COUNTING", "SHUFFLED_KEYS", "RANDOM_ROUTE"] + (["SEP_CA_DG"] if use_dg else [])
            per_bin_out[lbl] = {
                "n": len(recs), "real_bin_count": real_bin_count[lbl],
                "means": arm_means(recs, arms, gen_boot, n_boot),
                "sep_minus_flat": bootstrap_paired(recs, "SEP_CA", "FLAT", gen_boot, n_boot),
                "sep_minus_counting": bootstrap_paired(recs, "SEP_CA", "COUNTING", gen_boot, n_boot),
                "flat_minus_counting": bootstrap_paired(recs, "FLAT", "COUNTING", gen_boot, n_boot),
                "sep_minus_twin": bootstrap_paired(recs, "SEP_CA", "SHUFFLED_KEYS", gen_boot, n_boot),
            }
            if use_dg:
                per_bin_out[lbl]["dg_minus_sep"] = bootstrap_paired(recs, "SEP_CA_DG", "SEP_CA", gen_boot, n_boot)
        # REAL-FREQUENCY-WEIGHTED pooled = the deployed value at the true operating point
        pooled = {
            "n": len(all_recs),
            "sep_minus_flat": bootstrap_paired(all_recs, "SEP_CA", "FLAT", gen_boot, n_boot, weights=all_w),
            "sep_minus_counting": bootstrap_paired(all_recs, "SEP_CA", "COUNTING", gen_boot, n_boot, weights=all_w),
            "sep_minus_twin": bootstrap_paired(all_recs, "SEP_CA", "SHUFFLED_KEYS", gen_boot, n_boot, weights=all_w),
            "flat_minus_counting": bootstrap_paired(all_recs, "FLAT", "COUNTING", gen_boot, n_boot, weights=all_w),
        }
        # weighted arm means
        wv = np.asarray(all_w, dtype=np.float64); wv = wv / wv.sum()
        wmeans = {a: float(np.sum(np.array([r[a] for r in all_recs]) * wv))
                  for a in ["FLAT", "SEP_CA", "COUNTING"]}
        pooled["weighted_means"] = wmeans
        results["per_p"]["p%.1f" % p] = {"pooled_real_weighted": pooled, "by_bin": per_bin_out}
        _log("p=%.1f WEIGHTED-real: SEP_CA=%.3f FLAT=%.3f COUNT=%.3f | SEP-FLAT=%+.3f[%s] SEP-COUNT=%+.3f[%s]"
             % (p, wmeans["SEP_CA"], wmeans["FLAT"], wmeans["COUNTING"], pooled["sep_minus_flat"]["delta"],
                pooled["sep_minus_flat"]["band"], pooled["sep_minus_counting"]["delta"],
                pooled["sep_minus_counting"]["band"]))

    # ---- DG build-across drill: with CORRELATED verb codes (near-synonyms similar), is DG needed? ----
    _log("DG DRILL: correlated verb codes at the high-fan tail (does DG pattern-separation help THERE?)")
    gen_t_corr = torch.Generator().manual_seed(20260831)
    cb_corr = build_codebooks(verb_ct, d, gen_t_corr, correlated=True)
    dg_drill = {}
    for lbl in ("17-63", "64+"):
        recs_o, recs_c = [], []
        for si, (ekey, events) in enumerate(by_bin[lbl]):
            recs_o.append(score_entity(events, cb, d, 0.7, seed=2000 + si, use_dg=True))
            recs_c.append(score_entity(events, cb_corr, d, 0.7, seed=2000 + si, use_dg=True))
        dg_drill[lbl] = {
            "orthogonal_codes": {"means": arm_means(recs_o, ["SEP_CA", "SEP_CA_DG", "FLAT"], gen_boot, n_boot),
                                 "dg_minus_sep": bootstrap_paired(recs_o, "SEP_CA_DG", "SEP_CA", gen_boot, n_boot)},
            "correlated_codes": {"means": arm_means(recs_c, ["SEP_CA", "SEP_CA_DG", "FLAT"], gen_boot, n_boot),
                                 "dg_minus_sep": bootstrap_paired(recs_c, "SEP_CA_DG", "SEP_CA", gen_boot, n_boot)},
        }
        _log("  %s ortho: SEP=%.3f DG=%.3f (DG-SEP %+.3f[%s]) | corr: SEP=%.3f DG=%.3f (DG-SEP %+.3f[%s])"
             % (lbl, dg_drill[lbl]["orthogonal_codes"]["means"]["SEP_CA"]["mean"],
                dg_drill[lbl]["orthogonal_codes"]["means"]["SEP_CA_DG"]["mean"],
                dg_drill[lbl]["orthogonal_codes"]["dg_minus_sep"]["delta"],
                dg_drill[lbl]["orthogonal_codes"]["dg_minus_sep"]["band"],
                dg_drill[lbl]["correlated_codes"]["means"]["SEP_CA"]["mean"],
                dg_drill[lbl]["correlated_codes"]["means"]["SEP_CA_DG"]["mean"],
                dg_drill[lbl]["correlated_codes"]["dg_minus_sep"]["delta"],
                dg_drill[lbl]["correlated_codes"]["dg_minus_sep"]["band"]))
    results["dg_build_across_drill"] = dg_drill

    # synthetic positive control (harness reproduces the organ's win)
    results["synthetic_positive_control"] = synthetic_positive_control(gen_boot)
    spc = results["synthetic_positive_control"]["sep_minus_flat"]
    _log("SYNTHETIC POS-CTRL (load=32 rho=0 p=0.7): SEP_CA-FLAT = %+.3f [%.3f,%.3f] band=%s"
         % (spc["delta"], spc["lo"], spc["hi"], spc["band"]))

    results["meta"] = {"anchor": ANCHOR, "mode": mode, "d": d, "n_entities_total": len(ents),
                       "n_events_total": int(sum(len(v) for v in ents.values())),
                       "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                       "ca_params": CA, "dg_params": DG}
    return results


# ------------------------------------------------------------------ self-test
def self_test():
    _log("SELF-TEST: real cache loads; distribution matches the known n=28569 events")
    ents, verb_ct = load_entities()
    n_ev = sum(len(v) for v in ents.values())
    assert n_ev == 28569, "expected 28569 gov_verb events, got %d" % n_ev
    assert 7000 <= len(ents) <= 8500, "entity count off: %d" % len(ents)
    _log("  entities=%d events=%d distinct_verbs=%d" % (len(ents), n_ev, len(verb_ct)))

    _log("SELF-TEST: a single-event entity is trivially recovered by FLAT and SEP_CA at full cue")
    d = 128
    gen_t = torch.Generator().manual_seed(1)
    cb = build_codebooks(verb_ct, d, gen_t)
    r = score_entity([(0, "say")], cb, d, p=0.0, seed=1)
    assert r["FLAT"] == 1.0 and r["SEP_CA"] == 1.0, "single-event full-cue must be exact: %s" % r

    _log("SELF-TEST: harness reproduces the organ's SYNTHETIC win (SEP_CA>FLAT at load=32,p=0.7)")
    res, pop = CAR.run_cell(128, 32, 0.0, 0.7, 101, 12)
    assert res["SEP_CA"]["mean"] > res["FLAT"]["mean"] + 0.10, \
        "harness must reproduce the organ's win: SEP_CA=%.3f FLAT=%.3f" % (res["SEP_CA"]["mean"], res["FLAT"]["mean"])
    _log("  synthetic load=32 p=0.7: SEP_CA=%.3f FLAT=%.3f (reproduced)" % (res["SEP_CA"]["mean"], res["FLAT"]["mean"]))

    _log("SELF-TEST: counting floor = per-entity majority verb")
    assert counting_pred([(0, "be"), (1, "be"), (0, "say")]) == [1, 1, 0], "counting floor wrong"
    _log("SELF-TEST PASS")
    return {"n_entities": len(ents), "n_events": n_ev, "distinct_verbs": len(verb_ct)}


# ------------------------------------------------------------------ harness
def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()

    if args.self_test or not (args.smoke or args.full):
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now_iso()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    mode = "full" if args.full else "smoke"
    res = run(mode=mode, n_boot=2000 if mode == "full" else 800)
    out = OUTPUT_DIR if mode == "full" else os.path.join(OUTPUT_DIR, "_smoke")
    _atomic_write(os.path.join(out, "metrics.json"), res)
    _log("DONE %s in %.1fs -> %s" % (mode, time.perf_counter() - t0, out))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                      {"verdict": "CELL_CRASHED", "err": "%s: %s" % (type(e).__name__, str(e)[:400]),
                       "traceback": traceback.format_exc()[:3000], "ts_iso": _now_iso()})
        raise
