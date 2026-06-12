"""
exp_two_vector_real_substrate_identity_validation_cpu_v1.py -- validate the two-vector trilogy on the REAL substrate atoms -- CPU/local.

ROUTING: the trilogy (alpha-plateau / scaling / query-SNR) used SYNTHETIC random vectors. This cell validates it on the ACTUAL
  production substrate (PartitionedStore data/substrate_index; 1743 atoms, 242 with composite_hrr). The AlgebraIndex is pure
  numpy (no torch/bge) so this is cheap PartitionedStore work, local-safe. Measures the ATOM-KEYED composite identity channel
  on real data:
    (1) real identity_prec@1 -- cue = each atom's clean name_vec; retrieve nearest composite_hrr; is it the atom? (real
        collision rate among actual atom names/algebra)
    (2) self-alignment cos(name_vec, composite_hrr) + nearest-distractor margin (the real operating margin)
    (3) degraded-cue sweep on REAL vectors -- name_vec + q*noise; find the real break-point cos and compare to the synthetic
        cos~0.45 threshold (does the trilogy's generous margin hold on real data, where atoms can share name/algebra tokens?)
  NO LLM; substrate-physics on the production index, real atoms.

PRE-REGISTERED: HARD-PASS real clean-cue identity_prec@1 >= 0.95 AND real degraded break-point cos <= 0.55 (margin consistent
  with the synthetic ~0.45, allowing some real collisions). MIDDLE: clean >=0.90 OR break cos <=0.65. HARD-FAIL: clean <0.90
  (real atoms collide badly -- name_vec under-identifies). UNKNOWN if store missing.
ASCII-only. CPU/local (numpy-only). --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "two_vector_real_substrate_identity_validation_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
QGRID = [0.6, 2.0] if SMOKE else [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]


def _norm_rows(X):
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def _selftest():
    x = np.random.default_rng(0).standard_normal((4, 32)); xn = _norm_rows(x)
    assert abs(float((xn ** 2).sum(1).mean()) - 1.0) < 1e-6
    print("[selftest] PASS: two_vector_real_substrate_identity_validation_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "store_missing", "note": str(root)}
    ps = PartitionedStore(root); idx = AlgebraIndex()
    # single pass: encode each atom and keep (composite, name_vec) together -- avoids any atom_id/id mismatch
    comp_list = []; name_list = []
    for a in ps.all_atoms():
        av = idx.encode_atom(a)
        if av.composite_hrr is None:
            continue
        nv = idx._name_vec(a)
        if nv is None:
            continue
        comp_list.append(av.composite_hrr); name_list.append(nv)
        if SMOKE and len(comp_list) >= 80:
            break
    comp = _norm_rows(np.stack(comp_list)); name = _norm_rows(np.stack(name_list))
    n = comp.shape[0]; idxarr = np.arange(n)
    # (1) real clean-cue identity precision@1
    S = name @ comp.T
    pred = S.argmax(1); id_prec = float((pred == idxarr).mean())
    # (2) self-alignment + nearest-distractor margin
    self_cos = S[idxarr, idxarr]
    Soff = S.copy(); Soff[idxarr, idxarr] = -1e9
    nn_cos = Soff.max(1)
    margin = float((self_cos - nn_cos).mean())
    print("  REAL atoms with composite_hrr: %d" % n, flush=True)
    print("  (1) clean-cue identity_prec@1 = %.4f" % id_prec, flush=True)
    print("  (2) self-cos(name,composite) mean=%.3f min=%.3f | nearest-distractor mean=%.3f | margin mean=%.3f" %
          (float(self_cos.mean()), float(self_cos.min()), float(nn_cos.mean()), margin), flush=True)
    # (3) degraded-cue sweep on REAL vectors
    rng = np.random.default_rng(1028); rows = []
    for q in QGRID:
        noise = _norm_rows(rng.standard_normal((n, comp.shape[1])))
        cue = _norm_rows(name + q * noise)
        Sd = cue @ comp.T; p = Sd.argmax(1); acc = float((p == idxarr).mean())
        cos_cue = float((cue * name).sum(1).mean())   # realized cue-to-name cos
        rows.append({"q": q, "cos_cue": round(cos_cue, 4), "id_prec": round(acc, 4)})
        print("  q=%4.1f  cos(cue,name)=%.3f  id_prec@1=%.4f" % (q, cos_cue, acc), flush=True)
    ok = [r for r in rows if r["id_prec"] >= 0.90]
    break_cos = min((r["cos_cue"] for r in ok), default=1.0)
    print("  [real margin] identity holds (>=0.90) down to cos(cue,name)>=%.3f -- vs synthetic trilogy ~0.45" % break_cos, flush=True)
    return {"n": n, "clean_id_prec": round(id_prec, 4), "self_cos_mean": round(float(self_cos.mean()), 4),
            "self_cos_min": round(float(self_cos.min()), 4), "margin": round(margin, 4),
            "break_cos": round(break_cos, 4), "rows": rows}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + r.get("note", ""))
    cp = r["clean_id_prec"]; bc = r["break_cos"]
    s = "n=%d real atoms; clean-cue id_prec@1=%.4f; self-cos mean=%.3f min=%.3f; margin=%.3f; real break cos=%.3f (synthetic ~0.45); curve=%s" % (
        r["n"], cp, r["self_cos_mean"], r["self_cos_min"], r["margin"], bc, [(x["q"], x["cos_cue"], x["id_prec"]) for x in r["rows"]])
    if cp >= 0.95 and bc <= 0.55:
        return ("HARD_PASS", "HARD_PASS: the two-vector identity channel VALIDATES on the REAL substrate -- clean-cue identity is near-perfect (>=0.95) and the degraded break-point cos (<=0.55) matches the synthetic trilogy's generous ~0.45 margin. The atom-keyed identity design works on actual atoms; real name/algebra collisions do not break it. " + s)
    if cp >= 0.90 or bc <= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: real-substrate identity mostly validates the trilogy but with a tighter margin than synthetic -- some real atoms share name/algebra tokens. " + s)
    return ("HARD_FAIL", "HARD_FAIL: real clean-cue identity <0.90 -- real atoms collide more than synthetic predicted; name_vec under-identifies on the actual substrate (token overlap). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
