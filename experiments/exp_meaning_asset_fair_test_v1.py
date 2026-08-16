"""exp_meaning_asset_fair_test_v1 -- score the BUILT-BUT-UNWIRED meaning assets on the
UNCHANGED encoding-quality instrument.

Pre-reg: preregs/exp_meaning_asset_fair_test_v1.md (bands fixed BEFORE any run).
Parent:  experiments/exp_encoding_quality_instrument_v2.py at 542e1fc0d -- IMPORTED AS A LIBRARY,
         NEVER EDITED. Vocabulary, golds, pools, sigmas, seeds, tie-break, chance baseline and
         every metric function come from that module so the comparison is like-for-like.

WHY: v2 measured the DEFAULT LIVE encoder (sha256 -> bipolar) and found the structure-axis null.
That is true of the default path and NOT true of the project: meaning-bearing encoder assets were
built and left unwired, and v2's own disclosure says they were not scored. A fair test of a WEAK
implementation proves that setup failed, not that the capability is impossible.

ASSETS (native d in brackets):
  ASSET_V2_*        TinyTransformer v2   data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt   [512]
  ASSET_RETRAIN_*   minimal-unfreeze     data/exp_encoder_retrain_persist_v1/ckpt_seed_7.pt           [512]
  CTRL_RANDINIT_*   same arch/tokenizer, UNTRAINED (the STEP C random-init arm)                       [512]
  ASSET_NORMS12     Lancaster + Brysbaert via hdlab/grounded_similarity.py                            [12]
The v3_relobj checkpoint is the WRONG one (correction C6) and is loaded ONLY to assert by sha256
that no arm under test is it.

THREE READ-OUTS per learned checkpoint so "the asset failed" cannot mean "one weak read-out failed":
  _TOKEMB  input-embedding rows of the word's BPE pieces (no transformer)
  _ISOL    mean-pool of contextual reps of the word encoded alone
  _CTX     type vector = mean over up to K_CTX corpus occurrences of the word's OWN token-span
           contextual reps. THE STRONG VERSION; the direct analogue of how P_LIVE_CONCEPT is built.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS          # THE INSTRUMENT, UNCHANGED
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "meaning_asset_fair_test_v1"
CODE_VERSION = "v1.0"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = bool(_ARGS.smoke) or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
RUN_MODE = "smoke" if SMOKE else "full"

# ---- config INHERITED from the instrument (never redefined here) ----
V = INS.V
SEEDS = INS.SEEDS
SIGMAS = INS.SIGMAS
N_SWEEP = INS.N_SWEEP
N_GATE = INS.N_GATE
AP_PROBES = INS.AP_PROBES
CORPUS_BYTES = INS.CORPUS_BYTES
BUNDLE_B = INS.BUNDLE_B
SIGMA_GATE = INS.SIGMA_GATE
K_DISTRACT = INS.K_DISTRACT
CORPUS = INS.CORPUS
SIMLEX = INS.SIMLEX

# ---- this cell's own config ----
K_CTX = 4 if SMOKE else 8          # corpus occurrences per word for the _CTX type vector
CTX_HALFWIN = 10                   # words of context each side of the target occurrence
CTX_BATCH = 128
D_LEARNED = 512                    # native d of the TinyTransformer
D_NORMS = 12                       # native d of the grounding norms
N_BOOT = 2000 if SMOKE else 10000
BOOT_SEED = 20260815

CKPT_V2 = REPO / "data" / "exp_scale_meaning_learn_arc_heldout_v2" / "ckpt_seed_7.pt"
CKPT_RETRAIN = REPO / "data" / "exp_encoder_retrain_persist_v1" / "ckpt_seed_7.pt"
CKPT_V3_WRONG = REPO / "data" / "exp_scale_meaning_learn_arc_heldout_v3_relobj" / "ckpt_seed_7.pt"
SHA_V2 = "a5ed6bec534067cb6a3ab885a3a31ce1b13785ef063da8e75fc56d00c1f317d6"
SHA_V3_WRONG = "f03051248c26a756d09d0076697cb470b477405cbaa289376e4a876bef3cb17a"

BRYSBAERT = REPO / "data" / "grounding_testbed" / "Concreteness_ratings_Brysbaert_et_al_BRM.txt"

# pre-registered bands (prereg section 5)
T_MARGIN_MIN = 0.05                # minimum point margin in rho over the strongest floor
T_REG2_RHO_MAX = 0.10
T_REG2_LIFT_MAX = 1.15
T_REG3_COLLAPSE_RECOV_MAX = 0.05
T_REG4_ORTHO_LIFT_MIN = 3.0
T_BUNDLE_RETAINED_MIN = 0.5

FLOOR_ARMS = ["A_ORTHOGRAPHIC", "A_FREQUENCY"]
REF_ARMS = ["A_RANDOM_IID", "A_COLLAPSE", "P_LIVE_WORD"]

LEARNED_SOURCES = {"V2": CKPT_V2, "RETRAIN": CKPT_RETRAIN, "RANDINIT": CKPT_V2}
LEARNED_VARIANTS = ["TOKEMB", "ISOL", "CTX"]


def learned_arms() -> List[str]:
    out = []
    for src in ("V2", "RETRAIN", "RANDINIT"):
        pre = "CTRL_RANDINIT" if src == "RANDINIT" else f"ASSET_{src}"
        for var in LEARNED_VARIANTS:
            out.append(f"{pre}_{var}")
    return out


def block_arms(d: int) -> List[str]:
    base = FLOOR_ARMS + REF_ARMS
    if d == D_LEARNED:
        arms = learned_arms()
        return base + arms + [a + "_SHUFFLED" for a in arms if a.endswith("_CTX")]
    if d == D_NORMS:
        return base + ["ASSET_NORMS12", "ASSET_NORMS12_SHUFFLED", "CTRL_CONCRETENESS_ONLY"]
    raise SystemExit(f"[fatal] no arm list for d={d}")


D_BLOCKS = [D_LEARNED, D_NORMS]


def config_fp() -> str:
    """Full config fingerprint. Goes into EVERY unit key so a smoke unit can never be reloaded
    by a full run (tools/exp_checkpoint.unit_key ignores N by itself; that file is NOT edited)."""
    cfg = {"code": CODE_VERSION, "mode": RUN_MODE, "V": V, "CORPUS_BYTES": CORPUS_BYTES,
           "N_SWEEP": N_SWEEP, "N_GATE": N_GATE, "SIGMAS": SIGMAS, "AP_PROBES": AP_PROBES,
           "SEEDS": SEEDS, "K_CTX": K_CTX, "CTX_HALFWIN": CTX_HALFWIN, "B": BUNDLE_B}
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


# ----------------------------------------------------------------------------------
# per-probe variants of the instrument's scorers.  COPIES of INS.structure_ap /
# INS.simlex_rho that return the per-item values a paired bootstrap needs.  Self-test 1
# asserts their means equal the instrument's own outputs EXACTLY.
# ----------------------------------------------------------------------------------
def structure_ap_perprobe(codes, labels, n_probe, seed):
    C = INS._l2n(codes)
    v = C.shape[0]
    elig = np.where(labels >= 0)[0]
    if len(elig) == 0:
        return np.array([]), np.array([]), np.array([], dtype=np.int64)
    rng = np.random.default_rng(seed ^ 0xA9)
    m = min(n_probe, len(elig))
    probes = np.sort(rng.choice(elig, size=m, replace=False))
    S = INS._tiebreak(C[probes] @ C.T, rng)
    rrng = np.random.default_rng(seed ^ 0x5A5A)
    aps, rands, kept = [], [], []
    for r, i in enumerate(probes):
        same = (labels == labels[i])
        same[i] = False
        n_same = int(same.sum())
        if n_same == 0:
            continue
        aps.append(INS._ap_one(S[r], same, i, n_same))
        rands.append(float(np.mean([INS._ap_one(rrng.random(v), same, i, n_same)
                                    for _ in range(INS.AP_RAND_REPEATS)])))
        kept.append(int(i))
    return np.array(aps), np.array(rands), np.array(kept, dtype=np.int64)


def simlex_perpair(codes, w2i, pairs):
    cs, gs, names = [], [], []
    for a, b, s in pairs:
        ia, ib = w2i.get(a), w2i.get(b)
        if ia is None or ib is None:
            continue
        cs.append(float(codes[ia] @ codes[ib]))
        gs.append(s)
        names.append(a + "|" + b)
    return np.array(cs), np.array(gs), names


# ----------------------------------------------------------------------------------
# NEW ENCODERS: the floors and the assets
# ----------------------------------------------------------------------------------
def _rbf_lift(vals: np.ndarray, d: int, seed: int, n_centres: int = 64,
              missing: Optional[np.ndarray] = None) -> np.ndarray:
    """Lift a scalar per-word property to d dims: n_centres RBF bumps over the property's range,
    then a FIXED random projection. Zero spelling, zero identity beyond the scalar itself."""
    x = np.asarray(vals, dtype=np.float64)
    finite = np.isfinite(x)
    lo, hi = float(np.min(x[finite])), float(np.max(x[finite]))
    centres = np.linspace(lo, hi, n_centres)
    width = (hi - lo) / max(n_centres - 1, 1) * 1.5 + 1e-9
    A = np.exp(-((x[:, None] - centres[None, :]) / width) ** 2)
    P = np.random.default_rng(seed ^ 0xF7E9).standard_normal((n_centres, d))
    X = (A @ P).astype(np.float32)
    if missing is not None and missing.any():
        g = np.random.default_rng(seed ^ 0x5171)
        X[missing] = 1e-3 * g.standard_normal((int(missing.sum()), d)).astype(np.float32)
    return INS._l2n(X)


def enc_frequency(words, counts, d, seed):
    """A_FREQUENCY: a STANDALONE frequency-only floor. Code is a function of log corpus frequency
    and nothing else."""
    return _rbf_lift(np.log(np.asarray(counts, dtype=np.float64) + 1.0), d, seed)


_BRYS_CACHE: Dict[str, float] = {}


def brysbaert_conc() -> Dict[str, float]:
    if _BRYS_CACHE:
        return _BRYS_CACHE
    with open(BRYSBAERT, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            w = (row.get("Word") or "").strip().lower()
            if not w or " " in w:
                continue
            try:
                _BRYS_CACHE[w] = float(row["Conc.M"])
            except (ValueError, KeyError, TypeError):
                continue
    return _BRYS_CACHE


def enc_concreteness_only(words, d, seed):
    """CTRL_CONCRETENESS_ONLY: the concreteness confound as a standalone arm (STEP C)."""
    tab = brysbaert_conc()
    vals = np.array([tab.get(w, np.nan) for w in words], dtype=np.float64)
    miss = ~np.isfinite(vals)
    med = float(np.nanmedian(vals)) if np.isfinite(vals).any() else 0.0
    vals[miss] = med
    return _rbf_lift(vals, d, seed, missing=miss)


def enc_norms12(words, d, seed):
    """ASSET_NORMS12: the grounding-norms asset, read through its own live module."""
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    X = np.zeros((len(words), 12), dtype=np.float32)
    miss = np.zeros(len(words), dtype=bool)
    for i, w in enumerate(words):
        v = tab.get(w.lower())
        if v is None:
            miss[i] = True
        else:
            X[i] = np.asarray(v, dtype=np.float32)
    g = np.random.default_rng(seed ^ 0x9911)
    X[miss] = 1e-3 * g.standard_normal((int(miss.sum()), 12)).astype(np.float32)
    enc_norms12.last_missing = int(miss.sum())
    return INS._l2n(X)


enc_norms12.last_missing = 0


# ---------------------------- the learned encoder ----------------------------------
class TinyEnc:
    """Loads a v2-family checkpoint (or builds an UNTRAINED twin of it) and produces one static
    code per vocabulary word by three read-outs. Runtime evidence: everything below is obtained by
    importing and running the model, never by reading a doc."""

    def __init__(self, ckpt_path: Path, random_init: bool = False, init_seed: int = 7):
        import torch
        from tokenizers import Tokenizer
        import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base
        self.torch = torch
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        mc = ck["model_cfg"]
        self.cfg = {k: int(v) for k, v in mc.items()}
        self.pad_id = int(mc["pad_id"])
        self.d = int(mc["d_model"])
        self.max_len = int(mc["max_len"])
        if random_init:
            torch.manual_seed(init_seed)
        self.model = base.V2Transformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                        mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        self.random_init = random_init
        if not random_init:
            self.model.load_state_dict(ck["state_dict"])
        self.model.eval()
        self.tok = Tokenizer.from_str(ck["tokenizer_json"])
        self.n_params = int(sum(p.numel() for p in self.model.parameters()))

    # ---- variant 1: static input embedding of the word's BPE pieces
    def tokemb(self, words: Sequence[str]) -> np.ndarray:
        W = self.model.tok_emb.weight.detach().numpy()
        X = np.zeros((len(words), self.d), dtype=np.float32)
        for i, w in enumerate(words):
            ids = [j for j in self.tok.encode(w).ids if j != self.pad_id]
            X[i] = W[ids].mean(axis=0) if ids else 0.0
        return INS._l2n(X)

    # ---- variant 2: contextual reps of the word encoded ALONE
    def isolated(self, words: Sequence[str], batch: int = 256) -> np.ndarray:
        torch = self.torch
        X = np.zeros((len(words), self.d), dtype=np.float32)
        cap = min(16, self.max_len)
        for a in range(0, len(words), batch):
            chunk = words[a:a + batch]
            ids = np.full((len(chunk), cap), self.pad_id, dtype=np.int64)
            for r, w in enumerate(chunk):
                e = self.tok.encode(w).ids[:cap]
                ids[r, :len(e)] = e
            h, pad = self.model.token_reps(torch.from_numpy(ids))
            X[a:a + len(chunk)] = _meanpool(h, pad).numpy()
        return INS._l2n(X)

    # ---- variant 3: THE STRONG VERSION -- type vector from corpus occurrences
    def contextual_type(self, words: Sequence[str], occ: List[Tuple[int, str, int, int]],
                        tag: str = "") -> Tuple[np.ndarray, Dict]:
        torch = self.torch
        acc = np.zeros((len(words), self.d), dtype=np.float64)
        cnt = np.zeros(len(words), dtype=np.int64)
        cap = min(64, self.max_len)
        t0 = time.time()
        n_span_empty = 0
        for a in range(0, len(occ), CTX_BATCH):
            chunk = occ[a:a + CTX_BATCH]
            ids = np.full((len(chunk), cap), self.pad_id, dtype=np.int64)
            offs = []
            for r, (_row, txt, _cs, _ce) in enumerate(chunk):
                e = self.tok.encode(txt)
                ii = e.ids[:cap]
                ids[r, :len(ii)] = ii
                offs.append(e.offsets[:cap])
            h, pad = self.model.token_reps(torch.from_numpy(ids))
            H = h.numpy()
            for r, (row, _txt, cs, ce) in enumerate(chunk):
                sel = [k for k, (x, y) in enumerate(offs[r]) if (x < ce and y > cs and y > x)]
                if not sel:
                    n_span_empty += 1
                    continue
                acc[row] += H[r, sel].mean(axis=0)
                cnt[row] += 1
            if a and (a % (CTX_BATCH * 40) == 0):
                print(f"[ctx{tag}] {a}/{len(occ)} ({time.time() - t0:.0f}s)", flush=True)
        n_zero = int((cnt == 0).sum())
        g = np.random.default_rng(0xC7 ^ len(words))
        out = np.zeros((len(words), self.d), dtype=np.float32)
        nz = cnt > 0
        out[nz] = (acc[nz] / cnt[nz][:, None]).astype(np.float32)
        out[~nz] = 1e-3 * g.standard_normal((int((~nz).sum()), self.d)).astype(np.float32)
        stats = {"n_occurrences": len(occ), "n_words_with_zero_occurrences": n_zero,
                 "mean_occurrences_per_word": float(cnt.mean()),
                 "n_span_resolution_failures": n_span_empty,
                 "elapsed_s": round(time.time() - t0, 1)}
        return INS._l2n(out), stats


def _meanpool(reps, pad):
    keep = (~pad).unsqueeze(-1).float()
    return (reps * keep).sum(1) / keep.sum(1).clamp_min(1.0)


def build_occurrences(words: Sequence[str], k: int) -> Tuple[List[Tuple[int, str, int, int]], Dict]:
    """Deterministic: the FIRST k corpus occurrences of each vocabulary word, as a +-CTX_HALFWIN
    word window with the target's char span inside it. Same corpus and byte budget the instrument
    used to build the vocabulary and the live concept profiles."""
    w2i = {w: i for i, w in enumerate(words)}
    need = np.full(len(words), k, dtype=np.int64)
    occ: List[Tuple[int, str, int, int]] = []
    t0 = time.time()
    with open(CORPUS, "rb") as f:
        raw = f.read(CORPUS_BYTES)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    n_lines = 0
    for line in raw.decode("utf-8", errors="ignore").lower().split("\n"):
        n_lines += 1
        toks = re.findall(r"[a-z]+", line)
        if not toks:
            continue
        hit = [(j, t) for j, t in enumerate(toks) if t in w2i and need[w2i[t]] > 0]
        if not hit:
            continue
        for j, t in hit:
            row = w2i[t]
            if need[row] <= 0:
                continue
            lo = max(0, j - CTX_HALFWIN)
            hi = min(len(toks), j + CTX_HALFWIN + 1)
            win = toks[lo:hi]
            cs = sum(len(x) + 1 for x in win[:j - lo])
            occ.append((row, " ".join(win), cs, cs + len(t)))
            need[row] -= 1
        if not need.any():
            break
    stats = {"corpus": str(CORPUS.relative_to(REPO)).replace("\\", "/"),
             "corpus_bytes": CORPUS_BYTES, "lines_scanned": n_lines,
             "k_requested_per_word": k, "n_occurrences": len(occ),
             "n_words_short_of_k": int((need > 0).sum()), "build_s": round(time.time() - t0, 1)}
    return occ, stats


# ----------------------------------------------------------------------------------
# code construction per arm
# ----------------------------------------------------------------------------------
_ENC_CACHE: Dict[str, np.ndarray] = {}
_CTX_STATS: Dict[str, Dict] = {}
_OCC: Optional[List[Tuple[int, str, int, int]]] = None
_OCC_STATS: Dict = {}


def _occurrences(words):
    global _OCC, _OCC_STATS
    if _OCC is None:
        _OCC, _OCC_STATS = build_occurrences(words, K_CTX)
        print(f"[occ] {_OCC_STATS}", flush=True)
    return _OCC


def learned_codes(src: str, variant: str, words, seed: int) -> np.ndarray:
    key = f"{src}|{variant}"
    if key in _ENC_CACHE:
        return _ENC_CACHE[key]
    enc = TinyEnc(LEARNED_SOURCES[src], random_init=(src == "RANDINIT"), init_seed=7)
    if variant == "TOKEMB":
        X = enc.tokemb(words)
    elif variant == "ISOL":
        X = enc.isolated(words)
    elif variant == "CTX":
        X, st = enc.contextual_type(words, _occurrences(words), tag=":" + src)
        _CTX_STATS[src] = st
        print(f"[ctx:{src}] {st}", flush=True)
    else:
        raise SystemExit(f"[fatal] unknown variant {variant}")
    _ENC_CACHE[key] = X
    return X


def build_codes(arm: str, d: int, seed: int, words, counts, pairs, out_dir):
    if arm in ("A_RANDOM_IID", "A_COLLAPSE", "A_ORTHOGRAPHIC", "P_LIVE_WORD"):
        return INS.build_codes(arm, d, seed, words, pairs, out_dir)[0]
    if arm == "A_FREQUENCY":
        return enc_frequency(words, counts, d, seed)
    if arm == "CTRL_CONCRETENESS_ONLY":
        return enc_concreteness_only(words, d, seed)
    if arm.startswith("ASSET_NORMS12"):
        X = enc_norms12(words, d, seed)
        if arm.endswith("_SHUFFLED"):
            X = X[np.random.default_rng(seed ^ 0xC0FFEE).permutation(len(words))]
        return X
    if arm.startswith("ASSET_") or arm.startswith("CTRL_RANDINIT"):
        core = arm[:-len("_SHUFFLED")] if arm.endswith("_SHUFFLED") else arm
        parts = core.split("_")
        variant = parts[-1]
        src = "RANDINIT" if core.startswith("CTRL_RANDINIT") else parts[1]
        X = learned_codes(src, variant, words, seed)
        if arm.endswith("_SHUFFLED"):
            X = X[np.random.default_rng(seed ^ 0xC0FFEE).permutation(len(words))]
        return X
    raise SystemExit(f"[fatal] unknown arm {arm}")


# ----------------------------------------------------------------------------------
# one (arm, d, seed) unit -- metrics are the INSTRUMENT's, called not copied
# ----------------------------------------------------------------------------------
def run_unit(arm, d, seed, words, counts, ortho_pool, freq_pool, golds, pairs, w2i, out_dir):
    t0 = time.time()
    codes = INS._l2n(build_codes(arm, d, seed, words, counts, pairs, out_dir))
    d_eff = int(codes.shape[1])

    recov = {}
    for n in N_SWEEP:
        if n > len(words):
            continue
        recov[str(n)] = {f"{s:g}": INS.recoverability(codes, n, s, seed) for s in SIGMAS}
    disc = {
        "disc_ortho": {f"{s:g}": INS.discriminability(codes, ortho_pool, s, seed) for s in SIGMAS},
        "disc_freq": {f"{s:g}": INS.discriminability(codes, freq_pool, s, seed) for s in SIGMAS},
    }

    ng = min(N_GATE, len(words))
    onehot = np.eye(len(words), dtype=np.float32)
    signed = INS._l2n(np.sign(codes).astype(np.float32))
    stages = [
        ("S0_ORACLE", INS.recoverability_topb(onehot, ng, SIGMA_GATE, seed, BUNDLE_B)),
        ("S1_ENCODE", INS.recoverability_topb(codes, ng, SIGMA_GATE, seed, BUNDLE_B)),
        ("S2_ENCODE_SIGN", INS.recoverability_topb(signed, ng, SIGMA_GATE, seed, BUNDLE_B)),
        ("S3_BUNDLE", INS.bundle_survival(codes, ng, BUNDLE_B, False, seed)),
        ("S4_BUNDLE_SIGN", INS.bundle_survival(codes, ng, BUNDLE_B, True, seed)),
    ]
    chain, prev = [], None
    for name, acc in stages:
        bits = INS.fano_bits_list(acc, ng, BUNDLE_B) if acc == acc else float("nan")
        chain.append({"stage": name, "accuracy": acc, "info_bits_lower_bound": bits,
                      "criterion": f"top-{BUNDLE_B} of {ng}",
                      "destroyed_bits_vs_prev": (None if prev is None else prev - bits)})
        prev = bits

    struct, per_probe = {}, {}
    for gname, lab in golds.items():
        # per-probe values ONLY; the scalars below are derived from them. Self-test 1 asserts this
        # derivation equals INS.structure_ap to 1e-12, so the scorer is the instrument's.
        a_i, r_i, keep = structure_ap_perprobe(codes, lab, AP_PROBES, seed)
        ap = float(a_i.mean()) if len(a_i) else float("nan")
        ch = float(r_i.mean()) if len(r_i) else float("nan")
        struct[gname] = {"ap": ap, "chance": ch,
                         "lift": (ap / ch if ch > 0 else float("nan")), "n_scored": int(len(a_i))}
        per_probe[gname] = {"ap": a_i.tolist(), "rand": r_i.tolist()}
    rho, n_pairs = INS.simlex_rho(codes, w2i, pairs)
    cs, gs, names = simlex_perpair(codes, w2i, pairs)

    return {
        "arm": arm, "d": d, "seed": seed, "d_eff": d_eff,
        "recoverability": recov,
        "sigma_half_at_N_GATE": INS.sigma_half(recov.get(str(ng), {}), SIGMAS),
        "discriminability": disc, "stage_chain": chain,
        "structure": struct, "simlex_rho": rho, "simlex_pairs_covered": n_pairs,
        "per_probe": per_probe, "simlex_cos": cs.tolist(), "simlex_gold": gs.tolist(),
        "elapsed_s": round(time.time() - t0, 1),
    }


# ----------------------------------------------------------------------------------
# paired bootstrap
# ----------------------------------------------------------------------------------
def _spearman(a, b):
    return INS._spearman(np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64))


def boot_rho_diff(cos_a, cos_b, gold, n_boot=None, seed=BOOT_SEED):
    """Paired bootstrap over the SAME SimLex pairs of rho(a) - rho(b)."""
    n_boot = n_boot or N_BOOT
    cos_a, cos_b, gold = np.asarray(cos_a), np.asarray(cos_b), np.asarray(gold)
    n = len(gold)
    if n < 5:
        return {"point": float("nan"), "ci95": [float("nan")] * 2, "n": n}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    d = np.empty(n_boot)
    for b in range(n_boot):
        j = idx[b]
        d[b] = _spearman(cos_a[j], gold[j]) - _spearman(cos_b[j], gold[j])
    d = d[np.isfinite(d)]
    pt = _spearman(cos_a, gold) - _spearman(cos_b, gold)
    return {"point": float(pt), "ci95": [float(np.percentile(d, 2.5)),
                                         float(np.percentile(d, 97.5))], "n": int(n)}


def boot_rho(cos, gold, n_boot=None, seed=BOOT_SEED):
    n_boot = n_boot or N_BOOT
    cos, gold = np.asarray(cos), np.asarray(gold)
    n = len(gold)
    if n < 5:
        return {"point": float("nan"), "ci95": [float("nan")] * 2, "n": n}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    r = np.array([_spearman(cos[j], gold[j]) for j in idx])
    r = r[np.isfinite(r)]
    return {"point": float(_spearman(cos, gold)),
            "ci95": [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))], "n": int(n)}


def boot_lift_diff(ap_a, rand_a, ap_b, rand_b, n_boot=None, seed=BOOT_SEED):
    """Paired bootstrap over the SHARED probe set of lift(a) - lift(b), lift = mean(ap)/mean(rand)."""
    n_boot = n_boot or N_BOOT
    ap_a, rand_a, ap_b, rand_b = map(np.asarray, (ap_a, rand_a, ap_b, rand_b))
    n = len(ap_a)
    if n < 5 or len(ap_b) != n:
        return {"point": float("nan"), "ci95": [float("nan")] * 2, "n": n}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    la = ap_a[idx].mean(1) / np.maximum(rand_a[idx].mean(1), 1e-12)
    lb = ap_b[idx].mean(1) / np.maximum(rand_b[idx].mean(1), 1e-12)
    d = la - lb
    pt = ap_a.mean() / max(rand_a.mean(), 1e-12) - ap_b.mean() / max(rand_b.mean(), 1e-12)
    return {"point": float(pt), "ci95": [float(np.percentile(d, 2.5)),
                                         float(np.percentile(d, 97.5))], "n": int(n)}


def band(ci) -> str:
    lo, hi = ci
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "UNDEFINED"
    if lo > 0:
        return "ABOVE"
    if hi < 0:
        return "BELOW"
    return "NOT_SEPARATED"


# ----------------------------------------------------------------------------------
# self-tests -- run BEFORE any full run
# ----------------------------------------------------------------------------------
def selftest() -> None:
    print("[selftest] instrument's own formula self-tests ...", flush=True)
    INS.selftest()

    # 1. per-probe scorers reproduce the instrument's scalars EXACTLY
    words = [f"w{i:04d}" for i in range(256)]
    X = INS.enc_random_iid(words, 64, 7)
    lab = np.arange(256) % 8
    ap, ch, lift, ns = INS.structure_ap(X, lab, 64, 7)
    a_i, r_i, keep = structure_ap_perprobe(X, lab, 64, 7)
    assert len(a_i) == ns, f"per-probe count {len(a_i)} != {ns}"
    assert abs(float(a_i.mean()) - ap) < 1e-12, "per-probe AP mean != instrument AP"
    assert abs(float(r_i.mean()) - ch) < 1e-12, "per-probe chance mean != instrument chance"
    assert abs(float(a_i.mean() / r_i.mean()) - lift) < 1e-12, "per-probe lift != instrument lift"

    # 2. per-pair SimLex reproduces the instrument's rho EXACTLY
    pr = [(words[i], words[(i * 7) % 256], float(i % 10)) for i in range(60)]
    w2i = {w: i for i, w in enumerate(words)}
    rho, npair = INS.simlex_rho(X, w2i, pr)
    cs, gs, _ = simlex_perpair(X, w2i, pr)
    assert npair == len(cs), "pair count mismatch"
    assert abs(_spearman(cs, gs) - rho) < 1e-12, "per-pair rho != instrument rho"

    # 3. bootstrap behaves: identical arms -> CI contains 0; separated arms -> CI excludes 0
    g = np.random.default_rng(1)
    gold = g.random(200)
    good = gold + 0.05 * g.standard_normal(200)
    noise = g.standard_normal(200)
    b_same = boot_rho_diff(good, good.copy(), gold, n_boot=400)
    assert band(b_same["ci95"]) == "NOT_SEPARATED", f"identical arms separated: {b_same}"
    b_diff = boot_rho_diff(good, noise, gold, n_boot=400)
    assert band(b_diff["ci95"]) == "ABOVE", f"clearly-better arm not separated: {b_diff}"

    # 4. the frequency floor is a FUNCTION OF FREQUENCY ONLY and is not degenerate
    cnt = np.array([10 ** (3 - 2 * i / 255.0) for i in range(256)])
    F = enc_frequency(words, cnt, 64, 7)
    F2 = enc_frequency([w.upper() for w in words], cnt, 64, 7)
    assert np.allclose(F, F2), "A_FREQUENCY depends on the string -- not frequency-only"
    assert INS.structure_ap(F, INS.gold_freqband(cnt), 64, 7)[2] > 2.0, "freq floor cannot see freq"
    assert INS.recoverability(F, 128, 1.0, 7) > 0.20, "freq floor is degenerate"

    # 5. RIGHT CHECKPOINT (guards correction C6: a prior cell loaded the v3_relobj HARD_FAIL ckpt)
    s2 = sha256_file(CKPT_V2)
    assert s2 == SHA_V2, f"v2 ckpt sha256 {s2} != recorded {SHA_V2}"
    assert s2 != SHA_V3_WRONG, "loaded the v3_relobj checkpoint"
    assert sha256_file(CKPT_V3_WRONG) == SHA_V3_WRONG, "v3 ckpt changed on disk"

    # 6. arms-must-differ: trained vs random-init, and v2 vs retrain
    tw = [f"word{i}" for i in range(32)]
    e_tr = TinyEnc(CKPT_V2)
    e_ri = TinyEnc(CKPT_V2, random_init=True, init_seed=7)
    e_rt = TinyEnc(CKPT_RETRAIN)
    a, b, c = e_tr.tokemb(tw), e_ri.tokemb(tw), e_rt.tokemb(tw)
    assert not np.allclose(a, b), "random-init tokemb == trained tokemb"
    assert np.allclose(a, c), "v2 and retrain tok_emb differ (C5 says they are byte-identical)"
    ia, ib = e_tr.isolated(tw), e_ri.isolated(tw)
    assert not np.allclose(ia, ib), "random-init isolated == trained isolated"
    ir = e_rt.isolated(tw)
    assert not np.allclose(ia, ir), "v2 and retrain isolated reps identical -- wrong ckpt loaded"
    assert e_tr.d == D_LEARNED and e_tr.n_params == 27172864, "unexpected model size"

    # 7. the norms asset is the one on disk
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    assert len(tab) == 36810, f"norms table size {len(tab)} != 36810"
    assert INS._l2n(enc_norms12(["dog", "cat", "zzzznotaword"], 12, 7)).shape == (3, 12)

    # 8. the CTX type vector really is the mean of that word's own occurrence vectors
    occ = [(0, "the quick brown fox", 4, 9), (0, "a quick test", 2, 7), (1, "brown bear", 0, 5)]
    Xc, st = e_tr.contextual_type(["quick", "brown"], occ)
    assert st["n_words_with_zero_occurrences"] == 0, st
    assert abs(st["mean_occurrences_per_word"] - 1.5) < 1e-9, st
    print("[selftest] ALL PASS", flush=True)


# ----------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    if _ARGS.self_test:
        selftest()
        return 0
    selftest()

    out_dir = get_output_dir(ANCHOR_NAME if not SMOKE else ANCHOR_NAME + "_smoke")
    out_dir.mkdir(parents=True, exist_ok=True)
    fp = config_fp()
    print(f"[cfg] mode={RUN_MODE} V={V} seeds={SEEDS} K_CTX={K_CTX} fp={fp}", flush=True)

    words, counts = INS.build_vocab(CORPUS, CORPUS_BYTES, V)
    w2i = {w: i for i, w in enumerate(words)}
    ortho_pool = INS.build_ortho_neighbours(words, K_DISTRACT)
    freq_pool = INS.build_freq_controls(counts, ortho_pool, K_DISTRACT)
    golds = {"GOLD_ORTHO": INS.gold_ortho(words),
             "GOLD_FREQBAND": INS.gold_freqband(counts),
             "GOLD_PLANTED": INS.gold_planted(len(words))}
    pairs = INS.load_simlex(SIMLEX)
    print(f"[vocab] V={len(words)} first={words[0]} last={words[-1]} simlex_rows={len(pairs)}",
          flush=True)

    done = completed_units(str(out_dir))
    units: Dict[str, Dict] = load_units(str(out_dir))
    for d in D_BLOCKS:
        for arm in block_arms(d):
            for seed in SEEDS:
                key = unit_key(ANCHOR_NAME, CODE_VERSION, fp, RUN_MODE, arm, f"d{d}",
                               f"seed{seed}", f"V{V}", f"N{N_GATE}")
                if key in done:
                    continue
                res = run_unit(arm, d, seed, words, counts, ortho_pool, freq_pool, golds, pairs,
                               w2i, out_dir)
                record_unit(str(out_dir), key, res)
                units[key] = res
                print(f"[unit] {arm} d={d} seed={seed} rho={res['simlex_rho']:.4f} "
                      f"ortho_lift={res['structure']['GOLD_ORTHO']['lift']:.3f} "
                      f"({res['elapsed_s']}s)", flush=True)

    # ---------------- aggregate ----------------
    by = {}
    for k, u in units.items():
        if u.get("arm") is None:
            continue
        by.setdefault(int(u["d"]), {}).setdefault(u["arm"], {})[int(u["seed"])] = u

    def agg(d, arm, path, default=float("nan")):
        vals = []
        for s in SEEDS:
            u = by.get(d, {}).get(arm, {}).get(s)
            if u is None:
                continue
            cur = u
            for p in path:
                cur = cur.get(p) if isinstance(cur, dict) else None
                if cur is None:
                    break
            if isinstance(cur, (int, float)) and cur == cur:
                vals.append(float(cur))
        return float(np.mean(vals)) if vals else default

    # ---- REG gates
    reg = []

    def add_reg(gid, claim, observed, op, thr):
        ok = (observed == observed) and ((observed <= thr) if op == "<=" else (observed >= thr))
        reg.append({"gate_id": gid, "claim": claim, "observed": (None if observed != observed
                                                                else float(observed)),
                    "op": op, "threshold": thr, "passed": bool(ok)})

    # REG1: reproduce the PUBLISHED v2 numbers for an instrument arm, exactly.
    # AMENDMENT 2026-08-15 (before any run): FULL-scale only. The published numbers are the mean
    # over SEEDS at V=4096; a smoke run has a different vocabulary and one seed, so the gate is
    # not evaluable there. Recorded as SKIPPED_SMOKE_SCALE, never as a pass.
    pub_path = REPO / "data" / "exp_encoding_quality_instrument_v2" / "metrics.json"
    reg1_detail = {"published_metrics": str(pub_path.relative_to(REPO)).replace("\\", "/")}
    if SMOKE:
        reg1_detail["status"] = "SKIPPED_SMOKE_SCALE"
    else:
        try:
            pub = json.load(open(pub_path, encoding="utf-8"))
            pa = pub["per_arm_by_d"]["256"]["P_LIVE_WORD"]
            rs = [run_unit("P_LIVE_WORD", 256, s, words, counts, ortho_pool, freq_pool, golds,
                           pairs, w2i, out_dir) for s in SEEDS]
            mine_rho = float(np.mean([r["simlex_rho"] for r in rs]))
            deltas = {"simlex_rho": abs(pa["simlex_rho"] - mine_rho)}
            mine_lift = {}
            for g in golds:
                mine_lift[g] = float(np.mean([r["structure"][g]["lift"] for r in rs]))
                deltas["lift_" + g] = abs(pa["structure"][g]["lift"] - mine_lift[g])
            worst = max(deltas.values())
            reg1_detail.update({"deltas": deltas, "n_seeds": len(SEEDS),
                                "published": {"simlex_rho": pa["simlex_rho"],
                                              "GOLD_ORTHO_lift":
                                                  pa["structure"]["GOLD_ORTHO"]["lift"]},
                                "recomputed": {"simlex_rho": mine_rho,
                                               "GOLD_ORTHO_lift": mine_lift["GOLD_ORTHO"]}})
            add_reg("REG1", "P_LIVE_WORD d=256 reproduces published v2 seed-mean (max |delta|)",
                    -worst, ">=", -1e-9)
        except Exception as e:                                # noqa: BLE001 recorded, not swallowed
            reg1_detail["error"] = repr(e)
            add_reg("REG1", "P_LIVE_WORD reproduces published v2 numbers", float("nan"), ">=",
                    -1e-9)

    for d in D_BLOCKS:
        add_reg(f"REG2a_d{d}", f"A_RANDOM_IID |simlex rho| <= {T_REG2_RHO_MAX} at d={d}",
                abs(agg(d, "A_RANDOM_IID", ["simlex_rho"])), "<=", T_REG2_RHO_MAX)
        add_reg(f"REG2b_d{d}", f"A_RANDOM_IID GOLD_ORTHO lift <= {T_REG2_LIFT_MAX} at d={d}",
                agg(d, "A_RANDOM_IID", ["structure", "GOLD_ORTHO", "lift"]), "<=", T_REG2_LIFT_MAX)
        add_reg(f"REG3_d{d}", f"A_COLLAPSE recoverability <= {T_REG3_COLLAPSE_RECOV_MAX} at d={d}",
                agg(d, "A_COLLAPSE", ["recoverability", str(min(N_GATE, V)),
                                      f"{SIGMA_GATE:g}"]), "<=", T_REG3_COLLAPSE_RECOV_MAX)
        add_reg(f"REG4_d{d}", f"A_ORTHOGRAPHIC GOLD_ORTHO lift >= {T_REG4_ORTHO_LIFT_MIN} at d={d}",
                agg(d, "A_ORTHOGRAPHIC", ["structure", "GOLD_ORTHO", "lift"]), ">=",
                T_REG4_ORTHO_LIFT_MIN)

    # REG5/REG6 are asserted in selftest(); record them as observed facts
    add_reg("REG5", "loaded ckpt sha256 == recorded and != v3_relobj", 1.0, ">=", 1.0)
    add_reg("REG6", "CTRL_RANDINIT codes differ from ASSET_V2 codes", 1.0, ">=", 1.0)
    reg_ok = all(r["passed"] for r in reg)

    # ---- per-asset comparison against the strongest floor
    def floors_for(d, arm):
        f = list(FLOOR_ARMS)
        sh = arm + "_SHUFFLED"
        if sh in by.get(d, {}):
            f.append(sh)
        return f

    comparisons = {}
    for d in D_BLOCKS:
        for arm in block_arms(d):
            if not (arm.startswith("ASSET_") or arm.startswith("CTRL_")) or arm.endswith("_SHUFFLED"):
                continue
            u = by.get(d, {}).get(arm, {}).get(SEEDS[0])
            if u is None:
                continue
            fl = floors_for(d, arm)
            # SimLex: pick the strongest floor by point rho, then paired-bootstrap the difference
            f_rho = {f: agg(d, f, ["simlex_rho"]) for f in fl}
            best_f = max(f_rho, key=lambda k: (f_rho[k] if f_rho[k] == f_rho[k] else -9))
            uf = by[d][best_f][SEEDS[0]]
            gold = u["simlex_gold"]
            simlex_cmp = {
                "arm_rho": boot_rho(u["simlex_cos"], gold),
                "strongest_floor": best_f,
                "floor_rho_by_arm": f_rho,
                "diff_vs_strongest_floor": boot_rho_diff(u["simlex_cos"], uf["simlex_cos"], gold),
            }
            simlex_cmp["band"] = band(simlex_cmp["diff_vs_strongest_floor"]["ci95"])
            simlex_cmp["clears_floor"] = bool(
                simlex_cmp["band"] == "ABOVE"
                and simlex_cmp["diff_vs_strongest_floor"]["point"] >= T_MARGIN_MIN)

            gold_cmp = {}
            for g in golds:
                f_lift = {f: agg(d, f, ["structure", g, "lift"]) for f in fl}
                bf = max(f_lift, key=lambda k: (f_lift[k] if f_lift[k] == f_lift[k] else -9))
                ufg = by[d][bf][SEEDS[0]]["per_probe"][g]
                pp = u["per_probe"][g]
                bd = boot_lift_diff(pp["ap"], pp["rand"], ufg["ap"], ufg["rand"])
                gold_cmp[g] = {"arm_lift": agg(d, arm, ["structure", g, "lift"]),
                               "floor_lift_by_arm": f_lift, "strongest_floor": bf,
                               "diff_vs_strongest_floor": bd, "band": band(bd["ci95"])}

            # trained vs random-init (STEP C)
            tvr = None
            if arm.startswith("ASSET_") and arm.split("_")[-1] in LEARNED_VARIANTS and d == D_LEARNED:
                ri = "CTRL_RANDINIT_" + arm.split("_")[-1]
                if ri in by.get(d, {}):
                    uri = by[d][ri][SEEDS[0]]
                    tvr = {"vs": ri,
                           "simlex_diff": boot_rho_diff(u["simlex_cos"], uri["simlex_cos"], gold)}
                    tvr["simlex_band"] = band(tvr["simlex_diff"]["ci95"])

            ch = u["stage_chain"]
            s2b = next(x["info_bits_lower_bound"] for x in ch if x["stage"] == "S2_ENCODE_SIGN")
            s3b = next(x["info_bits_lower_bound"] for x in ch if x["stage"] == "S3_BUNDLE")
            comparisons[f"d{d}|{arm}"] = {
                "arm": arm, "d": d,
                "IDENTITY": {"sigma_half": agg(d, arm, ["sigma_half_at_N_GATE"]),
                             "recoverability_at_N_GATE":
                                 by[d][arm][SEEDS[0]]["recoverability"].get(str(min(N_GATE, V))),
                             "disc_ortho_minus_disc_freq_at_sigma8": (
                                 agg(d, arm, ["discriminability", "disc_freq", "8"])
                                 - agg(d, arm, ["discriminability", "disc_ortho", "8"]))},
                "STRUCTURE_SEMANTIC_SIMLEX": simlex_cmp,
                "STRUCTURE_GOLDS": gold_cmp,
                "BUNDLING": {"bits_before_sum_S2": s2b, "bits_after_sum_S3": s3b,
                             "bits_destroyed_by_the_sum": s2b - s3b,
                             "ceiling_bits": math.log2(min(N_GATE, V) / float(BUNDLE_B)),
                             "retained_ge_half_bit": bool(s3b >= T_BUNDLE_RETAINED_MIN)},
                "TRAINED_VS_RANDOM_INIT": tvr,
            }

    headline_assets = [k for k in comparisons if "|ASSET_" in k]
    any_clears = any(comparisons[k]["STRUCTURE_SEMANTIC_SIMLEX"]["clears_floor"]
                     for k in headline_assets)
    if not reg_ok:
        verdict = "INVALID_VALIDITY_GATE_FAILED"
    elif any_clears:
        verdict = "ASSET_CLEARS_THE_STRONGEST_FLOOR"
    else:
        verdict = "NO_ASSET_CLEARS_THE_STRONGEST_FLOOR"

    per_arm = {}
    for d in D_BLOCKS:
        for arm in block_arms(d):
            if arm not in by.get(d, {}):
                continue
            per_arm[f"d{d}|{arm}"] = {
                "simlex_rho": agg(d, arm, ["simlex_rho"]),
                "simlex_pairs_covered": agg(d, arm, ["simlex_pairs_covered"]),
                "GOLD_ORTHO_lift": agg(d, arm, ["structure", "GOLD_ORTHO", "lift"]),
                "GOLD_FREQBAND_lift": agg(d, arm, ["structure", "GOLD_FREQBAND", "lift"]),
                "GOLD_PLANTED_lift": agg(d, arm, ["structure", "GOLD_PLANTED", "lift"]),
                "sigma_half": agg(d, arm, ["sigma_half_at_N_GATE"]),
                "recov_N_GATE_sigma1": agg(d, arm, ["recoverability", str(min(N_GATE, V)),
                                                    f"{SIGMA_GATE:g}"]),
                "bundling_bits_after_sum": agg(d, arm, ["stage_chain"], float("nan")),
            }
            u0 = by[d][arm][SEEDS[0]]
            per_arm[f"d{d}|{arm}"]["bundling_bits_after_sum"] = next(
                x["info_bits_lower_bound"] for x in u0["stage_chain"] if x["stage"] == "S3_BUNDLE")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "config_fingerprint": fp, "verdict": verdict,
        "verdict_msg": ("Do the built-but-unwired meaning assets clear the strongest floor "
                        "CI-separated on the structure axis? -> " + verdict),
        "instrument": {"module": "experiments/exp_encoding_quality_instrument_v2.py",
                       "commit_at_authoring": "542e1fc0d", "edited": False},
        "config": {"V": V, "SEEDS": SEEDS, "SIGMAS": SIGMAS, "N_SWEEP": N_SWEEP,
                   "N_GATE": N_GATE, "AP_PROBES": AP_PROBES, "CORPUS_BYTES": CORPUS_BYTES,
                   "K_CTX": K_CTX, "CTX_HALFWIN": CTX_HALFWIN, "N_BOOT": N_BOOT,
                   "D_BLOCKS": D_BLOCKS},
        "validity_gates": reg, "validity_gates_all_passed": reg_ok, "REG1_detail": reg1_detail,
        "asset_provenance": {
            "ASSET_V2": {"path": str(CKPT_V2.relative_to(REPO)).replace("\\", "/"),
                         "sha256": SHA_V2, "trained_tokens_per_seed": 121082196,
                         "corpus_tokens": 237700000,
                         "note": "121.1M-token encoder trained on a 237.7M-token corpus"},
            "ASSET_RETRAIN": {"path": str(CKPT_RETRAIN.relative_to(REPO)).replace("\\", "/")},
            "REJECTED_WRONG_CKPT": {"path": str(CKPT_V3_WRONG.relative_to(REPO)).replace("\\", "/"),
                                    "sha256": SHA_V3_WRONG,
                                    "why": "correction C6: HARD_FAIL_ARCHITECTURE_BOUND"},
            "ASSET_NORMS12": {"module": "hdlab/grounded_similarity.py"},
        },
        "occurrence_index": _OCC_STATS, "ctx_build_stats": _CTX_STATS,
        "norms_missing_in_vocab": enc_norms12.last_missing,
        "per_arm": per_arm, "comparisons": comparisons,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print(json.dumps({"verdict": verdict, "validity_gates_all_passed": reg_ok}, indent=1))
    print(f"[done] {out_dir}/metrics.json ({metrics['elapsed_s']}s)", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:                                          # noqa: BLE001 -- printed, not hidden
        import traceback
        traceback.print_exc()
        sys.exit(2)
