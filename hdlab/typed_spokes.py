"""hdlab/typed_spokes.py -- FROZEN TYPED, DIRECTED world-knowledge SPOKES on the ATL hub (the C5/C6/C7 spokes of
the knowledge foundation). The ADDITIVE fix for the SUPERPOSITION CEILING located by
expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate (owner-DONE, Q111 landing).

WHAT THIS ORGAN COMPUTES (the brain operation, PINNED). Semantic memory is a transmodal ATL HUB with TYPED SPOKES
(Lambon-Ralph 2017): concepts are shared nodes, and each relation (is-a, part-whole, used-for, opposition) is a
distinct TYPED, often DIRECTED projection a task reads selectively. The frozen C1 sense-signature superposes ALL of
a synset's knowledge into ONE dense 200-d vector, read by SYMMETRIC cosine -- analytically INCAPABLE of a directed
or typed relation (is-a direction: symmetric cap 0.500 on MoNLI; part-whole: symmetric fooled BELOW chance on
confusable distractors; antonymy: symmetric is ANTI-predictive, AUC 0.391). This organ re-admits that knowledge as
directed typed spokes, keyed by the SAME hub nodes as C1/C2 (WordNet synset + lemma), so a consumer can read WHICH
relation and WHICH direction, not just "how related". ADDITIVE: it never touches C1; the WSD path is byte-unchanged.

THE THREE SPOKES (each realizes the STORE-ORGANIZATION PRINCIPLE earned by drilling the gate wall):
  * C5  is-a / taxonomy (DIRECTED, TRANSITIVE-CLOSURE store). The taxonomic hierarchy (Collins-Quillian 1969;
        Rogers-McClelland 2004) consulted by monotonicity-respecting inference (natural logic; van Benthem;
        MacCartney-Manning 2009). A CLOSURE store must NOT be edge-filtered -- pruning any clean edge disconnects its
        ancestors (measured to break the gated closure to 0.52). It is admitted by PROVENANCE + RESOLUTION and then
        closed; the consolidation gate's schema-margin (reused from the meaning_foundation signatures) only REJECTS
        wrong edges BEFORE closure for a NOISY source. WordNet hypernymy is a clean, provenance-admitted source, so
        the gate degenerates to keep-all and the store is WordNet's transitive closure read live (nltk), MFS-resolved
        for lemma queries. Reads: isa_ancestors(synset), is_a(sub, sup), entails(lex1, lex2, negated) [the directed
        monotonicity judge], and the PARSE-FREE sentence-level closed-class monotonicity marker is_downward(sentence)
        (the brain's fast operator-recognition register) + natural_logic_label(s1, s2).
  * C6  part-whole / instrument (DIRECTED, NON-closure typed LOOKUP). Bridging inference fills the unstated
        part-whole / instrument link (Clark 1975; Kintsch 1988; the N400 specific-coherence signal, Kuperberg-Jaeger
        2016). A NON-closure store has no chain to break, so it may be edge-filtered freely. Built OFFLINE from
        WordNet meronymy + ConceptNet PartOf/HasA/MadeOf (part-whole) and ConceptNet UsedFor (instrument), resolved
        to hub lemmas. Reads: holonym_prototype(whole) [mean unit-hub of the whole's known parts -- the O(1)
        consolidated-store read], part_whole_score(part, whole) [directed: cos(hub(part), prototype) + reach bonus],
        part_of(part, whole), covers_whole(whole). family="part" (default) or "instrument".
  * C7  antonymy (lexical opposition; NON-closure lookup). A distinct lexical relation the mental lexicon stores
        explicitly (Deese 1965; Murphy-Andrew 1993; Mohammad 2013) -- NOT derivable from similarity (antonyms are
        among the MOST distributionally similar pairs). Built OFFLINE from ConceptNet Antonym. Read: antonym(a, b).

PROMOTED byte-faithfully from the SOLVED cells (adapted only to hdlab: stdlib + nltk + numpy + hdlab.meaning_foundation
for the gate; NO experiments. dependency, NO spaCy -- spaCy is a NON-admissible ceiling reference in the SOLVED):
  is-a / entails / gate / natural-logic  <- experiments/exp_isa_typed_spoke_monli_v1.py,
                                            experiments/exp_natural_logic_monotonicity_med_v1.py
  part-whole / instrument prototype       <- experiments/exp_partwhole_typed_spoke_bridging_v1.py
  antonym                                 <- experiments/exp_antonym_typed_spoke_valence_v1.py

RELATION TO hdlab/structured_matcher.py (just landed, a DIFFERENT problem): that organ is a LEXICAL-HEAD sign
matcher (is_a / part_of / antonym / converse / cohyponym) that abstains to the ATL hub, for goal-congruence /
type-membership consumers. This organ is SYNSET-keyed, DIRECTED (transitive-closure is-a, holonym-PROTOTYPE
part-whole, natural-logic composition) for the meaning FOUNDATION (entailment / coref type-licensing / bridging).
They read overlapping edge families but compute different things; see the module's landing note for the
consolidation recommendation.

DEFAULT-SAFE / ISLAND: a NEW module -- importing it changes NO existing behaviour and NO live consumer reads it yet
(wiring is a separate measured step). Every read DEGRADES GRACEFULLY (returns None / False / -inf / abstains, never
raises) when nltk WordNet, the frozen C6/C7 assets, or the hub are absent. The offline build
(python -m hdlab.typed_spokes --build) fits + freezes the C6/C7 assets under data/frontend_assets/ (float16,
gitignored per the whole-data/-tree convention). Glass-box. NO external LLM at inference. NO training. ASCII.
"""
from __future__ import annotations

import collections
import json
import os
import re
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PW_ASSET = os.path.join(_REPO, "data", "frontend_assets", "typed_spoke_partwhole_v1.npz")
_ANT_ASSET = os.path.join(_REPO, "data", "frontend_assets", "typed_spoke_antonym_v1.npz")
_HUB_PATH = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
_CN_DIR = os.path.join(_REPO, "data", "bridge_relation_assets_v1")
_CN_100K = os.path.join(_REPO, "data", "datasets", "conceptnet5_en_100k.jsonl")

_EPS = 1e-9


def _unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    return v / (n + _EPS) if n > 0 else v


# =========================================================================== WordNet (lazy, degrades)
_WN = None
_WN_MISSING = False


def _wordnet():
    """The WordNet corpus reader, loaded ONCE (lazy). None if unavailable -- is-a/entails degrade to False/None."""
    global _WN, _WN_MISSING
    if _WN is None and not _WN_MISSING:
        try:
            from nltk.corpus import wordnet as wn
            wn.synsets("test", pos=wn.NOUN)  # force lazy corpus load now so later calls cannot raise
            _WN = wn
        except Exception:
            _WN_MISSING = True
            _WN = None
    return _WN


# =========================================================================================================
# C5 -- is-a directed taxonomy (TRANSITIVE-CLOSURE store; clean WordNet provenance + a gate for noisy sources)
# =========================================================================================================
_ANC_SYN: Dict[str, frozenset] = {}      # synset name -> transitive hypernym closure (incl. self)
_ANC_UNION: Dict[str, frozenset] = {}    # lemma -> union closure over ALL senses (the raw/unresolved twin)
_MFS: Dict[str, Optional[str]] = {}      # lemma -> most-frequent-sense noun synset name


def _mfs_synset(lemma: str) -> Optional[str]:
    """The most-frequent-sense (dominant) noun synset name of a lemma, or None. Byte-faithful to
    exp_isa_typed_spoke_monli_v1.mfs_syn (nltk lists synsets most-frequent-first)."""
    if lemma in _MFS:
        return _MFS[lemma]
    wn = _wordnet()
    if wn is None:
        return None
    ss = wn.synsets(lemma, pos=wn.NOUN)
    _MFS[lemma] = ss[0].name() if ss else None
    return _MFS[lemma]


def isa_ancestors(synset: str) -> frozenset:
    """The DIRECTED is-a spoke: the transitive hypernym closure (synset-name set, INCLUDING `synset` itself) of a
    WordNet synset name. Byte-faithful to exp_isa_typed_spoke_monli_v1.anc_mfs's closure over hypernym_paths.
    Empty frozenset if WordNet is absent or the synset is unknown. Memoized -- the O(1) consolidated-store read."""
    if synset in _ANC_SYN:
        return _ANC_SYN[synset]
    wn = _wordnet()
    acc: Set[str] = set()
    if wn is not None:
        try:
            s = wn.synset(synset)
            acc.add(s.name())
            for path in s.hypernym_paths():
                for h in path:
                    acc.add(h.name())
        except Exception:
            acc = set()
    fs = frozenset(acc)
    _ANC_SYN[synset] = fs
    return fs


def _anc_union(lemma: str) -> frozenset:
    """Union hypernym closure over ALL senses of a lemma (the raw-string, sense-UNRESOLVED read). Byte-faithful to
    exp_isa_typed_spoke_monli_v1.anc_union / exp_natural_logic_monotonicity_med_v1._anc_union."""
    if lemma in _ANC_UNION:
        return _ANC_UNION[lemma]
    wn = _wordnet()
    acc: Set[str] = set()
    if wn is not None:
        for s in wn.synsets(lemma, pos=wn.NOUN):
            acc.add(s.name())
            for path in s.hypernym_paths():
                for h in path:
                    acc.add(h.name())
    fs = frozenset(acc)
    _ANC_UNION[lemma] = fs
    return fs


def _synset_names(lemma: str) -> frozenset:
    wn = _wordnet()
    if wn is None:
        return frozenset()
    return frozenset(s.name() for s in wn.synsets(lemma, pos=wn.NOUN))


def is_a(sub: str, sup: str, resolve: bool = True) -> bool:
    """DIRECTED type-membership: does lemma `sub` denote a KIND OF `sup`?  resolve=True (default) is the
    MFS-RESOLVED read (byte-faithful to exp_isa_typed_spoke_monli_v1.isa_mfs_fn -- the reported 0.817 MoNLI read):
    sup's MFS synset is an ancestor of sub's MFS synset. resolve=False is the sense-UNRESOLVED union read
    (isa_union_fn -- over-generates cross-sense edges; the raw twin, and the setup the MED natural-logic headline
    used). False if either lemma is unknown / WordNet is absent."""
    if resolve:
        sub_mfs = _mfs_synset(sub)
        if sub_mfs is None:
            return False
        sup_mfs = _mfs_synset(sup)
        return sup_mfs is not None and sup_mfs in isa_ancestors(sub_mfs)
    return bool(_anc_union(sub) & _synset_names(sup))


def entails(lex1: str, lex2: str, negated: bool = False, resolve: bool = True) -> bool:
    """The DIRECTED natural-logic monotonicity judge for a single lexical substitution (lex1 -> lex2): does a
    sentence asserting lex1 ENTAIL the same sentence with lex2?  Upward (not negated): entail iff lex1 IS-A lex2
    (replace a term by its hypernym). Downward (negated -- under negation/no/every-restrictor the polarity FLIPS):
    entail iff lex2 IS-A lex1. Byte-faithful to exp_isa_typed_spoke_monli_v1.judge's per-item rule. The sentence's
    polarity comes from is_downward() (the parse-free closed-class marker) -- the brain's fast register."""
    return is_a(lex2, lex1, resolve=resolve) if negated else is_a(lex1, lex2, resolve=resolve)


# ------------------------------------------- the TYPE-LICENSING read for common-noun coreference (C5 is-a + C6 mero)
# The brain-faithful use of the taxonomic/part-whole spokes in reference: type knowledge LICENSES a candidate
# antecedent; it does NOT SELECT one (recency/Centering selects). Promoted byte-faithfully from
# exp_isa_spoke_commonnoun_coref_gum_v1.wk_related (the SOLVED's reference filter). Lemma-level MFS reads.
_MERO_MFS: Dict[str, frozenset] = {}


def _mfs_anc(lemma: str) -> frozenset:
    """MFS hypernym closure (synset-name set) of a lemma -- the directed is-a spoke read used for licensing.
    == exp_isa_spoke_commonnoun_coref_gum_v1._anc (isa_ancestors of the lemma's MFS synset)."""
    ms = _mfs_synset(lemma)
    return isa_ancestors(ms) if ms else frozenset()


def _mfs_mero_holo(lemma: str) -> frozenset:
    """MFS part/substance/member meronyms + holonyms (synset-name set) of a lemma -- the part-whole spoke read used
    for licensing. Byte-faithful to exp_isa_spoke_commonnoun_coref_gum_v1._mero_holo. Empty if WordNet absent."""
    if lemma in _MERO_MFS:
        return _MERO_MFS[lemma]
    wn = _wordnet()
    acc: Set[str] = set()
    if wn is not None:
        ss = wn.synsets(lemma, pos=wn.NOUN)
        if ss:
            s = ss[0]
            for rel in (s.part_meronyms(), s.substance_meronyms(), s.member_meronyms(),
                        s.part_holonyms(), s.substance_holonyms(), s.member_holonyms()):
                for x in rel:
                    acc.add(x.name())
    fs = frozenset(acc)
    _MERO_MFS[lemma] = fs
    return fs


def coref_type_license(head_a: str, head_b: str, anc_fn=None, mero_fn=None, syn_fn=None) -> bool:
    """The binary TYPE-LICENSING predicate for common-noun coreference (Lambon-Ralph typed spokes; Sanford-Garrod
    scenario binding): may an anaphor head `head_a` co-refer with a DIFFERENT-head candidate antecedent `head_b`
    on TYPE grounds?  True iff they share a synset (synonym), stand in an is-a relation EITHER direction (MFS
    hypernym closure -- "the animal" resumes "a dog"), or a part-whole/member relation either direction. The
    consumer keeps recency/Centering as the SELECTOR among the licensed set; this only LICENSES, BINARY (the SOLVED
    proved graded HURTS). Byte-faithful to exp_isa_spoke_commonnoun_coref_gum_v1.wk_related. anc_fn/mero_fn/syn_fn
    are injectable so the shuffled-graph info-free twin can pass remapped closures. Degrades to False (never raises)
    when WordNet is absent or either head is out-of-vocabulary -- an unknown head is NOT licensed to bridge
    (recall-safe: same-head identity remains the linker's job)."""
    if head_a == head_b:
        return False                     # same head is the head-identity linker's job, not the typed spoke's
    if _wordnet() is None:
        return False
    syn = syn_fn or _synset_names
    anc = anc_fn or _mfs_anc
    mero = mero_fn or _mfs_mero_holo
    a_syn = syn(head_a)
    b_syn = syn(head_b)
    if not a_syn or not b_syn:
        return False
    if a_syn & b_syn:
        return True                      # synonym / shared sense
    if (b_syn & anc(head_a)) or (a_syn & anc(head_b)):
        return True                      # is-a either direction
    if (b_syn & mero(head_a)) or (a_syn & mero(head_b)):
        return True                      # part-whole / member either direction
    return False


# --------------------------------------------------------- parse-free monotonicity marker + natural-logic readout
# byte-faithful to exp_natural_logic_monotonicity_med_v1 (MED-calibrated closed-class operators).
_NL_STOP = set("a an the is are was were be been being to of in on at and or this that s".split())
_DE = set("no not never without none nobody nothing neither nor rarely hardly seldom doesnt dont didnt cannot "
          "cant wont isnt arent wasnt werent".split())
_DE_PHRASE = ("at most", "fewer than", "less than", "no more than")


def _nl_content(s: str) -> List[str]:
    return [w for w in re.findall(r"[a-z]+", s.lower()) if w not in _NL_STOP]


def is_downward(sentence: str) -> bool:
    """The PARSE-FREE sentence-level closed-class monotonicity marker (the brain's fast operator-RECOGNITION
    register; Neville 1992, Pulvermuller 1995). A sentence is DOWNWARD-entailing iff it contains an ODD number of
    downward-entailing operators (double negation flips back). MED-calibrated: guards 'a few / a little' (UPWARD),
    counts phrase operators ('at most', ...) and the conditional 'if' antecedent. Byte-faithful to
    exp_natural_logic_monotonicity_med_v1.is_downward (the fully-brain-foundational 0.767 headline, ~85% coverage)."""
    t = sentence.lower().replace("'", "")
    ws = re.findall(r"[a-z]+", t)
    cnt = 0
    for i, w in enumerate(ws):
        if w in _DE:
            cnt += 1
        elif w in ("few", "little") and not (i > 0 and ws[i - 1] == "a"):
            cnt += 1
    cnt += sum(t.count(p) for p in _DE_PHRASE)
    if t.startswith("if ") or " if " in t:
        cnt += 1
    return cnt % 2 == 1


def classify_edit(s1: str, s2: str) -> Tuple[str, Optional[str], Optional[str]]:
    """Content-word multiset diff of s1 vs s2 -> ('sub', w1, w2) | ('del', None, None) | ('ins', None, None) |
    ('complex', None, None). Byte-faithful to exp_natural_logic_monotonicity_med_v1.classify_edit."""
    a, b = collections.Counter(_nl_content(s1)), collections.Counter(_nl_content(s2))
    oa = list((a - b).elements())
    ob = list((b - a).elements())
    if len(oa) == 1 and len(ob) == 1:
        return ("sub", oa[0], ob[0])
    if len(oa) >= 1 and len(ob) == 0:
        return ("del", None, None)
    if len(oa) == 0 and len(ob) >= 1:
        return ("ins", None, None)
    return ("complex", None, None)


def nat_logic_pred(kind: str, w1: Optional[str], w2: Optional[str], down: bool) -> Optional[str]:
    """The natural-logic entailment rule, or None (abstain -- complex / uncovered). SUB uses the UNION (unresolved)
    is-a read, byte-faithful to exp_natural_logic_monotonicity_med_v1.nat_logic_pred (the validated MED setup);
    DEL upward->entail / downward->neutral; INS upward->neutral / downward->entail. down FLIPS all rules."""
    wn = _wordnet()
    up = not down
    if kind == "sub":
        if wn is None or not (wn.synsets(w1, pos=wn.NOUN) and wn.synsets(w2, pos=wn.NOUN)):
            return None
        rel = is_a(w1, w2, resolve=False) if up else is_a(w2, w1, resolve=False)
        return "entailment" if rel else "neutral"
    if kind == "del":
        return "entailment" if up else "neutral"
    if kind == "ins":
        return "neutral" if up else "entailment"
    return None


def natural_logic_label(s1: str, s2: str) -> Optional[str]:
    """The full glass-box natural-logic readout for a sentence pair: detect the single edit (sub/del/ins), mark the
    sentence polarity with the parse-free is_downward() marker, apply the monotonicity rule. Returns 'entailment' /
    'neutral' or None (abstain on complex / uncovered edits). Byte-faithful to the MED cell's headline path
    (polarity read from sentence1; ~85% coverage; self-detected-monotonicity acc 0.767 on MED, near-human)."""
    kind, w1, w2 = classify_edit(s1, s2)
    return nat_logic_pred(kind, w1, w2, is_downward(s1))


# ------------------------------------------------- the consolidation GATE for a NOISY is-a source (reject-then-close)
def _mf_sig(synset: str, cache: Dict[str, Optional[np.ndarray]]) -> Optional[np.ndarray]:
    """The UPSTREAM meaning_foundation UNIT signature for a synset (memoized), or None. Reuses the frozen C1 asset
    read-only -- the gate SCORES admission with the same signatures the meaning channel reads (full-stack: the
    spoke's admission quality depends on the upstream signature quality). Degrades to None if C1 is absent."""
    if synset in cache:
        return cache[synset]
    v = None
    try:
        from hdlab.meaning_foundation import sense_signature
        v = sense_signature(synset)
    except Exception:
        v = None
    cache[synset] = v
    return v


def schema_margin(child: str, parent: str, cache: Dict[str, Optional[np.ndarray]],
                  competitors: Sequence[str]) -> Optional[float]:
    """The consolidation-gate SCHEMA step on an is-a edge (child->parent): margin = cos(sig(child), sig(parent)) -
    max_r cos(sig(child), sig(r)) over random competitor synsets. High for a true edge, low for a wrong one.
    Byte-faithful to exp_isa_typed_spoke_monli_v1.schema_margin (== consolidate()'s discriminativeness keep).
    None if either signature is absent."""
    sc = _mf_sig(child, cache)
    sp = _mf_sig(parent, cache)
    if sc is None or sp is None:
        return None
    self_s = float(sc @ sp)
    sib = -1.0
    for r in competitors:
        sr = _mf_sig(r, cache)
        if sr is not None:
            sib = max(sib, float(sc @ sr))
    return self_s - sib


def gate_isa_edges(edges: Sequence[Tuple[str, str]], margin: float = 0.05, n_comp: int = 8,
                   seed: int = 0) -> Set[Tuple[str, str]]:
    """REJECT wrong (child->parent) is-a edges from a NOISY source BEFORE closure (the closure-store discipline:
    never edge-filter AFTER closing -- pruning a clean edge disconnects ancestors; reject then close). Admit an edge
    iff its schema-margin >= `margin` (unscorable edges are admitted -- no evidence to reject). A CLEAN curated
    source (WordNet) needs no gate: pass its edges straight to close_isa (provenance keep-all). Byte-faithful to
    exp_isa_typed_spoke_monli_v1.gate_edges' admission branch."""
    edges = list(edges)
    all_syn = sorted({p for _, p in edges} | {c for c, _ in edges})
    if not all_syn:
        return set()
    rng = np.random.default_rng(seed)
    cache: Dict[str, Optional[np.ndarray]] = {}
    admitted: Set[Tuple[str, str]] = set()
    for (c, p) in edges:
        comp = [all_syn[i] for i in rng.integers(0, len(all_syn), n_comp)]
        m = schema_margin(c, p, cache, comp)
        if m is None or m >= margin:
            admitted.add((c, p))
    return admitted


def close_isa(edges: Sequence[Tuple[str, str]]) -> Dict[str, Set[str]]:
    """Transitive is-a ancestor map {synset: set(ancestors)} from an admitted (child->parent) edge set. The CLOSURE
    step of the closure store (run AFTER any reject step, NEVER an edge-filter on the closed graph). Byte-faithful to
    exp_isa_typed_spoke_monli_v1.closure_from_edges."""
    child2par: Dict[str, Set[str]] = collections.defaultdict(set)
    for (c, p) in edges:
        child2par[c].add(p)
    anc: Dict[str, Set[str]] = {}

    def walk(n: str, seen: Set[str]) -> Set[str]:
        if n in anc:
            return anc[n]
        if n in seen:
            return set()
        seen.add(n)
        acc: Set[str] = set()
        for p in child2par.get(n, ()):
            acc.add(p)
            acc |= walk(p, seen)
        anc[n] = acc
        return acc

    for n in list(child2par.keys()):
        walk(n, set())
    return anc


# =========================================================================================================
# C6 -- part-whole / instrument directed (NON-closure typed LOOKUP; edge-filterable)
# =========================================================================================================
_PW_STORE: Optional[Dict] = None
_PW_MISSING = False


def _pw_store() -> Optional[Dict]:
    """The frozen part-whole + instrument spoke, loaded ONCE. None (not an exception) if the gitignored asset is
    absent -- reads abstain. Per family {'part','instrument'}: wholes (list[str]), row (whole->proto row idx),
    proto (float16 [K,200] holonym prototypes = mean unit-hub of the whole's known parts), parts_of (whole->set of
    part lemmas, for reach / part_of / coverage)."""
    global _PW_STORE, _PW_MISSING
    if _PW_STORE is None and not _PW_MISSING:
        try:
            z = np.load(_PW_ASSET, allow_pickle=False)
            store: Dict[str, Dict] = {}
            for fam in ("part", "instrument"):
                wholes = [str(w) for w in z["%s_wholes" % fam].tolist()]
                parts_of: Dict[str, Set[str]] = collections.defaultdict(set)
                ep = [str(x) for x in z["%s_edge_part" % fam].tolist()]
                ew = [str(x) for x in z["%s_edge_whole" % fam].tolist()]
                for p, w in zip(ep, ew):
                    parts_of[w].add(p)
                store[fam] = {"wholes": wholes, "row": {w: i for i, w in enumerate(wholes)},
                              "proto": z["%s_proto" % fam], "parts_of": parts_of}
            _PW_STORE = store
        except (FileNotFoundError, OSError, KeyError, ValueError):
            _PW_MISSING = True
            _PW_STORE = None
    return _PW_STORE


def available_partwhole() -> bool:
    """Whether the frozen C6 part-whole/instrument asset is present. False -> the C6 reads abstain, never raise."""
    return _pw_store() is not None


def holonym_prototype(whole: str, family: str = "part") -> Optional[np.ndarray]:
    """The MERONYM-PROTOTYPE (float64 unit vector) of a whole: the mean unit-hub vector of the whole's KNOWN parts
    -- "what the things typically part of `whole` look like" (the O(1) consolidated-store read, PINNED). None if the
    asset is absent, the whole is unknown, or the row is a zero vector. Byte-faithful to
    exp_partwhole_typed_spoke_bridging_v1.eval_bridging's proto() over all of the whole's parts (no exclusion = the
    in-domain COVERED read that scored 0.926/0.828)."""
    st = _pw_store()
    if st is None or family not in st:
        return None
    i = st[family]["row"].get(whole)
    if i is None:
        return None
    v = np.asarray(st[family]["proto"][i], dtype=np.float64)
    return v if float(np.linalg.norm(v)) > 1e-6 else None


def part_of(part: str, whole: str, family: str = "part") -> bool:
    """DIRECTED reachability: is `part` a stored part of `whole` (instrument: `part` is used for purpose `whole`)?
    The typed-graph edge (reach), no closure."""
    st = _pw_store()
    if st is None or family not in st:
        return False
    return part in st[family]["parts_of"].get(whole, ())


def covers_whole(whole: str, family: str = "part") -> bool:
    """Whether the spoke stores any part for `whole` (the HYBRID coverage test: typed read where covered, else the
    consumer's distributional fallback -- part-whole does NOT generalize to novel wholes, the SOLVED located neg)."""
    st = _pw_store()
    if st is None or family not in st:
        return False
    return bool(st[family]["parts_of"].get(whole))


def part_whole_score(part: str, whole: str, family: str = "part") -> float:
    """The DIRECTED typed-spoke bridging score of candidate `whole` for target `part`:
    cos(hub(part), holonym_prototype(whole)) + 2.0 * reach, where reach = 1 if `part` is a stored part of `whole`.
    Byte-faithful to exp_partwhole_typed_spoke_bridging_v1's TYPED_directed_spoke arm. Returns -9.0 (abstain
    sentinel, matching the cell) when the prototype or the hub vector of `part` is unavailable. Needs the hub (loaded
    lazily) for the target-part vector."""
    proto = holonym_prototype(whole, family=family)
    hv = _hub_unit(part)
    base = float(hv @ proto) if (proto is not None and hv is not None) else -9.0
    reach = 1.0 if part_of(part, whole, family=family) else 0.0
    return base + 2.0 * reach


# ------------------------------------------------------------------------------------- hub (lazy, degrades)
_HUB: Optional[Dict[str, np.ndarray]] = None
_HUB_MISSING = False


def _hub() -> Optional[Dict[str, np.ndarray]]:
    """The PPMI-SVD 200-d ATL hub (word -> vector), loaded ONCE. None if absent -- part_whole_score abstains for
    the target part vector."""
    global _HUB, _HUB_MISSING
    if _HUB is None and not _HUB_MISSING:
        try:
            import pickle
            _HUB = pickle.load(open(_HUB_PATH, "rb"))["hub"]
        except Exception:
            _HUB_MISSING = True
            _HUB = None
    return _HUB


def _hub_unit(word: str) -> Optional[np.ndarray]:
    hub = _hub()
    if hub is None:
        return None
    v = hub.get(word)
    return _unit(v) if v is not None else None


# =========================================================================================================
# C7 -- antonymy (lexical opposition; NON-closure lookup)
# =========================================================================================================
_ANT_STORE: Optional[Set[Tuple[str, str]]] = None
_ANT_MISSING = False


def _ant_norm(w: str) -> str:
    """Normalize an antonym key: lowercase, underscores->spaces (byte-faithful to
    exp_antonym_typed_spoke_valence_v1.load_antonyms)."""
    return str(w).lower().replace("_", " ").strip()


def _ant_store_load() -> Optional[Set[Tuple[str, str]]]:
    """The frozen ConceptNet-Antonym opposition set (unordered lemma pairs, sorted-tuple keys), loaded ONCE. None if
    the gitignored asset is absent -- antonym() abstains."""
    global _ANT_STORE, _ANT_MISSING
    if _ANT_STORE is None and not _ANT_MISSING:
        try:
            z = np.load(_ANT_ASSET, allow_pickle=False)
            a = [str(x) for x in z["ant_a"].tolist()]
            b = [str(x) for x in z["ant_b"].tolist()]
            _ANT_STORE = {tuple(sorted((x, y))) for x, y in zip(a, b)}
        except (FileNotFoundError, OSError, KeyError, ValueError):
            _ANT_MISSING = True
            _ANT_STORE = None
    return _ANT_STORE


def available_antonym() -> bool:
    """Whether the frozen C7 antonym asset is present. False -> antonym() abstains (returns False), never raises."""
    return _ant_store_load() is not None


def antonym(a: str, b: str) -> bool:
    """Whether (a, b) is a stored lexical OPPOSITION (ConceptNet Antonym). Symmetric. The typed spoke a similarity
    read cannot supply: antonyms are MORE distributionally similar than synonyms (symmetric cosine AUC 0.391,
    anti-predictive), so opposition-aware valence REQUIRES this typed edge."""
    st = _ant_store_load()
    if st is None:
        return False
    return tuple(sorted((_ant_norm(a), _ant_norm(b)))) in st


# =========================================================================================================
# C8 -- DIRECTED ENTITY-TYPE SPOKE (proper-name entities onto the C5 taxonomy; DBpedia InstanceOf 2022.12.01).
# Extends the ATL typed store to PROPER NAMES (which WordNet omits), licensing name-bridge coref ("the artist" <-
# Zurbaran; the ~6-10% of anaphoric common nouns whose antecedent is a proper name). A proper name's TYPE is a
# directed instance-of edge (name -> dbo type -> WordNet type lemma), and coref LICENSING reuses the C5 is-a closure
# above -- NO new taxonomy, just proper-name nodes onto the existing one. Ported byte-faithfully from the owner-DONE
# `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref` (experiments/_entity_type_spoke.py +
# build_entity_type_spoke_v1.norm_surface). Island-safe: every read abstains (empty/False) if the asset or WordNet
# is absent, never raises. THE consumer is the two-route name-bridge coref path (consolidated C8 UNION episodic
# in-text is-a); a KB alone is coverage-bounded (+0.034 not-sep), the two-route CLS system is +0.0955 CI-sep.
# =========================================================================================================
_C8_DB = os.path.join(_REPO, "data", "frontend_assets", "entity_type_spoke_v1.sqlite")
_C8_LEMMAS_PATH = os.path.join(_REPO, "data", "frontend_assets", "entity_type_class_lemmas_v1.json")
_C8_PUNCT = re.compile(r"[^a-z0-9 ]")
_C8_WS = re.compile(r"\s+")
_C8_CON = None
_C8_CON_MISSING = False
_C8_LEMMAS: Optional[Dict[str, List[str]]] = None
_C8_CLASS_CACHE: Dict[str, frozenset] = {}


def entity_type_norm_surface(s: str) -> str:
    """Normalize a proper-name surface for C8 keying: URL-decode, underscores->spaces, strip accents (NFKD),
    lowercase, drop non-alphanumerics, collapse whitespace. MUST be byte-identical between build and read
    (byte-faithful to experiments/build_entity_type_spoke_v1.norm_surface)."""
    import unicodedata
    import urllib.parse
    s = urllib.parse.unquote(s)
    s = s.replace("_", " ")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = _C8_PUNCT.sub(" ", s)
    return _C8_WS.sub(" ", s).strip()


def _c8_con():
    """Read-only sqlite connection to the frozen entity-type spoke, or None if the asset is absent (abstain)."""
    global _C8_CON, _C8_CON_MISSING
    if _C8_CON is None and not _C8_CON_MISSING:
        if not os.path.exists(_C8_DB):
            _C8_CON_MISSING = True
            return None
        import sqlite3
        _C8_CON = sqlite3.connect("file:%s?mode=ro" % _C8_DB.replace(os.sep, "/"), uri=True,
                                  check_same_thread=False)
    return _C8_CON


def _c8_lemmas() -> Dict[str, List[str]]:
    global _C8_LEMMAS
    if _C8_LEMMAS is None:
        _C8_LEMMAS = json.load(open(_C8_LEMMAS_PATH, encoding="ascii")) if os.path.exists(_C8_LEMMAS_PATH) else {}
    return _C8_LEMMAS


def available_entity_type() -> bool:
    """Whether the frozen C8 entity-type spoke asset is present. False -> the C8 reads abstain, never raise."""
    return _c8_con() is not None


def entity_classes(surface: str, backoff: bool = False) -> frozenset:
    """The dbo class(es) DBpedia records for a proper-name surface (exact normalized match; redirect aliases already
    folded into the store). backoff=True falls back to the LAST token (surname/head-word; higher recall / lower
    precision). Empty frozenset = abstain. Byte-faithful to experiments/_entity_type_spoke.entity_classes."""
    con = _c8_con()
    if con is None:
        return frozenset()
    key = entity_type_norm_surface(surface)
    if not key:
        return frozenset()
    if key in _C8_CLASS_CACHE:
        return _C8_CLASS_CACHE[key]
    rows = con.execute("SELECT cls FROM types WHERE surf=?", (key,)).fetchall()
    cls = {r[0] for r in rows}
    if not cls and backoff:
        toks = key.split()
        if len(toks) > 1:
            rows = con.execute("SELECT cls FROM types WHERE surf=?", (toks[-1],)).fetchall()
            cls = {r[0] for r in rows}
    fs = frozenset(cls)
    _C8_CLASS_CACHE[key] = fs
    return fs


def entity_type_lemmas(surface: str, backoff: bool = False) -> frozenset:
    """The WordNet-resolvable type LEMMA(s) of a proper-name surface (its dbo classes mapped through the
    class->lemma table). Empty = abstain. Byte-faithful to experiments/_entity_type_spoke.entity_type_lemmas."""
    lm = _c8_lemmas()
    out: Set[str] = set()
    for c in entity_classes(surface, backoff=backoff):
        out.update(lm.get(c, ()))
    return frozenset(out)


def entity_type_synsets(surface: str, backoff: bool = False) -> frozenset:
    """The MFS synset(s) of the entity's type lemmas -- the SYNSET-KEYED read: the type nodes the entity's directed
    instance-of edges point to, read through the SAME C5 taxonomy as lexical knowledge (encyclopedic + lexical
    semantic memory unified in one hub, exactly the ATL). Empty = abstain."""
    out: Set[str] = set()
    for tl in entity_type_lemmas(surface, backoff=backoff):
        ms = _mfs_synset(tl)
        if ms:
            out.add(ms)
    return frozenset(out)


def _entity_license_lemma(anaphor_head: str, type_lemma: str) -> bool:
    """Does a proper-name entity typed `type_lemma` satisfy an anaphor headed `anaphor_head`? True iff equal,
    synonym, or an is-a relation EITHER direction (reuses the C5 closure: painter is-a artist; poet is-a person).
    Unlike coref_type_license this ADMITS exact type match. Byte-faithful to _entity_type_spoke._license_lemma."""
    if anaphor_head == type_lemma:
        return True
    if _wordnet() is None:
        return False
    a = _synset_names(anaphor_head)
    b = _synset_names(type_lemma)
    if not a or not b:
        return False
    if a & b:
        return True                                   # synonym
    if is_a(type_lemma, anaphor_head) or is_a(anaphor_head, type_lemma):
        return True                                   # is-a either direction (C5)
    return False


def entity_is_a(surface: str, type_word: str, backoff: bool = False) -> bool:
    """The DIRECTED C8 instance-of read: is the proper-name entity `surface` a KIND OF `type_word`, via the C5
    closure over its recorded type(s)? 'Zurbaran is-a artist' YES (painter is-a artist); 'Argentina is-a artist' NO.
    Equal/synonym also True. Abstains (False) if the asset/WordNet is absent."""
    for tl in entity_type_lemmas(surface, backoff=backoff):
        if tl == type_word:
            return True
        if _wordnet() is not None:
            if _synset_names(tl) & _synset_names(type_word):
                return True
            if is_a(tl, type_word):                   # the entity's specific type is a KIND OF type_word
                return True
    return False


def type_licenses(anaphor_head: str, surface: str, backoff: bool = False,
                  lemmas_override: Optional[frozenset] = None) -> bool:
    """The bounded TYPE-LICENSE for a name-bridge link: may a common-noun anaphor headed `anaphor_head` co-refer
    with the proper-name antecedent `surface` on entity-type grounds? True iff ANY of the entity's type lemmas
    licenses the anaphor head (equal / synonym / is-a either direction). `lemmas_override` lets the shuffled-KB twin
    inject remapped types. Byte-faithful to experiments/_entity_type_spoke.type_licenses. THE name-bridge consumer."""
    lems = lemmas_override if lemmas_override is not None else entity_type_lemmas(surface, backoff=backoff)
    for tl in lems:
        if _entity_license_lemma(anaphor_head, tl):
            return True
    return False


# =========================================================================================================
# OFFLINE BUILD (static admissible foundation assets; run once, gitignored)
# =========================================================================================================
def _load_cn_pairs(rel: str) -> List[Tuple[str, str]]:
    """(s, o) pairs from a bridge_relation_assets_v1 relation jsonl. Byte-faithful to
    exp_partwhole_typed_spoke_bridging_v1._load_cn."""
    fp = os.path.join(_CN_DIR, rel + ".jsonl")
    if not os.path.exists(fp):
        return []
    return [(d["s"], d["o"]) for d in (json.loads(l) for l in open(fp, encoding="ascii"))]


def wn_meronymy(hub) -> List[Tuple[str, str]]:
    """(part, whole) meronymy edges from WordNet over concrete lexnames, both endpoints in hub. Byte-faithful to
    exp_partwhole_typed_spoke_bridging_v1.wn_meronymy."""
    wn = _wordnet()
    if wn is None:
        return []
    CONC = ("noun.artifact", "noun.body", "noun.food", "noun.plant", "noun.animal", "noun.object", "noun.substance")
    out: List[Tuple[str, str]] = []
    for syn in wn.all_synsets("n"):
        if syn.lexname() not in CONC:
            continue
        wholes = [l.name().lower() for l in syn.lemmas() if "_" not in l.name()]
        for mer in (syn.part_meronyms() + syn.substance_meronyms()):
            parts = [l.name().lower() for l in mer.lemmas() if "_" not in l.name()]
            for w in wholes:
                for p in parts:
                    if w != p and w in hub and p in hub:
                        out.append((p, w))
    return out


def build_partwhole_graph(hub) -> Set[Tuple[str, str]]:
    """Directed (part->whole) edges from WordNet meronymy + ConceptNet PartOf/HasA/MadeOf, both endpoints in hub.
    Byte-faithful to exp_partwhole_typed_spoke_bridging_v1.build_partwhole_graph (incl. its edge orientations)."""
    edges: Set[Tuple[str, str]] = set()
    for s, o in _load_cn_pairs("PartOf"):
        if s in hub and o in hub and s != o:
            edges.add((s, o))
    for s, o in _load_cn_pairs("MadeOf"):
        if s in hub and o in hub and s != o:
            edges.add((s, o))            # object MadeOf material: material is a 'part'
    for s, o in _load_cn_pairs("HasA"):
        if s in hub and o in hub and s != o:
            edges.add((o, s))            # s HasA o -> o is part of s
    for p, w in wn_meronymy(hub):
        edges.add((p, w))
    return edges


def build_instrument_graph(hub) -> Set[Tuple[str, str]]:
    """Directed (instrument->purpose) edges from ConceptNet UsedFor, both endpoints in hub. Byte-faithful to
    exp_partwhole_typed_spoke_bridging_v1.eval_bridging's instrument pw_graph."""
    return {(s, o) for s, o in _load_cn_pairs("UsedFor") if s in hub and o in hub}


def _protos_for(edges: Set[Tuple[str, str]], hub) -> Tuple[List[str], np.ndarray, List[str], List[str]]:
    """Build the per-whole holonym prototypes (mean unit-hub of the whole's parts) + the flat edge arrays for a
    family. Returns (wholes, proto float16 [K,200], edge_part, edge_whole)."""
    parts_of: Dict[str, Set[str]] = collections.defaultdict(set)
    ep: List[str] = []
    ew: List[str] = []
    for p, w in sorted(edges):
        parts_of[w].add(p)
        ep.append(p)
        ew.append(w)
    U = {w: _unit(hub[w]) for w in {x for e in edges for x in e} if w in hub}
    dim = len(next(iter(U.values()))) if U else 200
    wholes = sorted(parts_of.keys())
    proto = np.zeros((len(wholes), dim), dtype=np.float16)
    for i, w in enumerate(wholes):
        ps = [U[p] for p in parts_of[w] if p in U]
        if ps:
            proto[i] = _unit(np.mean(ps, axis=0)).astype(np.float16)
    return wholes, proto, ep, ew


def build_and_freeze_partwhole(path: str = _PW_ASSET) -> Dict:
    """Fit + freeze the C6 part-whole + instrument spoke asset (float16 prototypes + edge lists). OFFLINE ONLY.
    Atomic write. The consolidation gate for C6 (NON-closure) is edge-level provenance+resolution: every edge is a
    curated KB fact resolved to a hub lemma (keep-all on a clean source), so the build IS the admission."""
    import pickle
    hub = pickle.load(open(_HUB_PATH, "rb"))["hub"]
    pw_edges = build_partwhole_graph(hub)
    inst_edges = build_instrument_graph(hub)
    pw_w, pw_proto, pw_ep, pw_ew = _protos_for(pw_edges, hub)
    in_w, in_proto, in_ep, in_ew = _protos_for(inst_edges, hub)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez(tmp,
             part_wholes=np.array(pw_w), part_proto=pw_proto,
             part_edge_part=np.array(pw_ep), part_edge_whole=np.array(pw_ew),
             instrument_wholes=np.array(in_w), instrument_proto=in_proto,
             instrument_edge_part=np.array(in_ep), instrument_edge_whole=np.array(in_ew))
    os.replace(tmp, path)
    return {"path": path, "part_wholes": len(pw_w), "part_edges": len(pw_ep),
            "instrument_wholes": len(in_w), "instrument_edges": len(in_ep),
            "bytes": os.path.getsize(path)}


def build_and_freeze_antonym(path: str = _ANT_ASSET) -> Dict:
    """Fit + freeze the C7 antonym spoke asset from ConceptNet Antonym (the full on-disk opposition set). OFFLINE
    ONLY. Atomic write. Byte-faithful to exp_antonym_typed_spoke_valence_v1.load_antonyms' normalization (NOT
    hub-filtered here -- the frozen store is the complete lexical-opposition foundation; consumers filter as needed)."""
    a_list: List[str] = []
    b_list: List[str] = []
    seen: Set[Tuple[str, str]] = set()
    if os.path.exists(_CN_100K):
        for ln in open(_CN_100K, encoding="utf-8"):
            d = json.loads(ln)
            if d.get("predicate") == "Antonym":
                a = _ant_norm(d["subject"])
                b = _ant_norm(d["object"])
                if a and b and a != b:
                    key = tuple(sorted((a, b)))
                    if key not in seen:
                        seen.add(key)
                        a_list.append(a)
                        b_list.append(b)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez(tmp, ant_a=np.array(a_list), ant_b=np.array(b_list))
    os.replace(tmp, path)
    return {"path": path, "antonym_pairs": len(a_list), "bytes": os.path.getsize(path)}


def _build_main() -> None:
    import time
    t0 = time.time()
    print("[typed_spokes] building C6 part-whole/instrument spoke (WordNet meronymy scan is the slow step) ...",
          flush=True)
    pw = build_and_freeze_partwhole()
    print("[typed_spokes] C6 froze -> %s (%.2f MB): part wholes=%d edges=%d | instrument wholes=%d edges=%d (%.1fs)"
          % (pw["path"], pw["bytes"] / 1e6, pw["part_wholes"], pw["part_edges"],
             pw["instrument_wholes"], pw["instrument_edges"], time.time() - t0), flush=True)
    t1 = time.time()
    ant = build_and_freeze_antonym()
    print("[typed_spokes] C7 froze -> %s (%.3f MB): antonym pairs=%d (%.1fs)"
          % (ant["path"], ant["bytes"] / 1e6, ant["antonym_pairs"], time.time() - t1), flush=True)
    print("[typed_spokes] total build %.1fs" % (time.time() - t0), flush=True)


def self_test() -> bool:
    """Reproduce the load-bearing directions of each spoke (needs nltk WordNet; C6/C7 need the built assets)."""
    wn = _wordnet()
    assert wn is not None, "nltk WordNet required for the self-test"
    # C5 is-a: DIRECTED (taxi is-a car, not the reverse); entails flips under negation.
    assert is_a("taxi", "car") and not is_a("car", "taxi"), "is-a is directed"
    assert is_a("dog", "animal") and not is_a("animal", "dog"), "dog is-a animal (directed)"
    assert entails("taxi", "car", negated=False), "upward: taxi -> car entails"
    assert not entails("car", "taxi", negated=False), "upward: car -> taxi does NOT entail"
    assert entails("dog", "mammal", negated=False), "upward: dog -> mammal entails"
    assert entails("mammal", "dog", negated=True), "downward (negated): not-a-mammal entails not-a-dog"
    assert not entails("dog", "mammal", negated=True), "downward flips: not-a-dog does NOT entail not-a-mammal"
    # isa_ancestors closure includes a mid + top node.
    anc = isa_ancestors(_mfs_synset("dog"))
    assert "animal.n.01" in anc or "carnivore.n.01" in anc, "closure reaches an ancestor: %s" % (sorted(anc)[:5],)
    # parse-free monotonicity marker.
    assert is_downward("no delegate finished the report") and not is_downward("some delegates finished")
    assert not is_downward("no one did not leave"), "double DE (no, not) -> even -> upward"
    assert is_downward("at most ten delegates finished"), "phrase operator 'at most' -> downward"
    assert not is_downward("a few delegates finished"), "'a few' is UPWARD (article guard)"
    assert natural_logic_label("a taxi arrived", "a car arrived") == "entailment"
    assert natural_logic_label("a man won the big prize", "a man won the prize") == "entailment"  # upward del
    # C5+C6 TYPE-LICENSING for coref: is-a either direction / part-whole license; same-head + unrelated do NOT.
    assert coref_type_license("animal", "dog") and coref_type_license("dog", "animal"), "is-a either direction"
    assert not coref_type_license("dog", "dog"), "same head is the head-identity linker's job"
    assert not coref_type_license("dog", "democracy"), "unrelated heads are NOT licensed to bridge"
    # gate + closure shape.
    admitted = gate_isa_edges([("dog.n.01", "mammal.n.01")])
    anc_map = close_isa({("dog.n.01", "mammal.n.01"), ("mammal.n.01", "animal.n.01")})
    assert "animal.n.01" in anc_map["dog.n.01"], "transitive closure: %s" % anc_map
    # C6 part-whole / instrument (needs the built asset).
    if available_partwhole():
        assert holonym_prototype("car") is not None or holonym_prototype("automobile") is not None, \
            "a common whole should have a prototype"
    # C7 antonym (needs the built asset).
    if available_antonym():
        # ConceptNet holds common oppositions; symmetric.
        assert antonym("hot", "cold") == antonym("cold", "hot"), "antonym is symmetric"
    print("SELFTEST PASS (is-a directed + entails flips under negation + marker + closure"
          + ("; C6 proto" if available_partwhole() else "")
          + ("; C7 antonym" if available_antonym() else "") + ")", flush=True)
    return True


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="typed_spokes: build the offline C6/C7 assets, or self-test the reads.")
    ap.add_argument("--build", action="store_true", help="fit + freeze the offline C6 part-whole/instrument + C7 antonym assets")
    ap.add_argument("--self-test", action="store_true", help="reproduce the load-bearing spoke directions")
    a = ap.parse_args()
    if a.build:
        _build_main()
    if a.self_test:
        self_test()
    if not (a.build or a.self_test):
        print("C6 part-whole/instrument present: %s (%s)" % (available_partwhole(), _PW_ASSET))
        print("C7 antonym present: %s (%s)" % (available_antonym(), _ANT_ASSET))
