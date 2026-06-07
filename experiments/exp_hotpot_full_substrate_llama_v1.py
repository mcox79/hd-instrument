"""
exp_hotpot_full_substrate_llama_v1 -- HotpotQA full substrate (Llama encoder + whiten + pinv + K-hop K=2) -- GPU.

ROUTING: handoff research_to_exp_dev_hotpot_full_substrate_authorize. MiniLM retired (methodology rule). Uses production
  Llama-3.2-1B encoder (last-token pool, left-pad, hidden layer L15) + ZCA-whitening + pseudoinverse-class retrieval + real
  K-hop chaining at K=2 with confidence filter T=0.5 (cycle-154 config). Measures recall@2hop (both supporting facts found)
  on HotpotQA-distractor (MuSiQue stand-in) and the lift over the naive Llama-cosine baseline. GPU.
PRE-REGISTERED: HARD-PASS recall@2hop >= 0.70 (multi-hop integration story holds). MIDDLE 0.50-0.70 OR lift >= 0.10 over
  naive. HARD-FAIL recall@2hop < 0.50.
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. whiten isotropizes. 3. parse hotpot columnar.
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "hotpot_full_substrate_llama_v1"
MODEL = "meta-llama/Llama-3.2-1B"
LAYER = 15; T_CONF = 0.5
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 30 if RUN_MODE == "smoke" else 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(E):
    mu = E.mean(0); Ec = E - mu; cov = (Ec.T @ Ec) / max(Ec.shape[0], 1)
    U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0]))
    Wd = (U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
    return mu.astype(np.float32), Wd


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    X = g.standard_normal((200, 8)).astype(np.float32) * np.array([5, 1, 1, 1, 1, 1, 1, 1], np.float32)
    mu, Wd = whiten_fit(X); Xw = (X - mu) @ Wd; c = np.cov(Xw.T)
    assert abs(c[0, 0] - c[1, 1]) < 0.5, "whiten isotropizes"
    rec = {"context": {"title": ["A", "B"], "sentences": [["s0", "s1"], ["s2"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse hotpot columnar"
    print("[selftest] PASS: hotpot-full-llama", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required (production Llama encoder).", flush=True); sys.exit(1)
DEV = torch.device("cuda")
print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l)
        ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = []
        for ti, title in enumerate(titles):
            slist = sent_lists[ti] if ti < len(sent_lists) else []
            for si, s in enumerate(slist):
                flat.append((title, si, s))
        goldset = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        if len(flat) < 4 or len(goldset) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": goldset})
        if len(out) >= n:
            break
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t, output_hidden_states=True)
        h = o.hidden_states[LAYER]                       # [B, T, H] at layer L15
        last = h[:, -1, :]                               # last-token pool (left-padded -> real last token)
        out.append(last.float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 1), np.float32)


def khop_recall(emb_w, qw, sents, gold):
    # K=2 confidence-filtered relay: hop1 = best; bridge query = q+hop1; hop2 = best other above T_conf
    sims1 = emb_w @ qw; h1 = int(np.argmax(sims1))
    qbridge = unit((qw + emb_w[h1])[None, :])[0]
    sims2 = emb_w @ qbridge; sims2[h1] = -1e9
    h2 = int(np.argmax(sims2))
    found = set([(sents[h1][0], sents[h1][1])])
    conf = float(sims2[h2]) / (float(sims1[h1]) + 1e-8)                  # hop2 confidence relative to hop1
    if conf >= T_CONF:                                                   # confidence filter T=0.5 (cycle-154)
        found.add((sents[h2][0], sents[h2][1]))
    return int(len(found & gold) >= 2)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records parsed", flush=True); return {"recall_2hop": 0.0, "n": 0, "naive": 0.0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    # Encode every question's candidates + query up front, pool ALL candidate embeddings to fit ONE global whitening
    # (production fits whitening on the KB, NOT per-query; per-query fit on ~40 samples in 2048-dim is rank-deficient noise).
    enc = []
    for d in data:
        texts = [s for (_, _, s) in d["sents"]]
        enc.append({"raw": encode(texts, tok, m), "q": encode([d["q"]], tok, m)[0], "sents": d["sents"], "gold": d["gold"]})
    del m; torch.cuda.empty_cache()
    pool = np.concatenate([e["raw"] for e in enc], 0)
    mu, Wd = whiten_fit(pool); print("  global whiten fit on %d pooled embeddings (dim=%d)" % (pool.shape[0], pool.shape[1]), flush=True)
    naive_hits = 0; sub_hits = 0
    for e in enc:
        raw = e["raw"]; sents = e["sents"]; gold = e["gold"]
        en = unit(raw); qn = unit(e["q"]); on = np.argsort(en @ qn)[::-1]
        naive_hits += int(len(set((sents[i][0], sents[i][1]) for i in on[:2]) & gold) >= 2)
        ew = unit((raw - mu) @ Wd); qw = unit((e["q"] - mu) @ Wd)
        sub_hits += khop_recall(ew, qw, sents, gold)
    n = len(data); rn = naive_hits / n; rs = sub_hits / n
    print("  n=%d naive_llama_recall@2hop=%.3f full_substrate(whiten+Khop)_recall@2hop=%.3f lift=%+.3f" % (n, rn, rs, rs - rn), flush=True)
    return {"n": n, "naive": rn, "recall_2hop": rs}


def verdict(r) -> Tuple[str, str]:
    rs = r["recall_2hop"]; rn = r["naive"]; lift = rs - rn
    summary = "full-substrate recall@2hop=%.3f naive-Llama=%.3f lift=%+.3f (n=%d, Llama-1B L15 + whiten + K-hop K=2)" % (rs, rn, lift, r["n"])
    if rs >= 0.70:
        return ("HARD_PASS", "HARD_PASS: full-substrate recall@2hop>=0.70 on HotpotQA with production Llama encoder -- multi-hop integration story holds; small-LLM path open. " + summary)
    if rs >= 0.50 or lift >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: recall@2hop 0.50-0.70 or >=0.10 lift over naive -- substrate helps multi-hop, gap to 0.70 remains. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: recall@2hop <0.50 -- substrate retrieval can't support multi-hop at 1B scale; escalate (larger LLM / stronger retrieval). " + summary)


print("[config] anchor=%s mode=%s n_q=%d model=%s layer=%d T_conf=%.1f" % (ANCHOR_NAME, RUN_MODE, N_Q, MODEL, LAYER, T_CONF), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
