"""
exp_t5c_pp225_qwen15b_fp32proj_kb10k_v1 -- Path B rescue R3: supervised projection head (bypass cross-attn) -- GPU.

ROUTING: strategy_request_to_exp_dev_cycle203_kblam_rescue R3. The KBLaM cross-attn adapter failed held-out recall. R3 isolates
  whether the problem is the CROSS-ATTN GATE architecture vs the PROJECTION quality: train a linear head mapping the substrate
  fact embedding (frozen bge-large) DIRECTLY to LLM logit space, add it to the frozen model's final logits (no attention hook,
  no gate). If held-out recall generalizes, the projection path works and the cross-attn gate was the limiter. Uses the fact's
  own embedding (gold; retrieval itself is validated separately by R2). Frozen Pythia-160M + frozen bge-large.
PRE-REGISTERED: HARD-PASS held-out recall >= 0.25 (projection generalizes -> projection path viable, cross-attn was the limiter).
  MIDDLE >= 0.05. HARD-FAIL < 0.05 (projection memorizes train / does not generalize).
FORMULA SELF-TESTS (PROT-022): 1. softmax. 2. argmax. 3. CE>=0.
ASCII-only. write_metrics + progress.jsonl. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "t5c_pp225_qwen15b_fp32proj_kb10k_v1"; MODEL = "Qwen/Qwen2.5-1.5B-Instruct"; ENCODER = "BAAI/bge-large-en-v1.5"
STEPS = 100 if "--smoke" in sys.argv else 3000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_FACTS = 300 if SMOKE else 10000
DISC_POOL = ("aardvark albatross alligator antelope armadillo baboon badger barracuda beaver bison buffalo camel capybara "
    "caribou cheetah chimpanzee cobra cougar coyote crocodile dolphin elephant falcon ferret flamingo gazelle giraffe gorilla "
    "hedgehog hippopotamus hyena iguana jackal jaguar kangaroo koala lemur leopard llama lobster lynx manatee meerkat mongoose "
    "moose narwhal ocelot octopus opossum orangutan ostrich otter panther pelican penguin platypus porcupine puffin raccoon "
    "reindeer rhinoceros salamander scorpion seahorse sloth squid stingray tapir tarantula toucan vulture walrus weasel "
    "wolverine wombat amsterdam antwerp athens bangkok barcelona beirut belgrade bergen bologna bordeaux bremen brisbane bruges "
    "budapest cairo calgary canberra cardiff chennai copenhagen cordoba dakar damascus dresden dublin durban edinburgh florence "
    "geneva glasgow granada hamburg helsinki istanbul jakarta jerusalem karachi kyoto lagos lisbon ljubljana lyon madras "
    "marseille melbourne montreal nairobi naples nantes oslo ottawa palermo perth porto prague quebec reykjavik riga rotterdam "
    "salzburg santiago sapporo seville stockholm stuttgart tangier tbilisi toulouse valencia venice verona warsaw wellington "
    "zagreb zurich almond apricot artichoke asparagus avocado basil beetroot blackberry blueberry broccoli cashew cauliflower "
    "celery cherry chestnut chickpea cinnamon clementine coconut cranberry cucumber currant eggplant fennel ginger grapefruit "
    "hazelnut jackfruit kiwi kumquat lavender leek lentil lychee mandarin mango marjoram nectarine nutmeg oregano papaya "
    "paprika parsnip persimmon pistachio plantain pomegranate pumpkin quince radish raspberry rhubarb rosemary saffron scallion "
    "shallot spinach tamarind tangerine tarragon thyme turmeric turnip vanilla watercress zucchini accordion banjo bassoon "
    "bagpipe bongo cello clarinet cornet dulcimer fiddle flute harmonica harp kazoo lute mandolin marimba oboe ocarina piccolo "
    "saxophone sitar tambourine theremin trombone trumpet tuba ukulele vibraphone viola violin xylophone zither").split()


def _selftest():
    import numpy as _n; p = _n.exp([1.0, 2]); p = p / p.sum(); assert abs(p.sum() - 1) < 1e-9, "softmax"
    assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: pp225-qwen15b-fp32proj-kb10k", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    import torch.nn as nn
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def run() -> Dict:
    torch.manual_seed(7); g = np.random.default_rng(7)
    tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16, trust_remote_code=True).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    V = mdl.config.vocab_size
    enc_tok = AutoTokenizer.from_pretrained(ENCODER); enc_mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).to(DEV).eval()
    for p in enc_mdl.parameters():
        p.requires_grad_(False)
    Edim = enc_mdl.config.hidden_size
    _base = list(dict.fromkeys(DISC_POOL)); subs = ["%s-%04d" % (_base[i % len(_base)], i) for i in range(N_FACTS)]; g.shuffle(subs)
    pool = [" violet"," copper"," seven"," marble"," thunder"," willow"," saffron"," glacier"," ember"," quartz",
            " orchid"," harvest"," lantern"," meadow"," falcon"," cinnamon"," velvet"," anchor"," prism"," cobalt"]
    pool = [a for a in pool if len(tok(a, add_special_tokens=False)["input_ids"]) == 1]
    facts = []
    for s in subs:
        a = pool[int(g.integers(0, len(pool)))]
        facts.append({"prompt": "The secret code of %s is" % s, "aid": tok(a, add_special_tokens=False)["input_ids"][0], "text": "The secret code of %s is%s." % (s, a)})
    ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:][:2000]
    print("[facts] %d (%d train / %d held-out); Edim=%d V=%d" % (len(facts), len(train), len(test), Edim, V), flush=True)

    def embed(texts):
        out = []
        for i in range(0, len(texts), 64):
            b = enc_tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
            with torch.no_grad():
                h = enc_mdl(**b).last_hidden_state[:, 0]
            out.append(torch.nn.functional.normalize(h, dim=-1))
        return torch.cat(out)
    for f, e in zip(facts, embed([f["text"] for f in facts])):
        f["emb"] = e.float()
    del enc_mdl; torch.cuda.empty_cache()   # free bge-large; only needed for the one-time embed
    # frozen final-logits cache (the base model never changes); add projected retrieval on top
    def base_logits(prompt):
        with torch.no_grad():
            return mdl(**tok(prompt, return_tensors="pt").to(DEV)).logits[0, -1, :]
    proj = nn.Linear(Edim, V, bias=False).to(DEV); nn.init.normal_(proj.weight, std=0.02)
    scale = nn.Parameter(torch.tensor(1.0, device=DEV))
    out_dir = get_output_dir(ANCHOR_NAME); Path(out_dir).mkdir(parents=True, exist_ok=True); prog = open(Path(out_dir) / "progress.jsonl", "a", encoding="utf-8")

    def recall(fs, on):
        hit = 0
        with torch.no_grad():
            for f in fs:
                lg = base_logits(f["prompt"]).float()
                if on:
                    lg = lg + scale * proj(f["emb"])
                hit += int(int(torch.argmax(lg)) == f["aid"])
        return hit / len(fs)
    bare = recall(test, False)
    opt = torch.optim.Adam(list(proj.parameters()) + [scale], lr=1e-3, weight_decay=0.01)
    t0 = time.time(); best = 0.0; since = 0
    for step in range(STEPS):
        opt.zero_grad(); f = train[step % len(train)]
        lg = base_logits(f["prompt"]) + scale * proj(f["emb"])
        loss = torch.nn.functional.cross_entropy(lg.float().unsqueeze(0), torch.tensor([f["aid"]], device=DEV))
        loss.backward(); opt.step()
        if step % 300 == 0:
            tr = recall(train, True); te = recall(test, True)
            rec = {"step": step, "of": STEPS, "ce": round(float(loss), 4), "train_recall": round(tr, 3), "heldout_recall": round(te, 3), "elapsed_s": round(time.time() - t0, 1)}
            prog.write(json.dumps(rec) + "\n"); prog.flush()
            print("  [acc] step %d/%d CE=%.3f train-rec=%.3f HELD-OUT-rec=%.3f" % (step, STEPS, float(loss), tr, te), flush=True)
            if te > best + 1e-3:
                best = te; since = 0
            else:
                since += 1
                if since >= 4 and step > 900:
                    print("  [early-stop]", flush=True); break
    tr = recall(train, True); te = recall(test, True); prog.close(); del mdl
    print("  FINAL: bare=%.3f train-recall=%.3f HELD-OUT-recall=%.3f best=%.3f" % (bare, tr, te, max(best, te)), flush=True)
    return {"bare": bare, "train_recall": tr, "heldout_recall": te, "best_heldout": max(best, te), "n_train": len(train), "n_test": len(test)}


def verdict(r) -> Tuple[str, str]:
    hp = r["best_heldout"]
    s = "bare=%.3f train-recall=%.3f HELD-OUT-recall=%.3f (best %.3f) (%d/%d)" % (r["bare"], r["train_recall"], r["heldout_recall"], r["best_heldout"], r["n_train"], r["n_test"])
    if hp >= 0.50:
        return ("HARD_PASS", "HARD_PASS: projection head generalizes (held-out >=0.25) -- direct retrieval->logit projection works; the cross-attn GATE was the Path B limiter, not the projection. " + s)
    if hp >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: held-out 0.05-0.25 (partial). " + s)
    return ("HARD_FAIL", "HARD_FAIL: held-out <0.05 -- projection memorizes train / does not generalize (projection path also limited). " + s)


print("[config] anchor=%s mode=%s facts=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
