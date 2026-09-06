"""hdlab/bridging_inference.py -- the CONSTRUCTION-INTEGRATION bridging-inference organ, and the meaning
channel's FIRST live read()-time consumer (owner-DONE bridging_inference_infer_the_unstated_link_between_
adjacent_sentences, Q111 landing 2026-09-06).

WHAT THIS ORGAN COMPUTES (the brain operation, PINNED).
Comprehension fills the UNSTATED coherence link between adjacent sentences -- which whole a part belongs to
("We checked the picnic supplies. The beer was warm." -> beer PART-OF supplies), which event an instrument
serves ("John was murdered. The knife was found nearby." -> knife INSTRUMENT-OF the murder). Kintsch (1988)
CONSTRUCTION-INTEGRATION: comprehension constructs a weakly-connected network of stated elements plus the
small set of likely bridging inferences, then integrates by spreading activation until it settles onto the
links that survive; Clark (1975) bridging; Haviland & Clark (1974) given-new. The relatedness that says which
antecedent is plausible is read from the ATL semantic hub (Lambon Ralph 2017 -- graded, distributional,
transmodal). The "pick the SPECIFIC coherent link, not the GENERICALLY-salient one" is the N400 /
predictive-coding signal -- relatedness BEYOND baseline expectation (Kuperberg & Jaeger 2016).

THE OPERATION (glass-box, NO LLM, deterministic). Given a bridging TARGET word (the part / the instrument)
and a candidate SET of prior situation-model antecedents (entity heads / event predicates), SELECT the
antecedent whose meaning-store relatedness to the target is highest (optionally salience-discounted), and
ABSTAIN when the winning margin is below tau (McKoon-Ratcliff 1992 minimalist: commit only the
coherence-REQUIRED inference). This is antecedent SELECTION -- the validated half of propose-score-select;
the relation TYPE (part vs instrument vs cause) is schema/syntax, a DIFFERENT organ (measured: typing is
structural, not distributional -- SOLVED section 2c).

MEANING SOURCES -- REUSE the LIVE stores, do NOT rebuild (owner: reuse organs):
  "hub"  = the ATL PPMI+SVD hub  data/frontend_assets/hub_ppmi_svd_200d.pkl  (RAW_HUB, the validated headline:
           referential-PART WordNet meronymy 0.4720 / ConceptNet PartOf 0.6087 / INSTRUMENT UsedFor 0.4522,
           each CI-separated over the no-inference + most-salient floors, shuffled-meaning twin at chance).
  "mfnd" = hdlab.meaning_foundation MFS sense signatures (the frozen curated foundation -- the STRONGEST single
           source on PartOf 0.6541; the concrete justification for wiring the curated store live).
  "cond" = "hub" with the N400/predictive-coding CONDITIONING (score = relatedness - beta*salience) -- the
           salience-discount that separates the specific coherence link from the generically-frequent entity.

BYTE-FAITHFUL to the validated bridging arm: the RAW_HUB / MEAN_FND scoring here is the SAME computation as
experiments/exp_bridging_selection_v2.py (unit-vector cosine argmax over the SAME hub pkl; MFS = the first
WordNet synset signature). The FUSE (spreading-activation PPR over the relational graph fused with the
distributional read), the multi-cue Competition-Model fusion, and the entropy-gated SELECTIVE bridging are
brain-faithful UPGRADES prototyped + measured in the SOLVED (each held-out, twin-controlled) -- available as
follow-on estimators, NOT the validated headline this organ lands.

Glass-box. NO external LLM at inference. ASCII-only. Deterministic. Assets are large gitignored data assets
(the whole data/ tree is gitignored); the organ DEGRADES GRACEFULLY (available()==False -> select() abstains,
never raises) when they are absent, so a default-on live consumer is safe in an asset-less environment.
"""
from __future__ import annotations

import os
import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
_EPS = 1e-9

# lazy process-singletons (loaded ONCE; a reader that never touches the meaning channel pays nothing)
_HUB: Optional[Dict[str, np.ndarray]] = None
_HUB_MISSING = False
_UNIT_CACHE: Dict[str, np.ndarray] = {}
_SALIENCE: Optional[Dict[str, float]] = None


def _unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    return v / (n + _EPS) if n > 0 else v


def _hub() -> Optional[Dict[str, np.ndarray]]:
    """The ATL PPMI+SVD hub as {word -> 200-d vector}, loaded ONCE. None (not an exception) if the gitignored
    asset is absent -- the caller degrades to abstain."""
    global _HUB, _HUB_MISSING
    if _HUB is None and not _HUB_MISSING:
        try:
            with open(HUB_ASSET, "rb") as fh:
                _HUB = pickle.load(fh)["hub"]
        except (FileNotFoundError, OSError, KeyError, pickle.UnpicklingError):
            _HUB_MISSING = True
            _HUB = None
    return _HUB


def _hub_unit(word: str) -> Optional[np.ndarray]:
    """The UNIT hub vector for a word (memoized), or None if OOV / no hub."""
    hub = _hub()
    if hub is None:
        return None
    v = _UNIT_CACHE.get(word)
    if v is None:
        raw = hub.get(word)
        if raw is None:
            return None
        v = _unit(raw)
        _UNIT_CACHE[word] = v
    return v


def _salience() -> Optional[Dict[str, float]]:
    """Per-word generic salience = mean cosine to a fixed 2000-word vocab sample (hubness). Byte-faithful to
    experiments/exp_bridging_selection_v2.py (rng seed 7, 2000-word sample). Lazily built ONLY for cond mode."""
    global _SALIENCE
    if _SALIENCE is None:
        hub = _hub()
        if hub is None:
            return None
        vocab = list(hub.keys())
        rng0 = np.random.default_rng(7)
        sample = [vocab[i] for i in rng0.choice(len(vocab), size=min(2000, len(vocab)), replace=False)]
        S = np.array([_unit(hub[w]) for w in sample])
        _SALIENCE = {w: float(np.mean(S @ _unit(hub[w]))) for w in vocab}
    return _SALIENCE


def available() -> bool:
    """Whether the meaning-store assets are present (the hub loads). False -> select() abstains, never raises."""
    return _hub() is not None


# ---------------------------------------------------------------- meaning_foundation (MFS) source
_MFND_CACHE: Dict[str, Optional[np.ndarray]] = {}


def _mfnd_unit(word: str) -> Optional[np.ndarray]:
    """The curated MFS (most-frequent-sense) signature UNIT vector for a word, via hdlab.meaning_foundation
    (the first WordNet synset -- byte-faithful to exp_bridging_selection_v2.build_mfnd_vec), or None. Lazy
    imports wordnet + the frozen store so the default (hub) path never loads them."""
    if word in _MFND_CACHE:
        v = _MFND_CACHE[word]
        return v
    v = None
    try:
        from hdlab.meaning_foundation import sense_signature
        from nltk.corpus import wordnet as wn
        ss = wn.synsets(word)
        if ss:
            sig = sense_signature(ss[0].name())
            if sig is not None and float(np.linalg.norm(sig)) > 0:
                v = _unit(sig)
    except Exception:
        v = None
    _MFND_CACHE[word] = v
    return v


# ---------------------------------------------------------------- the bridge record + the organ
@dataclass
class Bridge:
    """One inferred (or abstained) bridging link -- the glass-box trace of a construction-integration select."""
    target: str                       # the bridging element (part / instrument surface form)
    antecedent: Optional[str]         # the SELECTED prior element (whole / event), None if nothing scored
    source: str                       # "hub" | "mfnd" | "cond"
    score: float                      # relatedness score of the winner (salience-discounted in cond mode)
    margin: float                     # winner - runner-up (the competition/settling margin)
    abstained: bool                   # True when no antecedent scored OR margin < tau (commit withheld)
    ranked: List[Tuple[str, float]] = field(default_factory=list)   # all candidates, score-desc (trace)


class BridgeInference:
    """Antecedent SELECTION over the situation model's prior elements by meaning-store relatedness. Reuses the
    LIVE ATL hub / curated meaning foundation; never rebuilds a store. Stateless apart from the process-level
    asset singletons -- one instance per reader is fine."""

    VALID_SOURCES = ("hub", "mfnd", "cond")

    def __init__(self, source: str = "hub", beta: float = 0.0, tau: float = 0.0) -> None:
        if source not in self.VALID_SOURCES:
            raise ValueError("source must be one of %s, got %r" % (self.VALID_SOURCES, source))
        self.source = source
        self.beta = float(beta)          # N400 salience-discount coefficient (cond mode)
        self.tau = float(tau)            # abstain margin: commit only when winner-runnerup >= tau

    def available(self) -> bool:
        return available()

    def relatedness(self, target: str, cand: str, source: Optional[str] = None) -> Optional[float]:
        """Meaning-store relatedness target<->cand (cosine), or None when either side is uncovered / no asset.
        `source` overrides the instance default. Salience is NOT applied here (that is the selection-level
        conditioning); this is the raw associative read the ATL supplies."""
        src = source or self.source
        if src in ("hub", "cond"):
            tv, cv = _hub_unit(target), _hub_unit(cand)
        elif src == "mfnd":
            tv, cv = _mfnd_unit(target), _mfnd_unit(cand)
        else:
            raise ValueError("bad source %r" % src)
        if tv is None or cv is None:
            return None
        return float(tv @ cv)

    def select(self, target: str, candidates: Sequence[str], *, source: Optional[str] = None,
               beta: Optional[float] = None, tau: Optional[float] = None) -> Optional[Bridge]:
        """SELECT the candidate antecedent best supported by meaning-store relatedness to `target` (Kintsch
        construction-integration; the ATL relatedness read). Returns a Bridge with the full glass-box ranking,
        or None when `target`/all candidates are OOV or there are no candidates (nothing to infer -> the caller
        treats it as an abstain). In cond mode the winner is the SPECIFIC link (relatedness - beta*salience),
        not the generically-salient one. `abstained` is set when the winning margin < tau."""
        src = source or self.source
        b = self.beta if beta is None else float(beta)
        t = self.tau if tau is None else float(tau)
        # dedupe candidates, drop the target itself (an element does not bridge to itself)
        seen = set()
        cands = []
        for c in candidates:
            if c is None or c == target or c in seen:
                continue
            seen.add(c)
            cands.append(c)
        if not cands:
            return None
        sal = _salience() if (src == "cond" and b != 0.0) else None
        scored: List[Tuple[str, float]] = []
        for c in cands:
            r = self.relatedness(target, c, source=src)
            if r is None:
                continue
            s = r
            if sal is not None:
                s = r - b * float(sal.get(c, 0.0))
            scored.append((c, s))
        if not scored:
            return None
        scored.sort(key=lambda cs: (-cs[1], cs[0]))   # deterministic tie-break by word
        top_c, top_s = scored[0]
        runner = scored[1][1] if len(scored) > 1 else float("-inf")
        margin = top_s - runner if len(scored) > 1 else float("inf")
        abstained = margin < t
        return Bridge(target=target, antecedent=top_c, source=src, score=round(top_s, 6),
                      margin=(round(margin, 6) if margin != float("inf") else float("inf")),
                      abstained=bool(abstained), ranked=[(c, round(s, 6)) for c, s in scored])
