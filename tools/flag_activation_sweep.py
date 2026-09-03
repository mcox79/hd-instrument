"""flag_activation_sweep -- GREEDY forward activation of the reader's default-off capability flags,
top-down (dependency order), with PER-DIMENSION SIGNAL TRACING so a bad upstream component that kills a
downstream dimension is caught, not silently averaged away.

Owner directive 2026-09-03 (overnight): "turn them on, 1 at a time, from the top down, measure which are
net positives and which are not; trace signal at every step to ensure one bad bottleneck component isn't
killing everything downstream; fix downstream items to work with the upstream improvements."

METHOD: start from the reader's true default (all off). Add ONE flag at a time in dependency order. At each
step, score the reader's per-dimension QA (coref / events[who-did-what] / temporal / causal / location /
belief) + the aggregate, on the SAME docs. Record the per-dimension DELTA vs the current kept baseline.
GREEDY: keep a flag if the aggregate is net non-negative AND no scored dimension is badly hurt; otherwise
mark it DROP or NEEDS-DOWNSTREAM-FIX (a dim it hurt = a downstream organ to adapt to the new upstream input).

The who-has-what dims (track_world_state / densify_world_state) and the JOINT (bind_event_tokens) are scored
by their OWN instruments (already measured net-positive: densify +0.148, world-state register, the p4 JOINT)
and are noted, not re-run here. Resumable: writes results incrementally to data/flag_activation_sweep/.
CPU, glass-box, NO LLM.
"""
from __future__ import annotations
import os
import sys
import json
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_situation_model_qa_v1 as QA  # noqa: E402
from hdlab.situation_reader import SituationReader  # noqa: E402

OUT_DIR = os.path.join(REPO, "data", "flag_activation_sweep")
os.makedirs(OUT_DIR, exist_ok=True)
RESULTS = os.path.join(OUT_DIR, "results.json")
SEED = 20260903

# Dependency-ordered (upstream -> downstream). role_route flips to the parse route so parser_arceager can act.
FLAGS_ORDER = [
    ("tense_agnostic_events", {"tense_agnostic_events": True}),   # keystone: event detection 0.33->0.95
    ("preserve_tense",        {"preserve_tense": True}),          # real tense (feeds the timeline)
    ("role_route=wired",      {"role_route": "wired"}),           # route roles through a real parse (gates arceager)
    ("parser_arceager",       {"parser_arceager": True}),         # arc-eager tree (UAS +0.067 modern; ~flat 19c)
    ("np_head_reduce",        {"np_head_reduce": True}),          # NP-head role fix (+0.20 clean who-did-what)
    ("predict_revise",        {"predict_revise": True}),          # recover dropped patients (+0.06 wdw)
    ("verb_subcat_gate",      {"verb_subcat_gate": True}),        # suppress spurious patients on intransitives
    ("predict_surprisal",     {"predict_surprisal": True}),       # N400 forward-prediction confidence
    ("timeline_register",     {"timeline_register": True}),       # TIME dimension
    ("track_space",           {"track_space": True}),             # SPACE dimension
    ("track_belief",          {"track_belief": True}),            # ToM dimension
]
DIMS = ("coref", "events", "temporal", "causal", "location", "belief")
DROP_TOL = 0.005   # a dim drop beyond this = a downstream signal loss to flag


def score(cfg, docs, gaz):
    """Monkeypatch build_reader to score a reader with an arbitrary flag set; return per-dim + aggregate acc."""
    orig = QA.build_reader
    QA.build_reader = lambda g, capable=True: SituationReader(gaz=g, **cfg)
    try:
        res = QA.run(docs, seed=SEED, capable=True)
    finally:
        QA.build_reader = orig
    pd = res.get("per_dimension", {})
    return {
        "agg": res.get("aggregate", {}).get("model_acc"),
        "dims": {d: pd.get(d, {}).get("model_acc") for d in DIMS},
        "n": res.get("aggregate", {}).get("n"),
    }


def _delta(a, b):
    return None if (a is None or b is None) else round(a - b, 4)


def main():
    t0 = time.time()
    gaz = QA.load_given_gazetteer()
    docs = [d for d in QA.load_docs(16) if os.path.exists(os.path.join(QA.CONLL_DIR, d + ".conll"))]
    print("[sweep] %d docs; greedy forward activation over %d flags" % (len(docs), len(FLAGS_ORDER)), flush=True)

    kept: dict = {}
    base = score(kept, docs, gaz)   # true default, all off
    log = {"docs": len(docs), "seed": SEED, "baseline_all_off": base, "steps": []}
    print("[sweep] BASELINE (all off): agg=%s dims=%s" % (base["agg"], base["dims"]), flush=True)
    json.dump(log, open(RESULTS, "w", encoding="ascii"), indent=2)

    for name, flags in FLAGS_ORDER:
        cfg = {**kept, **flags}
        r = score(cfg, docs, gaz)
        agg_d = _delta(r["agg"], base["agg"])
        dim_d = {d: _delta(r["dims"][d], base["dims"][d]) for d in DIMS}
        hurt = [d for d in DIMS if dim_d[d] is not None and dim_d[d] < -DROP_TOL]
        # greedy verdict: keep if aggregate non-negative AND nothing badly hurt
        if agg_d is not None and agg_d >= -1e-9 and not hurt:
            verdict = "KEEP"
        elif hurt and (agg_d is None or agg_d >= -DROP_TOL):
            verdict = "KEEP_BUT_DOWNSTREAM_FIX"   # net ~flat/up but hurt a dim -> adapt that downstream organ
        else:
            verdict = "DROP"
        step = {"flag": name, "cfg_after": {k: v for k, v in cfg.items()},
                "agg": r["agg"], "agg_delta_vs_kept": agg_d, "dims": r["dims"],
                "dim_delta_vs_kept": dim_d, "hurt_dims": hurt, "verdict": verdict}
        log["steps"].append(step)
        if verdict in ("KEEP", "KEEP_BUT_DOWNSTREAM_FIX"):
            kept = cfg
            base = r     # new baseline is the kept stack
        print("[sweep] +%-20s agg %s (%+ .4f) | dims %s | hurt %s -> %s"
              % (name, r["agg"], (agg_d or 0.0), {d: r["dims"][d] for d in DIMS}, hurt, verdict), flush=True)
        log["kept_so_far"] = list(kept.keys())
        json.dump(log, open(RESULTS, "w", encoding="ascii"), indent=2)

    log["final_kept_config"] = kept
    log["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(log, open(RESULTS, "w", encoding="ascii"), indent=2)
    print("\n[sweep] FINAL KEPT: %s" % list(kept.keys()), flush=True)
    print("[sweep] wrote %s (%.0fs)" % (RESULTS, log["elapsed_s"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
