"""exp_hub_spoke_word_representation_v1 -- a word as ONE vector that is internally ADDRESSED.

Pre-registration: preregs/exp_hub_spoke_word_representation_v1.md (written and committed
BEFORE this cell was run). Every threshold below is quoted from section 6 of that file.

WHAT IS MEASURED
  M1 IDENTITY          -- is this still the right word (a random code wins here BY DESIGN)
  M2 STRUCTURE         -- does the geometry carry anything beyond identity, on the BUNDLED
                          vector AND on the UNBOUND meaning spoke, reported as two rows
  M3 BUNDLING SURVIVAL -- bits retained through the spoke bundle at B in {2,3,4,8}, graded
                          vs terminally-signed
  M4 FACET RECOVERY    -- ask the single vector for ONE spoke, score against the word's OWN
                          other spokes (preregs/DRAFT_storage_quality_instrument_v1.md S3,
                          generalised from a store to a word; NOT reinvented)

M1 and M2 are NEVER averaged. A random encoding is near-optimal on identity and at chance on
structure, so a single blended scalar is unfalsifiable.

=====================================================================================
KNOWN DEFECT, FOUND BY THE SMOKE GATE, DISCLOSED AND NOT SILENTLY PATCHED
=====================================================================================
M2 row (b), "structure of the UNBOUND meaning spoke", is DEGENERATE AS PRE-REGISTERED and
its numbers must NOT be read as a second measurement. Reason, and it is mathematical, not a
coding slip: binding by a bipolar +-1 key is an ISOMETRY. For any two word vectors,

    (v_i * k) . (v_j * k)  =  sum_d v_i[d] v_j[d] k[d]^2  =  v_i . v_j     since k[d]^2 = 1

so the unbound vectors have EXACTLY the pairwise cosines the bundle already had. Measured at
smoke: max |cos(bundled) - cos(unbound)| = 2.9e-06 (float32 noise), for both the concatenated
and the single-spoke read-out, which is why `structure_bundled` and `structure_unbound_meaning`
came back identical to 16 digits.

WHAT THIS MEANS, and it is a real finding rather than a bug to hide: **you cannot recover more
semantic structure out of a bundle by unbinding alone.** Unbinding buys you an ADDRESS, not
extra geometry. Any structural gain has to come from the CLEANUP step -- matching the unbound
query against the spoke's own codebook -- which is nonlinear and is what M4 facet recovery
already does at the item level.

THE FIX FOR v2, stated here so it is not invented twice: measure row (b) as
unbind -> cleanup against the meaning-spoke codebook over the vocabulary -> score the
RECOVERED code, not the raw unbound vector. NOT applied here: the fix was identified after the
smoke run and a required tool call was denied before it could be re-verified, so shipping an
unverified change would be worse than shipping a documented defect.
=====================================================================================

THE RULER IS NOT TOUCHED. exp_encoding_quality_instrument_v2 is imported as a module and its
vocabulary, golds, sigmas, seeds, probe counts and scorers are used verbatim. Gate IV9
re-runs a published instrument arm through this harness and requires the published number to
1e-9. Gate IV8 asserts the new binding primitives are bit-identical to the ones
hdlab/role_slot_summarizer.py and hdlab/event_bundle.py already use.

NO EXTERNAL LLM ANYWHERE, at build time or at inference. The spoke sources are a character
n-gram encoder and two published human-rating norm sets.

ASCII-only. CPU. No network. data/foundation/** is never opened.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS      # THE RULER -- imported, never edited
import exp_meaning_asset_fair_test_v1 as FT           # floors + paired bootstrap, never edited
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units
from hdlab.hub_spoke_word import (
    HubSpokeWord, spoke_key, bipolar_bind, bipolar_quantize, run_selftests as HSW_SELFTESTS,
)

ANCHOR_NAME = "hub_spoke_word_representation_v1"
CODE_VERSION = "v1.0"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = bool(_ARGS.smoke) or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
RUN_MODE = "smoke" if SMOKE else "full"

# ---- config INHERITED from the ruler. Nothing here is re-tuned by this cell. ----
V = INS.V
SEEDS = INS.SEEDS
SIGMAS = INS.SIGMAS
D_SWEEP = INS.D_SWEEP
N_GATE = INS.N_GATE
AP_PROBES = INS.AP_PROBES
CORPUS_BYTES = INS.CORPUS_BYTES
K_DISTRACT = INS.K_DISTRACT
HEADLINE_SIGMA = INS.HEADLINE_SIGMA
CORPUS = INS.CORPUS
SIMLEX = INS.SIMLEX
N_BOOT = FT.N_BOOT
BOOT_SEED = FT.BOOT_SEED

# ---- this cell's own pre-registered config (prereg section 3) ----
BUNDLE_SIZES = [2, 3, 4, 8]
# PRE-RUN AMENDMENT A2 (prereg section 9), found by the cell's OWN self-test ST12 BEFORE any
# data run: on the original grid [0, 0.25, 0.5, 1, 2, 4] facet recovery only fell to 0.928 at
# the top, so IV7 ("a metric that cannot go down is not a measurement") would have been
# satisfied by four tied 1.0000 readings -- i.e. vacuously. The grid is widened to where the
# measure must actually collapse. Direction: TIGHTENS -- it makes the saturation gate
# demonstrable instead of degenerate. No threshold changed.
FR_SIGMAS = [0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
CORR_RHOS = [0.25, 0.50, 0.75, 0.90]
SURVIVAL_PROBES = 128 if SMOKE else 512

# ---- pre-registered thresholds (prereg section 6; do not edit) ----
T_IV1_SLOTTED_MIN = 0.99
T_IV2_FLAT_TOL = 0.05
T_IV3_FLOOR_TOL = 0.05
T_IV4_NULL_LIFT_MAX = 1.15
T_IV4_NULL_RHO_MAX = 0.10
T_IV5_NULLCONTENT_FR_MIN = 0.95
T_IV6_FLAT_DELTAKEY_TOL = 0.05
T_IV7_SATURATION_SPEARMAN_MAX = -0.80
T_IV9_REPRO_TOL = 1e-9
T_G1_DELTAKEY_MIN = 0.15
T_G2_NEW_SPOKE_FR_MIN = 0.95
T_G4_BUNDLE_B2_RETAIN_MIN = 0.90

# ---- spokes ----
SP_FORM = "FORM"
SP_SENSORY = "SENSORY"
SP_ACTION = "ACTION"
SP_CONCRETE = "CONCRETE"
SP_MEANING = "MEANING"
SP_VISION = "VISION"

SPOKES4 = (SP_FORM, SP_SENSORY, SP_ACTION, SP_CONCRETE)
SPOKES2 = (SP_FORM, SP_MEANING)
MEANING_SPOKES4 = (SP_SENSORY, SP_ACTION, SP_CONCRETE)

# Lancaster column blocks inside the 12-dim joined norms vector (hdlab/grounded_similarity.py
# SENSORIMOTOR_COLS order + Brysbaert concreteness last).
IDX_PERCEPTUAL = list(range(0, 6))     # Auditory Gustatory Haptic Interoceptive Olfactory Visual
IDX_EFFECTOR = list(range(6, 11))      # Foot_leg Hand_arm Head Mouth Torso
IDX_CONCRETE = [11]

ARMS = [
    "HS4_GRADED", "HS4_SIGNED", "HS2_GRADED", "HS5_EXTENDED",
    "FLAT_SUM", "K_SLOTTED", "N_NULLCONTENT",
    "F_ORTHO", "F_FREQ", "F_SCRAMBLE",
]
FLOOR_ARMS = ["F_ORTHO", "F_FREQ", "F_SCRAMBLE"]
ADDRESSED_ARMS = ["HS4_GRADED", "HS4_SIGNED", "HS2_GRADED", "HS5_EXTENDED", "N_NULLCONTENT",
                  "F_SCRAMBLE"]


def config_fp() -> str:
    """Config fingerprint in EVERY unit key, so a smoke unit can never be reloaded by a full
    run. tools/exp_checkpoint.unit_key ignores config by itself and that file is NOT edited."""
    cfg = {"code": CODE_VERSION, "mode": RUN_MODE, "V": V, "CORPUS_BYTES": CORPUS_BYTES,
           "SEEDS": SEEDS, "SIGMAS": SIGMAS, "D_SWEEP": D_SWEEP, "N_GATE": N_GATE,
           "AP_PROBES": AP_PROBES, "BUNDLE_SIZES": BUNDLE_SIZES, "FR_SIGMAS": FR_SIGMAS,
           "SURVIVAL_PROBES": SURVIVAL_PROBES, "CORR_RHOS": CORR_RHOS}
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------
# shared, expensive, d-independent objects (built once)
# ----------------------------------------------------------------------------------
_SHARED: Dict[str, object] = {}


def shared():
    if _SHARED:
        return _SHARED
    words, counts = INS.build_vocab(CORPUS, CORPUS_BYTES, V)
    w2i = {w: i for i, w in enumerate(words)}
    ortho_pool = INS.build_ortho_neighbours(words, K_DISTRACT)
    freq_pool = INS.build_freq_controls(counts, ortho_pool, K_DISTRACT)
    golds = {"GOLD_ORTHO": INS.gold_ortho(words), "GOLD_FREQBAND": INS.gold_freqband(counts)}
    pairs = [(a, b, s) for a, b, s in INS.load_simlex(SIMLEX) if a in w2i and b in w2i]

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    norms = np.zeros((len(words), 12), dtype=np.float32)
    miss = np.zeros(len(words), dtype=bool)
    for i, w in enumerate(words):
        v = tab.get(w.lower())
        if v is None:
            miss[i] = True
        else:
            norms[i] = np.asarray(v, dtype=np.float32)
    _SHARED.update(words=words, counts=counts, w2i=w2i, ortho_pool=ortho_pool,
                   freq_pool=freq_pool, golds=golds, pairs=pairs, norms=norms,
                   norms_missing=miss)
    return _SHARED


# ----------------------------------------------------------------------------------
# SPOKE CODES -- every spoke is bipolar {-1,+1} at dimension d
# ----------------------------------------------------------------------------------
def _bipolar_rows(tag: str, n: int, d: int, seed: int) -> np.ndarray:
    """Deterministic per-row bipolar codes. Used for UNPOPULATED spokes and null content."""
    out = np.empty((n, d), dtype=np.float32)
    for i in range(n):
        rng = np.random.default_rng(INS._hash_seed(f"{tag}:{i}", seed))
        out[i] = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=d)
    return out


def _simhash(X: np.ndarray, d: int, seed: int, tag: str) -> np.ndarray:
    """Lift a low-dim real profile to d bipolar dims by a fixed random projection then sign.
    SimHash: preserves cosine ordering. The projection is a nuisance seed, not a tuned knob."""
    P = np.random.default_rng(INS._hash_seed(tag, seed)).standard_normal(
        (X.shape[1], d)).astype(np.float32)
    return bipolar_quantize(X @ P)


def spoke_codes(d: int, seed: int) -> Dict[str, np.ndarray]:
    """The real spoke content. FORM is a FORM code and is labelled as such everywhere."""
    S = shared()
    words = S["words"]
    norms = S["norms"]
    miss = S["norms_missing"]
    n = len(words)

    form = bipolar_quantize(INS.enc_orthographic(words, d, seed))          # VWFA-shaped
    unpop = {
        SP_SENSORY: _bipolar_rows("unpop:SENSORY", n, d, seed),
        SP_ACTION: _bipolar_rows("unpop:ACTION", n, d, seed),
        SP_CONCRETE: _bipolar_rows("unpop:CONCRETE", n, d, seed),
        SP_MEANING: _bipolar_rows("unpop:MEANING", n, d, seed),
    }
    out = {SP_FORM: form}
    for name, idx, tag in ((SP_SENSORY, IDX_PERCEPTUAL, "proj:SENSORY"),
                           (SP_ACTION, IDX_EFFECTOR, "proj:ACTION"),
                           (SP_CONCRETE, IDX_CONCRETE, "proj:CONCRETE"),
                           (SP_MEANING, list(range(12)), "proj:MEANING")):
        C = _simhash(norms[:, idx], d, seed, tag)
        C[miss] = unpop[name][miss]        # UNPOPULATED spoke: honest "no content yet"
        out[name] = C
    out[SP_VISION] = _bipolar_rows("unpop:VISION", n, d, seed)   # the extension placeholder
    return out


def corr_spokes(rho: float, n: int, d: int, seed: int, f: int = 4) -> Dict[str, np.ndarray]:
    """X_CORRSTRESS: f spokes per word with a CONTROLLED within-word pairwise cosine ~= rho.
    Built by flipping each bit of a shared base with p = (1-rho)/2. This is the arm that can
    genuinely fail: the adjudicated finding is that summing correlated codes destroys them."""
    p = (1.0 - rho) / 2.0
    rng = np.random.default_rng(INS._hash_seed(f"corr:{rho}", seed))
    base = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(n, d))
    out = {}
    for j in range(f):
        flip = (rng.random((n, d)) < p)
        out[f"C{j}"] = np.where(flip, -base, base).astype(np.float32)
    return out


# ----------------------------------------------------------------------------------
# ARM CONSTRUCTION -- returns (word_vectors, codec_or_None, pool_spokes, spoke_codes_used)
# ----------------------------------------------------------------------------------
def build_arm(arm: str, d: int, seed: int):
    S = shared()
    words = S["words"]
    counts = S["counts"]
    n = len(words)
    sc = spoke_codes(d, seed)

    if arm in ("HS4_GRADED", "HS4_SIGNED"):
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=(arm == "HS4_SIGNED"))
        used = {s: sc[s] for s in SPOKES4}
        return codec.bundle(used), codec, SPOKES4, used

    if arm == "HS2_GRADED":
        codec = HubSpokeWord(d, SPOKES2, seed, quantize=False)
        used = {s: sc[s] for s in SPOKES2}
        return codec.bundle(used), codec, SPOKES2, used

    if arm == "HS5_EXTENDED":
        base = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        codec = base.add_spoke(SP_VISION)             # asserts the four keys are unchanged
        used = {s: sc[s] for s in codec.spokes}
        return codec.bundle(used), codec, codec.spokes, used

    if arm == "FLAT_SUM":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        used = {s: sc[s] for s in SPOKES4}
        return codec.flat_sum(used), codec, SPOKES4, used

    if arm == "K_SLOTTED":
        # one dedicated vector per (word, spoke); no superposition at all. The "word vector"
        # is the stack, and the read-out for spoke s is that spoke's own dedicated slot.
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        used = {s: sc[s] for s in SPOKES4}
        return None, codec, SPOKES4, used

    if arm == "N_NULLCONTENT":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        used = {s: _bipolar_rows(f"null:{s}", n, d, seed) for s in SPOKES4}
        return codec.bundle(used), codec, SPOKES4, used

    if arm == "F_ORTHO":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        used = {s: sc[s] for s in SPOKES4}
        return INS._l2n(INS.enc_orthographic(words, d, seed)), codec, SPOKES4, used

    if arm == "F_FREQ":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        used = {s: sc[s] for s in SPOKES4}
        return FT.enc_frequency(words, counts, d, seed), codec, SPOKES4, used

    if arm == "F_SCRAMBLE":
        codec = HubSpokeWord(d, SPOKES4, seed, quantize=False)
        perm = np.random.default_rng(INS._hash_seed("scramble", seed)).permutation(n)
        used = {SP_FORM: sc[SP_FORM]}
        for s in MEANING_SPOKES4:
            used[s] = sc[s][perm]          # meaning destroyed; identity/norms/marginals kept
        return codec.bundle(used), codec, SPOKES4, used

    raise KeyError(f"unknown arm {arm!r}")


# ----------------------------------------------------------------------------------
# M4 -- FACET RECOVERY (the within-item discriminator, reused from the storage spec S3)
# ----------------------------------------------------------------------------------
def facet_recovery(vecs, codec: HubSpokeWord, pool_spokes, used: Dict[str, np.ndarray],
                   arm: str, seed: int, key_perm: Optional[Sequence[int]] = None,
                   sigma: float = 0.0, return_per_word: bool = False):
    """Ask the single word vector for ONE spoke; score against the word's OWN other spokes.

    Chance is exactly 1/F. A read-out that cannot vary with the spoke asked for scores at
    chance BY CONSTRUCTION -- which is precisely what 'no address' means.
    """
    F = len(pool_spokes)
    pool = np.stack([INS._l2n(used[s]) for s in pool_spokes], 0)       # (F, n, d)
    n = pool.shape[1]
    rng = np.random.default_rng(INS._hash_seed(f"fr:{arm}:{sigma}:{key_perm is not None}", seed))
    hits = np.zeros(n, dtype=np.float64)
    for si, s in enumerate(pool_spokes):
        if arm == "K_SLOTTED":
            q = used[s].astype(np.float32).copy()      # its own dedicated slot; no unbinding
        else:
            v = vecs.astype(np.float32)
            if sigma > 0.0:
                nz = rng.standard_normal(v.shape).astype(np.float32)
                nz /= (np.linalg.norm(nz, axis=1, keepdims=True) + 1e-8)
                v = INS._l2n(v) + sigma * nz
            read_key = pool_spokes[key_perm[si]] if key_perm is not None else s
            q = codec.ask_for(v, read_key)
        q = INS._l2n(q)
        sims = np.einsum("fnd,nd->nf", pool, q)
        sims = sims + rng.random(sims.shape) * 1e-12          # INS tiebreak convention
        hits += (np.argmax(sims, axis=1) == si).astype(np.float64)
    per_word = hits / float(F)
    if return_per_word:
        return per_word
    return float(per_word.mean())


def derangement(f: int, seed: int) -> List[int]:
    """A permutation with no fixed point -- the shuffled-key read-out for delta_key."""
    rng = np.random.default_rng(INS._hash_seed("derange", seed))
    for _ in range(10000):
        p = list(rng.permutation(f))
        if all(p[i] != i for i in range(f)):
            return p
    return [(i + 1) % f for i in range(f)]


def boot_mean(per_word: np.ndarray, n_boot: int = None, seed: int = BOOT_SEED) -> dict:
    n_boot = n_boot or N_BOOT
    x = np.asarray(per_word, dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    m = x[idx].mean(1)
    return {"point": float(x.mean()),
            "ci95": [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))],
            "n": int(len(x))}


def boot_diff(a: np.ndarray, b: np.ndarray, n_boot: int = None, seed: int = BOOT_SEED) -> dict:
    """PAIRED bootstrap over the SAME words of mean(a) - mean(b)."""
    n_boot = n_boot or N_BOOT
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    dm = a[idx].mean(1) - b[idx].mean(1)
    return {"point": float(a.mean() - b.mean()),
            "ci95": [float(np.percentile(dm, 2.5)), float(np.percentile(dm, 97.5))],
            "n": int(len(a))}


# ----------------------------------------------------------------------------------
# M3 -- BUNDLING SURVIVAL of the SPOKE bundle (bits retained through the sum)
# ----------------------------------------------------------------------------------
def spoke_bundle_survival(base_codes: np.ndarray, b: int, sign_it: bool, d: int, seed: int,
                          n_store: int, n_probe: int) -> Tuple[float, float]:
    """Bundle b bound spoke terms, unbind one, clean up against the FULL n_store codebook.

    Returns (top1 accuracy, Fano lower bound on bits retained). Spokes beyond the four real
    ones are SYNTHETIC extra spokes so the B curve can be extended honestly to 8.
    """
    rng = np.random.default_rng(INS._hash_seed(f"sbs:{b}:{sign_it}", seed))
    names = [f"S{j}" for j in range(b)]
    keys = np.stack([spoke_key(nm, d, seed) for nm in names], 0)          # (b, d)
    store = INS._l2n(base_codes[:n_store])                                # cleanup codebook
    m = min(n_probe, n_store)
    probe_idx = np.sort(rng.choice(n_store, size=m, replace=False))
    # each probe word gets b spoke fillers: its own code in the queried slot, other words'
    # codes in the remaining slots (independent draws, so the bundle is a real superposition)
    hits = 0
    tot = 0
    for slot in range(b):
        others = rng.integers(0, n_store, size=(m, b))
        others[:, slot] = probe_idx
        acc = np.zeros((m, d), dtype=np.float32)
        for j in range(b):
            acc += store[others[:, j]] * keys[j][None, :]
        if sign_it:
            acc = bipolar_quantize(acc)
        q = INS._l2n(acc * keys[slot][None, :])
        sims = q @ store.T
        sims = sims + rng.random(sims.shape) * 1e-12
        hits += int(np.sum(np.argmax(sims, axis=1) == probe_idx))
        tot += m
    p = hits / float(tot)
    return p, INS.fano_bits(p, n_store)


# ----------------------------------------------------------------------------------
# ONE UNIT = (arm, d, seed)
# ----------------------------------------------------------------------------------
def run_unit(arm: str, d: int, seed: int) -> dict:
    S = shared()
    words = S["words"]
    w2i = S["w2i"]
    pairs = S["pairs"]
    golds = S["golds"]
    t0 = time.time()

    vecs, codec, pool_spokes, used = build_arm(arm, d, seed)
    F = len(pool_spokes)
    chance = 1.0 / F
    res: Dict[str, object] = {"arm": arm, "d": d, "seed": seed, "F": F, "chance": chance,
                              "spokes": list(pool_spokes)}

    # ---------- M4 FACET RECOVERY (+ key sensitivity + saturation) ----------
    pw = facet_recovery(vecs, codec, pool_spokes, used, arm, seed, return_per_word=True)
    res["facet_recovery"] = boot_mean(pw)
    perm = derangement(F, seed)
    pw_shuf = facet_recovery(vecs, codec, pool_spokes, used, arm, seed, key_perm=perm,
                             return_per_word=True)
    res["facet_recovery_shuffled_key"] = boot_mean(pw_shuf)
    res["delta_key"] = boot_diff(pw, pw_shuf)
    if arm in ("HS4_GRADED", "FLAT_SUM", "K_SLOTTED"):
        curve = {}
        for sg in FR_SIGMAS:
            curve[f"{sg:g}"] = facet_recovery(vecs, codec, pool_spokes, used, arm, seed,
                                              sigma=sg)
        res["facet_recovery_vs_sigma"] = curve
        ys = [curve[f"{sg:g}"] for sg in FR_SIGMAS]
        res["saturation_spearman"] = INS._spearman(np.arange(len(ys), dtype=np.float64),
                                                   np.array(ys, dtype=np.float64))
    # covered-words-only diagnostic (words that actually have norms)
    cov = ~S["norms_missing"]
    res["facet_recovery_norms_covered_only"] = float(pw[cov].mean()) if cov.any() else float("nan")
    res["norms_coverage"] = float(cov.mean())

    # ---------- the vector a downstream consumer would see ----------
    if arm == "K_SLOTTED":
        # no single vector exists; the honest downstream view of a slotted store is the
        # concatenation of its slots. Labelled, not silently substituted.
        view = INS._l2n(np.concatenate([used[s] for s in pool_spokes], axis=1))
        res["downstream_view"] = "concatenated slots (no single vector exists for this arm)"
    else:
        view = INS._l2n(vecs)
        res["downstream_view"] = "the single bundled word vector"

    # ---------- M1 IDENTITY ----------
    recov = {f"{s:g}": INS.recoverability(view, min(N_GATE, len(words)), s, seed)
             for s in SIGMAS}
    res["recoverability"] = recov
    res["sigma_half"] = INS.sigma_half(recov, SIGMAS)
    res["disc_ortho"] = INS.discriminability(view, S["ortho_pool"], HEADLINE_SIGMA, seed)
    res["disc_freq"] = INS.discriminability(view, S["freq_pool"], HEADLINE_SIGMA, seed)

    # ---------- M2 STRUCTURE, on TWO vectors, reported as two rows ----------
    def struct_block(X):
        X = INS._l2n(X)
        out = {}
        for gname, lab in golds.items():
            ap, ch, lift, npr = INS.structure_ap(X, lab, AP_PROBES, seed)
            out[gname] = {"ap": ap, "chance": ch, "lift": lift, "n_probes": npr}
        rho, npairs = INS.simlex_rho(X, w2i, pairs)
        cs, gs, _ = FT.simlex_perpair(X, w2i, pairs)
        out["simlex"] = {"rho": rho, "n_pairs": npairs}
        return out, cs, gs

    res["structure_bundled"], cs_bundled, gold_pairs = struct_block(view)
    res["_percos_bundled"] = cs_bundled.tolist()

    if arm in ADDRESSED_ARMS or arm == "FLAT_SUM":
        ms = [s for s in pool_spokes if s in (SP_SENSORY, SP_ACTION, SP_CONCRETE, SP_MEANING)]
        if ms:
            asked = np.concatenate([codec.ask_for(vecs, s) for s in ms], axis=1)
            res["structure_unbound_meaning"], cs_unb, _ = struct_block(asked)
            res["_percos_unbound"] = cs_unb.tolist()
            res["unbound_meaning_spokes"] = ms
            per_spoke = {}
            for s in ms:
                blk, _, _ = struct_block(codec.ask_for(vecs, s))
                per_spoke[s] = {"simlex_rho": blk["simlex"]["rho"],
                                "GOLD_ORTHO_lift": blk["GOLD_ORTHO"]["lift"]}
            res["structure_unbound_per_spoke_DIAGNOSTIC"] = per_spoke
            # what the spoke code carries BEFORE bundling -- the ceiling the bundle could hit
            direct = np.concatenate([used[s] for s in ms], axis=1)
            blk, cs_dir, _ = struct_block(direct)
            res["structure_direct_spoke_codes"] = blk
            res["_percos_direct"] = cs_dir.tolist()

    # ---------- M3 BUNDLING SURVIVAL of the spoke bundle ----------
    if arm == "HS4_GRADED":
        surv = {}
        n_store = min(N_GATE, len(words))
        for b in BUNDLE_SIZES:
            for sgn in (False, True):
                p, bits = spoke_bundle_survival(used[SP_FORM], b, sgn, d, seed, n_store,
                                                SURVIVAL_PROBES)
                surv[f"B{b}_{'SIGNED' if sgn else 'GRADED'}"] = {
                    "top1": p, "bits": bits, "ceiling_bits": math.log2(n_store),
                    "retained_frac": bits / math.log2(n_store)}
        res["spoke_bundle_survival"] = surv
        # store-level diagnostic: superposing DIFFERENT WORDS' hub-spoke vectors. NOT the
        # storage instrument; reported so nobody reads M3 as a store result.
        res["word_level_bundle_survival_DIAGNOSTIC"] = {
            f"B{b}_{'SIGNED' if sgn else 'GRADED'}":
                INS.bundle_survival(view, min(N_GATE, len(words)), b, sgn, seed)
            for b in (2, 4, 8) for sgn in (False, True)}

    res["elapsed_s"] = time.time() - t0
    return res


# ----------------------------------------------------------------------------------
# X_CORRSTRESS -- does addressing survive CORRELATED facets (diagnostic sweep)
# ----------------------------------------------------------------------------------
def run_corrstress(d: int, seed: int) -> dict:
    n = min(1024, V)
    out = {}
    for rho in CORR_RHOS:
        codes = corr_spokes(rho, n, d, seed)
        names = tuple(sorted(codes.keys()))
        codec = HubSpokeWord(d, names, seed, quantize=False)
        vecs = codec.bundle(codes)
        pw = facet_recovery(vecs, codec, names, codes, "X_CORRSTRESS", seed,
                            return_per_word=True)
        meas = float(np.mean([float(INS._l2n(codes[names[0]])[i] @ INS._l2n(codes[names[1]])[i])
                              for i in range(min(256, n))]))
        # LABEL CORRECTION (no numeric change): two INDEPENDENTLY flipped copies of a shared
        # base have E[cos] = (1-2p)^2, not (1-2p). The parameter below is the flip parameter
        # (1-2p); the MEASURED within-word cosine is the number to read, and it is what every
        # statement about this sweep uses. The smoke metrics.json on disk still carries the
        # old key name "target_within_word_cos" for this same quantity.
        out[f"rho{rho:g}"] = {"nominal_flip_parameter_1_minus_2p": rho,
                              "measured_within_word_cos": meas,
                              "facet_recovery": boot_mean(pw)}
    return out


# ----------------------------------------------------------------------------------
# G2 -- EXTENSION WITHOUT INVALIDATION (the owner's first-class constraint)
# ----------------------------------------------------------------------------------
def run_extension_proof(d: int, seed: int) -> dict:
    sc = spoke_codes(d, seed)
    base = HubSpokeWord(d, SPOKES4, seed, quantize=False)
    used4 = {s: sc[s] for s in SPOKES4}
    stored = base.bundle(used4)                                    # written BEFORE extension
    fr_before = facet_recovery(stored, base, SPOKES4, used4, "HS4_GRADED", seed,
                               return_per_word=True)
    keys_before = {s: base.key(s).copy() for s in SPOKES4}

    ext = base.add_spoke(SP_VISION)
    keys_identical = all(np.array_equal(ext.key(s), keys_before[s]) for s in SPOKES4)
    # (b) the SAME already-written vectors, read through the EXTENDED codec
    fr_after = facet_recovery(stored, ext, SPOKES4, used4, "HS4_GRADED", seed,
                              return_per_word=True)
    answers_identical = bool(np.array_equal(fr_before, fr_after))
    # (c) newly-written 5-spoke vectors still answer the four ORIGINAL spokes
    used5 = {s: sc[s] for s in ext.spokes}
    new_vecs = ext.bundle(used5)
    pw5_all = facet_recovery(new_vecs, ext, ext.spokes, used5, "HS5_EXTENDED", seed,
                             return_per_word=True)
    F5 = len(ext.spokes)
    pool5 = np.stack([INS._l2n(used5[s]) for s in ext.spokes], 0)
    rng = np.random.default_rng(INS._hash_seed("g2c", seed))
    hits = 0
    tot = 0
    for si, s in enumerate(ext.spokes):
        if s == SP_VISION:
            continue
        q = INS._l2n(ext.ask_for(new_vecs, s))
        sims = np.einsum("fnd,nd->nf", pool5, q) + rng.random((pool5.shape[1], F5)) * 1e-12
        hits += int(np.sum(np.argmax(sims, axis=1) == si))
        tot += pool5.shape[1]
    fr5_original_spokes = hits / float(tot)
    return {
        "d": d, "seed": seed,
        "G2a_existing_keys_bit_identical": keys_identical,
        "G2b_answers_on_already_written_vectors_bit_identical": answers_identical,
        "G2b_fr_before": float(fr_before.mean()),
        "G2b_fr_after": float(fr_after.mean()),
        "G2c_fr_on_original_spokes_after_writing_5_spoke_vectors": fr5_original_spokes,
        "fr_all_5_spokes": float(pw5_all.mean()),
        "chance_4spoke": 0.25, "chance_5spoke": 0.20,
    }


# ----------------------------------------------------------------------------------
# SELF-TESTS -- must pass BEFORE any data run. Assert VALUES, not just absence of errors.
# ----------------------------------------------------------------------------------
def selftest() -> dict:
    out = {}

    # ST1/ST2 -- the reuse proof (bit-identity to role_slot_summarizer + EventBundleCodec)
    out["ST1_ST2_reuse"] = HSW_SELFTESTS()

    # ST3 -- bipolar bind is self-inverse
    r = np.random.default_rng(1)
    a = r.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(8, 256))
    k = spoke_key("X", 256, 7)
    assert np.array_equal(bipolar_bind(bipolar_bind(a, k), k), a), "bind is not self-inverse"
    out["ST3_bind_self_inverse"] = True

    # ST4 -- key derivation is ORDER-INDEPENDENT (the extension guarantee, at the key level)
    k4 = HubSpokeWord(256, SPOKES4, 7)
    k5 = HubSpokeWord(256, (SP_VISION,) + SPOKES4, 7)
    assert all(np.array_equal(k4.key(s), k5.key(s)) for s in SPOKES4), \
        "spoke keys depend on the spoke set -- extension would invalidate stored vectors"
    out["ST4_keys_order_independent"] = True

    # ST5 -- an ADDRESSED bundle recovers its facets and a FLAT sum does not, on synthetic
    # codes, at the exact chance level the gates use
    d, n = 512, 512
    codes = {s: _bipolar_rows(f"st5:{s}", n, d, 7) for s in SPOKES4}
    c = HubSpokeWord(d, SPOKES4, 7)
    fr_addr = facet_recovery(c.bundle(codes), c, SPOKES4, codes, "HS4_GRADED", 7)
    fr_flat = facet_recovery(c.flat_sum(codes), c, SPOKES4, codes, "FLAT_SUM", 7)
    assert fr_addr >= 0.99, f"ST5 addressed facet recovery {fr_addr} < 0.99"
    assert abs(fr_flat - 0.25) <= 0.05, f"ST5 flat facet recovery {fr_flat} not at chance 0.25"
    out["ST5_addressed_vs_flat"] = {"addressed": fr_addr, "flat": fr_flat, "chance": 0.25}

    # ST6 -- shuffled key COLLAPSES an addressed bundle (delta_key is real, not a label)
    perm = derangement(4, 7)
    fr_shuf = facet_recovery(c.bundle(codes), c, SPOKES4, codes, "HS4_GRADED", 7, key_perm=perm)
    assert fr_shuf <= 0.05, f"ST6 shuffled-key recovery {fr_shuf} did not collapse"
    out["ST6_shuffled_key_collapses"] = {"true_key": fr_addr, "shuffled_key": fr_shuf}

    # ST7 -- the Fano machinery is the instrument's own and behaves as published
    assert abs(INS.fano_bits(1.0, 1024) - 10.0) < 1e-6, "fano_bits ceiling wrong"
    assert INS.fano_bits(1.0 / 1024, 1024) < 0.05, "fano_bits at chance is not ~0"
    assert abs(INS.fano_bits_list(1.0, 1024, 8) - 7.0) < 1e-6, "fano_bits_list ceiling wrong"
    out["ST7_fano"] = True

    # ST8 -- SimHash preserves cosine ORDERING (the lift is not scrambling the norms)
    g = np.random.default_rng(5)
    base = g.standard_normal((3, 6)).astype(np.float32)
    X = np.stack([base[0], base[0] + 0.05 * g.standard_normal(6).astype(np.float32), base[1]])
    H = _simhash(X, 4096, 7, "st8")
    Hn = INS._l2n(H)
    assert float(Hn[0] @ Hn[1]) > float(Hn[0] @ Hn[2]), "SimHash lift broke cosine ordering"
    out["ST8_simhash_order"] = {"near": float(Hn[0] @ Hn[1]), "far": float(Hn[0] @ Hn[2])}

    # ST9 -- the ruler is CLEAN at HEAD (it must not have been edited by this cell).
    # PRE-RUN AMENDMENT A1 (prereg section 9, made BEFORE any data run): git status reports
    # '??' for a file that was NEVER COMMITTED, which is provenance news, not a modification.
    # The two are now distinguished: a TRACKED ruler must be unmodified (hard assert); an
    # UNTRACKED helper is recorded with its sha256 so the provenance gap is visible in the
    # metrics rather than silently swallowed. Direction: neither tightens nor loosens any
    # measurement; it stops a provenance fact masquerading as a tamper alarm.
    ruler_status = {}
    for f in ("experiments/exp_encoding_quality_instrument_v2.py",
              "experiments/exp_meaning_asset_fair_test_v1.py",
              "hdlab/char_trigram_encoder.py", "hdlab/grounded_similarity.py",
              "hdlab/role_slot_summarizer.py", "hdlab/event_bundle.py"):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", f], cwd=str(REPO),
                                 capture_output=True, text=True).returncode == 0
        porc = subprocess.run(["git", "status", "--porcelain", "--", f], cwd=str(REPO),
                              capture_output=True, text=True).stdout.strip()
        sha = hashlib.sha256((REPO / f).read_bytes()).hexdigest()[:16]
        ruler_status[f] = {"tracked": tracked, "porcelain": porc, "sha256_16": sha}
        if tracked:
            assert porc == "", f"TRACKED RULER MODIFIED: {f} -> {porc!r}"
    out["ST9_ruler_status"] = ruler_status
    out["ST9_untracked_helpers"] = sorted(k for k, v in ruler_status.items() if not v["tracked"])

    # ST10 -- arms must DIFFER (a silent alias would make every comparison vacuous)
    v_a, c_a, sp_a, u_a = build_arm("HS4_GRADED", 256, 7)
    v_b, _, _, _ = build_arm("HS4_SIGNED", 256, 7)
    v_c, _, _, _ = build_arm("FLAT_SUM", 256, 7)
    assert not np.array_equal(INS._l2n(v_a), INS._l2n(v_b)), "HS4_GRADED == HS4_SIGNED"
    assert not np.array_equal(INS._l2n(v_a), INS._l2n(v_c)), "HS4_GRADED == FLAT_SUM"
    out["ST10_arms_differ"] = True

    # ST11 -- IV9 reproduction: a PUBLISHED instrument arm run through THIS harness
    S = shared()
    words = S["words"]
    X = INS.enc_orthographic(words, 256, 7)
    rho, npair = INS.simlex_rho(INS._l2n(X), S["w2i"], S["pairs"])
    recov = INS.recoverability(INS._l2n(X), min(N_GATE, len(words)), 1.0, 7)
    out["ST11_instrument_repro"] = {"A_ORTHOGRAPHIC_d256_simlex_rho": rho,
                                    "n_pairs": npair,
                                    "recoverability_sigma1": recov,
                                    "published_full_run_rho": -0.0122,
                                    "note": ("full-run published value is the 3-seed mean at "
                                             "V=4096; single-seed here. Exact-match assertion "
                                             "is gate IV9 in the full run, not here.")}

    # ST12 -- facet recovery DOES go down under noise (a metric that cannot move is not one)
    fr0 = facet_recovery(c.bundle(codes), c, SPOKES4, codes, "HS4_GRADED", 7, sigma=0.0)
    fr4 = facet_recovery(c.bundle(codes), c, SPOKES4, codes, "HS4_GRADED", 7, sigma=4.0)
    assert fr4 < fr0, f"facet recovery did not decline under noise: {fr0} -> {fr4}"
    out["ST12_saturation_moves"] = {"sigma0": fr0, "sigma4": fr4}

    # ST13 -- no external LLM anywhere in this cell's import closure
    banned = [m for m in sys.modules
              if any(t in m.lower() for t in ("transformers", "openai", "llama", "sentence_transformers"))]
    assert not banned, f"external LLM module present in the runtime path: {banned}"
    out["ST13_no_external_llm"] = True

    return out


# ----------------------------------------------------------------------------------
# EVALUATION
# ----------------------------------------------------------------------------------
def _get(units, d, arm):
    for u in units:
        if u.get("d") == d and u.get("arm") == arm:
            return u
    return None


def _mean_over_seeds(units, d, arm, path, default=float("nan")):
    vals = []
    for u in units:
        if u.get("d") != d or u.get("arm") != arm:
            continue
        cur = u
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, (int, float)) and np.isfinite(cur):
            vals.append(float(cur))
    return float(np.mean(vals)) if vals else default


def evaluate(units, corr, ext_proofs) -> Tuple[str, List[dict], dict]:
    gates: List[dict] = []
    d_head = D_SWEEP[-1] if len(D_SWEEP) > 1 else D_SWEEP[0]     # production-native d=256

    def add(gid, family, claim, observed, op, thr):
        ok = (observed >= thr) if op == ">=" else (observed <= thr)
        if isinstance(observed, float) and not np.isfinite(observed):
            ok = False
        gates.append({"id": gid, "family": family, "claim": claim, "observed": observed,
                      "op": op, "threshold": thr, "passed": bool(ok)})

    # pooled per-word vectors across seeds at the headline d, for the CI gates
    def pooled(arm, key):
        xs = []
        for u in units:
            if u.get("d") == d_head and u.get("arm") == arm and key in u:
                xs.append(u[key]["point"])
        return xs

    fr = lambda arm: _mean_over_seeds(units, d_head, arm, ["facet_recovery", "point"])
    fr_ci = lambda arm: [
        _mean_over_seeds(units, d_head, arm, ["facet_recovery", "ci95", 0])
        if False else np.mean([u["facet_recovery"]["ci95"][0] for u in units
                               if u.get("d") == d_head and u.get("arm") == arm]),
        np.mean([u["facet_recovery"]["ci95"][1] for u in units
                 if u.get("d") == d_head and u.get("arm") == arm])]
    chance4 = 0.25

    add("IV1", "KNOWN", "K_SLOTTED facet recovery >= 0.99", fr("K_SLOTTED"), ">=",
        T_IV1_SLOTTED_MIN)
    add("IV2a", "NULL", "FLAT_SUM facet recovery within chance +- 0.05",
        abs(fr("FLAT_SUM") - chance4), "<=", T_IV2_FLAT_TOL)
    lo, hi = fr_ci("FLAT_SUM")
    gates.append({"id": "IV2b", "family": "NULL",
                  "claim": "FLAT_SUM facet-recovery 95% CI covers chance 0.25",
                  "observed": [float(lo), float(hi)], "op": "covers", "threshold": chance4,
                  "passed": bool(lo <= chance4 <= hi)})
    for a in ("F_ORTHO", "F_FREQ"):
        add(f"IV3_{a}", "NULL", f"{a} facet recovery within chance +- 0.05",
            abs(fr(a) - chance4), "<=", T_IV3_FLOOR_TOL)
    add("IV4a", "NULL", "N_NULLCONTENT bundled GOLD_ORTHO lift <= 1.15",
        _mean_over_seeds(units, d_head, "N_NULLCONTENT",
                         ["structure_bundled", "GOLD_ORTHO", "lift"]), "<=", T_IV4_NULL_LIFT_MAX)
    add("IV4b", "NULL", "N_NULLCONTENT bundled |simlex rho| <= 0.10",
        abs(_mean_over_seeds(units, d_head, "N_NULLCONTENT",
                             ["structure_bundled", "simlex", "rho"])), "<=", T_IV4_NULL_RHO_MAX)
    add("IV5", "KNOWN", "N_NULLCONTENT facet recovery >= 0.95 (addressing is content-free)",
        fr("N_NULLCONTENT"), ">=", T_IV5_NULLCONTENT_FR_MIN)
    add("IV6", "NULL", "FLAT_SUM delta_key within +- 0.05 of 0",
        abs(_mean_over_seeds(units, d_head, "FLAT_SUM", ["delta_key", "point"])), "<=",
        T_IV6_FLAT_DELTAKEY_TOL)
    add("IV7", "SAT", "HS4_GRADED facet recovery declines monotonically with noise "
                      "(spearman <= -0.80)",
        _mean_over_seeds(units, d_head, "HS4_GRADED", ["saturation_spearman"]), "<=",
        T_IV7_SATURATION_SPEARMAN_MAX)
    gates.append({"id": "IV8", "family": "KNOWN",
                  "claim": "binding primitives bit-identical to role_slot_summarizer and "
                           "EventBundleCodec.encode_event",
                  "observed": 1.0, "op": ">=", "threshold": 1.0, "passed": True,
                  "note": "asserted in selftest ST1/ST2; the run aborts if it fails"})
    # IV9: the ruler reproduces itself through this harness
    ivrepro = _mean_over_seeds(units, d_head, "F_ORTHO", ["_iv9_delta"], default=0.0)
    gates.append({"id": "IV9", "family": "KNOWN",
                  "claim": "F_ORTHO structure equals INS.enc_orthographic run directly, to 1e-9",
                  "observed": ivrepro, "op": "<=", "threshold": T_IV9_REPRO_TOL,
                  "passed": bool(abs(ivrepro) <= T_IV9_REPRO_TOL)})

    iv_pass = all(g["passed"] for g in gates)

    # ---------------- SCIENTIFIC GATES ----------------
    sci: List[dict] = []
    floor_fr = max(fr(a) for a in FLOOR_ARMS)
    floor_hi = max(fr_ci(a)[1] for a in FLOOR_ARMS)
    hs4_lo = fr_ci("HS4_GRADED")[0]
    dk = _mean_over_seeds(units, d_head, "HS4_GRADED", ["delta_key", "point"])
    dk_lo = np.mean([u["delta_key"]["ci95"][0] for u in units
                     if u.get("d") == d_head and u.get("arm") == "HS4_GRADED"])
    g1 = bool(hs4_lo > floor_hi and dk >= T_G1_DELTAKEY_MIN and dk_lo > 0)
    sci.append({"id": "G1", "claim": "ADDRESSED: HS4_GRADED facet-recovery CI lower > "
                                     "max-floor CI upper AND delta_key >= 0.15 with CI > 0",
                "hs4_ci_lower": float(hs4_lo), "max_floor_ci_upper": float(floor_hi),
                "delta_key": float(dk), "delta_key_ci_lower": float(dk_lo),
                "passed": g1,
                "HONEST_LABEL": "CONSTRUCTION PROOF, not a capability win. Role binding "
                                "recovering its own role is algebra. The can-fail content "
                                "is X_CORRSTRESS."})

    g2ok = all(e["G2a_existing_keys_bit_identical"]
               and e["G2b_answers_on_already_written_vectors_bit_identical"]
               and e["G2c_fr_on_original_spokes_after_writing_5_spoke_vectors"]
               >= T_G2_NEW_SPOKE_FR_MIN for e in ext_proofs)
    sci.append({"id": "G2", "claim": "EXTENSION WITHOUT INVALIDATION (a,b,c all required)",
                "per_config": ext_proofs, "passed": bool(g2ok)})

    # G3 -- the meaning claim, expected to FAIL. Paired bootstrap over the identical pairs.
    sci.append({"id": "G3", "claim": "unbound meaning spoke CI-separated above "
                                     "max(orthographic, hardened FREQ_MIN, scramble) on the "
                                     "identical 322 SimLex pairs",
                "filled_in_by": "main() -- needs the per-pair cosine vectors",
                "passed": None})

    b2 = _mean_over_seeds(units, d_head, "HS4_GRADED",
                          ["spoke_bundle_survival", "B2_GRADED", "retained_frac"])
    sci.append({"id": "G4", "claim": "spoke-bundle survival at B=2 retains >= 0.90 of the "
                                     "list-decoding ceiling",
                "observed": b2, "threshold": T_G4_BUNDLE_B2_RETAIN_MIN,
                "passed": bool(np.isfinite(b2) and b2 >= T_G4_BUNDLE_B2_RETAIN_MIN)})

    sign_cost = {}
    for b in BUNDLE_SIZES:
        gb = _mean_over_seeds(units, d_head, "HS4_GRADED",
                              ["spoke_bundle_survival", f"B{b}_GRADED", "bits"])
        sb = _mean_over_seeds(units, d_head, "HS4_GRADED",
                              ["spoke_bundle_survival", f"B{b}_SIGNED", "bits"])
        sign_cost[f"B{b}"] = {"graded_bits": gb, "signed_bits": sb, "sign_cost_bits": gb - sb}
    sci.append({"id": "G5", "claim": "SIGN COST -- reported, not gated",
                "observed": sign_cost, "passed": None})

    summary = {"d_headline": d_head, "chance_4spoke": chance4,
               "facet_recovery_by_arm": {a: fr(a) for a in ARMS},
               "max_floor_facet_recovery": float(floor_fr),
               "corrstress": corr}
    verdict = ("INSTRUMENT_STILL_LOOSE" if not iv_pass
               else ("ADDRESSED_AND_EXTENSIBLE" if (g1 and g2ok) else "PARTIAL"))
    return verdict, gates + sci, summary


# ----------------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    st = selftest()
    if _ARGS.self_test:
        print("[selftest] PASS " + json.dumps(st, default=str)[:4000])
        return 0

    fp = config_fp()
    done = completed_units(out_dir)
    for d in D_SWEEP:
        for seed in SEEDS:
            for arm in ARMS:
                key = unit_key(ANCHOR_NAME, fp, arm, str(d), str(seed))
                if key in done:
                    continue
                r = run_unit(arm, d, seed)
                if arm == "F_ORTHO":
                    S = shared()
                    X = INS._l2n(INS.enc_orthographic(S["words"], d, seed))
                    rho_ref, _ = INS.simlex_rho(X, S["w2i"], S["pairs"])
                    r["_iv9_delta"] = abs(float(rho_ref) -
                                          float(r["structure_bundled"]["simlex"]["rho"]))
                record_unit(out_dir, key, r)
                print(f"  unit d={d} seed={seed} arm={arm} "
                      f"FR={r['facet_recovery']['point']:.4f} "
                      f"({r['elapsed_s']:.1f}s)", flush=True)

    # load_units returns {unit_key: result}; iterate the VALUES. Sorted by key so the
    # assembled metrics are order-deterministic on a resumed run (sorted(set()) discipline).
    _loaded = load_units(out_dir)
    units = [_loaded[k] for k in sorted(_loaded)
             if isinstance(_loaded[k], dict) and "arm" in _loaded[k]]
    if not units:
        raise SystemExit("[fatal] no units loaded from units.jsonl -- refusing to evaluate "
                         "gates on an empty unit set")

    corr = {}
    ext_proofs = []
    for d in D_SWEEP:
        corr[f"d{d}"] = run_corrstress(d, SEEDS[0])
        for seed in SEEDS:
            ext_proofs.append(run_extension_proof(d, seed))
        print(f"  corrstress + extension proof done for d={d}", flush=True)

    verdict, gates, summary = evaluate(units, corr, ext_proofs)

    # ---- G3: the meaning claim, on the identical pairs, paired bootstrap ----
    S = shared()
    d_head = D_SWEEP[-1] if len(D_SWEEP) > 1 else D_SWEEP[0]
    gold = np.array([s for _, _, s in S["pairs"]], dtype=np.float64)
    lf = np.log(S["counts"] + 1.0)
    la = np.array([lf[S["w2i"][a]] for a, _, _ in S["pairs"]])
    lb = np.array([lf[S["w2i"][b]] for _, b, _ in S["pairs"]])
    freq_min = np.minimum(la, lb)          # the hardened FREQ_MIN channel, seed-free
    g3 = {"n_pairs": int(len(gold)), "d": d_head,
          "floors": {"HARDENED_FREQ_MIN": FT.boot_rho(freq_min, gold)}}
    seed0 = SEEDS[0]
    u_ortho = _get([u for u in units if u["seed"] == seed0], d_head, "F_ORTHO")
    u_scram = _get([u for u in units if u["seed"] == seed0], d_head, "F_SCRAMBLE")
    u_hs4 = _get([u for u in units if u["seed"] == seed0], d_head, "HS4_GRADED")
    if u_ortho:
        g3["floors"]["ORTHOGRAPHIC"] = FT.boot_rho(np.array(u_ortho["_percos_bundled"]), gold)
    if u_scram and "_percos_unbound" in u_scram:
        g3["floors"]["SCRAMBLE_unbound_meaning"] = FT.boot_rho(
            np.array(u_scram["_percos_unbound"]), gold)
    if u_hs4 and "_percos_unbound" in u_hs4:
        arm_cos = np.array(u_hs4["_percos_unbound"])
        g3["arm_unbound_meaning"] = FT.boot_rho(arm_cos, gold)
        g3["arm_bundled"] = FT.boot_rho(np.array(u_hs4["_percos_bundled"]), gold)
        g3["arm_direct_spoke_codes"] = FT.boot_rho(np.array(u_hs4["_percos_direct"]), gold)
        strongest = max(g3["floors"], key=lambda k: g3["floors"][k]["point"])
        floor_vec = {"HARDENED_FREQ_MIN": freq_min,
                     "ORTHOGRAPHIC": np.array(u_ortho["_percos_bundled"]) if u_ortho else None,
                     "SCRAMBLE_unbound_meaning": (np.array(u_scram["_percos_unbound"])
                                                  if u_scram and "_percos_unbound" in u_scram
                                                  else None)}[strongest]
        g3["strongest_floor"] = strongest
        g3["margin_over_strongest_floor"] = FT.boot_rho_diff(arm_cos, floor_vec, gold)
        g3["band"] = FT.band(g3["margin_over_strongest_floor"]["ci95"])
        g3["clears_floor"] = bool(g3["margin_over_strongest_floor"]["ci95"][0] > 0)
    for g in gates:
        if g.get("id") == "G3":
            g.update(g3)
            g["passed"] = bool(g3.get("clears_floor", False))
    if not all(x["passed"] for x in gates if x["id"].startswith("IV")):
        verdict = "INSTRUMENT_STILL_LOOSE"

    # strip the bulky per-pair vectors from what is persisted
    for u in units:
        for k in ("_percos_bundled", "_percos_unbound", "_percos_direct"):
            u.pop(k, None)

    iv = [g for g in gates if g["id"].startswith("IV")]
    npass = sum(1 for g in iv if g["passed"])
    g1 = next(g for g in gates if g["id"] == "G1")
    g2 = next(g for g in gates if g["id"] == "G2")
    g3g = next(g for g in gates if g["id"] == "G3")
    vmsg = (f"{verdict}. instrument-validity {npass}/{len(iv)}. "
            f"G1 ADDRESSED={g1['passed']} (HS4 facet recovery "
            f"{summary['facet_recovery_by_arm']['HS4_GRADED']:.4f} vs max floor "
            f"{summary['max_floor_facet_recovery']:.4f}, chance 0.25; CONSTRUCTION PROOF not a "
            f"capability win). G2 EXTENSION={g2['passed']}. G3 MEANING={g3g['passed']} "
            f"(pre-declared expectation was FAIL; a null here is a real result).")

    metrics = {
        "anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "run_mode": RUN_MODE,
        "prereg": "preregs/exp_hub_spoke_word_representation_v1.md",
        "config_fingerprint": fp,
        "config": {"V": V, "D_SWEEP": D_SWEEP, "SEEDS": SEEDS, "SIGMAS": SIGMAS,
                   "N_GATE": N_GATE, "AP_PROBES": AP_PROBES, "CORPUS_BYTES": CORPUS_BYTES,
                   "N_BOOT": N_BOOT, "BOOT_SEED": BOOT_SEED, "BUNDLE_SIZES": BUNDLE_SIZES,
                   "FR_SIGMAS": FR_SIGMAS, "CORR_RHOS": CORR_RHOS,
                   "config_inherited_from": "exp_encoding_quality_instrument_v2 (unedited)"},
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
        "gates": gates, "summary_block": summary, "selftest": st,
        "extension_proof": ext_proofs, "corrstress": corr, "units": units,
        "elapsed_s": time.time() - t_start,
    }
    write_metrics(out_dir, metrics)
    print(json.dumps({"verdict": verdict, "iv": f"{npass}/{len(iv)}",
                      "G1": g1["passed"], "G2": g2["passed"], "G3": g3g["passed"],
                      "FR": summary["facet_recovery_by_arm"],
                      "elapsed_s": round(metrics["elapsed_s"], 1)}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
