# HDLAB INTEGRATION SPEC -- the parser-free brain-foundational learned meaning channel (for strategy to land, Q111)

**What to add.** A glass-box, parser-free, online-capable LEARNED structured-meaning channel that replaces the
NOT_BF supervised parser (`pos_tagger` + `arceager_parser`) in the meaning chain's learned/identity channel. It
derives the substitutability signal from DIRECTIONAL-SEQUENTIAL context on the raw word stream (the brain's actual
input), carries a per-word GAIN scalar (accumulated evidence) for precision-weighting, and is strictly more
brain-foundational than the parser it replaces.

**Why it is landable (measured, `exp_bf_learned_channel_landing_v1`, held-out SimLex-999, n=338, 3000-boot).**
- Parser-free chain {grounded, SEQ, WordNet} = MRR **0.298** vs the current NOT_BF-parser chain {grounded, DEP,
  WordNet} = **0.294** (+0.004, CI [-0.011, +0.020]) -- **no accuracy cost**, and it removes a NOT_BF component,
  the ~0.3s parser load at read time, and enables online learning.
- The channel is real: its row-shuffle info-free twin LOSES (0.215 vs 0.284).
- BF status: **BF** (order coding + Hebbian-predictive PPMI + divisive normalisation; no treebank/POS/perceptron/
  hard-decode). This is C7 audit row 3b's "route through a BF parse" resolved, and it retires audit row 5b's NOT_BF
  parser dependency for this channel.

**BF verification (each operation).** direction+distance typing = temporal-order coding (`sequence_memory`); PPMI
= the fixed point of Hebbian-predictive association (Levy-Goldberg 2014) + neural rectification; L2 = divisive
normalisation (Carandini-Heeger); learned from the raw stream = statistical/predictive language acquisition
(Saffran; Christiansen-Chater). Detail: `ALL_BF_UPSTREAM_TRACE.md` Section 2.

---

## PROPOSED MODULE -- `hdlab/sequential_meaning_channel.py` (self-contained; numpy/scipy; NO torch, NO LLM)

```python
"""hdlab/sequential_meaning_channel.py -- parser-free LEARNED structured-meaning channel (BF).

Replaces the NOT_BF supervised-parser dependency channel: the substitutability/identity signal is learned from
DIRECTIONAL-SEQUENTIAL context on the raw word stream (no treebank, no POS, no perceptron, no hard decode). BF:
order coding (sequence_memory) + Hebbian-predictive PPMI (Levy-Goldberg 2014, rectified) + divisive normalisation
(Carandini-Heeger). Carries a per-word GAIN = accumulated evidence (Ma/Pouget population precision) for
reliability-weighting. Online-capable (counts update incrementally). Proven parser-free at no accuracy cost:
notes/problems/the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code/HDLAB_INTEGRATION_SPEC.md
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from scipy import sparse

from hdlab.reading_grounding_loop import normalize_lemma

__bf_status__ = "BF"
__bf_note__ = ("directional-sequential PPMI context from the raw stream -- order coding + Hebbian-predictive PPMI "
               "+ divisive norm; parser-free replacement for the NOT_BF supervised parse; carries evidence gain")

# direction+distance context taps -- the brain's directed local sequence (fixed a priori, not tuned on gold)
SEQ_TAPS: List[Tuple[int, str]] = [(-1, "L1"), (1, "R1"), (-2, "L2"), (2, "R2")]


class SequentialMeaningChannel:
    """Accumulate directional-sequential context counts by reading; build PPMI+L2 vectors + per-word gain."""

    def __init__(self) -> None:
        self._counts: Dict[str, Counter] = defaultdict(Counter)   # lemma -> {(dir_dist_type, ctx_lemma): count}

    def observe_sentence(self, tokens: Iterable[str]) -> None:
        """ONLINE update: add one sentence's directional context. `tokens` = surface words (lemmatised internally)."""
        lem = [normalize_lemma(t) for t in tokens]
        n = len(lem)
        for i in range(n):
            w = lem[i]
            for d, typ in SEQ_TAPS:
                j = i + d
                if 0 <= j < n:
                    self._counts[w][(typ, lem[j])] += 1

    def gain(self, word: str) -> float:
        """Intrinsic precision proxy = accumulated evidence for `word` (total directional context count)."""
        return float(sum(self._counts.get(normalize_lemma(word), {}).values()))

    def build_matrix(self, words: List[str]) -> Tuple[np.ndarray, "sparse.csr_matrix"]:
        """PPMI-weighted, L2-normalised sparse vectors for `words` (rows aligned to `words`). Returns (mask, csr).
        PPMI(w,c)=max(0, log[p(w,c)/(p(w)p(c))]); rows L2-normalised (divisive normalisation)."""
        feat: Dict[Tuple[str, str], int] = {}
        for w in words:
            for c in self._counts.get(normalize_lemma(w), ()):  # noqa
                if c not in feat:
                    feat[c] = len(feat)
        F = max(1, len(feat))
        data, ri, ci = [], [], []
        for i, w in enumerate(words):
            for c, k in self._counts.get(normalize_lemma(w), {}).items():
                ri.append(i); ci.append(feat[c]); data.append(float(k))
        X = sparse.csr_matrix((data, (ri, ci)), shape=(len(words), F), dtype=np.float64)
        total = X.sum()
        if total <= 0:
            return np.zeros(len(words), bool), X
        rs = np.asarray(X.sum(axis=1)).ravel(); cs = np.asarray(X.sum(axis=0)).ravel()
        Xc = X.tocoo(); pm = np.empty(len(Xc.data))
        for t in range(len(Xc.data)):
            pmi = np.log((Xc.data[t] * total) / (rs[Xc.row[t]] * cs[Xc.col[t]] + 1e-12) + 1e-12)
            pm[t] = max(0.0, pmi)
        P = sparse.csr_matrix((pm, (Xc.row, Xc.col)), shape=X.shape)
        nrm = np.sqrt(P.multiply(P).sum(axis=1)).A.ravel()
        mask = nrm > 1e-9
        inv = sparse.diags(np.where(mask, 1.0 / np.maximum(nrm, 1e-12), 0.0))
        return mask, inv @ P
```

(The build math is byte-identical to the proven `experiments/exp_learned_structured_meaning_v1.dep_ppmi_matrix`;
the only change is the CONTEXT SOURCE -- directional sequence instead of a supervised parse.)

## WIRING (where strategy adds it)
1. Read-time: as reading proceeds, call `observe_sentence(tokens)` on each sentence (online, no parser). This is
   the same reading the loop already does; it just accumulates directional counts instead of requiring a parse.
2. Build the channel matrix over the concept vocabulary; add it to the convergent read alongside grounded +
   taxonomic (it is the LEARNED identity channel; it supersedes the unordered distributional bag).
3. Carry `gain(word)` as the per-concept precision scalar (for the gain-ratio fusion below).

## THE FUSION (fixing the fitted weight, Q111)
Replace `convergent_cue_reader.DEFAULT_W` (a fitted OUR-INVENTION scalar) with the intrinsic per-query GAIN RATIO.
IMPORTANT brain-foundational rule (measured): gain-modulate ONLY the channels whose evidence is EARNED (grounded,
SEQ); a SUPPLIED ontology's gain is UNIFORM (constant), i.e. equal weight -- using its feature-count as a gain is
WRONG (CI-sep worse: -0.0155). At current reading volume the earned channels are still weak, so precision-weighting
is net-neutral-to-slightly-negative on the full mix; land the channel now, and turn ON gain-weighting once the
learned channel grows to ontology parity (grow-by-reading; the earned-only fusion already wins CI-sep, +0.0135).

## INVARIANTS (do NOT change)
- The recall/recognition path (attractor: `ca3_completer`, `gap_detector`, `hippocampal_encoder`) is UNTOUCHED --
  it reads the normalised vectors; the gain is a separate scalar the RANKING reads. Byte-identical
  (`exp_ppc_no_regression_v1` INV1/INV2).
- No external tool/LLM at inference; the channel is glass-box and online.

## REVERIFY
`.venv/Scripts/python.exe verification/test_ppc_meaning_representation.py`  (28/28; the D-section covers the
landable parser-free channel). Landing witness for the channel itself: `exp_bf_learned_channel_landing_v1`
(LANDABLE_A ties the parser chain, twin loses, uniform-supplied-gain beats the wrong feature-count gain).

## BF STATUS DELTAS to record (Q111)
- NEW: `hdlab/sequential_meaning_channel` -> "BF".
- `pos_tagger` / `arceager_parser` -> remain "NOT_BF" but are NO LONGER REQUIRED by the meaning chain (the learned
  identity channel is now parser-free); the parser dependency in audit row 5b is retired for this channel.
- `convergent_cue_reader` -> the fitted `w` is replaceable by the intrinsic gain ratio (BF fix; turn on with exposure).
