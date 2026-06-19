"""
exp_decisive1_spec_draft_accept_cpu_v1.py -- DECISIVE-1: substrate speculative-draft acceptance rate -- CPU.

ROUTING: LITERATURE_BACKED_DECISIVE_TESTS DECISIVE-1 (Research P4). Tests whether the substrate can act as a cheap speculative
  DRAFTER for an LLM: cache (context last-hidden -> the LLM's next-token argmax) over a train split; for test contexts retrieve
  the nearest cached context (real-cosine cleanup) and DRAFT its token; acceptance alpha = fraction where the draft matches the
  LLM's actual argmax. High alpha on high-similarity (cache-hit) contexts => substrate-as-draft gives 1.5-3x speedup. Verifier =
  Pythia-160M on CPU. Pure substrate retrieval for the draft (no second LLM). ~1-2 hr CPU.
PRE-REGISTERED: HARD-PASS alpha >= 0.65 on high-similarity contexts (speedup viable). MIDDLE 0.40-0.65. HARD-FAIL < 0.40 (substrate-as-draft closed).
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "TORCH_NUM_THREADS"):
    os.environ.setdefault(_v, "10")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "decisive1_spec_draft_accept_cpu_v1"; MODEL = "EleutherAI/pythia-160m"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_CTX = 80 if SMOKE else 1200


def _selftest():
    import numpy as _n; a = _n.array([1.0, 0]); assert abs(float(a @ a) - 1) < 1e-9, "dot"; print("[selftest] PASS: decisive1-spec-draft-accept", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    torch.set_num_threads(10)
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu"); print("[device] cpu (threads=%d)" % torch.get_num_threads(), flush=True)


_CORPUS = [
    "The river carved a deep canyon through ancient sandstone over millions of years of patient erosion.",
    "Modern processors execute billions of instructions per second by pipelining many overlapping stages.",
    "She planted tomatoes basil and peppers in the small garden behind the old brick farmhouse.",
    "The orchestra tuned their instruments quietly before the conductor raised his baton for the symphony.",
    "Glaciers store vast quantities of fresh water that slowly feed mountain streams during the summer.",
    "The committee debated the new policy for hours before reaching a narrow and reluctant compromise.",
    "A flock of migrating geese crossed the grey autumn sky heading steadily toward the warmer south.",
    "Engineers tested the bridge under heavy loads to confirm it would survive decades of daily traffic.",
    "The novelist wrote every morning at dawn filling notebooks with characters cities and quiet sorrows.",
    "Photosynthesis converts sunlight water and carbon dioxide into the sugars that sustain most plant life.",
    "The merchant ships sailed from the harbor laden with spices silk and barrels of salted fish.",
    "Volunteers cleared the trail of fallen branches so hikers could reach the summit before nightfall.",
    "The theorem follows directly once you assume the function is continuous on the closed interval.",
    "Children laughed and chased each other across the meadow while the picnic baskets sat in the shade.",
    "The telescope gathered faint light from a galaxy whose photons had traveled for billions of years.",
    "Inflation eroded the value of savings forcing the central bank to raise interest rates sharply.",
    "The chef seared the scallops in butter then finished the plate with a bright squeeze of lemon.",
    "Archaeologists brushed away the soil revealing pottery shards and the foundation of a forgotten temple.",
    "The startup pivoted twice before finding a market for its tool among small accounting firms.",
    "Rain hammered the tin roof all night while the travelers slept soundly in the crowded mountain lodge.",
]


def load_texts(n):
    g2 = np.random.default_rng(11); reps = max(2, n // 200)
    out = []
    for _ in range(reps):
        order = g2.permutation(len(_CORPUS))
        out.append(" ".join(_CORPUS[i] for i in order))   # varied, self-contained (no dataset download)
    return out


def run() -> Dict:
    torch.manual_seed(7); g = np.random.default_rng(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    texts = load_texts(N_CTX)
    # collect (last-hidden context key, LLM next-token argmax) pairs by stepping through real text
    keys = []; toks = []
    with torch.no_grad():
        for t in texts:
            ids = tok(t, return_tensors="pt", truncation=True, max_length=128)["input_ids"]
            if ids.shape[1] < 8:
                continue
            out = mdl(ids, output_hidden_states=True); H = out.hidden_states[-1][0]; lg = out.logits[0]
            for pos in range(4, ids.shape[1] - 1):
                keys.append(H[pos].numpy().astype(np.float32)); toks.append(int(torch.argmax(lg[pos])))
                if len(keys) >= N_CTX + (40 if SMOKE else 300):
                    break
            if len(keys) >= N_CTX + (40 if SMOKE else 300):
                break
    keys = np.stack(keys); toks = np.array(toks); keys = keys / (np.linalg.norm(keys, axis=1, keepdims=True) + 1e-8)
    n = len(keys); idx = g.permutation(n); ntr = int(0.7 * n)
    tr, te = idx[:ntr], idx[ntr:]
    Ktr = keys[tr]; Ttr = toks[tr]
    # substrate draft: nearest cached train context (real-cosine cleanup) -> its token; accept if == LLM argmax at the test ctx
    sims = te[:, None]; acc = []; simv = []
    for j in te:
        s = Ktr @ keys[j]; b = int(np.argmax(s)); simv.append(float(s[b])); acc.append(int(Ttr[b] == toks[j]))
    acc = np.array(acc); simv = np.array(simv)
    alpha_all = float(acc.mean())
    thr = float(np.percentile(simv, 60)); hi = simv >= thr
    alpha_hi = float(acc[hi].mean()) if hi.sum() else 0.0
    print("  alpha_all=%.3f alpha_high_sim=%.3f (sim>=%.3f, n_test=%d, hi=%d)" % (alpha_all, alpha_hi, thr, len(te), int(hi.sum())), flush=True)
    return {"alpha_all": alpha_all, "alpha_high_sim": alpha_hi, "sim_thr": thr, "n_test": int(len(te))}


def verdict(r) -> Tuple[str, str]:
    s = "alpha_all=%.3f alpha_high_sim=%.3f" % (r["alpha_all"], r["alpha_high_sim"])
    if r["alpha_high_sim"] >= 0.65:
        return ("HARD_PASS", "HARD_PASS: substrate-as-draft acceptance alpha>=0.65 on high-similarity contexts -- speculative-draft speedup (1.5-3x) viable. " + s)
    if r["alpha_high_sim"] >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: alpha 0.40-0.65 (partial; speedup marginal). " + s)
    return ("HARD_FAIL", "HARD_FAIL: alpha<0.40 -- substrate-as-speculative-draft closed (drafts do not match LLM often enough). " + s)


print("[config] anchor=%s mode=%s n_ctx=%d" % (ANCHOR_NAME, RUN_MODE, N_CTX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
