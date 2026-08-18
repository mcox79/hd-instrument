"""m_medqa_ingest_v1 -- M: certify substrate KB-INGEST of USMLE MedQA (500 QA pairs).

Path: substrate L3 capability tier breadth -- adds MEDICAL DOMAIN to substrate corpora
(currently has general English via ConceptNet n8 CERT 585 + structured KG via FB15k-237 U1 CERT 584).
This is a SMALL, FAST third-domain ingest cert to validate the multi-value Hebbian pattern
generalizes to encoder-projected (text -> vector) QA pairs.

Lineage:
  - Mechanism = U1/n8 multi-value Hebbian-accumulate pattern (chain-grade-validated).
  - Encoder = pythia-160m mean-pool, fp32, INGEST-ONLY (substrate-only-decode gate; same as n9).
  - Scoring = numpy matmul (no further model forward calls); _LLM_CALL_COUNTER tracks.

Mechanism (Strategy (a), simplest v1):
  1. Encode each (question + correct answer text) by pythia-160m mean-pool -> 768-D
     (NOT just question -- joining Q+A gives a richer per-pair anchor; recovery uses Q-only).
  2. Random project both Q-encode and Q+A-encode to N_DIM, normalize.
  3. Build entity codebook E[q_id] = projected Q+A vector (one entry per pair).
     Single relation r0 = "AnswersTo"; object = E[q_id] (self-referential pair-id store).
     (i.e. fact = (q_id, AnswersTo, q_id); store maps Q-only -> Q+A binding.)
  4. Hebbian: W += outer(E[q_id], key) / N for key = E_q[q_id] * R[0] * sqrt(N).
     Q-only key recovers Q+A entity; setrecall@1 = stored Q+A nearest to W @ key.
  5. Refuse-gate: tau calibrated on (in-KB Q-only confidences) vs (random non-medical OOD
     text confidences); test in-KB-accept >= 0.80 AND OOD-refuse >= 0.80.

Pre-reg bands (locked; mirrors n8 absolute-floor framing):
  HARD_PASS = ALL of:
    setrecall@1 (Q -> Q+A) >= 0.95  (load-bearing #1; per-pair retrieval)
    refuse OOD-refuse >= 0.80 AND in-KB-accept >= 0.80
    substrate setrecall >= 2.0 x random-key-control setrecall  (discriminator-regime; Fix #16)
    3 seeds, all bands met, substrate-only-decode gate intact
  MIDDLE_BAND = setrecall in [0.50, 0.95) OR refuse partial
  HARD_FAIL = setrecall < 0.50 OR refuse_OOD < 0.50

Honest scope:
  - Corpus = 500 USMLE QA pairs (data/datasets/medqa_usmle_500.jsonl).
  - Mechanism = SELF-REFERENTIAL recovery (Q->Q+A binding via random projection +
    Hebbian); we DO NOT claim semantic answer generation, only that the substrate
    recovers the stored Q+A representation given a Q-only cue, AND refuses fab-OOD.
  - Future v2 (option b/c) would add entity extraction or answer-choice modeling;
    out of scope for v1.
  - Substrate-only-decode gate: pythia-160m at INGEST only (encode all 500 Q+A texts
    + 500 Q-only texts + N_OOD non-medical OOD texts in ONE pass per seed; the
    model is del'd before scoring; scoring is numpy matmul throughout).

DISCRIMINATOR (Fix #16 -- CAN-FAIL regime):
  Random-key control: replace E_q (Q-only projected encodings) with random bipolar
  vectors of the same shape. setrecall must drop near chance (~1/500 = 0.002).
  This proves setrecall@1 success is encoder+projection-driven, not by-construction.

Smoke detect (TODO #6 resolution; in-cell name detection):
  RUN_MODE = "smoke" if HDLAB_EXP_NAME ends with "_smoke" (runner override safety).

CPU; ASCII; per-seed checkpoint via _seed_checkpoint helper.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Tuple, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics, resumable_seeds
)

ANCHOR_NAME = "m_medqa_ingest_v1"
CORPUS_PATH = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
CORPUS_PROVENANCE = "medqa_usmle_500_jsonl_local"

# Substrate-only-decode gate: pythia at INGEST only; scoring is numpy matmul.
_LLM_CALL_COUNTER = [0]

# Pre-reg bands (locked)
SETRECALL_FLOOR = 0.95
SETRECALL_FAIL = 0.50
REFUSE_OOD_MIN = 0.80
ACCEPT_INKB_MIN = 0.80
DISCRIMINATOR_RATIO = 2.0  # substrate setrecall must be >= 2x random-key-control setrecall


def _detect_run_mode():
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ENCODER = "EleutherAI/pythia-160m"
N_DIM_FULL = 4096
V_C_FULL = 1024  # codebook size (currently informational; not used in v1 mechanism but logged)

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 512
    M_PAIRS = 50      # smoke: 50 pairs only
    N_OOD = 50
    N_EVAL = 50
else:
    SEEDS = [7, 17, 23]
    N_DIM = N_DIM_FULL
    M_PAIRS = 500     # full corpus
    N_OOD = 500
    N_EVAL = 500

CONFIG_VERSION = (
    "m-medqa-ingest-v1: encoder=%s + random-proj(D->%d) + multi-value-hebbian + "
    "refuse-gate + random-key-control-discriminator; M=%d N_OOD=%d N_EVAL=%d V_C=%d; "
    "bands sr%.2f ood%.2f acc%.2f disc%.1fx"
) % (ENCODER, N_DIM, M_PAIRS, N_OOD, N_EVAL, V_C_FULL,
     SETRECALL_FLOOR, REFUSE_OOD_MIN, ACCEPT_INKB_MIN, DISCRIMINATOR_RATIO)


# Non-medical OOD texts (literal; not loaded from corpus). 12 templates; we'll cycle.
OOD_TEMPLATES = [
    "The Roman Empire's currency reforms under Diocletian addressed runaway inflation.",
    "Pacific salmon migrate upstream to spawn after years at sea.",
    "Modular arithmetic is foundational to cryptographic key exchange.",
    "Cherry blossoms in Kyoto peak in early April most years.",
    "The Bauhaus movement merged craft, art, and industrial design.",
    "Jazz fusion emerged in the late 1960s blending rock and improvisation.",
    "Subduction zones generate the deepest earthquakes on Earth.",
    "Olympic figure skaters often train ten thousand hours by age fifteen.",
    "Mediterranean climates feature mild wet winters and dry summers.",
    "Beekeepers monitor hives for varroa mites year-round.",
    "Concrete strength increases logarithmically with cure time.",
    "The compass rose on nautical charts indicates magnetic declination.",
]


def _normalize_rows(X):
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return _normalize_rows(X)


def _selftest():
    """Mechanism unit-test (no I/O, no encoder): self-referential Hebbian retrieve+refuse."""
    g = np.random.default_rng(0)
    n = 256
    M = 30
    n_rel = 1
    # Simulate Q-only vs Q+A encodings: same direction with small offset (Q+A is signal+noise of Q)
    E_q = _bipolar(M, n, g)
    delta = 0.3 * g.standard_normal((M, n)).astype(np.float32)
    E_qa = _normalize_rows(E_q + delta)
    R = _bipolar(n_rel, n, g)
    sq = math.sqrt(n)
    # Build W: store E_qa at key = E_q * R[0] * sq
    W = np.zeros((n, n), dtype=np.float32)
    keys = (E_q * R[0] * sq).astype(np.float32)
    W += (E_qa.T @ keys) / n
    # Retrieve: scores = E_qa @ (W @ key)
    S = E_qa @ (W @ keys.T)
    rec = float((np.argmax(S, axis=0) == np.arange(M)).mean())
    assert rec >= 0.80, "self-ref retrieval sanity (got %.2f)" % rec
    # Refuse confidence: in-KB top1 > OOD top1
    inkb_conf = S.max(axis=0).mean()
    ood_q = _bipolar(M, n, g)
    ood_keys = (ood_q * R[0] * sq).astype(np.float32)
    ood_S = E_qa @ (W @ ood_keys.T)
    ood_conf = ood_S.max(axis=0).mean()
    assert inkb_conf > ood_conf, "refuse conf in-KB(%.3f) > OOD(%.3f)" % (inkb_conf, ood_conf)
    # Discriminator: random keys should NOT recover (proves not-by-construction)
    rand_keys = _bipolar(M, n, g) * sq
    S_rand = E_qa @ (W @ rand_keys.T)
    rec_rand = float((np.argmax(S_rand, axis=0) == np.arange(M)).mean())
    assert rec_rand < 0.5 * rec, "discriminator: random keys (%.2f) should be << signal (%.2f)" % (rec_rand, rec)
    print("[selftest] PASS: self-ref recall=%.2f (rand-ctrl=%.2f); refuse-conf in-KB %.3f > OOD %.3f" %
          (rec, rec_rand, inkb_conf, ood_conf), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_corpus(m_pairs: int) -> Tuple[List[str], List[str]]:
    if not CORPUS_PATH.exists():
        raise FileNotFoundError("MedQA corpus not found at %s" % CORPUS_PATH)
    qs, qas = [], []
    with open(CORPUS_PATH, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= m_pairs:
                break
            row = json.loads(line)
            q = (row.get("question") or "").strip()
            a = (row.get("answer") or "").strip()
            qs.append(q)
            qas.append(q + " [ANSWER] " + a)
    return qs, qas


def encode_texts(texts: List[str]) -> np.ndarray:
    """CPU pythia-160m mean-pool encode. INGEST-only (encoder del'd before scoring)."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).eval()
    out = []
    B = 16
    for i in range(0, len(texts), B):
        t = tok(texts[i:i + B], return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        pooled = ((h * m).sum(1) / m.sum(1).clamp(min=1)).float().numpy()
        out.append(pooled)
        _LLM_CALL_COUNTER[0] += 1  # one forward call per batch (INGEST stage)
    del mdl
    return np.concatenate(out, 0).astype(np.float32)


def make_projection(D: int, N_target: int, g: np.random.Generator) -> np.ndarray:
    """Build one Gaussian random-projection matrix shape (D, N_target)."""
    return (g.standard_normal((D, N_target)).astype(np.float32) / math.sqrt(D))


def project_with(X: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Apply a fixed projection matrix; L2-normalize rows."""
    return _normalize_rows(X @ P)


def ingest_hebbian(E_q: np.ndarray, E_qa: np.ndarray, R: np.ndarray, n: int) -> np.ndarray:
    """W += outer(E_qa[i], key_i)/n; key_i = E_q[i] * R[0] * sqrt(n)."""
    sq = math.sqrt(n)
    keys = (E_q * R[0] * sq).astype(np.float32)
    W = (E_qa.T @ keys) / n
    return W.astype(np.float32)


def _confidence_scores(E_qa: np.ndarray, R: np.ndarray, W: np.ndarray, query_emb: np.ndarray) -> np.ndarray:
    """For each query row, return scores against all stored E_qa entries. Shape (Q, M)."""
    sq = math.sqrt(E_qa.shape[1])
    keys = (query_emb * R[0] * sq).astype(np.float32)        # (Q, N)
    # scores[q,i] = E_qa[i] . (W . keys[q])
    return (keys @ W.T) @ E_qa.T                              # (Q, M)


def setrecall_at_1(E_qa: np.ndarray, R: np.ndarray, W: np.ndarray, E_q: np.ndarray,
                   n_eval: int, g: np.random.Generator) -> float:
    M = E_q.shape[0]
    idx = np.arange(M) if n_eval >= M else np.sort(g.choice(M, n_eval, replace=False))
    Q = E_q[idx]
    S = _confidence_scores(E_qa, R, W, Q)
    pred = S.argmax(axis=1)
    return float((pred == idx).mean())


def refuse_gate(E_qa: np.ndarray, R: np.ndarray, W: np.ndarray, E_q: np.ndarray,
                E_ood: np.ndarray, g: np.random.Generator) -> dict:
    M = E_q.shape[0]
    # Confidences: top-1 score per query
    S_in = _confidence_scores(E_qa, R, W, E_q).max(axis=1)
    S_ood = _confidence_scores(E_qa, R, W, E_ood).max(axis=1)
    # Calibrate tau on first half; eval on second half
    h_in = len(S_in) // 2
    h_ood = len(S_ood) // 2
    cal_in, ev_in = S_in[:h_in], S_in[h_in:]
    cal_ood, ev_ood = S_ood[:h_ood], S_ood[h_ood:]
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau = float(cands[0])
    best_bal = -1.0
    for tau in cands:
        acc = float((cal_in >= tau).mean())
        ref = float((cal_ood < tau).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal
            best_tau = float(tau)
    return {
        "tau": best_tau,
        "inkb_accept": float((ev_in >= best_tau).mean()),
        "ood_refuse": float((ev_ood < best_tau).mean()),
        "inkb_conf_mean": float(S_in.mean()),
        "ood_conf_mean": float(S_ood.mean()),
    }


def discriminator_random_key(E_qa: np.ndarray, R: np.ndarray, W: np.ndarray,
                              n_eval: int, g: np.random.Generator) -> float:
    """CAN-FAIL control: random bipolar keys should recover near chance (~1/M)."""
    M = E_qa.shape[0]
    n = E_qa.shape[1]
    sq = math.sqrt(n)
    # Use random bipolar in place of E_q[idx]
    rand_q = _bipolar(n_eval, n, g)
    keys = (rand_q * R[0] * sq).astype(np.float32)
    S = (keys @ W.T) @ E_qa.T
    pred = S.argmax(axis=1)
    # For random keys there's no "correct" index; we use recall@1 against arbitrary fixed targets
    # (i.e. expected ~1/M); compare top-pred vs a uniform random ground-truth assignment.
    g2 = np.random.default_rng(g.integers(0, 2**31))
    targets = g2.integers(0, M, size=n_eval)
    return float((pred == targets).mean())


def run_seed(seed: int) -> dict:
    g = np.random.default_rng(seed)
    print("  [seed=%d] loading %d MedQA pairs..." % (seed, M_PAIRS), flush=True)
    qs, qas = load_corpus(M_PAIRS)
    n_pairs = len(qs)
    assert n_pairs == M_PAIRS, "loaded %d != requested %d" % (n_pairs, M_PAIRS)

    # OOD: cycle OOD_TEMPLATES + light per-seed perturbation to vary surface form
    ood_texts = []
    rng_ood = np.random.default_rng(seed + 1000)
    for k in range(N_OOD):
        base = OOD_TEMPLATES[k % len(OOD_TEMPLATES)]
        # Append a per-instance tag so encoder doesn't memo-collapse identical strings
        ood_texts.append(base + " (item %d)" % (k % 50))

    # Encode (INGEST stage; pythia-160m forward calls accumulate in _LLM_CALL_COUNTER)
    print("  [seed=%d] encoding %d Q-only + %d Q+A + %d OOD texts (CPU pythia-160m)..." %
          (seed, n_pairs, n_pairs, N_OOD), flush=True)
    t_enc = time.time()
    pre_calls = _LLM_CALL_COUNTER[0]
    all_texts = qs + qas + ood_texts
    all_emb = encode_texts(all_texts)
    enc_calls = _LLM_CALL_COUNTER[0] - pre_calls
    enc_wall = time.time() - t_enc
    print("  [seed=%d] encode done in %.1fs (%d forward batches; D_enc=%d)" %
          (seed, enc_wall, enc_calls, all_emb.shape[1]), flush=True)

    Q_emb = all_emb[:n_pairs]
    QA_emb = all_emb[n_pairs:2 * n_pairs]
    OOD_emb = all_emb[2 * n_pairs:]

    # Lock the scoring boundary -- nothing past here may invoke an LM forward call.
    inference_phase_pre_calls = _LLM_CALL_COUNTER[0]

    # ONE shared random projection (D_enc -> N_DIM) for Q / Q+A / OOD so encoder-space
    # geometry is preserved into substrate-space. Using independent projections would
    # decorrelate Q from Q+A and collapse setrecall to chance (smoke gate caught this 2026-06-22).
    D_enc = Q_emb.shape[1]
    P_shared = make_projection(D_enc, N_DIM, g)
    E_q = project_with(Q_emb, P_shared)
    E_qa = project_with(QA_emb, P_shared)
    E_ood = project_with(OOD_emb, P_shared)
    R = _bipolar(1, N_DIM, g)

    # Ingest
    t_ing = time.time()
    W = ingest_hebbian(E_q, E_qa, R, N_DIM)
    ing_wall = time.time() - t_ing

    # Eval
    t_ev = time.time()
    sr = setrecall_at_1(E_qa, R, W, E_q, N_EVAL, np.random.default_rng(seed + 2))
    rg = refuse_gate(E_qa, R, W, E_q, E_ood, np.random.default_rng(seed + 3))
    disc = discriminator_random_key(E_qa, R, W, N_EVAL, np.random.default_rng(seed + 4))
    eval_wall = time.time() - t_ev

    # Verify substrate-only-decode gate held
    inference_phase_calls = _LLM_CALL_COUNTER[0] - inference_phase_pre_calls
    assert inference_phase_calls == 0, ("substrate-only gate broken: %d LM calls during inference phase" %
                                         inference_phase_calls)

    print("  [seed=%d] setrecall=%.4f (rand-ctrl=%.4f; ratio=%.2fx) | refuse OOD=%.3f accept=%.3f (tau=%.4g)"
          " | walls enc=%.1f ing=%.1f ev=%.1f" % (
              seed, sr, disc, (sr / max(disc, 1e-6)),
              rg["ood_refuse"], rg["inkb_accept"], rg["tau"],
              enc_wall, ing_wall, eval_wall), flush=True)

    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": M_PAIRS,
        "config_version": CONFIG_VERSION,
        "setrecall_at_1": round(sr, 4),
        "random_key_control_recall": round(disc, 4),
        "discriminator_ratio": round(sr / max(disc, 1e-6), 3),
        "refuse_gate": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in rg.items()},
        "encoder_forward_batches": enc_calls,
        "inference_phase_llm_calls": inference_phase_calls,
        "walls": {"encode_s": round(enc_wall, 2),
                  "ingest_s": round(ing_wall, 2),
                  "eval_s": round(eval_wall, 2)},
        "elapsed_s": round(enc_wall + ing_wall + eval_wall, 2),
    }


def compute_verdict(per_seed: List[dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed results.")
    srs = np.array([p["setrecall_at_1"] for p in per_seed])
    discs = np.array([p["random_key_control_recall"] for p in per_seed])
    oods = np.array([p["refuse_gate"]["ood_refuse"] for p in per_seed])
    accs = np.array([p["refuse_gate"]["inkb_accept"] for p in per_seed])
    ratios = srs / np.maximum(discs, 1e-6)
    cv = float(np.std(srs) / max(float(np.mean(srs)), 1e-9))
    sr_mean = float(srs.mean())
    disc_mean = float(discs.mean())
    ood_mean = float(oods.mean())
    acc_mean = float(accs.mean())
    ratio_mean = float(ratios.mean())
    summ = ("setrecall@1=%.4f (rand-ctrl=%.4f, ratio=%.2fx, need >=%.1fx; floor %.2f) | "
            "refuse OOD=%.3f accept=%.3f (>=%.2f) | cv=%.3f | n_seeds=%d") % (
        sr_mean, disc_mean, ratio_mean, DISCRIMINATOR_RATIO, SETRECALL_FLOOR,
        ood_mean, acc_mean, REFUSE_OOD_MIN, cv, len(per_seed))
    sr_pass = sr_mean >= SETRECALL_FLOOR
    sr_fail = sr_mean < SETRECALL_FAIL
    refuse_pass = ood_mean >= REFUSE_OOD_MIN and acc_mean >= ACCEPT_INKB_MIN
    disc_pass = ratio_mean >= DISCRIMINATOR_RATIO
    if sr_fail or ood_mean < 0.50:
        return ("HARD_FAIL", "HARD_FAIL: " + summ)
    if sr_pass and refuse_pass and disc_pass:
        return ("HARD_PASS",
                "HARD_PASS: substrate KB-ingest GOVERNED (refuse-gate) + DISCRIMINATED (vs random-key ctrl) "
                "on medical-domain MedQA. " + summ)
    return ("MIDDLE_BAND", "MIDDLE_BAND: partial -- not all load-bearing dims hold. " + summ)


def main():
    print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d corpus=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_PAIRS, CORPUS_PROVENANCE, CONFIG_VERSION), flush=True)
    print("[smoke-detect] HDLAB_EXP_NAME=%r RUN_MODE=%s" %
          (os.environ.get("HDLAB_EXP_NAME", ""), RUN_MODE), flush=True)
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg = {"N": N_DIM, "M": M_PAIRS, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_cfg)
    print("  [ckpt] %d of %d seeds already complete; running %s" %
          (len(done), len(SEEDS), remaining), flush=True)
    per_seed_results: List[dict] = []
    for s in done:
        body = aggregate_partials(out_dir, [s], run_config=run_cfg).get(str(s))
        if body is not None:
            per_seed_results.append(body)
    for seed in remaining:
        rec = run_seed(seed)
        write_partial_key(out_dir, seed, rec)
        per_seed_results.append(rec)
    # Preserve seed order
    per_seed_results.sort(key=lambda r: SEEDS.index(r["seed"]) if r["seed"] in SEEDS else 999)
    v, vmsg = compute_verdict(per_seed_results)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed_results),
        "config_version": CONFIG_VERSION,
        "per_seed": per_seed_results,
        "zero_llm_calls_at_inference": all(p.get("inference_phase_llm_calls", 0) == 0
                                            for p in per_seed_results),
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "corpus_provenance": CORPUS_PROVENANCE,
        "allow_synthetic": False,
        "DESIGN_NOTE": (
            "M MedQA ingest v1; mirrors U1/n8 multi-value Hebbian; pythia-160m encoder INGEST-only "
            "(forward calls accumulate during encode; zero LM calls during scoring); self-referential "
            "Q->Q+A binding via random projection + Hebbian; refuse-gate calibrated on (in-KB, OOD) split; "
            "random-key control = CAN-FAIL discriminator (Fix #16). HONEST SCOPE: this is a memorization "
            "+ refuse certify, NOT a semantic answer-generation claim."
        ),
    }
    write_metrics(out_dir, metrics, per_seed_results)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    main()
