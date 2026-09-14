"""pri 108 -- THE ROLE COMPETITION HAS NO NMOD CLASS: a nominal licensed by a nominal is a PROPERTY, not an OBLIQUE.

BRAIN COMPUTATION (PINNED at the computational level -- Bates & MacWhinney Competition Model 1982/1989; MacWhinney 1987):
a nominal's grammatical role is decided by PARALLEL competition of surface CUES, each carrying a LEARNED VALIDITY
(availability x reliability) read WITHIN the configuration it applies to:

    activation(role) = log P(role) + [log P(role|cfg) - log P(role)] + SUM_cues [log P(role|cfg,value) - log P(role|cfg)]

softmax = the posterior, argmax = the MAP read. THIS EXPERIMENT DOES NOT CHANGE THAT OPERATION. It changes (1) the
CLASS SPACE the competition competes over and (2) one CUE VALUE that English marks and the built cue set never read.

  1. THE MISSING CLASS. `ROLE_CLASSES` has no NMOD. A case-marked phrase licensed by a PREDICATE is an oblique
     PARTICIPANT of an event; one licensed by a NOMINAL is a PROPERTY of a thing. Those are different things in the
     brain's situation model -- the first fills an event slot, the second modifies an entity -- and the organ could
     not say the second at all: gold `nmod` is 0/489 correct even given the gold tree. The distinction is a pure
     function of the LICENSING HOST'S CATEGORY, which the organ ALREADY computes as its `config` cue (head class x
     order), so the class is free: NO new cue is needed for the prepositional kind. Implemented as LEARNED CUE VALUES
     (the counts decide), never as the 98.1%-correct host-category rule.
  2. THE MISSING CASE VALUE (the genitive). A quarter of gold nmod in UD-EWT test 700 is `nmod:poss` (125 of 489), and
     English marks it with a CASE MARKER the cue set never read: the genitive clitic 's (to the nominal's RIGHT, the
     only right-side case marker in the language) and the possessive pronoun forms (my/your/his/her/its/our/their/
     whose). Case marking is a TOP Competition-Model cue (Bates & MacWhinney 1989; MacWhinney 1987) and pri 103
     already lexicalised the preposition; the genitive was simply missing, so a possessor competed with a COMPOUND
     (348 tokens in the same NOUN_pre configuration) on no evidence at all. Added as two VALUES of the EXISTING `case`
     cue -- `gen_clitic` and `gen_pron` -- so the strength is learned like every other cue value and an absent value
     abstains.

SELF-GATING (the pri-103 pattern, so the shipped organ is byte-identical on every existing asset):
  * `strengths_from_counts` reads K from the ASSET's own count vectors and pads the output to the organ's class space
    with a never-winning prior -- a 7-class (pre-2026-09-14) table therefore produces byte-identical strengths and can
    never emit NMOD.
  * the genitive case values fire only when the loaded table declares `cue_set: v4`.
  * `observe_role_outcome` UPGRADES the counts to the full class space before accruing, so the online path covers NMOD.

Populations (UD-EWT test 700, subtype-preserving gold, the organ's own argument-head population):
  gold obl-base 443 (obl 382 / obl:unmarked 42 / obl:agent 19), gold nmod-base 489 (nmod 286 / nmod:poss 125 /
  nmod:unmarked 60 / nmod:desc 18), all expressible nominals 2099.

Run:  python experiments/exp_role_nmod_class_v1.py --self-test
      python experiments/exp_role_nmod_class_v1.py --cache      # perceive train+test once on the CURRENT live chain
      python experiments/exp_role_nmod_class_v1.py --run        # floor / nmod-class / +genitive / twin, gold + live heads
      python experiments/exp_role_nmod_class_v1.py --emit       # write the candidate table to data/hook_state/
      python experiments/exp_role_nmod_class_v1.py --consumer   # causation-typing landing doc + copular state read
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import json
import pickle
import sys
import time
from collections import Counter, defaultdict
from contextlib import contextmanager

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir
from hdlab import graded_role_assigner as GRA
from hdlab.graded_competition import net_activation, softmax
from hdlab.thematic_role_labeler import lemma_verb

UD = os.path.join(REPO, "data", "corpora", "ud_english_ewt")
TRAIN = os.path.join(UD, "en_ewt-ud-train.conllu")
TEST = os.path.join(UD, "en_ewt-ud-test.conllu")
TEST_CAP = 700
ANCHOR = "role_nmod_class_v1"

ROLES7 = ["SUBJ", "OBJ", "PASS_SUBJ", "BY_AGENT", "OBL", "OTHER", "IOBJ"]
ROLES8 = ROLES7 + ["NMOD"]
DEP7 = dict(GRA.ROLE_TO_DEP)
DEP8 = dict(DEP7); DEP8["NMOD"] = "nmod"
KEEP_FULL = ("nsubj:pass", "obl:agent", "csubj:pass")
_ALPHA = 0.5
_M = 2.0
MIN_CONF = 0.5            # pri 103's reliability gate on learning (swept there; kept, re-swept here)

# ----------------------------------------------------------------------------------------------- THE GENITIVE CUE
_POSS_MARK = frozenset({"'s", "'", "s'", "’s", "’"})
_POSS_PRON = frozenset({"my", "your", "his", "her", "its", "our", "their", "whose",
                        "mine", "yours", "hers", "ours", "theirs"})
_NP_START = frozenset({"NOUN", "PROPN", "ADJ", "NUM", "DET", "PRON", "X", "SYM"})


def genitive_value(toks, pos, i):
    """The ENGLISH GENITIVE as a CASE MARKER (Competition Model: case marking is a top cue; the marker FORM is the
    value -- pri 103 lexicalised the preposition, this is the one marker the language puts to the nominal's RIGHT).
    'gen_clitic' -- the nominal is immediately followed by 's / ' (John 's hat; the boys ' coach).
    'gen_pron'   -- the token IS a possessive pronoun form standing in the pre-nominal (determiner) position.
    Arc-free (toks/pos only); AMBIGUOUS by design ('her' is also the object form) -- the validity decides, not a rule."""
    low = toks[i - 1].lower()
    if i < len(toks) and toks[i].lower() in _POSS_MARK:
        return "gen_clitic"
    if low in _POSS_PRON and i < len(toks) and (pos[i] if i < len(pos) else "") in _NP_START:
        return "gen_pron"
    return None


_CONTENT = ("NOUN", "PROPN", "PRON", "VERB", "AUX", "ADJ", "NUM", "ADV", "SYM", "INTJ", "X")
_LEFT_SKIP = ("DET", "ADJ", "NUM", "ADV", "PART", "PUNCT")
_LEFT_STOP = ("SCONJ", "CCONJ")


def host_surface(toks, pos, i, maxscan=8):
    """THE ARC-FREE LICENSOR CUE. The obl/nmod decision IS the licensing host's category, and the organ reads that
    category only through its `config` cue -- i.e. THROUGH THE GOVERNOR'S ARC, so it inherits every attachment error
    at BOTH learning and reading time. But the brain does not need to know WHICH noun licenses a phrase to know THAT
    a noun licenses it: the nearest preceding lexical head is the default licensor (Late Closure / Recency, Frazier
    1979 -- PINNED, and the same locality principle the attachment arm's own distance cue implements), and for a
    genitive-marked nominal the licensor is the following head (English genitives are left-branching).
    Arc-free (toks/pos only), so its validity is learned from clean experience whatever the governor did.
    Measured alone on UD-EWT test 700 obl+nmod it is 0.707 -- a HIGH-availability, MODERATE-reliability cue, which is
    exactly what a Competition-Model cue is; it is added to the competition, never used as a rule."""
    if genitive_value(toks, pos, i) is not None:
        j, steps = i, 0
        while j < len(pos) and steps < maxscan:
            p = pos[j]
            if p in ("PART", "DET", "ADJ", "NUM", "ADV", "PUNCT"):
                j += 1; steps += 1; continue
            return ("r" + p) if p in _CONTENT else "rOTHER"
        return "none"
    j, steps, seen_adp = i - 1, 0, False
    while j >= 1 and steps < maxscan:
        p = pos[j - 1]
        if p == "ADP" and not seen_adp:
            seen_adp = True; j -= 1; steps += 1; continue
        if p in _LEFT_SKIP:
            j -= 1; steps += 1; continue
        if genitive_value(toks, pos, j) is not None:
            # a GENITIVE stands in DETERMINER position -- it is the nominal's own left modifier, not its licensor
            # (the DP-head rule the organ already applies in `is_arg_head`). Found by a consumer negative: without
            # this, "HER office is on the third floor" read `Her` as office's licensor and the copular state read
            # lost its holder.
            j -= 1; steps += 1; continue
        if p in _LEFT_STOP:
            return "none"
        return ("l" + p) if p in _CONTENT else "lOTHER"
    return "none"


_BREAK_TOK = frozenset({",", ";", "--", "—", "–", "(", ")", ":"})
_NPLEFT_SKIP = ("DET", "ADJ", "NUM", "ADV", "PART")


def prosodic_break(toks, pos, heads, i, maxscan=5):
    """THE INTONATION-PHRASE BOUNDARY as a cue. A nominal separated from its host by a prosodic break is a SEPARATE
    phrase describing the host ("Washington , D.C."; "First Union Securities , Inc.") rather than part of one compound
    ("John Smith"). Prosody is a first-class Competition-Model cue (MacWhinney 1987 lists intonation/stress alongside
    order, morphology and case); in written text the comma/dash/paren is its orthographic trace. Two values, read
    surface-first: whether the nominal's own left edge is preceded by a break, and whether a break intervenes between
    the nominal and its head."""
    j, steps = i - 1, 0
    left = "none"
    while j >= 1 and steps < maxscan:
        p = pos[j - 1]
        if p in _NPLEFT_SKIP:
            j -= 1; steps += 1; continue
        if toks[j - 1] in _BREAK_TOK:
            left = "brk"
        break
    h = heads.get(i, 0) or 0
    inter = "none"
    if h:
        lo, hi = (i, h) if i < h else (h, i)
        if any(toks[k - 1] in _BREAK_TOK for k in range(lo + 1, hi)):
            inter = "int"
    return left + "_" + inter


def clause_initial(toks, pos, i):
    """THE FIRST-NOUN CUE, ARC-FREE. In English the Competition Model's single highest-validity cue is preverbal
    position -- "first noun = agent" (MacWhinney, Bates & Kliegl 1984; Bates & MacWhinney 1989). The built cue set has
    the mirror of it (`pre_slot`: is the verb's preverbal slot empty?) only for POST-verbal nominals, and pri 103's
    `pre_rank` is ARC-dependent and precision-gated -- so a nominal has no arc-free way to say "I am the first thing in
    this clause". That is exactly the signal a perceived-heads table erodes: it learned from the governor's own
    misattachments that a NOUN left of a VERB is often not its subject (pri 103, 45 canonical subjects -> OTHER), and
    'The storm flooded the village' lost its affector to that. Clause boundary = punctuation / SCONJ / CCONJ."""
    j = i - 1
    while j >= 1:
        p = pos[j - 1]
        if p in ("PUNCT", "SCONJ", "CCONJ"):
            return "initial"
        if p in _CONTENT:
            return "later"
        j -= 1
    return "initial"


def cues_of(toks, pos, heads, i, frames, v3, conf, gen, hostsurf=False, brk=False, relcl=False, vprep=False,
            edge=False):
    """The organ's own cue values (GRA.coarse_role_cues, unchanged) plus, when the table declares cue_set v4, the
    genitive CASE value and the arc-free LICENSOR cue. `hostsurf` is a NEW cue key: a table that does not carry it
    simply has no strength entry, so the cue abstains and the organ is unchanged."""
    c = GRA.coarse_role_cues(toks, pos, heads, i, frames, v3, conf)
    if gen:
        g = genitive_value(toks, pos, i)
        if g is not None:
            c["case"] = g
    if hostsurf:
        c["hostsurf"] = host_surface(toks, pos, i)
    if hostsurf == "marked":
        if relcl and toks[i - 1].lower() in GRA._WHREL and not (i >= 2 and pos[i - 2] == "ADP"):
            # A RELATIVE PRONOUN IS THE FILLER OF A GAP, NOT A CASE-MARKED PHRASE. pri 103 stopped the surface case
            # scan AT a relativizer; it never stopped it FOR one, so "an area THAT will need" reads `to` (which marks
            # the antecedent, two nouns to the left) as `that`'s own case marker. Only a PIED-PIPED preposition
            # immediately to its left can mark a wh-word ("in which", "to whom"). Found in the core-argument losses:
            # 6 relative-clause subjects labelled nmod.
            c["prep"] = "none"
        c["hostsurf"] = (host_surface(toks, pos, i)
                         if (genitive_value(toks, pos, i) is not None
                             or (c["prep"] not in ("none",) and GRA._prep_of_v3(toks, pos, heads, i)[0] is not None))
                         else "na")
    if edge:
        c["edge"] = clause_initial(toks, pos, i)
    if vprep:
        # THE PHRASAL VERB IS A STORED LEXICAL ITEM (MacWhinney's item-based constructions; pri 103's queued alternate
        # path). The lexical `prep` cue cannot tell the PARTICLE of "worked OUT a deal" from the case marker of
        # "walked OUT of the room", so 8 objects read as obliques. The distinction is a property of the VERB-PLUS-
        # PARTICLE PAIR, so the cue value is the pair, learned like any other and shrunk to its configuration.
        h = heads.get(i, 0) or 0
        pr = c.get("prep", "none")
        if h and 1 <= h <= len(pos) and pos[h - 1] in ("VERB", "AUX") and pr not in ("none", "na"):
            c["vprep"] = lemma_verb(toks[h - 1]).lower() + "+" + pr.split("_")[0]
        else:
            c["vprep"] = "na"
    if brk:
        c["brk"] = prosodic_break(toks, pos, heads, i)
    return c


# ----------------------------------------------------------------------------------------------- class space
@contextmanager
def role_space(classes, deps):
    """Run GRA with a given class space (the shipped patch sets these statically; the cell needs both to measure the
    floor and the arm in one process)."""
    oc, od = GRA.ROLE_CLASSES, GRA.ROLE_TO_DEP
    GRA.ROLE_CLASSES, GRA.ROLE_TO_DEP = list(classes), dict(deps)
    try:
        yield
    finally:
        GRA.ROLE_CLASSES, GRA.ROLE_TO_DEP = oc, od


def coarse_of(dep, classes, poss="NMOD"):
    """Gold deprel -> the competition's CLASS. With NMOD in the space, a nominal licensed by a nominal is NMOD; the
    possessive is a genitive-marked member of that same class (`poss` sweeps it to OTHER for the measurement)."""
    full = dep or ""
    d = full.split(":")[0]
    if full.startswith("nsubj:pass") or full == "nsubjpass":
        return "PASS_SUBJ"
    if d in ("nsubj", "csubj"):
        return "SUBJ"
    if d == "iobj":
        return "IOBJ"
    if d in ("obj", "dobj"):
        return "OBJ"
    if full == "obl:agent":
        return "BY_AGENT"
    if "NMOD" in classes:
        if full == "nmod:poss":
            return poss
        if d == "nmod":
            return "NMOD"
        if d == "obl":
            return "OBL"
        return "OTHER"
    if full == "nmod:poss":
        return "OTHER"
    if d in ("obl", "nmod"):
        return "OBL"
    return "OTHER"


def norm(dep):
    """Base relation, keeping the subtypes the labeler itself distinguishes."""
    if not dep:
        return "dep"
    return dep if dep in KEEP_FULL else dep.split(":", 1)[0]


# ----------------------------------------------------------------------------------------------- gold reader
def sentences(path, cap=None):
    """UD reader that KEEPS the deprel subtype (pri 103's instrument correction)."""
    out, toks, pos, heads, rels = [], [], [], [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    out.append((toks, pos, heads, rels))
                toks, pos, heads, rels = [], [], [], []
                if cap and len(out) >= cap:
                    break
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); pos.append(c[3]); heads.append(int(c[6])); rels.append(c[7])
    if toks and (not cap or len(out) < cap):
        out.append((toks, pos, heads, rels))
    return out


# ----------------------------------------------------------------------------------------------- perception cache
def build_cache(out_dir):
    """Perceive TRAIN and TEST once with THE CURRENT LIVE CHAIN -- hdlab.frontend (category organ `counts` -> the
    attachment arm, graded category hand-off, MBR in-order decode), exactly what the live reader reads. The arm's own
    P(MAP head) is the confidence weight (pri 103's reliability-weighted learning)."""
    from hdlab import frontend as FE
    tg, pp = FE.Tagger(), FE.Parser()
    print("[cache] %s" % FE.describe(), flush=True)
    for name, path, cap in (("test", TEST, TEST_CAP), ("train", TRAIN, None)):
        t0 = time.time(); rows = []
        for toks, gpos, gheads, rels in sentences(path, cap=cap):
            cats, tpost = tg.tag_with_posterior(list(toks))
            po = pp.parse(list(toks), cats, tpost)
            heads = dict(po.heads)
            marg = po.marginals or {}
            conf = {i: float((marg.get(i) or {}).get(h, 1.0 if not marg else 0.0)) for i, h in heads.items()}
            rows.append({"toks": toks, "gpos": gpos, "gheads": {i + 1: h for i, h in enumerate(gheads)},
                         "rels": rels, "ppos": list(cats), "pheads": heads, "conf": conf,
                         "post": {i: {h: float(p) for h, p in d.items() if p >= 0.02} for i, d in marg.items()}})
        p = os.path.join(out_dir, "perc_%s.pkl" % name)
        with open(p, "wb") as f:
            pickle.dump(rows, f, protocol=4)
        print("[cache] %s: %d sentences in %.0fs -> %s" % (name, len(rows), time.time() - t0, p), flush=True)


def load_cache(out_dir, name):
    with open(os.path.join(out_dir, "perc_%s.pkl" % name), "rb") as f:
        return pickle.load(f)


# ----------------------------------------------------------------------------------------------- the learner
def lemma_frames_from(rows):
    """Verb-frame knowledge in COUNTS (per lemma: recipients out of nominal dependents), accrued from reading."""
    from hdlab.thematic_role_labeler import lemma_verb
    lf = defaultdict(lambda: [0, 0])
    for r in rows:
        toks, gpos, gh, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
        for i in range(1, len(toks) + 1):
            h = gh.get(i, 0)
            if gpos[i - 1] in GRA.NOMINAL and h and gpos[h - 1] in ("VERB", "AUX"):
                x = lf[lemma_verb(toks[h - 1]).lower()]
                x[1] += 1; x[0] += int((rels[i - 1] or "").split(":")[0] == "iobj")
    return {k: v for k, v in lf.items() if v[1] >= 5}


def slot_capacity_from(rows, classes):
    n1, n2 = Counter(), Counter()
    for r in rows:
        toks, gpos, gh, rels = r["toks"], r["gpos"], r["gheads"], r["rels"]
        by = {}
        for i in range(1, len(toks) + 1):
            h = gh.get(i, 0)
            if gpos[i - 1] in GRA.NOMINAL and h and gpos[h - 1] in ("VERB", "AUX"):
                by.setdefault(h, []).append(coarse_of(rels[i - 1], classes))
        for h, rr in by.items():
            sc = Counter(GRA.ROLE_TO_SLOT.get(x) for x in rr if GRA.ROLE_TO_SLOT.get(x))
            for s, c in sc.items():
                n1[s] += 1
                if c >= 2:
                    n2[s] += 1
    return {s: [int(n1[s]), int(n2[s])] for s in GRA.CORE_SLOTS}


POST_MIN_P = 0.05


_PREDH = ("VERB", "AUX", "ADJ", "ADV")


def _converges(toks, pos, heads, i):
    """CUE-CONVERGENCE RELIABILITY (gold-free): does the governor's arc agree with the arc-free licensor about the ONE
    thing this decision turns on -- predicate host or nominal host? Disagreement means the experience is unreliable
    for THIS contrast whatever the governor's confidence was (Ernst & Banks 2002 reliability weighting, applied to
    agreement between two cues rather than to one cue's own confidence)."""
    h = heads.get(i, 0) or 0
    hc = pos[h - 1] if 1 <= h <= len(pos) else "ROOT"
    hs = host_surface(toks, pos, i)
    if hs == "none":
        return True
    surf_pred = hs[1:] in _PREDH
    return (hc in _PREDH) == surf_pred


def build_counts(rows, classes, gen, poss="NMOD", min_conf=MIN_CONF, perceived=True, hostsurf=False,
                 post_accrual=False, converge_gate=False, brk=False, relcl=False, vprep=False, edge=False):
    """Accrue the Competition-Model counts from READING: for every argument-head nominal the governor believed it
    attached (reliability gate), one decision teaches the configuration and every fired cue value.

    post_accrual=True: LEARN OVER THE GOVERNOR'S POSTERIOR, NOT ITS MAP HEAD. The configuration cue IS the licensing
    host's category, so when the governor mis-attaches, the labels rung is taught the WRONG host category with full
    weight -- the single largest loss measured here (an oracle-trained table reaches gold-heads nmod 0.855 / obl 0.905
    where the MAP-trained one reaches 0.685 / 0.788). The brain's own hand-off down the chain is GRADED, and
    consolidating a latent-cause belief means accruing EXPECTED sufficient statistics under the posterior, not under
    a hard pick (Dempster/Laird/Rubin's E-step; Courville, Daw & Touretzky 2006 for credit assignment over a posterior
    of latent causes). So one comprehension decision teaches every candidate configuration in proportion to
    P(head = h | dependent), the arm's own exact single-root marginal. Reading stays on the MAP head (pri 103 measured
    that marginalising the READ loses, because the posterior is broad and mis-centred; this is the other direction --
    the learner is an expectation, not a decision)."""
    K = len(classes); ix = {r: k for k, r in enumerate(classes)}
    cfg_c = defaultdict(lambda: [0.0] * K)
    cue_c = defaultdict(lambda: defaultdict(lambda: [0.0] * K))
    prior = [0.0] * K; dec = 0.0
    lf = lemma_frames_from(rows)
    for r in rows:
        toks, gpos, rels = r["toks"], r["gpos"], r["rels"]
        pos = r["ppos"] if perceived else gpos
        heads = r["pheads"] if perceived else r["gheads"]
        conf = r["conf"] if perceived else None
        post = r.get("post") if (perceived and post_accrual) else None
        for i in range(1, len(toks) + 1):
            if not GRA.is_arg_head(toks, gpos, i):
                continue
            w = float(conf.get(i, 0.0)) if conf is not None else 1.0
            if w <= 0 or (conf is not None and w < min_conf):
                continue
            if converge_gate and conf is not None and not _converges(toks, pos, heads, i):
                continue
            dec += w
            g = ix[coarse_of(rels[i - 1], classes, poss)]
            prior[g] += w
            if post is not None:
                cand = {h: p for h, p in (post.get(i) or {}).items() if p >= POST_MIN_P and h != i}
                tot = sum(cand.values())
            else:
                cand, tot = {}, 0.0
            if tot <= 0:
                cand, tot = {heads.get(i, 0): 1.0}, 1.0
            for h, p in cand.items():
                if p == 1.0 and len(cand) == 1:
                    hh = heads
                else:
                    hh = dict(heads); hh[i] = int(h)
                cu = cues_of(toks, pos, hh, i, lf, True, conf, gen, hostsurf, brk, relcl, vprep, edge)
                ww = w * (p / tot)
                cfg = cu["config"]; cfg_c[cfg][g] += ww
                for c, v in cu.items():
                    if c != "config":
                        cue_c[c][f"{cfg}|{v}"][g] += ww
    return {"prior": prior, "config": dict(cfg_c),
            "cues": {c: dict(v) for c, v in cue_c.items()},
            "slot_capacity": slot_capacity_from(rows, classes),
            "_decisions": dec, "_lemma_frames": lf}


def table_from_counts(counts, classes):
    with role_space(classes, DEP8):
        b = GRA.strengths_from_counts({k: v for k, v in counts.items() if not k.startswith("_")})
    return {"prior": b["prior"], "strength": b["strength"], "counts": counts,
            "lemma_frames": counts.get("_lemma_frames", {}), "cue_set": "v4" if True else "v3",
            "slot_capacity": counts.get("slot_capacity")}


def twin_table(tab, seed=17):
    """INFO-FREE TWIN: the learned strength VECTORS permuted across the cue VALUES of every cue (config included).
    The whole competition machinery runs, on a destroyed value->role mapping."""
    rng = np.random.default_rng(seed); st = {}
    for c, vals in tab["strength"].items():
        keys = list(vals.keys()); perm = list(rng.permutation(len(keys)))
        st[c] = {keys[j]: vals[keys[perm[j]]] for j in range(len(keys))}
    return {"prior": tab["prior"], "strength": st, "counts": tab.get("counts"),
            "lemma_frames": tab.get("lemma_frames"), "cue_set": tab.get("cue_set"),
            "slot_capacity": tab.get("slot_capacity")}


# ----------------------------------------------------------------------------------------------- the reader
def label_sent(toks, pos, heads, tab, classes, deps, gen, conf=None, hostsurf=False, brk=False, relcl=False, vprep=False, edge=False):
    """The organ's read, with the cell's class space: additive cue activation -> MAP (GRA's own supports math)."""
    out = {}
    for i in range(1, len(toks) + 1):
        if i - 1 >= len(pos) or not GRA.is_arg_head(toks, pos, i):
            continue
        cu = cues_of(toks, pos, heads, i, tab.get("lemma_frames"), True, conf, gen, hostsurf, brk, relcl, vprep, edge)
        S = {"prior": tab["prior"]}
        cfg = cu["config"]
        v = tab["strength"].get("config", {}).get(cfg)
        if v is not None:
            S["config"] = v
        for c, val in cu.items():
            if c == "config":
                continue
            v = tab["strength"].get(c, {}).get(f"{cfg}|{val}")
            if v is not None:
                S[c] = v
        A = np.asarray(net_activation(S, {c: 1.0 for c in S}), dtype=float)
        out[i] = deps[classes[int(np.argmax(A[:len(classes)]))]]
    return out


def read_all(rows, tab, classes, deps, gen, heads_source, hostsurf=False, brk=False, relcl=False, vprep=False, edge=False):
    """heads_source: 'gold' (the labels rung's own ceiling) | 'live' (the frontend Parser's in-order tree)."""
    preds = []
    for r in rows:
        toks = r["toks"]
        if heads_source == "gold":
            pos, heads, conf = r["gpos"], r["gheads"], None
        else:
            pos, heads, conf = r["ppos"], r["pheads"], r["conf"]
        preds.append(label_sent(toks, pos, heads, tab, classes, deps, gen, conf, hostsurf, brk, relcl, vprep, edge))
    return preds


# ----------------------------------------------------------------------------------------------- metrics
NMOD_SUB = ("nmod", "nmod:poss", "nmod:unmarked", "nmod:desc")
OBL_SUB = ("obl", "obl:unmarked", "obl:agent")
EXPRESSIBLE = ("nsubj", "obj", "iobj", "obl", "nmod")


def populations(rows):
    """Per-item (sentence, token) membership of every measured population, from the GOLD annotation only."""
    pops = defaultdict(list)
    for si, r in enumerate(rows):
        toks, gpos, rels = r["toks"], r["gpos"], r["rels"]
        for i in range(1, len(toks) + 1):
            if gpos[i - 1] not in GRA.NOMINAL:
                continue
            g = rels[i - 1]; b = g.split(":")[0]
            key = (si, i)
            if b in EXPRESSIBLE:
                pops["all_expressible"].append(key)
            if b == "nmod":
                pops["nmod"].append(key); pops["obl_nmod"].append(key)
                pops["nmod_" + (g.split(":")[1] if ":" in g else "bare")].append(key)
            if b == "obl":
                pops["obl"].append(key); pops["obl_nmod"].append(key)
            if b in ("nsubj", "obj", "iobj") or g in ("nsubj:pass", "obl:agent"):
                pops["core"].append(key)
    return pops


def score(rows, preds, pops):
    """Correct iff the emitted relation equals the gold relation at the labeler's own granularity (base relation,
    keeping nsubj:pass / obl:agent). A gold nmod scored against an emitted `obl` or `dep` is WRONG -- that is the
    defect being measured."""
    ok = {}
    for si, r in enumerate(rows):
        pr = preds[si]; rels = r["rels"]
        for i in range(1, len(r["toks"]) + 1):
            ok[(si, i)] = int(norm(pr.get(i, "dep")) == norm(rels[i - 1]))
    return {k: np.array([ok.get(it, 0) for it in items], dtype=float) for k, items in pops.items()}


def boot(a, b, n=4000, seed=20260914):
    """Paired bootstrap over ITEMS of the same population."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed); d = b - a
    idx = rng.integers(0, len(d), size=(n, len(d)))
    s = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def confusion(rows, preds, base):
    c = Counter()
    for si, r in enumerate(rows):
        for i in range(1, len(r["toks"]) + 1):
            if r["gpos"][i - 1] not in GRA.NOMINAL:
                continue
            g = r["rels"][i - 1].split(":")[0]
            if g == base:
                c[norm(preds[si].get(i, "dep"))] += 1
    return c


# ----------------------------------------------------------------------------------------------- self test
def self_test():
    fails = []

    def ck(name, cond, detail=""):
        print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else "  " + str(detail)))
        if not cond:
            fails.append(name)

    # 1. the defect the brief names, reproduced on the SHIPPED organ: no nmod in the emittable set
    ck("shipped ROLE_TO_DEP cannot emit nmod", "nmod" not in set(GRA.ROLE_TO_DEP.values()), GRA.ROLE_TO_DEP)
    # 2. the genitive cue
    t = "John 's hat".split(); p = ["PROPN", "PART", "NOUN"]
    ck("genitive clitic fires on the possessor", genitive_value(t, p, 1) == "gen_clitic", genitive_value(t, p, 1))
    ck("genitive clitic does not fire on the head noun", genitive_value(t, p, 3) is None)
    t = "her hat fell".split(); p = ["PRON", "NOUN", "VERB"]
    ck("possessive pronoun fires pre-nominally", genitive_value(t, p, 1) == "gen_pron")
    t = "I saw her .".split(); p = ["PRON", "VERB", "PRON", "PUNCT"]
    ck("object 'her' before punctuation is not genitive", genitive_value(t, p, 3) is None)
    # 3. class mapping
    ck("nmod:poss is a member of NMOD in the 8-class space", coarse_of("nmod:poss", ROLES8) == "NMOD")
    ck("obl stays OBL", coarse_of("obl", ROLES8) == "OBL" and coarse_of("obl:agent", ROLES8) == "BY_AGENT")
    ck("7-class space is unchanged", coarse_of("nmod", ROLES7) == "OBL" and coarse_of("nmod:poss", ROLES7) == "OTHER")
    # 4. scoring: a gold nmod labelled obl or dep is WRONG (the 0/489 fact)
    ck("scoring: obl for a gold nmod is wrong", norm("obl") != norm("nmod:poss"))
    ck("scoring: nmod for gold nmod:poss is right", norm("nmod") == norm("nmod:poss"))
    # 5. the strengths math is the organ's own, and padding a short asset cannot invent a class
    counts = {"prior": [10.0] * 7, "config": {"NOUN_post": [1.0] * 7}, "cues": {"case": {"NOUN_post|none": [1.0] * 7}}}
    with role_space(ROLES8, DEP8):
        b = GRA.strengths_from_counts(counts)
    ck("a 7-class asset keeps 7 live classes under the 8-class organ", len(b["prior"]) == 7, len(b["prior"]))
    print("\nself-test: %d failed" % len(fails))
    return 1 if fails else 0


# ----------------------------------------------------------------------------------------------- arms
def arms_for(tr, te, out_dir, sweep=False):
    """Build every arm's table ONCE from the accrued counts (the learner), then read TEST under gold and live heads."""
    arms = {}
    spec = [("floor", ROLES7, DEP7, False, False, {}),
            ("nmod", ROLES8, DEP8, False, False, {}),
            ("nmod_gen", ROLES8, DEP8, True, False, {}),
            ("nmod_gen_hs", ROLES8, DEP8, True, True, {}),
            ("nmod_gen_post", ROLES8, DEP8, True, False, {"post_accrual": True}),
            ("nmod_gen_hs_post", ROLES8, DEP8, True, True, {"post_accrual": True}),
            ("nmod_gen_hs_conv", ROLES8, DEP8, True, True, {"converge_gate": True}),
            ("nmod_gen_hs_brk", ROLES8, DEP8, True, True, {"brk": True}),
            ("nmod_gen_brk", ROLES8, DEP8, True, False, {"brk": True}),
            ("nmod_gen_hsm", ROLES8, DEP8, True, "marked", {}),
            ("nmod_gen_hsm_rel", ROLES8, DEP8, True, "marked", {"relcl": True}),
            ("nmod_gen_hsm_rel_vp", ROLES8, DEP8, True, "marked", {"relcl": True, "vprep": True}),
            ("FULL", ROLES8, DEP8, True, "marked", {"relcl": True, "vprep": True, "edge": True})]
    if sweep:
        spec += [("nmod_gen_possOTHER", ROLES8, DEP8, True, False, {"poss": "OTHER"}),
                 # UPSTREAM ORACLE ABLATION (diagnostic, NOT shippable: it reads the gold tree at learning time) --
                 # it separates the loss the CUE SET carries from the loss the perceived-heads LEARNING rung carries.
                 ("nmod_gen_goldtrain", ROLES8, DEP8, True, False, {"perceived": False}),
                 ("nmod_gen_hs_goldtrain", ROLES8, DEP8, True, True, {"perceived": False}),
                 ("nmod_gen_nogate", ROLES8, DEP8, True, False, {"min_conf": 0.0}),
                 ("nmod_gen_gate08", ROLES8, DEP8, True, False, {"min_conf": 0.8}),
                 ("nmod_hs_only", ROLES8, DEP8, False, True, {})]
    only = [a for a in argv_arms() if a]
    for name, classes, deps, gen, hs, kw in spec:
        if only and name not in only and name != "floor":
            continue
        t0 = time.time()
        arms[name] = (classes, deps, gen, hs, bool(kw.get("brk")), bool(kw.get("relcl")), bool(kw.get("vprep")),
                      bool(kw.get("edge")), build_counts(tr, classes, gen=gen, hostsurf=hs, **kw))
        print("[build] %s %.0fs" % (name, time.time() - t0), flush=True)
    return arms


_ARMS_ONLY = []


def argv_arms():
    return _ARMS_ONLY


def diag(tr, te, pops, out_dir):
    """THE SIGNAL-LOSS TRACE, chain by chain, with counts."""
    o = {}
    # (1) HOW PEAKED IS THE GOVERNOR'S POSTERIOR? -- why learning over it changes nothing.
    ps, share = [], []
    for r in te:
        for i, h in r["pheads"].items():
            d = r.get("post", {}).get(i) or {}
            if not d:
                continue
            ps.append(float(d.get(h, 0.0)))
            share.append(len([1 for p in d.values() if p >= POST_MIN_P]))
    o["head_posterior"] = {"mean_P_MAP": round(float(np.mean(ps)), 4), "frac_P_MAP_ge_0.9": round(float(np.mean(np.array(ps) >= 0.9)), 4),
                           "mean_candidates_above_0.05": round(float(np.mean(share)), 3), "n": len(ps)}
    # (2) HOW MUCH EXPERIENCE THE CONVERGENCE GATE THROWS AWAY
    kept = tot = 0
    for r in tr:
        toks, gpos = r["toks"], r["gpos"]
        for i in range(1, len(toks) + 1):
            if not GRA.is_arg_head(toks, gpos, i):
                continue
            if float(r["conf"].get(i, 0.0)) < MIN_CONF:
                continue
            tot += 1; kept += int(_converges(toks, r["ppos"], r["pheads"], i))
    o["converge_gate"] = {"decisions_total": tot, "kept": kept, "discarded": tot - kept,
                          "frac_discarded": round((tot - kept) / max(tot, 1), 4)}
    # (3) THE LIVE obl -> nmod FLIPS: is the label wrong, or is the HEAD wrong?
    counts = build_counts(tr, ROLES8, gen=True, hostsurf="marked", relcl=True, vprep=True)
    tab = table_from_counts(counts, ROLES8)
    pred = read_all(te, tab, ROLES8, DEP8, True, "live", "marked", False, True, True)
    flip = {"obl_to_nmod": 0, "of_which_live_head_is_nominal": 0, "of_which_live_head_correct": 0,
            "obl_to_nmod_head_wrong": 0}
    for si, r in enumerate(te):
        for i in range(1, len(r["toks"]) + 1):
            if r["gpos"][i - 1] not in GRA.NOMINAL or r["rels"][i - 1].split(":")[0] != "obl":
                continue
            if norm(pred[si].get(i, "dep")) != "nmod":
                continue
            flip["obl_to_nmod"] += 1
            lh = r["pheads"].get(i, 0); gh = r["gheads"].get(i, 0)
            lc = r["ppos"][lh - 1] if 1 <= lh <= len(r["toks"]) else "ROOT"
            flip["of_which_live_head_is_nominal"] += int(lc in ("NOUN", "PROPN", "PRON", "NUM"))
            flip["of_which_live_head_correct"] += int(lh == gh)
            flip["obl_to_nmod_head_wrong"] += int(lh != gh)
    o["live_obl_to_nmod"] = flip
    # (4) THE BINARY READOUT: the 0.9813 host-category figure is a TWO-WAY readout on a population GIVEN to be
    # obl-or-nmod. Measure the organ the same way -- argmax restricted to {OBL, NMOD} on the same 932 tokens.
    kO, kN = ROLES8.index("OBL"), ROLES8.index("NMOD")
    ok = n = 0; okg = 0
    for si, r in enumerate(te):
        toks, gpos, gh = r["toks"], r["gpos"], r["gheads"]
        for i in range(1, len(toks) + 1):
            if gpos[i - 1] not in GRA.NOMINAL:
                continue
            b = r["rels"][i - 1].split(":")[0]
            if b not in ("obl", "nmod"):
                continue
            cu = cues_of(toks, gpos, gh, i, tab.get("lemma_frames"), True, None, True, "marked", False, True, True)
            S = {"prior": tab["prior"]}
            cfg = cu["config"]
            v = tab["strength"].get("config", {}).get(cfg)
            if v is not None:
                S["config"] = v
            for c, val in cu.items():
                if c == "config":
                    continue
                v = tab["strength"].get(c, {}).get(f"{cfg}|{val}")
                if v is not None:
                    S[c] = v
            A = np.asarray(net_activation(S, {c: 1.0 for c in S}), dtype=float)
            ok += int(("nmod" if A[kN] > A[kO] else "obl") == b); n += 1
            h = gh.get(i, 0); hc = gpos[h - 1] if 1 <= h <= len(toks) else "ROOT"
            okg += int(("obl" if hc in _PREDH else "nmod") == b)
    o["binary_readout_gold_heads"] = {"organ_restricted_to_OBL_vs_NMOD": round(ok / n, 4),
                                      "host_category_rule": round(okg / n, 4), "n": n}
    # (5) THE nmod RESIDUAL under gold heads, by what the organ said and what cue values it saw
    predg = read_all(te, tab, ROLES8, DEP8, True, "gold", "marked", False, True, True)
    res = Counter(); res_cfg = Counter()
    for si, r in enumerate(te):
        for i in range(1, len(r["toks"]) + 1):
            if r["gpos"][i - 1] not in GRA.NOMINAL or r["rels"][i - 1].split(":")[0] != "nmod":
                continue
            if norm(predg[si].get(i, "dep")) == "nmod":
                continue
            res[(r["rels"][i - 1], norm(predg[si].get(i, "dep")))] += 1
            cu = cues_of(r["toks"], r["gpos"], r["gheads"], i, tab.get("lemma_frames"), True, None, True, "marked", False, True, True)
            res_cfg[(cu["config"], cu["case"], cu["hostsurf"])] += 1
    o["nmod_residual_gold_heads"] = {"%s->%s" % k: v for k, v in res.most_common(12)}
    o["nmod_residual_cues"] = {"|".join(k): v for k, v in res_cfg.most_common(12)}
    with open(os.path.join(out_dir, "diag.json"), "w", encoding="utf-8") as f:
        json.dump(o, f, indent=1)
    print(json.dumps(o, indent=1))
    return 0


def main(argv):
    out_dir = str(get_output_dir(ANCHOR))
    os.makedirs(out_dir, exist_ok=True)
    if "--self-test" in argv:
        return self_test()
    if "--cache" in argv:
        build_cache(out_dir); return 0
    tr = load_cache(out_dir, "train"); te = load_cache(out_dir, "test")
    pops = populations(te)
    print("populations: " + "  ".join("%s=%d" % (k, len(v)) for k, v in sorted(pops.items())), flush=True)

    if "--diag" in argv:
        return diag(tr, te, pops, out_dir)
    if "--emit" in argv:
        counts = build_counts(tr, ROLES8, gen=True, hostsurf="marked", relcl=True, vprep=True, edge=True)
        lf = counts.pop("_lemma_frames"); dec = counts.pop("_decisions")
        with role_space(ROLES8, DEP8):
            b = GRA.strengths_from_counts(counts)
        doc = {"source": "Competition-Model cue validities with the NMOD class (a nominal licensed by a nominal) and the "
                         "ENGLISH GENITIVE as a case-cue value and the ARC-FREE LICENSOR cue (hostsurf); accrued from reading UD-EWT train perceived by the live "
                         "chain (hdlab.frontend: category organ -> attachment arm), reliability-weighted by the arm's own "
                         "P(MAP head) with a %.1f gate. Strengths = graded_role_assigner.strengths_from_counts(counts)." % MIN_CONF,
               "decisions": dec, "roles": ROLES8, "prior": [round(float(x), 4) for x in b["prior"]],
               "strength": {c: {v: [round(float(x), 4) for x in vec] for v, vec in vals.items()}
                            for c, vals in b["strength"].items()},
               "lemma_frames": lf, "counts": counts, "perceived": True, "confidence_weighted": True,
               "cue_set": "v4", "min_conf": MIN_CONF, "m_config_backoff": 0.0,
               "slot_capacity": counts.get("slot_capacity")}
        p = os.path.join(REPO, "data", "hook_state", "coarse_role_validities_pri108_v4.json")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1)
        print("wrote", p, "decisions=%.1f" % dec)
        return 0

    sweep = "--sweep" in argv
    global _ARMS_ONLY
    for a in argv:
        if a.startswith("--only="):
            _ARMS_ONLY = a.split("=", 1)[1].split(",")
    arms = arms_for(tr, te, out_dir, sweep=sweep)
    res = {}; acc = {}
    for name, (classes, deps, gen, hsf, bk, rc, vp, eg, counts) in arms.items():
        tab = table_from_counts(counts, classes)
        for hs in ("gold", "live"):
            preds = read_all(te, tab, classes, deps, gen, hs, hsf, bk, rc, vp, eg)
            acc[(name, hs)] = score(te, preds, pops)
            res[(name, hs, "conf_nmod")] = confusion(te, preds, "nmod")
            res[(name, hs, "conf_obl")] = confusion(te, preds, "obl")
        tw = twin_table(tab)
        for hs in ("gold", "live"):
            preds = read_all(te, tw, classes, deps, gen, hs, hsf, bk, rc, vp, eg)
            acc[(name + "_twin", hs)] = score(te, preds, pops)
        print("[arm] %s done" % name, flush=True)

    out = {"populations": {k: len(v) for k, v in pops.items()}, "arms": {}, "deltas": {}, "confusion": {}}
    for (name, hs), sc in sorted(acc.items()):
        out["arms"]["%s|%s" % (name, hs)] = {k: round(float(v.mean()), 4) for k, v in sc.items()}
    for name in arms:
        for hs in ("gold", "live"):
            for k in acc[("floor", hs)]:
                d, lo, hi = boot(acc[("floor", hs)][k], acc[(name, hs)][k])
                out["deltas"]["%s|%s|%s" % (name, hs, k)] = [round(d, 4), round(lo, 4), round(hi, 4)]
    for k, v in res.items():
        out["confusion"]["%s|%s|%s" % k] = dict(v.most_common())
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)

    print("\n%-22s %-6s %8s %8s %8s %8s %8s" % ("arm", "heads", "nmod", "obl", "obl+nmod", "allexpr", "core"))
    for name in list(arms) + [n + "_twin" for n in arms]:
        for hs in ("gold", "live"):
            if (name, hs) not in acc:
                continue
            s = acc[(name, hs)]
            print("%-22s %-6s %8.4f %8.4f %8.4f %8.4f %8.4f" % (
                name, hs, s["nmod"].mean(), s["obl"].mean(), s["obl_nmod"].mean(),
                s["all_expressible"].mean(), s["core"].mean()))
    print("\nDELTAS vs floor (paired item bootstrap, 4000):")
    for key in sorted(out["deltas"]):
        n, hs, k = key.split("|")
        if n == "floor" or k not in ("nmod", "obl", "obl_nmod", "all_expressible", "core"):
            continue
        d, lo, hi = out["deltas"][key]
        print("  %-16s %-5s %-15s %+0.4f CI[%+0.4f,%+0.4f]%s" % (n, hs, k, d, lo, hi, "  CI-SEP" if lo > 0 or hi < 0 else ""))
    print("\nconfusion, gold nmod (gold heads): floor=%s" % dict(res[("floor", "gold", "conf_nmod")].most_common(5)))
    for n in arms:
        if n != "floor":
            print("   %-16s %s" % (n, dict(res[(n, "gold", "conf_nmod")].most_common(5))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
