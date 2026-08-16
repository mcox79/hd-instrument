"""exp_meaning_asset_hardened_margins_v2_complete -- the COMPLETE headline table.

Supersedes exp_meaning_asset_hardened_margins_v1, which ran at 18:12 while
data/exp_meaning_asset_fair_test_v1/units.jsonl was still being written and therefore
covered only 6 of the 25 arms. It missed ASSET_V2_CTX, both ASSET_RETRAIN_* read-outs and
ASSET_NORMS12 -- i.e. every arm that scored highest. Nothing about any arm is recomputed
here; this reads the per-pair cosines the two fair-test cells already wrote.

What this cell fixes, beyond coverage:
1. FLOOR SEED CHOICE. v1 took seed 7 for the floor arms. A_ORTHOGRAPHIC / A_FREQUENCY /
   OWN_SCRAMBLE are the seeded arms (their per-pair cosines DO move with the nuisance seed;
   the asset arms' do not, asserted in self-test). Taking one seed can understate the floor.
   Here the floor takes the seed with the HIGHEST rho -- the STRONGEST floor, per the
   standing rule. This can only lower a margin, never raise it.
2. CONCRETENESS CONTROL ON THE INSTRUMENT POPULATION. A concreteness confound has inflated
   a learned-encoder result on this project before. Every margin is recomputed as a paired
   bootstrap of PARTIAL rho (both words' mean concreteness and their absolute difference
   regressed out of both rank vectors), alongside the raw margin.
3. TRAINED vs RANDOM-INIT on the instrument population, per read-out. A random-init arm has
   TIED the learned encoder before.

Population: the instrument's own 322 covered SimLex-999 pairs at V=4096. Like-for-like.
Identity-axis numbers are carried through UNAVERAGED and reported in their own block.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS
import exp_meaning_asset_fair_test_v1 as FT
import exp_meaning_asset_power_extension_v1 as PX
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import load_units

ANCHOR_NAME = "meaning_asset_hardened_margins_v2_complete"
SRC = ["data/exp_meaning_asset_fair_test_v1",
       "data/exp_meaning_asset_fair_test_v1b_distributional"]
FAIRTEST_METRICS = REPO / "data/exp_meaning_asset_fair_test_v1/metrics.json"

# arms that ARE floors / controls, never scored as assets
NON_ASSET = {"A_COLLAPSE", "A_RANDOM_IID", "A_FREQUENCY"}
# published values re-asserted before anything is reported (right-arm / right-metric guard)
PUBLISHED = {
    "d512|ASSET_V2_ISOL": 0.18904546318905402,
    "d512|ASSET_V2_CTX": 0.20646711075675162,
    "d512|ASSET_RETRAIN_ISOL": 0.2581,     # 4dp, checked loosely
    "d12|ASSET_NORMS12": 0.2701,           # 4dp, checked loosely
}


def load_cos():
    """{f'd{d}|{arm}': {seed: per-pair cosine vector}} from the two fair-test cells."""
    cos = {}
    for s in SRC:
        for u in load_units(str(REPO / s)).values():
            if not isinstance(u, dict) or "simlex_cos" not in u:
                continue
            key = f"d{u['d']}|{u['arm']}"
            cos.setdefault(key, {})[int(u["seed"])] = np.array(u["simlex_cos"],
                                                               dtype=np.float64)
    return cos


def strongest_seed(byseed, gold):
    """The seed whose rho is HIGHEST -- the strongest version of a seeded floor."""
    best = max(byseed, key=lambda s: FT._spearman(byseed[s], gold))
    return byseed[best], best, FT._spearman(byseed[best], gold)


def selftest(cos, pairs, gold) -> None:
    print("[selftest] ...", flush=True)
    assert len(pairs) == 322, f"pair count {len(pairs)} != 322"
    for k, v in cos.items():
        assert len(v) == 3, f"{k} has seeds {sorted(v)}, expected 3"
        assert all(len(x) == 322 for x in v.values()), f"{k} pair-set mismatch"
    # asset arms must be seed-invariant (they are deterministic given the checkpoint/table);
    # if this ever fails, the "use seed 7" shortcut below is unsound and must not be used.
    for k, v in cos.items():
        if "ASSET_" in k and not k.endswith("_SHUFFLED"):
            a = v[min(v)]
            md = max(float(np.abs(a - v[s]).max()) for s in v)
            assert md == 0.0, f"{k} asset arm varies across seeds by {md}"
    # seeded floors must actually vary, else the strongest-seed step is a no-op we'd not notice
    varies = 0
    for k, v in cos.items():
        if k.endswith("_SHUFFLED") or "|A_FREQUENCY" in k:
            a = v[min(v)]
            if max(float(np.abs(a - v[s]).max()) for s in v) > 0:
                varies += 1
    assert varies >= 6, f"only {varies} seeded floor arms vary across seeds"
    # right-metric: our rho on the stored cosines must reproduce the published per-arm rho
    m = json.loads(FAIRTEST_METRICS.read_text())
    for key, want in PUBLISHED.items():
        got = FT._spearman(cos[key][7], gold)
        tol = 1e-9 if abs(want) > 0.01 and len(str(want)) > 8 else 1e-4
        assert abs(got - want) <= tol, f"{key}: {got} vs published {want}"
        assert abs(m["per_arm"][key]["simlex_rho"] - got) <= 1e-12, f"{key} metrics.json mismatch"
    # band() sanity
    assert FT.band([0.1, 0.2]) == "ABOVE"
    assert FT.band([-0.1, 0.2]) == "NOT_SEPARATED"
    assert FT.band([-0.2, -0.1]) == "BELOW"
    # partial_spearman must null out a CONFOUND: two variables correlated only THROUGH the
    # control must come out ~0 partial while their RAW rho is high. (A degenerate y == control
    # is not a valid case -- its residual is identically zero and the correlation undefined.)
    rng = np.random.default_rng(0)
    n = 4000
    z = rng.normal(size=n)
    a = z + 0.3 * rng.normal(size=n)
    b = z + 0.3 * rng.normal(size=n)
    C = z.reshape(-1, 1)
    raw = FT._spearman(a, b)
    par = PX.partial_spearman(a, b, C)
    assert raw > 0.8, f"confound setup broken: raw rho {raw}"
    assert abs(par) < 0.06, f"partial_spearman leaves {par} of a pure confound"
    # and it must NOT destroy a real association independent of the control
    e = rng.normal(size=n)
    f = e + 0.3 * rng.normal(size=n)
    assert PX.partial_spearman(e, f, C) > 0.8, "partial_spearman destroys a real association"
    print("[selftest] OK", flush=True)


def boot_partial_diff(a, b, gold, ctrl, n_boot=2000, seed=FT.BOOT_SEED):
    """Paired bootstrap of partial_rho(a) - partial_rho(b), controls regressed out."""
    n = len(gold)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    d = np.empty(n_boot)
    for i in range(n_boot):
        j = idx[i]
        d[i] = (PX.partial_spearman(a[j], gold[j], ctrl[j])
                - PX.partial_spearman(b[j], gold[j], ctrl[j]))
    d = d[np.isfinite(d)]
    pt = PX.partial_spearman(a, gold, ctrl) - PX.partial_spearman(b, gold, ctrl)
    return {"point": float(pt), "ci95": [float(np.percentile(d, 2.5)),
                                         float(np.percentile(d, 97.5))], "n": int(n)}


def main() -> int:
    t0 = time.time()
    words, counts = INS.build_vocab(INS.CORPUS, INS.CORPUS_BYTES, INS.V)
    w2i = {w: i for i, w in enumerate(words)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(INS.SIMLEX) if a in w2i and b in w2i]
    gold = np.array([s for _, _, s in pairs], dtype=np.float64)

    cos = load_cos()
    selftest(cos, pairs, gold)
    if "--self-test" in sys.argv:
        print("SELFTEST_ONLY_OK")
        return 0

    # ---- seed-free frequency floor, computed directly on the pair scores
    lf = np.log(counts + 1.0)
    la = np.array([lf[w2i[a]] for a, _, _ in pairs])
    lb = np.array([lf[w2i[b]] for _, b, _ in pairs])
    freq_channels = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb),
                     "FREQ_SUM": la + lb,
                     "FREQ_MIN": np.minimum(la, lb),
                     "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    freq_rho = {k: FT._spearman(v, gold) for k, v in freq_channels.items()}
    best_freq = max(freq_rho, key=lambda k: freq_rho[k])

    # ---- concreteness controls on the instrument population
    brys = FT.brysbaert_conc()
    ok = np.array([(a in brys and b in brys) for a, b, _ in pairs])
    ca = np.array([brys.get(a, np.nan) for a, _, _ in pairs])
    cb = np.array([brys.get(b, np.nan) for _, b, _ in pairs])
    ctrl_full = np.column_stack([(ca + cb) / 2.0, np.abs(ca - cb)])

    rows = {}
    for key in sorted(cos):
        d, arm = key.split("|", 1)
        if arm.endswith("_SHUFFLED") or arm in NON_ASSET:
            continue
        c = cos[key][7]
        cands = {"HARDENED_FREQUENCY_" + best_freq: (freq_channels[best_freq], "seed-free")}
        o = cos.get(f"{d}|A_ORTHOGRAPHIC")
        if o:
            v, s, _ = strongest_seed(o, gold)
            cands["A_ORTHOGRAPHIC"] = (v, f"strongest of 3 seeds (seed {s})")
        sh = cos.get(f"{d}|{arm}_SHUFFLED")
        if sh:
            v, s, _ = strongest_seed(sh, gold)
            cands["OWN_SCRAMBLE"] = (v, f"strongest of 3 seeds (seed {s})")
        rho_f = {k: FT._spearman(v[0], gold) for k, v in cands.items()}
        bf = max(rho_f, key=lambda k: rho_f[k])
        fv = cands[bf][0]

        diff = FT.boot_rho_diff(c, fv, gold)
        b = FT.band(diff["ci95"])
        pdiff = boot_partial_diff(c[ok], fv[ok], gold[ok], ctrl_full[ok])
        rows[key] = {
            "arm_rho": FT.boot_rho(c, gold),
            "floor_rho_by_arm": {k: round(v, 4) for k, v in rho_f.items()},
            "floor_seed_policy": {k: v[1] for k, v in cands.items()},
            "strongest_floor": bf,
            "margin_over_strongest_floor": diff,
            "band": b,
            "clears_floor": bool(b == "ABOVE" and diff["point"] >= FT.T_MARGIN_MIN),
            "concreteness_controlled": {
                "n_pairs_with_concreteness": int(ok.sum()),
                "arm_partial_rho": round(PX.partial_spearman(c[ok], gold[ok], ctrl_full[ok]), 4),
                "floor_partial_rho": round(PX.partial_spearman(fv[ok], gold[ok], ctrl_full[ok]), 4),
                "partial_margin": pdiff,
                "band": FT.band(pdiff["ci95"]),
                "clears_floor_concreteness_controlled":
                    bool(FT.band(pdiff["ci95"]) == "ABOVE" and pdiff["point"] >= FT.T_MARGIN_MIN),
            },
        }

    # ---- trained vs random-init, instrument population
    tvr = {}
    for ro in ("TOKEMB", "ISOL", "CTX"):
        r = cos.get(f"d512|CTRL_RANDINIT_{ro}")
        if not r:
            continue
        for fam in ("ASSET_V2", "ASSET_RETRAIN"):
            a = cos.get(f"d512|{fam}_{ro}")
            if not a:
                continue
            dd = FT.boot_rho_diff(a[7], r[7], gold)
            tvr[f"d512|{fam}_{ro}_vs_RANDINIT"] = {
                "trained_rho": round(FT._spearman(a[7], gold), 4),
                "random_init_rho": round(FT._spearman(r[7], gold), 4),
                "diff": dd, "band": FT.band(dd["ci95"]),
            }

    # ---- identity axis, carried through UNAVERAGED
    fm = json.loads(FAIRTEST_METRICS.read_text())
    identity = {k: {"sigma_half": v.get("sigma_half"),
                    "recov_N_GATE_sigma1": v.get("recov_N_GATE_sigma1"),
                    "bundling_bits_after_sum": v.get("bundling_bits_after_sum")}
                for k, v in fm["per_arm"].items()}

    clears = sorted(k for k, v in rows.items() if v["clears_floor"] and "|ASSET_" in k)
    clears_cc = sorted(k for k, v in rows.items()
                       if v["concreteness_controlled"]["clears_floor_concreteness_controlled"]
                       and "|ASSET_" in k)
    both = sorted(set(clears) & set(clears_cc))
    verdict = "ASSET_CLEARS_THE_HARDENED_FLOOR" if both else "NO_ASSET_CLEARS_THE_HARDENED_FLOOR"

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": "full", "n_pairs": len(pairs),
        "population": "the instrument's own 322 covered SimLex-999 pairs at V=4096 (like-for-like)",
        "supersedes": "data/exp_meaning_asset_hardened_margins_v1/metrics.json (partial: 6 of 25 arms)",
        "hardened_frequency_floor": {"channel": best_freq, "rho": round(freq_rho[best_freq], 4),
                                     "all_channels": {k: round(v, 4) for k, v in freq_rho.items()}},
        "predeclared_margin_min": FT.T_MARGIN_MIN,
        "verdict": verdict,
        "arms_clearing_raw": clears,
        "arms_clearing_concreteness_controlled": clears_cc,
        "arms_clearing_BOTH": both,
        "rows": rows,
        "trained_vs_random_init": tvr,
        "IDENTITY_AXIS_NOT_AVERAGED_WITH_STRUCTURE": identity,
        "note": ("Every margin is a PAIRED bootstrap over the identical 322 SimLex pairs "
                 "(10,000 resamples raw / 2,000 partial). Seeded floors take their STRONGEST "
                 "seed. Both hardenings can only lower a margin."),
    }
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["summary"] = verdict
    write_metrics(out_dir, out)

    for k, v in sorted(rows.items(), key=lambda kv: -kv[1]["arm_rho"]["point"]):
        m = v["margin_over_strongest_floor"]
        cc = v["concreteness_controlled"]["partial_margin"]
        print(f"{k:<34} rho={v['arm_rho']['point']:+.4f} "
              f"[{v['arm_rho']['ci95'][0]:+.4f},{v['arm_rho']['ci95'][1]:+.4f}]  "
              f"floor={v['strongest_floor']:<30} margin={m['point']:+.4f} "
              f"[{m['ci95'][0]:+.4f},{m['ci95'][1]:+.4f}] {v['band']:<14} "
              f"| conc-ctrl {cc['point']:+.4f} [{cc['ci95'][0]:+.4f},{cc['ci95'][1]:+.4f}] "
              f"{v['concreteness_controlled']['band']}")
    print()
    for k, v in sorted(tvr.items()):
        print(f"{k:<44} trained={v['trained_rho']:+.4f} randinit={v['random_init_rho']:+.4f} "
              f"diff={v['diff']['point']:+.4f} "
              f"[{v['diff']['ci95'][0]:+.4f},{v['diff']['ci95'][1]:+.4f}] {v['band']}")
    print("\nVERDICT:", verdict, "| raw:", clears, "| conc-ctrl:", clears_cc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
