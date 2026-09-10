"""_polarity_operator -- a glass-box TRUTH-CONDITIONAL polarity + quantity OPERATOR over the reader's
extracted event/argument propositions. It does NOT re-extract: it CONSUMES an already-extracted
proposition (predicate token index + the sentence tokens + the argument set) and decides (a) whether the
proposition HOLDS (polarity) and (b) over HOW MANY / WHICH of its argument set it ranges (cardinality/scope).

BRAIN FRAME (PINNED -- the computation we copy):
  * NEGATION IS AN OPERATOR THAT TOGGLES THE TRUTH VALUE OF A REPRESENTED PROPOSITION, not a lexeme that
    adds a fact. Kaup & Zwaan (2005); Kaup, Ludtke & Zwaan (2006): comprehension is TWO-STEP -- the reader
    transiently represents the to-be-negated state (the key BEING taken) then represents the ACTUAL state
    (the key NOT taken) and ENDS on the actual state. A polarity-blind extractor performs only step ONE (it
    keeps the embedded positive content), which is exactly the bug. Neuroscience: negating an action sentence
    SUPPRESSES activation of the negated content (Tettamanti 2008; Tomasino 2010) -- an inhibitory operation
    OVER a proposition; logical/scopal composition recruits left inferior frontal cortex.
  * QUANTIFICATION IS CARDINALITY OVER THE MODEL'S TOKEN SET. Johnson-Laird mental models: "some" = at least
    one token; "all/every/each" = every token of the set; "none/no" = ZERO tokens; "everyone but X" = every
    token except the X token. "none" UNIFIES with negation: zero tokens satisfy the predicate == the
    existential does NOT hold (not(exists x. P x)). So a negative quantifier subject is BOTH a cardinality
    (0) AND a polarity flip -- one representation, the ACTUAL state of affairs.
  * SCOPE IS THE OPERATOR'S CLAUSE-LOCAL c-command DOMAIN. Negation toggles its own finite clause's
    predicate and any predicate COORDINATED with it at the same clausal level; it does NOT cross into an
    embedded COMPLEMENT clause. A complement clause's factuality is governed by the MATRIX verb's
    IMPLICATIVE / FACTIVE signature (Karttunen 1971 implicatives; de Marneffe 2012 veridicality), NOT by
    negation propagation -- "did not remember [X happening]" leaves X TRUE (factive presupposition survives
    negation); "did not manage to X" makes X FALSE (implicative); "did not want to X" leaves X UNKNOWN.

THE PARAMETERS WE SWEEP (OUR-INVENTION-UNDER-TEST -- labelled; copy the computation, sweep these):
  the cue lexicon, the transparent-adverb skip window, the coordinator set, the implicative/factive lexicon,
  the quantifier -> cardinality table, the exception construction ("but/except X"), the abstain thresholds.

REUSE (do NOT re-derive): hdlab.state_register supplies the polarity PRIMITIVE (StateSpan polarity +1/-1),
the antonym/contradiction guards (incompatible, _contradictory_pair) and the ATL-hub WordNet entailment
matcher (state_match: MATCH/NO/NONE with privative / open-vs-closed-scale / typed-antonymy guards). This
operator is the copular-state polarity primitive EXTENDED onto EVENT/action propositions + a quantifier layer.

GLASS-BOX: pure symbolic; NO external LLM, NO learned NLI black box, NO network at inference. ASCII only.
EXPERIMENTS-side (the solver may not write hdlab/); SOLVED.md states the proposed hdlab landing.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'truth-conditional POLARITY + quantity operator over extracted propositions (pinned truth-conditional frame); the live surface-scan is kept because the parse-aware c-command version measured WORSE (0.909<0.932) -- a parser-gated located-negative, revisit when C3 parser improves'
__bf_corrections__ = []


from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------------------------------
# CUE LEXICONS (OUR-INVENTION-UNDER-TEST -- sweep). Clause-local sentential negators.
# --------------------------------------------------------------------------------------------------
# do-support / modal / adverbial sentential negation ("did not", "n't", "never")
NEG_CUES = {"not", "never", "no", "cannot"}
# informal / web-register contractions WITHOUT the apostrophe (EWT is naturalistic web text). These are
# overwhelmingly negations in-register; SWEPT (a rare noun "cant"/"wont" is the tolerated tail).
NEG_NO_APOS = {"dont", "cant", "wont", "wouldnt", "couldnt", "shouldnt", "didnt", "doesnt", "isnt",
               "arent", "wasnt", "wasent", "werent", "havent", "hasnt", "hadnt", "aint", "cannot",
               "neednt", "mustnt", "shant", "mightnt"}
# negative-quantifier / negative-existential SUBJECTS (these ALSO carry cardinality 0 -- the unification)
NEG_QUANT = {"no", "none", "nobody", "nothing", "neither", "nowhere"}
# adverbs + AUXILIARIES transparent to the backward negator scan (a negator may sit across them: "did not
# REALLY want", "cannot BE eliminated", "has not YET penetrated", "would not HAVE been done").
_ASPECT_ADV = {"really", "ever", "always", "just", "simply", "even", "quite", "only", "truly", "yet",
               "actually", "once", "also", "still", "necessarily", "particularly", "generally", "longer"}
_AUX = {"be", "been", "being", "is", "are", "am", "was", "were", "have", "has", "had", "do", "does",
        "did", "will", "would", "can", "could", "shall", "should", "may", "might", "must", "to"}
NEG_TRANSPARENT = _ASPECT_ADV | _AUX
# focus items that CANCEL a would-be negation ("not only", "no matter", "not just") -- litotes/focus guards
FOCUS_AFTER = {"only", "just", "merely", "simply", "matter"}
NEG_MAX_SKIP = 5
# coordinators. COORD = any coordinator (structure detection); COORD_SHARE = the ones that SHARE a negation
# across VP-coordination. "but" is CONTRASTIVE ("not done a test BUT have done a panel" -> the 2nd clause is
# AFFIRMATIVE), so it BLOCKS negation sharing; "and/or/nor" share it ("not eat or sleep" -> both negated,
# De Morgan). This is the categorial-parallelism + polarity-of-the-coordinator rule (not a learned label).
COORD = {"and", "or", "nor", "but"}
COORD_SHARE = {"and", "or", "nor", ","}
# tokens that OPEN an embedded complement / subordinate clause -> a scope boundary the matrix negation does
# NOT cross by propagation (the complement's factuality comes from the matrix verb's implicative signature)
CLAUSE_BOUNDARY = {"that", "which", "who", "whom", "whose", "because", "since", "although", "though",
                   "while", "when", "where", "if", "unless", "after", "before", "as", "so",
                   "whether", "how", "why", "what", "until"}

# --------------------------------------------------------------------------------------------------
# IMPLICATIVE / FACTIVE SIGNATURES (Karttunen; de Marneffe veridicality) -- OUR-INVENTION-SWEEP, closed
# lexicon. Signature = (factuality of the complement when the matrix is POSITIVE, when the matrix is
# NEGATED). +1 = complement TRUE, -1 = complement FALSE, 0 = UNKNOWN (non-implicative / neutral).
# This is how the brain assigns complement-clause factuality WITHOUT propagating negation into it.
# --------------------------------------------------------------------------------------------------
IMPLICATIVE: Dict[str, Tuple[int, int]] = {
    # two-way implicatives: complement truth flips with the matrix polarity
    "manage": (+1, -1), "manages": (+1, -1), "managed": (+1, -1),
    "dare": (+1, -1), "dared": (+1, -1),
    "bother": (+1, -1), "bothered": (+1, -1),
    "remember": (+1, -1), "remembered": (+1, -1),   # remember-to (as implicative)
    "happen": (+1, -1), "happened": (+1, -1),
    # one-way (+): positive matrix -> complement true; negated matrix -> unknown
    "force": (+1, 0), "forced": (+1, 0), "cause": (+1, 0), "caused": (+1, 0),
    "make": (+1, 0), "made": (+1, 0), "get": (+1, 0), "got": (+1, 0),
    # more two-way implicatives (Karttunen 1971; de Marneffe et al. 2012) -- curated stored signatures
    "condescend": (+1, -1), "condescended": (+1, -1), "deign": (+1, -1), "deigned": (+1, -1),
    "prove": (+1, -1), "proved": (+1, -1), "proven": (+1, -1),
    # more one-way (+): positive matrix -> complement true; negated matrix -> unknown
    "compel": (+1, 0), "compelled": (+1, 0), "drive": (+1, 0), "drove": (+1, 0),
    "lead": (+1, 0), "led": (+1, 0), "prompt": (+1, 0), "prompted": (+1, 0), "enable": (+1, 0), "enabled": (+1, 0),
    # negative implicatives: positive matrix -> complement FALSE; negated matrix -> TRUE
    "fail": (-1, +1), "failed": (-1, +1), "fails": (-1, +1),
    "refuse": (-1, +1), "refused": (-1, +1), "decline": (-1, +1), "declined": (-1, +1),
    "forget": (-1, +1), "forgot": (-1, +1), "neglect": (-1, +1), "neglected": (-1, +1),
    "prevent": (-1, +1), "prevented": (-1, +1), "avoid": (-1, +1), "avoided": (-1, +1),
    "hesitate": (-1, +1), "hesitated": (-1, +1),   # 'hesitate to X' -> not X; 'not hesitate to X' -> X
    "omit": (-1, +1), "omitted": (-1, +1), "refrain": (-1, +1), "refrained": (-1, +1),
    "forbear": (-1, +1), "forbore": (-1, +1),
    # non-implicative / neutral (desideratives, propositional attitudes): complement UNKNOWN either way
    "want": (0, 0), "wanted": (0, 0), "wish": (0, 0), "wished": (0, 0), "hope": (0, 0), "hoped": (0, 0),
    "try": (0, 0), "tried": (0, 0), "plan": (0, 0), "planned": (0, 0), "intend": (0, 0), "intended": (0, 0),
    "expect": (0, 0), "expected": (0, 0), "believe": (0, 0), "believed": (0, 0),
    "think": (0, 0), "thought": (0, 0), "seem": (0, 0), "seemed": (0, 0), "appear": (0, 0), "appeared": (0, 0),
    "decide": (0, 0), "decided": (0, 0), "agree": (0, 0), "agreed": (0, 0), "offer": (0, 0), "offered": (0, 0),
    "promise": (0, 0), "promised": (0, 0), "mean": (0, 0), "meant": (0, 0), "prefer": (0, 0), "preferred": (0, 0),
    "choose": (0, 0), "chose": (0, 0), "claim": (0, 0), "claimed": (0, 0), "attempt": (0, 0), "attempted": (0, 0),
    "seek": (0, 0), "sought": (0, 0), "aim": (0, 0), "aimed": (0, 0), "strive": (0, 0), "strove": (0, 0),
    "threaten": (0, 0), "threatened": (0, 0), "propose": (0, 0), "proposed": (0, 0), "suggest": (0, 0),
    "suggested": (0, 0), "vow": (0, 0), "vowed": (0, 0), "long": (0, 0), "longed": (0, 0),
}
# FACTIVE verbs: their complement is PRESUPPOSED true and SURVIVES matrix negation (both slots +1).
FACTIVE = {"know", "knew", "realize", "realized", "regret", "regretted", "notice", "noticed",
           "discover", "discovered", "admit", "admitted", "reveal", "revealed",
           "acknowledge", "acknowledged", "recognize", "recognized", "confess", "confessed",
           "observe", "observed", "resent", "resented", "understand", "understood"}
for _f in FACTIVE:
    IMPLICATIVE.setdefault(_f, (+1, +1))


# --------------------------------------------------------------------------------------------------
# QUANTIFIER -> CARDINALITY (Johnson-Laird tokens over the argument set). OUR-INVENTION-SWEEP.
# card class: "ALL" every token | "SOME" >=1 | "ZERO" 0 | "MOST" > half | "FEW" small>0 | "EXC" all-but-X
# holds_of(quant, is_member, is_exception): does the predicate hold of a queried individual?
# --------------------------------------------------------------------------------------------------
QUANT_CARD: Dict[str, str] = {
    "all": "ALL", "every": "ALL", "each": "ALL", "everyone": "ALL", "everybody": "ALL",
    "everything": "ALL", "both": "ALL", "any": "ALL",
    "some": "SOME", "several": "SOME", "many": "SOME", "a": "SOME", "an": "SOME",
    "someone": "SOME", "somebody": "SOME", "something": "SOME", "certain": "SOME", "various": "SOME",
    "no": "ZERO", "none": "ZERO", "nobody": "ZERO", "nothing": "ZERO", "neither": "ZERO", "no-one": "ZERO",
    "most": "MOST", "few": "FEW", "little": "FEW",
}
EXCEPT_MARKERS = {"but", "except", "excepting", "save", "besides", "aside"}
_SUBJ_PRON = {"i", "you", "he", "she", "it", "we", "they"}


def canon(tok: str) -> str:
    return tok.lower().strip().strip(".,;:'\"!?()")


# ==================================================================================================
# NEGATION SCOPE (clause-local, coordination-aware, complement-gated) -- the brain-foundational operator.
# ==================================================================================================
def _is_negator(tok: str) -> bool:
    t = canon(tok)
    return t in NEG_CUES or t in NEG_NO_APOS or tok.lower().endswith("n't")


def _neg_quant_subject(toks: Sequence[str], pred_idx: int) -> bool:
    """A NEGATIVE-EXISTENTIAL subject governs this predicate: 'no one left', 'none of the guards moved',
    'nobody agreed', 'not a single guard moved'. Scans the pre-verbal region for a negative quantifier
    heading the subject NP (before any clause boundary). This is the cardinality-0 == not-exists case."""
    for i in range(max(0, pred_idx - 1), -1, -1):
        t = canon(toks[i])
        if not t:
            continue
        if t in NEG_QUANT:
            # 'no one', 'no-one' handled by NEG_QUANT('no'/'no-one'); guard 'no matter'
            nxt = canon(toks[i + 1]) if i + 1 < len(toks) else ""
            if t == "no" and nxt in FOCUS_AFTER:
                return False
            return True
        if t in CLAUSE_BOUNDARY or t in COORD:
            break            # left the subject's clause
    return False


def clause_local_negated(toks: Sequence[str], pred_idx: int) -> Tuple[bool, str]:
    """Is the predicate at toks[pred_idx] DIRECTLY negated within its own clause?
    Returns (negated, provenance). Two brain-faithful routes:
      (1) do-support/modal/adverbial negator immediately LEFT of the verb, skipping transparent adverbs
          (reuses hdlab.goal_typing._verb_negated_before semantics; a negator on a following 'to VP'
          complement never suppresses -- it sits AFTER the verb);
      (2) a negative-existential SUBJECT ('no one', 'none', 'nobody') -- cardinality 0 == not-exists.
    Focus/litotes guard: 'not only/just' does NOT negate the proposition (it foregrounds it)."""
    n = len(toks)
    if pred_idx < 0 or pred_idx >= n:
        return False, "no_verb"
    # route (1): backward do-support / modal / never scan
    steps = 0
    j = pred_idx - 1
    while j >= 0 and steps <= NEG_MAX_SKIP:
        t = canon(toks[j])
        if not t:
            j -= 1
            continue
        if _is_negator(toks[j]):
            nxt = canon(toks[j + 1]) if j + 1 < n else ""
            if nxt in FOCUS_AFTER:                        # 'not only' -> foregrounds, not negates
                return False, "focus_cancelled"
            return True, "direct_negator"
        # interrogative subject-aux INVERSION: '[cannot] [you] [see]' -- a subject pronoun may sit between
        # the inverted aux-negator and the verb ('can't you see', 'did he not go'). Skip ONE subject pronoun
        # iff its LEFT neighbour is a negator.
        if t in _SUBJ_PRON and j - 1 >= 0 and _is_negator(toks[j - 1]):
            return True, "inversion_negator"
        if t in NEG_TRANSPARENT:
            j -= 1
            steps += 1
            continue
        break                                             # a content word / boundary stops the scan
    # route (2): negative-existential SUBJECT ('no one left', 'none moved')
    if _neg_quant_subject(toks, pred_idx):
        return True, "neg_quant_subject"
    # route (3): post-verbal negative-quantifier OBJECT ('has NO money', 'found NO evidence', 'saw NO one')
    # -- a negative determiner on the object takes sentential scope (Klima): the have/find relation is FALSE.
    for i in range(pred_idx + 1, min(n, pred_idx + 4)):
        ci = canon(toks[i])
        if not ci:
            continue
        if ci in NEG_QUANT:
            return True, "neg_quant_object"
        if ci in CLAUSE_BOUNDARY or ci in COORD or ci == "to":
            break
        if i > pred_idx + 1 and ci not in ("a", "an", "the", "any", "much", "many"):
            break                                         # only a determiner-adjacent object neg counts
    return False, "none"


def _verb_indices(pos: Optional[Sequence[str]], toks: Sequence[str],
                  verb_lows: Optional[set] = None) -> List[int]:
    """Token indices that are verbs. Uses POS when supplied; else a light heuristic (verb_lows set)."""
    if pos is not None:
        return [i for i, p in enumerate(pos) if p == "VERB"]
    if verb_lows is not None:
        return [i for i, t in enumerate(toks) if canon(t) in verb_lows]
    return []


def coordination_shares_negation(toks: Sequence[str], neg_verb_idx: int, target_idx: int,
                                 verb_idxs: Sequence[int]) -> bool:
    """Does the negation on neg_verb_idx SHARE (via VP-coordination) with the predicate at target_idx?
    Brain-faithful surface test (categorial parallelism + overt coordinator), NOT a learned deprel label:
      target is to the RIGHT of neg_verb, an overt COORDINATOR ('and/or/nor/but'/comma) sits between them,
      and NO clause boundary / complementizer / 'to'-infinitive / new finite subject intervenes.
    This catches 'she did not eat AND sleep' (shared) while refusing 'she did not want [to sleep]'
    (complement -- no coordinator, has 'to') and 'she did not eat, and HE slept' (new subject)."""
    if target_idx <= neg_verb_idx:
        return False
    raw = list(toks[neg_verb_idx + 1:target_idx])
    seg = [canon(t) for t in raw]
    if "but" in seg:
        return False                                       # CONTRASTIVE coordinator -> 2nd clause affirmative
    # a coordinator OR a comma is the sharing signal (canon() strips punctuation, so check raw for ',')
    if not (any(c in COORD_SHARE for c in seg) or any(t == "," for t in raw)):
        return False                                       # no negation-sharing coordinator/comma -> not coord
    for c in seg:
        if c in CLAUSE_BOUNDARY or c == "to":
            return False                                   # complement/subordinate/infinitival boundary
    # CHAIN: intervening verbs ARE allowed (a coordination LIST 'invade, endanger and butcher' shares the
    # negation across all conjuncts -- Johnson-Laird categorial parallelism). A NEW explicit subject pronoun
    # between them would start a fresh clause -> block (that is clausal, not VP, coordination).
    if any(c in ("i", "you", "he", "she", "it", "we", "they") for c in seg):
        return False
    return True


def complement_factuality(matrix_lemma: str, matrix_negated: bool) -> Optional[int]:
    """If matrix_lemma is a known implicative/factive verb, the factuality its complement inherits:
    +1 true, -1 false, 0/None unknown. This REPLACES negation propagation into the complement (the
    upstream fix for the conj/complement over-propagation wall)."""
    sig = IMPLICATIVE.get(canon(matrix_lemma))
    if sig is None:
        return None
    pos_val, neg_val = sig
    v = neg_val if matrix_negated else pos_val
    return v if v != 0 else None


@dataclass
class PolarityReadout:
    """The operator's decision for one event proposition."""
    polarity: int                 # +1 holds, -1 does-not-hold, 0 undetermined (abstain)
    provenance: str               # why (direct_negator / neg_quant_subject / coord_shared / implicative:<v> / positive)
    scoped: bool                  # whether an operator (not the default +1) actually fired


def event_polarity(toks: Sequence[str], pred_idx: int, pred_lemma: str = "",
                   pos: Optional[Sequence[str]] = None, verb_lows: Optional[set] = None,
                   propagate: bool = True, implicative: bool = True) -> PolarityReadout:
    """The truth-conditional polarity of the event proposition at toks[pred_idx].
    propagate=False, implicative=False -> the ABLATION (direct clause-local negation only)."""
    direct, prov = clause_local_negated(toks, pred_idx)
    if direct:
        return PolarityReadout(-1, prov, True)
    verb_idxs = _verb_indices(pos, toks, verb_lows)
    # complement gate: if this verb is the COMPLEMENT of an implicative/factive matrix verb to its LEFT,
    # its factuality comes from the matrix signature -- NOT from propagation.
    if implicative:
        for mv in reversed([v for v in verb_idxs if v < pred_idx]):
            # a 'to'/'that'/bare complement of mv: mv is implicative and governs pred_idx
            seg = [canon(t) for t in toks[mv + 1:pred_idx]]
            if any(c in COORD for c in seg):
                break                                       # coordination, not complementation
            mlem = canon(toks[mv])
            sig = IMPLICATIVE.get(mlem)
            if sig is not None:
                m_neg, _ = clause_local_negated(toks, mv)
                # MEMORY-VERB COMPLEMENT-TYPE (Kiparsky & Kiparsky 1970 factive gerunds): 'remember/forget +
                # GERUND or THAT' is FACTIVE -- the complement is PRESUPPOSED true and SURVIVES matrix negation
                # ('did not remember [George telling]' -> telling TRUE). 'remember/forget + TO' is IMPLICATIVE.
                if mlem in ("remember", "remembered", "forget", "forgot", "recall", "recalled"):
                    gerund = pred_lemma.endswith("ing") or canon(toks[pred_idx]).endswith("ing")
                    thatcomp = "that" in seg
                    if gerund or thatcomp:
                        return PolarityReadout(+1, "factive:%s" % mlem, True)
                fv = complement_factuality(toks[mv], m_neg)
                if fv is not None:
                    return PolarityReadout(fv, "implicative:%s%s" % (mlem, "(neg)" if m_neg else ""), True)
                return PolarityReadout(0, "attitude:%s" % mlem, True)   # want/hope -> unknown
            break                                           # nearest left verb is not implicative -> stop
    # coordination propagation: a negated verb to the LEFT that shares via VP-coordination
    if propagate:
        for nv in [v for v in verb_idxs if v < pred_idx]:
            nvneg, _ = clause_local_negated(toks, nv)
            if nvneg and coordination_shares_negation(toks, nv, pred_idx, verb_idxs):
                return PolarityReadout(-1, "coord_shared", True)
    return PolarityReadout(+1, "positive", False)


# ==================================================================================================
# PARSE-AWARE SCOPE RESOLUTION (the brain's actual mechanism -- syntactic scope over the dependency tree).
# The brain resolves negation scope STRUCTURALLY: negation is an advmod on its verb; coordination shares it
# via conj edges; a complement clause (xcomp/ccomp/acl) is a scope island whose factuality comes from the
# matrix verb's implicative/factive signature; an object negative-determiner (det 'no') takes sentential scope.
# This consumes the reader's OWN front-end parse (heads + arc-labeler deprels) -- 1-BASED indices, as the
# arceager parser / ArcLabeler emit. It is the principled successor to the surface scan; the residual it
# cannot cross is a PARSE-ATTACHMENT error (a mis-attached conj), which is the upstream parser-quality lever.
# ==================================================================================================
def _children(heads: Dict[int, int]) -> Dict[int, List[int]]:
    ch: Dict[int, List[int]] = {}
    for c, h in heads.items():
        ch.setdefault(h, []).append(c)
    return ch


def _directly_negated_parsed(v: int, toks: Sequence[str], heads: Dict[int, int],
                             labels: Dict[int, str], children: Dict[int, List[int]]) -> bool:
    """Verb v (1-based) carries a direct negation: an advmod/neg negator child ('not'/'never'/'n't'), OR a
    negative-determiner on its subject ('no one'), OR a negative-determiner on its object ('has no money')."""
    for c in children.get(v, []):
        tok = toks[c - 1]
        if _is_negator(tok) and labels.get(c) in ("advmod", "neg", "aux", "det"):
            nxt = canon(toks[c]) if c < len(toks) else ""
            if nxt in FOCUS_AFTER:
                return False
            return True
        # a nominal argument (subj/obj) headed by / determined by a negative quantifier
        if labels.get(c) in ("nsubj", "obj", "nsubj:pass", "obl"):
            if canon(tok) in NEG_QUANT:
                return True
            for gc in children.get(c, []):
                if labels.get(gc) == "det" and canon(toks[gc - 1]) in NEG_QUANT:
                    return True
    return False


def event_polarity_parsed(v: int, toks: Sequence[str], heads: Dict[int, int], labels: Dict[int, str],
                          implicative: bool = True, propagate: bool = True) -> PolarityReadout:
    """Structural polarity of the verb at 1-based index v, over the reader's dependency parse.
    Mirrors event_polarity but resolves scope from heads+deprels instead of a surface scan."""
    children = _children(heads)
    if _directly_negated_parsed(v, toks, heads, labels, children):
        return PolarityReadout(-1, "parsed_direct", True)
    lab = labels.get(v)
    head = heads.get(v)
    # COMPLEMENT clause (xcomp/ccomp/acl/advcl): factuality from the matrix verb's implicative/factive signature
    if implicative and lab in ("xcomp", "ccomp", "acl", "acl:relcl", "advcl", "csubj") and head and head >= 1:
        mlem = canon(toks[head - 1])
        sig = IMPLICATIVE.get(mlem)
        m_neg = _directly_negated_parsed(head, toks, heads, labels, children)
        if mlem in ("remember", "remembered", "forget", "forgot", "recall", "recalled") and \
                (lab in ("ccomp", "acl", "acl:relcl") or canon(toks[v - 1]).endswith("ing")):
            return PolarityReadout(+1, "parsed_factive:%s" % mlem, True)   # factive gerund/that survives negation
        if sig is not None:
            fv = complement_factuality(toks[head - 1], m_neg)
            if fv is not None:
                return PolarityReadout(fv, "parsed_implicative:%s%s" % (mlem, "(neg)" if m_neg else ""), True)
            return PolarityReadout(0, "parsed_attitude:%s" % mlem, True)
        # non-implicative complement of a NEGATED matrix -> unknown (do NOT propagate); of a positive matrix -> +1
        return PolarityReadout(0 if m_neg else 1, "parsed_complement", True)
    # COORDINATION: a conj verb inherits its (recursively-resolved) head verb's negation (De Morgan; the head
    # coordinator must not be contrastive 'but'). BUT the LEXICON governs first: if the conj HEAD is a
    # COMPLEMENT-TAKING verb (subcategorizes a to-VP), then v is coordinated INSIDE that verb's COMPLEMENT
    # domain (Frazier parallelism at the complement level) -- so v's factuality comes from the matrix's
    # IMPLICATIVE signature ('not hesitate to use or refer' -> refer HAPPENS; 'do not want X to trigger' ->
    # trigger UNKNOWN), NOT from inheriting the matrix clause negation. This is stored verb argument-structure
    # (MacDonald/Trueswell constraint-based parsing) correcting a parse attachment-LEVEL error -- NO training.
    if propagate and lab == "conj" and head and head >= 1:
        but = any(canon(toks[c - 1]) == "but" and labels.get(c) == "cc" for c in children.get(v, []))
        # SHARED-SUBJECT constraint (VP-coordination shares negation ONLY if it shares the subject): a conj verb
        # with its OWN overt subject is a SEPARATE clause / REDUCED RELATIVE ('the things [that] guys TOLD'), not a
        # VP-coordinate -- its factuality is independent, so it does NOT inherit the matrix negation. Frazier
        # categorial parallelism at the VP level; stored structural knowledge, no training.
        own_subject = any(labels.get(c) in ("nsubj", "nsubj:pass", "csubj") for c in children.get(v, []))
        if not but and not own_subject:
            hlem = canon(toks[head - 1])
            if implicative and hlem in IMPLICATIVE:
                m_neg = _directly_negated_parsed(head, toks, heads, labels, children)
                fv = complement_factuality(toks[head - 1], m_neg)
                if fv is not None:
                    return PolarityReadout(fv, "parsed_conj_in_complement:%s%s" % (hlem, "(neg)" if m_neg else ""),
                                           True)
                return PolarityReadout(0, "parsed_conj_attitude:%s" % hlem, True)
            hp = event_polarity_parsed(head, toks, heads, labels, implicative=implicative, propagate=propagate)
            if hp.polarity == -1:
                return PolarityReadout(-1, "parsed_coord", True)
    return PolarityReadout(+1, "parsed_positive", False)


# ==================================================================================================
# QUANTIFIER SCOPE / CARDINALITY (Johnson-Laird tokens over the argument set). Reader-native readout.
# ==================================================================================================
@dataclass
class QuantReadout:
    quant: Optional[str]          # the surface determiner ('all'/'no'/'some'/'every'/...)
    card: Optional[str]           # ALL | SOME | ZERO | MOST | FEW | EXC | None
    exception: Optional[str]      # the excepted individual for 'everyone but X'
    scoped: bool


def read_quantifier(toks: Sequence[str], arg_head_idx: Optional[int] = None,
                    subject_region: Optional[Tuple[int, int]] = None) -> QuantReadout:
    """Read the quantifier heading an argument NP + any 'but/except X' exception.
    Looks in [subject_region) if given, else scans the pre-predicate region for a determiner in QUANT_CARD.
    'everyone but Mary' -> card=ALL, exception='mary' (predicate holds of ALL EXCEPT mary)."""
    n = len(toks)
    lo, hi = (subject_region if subject_region is not None else (0, n))
    lo, hi = max(0, lo), min(n, hi)
    region = [canon(toks[i]) for i in range(lo, hi)]
    # NEGATIVE-EXISTENTIAL idioms take precedence over a bare indefinite ('not a single guard' is ZERO, not
    # 'a' -> SOME; 'not one', 'not any'). A negator immediately before an indefinite -> cardinality 0.
    for k in range(len(region) - 1):
        if (region[k] == "not" or toks[lo + k].lower().endswith("n't")) and \
                region[k + 1] in ("a", "an", "one", "any", "single"):
            return QuantReadout("no", "ZERO", None, True)
    q = None
    q_idx = None
    for i in range(lo, hi):
        c = canon(toks[i])
        if c in QUANT_CARD:
            q, q_idx = c, i
            break
    if q is None:
        return QuantReadout(None, None, None, False)
    card = QUANT_CARD[q]
    exception = None
    # 'everyone/all X but/except Y' -> exception Y
    if q_idx is not None:
        for i in range(q_idx + 1, min(n, hi + 4)):
            if canon(toks[i]) in EXCEPT_MARKERS:
                # exception individual = the next capitalised/content token
                for j in range(i + 1, min(n, i + 4)):
                    cj = toks[j]
                    if canon(cj) and canon(cj) not in ("the", "a", "an", "of"):
                        exception = canon(cj)
                        card = "EXC"
                        break
                break
    return QuantReadout(q, card, exception, True)


def quant_holds_of(card: Optional[str], exception: Optional[str], queried: Optional[str],
                   is_member: bool = True) -> Optional[bool]:
    """Does the predicate hold of the queried individual, given the subject quantifier's cardinality?
    Returns True / False / None (undetermined). 'queried' is the lemma being asked about (for EXC)."""
    if card is None:
        return None
    if card == "ZERO":
        return False                          # holds of nobody
    if card == "ALL":
        return True if is_member else None    # holds of every member
    if card == "SOME":
        return None                           # holds of at-least-one -- says nothing about a SPECIFIC one
    if card == "MOST":
        return None                           # >half -- indeterminate for a specific individual
    if card == "FEW":
        return False if is_member else None   # 'few Xed' -> a given member most-likely did NOT (default)
    if card == "EXC":
        if queried is not None and exception is not None and canon(queried) == canon(exception):
            return False                      # 'everyone but Mary' -> Mary did NOT
        return True if is_member else None    # any other member did
    return None


def quant_existential(card: Optional[str]) -> Optional[bool]:
    """Did the predicate hold of ANYONE (the existential truth of the whole proposition)?
    'no one left' -> False; 'someone/all/everyone left' -> True; 'few' -> True(>0)."""
    if card is None:
        return None
    if card == "ZERO":
        return False
    if card in ("ALL", "SOME", "MOST", "FEW", "EXC"):
        return True
    return None


# ==================================================================================================
# TRUTH-CONDITIONAL READOUT -- the polarity-BLIND floor vs the operator, on one proposition.
# ==================================================================================================
def blind_holds() -> int:
    """The polarity-blind floor: every extracted proposition is stored POSITIVE and SINGULAR -> it HOLDS."""
    return +1


# ==================================================================================================
# UNIFIED TRUTH-CONDITIONAL QUERY (P2) -- route EVENT-proposition polarity through the SAME state_register
# primitive that answers COPULAR-state queries, so copular and event polarity share ONE representation
# (Kaup-Zwaan: comprehension ends on the ACTUAL state, whatever the proposition type). This is the
# consolidation the AUDIT UPDATE calls for: not a second polarity path, the same one extended onto events.
# ==================================================================================================
def proposition_answer(toks: Sequence[str], pred_idx: int, pred_lemma: str, query_lemma: str,
                       pos: Optional[Sequence[str]] = None, verb_lows: Optional[set] = None,
                       semantic: bool = True) -> str:
    """Does the queried predicate hold of the stored event proposition? Returns 'YES' / 'NO' / 'UNKNOWN'.
    Computes the event's truth-polarity with the operator, then answers through hdlab.state_register.state_match
    (MATCH/NO/NONE, with the privative / open-vs-closed-scale / typed-antonymy guards) -- the IDENTICAL primitive
    used for 'is X ill?' copular queries. So 'did she take the key?' (event) and 'is she ill?' (state) run one
    representation; a synonym/entailment query ('did she grab it?' vs stored 'take') resolves via the ATL-hub
    matcher for free. semantic=False = exact-lemma (skip WordNet)."""
    pol = event_polarity(toks, pred_idx, pred_lemma, pos=pos, verb_lows=verb_lows)
    if pol.polarity == 0:
        return "UNKNOWN"
    if not semantic:
        if canon(query_lemma) == canon(pred_lemma):
            return "YES" if pol.polarity == 1 else "NO"
        return "UNKNOWN"
    from hdlab.state_register import state_match
    m = state_match(query_lemma, pred_lemma, pol.polarity)      # REUSE the copular-state matcher verbatim
    return {"MATCH": "YES", "NO": "NO", "NONE": "UNKNOWN"}[m]


def shuffle_token(cue: str, rng) -> str:
    """Info-free twin helper: given a cue token, return a random OTHER cue of the same class (permute the
    negation cues / quantifier determiners across items, keeping the proposition + shapes)."""
    return cue  # replaced by a population-level permutation in the experiments (kept here for provenance)


# ==================================================================================================
def _self_test() -> None:
    ok = 0
    cases = []

    def chk(note, cond):
        cases.append((note, bool(cond)))

    # --- NEGATION: direct clause-local ---
    t = "She did not take the key .".split()
    r = event_polarity(t, 3, "take")      # take @3
    chk("direct: 'did not take' -> -1", r.polarity == -1 and r.scoped)
    t = "She took the key .".split()
    chk("positive: 'took' -> +1", event_polarity(t, 1, "take").polarity == +1)

    # --- NEGATION: negative-existential subject ---
    t = "No one left the room .".split()
    chk("neg-quant subj: 'no one left' -> -1", event_polarity(t, 2, "leave").polarity == -1)
    t = "Nobody agreed .".split()
    chk("neg-quant subj: 'nobody agreed' -> -1", event_polarity(t, 1, "agree").polarity == -1)

    # --- FOCUS guard: 'not only' does NOT negate ---
    t = "She did not only sing but dance .".split()
    chk("focus guard: 'not only' -> not negated", event_polarity(t, 4, "sing").polarity == +1)

    # --- COORDINATION propagation: shared negation across VP-conj ---
    t = "She did not eat or sleep .".split()   # eat@3 sleep@5, coordinator 'or'@4
    chk("coord shared: 'did not eat or sleep' -> sleep -1",
        event_polarity(t, 5, "sleep", verb_lows={"eat", "sleep"}).polarity == -1)

    # --- COMPLEMENT gate: negation does NOT propagate into a complement clause ---
    # 'did not want to leave' -> leave is a non-implicative(attitude) complement -> UNKNOWN, not negated
    t = "She did not want to leave .".split()   # want@3 leave@5
    rr = event_polarity(t, 5, "leave", verb_lows={"want", "leave"})
    chk("complement attitude: 'not want to leave' -> leave UNKNOWN (not -1)", rr.polarity == 0)
    # 'did not manage to escape' -> implicative negated -> escape FALSE
    t = "He did not manage to escape .".split()   # manage@3 escape@5
    chk("implicative(neg): 'not manage to escape' -> escape -1",
        event_polarity(t, 5, "escape", verb_lows={"manage", "escape"}).polarity == -1)
    # 'did not fail to arrive' -> negative-implicative negated -> arrive TRUE
    t = "She did not fail to arrive .".split()   # fail@3 arrive@5
    chk("neg-implicative(neg): 'not fail to arrive' -> arrive +1",
        event_polarity(t, 5, "arrive", verb_lows={"fail", "arrive"}).polarity == +1)
    # factive survives negation: 'did not remember that he left' -> left TRUE (presupposition)
    t = "She did not know that he left .".split()   # know@3 left@6, factive
    chk("factive: 'not know that he left' -> left +1 (presupposition survives)",
        event_polarity(t, 6, "leave", verb_lows={"know", "left", "leave"}).polarity == +1)

    # --- NEGATION: interrogative subject-aux inversion ---
    t = "why can't you see this ?".split()      # why@0 can't@1 you@2 see@3
    chk("inversion: 'can't you see' -> see -1", event_polarity(t, 3, "see").polarity == -1)

    # --- NEGATION: multi-way comma+and coordination chain ---
    t = "He did not invade Kuwait , endanger Arabia and butcher people .".split()
    vl = {"invade", "endanger", "butcher"}       # endanger@6 butcher@9
    chk("coord chain (comma): 'not invade, endanger and butcher' -> endanger -1",
        event_polarity(t, 6, "endanger", verb_lows=vl).polarity == -1)
    chk("coord chain (and): butcher -1", event_polarity(t, 9, "butcher", verb_lows=vl).polarity == -1)

    # --- NEGATION: post-verbal negative-quantifier object (neg-incorporation) ---
    t = "She has no money .".split()             # has@1 no@2
    chk("neg-quant object: 'has no money' -> has -1", event_polarity(t, 1, "have").polarity == -1)

    # --- NEGATION: 'but' does NOT share (contrastive 2nd clause is affirmative) ---
    t = "I have not done a test but have done a panel .".split()   # done@3 done@8
    chk("but-contrast: 'not done a test but have done a panel' -> 2nd done +1",
        event_polarity(t, 8, "do", verb_lows={"do", "done"}).polarity == +1)

    # --- NEGATION: factive gerund survives negation ---
    t = "She did not remember him leaving .".split()   # remember@3 leaving@5
    chk("factive gerund: 'not remember him leaving' -> leaving +1",
        event_polarity(t, 5, "leaving", verb_lows={"remember", "leaving"}).polarity == +1)

    # --- QUANTIFIER cardinality ---
    t = "Everyone but Mary agreed .".split()
    q = read_quantifier(t, subject_region=(0, 3))
    chk("quant: 'everyone but Mary' -> EXC exception=mary", q.card == "EXC" and q.exception == "mary")
    chk("quant: Mary did NOT agree", quant_holds_of(q.card, q.exception, "mary") is False)
    chk("quant: John DID agree", quant_holds_of(q.card, q.exception, "john") is True)
    t = "None of the guards moved .".split()
    q = read_quantifier(t, subject_region=(0, 4))
    chk("quant: 'none of the guards' -> ZERO", q.card == "ZERO")
    chk("quant: existential(none moved) -> False", quant_existential(q.card) is False)
    t = "All the guards moved .".split()
    q = read_quantifier(t, subject_region=(0, 3))
    chk("quant: 'all the guards' -> ALL, a guard moved -> True",
        q.card == "ALL" and quant_holds_of(q.card, None, "guard") is True)
    t = "Some guards moved .".split()
    q = read_quantifier(t, subject_region=(0, 2))
    chk("quant: 'some guards' -> SOME, existential True, specific None",
        q.card == "SOME" and quant_existential(q.card) is True
        and quant_holds_of(q.card, None, "guard") is None)

    # --- P2 UNIFIED query through state_register.state_match (event + copular share one representation) ---
    t = "She did not take the key .".split()
    chk("unified: 'did she take the key?' over 'did not take' -> NO",
        proposition_answer(t, 3, "take", "take") == "NO")
    t = "She took the key .".split()
    chk("unified: 'did she take the key?' over 'took' -> YES",
        proposition_answer(t, 1, "take", "take") == "YES")
    t = "He did not manage to escape .".split()
    chk("unified: implicative 'did he escape?' over 'not manage to escape' -> NO",
        proposition_answer(t, 5, "escape", "escape", verb_lows={"manage", "escape"}) == "NO")

    for note, good in cases:
        ok += int(good)
        print("  [%s] %s" % ("PASS" if good else "FAIL", note))
    print("SELF-TEST %d/%d cases" % (ok, len(cases)))
    assert ok == len(cases), "polarity_operator self-test failed (%d/%d)" % (ok, len(cases))


if __name__ == "__main__":
    _self_test()
