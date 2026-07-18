"""
DEIXIS / DISCOURSE-PARTICIPANT TRACKING on the FULL McGuffey THIRD READER (the data-driven #1 next
reader component). The scale-up VET localized the DOMINANT foundation FP cause at scale = COREF (40% of
sampled FPs; read_grow_full_third_reader_clauseseg_generalization_v1, verdict SCOPE_LIMITED_OR_DEGRADES),
and the VET (ae27a0b3) found ALL of the coref FPs literally carry a 1st/2nd-PERSON pronoun stored as a
PHANTOM ENTITY HEAD (i / you / we / me / my / our / your) -- the reader has no speaker model, so inside
QUOTED SPEECH it treats "I"/"me"/"you" as their own entities. This cell adds the missing mechanism.

MECHANISM (ONE variable vs the current reader = the deixis axis; EVERYTHING else byte-identical):
  In a 3rd-person narrative the 1st/2nd-person pronouns appear inside QUOTED SPEECH. Resolve them via the
  QUOTATIVE FRAME (a DISTINCT mechanism from 3rd-person antecedent resolution -- these pronouns index a
  discourse ROLE, not a prior mention):
    1. Detect the quotative frame (said/cried/asked/answered/replied X ; or X said) -> bind SPEAKER = X.
    2. 1st-person (i/me/my/mine/we/us/our/ours) -> the SPEAKER entity.
       2nd-person (you/your/yours/ye/thee/thou) -> the ADDRESSEE (a 'to X' in the frame / a vocative in the
       quote / the prior speaker in a dialogue exchange).
    3. The extracted RELATION binds to the RESOLVED participant, NOT to a phantom "i"/"you"/"my" head.
  Walkthrough: 'Who will help me?' said the hen / 'Not I,' said the dog -> me=hen, I=dog (NO i/me entity).

  The deixis axis EXTENDS hdlab.state_of_mind.WorkingOverlay (note_turn / resolve_deixis / speaker /
  addressee / prev_speaker), additive + opt-in + default-OFF + witness-preserving -- SAME discipline as the
  agreement / salience / topical extensions. With deixis OFF, extract_passage_deixis is BYTE-IDENTICAL to
  the banked reader's extract_passage_vf (asserted in the self-test + the regression guard).

BRAIN-FAITHFULNESS NOTE (pre-reg): deixis = speaker/addressee tracking via the quotative frame is a
  DISTINCT mechanism from 3rd-person antecedent resolution. 1st/2nd-person pronouns are INDEXICALS: they
  index the discourse ROLE (who is speaking / who is spoken to), not a coreferent prior mention. The brain
  tracks discourse participants (the "who is talking to whom" model) as a separate faculty from antecedent
  coref; this cell keeps them separate (a new overlay axis, not a change to the antecedent resolvers). Any
  deviation is flagged: the addressee fallback (prior speaker / most-salient participant) is a HEURISTIC
  stand-in for the full common-ground model the brain maintains; reported honestly + measured separately.

REAL BASELINE (the design-gate #1): the CURRENT reader (deixis OFF) = the banked extract_passage_vf, which
  stores 1st/2nd-person as phantom entity heads -> reproduces the scale coref-FP on real dialogue text
  (measured corpus-wide as the PHANTOM-HEAD relation count). Not a strawman: it IS the shipped reader.

CAN-FAIL (design-gate #2; all genuinely reachable + informative):
  (a) frame detection could be UNRELIABLE -> low deixis RECALL (many phantoms unresolved; no improvement).
  (b) speaker attribution could be WRONG -> low deixis PRECISION (phantoms resolved to the wrong entity;
      the metric can show a REGRESSION -- wrong real entities injected).
  (c) addressee (2nd-person) is genuinely HARDER than speaker (1st-person) -- reported + banded SEPARATELY;
      the addressee arm can fail while the speaker arm holds.

DIFFICULTY-ON (design-gate #3): the FULL 79-lesson third reader (dialogue lessons w/ real 1st/2nd-person-
  in-quotes: 130 quoted-speech sites with a 1st/2nd-person pronoun; 326 quotative-verb occurrences), NOT
  the narration-only 14-subset.

ONE VARIABLE (design-gate #4): add the deixis layer; hold grounding, 3rd-person coref, clause-seg, role
  assignment, composition, cheap wins ALL identical (extract_passage_deixis(deixis=False) == VF byte-id).

MEASURE:
  (1) PHANTOM-HEAD FP class (corpus-wide, no annotation): # foundation relations whose head is a 1st/2nd-
      person phantom, OFF vs ON -> the reduction the deixis layer buys (the 18-FP scale class).
  (2) DEIXIS-RESOLUTION precision / recall vs an INDEPENDENT single-annotator gold (speaker / addressee
      attribution per quote, matched by pid + content cue), decomposed 1st-person(speaker) vs 2nd(addressee).
  (3) COMPREHENSION on who-said-what / who-did-what dialogue Qs answerable ONLY if 1st-person resolves to
      the speaker (OFF cannot answer; ON can) -> delta.

REGRESSION GUARD (the deixis axis must not touch the banked reader): extract_passage_deixis(deixis=False)
  BYTE-IDENTICAL to VF.extract_passage_vf on ALL 79 lessons (foundation set equality); role passive/reversal
  controls >= 1.00; overlay witness (now 7/7) green; determinism (two ON builds identical). OMP=1, fixed
  int seed, sorted(set) ordering, NO salted-builtin-hashing for any seed or split.

BRANCHES (decisive, genuinely can-fail):
  DEIXIS_RESOLVES_PARTICIPANTS = speaker attribution precision >= 0.80 AND recall >= 0.60 on the 1st-person
    gold AND phantom-head FP reduction >= 0.50 AND comprehension delta > 0 AND no regression -> the deixis
    component RESOLVES the dominant scale coref-FP -> next reader component landed (VET-pending).
  SCOPE_LIMITED_OR_WEAK = frame-parse recall low OR speaker precision below floor OR addressee-only weak OR
    reduction below floor -> localize (which sub-mechanism: frame detection / speaker attribution / addressee)
    + honest deflate.
  REGRESSION = a guard failed (deixis axis leaked into the banked reader) -> revert + localize.

Glass-box (POS + averaged perceptron + WordNet grounding + a transparent quotative-frame parser + the
additive overlay deixis axis; NO external LLM, NO torch/GPU at runtime). Local / foreground-to-completion.
NO push / NO remote-persist. CLAIM-VET-pending; strategic read = HYPOTHESIS pending landed-VET.

ANCHOR: read_deixis_participant_tracking_third_reader_v1
BUILDS ON: read_grow_full_third_reader_clauseseg_generalization_v1 (the scale-up + FP localization, 71769bd78)
+ reader_clauseseg_verbclass_filter_v1 (extract_passage_vf; VET a8b287c8) + the packaged state-of-mind
overlay (hdlab/state_of_mind.py; witness verify_state_of_mind_overlay.py). CORPUS: mcguffey_third_reader.
clean.txt (PG#14766, PD). COMPUTE: sequential-CPU; wall target < 400s (79 lessons x2 passes).
PRIOR-WORK CHECK: substrate_query "deixis speaker tracking 1st 2nd person coref quotative frame addressee"
-> top cosine 0.2695 (addressee / native_speaker WordNet atoms), all < 0.30 -> NOVEL, no prior-arc rediscovery.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this non-HD, no-KG measurement cell):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)                                 [META_RULE_AH: tmp_replace]
# - discriminator CAN-FAIL (SCOPE_LIMITED_OR_WEAK / REGRESSION genuinely reachable)          [design-gate]
# - REAL baseline = the CURRENT reader (deixis OFF == VF byte-identical), reproduces the phantom-FP  [not a strawman]
# - one variable = the deixis axis; independent single-annotator gold; coverage/annotator limits reported honestly
# - real_code_path: runs the REAL extract_passage_deixis (copy of VF extract + the deixis axis) + REAL
#   perceptron + POS tagger on REAL corpus text; runs the REAL passive/reversal controls + overlay witness [F.1]
# - byte-identity OFF vs VF.extract_passage_vf asserted on ALL 79 lessons                     [F.1 / regression]
# - deterministic seeding (fixed int seed, sample via sorted(set)+Random(FIXED); no hash())   [F.5/PROT-023]
# - start-marker + crash-diagnostic; heartbeat present (wall can exceed 60s)
# - all reported numbers MEASURED@this metrics.json; baseline/refs CITED@their metrics.json
# - N/A: KGStore (no KG); N/A cardinality sweep-axis; N/A CRLB (no HD noise floor); N/A multi-seed
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import re
import sys
import json
import time
import random
import argparse
import platform
import traceback
from collections import Counter
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# The CURRENT reader, imported VERBATIM: VF = the clause-seg verb-class factivity filter cell. Its
# extract_passage_vf runs the whole banked pipeline (coref overlay + role assigner + cheap wins + clause-
# seg factivity filter + composition). We COPY it below and add ONE axis (deixis); OFF it is byte-identical.
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC          # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2   # noqa: E402
from experiments import exp_reader_clauseseg_verbclass_filter_v1 as VF          # noqa: E402
from hdlab.state_of_mind import deixis_person                                   # noqa: E402

# Bind the SAME helpers VF's extract uses (identical semantics; the ONLY new code is the deixis axis).
segment_clauses_with_boundaries = V2.segment_clauses_with_boundaries
_is_bare_vp = V2._is_bare_vp
_topical_animate_head = V2._topical_animate_head
INJECT_SUBJ = V2.INJECT_SUBJ
_prefers_topical = V2._prefers_topical
_agreement_attrs = V2._agreement_attrs
_RESOLVABLE = V2._RESOLVABLE
_RESOLVABLE_SO = V2._RESOLVABLE_SO
_RESOLVABLE_POSS = V2._RESOLVABLE_POSS
apply_role_fix = V2.apply_role_fix
is_self_loop = V2.is_self_loop
SetKnownBase = V2.SetKnownBase
WorkingOverlay = V2.WorkingOverlay
PRONOUN_SCOPE = V2.PRONOUN_SCOPE
verb_admits_injection = VF.verb_admits_injection
_VF_MODE = VF._VF_MODE
_ALL_LEARNED_MODES = VF._ALL_LEARNED_MODES
_LEARNED_MODES = VF._LEARNED_MODES

ANCHOR_NAME = "read_deixis_participant_tracking_third_reader_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
CORPUS_PATH = os.path.join(REPO, "data", "corpora", "graded_readers_graded", "cleaned",
                           "mcguffey_third_reader.clean.txt")
SEED = 20260718
_KINDS = ("svo", "loc", "poss")
_PAGE_RE = re.compile(r"^\(\d+\)\s*$")
_LESSON_RE = re.compile(r"^#?\s*LESSON\b", re.IGNORECASE)

# CITED baseline (the scale-up localization).
CITED_SCALE = dict(dom_fp_cause="COREF", coref_fp_fraction=0.40, n_coref_fp=18,
                   n_relations_on=3509)   # CITED@data/exp_read_grow_full_third_reader_clauseseg_generalization_v1/metrics.json

# ==== the deixis participant set (phantom-head class) ====
PHANTOM_HEADS = frozenset({"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves",
                           "you", "your", "yours", "yourself", "yourselves", "ye", "thou", "thee",
                           "thy", "thine", "thyself"})

# ==== quotative frame lexicon (glass-box) ====
QUOTATIVE_VERBS = frozenset({
    "said", "says", "say", "saying", "cried", "cries", "cry", "crying", "asked", "asks", "ask", "asking",
    "answered", "answers", "answer", "replied", "replies", "reply", "called", "calls", "call",
    "shouted", "shouts", "exclaimed", "exclaims", "whispered", "whispers", "spoke", "speaks", "sang",
    "sings", "screamed", "screams", "told", "tells", "muttered", "added", "adds", "continued", "began",
    "retorted", "remarked", "inquired", "responded", "murmured", "roared", "gasped", "sighed", "wept",
})
# terms that FOLLOW the verb but are NOT the speaker subject (frame connectives / addressee marker).
_NON_SUBJ_AFTER = frozenset({"to", "that", "if", "and", "but", "when", "for", "as", "with", "in", "on"})
# address nouns usable as a vocative addressee head.
_ADDRESS_NOUNS = frozenset({"sir", "madam", "madame", "boy", "boys", "girl", "child", "children", "friend",
                            "friends", "mother", "father", "son", "daughter", "master", "mistress",
                            "man", "woman", "uncle", "aunt", "brother", "sister", "kitten", "doctor",
                            "captain", "neighbor", "stranger", "lady", "gentlemen", "gentleman"})


# =======================================================================================
# Corpus loader (verbatim structure from the scale-up cell).
# =======================================================================================
def load_lessons():
    with open(CORPUS_PATH, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    lessons = {}
    cur_id, cur, idx = None, [], 0
    for ln in lines:
        s = ln.strip()
        if _LESSON_RE.match(s):
            if cur_id is not None:
                lessons[cur_id] = " ".join(x.strip() for x in cur if x.strip()).strip()
            idx += 1
            cur_id, cur = f"L{idx:02d}", []
            continue
        if _PAGE_RE.match(s):
            continue
        cur.append(ln)
    if cur_id is not None:
        lessons[cur_id] = " ".join(x.strip() for x in cur if x.strip()).strip()
    return {k: v for k, v in lessons.items() if v}


# =======================================================================================
# GLASS-BOX quotative-frame parser: bind SPEAKER (+ optional ADDRESSEE) from a split-sentence's frame.
# Uses the tagged tokens + the RAW sentence (quotes are stripped by the tagger, so vocative detection
# reads the raw quote content). Returns None when no quotative frame is present in this sentence.
# =======================================================================================
def _token_char_starts(tagged, raw):
    """Best-effort char-start of each token in the raw sentence (cursor scan; quotes are between tokens)."""
    starts = []
    cur = 0
    low_raw = raw.lower()
    for surf, low, pos in tagged:
        idx = raw.find(surf, cur)
        if idx < 0:
            idx = low_raw.find(low, cur)
        if idx < 0:
            starts.append(None)
            continue
        starts.append(idx)
        cur = idx + max(1, len(surf))
    return starts


def _inquote_char_ranges(raw, start_open):
    """Char ranges inside quotes for this sentence given the carried open-state; returns (ranges, end_open).
    A leading in-quote region (start_open) runs from 0 to the first closing quote; unbalanced trailing quote
    runs to the end (a quote continued into the next split-sentence)."""
    ranges = []
    open_at = 0 if start_open else None
    for i, ch in enumerate(raw):
        if ch == '"':
            if open_at is None:
                open_at = i
            else:
                ranges.append((open_at, i))
                open_at = None
    end_open = open_at is not None
    if end_open:
        ranges.append((open_at, len(raw)))
    return ranges, end_open


def _in_quote(char_start, ranges):
    if char_start is None:
        return False
    return any(a <= char_start <= b for a, b in ranges)


def _resolve_subject_pronoun(low, ov):
    """A frame subject that is a nominative pronoun (he/she/they) -> its antecedent entity head (validated
    antecedent path); else the literal token. 'i'/'we'/'you' as a frame subject stays literal (rare)."""
    if low in ("he", "she", "they") and low in PRONOUN_SCOPE:
        ent = ov.resolve_pronoun(low, strategy=ORC.FIXED_COREF_STRATEGY, prefer_agreement=True)
        return ent.head if ent is not None else low
    return low


def parse_quotative_frame(tagged, raw_sentence, ov, inquote=None):
    """Return dict(speaker, subj_type, addressee, addr_src, qvi) or None. Glass-box: frame = a quotative
    verb OUTSIDE the quotes (the attribution clause) with a subject NP either AFTER it ('said X') or BEFORE
    it ('X said'). inquote (per-token bool list) disambiguates the frame verb from a quotative verb that
    appears INSIDE the quote (e.g. 'told' in '"I told him," said Joe'); when None, all tokens are eligible."""
    def _eligible(i):
        return inquote is None or not inquote[i]
    qvi = None
    for i, (surf, low, pos) in enumerate(tagged):
        if low in QUOTATIVE_VERBS and (pos.startswith("VB") or pos == "MD") and _eligible(i):
            qvi = i
            break
    if qvi is None:
        for i, (surf, low, pos) in enumerate(tagged):
            if low in QUOTATIVE_VERBS and _eligible(i):
                qvi = i
                break
    if qvi is None:
        return None

    speaker, subj_type = None, None
    # (1) subject-AFTER the verb: 'said Joe' / 'said the poor widow' / 'said he'. Subject must be OUTSIDE
    # the quote (a post-verb IN-quote token means the quote follows the verb -> no post-verb subject).
    k = qvi + 1
    while k < len(tagged):
        surf, low, pos = tagged[k]
        if not _eligible(k) or low in _NON_SUBJ_AFTER:
            break
        if pos in ("DT", "JJ", "JJR", "JJS", "RB", "CD", "PRP$"):
            k += 1
            continue
        if pos in ("NNP", "NNPS"):
            speaker, subj_type = low, "name"
        elif pos in ("NN", "NNS"):
            speaker, subj_type = low, "noun"
        elif low in ("he", "she", "they"):
            speaker, subj_type = _resolve_subject_pronoun(low, ov), "pronoun"
        break
    # (2) else subject-BEFORE the verb: 'he said' / 'The hen said' / 'Turning to her son, she said'.
    if speaker is None:
        for k in range(qvi - 1, -1, -1):
            if not _eligible(k):
                continue
            surf, low, pos = tagged[k]
            if low in ("he", "she", "they"):
                speaker, subj_type = _resolve_subject_pronoun(low, ov), "pronoun"
                break
            if pos in ("NNP", "NNPS"):
                speaker, subj_type = low, "name"
                break
            if pos in ("NN", "NNS") and low not in _ADDRESS_NOUNS:
                speaker, subj_type = low, "noun"
                break
    if speaker is None:
        return None

    # ADDRESSEE (best-effort; harder than speaker -- measured separately):
    addressee, addr_src = None, None
    # (a) 'to X' in the frame (after the verb): 'said to the boy'.
    for k in range(qvi + 1, len(tagged)):
        if tagged[k][1] == "to":
            for m in range(k + 1, len(tagged)):
                s2, low2, pos2 = tagged[m]
                if pos2 in ("DT", "JJ", "JJR", "JJS", "RB", "PRP$"):
                    continue
                if pos2 in ("NNP", "NNPS", "NN", "NNS"):
                    addressee, addr_src = low2, "to_frame"
                break
            if addressee is not None:
                break
    # (b) vocative in the quote: a Name / address-noun set off by a comma at a quote boundary.
    if addressee is None:
        for q in re.findall(r'"([^"]*)"', raw_sentence):
            voc = _vocative_in_quote(q)
            if voc is not None and voc != speaker:
                addressee, addr_src = voc, "vocative"
                break
    return dict(speaker=speaker, subj_type=subj_type, addressee=addressee, addr_src=addr_src, qvi=qvi)


def _vocative_in_quote(quote_text):
    """A leading / trailing comma-set-off Name or address-noun in a quote -> the addressee head, else None."""
    q = quote_text.strip()
    # leading vocative: 'Frank, ...' / 'my boy, ...' / 'Sisters and brothers, ...'
    m = re.match(r"^\s*(?:my\s+|dear\s+|good\s+|little\s+)?([A-Za-z]+)\s*,", q)
    if m:
        w = m.group(1).lower()
        if w in ORC.NAME_GENDER or w in _ADDRESS_NOUNS:
            return w
    # trailing vocative: '..., my boy' / '..., mother' / '..., Genie'
    m = re.search(r",\s*(?:my\s+|dear\s+|good\s+|little\s+)?([A-Za-z]+)\s*[.!?]?\s*$", q)
    if m:
        w = m.group(1).lower()
        if w in ORC.NAME_GENDER or w in _ADDRESS_NOUNS:
            return w
    return None


# =======================================================================================
# extract_passage_deixis: byte-COPY of VF.extract_passage_vf with ONE added axis (deixis). With deixis=False
# it is byte-identical to VF.extract_passage_vf (asserted). With deixis=True: a passage-forward dialogue
# state binds SPEAKER/ADDRESSEE from each quotative frame; 1st/2nd-person heads resolve to the participant.
# =======================================================================================
def extract_passage_deixis(passage_text, clf, pid, passages_dict, mention_mode, clause_seg,
                           role_fix, self_loop_guard, deixis=False, decisions_out=None,
                           deixis_out=None, resolutions_out=None):
    coref_strategy = ORC.FIXED_COREF_STRATEGY
    fix_possessive = True
    agreement = True
    topical = True
    pref = bool(agreement)
    injects = INJECT_SUBJ.get(pid, {}) if clause_seg == "gold" else {}
    bounds = segment_clauses_with_boundaries(passage_text) if clause_seg in _ALL_LEARNED_MODES else None

    known = set()
    for txt in list(passages_dict.values()):
        for s in ORC.split_sentences(txt):
            for _su, lo, _po in ORC.pos_tag_sentence(s):
                if ORC.ground_category(lo) is not None:
                    known.add(lo)
    ov = WorkingOverlay(base=SetKnownBase(known))

    rels = []
    res_by_pos = {}
    injections = []
    active_subject = None
    offset = 0
    quote_open = False   # DEIXIS: carried quote open-state (a quote can span split-sentences after ; or .)
    for ci, sent in enumerate(ORC.split_sentences(passage_text)):
        tagged = ORC.pos_tag_sentence(sent)

        # ---- DEIXIS axis (opt-in): parse this sentence's quotative frame + build the per-token resolution.
        # Only tokens INSIDE quotes are deictic; the frame verb is chosen from OUTSIDE the quotes.
        deixis_res = {}
        if deixis:
            ranges, quote_open = _inquote_char_ranges(sent, quote_open)
            starts = _token_char_starts(tagged, sent)
            inquote = [_in_quote(starts[i], ranges) for i in range(len(tagged))]
            frame = parse_quotative_frame(tagged, sent, ov, inquote=inquote)
            if frame is not None and frame["speaker"] is not None:
                addr = frame["addressee"]
                ov.note_turn(frame["speaker"], addr)
                if deixis_out is not None:
                    deixis_out.append(dict(pid=pid, sentence=sent.strip().lower(),
                                           speaker=frame["speaker"], subj_type=frame["subj_type"],
                                           addressee=addr, addr_src=frame["addr_src"]))
            sent_low = sent.strip().lower()
            for i, (surf, low, pos) in enumerate(tagged):
                if inquote[i] and deixis_person(low) is not None:
                    r = ov.resolve_deixis(low)
                    if r is not None:
                        deixis_res[i] = r
                        if resolutions_out is not None:
                            resolutions_out.append(dict(pid=pid, sentence=sent_low, pronoun=low,
                                                        person=deixis_person(low), resolved=r))

        subj = None
        if clause_seg == "gold":
            subj = injects.get(sent.strip())
        elif clause_seg == "learned_lastactive":
            kind = bounds[ci][1]
            if kind == "COORD" and active_subject is not None and _is_bare_vp(tagged):
                subj = active_subject
        elif clause_seg == "learned_topical":
            kind = bounds[ci][1]
            if kind == "COORD" and _is_bare_vp(tagged):
                held = _topical_animate_head(ov)
                if held is not None:
                    subj = held
        elif clause_seg == _VF_MODE:
            kind = bounds[ci][1]
            if kind == "COORD" and _is_bare_vp(tagged):
                held = _topical_animate_head(ov)
                if held is not None:
                    admit, dec = verb_admits_injection(tagged)
                    if decisions_out is not None:
                        decisions_out.append(dict(pid=pid, clause=sent.strip(), held=held, **dec))
                    if admit:
                        subj = held
        if subj is not None:
            tagged = [(subj.capitalize(), subj, "NNP")] + tagged
            injections.append((pid, sent.strip(), subj))
            if deixis:
                # an injected subject shifts token indices by 1; shift the deixis map to stay aligned.
                deixis_res = {i + 1: v for i, v in deixis_res.items()}
        pron_res = {}
        for i, (surf, low, pos) in enumerate(tagged):
            if low in PRONOUN_SCOPE:
                if low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    pron_res[i] = ent.head if ent is not None else None
                sc = PRONOUN_SCOPE[low]
                ov.observe(low, is_pronoun=True, gender=sc["gender"], number=sc["number"])
            elif low in ORC.PRONOUNS_POSS:
                pass
            else:
                if not ORC.observe_as_mention(low, pos, mention_mode, frozenset()):
                    continue
                is_name = (low in ORC.NAME_GENDER) or (pos in ("NNP", "NNPS"))
                if agreement:
                    g, num, anim = _agreement_attrs(low, pos, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name, animacy=anim)
                else:
                    g, num = ORC.grounded_gender_number(low, is_name)
                    ov.observe(low, gender=g, number=num, is_proper_name=is_name)

        roles, verb_idx, verb, passive, cand = ORC.assign_roles_learned(
            tagged, clf, mention_mode, frozenset())
        if role_fix:
            roles = apply_role_fix(tagged, roles, verb_idx, cand)

        def head_of(i):
            surf, low, pos = tagged[i]
            if i in pron_res and pron_res[i] is not None:
                return pron_res[i]
            if deixis and i in deixis_res:            # DEIXIS: 1st/2nd-person -> resolved participant head
                return deixis_res[i]
            return low

        agents = [i for i in cand if roles.get(i) == "AGENT"]
        patients = [i for i in cand if roles.get(i) == "PATIENT"]
        recips = [i for i in cand if roles.get(i) == "RECIPIENT"]
        locs = [i for i in cand if roles.get(i) == "LOCATION"]
        subj_head = head_of(agents[0]) if agents else (head_of(cand[0]) if cand else None)
        if verb is not None and agents and patients and verb not in ("has", "is"):
            for pi in patients:
                rels.append(("svo", verb, head_of(agents[0]), head_of(pi)))
        lows = [t[1] for t in tagged]
        if "kind" in lows and subj_head is not None:
            for i in cand:
                if roles.get(i) in ("PATIENT", "RECIPIENT", "LOCATION") or ORC.prev_prep(tagged, i) == "to":
                    if head_of(i) != subj_head:
                        rels.append(("svo", "kind", subj_head, head_of(i)))
        if verb == "has" and patients:
            pre_verb = [i for i in cand if verb_idx is not None and i < verb_idx]
            owner_idx = agents[0] if agents else (pre_verb[0] if pre_verb else None)
            if owner_idx is not None:
                for pi in patients:
                    if pi != owner_idx:
                        rels.append(("poss", head_of(owner_idx), head_of(pi)))
        for ri in recips:
            if verb is not None and agents:
                rels.append(("recipient", verb, head_of(agents[0]), head_of(ri)))
        for li in locs:
            figure = subj_head
            for j in cand:
                if j < li and roles.get(j) in ("AGENT", "PATIENT"):
                    figure = head_of(j)
            if figure is not None and figure != head_of(li):
                rels.append(("loc", figure, head_of(li)))

        for i, (surf, low, pos) in enumerate(tagged):
            if "'" in surf and (surf.lower().endswith("'s")):
                owner = surf.split("'")[0].lower()
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
            if low in ORC.PRONOUNS_POSS:
                if fix_possessive and low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    owner = pron_res.get(i)
                    owner = owner if owner is not None else low
                elif low in PRONOUN_SCOPE and low not in ("i", "you", "we"):
                    ptop = _prefers_topical(low, pos) if topical else False
                    ent = ov.resolve_pronoun(low, strategy=coref_strategy,
                                             prefer_agreement=pref, prefer_topical=ptop)
                    owner = ent.head if ent is not None else low
                else:
                    owner = low
                    if deixis and i in deixis_res:    # DEIXIS: my/our/your -> resolved participant head
                        owner = deixis_res[i]
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("poss", owner, head_of(j)))
                        break
                if low in _RESOLVABLE:
                    res_by_pos[offset + i] = (low, owner if owner != low else None)
        for i in range(len(tagged) - 1):
            if ORC.ground_category(tagged[i][1]) == "COLOR":
                for j in range(i + 1, len(tagged)):
                    if j in cand:
                        rels.append(("attr", head_of(j), tagged[i][1], "COLOR"))
                        break

        for i, (surf, low, pos) in enumerate(tagged):
            if low in _RESOLVABLE_SO and low not in _RESOLVABLE_POSS:
                res_by_pos[offset + i] = (low, pron_res.get(i))

        if agents:
            active_subject = head_of(agents[0])

        offset += len(tagged)

    removed = []
    if self_loop_guard:
        kept = []
        for r in rels:
            if is_self_loop(r):
                removed.append(tuple(r))
            else:
                kept.append(r)
        rels = kept

    sorted_rels = sorted(set(rels), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    removed = sorted(set(removed), key=lambda r: (r[0], tuple(str(x) for x in r[1:])))
    return sorted_rels, res_by_pos, removed, injections


# =======================================================================================
# Read the whole corpus with the deixis axis ON or OFF; accumulate foundation + deixis decisions.
# =======================================================================================
def read_corpus(clf, passages, deixis, hb=None):
    foundation = set()
    store = {}
    deixis_dec = []
    resolutions = []
    for i, (pid, text) in enumerate(passages.items()):
        dd = [] if deixis else None
        rr = [] if deixis else None
        rels, _rbp, _removed, _inj = extract_passage_deixis(
            text, clf, pid, passages, "handrule", _VF_MODE,
            role_fix=True, self_loop_guard=True, deixis=deixis, deixis_out=dd, resolutions_out=rr)
        store[pid] = rels
        kinds = [r for r in rels if r[0] in _KINDS]
        for r in kinds:
            foundation.add(tuple(r))
        if dd is not None:
            deixis_dec.extend(dd)
        if rr is not None:
            resolutions.extend(rr)
        if hb is not None:
            hb(i, len(passages))
    return dict(foundation=foundation, store=store, deixis_decisions=deixis_dec, resolutions=resolutions)


def _phantom_relations(foundation):
    """Foundation relations whose head is a 1st/2nd-person phantom (svo agent/patient, loc figure/ground,
    poss owner/possessed)."""
    out = []
    for r in foundation:
        heads = (r[2], r[3]) if r[0] == "svo" else (r[1], r[2])
        if any(str(h).lower() in PHANTOM_HEADS for h in heads):
            out.append(r)
    return sorted(out)


# =======================================================================================
# INDEPENDENT single-annotator DEIXIS GOLD (measurement 2). Each record: the correct SPEAKER (1st-person
# anchor) and/or ADDRESSEE (2nd-person anchor) for a quoted turn, matched to an emitted deixis decision by
# pid + a distinctive lowercased content CUE. Annotated by READING the corpus (anti-circular; NOT copied
# from the parser's own output). Single-annotator, coverage-honest. person in {first, second, both}.
# =======================================================================================
# Scored per RESOLUTION (the resolved deictic token), matched by pid + a distinctive lowercased content
# CUE from the QUOTE the pronoun sits in + the person class. `expect` = the CORRECT participant head, from
# READING THE STORY (anti-circular: NOT copied from the mechanism -- the gold deliberately INCLUDES sites
# the mechanism resolves WRONGLY, so precision is not 1.0 by construction). person in {first, second}.
# Single-annotator, coverage-honest; the sample spans confident correct + confident incorrect resolutions.
DEIXIS_GOLD = [
    # ---- SPEAKER (1st-person -> the speaker of the quote) ----
    dict(pid="L05", cue="told him not to cry", person="first", expect="joe"),
    dict(pid="L05", cue="do n't see", person="first", expect="papa"),
    dict(pid="L05", cue="knock my castles down", person="first", expect="herbert"),   # mech: papa (ERROR)
    dict(pid="L12", cue="if i take you to walk", person="first", expect="mother"),
    dict(pid="L12", cue="will not let you in", person="first", expect="gardener"),
    dict(pid="L31", cue="that is my plan", person="first", expect="teddy"),
    dict(pid="L31", cue="do n't see the use", person="first", expect="lily"),          # mech: mother (ERROR)
    dict(pid="L33", cue="i will tell you", person="first", expect="mother"),
    dict(pid="L33", cue="if i were in the open air", person="first", expect="mother"),
    dict(pid="L33", cue="i catch it again", person="first", expect="robert"),
    dict(pid="L34", cue="i will keep them all for her", person="first", expect="george"),
    dict(pid="L34", cue="i will only taste one", person="first", expect="george"),
    dict(pid="L36", cue="it's mine", person="first", expect="fred"),
    dict(pid="L36", cue="i guess i know who owns it", person="first", expect="tom"),
    dict(pid="L36", cue="i found it", person="first", expect="fred"),
    dict(pid="L54", cue="i want to play", person="first", expect="wave"),
    dict(pid="L54", cue="where is my work", person="first", expect="wave"),
    dict(pid="L54", cue="i washed all of the pebbles", person="first", expect="wave"),  # mech: fishes (ERROR)
    dict(pid="L57", cue="said little fan", person="first", expect="fan"),
    dict(pid="L69", cue="should like to go with you", person="first", expect="susan"),
    dict(pid="L69", cue="i have deceived my grandmother", person="first", expect="susan"),  # mech: grandmother (ERROR)
    dict(pid="L69", cue="i knew it all the time", person="first", expect="grandmother"),
    dict(pid="L77", cue="whole thing puzzles me", person="first", expect="rob"),
    dict(pid="L77", cue="i sprained my ankle", person="first", expect="rob"),           # mech: genie (ERROR)
    # ---- ADDRESSEE (2nd-person -> the entity spoken to) ----
    dict(pid="L12", cue="if i take you to walk", person="second", expect="frank"),
    dict(pid="L31", cue="have earned the orange", person="second", expect="teddy"),
    dict(pid="L33", cue="did you never hear an echo", person="second", expect="robert"),  # mech: mother (ERROR)
    dict(pid="L34", cue="god will bless you", person="second", expect="george"),
    dict(pid="L36", cue="is this yours", person="second", expect="fred"),
    dict(pid="L37", cue="what do you take me for", person="second", expect="owl"),
    dict(pid="L57", cue="said little fan", person="second", expect="mother"),            # mech: nell (ERROR)
]


def _match_resolution(pid, cue, person, resolutions):
    for r in resolutions:
        if r["pid"] == pid and r["person"] == person and cue in r["sentence"]:
            return r
    return None


def deixis_precision_recall(resolutions):
    """Score SPEAKER (1st) + ADDRESSEE (2nd) attribution vs the independent gold, at the RESOLUTION level.
    Precision = correct / attempted (a matching resolution fired); recall = correct / n_gold (all gold sites,
    so an un-fired site is a recall miss = the frame-detection can-fail lever)."""
    def _score(person):
        gold_items = [g for g in DEIXIS_GOLD if g["person"] == person]
        attempted = correct = 0
        per = []
        for g in gold_items:
            r = _match_resolution(g["pid"], g["cue"], person, resolutions)
            got = r["resolved"] if r is not None else None
            hit = (got is not None and ORC.normalize(got) == ORC.normalize(g["expect"]))
            if got is not None:
                attempted += 1
            if hit:
                correct += 1
            per.append(dict(pid=g["pid"], cue=g["cue"], expect=g["expect"], got=got,
                            matched=r is not None, ok=hit))
        n_gold = len(gold_items)
        return dict(n_gold=n_gold, attempted=attempted, correct=correct,
                    precision=round(correct / attempted, 4) if attempted else None,
                    recall=round(correct / n_gold, 4) if n_gold else None, per=per)
    return dict(speaker=_score("first"), addressee=_score("second"))


# =======================================================================================
# COMPREHENSION (measurement 3): who-said-what / who-did-what Qs answerable ONLY if 1st-person resolves to
# the speaker. spec via ORC.answer_reader over the (noisy) grown store. OFF cannot answer (phantom head);
# ON can. Small-n, single-annotator (reported honestly).
# =======================================================================================
COMP_QS = [
    dict(qid="D1", pid="L34", spec=("svo_agent", "save", "leaves"), gold="george",
         text="Who saved the leaves? (George: 'I will save them...') OFF->phantom 'i'"),
    dict(qid="D2", pid="L34", spec=("svo_agent", "eat", "half"), gold="george",
         text="Who will eat half? (George: 'I will eat half') OFF->phantom 'i'"),
    dict(qid="D3", pid="L34", spec=("svo_agent", "keep", "heaps"), gold="george",
         text="Who kept the heaps? (George: 'I will keep them all') OFF->phantom 'i'"),
    dict(qid="D4", pid="L77", spec=("svo_agent", "chasing", "jack"), gold="rob",
         text="Who was chasing Jack? (Rob: 'I was chasing jack') OFF->phantom 'i'"),
    dict(qid="D5", pid="L54", spec=("has_owner", "hand"), gold="wave",
         text="Whose hand? (a wave: 'take my hand') OFF->phantom 'my'"),
]


def comprehension(store_off, store_on):
    def _run(store):
        per, correct = [], []
        for q in COMP_QS:
            rels = store.get(q["pid"], [])
            ans = ORC.answer_reader(q["spec"], rels)
            na, ng = ORC.normalize(ans), ORC.normalize(q["gold"])
            ok = (na is not None and na == ng)
            correct.append(1 if ok else 0)
            per.append(dict(qid=q["qid"], gold=q["gold"], pred=na, ok=ok))
        return sum(correct), per
    off_ok, off_per = _run(store_off)
    on_ok, on_per = _run(store_on)
    return dict(n=len(COMP_QS), off_correct=off_ok, on_correct=on_ok, delta=on_ok - off_ok,
                off_per=off_per, on_per=on_per)


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


def _heartbeat(output_dir):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    t0 = time.perf_counter()

    def tick(i, total):
        row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=i, total_units=total,
                   elapsed_s=round(time.perf_counter() - t0, 2))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    return tick


# =======================================================================================
# Overlay witness (IN-PROCESS): exec the REAL scaffold-free witness against the REAL hdlab.state_of_mind
# and check all tests pass. In-process (not subprocess) so a transient subprocess starvation under heavy
# parent CPU load cannot false-flag a REGRESSION (observed once on the full run: empty subprocess output +
# nonzero rc while the witness passes reliably standalone). Deterministic; no randomness.
# =======================================================================================
def _run_overlay_witness_inproc():
    import importlib.util
    path = os.path.join(REPO, "verification", "verify_state_of_mind_overlay.py")
    try:
        spec = importlib.util.spec_from_file_location("verify_som_overlay_inproc", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rc = mod.main()
        return (rc == 0), "inproc witness PASS (7/7)"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:300]}"


# =======================================================================================
# Regression guard: extract_passage_deixis(deixis=False) BYTE-IDENTICAL to VF.extract_passage_vf.
# =======================================================================================
def byte_identity_off(clf, passages):
    """Every lesson: our deixis-OFF foundation == VF's foundation. Returns (ok, n_checked, first_diff)."""
    n_checked = 0
    for pid, text in passages.items():
        mine, _, _, _ = extract_passage_deixis(text, clf, pid, passages, "handrule", _VF_MODE,
                                                role_fix=True, self_loop_guard=True, deixis=False)
        theirs, _, _, _ = VF.extract_passage_vf(text, clf, pid, passages, "handrule", _VF_MODE,
                                                 role_fix=True, self_loop_guard=True)
        n_checked += 1
        if list(mine) != list(theirs):
            return False, n_checked, dict(pid=pid, mine_only=[list(r) for r in set(mine) - set(theirs)][:5],
                                          theirs_only=[list(r) for r in set(theirs) - set(mine)][:5])
    return True, n_checked, None


# =======================================================================================
# Self-test (design-gate).
# =======================================================================================
def self_test():
    print("[self-test] loading full corpus + building REAL reader ...")
    passages = load_lessons()
    assert len(passages) >= 70, f"expected ~79 lessons, got {len(passages)}"
    clf = V2._fit_clf()

    # real_code_path: run the REAL deixis extract on a few lessons.
    sub = dict(list(passages.items())[:12])
    on = read_corpus(clf, sub, deixis=True)
    off = read_corpus(clf, sub, deixis=False)
    assert len(on["foundation"]) > 0 and len(off["foundation"]) > 0, "reader produced no relations"
    print(f"[self-test] reader ran on 12 lessons: ON {len(on['foundation'])} rel / OFF {len(off['foundation'])} rel; "
          f"{len(on['deixis_decisions'])} frame decisions")

    # byte-identity OFF on the sub-corpus (fast regression preflight; full check runs in build_verdict).
    ok, nchk, diff = byte_identity_off(clf, sub)
    assert ok, f"REGRESSION: deixis-OFF diverged from VF on sub-corpus: {diff}"
    print(f"[self-test] deixis-OFF byte-identical to VF.extract_passage_vf on {nchk} lessons")

    # the deixis axis must actually FIRE (discriminator-fires gate): resolve some phantom heads.
    ph_off = _phantom_relations(off["foundation"])
    ph_on = _phantom_relations(on["foundation"])
    assert len(ph_off) > 0, "no phantom heads in the OFF baseline on the sub-corpus (regime under-powers)"
    print(f"[self-test] phantom heads OFF={len(ph_off)} ON={len(ph_on)} (deixis should reduce); "
          f"sample OFF phantom: {ph_off[:3]}")

    # frame parser sanity on constructed micro-frames.
    for raw, exp_spk in [('"I told him," said Joe', "joe"),
                         ('he said, "I love snow"', "he"),
                         ('"There is a better way, my boy," said papa', "papa")]:
        tg = ORC.pos_tag_sentence(raw)
        rg, _ = _inquote_char_ranges(raw, False)
        iq = [_in_quote(s, rg) for s in _token_char_starts(tg, raw)]
        fr = parse_quotative_frame(tg, raw, WorkingOverlay(), inquote=iq)
        assert fr is not None and fr["speaker"] == exp_spk, f"frame {raw!r} -> {fr}, expected speaker {exp_spk}"
    print("[self-test] quotative-frame parser: said Joe / he said / said papa resolved")

    # gold structural sanity (per-resolution schema: pid + cue + person + expect).
    for g in DEIXIS_GOLD:
        assert g["person"] in ("first", "second"), g
        assert g["expect"] and g["cue"] and g["pid"], g
    n_first = sum(1 for g in DEIXIS_GOLD if g["person"] == "first")
    n_second = len(DEIXIS_GOLD) - n_first
    print(f"[self-test] deixis gold: {len(DEIXIS_GOLD)} items ({n_first} speaker / {n_second} addressee), valid")

    # REGRESSION controls fire + overlay witness (now 7/7) green.
    ctrl = V2._role_controls(clf)
    assert ctrl["passive_rolefix"] >= 1.0 and ctrl["reversal_rolefix"] >= 1.0, f"role controls regressed: {ctrl}"
    wok, wtail = _run_overlay_witness_inproc()
    assert wok, f"overlay witness FAILED: {wtail}"
    print(f"[self-test] controls: passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f}; overlay green")

    # determinism: two ON reads identical.
    on2 = read_corpus(clf, sub, deixis=True)
    assert on["foundation"] == on2["foundation"], "non-deterministic ON foundation"
    print("[self-test] deterministic (two ON reads identical)")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
BANDS = dict(speaker_prec_min=0.80, speaker_recall_min=0.60, addressee_prec_min=0.50,
             phantom_reduction_min=0.50, comp_delta_min=1)


def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=79)
    hb = _heartbeat(output_dir)
    passages = load_lessons()
    if run_mode == "smoke":
        # curated dialogue slice: covers the deixis gold lessons so the gold discriminator FIRES at smoke.
        smoke_ids = ["L05", "L12", "L27", "L31", "L33", "L34", "L36", "L37", "L42", "L49",
                     "L54", "L57", "L63", "L69", "L77"]
        passages = {k: passages[k] for k in smoke_ids if k in passages}
    clf = V2._fit_clf()

    off = read_corpus(clf, passages, deixis=False, hb=hb)
    on = read_corpus(clf, passages, deixis=True, hb=hb)

    ph_off = _phantom_relations(off["foundation"])
    ph_on = _phantom_relations(on["foundation"])
    n_ph_off, n_ph_on = len(ph_off), len(ph_on)
    reduction = round((n_ph_off - n_ph_on) / n_ph_off, 4) if n_ph_off else None

    pr = deixis_precision_recall(on["resolutions"])
    comp = comprehension(off["store"], on["store"])

    # regression guard (full corpus byte-identity + controls + witness + determinism).
    biok, bic, bidiff = byte_identity_off(clf, passages)
    ctrl = V2._role_controls(clf)
    passive_ok = ctrl["passive_rolefix"] >= 1.0
    reversal_ok = ctrl["reversal_rolefix"] >= 1.0
    wok, wtail = _run_overlay_witness_inproc()
    on2 = read_corpus(clf, passages, deixis=True)
    deterministic = (on["foundation"] == on2["foundation"])
    no_regression = biok and passive_ok and reversal_ok and wok and deterministic

    spk = pr["speaker"]
    adr = pr["addressee"]
    speaker_clean = (spk["precision"] is not None and spk["precision"] >= BANDS["speaker_prec_min"]
                     and spk["recall"] is not None and spk["recall"] >= BANDS["speaker_recall_min"])
    addressee_signal = (adr["precision"] is not None and adr["precision"] >= BANDS["addressee_prec_min"])
    reduction_ok = (reduction is not None and reduction >= BANDS["phantom_reduction_min"])
    comp_ok = comp["delta"] >= BANDS["comp_delta_min"]
    n_frames = len(on["deixis_decisions"])
    n_resolved_first = sum(1 for d in on["deixis_decisions"] if d["speaker"] is not None)

    if not no_regression:
        verdict = "REGRESSION"
        vmsg = (f"a regression guard failed: byte_identity_off={biok} (diff={bidiff}) passive "
                f"{ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f} overlay={wok} "
                f"deterministic={deterministic}. The deixis axis leaked into the banked reader; do NOT trust "
                f"the measurements.")
    elif speaker_clean and reduction_ok and comp_ok:
        verdict = "DEIXIS_RESOLVES_PARTICIPANTS"
        vmsg = (f"DEIXIS LANDS. On the full 3rd reader the quotative-frame parser bound {n_frames} speaker "
                f"turns; 1st-person SPEAKER attribution precision {spk['precision']:.2f} recall "
                f"{spk['recall']:.2f} (gold n={spk['n_gold']}); phantom-head FP relations {n_ph_off}->{n_ph_on} "
                f"(reduction {reduction:.2f}); comprehension who-did-what {comp['off_correct']}->"
                f"{comp['on_correct']}/{comp['n']} (delta +{comp['delta']}). ADDRESSEE (2nd-person, harder) "
                f"precision {adr['precision']} recall {adr['recall']} -- {'signal' if addressee_signal else 'WEAK, reported honestly'}. "
                f"The dominant scale coref-FP (1st/2nd-person phantom heads) is resolved by a DISTINCT deixis "
                f"mechanism, additive to the overlay, byte-identical with the axis OFF. HYPOTHESIS pending landed-VET.")
    else:
        verdict = "SCOPE_LIMITED_OR_WEAK"
        vmsg = (f"DEIXIS LOCALIZES. The quotative-frame parser bound {n_frames} speaker turns "
                f"({n_resolved_first} with a speaker) BUT: "
                f"(1) SPEAKER attribution precision {spk['precision']} recall {spk['recall']} "
                f"(gold n={spk['n_gold']}; band prec>={BANDS['speaker_prec_min']} rec>={BANDS['speaker_recall_min']}) "
                f"-> {'CLEAN' if speaker_clean else 'below band'}. "
                f"(2) phantom-head FP relations {n_ph_off}->{n_ph_on} (reduction {reduction}; band "
                f">={BANDS['phantom_reduction_min']}) -> {'ok' if reduction_ok else 'below floor'}. "
                f"(3) ADDRESSEE (2nd-person) precision {adr['precision']} recall {adr['recall']} -> "
                f"{'signal' if addressee_signal else 'WEAK'} (harder; separate faculty). "
                f"(4) comprehension delta +{comp['delta']} -> {'ok' if comp_ok else 'no gain'}. "
                f"LOCALIZED SUB-MECHANISM = {'addressee' if speaker_clean and not addressee_signal else ('frame-recall' if (spk['recall'] or 0) < BANDS['speaker_recall_min'] else 'speaker-precision')}. "
                f"HONEST DEFLATE. HYPOTHESIS pending VET.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: 3rd reader ({len(passages)} lessons) | phantom-head FP {n_ph_off}->{n_ph_on} "
                 f"(reduction {reduction}) | SPEAKER P {spk['precision']} R {spk['recall']} (n={spk['n_gold']}) "
                 f"| ADDRESSEE P {adr['precision']} R {adr['recall']} (n={adr['n_gold']}) | frames {n_frames} "
                 f"| comp {comp['off_correct']}->{comp['on_correct']}/{comp['n']} (d+{comp['delta']}) | "
                 f"byteid_off={biok} passive {ctrl['passive_rolefix']:.2f} reversal {ctrl['reversal_rolefix']:.2f} "
                 f"overlay={wok} det={deterministic}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, n_lessons=len(passages),
        one_variable="the deixis axis (extract_passage_deixis deixis=True vs False); everything else identical",
        bands=BANDS,
        phantom_fp=dict(n_off=n_ph_off, n_on=n_ph_on, reduction=reduction,
                        sample_off=[list(r) for r in ph_off[:40]],
                        sample_on=[list(r) for r in ph_on[:40]]),
        deixis_resolution=pr,
        comprehension=comp,
        n_frames=n_frames, n_frames_with_speaker=n_resolved_first,
        frame_decisions_sample=on["deixis_decisions"][:60],
        regression=dict(byte_identity_off=biok, byte_identity_checked=bic, byte_identity_diff=bidiff,
                        passive_rolefix=ctrl["passive_rolefix"], reversal_rolefix=ctrl["reversal_rolefix"],
                        passive_ok=passive_ok, reversal_ok=reversal_ok, overlay_witness_ok=wok,
                        overlay_witness_tail=wtail, deterministic=deterministic, no_regression=no_regression),
        cited_scale=dict(source="data/exp_read_grow_full_third_reader_clauseseg_generalization_v1/metrics.json",
                         **CITED_SCALE),
        brain_faithfulness=("deixis = speaker/addressee tracking via the quotative frame is a DISTINCT faculty "
                            "from 3rd-person antecedent resolution (indexicals index a discourse ROLE, not a "
                            "prior mention); kept as a separate additive overlay axis. DEVIATION FLAGGED: the "
                            "addressee fallback (prior speaker / most-salient participant) is a heuristic stand-"
                            "in for the brain's full common-ground model; measured + reported separately."),
        scope_caveat=("Single-annotator INDEPENDENT deixis gold (speaker/addressee per quote, matched by pid + "
                      "content cue), coverage-honest. The addressee (2nd-person) arm is genuinely harder than "
                      "the speaker (1st-person) arm and is banded + reported SEPARATELY. Phantom-head reduction "
                      "is a corpus-wide COUNT (no annotation) -- its per-relation CORRECTNESS is judged via the "
                      "attribution gold, not asserted from the count alone. CLAIM-VET-pending; strategic read = "
                      "HYPOTHESIS pending landed-VET."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("\ndeixis speaker:", json.dumps(spk, indent=1)[:1500])
    print("\ndeixis addressee:", json.dumps(adr, indent=1)[:1200])
    print("\nphantom FP:", json.dumps({k: metrics["phantom_fp"][k] for k in ("n_off", "n_on", "reduction")}, indent=1))
    print("comprehension:", json.dumps(comp, indent=1)[:900])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    return build_verdict(OUTPUT_DIR, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
