"""SKUNKWORKS AUDITOR comprehensive over-claim scan (read-only).
Cross-references every scorecard-CLAIMED capability against the actual atomized EXPERIMENT_RECORD
verdicts. Flags: REAL-WIN (a cert-grade PASS exists) / THIN (PASS only at smoke|legacy) /
FALSE-VICTORY (no PASS at all -- best matching experiment is HARD_FAIL or MIDDLE_BAND or unanchored).
USER directive 2026-06-17: 'dig through all research+results; would be shocked if we declared victory
against a result that did not happen.' This is the systematic answer."""
import json
from collections import Counter
from pathlib import Path
REPO = Path(r"D:\AI\hd-instrument")

def load_exp():
    out = []
    for corpus in ("math", "concept"):
        p = REPO / "data/substrate_index" / corpus / "atoms.jsonl"
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            a = json.loads(line)
            if a.get("kind") != "experiment_record":
                continue
            m = a.get("metadata", {})
            text = " ".join([a.get("id", ""), m.get("hypothesis") or "", m.get("metrics_headline") or ""]).lower()
            out.append({"id": a["id"], "verdict": m.get("verdict"), "tier": m.get("relevance_tier"),
                        "prov": m.get("provenance_quality"), "headline": (m.get("metrics_headline") or "")[:70], "text": text})
    return out

CLAIMS = [
    ("BP1 Drosophila MB sparse f=0.05 VALIDATED", ["drosophila", "mb_sparse"]),
    ("BP2 cf-RPE counterfactual rank-1 VALIDATED", ["cf_rpe", "counterfactual", "cfrpe"]),
    ("BP3 position-binding+sym-Hebbian VALIDATED +1.291nats", ["position_binding", "hebbian"]),
    ("BP4 STDP-asymmetric VALIDATED +1.249nats", ["stdp"]),
    ("BP5 DG sparse-expansion 48x VALIDATED", ["dentate", "dg_sparse", "sparse_expansion"]),
    ("BP6 D-ECR eviction 2x FLAGSHIP", ["d_ecr", "_b6_", "eviction"]),
    ("BP7 cortical column B4 VALIDATED", ["cortical", "_b4_", "column"]),
    ("BP8a active gating 13.8x VALIDATED", ["active_gat", "_b3a_", "topk_gat", "top_k_gat"]),
    ("BP8b surprise gating 116% VALIDATED", ["surprise", "_b3b_"]),
    ("BP9 logit sparse residual B8 VALIDATED", ["_b8_", "logit_sparse", "sparse_residual", "sparse_readout"]),
    ("BP10 hierarchical aggregator 98.6% VALIDATED", ["hierarchical"]),
    ("BP11 SQ2 K=12 multihop 100% FLAGSHIP", ["sq2", "multi_hop", "multihop", "k12", "k_12", "iterated_retrieval"]),
    ("CAP Composition L=10000 EXACT VALIDATED", ["burial_depth", "comp11", "comp_a", "composition"]),
    ("CAP Deletion cert cos=1 VALIDATED", ["deletion_cert"]),
    ("CAP Drift detection kappa_3 VALIDATED", ["kappa3", "kappa_3", "drift_detect"]),
    ("CAP Tier-6 charLM hybrid FLAGSHIP@smoke", ["tier6", "tier_6", "char_lm", "charlm", "4_layer", "shakespeare"]),
    ("CAP capacity MULT 125k B2xB4 FLAGSHIP", ["b2_x_b4", "125", "multiplicative", "independence_recall"]),
    ("CAP cortical/ensemble param-efficient", ["ensemble", "redundant_substrate"]),
]
RANK = {"PASS": 4, "LOAD_BEARING": 4, "HONEST_BOUNDED": 2, "MIDDLE_BAND": 2, None: 1, "None": 1, "KILLED": 0, "HARD_FAIL": 0}
atoms = load_exp()
print(f"=== SKUNKWORKS OVER-CLAIM SCAN | {len(atoms)} EXPERIMENT_RECORD atoms ===\n")
fv, thin, real, noanchor = [], [], [], []
for name, kws in CLAIMS:
    ms = [a for a in atoms if any(k in a["text"] for k in kws)]
    if not ms:
        print(f"[NO-ANCHOR ] {name}\n             0 matching experiments in-store"); noanchor.append(name); continue
    vc = dict(Counter(a["verdict"] for a in ms))
    cert_pass = [a for a in ms if a["verdict"] in ("PASS", "LOAD_BEARING") and a["prov"] == "CERT_CHAIN_GRADE"]
    any_pass = [a for a in ms if a["verdict"] in ("PASS", "LOAD_BEARING")]
    best = max(ms, key=lambda a: (RANK.get(a["verdict"], 1), 1 if a["prov"] == "CERT_CHAIN_GRADE" else 0))
    if cert_pass:
        flag, bucket = "REAL-WIN  ", real
    elif any_pass:
        flag, bucket = "THIN      ", thin
    else:
        flag, bucket = "FALSE-VICT", fv
    bucket.append(name)
    print(f"[{flag}] {name}  (n={len(ms)}; verdicts={vc})")
    print(f"             best: [{best['verdict']}/{best['prov']}] {best['id'].split('/')[-1][:44]} :: {best['headline'][:52]}")
print("\n=== SUMMARY ===")
print(f"REAL-WIN (cert-grade PASS exists):        {len(real):>2}  {real}")
print(f"THIN (PASS only smoke/legacy, not cert):  {len(thin):>2}  {thin}")
print(f"FALSE-VICTORY (NO PASS; best HF/MIDDLE):   {len(fv):>2}  {fv}")
print(f"NO-ANCHOR (0 matching experiments):       {len(noanchor):>2}  {noanchor}")
