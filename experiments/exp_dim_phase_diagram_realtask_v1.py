"""DIMENSIONAL PHASE DIAGRAM -- the REAL cross-sentence who-did-what task, register decode vs D.

Part A/B (exp_dim_phase_diagram_register_v1) is the SYNTHETIC cliff + positive control + lever test on
the register primitive. THIS cell anchors it to the LIVE task: it sweeps the FHRR dimensionality D of
the situation-model register on the real LitBank entity-tracking harness and asks whether the observed
who-did-what ceiling MOVES with D (UNDER-DIMENSIONED) or is FLAT (STRUCTURAL: the bottleneck is linking/
mechanism, not capacity).

HOW: the harness `experiments.exp_litbank_entity_tracking_end_to_end_v1` reads its FHRR dim from a MODULE
GLOBAL `D`; we monkeypatch `H.D = d` per sweep point and re-run `H.run(...)` -- no hdlab write, no cell
edit. At each D we recompute, ON THAT D's OWN register population:
  * ORACLE pronoun-subset accuracy = the register's decode fidelity GIVEN perfect linking (the cleanest
    read of "is the register capacity-limited here?").
  * ACTR_BINDER pronoun/full accuracy = the live organ.
  * FLOORS recomputed at each D: majority-verb floor (label-frequency, D-independent) AND the info-free
    SHUFFLED_TWIN (scrambled linking through the SAME D register -- D-dependent) AND STRING_IDENTITY.
  * fan_profile (accuracy stratified by entity event-count) -- WHERE on the load axis the real organ sits.
Both backends (multibank=live default, flat=the un-routed store) at each D -> the two-lever read on the
real task too.

VERDICT RULE (bar sec 2): STRUCTURAL if ORACLE pron acc is flat within CI across the top of the D range
and the twin still loses at the operating D; UNDER-DIMENSIONED if it is CI-separated-RISING at D=1024.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_realtask_v1.py [--docs N] [--dgrid 256,1024,4096] [--nboot 500]
ASCII only. Writes ONLY to data/exp_dim_phase_diagram_realtask_v1/. NO hdlab/ write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_realtask_v1")
D_GRID = [256, 512, 1024, 2048, 4096, 8192]


def _install_fast_decode():
    """Runtime-patch the register classes' decode() with a VECTORISED cleanup (one matmul over a cached
    [V, d] role matrix) instead of the organ's Python loop over V verbs. IDENTICAL math -- argmax over
    Re(sum(conj(role_v) * readback)) -- just not O(V) torch calls per decode (the D=8192 bottleneck). This
    is a runtime speed patch to MY copy of the class methods, NOT an hdlab file edit; the science is
    byte-identical to hdlab.situation_model_accumulate.cleanup_argmax."""
    import torch
    from hdlab import binding as _b
    from hdlab.situation_model_accumulate import AccumulateRegister
    from hdlab.situation_model_multibank import MultiBankAccumulateRegister, stable_bank_id

    def _rolemat(self):
        rm = getattr(self, "_rolemat_cache", None)
        if rm is None:
            self._role_names = list(self.role_vecs.keys())
            rm = torch.stack([self.role_vecs[n] for n in self._role_names], dim=0)
            self._rolemat_cache = rm
        return rm

    def flat_decode(self, entity, event_idx):
        rm = _rolemat(self); reg = self.register(entity)
        read = _b.unbind(reg, self.idx_vecs[event_idx])
        return self._role_names[int(torch.argmax(torch.real(torch.conj(rm) @ read)))], {}

    def mb_decode(self, entity, event_idx):
        rm = _rolemat(self); bank = stable_bank_id(event_idx, self.n_banks)
        reg = self._bank_register(entity, bank)
        read = _b.unbind(reg, self.idx_vecs[event_idx])
        return self._role_names[int(torch.argmax(torch.real(torch.conj(rm) @ read)))], {}

    AccumulateRegister.decode = flat_decode
    MultiBankAccumulateRegister.decode = mb_decode


def _ci_overlap(a, b):
    """True if two [pt, lo, hi] CIs overlap (accuracy indistinguishable)."""
    return not (a[2] < b[1] or b[2] < a[1])


def sweep(docs=100, d_grid=None, n_boot=500, backends=("multibank", "flat")):
    d_grid = d_grid or D_GRID
    _install_fast_decode()          # vectorised cleanup -> the sweep is fast + local (identical math)
    recs = H.load_cache()[:docs]
    rows = {b: {} for b in backends}
    orig_D = H.D
    try:
        for backend in backends:
            for d in d_grid:
                H.D = d
                res = H.run(records=recs, backend=backend, n_boot=n_boot)
                rows[backend][d] = {
                    "oracle_pron": res["accuracy_pronoun"]["ORACLE"],
                    "actr_pron": res["accuracy_pronoun"]["ACTR_BINDER"],
                    "string_identity_pron": res["accuracy_pronoun"]["STRING_IDENTITY"],
                    "shuffled_twin_pron": res["accuracy_pronoun"]["SHUFFLED_TWIN"],
                    "actr_full": res["accuracy_full"]["ACTR_BINDER"],
                    "majority_floor_pron": res["majority_verb_floor_pronoun"],
                    "fan_oracle": res["fan_profile_oracle"],
                    "actr_over_twin_pron": res["ACTR_over_shuffled_twin_pronoun"],
                    "n_pron": res["n_pronoun_queries"],
                }
    finally:
        H.D = orig_D
    return {"docs": docs, "d_grid": d_grid, "n_boot": n_boot, "rows": rows}


def verdict(rows_backend, d_grid):
    """STRUCTURAL vs UNDER-DIMENSIONED for the ORACLE register-decode curve (cleanest read of capacity)."""
    top = d_grid[-1]; op = 1024 if 1024 in d_grid else d_grid[len(d_grid) // 2]
    lo_probe = d_grid[0]
    oracle = {d: rows_backend[d]["oracle_pron"] for d in d_grid}
    # rising at operating point? compare op vs top: if top CI-separated ABOVE op -> still climbing
    a_op, a_top = oracle[op], oracle[top]
    rising = a_top[1] > a_op[2]     # top lower-bound above op upper-bound
    flat_top = _ci_overlap(oracle[op], oracle[top])
    twin = rows_backend[op]["actr_over_twin_pron"]["band"]
    return {"operating_D": op, "oracle_at_lo": oracle[lo_probe], "oracle_at_op": a_op,
            "oracle_at_top": a_top, "rising_op_to_top": bool(rising), "flat_op_to_top": bool(flat_top),
            "twin_loses_at_op": twin == "ABOVE",
            "verdict": "UNDER_DIMENSIONED" if rising else "STRUCTURAL"}


def summarize(res):
    d_grid = res["d_grid"]
    for backend in res["rows"]:
        rb = res["rows"][backend]
        print(f"\n=== REAL-TASK register phase diagram [{backend}] "
              f"(docs={res['docs']}, n_pron={rb[d_grid[0]]['n_pron']}) ===")
        print("     D    ORACLE_pron[lo,hi]     ACTR_pron        strID    shuf_twin   maj_floor")
        for d in d_grid:
            r = rb[d]
            o, a = r["oracle_pron"], r["actr_pron"]
            print(f"  {d:>5d}  {o[0]:.3f}[{o[1]:.3f},{o[2]:.3f}]  {a[0]:.3f}[{a[1]:.3f},{a[2]:.3f}]  "
                  f"{r['string_identity_pron'][0]:.3f}  {r['shuffled_twin_pron'][0]:.3f}  {r['majority_floor_pron']}")
        v = verdict(rb, d_grid)
        print(f"  VERDICT [{backend}]: ORACLE register decode {v['verdict']}  "
              f"(op D={v['operating_D']}: {v['oracle_at_op'][0]:.3f}; top D={d_grid[-1]}: {v['oracle_at_top'][0]:.3f}; "
              f"rising={v['rising_op_to_top']}, twin_loses={v['twin_loses_at_op']})")
    # multibank vs flat at operating D = the real-task lever read
    if "flat" in res["rows"] and "multibank" in res["rows"]:
        op = 1024 if 1024 in d_grid else d_grid[len(d_grid) // 2]
        mb = res["rows"]["multibank"][op]["oracle_pron"][0]
        fl = res["rows"]["flat"][op]["oracle_pron"][0]
        print(f"\n  LEVER (real task, D={op}): flat ORACLE={fl:.3f}  multibank ORACLE={mb:.3f}  "
              f"routing_gain={mb-fl:+.3f}")


def main():
    docs = 100
    d_grid = D_GRID
    n_boot = 500
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    if "--dgrid" in sys.argv:
        d_grid = [int(x) for x in sys.argv[sys.argv.index("--dgrid") + 1].split(",")]
    if "--nboot" in sys.argv:
        n_boot = int(sys.argv[sys.argv.index("--nboot") + 1])
    backends = ("multibank", "flat")
    if "--mbonly" in sys.argv:
        backends = ("multibank",)
    t0 = time.time()
    res = sweep(docs=docs, d_grid=d_grid, n_boot=n_boot, backends=backends)
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["verdict"] = {b: verdict(res["rows"][b], d_grid) for b in res["rows"]}
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    tag = f"_docs{docs}_d{'-'.join(str(x) for x in d_grid)}"
    with open(os.path.join(OUTDIR, f"metrics{tag}.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR}  (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
