"""affected_entity_resolver -- the LIKELIHOOD half of pronoun-undergoer resolution (mathematically BF).

Promoted verbatim from the owner-DONE solution
`who_was_affected_needs_the_forward_salience_prior_join_undergoer_to_discourse_entity`
(BUILD 4, the corrected lever). Resolves an AMBIGUOUS undergoer PRONOUN ("...frightened HIM") to the
right DISCOURSE ENTITY (the affected CHARACTER), not merely a token. The three prior semantic cues
(type-coherence, implicit causality) were located negatives; the discriminating action for an
ARGUMENT pronoun is the grammatical LIKELIHOOD P(pronoun|referent), on top of the ACT-R salience PRIOR:

  - PRINCIPLE B  [PINNED universal; Chomsky 1981, Reinhart 1983] -- a HARD ZERO. A plain (non-reflexive)
    pronoun cannot corefer with its clause-mate co-argument ("John hit HIM" => him != John). We EXCLUDE
    the co-argument entity: for an OBJ pronoun, the clause-mate SUBJECT of its verb; for nsubj:pass, the
    by-agent. Implemented FRESH from the parse (NOT the BF-unregistered gold-mention organ).
  - ROLE PARALLELISM  [PINNED; Smyth 1994, Stevenson 1995] -- a SOFT bias. OBJECT pronouns take OBJECT
    antecedents; undergoer=PATIENT -> prior PATIENTs. The Bayesian LIKELIHOOD form exp(gamma*1[role-match])
    (gamma SWEPT, not adopted) -- NOT the BF_SPIRIT invented-arithmetic fixed bonus.
  - SALIENCE PRIOR  [BF; hdlab.salience_binder.actr_activation] -- ACT-R base-level activation over the
    online, head-individuated discourse referents (Anderson; Lewis & Vasishth).

  score(c | anaphor a) = ln p_sal(c)  +  gamma_g * 1[gram-role(c) = gram-role(a)]  +  gamma_t * 1[c is PATIENT]
  argmax over candidates c NOT excluded by Principle B. Bayesian:
  P(c|a) proportional to  1[c not co-arg] * exp(parallelism) * softmax(ACT-R).

WHY THE LEVER: the current subject-biased salience picks the ILLEGAL clause-mate co-argument ~19% of the
time (221/1142 GUM undergoers) -- that single number mechanistically explains the ~0.45 salience wall.
Principle B + parallelism ~doubles the lift over salience-alone: +0.093 CI-sep on gold roles, and it
SURVIVES the real supervised parse (+0.049 Principle-B robust to +0.060 full, CI-sep, n=952). The
parallelism term degrades ~1/3 under noisy predicted role labels; Principle B is unchanged (robust to
parser error, being a categorical co-argument universal).

MATHEMATICALLY BF (owner-verified): Principle B = PINNED categorical universal from the parse;
parallelism = PINNED Bayesian likelihood exp(gamma*.) with gamma swept; salience = BF ACT-R. The only
un-upgraded dependency is the supervised parse spine (a declared NOT_BF offline scaffold) -- which is
exactly why the win was measured on gold roles AND re-measured on the predicted parse (it survives).

FORWARD HALF (strategy 2026-09-12, pri-1 `generative_entity_state_reranks_which_entity_is_the_affected_undergoer`,
research note notes/RESEARCH_generative_entity_state_pri1_2026-09-12.md): the resolver is now also an INCREMENTAL
entity-TOKEN machine (`EntityTokens`): every reference -- including every RESOLVED PRONOUN -- is written to its
token's history (Kahneman-Treisman-Gibbs 1992 object-file reviewing+impletion; ACT-R: every retrieval is a
presentation), so later activations see the FULL reference history; candidates referenced within the last
FOREGROUND_WINDOW sentences are tried first (Glenberg-Meyer-Lindem 1987 availability; Zwaan-Radvansky event-model
foreground), falling back to all; and REFLEXIVES obey Principle A (must corefer with the clause-mate co-argument --
the mirror of Principle B). Measured on THIRD-person GUM undergoers (n=596 gold / 593 predicted parse): +0.0436
CI[+0.017,+0.071] gold, +0.0371 CI[+0.012,+0.062] predicted, over the landed resolver; accrual-scramble and
window-scramble twins collapse (0.445 / 0.216). Operating point swept (W 1/2/3/5 flat; decay and clock = the
organ's own), never fitted.

Glass-box, pure, no external LLM, ASCII. This organ is the load-bearing resolver; the experiment cell
`experiments/exp_affected_entity_binding_parallelism_gum_v1.py` imports it (so its 4/4 witness IS this
organ), and the live reader binds `sm.who_was_affected` over it.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY

__bf_status__ = "BF_SPIRIT"
# BF: the composition is a PINNED cascade (Kehler-Rohde Bayesian pronoun resolution -- salience PRIOR x
# grammatical LIKELIHOOD). Principle B = PINNED universal (categorical); parallelism = PINNED Bayesian
# likelihood exp(gamma*1[match]) with gamma SWEPT not adopted; salience = the BF ACT-R organ. The
# gamma weights are OUR-INVENTION-free swept parameters (a constraint we do not share), not fitted
# arithmetic. The upstream parse spine is the declared NOT_BF offline scaffold (the win survives it).
__bf_verified__ = (
    "2026-09-11 owner-DONE who_was_affected...forward_salience_prior integration: promoted the BUILD-4 "
    "corrected lever into a self-contained organ; the experiment cell imports it so its 4/4 witness IS "
    "the organ (A1 0.3704 -> A2 Principle-B 0.4186 +0.048 -> A5 full 0.4632 +0.093 CI-sep; survives the "
    "predicted parse +0.049/+0.060 n=952); organ self-test PASS; strategy first-hand"
)
__bf_note__ = (
    "Kehler-Rohde Bayesian pronoun resolution: ACT-R salience PRIOR (BF salience_binder) x grammatical "
    "LIKELIHOOD = Principle B [PINNED categorical universal, co-argument exclusion fresh from the parse] "
    "+ role/thematic parallelism [PINNED exp(gamma*1[role-match]), gamma SWEPT]. Retires the subject-"
    "biased coref.CENTER_PARALLEL_BONUS + the BF-unregistered gold-mention _principle_b_filter. Upstream "
    "parse spine = declared NOT_BF offline scaffold. LATENT until the reader binds sm.who_was_affected."
)
__bf_corrections__ = (
    "Replaces the BF_SPIRIT subject-biased coref.CENTER_PARALLEL_BONUS (flagged right-op-wrong-metric) "
    "and the BF-unregistered gold-mention coreference_resolver._principle_b_filter with the PINNED "
    "categorical Principle B built fresh from the parse + the PINNED exp(gamma*1[role-match]) likelihood."
)

# --- role / dependency-label vocabulary (UD; matches the proven experiment) ---------------------------
SUBJ_DEPS = {"nsubj", "nsubj:pass", "nsubjpass", "csubj"}
OBJ_DEPS = {"obj", "dobj", "iobj", "obl", "obl:arg", "obl:agent", "nmod"}
PATIENT_DEPS = {"obj", "dobj", "nsubj:pass", "nsubjpass"}
UND_DEPRELS = {"obj", "dobj", "nsubj:pass", "nsubjpass"}   # an undergoer is an OBJ or a passive subject
GAMMA_G = 1.0   # grammatical-role parallelism weight (swept 0.5/1.0/2.0 -> all CI-sep; 1.0 the reported)
GAMMA_T = 1.0   # thematic (PATIENT) parallelism weight
FOREGROUND_WINDOW = 2          # sentences; the event-model foreground (swept 1/2/3/5: flat; 2 reported)
REFLEXIVES = frozenset({"himself", "herself", "itself", "themselves", "oneself"})
REFLEXIVE_GN = {"himself": ("masc", "singular"), "herself": ("fem", "singular"), "itself": ("neuter", "singular"),
                "themselves": (None, "plural"), "oneself": (None, "singular")}
ROLE_OF_RANK = {0: "SUBJECT", 1: "OBJECT"}   # sent_role_rank -> ACT-R role-prominence class


def role_class(dep: Optional[str]) -> str:
    """Coarse grammatical-role class of a UD deprel: SUBJ / OBJ / OTHER (the parallelism-match key)."""
    if dep in SUBJ_DEPS:
        return "SUBJ"
    if dep in OBJ_DEPS:
        return "OBJ"
    return "OTHER"


def coarg_head_gidx(toks: Sequence, t) -> Optional[int]:
    """Principle B/C co-argument to EXCLUDE for an undergoer token `t` (an obj / passive-subject pronoun):
    for an OBJ pronoun, the clause-mate SUBJECT of t's verb; for an nsubj:pass, the by-AGENT (obl:agent).
    Returns the excluded token's `gidx`, or None. `toks` is the document token stream; each token has
    `.sent .head .deprel .gidx .idx .lemma` (the experiment's Tok shape). Parse-fresh (no gold mention)."""
    V = t.head
    sent = t.sent
    want = OBJ_DEPS if t.deprel in ("nsubj:pass", "nsubjpass") else SUBJ_DEPS
    for s in toks:
        if s.sent == sent and s.head == V and s.deprel in want and s.gidx != t.gidx:
            if t.deprel in ("nsubj:pass", "nsubjpass") and s.deprel not in ("obl:agent",):
                # Principle C for passive: exclude the by-agent specifically
                if not (s.deprel.startswith("obl") and any(
                        c.head == s.idx and c.sent == sent and c.lemma == "by" for c in toks)):
                    continue
            return s.gidx
    return None


def salience_prior(ent_hist: Dict[object, list], now: float,
                   decay: float = DEFAULT_DECAY) -> Dict[object, float]:
    """The forward salience PRIOR: per-entity ACT-R base-level activation over its mention history
    [(order, role_class), ...] at story-time `now`. Reuses the BF salience_binder organ verbatim."""
    return {h: actr_activation(hist, float(now), decay=decay, role_prominence=ROLE_PROMINENCE)
            for h, hist in ent_hist.items()}


def score_and_pick(cand_set: Sequence, sal: Dict[object, float], role_of: Dict[object, str],
                   patient_of: Dict[object, bool], a_role: str,
                   use_par_g: bool = True, use_par_t: bool = True,
                   gamma_g: float = GAMMA_G, gamma_t: float = GAMMA_T):
    """The deterministic resolver argmax: over `cand_set` (the Principle-B-legal candidates), pick the
    entity maximizing ln-salience + gamma_g*1[gram-role match] + gamma_t*1[candidate is PATIENT]. This is
    THE win's core (A5 = both bonuses; A1 salience-alone = both False). Returns the picked entity key."""
    best, bs = None, -1e18
    for h in cand_set:
        s = sal[h]
        if use_par_g and role_of[h] == a_role:
            s += gamma_g
        if use_par_t and patient_of.get(h):
            s += gamma_t
        if s > bs:
            bs, best = s, h
    return best


def legal_candidates(entities: Sequence, coarg_key) -> List:
    """The Principle-B-filtered candidate set: `entities` minus the co-argument entity. Degrades to the
    full set when the filter would empty the pool (never abstain to nothing)."""
    legal = [h for h in entities if h != coarg_key]
    return legal if legal else list(entities)


def is_reflexive(form: Optional[str]) -> bool:
    return bool(form) and form.lower() in REFLEXIVES


def foreground(cands: Sequence, last_ref_sent: Dict[object, float], now_sent: Optional[float],
               window: Optional[int] = FOREGROUND_WINDOW) -> List:
    """The event-model FOREGROUND: candidates whose last reference lies within `window` sentences of the pronoun's
    sentence; falls back to all candidates when none is in focus (never abstains to nothing)."""
    if window is None or now_sent is None or len(cands) < 2:
        return list(cands)
    inwin = [h for h in cands if now_sent - last_ref_sent.get(h, float("-inf")) <= window]
    return inwin if inwin else list(cands)


def resolve(entities: Sequence, sal: Dict[object, float], role_of: Dict[object, str],
            patient_of: Dict[object, bool], a_role: str, coarg_key=None,
            gamma_g: float = GAMMA_G, gamma_t: float = GAMMA_T, reflexive: bool = False):
    """High-level convenience: Principle-B filter (exclude `coarg_key`) then salience x parallelism pick.
    `reflexive=True` applies PRINCIPLE A instead [PINNED]: a reflexive must corefer with its clause-mate co-argument,
    so the co-argument IS the answer when it is a known entity. Returns the resolved discourse-entity key (the
    affected CHARACTER), or None if `entities` is empty."""
    if not entities:
        return None
    if reflexive and coarg_key is not None and coarg_key in entities:
        return coarg_key
    cand = legal_candidates(entities, coarg_key)
    return score_and_pick(cand, sal, role_of, patient_of, a_role,
                          use_par_g=True, use_par_t=True, gamma_g=gamma_g, gamma_t=gamma_t)


class EntityTokens:
    """INCREMENTAL entity tokens (object files) for the forward half. Feed mentions in document order:
    `observe(head, order, role, sent, gender, number, dep)` for a NON-pronoun mention (the token is keyed by the
    head-individuated entity, as the landed resolver), `resolve_pronoun(...)` for a pronoun mention -- it returns the
    picked token key AND writes the pronoun's (order, role) to that token's history (impletion), so every later
    activation sees the full reference history. Gender/number compatibility is checked per mention (unknown =
    wildcard); the role/patient cue is the token's last COMPATIBLE non-pronoun mention. No gold anywhere."""

    def __init__(self, window: Optional[int] = FOREGROUND_WINDOW, decay: float = DEFAULT_DECAY,
                 gamma_g: float = GAMMA_G, gamma_t: float = GAMMA_T, accrue: bool = True):
        self.window, self.decay, self.gamma_g, self.gamma_t, self.accrue = window, decay, gamma_g, gamma_t, accrue
        self.mentions: Dict[object, list] = {}      # key -> [(order, role, gender, number, dep, sent, payload)]
        self.pron_hist: Dict[object, list] = {}     # key -> [(order, role)] accrued pronoun references
        self.last_ref_sent: Dict[object, float] = {}

    def observe(self, key, order: float, role: str, sent: float, gender=None, number=None, dep: str = "",
                payload=None) -> None:
        """`payload` is opaque to the organ (a caller handle, e.g. the mention record); never read in a decision."""
        self.mentions.setdefault(key, []).append((float(order), role, gender or None, number or None, dep or "", float(sent), payload))
        self.last_ref_sent[key] = float(sent)

    @staticmethod
    def _gn_ok(ug, un, g, n) -> bool:
        if ug and g and ug != g:
            return False
        if un and n and un != n:
            return False
        return True

    def candidates(self, gender=None, number=None) -> Dict[object, list]:
        """key -> its gender/number-compatible non-pronoun mentions (only keys with at least one)."""
        out = {}
        for k, ms in self.mentions.items():
            c = [m for m in ms if self._gn_ok(gender, number, m[2], m[3])]
            if c:
                out[k] = c
        return out

    def resolve_pronoun(self, order: float, sent: float, *, gender=None, number=None, a_role: str = "OBJ",
                        role: str = "OTHER", coarg_key=None, reflexive: bool = False, accrue: Optional[bool] = None):
        """Resolve one pronoun reference over the current tokens and ACCRUE it. Returns (key or None, n_candidates)."""
        compat = self.candidates(gender, number)
        ents = list(compat)
        if not ents:
            return None, 0
        if reflexive and coarg_key is not None and coarg_key in ents:
            pick = coarg_key
        else:
            legal = legal_candidates(ents, coarg_key)
            legal = foreground(legal, self.last_ref_sent, float(sent), self.window)
            sal, role_of, patient_of = {}, {}, {}
            for k in legal:
                hist = [(m[0], m[1]) for m in compat[k]]
                if self.accrue if accrue is None else accrue:
                    hist = hist + list(self.pron_hist.get(k, ()))
                a = actr_activation(hist, float(order), decay=self.decay, role_prominence=ROLE_PROMINENCE)
                sal[k] = a if a != float("-inf") else -1e9
                last = max(compat[k], key=lambda m: m[0])
                role_of[k] = role_class(last[4]); patient_of[k] = last[4] in PATIENT_DEPS
            pick = score_and_pick(legal, sal, role_of, patient_of, a_role, gamma_g=self.gamma_g, gamma_t=self.gamma_t)
        if pick is not None:
            self.pron_hist.setdefault(pick, []).append((float(order), role))
            self.last_ref_sent[pick] = float(sent)
        return pick, len(ents)

    def last_mention(self, key, gender=None, number=None):
        c = self.candidates(gender, number).get(key) or self.mentions.get(key) or []
        return max(c, key=lambda m: m[0]) if c else None


def self_test() -> None:
    """Minimal glass-box self-test of the mechanism (not the corpus win -- that is the experiment's 4/4
    witness). (a) Principle B excludes the co-argument; (b) parallelism breaks a salience tie toward the
    role-matched / PATIENT candidate; (c) salience alone otherwise wins."""
    # three entities a,b,c with equal salience; anaphor is an OBJECT undergoer (a_role='OBJ').
    sal = {"a": 1.0, "b": 1.0, "c": 1.0}
    role_of = {"a": "SUBJ", "b": "OBJ", "c": "OTHER"}
    patient_of = {"a": False, "b": True, "c": False}
    # (a) Principle B: exclude 'b' as the co-argument -> 'b' cannot be picked even though it is role/patient matched.
    got = resolve(["a", "b", "c"], sal, role_of, patient_of, a_role="OBJ", coarg_key="b")
    assert got != "b", f"Principle B failed to exclude the co-argument: got {got}"
    # (b) parallelism: no co-arg filter -> 'b' (OBJ + PATIENT) beats the equal-salience 'a'/'c'.
    got = resolve(["a", "b", "c"], sal, role_of, patient_of, a_role="OBJ", coarg_key=None)
    assert got == "b", f"parallelism failed to prefer the role/patient-matched candidate: got {got}"
    # (c) salience prior: raise 'a' -> it wins despite no parallelism match.
    sal2 = {"a": 5.0, "b": 1.0, "c": 1.0}
    got = score_and_pick(["a", "c"], sal2, role_of, patient_of, a_role="OBJ",
                         use_par_g=False, use_par_t=False)
    assert got == "a", f"salience prior did not win when parallelism is off: got {got}"
    # (d) legal_candidates degrades gracefully when the filter would empty the pool.
    assert legal_candidates(["a"], "a") == ["a"], "legal_candidates must not empty the pool"
    # (e) Principle A: a reflexive resolves TO the co-argument.
    assert resolve(["a", "b"], sal, role_of, patient_of, a_role="OBJ", coarg_key="a", reflexive=True) == "a"
    # (f) forward half: accrued pronoun references raise the token; the foreground window prefers in-focus tokens.
    T = EntityTokens(window=2)
    T.observe("x", 0, "SUBJECT", 0, "masc", "singular", "nsubj"); T.observe("y", 1, "OBJECT", 0, "masc", "singular", "obj")
    T.observe("z", 2, "SUBJECT", 5, "masc", "singular", "nsubj")
    k, n = T.resolve_pronoun(3, 5, gender="masc", number="singular", a_role="OBJ", role="OBJECT")
    assert k == "z" and n == 3, (k, n)                 # only z is in the 2-sentence foreground
    T2 = EntityTokens(window=None)
    T2.observe("x", 0, "OBJECT", 0, "masc", "singular", "obj"); T2.observe("y", 1, "OBJECT", 0, "masc", "singular", "obj")
    for o in (2, 3, 4):
        T2.pron_hist.setdefault("x", []).append((float(o), "OBJECT"))   # x was referenced three times by pronouns
    k2, _ = T2.resolve_pronoun(5, 1, gender="masc", number="singular", a_role="OBJ")
    assert k2 == "x", k2                               # accrual makes x the more active token
    assert T2.pron_hist["x"][-1][0] == 5.0            # and the new reference was written to it
    print("[SELFTEST PASS] affected_entity_resolver: Principle-B exclusion + role/thematic parallelism + "
          "ACT-R salience prior compose as the mathematically-BF undergoer-pronoun resolver.")


if __name__ == "__main__":
    self_test()
