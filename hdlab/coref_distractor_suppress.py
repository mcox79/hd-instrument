"""GENERIC-DISTRACTOR SUPPRESSION + ABSTENTION for cross-sentence pronoun coref.

Pluggable extension of hdlab.coref / hdlab.bundle_focus_coref. Attacks the
DIAGNOSTIC-CONFIRMED cross-sentence coref wall (NOT the refuted appositive bridging):
  (1) the wrong picks are GENERIC / NON-REFERENTIAL common nouns
      (servants / people / one / country / nobody / neighbourhood) out-competing the
      correct SPECIFIC character;
  (2) the reader NEVER ABSTAINS -- 100% of misses are CONFIDENT wrong picks (attempt
      rate 1.0 on every cross-sentence arm), so the single-sentence reader's
      never-confidently-wrong property is absent cross-sentence.

TWO BRAIN-FAITHFUL LEVERS (each ablatable):
  LEVER 1  GENERIC-DISTRACTOR SUPPRESSION. A pronoun refers to a salient DISCOURSE
           ENTITY (a specific character), NOT a generic / non-referential noun.
           Suppress generic antecedent candidates via GENERAL tests (NOT tuned to
           LitBank characters):
             (1a) NONREF  : head in a closed GRAMMATICAL class of indefinite /
                            quantifier pro-forms (one, none, nobody, someone, other,
                            some, any, ...). These never introduce a specific referent.
             (1b) STRUCT  : a COMMON noun (not a proper name, no gender cue) that was
                            NEVER realized in SUBJECT / agent (first-in-sentence)
                            position anywhere in the document. Discourse protagonists
                            are repeatedly realized as grammatical subjects; a bare
                            generic distractor that is never a subject is not a
                            referential discourse entity. Purely structural (parse
                            role rank), no lexicon, book-agnostic.
           GUARD (anti-over-suppression): NEVER suppress a proper-name entity or a
           gender-cued entity (mother / father / widow / a gazetteer-gendered name) --
           those are specific characters. If suppression would empty the candidate
           pool, LEVER 2 decides (abstain) or the arm falls back to the unfiltered pick.
  LEVER 2  ABSTENTION (never-confidently-wrong). When no confident SPECIFIC antecedent
           survives suppression (the pool is empty, or the top specific candidate's
           salience margin over its runner-up is below threshold), ABSTAIN instead of
           forcing a pick. Converts confident-wrong -> abstain (trustworthiness), at a
           coverage cost measured honestly (attempt rate + precision-on-answered).
  LEVER 3  (optional) PRONOUN-CHAIN CONTINUITY. Chain each resolved pronoun back onto
           its (specific) antecedent so the topical entity stays salient across a
           pronoun run. Because resolution now targets only the SPECIFIC pool, chaining
           re-adds no generic noise (the step-1b runaway was chaining onto whatever won,
           including generics). Default ON to match the 0.2053 backbone (xsent_all).

FAITHFUL REUSE (nothing improved over validated logic; banked cells NOT edited):
  - WorkingOverlay + resolvers + salience + agreement: hdlab.state_of_mind.
  - parse_litbank_conll / build_pronoun_targets / sent_dist_bucket / CENTER_* constants:
    hdlab.coref.
The suppress-OFF configuration reproduces hdlab.coref.CorefReader's adaptive pick
BIT-FOR-BIT (asserted in the self-test): suppression is the ONE isolated variable.

GLASS-BOX: pure symbolic; NO torch, NO external LLM, NO network. ASCII-only, no em-dash.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from hdlab.coref import (
    CENTER_PARALLEL_BONUS,
    CENTER_SUBJECT_W,
    name_content_tokens,
    sent_dist_bucket,
)
from hdlab.state_of_mind import (
    OVERLAY_BETA,
    OVERLAY_TIEBREAK_LAMBDA,
    PRONOUN_SCOPE,
    TARGET_PRONOUNS,
    WINDOW_K_DEFAULT,
    SetKnownBase,
    WorkingOverlay,
    EntityState,
)

# ---------------------------------------------------------------------------
# LEVER 1a: a CLOSED GRAMMATICAL CLASS of indefinite / quantifier pro-forms and
# generic pro-nouns. These are NON-REFERENTIAL (they do not introduce a specific
# discourse entity a he/she pronoun corefers back to). This is a general English
# function-word class -- NOT a list of LitBank character names (anti-circular).
# Deliberately EXCLUDES gendered / person common nouns (man, woman, mother, father,
# widow, ...): those ARE specific-character candidates and are protected by the guard.
# ---------------------------------------------------------------------------
QUANTIFIER_STOPLIST: frozenset = frozenset({
    # indefinite pronouns
    "one", "none", "nobody", "no-one", "noone", "someone", "somebody",
    "anyone", "anybody", "everyone", "everybody", "somewhat",
    "something", "nothing", "anything", "everything",
    # quantifier / determiner pro-forms used pronominally
    "other", "others", "another", "some", "any", "all", "each", "both",
    "either", "neither", "few", "many", "several", "most", "none",
    "such", "same", "rest", "half", "part", "kind", "sort",
})


def is_quantifier_nonref(head: str) -> bool:
    """LEVER 1a test: head is a closed-class indefinite / quantifier pro-form."""
    return head.lower().strip(".,'\"!?;:") in QUANTIFIER_STOPLIST


# ---------------------------------------------------------------------------
# LEVER 1: the generic-distractor classifier (structural; general; ablatable).
# ---------------------------------------------------------------------------
class GenericDistractorFilter:
    """Decide whether an overlay EntityState is a GENERIC / non-referential distractor.

    ever_subject_heads: the set of lowercased heads that were realized at least once in
      SUBJECT / agent (first-referring-mention-in-sentence) position anywhere in the doc
      (the STRUCT topicality signal; parse field sent_role_rank == 0).

    Sub-tests (each individually toggleable for ablation):
      use_nonref  LEVER 1a: head in QUANTIFIER_STOPLIST.
      use_struct  LEVER 1b: a COMMON noun (not named, no gender cue) never realized as
                  a subject/agent -> a non-topical bare generic.

    GUARD: a proper-name entity (is_named) or a gender-cued entity (gender is not None)
    is NEVER generic -- those are specific characters. Applied before any sub-test.
    """

    def __init__(self, ever_subject_heads: Set[str], *,
                 use_nonref: bool = True, use_struct: bool = True) -> None:
        self.ever_subject_heads = ever_subject_heads
        self.use_nonref = use_nonref
        self.use_struct = use_struct

    def is_generic(self, ent: EntityState) -> bool:
        # GUARD: specific characters (named or gender-cued) are never suppressed.
        if ent.is_named or ent.gender is not None:
            return False
        head = ent.head.lower()
        if self.use_nonref and is_quantifier_nonref(head):
            return True
        if self.use_struct and (head not in self.ever_subject_heads):
            # common, gender-unknown, never a grammatical subject -> bare generic.
            return True
        return False


def build_ever_subject_heads(mentions: List[dict]) -> Set[str]:
    """Lowercased heads realized as a subject/agent (sent_role_rank == 0) at least once."""
    out: Set[str] = set()
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        if m.get("sent_role_rank", 99) == 0:
            out.add(m["head"].lower())
    return out


# ---------------------------------------------------------------------------
# The suppression-aware reader. Mirrors hdlab.coref.CorefReader.resolve_stream's
# per-target record schema so the cell scores every arm identically.
# ---------------------------------------------------------------------------
class SuppressReader:
    """Cross-sentence pronoun reader with generic-distractor suppression + abstention.

    The adaptive pick (recency-within-window else centering) is reproduced from
    hdlab.coref.CorefReader with the SAME validated constants; the ONLY change is that
    the candidate pool is optionally filtered by GenericDistractorFilter. With
    suppress_generic=False the pick is bit-identical to CorefReader's adaptive arm."""

    def __init__(self, *, base=None, beta: float = OVERLAY_BETA,
                 lam: float = OVERLAY_TIEBREAK_LAMBDA,
                 window_k: int = WINDOW_K_DEFAULT) -> None:
        self._base = base if base is not None else SetKnownBase()
        self._beta = beta
        self._lam = lam
        self._window_k = window_k

    def _new_overlay(self) -> WorkingOverlay:
        return WorkingOverlay(base=self._base, beta=self._beta, lam=self._lam,
                              window_k=self._window_k)

    # ---- pick helpers (reproduce CorefReader adaptive/centering over a POOL) ----
    def _centering_pick(self, pool: List[EntityState], now: int, target_rank: int,
                        midx_to_role: Dict[int, int]) -> Optional[EntityState]:
        """Reproduces CorefReader._centering_pick over an arbitrary candidate pool."""
        if not pool:
            return None
        target_is_subj = (target_rank == 0)
        best, best_s = None, -1.0
        for e in pool:
            s = 0.0
            for mx in e.mention_midxs:
                s += CENTER_SUBJECT_W if midx_to_role.get(mx, 99) == 0 else 1.0
            s += self._beta * math.exp(-self._lam * (now - e.last_midx))
            if (midx_to_role.get(e.last_midx, 99) == 0) == target_is_subj:
                s += CENTER_PARALLEL_BONUS
            if s > best_s:
                best_s = s
                best = e
        return best

    def _adaptive_pick(self, pool: List[EntityState], now: int, target_rank: int,
                       midx_to_role: Dict[int, int]) -> Optional[EntityState]:
        """Reproduces CorefReader._adaptive_pick over a POOL: recency-window first, else
        centering. With pool = all compatible entities this is bit-identical to
        CorefReader (recency_window picks max last_midx among in-window entities)."""
        if not pool:
            return None
        in_win = [e for e in pool if (now - e.last_midx) <= self._window_k]
        if in_win:
            return max(in_win, key=lambda e: e.last_midx)
        return self._centering_pick(pool, now, target_rank, midx_to_role)

    @staticmethod
    def _margin(pool: List[EntityState], picked: Optional[EntityState],
                now: int, beta: float, lam: float) -> Optional[float]:
        """Salience margin of the picked entity over the best OTHER pool entity (maintained
        salience). None if fewer than 2 candidates (no competitor -> unambiguous)."""
        if picked is None or len(pool) < 2:
            return None
        sal = {id(e): e.salience(now, beta, lam) for e in pool}
        top = sal[id(picked)]
        others = [v for e, v in ((e, sal[id(e)]) for e in pool) if e is not picked]
        return top - max(others)

    def resolve_stream(self, mentions: List[dict], targets: List[dict], *,
                       use_gazetteer: bool = True, chain_pronouns: bool = True,
                       suppress_generic: bool = True,
                       use_nonref: bool = True, use_struct: bool = True,
                       abstain_on_empty: bool = False,
                       margin_abstain: bool = False,
                       margin_thresh: float = 0.5) -> List[dict]:
        """Read mentions in order; resolve each target pronoun. Returns per-target records:
          {target_midx, gold_cluster, sent_dist, bucket, resolved_head, resolved_cluster,
           attempted, correct, pool_empty, suppressed_any}
        attempted=False = ABSTAINED (never-confidently-wrong). correct requires attempted.

        suppress_generic=False, abstain_on_empty=False, margin_abstain=False reproduces
        CorefReader's adaptive+chain+gazetteer arm (the 0.2053 backbone) bit-for-bit."""
        ever_subj = build_ever_subject_heads(mentions)
        filt = GenericDistractorFilter(ever_subj, use_nonref=use_nonref,
                                       use_struct=use_struct)
        midx_to_role = {m["midx"]: m.get("sent_role_rank", 99) for m in mentions}
        target_by_midx = {t["target"]["midx"]: t for t in targets}
        overlay = self._new_overlay()
        head_to_cluster: Dict[str, int] = {}
        records: List[dict] = []

        for m in mentions:
            resolved_ent = None
            pool_empty = False
            suppressed_any = False
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
                    resolved_ent = self._adaptive_pick(pool, now, trank, midx_to_role)
                    if margin_abstain and resolved_ent is not None:
                        mg = self._margin(pool, resolved_ent, now, self._beta, self._lam)
                        if mg is not None and mg < margin_thresh:
                            resolved_ent = None      # ambiguous -> abstain
                else:
                    pool_empty = True
                    if not abstain_on_empty:
                        # fall back to the UNFILTERED pick (no abstain -> accuracy arm)
                        resolved_ent = self._adaptive_pick(cands, now, trank, midx_to_role)
                    # else: leave resolved_ent = None -> ABSTAIN

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
                    rec.update(target_midx=m["midx"], gold_cluster=m["cluster"],
                               sent_dist=tinfo["sent_dist"],
                               bucket=sent_dist_bucket(tinfo["sent_dist"]),
                               pool_empty=pool_empty, suppressed_any=suppressed_any,
                               n_cands=len(cands), n_pool=len(pool))
                    records.append(rec)

            # advance the mention stream
            if m["is_pronoun"]:
                overlay.observe(m["head"], is_pronoun=True,
                                gender=m["gender"], number=m["number"])
                # LEVER 3: chain the resolved (specific) antecedent's salience.
                if chain_pronouns and resolved_ent is not None:
                    resolved_ent.mention_midxs.append(m["midx"])
            else:
                eff_gender = m["gender"]
                if eff_gender is None and use_gazetteer:
                    eff_gender = m.get("name_gender")
                # GENERAL proper-name detection (any capitalized name span; not just
                # gazetteer hits) so every named character is guard-protected.
                is_named = bool(name_content_tokens(m.get("span_toks", [m["head"]])))
                overlay.observe(m["head"], gender=eff_gender, number=m["number"],
                                is_proper_name=is_named)
                head_to_cluster[m["head"].lower()] = m["cluster"]

        return records


# ===================== formula self-tests ==========================================

def _mk(head, cluster, is_pron, sent, midx, gender, role_rank, number="singular",
        name_gender=None):
    return {"head": head, "cluster": cluster, "is_pronoun": is_pron,
            "sent_idx": sent, "midx": midx, "gender": gender, "number": number,
            "name_gender": name_gender, "sent_role_rank": role_rank,
            "is_subject": (role_rank == 0), "span_toks": [head]}


def _selftest_suppress_off_matches_coref_adaptive() -> None:
    """suppress_generic=False reproduces CorefReader.resolve_stream(adaptive+chain+gaz)
    bit-for-bit on a constructed doc (suppression is the ONE isolated variable)."""
    from hdlab.coref import CorefReader, build_pronoun_targets

    # A doc with a named protagonist, a generic distractor, cross-sentence pronouns.
    mentions = []
    mi = 0
    # S0: Anna(1, fem, subject) walked with the servants(2, generic, object).
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    mentions.append(_mk("servants", 2, False, 0, mi, None, 1)); mi += 1
    # S1: She(1) rested.  (cross-sentence; gold=1 Anna)
    mentions.append(_mk("she", 1, True, 1, mi, "fem", 0)); mi += 1
    # S2: the servants(2, still object) waited; she(1) called.
    mentions.append(_mk("servants", 2, False, 2, mi, None, 1)); mi += 1
    mentions.append(_mk("she", 1, True, 2, mi, "fem", 0)); mi += 1
    targets = build_pronoun_targets(mentions)

    coref = CorefReader()
    base = coref.resolve_stream(mentions, targets, reset_per_sentence=False,
                                adaptive=True, chain_pronouns=True, use_gazetteer=True)
    sup = SuppressReader()
    off = sup.resolve_stream(mentions, targets, suppress_generic=False,
                             chain_pronouns=True, use_gazetteer=True)
    assert len(base) == len(off) == len(targets), "record count mismatch"
    for b, o in zip(base, off):
        assert b["resolved_cluster"] == o["resolved_cluster"], (
            "suppress-OFF diverged from CorefReader adaptive: base=%s off=%s"
            % (b["resolved_cluster"], o["resolved_cluster"]))
        assert b["attempted"] == o["attempted"], "attempt divergence"


def _selftest_suppression_fires_and_helps() -> None:
    """On the constructed doc, suppression removes the generic 'servants' from the pool so
    the specific 'anna' wins the cross-sentence pronouns; suppress-OFF (backbone) may pick
    the recency-local generic. Suppression FIRES (>=1 suppressed) and does not hurt."""
    from hdlab.coref import build_pronoun_targets

    mentions = []
    mi = 0
    mentions.append(_mk("anna", 1, False, 0, mi, "fem", 0, name_gender="fem")); mi += 1
    # generic distractor mentioned right before each pronoun, never a subject, no gender:
    for s in range(1, 4):
        mentions.append(_mk("servants", 2, False, s, mi, None, 1)); mi += 1
        mentions.append(_mk("she", 1, True, s, mi, "fem", 0)); mi += 1  # gold = Anna(1)
    targets = build_pronoun_targets(mentions)
    assert len(targets) == 3

    sup = SuppressReader()
    on = sup.resolve_stream(mentions, targets, suppress_generic=True,
                            use_nonref=True, use_struct=True, chain_pronouns=True)
    # suppression must FIRE (servants is a never-subject genderless common noun)
    assert any(r["suppressed_any"] for r in on), "suppression never fired"
    acc_on = sum(r["correct"] for r in on) / len(on)
    assert acc_on >= 0.99, "suppression should let the specific Anna win: acc=%.3f" % acc_on
    heads = [r["resolved_head"] for r in on if r["attempted"]]
    assert all(h == "anna" for h in heads), "expected all -> anna, got %s" % heads


def _selftest_abstention_converts_confident_wrong() -> None:
    """When the ONLY compatible candidate is a generic distractor, abstain_on_empty ABSTAINS
    (attempted=False) instead of forcing a confident-wrong pick; the guard protects a
    gender-cued specific noun (never suppressed)."""
    from hdlab.coref import build_pronoun_targets

    # A masc pronoun whose only masc-compatible entity is a generic never-subject noun.
    mentions = []
    mi = 0
    # S0: nobody(2, generic quantifier, object) present.
    mentions.append(_mk("nobody", 2, False, 0, mi, None, 1)); mi += 1
    # S1: He(3) spoke. gold cluster 3 has NO prior mention -> not a target; make a prior.
    # Give a prior masc pronoun-less mention that is ALSO generic so pool empties.
    mentions.append(_mk("crowd", 3, False, 0, mi, None, 1)); mi += 1  # generic, object
    mentions.append(_mk("he", 3, True, 1, mi, "masc", 0)); mi += 1     # gold=3 crowd
    targets = build_pronoun_targets(mentions)
    assert len(targets) == 1 and targets[0]["target"]["head"] == "he"

    sup = SuppressReader()
    # accuracy arm (fallback): forces a pick -> attempted True
    acc_arm = sup.resolve_stream(mentions, targets, suppress_generic=True,
                                 abstain_on_empty=False, chain_pronouns=True)
    assert acc_arm[0]["attempted"] is True, "fallback arm must force a pick"
    # trust arm (abstain): pool empty after suppression -> ABSTAIN
    trust_arm = sup.resolve_stream(mentions, targets, suppress_generic=True,
                                   abstain_on_empty=True, chain_pronouns=True)
    assert trust_arm[0]["attempted"] is False, (
        "abstain arm must ABSTAIN when only generics compatible, got %s"
        % trust_arm[0]["resolved_head"])
    assert trust_arm[0]["pool_empty"] is True


def _selftest_guard_protects_specific_characters() -> None:
    """The guard must NEVER suppress a proper-name or gender-cued entity even if it is never
    a subject (a specific character mentioned only in object position)."""
    ever_subj: Set[str] = set()   # nobody is ever a subject in this micro-check
    filt = GenericDistractorFilter(ever_subj, use_nonref=True, use_struct=True)
    named = EntityState("bennet", gender=None, number=None, is_named=True)
    gendered = EntityState("widow", gender="fem", number=None, is_named=False)
    generic = EntityState("country", gender=None, number=None, is_named=False)
    quant = EntityState("nobody", gender=None, number=None, is_named=False)
    assert filt.is_generic(named) is False, "named entity must be protected"
    assert filt.is_generic(gendered) is False, "gender-cued entity must be protected"
    assert filt.is_generic(generic) is True, "never-subject genderless common noun -> generic"
    assert filt.is_generic(quant) is True, "quantifier pro-form -> generic"


def _run_all_selftests() -> dict:
    _selftest_suppress_off_matches_coref_adaptive()
    _selftest_suppression_fires_and_helps()
    _selftest_abstention_converts_confident_wrong()
    _selftest_guard_protects_specific_characters()
    return {"quantifier_stoplist_size": len(QUANTIFIER_STOPLIST),
            "reuse": ["WorkingOverlay", "CorefReader.adaptive(reproduced)",
                      "CENTER_SUBJECT_W", "CENTER_PARALLEL_BONUS"]}


if __name__ == "__main__":
    r = _run_all_selftests()
    print("[coref_distractor_suppress selftest] PASS %s" % r)
