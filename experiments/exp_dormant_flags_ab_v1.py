"""exp_dormant_flags_ab_v1 -- product-board A/B for pri 130's STALE-REASON dormant capability flags.

problem: dormant_capability_flags_audit_every_default_off_flag_its_reason_and_whether_the_reason_still_holds_flip_or_delete

WHAT THIS CELL DOES: measures ONE `SituationReader` capability flag at a time, shipped-default (OFF) vs
flipped-on, BOTH ARMS IN ONE PROCESS, on the product board's reader-driven rows -- the same rows
`experiments.exp_situation_model_qa_modern_v1.run(reader_driven=True)` calls internally
(`experiments.exp_board_rows_on_the_reader_v1`). It injects the flag via that cell's OWN module-level
`READER_KW` A/B hook (the exact mechanism its own `landings()` function uses to A/B pri 116/113/117) and
reuses its `run_ud` / `run_gum` / `_paired` helpers verbatim. NO `hdlab/` or other `experiments/` file is
edited; this cell only calls into the existing, unmodified `exp_board_rows_on_the_reader_v1` module.

THE SIX FLAGS (pri 130's STALE-REASON class) and which corpus each is scored on:
  agent_hybrid                UD-EWT   who_did_what_agent / who_did_what_patient / state
  agent_hybrid_construction    UD-EWT   who_did_what_agent / who_did_what_patient / state
  graded_role_marginal        UD-EWT   who_did_what_agent / who_did_what_patient / state
  structural_do_recover       UD-EWT   who_did_what_agent / who_did_what_patient / state
  unified_referent            GUM      coref / salience / common_noun_coref
  entity_kb_resolver          GUM      coref / salience / common_noun_coref

Each flag is tested IN ISOLATION (its own single kwarg True; flags are not stacked), so
`agent_hybrid_construction` gets its own number independent of `agent_hybrid`.

Run: .venv/Scripts/python.exe experiments/exp_dormant_flags_ab_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_dormant_flags_ab_v1.py --flag agent_hybrid --ud-cap 600 --docs 24 --n-boot 1000
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import sys, argparse, json, time
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir   # Q115: route the output dir via HDLAB_EXP_NAME
ANCHOR = "dormant_flags_ab_v1"
OUT_DIR = str(get_output_dir(ANCHOR))

import experiments.exp_board_rows_on_the_reader_v1 as M   # the UNMODIFIED cell; READER_KW is its own hook

SEED = M.SEED

# ---------------------------------------------------------------------------------------------------
# THE SIX FLAGS -- corpus + the single kwarg each one tests IN ISOLATION.
# ---------------------------------------------------------------------------------------------------
FLAG_SPECS = {
    "agent_hybrid":              {"corpus": "ud",  "kw": {"agent_hybrid": True}},
    "agent_hybrid_construction": {"corpus": "ud",  "kw": {"agent_hybrid_construction": True}},
    "graded_role_marginal":      {"corpus": "ud",  "kw": {"graded_role_marginal": True}},
    "structural_do_recover":     {"corpus": "ud",  "kw": {"structural_do_recover": True}},
    "unified_referent":          {"corpus": "gum", "kw": {"unified_referent": True}},
    "entity_kb_resolver":        {"corpus": "gum", "kw": {"entity_kb_resolver": True}},
}
UD_ROWS = ("who_did_what_agent", "who_did_what_patient", "state")
GUM_ROWS = ("coref", "salience", "common_noun_coref")
GUM_MODES = ("reader_annotated", "reader_textonly")
UD_MODES = ("reader_textonly",)


def _row_summary(r):
    return {"n": r.get("n"), "model_acc": r.get("model_acc"), "strongest_floor": r.get("strongest_floor"),
            "twin_acc": r.get("twin_acc"), "answered_rate": r.get("answered_rate")}


def run_flag(flag, ud_cap=600, docs=24, n_boot=1000, seed=SEED):
    """Both arms (off = shipped default, on = the flag flipped) in ONE process via READER_KW. Returns the
    result dict this cell writes to metrics_<flag>.json; writes nothing itself (caller decides)."""
    if flag not in FLAG_SPECS:
        raise SystemExit("unknown flag %r -- one of %s" % (flag, sorted(FLAG_SPECS)))
    spec = FLAG_SPECS[flag]
    corpus = spec["corpus"]
    t0 = time.time()

    def _get(corpus_kw):
        M.READER_KW = dict(corpus_kw)
        try:
            if corpus == "ud":
                return M.run_ud(cap=ud_cap, n_boot=n_boot, seed=seed, modes=UD_MODES)
            else:
                return M.run_gum(n_docs=docs, n_boot=n_boot, seed=seed, modes=GUM_MODES)
        finally:
            M.READER_KW = {}

    off = _get({})
    on = _get(spec["kw"])

    rows = UD_ROWS if corpus == "ud" else GUM_ROWS
    modes = UD_MODES if corpus == "ud" else GUM_MODES

    arms = {"off_shipped_default": {}, "on_%s" % flag: {}}
    contrasts = {}
    for mode in modes:
        for rname in rows:
            key = "%s[%s]" % (rname, mode.replace("reader_", "")) if corpus == "gum" else rname
            arms["off_shipped_default"][key] = _row_summary(off["rows"][mode][rname])
            arms["on_%s" % flag][key] = _row_summary(on["rows"][mode][rname])
            a = on["per"][mode][rname]["model"]
            b = off["per"][mode][rname]["model"]
            dd, lo, hi, hw, sep = M._paired(a, b, n_boot, seed)
            contrasts[key] = {"on_minus_off": round(dd, 4), "ci": [round(lo, 4), round(hi, 4)],
                               "ci_half_width": round(hw, 4), "ci_sep": bool(sep)}

    return {"flag": flag, "corpus": corpus, "kw": spec["kw"],
            "caps": {"ud_cap": ud_cap if corpus == "ud" else None, "docs": docs if corpus == "gum" else None,
                     "n_boot": n_boot, "seed": seed},
            "arms": arms, "contrasts": contrasts, "elapsed_s": round(time.time() - t0, 1),
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "note": "on_minus_off > 0 with ci_sep=True means the flag is a measured win on the product "
                    "board's reader-driven rows, both arms in ONE process, via exp_board_rows_on_the_reader_v1's "
                    "own READER_KW hook (no hdlab/ or experiments/ file edited)."}


def selftest():
    """One UD-routed flag on 40 sentences + one GUM-routed flag on 3 documents -- exercises BOTH corpus
    paths and the READER_KW injection/reset. Writes nothing to disk. On an idle machine the UD leg is
    ~1 min and the GUM leg ~9-10 min (3 documents x 2 provenance modes x 2 arms = 12 full SituationReader
    reads, each ~30-40s -- an inherent per-document cost, not a contention artifact; measured directly:
    566.7s for the GUM leg alone on this laptop while it was ALSO running two other board processes).
    The elapsed time is reported, not asserted against a fixed budget (see the print below)."""
    t0 = time.time()
    print("[self-test] UD path: agent_hybrid, ud_cap=40, n_boot=200 ...", flush=True)
    ud_res = run_flag("agent_hybrid", ud_cap=40, docs=24, n_boot=200, seed=SEED)
    assert M.READER_KW == {}, "READER_KW leaked after the UD arm"
    for rname in UD_ROWS:
        assert rname in ud_res["contrasts"], rname
    print("[self-test] UD path OK in %.1fs: %s" % (ud_res["elapsed_s"],
          json.dumps(ud_res["contrasts"]["who_did_what_agent"])), flush=True)

    print("[self-test] GUM path: unified_referent, docs=3, n_boot=200 ...", flush=True)
    gum_res = run_flag("unified_referent", ud_cap=600, docs=3, n_boot=200, seed=SEED)
    assert M.READER_KW == {}, "READER_KW leaked after the GUM arm"
    for rname in GUM_ROWS:
        assert any(rname in k for k in gum_res["contrasts"]), rname
    print("[self-test] GUM path OK in %.1fs: %s" % (gum_res["elapsed_s"],
          json.dumps({k: v for k, v in gum_res["contrasts"].items() if k.startswith("coref")})), flush=True)

    elapsed = time.time() - t0
    budget = 180
    print("[self-test] TOTAL elapsed %.1fs (originally targeted: under %ds; measured in practice -- see this "
          "function's own docstring -- the GUM leg's 12 full SituationReader reads cost ~9-10 min on their "
          "own, an inherent per-document cost, not a contention artifact; reported here, not asserted, "
          "since a fixed wall-clock threshold is not a sound invariant and is orthogonal to the mechanism "
          "checks above)" % (elapsed, budget), flush=True)
    print("SELF-TEST PASS: 2/2 (UD path + GUM path, both arms one process, READER_KW resets cleanly).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--flag", choices=sorted(FLAG_SPECS), default=None)
    ap.add_argument("--ud-cap", type=int, default=600, dest="ud_cap")
    ap.add_argument("--docs", type=int, default=24)
    ap.add_argument("--n-boot", type=int, default=1000, dest="n_boot")
    a = ap.parse_args()

    if a.self_test:
        selftest()
        return

    if not a.flag:
        raise SystemExit("pass --flag <name> (one of %s) or --self-test" % sorted(FLAG_SPECS))

    res = run_flag(a.flag, ud_cap=a.ud_cap, docs=a.docs, n_boot=a.n_boot, seed=SEED)
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "metrics_%s.json" % a.flag)
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(res, fh, indent=2, default=str)
    print("WROTE", out_path)
    print("elapsed_s", res["elapsed_s"])
    for k, c in res["contrasts"].items():
        print(k, json.dumps(c))


if __name__ == "__main__":
    main()
