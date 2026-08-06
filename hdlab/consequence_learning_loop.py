"""hdlab/consequence_learning_loop.py -- continuous consequence-learning loop for OOV outcome-verb
result-valence (2026-08-06).

WHAT: as the substrate READS goal-bearing stories, when an out-of-vocabulary (OOV) outcome verb
appears it LEARNS that verb's result-valence from the episode's OWN computed MET/UNMET consequence,
accumulated CROSS-SITUATIONALLY across independent episodes. "A child learns waste=bad by living the
bad consequence," bootstrapped by the seed outcome lexicon standing in for the felt affective core.

TEACHER SIGNAL (make-or-break, per research/Director VET on disk 2026-08-06): the story's OWN
structural MET/UNMET verdict from hdlab.goal_typing.congruence_decision (Signal A) corroborated by the
independent flat-lexicon hdlab.goal_typing.lexicon_predict (Signal B). NOT the reward-earned appraisal
theta (pfc_gate_cfrpe / context_grounded_valence) -- those were VET-confirmed the WRONG mechanism
(planning gate / governor-gated), never imported here.

CREDIT ASSIGNMENT (structural, not a stopword list): an episode credits the outcome-clause verb whose
LOCAL-CLAUSE referent (pre-verb subject NP-head OR post-verb object NP-head, via the reused
hdlab.goal_typing._np_last_content, clause-bounded by the reused _CB_CLAUSE_BOUNDARY) LINKS (via the
reused _referent_links: literal / pronoun-coref / shared-feature tiers) to the GOAL's own referent
(find_desired_state(goal_sentence)["referent"]). Bystanders (savings/buy/...) are excluded because
they do not independently satisfy the SAME referent-linking test a real credit target must clear --
structural exclusion, no hand-written stoplist.

CONSOLIDATION: a verb grounds POS/NEG only after >= MIN_CONFIRM agreed exposures across INDEPENDENT
episodes with a vote margin clearing NEUTRAL_BAND; a below-band verb with enough data lands
GROUNDED_NEUTRAL (the pre-registered light-verb payoff -- be/go/make/give co-occur with BOTH met and
unmet so they wash out, they do NOT abstain and are NOT forced to a polarity); a verb with < MIN_CONFIRM
data stays PENDING (correctly OOV). The 3-way wrapper reuses hdlab.self_improving_loop.
decide_keep_or_revert's abstain-band-above-0 ARCHITECTURE (best-candidate-must-clear-a-margin).

MULTI-PASS BOOTSTRAP: reuses the self-extension loop family's read -> propose -> consolidate ->
re-read control flow. Each pass registers its newly-grounded words into the Tier-3 overlay
(verb_lexical_similarity.register_acquired_outcome), which the NEXT pass's Signal A automatically
consults (goal_typing._verb_classes' Tier-3 sentinel, already-wired), so more windows compute a teacher
verdict pass-over-pass. Fixed point on a zero-new-POS/NEG pass.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim, NEVER modified):
  hdlab.goal_typing.find_desired_state / congruence_decision / lexicon_predict           (teacher)
  hdlab.goal_typing._referent_links / _np_last_content / _tokens / _sentences            (credit scan)
  hdlab.goal_typing._STOP_BOUNDARY / _CB_CLAUSE_BOUNDARY                                  (clause bounds)
  hdlab.thematic_role_labeler.lemma_verb                                                  (lemmatize)
  hdlab.verb_lexical_similarity.in_lexicon / register_acquired_outcome / clear_acquired_outcome
  hdlab.self_improving_loop.decide_keep_or_revert                                         (abstain band)

GENUINELY-NEW code here (the consequence-learning orchestration): credit_window, consolidate (3-way
wrapper), run_pass, learn_corpus (multi-pass driver), and the referent-linked credit-target scan
(_credit_targets). NO new binding op, NO new taxonomy, NO external LLM, NO borrowed embedding.

SCOPE (do not overclaim): the teacher's precision is exactly congruence_decision's on real narrative
windows; credit is precision-first (referent-linkage required), so yield is honestly expected sparse
(the pre-reg's P_deflated ~= 0.30). This module is an EXPERIMENT-SUPPORT organ consumed by
experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py; it is NOT auto-imported by
any production/cert path (the Tier-3 overlay stays EMPTY at import).

Cites: preregs/2026-08-06_consequence_learning_loop_oov_outcome_verb_valence_v1.md (bands, config);
notes/research_consequence_learning_loop_oov_outcome_verb_valence_2026-08-06.md (mechanism spec);
hdlab.self_improving_loop (abstain-band architecture); the self-extension loop family
(experiments/exp_self_extension_loop_v1.py / _grounded_realprose_v1.py, multi-pass control flow).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from hdlab.goal_typing import (
    find_desired_state,
    congruence_decision,
    lexicon_predict,
    _referent_links,
    _np_last_content,
    _tokens,
    _sentences,
    _STOP_BOUNDARY,
    _CB_CLAUSE_BOUNDARY,
)
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.verb_lexical_similarity import (
    in_lexicon,
    register_acquired_outcome,
    clear_acquired_outcome,
)
from hdlab.self_improving_loop import decide_keep_or_revert

# ---- pre-registered config (fixed BEFORE any run; preregs/2026-08-06_consequence_learning_loop_*) ---
W_DEFAULT = 3            # window = goal sentence + next W sentences
MIN_CONFIRM = 3         # total agreed exposures before consolidation is consulted
NEUTRAL_BAND = 0.34     # |pos-neg|/(pos+neg) magnitude; below -> GROUNDED_NEUTRAL (>2:1 skew to call)
N_PASSES_DEFAULT = 3    # bootstrap cap; early-stop on a zero-new-POS/NEG pass


# ============================================================================ credit-target scan (new)
def _is_verblike(tok: str) -> bool:
    """Morphological verb-likeness test, BYTE-IDENTICAL to the diagnostic corpus scan's own
    OOV-candidate heuristic (companion spec Section 7): the lemmatizer changed the surface form OR it
    carries an -ed/-ing inflection. This is a general English inflection test applied UNIFORMLY to
    every token; it is NOT a hand-curated word list and encodes NO outcome-polarity information, so it
    is fully consistent with the 'credit assigned structurally, not via a stoplist' non-circularity
    claim. Excludes function words / determiners / bare nouns (the/and/nell) that sit next to the goal
    referent but are not the outcome verb. Known recall cost: a rare base-form or non-lemmatized
    irregular verb with no -ed/-ing (e.g. bare 'praise', irregular 'wept') is missed -- reported
    honestly, not hidden."""
    return lemma_verb(tok) != tok or tok.endswith(("ed", "ing"))


def _credit_targets(window_text: str, desired_referent) -> List[str]:
    """Structural credit-target scan. Returns the sorted set of OOV outcome-verb lemmas in
    `window_text` whose LOCAL-CLAUSE referent (pre-verb subject NP-head OR post-verb object NP-head,
    within the token's own clause bounded by _CB_CLAUSE_BOUNDARY) LINKS (via _referent_links) to
    `desired_referent`. A lemma already known to the FULL outcome lexicon (Tier-1/2/3) is excluded
    (in_lexicon True -> not a genuinely-novel target). Bystanders are excluded STRUCTURALLY (their
    subject/object does not link to the goal referent), never by a stopword list."""
    if desired_referent is None:
        return []
    toks = _tokens(window_text)
    targets: List[str] = []
    for idx, tok in enumerate(toks):
        if not _is_verblike(tok):
            continue  # morphological gate (Section 7 heuristic); excludes function words / bare nouns
        lemma = lemma_verb(tok)
        if in_lexicon(lemma, "outcome"):
            continue  # already grounded / seed-known -> not a novel credit target
        # local clause bounds around this token (coordinator/subordinator splitting, same set
        # _cb_analyze_outcome_clause uses; commas already stripped by _tokens' [a-z'] regex).
        cl_start = idx
        while cl_start > 0 and toks[cl_start - 1] not in _CB_CLAUSE_BOUNDARY:
            cl_start -= 1
        cl_end = idx
        while cl_end < len(toks) - 1 and toks[cl_end + 1] not in _CB_CLAUSE_BOUNDARY:
            cl_end += 1
        # pre-verb SUBJECT NP-head (mirrors find_desired_state's SUBJECT_IS_REFERENT extraction).
        subj_ref = _np_last_content(toks[cl_start:idx])
        # post-verb OBJECT NP-head: walk forward until a stop boundary / infinitival "to", then take
        # the NP-head (mirrors find_desired_state's OBJECT_IS_REFERENT extraction).
        j = idx + 1
        obj_span: List[str] = []
        while j <= cl_end and toks[j] not in _STOP_BOUNDARY and toks[j] != "to":
            obj_span.append(toks[j])
            j += 1
        obj_ref = _np_last_content(obj_span)
        linked = False
        for cand_ref in (subj_ref, obj_ref):
            if cand_ref is None:
                continue
            ok, _tier = _referent_links(desired_referent, cand_ref)
            if ok:
                linked = True
                break
        if linked:
            targets.append(lemma)
    return sorted(set(targets))


def _oov_lemmas_in_window(window_text: str) -> List[str]:
    """All verb-like OOV outcome-verb lemmas in the window, order-preserving-dedup. Used ONLY by the
    RANDOM-CREDIT ablation. Applies the SAME verb-like + OOV candidate gate as _credit_targets so the
    ONLY difference between the real and random-credit arms is the referent-linkage filter (isolates
    that STRUCTURAL referent-linkage, not the candidate pool, is load-bearing)."""
    seen = set()
    out: List[str] = []
    for tok in _tokens(window_text):
        if not _is_verblike(tok):
            continue
        lemma = lemma_verb(tok)
        if in_lexicon(lemma, "outcome"):
            continue
        if lemma not in seen:
            seen.add(lemma)
            out.append(lemma)
    return out


# ============================================================================ teacher + credit window (new)
def teacher_verdict(goal_sentence: str, window_text: str,
                    signal_mode: str = "and_gate") -> Optional[str]:
    """The episode's teacher label from the story's OWN computed consequence. Returns "MET", "UNMET",
    or None (ABSTAIN_EPISODE).

    signal_mode:
      "and_gate"  (production): Signal A (congruence_decision, structural + referent-linked) must fire
                  MET/UNMET AND Signal B (lexicon_predict, flat bag-of-words) must AGREE (== Signal A)
                  or be SILENT (NONE). Any other Signal B (opposite polarity or AMBIGUOUS) -> abstain.
      "signal_a_only": trust Signal A alone (ablation).
      "signal_b_only": trust Signal B alone (ablation).
    """
    if signal_mode == "signal_b_only":
        b = lexicon_predict(window_text)
        return b if b in ("MET", "UNMET") else None
    a, _detail = congruence_decision([goal_sentence], window_text)
    if a not in ("MET", "UNMET"):
        return None
    if signal_mode == "signal_a_only":
        return a
    # and_gate: require Signal B agreement or silence
    b = lexicon_predict(window_text)
    if b == a or b == "NONE":
        return a
    return None  # opposite polarity or AMBIGUOUS -> hard disagreement -> abstain


def credit_window(goal_sentence: str, window_text: str, desired_referent,
                  signal_mode: str = "and_gate",
                  credit_mode: str = "referent_linked",
                  rng_choice=None) -> Optional[dict]:
    """One episode. Returns {"teacher_verdict": "MET"|"UNMET", "credit_targets": [lemma, ...]} or None.

    credit_mode:
      "referent_linked" (production): _credit_targets (structural referent linkage).
      "random"          (ablation): one uniformly-random OOV lemma from the window (rng_choice(list)
                        -> element), ignoring referent linkage entirely.
    """
    tv = teacher_verdict(goal_sentence, window_text, signal_mode=signal_mode)
    if tv is None:
        return None
    if credit_mode == "random":
        oov = _oov_lemmas_in_window(window_text)
        if not oov or rng_choice is None:
            return None
        targets = [rng_choice(oov)]
    else:
        targets = _credit_targets(window_text, desired_referent)
    if not targets:
        return None
    return {"teacher_verdict": tv, "credit_targets": targets}


# ============================================================================ 3-way consolidation (new)
def consolidate(exposure_counter: Dict[str, Dict[str, int]]) -> Dict[str, str]:
    """Pure function {lemma: {"POS": n, "NEG": n}} -> {lemma: "POS"|"NEG"|"GROUNDED_NEUTRAL"|"PENDING"}.

    Reuses hdlab.self_improving_loop.decide_keep_or_revert's abstain-band-above-0 architecture (best
    candidate must STRICTLY clear the band): POS vs NEG are scored by the signed vote margin, the band
    is NEUTRAL_BAND. A -1e-9 nudge reconciles decide_keep_or_revert's STRICT '>' with the pre-reg's
    inclusive '>=' boundary so the registered band (margin >= 0.34 -> POS) is honored exactly.
    Below-band-with-enough-data -> GROUNDED_NEUTRAL (the light-verb payoff, an ACTIVE recognition of
    balance, distinct from PENDING = not-enough-data)."""
    out: Dict[str, str] = {}
    for lemma, votes in exposure_counter.items():
        pos = int(votes.get("POS", 0))
        neg = int(votes.get("NEG", 0))
        total = pos + neg
        if total < MIN_CONFIRM:
            out[lemma] = "PENDING"
            continue
        margin = (pos - neg) / total
        adopt = decide_keep_or_revert({"POS": margin, "NEG": -margin},
                                      abstain_band=NEUTRAL_BAND - 1e-9)
        out[lemma] = adopt if adopt is not None else "GROUNDED_NEUTRAL"
    return out


# ============================================================================ one pass (new)
def run_pass(goal_windows: List[Tuple[str, str, object]],
             signal_mode: str = "and_gate",
             credit_mode: str = "referent_linked",
             rng_choice=None) -> Tuple[int, int, List[dict]]:
    """One corpus pass over `goal_windows` (each (goal_sentence, window_text, desired_referent)),
    using the CURRENT Tier-3 overlay state (Signal A automatically sees words grounded by prior
    passes). Returns (n_windows_with_teacher, n_windows_credited, exposure_records):
      n_windows_with_teacher -- windows whose teacher signal fired MET/UNMET (the bootstrap curve; rises
                                pass-over-pass as newly-grounded Tier-3 words feed Signal A);
      n_windows_credited     -- windows that ALSO produced >= 1 novel credit target (drops as words get
                                grounded and drop out of the OOV credit pool, per the pre-reg's
                                Tier-3-exclusion rule -- this is expected, not a bug);
      exposure_records       -- flat [{"lemma","window_id","teacher_verdict"}] for the master tally +
                                the label-scramble control."""
    exposure_records: List[dict] = []
    n_with_teacher = 0
    n_credited = 0
    for wid, (goal_sentence, window_text, desired_referent) in enumerate(goal_windows):
        tv = teacher_verdict(goal_sentence, window_text, signal_mode=signal_mode)
        if tv is None:
            continue
        n_with_teacher += 1
        if credit_mode == "random":
            oov = _oov_lemmas_in_window(window_text)
            targets = [rng_choice(oov)] if (oov and rng_choice is not None) else []
        else:
            targets = _credit_targets(window_text, desired_referent)
        if not targets:
            continue
        n_credited += 1
        for lemma in targets:
            exposure_records.append({"lemma": lemma, "window_id": wid, "teacher_verdict": tv})
    return n_with_teacher, n_credited, exposure_records


# ============================================================================ multi-pass driver (new)
def learn_corpus(goal_windows: List[Tuple[str, str, object]],
                 n_passes: int = N_PASSES_DEFAULT,
                 signal_mode: str = "and_gate",
                 credit_mode: str = "referent_linked",
                 rng_choice=None,
                 register: bool = True) -> dict:
    """Multi-pass bootstrap driver. Clears the Tier-3 overlay, runs up to n_passes corpus passes.
    Exposures are merged into a MASTER cross-situational tally deduplicated by (window_id, lemma)
    first-verdict-wins (so a word's evidence is retained even after it is grounded and drops out of the
    OOV credit pool in later passes, and a window that scores in several passes is never double-counted).
    After each pass the running master is consolidated and any newly-grounded POS/NEG word is registered
    into the Tier-3 overlay (iff register=True) so the NEXT pass's Signal A picks it up (the bootstrap).
    Early-stops on a pass that adds zero new (window,lemma) exposures.

    Returns: master_counter (the definitive cross-situational tally), master_grounded (consolidate of
    it -- the single source of truth for every canary/learnable/noise number), registered (the overlay
    POS/NEG map used for scoring), master_records (deduped flat records for the scramble control), and
    the per-pass bootstrap curve. Leaves the overlay POPULATED with the final POS/NEG grounding iff
    register=True (caller scores against the live overlay then clears for hygiene)."""
    clear_acquired_outcome()
    master: Dict[str, Dict[str, int]] = {}
    master_records: List[dict] = []
    seen_pairs = set()                        # (window_id, lemma) dedup
    registered: Dict[str, str] = {}           # lemma -> "POS"/"NEG" currently in overlay
    pass_reports: List[dict] = []
    for p in range(n_passes):
        n_with_teacher, n_credited, records = run_pass(
            goal_windows, signal_mode=signal_mode, credit_mode=credit_mode, rng_choice=rng_choice)
        added = 0
        for rec in records:
            key = (rec["window_id"], rec["lemma"])
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            pole = "POS" if rec["teacher_verdict"] == "MET" else "NEG"
            master.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += 1
            master_records.append(rec)
            added += 1
        grounded = consolidate(master)
        newly_pos = newly_neg = 0
        for lemma, verdict in grounded.items():
            if verdict in ("POS", "NEG") and registered.get(lemma) != verdict:
                if register:
                    register_acquired_outcome(lemma, verdict)
                registered[lemma] = verdict
                if verdict == "POS":
                    newly_pos += 1
                else:
                    newly_neg += 1
        pass_reports.append({
            "pass": p + 1,
            "n_windows_with_teacher": n_with_teacher,
            "n_windows_credited": n_credited,
            "n_new_exposure_pairs": added,
            "n_newly_registered_pos": newly_pos,
            "n_newly_registered_neg": newly_neg,
            "cumulative_registered": len(registered),
            "n_grounded_neutral": sum(1 for v in grounded.values() if v == "GROUNDED_NEUTRAL"),
            "n_lemmas_pending": sum(1 for v in grounded.values() if v == "PENDING"),
        })
        if p > 0 and added == 0:
            break  # fixed point: no new exposures
    return {
        "registered": dict(registered),
        "master_counter": master,
        "master_grounded": consolidate(master),
        "master_records": master_records,
        "pass_reports": pass_reports,
    }


# ============================================================================ self-test
def self_test() -> dict:
    """Scaffold-free construction-level self-test on HAND-AUTHORED micro-episodes (proves the
    mechanism fires + the reused organs are wired), plus a determinism + abstain-band check. Does NOT
    touch the real corpus or the eval bank (that is the cell's job)."""
    clear_acquired_outcome()

    # (1) consolidate is a pure 3-way abstain-band split, honoring the registered bands.
    assert consolidate({"a": {"POS": 3, "NEG": 0}})["a"] == "POS"          # margin 1.0 >= 0.34
    assert consolidate({"a": {"POS": 0, "NEG": 3}})["a"] == "NEG"          # margin -1.0
    assert consolidate({"a": {"POS": 2, "NEG": 2}})["a"] == "GROUNDED_NEUTRAL"  # margin 0.0
    assert consolidate({"a": {"POS": 2, "NEG": 1}})["a"] == "GROUNDED_NEUTRAL"  # margin 0.333 < 0.34
    assert consolidate({"a": {"POS": 1, "NEG": 0}})["a"] == "PENDING"      # total 1 < MIN_CONFIRM
    # boundary: margin exactly 0.34 (pos=67,neg=33) -> POS (inclusive >=, reconciled vs strict >)
    assert consolidate({"a": {"POS": 67, "NEG": 33}})["a"] == "POS"

    # (2) teacher AND-gate fires MET and UNMET when Signal A (structural) and Signal B (flat lexicon)
    # AGREE. NOTE (design-honest): an INVERTED goal (goal=sink(raft), outcome=sank) makes Signal A read
    # MET while the flat lexicon reads 'sank' as its default-UNMET -> the AND-gate correctly ABSTAINS on
    # that disagreement (a precision cost the AND-gate is supposed to pay), so the MET case below uses a
    # non-inverted goal where both signals agree.
    g_save = "Owen wanted to save the boat before the storm hit"
    win_unmet = "The men worked hard. The boat sank in the storm."
    assert teacher_verdict(g_save, win_unmet) == "UNMET", "goal=save(boat), outcome=sank(boat) -> UNMET"
    g_mend = "Owen wanted to mend the canoe before the flood came"
    win_met = "The men worked all night. The canoe mended by dawn."
    assert teacher_verdict(g_mend, win_met) == "MET", "goal=mend(canoe), outcome=mended(canoe) -> MET"
    assert teacher_verdict(g_save, "Nothing at all happened here today.") is None, "no outcome -> abstain"

    # (3) credit-target scan: an OOV verb (croak) whose object/subject links to the goal referent is a
    # target; a bystander OOV verb in a DIFFERENT-referent clause is not.
    g_lantern = "Nell wanted to fix the lantern before the guests came"
    # 'tinker' is OOV of the outcome lexicon; its object 'lantern' links (literal) to the goal referent.
    win_credit = "Nell tinkered the lantern and the savings dwindled in the drawer."
    tgts = _credit_targets(win_credit, "lantern")
    assert "tinker" in tgts, f"referent-linked OOV verb 'tinker' must be credited, got {tgts}"
    assert "dwindle" not in tgts, f"bystander 'dwindle' (referent=savings/drawer) must NOT be credited, got {tgts}"

    # (4) credit_window returns None when there is a teacher but no linked credit target, and a record
    # when both are present.
    rec = credit_window(g_lantern, "Nell mended the lantern quickly.", "lantern")
    # 'mend' is IN the outcome lexicon (REPAIR_PRESERVE) so it is NOT a novel target -> None.
    assert rec is None, f"a window whose only outcome verb is already-known must yield no novel credit, got {rec}"

    # (5) determinism: two runs of a tiny corpus produce identical master grounding + registered maps.
    windows = [
        (g_save, win_unmet, "boat"),
        (g_lantern, win_credit, "lantern"),
    ]
    r1 = learn_corpus(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    r2 = learn_corpus(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    assert r1["master_grounded"] == r2["master_grounded"], "GLASS-BOX FAILURE: non-deterministic grounding"
    assert r1["registered"] == r2["registered"], "GLASS-BOX FAILURE: non-deterministic registered map"

    # (6) the AND-gate is never MORE permissive than Signal-A-only (it requires Signal B agreement on
    # top of Signal A): whenever the AND-gate fires, Signal-A-only must have fired the same verdict.
    for gs, win in [(g_save, win_unmet), (g_mend, win_met),
                    (g_save, "The girl was sorry she was late and the boy fell down laughing.")]:
        ag = teacher_verdict(gs, win, signal_mode="and_gate")
        ao = teacher_verdict(gs, win, signal_mode="signal_a_only")
        assert ag is None or ag == ao, "AND-gate must never fire a verdict Signal-A-only did not"

    clear_acquired_outcome()
    return {
        "consolidate_ok": True,
        "teacher_flip_ok": True,
        "credit_target_referent_linked_ok": True,
        "determinism_ok": r1["master_grounded"] == r2["master_grounded"],
        "config": {"W": W_DEFAULT, "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "N_PASSES": N_PASSES_DEFAULT},
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
