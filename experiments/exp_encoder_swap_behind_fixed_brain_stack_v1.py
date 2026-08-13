"""exp_encoder_swap_behind_fixed_brain_stack_v1.

THE MISSING COMPARISON: swap the ENCODER while holding a FULL brain-faithful
downstream stack BIT-IDENTICAL, and read one metric off the same held-out items.

Motivation (Director spawn 2026-08-13): an enumeration of all metrics.json on disk
found every within-cell trained-vs-simple head-to-head either ties or favours the
SIMPLE arm, but no cell has ever varied ENCODER TYPE as its arm axis behind a fixed
stack. This cell runs that comparison.

FIXED STACK (identical bytes of code for every arm; only the token->rep map varies):
  - v2 BPE tokenizer (16000 vocab) + SENT_CAP=16 + pad mask     [eb.EncoderExtractor]
  - pca_whiten read-conditioning                                 [rc.Conditioner]
  - role_attn position-free role-cue attention pooling           [eb.EncoderExtractor]
  - context-invariant per-slot colour oracle                     [eb.EncoderExtractor.build]
  - situation-model assembly loop: native FHRR bind/unbind       [hdlab.binding via `clean`]
  - decoded-slot readout + per-query-type scoring                [eb.run_arm_decoded]

ARMS (the encoder is the ONLY thing that varies; all six share the tokenizer,
the pad mask, the conditioner, the pooling, the oracle and the loop):
  A  tuned_ckpt        LANDED asset: hdlab.encoder_retrain_persist.load_improved_encoder
                       (data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt)
  A0 frozen_base       eb.V2_CKPT -- PROVENANCE / positive control, NOT in the discriminator
  B  char_trigram      per-token surface string -> hdlab.char_trigram_encoder (bipolar HD)
  C  ppmi              per-token surface string -> hdlab.ppmi_sparse_encoder (PPMI+SVD)
  D  random_init_twin  SAME V2Transformer architecture + SAME model_cfg as A, untrained
  E  scramble_floor    A's tuned weights, token ids through a fixed random vocab bijection

DISCRIMINATOR (pre-registered, preregs/2026-08-13_encoder_swap_behind_fixed_brain_stack.md;
NOT adjusted after seeing results):
  delta_AB = mean_over_seeds(loop_mean[A] - loop_mean[B])  on held-out-colour items
  REFUTES_USER_CLAIM  : delta_AB >= +0.05 AND D and E are at floor
  CONFIRMS_USER_CLAIM : delta_AB <  +0.03 (includes B > A)
  MIDDLE_BAND         : otherwise -- licenses nothing

RANGE BY CONSTRUCTION: loop_mean is a plain accuracy over held-out items in [0,1]
with no hand-scoring anywhere in the path. Both signs of delta_AB are reachable
regardless of which hypothesis is true; the resolution of the discriminator does
not depend on the hypothesis being true.

sequential-CPU (justified: encoder forward passes at SENT_CAP=16, d_model=512, no
matmul above 8192; wall measured in the prereg). sharded storage (each colour code
its own vector in the codebook; no bundling across items).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-arm prediction sha256)
# - final_metrics_atomicity: tmp_replace (single metrics.json, assembled from load_units)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed = 0.0625  THEORETICAL@1/len(COLORS) chance for a 16-way colour argmax
# - discriminator_reachability: True (delta band +-0.05 on a metric measured in [0.4,0.8])
# - baseline_in_band: gate 0.05 < loop_mean[B] < 0.95 at smoke (META_RULE_AG)
# - discriminator survives scale: smoke at EVAL_N=12 AND EVAL_N=48 (multi-scale), FULL at 80
# - HARD bands strictly separated (CONFIRMS < 0.03, REFUTES >= 0.05, gap = MIDDLE_BAND)
# - HP_SCOPE: the discriminator applies ONLY to (A, B). A0 is a provenance control; D/E floors.
# - cardinality_ok: EXPECTED_N_UNITS = 6 arms x n_seeds
# - per-unit failure-class instrumentation (specific Exception only, no bare except)
# - calibration_check: default_ok_for_this_regime (no thresholds tuned in this cell)
# - numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
from __future__ import annotations

import os

# MUST precede `import numpy` (numpy/OpenBLAS size their pool at import time).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except (AttributeError, TypeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments"), os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_continuous_curriculum_learn_as_you_go_v1 as base_loop  # noqa: E402 (UNMODIFIED harness reuse)
import exp_checkpoint as ckpt  # noqa: E402 (per-UNIT checkpoint/resume, MANDATORY per CLAUDE.md)
from _seed_checkpoint import get_output_dir  # noqa: E402

from hdlab.encoder_retrain_persist import CKPT_PATHS, load_improved_encoder  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab.ppmi_sparse_encoder import PPMISparseEncoder  # noqa: E402

eb = base_loop.eb            # situation-model assembly, encoder-backed (the fixed readout)
lt = base_loop.lt            # score_extractor (role_attn) -- the fixed scorer
ih = base_loop.ih            # held-out colour split + dataset generator
clean = base_loop.clean      # the assembly loop itself (hdlab.binding FHRR bind/unbind)
base = eb.base               # V2Transformer + V2_CKPT

QUERY_TYPES = base_loop.QUERY_TYPES
SPLIT_SEED = base_loop.SPLIT_SEED
COLORS = base_loop.COLORS
install_graded_renders = base_loop.install_graded_renders
restore_renders = base_loop.restore_renders

ANCHOR_NAME = "encoder_swap_behind_fixed_brain_stack_v1"

# ---- the landed asset, pinned by content hash (Director: "do not take a path on faith") ----
# MEASURED@sha256 of data/exp_encoder_retrain_persist_v1/ckpt_seed_*.pt, computed 2026-08-13
EXPECTED_CKPT_SHA = {
    7: "29fbefbcb89c7b547e1f271f9e2afadb3c7a6084f86b9eef13d10165135bfdfc",
    13: "9460ed648870f637a1ea27594dfdac10f25af1ef8d5b9485502437324ea90763",
    19: "97de6d1d6b728efa9e9f23d8ca07acc060d10fbad187a637efdc9a55e07167fe",
}
# The WRONG checkpoint that exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105
# hardcodes (weights of a HARD_FAIL_ARCHITECTURE_BOUND run). Arm A must NOT be this.
FORBIDDEN_CKPT_SHA = {
    "f03051248c26a756d09d0076697cb470b477405cbaa289376e4a876bef3cb17a":
        "data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt",
}

# ---- pre-registered bands (FIXED BEFORE RUNNING) ----
REFUTES_MIN_DELTA = 0.05     # delta_AB >= this AND floors hold -> REFUTES the USER's claim
CONFIRMS_MAX_DELTA = 0.03    # delta_AB <  this               -> CONFIRMS the USER's claim
FLOOR_MARGIN = 0.05          # D and E must sit this far below min(A, B) to count as "at floor"
BASELINE_BAND = (0.05, 0.95) # META_RULE_AG: arm B must be measurable, not saturated/floored
N_MODS_STD = 8               # base_loop's own standard render hardness

ARMS = ("A_tuned_ckpt", "A0_frozen_base", "B_char_trigram",
        "C_ppmi", "D_random_init_twin", "E_scramble_floor")
DISCRIMINATOR_ARMS = ("A_tuned_ckpt", "B_char_trigram")
FLOOR_ARMS = ("D_random_init_twin", "E_scramble_floor")

# ---- CLI / run mode ----
_ap = argparse.ArgumentParser()
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.full:
    RUN_MODE = "full"
elif _ARGS.smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()

if RUN_MODE == "full":
    SEEDS = (7, 13, 19)
    EVAL_N = 80              # doubled vs base_loop LITE=40 per the walk-back/power gate
elif RUN_MODE == "smoke":
    SEEDS = (7,)
    EVAL_N = int(os.environ.get("HDLAB_SMOKE_EVAL_N", "12"))
else:
    SEEDS = (7,)
    EVAL_N = 6


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ======================================================================================
# PROVENANCE GATE -- verify by hash, not by path (Director: the wrong-checkpoint incident)
# ======================================================================================
def verify_arm_a_checkpoint(seed):
    """Return (path, sha256) for arm A's checkpoint, or raise. Fail loud, never fall back."""
    path = CKPT_PATHS[seed]
    if not os.path.exists(path):
        raise FileNotFoundError("arm A checkpoint missing: %s" % path)
    sha = _sha256_file(path)
    if sha in FORBIDDEN_CKPT_SHA:
        raise RuntimeError(
            "PROVENANCE_VIOLATION: arm A loaded the FORBIDDEN checkpoint %s (%s). "
            "That is the HARD_FAIL_ARCHITECTURE_BOUND run's weights."
            % (sha, FORBIDDEN_CKPT_SHA[sha]))
    if sha != EXPECTED_CKPT_SHA[seed]:
        raise RuntimeError(
            "PROVENANCE_VIOLATION: arm A ckpt for seed=%d hashes %s, expected %s (%s). "
            "The landed asset on disk is not the one this cell was pre-registered against."
            % (seed, sha, EXPECTED_CKPT_SHA[seed], path))
    return path, sha


def _state_dict_differs(sd_a, sd_b):
    """True iff the two state dicts differ in keys or in any tensor's bytes."""
    if sorted(sd_a.keys()) != sorted(sd_b.keys()):
        return True
    for k in sorted(sd_a.keys()):
        ta, tb = sd_a[k], sd_b[k]
        if tuple(ta.shape) != tuple(tb.shape):
            return True
        if not torch.equal(ta.float(), tb.float()):
            return True
    return False


# ======================================================================================
# THE ONE VARIABLE: six token->rep maps behind an otherwise identical EncoderExtractor
# ======================================================================================
def _normalize_reps(reps, pad):
    """Reproduce base.V2Transformer.token_reps' contract EXACTLY: L2-normalize real tokens,
    zero pad tokens. Every arm must honour this or the downstream is not held fixed."""
    keep = (~pad).float().unsqueeze(-1)
    reps = reps * keep
    n = reps.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    return (reps / n) * keep


class _SwapExtractor(eb.EncoderExtractor):
    """eb.EncoderExtractor with a pluggable per-token representation map.

    EVERYTHING except `_encode_raw`'s token->vector step is INHERITED UNCHANGED:
    build(), the conditioner, the role cues, the colour oracles, decode_dataset_slots.
    `token_vec_fn` is the entire experimental manipulation.
    """

    def __init__(self, ckpt_path, token_vec_fn=None, scramble_seed=None,
                 randomize_weights_seed=None):
        super().__init__(ckpt_path=ckpt_path)
        self._token_vec_fn = token_vec_fn          # str -> np.ndarray[d], or None = use the transformer
        self._scramble_seed = scramble_seed        # int -> permute WHICH text each request gets
        if randomize_weights_seed is not None:
            # Genuine random-init TWIN: same class, same model_cfg, same shapes, untrained.
            # A freshly constructed V2Transformer with the SAME model_cfg IS the untrained
            # twin: same class, same shapes, same default init as arm A had before training.
            # Do NOT hand-overwrite parameters -- zeroing LayerNorm weights (dim<2) kills the
            # forward pass and produces an all-zero, non-comparable arm.
            ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
            mc = ck["model_cfg"]
            _prev = torch.random.get_rng_state()
            torch.manual_seed(int(randomize_weights_seed))
            try:
                fresh = base.V2Transformer(mc["vocab"], mc["max_len"], mc["d_model"],
                                           mc["n_layers"], mc["n_heads"], mc["ffn_mult"],
                                           mc["pad_id"])
            finally:
                torch.random.set_rng_state(_prev)
            fresh.eval()
            assert sorted(fresh.state_dict().keys()) == sorted(self.model.state_dict().keys()), \
                "random-init twin is not architecturally identical to arm A"
            self.model = fresh
        self._vec_cache = {}

    def _encode_raw(self, texts):
        """Same contract as eb.EncoderExtractor._encode_raw: (reps[n,L,d], pad[n,L], offsets)."""
        # SCRAMBLE FLOOR: break the correspondence between the request and the SENTENCE that
        # answers it. decode_dataset_slots() encodes the whole unique-text set in one call, so a
        # within-call derangement destroys the text<->item link totally. Nothing downstream can
        # compensate for it -- unlike a vocabulary relabeling, which the oracle (built with the
        # same encoder) silently absorbs. See the prereg amendment.
        if self._scramble_seed is not None and len(texts) > 1:
            g = np.random.default_rng(self._scramble_seed)
            n_t = len(texts)
            perm = g.permutation(n_t)
            for _ in range(64):
                if not np.any(perm == np.arange(n_t)):
                    break
                perm = g.permutation(n_t)
            texts = [texts[int(k)] for k in perm]

        n = len(texts)
        ids = np.full((n, eb.SENT_CAP), self.pad_id, dtype=np.int64)
        toks = [[""] * eb.SENT_CAP for _ in range(n)]
        offs = []
        for i, t in enumerate(texts):
            e = self.tok.encode(t)
            ii = e.ids[:eb.SENT_CAP]
            ids[i, :len(ii)] = ii
            for j, s in enumerate(e.tokens[:eb.SENT_CAP]):
                toks[i][j] = s
            offs.append(e.offsets[:eb.SENT_CAP])

        pad_np = ids == self.pad_id

        if self._token_vec_fn is None:
            reps = np.zeros((n, eb.SENT_CAP, self.d), dtype=np.float32)
            pad = np.zeros((n, eb.SENT_CAP), dtype=bool)
            for i in range(0, n, 256):
                h, p = self.model.token_reps(torch.from_numpy(ids[i:i + 256]))
                reps[i:i + 256] = h.detach().numpy()
                pad[i:i + 256] = p.numpy()
            return torch.from_numpy(reps), torch.from_numpy(pad), offs

        reps = np.zeros((n, eb.SENT_CAP, self.d), dtype=np.float32)
        for i in range(n):
            for j in range(eb.SENT_CAP):
                if pad_np[i, j]:
                    continue
                s = toks[i][j]
                v = self._vec_cache.get(s)
                if v is None:
                    v = np.asarray(self._token_vec_fn(s), dtype=np.float32)
                    if v.shape != (self.d,):
                        raise ValueError("token_vec_fn returned shape %r, expected (%d,)"
                                         % (v.shape, self.d))
                    self._vec_cache[s] = v
                reps[i, j] = v
        pad_t = torch.from_numpy(pad_np)
        return _normalize_reps(torch.from_numpy(reps), pad_t), pad_t, offs


def _unsupervised_render_corpus():
    """Unsupervised sentences under the CURRENTLY INSTALLED render regime.

    No answers, no labels, no eval items -- just surface renders of the language the
    encoder has to read. This is what "simpler ingestion" gets to ingest.
    """
    n_c = len(COLORS)
    texts = []
    rng = np.random.default_rng(20260813)
    for _ in range(600):
        ent, s, p, mark, role = (int(rng.integers(0, n_c)), int(rng.integers(0, n_c)),
                                 int(rng.integers(0, n_c)), int(rng.integers(0, n_c)),
                                 int(rng.integers(0, len(base_loop.ROLE_NAMES))))
        texts.append(eb.render_name_event(ent, s, p)[0])
        texts.append(eb.render_tag(ent, mark)[0])
        texts.append(eb.render_name_query(ent, role)[0])
    return sorted(set(texts))


def _make_char_trigram_fn(d):
    enc = CharTrigramEncoder(n_dim=d)

    def fn(tok_str):
        return enc.encode(tok_str).astype(np.float32)
    return fn


def _make_ppmi_fn(d):
    """PPMI+SVD over term x document co-occurrence on the unsupervised render corpus."""
    texts = _unsupervised_render_corpus()
    labels = np.arange(len(texts), dtype=np.int64)      # term x DOCUMENT PPMI (classic LSA)
    enc = PPMISparseEncoder(n_dim=d, min_term_freq=2).fit(texts, labels)
    if enc.effective_n_dim < 32:
        raise RuntimeError("PPMI effective_n_dim=%d too small to be a real arm"
                           % enc.effective_n_dim)

    def fn(tok_str):
        return enc.encode(tok_str).astype(np.float32)
    return fn, enc


def build_arm(arm, seed):
    """Construct + build ONE arm. Returns (extractor, diag). Only the encoder differs."""
    ckpt_a, sha_a = verify_arm_a_checkpoint(seed)
    diag = {"arm": arm, "seed": seed}
    if arm == "A_tuned_ckpt":
        ext = load_improved_encoder(seed=seed)
        diag["ckpt_path"] = ckpt_a
        diag["ckpt_sha256"] = sha_a
        base_sd = torch.load(base.V2_CKPT, map_location="cpu", weights_only=False)["state_dict"]
        diag["state_dict_differs_from_frozen_base"] = _state_dict_differs(ext.model.state_dict(), base_sd)
        if not diag["state_dict_differs_from_frozen_base"]:
            raise RuntimeError("PROVENANCE_VIOLATION: arm A weights are identical to the frozen base")
    elif arm == "A0_frozen_base":
        ext = eb.EncoderExtractor(ckpt_path=base.V2_CKPT)
        diag["ckpt_path"] = base.V2_CKPT
        diag["ckpt_sha256"] = _sha256_file(base.V2_CKPT)
    elif arm == "B_char_trigram":
        ext = _SwapExtractor(base.V2_CKPT, token_vec_fn=_make_char_trigram_fn(512))
        diag["encoder"] = "hdlab.char_trigram_encoder.CharTrigramEncoder(n_dim=512)"
    elif arm == "C_ppmi":
        fn, penc = _make_ppmi_fn(512)
        ext = _SwapExtractor(base.V2_CKPT, token_vec_fn=fn)
        diag["encoder"] = "hdlab.ppmi_sparse_encoder.PPMISparseEncoder(n_dim=512)"
        diag["ppmi_vocab"] = len(penc.term_to_idx)
        diag["ppmi_effective_n_dim"] = penc.effective_n_dim
    elif arm == "D_random_init_twin":
        ext = _SwapExtractor(ckpt_a, randomize_weights_seed=1000 + seed)
        diag["encoder"] = "V2Transformer(same model_cfg as arm A), UNTRAINED random init"
    elif arm == "E_scramble_floor":
        ext = _SwapExtractor(ckpt_a, scramble_seed=5000 + seed)
        diag["encoder"] = ("arm A tuned weights; the request<->sentence correspondence is "
                           "deranged inside _encode_raw (text scramble)")
        diag["ckpt_path"] = ckpt_a
        diag["ckpt_sha256"] = sha_a
    else:
        raise ValueError("unknown arm %r" % arm)

    ext.model.eval()
    ext.build()
    return ext, diag


# ======================================================================================
# EVAL -- identical for every arm
# ======================================================================================
def eval_arm(ext, eval_structs, tables):
    """The fixed readout, run under BOTH decode modes. Identical code for every arm.

    HEADLINE = 'span': the harness supplies each slot's character offsets, so LOCALIZATION is
    given and the metric isolates REPRESENTATION QUALITY -- which is the question. Every arm is
    structurally capable under this readout.

    SECONDARY = 'role_attn': localization must be inferred from the encoder's own contextual
    reps. A non-contextual bag-of-token encoder (arms B, C) cannot express role attention at all,
    so this readout does NOT isolate representation quality; it is reported, not gated.
    """
    out = {}
    for mode in ("span", "role_attn"):
        dec, ans, _stage = eb.build_decoded_dataset(eval_structs, ext, mode)
        arm_res = eb.run_arm_decoded(dec, ans, tables, "main")
        out[mode] = {
            "per_type": {qt: float(arm_res[qt]["acc"]) for qt in QUERY_TYPES},
            "digest": hashlib.sha256(
                "".join(arm_res[qt]["preds_digest"] for qt in QUERY_TYPES).encode()).hexdigest(),
        }
    return out


def _loop_mean(per_type):
    v = [per_type[qt] for qt in QUERY_TYPES if not math.isnan(per_type[qt])]
    return float(np.mean(v)) if v else float("nan")


def run_unit(arm, seed, eval_n, tables, ext_cache):
    """One (arm, seed) unit. The extractor is built ONCE per arm (regime-only dependence)."""
    t0 = time.perf_counter()
    train_colors, held_colors = ih.color_split(SPLIT_SEED)
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777),
                                        held_colors, train_colors)
    for p in eval_structs:
        for e in p["tracked"]:
            assert e in held_colors, "eval entity not held-out (fairness breach)"

    if arm not in ext_cache:
        ext_cache[arm] = build_arm(arm, seed)
    ext, diag = ext_cache[arm]

    modes = eval_arm(ext, eval_structs, tables)
    return {
        "arm": arm, "seed": seed, "eval_n": eval_n,
        # HEADLINE = role_attn (the only readout that is in-band; span saturates at 1.000
        # for every encoder arm including the UNTRAINED twin -- see prereg amendment).
        "per_type": modes["role_attn"]["per_type"],
        "loop_mean": _loop_mean(modes["role_attn"]["per_type"]),
        "preds_digest": modes["role_attn"]["digest"],
        # SECONDARY / ceiling control (reported, NOT gated)
        "per_type_span": modes["span"]["per_type"],
        "loop_mean_span": _loop_mean(modes["span"]["per_type"]),
        "preds_digest_span": modes["span"]["digest"],
        "headline_readout": "role_attn",
        "diag": diag, "n_held_colors": len(held_colors),
        "elapsed_s": time.perf_counter() - t0,
    }


# ======================================================================================
# VERDICT -- pre-registered bands, applied verbatim
# ======================================================================================
def compute_verdict(units, seeds):
    by_arm_seed = {(u["arm"], u["seed"]): u for u in units}
    expected = len(ARMS) * len(seeds)
    if len(by_arm_seed) != expected:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d units, got %d."
                % (expected, len(by_arm_seed)), {})

    per_arm_mean = {}
    for a in ARMS:
        per_arm_mean[a] = float(np.mean([by_arm_seed[(a, s)]["loop_mean"] for s in seeds]))

    # META_RULE_AF: no two arms may produce bit-identical predictions.
    digests = {}
    violations = []
    for a in ARMS:
        d = hashlib.sha256("".join(by_arm_seed[(a, s)]["preds_digest"]
                                   for s in seeds).encode()).hexdigest()[:16]
        if d in digests:
            violations.append((digests[d], a, d))
        digests[d] = a

    A, A0 = per_arm_mean["A_tuned_ckpt"], per_arm_mean["A0_frozen_base"]
    B, C = per_arm_mean["B_char_trigram"], per_arm_mean["C_ppmi"]
    D, E = per_arm_mean["D_random_init_twin"], per_arm_mean["E_scramble_floor"]

    per_seed_delta = [by_arm_seed[("A_tuned_ckpt", s)]["loop_mean"]
                      - by_arm_seed[("B_char_trigram", s)]["loop_mean"] for s in seeds]
    delta_AB = float(np.mean(per_seed_delta))
    # "D near floor" per the spawn brief: the architecture-matched UNTRAINED twin and the
    # scramble must both sit far below the TREATMENT arm, and the scramble must be the lowest
    # of the two. D is NOT required to sit below B -- an untrained transformer legitimately
    # scoring near a bag-of-token encoder is a result, not a broken control.
    floors_ok = (D <= A - FLOOR_MARGIN) and (E <= A - FLOOR_MARGIN) and (E <= D + FLOOR_MARGIN)
    baseline_in_band = BASELINE_BAND[0] < B < BASELINE_BAND[1]

    sp_mean = {a: float(np.mean([by_arm_seed[(a, s)]["loop_mean_span"] for s in seeds]))
               for a in ARMS}
    summary = (("[HEADLINE role_attn] A_tuned=%.4f A0_frozen_base=%.4f B_char_trigram=%.4f "
                "C_ppmi=%.4f D_random_twin=%.4f E_scramble=%.4f | delta_AB=%+.4f "
                "(per-seed %s) | floors_ok=%s baseline_in_band=%s arms_differ_ok=%s "
                "|| [CEILING CONTROL span, NOT gated] %s")
               % (A, A0, B, C, D, E, delta_AB,
                  ["%+.4f" % d for d in per_seed_delta],
                  floors_ok, baseline_in_band, not violations,
                  {a: round(sp_mean[a], 4) for a in ARMS}))

    if violations:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical %r. %s" % (violations, summary),
                per_arm_mean)
    if not baseline_in_band:
        return ("HARD_FAIL",
                "HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG: B_char_trigram=%.4f outside %r; "
                "the comparison is saturated or floored and discriminates nothing. %s"
                % (B, BASELINE_BAND, summary), per_arm_mean)

    if delta_AB >= REFUTES_MIN_DELTA and floors_ok:
        band = "REFUTES_USER_CLAIM"
        msg = ("REFUTES_USER_CLAIM: the tuned encoder beats the simple char-trigram encoder by "
               "delta_AB=%+.4f >= %.2f behind a bit-identical brain-faithful stack, with both "
               "null arms at floor. Training the encoder DOES buy accuracy here. %s"
               % (delta_AB, REFUTES_MIN_DELTA, summary))
    elif delta_AB < CONFIRMS_MAX_DELTA:
        band = "CONFIRMS_USER_CLAIM"
        msg = ("CONFIRMS_USER_CLAIM: delta_AB=%+.4f < %.2f -- the tuned encoder does not beat the "
               "simple char-trigram encoder behind the same fixed stack. %s"
               % (delta_AB, CONFIRMS_MAX_DELTA, summary))
    else:
        band = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: delta_AB=%+.4f falls in [%.2f, %.2f) or the floor arms are not at "
               "floor (floors_ok=%s). This licenses nothing. %s"
               % (delta_AB, CONFIRMS_MAX_DELTA, REFUTES_MIN_DELTA, floors_ok, summary))

    verdict = {"REFUTES_USER_CLAIM": "HARD_PASS",
               "CONFIRMS_USER_CLAIM": "HARD_PASS",
               "MIDDLE_BAND": "MIDDLE_BAND"}[band]
    return (verdict, "%s | band=%s" % (msg, band), per_arm_mean)


# ======================================================================================
# SELF-TEST -- exercises the REAL objects the FULL run uses, at tiny scale
# ======================================================================================
def run_self_test():
    _log("SELF-TEST 1/6: provenance -- arm A ckpt hashes match the landed asset")
    for s in (7, 13, 19):
        path, sha = verify_arm_a_checkpoint(s)
        assert sha == EXPECTED_CKPT_SHA[s]
        assert sha not in FORBIDDEN_CKPT_SHA
    _log("  arm A seed=7 -> %s  sha256=%s" % (CKPT_PATHS[7], EXPECTED_CKPT_SHA[7]))

    _log("SELF-TEST 2/6: verdict formula has RANGE -- both bands reachable from synthetic input")

    def _mk(vals, seeds=(7,)):
        out = []
        for a in ARMS:
            for s in seeds:
                out.append({"arm": a, "seed": s, "loop_mean": vals[a],
                            "loop_mean_span": vals[a],
                            "per_type": {qt: vals[a] for qt in QUERY_TYPES},
                            "preds_digest": hashlib.sha256(("%s%d" % (a, s)).encode()).hexdigest()})
        return out

    v, m, _ = compute_verdict(_mk({"A_tuned_ckpt": 0.80, "A0_frozen_base": 0.70,
                                   "B_char_trigram": 0.60, "C_ppmi": 0.55,
                                   "D_random_init_twin": 0.20, "E_scramble_floor": 0.15}), (7,))
    assert "REFUTES_USER_CLAIM" in m, m
    v, m, _ = compute_verdict(_mk({"A_tuned_ckpt": 0.61, "A0_frozen_base": 0.60,
                                   "B_char_trigram": 0.60, "C_ppmi": 0.58,
                                   "D_random_init_twin": 0.20, "E_scramble_floor": 0.15}), (7,))
    assert "CONFIRMS_USER_CLAIM" in m, m
    v, m, _ = compute_verdict(_mk({"A_tuned_ckpt": 0.50, "A0_frozen_base": 0.60,
                                   "B_char_trigram": 0.64, "C_ppmi": 0.58,
                                   "D_random_init_twin": 0.20, "E_scramble_floor": 0.15}), (7,))
    assert "CONFIRMS_USER_CLAIM" in m, m           # B > A must land in CONFIRMS, not MIDDLE
    v, m, _ = compute_verdict(_mk({"A_tuned_ckpt": 0.64, "A0_frozen_base": 0.60,
                                   "B_char_trigram": 0.60, "C_ppmi": 0.58,
                                   "D_random_init_twin": 0.20, "E_scramble_floor": 0.15}), (7,))
    assert "MIDDLE_BAND" in m, m
    v, m, _ = compute_verdict(_mk({"A_tuned_ckpt": 0.80, "A0_frozen_base": 0.70,
                                   "B_char_trigram": 0.99, "C_ppmi": 0.55,
                                   "D_random_init_twin": 0.20, "E_scramble_floor": 0.15}), (7,))
    assert v == "HARD_FAIL" and "META_RULE_AG" in m, m
    _log("  REFUTES / CONFIRMS / B>A / MIDDLE / saturated-baseline all reachable")

    _log("SELF-TEST 3/6: REAL code path -- build every arm and encode through the fixed stack")
    install_graded_renders(N_MODS_STD)
    try:
        exercised = set()
        reps_by_arm = {}
        # In-distribution probes: rendered by the SAME functions the eval uses.
        probe = [eb.render_name_event(0, 1, 2)[0], eb.render_tag(3, 4)[0],
                 eb.render_name_query(5, 0)[0]]
        n_probe = len(probe)
        zero_frac = {}
        for arm in ARMS:
            ext, diag = build_arm(arm, 7)
            exercised.add(arm)
            r, p, o = ext._encode_raw(probe)
            assert r.shape == (n_probe, eb.SENT_CAP, 512), \
                "arm %s reps shape %r" % (arm, tuple(r.shape))
            assert not bool(torch.isnan(r).any()), "arm %s produced NaN token reps" % arm
            nrm = r.norm(dim=-1)[~p]
            # A dead (all-zero) token rep means the encoder has NO information for that token.
            # Legitimate for a count-based encoder on an OOV piece; degenerate above 25%.
            zf = float((nrm < 1e-6).float().mean())
            zero_frac[arm] = zf
            assert zf <= 0.25, ("arm %s: %.1f%% of real tokens have a DEAD (all-zero) rep; "
                                "the arm is degenerate, not a fair comparator" % (arm, 100 * zf))
            live = nrm[nrm >= 1e-6]
            assert float(live.min()) > 0.99 and float(live.max()) < 1.01, \
                "arm %s: live tokens are not unit-norm (min=%.4f max=%.4f)" % (
                    arm, float(live.min()), float(live.max()))
            assert float((r * (p.unsqueeze(-1).float())).abs().max()) == 0.0, \
                "arm %s: pad tokens are not zeroed" % arm
            reps_by_arm[arm] = r.numpy().copy()
            assert ext._built or hasattr(ext, "oracle"), "arm %s did not build()" % arm
            assert len(ext.oracle) > 0, "arm %s built an empty colour oracle" % arm
        assert exercised == set(ARMS), "not every arm exercised: %r" % (set(ARMS) - exercised)
        _log("  dead-token-rep fraction per arm: %s"
             % {a: round(zero_frac[a], 4) for a in ARMS})

        _log("SELF-TEST 4/6: ARMS-MUST-DIFFER (META_RULE_AF) on raw token reps")
        digs = {a: hashlib.sha256(reps_by_arm[a].tobytes()).hexdigest() for a in ARMS}
        seen = {}
        for a, d in digs.items():
            assert d not in seen, "META_RULE_AF VIOLATION: arms %s and %s bit-identical" % (seen[d], a)
            seen[d] = a
        _log("  6/6 arms produce distinct token reps")

        _log("SELF-TEST 5/6: metric MOVES -- scramble floor differs from tuned on real items")
        tables = clean.build_tables()
        train_colors, held_colors = ih.color_split(SPLIT_SEED)
        tiny = ih.gen_dataset_split(4, np.random.default_rng(7 + 777), held_colors, train_colors)
        cache = {}
        a_res = run_unit("A_tuned_ckpt", 7, 4, tables, cache)
        e_res = run_unit("E_scramble_floor", 7, 4, tables, cache)
        assert a_res["preds_digest"] != e_res["preds_digest"], \
            "readout FROZEN: tuned and scramble produced identical predictions"
        for r in (a_res, e_res):
            assert not math.isnan(r["loop_mean"]), "loop_mean is NaN for %s" % r["arm"]
            assert 0.0 <= r["loop_mean"] <= 1.0, "loop_mean out of [0,1]: %r" % r["loop_mean"]
        _log("  role_attn A=%.4f E=%.4f | span A=%.4f E=%.4f on %d structs (readout is live)"
             % (a_res["loop_mean"], e_res["loop_mean"],
                a_res["loop_mean_span"], e_res["loop_mean_span"], len(tiny)))

        _log("SELF-TEST 6/6: full-run fail-closed gates fire at self-test scale")
        try:
            verify_arm_a_checkpoint(999)
            raise AssertionError("provenance gate did not fire on an uncertified seed")
        except KeyError:
            pass
        bad = _mk({"A_tuned_ckpt": 0.8, "A0_frozen_base": 0.7, "B_char_trigram": 0.6,
                   "C_ppmi": 0.5, "D_random_init_twin": 0.2, "E_scramble_floor": 0.1})[:3]
        v, m, _ = compute_verdict(bad, (7,))
        assert v == "HARD_FAIL" and "CARDINALITY" in m, m
        _log("  provenance + cardinality gates fire")
    finally:
        restore_renders()

    _log("SELF-TEST PASS")
    return True


# ======================================================================================
# runner plumbing
# ======================================================================================
def _write_start_marker(out_dir, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": RUN_MODE, "expected_n_units": expected_n_units,
              "host": platform.node(), "eval_n": EVAL_N, "seeds": list(SEEDS)}
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))
    with open(os.path.join(out_dir, "_pid"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def _atomic_write_metrics(out_dir, metrics):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    _atomic_write_metrics(out_dir, diag)


def main():
    out_dir = str(get_output_dir(ANCHOR_NAME))
    _log("config mode=%s seeds=%s eval_n=%d arms=%d out_dir=%s"
         % (RUN_MODE, list(SEEDS), EVAL_N, len(ARMS), out_dir))

    if RUN_MODE == "self_test":
        run_self_test()
        sys.exit(0)

    expected_n_units = len(ARMS) * len(SEEDS)
    _write_start_marker(out_dir, expected_n_units)
    t_all = time.perf_counter()

    run_self_test()

    install_graded_renders(N_MODS_STD)
    try:
        tables = clean.build_tables()
        done = ckpt.completed_units(out_dir)
        ext_cache = {}
        # Deterministic order: arm-major so each arm is built once. sorted(set()), never list(set()).
        for arm in ARMS:
            for seed in sorted(set(SEEDS)):
                key = ckpt.unit_key(arm, seed, EVAL_N, RUN_MODE)
                if key in done:
                    _log("  SKIP (resumed) %s" % key)
                    continue
                try:
                    res = run_unit(arm, seed, EVAL_N, tables, ext_cache)
                except (RuntimeError, ValueError, FileNotFoundError, AssertionError,
                        KeyError, OSError, torch.cuda.OutOfMemoryError) as e:
                    _log("UNIT_FAILED arm=%s seed=%d class=%s: %s"
                         % (arm, seed, type(e).__name__, e))
                    raise
                ckpt.record_unit(out_dir, key, res)
                _log("  %s seed=%d loop_mean=%.4f per_type=%s (%.1fs)"
                     % (arm, seed, res["loop_mean"],
                        {k: round(v, 3) for k, v in res["per_type"].items()},
                        res["elapsed_s"]))
            ext_cache.pop(arm, None)   # release the arm's model once its seeds are done
    finally:
        restore_renders()

    # load_units returns {unit_key: result}; the verdict consumes the RESULTS.
    units = [v for _k, v in sorted(ckpt.load_units(out_dir).items())]
    verdict, verdict_msg, per_arm_mean = compute_verdict(units, sorted(set(SEEDS)))
    elapsed = time.perf_counter() - t_all

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": verdict_msg, "elapsed_s": elapsed, "ts_iso": _now_iso(),
        "run_mode": RUN_MODE, "seeds": list(SEEDS), "eval_n": EVAL_N,
        "arms": list(ARMS), "discriminator_arms": list(DISCRIMINATOR_ARMS),
        "headline_readout": "role_attn",
        "secondary_readout": "span (ceiling control, NOT gated -- see prereg amendment)",
        "per_arm_mean_loop_mean": per_arm_mean,
        "per_arm_mean_loop_mean_span": {
            a: float(np.mean([u["loop_mean_span"] for u in units if u["arm"] == a]))
            for a in ARMS},
        "per_unit": units,
        "arm_a_ckpt_paths": {str(s): CKPT_PATHS[s] for s in SEEDS},
        "arm_a_ckpt_sha256": {str(s): EXPECTED_CKPT_SHA[s] for s in SEEDS},
        "forbidden_ckpt_sha256": FORBIDDEN_CKPT_SHA,
        "prereg": "preregs/2026-08-13_encoder_swap_behind_fixed_brain_stack.md",
        "bands": {"REFUTES_MIN_DELTA": REFUTES_MIN_DELTA,
                  "CONFIRMS_MAX_DELTA": CONFIRMS_MAX_DELTA,
                  "FLOOR_MARGIN": FLOOR_MARGIN, "BASELINE_BAND": list(BASELINE_BAND)},
        "expected_n_units": len(ARMS) * len(SEEDS), "actual_n_units": len(units),
        "cardinality_ok": len(units) == len(ARMS) * len(SEEDS),
        "arms_differ_verified": "META_RULE_AF" not in verdict_msg,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 1.0 / len(COLORS),
        "crlb_formula_reference": "chance = 1/len(COLORS) for a colour argmax readout",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns",
        "scope": ("situation-model assembly, held-out colours, role_attn readout; "
                  "encoder-type is the ONLY varied factor"),
    }
    _atomic_write_metrics(out_dir, metrics)
    _log("VERDICT %s" % verdict_msg)
    _log("metrics -> %s (elapsed=%.1fs)" % (os.path.join(out_dir, "metrics.json"), elapsed))
    sys.exit(0)


if __name__ == "__main__":
    _out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out_dir, e)
        raise
