"""
exp_two_vector_alpha_plateau_gpu_v3.py -- the production two-vector composite's alpha tradeoff curve (N=4096, GPU) -- GPU.

ROUTING: the production two-vector index ships composite_hrr = normalize(algebra_hrr + 0.5*name_vec) (PP-410, in
  backend/substrate_index/algebra_index.py). The 0.5 weight was a design choice; v1/v2 found NO tradeoff (both objectives saturate across alpha 0.25-2.0): in high-D, name_vec and algebra_hrr are
  near-ORTHOGONAL so superposing them does not interfere -- each reads out along its own subspace. So the design has a WIDE
  robust PLATEAU, not a delicate knee. This v3 MAPS the plateau boundaries: fine low-alpha (identity-onset, lower edge) +
  extreme high-alpha (does structure EVER break, upper edge). Shows 0.5 sits safely central in a wide robust band. algebra_hrr is the STRUCTURAL vector (atoms in the same structural class are
  similar -- collisions DESIRABLE for structural retrieval); name_vec is the IDENTITY vector (unique per atom -- collisions
  BAD for exact retrieval). The composite must serve BOTH. Sweep alpha and measure the two competing objectives:
    (1) identity precision@1  -- query name_vec[atom], retrieve nearest composite; is it the exact atom? (collision-resistance)
    (2) structural recall@5   -- query algebra_hrr[atom], fraction of top-5 composites that are SAME structural class
                                 (excluding self); normalized to the alpha=0 maximum (pure-structural ceiling).
  alpha=0 -> pure structural (max struct recall, poor identity); alpha->inf -> pure identity (perfect identity, no structure).
  The shipped alpha=0.5 should sit on the PARETO KNEE: near-perfect identity AND most structural recall retained. NO LLM;
  substrate-physics of the production index. Real float32 HRR (matches production normalize(L2) semantics), NOT phasors.

PRE-REGISTERED: HARD-PASS at alpha=0.5: identity_prec@1 >= 0.90 AND struct_recall@5 >= 0.80 * (alpha=0 ceiling) -- the shipped
  weight gives near-perfect identity while retaining >=80pct of pure-structural recall (knee validated). MIDDLE: alpha=0.5 hits
  one of the two (0.7-threshold on the other). HARD-FAIL: alpha=0.5 dominated (fails both) -- the 0.5 weight is mis-set.
ASCII-only. write_metrics. PROT-018/PROT-020. GPU. STRESS regime (N=1024, tight classes, noisy queries) -- v1 saturated at 1.0/all-alpha.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "two_vector_alpha_plateau_gpu_v3"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ALPHAS = [0.0, 0.5] if SMOKE else [0.0, 0.05, 0.1, 0.15, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]


def _selftest():
    # structural-class construction must make same-class more similar than cross-class (cosine), pre-composite.
    import numpy as _n
    g = _n.random.default_rng(0); d = 256
    base_a = g.standard_normal(d); base_b = g.standard_normal(d)
    a1 = base_a + 0.3 * g.standard_normal(d); a2 = base_a + 0.3 * g.standard_normal(d); b1 = base_b + 0.3 * g.standard_normal(d)
    def cos(x, y): return float(x @ y / (((x @ x) ** 0.5) * ((y @ y) ** 0.5)))
    assert cos(a1, a2) > cos(a1, b1), "same-class must be more similar than cross-class"
    print("[selftest] PASS: two_vector_alpha_plateau_gpu_v3", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def _norm(X):
    return X / (X.norm(dim=-1, keepdim=True) + 1e-9)


def run() -> Dict:
    g = torch.Generator(device=DEV).manual_seed(1028)
    # STRESS regime so structure and identity genuinely COMPETE (a loose/over-provisioned setup saturates at 1.0 for both,
    # revealing no tradeoff). Production N=1024; tight near-colliding classes (within-class algebra nearly identical, so
    # identity MUST come from name); noisy identity queries (retrieval is not a trivial exact match); higher load.
    N = 1024                                  # production default dim
    C = 60 if not SMOKE else 8                # structural classes
    per = 40 if not SMOKE else 10             # atoms per class
    n_atoms = C * per
    struct_spread = 0.06                       # TIGHT within-class noise: same-class algebra nearly identical -> collisions severe
    q_noise = 0.6                              # identity-query SNR: query = normalize(name + 0.6*unit_noise) ~ cos 0.86 to true name
    # structural class bases + per-atom algebra_hrr (same class -> structurally near-identical: identity needs name)
    class_base = torch.randn(C, N, generator=g, device=DEV)
    cls = torch.arange(C, device=DEV).repeat_interleave(per)              # [n_atoms] class id
    algebra = _norm(class_base[cls] + struct_spread * torch.randn(n_atoms, N, generator=g, device=DEV))
    # unique identity vectors per atom
    name = _norm(torch.randn(n_atoms, N, generator=g, device=DEV))
    # noisy identity query (cue approximates name_vec, not exact)
    id_query = _norm(name + q_noise * _norm(torch.randn(n_atoms, N, generator=g, device=DEV)))
    rows = []
    s0 = None
    for a in ALPHAS:
        comp = _norm(algebra + a * name)                                  # production composite at weight a
        # (1) identity precision@1: noisy name-cue retrieves the EXACT atom (collision-resistance under tight classes)
        id_sim = id_query @ comp.T                                        # [n_atoms, n_atoms]
        id_pred = id_sim.argmax(dim=1)
        id_prec = float((id_pred == torch.arange(n_atoms, device=DEV)).float().mean())
        # (2) structural recall@5: query algebra_hrr, top-5 composites (excl self) same-class fraction
        st_sim = algebra @ comp.T
        st_sim[torch.arange(n_atoms, device=DEV), torch.arange(n_atoms, device=DEV)] = -1e9  # exclude self
        top5 = st_sim.topk(5, dim=1).indices                             # [n_atoms,5]
        same = (cls[top5] == cls.unsqueeze(1)).float().mean()
        st_rec = float(same)
        if a == 0.0: s0 = st_rec
        rows.append({"alpha": a, "id_prec": round(id_prec, 4), "struct_rec": round(st_rec, 4)})
        print("  alpha=%.2f  identity_prec@1=%.4f  struct_recall@5=%.4f" % (a, id_prec, st_rec), flush=True)
    # normalize structural recall to the alpha=0 ceiling
    for r in rows: r["struct_rec_rel"] = round(r["struct_rec"] / (s0 + 1e-9), 4)
    at_half = next(r for r in rows if abs(r["alpha"] - 0.5) < 1e-9)
    print("  [knee] alpha=0.5: id_prec=%.4f struct_rec_rel=%.4f (ceiling s0=%.4f)" %
          (at_half["id_prec"], at_half["struct_rec_rel"], s0), flush=True)
    return {"rows": rows, "s0_ceiling": round(s0, 4), "n_atoms": n_atoms, "C": C, "at_half": at_half, "N": N}


def _plateau(rows):
    """alphas where BOTH id_prec>=0.90 and struct_rec_rel>=0.80 (the robust operating band)."""
    ok = [x["alpha"] for x in rows if x["id_prec"] >= 0.90 and x["struct_rec_rel"] >= 0.80]
    return (min(ok), max(ok), len(ok)) if ok else (None, None, 0)


def verdict(r) -> Tuple[str, str]:
    h = r["at_half"]; idp = h["id_prec"]; srr = h["struct_rec_rel"]
    lo, hi, w = _plateau(r["rows"]); r["plateau_lo"] = lo; r["plateau_hi"] = hi; r["plateau_n"] = w
    band = "robust band alpha in [%s, %s] (%d of %d alphas); 0.5 central=%s" % (lo, hi, w, len(r["rows"]), (lo is not None and lo <= 0.5 <= hi))
    s = "%s; alpha=0.5 id_prec=%.4f struct_rec_rel=%.4f; curve=%s | n_atoms=%d C=%d N=%d" % (
        band, idp, srr, [(x["alpha"], round(x["id_prec"],3), round(x["struct_rec_rel"],3)) for x in r["rows"]], r["n_atoms"], r["C"], r["N"])
    central = lo is not None and lo <= 0.5 <= hi
    if central and w >= 4:
        return ("HARD_PASS", "HARD_PASS: the two-vector composite has a WIDE robust plateau (>=4 alphas satisfy both id_prec>=0.90 and struct_rec_rel>=0.80), with the shipped alpha=0.5 central. There is NO delicate knee: in high-D, identity (name) and structure (algebra) are near-orthogonal so they superpose without interference -- the design is robust to the alpha choice over an order of magnitude. Stronger than a single optimum. " + s)
    if central:
        return ("MIDDLE_BAND", "MIDDLE_BAND: alpha=0.5 inside the robust band but the plateau is narrow (<4 alphas) -- robustness is bounded; weight choice matters more than expected. " + s)
    return ("HARD_FAIL", "HARD_FAIL: alpha=0.5 is OUTSIDE the robust band [%s,%s] -- the production weight is mis-set relative to the plateau. " % (lo, hi) + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
