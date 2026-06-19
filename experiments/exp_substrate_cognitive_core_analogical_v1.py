"""
substrate_cognitive_core_analogical_v1 -- CCC-1-v2 capability dim: analogical reasoning (A:B::C:?) -- GPU baseline.

ROUTING: ccc1_revised_v2 spec (analogical dimension; VSA binding native). Tests A:B::C:D where B=A bound with a NOVEL
  relation r and D=C bound with the same r. Substrate recovers r = B*A (bipolar self-inverse) and applies D = C*r,
  cleanup -> exact (VSA-native analogy mechanism, works on ANY relation). Pythia-160M must do it via in-context
  few-shot (ICL) on novel/nonsense tokens -- no memorized world-knowledge to fall back on -> weak. torch GPU $0.

MODEL: n_ent entities (bipolar), n_rel NOVEL relations (bipolar). Object O[s][r] = S[s]*Rel[r] (VSA bind). Analogy
  query (s1,r,s2): A=S[s1], B=O[s1][r], C=S[s2] -> D_hat = cleanup_over_all_O(C * (B*A)); correct iff == O[s2][r].
  Pythia: few-shot ICL of the relation pattern with pseudo-token labels, then predict the held-out object label.

PRE-REGISTERED bands: HARD-PASS substrate analogical EM >= 2.0x Pythia ICL EM. MIDDLE: >= 1.2x. HARD-FAIL: < 1.2x.
FORMULA SELF-TESTS (PROT-022): 1. VSA bind self-inverse. 2. analogy recovery exact. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_analogical_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENT = 30; N_REL = 5; N_EVAL = 60; SHOTS = 4
else:
    SEEDS = [7, 17, 23]; N_ENT = 60; N_REL = 12; N_EVAL = 300; SHOTS = 5


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 256; S = ub(3, n, g); R = ub(2, n, g)
    A = S[0]; r = R[0]; B = A * r * math.sqrt(n); C = S[1]; D = C * r * math.sqrt(n)
    r_hat = B * A; D_hat = C * r_hat
    allO = np.stack([S[i] * R[j] * math.sqrt(n) for i in range(3) for j in range(2)])
    pred = int(np.argmax(allO @ D_hat)); target = 1 * 2 + 0   # entity1 rel0
    assert pred == target, "analogy recovery exact"
    assert N_SUB == 4096; print("[selftest] PASS: vsa analogy", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(DEVICE).eval()
ENTTOK = lambda i: "ent%d" % i
RELTOK = lambda j: "rel%d" % j


def pythia_icl(shots_text, query_text, target_label):
    ids = _TOK(shots_text + query_text, return_tensors="pt", truncation=True, max_length=2048).input_ids.to(DEVICE)
    tgt_ids = _TOK(" " + target_label, add_special_tokens=False).input_ids
    with torch.no_grad():
        out = _MODEL.generate(ids, max_new_tokens=len(tgt_ids) + 1, do_sample=False, pad_token_id=_TOK.eos_token_id)
    gen = _TOK.decode(out[0, ids.shape[1]:]).strip()
    return gen.startswith(target_label)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_SUB; sq = math.sqrt(n)
    S = ub(N_ENT, n, g); R = ub(N_REL, n, g)
    O = np.stack([[S[i] * R[j] * sq for j in range(N_REL)] for i in range(N_ENT)])  # (ent, rel, n)
    allO = O.reshape(N_ENT * N_REL, n)
    # OPAQUE labels: shuffled 4-digit ids per (s,r) -- NOT derivable from ent/rel tokens
    _ids = list(range(1000, 1000 + N_ENT * N_REL)); g.shuffle(_ids)
    OBJLAB = {(i, j): str(_ids[i * N_REL + j]) for i in range(N_ENT) for j in range(N_REL)}
    sub_ok = 0; py_ok = 0; tot = 0
    for _ in range(N_EVAL):
        r = int(g.integers(0, N_REL)); s1, s2 = g.choice(N_ENT, size=2, replace=False)
        A = S[s1]; B = O[s1][r]; C = S[s2]; D_idx = s2 * N_REL + r
        # substrate VSA analogy
        r_hat = B * A; D_hat = C * r_hat
        sub_ok += (int(np.argmax(allO @ D_hat)) == D_idx)
        # pythia ICL: few-shot examples of relation r, then query s2
        shots = [s for s in g.choice([e for e in range(N_ENT) if e != s2], size=SHOTS, replace=False)]
        shot_txt = "".join("%s %s is %s\n" % (ENTTOK(s), RELTOK(r), OBJLAB[(s, r)]) for s in shots)
        q_txt = "%s %s is" % (ENTTOK(s2), RELTOK(r))
        py_ok += pythia_icl(shot_txt, q_txt, OBJLAB[(s2, r)]); tot += 1
    return {"seed": seed, "n_eval": tot, "substrate_analogical": sub_ok / tot, "pythia_analogical": py_ok / tot,
            "ratio": float((sub_ok / tot) / max(py_ok / tot, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    s = float(np.mean([p["substrate_analogical"] for p in ps])); py = float(np.mean([p["pythia_analogical"] for p in ps]))
    ratio = s / max(py, 1e-6)
    summary = "substrate_analogical=%.3f pythia_icl=%.3f ratio=%.2fx" % (s, py, ratio)
    if ratio >= 2.0:
        return ("HARD_PASS", "HARD_PASS: substrate VSA-native analogy >=2x Pythia ICL (general analogy mechanism on novel relations). " + summary)
    if ratio >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate analogical 1.2-2x Pythia. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate analogical no better than Pythia ICL. " + summary)


print("[config] anchor=%s mode=%s seeds=%s n_ent=%d n_rel=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENT, N_REL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] substrate=%.3f pythia_icl=%.3f ratio=%.2fx" % (seed, r["substrate_analogical"], r["pythia_analogical"], r["ratio"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
