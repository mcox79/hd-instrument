"""
exp_legal_citation_snowball_gpu_v1 -- legal-citation snowball closure recovery at scale, SHARDED + GPU-batched -- GPU.

ROUTING: rebuild of legal_citation_1000seed_cpu_v1 (which used a MONOLITHIC bundle for ~12k edges -> past capacity floor ->
  noise-driven frontier explosion -> ~17hr/1000seeds and would time out writing nothing). Fix: (1) PER-SOURCE SHARDING -- each
  case's out-citations live in their own small clean sub-bundle SH[u]=sum_{o in adj[u]} cases[o], so the unbind is crisp (far
  under capacity) and the snowball does not explode; (2) GPU + BATCHED frontier -- one complex matmul per hop for the whole
  frontier (SH[frontier] @ cases.conj().T) instead of one matmul per node; (3) per-seed JSONL streaming so partial progress is
  salvageable/resumable; (4) measure PRECISION as well as recall (monolithic inflated recall by catching everything). This is
  the sharded-KG invariant applied to a legal-citation graph at 10x demo scale.
PRE-REGISTERED: HARD-PASS 3-hop closure recall >= 0.95 AND precision >= 0.90 over 1000 seeds at VC=4000. MIDDLE recall >= 0.85.
  HARD-FAIL recall < 0.85.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. sharded cleanup. 3. set recall.
ASCII-only. write_metrics + per-seed streaming. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "legal_citation_snowball_gpu_v1"; N = 8192
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
VC = 1200 if SMOKE else 4000; AVG = 3; NSEED = 100 if SMOKE else 1000; THRESH = 0.30; HOPS = 3


def _selftest():
    rng = np.random.default_rng(0)
    a = np.exp(1j * rng.random(64) * 2 * math.pi).astype(np.complex64); b = np.exp(1j * rng.random(64) * 2 * math.pi).astype(np.complex64)
    assert np.allclose(a * b * np.conj(a), b, atol=1e-3), "bind/unbind"
    shard = a + b; assert (np.abs((np.stack([a, b]) @ np.conj(shard)) / 64).real.min()) > 0.4, "sharded cleanup"
    tc = {1, 2, 3}; sn = {1, 2}; assert len(tc & sn) / len(tc) == 2 / 3, "set recall"
    print("[selftest] PASS: legal-citation-snowball-gpu", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def cphasor_t(m, d, g):
    ang = torch.from_numpy((g.random((m, d)) * 2 - 1).astype(np.float32)) * math.pi
    return torch.exp(1j * ang).to(torch.complex64)


def run() -> Dict:
    g = np.random.default_rng(82)
    cases = cphasor_t(VC, N, g).to(DEV)                                  # (VC, N) phasor codebook
    adj: Dict[int, List[int]] = {i: [] for i in range(VC)}
    SH = torch.zeros((VC, N), dtype=torch.complex64, device=DEV)         # per-source shard: SH[u] = sum of out-neighbor case vecs
    for i in range(VC):
        outs = g.choice(VC, size=int(g.integers(1, AVG + 2)), replace=False)
        for o in outs:
            o = int(o)
            if o != i and o not in adj[i]:
                adj[i].append(o); SH[i] = SH[i] + cases[o]
    casesH = cases.conj().T.contiguous()                                # (N, VC) for batched cleanup

    def tclose(seed):                                                    # ground-truth 3-hop transitive closure (set ops)
        seen = set(); fr = {seed}
        for _ in range(HOPS):
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - seen
            seen |= nf; fr = nf
        return seen

    def snow(seed):                                                      # substrate 3-hop snowball, GPU-batched frontier
        reached = set(); fr = [seed]
        for _ in range(HOPS):
            if not fr:
                break
            idx = torch.tensor(fr, device=DEV, dtype=torch.long)
            sc = (SH[idx] @ casesH).real / N                            # (|fr|, VC) cleanup scores
            cand = torch.nonzero(sc.amax(0) > THRESH).flatten().tolist()  # union of above-threshold cols
            nf = [int(v) for v in cand if v not in reached and v not in fr]
            reached |= set(nf); fr = nf
        return reached

    out_dir = get_output_dir(ANCHOR_NAME); Path(out_dir).mkdir(parents=True, exist_ok=True); prog = open(Path(out_dir) / "progress.jsonl", "w", encoding="utf-8")
    seeds = g.choice(VC, NSEED, replace=False); recs = []; precs = []; t_last = time.time()
    for si, seed in enumerate(seeds):
        seed = int(seed); tc = tclose(seed)
        if not tc:
            continue
        sn = snow(seed); inter = len(tc & sn)
        rec = inter / len(tc); prec = inter / max(1, len(sn))
        recs.append(rec); precs.append(prec)
        prog.write(json.dumps({"i": si, "seed": seed, "recall": rec, "precision": prec, "tc": len(tc), "snow": len(sn)}) + "\n")
        if time.time() - t_last > 30:                                    # streamed progress + flush every 30s
            prog.flush(); print("  ...%d/%d seeds | running recall=%.3f prec=%.3f" % (si + 1, NSEED, float(np.mean(recs)), float(np.mean(precs))), flush=True); t_last = time.time()
    prog.flush(); prog.close()
    r = {"recall": float(np.mean(recs)), "precision": float(np.mean(precs)), "cases": VC, "seeds": len(recs)}
    print("  3-hop closure: recall=%.3f precision=%.3f (%d seeds, %d cases, SHARDED)" % (r["recall"], r["precision"], r["seeds"], VC), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f precision=%.3f (%d seeds, %d cases)" % (r["recall"], r["precision"], r["seeds"], r["cases"])
    if r["recall"] >= 0.95 and r["precision"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: sharded legal-citation snowball holds >=0.95 recall AND >=0.90 precision at 10x demo scale -- per-source sharding fixes the monolithic frontier-explosion; legal-pitch dataset validated. " + s)
    if r["recall"] >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: closure recall 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: closure recall <0.85. " + s)


print("[config] anchor=%s mode=%s VC=%d seeds=%d thresh=%.2f" % (ANCHOR_NAME, RUN_MODE, VC, NSEED, THRESH), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
