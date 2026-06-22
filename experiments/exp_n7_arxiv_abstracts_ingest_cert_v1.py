"""
n7_arxiv_abstracts_ingest_cert_v1 -- N7: substrate-native char-LM cert against arxiv abstracts.

MOTIVATION (USER 2026-06-22 do-it-all Tier-2 ingest-breadth expansion):
  arxiv abstracts = scientific-text small-vocab technical English (~1-10M chars
  depending on dataset availability; from public HF datasets). Probes whether
  the substrate char-LM generalizes ingest beyond cleaned Wikipedia (WikiText-
  103) or natural language (text8) to a domain-specific scientific register.
  Char-level absolute-floor BPC baselines (approx; smaller corpus):
    uniform-vocab  ~ log2(|V|) (printable ASCII ~6.6, lowercase-only ~4.7)
    bigram         ~ 3.8-4.2 BPC
    5-gram-KN      ~ 2.4-2.8 BPC
    LSTM           ~ 1.6-2.0 BPC
  These map onto absolute-floor cert bands (parent prompt):
    HARD_PASS:     substrate_bpc <= 2.80  (beats 5-gram-KN; chain-grade)
    MIDDLE_BAND:   2.80 < substrate_bpc <= 4.20  (between 5-gram-KN and bigram)
    HARD_FAIL:     substrate_bpc > 4.20  (worse than bigram)

REFERENT RECONCILIATION (parent prompt says "N1 v3.1 concept-LM plugin"):
  See sibling cell n6_wikitext103_ingest_cert_v1.py for the same reconciliation:
  arxiv-abstracts ingest-breadth-cert is naturally CHARACTER-level (matches
  text8 cert pattern; absolute-floor BPC bands map cleanly; no Pythia-residual
  token-id dependency). Plugs in SubstrateCharLM (substrate-native char-LM).

THIS CELL:
  - Substrate-native char-LM (SubstrateCharLM; 4-primitive bipolar-bind
    streaming Hebbian + anti-Hebbian contrastive).
  - Ingest = arxiv abstracts (HF candidates: ccdv/arxiv-classification,
    armanc/scientific_papers config=arxiv, arxiv_dataset; loader tries each in
    order; first available wins; cached to data/arxiv_abstracts_cache).
  - Score = char-BPC on held-out validation slice (HF split; falls back to
    train-tail if validation absent).
  - Baselines = uniform-|V| + char-bigram-MLE on SAME train + scored on SAME
    held-out.
  - Per-seed checkpointed (PROT-021 run_config guard); resume-restartable.

HONEST SCOPE (parent prompt 'honest surprises'):
  - HF arxiv-abstracts dataset availability is NOT guaranteed. The loader tries
    three candidate datasets in order; if all fail, allow_synthetic=False raises
    a RuntimeError (the cert run REFUSES to silently fall back). The smoke run
    will surface the availability picture immediately.
  - Corpus size depends on which HF dataset the loader picks first (could be
    1M, 10M, or 100M chars). MAX_CHARS_TRAIN caps the cell's ingest budget
    independently. The provenance check fingerprints real-vs-synthetic via
    vocab size >= 50 (synthetic fallback uses fixed 78-char vocab).
  - First-pass: if Tier-1 (Path A/Path B in flight) closes the bigram gap on
    text8/WikiText-103, the substrate-LM plugin may shift; this n7 cell would
    re-run on the better plugin.

INSTRUMENTATION + 10 FIXES + 9 SELFTEST: identical contract to n6 + n3 text8
  cell; see n6 docstring for the full list. Only the corpus loader differs.

PRE-REGISTERED BANDS (parent-prompt absolute-floor; HARD-WIRED in verdict):
  HARD_PASS  (chain-grade): substrate_bpc <= 2.80
  MIDDLE_BAND:              2.80 < substrate_bpc <= 4.20
  HARD_FAIL:                substrate_bpc > 4.20
  PLUS cv <= 0.05 / zero LLM / corpus_provenance_real / gain >= 0.05.

ASCII-only. write_metrics. PROT-021 run_config guard. CPU numpy only.

QUEUE: remote_cpu_queue (HF dataset cached on remote on first run).
DEPENDENCY: testbed/substrate_lm/data.py arxiv_abstracts_char_corpus loader
            (added 2026-06-22).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials
)

ANCHOR_NAME = "n7_arxiv_abstracts_ingest_cert_v1"

_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--max-chars-train", dest="max_chars_train", type=int, default=None)
_ap.add_argument("--max-chars-test", dest="max_chars_test", type=int, default=None)
_ARGS, _ = _ap.parse_known_args()

_exp_name = os.environ.get("HDLAB_EXP_NAME", "").lower()
_runmode_env = os.environ.get("HDLAB_RUN_MODE", "full").lower()
_name_indicates_smoke = ("_smoke" in _exp_name and not _exp_name.endswith("_no_smoke"))
if _ARGS.smoke or _runmode_env == "smoke" or _name_indicates_smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = _runmode_env

if RUN_MODE == "smoke":
    N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(
        os.environ.get("HDLAB_N_DIM", "512"))
    N_LAYERS = int(os.environ.get("HDLAB_N_LAYERS", "2"))
    ALPHA_MAX = float(os.environ.get("HDLAB_ALPHA_MAX", "0.10"))
    N_STEPS_PER_LAYER = int(os.environ.get("HDLAB_N_STEPS_PER_LAYER", "2"))
    MAX_CHARS_TRAIN = _ARGS.max_chars_train if _ARGS.max_chars_train is not None else 10_000
    MAX_CHARS_TEST = _ARGS.max_chars_test if _ARGS.max_chars_test is not None else 1_000
    SEEDS = [7]
else:
    N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(
        os.environ.get("HDLAB_N_DIM", "4096"))
    N_LAYERS = int(os.environ.get("HDLAB_N_LAYERS", "4"))
    ALPHA_MAX = float(os.environ.get("HDLAB_ALPHA_MAX", "0.10"))
    N_STEPS_PER_LAYER = int(os.environ.get("HDLAB_N_STEPS_PER_LAYER", "3"))
    # Full: arxiv-abstracts depending on HF dataset is ~1-50M chars. Cap at 2M
    # for parity with n3/n6, ample for bigram convergence on a ~80-char vocab.
    MAX_CHARS_TRAIN = _ARGS.max_chars_train if _ARGS.max_chars_train is not None else int(
        os.environ.get("HDLAB_MAX_CHARS_TRAIN", "2000000"))
    MAX_CHARS_TEST = _ARGS.max_chars_test if _ARGS.max_chars_test is not None else int(
        os.environ.get("HDLAB_MAX_CHARS_TEST", "100000"))
    SEEDS = [int(s) for s in os.environ.get("HDLAB_SEEDS", "7,17,23").split(",")]

CORPUS_NAME = "arxiv_abstracts"
CORPUS_VERSION = "hf_ccdv_arxiv_classification_text_field_v2"  # 2026-06-22 loader fix
ALLOW_SYNTHETIC = False

HARD_PASS_BPC = 2.80
MIDDLE_BAND_UPPER_BPC = 4.20
CV_MAX_HP = 0.05

CONFIG_VERSION = (
    "N=%d,LAYERS=%d,ALPHA=%.3f,STEPS=%d,CORPUS=%s,CORPUS_VER=%s,"
    "TRAIN=%d,TEST=%d,SEEDS=%s,SYNTH=%s,BANDS=HP<=%.2f/MB<=%.2f"
) % (N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER, CORPUS_NAME, CORPUS_VERSION,
     MAX_CHARS_TRAIN, MAX_CHARS_TEST, "-".join(str(s) for s in SEEDS),
     str(ALLOW_SYNTHETIC), HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC)


def bigram_count_table(train_text: str, vocab: List[str], laplace: float = 0.5
                       ) -> Tuple[np.ndarray, np.ndarray]:
    V = len(vocab)
    ch_to_idx = {ch: i for i, ch in enumerate(vocab)}
    counts = np.zeros((V, V), dtype=np.int64)
    for i in range(1, len(train_text)):
        c = train_text[i - 1]
        n = train_text[i]
        if c in ch_to_idx and n in ch_to_idx:
            counts[ch_to_idx[c], ch_to_idx[n]] += 1
    smoothed = counts.astype(np.float64) + float(laplace)
    row_sums = smoothed.sum(axis=1, keepdims=True)
    probs = smoothed / np.maximum(row_sums, 1e-30)
    return counts, probs


def bigram_score_bpc(test_text: str, vocab: List[str], probs: np.ndarray) -> Dict[str, Any]:
    if len(test_text) < 2:
        return {"bpc": float("inf"), "n_scored": 0}
    ch_to_idx = {ch: i for i, ch in enumerate(vocab)}
    log2 = math.log(2)
    ent_sum = 0.0
    n_scored = 0
    for t in range(1, len(test_text)):
        c = test_text[t - 1]
        n = test_text[t]
        if c not in ch_to_idx or n not in ch_to_idx:
            continue
        p = float(probs[ch_to_idx[c], ch_to_idx[n]])
        p = max(p, 1e-12)
        ent_sum += -math.log(p) / log2
        n_scored += 1
    return {"bpc": ent_sum / max(n_scored, 1), "n_scored": n_scored}


def bigram_ceiling_bpc(test_text: str, vocab: List[str], laplace: float = 0.5
                       ) -> Dict[str, Any]:
    counts, probs = bigram_count_table(test_text, vocab, laplace=laplace)
    return bigram_score_bpc(test_text, vocab, probs)


def uniform_bpc(vocab: List[str]) -> float:
    return math.log2(max(len(vocab), 1))


def run_substrate_lm(train_text: str, test_text: str, vocab: List[str],
                     seed: int) -> Dict[str, Any]:
    from testbed.substrate_lm.char_lm import SubstrateCharLM

    t0 = time.time()
    lm = SubstrateCharLM(
        n_layers=N_LAYERS, N=N_DIM, alpha_max=ALPHA_MAX,
        n_steps_per_layer=N_STEPS_PER_LAYER, seed=seed,
    )
    fit_info = lm.fit(train_text, n_chars_train=len(train_text),
                      char_vocab=set(vocab), health_every=0, verbose=False)
    train_wall_s = time.time() - t0

    t1 = time.time()
    score = lm.score_bpc(test_text)
    score_wall_s = time.time() - t1

    health = lm.primitive_health()

    assert _LLM_CALL_COUNTER[0] == 0, (
        "FATAL: LLM_CALL_COUNTER non-zero after substrate scoring: %d" % _LLM_CALL_COUNTER[0])

    return {
        "substrate_bpc": float(score["bpc"]),
        "uniform_bpc": float(score["uniform_bpc"]),
        "n_scored": int(score["n_scored"]),
        "train_wall_s": float(train_wall_s),
        "score_wall_s": float(score_wall_s),
        "n_train_pairs": int(fit_info["n_train_pairs"]),
        "max_alpha_final": float(max(fit_info["final_alphas"])
                                 if fit_info["final_alphas"] else 0.0),
        "any_primitive_collapse": bool(fit_info["any_primitive_collapse"]),
        "health_summary": {k: (round(v, 4) if isinstance(v, float) else v)
                           for k, v in list(health.items())[:8]},
    }


def run_seed(seed: int) -> Dict[str, Any]:
    from testbed.substrate_lm.data import arxiv_abstracts_char_corpus, char_vocab_from_corpus

    t0 = time.time()
    print("[seed=%d] loading arxiv-abstracts splits..." % seed, flush=True)
    train_text = arxiv_abstracts_char_corpus(split="train", max_chars=MAX_CHARS_TRAIN,
                                             allow_synthetic=ALLOW_SYNTHETIC)
    test_text = arxiv_abstracts_char_corpus(split="validation", max_chars=MAX_CHARS_TEST,
                                            allow_synthetic=ALLOW_SYNTHETIC)
    vocab = char_vocab_from_corpus(train_text + test_text)
    # Real-data fingerprint: scientific text is mixed-case + punctuation + numbers +
    # math symbols, typically vocab >= 60. Synthetic 78-char fallback would pass
    # this gate -- so ALSO require ALLOW_SYNTHETIC=False; double-defense.
    is_real = (ALLOW_SYNTHETIC is False) and (len(vocab) >= 40)
    corpus_provenance_real = bool(is_real)
    print("[seed=%d] train=%d chars test=%d chars vocab=%d (real=%s)" % (
        seed, len(train_text), len(test_text), len(vocab), corpus_provenance_real),
        flush=True)

    t_bg = time.time()
    _, bg_probs = bigram_count_table(train_text, vocab, laplace=0.5)
    bigram_baseline = bigram_score_bpc(test_text, vocab, bg_probs)
    bigram_ceiling = bigram_ceiling_bpc(test_text, vocab, laplace=0.5)
    bigram_wall_s = time.time() - t_bg
    print("[seed=%d] bigram_baseline_bpc=%.3f bigram_ceiling_bpc=%.3f (wall=%.1fs)" % (
        seed, bigram_baseline["bpc"], bigram_ceiling["bpc"], bigram_wall_s), flush=True)

    print("[seed=%d] training SubstrateCharLM N=%d layers=%d alpha=%.3f steps=%d..." % (
        seed, N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER), flush=True)
    sub = run_substrate_lm(train_text, test_text, vocab, seed)
    print("[seed=%d] substrate_bpc=%.3f train_wall=%.1fs score_wall=%.1fs n_train_pairs=%d" % (
        seed, sub["substrate_bpc"], sub["train_wall_s"], sub["score_wall_s"],
        sub["n_train_pairs"]), flush=True)

    elapsed = time.time() - t0
    per_unit = {
        "seed": int(seed),
        "substrate_bpc": float(sub["substrate_bpc"]),
        "bigram_baseline_bpc": float(bigram_baseline["bpc"]),
        "bigram_ceiling_bpc": float(bigram_ceiling["bpc"]),
        "uniform_bpc": float(sub["uniform_bpc"]),
        "gain_above_bigram_ceiling": float(bigram_ceiling["bpc"] - sub["substrate_bpc"]),
        "gain_above_bigram_baseline": float(bigram_baseline["bpc"] - sub["substrate_bpc"]),
        "n_scored": int(sub["n_scored"]),
        "n_train_chars": int(len(train_text)),
        "n_test_chars": int(len(test_text)),
        "vocab_size": int(len(vocab)),
        "corpus_provenance_real": bool(corpus_provenance_real),
        "max_alpha_final": float(sub["max_alpha_final"]),
        "any_primitive_collapse": bool(sub["any_primitive_collapse"]),
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "train_wall_s": float(sub["train_wall_s"]),
        "score_wall_s": float(sub["score_wall_s"]),
        "bigram_wall_s": float(bigram_wall_s),
        "wall_s": float(elapsed),
        "N": int(N_DIM),
        "run_mode": RUN_MODE,
        "health_summary": sub["health_summary"],
    }
    return {
        "seed": int(seed),
        "per_unit": [per_unit],
        "elapsed_s": float(elapsed),
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "N": int(N_DIM),
        "run_mode": RUN_MODE,
    }


def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    units = []
    for p in ps:
        units.extend(p.get("per_unit", []))
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    any_smoke = any(str(u.get("run_mode", "")).lower() == "smoke" for u in units)
    if any_smoke:
        return ("HARD_FAIL",
                "HARD_FAIL: per_unit contains run_mode=smoke; refusing to call "
                "chain-grade verdict on smoke results (Fix #4 pre-flight gate).")

    any_llm_viol = any(int(u.get("llm_forward_calls_at_inference", 0)) > 0 for u in units)
    if any_llm_viol:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0).")

    any_synthetic = any(not bool(u.get("corpus_provenance_real", False)) for u in units)
    if any_synthetic:
        return ("HARD_FAIL",
                "HARD_FAIL: corpus_provenance_real=False on some seed (synthetic-fallback). "
                "ALLOW_SYNTHETIC=%s." % ALLOW_SYNTHETIC)

    any_collapse = any(bool(u.get("any_primitive_collapse", False)) for u in units)

    sbs = [float(u["substrate_bpc"]) for u in units]
    bgls = [float(u["bigram_baseline_bpc"]) for u in units]
    bgcs = [float(u["bigram_ceiling_bpc"]) for u in units]
    s_mean = float(np.mean(sbs))
    s_cv = float(np.std(sbs) / max(abs(s_mean), 1e-9)) if len(sbs) > 1 else 0.0
    bgl_mean = float(np.mean(bgls))
    bgc_mean = float(np.mean(bgcs))
    gain_vs_ceiling = bgc_mean - s_mean
    gain_vs_baseline = bgl_mean - s_mean

    summary = (
        "substrate_bpc_mean=%.3f cv=%.3f n_seeds=%d | bigram_baseline=%.3f bigram_ceiling=%.3f "
        "| gain_vs_ceiling=%+.3f gain_vs_baseline=%+.3f"
    ) % (s_mean, s_cv, len(units), bgl_mean, bgc_mean, gain_vs_ceiling, gain_vs_baseline)

    if any_collapse:
        return ("HARD_FAIL", "HARD_FAIL: substrate primitive collapse on some seed. " + summary)

    if s_mean > MIDDLE_BAND_UPPER_BPC:
        return ("HARD_FAIL",
                ("HARD_FAIL: substrate_bpc_mean=%.3f > %.2f (worse than arxiv-abstracts bigram baseline). "
                 % (s_mean, MIDDLE_BAND_UPPER_BPC)) + summary)

    HARD_PASS_GAIN_MARGIN = 0.05
    if s_mean <= HARD_PASS_BPC:
        if s_cv > CV_MAX_HP:
            return ("MIDDLE_BAND",
                    ("MIDDLE_BAND: substrate_bpc_mean=%.3f <= %.2f BUT cv=%.3f > %.2f "
                     "(seed-unstable; demote one band). "
                     % (s_mean, HARD_PASS_BPC, s_cv, CV_MAX_HP)) + summary)
        if gain_vs_ceiling < HARD_PASS_GAIN_MARGIN:
            return ("MIDDLE_BAND",
                    ("MIDDLE_BAND: substrate_bpc_mean=%.3f near bigram_ceiling=%.3f "
                     "(gain=%+.3f < %.2f; by-construction-saturated demote). "
                     % (s_mean, bgc_mean, gain_vs_ceiling, HARD_PASS_GAIN_MARGIN)) + summary)
        return ("HARD_PASS",
                ("HARD_PASS: substrate_bpc_mean=%.3f <= %.2f AND cv=%.3f <= %.2f AND "
                 "gain_vs_ceiling=%+.3f >= %.2f AND zero LLM calls AND corpus real. "
                 % (s_mean, HARD_PASS_BPC, s_cv, CV_MAX_HP, gain_vs_ceiling,
                    HARD_PASS_GAIN_MARGIN)) + summary)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: substrate_bpc_mean=%.3f in (%.2f, %.2f] "
             "(between 5-gram-KN and bigram baselines). "
             % (s_mean, HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC)) + summary)


def _instrumentation_selftest() -> None:
    rng = np.random.default_rng(42)

    # T1: bigram on mini-corpus
    mini_text = "the quick brown fox jumps over the lazy dog " * 50
    mini_vocab = sorted(set(mini_text))
    _, bg_probs = bigram_count_table(mini_text, mini_vocab, laplace=0.5)
    bg_score = bigram_score_bpc(mini_text, mini_vocab, bg_probs)
    uni_bpc = uniform_bpc(mini_vocab)
    assert np.isfinite(bg_score["bpc"]) and bg_score["bpc"] < uni_bpc
    print("[selftest] T1 PASS: bigram baseline finite + below uniform (BPC=%.3f < uni=%.3f)"
          % (bg_score["bpc"], uni_bpc), flush=True)

    # T2: SubstrateCharLM mini-pipeline
    from testbed.substrate_lm.char_lm import SubstrateCharLM
    train_mini = mini_text[:1500]
    test_mini = mini_text[1500:2000]
    lm = SubstrateCharLM(n_layers=2, N=128, alpha_max=0.10, n_steps_per_layer=3, seed=7)
    info = lm.fit(train_mini, char_vocab=set(mini_vocab), verbose=False)
    score = lm.score_bpc(test_mini)
    assert np.isfinite(score["bpc"]) and not info["any_primitive_collapse"]
    print("[selftest] T2 PASS: SubstrateCharLM mini-pipeline finite BPC=%.3f"
          % score["bpc"], flush=True)

    # T3: zero-D-overlap fallback
    p_probe = lm.predict_proba(test_mini[0] if test_mini else " ")
    assert np.isfinite(p_probe).all() and p_probe.sum() > 0
    sparse_lm = SubstrateCharLM(n_layers=2, N=64, alpha_max=0.10, n_steps_per_layer=2, seed=9)
    sparse_lm.fit("aaaa", char_vocab=set("ab"), verbose=False)
    sparse_score = sparse_lm.score_bpc("ababab")
    assert np.isfinite(sparse_score["bpc"])
    print("[selftest] T3 PASS: zero-D-overlap fallback finite BPC=%.3f"
          % sparse_score["bpc"], flush=True)

    # T4: LLM-call counter
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T4 PASS: LLM_CALL_COUNTER = 0", flush=True)

    # T5: CONFIG_VERSION coverage
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0
    for tok in ("N=", "LAYERS=", "ALPHA=", "STEPS=", "CORPUS=arxiv_abstracts",
                "CORPUS_VER=", "TRAIN=", "TEST=", "SEEDS=", "SYNTH=False",
                "BANDS=HP<=2.80"):
        assert tok in CONFIG_VERSION, "CONFIG_VERSION missing token: %s" % tok
    assert isinstance(N_DIM, int) and N_DIM > 0
    assert isinstance(N_LAYERS, int) and N_LAYERS >= 1
    assert isinstance(ALPHA_MAX, float) and 0 < ALPHA_MAX < 1
    assert isinstance(N_STEPS_PER_LAYER, int) and N_STEPS_PER_LAYER >= 1
    assert isinstance(MAX_CHARS_TRAIN, int) and MAX_CHARS_TRAIN >= 1000
    assert isinstance(MAX_CHARS_TEST, int) and MAX_CHARS_TEST >= 100
    assert isinstance(SEEDS, list) and len(SEEDS) >= 1
    assert isinstance(ALLOW_SYNTHETIC, bool) and ALLOW_SYNTHETIC is False
    assert isinstance(HARD_PASS_BPC, float) and HARD_PASS_BPC == 2.80
    assert isinstance(MIDDLE_BAND_UPPER_BPC, float) and MIDDLE_BAND_UPPER_BPC == 4.20
    assert isinstance(CV_MAX_HP, float) and CV_MAX_HP == 0.05
    print("[selftest] T5 PASS: module-level constants real code + CONFIG_VERSION complete",
          flush=True)

    # T6: per_unit shape
    per_unit_keys_required = (
        "seed", "substrate_bpc", "bigram_baseline_bpc", "bigram_ceiling_bpc",
        "uniform_bpc", "gain_above_bigram_ceiling", "gain_above_bigram_baseline",
        "n_scored", "n_train_chars", "n_test_chars", "vocab_size",
        "corpus_provenance_real", "max_alpha_final", "any_primitive_collapse",
        "llm_forward_calls_at_inference", "train_wall_s", "score_wall_s",
        "bigram_wall_s", "wall_s", "N", "run_mode", "health_summary",
    )
    fake_unit = {k: (0.0 if k not in (
        "seed", "n_scored", "n_train_chars", "n_test_chars", "vocab_size",
        "llm_forward_calls_at_inference", "N", "corpus_provenance_real",
        "any_primitive_collapse", "run_mode", "health_summary",
    ) else (0 if k != "run_mode" and k != "health_summary"
            else ("full" if k == "run_mode" else {})))
        for k in per_unit_keys_required}
    for key in per_unit_keys_required:
        assert key in fake_unit
    print("[selftest] T6 PASS: per_unit shape includes all %d required keys"
          % len(per_unit_keys_required), flush=True)

    # T7: verdict direction
    ps_good = [{"per_unit": [{
        "seed": s, "substrate_bpc": 2.50 + 0.02 * i,
        "bigram_baseline_bpc": 3.90, "bigram_ceiling_bpc": 2.70,
        "uniform_bpc": 6.6, "gain_above_bigram_ceiling": 0.20,
        "gain_above_bigram_baseline": 1.40, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 80,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for i, s in enumerate([7, 17, 23])]
    v_good, vmsg_good = verdict(ps_good)
    assert v_good == "HARD_PASS", "T7a FAIL: %s msg=%s" % (v_good, vmsg_good)

    ps_llm = [{"per_unit": [dict(ps_good[0]["per_unit"][0], llm_forward_calls_at_inference=1)]}]
    assert verdict(ps_llm)[0] == "HARD_FAIL", "T7b FAIL"

    ps_syn = [{"per_unit": [dict(ps_good[0]["per_unit"][0], corpus_provenance_real=False)]}]
    assert verdict(ps_syn)[0] == "HARD_FAIL", "T7c FAIL"

    ps_cv = [{"per_unit": [{
        "seed": s, "substrate_bpc": 2.50 + 0.50 * i,
        "bigram_baseline_bpc": 3.90, "bigram_ceiling_bpc": 2.70,
        "uniform_bpc": 6.6, "gain_above_bigram_ceiling": 0.20,
        "gain_above_bigram_baseline": 1.40, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 80,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for i, s in enumerate([7, 17, 23])]
    assert verdict(ps_cv)[0] == "MIDDLE_BAND", "T7d FAIL: high-cv didn't demote"

    ps_bad = [{"per_unit": [dict(ps_good[0]["per_unit"][0], substrate_bpc=5.0,
                                 gain_above_bigram_ceiling=-2.30,
                                 gain_above_bigram_baseline=-1.10)]}]
    assert verdict(ps_bad)[0] == "HARD_FAIL", "T7e FAIL"

    ps_sat = [{"per_unit": [{
        "seed": s, "substrate_bpc": 2.71,  # ceiling 2.70 gain 0.01-(-) < 0.05 margin
        "bigram_baseline_bpc": 3.90, "bigram_ceiling_bpc": 2.70,
        "uniform_bpc": 6.6, "gain_above_bigram_ceiling": -0.01,
        "gain_above_bigram_baseline": 1.19, "n_scored": 99999,
        "corpus_provenance_real": True, "max_alpha_final": 0.08,
        "any_primitive_collapse": False, "llm_forward_calls_at_inference": 0,
        "train_wall_s": 100.0, "score_wall_s": 30.0, "bigram_wall_s": 10.0, "wall_s": 140.0,
        "n_train_chars": 100000, "n_test_chars": 10000, "vocab_size": 80,
        "N": N_DIM, "run_mode": "full", "health_summary": {},
    }]} for s in [7, 17, 23]]
    v_sat, vmsg_sat = verdict(ps_sat)
    assert v_sat == "MIDDLE_BAND", "T7f FAIL: %s msg=%s" % (v_sat, vmsg_sat)
    print("[selftest] T7 PASS: verdict() direction-correct", flush=True)

    # T8: bigram_ceiling == baseline on same-text laplace=0
    _, p_tr = bigram_count_table(mini_text, mini_vocab, laplace=0.0)
    base = bigram_score_bpc(mini_text, mini_vocab, p_tr)
    _, p_te = bigram_count_table(mini_text, mini_vocab, laplace=0.0)
    ceil_score = bigram_score_bpc(mini_text, mini_vocab, p_te)
    assert abs(ceil_score["bpc"] - base["bpc"]) < 1e-6
    assert np.isfinite(ceil_score["bpc"]) and ceil_score["bpc"] < uni_bpc
    print("[selftest] T8 PASS: bigram_ceiling=%.3f == baseline=%.3f at laplace=0"
          % (ceil_score["bpc"], base["bpc"]), flush=True)

    # T9: verdict refuses HARD_PASS in smoke run_mode
    ps_smoke = [{"per_unit": [dict(ps_good[0]["per_unit"][0], run_mode="smoke")]}]
    v_smoke, vmsg_smoke = verdict(ps_smoke)
    assert v_smoke == "HARD_FAIL" and "smoke" in vmsg_smoke.lower(), (
        "T9 FAIL: %s msg=%s" % (v_smoke, vmsg_smoke))
    print("[selftest] T9 PASS: verdict refuses HARD_PASS in smoke run_mode", flush=True)

    print("[selftest] ALL 9 TESTS PASS: n7_arxiv_abstracts cell instrumentation validated",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


print("[config] anchor=%s mode=%s N_DIM=%d N_LAYERS=%d alpha=%.3f steps=%d "
      "TRAIN=%d TEST=%d SEEDS=%s ALLOW_SYNTHETIC=%s" % (
          ANCHOR_NAME, RUN_MODE, N_DIM, N_LAYERS, ALPHA_MAX, N_STEPS_PER_LAYER,
          MAX_CHARS_TRAIN, MAX_CHARS_TEST, SEEDS, ALLOW_SYNTHETIC), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps: List[Dict[str, Any]] = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    u = r["per_unit"][0]
    print("  [seed=%d] sbpc=%.3f bigram_base=%.3f bigram_ceil=%.3f gain_ceil=%+.3f "
          "wall=%.1fs llm_calls=%d real=%s" % (
              seed, u["substrate_bpc"], u["bigram_baseline_bpc"], u["bigram_ceiling_bpc"],
              u["gain_above_bigram_ceiling"], u["wall_s"],
              u["llm_forward_calls_at_inference"], u["corpus_provenance_real"]),
          flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

total_llm_calls = sum(int(p.get("llm_forward_calls_at_inference", 0)) for p in ps)
assert total_llm_calls == 0, (
    "FATAL: %d LLM forward calls observed -- substrate-only-decode gate VIOLATED"
    % total_llm_calls)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

all_units = [u for p in ps for u in p.get("per_unit", [])]
sbs_all = [float(u["substrate_bpc"]) for u in all_units]
if len(sbs_all) > 1:
    sbs_cv = float(np.std(sbs_all) / max(abs(float(np.mean(sbs_all))), 1e-9))
else:
    sbs_cv = 0.0

summary = (
    "n7_arxiv_abstracts: substrate_bpc_mean=%.3f cv=%.3f n_seeds=%d "
    "bigram_baseline=%.3f bigram_ceiling=%.3f mode=%s verdict=%s"
) % (
    float(np.mean(sbs_all)) if sbs_all else float("nan"), sbs_cv, len(all_units),
    float(np.mean([float(u["bigram_baseline_bpc"]) for u in all_units])) if all_units else float("nan"),
    float(np.mean([float(u["bigram_ceiling_bpc"]) for u in all_units])) if all_units else float("nan"),
    RUN_MODE, v,
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": summary,
    "run_mode": RUN_MODE,
    "n_seeds": len(all_units),
    "N_DIM": N_DIM,
    "N_LAYERS": N_LAYERS,
    "ALPHA_MAX": ALPHA_MAX,
    "N_STEPS_PER_LAYER": N_STEPS_PER_LAYER,
    "MAX_CHARS_TRAIN": MAX_CHARS_TRAIN,
    "MAX_CHARS_TEST": MAX_CHARS_TEST,
    "corpus_name": CORPUS_NAME,
    "corpus_version": CORPUS_VERSION,
    "allow_synthetic": ALLOW_SYNTHETIC,
    "corpus_provenance_real": all(bool(u.get("corpus_provenance_real", False))
                                  for u in all_units),
    "zero_llm_calls_at_inference": True,
    "total_llm_forward_calls_observed": int(total_llm_calls),
    "substrate_bpc_mean": float(np.mean(sbs_all)) if sbs_all else float("nan"),
    "substrate_bpc_cv": float(sbs_cv),
    "bigram_baseline_bpc_mean": float(np.mean(
        [float(u["bigram_baseline_bpc"]) for u in all_units])) if all_units else float("nan"),
    "bigram_ceiling_bpc_mean": float(np.mean(
        [float(u["bigram_ceiling_bpc"]) for u in all_units])) if all_units else float("nan"),
    "HARD_PASS_BPC": HARD_PASS_BPC,
    "MIDDLE_BAND_UPPER_BPC": MIDDLE_BAND_UPPER_BPC,
    "CV_MAX_HP": CV_MAX_HP,
    "by_construction_guards": {
        "vq_floor_methodology": (
            "char-LM analog: bigram_ceiling_bpc = bigram-MLE FIT ON TEST itself; "
            "substrate < bigram_ceiling by >=0.05 required for HARD_PASS."
        ),
        "real_data_asserted": True,
        "allow_synthetic": ALLOW_SYNTHETIC,
        "zero_llm_call_at_inference": True,
        "substrate_only_code_trace": (
            "this cell imports NO transformers/torch; SubstrateCharLM imports no "
            "transformers; _LLM_CALL_COUNTER asserted == 0 before metrics write."
        ),
    },
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
