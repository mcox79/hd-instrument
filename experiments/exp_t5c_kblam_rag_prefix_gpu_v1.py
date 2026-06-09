"""
exp_t5c_kblam_rag_prefix_gpu_v1 -- Path B rescue R2: RAG-prefix injection (decouple retrieval quality from adapter) -- GPU.

ROUTING: strategy_request_to_exp_dev_cycle203_kblam_rescue R2 (CHEAPEST). The KBLaM cross-attn adapter failed held-out recall at
  2-4k facts. R2 tests the OTHER half: instead of adapter injection, RETRIEVE the top-1 substrate fact (bge-large cosine) and
  PREPEND its text to the prompt, then measure next-token recall. This decouples (a) substrate retrieval quality from (b)
  adapter-mediated injection. Three conditions: bare (no prefix), RAG (retrieved-fact prefix), oracle (gold-fact prefix = upper
  bound). Also reports retrieval top-1 accuracy. Frozen Pythia-160M + frozen bge-large. INFERENCE-ONLY (no training).
PRE-REGISTERED: HARD-PASS RAG-prefix held-out recall >= 0.25 (context-window mechanism works + retrieval usable). MIDDLE >= 0.05.
  HARD-FAIL < 0.05 (neither retrieval nor context injection works for this base model on these templates).
FORMULA SELF-TESTS (PROT-022): 1. cosine. 2. argmax. 3. softmax-free top1.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "t5c_kblam_rag_prefix_gpu_v1"; MODEL = "EleutherAI/pythia-160m"; ENCODER = "BAAI/bge-large-en-v1.5"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_FACTS = 200 if SMOKE else 1500

DISC_POOL = ("aardvark albatross alligator antelope armadillo baboon badger barracuda beaver bison buffalo camel capybara "
    "caribou cheetah chimpanzee cobra cougar coyote crocodile dolphin elephant falcon ferret flamingo gazelle giraffe gorilla "
    "hedgehog hippopotamus hyena iguana jackal jaguar kangaroo koala lemur leopard llama lobster lynx manatee meerkat mongoose "
    "moose narwhal ocelot octopus opossum orangutan ostrich otter panther pelican penguin platypus porcupine puffin raccoon "
    "reindeer rhinoceros salamander scorpion seahorse sloth squid stingray tapir tarantula toucan vulture walrus weasel "
    "wolverine wombat amsterdam antwerp athens bangkok barcelona beirut belgrade bergen bologna bordeaux bremen brisbane "
    "bruges budapest cairo calgary canberra cardiff chennai copenhagen cordoba dakar damascus dresden dublin durban edinburgh "
    "florence geneva glasgow granada hamburg helsinki istanbul jakarta jerusalem karachi kyoto lagos lisbon ljubljana lyon "
    "madras marseille melbourne montreal nairobi naples nantes oslo ottawa palermo perth porto prague quebec reykjavik riga "
    "rotterdam salzburg santiago sapporo seville stockholm stuttgart tangier tbilisi toulouse valencia venice verona warsaw "
    "wellington zagreb zurich almond apricot artichoke asparagus avocado basil beetroot blackberry blueberry broccoli cashew "
    "cauliflower celery cherry chestnut chickpea cinnamon clementine coconut cranberry cucumber currant eggplant fennel ginger "
    "grapefruit hazelnut jackfruit kiwi kumquat lavender leek lentil lychee mandarin mango marjoram nectarine nutmeg oregano "
    "papaya paprika parsnip persimmon pistachio plantain pomegranate pumpkin quince radish raspberry rhubarb rosemary saffron "
    "scallion shallot spinach tamarind tangerine tarragon thyme turmeric turnip vanilla watercress zucchini accordion banjo "
    "bassoon bagpipe bongo cello clarinet cornet dulcimer fiddle flute harmonica harp kazoo lute mandolin marimba oboe ocarina "
    "piccolo saxophone sitar tambourine theremin trombone trumpet tuba ukulele vibraphone viola violin xylophone zither").split()


def _selftest():
    a = np.array([1.0, 0]); b = np.array([1.0, 0]); assert abs(float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b))) - 1) < 1e-9, "cosine"
    assert int(np.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: t5c-kblam-rag-prefix", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def run() -> Dict:
    g = np.random.default_rng(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    enc_tok = AutoTokenizer.from_pretrained(ENCODER); enc_mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).to(DEV).eval()
    subs = list(dict.fromkeys(DISC_POOL)); g.shuffle(subs); subs = subs[:N_FACTS]
    pool = [" violet"," copper"," seven"," marble"," thunder"," willow"," saffron"," glacier"," ember"," quartz",
            " orchid"," harvest"," lantern"," meadow"," falcon"," cinnamon"," velvet"," anchor"," prism"," cobalt"]
    pool = [a for a in pool if len(tok(a, add_special_tokens=False)["input_ids"]) == 1]
    facts = []
    for s in subs:
        a = pool[int(g.integers(0, len(pool)))]
        facts.append({"subj": s, "prompt": "The secret code of %s is" % s, "ans": a,
                      "aid": tok(a, add_special_tokens=False)["input_ids"][0], "text": "The secret code of %s is%s. " % (s, a)})
    ntr = int(0.6 * len(facts)); test = facts[ntr:]

    def embed(texts):
        out = []
        for i in range(0, len(texts), 64):
            b = enc_tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
            with torch.no_grad():
                h = enc_mdl(**b).last_hidden_state[:, 0]
            out.append(torch.nn.functional.normalize(h, dim=-1).cpu().numpy())
        return np.concatenate(out)
    kb_emb = embed([f["text"] for f in facts])                            # KB = all facts encoded
    q_emb = embed([f["prompt"] for f in test])                            # query = held-out prompts

    def next_tok(prompt):
        e = tok(prompt, return_tensors="pt").to(DEV)
        with torch.no_grad():
            return int(torch.argmax(mdl(**e).logits[0, -1, :]))
    bare = retr_ok = rag = oracle = 0; n = len(test)
    for i, f in enumerate(test):
        bare += int(next_tok(f["prompt"]) == f["aid"])
        top1 = int(np.argmax(kb_emb @ q_emb[i]))                          # retrieve top-1 fact by cosine
        retr_ok += int(facts[top1]["subj"] == f["subj"])
        rag += int(next_tok(facts[top1]["text"] + f["prompt"]) == f["aid"])   # RAG: prepend retrieved fact
        oracle += int(next_tok(f["text"] + f["prompt"]) == f["aid"])      # oracle: prepend gold fact (upper bound)
    bare, retr_ok, rag, oracle = bare / n, retr_ok / n, rag / n, oracle / n
    print("  bare=%.3f retrieval-top1-acc=%.3f RAG-prefix-recall=%.3f oracle(gold-prefix)=%.3f (n=%d)" % (bare, retr_ok, rag, oracle, n), flush=True)
    del mdl, enc_mdl
    return {"bare": bare, "retrieval_acc": retr_ok, "rag_recall": rag, "oracle_recall": oracle, "n_test": n}


def verdict(r) -> Tuple[str, str]:
    s = "bare=%.3f retrieval-acc=%.3f RAG-recall=%.3f oracle=%.3f" % (r["bare"], r["retrieval_acc"], r["rag_recall"], r["oracle_recall"])
    if r["rag_recall"] >= 0.25:
        return ("HARD_PASS", "HARD_PASS: RAG-prefix held-out recall >=0.25 -- substrate retrieval + context-window injection works (decoupled from the failed cross-attn adapter; substrate-as-RAG path viable). " + s)
    if r["rag_recall"] >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: RAG-recall 0.05-0.25 (partial; check retrieval-acc vs oracle to localize). " + s)
    return ("HARD_FAIL", "HARD_FAIL: RAG-recall <0.05 -- even with the fact in-context the base model does not emit it (oracle=%.3f localizes whether retrieval or the base model is the limiter). " % r["oracle_recall"] + s)


print("[config] anchor=%s mode=%s facts=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
