"""hdlab/grounded_similarity.py -- perceptual-grounding fallback for OOV words (2026-08-11).

WHY (architecture-audit TIER-1 finding, notes/architecture_audit_2026-08-11.md): the LIVE
concept-similarity path (hdlab.lexical_similarity.concept_similarity) only judges the ~230
hand-typed concepts in CONCEPT_FEATURES -- every other word returns None ("cannot judge"), even
though a 39,707-word grounding-norms asset (Lancaster sensorimotor norms + Brysbaert concreteness,
data/grounding_testbed/*.csv) has sat on disk, fully downloaded, with ZERO live inference paths
(grep-confirmed: only exp_cskg_foundation_v1 ever touched it, for a build-time diagnostic, not a
runtime call). This module wires that asset in as a FALLBACK feature space, ADDITIVE to (never
replacing) the hand lexicon.

BRAIN-FOUNDATIONAL RATIONALE: the ATL amodal hub aggregates graded, MULTIMODAL sensorimotor
experience (Cox et al. 2024, PMC12224414 -- same citation hdlab.lexical_similarity's own docstring
uses), not bag-of-words co-occurrence. Lancaster sensorimotor norms (Lynott, Connell, Brysbaert,
Brand & Carney 2020, Behavior Research Methods) are a direct behavioral measurement of exactly that
signal (11 perceptual/action-effector strength ratings per word) and Brysbaert concreteness norms
(Brysbaert, Warriner & Kuperman 2014) measure the companion imageability/grounding-in-experience
dimension. This is the PREFERRED grounded feature space per director instruction (perceptual
grounding = most brain-foundational), evaluated ahead of the from-scratch learned encoder
(scale_win_tinytransformer_encoder, see capability_registry.jsonl) as the primary asset to wire.

HONEST, MEASURED LIMIT (this is the module's central engineering constraint, not an afterthought):
raw cosine similarity over the z-scored 11-dim sensorimotor + 1-dim concreteness vector CANNOT
separate a true near-synonym pair from a same-domain SIBLING pair that is perceptually similar but
identity-distinct. MEASURED@this module's calibration probe (repo scratch, 2026-08-11, n=2000
random background pairs for percentile context):
    sofa/couch   (TRUE SYNONYM)      raw_cos=0.968
    happy/joyful (TRUE SYNONYM)      raw_cos=0.962
    apple/orange (SIBLING, DISTINCT) raw_cos=0.952   <- indistinguishable from the synonym pairs
    dog/cat      (SIBLING, DISTINCT) raw_cos=0.932   <- indistinguishable from the synonym pairs
    wood/coal    (SIBLING, DISTINCT) raw_cos=0.785
    wood/plastic (SIBLING, DISTINCT) raw_cos=0.919
Percentile-normalizing against the random-pair background does not rescue this: SIBLING_DISTINCT
and TRUE_SYNONYM pairs both land at/above the p95-p99.9 tail of the background distribution, fully
overlapping. This is a genuine, principled ceiling of PURE sensorimotor-profile similarity (it
measures "how do I perceive/interact with X", not "what X specifically IS") -- not a calibration
bug and not something a different threshold on this SAME metric can fix.

SAFE-BY-CONSTRUCTION RESPONSE: because the raw metric cannot be trusted above a certain magnitude
(true synonyms and false-positive siblings are statistically inseparable there), this module caps
its returned similarity at GROUNDED_CAP = 0.45, STRUCTURALLY BELOW
hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD (0.50, the hand lexicon's own same-idea/merge
convention). This guarantees, by construction (not by luck or per-pair tuning), that the grounded
fallback can NEVER trigger a same-idea/merge decision at the project's standard link threshold --
it extends OOV coverage with a real, correctly-ordered (related > unrelated) GRADED relatedness
signal in the sub-ceiling band, while being honest that it cannot assert high-confidence identity
matches the way the hand lexicon can for its covered vocabulary. Below the cap the ordering is
genuine (MEASURED: unrelated pairs cluster near 0 or negative, weak/moderate relatedness produces
intermediate values) -- only the TOP of the range is deliberately flattened.

VAD (Warriner) + AoA (Kuperman) norms also live in data/grounding_testbed/ but are NOT used here:
both are affect/acquisition-trajectory signals, not identity-content signals, and folding them in
would not address the sibling/synonym confound above (also verified: mixing an incomplete-coverage
source, ~13,915 Warriner words vs ~39,707 Lancaster words, forces an asymmetric zero-fill for the
majority of words, which is its own artifact). Left as a documented, available extension point, not
used in this v1.

DATA-CLEANING: Lancaster's `Word` column is upper-case with many multi-word phrase rows ("A
CAPPELLA"); Brysbaert's is lower-case, single tokens. Both are lower-cased and space/hyphen-
containing (multi-token) rows are dropped so the joined vocabulary is single-token, matching
concept_similarity's word-pair API.

Public API:
    grounded_vector(word) -> Optional[Tensor]      z-scored 12-dim float32 vector, or None if OOV
                                                     of the Lancaster/Brysbaert intersection.
    in_grounded_lexicon(word) -> bool
    grounded_similarity(word_a, word_b) -> Optional[float]   capped, clipped-to-[0, GROUNDED_CAP]
                                                     cosine, or None if either word is OOV.
    coverage_stats() -> dict
    self_test() -> dict
"""
from __future__ import annotations

import csv
import os
import statistics
from typing import Dict, List, Optional, Tuple

import torch

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LANCASTER_PATH = os.path.join(_REPO_ROOT, "data", "grounding_testbed",
                               "Lancaster_sensorimotor_norms_for_39707_words.csv")
_BRYSBAERT_PATH = os.path.join(_REPO_ROOT, "data", "grounding_testbed",
                               "Concreteness_ratings_Brysbaert_et_al_BRM.txt")

SENSORIMOTOR_COLS: List[str] = [
    "Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
    "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean",
]
CONCRETENESS_COL = "Conc.M"
N_GROUNDED_DIM = len(SENSORIMOTOR_COLS) + 1  # 12

# Structurally BELOW hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD (0.50) -- see module
# docstring "SAFE-BY-CONSTRUCTION RESPONSE". Not re-derived per query; a fixed architectural cap.
GROUNDED_CAP = 0.45

_table_cache: Optional[Dict[str, torch.Tensor]] = None  # word(lower) -> z-scored 12-dim vector


def _is_single_token(word: str) -> bool:
    return bool(word) and (" " not in word) and ("\t" not in word)


def _load_lancaster() -> Dict[str, List[float]]:
    out: Dict[str, List[float]] = {}
    with open(_LANCASTER_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            w = (row.get("Word") or "").strip()
            if not _is_single_token(w):
                continue
            try:
                vec = [float(row[c]) for c in SENSORIMOTOR_COLS]
            except (ValueError, KeyError, TypeError):
                continue
            out[w.lower()] = vec
    return out


def _load_brysbaert() -> Dict[str, float]:
    out: Dict[str, float] = {}
    with open(_BRYSBAERT_PATH, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            w = (row.get("Word") or "").strip()
            if not _is_single_token(w):
                continue
            try:
                c = float(row[CONCRETENESS_COL])
            except (ValueError, KeyError, TypeError):
                continue
            out[w.lower()] = c
    return out


def _build_table() -> Dict[str, torch.Tensor]:
    """Deterministic build: join Lancaster (sensorimotor) with Brysbaert (concreteness) on the
    lower-cased single-token intersection, z-score each of the 12 dims over that population
    (sorted(set()) discipline for cross-process determinism), return word(lower) -> float32
    tensor. Cached at module scope; only loaded on first grounded_vector/grounded_similarity
    call (lazy -- importing this module does not pay the CSV-parse cost)."""
    lanc = _load_lancaster()
    brys = _load_brysbaert()
    words = sorted(set(lanc.keys()) & set(brys.keys()))
    raw = [lanc[w] + [brys[w]] for w in words]
    ndim = N_GROUNDED_DIM
    means = [statistics.fmean(row[i] for row in raw) for i in range(ndim)]
    stds = [statistics.pstdev(row[i] for row in raw) or 1.0 for i in range(ndim)]
    table: Dict[str, torch.Tensor] = {}
    for w, row in zip(words, raw):
        z = [(row[i] - means[i]) / stds[i] for i in range(ndim)]
        table[w] = torch.tensor(z, dtype=torch.float32)
    return table


def _table() -> Dict[str, torch.Tensor]:
    global _table_cache
    if _table_cache is None:
        _table_cache = _build_table()
    return _table_cache


def grounded_vector(word: str) -> Optional[torch.Tensor]:
    """z-scored 12-dim [11 Lancaster sensorimotor means + Brysbaert concreteness] vector for
    `word`, or None if OOV of the Lancaster/Brysbaert single-token intersection.

    LEMMATISE-ON-MISS (2026-08-25, from SOLVED lookup_does_not_lemmatise). The table is exact-string,
    so inflected forms (countries, released) miss though their lemma is covered. On a MISS, retry the
    word's lemma via `lemma_word` (already live on the reading path). BRAIN-PINNED: inflectional
    morphology is stripped at the lexical interface BEFORE semantic access (masked morphological
    priming; Rastle & Davis 2008; Taft & Forster 1975). MEASURED on SimVerb/SimLex shown in REAL
    inflected surface forms: lemmatise-on-miss scores rho 0.206 where the live exact lookup is MUTE,
    clears the strongest floor CI-separated (+0.185 [+0.128,+0.232]), the info-free twin (random
    covered word) LOSES, and a gold-lemma BASE oracle ~= LEMMA; false-recovery ~0.1% (lives->life).
    ADDITIVE -- fires ONLY on a miss, never changes a covered word. Held-out proven; the read()-path
    gain still awaits the B5 adapter (do not bill this as a read() gain). `in_grounded_lexicon` is
    left EXACT on purpose: recovered-vector != declared-membership; use `grounded_vector(w) is not
    None` where the recovered coverage is what matters."""
    v = _table().get(word.lower())
    if v is not None:
        return v
    from hdlab.thematic_role_labeler import lemma_word   # already live on the reading path
    return _table().get(lemma_word(word.lower()))


def in_grounded_lexicon(word: str) -> bool:
    return word.lower() in _table()


def _raw_cos(a: torch.Tensor, b: torch.Tensor) -> float:
    na = torch.linalg.vector_norm(a)
    nb = torch.linalg.vector_norm(b)
    if float(na) < 1e-9 or float(nb) < 1e-9:
        return 0.0
    return float(torch.dot(a, b) / (na * nb))


def grounded_similarity(word_a: str, word_b: str) -> Optional[float]:
    """Capped, non-negative cosine similarity over the grounded (sensorimotor+concreteness)
    profile, or None if either word is OOV of the Lancaster/Brysbaert intersection. Range
    [0.0, GROUNDED_CAP] -- see module docstring "SAFE-BY-CONSTRUCTION RESPONSE" for why the cap
    exists and why it sits below hdlab.lexical_similarity.SIMILARITY_LINK_THRESHOLD."""
    va = grounded_vector(word_a)
    vb = grounded_vector(word_b)
    if va is None or vb is None:
        return None
    raw = _raw_cos(va, vb)
    return min(GROUNDED_CAP, max(0.0, raw))


def substitutability(word_a: str, word_b: str) -> Optional[float]:
    """The TAUGHT DISTRIBUTIONAL substitutability score -- the word-context channel this organ's
    norm-only `grounded_similarity` (capped at GROUNDED_CAP=0.45) structurally lacks, so that path pins
    synonyms (sofa/couch) and mere associates (apple/orange) alike at 0.45. Delegates to the landed
    `hdlab.distilled_substitutability` (an OFFLINE PPMI+SVD consolidation of the reading co-occurrence
    counts with a grounded-hub-TAUGHT direction; cleared the licensed 484-pair substitutability
    instrument at AUC 0.8388, beating the info-free twin's max). UNCAPPED; returns None if either word is
    out of the consolidated distributional vocabulary (the caller then falls back to `grounded_similarity`).
    DEFAULT-SEPARATE: a NEW channel -- the capped `grounded_similarity` above is UNCHANGED (every existing
    caller is byte-identical). Lazy import so a missing asset never breaks THIS module's load. Landed
    2026-08-30 from `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by` (Q111)."""
    from hdlab.distilled_substitutability import distilled_substitutability
    return distilled_substitutability(word_a, word_b)


# ---------------------------------------------------------------------------------------------
# THE ATL DISTINCTIVE-FEATURE (feature-similarity) READ-OUT -- default-separate, ADDITIVE.
# ---------------------------------------------------------------------------------------------
# Landed 2026-08-26 from problem the_substrate_has_one_meaning_system_where_the_brain_has_two
# (integrated PARTIAL/EXCELLENT). The brain has TWO similarity systems: the ATL amodal hub computes
# FEATURE / correlational similarity weighted toward DISTINCTIVE features (Patterson, Nestor & Rogers
# 2007; Lambon Ralph controlled-semantic-cognition), and a distributed system computes ASSOCIATIVE
# relatedness. This carrier's OWN docstring measures the ATL failure mode: raw cosine cannot separate a
# synonym from a perceptually-similar sibling (apple/orange 0.952 ~ sofa/couch) because a DOMINANT SHARED
# axis (concreteness / general salience -- the top principal component is ~27% of the variance) swamps the
# discriminating dims. The ATL's actual operation is that failure stated in reverse: PRIVILEGE DISTINCTIVE
# FEATURES == DECORRELATION -- WHITEN the shared covariance (equalise variance across principal axes). On
# HELD-OUT similarity golds the whitened rep beats RAW grounded cosine CI-separated (SimLex +0.046, SimVerb
# +0.023) and LOWERS relatedness (the brain signature -- specialises toward "alike-in-kind"). DEV-SELECTED
# (SimVerb-dev500): k_drop=0, whiten=True == pure whitening.
#
# This is a NEW, UNCAPPED MEANING-READ-OUT path (a ranking score). The capped grounded_similarity() LINK
# score above is UNCHANGED and byte-identical -- a cap would destroy a similarity RANKING, and this is not a
# link decision. Nothing calls this unless a consumer asks for the feature-similarity axis. MEASURE on the
# live read-out before any capability claim (per the SOLVED caution).

_distinctive_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None  # (mu[12], W[12,12])


def _distinctive_transform() -> Tuple[torch.Tensor, torch.Tensor]:
    """Fit + cache the ATL distinctive-feature WHITENING transform from the FULL grounding table:
    (mu, W) with W = eigvecs(cov) * 1/sqrt(eigvals) (k_drop=0, whiten=True, dev-selected). A word's
    feature vector is (grounded_vector(w) - mu) @ W. Fit on the whole population -- gold-blind by
    construction (the experiment's benchmark-exclusion only kept held-out EVAL words out of the fit,
    which is N/A at inference)."""
    global _distinctive_cache
    if _distinctive_cache is None:
        t = _table()
        X = torch.stack([t[w] for w in sorted(t)]).double()          # (N, 12) z-scored per dim
        mu = X.mean(dim=0)
        Xc = X - mu
        cov = (Xc.T @ Xc) / Xc.shape[0]
        evals, evecs = torch.linalg.eigh(cov)                        # ascending; k_drop=0 keeps all
        scale = 1.0 / torch.sqrt(evals + 1e-8)                        # whiten: equalise the variance
        W = evecs * scale.unsqueeze(0)                               # (12, 12) whitening projection
        _distinctive_cache = (mu, W)
    return _distinctive_cache


def distinctive_grounded_vector(word: str) -> Optional[torch.Tensor]:
    """The z-scored grounding vector WHITENED by the ATL distinctive-feature transform (suppress the
    dominant shared concreteness axis, privilege distinctive features). None if OOV. The raw
    grounded_vector() is unchanged; this is the additive feature-similarity read-out path."""
    v = grounded_vector(word)
    if v is None:
        return None
    mu, W = _distinctive_transform()
    return ((v.double() - mu) @ W)


def distinctive_grounded_similarity(word_a: str, word_b: str) -> Optional[float]:
    """Cosine over the distinctive-feature-WHITENED grounding vectors -- the ATL "alike-in-kind"
    (FEATURE-similarity) meaning read-out. UNCAPPED (a ranking score, not a link decision -- the capped
    grounded_similarity() is the link score and is unchanged). Beats raw grounded cosine CI-separated on
    held-out SimLex/SimVerb and specialises toward similarity (lowers relatedness). None if either OOV."""
    a = distinctive_grounded_vector(word_a)
    b = distinctive_grounded_vector(word_b)
    if a is None or b is None:
        return None
    return _raw_cos(a.float(), b.float())


def coverage_stats() -> dict:
    t = _table()
    return {"n_words": len(t), "n_dim": N_GROUNDED_DIM, "grounded_cap": GROUNDED_CAP}


def self_test() -> dict:
    """Coverage + ordering (synonym > unrelated) + anti-over-merge-by-construction + OOV-never-
    crashes + determinism + circularity(scramble) checks. Does NOT assert the raw metric can
    separate true synonyms from perceptually-similar-but-distinct siblings -- MEASURED@module
    docstring that it cannot; the cap is the honest response to that limit, not a claim it doesn't
    exist."""
    stats = coverage_stats()
    assert stats["n_words"] >= 30000, "SUPPLY REGRESSION: grounded table coverage collapsed (%d words)" % stats["n_words"]

    # (1) never crashes on OOV; never links OOV.
    assert grounded_similarity("wood", "not_a_real_word_zzz99") is None
    assert not in_grounded_lexicon("not_a_real_word_zzz99")

    # (2) ordering: TRUE_SYNONYM pairs score meaningfully higher than a genuinely UNRELATED pair,
    # and everything returned is capped in [0, GROUNDED_CAP] by construction.
    sim_synonym = grounded_similarity("sofa", "couch")
    sim_unrelated = grounded_similarity("stone", "idea")
    assert sim_synonym is not None and sim_unrelated is not None
    assert 0.0 <= sim_synonym <= GROUNDED_CAP, "CAP VIOLATION: %r" % sim_synonym
    assert 0.0 <= sim_unrelated <= GROUNDED_CAP, "CAP VIOLATION: %r" % sim_unrelated
    assert sim_synonym > sim_unrelated, (
        "ORDERING FAILURE: synonym pair (sofa,couch)=%.4f must exceed unrelated pair (stone,idea)=%.4f"
        % (sim_synonym, sim_unrelated))

    # (3) anti-over-merge-by-construction: the cap sits strictly below the hand lexicon's
    # same-idea/merge threshold (0.50), so NOTHING this module returns can ever cross it.
    assert GROUNDED_CAP < 0.50, "SAFETY VIOLATION: GROUNDED_CAP must stay below SIMILARITY_LINK_THRESHOLD(0.50)"
    for a, b in (("wood", "coal"), ("apple", "orange"), ("dog", "cat"), ("wood", "plastic")):
        s = grounded_similarity(a, b)
        assert s is not None and s <= GROUNDED_CAP, "CAP VIOLATION on sibling pair (%s,%s)=%r" % (a, b, s)

    # (4) glass-box determinism: same word twice -> bit-identical vector.
    v1 = grounded_vector("wood")
    v2 = grounded_vector("wood")
    assert torch.equal(v1, v2), "GLASS-BOX FAILURE: same word must reproduce bit-identical vector"

    # (5) circularity: a SCRAMBLED word->vector assignment (fixed disjoint seed) must collapse the
    # MEAN synonym-pair raw-cosine gain -- proves the mechanism earns its ordering from genuine
    # per-word sensorimotor/concreteness content, not an artifact of the z-scoring/cap machinery
    # alone. Compared on RAW (uncapped) cosine -- real synonym pairs saturate the cap (raw >> 0.45
    # for most), so a capped-vs-capped comparison would trivially collide at the ceiling. Averaged
    # over 5 independent synonym pairs (not a single pair/seed) because this feature space has a
    # heavy-tailed background cosine distribution (a dominant shared "concreteness" axis means even
    # a SINGLE scrambled/random pair can land at moderate-high cosine by chance -- MEASURED@dev
    # calibration probe p90=0.57 of the random-pair background); averaging 5 pairs under the SAME
    # fixed-seed scramble suppresses that single-pair noise so the assertion is robust, not
    # cherry-picked to one lucky seed.
    words = sorted(_table().keys())
    gen = torch.Generator().manual_seed(999)
    perm = torch.randperm(len(words), generator=gen).tolist()
    scrambled = {words[i]: _table()[words[perm[i]]] for i in range(len(words))}
    synonym_pairs = [("sofa", "couch"), ("trash", "garbage"), ("shout", "yell"),
                     ("whisper", "murmur"), ("happy", "joyful")]
    real_raws = [_raw_cos(_table()[a], _table()[b]) for a, b in synonym_pairs]
    scr_raws = [_raw_cos(scrambled[a], scrambled[b]) for a, b in synonym_pairs]
    mean_real_raw = statistics.fmean(real_raws)
    mean_scr_raw = statistics.fmean(scr_raws)
    assert (mean_real_raw - mean_scr_raw) >= 0.30, (
        "CIRCULARITY FAILURE: scrambling word->vector assignment must collapse the mean synonym-"
        "pair raw-cosine gain (mean_real_raw=%.4f mean_scrambled_raw=%.4f delta=%.4f < 0.30)"
        % (mean_real_raw, mean_scr_raw, mean_real_raw - mean_scr_raw))

    return {
        "n_words": stats["n_words"],
        "grounded_cap": GROUNDED_CAP,
        "sim_sofa_couch": round(sim_synonym, 4),
        "sim_stone_idea": round(sim_unrelated, 4),
        "mean_synonym_raw": round(mean_real_raw, 4),
        "mean_synonym_raw_scrambled": round(mean_scr_raw, 4),
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
