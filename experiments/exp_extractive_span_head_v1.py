"""
exp_extractive_span_head_v1 -- PT3 (CRAZY): LLM-free extractive span head on encoder token reps -- CPU.

ROUTING: inference_alternatives_5_pretests PT3. The LLM-bypass path needs EXTRACTION, not raw top-1 sentences (sentences !=
  spans). Train a small 2-layer MLP on bge token embeddings (+ query rep) to predict the answer span (start/end token) over
  the retrieved context, then decode the span text. LLM-FREE answering: bge encode + MLP head (~ms) vs 1.23s LLM. HotpotQA
  extractive subset (answer is a context substring). Train/eval split. CPU (bge token encode + tiny MLP).
PRE-REGISTERED: HARD-PASS extracted-span F1 >= 0.55 on the eval split (LLM-free extraction viable). MIDDLE 0.40-0.55.
  HARD-FAIL < 0.40 (extraction head insufficient; LLM stays in the loop).
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. offset span alignment. 3. argmax span decode.
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
import argparse, time, json, re, string
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "extractive_span_head_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"; MAXTOK = 192
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_TRAIN = 80 if RUN_MODE == "smoke" else 400; N_EVAL = 30 if RUN_MODE == "smoke" else 150; EPOCHS = 8


def norm_ans(s):
    s = s.lower(); s = "".join(c for c in s if c not in string.punctuation); s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())


def f1_score(pred, gold):
    p = norm_ans(pred).split(); g = norm_ans(gold).split()
    if not p or not g:
        return float(p == g)
    nc = sum(min(p.count(w), g.count(w)) for w in set(p) & set(g))
    if nc == 0:
        return 0.0
    pr = nc / len(p); rc = nc / len(g); return 2 * pr * rc / (pr + rc)


def gold_span_tokens(offsets, ans_char_start, ans_char_end):
    # tokens whose char span overlaps [ans_char_start, ans_char_end)
    st = en = None
    for ti, (a, b) in enumerate(offsets):
        if b <= a:   # special token
            continue
        if a < ans_char_end and b > ans_char_start:
            if st is None:
                st = ti
            en = ti
    return st, en


def _selftest():
    assert abs(f1_score("Mount Everest", "mount everest") - 1.0) < 1e-6, "F1 identical=1"
    offs = [(0, 0), (0, 4), (5, 9), (10, 14)]; st, en = gold_span_tokens(offs, 5, 9); assert st == 2 and en == 2, "offset span alignment"
    logits_s = np.array([0.1, 0.9, 0.2]); logits_e = np.array([0.1, 0.3, 0.8]); s = int(np.argmax(logits_s)); e = s + int(np.argmax(logits_e[s:])); assert s == 1 and e == 2, "argmax span decode"
    print("[selftest] PASS: extractive-span-head", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        flat = [s for ti in range(len(titles)) for s in (sl[ti] if ti < len(sl) else [])]
        if len(flat) < 8 or not ans or ans.lower() in ("yes", "no"):
            continue
        context = " ".join(flat)
        if norm_ans(ans) and ans.lower() in context.lower():    # extractive only
            out.append({"q": r.get("question", ""), "ans": ans, "context": context})
        if len(out) >= n:
            break
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    import torch.nn as nn
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def featurize(data, tok, m):
    feats = []; labels = []; meta = []
    qreps = []
    for d in data:
        qt = tok([Q_INSTR + d["q"]], return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEV)
        with torch.no_grad():
            qrep = m(**qt).last_hidden_state[:, 0, :].float().cpu().numpy()[0]
        qreps.append(qrep)
    for d, qrep in zip(data, qreps):
        enc = tok(d["context"], return_tensors="pt", truncation=True, max_length=MAXTOK, return_offsets_mapping=True)
        offs = enc.pop("offset_mapping")[0].tolist(); enc = {k: v.to(DEV) for k, v in enc.items()}
        with torch.no_grad():
            tokemb = m(**enc).last_hidden_state[0].float().cpu().numpy()      # [T, d]
        T = tokemb.shape[0]
        lo = d["context"].lower(); cs = lo.find(d["ans"].lower()); ce = cs + len(d["ans"])
        gs, ge = gold_span_tokens(offs, cs, ce) if cs >= 0 else (None, None)
        q = np.tile(qrep, (T, 1)); feat = np.concatenate([tokemb, q, tokemb * q], axis=1).astype(np.float32)  # [T, 3d]
        feats.append(feat); labels.append((gs, ge)); meta.append((d, offs))
    return feats, labels, meta


class Head(nn.Module):
    def __init__(self, din):
        super().__init__(); self.net = nn.Sequential(nn.Linear(din, 256), nn.ReLU(), nn.Linear(256, 2))

    def forward(self, x):
        return self.net(x)


def run() -> Dict:
    data = load_hotpot(N_TRAIN + N_EVAL)
    if len(data) < 20:
        print("[FATAL] too few extractive examples", flush=True); return {"n": 0, "f1": 0.0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI).to(DEV).eval()
    tr = data[:N_TRAIN]; ev = data[N_TRAIN:N_TRAIN + N_EVAL]
    trf, trl, _ = featurize(tr, tok, m); evf, evl, evm = featurize(ev, tok, m)
    din = trf[0].shape[1]; head = Head(din).to(DEV); opt = torch.optim.Adam(head.parameters(), lr=1e-3); lossf = nn.CrossEntropyLoss()
    valid = [(f, l) for f, l in zip(trf, trl) if l[0] is not None and l[1] is not None]
    for ep in range(EPOCHS):
        tot = 0.0
        for f, (gs, ge) in valid:
            x = torch.tensor(f, device=DEV); out = head(x)            # [T, 2]
            ls = lossf(out[:, 0].unsqueeze(0), torch.tensor([gs], device=DEV)); le = lossf(out[:, 1].unsqueeze(0), torch.tensor([ge], device=DEV))
            loss = ls + le; opt.zero_grad(); loss.backward(); opt.step(); tot += float(loss)
        if ep == 0 or ep == EPOCHS - 1:
            print("  epoch %d train_loss=%.3f (%d valid spans)" % (ep, tot / max(len(valid), 1), len(valid)), flush=True)
    head.eval(); f1s = []
    for f, (d, offs) in zip(evf, evm):
        with torch.no_grad():
            out = head(torch.tensor(f, device=DEV)).cpu().numpy()
        s = int(np.argmax(out[:, 0])); e = s + int(np.argmax(out[s:, 1]))
        cs = offs[s][0]; ce = offs[min(e, len(offs) - 1)][1]; span = d["context"][cs:ce]
        f1s.append(f1_score(span, d["ans"]))
    del m; f1 = float(np.mean(f1s)) if f1s else 0.0
    print("  extractive span-head eval F1=%.3f (n_eval=%d, n_train_valid=%d)" % (f1, len(f1s), len(valid)), flush=True)
    return {"n": len(f1s), "f1": f1, "n_train": len(valid)}


def verdict(r) -> Tuple[str, str]:
    f1 = r["f1"]; summary = "extractive span-head F1=%.3f (n_eval=%d, n_train=%d)" % (f1, r["n"], r.get("n_train", 0))
    if f1 >= 0.55:
        return ("HARD_PASS", "HARD_PASS: LLM-free extractive span head reaches F1>=0.55 -- bge+MLP extraction (~ms) is a viable LLM-bypass for extractive queries. " + summary)
    if f1 >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: span-head F1 0.40-0.55 -- partial; useful for a high-confidence sub-segment with LLM fallback. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: span-head F1 <0.40 -- a tiny MLP on frozen bge tokens is insufficient for extraction; LLM stays in the loop. " + summary)


print("[config] anchor=%s mode=%s n_train=%d n_eval=%d epochs=%d" % (ANCHOR_NAME, RUN_MODE, N_TRAIN, N_EVAL, EPOCHS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
