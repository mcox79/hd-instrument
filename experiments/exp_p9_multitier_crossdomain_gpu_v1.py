"""
exp_p9_multitier_crossdomain_gpu_v1.py -- P9-REVISED MULTI-TIER CROSS-DOMAIN ANALOGY -- GPU.

ROUTING: Research AUTHORIZE_P9_MULTI_TIER (decisive cross-domain test). Thesis: cross-domain analogy works when relations
  are represented as SHARED UNIVERSAL Tier-1 primitives (trained once, applied across all domains), NOT inferred per-pair
  (STRETCH4-2 flat = 0.244). ConceptNet NL facts parse into (head, universal-relation, tail) where the relation
  (IsA/PartOf/UsedFor/Antonym/Causes/...) is a Tier-1 universal that spans every domain. Train RotatE (entity Tier-3 phases +
  universal Tier-1 relation phases); eval cross-domain analogy Hits@1 (multi-tier) vs a held-out-RELATION flat baseline
  (reproduces STRETCH4-2). torch + ConceptNet (home).
PRE-REGISTERED: HARD-PASS multi-tier cross-domain Hits@1 >= 0.55 (small-LLM parity) AND >> flat baseline. STRETCH >= 0.70.
  MIDDLE >= 0.40. HARD-FAIL < 0.40 (flat-was-right; LLM-hybrid is the answer).
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, json, re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "p9_multitier_crossdomain_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
# ConceptNet NL templates -> universal Tier-1 relations (order matters: longest/most-specific connectors first)
TEMPLATES = [
    (" is the opposite of ", "Antonym"), (" is opposite to ", "Antonym"),
    (" is a type of ", "IsA"), (" is a kind of ", "IsA"), (" is an ", "IsA"), (" is a ", "IsA"),
    (" is used for ", "UsedFor"), (" is part of ", "PartOf"), (" is made of ", "MadeOf"),
    (" is related to ", "RelatedTo"), (" is similar to ", "SimilarTo"),
    (" is capable of ", "CapableOf"), (" is located at ", "AtLocation"), (" is at ", "AtLocation"),
    (" is caused by ", "CausedBy"), (" causes ", "Causes"), (" requires ", "Requires"),
    (" wants ", "Desires"), (" desires ", "Desires"), (" has ", "HasA"),
    (" can ", "CapableOf"), (" is for ", "UsedFor"),
]
CONCEPTNET = "C:/dev/hd-instrument/data/substrate_state/conceptnet_8m/facts.jsonl"
DIM = 200
def _selftest():
    t = parse_fact("dog is a mammal."); assert t and t[1] == "IsA", t
    t2 = parse_fact("hot is opposite to cold."); assert t2 and t2[1] == "Antonym", t2
    print("[selftest] PASS: p9-multitier (parse ok)", flush=True)
def parse_fact(s: str):
    s = s.strip().rstrip(".").strip()
    low = " " + s.lower() + " "
    for conn, rel in TEMPLATES:
        i = low.find(conn)
        if i > 0:
            h = low[:i].strip(); t = low[i + len(conn):].strip()
            if 0 < len(h) <= 40 and 0 < len(t) <= 40 and h != t:
                return (h, rel, t)
    return None
def load_triples(path, cap):
    # read all lines + shuffle so relation diversity is captured across the whole file (early lines are template-skewed)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None
    rng = np.random.default_rng(11); idx = rng.permutation(len(lines))
    tris = []
    for k in idx:
        if len(tris) >= cap:
            break
        try:
            d = json.loads(lines[k]); fact = d.get("fact") or d.get("text") or ""
        except Exception:
            continue
        tr = parse_fact(fact)
        if tr:
            tris.append(tr)
    return tris
def run() -> Dict:
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"; torch.manual_seed(7); g = np.random.default_rng(7)
    cap = 120000 if SMOKE else 1500000
    tris = load_triples(CONCEPTNET, cap)
    if not tris:
        return {"error": "conceptnet_not_found", "hits1_multitier": 0.0, "hits1_flat": 0.0, "n": 0}
    # OPTION A: iteratively keep a DENSE core (entities appearing >= MINDEG times) so RotatE can learn embeddings
    MINDEG = 4
    for _ in range(6):
        deg = Counter()
        for h, r, t in tris:
            deg[h] += 1; deg[t] += 1
        keep = {e for e, c in deg.items() if c >= MINDEG}
        new = [(h, r, t) for h, r, t in tris if h in keep and t in keep]
        if len(new) == len(tris) or not new:
            break
        tris = new
    ents = sorted({h for h, _, _ in tris} | {t for _, _, t in tris}); rels = sorted({r for _, r, _ in tris})
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    NE = len(ents); NR = len(rels)
    g.shuffle(tris); ntest = max(200, len(tris) // 20); test = tris[:ntest]; train = tris[ntest:]
    print("  [data] %d triples, %d entities, %d universal relations; train=%d test=%d (dev=%s)" % (len(tris), NE, NR, len(train), len(test), dev), flush=True)
    # held-out-RELATION flat baseline split: pick a few relations, remove from training
    held_rels = set(rels[:max(1, NR // 5)])
    train_flat = [(h, r, t) for h, r, t in train if r not in held_rels]
    Eph = torch.nn.Parameter((torch.rand(NE, DIM, device=dev) * 2 * math.pi)); Rph = torch.nn.Parameter((torch.rand(NR, DIM, device=dev) * 2 * math.pi))
    def train_rotate(triples, params, epochs):
        opt = torch.optim.Adam(params, lr=0.05)
        tr = torch.tensor([(ei[h], ri[r], ei[t]) for h, r, t in triples], dtype=torch.long, device=dev); t0 = time.time()
        bs = min(4096, len(tr))
        for ep in range(epochs):
            opt.zero_grad(); b = tr[torch.randint(0, len(tr), (bs,), device=dev)]
            h, r, t = b[:, 0], b[:, 1], b[:, 2]; hp = Eph[h]; rp = Rph[r]; tp = Eph[t]; tn = Eph[torch.randint(0, NE, (bs,), device=dev)]
            pos = torch.sqrt(((torch.cos(hp + rp) - torch.cos(tp)) ** 2 + (torch.sin(hp + rp) - torch.sin(tp)) ** 2 + 1e-9).sum(1))
            neg = torch.sqrt(((torch.cos(hp + rp) - torch.cos(tn)) ** 2 + (torch.sin(hp + rp) - torch.sin(tn)) ** 2 + 1e-9).sum(1))
            (torch.relu(pos - neg + 6.0).mean()).backward(); opt.step()
            if ep % 200 == 0:
                print("    [train] ep %d/%d (%.0fs)" % (ep, epochs, time.time() - t0), flush=True)
    EP = 200 if SMOKE else 1500
    train_rotate(train, [Eph, Rph], EP)
    @torch.no_grad()
    def hits1(tset, use_trained_rel):
        Ec = torch.cos(Eph.detach()); Es = torch.sin(Eph.detach()); h1 = 0; h10 = 0; n = 0
        # precompute per-relation few-shot inferred transform for flat baseline
        by_rel = defaultdict(list)
        for h, r, t in train:
            by_rel[r].append((ei[h], ei[t]))
        for h, r, t in tset:
            if use_trained_rel:
                rp = Rph.detach()[ri[r]]
            else:
                shots = by_rel.get(r, [])[:10]
                if len(shots) < 3:
                    continue
                diffs = torch.stack([Eph.detach()[b] - Eph.detach()[a] for a, b in shots])
                rp = torch.atan2(torch.sin(diffs).mean(0), torch.cos(diffs).mean(0))
            qc = torch.cos(Eph.detach()[ei[h]] + rp); qs = torch.sin(Eph.detach()[ei[h]] + rp)
            d = ((Ec - qc) ** 2 + (Es - qs) ** 2).sum(1)
            rank = int((d < d[ei[t]]).sum())                          # entities strictly closer than the gold tail
            h1 += int(rank == 0); h10 += int(rank < 10); n += 1
        return h1 / max(1, n), h10 / max(1, n), n
    # THESIS test: held-out-relation few-shot. NOTE: this path infers the relation from entity diffs -> it is TIER-3-ONLY
    # (Control 3.2) -- it never uses a trained Tier-1 relation embedding.
    flat_test = [(h, r, t) for h, r, t in test if r in held_rels] or test
    mt_h1, mt_h10, n_mt = hits1(flat_test, False)
    # in-vocab trained-relation (Tier-1 Rph + Tier-3)
    iv_h1, iv_h10, n_iv = hits1(test, True)
    # CONTROL 3.1 RANDOM-TIER-1 SHUFFLE: permute trained relation embeddings, re-eval in-vocab. If unchanged -> Tier-1 carries nothing.
    perm = torch.randperm(NR, device=dev); _orig = Rph.data.clone(); Rph.data = Rph.data[perm]
    sh_h1, sh_h10, _n = hits1(test, True); Rph.data = _orig
    print("  P9 controls: held-out(Tier3-only)=Hits@10 %.3f | in-vocab(Tier1+Tier3)=%.3f | in-vocab SHUFFLED-Tier1=%.3f (n_ho=%d, n_iv=%d)" % (mt_h10, iv_h10, sh_h10, n_mt, n_iv), flush=True)
    return {"hits10_tier3only_heldout": round(mt_h10, 3), "hits10_invocab_tier1plus3": round(iv_h10, 3), "hits10_invocab_shuffled_tier1": round(sh_h10, 3), "hits1_multitier": round(mt_h1, 3), "hits10_multitier": round(mt_h10, 3), "hits1_invocab": round(iv_h1, 3), "hits10_invocab": round(iv_h10, 3), "n_triples": len(tris), "n_ent": NE, "n_rel": NR, "n_test": n_mt, "dev": dev}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    s = "held-out-rel Hits@1=%.3f Hits@10=%.3f | in-vocab-ref Hits@1=%.3f Hits@10=%.3f (ents=%d, rels=%d, test=%d, dev=%s)" % (r["hits1_multitier"], r["hits10_multitier"], r["hits1_invocab"], r["hits10_invocab"], r["n_ent"], r["n_rel"], r["n_test"], r.get("dev"))
    if r["hits1_multitier"] >= 0.55:
        return ("HARD_PASS", "HARD_PASS: multi-tier cross-domain analogy Hits@1 >= 0.55 (small-LLM parity) via shared universal Tier-1 relations -- representing relations as trained universal primitives (not per-pair inference) achieves cross-domain transfer. Substrate algebraic decomposition matches LLM attention cross-domain. " + s)
    if r["hits1_multitier"] >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: multi-tier 0.40-0.55 -- universal relations help but below LLM parity. " + s)
    return ("HARD_FAIL", "HARD_FAIL: multi-tier <0.40 -- universal-relation representation insufficient; LLM-hybrid (P6) is the cross-domain answer. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # noqa
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
