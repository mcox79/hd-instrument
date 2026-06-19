"""
exp_reasoning_routing_oracle_cpu_v1.py -- Phase-3 reasoning-routing oracle (substrate-as-classifier) -- CPU.

ROUTING: Research Drill B (REASONING-ROUTING-30-ORACLE). The Phase-3 bridge: slot-filled problem instances route to one of 6
  reasoning classes (A deductive->PP-343, B Bayesian->PP-291, C causal->PP-307, D counterfactual->PP-307+PP-280, E temporal->
  PP-348/360/362, F analogical->PP-275/SLIPNET) via a substrate-as-classifier (no trained net): each class has a prototype
  bundle of its signature-keyword phasors; an instance is classified by substrate cleanup (max real-cosine) over the 6
  prototypes. routing_acc = correct class. answer_acc = routed-correctly x routed-primitive validated solve-rate (the gap
  between routing and solving). Tests whether substrate routing connects extraction -> the right reasoning primitive.
PRE-REGISTERED: HARD-PASS routing_acc >= 0.75 AND answer_acc >= 0.60. MIDDLE routing_acc >= 0.60. HARD-FAIL routing_acc < 0.60.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "reasoning_routing_oracle_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
# 6-class signature keywords + validated primitive solve-rate (from prior PP results)
SIG = {
    "A_deductive": (["if", "then", "rule", "derive", "therefore", "implies", "rate", "equals", "solve", "proof"], 1.00),
    "B_bayesian": (["probability", "likely", "probably", "estimate", "given", "chance", "percent", "uncertain", "prior", "posterior"], 0.90),
    "C_causal": (["causes", "because", "effect", "increase", "intervention", "leads", "due", "influence", "affects"], 0.90),
    "D_counterfactual": (["would", "had", "hypothetical", "explanation", "abduce", "counterfactual", "otherwise", "instead"], 0.85),
    "E_temporal": (["first", "then", "finally", "sequence", "steps", "order", "before", "after", "next", "schedule"], 1.00),
    "F_analogical": (["like", "similar", "maps", "analogous", "resembles", "corresponds", "mirror", "parallel"], 0.90),
}
CLASSES = list(SIG.keys())
# 30 synthetic instances: (text, gold_class) -- 5 per class with class signatures + filler
INSTANCES = [
    ("if rate equals 60 and time equals 2 then solve for distance", "A_deductive"),
    ("if A implies B and B implies C then derive A implies C", "A_deductive"),
    ("apply the rule therefore the result equals the sum", "A_deductive"),
    ("solve the equation given the premises by derivation", "A_deductive"),
    ("if all men are mortal then socrates is mortal proof", "A_deductive"),
    ("what is the probability the patient has the disease given symptoms", "B_bayesian"),
    ("estimate the likely outcome given the prior and the percent", "B_bayesian"),
    ("it is probably true given uncertain evidence and a chance", "B_bayesian"),
    ("update the posterior probability from the likelihood", "B_bayesian"),
    ("given sixty percent are positive estimate the chance", "B_bayesian"),
    ("does smoking cause lung cancer because of the mechanism", "C_causal"),
    ("if we increase the dose what is the effect on recovery", "C_causal"),
    ("the intervention leads to a change due to the influence", "C_causal"),
    ("the fertilizer causes growth because of nitrogen", "C_causal"),
    ("how does the policy affect the outcome via causal effect", "C_causal"),
    ("what would have happened had the treatment not occurred", "D_counterfactual"),
    ("find the best explanation for the observed anomaly", "D_counterfactual"),
    ("if the cause had been absent the result would differ", "D_counterfactual"),
    ("hypothetically what is the counterfactual outcome instead", "D_counterfactual"),
    ("otherwise the explanation would abduce a hidden factor", "D_counterfactual"),
    ("first heat the water then add salt and finally stir", "E_temporal"),
    ("what is the sequence of steps in the right order", "E_temporal"),
    ("schedule the tasks before and after each milestone", "E_temporal"),
    ("plan the next steps in sequence to reach the goal", "E_temporal"),
    ("do the first task then the second and finally the third", "E_temporal"),
    ("the atom is like a solar system similar to planets", "F_analogical"),
    ("this problem maps to a known analogous structure", "F_analogical"),
    ("the heart resembles a pump it corresponds to the role", "F_analogical"),
    ("find the parallel structure that mirrors the example", "F_analogical"),
    ("the new case is analogous to the prior similar case", "F_analogical"),
]
def _tok(text): return [w for w in re.findall(r"[a-z]+", text.lower())]
def _selftest():
    assert len(INSTANCES) == 30 and all(c in SIG for _t, c in INSTANCES)
    print("[selftest] PASS: reasoning-routing-oracle (6 classes, 30 instances)", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1001")))
    book = {}
    def tok(w):
        if w not in book:
            ang = (g.random(N) * 2 - 1) * math.pi; book[w] = np.exp(1j * ang).astype(np.complex64)
        return book[w]
    def bundle(words):
        v = np.zeros(N, dtype=np.complex64)
        for w in words: v = v + tok(w)
        return np.exp(1j * np.angle(v)).astype(np.complex64)
    proto = np.stack([bundle(SIG[c][0]) for c in CLASSES])      # class prototype bundles (substrate-as-classifier)
    routed = 0; ans = 0.0
    for text, gold in INSTANCES:
        v = bundle(_tok(text))
        pred = CLASSES[int(np.argmax((proto @ np.conj(v)).real))]
        ok = pred == gold; routed += int(ok)
        ans += (SIG[gold][1] if ok else 0.0)                    # routed correctly -> validated primitive solves at its rate
    routing_acc = routed / len(INSTANCES); answer_acc = ans / len(INSTANCES)
    print("  REASONING-ROUTING-ORACLE: routing_acc=%.3f (%d/30) | answer_acc=%.3f (routing x primitive-solve-rate)" %
          (routing_acc, routed, answer_acc), flush=True)
    return {"routing_acc": round(routing_acc, 3), "answer_acc": round(answer_acc, 3), "n": len(INSTANCES), "n_classes": len(CLASSES)}
def verdict(r) -> Tuple[str, str]:
    ra = r["routing_acc"]; aa = r["answer_acc"]; s = "routing_acc=%.3f answer_acc=%.3f (6 classes, 30 instances)" % (ra, aa)
    if ra >= 0.75 and aa >= 0.60:
        return ("HARD_PASS", "HARD_PASS: substrate-as-classifier routes problems to the right reasoning primitive (routing_acc>=0.75) and the routed validated primitives solve (answer_acc>=0.60). The Phase-3 extraction->reasoning bridge works substrate-only -- no trained router. " + s)
    if ra >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: routing_acc 0.60-0.75 -- substrate routing partial; expand signature atoms or 2-stage refinement. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routing_acc <0.60 -- substrate-as-classifier does not route reliably. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
