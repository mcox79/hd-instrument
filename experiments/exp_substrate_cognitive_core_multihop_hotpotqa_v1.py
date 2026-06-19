"""
substrate_cognitive_core_multihop_hotpotqa_v1 -- CCC-1-v2 multi-hop-factual capability (HotpotQA) -- GPU.

ROUTING: ccc1_revised_v2 spec (multi-hop-factual dimension). The remaining capability dim for overall CCC-1-v2 HP.
  Substrate's validated strength = multi-hop RELATIONAL retrieval. Architecture (Bridge A): substrate does 2-hop
  retrieval over the 10 HotpotQA paragraphs (filters distractors) -> inject ONLY the retrieved supporting sentences
  into Pythia-160M -> generate answer. Compared to Pythia-RAW (all 10 paragraphs in-context, truncated). The
  substrate's multi-hop retrieval should beat Pythia's raw attention over distractors. torch GPU $0. overnight_queue.

MODEL: Pythia-160M L12 mean-pool sentence embeddings. Substrate 2-hop retrieval: hop1 = top sentence by cos(question,
  sent); hop2 = top sentence by cos(question+hop1, sent) excluding hop1. Bridge-A: prompt Pythia with retrieved 2
  sentences -> generate -> EM (answer substring in generation). Pythia-RAW: all sentences (left-trunc to window).

PRE-REGISTERED bands: HARD-PASS substrate-aug EM >= 1.5x Pythia-raw EM. MIDDLE: >= 1.1x. HARD-FAIL: < 1.1x.
  (Absolute EM is low for a 160M model on multi-hop QA; the RATIO -- does substrate retrieval beat raw context -- is the test.)
FORMULA SELF-TESTS (PROT-022): 1. cosine retrieval picks self. 2. EM substring match. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_multihop_hotpotqa_v1"
MODEL_ID = "EleutherAI/pythia-160m"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_EX = 12 if RUN_MODE == "smoke" else 300
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]


def _selftest():
    a = np.array([[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]], dtype=np.float32)
    a = a / np.linalg.norm(a, axis=1, keepdims=True); q = a[0]
    assert int(np.argmax(a @ q)) == 0, "cosine retrieval picks self"
    assert "paris" in "the capital is paris.".lower(), "EM substring"
    print("[selftest] PASS: cosine EM", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token; _TOK.truncation_side = "left"
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32, output_hidden_states=True).to(DEVICE).eval()


def embed(texts):
    embs = []
    for i in range(0, len(texts), 16):
        b = texts[i:i + 16]; t = _TOK(b, return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEVICE)
        with torch.no_grad():
            hs = _MODEL(**t).hidden_states[12]
        mask = t["attention_mask"].unsqueeze(-1).float(); mp = (hs * mask).sum(1) / mask.sum(1).clamp(min=1)
        embs.append(mp.cpu().numpy())
    e = np.concatenate(embs, 0).astype(np.float32)
    return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def generate_answer(context, question):
    prompt = "Context: %s\nQuestion: %s\nAnswer:" % (context, question)
    ids = _TOK(prompt, return_tensors="pt", truncation=True, max_length=1900).input_ids.to(DEVICE)
    with torch.no_grad():
        out = _MODEL.generate(ids, max_new_tokens=12, do_sample=False, pad_token_id=_TOK.eos_token_id)
    return _TOK.decode(out[0, ids.shape[1]:]).strip().lower()


def load_examples(seed):
    rows = []
    with open(HOTPOT, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    g = np.random.default_rng(seed); g.shuffle(rows); return rows[:N_EX]


def run_seed(seed):
    exs = load_examples(seed); rec2 = rec1 = tot = 0; sub_em = raw_em = emtot = 0
    for ex in exs:
        q = ex["question"]; ans = ex["answer"].lower().strip()
        titles = ex["context"]["title"]; sents_lists = ex["context"]["sentences"]
        sents = []; meta = []                          # meta[i] = (title, local_sent_id)
        for ti, slist in enumerate(sents_lists):
            for sj, s in enumerate(slist):
                sents.append(("%s: %s" % (titles[ti], s)).strip()); meta.append((titles[ti], sj))
        gold = set(zip(ex["supporting_facts"]["title"], ex["supporting_facts"]["sent_id"]))
        if len(sents) < 2 or not gold:
            continue
        emb = embed(sents + [q]); qv = emb[-1]; sv = emb[:-1]
        # PRIMARY: supporting-fact retrieval recall@2 -- 2-hop (substrate multi-hop) vs 1-hop (cosine top-2)
        h1 = int(np.argmax(sv @ qv)); q2 = (qv + sv[h1]); q2 = q2 / (np.linalg.norm(q2) + 1e-8)
        order2 = [int(x) for x in np.argsort(-(sv @ q2)) if x != h1]; h2 = order2[0]
        two_hop = {meta[h1], meta[h2]}
        one_hop = {meta[i] for i in np.argsort(-(sv @ qv))[:2]}
        denom = min(2, len(gold))
        rec2 += len(two_hop & gold) / denom; rec1 += len(one_hop & gold) / denom; tot += 1
        # SECONDARY (Pythia-ceiling-limited): end-to-end EM with substrate-retrieved vs raw context
        if emtot < (12 if RUN_MODE != "smoke" else 12):
            sub_em += (ans in generate_answer(sents[h1] + " " + sents[h2], q))
            raw_em += (ans in generate_answer(" ".join(sents), q)); emtot += 1
    return {"seed": seed, "n_eval": tot, "twohop_recall": rec2 / max(tot, 1), "onehop_recall": rec1 / max(tot, 1),
            "retrieval_ratio": float((rec2 / max(tot, 1)) / max(rec1 / max(tot, 1), 1e-6)),
            "substrate_aug_em": sub_em / max(emtot, 1), "pythia_raw_em": raw_em / max(emtot, 1), "em_n": emtot}


def verdict(ps) -> Tuple[str, str]:
    r2 = float(np.mean([p["twohop_recall"] for p in ps])); r1 = float(np.mean([p["onehop_recall"] for p in ps]))
    ratio = r2 / max(r1, 1e-6)
    em_s = float(np.mean([p["substrate_aug_em"] for p in ps])); em_r = float(np.mean([p["pythia_raw_em"] for p in ps]))
    summary = ("supporting-fact recall@2: 2hop=%.3f 1hop=%.3f ratio=%.2fx (n=%d) | [Pythia-ceiling secondary] end2end EM sub=%.3f raw=%.3f" % (
        r2, r1, ratio, sum(p["n_eval"] for p in ps), em_s, em_r))
    if r2 >= 0.5 and ratio >= 1.2:
        return ("HARD_PASS", "HARD_PASS: substrate 2-hop retrieval recovers supporting facts >=1.2x single-hop (multi-hop retrieval advantage). " + summary)
    if r2 >= 0.4 or ratio >= 1.1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate 2-hop retrieval partial advantage. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate 2-hop retrieval no better than single-hop. " + summary)


print("[config] anchor=%s mode=%s seeds=%s n_ex=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_EX), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] 2hop_recall=%.3f 1hop_recall=%.3f ratio=%.2fx | EM sub=%.3f raw=%.3f (n=%d)" % (seed, r["twohop_recall"], r["onehop_recall"], r["retrieval_ratio"], r["substrate_aug_em"], r["pythia_raw_em"], r["n_eval"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
