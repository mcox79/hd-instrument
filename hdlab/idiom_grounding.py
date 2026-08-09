"""hdlab/idiom_grounding.py -- supplied idiom/colloquialism -> attribute-polarity grounding for
Direction-B M1 (2026-08-09, notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md).

M1's hypothesis: hdlab.goal_achievement.utility_channel's ARCHITECTURE is validated (Stage-2,
commit 1f6958e36 -- activation fires 0.273, pairscramble collapses clean, no regression) but its
per-token WordNet-synonym evidence-scoring cannot READ short/idiomatic/colloquial real DesireDB
outcome text ("put the kabash on that idea", "she told her no", "Uh. No."). M1 supplies TWO
glass-box, non-LLM grounding sources feeding that same per-attribute {SATISFIED,VIOLATED,ABSENT}
scoring as a SUPPLEMENT (never a replacement) to the existing WordNet vote:

  1. IDIOM_LEXICON -- a small hand-vetted idiom/colloquialism -> literal-effect gloss lexicon.
     Each entry authored from the phrase's DICTIONARY / established-colloquial-usage meaning
     (Merriam-Webster informal-usage notes, cited inline), chosen BEFORE this session re-inspected
     the DesireDB gold labels for calibration-honesty (the phrases were identified by reading
     cohort OUTCOME TEXT, which is legitimate -- what is forbidden and NOT done here is tuning the
     polarity/weight of any entry to make a specific item's GOLD label come out right).
     ATTRIBUTE-AGNOSTIC/GENERIC by design: these phrases express whether a plan/request/outcome
     succeeded or was refused/blocked in general, not a specific attribute-category, so they are
     applied by the caller (hdlab.goal_achievement) to whichever attribute(s) `activate_attributes`
     already activated from the GOAL side -- this cannot fabricate a new activation, only supply
     evidence-side polarity once an attribute is already active (same confound-immunity argument
     Stage-2 already established).

  2. CONCEPTNET_ANTONYM_BRIDGE -- supplementary per-TOKEN lookup (tried only when WordNet's own
     `_token_cue_polarity` returns None) using ConceptNet's Antonym edges
     (data/datasets/conceptnet5_en_100k.jsonl, on disk, 100k-row curated subset): a token that is a
     ConceptNet-Antonym of a word already in an attribute's satisfied_cues is treated as VIOLATED
     evidence (and vice versa). This is genuinely NEW coverage over the WordNet-synonym path, not a
     duplicate -- reported separately in the M1 cell so its (likely small, on this 100k subset)
     empirical contribution is honest, not assumed.

De-duplication note (real-data finding, not a guess): DesireDB's `Evidence` field frequently
repeats the same sentence verbatim 2-3x (a scraping artifact, e.g. "Uh. No. Uh. No. Uh. No.").
`idiom_votes` therefore counts each DISTINCT pattern AT MOST ONCE per outcome (re.search, not
re.findall) so a duplicated fragment does not inflate vote weight relative to a single occurrence.
"""
from __future__ import annotations

import collections
import json
import os
import re
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CONCEPTNET_PATH = os.path.join(REPO_ROOT, "data", "datasets", "conceptnet5_en_100k.jsonl")

# ============================================================================ 1. IDIOM LEXICON
# Each entry: (compiled regex over lowercased/whitespace-normalized outcome text, polarity POS/NEG,
# phrase label, dictionary/usage citation). Authored from established dictionary/colloquial meaning,
# NOT reverse-engineered from any DesireDB gold label (calibration-honesty mandate).
_RAW_IDIOMS = [
    # ---- NEG (refusal / blockage / failure) ----------------------------------------------------
    (r"\bput the (?:kibosh|kabosh|kabash|kibash) on\b", "NEG", "put_the_kibosh_on",
     "Merriam-Webster: 'kibosh' = something that serves to check or stop; 'put the kibosh on' = to "
     "put a stop to (informal; DesireDB's own text spells it 'kabash')."),
    (r"\btold\s+(him|her|them|us|me)?\s*no\b", "NEG", "told_X_no",
     "plain-usage: 'told (someone) no' = refused a request."),
    (r"\bsaid\s+no\b", "NEG", "said_no", "plain-usage: refused/declined."),
    (r"\bno dice\b", "NEG", "no_dice",
     "Merriam-Webster informal: used to say no or that something is not allowed/possible."),
    (r"\bno way\b", "NEG", "no_way", "informal: an emphatic refusal."),
    (r"\bnot a chance\b", "NEG", "not_a_chance", "informal: firm refusal / impossibility."),
    (r"\bshot down\b", "NEG", "shot_down", "informal: rejected (a proposal/idea)."),
    (r"\bturned down\b", "NEG", "turned_down", "plain-usage: rejected (an offer/request)."),
    (r"\bfell through\b", "NEG", "fell_through", "plain-usage: (of a plan) failed to happen."),
    (r"\bdid(?:n'?t| not) pan out\b", "NEG", "didnt_pan_out",
     "informal: failed to develop successfully."),
    (r"\bcalled? it off\b", "NEG", "called_it_off", "plain-usage: cancelled."),
    (r"\bbacked out\b", "NEG", "backed_out", "plain-usage: withdrew from a commitment."),
    (r"\bbailed on\b", "NEG", "bailed_on", "informal: abandoned / failed to follow through on."),
    (r"\bstood\s+(me|him|her|us|them)\s+up\b", "NEG", "stood_X_up",
     "plain-usage: failed to keep an appointment/date."),
    (r"\bleft\s+(me|him|her|us|them)\s+hanging\b", "NEG", "left_X_hanging",
     "informal: failed to follow through / help when expected."),
    (r"\bgave\s+(me|him|her|us|them)\s+the cold shoulder\b", "NEG", "cold_shoulder",
     "idiom: deliberately unfriendly / rejecting treatment."),
    (r"\bblew\s+(me|him|her|us|them)\s+off\b", "NEG", "blew_X_off",
     "informal: ignored / failed to meet as planned."),
    (r"\buh[.,]?\s*no\b", "NEG", "uh_no", "colloquial terse refusal/negative reply."),
    (r"\bnope\b", "NEG", "nope", "informal: no."),
    (r"\bgave up on\b", "NEG", "gave_up_on", "plain-usage: abandoned (an attempt/goal)."),
    # ---- POS (success / agreement / approval) --------------------------------------------------
    (r"\bworked out\b", "POS", "worked_out", "plain-usage: (things) resolved favorably."),
    (r"\bcame through\b", "POS", "came_through",
     "plain-usage: succeeded in providing/doing what was needed."),
    (r"\bpulled it off\b", "POS", "pulled_it_off", "informal: succeeded at something difficult."),
    (r"\b(?:got|gave|give)\s+(?:the|us|him|her|me)?\s*green light\b", "POS", "green_light",
     "idiom: received approval to proceed."),
    (r"\bno problem\b", "POS", "no_problem", "informal reassurance: agreed / went fine."),
    (r"\bno worries\b", "POS", "no_worries", "informal reassurance: agreed / went fine."),
    (r"\bpiece of cake\b", "POS", "piece_of_cake", "idiom: accomplished easily."),
    (r"\bhit the jackpot\b", "POS", "hit_the_jackpot", "idiom: achieved a great success/gain."),
    (r"\bcame together\b", "POS", "came_together", "plain-usage: successfully organized/resolved."),
]
_IDIOM_PATTERNS = [(re.compile(pat, re.IGNORECASE), polarity, label, cite)
                    for pat, polarity, label, cite in _RAW_IDIOMS]


def dedupe_repeated_sentences(outcome: str) -> str:
    """Collapse DesireDB's own verbatim-repeated-TEXT scraping artifact to ONE occurrence.
    MEASURED@this session's smoke-run diagnostic: the Evidence field frequently repeats the same
    text block 2-3x, and -- unlike the tidy sentence-terminated case ('Uh. No. Uh. No. Uh. No.') --
    the repeats are often NOT cleanly period-separated ('...she told her no. So Jarrad calls...she
    told her no So Jarrad calls...she told her no ' -- only the FIRST copy keeps its trailing
    period). A naive sentence-split dedup misses this. Instead: WORD-level periodicity detection --
    find the smallest word-count period `p` such that the (case/punctuation-normalized) word
    sequence is `p`-periodic, allowing the final repeat to be a truncated prefix (common when a
    scrape cuts the last copy short); return the ORIGINAL words for just the first period. No
    detected periodicity (the common case for a real, non-repeated multi-sentence outcome) returns
    the input unmodified -- verified NOT to false-positive on a genuinely different multi-clause
    outcome (see self-test).

    General data-hygiene fix (NOT an idiom-lexicon change, no entries touched): without it, a
    per-TOKEN vote (WordNet or the ConceptNet bridge) over the duplicated text is inflated 2-3x
    proportional to a corpus artifact, not real signal -- the SAME concern that already motivated
    `idiom_votes`' at-most-once-per-pattern counting below; this extends the identical discipline to
    the token-level vote path (`hdlab.goal_achievement._attribute_outcome_state_idiom_grounded`)
    also reads through. Declared and applied uniformly to Direction-B M1's grounded path only --
    Stage-2's original `_attribute_outcome_state` (arm ii, the reference/comparator) is UNTOUCHED,
    so its landed numbers stay reproducible."""
    words = outcome.split()
    n = len(words)
    if n < 2:
        return outcome
    norm = [re.sub(r"[^a-z0-9]", "", w.lower()) for w in words]
    for p in range(1, n // 2 + 1):
        full_repeats = n // p
        if full_repeats < 2:
            continue
        remainder = n % p
        core = norm[:p]
        if any(w == "" for w in core):
            continue  # a period spanning pure-punctuation tokens is not a meaningful repeat unit
        if all(norm[k * p:(k + 1) * p] == core for k in range(1, full_repeats)) and \
                (remainder == 0 or norm[full_repeats * p:] == core[:remainder]):
            return " ".join(words[:p])
    return outcome


def idiom_votes(outcome: str) -> dict:
    """{'POS': int, 'NEG': int, 'matched': [phrase labels]} -- each DISTINCT idiom pattern counts
    AT MOST ONCE per outcome (re.search, not re.findall) so DesireDB's verbatim-repeated-sentence
    scraping artifact does not inflate vote weight."""
    o = " " + re.sub(r"\s+", " ", outcome.lower()).strip() + " "
    npos = nneg = 0
    matched = []
    for pat, polarity, label, _cite in _IDIOM_PATTERNS:
        if pat.search(o):
            matched.append(label)
            if polarity == "POS":
                npos += 1
            else:
                nneg += 1
    return {"POS": npos, "NEG": nneg, "matched": matched}


# ============================================================================ 2. CONCEPTNET ANTONYM
# BRIDGE. data/datasets/conceptnet5_en_100k.jsonl schema: {"subject","predicate","object"} triples;
# this curated 100k subset carries only 8 predicate types (AtLocation/CapableOf/Antonym/Causes/
# DerivedFrom/CausesDesire/DefinedAs/CreatedBy) -- MEASURED@this session (scan of the full file);
# no Synonym/FormOf idiom-phrase entries exist in this subset (spot-checked "kibosh": 0 hits), so
# ConceptNet's role here is the Antonym-bridge below, not idiom-phrase lookup (that is IDIOM_LEXICON
# above, hand-authored).
_antonym_cache = None


def _load_conceptnet_antonyms() -> dict:
    global _antonym_cache
    if _antonym_cache is None:
        d = collections.defaultdict(set)
        if os.path.exists(_CONCEPTNET_PATH):
            with open(_CONCEPTNET_PATH, encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if rec.get("predicate") != "Antonym":
                        continue
                    s = str(rec.get("subject", "")).replace("_", " ").strip()
                    o = str(rec.get("object", "")).replace("_", " ").strip()
                    if s and o:
                        d[s].add(o)
                        d[o].add(s)
        _antonym_cache = dict(d)
    return _antonym_cache


def conceptnet_bridge_vote(token_form: str, attr: str, attr_spec: dict) -> Optional[str]:
    """POS/NEG/None. Supplementary lookup (caller tries this only AFTER WordNet's own
    `_token_cue_polarity` returns None): if `token_form` is a ConceptNet-Antonym of a word already
    in `attr_spec['satisfied_cues']`, treat token_form as VIOLATED (NEG) evidence for `attr`, and
    vice versa for `violated_cues` -> SATISFIED (POS). `attr` is accepted for a stable call
    signature (parity with `_token_cue_polarity`) though the decision only depends on `attr_spec`.
    None if token_form has no ConceptNet-Antonym edge in this 100k subset, or the edge does not
    reach either cue pool -- most tokens will return None; report the empirical hit-rate, do not
    assume coverage."""
    del attr  # decision only depends on attr_spec's own cue pools
    antonyms = _load_conceptnet_antonyms().get(token_form, set())
    if not antonyms:
        return None
    if antonyms & set(attr_spec["satisfied_cues"]):
        return "NEG"
    if antonyms & set(attr_spec["violated_cues"]):
        return "POS"
    return None


def self_test_idiom_grounding() -> dict:
    """MECHANISM-FIRES checks on real cohort-derived outcome text (Direction-B M1 flagship cases)
    + the duplication-robustness invariant + ConceptNet-bridge graceful-degrade on an OOV token."""
    # real DesireDB artifact: 3x-repeated, only the FIRST copy keeps its trailing period.
    dd = dedupe_repeated_sentences(
        "So Jarrad calls and bec tells him she asked Robyn and she told her no. "
        "So Jarrad calls and bec tells him she asked Robyn and she told her no "
        "So Jarrad calls and bec tells him she asked Robyn and she told her no ")
    assert dd.count("Jarrad") == 1, dd
    dd_no_dup = dedupe_repeated_sentences("A single sentence with no repetition here.")
    assert "single sentence" in dd_no_dup.lower()  # no-op on already-unique text
    # no-false-positive: a genuinely different 2-clause outcome must NOT be collapsed.
    dd_distinct = dedupe_repeated_sentences(
        "The fence was repaired nicely. Meanwhile the weather was miserable and gloomy all week.")
    assert "repaired" in dd_distinct.lower() and "miserable" in dd_distinct.lower(), dd_distinct

    v1 = idiom_votes("Uh. No. Uh. No. Uh. No.")
    assert v1["NEG"] >= 1 and v1["POS"] == 0, v1
    v2 = idiom_votes("So Jarrad calls and bec tells him she asked Robyn and she told her no.")
    assert v2["NEG"] >= 1, v2
    v3 = idiom_votes("I put the kabash on that idea (privately), at least for the day.")
    assert v3["NEG"] >= 1 and "put_the_kibosh_on" in v3["matched"], v3
    v4 = idiom_votes("Everything worked out and we got the green light to proceed. No problem at all.")
    assert v4["POS"] >= 3 and v4["NEG"] == 0, v4
    # duplication-robustness: a 3x-repeated fragment must not inflate the vote beyond 1 per idiom.
    v5 = idiom_votes("No dice. No dice. No dice.")
    assert v5["NEG"] == 1, v5
    # ConceptNet bridge: callable + graceful-degrade on a token with no Antonym edge.
    cn_none = conceptnet_bridge_vote("zzz_not_a_real_word", "ACQUIRE_POSSESS",
                                      {"satisfied_cues": ["get"], "violated_cues": ["lose"]})
    assert cn_none is None
    # ConceptNet bridge: "abandon" IS a real Antonym-edge target in the 100k subset (MEASURED@this
    # module's own data scan: "abandon" Antonym "acquire"/"embrace"/"join"/"retain" etc.) and
    # ACQUIRE_POSSESS's violated_cues already contains "waste" not "abandon" as a literal cue --
    # verify the bridge reaches "acquire" (a ConceptNet-Antonym of "abandon") as SATISFIED-side
    # evidence for a violated_cues pool that lists "abandon"-adjacent OOV words. Uses SOCIAL_
    # CONNECTION's real violated_cues (which literally includes "abandon").
    cn_hit = conceptnet_bridge_vote(
        "acquire", "SOCIAL_CONNECTION",
        {"satisfied_cues": ["meet", "greet"],
         "violated_cues": ["reject", "abandon", "betray", "leave"]})
    assert cn_hit == "POS", cn_hit  # "acquire" is ConceptNet-Antonym of "abandon" (a violated_cue)
    return {"v1": v1, "v2": v2, "v3": v3, "v4": v4, "v5": v5, "dedupe_check": dd[:60],
            "conceptnet_bridge_none_case": cn_none, "conceptnet_bridge_hit_case": cn_hit,
            "n_idiom_patterns": len(_IDIOM_PATTERNS)}


if __name__ == "__main__":
    print(json.dumps(self_test_idiom_grounding(), indent=2, default=str))
