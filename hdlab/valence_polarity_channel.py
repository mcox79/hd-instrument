"""VALENCE-POLARITY meaning channel -- the SIGNED evaluative axis that un-blinds meaning to ANTONYMY.

THE GAP (pri-2 meaning-representation, HDLAB_INTEGRATION_SPEC "second landable"): the learned distributional +
perceptual meaning channels are RELATION-BLIND -- they score love/hate as similar as love/adore (synonym-vs-antonym
AUC ~0.51-0.53), because antonyms SHARE contexts, so co-occurrence cannot separate them; only a SUPPLIED ontology
(WordNet) discriminates (~0.87). Antonyms are OPPOSITE POLES on a shared graded EVALUATIVE dimension (Osgood 1957
semantic-differential Evaluation axis; Russell 1980 / Barrett core affect; vmPFC valence -- PINNED). Reading that
SIGNED dimension separates synonyms from antonyms WITHOUT WordNet.

WHAT THIS IS. A per-pair POLARITY read over the substrate's existing affect representation
(`hdlab.affect_lexicon.valence`, the offline Warriner et al. 2013 VAD norms -- an admissible curated FOUNDATION
asset): `valence_polarity(a,b) = -|valence(a) - valence(b)|` (near 0 = same pole = synonym-like; strongly negative
= opposite poles = antonym-like). `va_polarity` adds the arousal axis (2-space) when both norms are present. This
is the POLARITY axis, NOT a relatedness axis -- it is FUSED alongside the identity/relatedness channels (it is
COMPLEMENTARY: corr ~0.11 with the distributional channel), never pooled into them. `grounded_similarity`
deliberately OMITS it (its docstring: VAD is "NOT used here" -- it is an affect signal, not an identity signal);
this organ is where that signed axis lives.

MEASURED BASIS (`experiments/exp_valence_polarity_meaning_channel_v1.py`, SimVerb-3500 relation labels): a signed
valence read lifts synonym-vs-antonym AUC 0.535 -> 0.72 (full VAD 0.75) WITHOUT WordNet, CI-separated
[+0.084,+0.281], complementary to the distributional channel; the info-free twin (shuffled valence) collapses to
~0.5. HONEST BOUND: valence separates the AFFECTIVELY-opposed antonyms (~77% of antonyms); scalar-directional
(increase/decrease) and transfer converses (buy/sell) are DIFFERENT axes handled elsewhere (path-marker signature /
the role-binding generative channel).

CONSUMER. Fused into the meaning read alongside the grounded + learned-identity channels. The live fusion-wire is
gated on the end-to-end grounding-coverage measurement (`measure_end_to_end_whether_the_meaning_fusion_lifts_live_
grounding_coverage`, pri-5); until then this is the standalone BF polarity channel + its witness. Glass-box, NO
external LLM / NO WordNet in the channel.

INVARIANT: pure per-pair read over affect_lexicon; no I/O beyond the shared lexicon load; additive (importing it
changes nothing that does not call it).
"""

from __future__ import annotations

from typing import Optional

from hdlab.affect_lexicon import AffectLexicon

__all__ = ["valence_polarity", "va_polarity", "same_pole", "ValencePolarityChannel"]

_LEX: Optional[AffectLexicon] = None


def _lex() -> AffectLexicon:
    global _LEX
    if _LEX is None:
        _LEX = AffectLexicon.load()
    return _LEX


def valence_polarity(a: str, b: str) -> Optional[float]:
    """The SIGNED evaluative-axis polarity of a word pair (Osgood Evaluation; core-affect valence):
    `-|valence(a) - valence(b)|`. ~0 => same pole (synonym-like); strongly negative => opposite poles
    (antonym-like). None if either word lacks a valence norm (honest OOV; the caller falls back to the
    relatedness channels). Higher = more same-pole, so it fuses in the SAME direction as a similarity."""
    lx = _lex()
    va, vb = lx.valence(a), lx.valence(b)
    if va is None or vb is None:
        return None
    return -abs(va - vb)


def va_polarity(a: str, b: str) -> Optional[float]:
    """The 2-space (Valence, Arousal) core-affect distance, signed: `-||[V,A](a) - [V,A](b)||`. Uses the
    arousal axis in addition to valence when BOTH norms are present for both words; else None. A fuller
    core-affect read than valence alone (Russell/Barrett); dominance is not in the shared lexicon so this
    stops at V,A (the experiment's full VAD read loads the third axis separately)."""
    lx = _lex()
    va, vb = lx.valence(a), lx.valence(b)
    aa, ab = lx.arousal(a), lx.arousal(b)
    if None in (va, vb, aa, ab):
        return None
    dv = va - vb
    da = aa - ab
    return -((dv * dv + da * da) ** 0.5)


def same_pole(a: str, b: str) -> Optional[bool]:
    """True if the pair sits on the SAME evaluative pole (same valence SIGN), False if OPPOSITE poles
    (opposite signs), None if either lacks a clear pole. Uses affect_lexicon's signed read (a small neutral
    deadzone + family-polarity fallback); a near-neutral word (sign 0) has no pole -> None. A discrete read of
    the evaluative axis for gating/explanation."""
    lx = _lex()
    sa, sb = lx.valence_sign(a), lx.valence_sign(b)
    if not sa or not sb:            # None or 0 (near-neutral / no norm) -> no clear pole
        return None
    return sa == sb


class ValencePolarityChannel:
    """Thin object surface mirroring the other meaning channels (a `.similarity(a,b)`-style pair read), so a
    fusion caller can inject it uniformly. `.polarity(a,b)` is the raw signed read; `.similarity` is its alias
    (it fuses in the similarity direction: same-pole => higher)."""

    def __init__(self, use_arousal: bool = False) -> None:
        self.use_arousal = use_arousal

    def polarity(self, a: str, b: str) -> Optional[float]:
        return va_polarity(a, b) if self.use_arousal else valence_polarity(a, b)

    similarity = polarity


__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-10 pri-2 meaning-representation landing (piece 2): signed evaluative-axis polarity "
                   "(Osgood 1957; Russell/Barrett core affect) un-blinds antonymy WITHOUT WordNet; measured "
                   "SimVerb AUC 0.535->0.72 CI-sep [+0.084,+0.281], twin collapses; strategy first-hand")
__bf_note__ = ("SIGNED valence polarity -|valence(a)-valence(b)| over affect_lexicon/Warriner VAD (curated "
               "FOUNDATION). Osgood Evaluation axis / vmPFC valence (PINNED computation; norms = curated asset). "
               "The COMPLEMENTARY polarity axis the relatedness channels are blind to (corr ~0.11); grounded_"
               "similarity deliberately OMITS it. Fuse alongside identity/relatedness, never pool. Live fusion-"
               "wire gated on the meaning-fusion end-to-end measurement (pri-5).")


if __name__ == "__main__":
    # antonyms are OPPOSITE poles; synonyms share the pole; the signed read separates them.
    lp = valence_polarity("love", "hate")
    ln = valence_polarity("love", "adore")
    assert lp is not None and ln is not None, (lp, ln)
    assert lp < ln, ("antonym must be MORE negative (opposite poles) than the synonym", lp, ln)
    assert same_pole("love", "adore") is True and same_pole("love", "hate") is False
    assert valence_polarity("love", "zzzznotaword") is None      # honest OOV
    print("SELFTEST PASS: valence_polarity love/hate=%.3f < love/adore=%.3f (antonym = opposite pole)" % (lp, ln),
          flush=True)
