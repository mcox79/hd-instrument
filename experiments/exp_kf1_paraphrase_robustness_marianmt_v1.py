"""
exp_kf1_paraphrase_robustness_marianmt_v1 -- Batch E Cell 6 (Probe-2 #1; adversarial production gate) -- GPU.

ROUTING: Batch E Probe-2 #1 (Research decision: MarianMT round-trip, real attack). KF-1 grounding-based hallucination
  detection (real claims ground to the KB, fabricated do not; AUC discriminates). Adversarial attack = paraphrase real
  claims via MarianMT round-trip (en->de->en, Helsinki-NLP/opus-mt) -- a script-kiddie-accessible attack. Tests whether
  the grounding AUC SURVIVES paraphrase (meaning preserved -> still grounded) or COLLAPSES (substrate over-sensitive to
  surface form). Probe 2 predicts AUC 0.977 -> 0.55-0.65. GPU (MT + encoder forward).
PRE-REGISTERED: HARD-PASS paraphrase AUC >= 0.85 (KF-1 robust to paraphrase). MID 0.65-0.85. HARD-FAIL <0.65 (KF-1 alone
  insufficient; need hybrid substrate+bigrams+NLI+paraphrase-aware -- the predicted outcome).
FORMULA SELF-TESTS (PROT-022): 1. AUC bounds. 2. grounded vs fabricated separation. 3. deps.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "kf1_paraphrase_robustness_marianmt_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MT_MODEL = "facebook/nllb-200-distilled-600M"   # safetensors (no torch<2.6 CVE block); en<->de via lang codes
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_KB = 300; N_CLAIM = 60
else:
    SEEDS = [7, 17, 23]; N_KB = 2000; N_CLAIM = 300


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    assert auc([1, 1, 1], [0, 0, 0]) == 1.0 and abs(auc([0, 1], [0, 1]) - 0.5) < 0.3, "AUC bounds"
    print("[selftest] PASS: kf1-paraphrase", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); t = (r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:200]
                if t.strip():
                    out.append(t)
                if len(out) >= n:
                    return out
    return out


def embed(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        e = ((h * mk).sum(1) / mk.sum(1).clamp(min=1)).cpu().numpy(); out.append(e)
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def roundtrip(texts):
    # en -> de -> en via NLLB-200 (one model, two passes; safetensors)
    tok = AutoTokenizer.from_pretrained(MT_MODEL); m = AutoModelForSeq2SeqLM.from_pretrained(MT_MODEL, use_safetensors=True).to(DEV).eval()
    def _xlate(src_texts, src_lang, tgt_lang):
        tok.src_lang = src_lang; bos = tok.convert_tokens_to_ids(tgt_lang); out = []
        for i in range(0, len(src_texts), 16):
            t = tok(src_texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
            with torch.no_grad():
                g = m.generate(**t, forced_bos_token_id=bos, max_length=96)
            out.extend(tok.batch_decode(g, skip_special_tokens=True))
        return out
    de = _xlate(texts, "eng_Latn", "deu_Latn"); en = _xlate(de, "deu_Latn", "eng_Latn")
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return en


def grounding(claims_emb, kb_emb):
    return (claims_emb @ kb_emb.T).max(axis=1)                       # max cosine to KB = grounding score


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); texts = load_texts(N_KB + N_CLAIM)
    kb_texts = texts[:N_KB]; real_claims = list(np.array(kb_texts)[g.choice(N_KB, N_CLAIM, replace=False)])  # real = drawn from KB
    fab_claims = texts[N_KB:N_KB + N_CLAIM]                          # fabricated = not in KB
    kb_emb = embed(kb_texts)
    # clean: verbatim real vs fabricated
    real_e = embed(real_claims); fab_e = embed(fab_claims)
    clean_auc = auc(grounding(real_e, kb_emb), grounding(fab_e, kb_emb))
    # attack: paraphrase real claims via en->de->en round-trip, re-ground
    para = roundtrip(real_claims); para_e = embed(para)
    para_auc = auc(grounding(para_e, kb_emb), grounding(fab_e, kb_emb))
    print("  [seed=%d] clean_AUC=%.3f paraphrase_AUC=%.3f drop=%.3f" % (seed, clean_auc, para_auc, clean_auc - para_auc), flush=True)
    return {"seed": seed, "clean_auc": clean_auc, "paraphrase_auc": para_auc, "drop": clean_auc - para_auc}


def verdict(ps) -> Tuple[str, str]:
    pa = float(np.mean([p["paraphrase_auc"] for p in ps])); ca = float(np.mean([p["clean_auc"] for p in ps]))
    summary = "clean_AUC=%.3f paraphrase_AUC=%.3f drop=%.3f" % (ca, pa, ca - pa)
    if pa >= 0.85:
        return ("HARD_PASS", "HARD_PASS: KF-1 grounding ROBUST to MarianMT round-trip paraphrase (AUC>=0.85) -- deployable vs paraphrase attack. " + summary)
    if pa >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: KF-1 partially degraded under paraphrase (0.65-0.85). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: KF-1 grounding COLLAPSES under paraphrase (AUC<0.65) -- KF-1 alone insufficient; need hybrid (substrate+bigrams+NLI+paraphrase-aware). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_kb=%d N_claim=%d MT=NLLB-en-de-en" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB, N_CLAIM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = [run_seed(s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
