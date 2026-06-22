"""ARM A PROJECTED-KEY REVIVAL v1 -- Path C angle 4: does CERT 591-style contrastive projection unlock sparse-fan-in + kWTA + superposition (ARM A) that FAILS on raw LM keys?

Context: 4-arm anisotropy rescue (commit fc3b8771, smoke MIDDLE_BAND) showed ARM A cerebellar K=5 + kWTA + superposition recall ~0.04 ~ A'dense control on already-projected pythia-160m keys (smoke regime: TRAIN_M=600, 200 steps). Research routed 5 revival angles per USER STANDING route-negatives. ANGLE 4 = key-source composition: re-run ARM A on a CERT 591-strength projection + add a TRUE raw-keys ARM A control (was missing from 4-arm).

DISCRIMINATOR (one cell resolves the question):
  HARD_PASS = recall_armA_projected >= 0.60 at M=10k under sigma in {0,0.1} -> sparse-superpos isn't dead; CERT 591 projection unlocks it; storage-chain item#3 has TWO paths (tag-retrieval CLASS + sparse-superpos-on-projected). Higher capability frontier.
  HARD_FAIL = recall_armA_projected < 0.20 -> sparse-superpos genuinely doesn't work even with projection; tag-retrieval CLASS is the only storage path; Path D's class-level disposition is final.
  MIDDLE_BAND = recall 0.20-0.60 -> partial mechanism; characterize.

KEY DIFFERENCES from 4-arm cell:
  1. PROJECTION strength: TRAIN_M=2500 + TRAIN_STEPS=600 (vs 4-arm smoke TRAIN_M=600/200; matches CERT 591's training budget per-M scale).
  2. RAW-KEYS CONTROL: ARM A applied to raw pythia residuals (NO projection). This is the load-bearing missing control for "does projection help."
  3. NOISE SWEEP: sigma in {0, 0.1, 0.3} (the 4-arm fixed at 0.1; noise-robustness discipline per Skunkworks).
  4. PROJECTION CAN-FAIL CTRL: shuffled-(K,Q) projection -> ARM A recall must be ~chance (validates projection isn't memorizing).

ARM A logic (verbatim shape from exp_anisotropy_rescue_4arm_sweep_v1_gpu.py _arms):
  sparse-fan-in S (d_out=expand*d, K=5 random +-1 dims/row) -> Z = kWTA(Ks @ S.T, frac=0.10) -> superposition store W=codebook[y].T @ Z -> decode argmax cosine.

CPU-only (pythia-160m, M up to 10k); 3 seeds; per_unit per (M, sigma, seed); B_storage_bits_per_mem reported; ASCII; per-seed checkpoint.

Cites: dense_KV_learned_key_MM_anisotropy + Litwin-Kumar2017 + Skunkworks-NESS-noise-discipline + Research-route-negatives-angle-4.
"""
from __future__ import annotations
import sys, os, argparse, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "armA_projected_key_revival_v1"
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (CPU-only; pythia-160m)
ENCODER = "EleutherAI/pythia-160m"
PROJ_DIM = 256          # CERT 591 full proj_dim
C = 256                 # codebook size (value labels)
EXPAND = 5              # ARM A expand factor (d' = 5 * d)
K_FANIN = 5             # cerebellar K=5 per Litwin-Kumar
KWTA_FRAC = 0.10        # top-10% kWTA
HELDOUT_FRAC_TRAIN = 0.50  # held-out 50% reserved for storage units (max_M = M_SWEEP_max); train half feeds projection
MAX_Q = 800             # eval-query cap per unit
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    M_SWEEP = [1000, 5000, 10000]
    SIGMA_SWEEP = [0.0, 0.1, 0.3]
    TRAIN_M = 2500
    TRAIN_STEPS = 600
else:
    SEEDS = [0]
    M_SWEEP = [1000]
    SIGMA_SWEEP = [0.0]
    TRAIN_M = 600
    TRAIN_STEPS = 150
# CONFIG_VERSION must include every result-affecting param (PROT-021 lesson)
CONFIG_VERSION = ("armA_projected_revival_v1; encoder=%s proj=%d C=%d expand=%d K=%d kwta=%.2f "
                  "M=%s sigma=%s seeds=%s train_M=%d steps=%d") % (
                  ENCODER, PROJ_DIM, C, EXPAND, K_FANIN, KWTA_FRAC, M_SWEEP, SIGMA_SWEEP, SEEDS, TRAIN_M, TRAIN_STEPS)

# CERT 591 corpus
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M):                                          # VERBATIM CERT 591
    keys, vq = [], []
    for i in range(M):
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]
        value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value))
        vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _np_norm(X):                                            # VERBATIM CERT 591
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def _kwta(X, frac):                                          # keep top-frac magnitudes per row, zero rest (sign preserved)
    k = max(1, int(frac * X.shape[1]))
    out = np.zeros_like(X, np.float32)
    idx = np.argpartition(np.abs(X), -k, axis=1)[:, -k:]
    np.put_along_axis(out, idx, np.take_along_axis(X, idx, axis=1), axis=1)
    return out


def _sparse_fanin(d, dp, K, g):                              # cerebellar: dp expanded units, each reads K random input dims (random +-1)
    S = np.zeros((dp, d), np.float32)
    for i in range(dp):
        idx = g.choice(d, K, replace=False)
        S[i, idx] = g.integers(0, 2, K).astype(np.float32) * 2 - 1
    return S


def _decode_argmax(scores, codebook):                        # nearest codebook entry by cosine (codebook rows unit-norm via _np_norm)
    Sn = _np_norm(scores)
    return np.argmax(Sn @ codebook.T, axis=1)


def _armA_recall(K_keys, K_cues, y, qidx, sigma, g, codebook, S_fanin):
    """Run ARM A: sparse-fan-in -> kWTA -> superposition store -> decode. Recall@1 on qidx."""
    d = K_keys.shape[1]
    Ks = _np_norm(K_keys) * np.sqrt(d)
    noise = sigma * g.standard_normal((len(qidx), d)).astype(np.float32) if sigma > 0 else 0.0
    cue = K_cues[qidx] + noise if isinstance(noise, np.ndarray) else K_cues[qidx].copy()
    cue = _np_norm(cue) * np.sqrt(d)
    Kexp = _kwta(Ks @ S_fanin.T, KWTA_FRAC)
    cueE = _kwta(cue @ S_fanin.T, KWTA_FRAC)
    W = codebook[y].T @ Kexp                                 # (d', d') superposition matrix
    pred = _decode_argmax(cueE @ W.T, codebook)
    return float((pred == y[qidx]).mean())


def _train_contrastive(K_tr, Q_tr, d, steps, seed, shuffle=False):
    """linear InfoNCE projection W (D x d): align cue_i -> key_i. shuffle=CAN-FAIL control. CPU torch."""
    import torch
    import torch.nn.functional as F
    torch.manual_seed(seed)
    K = torch.tensor(K_tr); Q = torch.tensor(Q_tr); n, D = K.shape
    if shuffle:
        Q = Q[torch.randperm(n)]                             # break alignment
    W = (torch.randn(D, d) * (1.0 / D ** 0.5)).requires_grad_(True)
    opt = torch.optim.Adam([W], lr=1e-2)
    bs = min(256, n)
    for step in range(steps):
        idx = torch.randperm(n)[:bs]
        tgt = torch.arange(len(idx))
        kp = F.normalize(K[idx] @ W, dim=1)
        qp = F.normalize(Q[idx] @ W, dim=1)
        lq = (qp @ kp.T) / 0.07; lk = (kp @ qp.T) / 0.07
        loss_align = 0.5 * (F.cross_entropy(lq, tgt) + F.cross_entropy(lk, tgt))
        kk = kp @ kp.T; off = kk - torch.eye(len(idx)) * 2.0
        loss_unif = off.mean()
        loss = loss_align + 0.5 * loss_unif
        opt.zero_grad(); loss.backward(); opt.step()
    return W.detach().numpy().astype(np.float32)


def _encode(texts):
    """CPU pythia-160m mean-pool encode. Mirror of CERT 591 encode() but CPU-fixed."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=48)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().numpy())
    del mdl
    return np.concatenate(out, 0).astype(np.float32)


def run_unit(seed):
    g = np.random.default_rng(seed)
    n_total = max(M_SWEEP) + TRAIN_M
    keys, cues = make_facts(n_total)
    print("  [seed=%d] encoding %d facts on %s (CPU)..." % (seed, n_total, ENCODER), flush=True)
    t_enc = time.time()
    K = _encode(keys); Q = _encode(cues)
    print("  [seed=%d] encode done in %.1fs (D=%d)" % (seed, time.time() - t_enc, K.shape[1]), flush=True)
    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    # LEARNED CERT 591-style projection on train half
    t_tr = time.time()
    W = _train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Wsh = _train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed, shuffle=True)
    print("  [seed=%d] train_contrastive (+shuffled-ctrl) done in %.1fs" % (seed, time.time() - t_tr), flush=True)
    Kp_all = K[ho] @ W                                       # projected keys (CERT 591-strength)
    Qp_all = Q[ho] @ W                                       # projected cues
    Ksh_all = K[ho] @ Wsh                                    # shuffled-ctrl projected
    Qsh_all = Q[ho] @ Wsh
    Kraw_all = K[ho]                                         # raw pythia residuals (RAW CONTROL)
    Qraw_all = Q[ho]
    # diagnostic: keysep + recall (sanity-check projection is doing its job)
    Kp_norm = _np_norm(Kp_all[:max(M_SWEEP)])
    Qp_norm = _np_norm(Qp_all[:max(M_SWEEP)])
    proj_recall_chk = float((np.argmax(Qp_norm[:200] @ Kp_norm[:max(200, max(M_SWEEP))].T, axis=1) == np.arange(200)).mean())
    Kraw_norm = _np_norm(Kraw_all[:max(M_SWEEP)])
    Qraw_norm = _np_norm(Qraw_all[:max(M_SWEEP)])
    raw_recall_chk = float((np.argmax(Qraw_norm[:200] @ Kraw_norm[:max(200, max(M_SWEEP))].T, axis=1) == np.arange(200)).mean())
    print("  [seed=%d] PROJ value-cue recall@1 sanity = %.3f | RAW recall = %.3f" % (seed, proj_recall_chk, raw_recall_chk), flush=True)
    by_cell = {}
    # codebook in d'-dim (the ARM A storage space)
    d_proj = Kp_all.shape[1]; d_raw = Kraw_all.shape[1]
    dp_proj = EXPAND * d_proj; dp_raw = EXPAND * d_raw
    for M in M_SWEEP:
        y = g.integers(0, C, M)
        qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
        # rng per (M, seed) for noise + fanin reproducibility
        gM = np.random.default_rng(seed * 7 + M)
        S_proj = _sparse_fanin(d_proj, dp_proj, K_FANIN, gM)
        S_raw = _sparse_fanin(d_raw, dp_raw, K_FANIN, gM)
        S_sh = _sparse_fanin(d_proj, dp_proj, K_FANIN, gM)
        cb_proj = _np_norm(gM.standard_normal((C, dp_proj)).astype(np.float32))
        cb_raw = _np_norm(gM.standard_normal((C, dp_raw)).astype(np.float32))
        for sigma in SIGMA_SWEEP:
            gS = np.random.default_rng(seed * 100 + int(sigma * 1000) + M)
            r_proj = _armA_recall(Kp_all[:M], Qp_all[:M], y, qidx, sigma, gS, cb_proj, S_proj)
            r_raw = _armA_recall(Kraw_all[:M], Qraw_all[:M], y, qidx, sigma, gS, cb_raw, S_raw)
            r_sh = _armA_recall(Ksh_all[:M], Qsh_all[:M], y, qidx, sigma, gS, cb_proj, S_sh)
            cell = "M%d_sig%.2f" % (M, sigma)
            by_cell[cell] = {
                "M": M, "sigma": sigma,
                "recall_armA_projected": round(r_proj, 4),
                "recall_armA_raw_control": round(r_raw, 4),
                "recall_armA_shuffled_proj_ctrl": round(r_sh, 4),
                "B_storage_bits_per_mem_proj": round(dp_proj * dp_proj * 32.0 / max(M, 1), 1),  # superposition matrix amortized
                "B_storage_bits_per_mem_raw": round(dp_raw * dp_raw * 32.0 / max(M, 1), 1),
            }
            a = by_cell[cell]
            print("  [seed=%d M=%d sig=%.2f] armA_proj=%.3f armA_raw=%.3f armA_shuf=%.3f" % (
                seed, M, sigma, a["recall_armA_projected"], a["recall_armA_raw_control"], a["recall_armA_shuffled_proj_ctrl"]), flush=True)
    return {
        "seed": seed,
        "by_cell": by_cell,
        "proj_recall_sanity": round(proj_recall_chk, 4),
        "raw_recall_sanity": round(raw_recall_chk, 4),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    # aggregate per (M, sigma) across seeds
    by_cell_agg = {}
    cell_keys = set()
    for u in units:
        cell_keys.update(u["by_cell"].keys())
    for ck in sorted(cell_keys):
        proj = [u["by_cell"][ck]["recall_armA_projected"] for u in units if ck in u["by_cell"]]
        raw = [u["by_cell"][ck]["recall_armA_raw_control"] for u in units if ck in u["by_cell"]]
        sh = [u["by_cell"][ck]["recall_armA_shuffled_proj_ctrl"] for u in units if ck in u["by_cell"]]
        M = units[0]["by_cell"][ck]["M"]; sigma = units[0]["by_cell"][ck]["sigma"]
        proj_mean = float(np.mean(proj)); proj_std = float(np.std(proj))
        raw_mean = float(np.mean(raw))
        sh_mean = float(np.mean(sh))
        proj_cv = proj_std / max(proj_mean, 1e-6)
        by_cell_agg[ck] = {
            "M": M, "sigma": sigma,
            "armA_proj_mean": round(proj_mean, 4),
            "armA_proj_std": round(proj_std, 4),
            "armA_proj_cv": round(proj_cv, 4),
            "armA_raw_mean": round(raw_mean, 4),
            "armA_shuffled_mean": round(sh_mean, 4),
            "lift_proj_over_raw": round(proj_mean - raw_mean, 4),
        }
    # discriminator focus: M=10000 at sigma in {0, 0.1}
    M_top = max(M_SWEEP)
    proj_at_top = [by_cell_agg[ck] for ck in by_cell_agg if by_cell_agg[ck]["M"] == M_top]
    proj_at_top_clean = [c for c in proj_at_top if c["sigma"] in (0.0, 0.1)]
    if proj_at_top_clean:
        max_proj_clean = max(c["armA_proj_mean"] for c in proj_at_top_clean)
        worst_proj_clean = min(c["armA_proj_mean"] for c in proj_at_top_clean)
    else:
        max_proj_clean = 0.0; worst_proj_clean = 0.0
    # CAN-FAIL: shuffled-projection ARM A should be ~chance (1/C); flag if not
    shuf_max = max(by_cell_agg[ck]["armA_shuffled_mean"] for ck in by_cell_agg)
    chance = 1.0 / C
    shuffled_too_good = shuf_max > 5.0 * chance + 0.05  # well above chance -> projection leak / control invalid
    raw_at_top = max((c["armA_raw_mean"] for c in proj_at_top), default=0.0)
    # cv guard (per Skunkworks discipline)
    max_cv_clean = max((c["armA_proj_cv"] for c in proj_at_top_clean), default=0.0)
    detail = {
        "by_cell_agg": by_cell_agg,
        "M_top": M_top,
        "max_armA_proj_clean": round(max_proj_clean, 4),
        "worst_armA_proj_clean": round(worst_proj_clean, 4),
        "armA_raw_at_top_max": round(raw_at_top, 4),
        "shuffled_proj_ctrl_max": round(shuf_max, 4),
        "max_cv_clean": round(max_cv_clean, 4),
        "n_seeds": len(units),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": "encoder=%s; CPU-only; raw control = ARM A on UNPROJECTED pythia residuals; shuffled = CAN-FAIL ctrl (projection trained on broken alignment)" % ENCODER,
        "cites": ["dense_KV_learned_key_MM_anisotropy", "Litwin-Kumar2017_cerebellar", "CERT591_kv_learned_projection_v1", "Research_route_negatives_angle4_2026-06-21"],
    }
    summary = ("M=%d clean(sig in 0,0.1) armA_proj max=%.3f worst=%.3f | armA_raw_max=%.3f | shuffled_max=%.3f (chance=%.4f) | cv_max=%.3f"
               % (M_top, max_proj_clean, worst_proj_clean, raw_at_top, shuf_max, chance, max_cv_clean))
    if shuffled_too_good:
        return ("HARD_FAIL", "HARD_FAIL[control-invalid]: shuffled-projection ARM A recall %.3f >> 5x chance %.4f -> control failed (projection isn't the cause of any lift). " % (shuf_max, chance) + summary, detail)
    # discriminator bands
    if worst_proj_clean >= 0.60 and max_cv_clean <= 0.10:
        return ("HARD_PASS", "DISCRIMINATOR HARD_PASS: ARM A on CERT591-style projected keys recall>=0.60 (worst clean=%.3f) at M=%d under noise sigma in {0,0.1}; sparse-fan-in + kWTA + superposition IS NOT DEAD; storage-chain item#3 has two paths. Lift over raw control = %.3f. " % (worst_proj_clean, M_top, worst_proj_clean - raw_at_top) + summary, detail)
    if max_proj_clean < 0.20:
        return ("HARD_FAIL", "DISCRIMINATOR HARD_FAIL: ARM A on projected keys recall<0.20 (max clean=%.3f) at M=%d; sparse-superpos doesn't work even with CERT591-style projection; tag-retrieval CLASS is the only storage path. " % (max_proj_clean, M_top) + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: partial rescue (clean recall %.3f to %.3f at M=%d); projection composes with ARM A but doesn't clear PASS bar. " % (worst_proj_clean, max_proj_clean, M_top) + summary, detail)


def _selftest():
    """Mechanism selftest: anisotropic synthetic keys -> raw ARM A collapses; isotropic decode-meter holds."""
    g = np.random.default_rng(0)
    d = 64; M = 200
    # anisotropic synthetic (strong common-mode)
    sig = g.standard_normal((M, d)).astype(np.float32)
    mu = g.standard_normal((1, d)).astype(np.float32) * 3.0
    Kp = sig + mu
    y = g.integers(0, C, M)
    qidx = np.arange(M)
    dp = EXPAND * d
    S = _sparse_fanin(d, dp, K_FANIN, g)
    cb = _np_norm(g.standard_normal((C, dp)).astype(np.float32))
    r_aniso = _armA_recall(Kp, Kp, y, qidx, 0.0, g, cb, S)
    assert r_aniso < 0.40, "anisotropic ARM A should be low recall (got %.2f)" % r_aniso
    # isotropic synthetic (decode-meter sanity): self-recall must hold
    iso = g.standard_normal((100, d)).astype(np.float32)
    yi = g.integers(0, C, 100)
    qidx_i = np.arange(100)
    dp_i = EXPAND * d
    S_i = _sparse_fanin(d, dp_i, K_FANIN, g)
    cb_i = _np_norm(g.standard_normal((C, dp_i)).astype(np.float32))
    r_iso = _armA_recall(iso, iso, yi, qidx_i, 0.0, g, cb_i, S_i)
    assert r_iso > 0.50, "isotropic small-M ARM A self-recall (decode-meter) should hold (got %.2f)" % r_iso
    # kWTA + sparse-fanin sanity
    assert _kwta(g.standard_normal((5, 10)).astype(np.float32), 0.2).shape == (5, 10)
    assert _sparse_fanin(8, 20, 3, g).shape == (20, 8)
    print("[selftest] PASS: anisotropic ARM A collapses (%.2f) + isotropic decode-meter holds (%.2f) + kWTA/fanin shape OK" % (r_aniso, r_iso), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s proj=%d M=%s sigma=%s seeds=%s train=%d/%d | %s" % (
        ANCHOR_NAME, RUN_MODE, ENCODER, PROJ_DIM, M_SWEEP, SIGMA_SWEEP, SEEDS, TRAIN_M, TRAIN_STEPS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "expand": EXPAND, "kfanin": K_FANIN,
               "train_M": TRAIN_M, "train_steps": TRAIN_STEPS, "schema": "armA-projected-revival"}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "M_SWEEP": M_SWEEP,
        "SIGMA_SWEEP": SIGMA_SWEEP,
        "n_seeds": len(SEEDS),
        "train_M": TRAIN_M,
        "train_steps": TRAIN_STEPS,
        "detail": detail,
        "metrics_source": "measured_cpu_armA_projected_key_revival",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        # explicit doc: substrate-only-decode gate N/A (this is a KV-storage cell, not an LM cell)
        "substrate_only_decode_gate": "N/A (KV-storage cell, not LM cell; per Path C ARM A discriminator framing)",
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
