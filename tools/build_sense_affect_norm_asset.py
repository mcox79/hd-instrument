"""build_sense_affect_norm_asset.py -- OFFLINE foundation asset: a SENSE-KEYED affect norm for verbs.

WHY (the located defect). The reader's affect value is ONE number per WORD FORM. Warriner et al. (2013)
rated `treat` +0.46, `handle` +0.18, `hold` +0.26, `carry` +0.17, `grab` +0.11, `pull` +0.15 -- pleasant
words -- so the harm/help read answers HELP on "the guard treated the prisoner" and "he handled the box".
A word-form norm is an average over a word's senses weighted by whichever meaning the raters happened to
access out of context; the reader needs the value of the meaning that is ACTIVE.

THE BRAIN (the opening move: how does a reader feel `treat` differently in "a birthday treat", "treated
the wound", "treated the prisoner"?).
  1. THE VALUE IS ATTACHED TO THE ACTIVATED MEANING, NOT THE LETTER STRING. The anterior-temporal semantic
     hub settles on a sense from context (Rodd, Gaskell & Marslen-Wilson 2004: the settled semantic vector;
     Kuperberg's graded meaning activation; PPR spreading activation as the computational-level model,
     already an organ here) and the OFC/vmPFC values THAT meaning (Barsalou situated conceptualisation;
     PINNED valuation target -- BRAIN_MATH_REFERENCE section D).
  2. THE COMPUTATION IS AN EXPECTATION OVER THE SENSE POSTERIOR:
         value(verb | context) = SUM_s P(s | context) * value(s)
     P(s|context) = the log-linear blend of the frequency RESTING LEVEL and the settled spreading
     activation (the organ's own `select_sense_blended`, here read as a DISTRIBUTION instead of an argmax);
     value(s) = the affective value of the state THAT SENSE leaves the patient in.
  3. value(s) IS THE VALUE OF THE SIMULATED OUTCOME, AND AN UNSPECIFIED OUTCOME HAS NO VALUE. A sense whose
     event names no state change for the patient ("interact in a certain way", "be in charge of", "move
     while supporting") contributes ZERO, not "unknown": the OFC has nothing to value. That is what makes
     `treat`/`handle`/`hold`/`carry` come out neutral without an abstention RULE -- the pri-98 solver
     measured that an abstention rule (withhold the norm for manner-host verbs) is REFUTED by the human
     gold (Connotation Frames 0.9333 -> 0.9014).

WHERE value(s) COMES FROM -- five SENSE-KEYED channels, in order of their precision about the patient's
endstate. Every one of them is already sense-keyed inside the organ; what was missing is that the organ
COLLAPSED them across senses (cross-sense consensus) because it had no posterior to weight them with.
  R  RESULT STATE   VerbNet class semantics at result(E)/end(E) keyed by WordNet sense key, valued by the
                    affect lexicon or the innate nociceptive sign (forceful contact on a body = -1, PINNED).
  C  CAUSED EVENT   WordNet's own CAUSAL structure for THIS synset, restricted to a caused STATE CHANGE
                    (kill.v.01 CAUSES die.v.01, verb.change): the lexicon names the result state the patient
                    is left in. `entailments` are deliberately NOT read -- they mix presupposition
                    (divorce ENTAILS marry) with agent co-events (defend ENTAILS contend), neither of which
                    is a result the patient inherits; measured, reading them cost a live-gold item.
  M  MANNER         the manner/means/result filler of THIS synset's definition (the pri-98 manner asset,
                    already synset-keyed), gated by the CIRCUMPLEX RADIUS of the manner's core affect
                    (Russell 1980, PINNED: radius = intensity) -- Talmy manner/result complementarity.
  H  SUPERORDINATE  the value of the sense's immediate hypernym concept (anterior-temporal taxonomic
                    inheritance), estimated from that synset's names weighted by how often each names it.
  T  NEAREST        the same walked UPWARD to the nearest ancestor that carries a value at all (Collins &
     ANCESTOR       Quillian cognitive economy: a property lives at the most general node where it holds).
  S  CO-NAMES       the value of the sense's OTHER names (comfort.v.01 = soothe / console / solace), the
                    TARGET LEMMA EXCLUDED -- that exclusion is what stops the word-form norm re-entering
                    through the back door (treat.v.01 would otherwise read its own +0.46 back).
  else 0 (no predicted affective outcome).

Every channel mean is COUNT-WEIGHTED (SemCor lemma counts + smoothing), never a bare average: a concept's
value is estimated from its names in proportion to how often each is used to name it.

WHAT IS SHIPPED (data/frontend_assets/sense_affect_norm_v1.json):
  senses:  verb lemma -> [[synset, semcor_count, affecting01, {channel: value}], ...] over ALL of that
           lemma's verb senses -- COUNTS, so the table is
           plastic: `observe_sense(lemma, synset)` increments the resting level from running prose and the
           expectation is one pure function of those counts.
  meta:    thresholds used, channel histogram, provenance.
Nothing external runs at inference: the organ reads this dict (plus, when context is available, the
reader's own spreading-activation graph, an hdlab organ).

Run:  .venv/Scripts/python.exe tools/build_sense_affect_norm_asset.py
      .venv/Scripts/python.exe tools/build_sense_affect_norm_asset.py --limit 300     (smoke)
Deterministic, glass-box, ASCII. BUILD TIME ONLY.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import json
import sys
import time
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "data", "frontend_assets", "sense_affect_norm_v1.json")
MANNER_ASSET = os.path.join(REPO, "data", "frontend_assets", "manner_intensity_v1.json")

# ---- OPERATING POINT (all SWEPT in the cell; never adopted) ------------------------------------------
TAU_C = 0.30        # |value| a CAUSED event must carry to name the patient's outcome
TAU_H = 0.35        # |value| a SUPERORDINATE concept must carry (same knee as the landed hypernym arm)
TAU_S = 0.30        # |value| the sense's OTHER names must carry
AMBIGUITY_SHRINK = True   # weight every WORD-FORM witness by its own unambiguity (the missing precision)
TAU_RHO_WITNESS = 0.0     # drop a witness whose OWN name is more ambiguous than this (0 = keep all; SWEPT)
TAU_MANNER_VAL = 0.10     # pri-98 operating point (the manner's valence floor)
TAU_INTENSITY = 0.40      # pri-98 operating point (the circumplex radius / grounded action strength)
A0 = 0.40                 # circumplex resting point
LEMMA_SMOOTH = 0.5        # count smoothing for the count-weighted concept value
MAX_TAXONOMIC_DEPTH = 4   # how far the nearest-informative-ancestor walk may climb (SWEPT)
MANNER_SLOTS = ("ADVMOD", "MANNER_PP", "MEANS_PP", "RESULT_ADJ")


def _manner_asset() -> Dict:
    try:
        with open(MANNER_ASSET, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"words": {}, "evidence": {}}


_PREC: Dict[str, float] = {}


def unambiguity(word: str, wn) -> float:
    """THE MISSING PRECISION (Ernst & Banks w ~ 1/sigma^2; the rung the pri-98 solver named as un-cracked --
    "no cue carries a variance"). A WORD-FORM norm is a rating of a letter string: it estimates the value of
    ONE sense well exactly to the degree that the word HAS one sense. So the reliability of a name as a
    witness about a concept is the SIMPSON CONCENTRATION of that name's own sense distribution over ALL its
    senses and parts of speech (the resting levels the raters were sampling from):
        rho(w) = SUM_i p_i^2 ,  p_i = (SemCor count_i + a) / SUM_j (count_j + a)
    A monosemous name scores 1.0; `treat` (a dessert, an interaction, a medical act, ...) scores far less --
    which is exactly why Warriner's +0.46 is not a fact about the verb sense."""
    w = word.lower()
    if w in _PREC:
        return _PREC[w]
    counts = []
    try:
        for s in wn.synsets(w):
            c = 0
            for lm in s.lemmas():
                if lm.name().lower() == w:
                    c = lm.count()
                    break
            counts.append(float(c) + LEMMA_SMOOTH)
    except Exception:
        counts = []
    if not counts:
        rho = 1.0
    else:
        tot = sum(counts)
        rho = sum((c / tot) ** 2 for c in counts)
    _PREC[w] = rho
    return rho


def concept_value(syn, afx, exclude: Optional[str] = None, wn=None) -> Optional[float]:
    """The affective value of a CONCEPT, estimated from the names that denote it, each weighted by HOW
    OFTEN it is used to name it (SemCor lemma counts + smoothing) and SHRUNK toward zero in proportion to
    how AMBIGUOUS those names are (`unambiguity` above; the OFC's default for an unspecified outcome is no
    value, so the shrinkage target is 0). `exclude` drops the target lemma so a word never reads its own
    word-form norm back as evidence about its own sense."""
    num = den = 0.0
    for lm in syn.lemmas():
        name = lm.name().lower()
        if exclude is not None and name == exclude:
            continue
        head = name.replace("_", " ").split()[0]
        v = afx.valence(head)
        if v is None:
            continue
        rho = unambiguity(head, wn) if (AMBIGUITY_SHRINK and wn is not None) else 1.0
        if rho < TAU_RHO_WITNESS:
            continue
        w = (float(lm.count()) + LEMMA_SMOOTH) * rho
        num += w * v
        den += w
    if not den:
        return None
    return num / den


def manner_intensity(word: str, afx, words: Dict) -> Optional[float]:
    """max(circumplex radius of the word's core affect, its grounded action strength) -- pri-98, verbatim
    operating point. Russell 1980: intensity is the RADIUS in the valence x arousal plane, not arousal."""
    v = afx.valence(word)
    a = afx.arousal(word)
    g = words.get(word, {}).get("g")
    if v is None and a is None and g is None:
        return None
    r2 = (float(v) ** 2 if v is not None else 0.0)
    if a is not None:
        r2 += max(0.0, float(a) - A0) ** 2
    r = r2 ** 0.5
    if g is not None:
        r = max(r, float(g))
    return min(1.0, r)


def sense_channels(syn, lemma: str, afx, FDV, manner, wn,
                   tau_c: float = TAU_C, tau_h: float = TAU_H, tau_s: float = TAU_S,
                   channels: str = "RCMHST", _depth: int = 0) -> Dict[str, float]:
    """EVERY sense-keyed channel that fires for this sense, as {channel: value}. The READ chooses which
    channels to trust and in what order -- shipping all of them keeps the ablation honest and keeps the
    asset one pure function of the foundation."""
    got: Dict[str, float] = {}
    # --- R: the RESULT STATE the sense leaves the patient in (VerbNet, sense-key) ---
    if "R" in channels:
        table = FDV.result_state_table()
        vals = []
        for lm in syn.lemmas():
            key = lm.key().split("::")[0]
            for _cid, _member, sts in table.get(key, ()):
                for st in sts:
                    sv = FDV.state_value(st, afx)
                    if sv is not None:
                        vals.append(sv)
        if vals:
            m = sum(vals) / len(vals)
            if abs(m) >= FDV.STATE_MIN:
                got["R"] = m
    # --- C: the event the sense CAUSES or ENTAILS (the lexicon's own result event) ---
    if "C" in channels and _depth == 0:
        cv = []
        # ONLY `causes`, and only into a STATE CHANGE. WordNet's `entailments` mixes presupposition
        # (divorce ENTAILS marry), agent co-events (defend ENTAILS contend) and troponymic sub-events; none
        # of those is a result the PATIENT inherits, and reading them was measured to cost the live gold an
        # item (defend -> -0.365 from contend, gold HELP) and to put `divorce` on the wrong side of the human
        # gold (+0.512 against a HARM gold). What transfers to the patient is the value of the state the
        # event CAUSES: kill.v.01 CAUSES die.v.01 (verb.change) -- a state of the undergoer. The supersense
        # test is the state-change test (Levin/Rappaport Hovav result-state lexicalisation).
        for t in [c for c in syn.causes()
                  if c.lexname().split(".")[1] in ("change", "body", "emotion", "stative")]:
            x = concept_value(t, afx, wn=wn)
            if x is None:
                sub = sense_channels(t, "", afx, FDV, manner, wn, tau_c, tau_h, tau_s,
                                     channels="RHT", _depth=1)
                x = sub.get("R", sub.get("H", sub.get("T")))
            if x is not None:
                cv.append(x)
        if cv:
            m = sum(cv) / len(cv)
            if abs(m) >= tau_c:
                got["C"] = m
    # --- M: the MANNER this sense's definition lexicalises (pri-98 asset, synset-keyed) ---
    if "M" in channels and lemma:
        words = manner.get("words", {})
        mv = []
        for syn_name, slot, filler, cnt in manner.get("evidence", {}).get(lemma, ()):
            if syn_name != syn.name() or slot not in MANNER_SLOTS:
                continue
            x = afx.valence(filler)
            if x is None or abs(x) < TAU_MANNER_VAL:
                continue
            inten = manner_intensity(filler, afx, words)
            if inten is None or inten < TAU_INTENSITY:
                continue
            mv.append((x, float(cnt)))
        if mv:
            got["M"] = sum(x * c for x, c in mv) / sum(c for _x, c in mv)
    # --- H: the immediate SUPERORDINATE concept (taxonomic inheritance, depth 1) ---
    if "H" in channels:
        hv = [x for h in syn.hypernyms() for x in [concept_value(h, afx, wn=wn)] if x is not None]
        if hv:
            m = sum(hv) / len(hv)
            if abs(m) >= tau_h:
                got["H"] = m
    # --- T: the NEAREST INFORMATIVE ANCESTOR (cognitive economy, Collins & Quillian 1969: a property is
    # stored at the most general node where it holds, and retrieval walks up until it finds one). Depth 1
    # is H; T keeps climbing while the ancestors are affectively silent, so a sense whose parent is a bare
    # taxonomic node ('take', 'move') can still inherit from the first ancestor that carries a value.
    if "T" in channels:
        frontier = list(syn.hypernyms())
        seen = set()
        for _d in range(1, MAX_TAXONOMIC_DEPTH + 1):
            vals = []
            nxt = []
            for h in frontier:
                if h.name() in seen:
                    continue
                seen.add(h.name())
                x = concept_value(h, afx, wn=wn)
                if x is not None:
                    vals.append(x)
                nxt.extend(h.hypernyms())
            if vals:
                m = sum(vals) / len(vals)
                if abs(m) >= tau_h:
                    got["T"] = m
                    break
            frontier = nxt
            if not frontier:
                break
    # --- S: the sense's OTHER names, the target lemma EXCLUDED ---
    if "S" in channels and lemma:
        x = concept_value(syn, afx, exclude=lemma, wn=wn)
        if x is not None and abs(x) >= tau_s:
            got["S"] = x
    return got


def build(limit: Optional[int] = None) -> Dict:
    from nltk.corpus import wordnet as wn
    import hdlab.force_dynamics_valence as FDV
    from hdlab.affect_lexicon import AffectLexicon

    afx = AffectLexicon.load()
    manner = _manner_asset()
    FDV.result_state_table()

    # THE POPULATION: exactly the senses the harm/help read is allowed to value -- an AFFECTING supersense
    # with an ANIMATE-OBJECT frame (the same gate the landed result-state and superordinate reads use).
    def affecting(s) -> bool:
        return (s.lexname().split(".")[1] in FDV.AFFECTING_SUPERSENSES
                and bool(set(s.frame_ids()) & FDV.ANIMATE_OBJECT_FRAMES))

    syns = sorted([s for s in wn.all_synsets("v") if affecting(s)], key=lambda s: s.name())
    if limit:
        syns = syns[:limit]
    # THE LEMMA POPULATION: every one-word verb that has at least one AFFECTING-ANIMATE sense. But the
    # sense INVENTORY shipped for that lemma is ALL of its verb senses -- the semantic hub settles over the
    # whole inventory, so renormalising the posterior over the affecting subset alone puts probability ~1
    # on a rare sense (measured: `buy` -> bribe.v.01, `hate` -> hate.v.01, both wrong). The affecting gate
    # belongs on the VALUE (a non-affecting sense predicts no outcome for a patient, hence value 0), never
    # on the PROBABILITY.
    lemmas = sorted({lm.name().lower() for ss in syns for lm in ss.lemmas() if "_" not in lm.name()})

    senses: Dict[str, List] = {}
    hist: Dict[str, int] = {}
    t0 = time.time()
    for n, v in enumerate(lemmas):
        if n and n % 500 == 0:
            print("  %d/%d lemmas  %.0fs" % (n, len(lemmas), time.time() - t0), flush=True)
        rows = []
        for ss in wn.synsets(v, pos=wn.VERB):
            cnt = 0
            for lm in ss.lemmas():
                if lm.name().lower() == v:
                    cnt = lm.count()
                    break
            aff = affecting(ss)
            ch = sense_channels(ss, v, afx, FDV, manner, wn) if aff else {}
            ch = {k: round(float(x), 4) for k, x in sorted(ch.items())}
            rows.append([ss.name(), int(cnt), 1 if aff else 0, ch])
            for k in (ch or {"none": 0}):
                hist[k] = hist.get(k, 0) + 1
        senses[v] = rows

    # THE WORD-FORM RUNG, WITH ITS PRECISION. rho(verb) = how unambiguous the letter string is = how much
    # a rating of that string can be trusted as a statement about the sense in play. This is the number the
    # read fuses the Warriner norm in with; it is what makes `treat` (rho 0.25) yield to its senses while
    # `murder` (0.76) and `protect` (0.94) keep their word norm.
    words = {}
    for v in senses:
        words[v] = {"rho": round(unambiguity(v, wn), 4)}
        wv = afx.valence(v)
        if wv is not None:
            words[v]["v"] = round(float(wv), 4)

    return {
        "meta": {
            "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "WordNet verb senses (affecting supersense x animate-object frames) valued per SENSE "
                      "by five sense-keyed channels: VerbNet result state / WordNet caused event / the "
                      "pri-98 manner decomposition / the superordinate concept / the sense's co-names "
                      "(target lemma excluded); concept values are SemCor-count-weighted Warriner norms",
            "n_synsets": len(syns), "n_lemmas": len(senses),
            "n_rows": sum(len(r) for r in senses.values()),
            "channel_histogram": dict(sorted(hist.items())),
            "tau_c": TAU_C, "tau_h": TAU_H, "tau_s": TAU_S,
            "tau_manner_val": TAU_MANNER_VAL, "tau_intensity": TAU_INTENSITY,
            "lemma_smooth": LEMMA_SMOOTH, "ambiguity_shrink": AMBIGUITY_SHRINK,
            "tau_rho_witness": TAU_RHO_WITNESS, "max_taxonomic_depth": MAX_TAXONOMIC_DEPTH,
            "plastic": "rows carry the SemCor resting-level COUNT; observe_sense(lemma, synset) increments "
                       "it from running prose and the sense expectation is one pure function of the counts",
        },
        "senses": {k: v for k, v in sorted(senses.items())},
        "words": {k: words[k] for k in sorted(words)},
    }


def main() -> None:
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    asset = build(limit)
    if os.path.exists(OUT) and "--force" not in sys.argv:
        print("REFUSING to overwrite existing %s (pass --force)" % OUT)
        return
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(asset, f, separators=(",", ":"), sort_keys=True)
    os.replace(tmp, OUT)
    print("wrote %s" % OUT)
    print("  lemmas=%d synsets=%d channels=%s" % (
        asset["meta"]["n_lemmas"], asset["meta"]["n_synsets"], asset["meta"]["channel_histogram"]))
    for v in ("treat", "handle", "hold", "grab", "carry", "pull", "kill", "help", "comfort", "murder"):
        print("  %-8s %s" % (v, asset["senses"].get(v, [])[:6]))


if __name__ == "__main__":
    main()
