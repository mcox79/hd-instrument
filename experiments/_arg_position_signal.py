"""_arg_position_signal -- glass-box STRUCTURAL argument-position / dative-frame signal for the
trustworthy abstain gate. It DETECTS role-misassignment uncertainty; it does NOT solve role assignment.

MOTIVATION (the 29469 dialogue failure the coref-margin + conflict + NP-head signals cannot see):
    "Is this the promise that you made your mother?"  q="what did you make?" (theme)  gold "promise"
    the reader answers "mother" -- a valid HEAD noun (NP-head OK), high coref confidence, no match
    conflict -- so every existing gate signal KEEPS it. But "mother" is the RECIPIENT argument, not the
    THEME. This is a role (theta-role) misassignment invisible to the surface/lexical signals.

BRAIN GROUND (dative alternation; Levin dative-verb class): for a ditransitive/dative verb the surface
FRAME fixes which noun is recipient vs theme --
    double-object   "V NP1 NP2"        -> NP1 = recipient, NP2 = theme    ("gave your mother a gift")
    prepositional   "V NP2 to/for NP1" -> NP2 = theme,     NP1 = recipient ("gave a gift to your mother")
    extracted theme "the NP2 that SUBJ V NP1" -> NP1 (postverbal) = recipient, NP2 (relative head) = theme
                                                ("the promise that you made your mother")
The frame is a STRUCTURAL (POS + word-order + closed-class) fact, so the signal is DESIGNED TO TRANSFER
corpus-to-corpus exactly as the NP-head signal did.

THE SIGNAL (pure abstain FLAG; alters no answer; reads NO gold):
    for a THEME query (relation svo_patient) whose verb is a DATIVE verb, classify the answer noun's
    argument SLOT from the surface frame. If the answer sits in the RECIPIENT slot (and NOT in the theme
    slot), the role assignment is structurally INCONSISTENT with a theme query -> flag (abstain).

CONSERVATIVE BIAS (avoids false-abstain, the narrative-breaking danger): the signal has an opinion ONLY on
a POSITIVE recipient-slot detection for a dative verb + theme query. Non-dative verb, non-theme relation,
answer in the theme slot, simple transitive (single bare object), or an unparseable frame -> NO opinion
(consistent). It never fires on a theme-slot answer.

GENUINE CAN-FAIL (load-bearing): the signal is a DETECTOR, not a solver. If a role-misassignment occurs in
a frame the structural parse cannot resolve (e.g. no relativizer, single postverbal noun that is actually
the recipient with the theme absent, or a construction the POS frame mislabels), the signal does not fire
and the confabulation survives -> that residual is the MAPPED-ROLES ceiling (needs semantic role solving,
not structural detection). If the signal over-fires it false-abstains a correct theme answer -> breaks
coverage. Both are real failure outcomes measured against the gold, not assumed.

ASCII-only. Pure functions; POS pipeline (pos_tag_sentence / split_sentences) passed in; no torch/HD.
"""
from __future__ import annotations

NOUN_POS = ("NN", "NNS", "NNP", "NNPS")
_ADJ_POS = ("JJ", "JJR", "JJS")
_DET_POS = ("DT", "PRP$", "CD")
_PREP_POS = ("IN", "TO")

# closed dative / ditransitive verb class (Levin dative + benefactive). SURFACE forms (base + inflections)
# because the shared POS pipeline lowercases rather than lemmatizes ("made" stays "made"). Only these verbs
# license a recipient argument, so the signal is inert on every other verb (narrative safety).
_DATIVE_LEMMA_FORMS = {
    "give": ("give", "gives", "gave", "given", "giving"),
    "tell": ("tell", "tells", "told", "telling"),
    "show": ("show", "shows", "showed", "shown", "showing"),
    "offer": ("offer", "offers", "offered", "offering"),
    "promise": ("promise", "promises", "promised", "promising"),
    "send": ("send", "sends", "sent", "sending"),
    "bring": ("bring", "brings", "brought", "bringing"),
    "hand": ("hand", "hands", "handed", "handing"),
    "pay": ("pay", "pays", "paid", "paying"),
    "lend": ("lend", "lends", "lent", "lending"),
    "teach": ("teach", "teaches", "taught", "teaching"),
    "read": ("read", "reads", "reading"),
    "write": ("write", "writes", "wrote", "written", "writing"),
    "sell": ("sell", "sells", "sold", "selling"),
    "throw": ("throw", "throws", "threw", "thrown", "throwing"),
    "pass": ("pass", "passes", "passed", "passing"),
    "feed": ("feed", "feeds", "fed", "feeding"),
    "grant": ("grant", "grants", "granted", "granting"),
    "award": ("award", "awards", "awarded", "awarding"),
    "serve": ("serve", "serves", "served", "serving"),
    "owe": ("owe", "owes", "owed", "owing"),
    "make": ("make", "makes", "made", "making"),      # dative in "make someone a promise"
    "leave": ("leave", "leaves", "left", "leaving"),
    "wish": ("wish", "wishes", "wished", "wishing"),
    "deny": ("deny", "denies", "denied", "denying"),
    "hand_over": (),  # placeholder; not used
}
DATIVE_VERBS = frozenset(f for forms in _DATIVE_LEMMA_FORMS.values() for f in forms)

# recipient-introducing prepositions in the prepositional dative frame.
_RECIP_PREPS = frozenset({"to", "for"})
# object-relative markers (extracted-theme frame): "the NOUN that/which/whom SUBJ V ...".
RELATIVIZERS = frozenset({"that", "which", "whom", "who"})
# theme-query relation(s): the signal only engages for a theme / direct-object question.
THEME_RELATIONS = frozenset({"svo_patient"})


def is_dative_verb(verb):
    return str(verb).lower() in DATIVE_VERBS


def _is_noun(pos):
    return pos in NOUN_POS


def _run_heads(tagged, lo, hi):
    """Noun-run HEADS (idx, low) within tagged[lo:hi): a noun whose next in-range token is not a noun."""
    heads = []
    for i in range(lo, min(hi, len(tagged))):
        if _is_noun(tagged[i][2]):
            nxt_is_noun = (i + 1 < min(hi, len(tagged))) and _is_noun(tagged[i + 1][2])
            if not nxt_is_noun:
                heads.append((i, tagged[i][1]))
    return heads


def _find_verb_idx(tagged, verb):
    """Index of the query verb as a VERB token (low == verb, POS starts VB). Last match wins (main clause
    of an object-relative sits after the antecedent)."""
    v = str(verb).lower()
    found = -1
    for i, (_surf, low, pos) in enumerate(tagged):
        if low == v and pos.startswith("VB"):
            found = i
    if found == -1:  # fallback: surface match even if POS mis-tagged the verb
        for i, (_surf, low, _pos) in enumerate(tagged):
            if low == v:
                found = i
    return found


def _extracted_theme(tagged, v):
    """True if an OBJECT-RELATIVE extracts the theme before the verb: pattern 'NOUN <relativizer> ... V',
    i.e. a relativizer at r<v immediately preceded by a NOUN antecedent (tight, so a complementizer
    'V that SUBJ V' where a VERB precedes 'that' is NOT read as extraction). Returns the antecedent low."""
    for r in range(1, v):
        if tagged[r][1] in RELATIVIZERS and _is_noun(tagged[r - 1][2]):
            return tagged[r - 1][1]
    return None


def _frame(tagged, v):
    """Classify the dative frame at verb index v within one tagged sentence. Returns
    (frame, recipient_lows, theme_lows). The DIRECT object region is the contiguous postverbal NP run up to
    the first preposition / verb / comma (so 'makes observations on ...' stops at 'on' = single object)."""
    n = len(tagged)
    # direct-object region: v+1 .. first boundary (preposition, verb, comma, relativizer, or end).
    j = v + 1
    while j < n:
        pos = tagged[j][2]
        low = tagged[j][1]
        if pos in _PREP_POS or pos.startswith("VB") or low == "," or low in RELATIVIZERS:
            break
        j += 1
    direct_end = j
    direct_heads = _run_heads(tagged, v + 1, direct_end)

    # prepositional dative: first to/for preposition after the direct region introduces the recipient.
    prep_idx = -1
    for k in range(v + 1, n):
        if tagged[k][2] in _PREP_POS and tagged[k][1] in _RECIP_PREPS:
            prep_idx = k
            break
    if prep_idx != -1:
        # recipient region = contiguous NP after the preposition up to next boundary.
        m = prep_idx + 1
        while m < n:
            pos = tagged[m][2]
            low = tagged[m][1]
            if pos.startswith("VB") or low == "," or low in RELATIVIZERS or (pos in _PREP_POS and low in _RECIP_PREPS):
                break
            m += 1
        recip_heads = _run_heads(tagged, prep_idx + 1, m)
        theme_heads = direct_heads
        if recip_heads and theme_heads:
            return ("prepositional", [h[1] for h in recip_heads], [h[1] for h in theme_heads])

    # double-object: two bare NPs directly after the verb -> NP1 recipient, NP2 theme.
    if len(direct_heads) >= 2:
        return ("double_object", [direct_heads[0][1]], [h[1] for h in direct_heads[1:]])

    # extracted theme: exactly one postverbal NP + an object-relative antecedent before the verb.
    if len(direct_heads) == 1 and _extracted_theme(tagged, v) is not None:
        return ("extracted_theme", [direct_heads[0][1]], [])

    # simple transitive (single bare object, no extraction) -> that object IS the theme; no recipient.
    if len(direct_heads) == 1:
        return ("simple_transitive", [], [direct_heads[0][1]])

    return ("none", [], [])


def arg_role_status(ans, verb, passage_text, pos_tag_sentence, split_sentences):
    """Return one of {"recipient", "theme", "none"} for answer `ans` under the dative frame of `verb` in
    `passage_text`. Non-dative verb or unparseable frame -> "none". Reads NO gold. Pure fn of (ans, verb,
    passage). If the answer appears in a theme slot anywhere, "theme" WINS over "recipient" (conservative)."""
    if ans is None or not is_dative_verb(verb):
        return "none"
    a = str(ans).lower()
    saw_recipient = False
    saw_theme = False
    for sent in split_sentences(passage_text):
        tagged = pos_tag_sentence(sent)
        v = _find_verb_idx(tagged, verb)
        if v == -1:
            continue
        _frame_name, recip, theme = _frame(tagged, v)
        if a in [t.lower() for t in theme]:
            saw_theme = True
        if a in [t.lower() for t in recip]:
            saw_recipient = True
    if saw_theme:
        return "theme"
    if saw_recipient:
        return "recipient"
    return "none"


def arg_position_misassigned(ans, relation, verb, passage_text, pos_tag_sentence, split_sentences):
    """The abstain FLAG: True iff (theme query) AND (dative verb) AND (answer sits in the RECIPIENT slot
    and NOT the theme slot). POSITIVE detection only -> conservative; never fires on a theme-slot answer."""
    if relation not in THEME_RELATIONS or not is_dative_verb(verb):
        return False
    return arg_role_status(ans, verb, passage_text, pos_tag_sentence, split_sentences) == "recipient"


def arg_frame_debug(ans, verb, passage_text, pos_tag_sentence, split_sentences):
    """Diagnostic: (frame_name, recipient_lows, theme_lows) for the sentence carrying the verb."""
    if not is_dative_verb(verb):
        return ("non_dative", [], [])
    for sent in split_sentences(passage_text):
        tagged = pos_tag_sentence(sent)
        v = _find_verb_idx(tagged, verb)
        if v == -1:
            continue
        return _frame(tagged, v)
    return ("verb_not_found", [], [])
