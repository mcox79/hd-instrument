"""hdlab/quality_relation.py -- consolidated two-channel adjective opposition/relation detector
(wire-don't-island promotion, 2026-08-08).

Composes two independently PROVEN channels (session scratchpad proofs, lifted here verbatim):

  Channel A -- WordNet lexical-antonym opposition, G1 dominant-synset guard (adj_opposition_
    precision_sweep.py): restricting antonym-closure evidence to each word's single DOMINANT
    (WordNet sense-order first) adjective synset (satellite->head similar_tos() hop for pos='s'
    synsets) is the precision-safe guard -- 0 confirmed false positives on the adversarial
    big/soft, big/immature probes (the unrestricted-all-synsets variant DOES false-positive on
    both -- see the proof's LEAK-VECTOR CONFIRMATION section). Generalizes hdlab.
    wordnet_polarity_propagation.dictionary_lookup's antonym-first Stage-A precedence structure
    from verbs to adjectives (pos in {'a','s'}; adjectives have no hypernym taxonomy in WordNet,
    so there is no verb-style Stage-B path-similarity fallback -- the dominant-synset restriction
    IS the whole guard).

  Channel B -- signed FPE (Fractional Power Encoding) dimensional axis, ON the substrate
    (fpe_quality_axis_proof.py, HARD-PASS 15/15): opposition = substrate anti-correlation of a
    word's position on a hand-supplied continuous scalar axis (e.g. density: dense=+1.0 ..
    airy=-1.0), encoded as v(axis, s) = bind(R_axis, polar(1, theta_axis * s)) where theta_axis is
    narrow-banded around RATE_CENTER=pi/2 (full-width theta ~ U(0, 2*pi), i.e. unit_phase_vec's
    own draw, sinc-zeros the pole-to-pole cosine at gap=2 -- see the proof's STEP 1 naive-ablation
    diagnosis; the narrow band is REQUIRED, not a tuning nicety) and R_axis is a fully-independent
    per-axis identity key (binding is unitary, so it exactly preserves within-axis cosine geometry
    while decorrelating cross-axis comparisons to ~0 -- without this fix, two axes drawn around
    the same RATE_CENTER leak a deterministic (s_a - s_b)*RATE_CENTER cross-axis bias, see the
    proof's STEP 4). A flat bag-of-features cosine is bounded >=0 by construction and structurally
    CANNOT encode a signed opposition (measured on the proof's own 6 opposed pairs: FLAT
    opposed_mean=+0.40 vs FPE opposed_mean=-0.92) -- this is why channel B is a distinct mechanism
    from channel C below, not a redundant one.

  Channel C -- fallback SAME-pole check via the already-wired hdlab.lexical_similarity.
    concept_similarity (McRae-style shared-feature bundle cosine) for word pairs not covered by
    channel A or channel B.

Composition order (first channel to produce a verdict wins; NEVER guesses on OOV):
  1. Channel A fires opposed -> verdict "opposed", channel "wordnet_antonym".
  2. Else, if both words are in the FPE axis lexicon -> channel B decides categorically:
     different axes = "unrelated"; same axis = threshold the substrate cosine (<=OPP_THRESH
     "opposed", >=SAME_THRESH "same", else "unrelated") -- channel "fpe_axis".
  3. Else, if concept_similarity(word_a, word_b) clears its own link threshold -> verdict "same",
     channel "flat_same".
  4. Else, verdict "unrelated" if both words are known to at least one channel; verdict None
     (channel None) if either word is OOV of every channel -- never guess.

REUSE (import, not reimplement): hdlab.situation_model_accumulate.unit_phase_vec (the FHRR atomic-
symbol primitive, reused unmodified for channel B's per-axis identity keys), hdlab.
lexical_similarity._cos_complex (the FHRR cosine metric, reused for every channel-B cosine) and
.concept_similarity / .in_lexicon / .SIMILARITY_LINK_THRESHOLD (channel C, wired unmodified --
concept_similarity is itself already built on hdlab.bundling.bundle internally, so bundle is
reused TRANSITIVELY through this import; this module never builds its own bag-of-features encoder,
so it does not import bundle directly), hdlab.binding.bind (channel B's per-axis identity-key
bind, FHRR elementwise complex multiply, unitary). Channel A generalizes hdlab.
wordnet_polarity_propagation's antonym-first Stage-A precedence (verbs) to adjectives.

PRE-REGISTERED CONSTANTS (carried verbatim from the two scratchpad proofs, NOT re-tuned here):
  RATE_CENTER=pi/2, RATE_SPREAD=0.25 rad (fpe_quality_axis_proof.py STEP 2 calibration),
  OPP_THRESH=-0.30, SAME_THRESH=0.60 (STEP 3 pre-registration), AXIS_WORDS scalar seeds (STEP 4/6
  hand-authored 4-axis lexicon: density/sheen/energy/tone, 23 words total). These need
  re-validation when the axis lexicon scales up to Warriner et al. norms -- this is a small
  hand-supplied seed, not a general open-vocabulary solution (see the promotion report's honest
  coverage caveat).

No repo writes beyond this file. No git commit (the Director owns the commit for this wiring).
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import torch

from hdlab.binding import bind
from hdlab.lexical_similarity import _cos_complex as cos_complex
from hdlab.lexical_similarity import SIMILARITY_LINK_THRESHOLD, concept_similarity, in_lexicon
from hdlab.situation_model_accumulate import unit_phase_vec

N_DIM_DEFAULT = 1024

_wn = None


def _get_wn():
    """Lazy WordNet import (nltk is an already-promoted hdlab dep, see hdlab.animacy_lexicon /
    hdlab.wordnet_polarity_propagation); downloads the wordnet/omw-1.4 corpora on first use only."""
    global _wn
    if _wn is not None:
        return _wn
    from nltk.corpus import wordnet as wn_mod
    try:
        wn_mod.synsets("test")
    except LookupError:
        import nltk
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
    _wn = wn_mod
    return _wn


# =================================================================================================
# CHANNEL A -- WordNet adjective antonym opposition, G1 dominant-synset guard.
# =================================================================================================
_adj_syn_cache: Dict[str, list] = {}


def _adj_synsets(word: str, wn) -> list:
    """All ADJECTIVE synsets of word (pos in {'a' head, 's' satellite}), WordNet sense-order. Cached."""
    if word not in _adj_syn_cache:
        _adj_syn_cache[word] = [s for s in wn.synsets(word) if s.pos() in ("a", "s")]
    return _adj_syn_cache[word]


def _dominant_adj_synset(word: str, wn):
    """G1 guard: word's single most-frequent adjective synset, or None if word has no adj sense."""
    ss = _adj_synsets(word, wn)
    return ss[0] if ss else None


_g1_closure_cache: Dict[str, Dict[str, Tuple[str, str]]] = {}


def _g1_antonym_closure(word: str, wn) -> Dict[str, Tuple[str, str]]:
    """{antonym_word: (source_synset_name, antonym_synset_name)} reachable from word's DOMINANT
    adjective synset only (satellite->head similar_tos() hop for pos='s' synsets -- the adjective-
    specific extension over the verb-only Stage-A pattern in hdlab.wordnet_polarity_propagation.
    dictionary_lookup). Empty dict if word has no adjective sense. Cached."""
    if word in _g1_closure_cache:
        return _g1_closure_cache[word]
    dom = _dominant_adj_synset(word, wn)
    out: Dict[str, Tuple[str, str]] = {}
    if dom is not None:
        heads = [dom] + (list(dom.similar_tos()) if dom.pos() == "s" else [])
        for h in heads:
            for lem in h.lemmas():
                for ant in lem.antonyms():
                    aw = ant.name().replace("_", " ").lower()
                    out.setdefault(aw, (h.name(), ant.synset().name()))
    _g1_closure_cache[word] = out
    return out


def _wordnet_g1_opposed(word_a: str, word_b: str, wn) -> Optional[dict]:
    """G1 antonym-opposition verdict: word_b in word_a's dominant-synset closure, OR word_a in
    word_b's. Returns glass-box evidence (direction + the exact synset path) or None."""
    clo_a = _g1_antonym_closure(word_a, wn)
    if word_b in clo_a:
        src, ant_syn = clo_a[word_b]
        return {"direction": f"{word_a}->{word_b}", "source_synset": src, "antonym_synset": ant_syn}
    clo_b = _g1_antonym_closure(word_b, wn)
    if word_a in clo_b:
        src, ant_syn = clo_b[word_a]
        return {"direction": f"{word_b}->{word_a}", "source_synset": src, "antonym_synset": ant_syn}
    return None


def _wordnet_known(word: str, wn) -> bool:
    """True if word has at least one WordNet adjective sense (used only for the OOV never-guess gate)."""
    return _dominant_adj_synset(word, wn) is not None


# =================================================================================================
# CHANNEL B -- signed FPE dimensional axis, on-substrate. Pre-registered constants carried
# verbatim from fpe_quality_axis_proof.py (HARD-PASS 15/15); see module docstring.
# =================================================================================================
RATE_CENTER = math.pi / 2.0       # narrow-band phase-rate center (proof STEP 2); full-width
                                   # theta~U(0,2pi) sinc-zeros at the poles (proof STEP 1)
RATE_SPREAD = 0.25                # radians; per-dimension rate spread around RATE_CENTER
OPP_THRESH = -0.30                # pre-registered opposed threshold (proof STEP 3)
SAME_THRESH = 0.60                # pre-registered same threshold (proof STEP 3)

# Hand-authored 4-axis lexicon (proof STEP 4/6), word -> signed scalar position in [-1, 1].
# Coverage caveat (honest, not re-tuned here): 23 words across 4 axes -- a hand-supplied scalar
# seed, not a general open-vocabulary solution. Warriner et al. norms are the natural scale-up.
AXIS_WORDS: Dict[str, Dict[str, float]] = {
    "density": {"dense": 1.0, "thick": 0.8, "heavy": 0.7, "light": -0.7, "airy": -1.0, "fluffy": -0.8},
    "sheen": {"glossy": 1.0, "shiny": 0.9, "bright": 0.7, "matte": -0.9, "dull": -0.7, "flat": -0.6},
    "energy": {"energetic": 1.0, "lively": 0.8, "calm": -0.9, "mellow": -0.8, "sluggish": -1.0},
    "tone": {"humorous": 0.9, "funny": 0.9, "playful": 0.7, "solemn": -0.8, "serious": -0.6, "grave": -0.9},
}
# Base per-axis seeds (proof STEP 4); offset by the caller's `seed` param -- default seed=0
# reproduces the proof's exact hard-coded seeds (101/202/303/404 rate, 11/22/33/44 key) bit for bit.
_AXIS_RATE_SEED_BASE = {"density": 101, "sheen": 202, "energy": 303, "tone": 404}
_AXIS_KEY_SEED_BASE = {"density": 11, "sheen": 22, "energy": 33, "tone": 44}

WORD_AXIS: Dict[str, Tuple[str, float]] = {}
for _axis, _words in AXIS_WORDS.items():
    for _w, _s in _words.items():
        WORD_AXIS[_w] = (_axis, _s)

_axis_cache: Dict[Tuple[str, int, int], Tuple[torch.Tensor, torch.Tensor]] = {}


def _axis_rate(generator: torch.Generator, d: int) -> torch.Tensor:
    """Seeded per-axis phase-RATE vector, narrow-banded around RATE_CENTER (proof STEP 2)."""
    u = torch.rand(d, generator=generator)
    return RATE_CENTER + (u - 0.5) * (2.0 * RATE_SPREAD)


def _fpe_vec(theta_axis: torch.Tensor, s: float) -> torch.Tensor:
    """FPE scalar-code at signed position s: unit_phase_vec's own construction, theta scaled by s."""
    d = theta_axis.shape[0]
    return torch.polar(torch.ones(d), theta_axis * s).to(torch.complex64)


def _build_axis(axis: str, n_dim: int, seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """(rate_vec, identity_key_vec) for one axis, cached by (axis, n_dim, seed)."""
    cache_key = (axis, n_dim, seed)
    if cache_key not in _axis_cache:
        gen_r = torch.Generator().manual_seed(_AXIS_RATE_SEED_BASE[axis] + seed)
        rate = _axis_rate(gen_r, n_dim)
        gen_k = torch.Generator().manual_seed(_AXIS_KEY_SEED_BASE[axis] + seed)
        ident_key = unit_phase_vec(n_dim, gen_k)
        _axis_cache[cache_key] = (rate, ident_key)
    return _axis_cache[cache_key]


def _axis_word_vec(word: str, n_dim: int, seed: int) -> torch.Tensor:
    """Word's FPE vector on its axis, bound to the axis's fully-independent identity key (proof
    STEP 4 cross-axis independence fix: unitary binding preserves within-axis cosine geometry
    while decorrelating cross-axis comparisons)."""
    axis, s = WORD_AXIS[word]
    rate, ident_key = _build_axis(axis, n_dim, seed)
    return bind(ident_key, _fpe_vec(rate, s))


def _fpe_axis_relation(word_a: str, word_b: str, n_dim: int, seed: int) -> Tuple[str, float, str, str]:
    """Channel B categorical decision. Caller must ensure word_a, word_b are both in WORD_AXIS.
    Different axes -> "unrelated" categorically. Same axis -> threshold the substrate cosine
    against the pre-registered OPP_THRESH / SAME_THRESH."""
    axis_a, _ = WORD_AXIS[word_a]
    axis_b, _ = WORD_AXIS[word_b]
    cos = cos_complex(_axis_word_vec(word_a, n_dim, seed), _axis_word_vec(word_b, n_dim, seed))
    if axis_a != axis_b:
        return "unrelated", cos, axis_a, axis_b
    if cos <= OPP_THRESH:
        return "opposed", cos, axis_a, axis_b
    if cos >= SAME_THRESH:
        return "same", cos, axis_a, axis_b
    return "unrelated", cos, axis_a, axis_b


# =================================================================================================
# PUBLIC API
# =================================================================================================
def quality_relation(word_a: str, word_b: str, *, n_dim: int = N_DIM_DEFAULT, seed: int = 0) -> dict:
    """Glass-box quality/opposition relation between two words.

    Composition order (first channel to fire wins): (1) WordNet G1 dominant-synset antonym ->
    verdict "opposed", channel "wordnet_antonym"; (2) else if both words are on the supplied FPE
    axis lexicon -> substrate cosine decides "opposed"/"same"/"unrelated" on channel "fpe_axis"
    (cross-axis pairs are categorically "unrelated"); (3) else if concept_similarity clears its
    link threshold -> verdict "same", channel "flat_same"; (4) else verdict "unrelated" if both
    words are known to at least one channel, else verdict None (never guesses on OOV).
    Deterministic for a given seed (evidence cosines are bit-reproducible).
    """
    wn = _get_wn()
    a = word_a.lower()
    b = word_b.lower()

    wn_evidence = _wordnet_g1_opposed(a, b, wn)
    if wn_evidence is not None:
        return {"verdict": "opposed", "channel": "wordnet_antonym", "evidence": wn_evidence}

    if a in WORD_AXIS and b in WORD_AXIS:
        verdict, cos, axis_a, axis_b = _fpe_axis_relation(a, b, n_dim, seed)
        return {
            "verdict": verdict,
            "channel": "fpe_axis",
            "evidence": {"cosine": cos, "axis_a": axis_a, "axis_b": axis_b},
        }

    sim = concept_similarity(a, b)
    if sim is not None and sim >= SIMILARITY_LINK_THRESHOLD:
        return {"verdict": "same", "channel": "flat_same", "evidence": {"cosine": sim}}

    known_a = _wordnet_known(a, wn) or (a in WORD_AXIS) or in_lexicon(a)
    known_b = _wordnet_known(b, wn) or (b in WORD_AXIS) or in_lexicon(b)
    if not (known_a and known_b):
        return {"verdict": None, "channel": None, "evidence": None}
    return {"verdict": "unrelated", "channel": None, "evidence": {"cosine": sim}}


def self_test() -> dict:
    """Minimal reproduction of the two proofs' decisive HARD-PASS checks, for `python -m
    hdlab.quality_relation` diagnostics. The full assertion suite lives in
    verification/test_quality_relation.py."""
    checks = {}

    r = quality_relation("hot", "cold")
    checks["hot_cold_wordnet_antonym"] = (r["verdict"] == "opposed" and r["channel"] == "wordnet_antonym")

    r = quality_relation("dense", "airy")
    checks["dense_airy_fpe_opposed"] = (
        r["verdict"] == "opposed" and r["channel"] == "fpe_axis" and r["evidence"]["cosine"] <= OPP_THRESH
    )

    r = quality_relation("dense", "thick")
    checks["dense_thick_fpe_same"] = (
        r["verdict"] == "same" and r["channel"] == "fpe_axis" and r["evidence"]["cosine"] >= SAME_THRESH
    )

    r = quality_relation("dense", "humorous")
    checks["cross_axis_unrelated"] = (r["verdict"] == "unrelated" and r["channel"] == "fpe_axis")

    r = quality_relation("big", "soft")
    checks["g1_precision_guard_big_soft"] = (r["verdict"] != "opposed")
    r = quality_relation("big", "immature")
    checks["g1_precision_guard_big_immature"] = (r["verdict"] != "opposed")

    r = quality_relation("zzznotarealadjective", "alsofake")
    checks["oov_never_guesses"] = (r["verdict"] is None and r["channel"] is None)

    assert all(checks.values()), checks
    return checks


if __name__ == "__main__":
    import json

    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
