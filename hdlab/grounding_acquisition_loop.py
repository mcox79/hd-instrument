"""hdlab/grounding_acquisition_loop.py -- closed self-growing grounding loop (2026-08-09).

FLAG -> LIBRARY -> CONSOLIDATE ("sleep") -> GUARD (schema-consistency, escalate-don't-force-commit)
-> BANK. Wires hdlab.consequence_learning_loop's already-built propose/credit/teacher-verdict half
(FLAG) to a NEW trace-level library (this module) whose periodic consolidation pass gates every
BANK decision on a SCHEMA-CONSISTENCY signal computed over the item's own accumulated CONTEXT
vectors, independent of vote agreement. This is the missing piece the acquisition drill identified:
prior attempts (word_acquisition_loop.combine_votes, consequence_learning_loop.consolidate) gate
purely on VOTE agreement/margin; Warren et al. 2014 (vmPFC lesion, DRM) found that the SAME
schema-integration circuit that fast-tracks true learning also manufactures false memories, so
vote-agreement alone is exactly the failure mode a genuine anti-false-memory guard must catch, not
merely assume away.

Cites: notes/research_psych_acquisition_consolidation_loop_2026-08-09.md (full design + literature:
Dumay & Gaskell 2007 sleep-not-just-time word integration; Tamminen et al. 2010 replay-budget;
van Kesteren et al. 2012 SLIMM schema-gate; Warren et al. 2014 false-consolidation double-edge).
preregs/2026-08-09_grounding_acquisition_loop_v1.md (bands, config, deviations from the drill's
literal design -- notably: a split-half context-coherence metric standing in for a full FHRR/
hippocampal-encoder CA3-complete wiring, reusing exp_confidence_gated_codebook_consolidation_v1's
SPLIT-HALF RELIABILITY *shape* (test-retest consistency across two disjoint evidence slices),
applied to per-encounter bag-of-content-words context vectors instead of PPMI co-occurrence rows).

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim):
  hdlab.consequence_learning_loop.credit_window / teacher_verdict   (FLAG: OOV outcome-verb credit
                                                                      scan + episode teacher label)
  hdlab.self_improving_loop.decide_keep_or_revert                   (abstain-band vote-margin gate,
                                                                      byte-identical idiom to
                                                                      consequence_learning_loop.consolidate)
  hdlab.verb_lexical_similarity.register_acquired_outcome / in_lexicon   (BANK write-back, overlay)
  hdlab.hd_fact_store.HDFactStore                                   (BANK write-back, NATIVE -- see
                                                                      PROMOTE below, 2026-08-10)

PROMOTE (2026-08-10, notes/research_brain_scaffolding_that_fades_2026-08-10.md +
notes/research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md): consolidation_pass's BANK step
previously wrote ONLY into verb_lexical_similarity's flat overlay dict -- a permanent side-table,
never merged into any natively-read structure, which those two drills independently found makes the
"crutch fades" claim structurally impossible (an annotation, not a migration). This module now
OPTIONALLY (native_store=None preserves prior behavior byte-for-byte) also PROMOTES a banked item
into hdlab.hd_fact_store.HDFactStore's trust-bound representation, gated by a THIRD, independent
condition on top of the existing two (vote-margin abstain-band + schema-consistency split-half):
EXPOSURE (len(traces)) >= promote_min_exposure AND MAPPING-CONSISTENCY (abs(vote_margin)) >=
promote_min_consistency. This operationalizes Logan 1988 (Instance Theory: exposure count predicts
automaticity) and Schneider & Shiffrin 1977 (automaticity requires CONSISTENT mapping, not just
enough repetitions) as the promotion gate -- schema-coherence licenses BANKING (an "associative"
stage, Fitts & Posner 1967), but promotion to native/autonomous requires the stricter, independent
consistency bar this drill's Test A exists to validate. The existing false-memory guard
(schema_consistency_split_half) is NEVER loosened by this addition -- an item that fails it still
never reaches the BANK branch at all, so it structurally cannot promote either.

GENUINELY-NEW code here: context_vector (deterministic bag-of-content-words bipolar bundle, glass-
box, hashlib-seeded per PROT-023/F.5 -- never Python hash()), Library/LibraryItem/Trace (the
not-yet-grounded store, trace-level not counter-level -- traces are kept SEPARATE per Trueswell
propose-verify / the 07-28 audit's own core finding, never folded/averaged at intake),
schema_consistency_split_half (the guard signal), surprise_order (Tamminen/Rasch selective-replay
ordering, diagnostic), consolidation_pass (the periodic "sleep" pass: vote-margin gate AND
schema-consistency gate AND the Dumay-Gaskell intervening-pass rule, ESCALATE-don't-force-commit on
patience exhaustion -- ANY gate failing defers, never forces a commit).

ASCII-only. NumPy; deterministic integer/hashlib seeding throughout (no built-in hash(), no
list(set()) ordering -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from hdlab.consequence_learning_loop import (  # noqa: F401 (credit_window re-exported for callers)
    credit_window, _credit_targets, teacher_verdict,
)
from hdlab.self_improving_loop import decide_keep_or_revert
from hdlab.verb_lexical_similarity import register_acquired_outcome, in_lexicon
from hdlab.hd_fact_store import HDFactStore  # noqa: F401 (PROMOTE target; real code path, not a stub)

# ---- config (mine to set per exp_dev Autonomy grant; documented + justified in the pre-reg) ----
D = 256                      # context bipolar vector dimensionality
MIN_CONFIRM = 4                # schema_consistency_split_half needs >=2 traces PER HALF (n>=4) to
                                # ever produce a score; MIN_CONFIRM=4 (not consequence_learning_loop's
                                # 3) keeps "reached min_confirm" and "schema-scoreable" coincident so
                                # no item wastes patience while merely under-evidenced (see
                                # consolidation_pass: schema_score is None -> defer, no patience cost).
NEUTRAL_BAND = 0.34           # matches hdlab.consequence_learning_loop.NEUTRAL_BAND
PATIENCE_MAX = 3              # consolidation passes an item may fail the guard before ESCALATED
PROMOTE_MIN_EXPOSURE = 8       # native-promotion exposure floor (Logan 1988 instance count); strictly
                                # above MIN_CONFIRM=4 -- "eligible to bank" != "eligible to promote"
PROMOTE_MIN_CONSISTENCY = 0.75  # native-promotion |vote_margin| floor (Schneider & Shiffrin 1977
                                # consistent-mapping); strictly above NEUTRAL_BAND=0.34's banking bar
                                # -- a coherent-context item can bank (associative) on a much weaker
                                # vote margin than it needs to promote (autonomous).
PROMOTE_RELATION = "OUTCOME_POLARITY"  # hd_fact_store relation name for a promoted grounding

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by", "for", "with",
    "as", "is", "was", "were", "are", "be", "been", "being", "it", "its", "he", "she", "they",
    "him", "her", "them", "his", "their", "i", "you", "we", "me", "my", "your", "our", "this",
    "that", "these", "those", "not", "no", "so", "than", "then", "there", "here", "up", "out",
    "into", "over", "again", "very", "just", "would", "could", "should", "will", "shall", "can",
    "did", "do", "does", "had", "has", "have", "from", "all", "any", "some", "one", "two", "when",
    "what", "who", "which", "how", "why", "said", "upon",
})


def context_vector(window_text: str, d: int = D) -> np.ndarray:
    """Deterministic bag-of-content-words bipolar bundle (Kanerva random-indexing / BEAGLE-style
    context encoding). Each content word's vector = a hashlib.sha256-seeded bipolar draw (fixed
    across every call, no external embedding, no torch.Generator state to thread); the trace's
    context = sign(sum of its content words' vectors). Deterministic, PROT-023/F.5-compliant
    (hashlib, not built-in hash()). Returns an all-zero vector if the window has no content word
    (caller must guard cosine against a zero-norm vector -- see _cos)."""
    words = [w for w in re.findall(r"[a-z']+", window_text.lower())
             if w not in _STOPWORDS and len(w) > 2]
    if not words:
        return np.zeros(d, dtype=np.float64)
    acc = np.zeros(d, dtype=np.float64)
    for w in words:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2**32)
        rng = np.random.default_rng(seed)
        acc += rng.choice([-1.0, 1.0], size=d)
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """sign(sum(vecs)); zero entries broken toward +1 (bipolar cleanup, matches predictive_coding.py
    convention)."""
    out = np.sign(np.sum(vecs, axis=0))
    out[out == 0] = 1.0
    return out


@dataclass
class Trace:
    """One INDEPENDENT episode's evidence for a library item. Kept separate, never folded/averaged
    at intake (Trueswell propose-verify / the 07-28 audit's core finding)."""
    episode_id: str
    pole: str                  # "POS" | "NEG"  (MET->POS / UNMET->NEG, matching consequence_learning_loop)
    context_vec: np.ndarray
    pass_idx: int               # the pass this trace was recorded


@dataclass
class LibraryItem:
    lemma: str
    traces: List[Trace] = field(default_factory=list)
    status: str = "PENDING"     # PENDING | GROUNDED_POS | GROUNDED_NEG | GROUNDED_NEUTRAL | ESCALATED
    first_min_confirm_pass: Optional[int] = None
    patience: int = 0


class Library:
    """The not-yet-grounded store. Keyed by lemma-or-construction-signature (here: outcome-verb
    lemma, matching consequence_learning_loop's existing keying)."""

    def __init__(self) -> None:
        self.items: Dict[str, LibraryItem] = {}

    def flag(self, lemma: str, episode_id: str, pole: str, context_vec: np.ndarray,
             pass_idx: int) -> bool:
        """Append one trace. No-ops (returns False) for an item that already reached a terminal
        status (GROUNDED_* / ESCALATED) -- terminal items accept no further evidence. Returns True
        iff a trace was actually appended."""
        it = self.items.get(lemma)
        if it is None:
            it = LibraryItem(lemma=lemma)
            self.items[lemma] = it
        if it.status != "PENDING":
            return False
        it.traces.append(Trace(episode_id, pole, context_vec, pass_idx))
        return True


def schema_consistency_split_half(traces: List[Trace]) -> Optional[float]:
    """Split-half context-coherence (reuses exp_confidence_gated_codebook_consolidation_v1's
    split-by-position reliability SHAPE -- there: two independent PPMI builds over disjoint token
    halves; here: two independent context-vector bundles over disjoint TRACE halves, ordered by
    accumulation order not shuffled). Returns None (defer, not zero) if fewer than 2 traces exist
    per half -- an under-evidenced item cannot yet be schema-scored, distinct from a genuinely
    LOW score.

    Uses the RAW (non-sign-cleaned) sum of each half's context vectors, not the bipolar-cleaned
    bundle context_vector() itself returns: sign-cleanup's zero-tie-break-to-+1 convention (matches
    predictive_coding.py's own bipolar-cleanup convention) injects a systematic POSITIVE bias into
    the cosine between any two SMALL (e.g. 2-item) independently-random bundles, since ~50% of
    coordinates tie at 0 and both sides break the SAME direction -- confirmed empirically (self_test
    below caught a spurious 0.36 cosine between two independent noise bundles-of-2 under sign-
    cleanup). Cosine of the raw (uncleaned) sums has no such artifact and is the correct metric for
    a smooth reliability signal (we are not requesting a clean concept symbol here, just a coherence
    SCORE)."""
    n = len(traces)
    if n < 4:            # need >=2 traces per half for a non-degenerate split
        return None
    half = n // 2
    a, b = traces[:half], traces[half:]
    va = np.sum([t.context_vec for t in a], axis=0)
    vb = np.sum([t.context_vec for t in b], axis=0)
    return _cos(va, vb)


def surprise_order(traces: List[Trace]) -> List[Trace]:
    """Order traces by disagreement-with-the-bundle-of-the-OTHERS (Tamminen/Rasch selective-replay:
    highest-disagreement-with-the-rest first, i.e. the trace the running schema would predict
    LEAST well is replayed first). Diagnostic / logged (matches the v6 design's surprise-ordering
    leg); does not itself gate anything -- consolidation_pass uses the split-half score, not this
    order, to decide eligibility."""
    if len(traces) < 2:
        return list(traces)
    scored = []
    for i, t in enumerate(traces):
        others = [o.context_vec for j, o in enumerate(traces) if j != i]
        bundle = _bundle(others)
        scored.append((1.0 - _cos(t.context_vec, bundle), t))
    scored.sort(key=lambda x: -x[0])
    return [t for _, t in scored]


def _vote_margin(traces: List[Trace]) -> Tuple[float, int, int]:
    n = len(traces)
    pos = sum(1 for t in traces if t.pole == "POS")
    neg = n - pos
    margin = (pos - neg) / n if n else 0.0
    return margin, pos, neg


def consolidation_pass(library: Library, pass_idx: int, *,
                        min_confirm: int = MIN_CONFIRM,
                        schema_thresh: float = 0.10,
                        neutral_band: float = NEUTRAL_BAND,
                        patience_max: int = PATIENCE_MAX,
                        register: bool = True,
                        mdl_gate_fn: Optional[Callable[["LibraryItem"], bool]] = None,
                        native_store: Optional["HDFactStore"] = None,
                        promote_min_exposure: int = PROMOTE_MIN_EXPOSURE,
                        promote_min_consistency: float = PROMOTE_MIN_CONSISTENCY,
                        promote_relation: str = PROMOTE_RELATION,
                        promote_source: str = "grounding_acquisition_loop") -> dict:
    """One offline 'sleep' pass over the WHOLE library (Diekelmann & Born: offline, separate from
    the reading/FLAG pass). For each PENDING item with >= min_confirm traces:
      1. mark first_min_confirm_pass on the FIRST pass this threshold is reached (if not yet set).
      2. Dumay & Gaskell intervening-pass rule: an item may NOT integrate on the very pass it first
         becomes eligible -- it must survive to a LATER pass, matching sleep-dependent (not just
         elapsed-time) word integration. This pass costs NO patience (it is a structural wait, not
         a failed evaluation).
      3. On any pass where intervening_pass_ok: compute vote_margin (POS/NEG tally) and the
         schema-consistency split-half score. BANK (GROUNDED_POS/NEG/NEUTRAL) iff schema_score is
         non-None AND schema_score >= schema_thresh (the mandatory guard -- vote agreement ALONE
         never banks anything, per Warren et al. 2014's same-circuit false-memory finding). Else
         increment patience; at patience_max -> ESCALATED (terminal, NEVER force-committed).

    mdl_gate_fn (optional, CONJUNCTIVE -- AND, never OR, with the schema-consistency check; see
    preregs/2026-08-09_learner_mdl_gate_on_acquisition_traces_v1.md): when provided, called as
    mdl_gate_fn(item) -> bool ONLY on passes where schema_score >= schema_thresh already holds (the
    schema check remains a NECESSARY condition regardless of what mdl_gate_fn returns -- this is
    the structural guarantee that the existing false-consolidation guard invariants can never be
    WEAKENED by adding this gate, only made stricter). A False mdl_gate_fn verdict is treated
    identically to a schema-check failure: patience increments, no forced commit. Default None
    preserves the exact prior behavior byte-for-byte (the ternary below reduces to `if schema_ok`).
    Operationalizes Ghosh & Gilboa (2014)'s 'non-specific/abstracted structure' schema criterion via
    hdlab.learner's MDL two-part-code compression gate (Perfors & Tenenbaum 2009), as a SECOND,
    independent test of whether the item's own accumulated evidence is genuinely compressible, not
    merely internally coherent by the cosine-based split-half metric alone.

    native_store (2026-08-10, optional -- default None preserves prior behavior byte-for-byte): when
    provided, every item that BANKS as GROUNDED_POS/GROUNDED_NEG is ALSO evaluated for PROMOTION into
    native_store's trust-bound (s,r,o) representation, gated on exposure (len(traces)) >=
    promote_min_exposure AND consistency (abs(vote_margin)) >= promote_min_consistency -- a strictly
    STRONGER, independent bar than banking's own (schema_thresh, neutral_band) gates (see module
    docstring PROMOTE section). GROUNDED_NEUTRAL items never promote (no directional fact to assert).
    promote_min_exposure/promote_min_consistency default to the module constants but are NOT
    hard-coded into the gate logic -- a caller (e.g. a research cell) may vary them, which is exactly
    what lets Test A probe the threshold's shape. Every BANK-branch item (grounded, any label) gets a
    `promotion_log` entry recording exposure/consistency/label/promoted, whether or not native_store
    was supplied (promoted is always False when native_store is None) -- this is what lets a caller
    later correlate native coverage against the two fade predictors without re-deriving them.

    Returns a per-pass report dict; mutates `library` in place."""
    newly_grounded = {"POS": [], "NEG": [], "NEUTRAL": []}
    newly_escalated: List[str] = []
    promotion_log: List[dict] = []
    for lemma in sorted(library.items):
        it = library.items[lemma]
        if it.status != "PENDING":
            continue
        n = len(it.traces)
        if n < min_confirm:
            continue
        if it.first_min_confirm_pass is None:
            it.first_min_confirm_pass = pass_idx
        if pass_idx <= it.first_min_confirm_pass:
            continue  # mandatory intervening-pass wait; not a failure, no patience cost
        schema_score = schema_consistency_split_half(it.traces)
        if schema_score is None:
            continue  # insufficient evidence for a split yet (should not occur once n>=MIN_CONFIRM=4,
                       # but defensive: defer, no patience cost -- not-enough-evidence is not a guard
                       # FAILURE, it's an open question more exposure may still answer)
        schema_ok = schema_score >= schema_thresh
        # mdl_gate_fn only ever CONSULTED when schema already passes (AND semantics); when
        # mdl_gate_fn is None (default) or schema_ok is False, mdl_ok is vacuously True/irrelevant
        # -- the `schema_ok and mdl_ok` check below is then identical to the original `schema_ok`
        # check, byte-for-byte, so this is a strictly additive, backward-compatible change.
        mdl_ok = mdl_gate_fn(it) if (schema_ok and mdl_gate_fn is not None) else True
        if schema_ok and mdl_ok:
            margin, pos, neg = _vote_margin(it.traces)
            vote = decide_keep_or_revert({"POS": margin, "NEG": -margin},
                                         abstain_band=neutral_band - 1e-9)
            label = vote if vote is not None else "NEUTRAL"
            it.status = f"GROUNDED_{label}"
            if register and label in ("POS", "NEG"):
                register_acquired_outcome(lemma, label)
            newly_grounded[label].append(lemma)
            # ---- PROMOTE: overlay-bank (above) is NOT native-promotion. A THIRD, independent gate
            # (exposure AND consistency, both strictly stronger than banking's own thresholds) decides
            # whether this item ALSO migrates into native_store. schema_ok being True here is a
            # NECESSARY-for-bank precondition, never a sufficient-for-promote one -- a coherent-context
            # item with a merely-adequate (not highly consistent) vote history banks but must not
            # promote (this is the guard Test A vets hardest; see module PROMOTE docstring).
            exposure = n
            consistency = abs(margin)
            promoted = False
            if (native_store is not None and label in ("POS", "NEG")
                    and exposure >= promote_min_exposure
                    and consistency >= promote_min_consistency):
                trust_sym = "TRUST_HIGH" if consistency >= 0.9 else "TRUST_MID"
                native_store.store(lemma, promote_relation, label, promote_source, trust_sym)
                promoted = True
            promotion_log.append({"lemma": lemma, "exposure": exposure,
                                  "consistency": round(consistency, 6), "label": label,
                                  "promoted": promoted})
        else:
            it.patience += 1
            if it.patience >= patience_max:
                it.status = "ESCALATED"
                newly_escalated.append(lemma)
    return {
        "pass": pass_idx,
        "newly_grounded_pos": newly_grounded["POS"],
        "newly_grounded_neg": newly_grounded["NEG"],
        "newly_grounded_neutral": newly_grounded["NEUTRAL"],
        "newly_escalated": newly_escalated,
        "cumulative_grounded": sum(1 for i in library.items.values() if i.status.startswith("GROUNDED")),
        "cumulative_grounded_polar": sum(1 for i in library.items.values()
                                         if i.status in ("GROUNDED_POS", "GROUNDED_NEG")),
        "cumulative_escalated": sum(1 for i in library.items.values() if i.status == "ESCALATED"),
        "cumulative_pending": sum(1 for i in library.items.values() if i.status == "PENDING"),
        "promotion_log": promotion_log,
    }


def self_test() -> dict:
    """Fast off-disk gate exercising the REAL code path (real credit_window call on hand-authored
    micro-episodes, not a synthetic-only branch), per exp_dev SCHEMA-VET F.1."""
    # (1) context_vector: deterministic + content-sensitive.
    v1 = context_vector("The lantern flickered in the storm.")
    v2 = context_vector("The lantern flickered in the storm.")
    assert np.array_equal(v1, v2), "context_vector is non-deterministic"
    v3 = context_vector("The dragon roared over the mountain kingdom.")
    assert _cos(v1, v3) < 0.5, "unrelated windows should not bundle to near-identical vectors"
    assert np.all(context_vector("the a an of to") == 0.0), "all-stopword window must be all-zero"

    # (2) schema_consistency_split_half: coherent-repeat vs incoherent-scramble discriminate.
    coherent_traces = [Trace(f"e{i}", "POS", context_vector("Nell fixed the lantern by the fire."), 1)
                       for i in range(4)]
    coherent_score = schema_consistency_split_half(coherent_traces)
    assert coherent_score is not None and coherent_score > 0.95, (
        f"identical-context traces must split-half near cos=1.0, got {coherent_score}")
    rng = np.random.default_rng(0)
    scrambled_traces = [Trace(f"s{i}", "POS", rng.choice([-1.0, 1.0], size=D), 1) for i in range(4)]
    scrambled_score = schema_consistency_split_half(scrambled_traces)
    assert scrambled_score is not None and abs(scrambled_score) < 0.35, (
        f"independent-random-noise traces must split-half near cos=0.0, got {scrambled_score}")
    assert coherent_score > scrambled_score + 0.3, "discriminant-validity: coherent must clear scrambled"
    assert schema_consistency_split_half(coherent_traces[:3]) is None, "n=3 (<4) must defer (None), not score"

    # (3) Library.flag: appends + terminal no-op.
    lib = Library()
    assert lib.flag("catch", "e0", "POS", v1, 1) is True
    it = lib.items["catch"]
    assert len(it.traces) == 1
    it.status = "ESCALATED"
    assert lib.flag("catch", "e1", "POS", v1, 2) is False, "terminal item must reject new traces"
    assert len(lib.items["catch"].traces) == 1

    # (4) consolidation_pass: intervening-pass rule + guard-gated banking, real coherent item.
    lib2 = Library()
    for i in range(4):
        lib2.flag("mendtest", f"m{i}", "POS", context_vector("Owen mended the boat before the storm."), 1)
    r1 = consolidation_pass(lib2, 1, min_confirm=3, schema_thresh=0.10, register=False)
    assert lib2.items["mendtest"].status == "PENDING", (
        "must NOT ground on the very pass it first reaches min_confirm (Dumay-Gaskell rule)")
    assert r1["cumulative_grounded"] == 0
    r2 = consolidation_pass(lib2, 2, min_confirm=3, schema_thresh=0.10, register=False)
    assert lib2.items["mendtest"].status == "GROUNDED_POS", (
        f"coherent-context+consistent-vote item must ground on the intervening pass, got "
        f"{lib2.items['mendtest'].status}")
    assert "mendtest" in r2["newly_grounded_pos"]

    # (5) consolidation_pass: the guard REJECTS consistent-vote-but-scrambled-context (false-
    # consolidation can-fail case) -- must ESCALATE after patience_max, never GROUND.
    lib3 = Library()
    rng2 = np.random.default_rng(1)
    for i in range(4):
        lib3.flag("adversarialtest", f"a{i}", "POS", rng2.choice([-1.0, 1.0], size=D), 1)
    for p in range(1, 6):
        consolidation_pass(lib3, p, min_confirm=3, schema_thresh=0.10, patience_max=3, register=False)
    assert lib3.items["adversarialtest"].status == "ESCALATED", (
        f"scrambled-context item with consistent votes must ESCALATE not GROUND, got "
        f"{lib3.items['adversarialtest'].status}")

    # (6) real-code-path: actually call the REUSED hdlab.consequence_learning_loop referent-linked
    # credit scan on its own hand-authored micro-episode (not a synthetic-only branch). Uses
    # _credit_targets directly (byte-identical to consequence_learning_loop.self_test's own check)
    # since this particular window has no teacher_verdict (credit_window would return None for a
    # reason orthogonal to what this check tests: referent-linked OOV credit-scanning itself).
    g_lantern = "Nell wanted to fix the lantern before the guests came"
    win_credit = "Nell tinkered the lantern and the savings dwindled in the drawer."
    tgts = _credit_targets(win_credit, "lantern")
    assert "tinker" in tgts, f"real _credit_targets call did not credit 'tinker' as expected, got {tgts}"
    # and teacher_verdict (the OTHER real half credit_window composes) on a pair that DOES fire.
    g_save = "Owen wanted to save the boat before the storm hit"
    win_unmet = "The men worked hard. The boat sank in the storm."
    tv = teacher_verdict(g_save, win_unmet, signal_mode="signal_a_only")
    assert tv == "UNMET", f"real teacher_verdict call did not fire UNMET as expected, got {tv}"
    # credit_window itself composes both (verified separately above since this particular hand-
    # authored pair has no NOVEL credit target -- 'sank' is already lexicon-known -- exactly why
    # consequence_learning_loop.py's own self_test tests these two halves on separate examples too).
    assert credit_window(g_save, win_unmet, "boat", signal_mode="signal_a_only") is None, (
        "credit_window must return None when teacher fires but no OOV target is referent-linked")

    # (7) PROMOTE connector: real HDFactStore, real code path (not a synthetic-only branch).
    # 7a. high-exposure, highly-consistent, coherent-context item MUST bank AND promote.
    store = HDFactStore(n_dim=1024, seed=7)
    lib4 = Library()
    ctx_ok = context_vector("Nell repaired the engine before the harvest.")
    for i in range(8):
        lib4.flag("repairtest", f"r{i}", "POS", ctx_ok, 1)
    consolidation_pass(lib4, 1, min_confirm=4, schema_thresh=0.10, register=False, native_store=store,
                       promote_min_exposure=8, promote_min_consistency=0.75)
    r_promote = consolidation_pass(lib4, 2, min_confirm=4, schema_thresh=0.10, register=False,
                                   native_store=store, promote_min_exposure=8,
                                   promote_min_consistency=0.75)
    assert lib4.items["repairtest"].status == "GROUNDED_POS"
    assert any(e["lemma"] == "repairtest" and e["promoted"] for e in r_promote["promotion_log"]), (
        f"high-exposure consistent item must promote, log={r_promote['promotion_log']}")
    native_hit = store.query("repairtest", "OUTCOME_POLARITY")
    assert native_hit and native_hit[0]["object"] == "POS", (
        f"promoted fact must be readable lookup-free from hd_fact_store, got {native_hit}")

    # 7b. GUARD: same coherent context, same exposure count, but a merely-adequate (not highly
    # consistent) vote history -- must BANK (clears the low banking bar) but must NOT promote (fails
    # the strictly-stronger consistency bar). This is the sharp case DRILL 2 named: banking's own
    # vote-margin gate is much weaker than genuine automaticity requires.
    lib5 = Library()
    for i in range(6):
        lib5.flag("weaktest", f"w{i}", "POS", ctx_ok, 1)
    for i in range(2):
        lib5.flag("weaktest", f"wn{i}", "NEG", ctx_ok, 1)
    consolidation_pass(lib5, 1, min_confirm=4, schema_thresh=0.10, register=False, native_store=store,
                       promote_min_exposure=8, promote_min_consistency=0.75)
    r_guard = consolidation_pass(lib5, 2, min_confirm=4, schema_thresh=0.10, register=False,
                                 native_store=store, promote_min_exposure=8,
                                 promote_min_consistency=0.75)
    assert lib5.items["weaktest"].status == "GROUNDED_POS", (
        f"margin=0.5 (6 POS/2 NEG) must clear the banking bar (>0.34), got "
        f"{lib5.items['weaktest'].status}")
    assert not any(e["lemma"] == "weaktest" and e["promoted"] for e in r_guard["promotion_log"]), (
        f"consistency=0.5 (<0.75 promote floor) item must NOT promote despite banking, "
        f"log={r_guard['promotion_log']}")
    assert store.query("weaktest", "OUTCOME_POLARITY") == [], (
        "guard leak: an inconsistent-but-banked item is readable from native_store")

    return {
        "context_vector_deterministic": True,
        "schema_metric_discriminant_valid": True,
        "coherent_score": round(coherent_score, 4),
        "scrambled_score": round(scrambled_score, 4),
        "intervening_pass_rule_ok": True,
        "guard_rejects_scrambled_context_ok": True,
        "real_credit_window_exercised": True,
        "native_promotion_connector_ok": True,
        "native_promotion_guard_holds_ok": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
    print("ALL SELF-TESTS PASSED")
