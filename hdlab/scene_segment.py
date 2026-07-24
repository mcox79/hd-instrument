"""SITUATION-MODEL SCENE SEGMENTATION + PER-SCENE TOPICAL-PROTAGONIST coref.

Pluggable extension of hdlab.coref + hdlab.coref_distractor_suppress (banked cells /
modules NOT edited). Attacks the CONFIRMED cross-sentence coref residual wall (29513:
450/450 residual misses have >=2 same-gender specific competitors) with TWO ablatable
levers wired INTO the cross-sentence SuppressReader pipeline:

  LEVER 1  TOPICAL-PROTAGONIST PICK (Centering / Zwaan protagonist-continuity). For a
           same-gender-competing pronoun in a TOPICAL slot (nominative he/she + possessive
           his/her), prefer the TOPICAL protagonist -- the entity that DRIVES the events --
           over the merely-RECENT same-gender competitor. Topicality is scored by
           SUBJECT-ROLE-WEIGHTED mention mass (a subject mention weighs CENTER_SUBJECT_W,
           an oblique 1.0 = frequency + subject-role-mass) with a FIRST-MENTION primacy
           tie-break and NO recency term -- exactly the merely-recent lever this overrides.
           Object (him/them), neuter (it/its) and plural (they/their) slots KEEP the
           backbone recency pick (an object / inanimate referent is not the protagonist).
           This ports the VALIDATED exp_coref_salience_rank_topicality_v1 logic
           (WorkingOverlay._topical_ranked: (count, -first_midx)); the ROLE-MASS variant
           additionally weights subject mentions per the coref.py Centering Cf-ranking.

  LEVER 2  PER-SCENE SCOPING. The protagonist is PER-SCENE, not per-document. Detect scene
           boundaries via GENERAL closed-class time / location adjunct cues ("the next day"
           / "the next morning" / "meanwhile" / "years later" / chapter headings) and an
           optional character-set turnover signal, then window the topical-mass computation
           to the CURRENT scene. A pronoun in scene S prefers scene-S's protagonist, not a
           globally more-frequent character from an earlier scene. When the current scene
           has no candidate participant (a cross-scene reference), the pick FALLS BACK to
           the whole-doc topical pick over the same pool (so per-scene is a strict superset
           of information over whole-doc; the isolated variable is the scene window).

FAITHFUL REUSE (nothing improved over validated logic; banked cells/modules NOT edited):
  - SuppressReader (generic-distractor suppression + adaptive recency/centering pick) and
    its pool construction: hdlab.coref_distractor_suppress.
  - CENTER_SUBJECT_W (subject-role weight) + parse helpers: hdlab.coref.
  - WorkingOverlay._topical_ranked (frequency + first-mention primacy): hdlab.state_of_mind.
With ALL new levers OFF (prefer_topical=False) SceneProtagonistReader.resolve_stream
reproduces SuppressReader.resolve_stream BIT-FOR-BIT (asserted in the cell self-test):
topical + scene are the ONE / TWO isolated variables.

GLASS-BOX: pure symbolic; NO torch, NO external LLM, NO network. ASCII-only, no em-dash.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Set, Tuple

from hdlab.coref import CENTER_SUBJECT_W
from hdlab.coref_distractor_suppress import GenericDistractorFilter, SuppressReader
from hdlab.state_of_mind import (
    PRONOUN_SCOPE,
    TARGET_PRONOUNS,
    EntityState,
)

# ---------------------------------------------------------------------------
# Pronoun slot routing (GENERAL grammatical case; NOT tuned to LitBank characters).
# TOPICAL slots = the animate gendered protagonist slot: nominative (he/she) + possessive
# (his/her/hers). OBJECT (him/them) + NEUTER (it/its) + PLURAL (they/their) keep RECENCY.
# 'her' is genuinely case-ambiguous without POS (possessive PRP$ vs object PRP); LitBank
# CoNLL carries no POS, so 'her' defaults to the TOPICAL slot (its dominant possessive use
# in narrative prose) and the cell measures an explicit her->recency ablation for the
# object-'her' regression risk.
TOPICAL_SLOT_HEADS: frozenset = frozenset({"he", "she", "his", "her", "hers"})
RECENCY_SLOT_HEADS: frozenset = frozenset({"him", "them", "it", "its", "they", "their"})


# ---------------------------------------------------------------------------
# LEVER 2a: GENERAL closed-class scene-shift cue phrases (leading sentence n-grams).
# Temporal / scene-shift discourse markers of ordinary English narrative; NOT a list of
# LitBank characters or book-specific strings (anti-circular). Stored as token tuples;
# a sentence opens a new scene if its leading content tokens start with any cue.
# ---------------------------------------------------------------------------
_TIME_CUE_PHRASES: frozenset = frozenset({
    # "the next / following <time-unit>"
    ("the", "next", "day"), ("the", "next", "morning"), ("the", "next", "evening"),
    ("the", "next", "night"), ("the", "next", "week"), ("the", "next", "year"),
    ("the", "next", "afternoon"), ("the", "next", "spring"), ("the", "next", "summer"),
    ("the", "following", "day"), ("the", "following", "morning"),
    ("the", "following", "night"), ("the", "following", "week"),
    ("the", "following", "year"),
    # "that <time>"
    ("that", "night"), ("that", "evening"), ("that", "afternoon"), ("that", "day"),
    ("that", "morning"), ("that", "same", "day"), ("that", "same", "night"),
    # "one <time>"
    ("one", "day"), ("one", "morning"), ("one", "evening"), ("one", "night"),
    ("one", "afternoon"), ("one", "summer"), ("one", "winter"),
    # "<n> later" / afterwards
    ("years", "later"), ("days", "later"), ("hours", "later"), ("moments", "later"),
    ("a", "moment", "later"), ("some", "time", "later"), ("a", "week", "later"),
    ("a", "year", "later"), ("a", "few", "days", "later"), ("long", "afterwards"),
    ("years", "afterward"), ("years", "afterwards"),
    # temporal frame-shifts
    ("in", "the", "morning"), ("in", "the", "evening"), ("in", "the", "meantime"),
    ("at", "last"), ("at", "length"), ("after", "a", "while"), ("after", "a", "time"),
    ("soon", "after"), ("not", "long", "after"), ("early", "next", "morning"),
    # single-token discourse openers
    ("meanwhile",), ("afterwards",), ("afterward",), ("presently",),
    # chapter / section headings = strong scene boundary
    ("chapter",), ("book",),
})
_CUE_LENS: Tuple[int, ...] = (4, 3, 2, 1)
_LEAD_PUNCT = ".,'\"!?;:-()[]"


def _clean_lead(sent_tokens: Sequence[str], k: int = 4) -> Tuple[str, ...]:
    """First k alphabetic-ish leading tokens (lowercased, punctuation stripped)."""
    out: List[str] = []
    for t in sent_tokens:
        core = t.strip(_LEAD_PUNCT).lower()
        if not core:
            continue
        out.append(core)
        if len(out) >= k:
            break
    return tuple(out)


def sentence_opens_scene(sent_tokens: Sequence[str]) -> bool:
    """True iff the sentence begins with a closed-class scene-shift cue phrase."""
    lead = _clean_lead(sent_tokens, k=max(_CUE_LENS))
    for L in _CUE_LENS:
        if len(lead) >= L and lead[:L] in _TIME_CUE_PHRASES:
            return True
    return False


# ---------------------------------------------------------------------------
# CoNLL -> per-sentence token lists (aligned with hdlab.coref.parse_litbank_conll's
# sentence indexing: blank line = boundary, consecutive blanks collapse, '#' skipped).
# ---------------------------------------------------------------------------
def parse_conll_sentences(path: str) -> List[List[str]]:
    """Return the document's sentences as lowercased-token lists (sent_idx-aligned)."""
    sents: List[List[str]] = []
    cur: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                if cur:
                    sents.append(cur)
                    cur = []
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 4:
                continue
            cur.append(cols[3].lower())
    if cur:
        sents.append(cur)
    return sents


def _specific_chars_by_sent(mentions: List[dict], n_sents: int) -> List[Set[str]]:
    """Per-sentence set of specific-character heads (named or gender-cued nominal mentions)."""
    out: List[Set[str]] = [set() for _ in range(n_sents)]
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        si = m.get("sent_idx", 0)
        if si < 0 or si >= n_sents:
            continue
        is_specific = (m.get("gender") is not None) or (m.get("name_gender") is not None)
        if is_specific:
            out[si].add(m["head"].lower())
    return out


def detect_scene_boundaries(sentences: List[List[str]],
                            mentions: Optional[List[dict]] = None, *,
                            use_time_cues: bool = True,
                            use_charset_change: bool = False,
                            charset_window: int = 3) -> List[int]:
    """Assign a scene id to every sentence index.

    A sentence opens a new scene if (time-cue) it begins with a closed-class scene-shift
    cue phrase, OR (charset-change, optional) the specific-character set turns over
    completely relative to the previous charset_window sentences (a fully disjoint set
    that introduces at least one new character). scene ids are contiguous 0..K."""
    n = len(sentences)
    if n == 0:
        return []
    boundary = [False] * n
    if use_time_cues:
        for i in range(1, n):
            if sentence_opens_scene(sentences[i]):
                boundary[i] = True
    if use_charset_change and mentions is not None:
        chars = _specific_chars_by_sent(mentions, n)
        for i in range(1, n):
            active: Set[str] = set()
            for w in range(1, charset_window + 1):
                if i - w >= 0:
                    active |= chars[i - w]
            cur = chars[i]
            if cur and active and cur.isdisjoint(active) and (cur - active):
                boundary[i] = True
    scene = [0] * n
    s = 0
    for i in range(n):
        if i > 0 and boundary[i]:
            s += 1
        scene[i] = s
    return scene


# ---------------------------------------------------------------------------
# The scene-aware topical reader. Extends SuppressReader: same suppression backbone +
# adaptive recency/centering pick, PLUS the two new levers. With prefer_topical=False it
# reproduces SuppressReader.resolve_stream bit-for-bit (the ONE isolated variable).
# ---------------------------------------------------------------------------
class SceneProtagonistReader(SuppressReader):
    """SuppressReader + topical-protagonist pick (case-routed) + per-scene protagonist scope."""

    @staticmethod
    def _agreement_narrow(pool: List[EntityState],
                          gender: Optional[str]) -> List[EntityState]:
        """Port of WorkingOverlay._agreement_preferred tier-1: among the suppression pool,
        restrict to KNOWN-gender-matching candidates when any exist (a gendered pronoun's
        protagonist is an animate SAME-gender entity, not a frequent genderless inanimate
        that survived suppression as an occasional subject). If no known-gender candidate
        exists the tier is a NO-OP (abstain from over-narrowing = never-confidently-wrong).
        This is what makes the topical-mass rank pick the same-gender CHARACTER, not a
        high-frequency inanimate (streets / passengers / weather)."""
        if gender in ("masc", "fem"):
            known = [e for e in pool if e.gender == gender]
            if known:
                return known
        return pool

    @staticmethod
    def _topical_pick(pool: List[EntityState],
                      scene_midxs: Optional[Set[int]],
                      midx_to_role: Dict[int, int],
                      mode: str) -> Optional[EntityState]:
        """Pick the TOPICAL protagonist among the pool.

        mode='rolemass': score = subject-role-weighted mention mass (subject weighs
          CENTER_SUBJECT_W, oblique 1.0) -> frequency + subject-role-mass; tie-break by
          FIRST-MENTION primacy (earliest introduced); NO recency term.
        mode='freqonly': the VALIDATED WorkingOverlay._topical_ranked port -- score =
          mention count, tie-break first-mention primacy.
        scene_midxs=None: whole-document mass. Otherwise mass is restricted to the
          current scene's mentions (a candidate with no current-scene mention is skipped;
          the caller falls back to whole-doc topical when no scene participant survives)."""
        if not pool:
            return None
        best: Optional[EntityState] = None
        best_key: Optional[Tuple[float, int]] = None
        for e in pool:
            mids = e.mention_midxs
            if scene_midxs is not None:
                mids = [mx for mx in mids if mx in scene_midxs]
                if not mids:
                    continue
            if mode == "rolemass":
                mass = 0.0
                for mx in mids:
                    mass += CENTER_SUBJECT_W if midx_to_role.get(mx, 99) == 0 else 1.0
            else:  # freqonly
                mass = float(len(mids))
            first = min(mids)
            key = (mass, -first)
            if best_key is None or key > best_key:
                best_key = key
                best = e
        return best

    def resolve_stream(self, mentions: List[dict], targets: List[dict], *,
                       scene_ids: Optional[List[int]] = None,
                       prefer_topical: bool = False, per_scene: bool = False,
                       topical_mode: str = "rolemass",
                       topical_heads: Optional[frozenset] = None,
                       use_gazetteer: bool = True, chain_pronouns: bool = True,
                       suppress_generic: bool = True,
                       use_nonref: bool = True, use_struct: bool = True,
                       abstain_on_empty: bool = False,
                       margin_abstain: bool = False,
                       margin_thresh: float = 0.5) -> List[dict]:
        """SuppressReader.resolve_stream + topical/per-scene levers.

        prefer_topical=False reproduces SuppressReader.resolve_stream bit-for-bit (asserted
        in the cell self-test). prefer_topical=True: for a target pronoun whose head is in
        topical_heads (nominative/possessive gendered slot) the pool pick becomes the
        TOPICAL protagonist (per-scene when per_scene=True and scene_ids supplied) instead
        of the backbone recency/centering adaptive pick; object/neuter/plural slots keep the
        backbone pick. Record schema is identical to SuppressReader (adds topical_fired)."""
        from hdlab.coref_distractor_suppress import build_ever_subject_heads

        if topical_heads is None:
            topical_heads = TOPICAL_SLOT_HEADS
        ever_subj = build_ever_subject_heads(mentions)
        filt = GenericDistractorFilter(ever_subj, use_nonref=use_nonref,
                                       use_struct=use_struct)
        midx_to_role = {m["midx"]: m.get("sent_role_rank", 99) for m in mentions}
        target_by_midx = {t["target"]["midx"]: t for t in targets}

        # per-scene scaffolding (only when the scene lever is active)
        scene_of_midx: Dict[int, int] = {}
        scene_to_midxs: Dict[int, Set[int]] = defaultdict(set)
        use_scene = bool(prefer_topical and per_scene and scene_ids is not None)
        if use_scene:
            for m in mentions:
                si = m.get("sent_idx", 0)
                sc = scene_ids[si] if 0 <= si < len(scene_ids) else -1
                scene_of_midx[m["midx"]] = sc
                scene_to_midxs[sc].add(m["midx"])

        from hdlab.coref import name_content_tokens

        overlay = self._new_overlay()
        head_to_cluster: Dict[str, int] = {}
        records: List[dict] = []

        for m in mentions:
            resolved_ent = None
            pool_empty = False
            suppressed_any = False
            topical_fired = False
            if m["is_pronoun"] and m["head"] in TARGET_PRONOUNS:
                now = overlay.n_observed
                sc = PRONOUN_SCOPE[m["head"]]
                cands = overlay._compatible_entities(sc["gender"], sc["number"])
                trank = midx_to_role.get(m["midx"], 99)
                if suppress_generic:
                    pool = [c for c in cands if not filt.is_generic(c)]
                    suppressed_any = len(pool) < len(cands)
                else:
                    pool = cands
                if pool:
                    do_topical = prefer_topical and (m["head"] in topical_heads)
                    if do_topical:
                        # agreement-narrow (known same-gender character) BEFORE topical rank.
                        tpool = self._agreement_narrow(pool, sc["gender"])
                        scene_midxs = None
                        if use_scene:
                            cur_scene = scene_of_midx.get(m["midx"], -1)
                            scene_midxs = scene_to_midxs.get(cur_scene)
                        pick = self._topical_pick(tpool, scene_midxs, midx_to_role,
                                                  topical_mode)
                        if pick is None:  # no scene participant -> whole-doc topical fallback
                            pick = self._topical_pick(tpool, None, midx_to_role, topical_mode)
                        resolved_ent = pick
                        topical_fired = True
                    else:
                        resolved_ent = self._adaptive_pick(pool, now, trank, midx_to_role)
                    if margin_abstain and resolved_ent is not None:
                        mg = self._margin(pool, resolved_ent, now, self._beta, self._lam)
                        if mg is not None and mg < margin_thresh:
                            resolved_ent = None
                else:
                    pool_empty = True
                    if not abstain_on_empty:
                        resolved_ent = self._adaptive_pick(cands, now, trank, midx_to_role)

                if m["midx"] in target_by_midx:
                    tinfo = target_by_midx[m["midx"]]
                    if resolved_ent is None:
                        rec = dict(resolved_head=None, resolved_cluster=None,
                                   attempted=False, correct=False)
                    else:
                        rc = head_to_cluster.get(resolved_ent.head)
                        rec = dict(resolved_head=resolved_ent.head, resolved_cluster=rc,
                                   attempted=True,
                                   correct=(rc is not None and rc == m["cluster"]))
                    from hdlab.coref import sent_dist_bucket
                    rec.update(target_midx=m["midx"], gold_cluster=m["cluster"],
                               sent_dist=tinfo["sent_dist"],
                               bucket=sent_dist_bucket(tinfo["sent_dist"]),
                               pool_empty=pool_empty, suppressed_any=suppressed_any,
                               topical_fired=topical_fired,
                               n_cands=len(cands), n_pool=len(pool))
                    records.append(rec)

            # advance the mention stream
            if m["is_pronoun"]:
                overlay.observe(m["head"], is_pronoun=True,
                                gender=m["gender"], number=m["number"])
                if chain_pronouns and resolved_ent is not None:
                    resolved_ent.mention_midxs.append(m["midx"])
            else:
                eff_gender = m["gender"]
                if eff_gender is None and use_gazetteer:
                    eff_gender = m.get("name_gender")
                is_named = bool(name_content_tokens(m.get("span_toks", [m["head"]])))
                overlay.observe(m["head"], gender=eff_gender, number=m["number"],
                                is_proper_name=is_named)
                head_to_cluster[m["head"].lower()] = m["cluster"]

        return records
