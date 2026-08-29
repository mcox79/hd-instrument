"""idiom_gate_expand_v1 -- EXPAND the glass-box idiom / non-compositional-MWE foundation at scale.

WHY (brain mechanism): the mental lexicon stores non-compositional multiword expressions as UNITS and
retrieves the stored coarse event-frame holistically, BEFORE literal word-by-word composition (Cutting
& Bock 1997; Jackendoff's construction lexicon). Open-class idioms ("go bad", "come to a decision",
"carry out", "give up", "take on", "put off", institutional "pass a law" / "hold office") are the
residual that CAPS a compositional verb-sense disambiguator, because the non-compositionality is
LEXICALISED, not structural. So we store them as units and read the stored frame directly. NO LLM --
a static, committed data asset (the runtime lookup is a dict get in idiom_gate.idiom_sense).

WHAT THIS BUILDER ADDS ON TOP OF experiments/idiom_gate.py's asset (1813 phrasal + 414 vobj):
  PHRASAL -- WordNet already covers ~91% of canonical common English phrasal verbs (measured:
    263/289), so the phrasal space is near-saturated. We ADD a curated table of the genuinely-missing
    common phrasal verbs + the CLEAN corpus-mined (verb, prt) satellites (spaCy dep 'prt') that
    WordNet lacks, each hand-mapped to a coarse frame. (We never invent a frame for a mined pair we
    cannot justify -- WordNet-frame-where-it-exists, else curated; precision over recall.)
  VERB+OBJECT -- the real growth surface. Two mechanisms, precision-first:
    (b') a FREQUENCY-gated STRICT-OBJECT miner. KEY INSIGHT: light-verb MWEs ("take place", "make a
         decision") have LOW PMI because both tokens are ultra-frequent, so a pure PMI gate REJECTS
         them (the original builder's PMI gate added only 5 vobj). We therefore harvest attested
         (light_verb, institutional_object) direct-object bigrams by FREQUENCY, admitting a pair ONLY
         when (i) the verb is a bleached light/motion/contact verb, (ii) the object is in an
         UNAMBIGUOUS institutional/abstract object table (object alone fixes an institutional frame:
         social / communication / cognition / stative / competition), and (iii) that frame DIFFERS
         from the verb's WordNet-dominant frame (fr != dom -> the phrase is non-literal). Ambiguous
         objects (place / part / role / charge / sense / power / control / office / trial ...) are
         DELIBERATELY EXCLUDED from the object table and handled only via verb-specific curated pairs,
         so literal reads ("reach a place", "give charge") are never admitted.
    (a)  the original PMI + WordNet-verb_noun gate (kept): a high-PMI (v,o) whose dedicated WordNet
         'verb_noun' sense has a frame differing from the verb's dominant frame.
  A large hand-vetted CURATED_VOBJ_EXPAND overlay (light-verb collocations justified by their attested
  corpus frequencies) is applied LAST as the authoritative source for the clearest cases.

MERGE POLICY (non-destructive): every existing entry is PRESERVED with its existing frame; we only ADD
keys that are absent. Curated overrides MINED for a shared NEW key, but never overrides an existing
entry. The schema is unchanged ({"meta","phrasal","vobj"} keyed "verb|particle" / "verb|objecthead" ->
coarse frame) so experiments/idiom_gate.py loads the expanded asset with no code change. The pre-
expansion counts are recorded in meta.backup_pre_expansion.

Guards a missing corpus: the curated tables alone still expand the asset (mining is skipped). spaCy /
nltk import INLINE. ASCII only. Atomic write. No hdlab writes. No preregs.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the base module's frame inventory, WordNet helpers, atomic write, and paths (single source of
# truth; keeps the schema/loader identical).
from experiments import idiom_gate as IG  # noqa: E402
from experiments.idiom_gate import (  # noqa: E402
    COARSE_FRAMES, _FRAMESET, lexname_to_frame, _verb_dominant_frame, _lemma_sense_frame,
    _atomic_write_json, idiom_sense,
)

_ASSET_PATH = IG._ASSET_PATH
_CORPUS_DEFAULT = IG._CORPUS_DEFAULT

# ---------------------------------------------------------------------------
# (b') STRICT institutional/abstract object -> coarse frame. The OBJECT ALONE robustly fixes the frame
# regardless of which bleached light verb governs it. AMBIGUOUS objects whose frame flips by verb
# (place, part, role, charge, sense, power, control, office, trial, threat, claim, point, effect, care,
# step, action, shape ...) are OMITTED here and handled by verb-specific CURATED_VOBJ_EXPAND, so
# literal reads ("reach a place", "give charge", "make a shape") are never admitted by the miner.
# ---------------------------------------------------------------------------
OBJ2FRAME_STRICT: Dict[str, str] = {
    # governance / legislation / institutional events / ballots (social)
    "law": "social", "bill": "social", "legislation": "social", "statute": "social",
    "ordinance": "social", "amendment": "social", "referendum": "social", "election": "social",
    "ballot": "social", "veto": "social", "treaty": "social", "alliance": "social",
    "truce": "social", "ceasefire": "social", "armistice": "social", "pact": "social",
    "sanction": "social", "coup": "social", "meeting": "social",
    "ceremony": "social", "inauguration": "social",
    "coronation": "social", "vote": "social", "presidency": "social",
    "throne": "social",
    # NOTE: hearing / summit / rally / conference are DELIBERATELY EXCLUDED from the object-only table
    # -- each has a common non-institutional homonym a light verb can take literally ("reach the
    # summit" of a mountain, "lose hearing", "win a rally/conference"). Their institutional (social)
    # sense is captured precisely by the verb-specific curated pairs hold|hearing / hold|summit /
    # hold|rally / hold|conference instead.
    # speech acts -- the object denotes an utterance (communication)
    "speech": "communication", "lecture": "communication", "sermon": "communication",
    "announcement": "communication", "declaration": "communication", "proclamation": "communication",
    "statement": "communication", "question": "communication", "query": "communication",
    "inquiry": "communication", "complaint": "communication", "objection": "communication",
    "accusation": "communication", "allegation": "communication", "criticism": "communication",
    "promise": "communication", "pledge": "communication", "vow": "communication",
    "oath": "communication", "apology": "communication", "confession": "communication",
    "suggestion": "communication", "proposal": "communication", "recommendation": "communication",
    "remark": "communication", "comment": "communication", "argument": "communication",
    # mental acts (cognition)
    "decision": "cognition", "conclusion": "cognition", "judgment": "cognition",
    "judgement": "cognition", "verdict": "cognition", "assessment": "cognition",
    "evaluation": "cognition", "calculation": "cognition", "estimate": "cognition",
    "assumption": "cognition", "inference": "cognition", "deduction": "cognition",
    "hypothesis": "cognition", "mistake": "cognition", "error": "cognition", "blunder": "cognition",
    "guess": "cognition", "choice": "cognition", "attention": "cognition", "comparison": "cognition",
    "distinction": "cognition",
    # armed conflict (competition)
    "war": "competition", "battle": "competition", "combat": "competition", "duel": "competition",
}

# Bleached light / motion / contact verbs eligible for the strict-object frequency gate. Their literal
# frame is NOT the phrase's frame (a "take" in "take office" is not possession, "pass" in "pass a law"
# is not motion). The fr != dom check is what filters the literal reads.
LIGHT: set = {"make", "take", "give", "hold", "pass", "carry", "put", "come", "go", "break", "run",
              "turn", "call", "win", "lose", "wage", "declare", "veto", "sign", "bring", "stand",
              "draw", "reach", "pay", "cast", "raise", "pose", "seize", "gain", "deliver", "launch",
              "mount", "stage"}

# ---------------------------------------------------------------------------
# Authoritative hand-vetted VERB+OBJECT collocations (each justified by its attested corpus frequency;
# includes the verb-specific / ambiguous-object cases the strict miner deliberately omits). Applied
# LAST; adds only keys ABSENT from the existing asset (never overrides an existing frame). Every value
# is in COARSE_FRAMES.
# ---------------------------------------------------------------------------
CURATED_VOBJ_EXPAND: Dict[str, str] = {
    # --- cognition (decisions / judgments / mental acts) ---
    "make|decision": "cognition", "take|decision": "cognition", "reach|decision": "cognition",
    "come|decision": "cognition", "arrive|decision": "cognition", "make|sense": "cognition",
    "take|note": "cognition", "take|account": "cognition", "bear|mind": "cognition",
    "keep|mind": "cognition", "make|mistake": "cognition", "make|error": "cognition",
    "reach|conclusion": "cognition", "draw|conclusion": "cognition", "come|conclusion": "cognition",
    "form|opinion": "cognition", "hold|opinion": "cognition", "take|view": "cognition",
    "form|view": "cognition", "change|mind": "cognition", "make|guess": "cognition",
    "hazard|guess": "cognition", "make|choice": "cognition", "make|assessment": "cognition",
    "make|calculation": "cognition", "take|stock": "cognition", "make|judgment": "cognition",
    "pass|judgment": "cognition", "reach|verdict": "cognition", "make|comparison": "cognition",
    "draw|comparison": "cognition", "draw|distinction": "cognition", "make|distinction": "cognition",
    "reach|agreement": "cognition", "come|agreement": "cognition", "make|plan": "cognition",
    "pay|attention": "cognition",
    # --- communication (speech acts) ---
    "make|point": "communication", "prove|point": "communication", "make|case": "communication",
    "state|case": "communication", "make|argument": "communication", "give|speech": "communication",
    "deliver|speech": "communication", "make|speech": "communication", "give|talk": "communication",
    "give|lecture": "communication", "deliver|lecture": "communication",
    "give|address": "communication", "deliver|address": "communication",
    "make|statement": "communication", "issue|statement": "communication",
    "make|announcement": "communication", "make|remark": "communication",
    "pass|comment": "communication", "make|comment": "communication",
    "raise|question": "communication", "pose|question": "communication",
    "put|question": "communication", "raise|issue": "communication", "raise|objection": "communication",
    "raise|point": "communication", "make|promise": "communication", "break|promise": "communication",
    "give|warning": "communication", "issue|warning": "communication", "sound|warning": "communication",
    "make|threat": "communication", "give|order": "communication", "issue|order": "communication",
    "make|offer": "communication", "make|request": "communication", "make|demand": "communication",
    "make|complaint": "communication", "lodge|complaint": "communication",
    "file|complaint": "communication", "make|apology": "communication", "offer|apology": "communication",
    "make|confession": "communication", "make|excuse": "communication", "give|excuse": "communication",
    "make|suggestion": "communication", "make|proposal": "communication", "put|proposal": "communication",
    "make|claim": "communication", "give|account": "communication", "give|report": "communication",
    "tell|joke": "communication", "crack|joke": "communication", "make|joke": "communication",
    "tell|story": "communication", "say|prayer": "communication", "offer|prayer": "communication",
    "raise|alarm": "communication", "sound|alarm": "communication",
    # --- social (governance / institutions / collective + participatory action) ---
    "pass|law": "social", "pass|bill": "social", "pass|act": "social", "pass|legislation": "social",
    "pass|resolution": "social", "pass|amendment": "social", "pass|motion": "social",
    "pass|ordinance": "social", "pass|statute": "social", "sign|bill": "social", "sign|law": "social",
    "sign|treaty": "social", "sign|pact": "social", "sign|agreement": "social", "veto|bill": "social",
    "enact|law": "social", "hold|election": "social", "hold|meeting": "social", "hold|vote": "social",
    "hold|referendum": "social", "hold|hearing": "social", "hold|session": "social",
    "hold|conference": "social", "hold|ceremony": "social", "hold|summit": "social",
    "hold|talk": "social", "hold|rally": "social", "hold|office": "social", "take|office": "social",
    "run|office": "social", "take|part": "social", "take|control": "social", "take|charge": "social",
    "take|command": "social", "take|power": "social", "seize|power": "social", "seize|control": "social",
    "assume|control": "social", "assume|power": "social", "hold|power": "social", "gain|control": "social",
    "lose|control": "social", "give|control": "social", "take|action": "social", "take|measure": "social",
    "take|step": "social", "take|initiative": "social", "take|responsibility": "social",
    "take|blame": "social", "take|credit": "social", "take|lead": "social", "take|side": "social",
    "take|stand": "social", "take|oath": "social", "make|peace": "social", "sign|peace": "social",
    "keep|peace": "social", "bring|peace": "social", "stage|coup": "social", "launch|coup": "social",
    "stand|trial": "social", "face|trial": "social", "bring|charge": "social", "press|charge": "social",
    "drop|charge": "social",
    # --- competition (armed conflict / offensives) ---
    "declare|war": "competition", "wage|war": "competition", "make|war": "competition",
    "launch|attack": "competition", "mount|attack": "competition", "make|attack": "competition",
    "launch|offensive": "competition", "wage|campaign": "competition",
    # --- stative (eventive / states of being) ---
    "take|place": "stative", "take|shape": "stative", "take|form": "stative", "take|root": "stative",
    "take|hold": "stative", "take|toll": "stative", "take|priority": "stative",
    "take|precedence": "stative", "come|effect": "stative", "come|force": "stative",
    "serve|purpose": "stative", "play|role": "stative", "play|part": "stative", "pose|threat": "stative",
    "bear|fruit": "stative",
    # --- possession / transfer ---
    "lay|claim": "possession", "stake|claim": "possession", "take|possession": "possession",
    "give|rise": "creation",
    # --- perception ---
    "take|look": "perception", "cast|glance": "perception", "catch|glimpse": "perception",
    "catch|sight": "perception", "keep|eye": "perception",
    # --- emotion ---
    "lose|temper": "emotion", "lose|patience": "emotion", "take|offence": "emotion",
    "take|offense": "emotion", "bear|grudge": "emotion", "hold|grudge": "emotion",
    # --- body ---
    "give|birth": "body",
}

# ---------------------------------------------------------------------------
# Curated PHRASAL: the genuinely-missing common phrasal verbs (measured absent from the WordNet-derived
# 1813) + the CLEAN corpus-mined non-WordNet (verb, prt) satellites, each hand-mapped to a coarse
# frame. Added only for keys ABSENT from the existing asset.
# ---------------------------------------------------------------------------
CURATED_PHRASAL: Dict[str, str] = {
    "pass|down": "possession", "leave|behind": "possession", "hold|together": "stative",
    "keep|together": "contact", "settle|in": "stative", "wind|down": "change",
    "look|over": "perception", "look|through": "perception", "look|ahead": "cognition",
    "pull|apart": "change", "split|off": "change", "grow|out": "change", "take|aside": "communication",
    "give|over": "possession", "call|around": "communication", "pick|on": "social",
    "hand|in": "possession", "hand|back": "possession", "hand|off": "possession",
    "divide|up": "change", "match|up": "stative", "read|out": "communication", "join|in": "social",
    "join|up": "social", "start|off": "change", "leave|over": "possession", "branch|off": "motion",
    "team|up": "social", "bottle|up": "emotion",
}

# Resultative complements ("go bad", "fall ill", "come true"). The satellite is an ADJ/NP the caller may
# expose in EITHER the particle slot or the object-head slot, so these are written to BOTH maps.
CURATED_RESULTATIVE: Dict[str, str] = {
    "go|bad": "change", "go|wrong": "change", "go|sour": "change", "go|stale": "change",
    "go|bankrupt": "possession", "come|true": "change", "turn|sour": "change", "run|dry": "change",
    "go|blind": "body", "go|deaf": "body", "fall|ill": "body", "fall|sick": "body",
}


# ===========================================================================
# CORPUS MINING (offline; spaCy INLINE). One pass collects both prt satellites and dobj bigrams.
# ===========================================================================
def mine_corpus(corpus_path: str, max_sents: int, batch_size: int = 256) -> Dict:
    """Single spaCy pass. Returns counts for (verb,prt) satellites (dep 'prt') and (verb,dobj_head)
    bigrams (dep dobj/obj, head noun), plus verb/object marginals + total for PMI. spaCy INLINE."""
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    prt: Counter = Counter()
    dobj: Counter = Counter()
    vc: Counter = Counter()
    oc: Counter = Counter()
    total = 0

    def _gen():
        with open(corpus_path, "r", encoding="utf-8", errors="ignore") as f:
            n = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield line
                n += 1
                if n >= max_sents:
                    break

    n_sent = 0
    for doc in nlp.pipe(_gen(), batch_size=batch_size):
        n_sent += 1
        for tok in doc:
            if tok.pos_ != "VERB":
                continue
            v = tok.lemma_.lower()
            if not v.isalpha():
                continue
            for ch in tok.children:
                if ch.dep_ == "prt":
                    p = ch.lemma_.lower()
                    if p.isalpha():
                        prt[(v, p)] += 1
                elif ch.dep_ in ("dobj", "obj") and ch.pos_ in ("NOUN", "PROPN"):
                    o = ch.lemma_.lower()
                    if o.isalpha():
                        dobj[(v, o)] += 1
                        vc[v] += 1
                        oc[o] += 1
                        total += 1
    return {"prt": prt, "dobj": dobj, "vc": vc, "oc": oc, "total": total, "n_sent": n_sent}


def _pmi_pairs(mined: Dict, min_pair: int = 4, min_pmi: float = 2.0
               ) -> List[Tuple[str, str, int, float]]:
    """High-PMI (verb, dobj_head) pairs [(v,o,count,pmi)] sorted by PMI desc (gate (a) candidates)."""
    dobj, vc, oc, total = mined["dobj"], mined["vc"], mined["oc"], mined["total"]
    rows: List[Tuple[str, str, int, float]] = []
    if total == 0:
        return rows
    for (v, o), c in dobj.items():
        if c < min_pair:
            continue
        pmi = math.log((c * total) / (vc[v] * oc[o]))
        if pmi >= min_pmi:
            rows.append((v, o, c, pmi))
    rows.sort(key=lambda r: -r[3])
    return rows


def _wn_sense_frame(v: str, o: str, dom: Optional[str]) -> Optional[str]:
    """Gate (a): dedicated WordNet 'verb_noun' sense whose frame differs from the verb's dominant
    frame -> a lexicalised non-literal reading exists."""
    from nltk.corpus import wordnet as wn
    lemma = v + "_" + o
    if wn.synsets(lemma, "v"):
        fr = _lemma_sense_frame(lemma)
        if fr is not None and fr != dom:
            return fr
    return None


# ===========================================================================
# BUILD
# ===========================================================================
def _load_existing() -> Tuple[Dict[str, str], Dict[str, str], Dict]:
    """Load the current asset (phrasal, vobj, meta). If absent, build the base asset first (guard)."""
    if not os.path.exists(_ASSET_PATH):
        IG.build_asset(verbose=False)
    with open(_ASSET_PATH, "r", encoding="ascii") as f:
        obj = json.load(f)
    return dict(obj.get("phrasal", {})), dict(obj.get("vobj", {})), dict(obj.get("meta", {}))


def build_expanded(corpus_path: Optional[str] = None, max_sents: int = 120000,
                   out_path: Optional[str] = None, verbose: bool = True) -> Dict:
    """Expand the committed idiom asset in place (non-destructive) and write it atomically.
    Returns a stats dict. Guards a missing corpus (curated tables still expand the asset)."""
    corpus_path = corpus_path or _CORPUS_DEFAULT
    out_path = out_path or _ASSET_PATH

    phrasal, vobj, old_meta = _load_existing()
    pre_phrasal, pre_vobj = len(phrasal), len(vobj)
    # Snapshot the PRE-expansion keys so the curated overlay can override a NEW mined frame while
    # NEVER overriding an entry that already existed (non-destructive merge).
    existing_vobj_keys = set(vobj.keys())

    # ---- corpus mining (guarded) -------------------------------------------------
    mined: Optional[Dict] = None
    n_sent = 0
    if os.path.exists(corpus_path):
        if verbose:
            print(f"[expand] mining up to {max_sents} lines of {os.path.basename(corpus_path)} ...")
        mined = mine_corpus(corpus_path, max_sents=max_sents)
        n_sent = mined["n_sent"]
        if verbose:
            print(f"[expand] parsed {n_sent} sentences; {len(mined['prt'])} distinct (verb,prt), "
                  f"{len(mined['dobj'])} distinct (verb,dobj).")
    elif verbose:
        print(f"[expand] corpus MISSING ({corpus_path}) -- curated-only expansion (mining skipped).")

    # ---- precompute dominant frames for the light verbs (for the fr != dom gate) ----
    dom_cache: Dict[str, Optional[str]] = {v: _verb_dominant_frame(v) for v in LIGHT}

    # =========================== VOBJ ===========================================
    mined_strict_added = 0          # (b') frequency-gated strict institutional
    mined_wn_added = 0              # (a)  PMI + WordNet verb_noun sense
    pmi_candidates = 0
    pmi_kept = 0
    strict_examples: List[Tuple[str, str, int, str]] = []

    if mined is not None:
        MIN_INST_COUNT = 3
        # (b') strict-object frequency gate -- harvest attested light+institutional direct objects.
        for (v, o), c in sorted(mined["dobj"].items(), key=lambda kv: -kv[1]):
            if c < MIN_INST_COUNT or v not in LIGHT or o not in OBJ2FRAME_STRICT:
                continue
            key = v + "|" + o
            if key in vobj:
                continue
            fr = OBJ2FRAME_STRICT[o]
            if fr == dom_cache.get(v):        # frame == literal verb frame -> compositional, reject
                continue
            vobj[key] = fr
            mined_strict_added += 1
            if len(strict_examples) < 40:
                strict_examples.append((v, o, c, fr))

        # (a) PMI + WordNet verb_noun gate (kept from the original builder).
        pmi_rows = _pmi_pairs(mined)
        pmi_candidates = len(pmi_rows)
        for v, o, c, pmi in pmi_rows:
            key = v + "|" + o
            if key in vobj:
                continue
            dom = dom_cache.get(v)
            if dom is None:
                dom = _verb_dominant_frame(v)
            fr = _wn_sense_frame(v, o, dom)
            if fr is not None:
                vobj[key] = fr
                mined_wn_added += 1
                pmi_kept += 1

    # ---- curated VOBJ overlay (authoritative; adds only ABSENT keys; overrides mined-new) ----
    # curated overrides a NEW (mined-this-run) frame with its authoritative value, but NEVER overrides
    # an entry that already existed in the base asset.
    curated_vobj_added = 0
    for key, fr in CURATED_VOBJ_EXPAND.items():
        if key in existing_vobj_keys:
            continue
        if key not in vobj:
            vobj[key] = fr
            curated_vobj_added += 1
        elif vobj[key] != fr:             # override a NEW mined frame with the curated (authoritative)
            vobj[key] = fr

    # =========================== PHRASAL ========================================
    curated_phrasal_added = 0
    for key, fr in CURATED_PHRASAL.items():
        if key not in phrasal:
            phrasal[key] = fr
            curated_phrasal_added += 1

    # ---- resultatives -> BOTH maps (absent keys only) ----
    resultative_added = 0
    for key, fr in CURATED_RESULTATIVE.items():
        if key not in phrasal:
            phrasal[key] = fr
            resultative_added += 1
        if key not in vobj:
            vobj[key] = fr

    # ---- validate every stored frame is a legal coarse frame ----
    for m, name in ((phrasal, "phrasal"), (vobj, "vobj")):
        for k, fr in m.items():
            if fr not in _FRAMESET:
                raise ValueError("non-coarse frame %r for %s key %r" % (fr, name, k))

    keep_rate = (pmi_kept / pmi_candidates) if pmi_candidates else 0.0
    meta = {
        "source": "idiom_gate_expand_v1(strict_freq_gate+pmi_wn_gate+curated_vobj+curated_phrasal)",
        "base_source": old_meta.get("source"),
        "corpus": os.path.basename(corpus_path) if mined is not None else None,
        "corpus_used": mined is not None,
        "max_sents": max_sents if mined is not None else 0,
        "n_sentences_parsed": n_sent,
        "n_phrasal": len(phrasal),
        "n_vobj": len(vobj),
        "backup_pre_expansion": {"n_phrasal": pre_phrasal, "n_vobj": pre_vobj,
                                 "meta": old_meta},
        "expand_stats": {
            "phrasal_curated_added": curated_phrasal_added,
            "resultative_added_to_phrasal": resultative_added,
            "vobj_strict_freq_gate_added": mined_strict_added,
            "vobj_pmi_wn_gate_added": mined_wn_added,
            "vobj_curated_added": curated_vobj_added,
            "pmi_gate_candidates": pmi_candidates,
            "pmi_gate_kept": pmi_kept,
            "pmi_gate_keep_rate": round(keep_rate, 4),
            "min_inst_count": 3,
        },
    }
    asset = {"meta": meta, "phrasal": phrasal, "vobj": vobj}
    _atomic_write_json(out_path, asset)
    IG._CACHE = None  # drop base-module runtime cache so idiom_sense() re-reads the fresh asset

    if verbose:
        print(f"[expand] phrasal {pre_phrasal} -> {len(phrasal)} "
              f"(+{curated_phrasal_added} curated, +{resultative_added} resultative)")
        print(f"[expand] vobj    {pre_vobj} -> {len(vobj)} "
              f"(+{mined_strict_added} strict-freq-gate, +{mined_wn_added} pmi/wn-gate, "
              f"+{curated_vobj_added} curated)")
        print(f"[expand] PMI gate keep-rate: {pmi_kept}/{pmi_candidates} = {keep_rate:.3f}")
        print(f"[expand] wrote {out_path}")
    asset["_strict_examples"] = strict_examples
    return asset


# ===========================================================================
# SELF-TEST -- the base module's 7 assertions PLUS >=8 new expanded cases.
# ===========================================================================
def _self_test(rebuild: bool = True) -> bool:
    if rebuild or not os.path.exists(_ASSET_PATH):
        build_expanded(verbose=True)
    IG._CACHE = None

    base_checks = [
        ("[base] pass|away -> {change,stative,body}", idiom_sense("pass", "away", None) in {"change", "stative", "body"}),
        ("[base] go|off is not None",                 idiom_sense("go", "off", None) is not None),
        ("[base] make+sense in {cognition,communication}", idiom_sense("make", None, "sense") in {"cognition", "communication"}),
        ("[base] pass+law in {social,communication}", idiom_sense("pass", None, "law") in {"social", "communication"}),
        ("[base] take+place in {stative,social}",     idiom_sense("take", None, "place") in {"stative", "social"}),
        ("[base] leave+room is None",                 idiom_sense("leave", None, "room") is None),
        ("[base] leave+key is None",                  idiom_sense("leave", None, "key") is None),
    ]
    new_checks = [
        ("[new] carry|out in {creation,social,change}", idiom_sense("carry", "out", None) in {"creation", "social", "change"}),
        ("[new] give|up -> possession",               idiom_sense("give", "up", None) == "possession"),
        ("[new] break|down is not None",              idiom_sense("break", "down", None) is not None),
        ("[new] take+office -> social",               idiom_sense("take", None, "office") == "social"),
        ("[new] go|bad -> change (particle slot)",    idiom_sense("go", "bad", None) == "change"),
        ("[new] go|bad -> change (object slot)",      idiom_sense("go", None, "bad") == "change"),
        ("[new] come+decision -> cognition",          idiom_sense("come", None, "decision") == "cognition"),
        ("[new] pay+attention in {cognition,perception}", idiom_sense("pay", None, "attention") in {"cognition", "perception"}),
        ("[new] take+control -> social",              idiom_sense("take", None, "control") == "social"),
        ("[new] raise+question -> communication",     idiom_sense("raise", None, "question") == "communication"),
        ("[new] make+point -> communication",         idiom_sense("make", None, "point") == "communication"),
        ("[new] eat+apple is None (precision)",       idiom_sense("eat", None, "apple") is None),
        ("[new] leave+room is None (precision)",      idiom_sense("leave", None, "room") is None),
    ]
    print("\nSELF-TEST idiom_gate_expand_v1:")
    base_pass = 0
    for name, ok in base_checks:
        base_pass += int(bool(ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    new_pass = 0
    for name, ok in new_checks:
        new_pass += int(bool(ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"\n  BASE  {base_pass}/{len(base_checks)}   NEW {new_pass}/{len(new_checks)}")
    return base_pass == len(base_checks) and new_pass == len(new_checks)


if __name__ == "__main__":
    args = set(sys.argv[1:])
    _max = 120000
    for a in list(args):
        if a.startswith("--max-sents="):
            _max = int(a.split("=", 1)[1])
    if "--build" in args:
        build_expanded(max_sents=_max)
    elif "--self-test" in args:
        ok = _self_test(rebuild=("--no-rebuild" not in args))
        sys.exit(0 if ok else 1)
    else:
        print("usage: python -m experiments.idiom_gate_expand_v1 "
              "[--build [--max-sents=N] | --self-test [--no-rebuild]]")
