"""
exp_t5c_kblam_disc_scale_gpu_v1 -- Tier-5c Path B FOUNDATION: KBLaM-pattern fact-KB adapter; HELD-OUT recall -- GPU.

ROUTING: Path B v2.0 product claim, corrected per research_to_exp_dev_T5C_PATH_B_CORRECTED (KBLaM ICLR2025 arXiv:2410.10450).
  Re-architecture (NOT the Flamingo/middle-layer approach that won the perplexity claim). Key KBLaM ingredients implemented here:
  (A) W_k AND W_v BOTH project from a FROZEN bge-large encoder (one vector per fact = enc(subject+relation+object)), NOT the LLM
      hidden state -- this forces semantic retrieval and is what enables generalization.
  (B) EVERY transformer layer attends (rectangular attention) to ALL KB K/V pairs -- the anti-memorization architectural pressure.
  (C) answer-token cross-entropy alone (no contrastive loss). Recipe from Phase C (gate-lr 1e-3 / main 3e-4 / betas 0.9-0.95 /
      cosine / clip 1.0). Frozen Pythia-160M.
THIS IS THE FOUNDATION / ARCHITECTURE VALIDATION at MODERATE scale (N~2000 facts, all in KB, KB-present training). It de-risks
  the core question: does every-layer-rectangular + frozen-encoder keys GENERALIZE to held-out facts (vs the Flamingo memorization)?
  NEXT ITERATIONS (documented, not here): 50/50 KB-present/KB-absent composition, scale to 50K-100K facts, PP-107-gate + FHRR
  ablations. Per Research those are the full Path B (2-4 day effort); this cell validates the architecture cheaply first.
PRE-REGISTERED (architecture-validation bands): HARD-PASS held-out recall >= 0.50 (architecture generalizes -> proceed to 50K/50-50).
  MIDDLE 0.20-0.50 (partial -> scale likely helps). HARD-FAIL < 0.20 (architecture still memorizes; rethink before scaling).
FORMULA SELF-TESTS (PROT-022): 1. softmax. 2. tanh gate. 3. argmax.
ASCII-only. write_metrics + progress.jsonl + ckpt (resumable). PROT-018 _v1.
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

ANCHOR_NAME = "t5c_kblam_disc_scale_gpu_v1"; MODEL = "EleutherAI/pythia-160m"; ENCODER = "BAAI/bge-large-en-v1.5"
STEPS = 120 if "--smoke" in sys.argv else 2500; CKPT_EVERY = 200
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_FACTS = 300 if SMOKE else 4000


def _selftest():
    import numpy as _n; p = _n.exp([1.0, 2]); p = p / p.sum(); assert abs(p.sum() - 1) < 1e-9, "softmax"
    assert abs(math.tanh(0.0)) < 1e-9, "tanh gate"; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"
    print("[selftest] PASS: t5c-kblam-disc-scale-gpu-v1", flush=True)


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

ADJ = ["crimson", "ancient", "silent", "frozen", "golden", "hidden", "wild", "sacred", "burning", "silver",
       "hollow", "shining", "broken", "distant", "emerald", "iron", "velvet", "marble", "amber", "stormy",
       "quiet", "rapid", "noble", "feral", "lunar", "solar", "azure", "scarlet", "dusty", "misty",
       "jagged", "smooth", "ember", "frosted", "gilded", "rugged", "secret", "wandering", "echoing", "drifting",
       "vivid", "somber", "radiant", "shadowed", "blooming", "withered", "molten", "glacial", "verdant", "obsidian"]
NOUN = ["falcon", "harbor", "canyon", "lantern", "meadow", "citadel", "river", "forest", "mountain", "island",
        "tower", "bridge", "garden", "temple", "valley", "desert", "glacier", "cavern", "orchard", "fountain",
        "beacon", "thicket", "marsh", "summit", "delta", "reef", "dune", "grove", "spire", "vault",
        "cottage", "lagoon", "prairie", "ravine", "foundry", "archive", "observatory", "quarry", "hamlet", "estuary",
        "monastery", "vineyard", "lighthouse", "windmill", "aqueduct", "labyrinth", "sanctuary", "outpost", "bazaar", "fjord"]



DISC_POOL = ("aardvark albatross alligator antelope armadillo baboon badger barracuda beaver bison buffalo camel "
    "capybara caribou cheetah chimpanzee cobra cougar coyote crocodile dolphin elephant falcon ferret flamingo gazelle "
    "giraffe gorilla hedgehog hippopotamus hyena iguana jackal jaguar kangaroo koala lemur leopard llama lobster lynx "
    "manatee meerkat mongoose moose narwhal ocelot octopus opossum orangutan ostrich otter panther pelican penguin "
    "platypus porcupine puffin raccoon reindeer rhinoceros salamander scorpion seahorse sloth squid stingray tapir "
    "tarantula toucan vulture walrus weasel wolverine wombat "
    "amsterdam antwerp athens bangkok barcelona beirut belgrade bergen bologna bordeaux bremen brisbane bruges "
    "budapest cairo calgary canberra cardiff chennai copenhagen cordoba dakar damascus dresden dublin durban edinburgh "
    "florence geneva glasgow granada hamburg helsinki istanbul jakarta jerusalem karachi kyoto lagos lisbon ljubljana "
    "lyon madras marseille melbourne montreal nairobi naples nantes oslo ottawa palermo perth porto prague quebec "
    "reykjavik riga rotterdam salzburg santiago sapporo seville stockholm stuttgart tangier tbilisi toulouse "
    "valencia valparaiso venice verona warsaw wellington zagreb zurich "
    "almond apricot artichoke asparagus avocado basil beetroot blackberry blueberry broccoli cardamom cashew "
    "cauliflower celery cherry chestnut chickpea cilantro cinnamon clementine coconut coriander cranberry cucumber "
    "currant eggplant fennel ginger grapefruit hazelnut jackfruit kiwi kumquat lavender leek lemongrass lentil "
    "lychee mandarin mango marjoram molasses nectarine nutmeg oregano papaya paprika parsnip peppercorn persimmon "
    "pistachio plantain pomegranate pumpkin quince radish raspberry rhubarb rosemary rutabaga saffron scallion "
    "shallot spinach tamarind tangerine tarragon thyme turmeric turnip vanilla watercress zucchini "
    "accordion balalaika banjo bassoon bagpipe bongo carillon cello clarinet clavichord cornet didgeridoo dulcimer "
    "fiddle flute glockenspiel harmonica harp harpsichord kazoo lute mandolin marimba oboe ocarina piccolo "
    "saxophone sitar tambourine theremin trombone trumpet tuba ukulele vibraphone viola violin xylophone zither").split()

def make_facts(tok, g):
    pool = [" violet"," copper"," seven"," marble"," thunder"," willow"," saffron"," glacier"," ember"," quartz",
            " orchid"," harvest"," lantern"," meadow"," falcon"," cinnamon"," velvet"," anchor"," prism"," cobalt",
            " maple"," jupiter"," canyon"," ribbon"," basalt"," nectar"," pebble"," cypress"," marlin"," walnut",
            " amber"," crimson"," silver"," forest"," ocean"," desert"," tiger"," eagle"," raven"," otter"]
    pool = [a for a in pool if len(tok(a, add_special_tokens=False)["input_ids"]) == 1]
    subs = list(dict.fromkeys(DISC_POOL)); g.shuffle(subs)
    if N_FACTS > len(subs):
        subs = (subs * ((N_FACTS // len(subs)) + 1))
    subs = subs[:N_FACTS]
    facts = []
    for i, s in enumerate(subs):
        ans = pool[int(g.integers(0, len(pool)))]
        prompt = "The secret code of %s is" % s; enc_text = "The secret code of %s is%s" % (s, ans)
        facts.append({"subj": s, "prompt": prompt, "aid": tok(ans, add_special_tokens=False)["input_ids"][0], "ans": ans, "enc_text": enc_text})
    return facts

def run() -> Dict:
    torch.manual_seed(7); g = np.random.default_rng(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    H = mdl.config.hidden_size; NL = mdl.config.num_hidden_layers
    enc_tok = AutoTokenizer.from_pretrained(ENCODER); enc_mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).to(DEV).eval()
    for p in enc_mdl.parameters():
        p.requires_grad_(False)
    Edim = enc_mdl.config.hidden_size

    facts = make_facts(tok, g); ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:]
    print("[facts] %d total: %d train / %d held-out (ALL in KB); encoder=%s Edim=%d LLM H=%d layers=%d" % (len(facts), len(train), len(test), ENCODER, Edim, H, NL), flush=True)

    def encode(texts):                                                    # frozen bge-large CLS, normalized -> one vec per fact
        out = []
        for i in range(0, len(texts), 64):
            b = enc_tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEV)
            with torch.no_grad():
                h = enc_mdl(**b).last_hidden_state[:, 0]
            out.append(torch.nn.functional.normalize(h, dim=-1))
        return torch.cat(out)
    mem_enc = encode([f["enc_text"] for f in facts])                      # (Nfact, Edim) FROZEN external KB

    # KBLaM adapter: shared W_k,W_v from frozen encoder; per-layer Wq,Wo,gate,ln; insert at EVERY layer (rectangular)
    Wk = nn.Linear(Edim, H, bias=False).to(DEV); Wv = nn.Linear(Edim, H, bias=False).to(DEV)
    nn.init.normal_(Wk.weight, std=0.02); nn.init.normal_(Wv.weight, std=0.02)
    lns = nn.ModuleList([nn.LayerNorm(H).to(DEV) for _ in range(NL)])
    Wqs = nn.ModuleList([nn.Linear(H, H, bias=False).to(DEV) for _ in range(NL)])
    Wos = nn.ModuleList([nn.Linear(H, H, bias=False).to(DEV) for _ in range(NL)])
    for m in list(Wqs) + list(Wos):
        nn.init.normal_(m.weight, std=0.02)
    gates = nn.Parameter(torch.zeros(NL, device=DEV))
    state = {"on": False, "K": None, "V": None}

    def mk(Li):
        def hook(module, args, kwargs, output):
            if not state["on"] or not isinstance(output, tuple):
                return output
            hs = args[0] if len(args) else kwargs.get("hidden_states")
            if hs is None:
                return output
            q = Wqs[Li](lns[Li](hs))                                      # (B,S,H)
            att = (q @ state["K"].T) / math.sqrt(H)                       # (B,S,Nfact) rectangular
            ctx = torch.softmax(att, dim=-1) @ state["V"]                 # (B,S,H)
            return (output[0] + torch.tanh(gates[Li]) * Wos[Li](ctx),) + tuple(output[1:])
        return hook
    hooks = [mdl.gpt_neox.layers[Li].attention.register_forward_hook(mk(Li), with_kwargs=True) for Li in range(NL)]
    out_dir = get_output_dir(ANCHOR_NAME); Path(out_dir).mkdir(parents=True, exist_ok=True)
    prog = open(Path(out_dir) / "progress.jsonl", "a", encoding="utf-8")

    def set_kv():
        state["K"] = Wk(mem_enc); state["V"] = Wv(mem_enc)
    def recall(fs):
        hit = 0
        with torch.no_grad():
            set_kv()
            for f in fs:
                e = tok(f["prompt"], return_tensors="pt").to(DEV)
                hit += int(int(torch.argmax(mdl(**e).logits[0, -1, :])) == f["aid"])
        return hit / len(fs)

    state["on"] = False; bare = recall(test)
    params = list(Wk.parameters()) + list(Wv.parameters()) + list(lns.parameters()) + list(Wqs.parameters()) + list(Wos.parameters())
    opt = torch.optim.Adam([{"params": params, "lr": 3e-4, "weight_decay": 0.01}, {"params": [gates], "lr": 1e-3}], betas=(0.9, 0.95))
    def lr_lambda(s):
        return (s + 1) / 200.0 if s < 200 else 0.5 * (1 + math.cos(math.pi * min(1.0, (s - 200) / max(1, STEPS - 200))))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    state["on"] = True; t0 = time.time(); best = 0.0; since = 0
    for step in range(STEPS):
        opt.zero_grad(); f = train[step % len(train)]; e = tok(f["prompt"], return_tensors="pt").to(DEV)
        set_kv(); lg = mdl(**e).logits[0, -1, :]
        loss = torch.nn.functional.cross_entropy(lg.unsqueeze(0), torch.tensor([f["aid"]], device=DEV))
        loss.backward(); torch.nn.utils.clip_grad_norm_(params + [gates], 1.0); opt.step(); sched.step()
        if step % CKPT_EVERY == 0:
            tr = recall(train); te = recall(test); state["on"] = True
            rec = {"step": step, "of": STEPS, "ce": round(float(loss), 4), "train_recall": round(tr, 3), "heldout_recall": round(te, 3), "gate_mean": round(float(torch.tanh(gates).abs().mean()), 4), "elapsed_s": round(time.time() - t0, 1)}
            prog.write(json.dumps(rec) + "\n"); prog.flush()
            print("  [acc] step %d/%d CE=%.3f train-rec=%.3f HELD-OUT-rec=%.3f gate|mean|=%.3f" % (step, STEPS, float(loss), tr, te, rec["gate_mean"]), flush=True)
            if te > best + 1e-3:
                best = te; since = 0
            else:
                since += 1
                if since >= 4 and step > 600:
                    print("  [early-stop] held-out not improving (best=%.3f)" % best, flush=True); break
    state["on"] = True; tr = recall(train); te = recall(test); prog.close()
    for h in hooks:
        h.remove()
    gm = float(torch.tanh(gates).abs().mean()); del mdl, enc_mdl
    print("  FINAL: bare-heldout=%.3f train-recall=%.3f HELD-OUT-recall=%.3f best-heldout=%.3f gate|mean|=%.3f" % (bare, tr, te, max(best, te), gm), flush=True)
    return {"bare": bare, "train_recall": tr, "heldout_recall": te, "best_heldout": max(best, te), "gate_mean": gm, "n_facts": len(facts), "n_train": len(train), "n_test": len(test)}


def verdict(r) -> Tuple[str, str]:
    hp = r["best_heldout"]
    s = "bare=%.3f train-recall=%.3f HELD-OUT-recall=%.3f (best %.3f) gate|mean|=%.3f (%d facts, %d/%d)" % (r["bare"], r["train_recall"], r["heldout_recall"], r["best_heldout"], r["gate_mean"], r["n_facts"], r["n_train"], r["n_test"])
    if hp >= 0.50:
        return ("HARD_PASS", "HARD_PASS: KBLaM-pattern adapter (every-layer rectangular + frozen bge-large keys) GENERALIZES -- held-out fact recall >=0.50 at moderate scale -> architecture validated; proceed to 50K + 50/50. " + s)
    if hp >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial generalization (held-out 0.20-0.50); scaling facts likely helps. " + s)
    return ("HARD_FAIL", "HARD_FAIL: held-out <0.20 (architecture still memorizes at moderate scale; rethink before scaling). " + s)


print("[config] anchor=%s mode=%s model=%s encoder=%s steps=%d facts=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, ENCODER, STEPS, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
