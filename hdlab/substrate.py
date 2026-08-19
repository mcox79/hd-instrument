"""hdlab/substrate.py -- THE ASSEMBLED SUBSTRATE. One object that holds the organs and runs them.

WHY THIS FILE EXISTS (owner, 2026-08-18): "we need to have a current best substrate is my
assumption. you talk about parts wired into it -- we should envision a complete substrate (or
close to) and wire in the best versions of each."

Until this file existed, "wired" was a word. 163 modules import cleanly, 83 of 87 self-tests pass,
and 67 organs were built, passing and unreachable from any live entry point. This is the entry
point that reaches them.

WHAT IT IS BUILT ON, AND WHY NOT A PARALLEL PATH. `prelim_tier` and `foundation_persistence` both
key off `ReadingLoopState`, which belongs to `reading_grounding_loop` -- a LIVE entry point. The
adapter layer this assembly needs mostly already exists inside that loop. So this module WRAPS the
live path and wires the unwired organs INTO it. Authoring a second ingest path would produce a
second thing to audit instead of one thing that works (WIRE-DON'T-ISLAND, owner 2026-07-25/08-02).

THREE RULES THIS MODULE ENFORCES ON ITSELF, each earned by a measured failure:

  1. EVERY ORGAN IS BUILT LAZILY, ON FIRST USE. Importing this module builds nothing. On
     2026-08-19 `situation_reader` was found running a full training pass AT IMPORT TIME -- 190 s
     of its 205 s import -- which timed out its own self-test and kept a working organ off every
     wire list. Rebuilding that defect one layer up, where it would be paid by everything, is the
     obvious way to lose the fix.

  2. AN ORGAN THAT IS IMPORTED AND NEVER CALLED IS NOT WIRED. Every organ access goes through
     `_organ()`, which counts invocations, and the self-test asserts the counts are non-zero. The
     2026-08-13 accounting found 33 modules that self-tested PASS, were registered WIRED, and were
     absent from the live closure. A registry row is not evidence; a call count is.

  3. `organ_report()` CARRIES THREE STATES, NOT TWO. FILLED / NEEDS_ADAPTER / EMPTY. An organ that
     works but whose input nothing upstream produces is NEEDS_ADAPTER, never FILLED -- counting one
     as filled is exactly the false coverage that made "2,678 HARD_PASS" read as 2,678 wins.
     EXCLUDED is a fourth state and it is deliberate: three organs pass their own self-test AND are
     measurably inert, and the reason travels with the row.

WHAT THIS DOES AND DOES NOT DO, STATED PLAINLY SO NOBODY OVERREADS IT.
  IT DOES: read a corpus it chose off a shelf of 36, extract definitions from running prose, flag
  genuinely-unknown words, write each encounter one-shot into a sparse episodic store, consolidate
  what recurs into grounded facts, and persist the result so it survives a restart. Every fact
  traces back to the sentence it came from.
  IT DOES NOT: work an answer out (Q2 domain-general inference is EMPTY -- the reasoner equals a
  plain similarity baseline on 38 of 40 questions), or say anything in words (P1/P2 production is
  EMPTY -- `generation.py` returns codebook INDICES, and that is the slot the no-LLM invariant
  created and nobody wrote down).

**NOTHING HERE IS EVIDENCE THAT THE ASSEMBLY WORKS.** Every organ in it was validated ALONE, and
wiring ten together is precisely how a claims layer with 30 vetted results and 1 upheld came about.
The end-to-end can-fail test is Phase 2 of `notes/BUILD_PLAN_post_audit_2026-08-19.md` and it does
not exist yet. A self-test proves the plumbing runs. It does not prove the water is clean.

USAGE
  python -m hdlab.substrate            # self-test: build, read, query, assert organs ran
  from hdlab.substrate import Substrate
  s = Substrate(); s.read(n_sentences=200); s.query("velmara"); s.organ_report()
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# The spine. Imported eagerly because it IS the path -- everything else is lazy.
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    ReadingLoopState,
    checkpoint,
    content_lemmas,
    context_vector_masked,
    process_sentence,
    seed_known_words,
)

CONTEXT_DIM = 256      # context_vector_masked's own d; the episodic encoder's input_dim must match
DG_DIM = 2048          # expansion target for the dentate-gyrus projection
DG_SPARSITY = 0.02     # the organ probe measured 0.0195 at this setting

# The FROZEN schedule's harvests per patch, for the foraging ablation. MEASURED, not chosen: the
# live forager took 6 harvests across 2 patches on the 400-sentence self-test run, so 3 is what
# it actually does. This is RATE-MATCHING, and it is not optional -- an ablation that reads a
# different AMOUNT of text confounds "the organ contributes nothing" with "we read less", and
# this project has four arms whose apparent wins died to exactly that kind of unmatched twin.
_FROZEN_HARVESTS_PER_PATCH = 3


# ---------------------------------------------------------------------------------------------
# SLOT TABLE. The complete organ set, its filler, and its HONEST state.
# IDs are `notes/COMPLETE_SUBSTRATE_DESIGN_2026-08-18.md`'s, which are ORGAN_MAP's. Do not fork
# the taxonomy -- two documents with two architectures is how a project loses track of one.
# ---------------------------------------------------------------------------------------------
FILLED = "FILLED"                  # wired AND invoked on the real path
NEEDS_ADAPTER = "NEEDS_ADAPTER"    # works, but nothing upstream produces its input
EMPTY = "EMPTY"                    # nothing implements it
EXCLUDED = "EXCLUDED"              # implemented, self-test-passing, and measurably inert


@dataclass(frozen=True)
class Slot:
    slot_id: str
    job: str
    organ: Optional[str]
    state: str
    note: str = ""


SLOTS: List[Slot] = [
    # ---- TIER 0: reading ----
    Slot("R2", "know what material exists to read at all", "corpus_registry", FILLED,
         "36 corpora enumerated where the live loop's readable universe was a hard-coded 4"),
    Slot("H2", "what should I read next, and when to leave it", "information_foraging", FILLED,
         "MVT patch-leaving. NARROWING (vetting ledger): a FLOOR-BEATER, NOT A SHELF-BEATER -- "
         "FROZEN, the fixed schedule it exists to replace, scored HIGHER (0.0743 vs 0.0617)"),
    Slot("R1", "read a definition out of running prose", "definitional_extraction", FILLED,
         "228,133 definitions from 2.78M SimpleWiki lines; all 5 pattern families fire"),
    Slot("X1", "split text into the units everything else consumes",
         "corpus_registry.clean_sentences", FILLED, "byte-identical recipe to the live pipeline"),
    Slot("P3", "every answer carries where it came from", "reading_grounding_loop.provenance",
         FILLED, "per-fact source sentence and episode id"),
    # ---- TIER 1: memory ----
    Slot("H1", "do I already know this", "gap_detector", FILLED,
         "CA3/CA1 novelty margin, memoized per lemma"),
    Slot("D3", "one-shot episodic write", "hippocampal_encoder", FILLED,
         "probe: pattern completion cos 0.2000 -> 0.9173, sparsity 0.0195"),
    Slot("B3", "many encounters -> a concept", "reading_grounding_loop.checkpoint", FILLED,
         "consolidation pass; promotes MEANING_RELATION + KNOWN_WORD on grounding"),
    Slot("R3", "the foundation survives a restart", "foundation_persistence", FILLED,
         "deterministic save/reload of the full ReadingLoopState"),
    Slot("D2", "complete a pattern from a partial cue", "ca3_completer", NEEDS_ADAPTER,
         "consumes FHRR bundles + per-spoke codebooks; the ingest path produces neither. "
         "ALSO: UNTRACKED IN GIT -- exists only in the working tree"),
    Slot("R4", "promote provisional knowledge to durable knowledge", "prelim_tier", NEEDS_ADAPTER,
         "needs a TierState plus a cluster_key_fn the ingest path does not define"),
    # ---- TIER 2: comprehension ----
    Slot("E2", "situation model across sentences", "situation_reader", NEEDS_ADAPTER,
         "reads a FILE of prose (verified 2026-08-19, self-test PASS in 102.7s after the "
         "import-time-training fix). Composes, but on its own file-shaped input, not on the "
         "sentence stream this loop carries. 30s import"),
    Slot("E3", "who is 'he'", "coreference_resolver", NEEDS_ADAPTER,
         "build_mention_stream reads passage['entities'] -- a GOLD mention inventory keyed by "
         "gold entity name. It decides linking GIVEN the mentions. Its 0.7193 vs recency 0.5614 "
         "is true OF GOLD-ANNOTATED LITBANK and does not transfer to raw prose"),
    Slot("Q1", "a question -> a retrieval cue", "semantic_parser", NEEDS_ADAPTER,
         "needs a TRAINED IntentClassifier + slot dicts; no fitted artifact on the ingest path"),
    Slot("Q3", "accept / clarify / refuse the answer", "cortex", NEEDS_ADAPTER,
         "consumes torch HD tensors against its own codebooks. Probe: monotone confidence "
         "1.0 -> 0.0256, 11/11 distinct. Wire with atom_consultation OFF"),
    # ---- THE EMPTIES. Naming them is the point; an unnamed empty slot is the expensive kind. ----
    Slot("D7", "predictive relational map", None, EMPTY,
         "M = (I - gamma*P)^-1. THE ONLY SLOT WHERE THE BRAIN HANDS US A CLOSED FORM AND WE HAVE "
         "WRITTEN NONE OF IT. Highest value-per-effort in the design. D4 is blocked behind it"),
    Slot("Q2", "work the answer out (domain-general inference)", None, EMPTY,
         "AN ENTIRE NETWORK, not an organ. reasoner == a similarity baseline on 38 of 40 "
         "questions; multi_hop's default beta = n_dim collapses its softmax to a Dirac delta"),
    Slot("P1", "intention -> an ordered sequence of word meanings", None, EMPTY,
         "generation.py returns codebook INDICES; no lemma stage. Its own docstring says its "
         "test regime 'cannot fail by construction'"),
    Slot("P2", "word meanings -> a string a person reads", None, EMPTY,
         "the slot the no-LLM invariant created and nobody wrote down"),
    Slot("D5", "hold items actively", None, EMPTY,
         "THE FILENAME IS A TRAP: working_memory.py is 116 lines of assertion guards, no bank, "
         "no state, no update rule -- and it is LIVE"),
    Slot("F5", "notice comprehension has failed", None, EMPTY,
         "nothing computes ||delta situation model||"),
    Slot("F6", "settle a multi-sentence reading", None, EMPTY,
         "verify the brain-side equation before building; ORGAN_MAP flags it as recalled, not "
         "freshly re-verified"),
    Slot("E4", "bridge what is not stated", None, EMPTY,
         "NOT A BUILD TARGET. Two measured nulls, one the owner's own mechanism, CI-separated "
         "BELOW neighbour-copying. Do not fill until something upstream changes"),
    # ---- EXCLUDED. Self-test-passing AND inert. The intersection rule exists for these three. ----
    Slot("-", "consult banked atoms for a decision", "atom_consultation", EXCLUDED,
         "`applied` is hard-coded False. IT CANNOT CHANGE A DECISION BY CONSTRUCTION"),
    Slot("-", "extract definitional predicates", "definitional_predicate_v61", EXCLUDED,
         "fires on 1 of 375 already-definitional sentences -- 0.27% of its intended population"),
    Slot("-", "desiderative-negation channel", "goal_achievement", EXCLUDED,
         "7/7 on its own authored exemplars, 4/7 on minimal-edit paraphrases; also the one "
         "genuine self-test failure in the sweep"),
]

# A modest seed vocabulary. This is the pre-reading vocabulary a child brings to a page, not an
# answer key: it is closed-class plus high-frequency concrete nouns, and it contains no term any
# evaluation asks about.
SEED_VOCAB: List[str] = [
    "a", "an", "the", "this", "that", "these", "those", "is", "are", "was", "were", "be", "been",
    "of", "and", "or", "but", "in", "on", "at", "to", "for", "with", "from", "by", "as", "it",
    "its", "he", "she", "they", "them", "his", "her", "their", "not", "no", "all", "some", "many",
    "one", "two", "first", "new", "old", "long", "small", "large", "other", "such", "more", "most",
    "can", "will", "would", "may", "also", "than", "then", "when", "where", "which", "who",
    "what", "how", "there", "here", "have", "has", "had", "do", "does", "did", "make", "made",
    "use", "used", "call", "called", "know", "known", "name", "named", "part", "kind", "type",
    "form", "way", "time", "year", "day", "people", "person", "man", "woman", "child", "water",
    "land", "city", "town", "country", "world", "house", "school", "book", "word", "number",
]


# ---------------------------------------------------------------------------------------------
# SPINE WITNESSES. Some organs are invoked by `reading_grounding_loop`, not by us -- the
# GapDetector is built by `ReadingLoopState` itself (MEASURED 2026-08-19: it is NOT None at
# construction). For those, a call counter on THIS object is structurally zero however hard the
# organ is working, and reporting that as "never invoked" would be a false negative against
# working machinery.
#
# So each spine-owned organ names the ARTIFACT IT LEAVES BEHIND, and we count that instead.
# This is CLAUDE.md Evidence discipline 3 applied literally: observe what the process produces,
# never a proxy for it. `gap_cache` is written only by `is_gap()`, which is the GapDetector's
# only caller -- a non-empty cache is proof the organ classified something.
_SPINE_WITNESS: Dict[str, Callable[[Any], int]] = {
    "gap_detector": lambda s: len(s.state.gap_cache),
    "reading_grounding_loop.checkpoint": lambda s: len(s.state.growth_curve),
    "reading_grounding_loop.provenance": lambda s: len(s.state.provenance),
    "corpus_registry.clean_sentences": lambda s: int(s._calls.get("corpus_registry", 0)),
}


class _NullGapDetector:
    """The H1 ablation: the organ's INTERFACE intact, its DISCRIMINATION removed.

    Setting `state.gap_detector = None` is not an ablation, it is a crash -- `is_gap` calls
    `.familiarity()` unconditionally (verified at reading_grounding_loop.py:1142). And it would be
    the wrong control anyway: removing the call removes the novelty CHECK, so the loop would take
    a different path rather than the same path with a worse answer. This says GAP to everything,
    which is the honest "no novelty discrimination" arm -- the substrate still asks, and always
    gets the least informative possible answer back.
    """

    def familiarity(self, subject: str, relation: str, obj: str, **_kw):
        return type("_R", (), {"is_gap": True, "margin": 0.0, "ablated": True})()

    def refresh(self) -> None:
        return None


@dataclass
class ReadResult:
    """What one `read()` call did. Every field is a COUNT OF SOMETHING THAT HAPPENED, not a score."""
    corpora_visited: List[str] = field(default_factory=list)
    n_sentences: int = 0
    n_flagged: int = 0
    n_definitions: int = 0
    n_episodes_written: int = 0
    n_grounded: int = 0
    checkpoints: List[dict] = field(default_factory=list)
    foraging: List[dict] = field(default_factory=list)
    gain_stream: List[float] = field(default_factory=list)
    elapsed_s: float = 0.0
    organ_calls: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["checkpoints"] = self.checkpoints[-3:]     # the tail is what a reader wants
        return d


@dataclass
class QueryResult:
    """What the store returned, how sure it is, and where it came from. NOT a sentence."""
    cue: str
    known: bool = False
    facts: List[dict] = field(default_factory=list)
    episodic_hit: Optional[float] = None
    provenance: List[dict] = field(default_factory=list)
    decision: str = "REFUSE"
    note: str = ""

    def to_dict(self) -> dict:
        return dict(self.__dict__)


class Substrate:
    """The assembled reader. Organs are built on FIRST USE and every use is counted."""

    # Every ablation this substrate supports. THESE EXIST SO THE ASSEMBLY CAN BE TESTED, and the
    # reason is Phase 2's: an assembled substrate that nobody can switch pieces off in cannot be
    # distinguished from an expensive Counter. Each name turns exactly ONE organ off and changes
    # nothing else, so a delta is attributable.
    ABLATIONS = {
        "episodic": "do not write encounters to the hippocampal store (D3 off)",
        "definitions": "do not read definitions out of prose (R1 off)",
        "gap_detector": "do not check novelty; treat every content lemma as a gap (H1 off)",
        "foraging": "never leave a patch on the forager's signal; read a FIXED schedule "
                    "instead (H2 off). This is the FROZEN control the vetting ledger says "
                    "already SCORED HIGHER than foraging on reading yield -- 0.0743 vs 0.0617",
    }

    def __init__(self, *, seed: int = 20260819, n_dim: int = 2048,
                 corpora_dir: Optional[str] = None, seed_vocab: Optional[Sequence[str]] = None,
                 foundation_dir: Optional[str] = None,
                 ablate: Optional[Sequence[str]] = None) -> None:
        self.ablate = frozenset(ablate or ())
        unknown = self.ablate - set(self.ABLATIONS)
        if unknown:
            raise ValueError(f"unknown ablation(s) {sorted(unknown)}; "
                             f"known: {sorted(self.ABLATIONS)}")
        self.seed = int(seed)
        self.n_dim = int(n_dim)
        self.corpora_dir = corpora_dir
        self.foundation_dir = foundation_dir
        self._built: Dict[str, Any] = {}
        self._calls: Dict[str, int] = collections.Counter()
        self._pass_idx = 0

        store = HDFactStore(n_dim=self.n_dim, seed=self.seed,
                            relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                                  MEANING_RELATION: "FUNCTIONAL"},
                            use_index=True)
        self.state = ReadingLoopState(store=store)
        self._seed_vocab = list(seed_vocab) if seed_vocab is not None else list(SEED_VOCAB)
        seed_known_words(self.state, self._seed_vocab, source="substrate_seed")

    # -- organ access -------------------------------------------------------------------------

    def _organ(self, name: str, build: Callable[[], Any]) -> Any:
        """Build on first use, count every use. RULE 2: a call count, not a registry row."""
        self._calls[name] += 1
        if name not in self._built:
            self._built[name] = build()
        return self._built[name]

    def _registry(self):
        def build():
            from hdlab.corpus_registry import CorpusRegistry
            kw = {"corpora_dir": self.corpora_dir} if self.corpora_dir else {}
            return CorpusRegistry(**kw)
        return self._organ("corpus_registry", build)

    def _forager(self):
        def build():
            from hdlab.information_foraging import ForagingConfig, ForagingController
            return ForagingController(ForagingConfig(seed=self.seed, min_harvests_per_patch=2))
        return self._organ("information_foraging", build)

    def _definitions(self):
        def build():
            from hdlab.definitional_extraction import extract_definitions
            return extract_definitions
        return self._organ("definitional_extraction", build)

    def _episodic(self):
        def build():
            from hdlab.hippocampal_encoder import HippocampalEncoder
            return HippocampalEncoder(input_dim=CONTEXT_DIM, dg_dim=DG_DIM,
                                      sparsity=DG_SPARSITY, seed=self.seed)
        return self._organ("hippocampal_encoder", build)

    def _gap_detector(self):
        def build():
            from hdlab.gap_detector import GapDetector
            return GapDetector(self.state.store, floor=0.625)
        return self._organ("gap_detector", build)

    # -- INGEST -------------------------------------------------------------------------------

    def read(self, *, corpus: Optional[str] = None, n_sentences: int = 200,
             batch: int = 20, max_patches: int = 4) -> ReadResult:
        """Choose material off the shelf, read it, and consolidate what recurs.

        The forager decides WHEN TO LEAVE a corpus. Its gain currency is NOVEL LEMMAS PER
        SENTENCE -- a rate, deliberately not a count: `assert_gain_is_not_a_count` is called on
        the collected stream and raises if the signal ever degenerates to a constant, which is
        failure mode 6 in the organ's own docstring and the single easiest way to fake foraging.
        """
        t0 = time.time()
        res = ReadResult()
        reg = self._registry()
        readable = reg.readable_names()
        if not readable:
            res.elapsed_s = time.time() - t0
            res.organ_calls = dict(self._calls)
            return res

        order = [corpus] if corpus else readable
        order = [c for c in order if c in reg.handles]
        forager = self._forager()
        extract = self._definitions()
        episodic = self._episodic()

        # H1. MEASURED 2026-08-19, NOT ASSUMED: `ReadingLoopState` ALREADY carries a live
        # GapDetector at construction, so this branch does not fire and the organ is the SPINE's,
        # not ours. Kept as a guard for a state handed in without one. The organ genuinely runs --
        # see _SPINE_WITNESS below for how that is evidenced rather than asserted.
        if "gap_detector" in self.ablate:
            self.state.gap_detector = _NullGapDetector()
        elif self.state.gap_detector is None:
            self.state.gap_detector = self._gap_detector()

        read_budget = int(n_sentences)
        n_patches = max(1, min(int(max_patches), len(order)))
        frozen_per_patch = -(-read_budget // n_patches)      # ceil; the rate-matched twin's quota
        for patch_i, name in enumerate(order):
            if read_budget <= 0 or patch_i >= max_patches:
                break
            handle = reg.handles[name]
            if handle.remaining() <= 0:
                continue
            forager.enter_patch(name)
            res.corpora_visited.append(name)
            patch_gain: List[float] = []

            while read_budget > 0:
                take = min(batch, read_budget)
                sents = handle.take(take)
                if not sents:
                    break
                read_budget -= len(sents)

                flagged_here = 0
                defs_here = 0
                for j, sent in enumerate(sents):
                    ep = f"{name}_p{self._pass_idx}_{res.n_sentences + j}"
                    n_flag = process_sentence(self.state, sent, ep, pass_idx=self._pass_idx)
                    flagged_here += int(n_flag)

                    if "definitions" not in self.ablate:
                        for d in extract(sent):
                            lem = d.definiendum_lemma or d.definiendum
                            if lem:
                                self._definition_map[lem] = d.definiens
                                defs_here += 1

                    # ONE-SHOT EPISODIC WRITE, per flagged lemma occurrence. The cue is the
                    # sentence's context vector with the target itself REMOVED (the no-leak form)
                    # -- writing a word's own identity into its episode would make retrieval a
                    # lookup of the thing being asked about.
                    if n_flag and "episodic" not in self.ablate:
                        for lem in content_lemmas(sent):
                            if lem in self._seed_set:
                                continue
                            vec = context_vector_masked(sent, lem, d=CONTEXT_DIM)
                            if vec is None or not np.any(vec):
                                continue
                            episodic.encode_and_write(np.asarray(vec, dtype=np.float32
                                                                 ).reshape(1, -1))
                            self._episode_index.append((lem, ep))
                            res.n_episodes_written += 1

                res.n_sentences += len(sents)
                res.n_flagged += flagged_here
                res.n_definitions += defs_here

                gain = flagged_here / float(len(sents))   # a RATE, not a count
                patch_gain.append(gain)
                res.gain_stream.append(gain)
                forager.harvest(gain)
                # H2. Ablating foraging does NOT remove the decision -- it replaces the learned
                # leave rule with a FIXED schedule, which is the FROZEN arm the vetting ledger
                # says already beats it (0.0743 vs 0.0617 on reading yield).
                #
                # RATE-MATCHED ON SENTENCES, AND THE FIRST VERSION OF THIS WAS NOT. A fixed
                # harvests-per-patch constant let the frozen arm read 150 sentences against the
                # forager's 400, so every downstream difference was attributable to reading LESS
                # rather than to choosing worse. That is the unmatched-twin defect that killed
                # four apparent wins in this project's own record, rebuilt here by me. The frozen
                # schedule now splits the SAME total budget evenly across the SAME patches.
                if "foraging" in self.ablate:
                    if len(patch_gain) * batch >= frozen_per_patch:
                        break
                elif forager.should_leave():
                    break

            row = checkpoint(self.state, self._pass_idx, source_tag=name,
                             definition_map=dict(self._definition_map) or None)
            res.checkpoints.append(row)
            res.n_grounded = int(row.get("n_grounded_cumulative", res.n_grounded) or 0)
            self._pass_idx += 1

            st = forager.state()
            st["patch"] = name
            st["n_harvests"] = len(patch_gain)
            res.foraging.append(st)
            forager.travel()

        # FAILURE MODE 6, checked and not assumed: a gain stream that is one constant is not a
        # gain stream. The organ ships this guard; a caller that never calls it is not foraging.
        if len(res.gain_stream) >= 2:
            from hdlab.information_foraging import assert_gain_is_not_a_count
            try:
                assert_gain_is_not_a_count(res.gain_stream)
                self._gain_degenerate = False
            except AssertionError:
                self._gain_degenerate = True

        res.elapsed_s = time.time() - t0
        res.organ_calls = dict(self._calls)
        return res

    # -- RETRIEVAL ----------------------------------------------------------------------------

    def query(self, cue: str) -> QueryResult:
        """Address the store with a word. Returns what was RETRIEVED, never an answer worked out.

        Q2 (inference) and P1/P2 (production) are EMPTY, so this cannot reason and cannot speak.
        `decision` is a three-way ACCEPT / CLARIFY / REFUSE read off what the store actually
        holds; `cortex`, the organ that owns that gate properly, is NEEDS_ADAPTER because it
        consumes torch tensors against its own codebooks.
        """
        lem = (cue or "").strip().lower()
        out = QueryResult(cue=lem)
        if not lem:
            out.note = "empty cue"
            return out

        # Address the store by (subject, relation) -- its own indexed accessor, which recovers
        # each fact from HD by unbind. NOT a scan of live_facts(): those are FactRecord objects,
        # not dicts, and treating them as dicts silently returned zero facts for every cue,
        # including seeded ones. Caught by the self-test's seeded-query arm.
        facts: List[dict] = []
        for rel in (MEANING_RELATION, KNOWN_RELATION):
            for f in self.state.store.query(lem, rel):
                d = dict(f)
                d.setdefault("relation", rel)
                facts.append(d)
        out.facts = facts[:20]
        out.known = bool(facts)

        out.provenance = [p for p in self.state.provenance
                          if str(p.get("lemma", "")).lower() == lem][:10]

        if lem in self._definition_map:
            out.note = f"definition read from prose: {self._definition_map[lem][:120]}"

        n_meaning = sum(1 for f in out.facts
                        if str(f.get("relation", "")) == MEANING_RELATION)
        if n_meaning:
            out.decision = "ACCEPT"
        elif out.known:
            out.decision = "CLARIFY"
        else:
            out.decision = "REFUSE"
        return out

    # -- PERSISTENCE --------------------------------------------------------------------------

    def save(self, dir_path: str, *, source_tag: str = "substrate") -> dict:
        """Make it survive a restart. R3."""
        def build():
            from hdlab import foundation_persistence
            return foundation_persistence
        fp = self._organ("foundation_persistence", build)
        return fp.save_foundation(self.state, dir_path, source_tag=source_tag,
                                  next_pass_idx=self._pass_idx)

    # -- HONESTY ------------------------------------------------------------------------------

    def organ_report(self) -> dict:
        """Which slots are FILLED, which NEEDS_ADAPTER, which EMPTY, which EXCLUDED and why.

        RULE 3, and RULE 2's evidence in one table. `invoked` counts direct calls THIS instance
        made; `witness` counts the artifact a SPINE-OWNED organ leaves behind. Both are runtime
        evidence and neither is a registry row. A slot claiming FILLED with zero of both is
        reported in `filled_but_never_invoked`, which is the shape of the defect the whole organ
        audit exists to catch.
        """
        rows = []
        for s in SLOTS:
            base = (s.organ or "").split(".")[0]
            direct = int(self._calls.get(base, 0))
            wit_fn = _SPINE_WITNESS.get(s.organ or "")
            witness = int(wit_fn(self)) if wit_fn else 0
            rows.append({"slot": s.slot_id, "job": s.job, "organ": s.organ, "state": s.state,
                         "invoked": direct, "witness": witness,
                         "evidence": "direct-call" if direct else
                                     ("spine-artifact" if witness else "NONE"),
                         "note": s.note})
        by_state = collections.Counter(r["state"] for r in rows)
        # NO DOTTED-NAME EXEMPTION. An earlier draft skipped any organ whose name contained a dot,
        # which quietly excused four slots from the only check that binds. Every FILLED slot now
        # has to show one or the other kind of evidence.
        filled_never_called = [r["organ"] for r in rows
                               if r["state"] == FILLED and r["evidence"] == "NONE"]
        return {
            "counts": dict(by_state),
            "n_slots": len(rows),
            "ablated": sorted(self.ablate),
            "filled_but_never_invoked": filled_never_called,
            "gain_stream_degenerate": getattr(self, "_gain_degenerate", None),
            "rows": rows,
        }

    def profile(self) -> Dict[str, np.ndarray]:
        """Per-lemma accumulated context profile -- the substrate's OWN learned representation.

        TWO POPULATIONS, AND THE SECOND IS THE BIG ONE. MEASURED 2026-08-19: `ConceptSpace` is
        observed ONLY for seed-known words and at grounding time, so after 200 sentences it holds
        31 lemmas -- essentially the seed vocabulary. Reading it alone and calling it "what the
        substrate learned" would have scored an evaluation against the seed list.

        What the substrate actually holds about a word it is still working on is its LIBRARY
        ITEM's accumulated `Trace.context_vec`s. That is 1,472 lemmas at 550 sentences, and it is
        the representation any honest evaluation has to address. ConceptSpace wins on collision
        because a grounded word's profile is the consolidated one.
        """
        out: Dict[str, np.ndarray] = {}
        for lem, item in getattr(self.state.library, "items", {}).items():
            traces = getattr(item, "traces", None) or []
            vecs = [t.context_vec for t in traces if getattr(t, "context_vec", None) is not None]
            if not vecs:
                continue
            out[lem] = np.sum(np.asarray(vecs, dtype=np.float64), axis=0)
        for lem, vec in getattr(self.state.space, "_sums", {}).items():
            out[lem] = np.asarray(vec, dtype=np.float64)
        return out

    # -- lazily-initialised caches ------------------------------------------------------------

    @property
    def _definition_map(self) -> Dict[str, str]:
        if not hasattr(self, "__defmap"):
            setattr(self, "__defmap", {})
        return getattr(self, "__defmap")

    @property
    def _episode_index(self) -> List:
        if not hasattr(self, "__epidx"):
            setattr(self, "__epidx", [])
        return getattr(self, "__epidx")

    @property
    def _seed_set(self) -> frozenset:
        if not hasattr(self, "__seedset"):
            setattr(self, "__seedset", frozenset(self._seed_vocab))
        return getattr(self, "__seedset")


# ---------------------------------------------------------------------------------------------
# SELF-TEST. Proves the plumbing runs. Does NOT prove the assembly does anything useful --
# that is Phase 2's end-to-end can-fail test, which does not exist yet.
# ---------------------------------------------------------------------------------------------

def _selftest_import_builds_nothing() -> dict:
    """RULE 1: constructing a Substrate must not build or import any organ."""
    s = Substrate()
    assert not s._built, f"construction built organs eagerly: {sorted(s._built)}"
    heavy = [m for m in ("hdlab.definitional_extraction", "hdlab.corpus_registry",
                         "hdlab.information_foraging") if m in sys.modules]
    return {"built_at_construction": sorted(s._built), "heavy_modules_already_loaded": heavy}


def _selftest_organs_are_actually_called() -> dict:
    """RULE 2: a full ingest-and-persist cycle must INVOKE every organ the slot table calls
    FILLED, not merely import it. `save()` is part of the cycle on purpose -- R3's whole claim is
    that the foundation survives a restart, and an unexercised persistence organ is a claim."""
    # 400 SENTENCES, AND THE NUMBER IS MEASURED, NOT PICKED. Provenance rows are written ONLY at
    # the consolidation gate, so they are the proof that grounding actually fired. Measured
    # 2026-08-19 (scratch/phase1_grounding_scale.py): 100 sentences -> 0 provenance rows,
    # 400 -> 19. A 40-sentence self-test exercised the plumbing and never once reached the gate.
    s = Substrate()
    res = s.read(n_sentences=400, batch=25, max_patches=2)
    assert res.n_sentences > 0, "read() consumed no sentences -- is data/corpora present?"
    out_dir = os.path.join(_REPO, "scratch", "substrate_selftest_foundation")
    manifest = s.save(out_dir, source_tag="substrate_selftest")
    rep = s.organ_report()
    assert not rep["filled_but_never_invoked"], (
        "slots claim FILLED but their organ was never called: "
        f"{rep['filled_but_never_invoked']}")
    for organ in ("corpus_registry", "information_foraging", "definitional_extraction",
                  "hippocampal_encoder", "foundation_persistence"):
        assert s._calls.get(organ, 0) > 0, f"{organ} was never invoked"
    # The spine-owned organ, evidenced by its artifact rather than by a call count.
    assert len(s.state.gap_cache) > 0, (
        "the GapDetector classified nothing -- gap_cache is empty, so H1 did not run")
    assert len(s.state.growth_curve) > 0, "no consolidation checkpoint was recorded"
    assert len(s.state.provenance) > 0, (
        "nothing reached the consolidation gate -- P3 provenance is empty, so no fact in this "
        "run can be traced to the sentence it came from")
    # AND THE GATE MUST BE ABLE TO SAY NO. A consolidation gate that grounds everything it sees
    # is not a gate; the refusal list is the evidence that it discriminates.
    assert len(s.state.refusals) > 0, (
        "the grounding gate refused nothing -- it cannot be discriminating")
    return {"n_sentences": res.n_sentences, "n_flagged": res.n_flagged,
            "n_definitions": res.n_definitions, "n_episodes": res.n_episodes_written,
            "n_provenance_rows": len(s.state.provenance), "n_refused": len(s.state.refusals),
            "corpora_visited": res.corpora_visited,
            "organ_calls": res.organ_calls, "saved_keys": sorted(manifest)[:8],
            "elapsed_s": round(res.elapsed_s, 1)}


def _selftest_gain_is_a_rate_not_a_count() -> dict:
    """The forager's currency must vary. A constant gain stream is failure mode 6, and the organ
    ships the assertion that catches it -- this proves we CALL it."""
    s = Substrate()
    res = s.read(n_sentences=60, batch=10, max_patches=1)
    degenerate = getattr(s, "_gain_degenerate", None)
    assert len(res.gain_stream) >= 2, "too few harvests to judge the gain stream"
    assert degenerate is False, (
        f"the gain stream is a constant and is therefore not a gain: {res.gain_stream[:8]}")
    return {"gain_stream": [round(g, 4) for g in res.gain_stream[:8]],
            "n_harvests": len(res.gain_stream), "degenerate": degenerate}


def _selftest_query_refuses_what_it_never_read() -> dict:
    """A CAN-FAIL check, small but real: a word the substrate has never seen must NOT come back
    ACCEPT. A store that accepts everything is a store that knows nothing."""
    s = Substrate()
    s.read(n_sentences=40, batch=10, max_patches=1)
    nonce = s.query("zzqxvelmarathrom")
    assert nonce.decision == "REFUSE", f"a never-seen nonce returned {nonce.decision}"
    assert not nonce.known, "a never-seen nonce came back known"
    # THE OTHER HALF, and it is the half that has to bind: a word the substrate WAS given must
    # come back known. A store that refuses everything passes the nonce arm trivially.
    seeded = s.query("water")
    assert seeded.known, "a SEEDED word came back unknown -- the store is not being addressed"
    assert seeded.decision != "REFUSE", f"a seeded word returned {seeded.decision}"
    return {"nonce_decision": nonce.decision, "nonce_known": nonce.known,
            "seeded_decision": seeded.decision, "seeded_n_facts": len(seeded.facts)}


def _selftest_report_names_the_empties() -> dict:
    """The empty slots must be visible FROM THE OBJECT, not only from a note. An empty slot
    nobody wrote down is the most expensive kind."""
    s = Substrate()
    rep = s.organ_report()
    empties = [r["slot"] for r in rep["rows"] if r["state"] == EMPTY]
    assert "D7" in empties, "the successor representation must be reported EMPTY"
    assert "Q2" in empties and "P1" in empties, "inference and production must be reported EMPTY"
    assert rep["counts"].get(NEEDS_ADAPTER, 0) > 0, (
        "NEEDS_ADAPTER must not be collapsed into FILLED -- that is the false-coverage defect")
    return {"counts": rep["counts"], "empty_slots": empties}


def run_all_selftests() -> dict:
    tests = [
        ("import_builds_nothing", _selftest_import_builds_nothing),
        ("report_names_the_empties", _selftest_report_names_the_empties),
        ("organs_are_actually_called", _selftest_organs_are_actually_called),
        ("gain_is_a_rate_not_a_count", _selftest_gain_is_a_rate_not_a_count),
        ("query_refuses_what_it_never_read", _selftest_query_refuses_what_it_never_read),
    ]
    out: Dict[str, Any] = {}
    failed = []
    for name, fn in tests:
        t0 = time.time()
        try:
            out[name] = fn()
            out[name]["_ok"] = True
        except AssertionError as e:
            out[name] = {"_ok": False, "error": str(e)[:400]}
            failed.append(name)
        except Exception as e:  # a crash is a failure, and must say which kind
            out[name] = {"_ok": False, "error": f"{type(e).__name__}: {str(e)[:400]}"}
            failed.append(name)
        out[name]["_seconds"] = round(time.time() - t0, 1)
    out["_failed"] = failed
    out["_overall"] = "PASS" if not failed else "FAIL"
    return out


if __name__ == "__main__":
    r = run_all_selftests()
    print(json.dumps(r, indent=2, default=str))
    print("ALL SELF-TESTS PASSED" if r["_overall"] == "PASS"
          else f"SELF-TEST FAILURES: {r['_failed']}")
    sys.exit(0 if r["_overall"] == "PASS" else 1)
