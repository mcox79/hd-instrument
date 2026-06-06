"""
exp_g1_encoder_geometric_alignment_audit_v1 -- Batch G1 (encoder-selection protocol) -- CPU.

ROUTING: Batch G Tier-1 (strategic-priority Rank-1 + BGE-drill Test-1 merged). Characterizes the GEOMETRY that predicts
  substrate capacity: PR (participation ratio = effective dim) + rho_eff (mean pairwise cosine = anisotropy) for each
  candidate encoder on a fixed corpus. Corrected theory: high PR + low rho_eff (isotropic, high-rank) -> high capacity.
  Encoders: MiniLM-L6 / mpnet-768 / BGE-large / E5-large-v2 / Llama-3.2-1B(L15 last-token). Grounds the 4-step encoder
  selection protocol. CPU (model forwards on 500 samples; laptop-OK per spec but routed to runner for the cached models).
PRE-REGISTERED: HARD-PASS PR>40 AND rho_eff<0.35 for >=2 encoders (protocol confirmed). MID only 1 passes both. HF none.
FORMULA SELF-TESTS (PROT-022): 1. PR of isotropic ~ dim. 2. rho_eff of orthogonal ~ 0. 3. deps.
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

ANCHOR_NAME = "g1_encoder_geometric_alignment_audit_v1"
# (id, type, layer)
ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", "st", None), ("sentence-transformers/all-mpnet-base-v2", "st", None),
            ("BAAI/bge-large-en-v1.5", "st", None), ("intfloat/e5-large-v2", "st", None),
            ("meta-llama/Llama-3.2-1B", "lm", 15)]
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_ENC = 300; ENCODERS = ENCODERS[:2]
else:
    N_ENC = 500


def participation_ratio(emb):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False); s2 = s ** 2
    return float((s2.sum() ** 2) / (np.sum(s2 ** 2) + 1e-12))


def rho_eff(emb):
    e = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8); n = min(len(e), 400)
    G = e[:n] @ e[:n].T; iu = np.triu_indices(n, k=1)
    return float(np.mean(G[iu]))


def _selftest():
    g = np.random.default_rng(0); iso = g.standard_normal((300, 50)); assert participation_ratio(iso) > 30, "PR isotropic ~ dim"
    ortho = np.eye(40)[g.integers(0, 40, 200)] + 0.01 * g.standard_normal((200, 40)); assert rho_eff(ortho) < 0.2, "rho orthogonal ~ 0"
    print("[selftest] PASS: g1-geom", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n:
                    return out
    return out


def encode(eid, etype, layer, texts):
    tok = AutoTokenizer.from_pretrained(eid)
    if etype == "lm":
        tok.pad_token = tok.eos_token; m = AutoModelForCausalLM.from_pretrained(eid, output_hidden_states=True, use_safetensors=True).to(DEV).eval()
    else:
        m = AutoModel.from_pretrained(eid, use_safetensors=True).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t)
        if etype == "lm":
            h = o.hidden_states[layer]; lens = t["attention_mask"].sum(1) - 1; out.append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())
        else:
            h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def verdict(res) -> Tuple[str, str]:
    passers = [nm for nm, v in res.items() if v["PR"] > 40 and v["rho_eff"] < 0.35]
    summary = "PR/rho_eff: %s | pass(PR>40,rho<0.35): %s" % ({k: (round(v["PR"], 1), round(v["rho_eff"], 3)) for k, v in res.items()}, passers)
    if len(passers) >= 2:
        return ("HARD_PASS", "HARD_PASS: >=2 encoders pass (PR>40 AND rho_eff<0.35) -- geometric encoder-selection protocol confirmed. " + summary)
    if len(passers) == 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: only 1 encoder passes both criteria. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no encoder passes (PR>40 AND rho<0.35) -- geometry theory needs revision. " + summary)


print("[config] anchor=%s mode=%s N_enc=%d encoders=%s" % (ANCHOR_NAME, RUN_MODE, N_ENC, [e[0].split('/')[-1] for e in ENCODERS]), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); texts = load_texts(N_ENC); res = {}
for eid, etype, layer in ENCODERS:
    try:
        emb = encode(eid, etype, layer, texts); nm = eid.split("/")[-1]
        res[nm] = {"PR": participation_ratio(emb), "rho_eff": rho_eff(emb), "D": int(emb.shape[1])}
        print("  [%s] PR=%.1f rho_eff=%.3f D=%d" % (nm, res[nm]["PR"], res[nm]["rho_eff"], res[nm]["D"]), flush=True)
    except Exception as e:
        print("  [%s] SKIP: %s" % (eid, str(e)[:80]), flush=True)
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
