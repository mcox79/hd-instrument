"""exp_labels_rung_to_live_consumers_v1 -- route the DEFAULT read's remaining NOT_BF consumers to the
brain-foundational LABELS RUNG (the ONE Competition-Model role organ) and to the competition's own belief.

PRIORITY 129 (notes/problems/three_default_read_consumers_still_call_the_supervised_arc_labeler_and_the_
fitted_parse_confidence_readout_.../PROBLEM.md).

THE DEFECT (measured here, --probe): on a DEFAULT annotation-free read of a modern GUM document two organs
the registry marks NOT_BF are imported DURING `SituationReader.read` -- `hdlab/arc_labeler.py` (a frozen
supervised averaged-perceptron relation labeler) and `hdlab/parse_confidence.py` (a frozen fitted logistic
readout).  The brief names three consumers; the probe finds FIVE call sites, and the FIRST importer is one
the brief does not name (`_commonnoun_appos_map`).

HOW THE BRAIN DOES THIS (the opening move).
  * A relation label is not a classifier run after the parse.  The role a dependent bears is decided by the
    SAME parallel cue competition that attaches it -- the Competition Model (Bates & MacWhinney 1989;
    MacWhinney 1987), cue strengths = VALIDITIES accrued from experience.  That organ exists:
    `hdlab.graded_role_assigner.coarse_roles` / `coarse_role_posterior`, validities learned from UD-EWT
    counts as configuration-conditioned contrasts.
  * The reliability of a decision is the deciding accumulator's OWN balance of evidence, not a logistic fitted
    afterwards on another parser's features (Kiani & Shadlen 2009: the accumulator that makes the choice
    carries the certainty; Ernst & Banks 2002 / Ma-Beck-Latham-Pouget 2006: a consumer weights an input by its
    reliability).  AND -- the organ's own documented lesson -- reliability belongs to THE DECISION THE CONSUMER
    READS.  The consumer here asks "is this token the verb's patient", so the reliability is the competition's
    PATIENT-CLASS BELIEF, and the slot is contested: one object slot, several nominal candidates
    (Vosse & Kempen 2000 competitive unification).  Hence the arm built here:

        p_conf = P(role(pick) in {OBJ, PASS_SUBJ})  x  P(pick wins the object slot | the verb's candidates)

    both factors the competition's own posterior, ZERO fitted parameters, plastic through the organ's own
    `observe_role_outcome` / `observe_margin_outcome` counts.
  * A copular predication is a PREDICATE SLOT filled by a non-verbal word whose tense the copula carries
    (Pustet 2003; Maienborn 2005 Kimian states; Bemis & Pylkkanen 2011 LATL property attribution).  That organ
    exists too: `hdlab.attachment_arm.predicate_sites` (graded), already unioned into the state reader through
    `state_pairs_from_slot` -- but the DETECTION set the reader binds holders on still comes off the
    perceptron's `cop` label.
  * Purpose-vs-complement is LEXICALIST CONSTRAINT SATISFACTION: the governing verb's stored subcategorization
    frame decides whether a following "to VP" unifies as a complement or is reanalysed as an adjunct
    (MacDonald, Pearlmutter & Seidenberg 1994; Trueswell 1996; Garnsey et al. 1997; Vosse & Kempen 2000).
    Built here as an ARM of the same competition: cue validities learned from UD-EWT TRAIN counts as
    configuration-conditioned contrasts, softmax over {complement, purpose}.  No new classifier family.

WHAT THIS CELL MEASURES (every arm: the shipped consumer as the FLOOR, an information-free TWIN, and a
bootstrap CI paired over the population's own resampling unit).
  --probe     the import probe + per-call-site call counts on N modern GUM documents.
  --identity  is the perceptron's output DISCARDED where `structural_patient_pick` reads it?  (byte-identity of
              the patient pick with `coarse_roles` substituted for `ArcLabeler.label`.)
  --patient   right-vs-wrong sensitivity (AUC) + selective accuracy of the patient reliability: the shipped
              fitted logistic vs the competition's patient belief vs belief x slot-competition vs twin.
  --goal      the purpose-vs-complement decision on the EXACT population `goal_register` branch 3 reaches:
              the perceptron deprel filter vs the Competition-Model arm (tau + cue set selected on a
              train-internal dev split, reported on UD-EWT TEST) vs majority / never / always / twin floors.
  --state     copular (HOLDER, PROPERTY) read-back: `cop` from the perceptron vs from the predicate slot vs
              dropping the label path entirely (the can-fail arm: if dropping it is flat, the perceptron was
              never load-bearing; if it loses, the replacement is necessary).
  --isa       the is-a edge map (`_commonnoun_appos_map`): perceptron appos+cop vs a BF construction+slot read,
              split by half, with an ORACLE-HEADS arm that locates the residual at the heads rung.
  --rows      the live reader's board rows (agent / patient / state on UD-EWT; coref / salience /
              common-noun on GUM) with the shipped consumers vs the BF routing, BOTH ARMS IN ONE PROCESS.

Glass-box, deterministic.  NO spaCy / nltk tagger / supervised parser / external LLM at inference.  The
purpose-cue validities are counts accrued OFFLINE from UD-EWT train (a static foundation asset, the same class
as `coarse_role_validities_ud_ewt.json` and `verb_subcat_frames_ud_ewt.json`) and carry an online observe path.
ASCII-only.  Writes ONLY to its own get_output_dir.

  .venv/Scripts/python.exe experiments/exp_labels_rung_to_live_consumers_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_labels_rung_to_live_consumers_v1.py            # FULL (bare == full)
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import tempfile
import time
import traceback

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir            # noqa: E402

ANCHOR = "labels_rung_to_live_consumers_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260915

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/frontend_assets/coarse_role_validities_ud_ewt.json
# KB_REFERENT: data/frontend_assets/verb_subcat_frames_ud_ewt.json
# KB_REFERENT: data/frontend_assets/arc_labeler_hashed_ud_ewt.json
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
LAB_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json")
PURPOSE_ASSET_NAME = "purpose_complement_validities_ud_ewt.json"
# the LANDED location strategy ships this to at integration (the verb_subcat_frames precedent); the cell owns
# the build and writes it into its OWN output directory.
PURPOSE_ASSET_LANDED = os.path.join(_REPO, "data/frontend_assets", PURPOSE_ASSET_NAME)

NOMINAL = ("NOUN", "PROPN", "PRON")
NOM2 = ("NOUN", "PROPN")
BE_FORMS = ("be", "is", "are", "was", "were", "been", "being", "'s", "'re")
PURPOSE_CLASSES = ["complement", "purpose"]


# ==================================================================================================
# shared helpers
# ==================================================================================================
def _auc(y, x):
    """Rank AUC with tie-averaging.  nan when one class is empty."""
    y = np.asarray(y); x = np.asarray(x, dtype=float)
    p = x[y == 1]; n = x[y == 0]
    if len(p) == 0 or len(n) == 0:
        return float("nan")
    allv = np.concatenate([p, n])
    order = allv.argsort()
    ranks = np.empty(len(allv), dtype=float)
    ranks[order] = np.arange(1, len(allv) + 1, dtype=float)
    g = collections.defaultdict(list)
    for v, r in zip(allv, ranks):
        g[v].append(r)
    avg = {v: float(np.mean(rs)) for v, rs in g.items()}
    ranks = np.array([avg[v] for v in allv])
    return float((ranks[:len(p)].sum() - len(p) * (len(p) + 1) / 2.0) / (len(p) * len(n)))


def _boot_paired(units, by_unit, stat, n_boot=2000, seed=SEED):
    """Paired bootstrap over RESAMPLING UNITS (sentence / chunk / document): stat(rows) -> float."""
    rng = np.random.default_rng(seed)
    vals = []
    u = list(units)
    for _ in range(int(n_boot)):
        pick = rng.integers(0, len(u), len(u))
        rows = [r for i in pick for r in by_unit[u[i]]]
        v = stat(rows)
        if v == v:
            vals.append(v)
    if not vals:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n_boot": 0}
    a = np.sort(np.array(vals, dtype=float))
    return {"mean": float(a.mean()), "lo": float(a[int(0.025 * len(a))]), "hi": float(a[int(0.975 * len(a))]),
            "half_width": float((a[int(0.975 * len(a))] - a[int(0.025 * len(a))]) / 2.0), "n_boot": len(a)}


def _load_ud(path, cap=None):
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    s = load_ud(path)
    return s[:cap] if cap else s


def _frontend():
    from hdlab import frontend as FE
    return FE.tagger(), FE.parser()


def _parse_one(tg, ps, toks):
    """The live shared frontend read of ONE sentence: categories (graded), heads, head posterior, margins."""
    up, tp = tg.tag_with_posterior(list(toks))
    o = ps.parse(list(toks), list(up), tag_posterior=tp)
    heads = {int(j): int(h) for j, h in o.heads.items()}
    hp = o.marginals or None
    conf = {j: float((hp or {}).get(j, {}).get(h, 1.0)) for j, h in heads.items()}
    marg = {int(j): float(m) for j, m in o.margins.items()}
    return list(up), tp, heads, hp, conf, marg


def _tag_matrix(tp, n, tags):
    if not tp:
        return None
    return np.array([[float(tp[i].get(t, 0.0)) for t in tags] for i in range(n)], dtype=float)


# ==================================================================================================
# THE BF REPLACEMENTS  (exactly the bodies the proposed hdlab patch lands)
# ==================================================================================================
def bf_patient_confidence(toks, pos, heads, head_post, conf, v, pk):
    """THE BRAIN-FOUNDATIONAL PATIENT RELIABILITY (replaces parse_confidence.calibrated_patient_confidence).

    P(pk is the patient of v) = P(role(pk) in {OBJ, PASS_SUBJ})  x  P(pk wins v's object slot).

    Factor 1 is the Competition-Model organ's own posterior for pk, MARGINALISED over the heads rung's
    P(head | dep) when the attachment arm hands one down (the graded hand-off).  Factor 2 is the slot-level
    competition: the verb's nominal candidates (its MAP dependents plus anything the head posterior gives it
    >= 0.05 mass) normalise their patient beliefs against each other -- one slot, many claimants
    (Vosse & Kempen competitive unification).  No logistic, no fitted weight, no relation labeler.
    """
    from hdlab import graded_role_assigner as GRA
    ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}

    def belief(c):
        hpd = (head_post or {}).get(c)
        p = (GRA.coarse_role_posterior_headmarg(list(toks), list(pos), heads, c, hpd, conf=conf) if hpd
             else GRA.coarse_role_posterior(list(toks), list(pos), heads, c, conf=conf))
        return float(p[ix["OBJ"]] + p[ix["PASS_SUBJ"]])

    n = len(toks)
    if not (1 <= pk <= n):
        return None
    pp = belief(pk)
    cands = [c for c in range(1, n + 1)
             if pos[c - 1] in NOMINAL and (heads.get(c) == v or (head_post or {}).get(c, {}).get(v, 0.0) >= 0.05)]
    if pk not in cands:
        cands.append(pk)
    tot = 0.0
    for c in cands:
        tot += belief(c) if c != pk else pp
    slot = (pp / tot) if tot > 0 else 0.0
    return float(pp * slot)


def bf_cop_predicates(toks, pos, tag_matrix, tag_names):
    """THE PREDICATE SLOT as the copular DETECTION set (replaces the perceptron's `cop` label).
    1-based indices of every NON-VERBAL token that holds its clause's predicate slot."""
    from hdlab import attachment_arm as AA
    if tag_matrix is None:
        return set()
    sites = AA.predicate_sites(list(toks), list(pos), tag_matrix, list(tag_names))
    return {q + 1 for q, s in sites.items() if pos[q] != "VERB" and s > 0.0}


def bf_holders_for(toks, pos, heads, head_post, cop_preds, graded_min=0.5):
    """extract_entity_states' HOLDER binding, driven by ANY `cop_preds` source and by the COMPETITION for the
    subject role (no relation labeler): the competition's SUBJ/PASS_SUBJ belief over the predicate's nominal
    dependents, with the convention-agnostic 'the predicate's own nominal head IS the holder' repair kept."""
    from hdlab import graded_role_assigner as GRA
    ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}
    n = len(toks)
    roles = GRA.coarse_roles(list(toks), list(pos), heads, head_posterior=head_post)
    subj_of = {}
    for d, rel in roles.items():
        if rel in ("nsubj", "nsubj:pass"):
            h = heads.get(d, 0)
            if h in cop_preds and h not in subj_of:
                subj_of[h] = d
    for pred in cop_preds:
        if pred in subj_of:
            continue
        h = heads.get(pred, 0)
        if h and 1 <= h <= n and pos[h - 1] in NOMINAL:
            subj_of[pred] = h
    for pred in cop_preds:
        if pred in subj_of:
            continue
        best, bp = None, 0.0
        for d in range(1, n + 1):
            hpd = (head_post or {}).get(d)
            if heads.get(d) == pred or (hpd and hpd.get(pred, 0.0) > 0.0):
                if pos[d - 1] not in NOMINAL:
                    continue
                p = (GRA.coarse_role_posterior_headmarg(list(toks), list(pos), heads, d, hpd) if hpd
                     else GRA.coarse_role_posterior(list(toks), list(pos), heads, d))
                pr = float(p[ix["SUBJ"]] + p[ix["PASS_SUBJ"]])
                if pr > bp:
                    best, bp = d, pr
        if best is not None and bp >= graded_min:
            subj_of[pred] = best
    return {(subj_of[p] - 1, p - 1) for p in sorted(cop_preds) if p in subj_of}


# ---------------- the PURPOSE / COMPLEMENT arm of the competition ---------------------------------
def _purpose_cues(toks, pos, low, i, mvi, heads):
    """(configuration, {cue: value}) for the 'to' at 0-based `i` governed by the verb at 0-based `mvi`.
    CONFIGURATION = the unification window between the governor and the infinitival marker (Vosse-Kempen);
    every cue is read from the categories organ, the attachment arm's heads, or the stored verb frame."""
    from hdlab import goal_register as GR
    from hdlab.verb_subcat_frames import SubcatFrames
    try:
        sc = SubcatFrames.load()
    except Exception:
        sc = None
    n = len(toks)
    mv = low[mvi]
    mvl = GR._lemma(mv)
    pc = None
    if sc is not None:
        pc = sc.p_complement(mv)
        if pc is None:
            pc = sc.p_complement(mvl)
    between = pos[mvi + 1:i]
    if not between:
        cfg = "adjacent"
    elif all(c in NOMINAL or c in ("DET", "ADJ", "NUM") for c in between):
        cfg = "objonly"
    elif any(c == "ADP" for c in between):
        cfg = "pp"
    else:
        cfg = "other"
    h = heads.get(i + 2, 0)
    c = {
        "frame": "na" if pc is None else ("hi" if pc >= 0.7 else "mid" if pc >= 0.4 else "lo"),
        "prev": pos[i - 1] if i - 1 >= 0 else "NONE",
        "dist": "0" if (i - mvi) == 1 else "1" if (i - mvi) == 2 else "2" if (i - mvi) <= 4 else "3+",
        "headcat": (pos[h - 1] if h and 1 <= h <= n else "ROOT"),
        "headismv": "1" if h == mvi + 1 else "0",
        "post": "end" if (i + 2 >= n or all(pos[k] == "PUNCT" for k in range(i + 2, n)))
                else pos[min(i + 2, n - 1)],
        "mvlem": mvl,
        "hasobj": "1" if any(pos[k] in NOMINAL for k in range(mvi + 1, i)) else "0",
        "comma": "1" if (i - 1 >= 0 and low[i - 1] == ",") else "0",
    }
    return cfg, c


def purpose_sites(sents, tg, ps, with_gold=True):
    """Every 'to VINF' site that `goal_register.extract_goals_sentence` branch (3) actually REACHES -- the
    entry gate replicated verbatim, so the population is the consumer's own."""
    from hdlab import goal_register as GR
    from hdlab.verb_subcat_frames import SubcatFrames
    try:
        sc = SubcatFrames.load()
    except Exception:
        sc = None
    out = []
    for si, s in enumerate(sents):
        toks = [t["form"] for t in s]
        n = len(toks)
        if n < 3 or n > 80:
            continue
        low = [t.lower() for t in toks]
        up, tp = tg.tag_with_posterior(toks)
        if not any(low[k] == "to" and k + 1 < n and up[k + 1] == "VERB" for k in range(1, n - 1)):
            continue
        o = ps.parse(toks, list(up), tag_posterior=tp)
        heads = {int(j): int(h) for j, h in o.heads.items()}
        hp = o.marginals or None
        gold = {t["id"]: t["deprel"] for t in s} if with_gold else {}
        for i in range(1, n - 1):
            if low[i] != "to" or not (i + 1 < n and up[i + 1] == "VERB"):
                continue
            if low[i - 1] in ("order", "as"):
                continue
            mvi = None
            for j in range(i - 1, -1, -1):
                if up[j] == "VERB":
                    mvi = j
                    break
                if low[j] in (".", ";", ":", "!", "?"):
                    break
            if mvi is None:
                continue
            mv = low[mvi]
            mvl = GR._lemma(mv)
            adjacent = (mvi == i - 1)
            if GR._is_extraposed(toks, list(up), i, sc):
                continue
            if mv in GR.GOAL_VERBS or mvl in GR.GOAL_VERBS:
                continue
            if adjacent and sc is not None and (sc.is_complement_taker(mv) or sc.is_complement_taker(mvl)):
                continue
            gd = (gold.get(i + 2, "") or "").split(":")[0]
            g = ("purpose" if gd == "advcl" else
                 "complement" if gd in ("xcomp", "ccomp", "acl", "csubj") else None)
            cfg, cues = _purpose_cues(toks, list(up), low, i, mvi, heads)
            out.append({"sid": si, "gold": g, "cfg": cfg, "cues": cues, "to": i,
                        "inf1": i + 2, "toks": toks, "pos": list(up), "heads": heads, "hp": hp})
    return out


def purpose_learn(rows, alpha=1.0, min_count=3, drop=()):
    """Cue VALIDITIES as configuration-conditioned CONTRASTS accrued from counts -- the exact discipline of
    `graded_role_assigner.strengths_from_counts`: strength(cue=value)[k] = log P(k | cfg, value) - log P(k | cfg).
    A cue value never seen enough times contributes NOTHING (it abstains).  Counts are the asset; they are a
    pure function of observations, so `purpose_observe` can keep accruing online."""
    prior = collections.Counter(r["gold"] for r in rows if r["gold"])
    tot = sum(prior.values())
    P = [float(np.log((prior[k] + alpha) / (tot + alpha * len(PURPOSE_CLASSES)))) for k in PURPOSE_CLASSES]
    cfg_counts = collections.defaultdict(collections.Counter)
    cue_counts = collections.defaultdict(collections.Counter)
    for r in rows:
        if not r["gold"]:
            continue
        cfg_counts[r["cfg"]][r["gold"]] += 1
        for cn, cv in r["cues"].items():
            if cn in drop:
                continue
            cue_counts["%s|%s|%s" % (cn, r["cfg"], cv)][r["gold"]] += 1
    cfg = {}
    for k, cc in cfg_counts.items():
        t = sum(cc.values())
        cfg[k] = [float(np.log((cc[c] + alpha) / (t + alpha * len(PURPOSE_CLASSES)))) for c in PURPOSE_CLASSES]
    strength = {}
    for key, cc in cue_counts.items():
        t = sum(cc.values())
        if t < min_count:
            continue
        base = cfg.get(key.split("|")[1]) or P
        strength[key] = [float(np.log((cc[c] + alpha) / (t + alpha * len(PURPOSE_CLASSES))) - base[ci])
                         for ci, c in enumerate(PURPOSE_CLASSES)]
    return {"classes": PURPOSE_CLASSES, "alpha": float(alpha), "min_count": int(min_count),
            "dropped_cues": list(drop), "tau": 0.55,
            "prior": P, "cfg": cfg, "strength": strength,
            "counts": {"cfg": {k: dict(v) for k, v in cfg_counts.items()},
                       "cue": {k: dict(v) for k, v in cue_counts.items()}},
            "source": "P(complement|purpose) cue contrasts accrued from UD-EWT train counts on the population "
                      "goal_register branch (3) reaches; plastic -- see purpose_observe."}


def purpose_p_complement(tab, cfg, cues):
    """Additive cue competition -> softmax over {complement, purpose} (Lewis-Vasishth activation; McClelland
    2013 softmax = the Bayesian posterior).  Returns P(complement)."""
    from hdlab.graded_competition import softmax
    A = np.array(tab["cfg"].get(cfg) or tab["prior"], dtype=float)
    for cn, cv in cues.items():
        v = tab["strength"].get("%s|%s|%s" % (cn, cfg, cv))
        if v is not None:
            A = A + np.array(v, dtype=float)
    return float(softmax(A, gain=1.0)[0])


def purpose_observe(tab, cfg, cues, outcome):
    """PLASTICITY: accrue ONE confirmed comprehension outcome ('complement' / 'purpose') into the counts and
    recompute the strengths.  Nothing in this arm is frozen."""
    cc = tab["counts"]["cfg"].setdefault(cfg, {})
    cc[outcome] = cc.get(outcome, 0) + 1
    for cn, cv in cues.items():
        k = "%s|%s|%s" % (cn, cfg, cv)
        d = tab["counts"]["cue"].setdefault(k, {})
        d[outcome] = d.get(outcome, 0) + 1
    rows = []           # rebuild the strengths from the counts (a pure function of the counts)
    a = tab["alpha"]
    tot = sum(sum(v.values()) for v in [tab["counts"]["cfg"][k] for k in tab["counts"]["cfg"]])
    pri = collections.Counter()
    for v in tab["counts"]["cfg"].values():
        for c, x in v.items():
            pri[c] += x
    tab["prior"] = [float(np.log((pri[c] + a) / (max(1, tot) + a * len(PURPOSE_CLASSES))))
                    for c in PURPOSE_CLASSES]
    for k, v in tab["counts"]["cfg"].items():
        t = sum(v.values())
        tab["cfg"][k] = [float(np.log((v.get(c, 0) + a) / (t + a * len(PURPOSE_CLASSES))))
                         for c in PURPOSE_CLASSES]
    tab["strength"] = {}
    for k, v in tab["counts"]["cue"].items():
        t = sum(v.values())
        if t < tab["min_count"]:
            continue
        base = tab["cfg"].get(k.split("|")[1]) or tab["prior"]
        tab["strength"][k] = [float(np.log((v.get(c, 0) + a) / (t + a * len(PURPOSE_CLASSES))) - base[ci])
                              for ci, c in enumerate(PURPOSE_CLASSES)]
    del rows
    return tab


# ==================================================================================================
# ARM 1 -- the import probe + per-call-site counts
# ==================================================================================================
def notbf_modules():
    """The registry's NOT_BF module set, as importable dotted names."""
    out = set()
    with open(os.path.join(_REPO, "notes/bf_status_registry.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            if r.get("status") == "NOT_BF":
                out.add(r["module"].replace("hdlab/", "hdlab.").replace(".py", ""))
    return out


def import_probe(n_docs=1, smoke=False):
    """PASS A -- which hdlab modules are FIRST imported DURING `SituationReader.read`?

    The probe is a `sys.meta_path` finder, NOT a `builtins.__import__` hook: the hook MISSES
    `from hdlab import parse_confidence`, which passes the name 'hdlab' (that is exactly why the brief's
    one-document probe reported `parse_confidence` and the naive re-probe did not).  NOTHING that the probe
    itself needs may import a watched module before the read -- so the counters live in PASS B."""
    import importlib.abc
    phase = ["import"]
    first = {}

    class _Probe(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path=None, target=None):
            if name.startswith("hdlab") or name.split(".")[0] in ("nltk", "spacy"):
                if name not in first:
                    st = [f for f in traceback.extract_stack()[:-1]
                          if ("hdlab" in f.filename or "experiments" in f.filename)]
                    first[name] = {"phase": phase[0],
                                   "stack": " <- ".join("%s:%d:%s" % (os.path.basename(f.filename), f.lineno,
                                                                      f.name) for f in reversed(st[-8:]))}
            return None

    probe = _Probe()
    sys.meta_path.insert(0, probe)
    per_doc = []
    try:
        from experiments.exp_board_rows_on_the_reader_v1 import _gum_test_docs, _write_two_conll
        from hdlab.situation_reader import SituationReader
        docs, gaz = _gum_test_docs(n_docs=n_docs, prefix=bool(smoke))
        tmp = tempfile.mkdtemp(prefix="p129probeA_")
        for d in docs[:n_docs]:
            phase[0] = "pre"
            _p_ann, p_txt, _p_prn = _write_two_conll(d, tmp)
            phase[0] = "construct"
            rdr = SituationReader(gaz=gaz)
            phase[0] = "READ"
            t0 = time.time()
            sm = rdr.read(p_txt)
            per_doc.append({"docid": d.docid, "events": len(sm.events),
                            "entity_states": len(sm.entity_states or []),
                            "read_s": round(time.time() - t0, 2)})
    finally:
        sys.meta_path = [m for m in sys.meta_path if m is not probe]
    notbf = notbf_modules()
    during = sorted(k for k in first if k in notbf and first[k]["phase"] == "READ")
    return {"n_docs": len(per_doc), "per_doc": per_doc, "notbf_registry": sorted(notbf),
            "notbf_imported_during_read": during,
            "first_import": {k: first[k] for k in sorted(first) if k in notbf}}


def call_site_probe(n_docs=4, smoke=False):
    """PASS B -- WHICH CALL SITES drive the NOT_BF organs, and how often, on a default read."""
    from experiments.exp_board_rows_on_the_reader_v1 import _gum_test_docs, _write_two_conll
    from hdlab.situation_reader import SituationReader
    from hdlab.arc_labeler import ArcLabeler
    from hdlab import parse_confidence as PC
    counts = collections.Counter()

    def _site():
        for f in reversed(traceback.extract_stack()[:-2]):
            b = os.path.basename(f.filename)
            if b in ("situation_reader.py", "copular_binding.py", "predicate_argument_frontend.py",
                     "entity_resolver.py", "goal_register.py"):
                return "%s:%s" % (b, f.name)
        return "?"

    _ol = ArcLabeler.label
    _op = PC.calibrated_patient_confidence

    def _lab(self, *a, **k):
        counts["ArcLabeler.label @ " + _site()] += 1
        return _ol(self, *a, **k)

    def _pc(*a, **k):
        counts["parse_confidence.calibrated_patient_confidence @ " + _site()] += 1
        return _op(*a, **k)

    ArcLabeler.label = _lab
    PC.calibrated_patient_confidence = _pc
    per_doc = []
    try:
        docs, gaz = _gum_test_docs(n_docs=n_docs, prefix=bool(smoke))
        tmp = tempfile.mkdtemp(prefix="p129probeB_")
        for d in docs[:n_docs]:
            _a, p_txt, _p = _write_two_conll(d, tmp)
            t0 = time.time()
            sm = SituationReader(gaz=gaz).read(p_txt)
            per_doc.append({"docid": d.docid, "events": len(sm.events), "read_s": round(time.time() - t0, 2)})
    finally:
        ArcLabeler.label = _ol
        PC.calibrated_patient_confidence = _op
    return {"n_docs": len(per_doc), "per_doc": per_doc, "call_sites": dict(counts)}


def run_probe(n_docs=16, smoke=False, count_docs=4):
    a = import_probe(n_docs=n_docs, smoke=smoke)
    b = call_site_probe(n_docs=min(count_docs, n_docs), smoke=smoke)
    a["call_sites"] = b["call_sites"]
    a["call_site_docs"] = b["per_doc"]
    return a


# ==================================================================================================
# ARM 2 -- is the perceptron's output DISCARDED where structural_patient_pick reads it?
# ==================================================================================================
def run_identity(cap=None):
    from hdlab import graded_role_assigner as GRA
    from hdlab import predicate_argument_frontend as PAF
    from hdlab.relcl_resolver import precise_passive
    tg, ps = _frontend()
    sents = _load_ud(UD_TEST, cap)
    n_pick = n_same = n_lab_diff = 0
    diffs = []
    for s in sents:
        toks = [t["form"] for t in s]
        n = len(toks)
        if n < 2 or n > 80:
            continue
        up, _tp, heads, _hp, _conf, _marg = _parse_one(tg, ps, toks)
        lab_full = PAF._labeler().label(list(toks), list(up), heads)
        cm = GRA.coarse_roles(list(toks), list(up), heads)
        for v in PAF.matrix_verbs(toks, up, heads):
            pp = precise_passive(toks, up, v)
            a = PAF.labeled_pick(toks, up, v, heads, lab_full, pp, valency=True)
            b = PAF.labeled_pick(toks, up, v, heads, cm, pp, valency=True)
            n_pick += 1
            n_same += int(a == b)
        for i in range(1, n + 1):
            la = lab_full.get(i, "")
            lb = cm.get(i, "")
            if (la in ("obj", "nsubj:pass")) != (lb in ("obj", "nsubj:pass")):
                n_lab_diff += 1
                if len(diffs) < 20:
                    diffs.append({"tok": toks[i - 1], "pos": up[i - 1], "perceptron": la, "competition": lb})
    return {"matrix_verb_picks": n_pick, "identical_picks": n_same,
            "pick_identity": (n_same / n_pick) if n_pick else float("nan"),
            "tokens_membership_differs": n_lab_diff, "examples": diffs,
            "verdict": ("the perceptron's label is DISCARDED for every relation structural_patient_pick reads"
                        if n_pick and n_same == n_pick else "NOT identical -- see examples")}


# ==================================================================================================
# ARM 3 -- the patient reliability
# ==================================================================================================
def run_patient(cap=None, n_boot=2000, seed=SEED):
    from experiments.exp_board_rows_on_the_reader_v1 import _gold_patient_items
    from hdlab import parse_confidence as PC
    from hdlab import graded_role_assigner as GRA
    from hdlab.predicate_argument_frontend import structural_patient_pick
    from hdlab.relcl_resolver import precise_passive
    from hdlab.arc_labeler import ArcLabeler
    tg, ps = _frontend()
    lab = ArcLabeler.load(LAB_ASSET)
    ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}
    sents = _load_ud(UD_TEST, cap)
    rows = []
    for si, s in enumerate(sents):
        toks = [t["form"] for t in s]
        n = len(toks)
        if n < 2 or n > 80:
            continue
        up, _tp, heads, hp, conf, marg = _parse_one(tg, ps, toks)
        labels = lab.label(toks, up, heads, head_posterior=hp)
        for (v, pat, _pz) in _gold_patient_items(s):
            pick = structural_patient_pick(toks, up, heads, v, np_head_reduce=True)
            if pick is None:
                continue
            passive = bool(precise_passive(toks, up, v))
            try:
                shipped = float(PC.calibrated_patient_confidence(toks, up, heads, conf, marg, v, pick,
                                                                 labels, passive, a2_marg=0.0))
            except Exception:
                shipped = 0.0
            hpd = (hp or {}).get(pick)
            p = (GRA.coarse_role_posterior_headmarg(toks, up, heads, pick, hpd, conf=conf) if hpd
                 else GRA.coarse_role_posterior(toks, up, heads, pick, conf=conf))
            m = GRA.role_margin(p)
            rows.append({
                "sid": si, "correct": int(pick == pat),
                "shipped_logistic": shipped,
                "competition_margin": float(m),
                "competition_margin_reliability": float(GRA.margin_reliability(m, "patient")),
                "attachment_marginal": float((hpd or {}).get(v, conf.get(pick, 0.0))),
                "competition_patient_belief": float(p[ix["OBJ"]] + p[ix["PASS_SUBJ"]]),
                "bf_belief_x_slot": float(bf_patient_confidence(toks, up, heads, hp, conf, v, pick) or 0.0),
            })
    if not rows:
        return {"n": 0}
    ARMS = ("shipped_logistic", "competition_margin", "competition_margin_reliability",
            "attachment_marginal", "competition_patient_belief", "bf_belief_x_slot")
    y = [r["correct"] for r in rows]
    out = {"n_items": len(rows), "n_sentences_scored": len({r["sid"] for r in rows}),
           "blanket_accuracy": float(np.mean(y)),
           "auc": {a: _auc(y, [r[a] for r in rows]) for a in ARMS}}
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(rows))
    out["auc"]["twin_bf_permuted"] = _auc(y, [rows[i]["bf_belief_x_slot"] for i in perm])
    out["auc"]["twin_shipped_permuted"] = _auc(y, [rows[i]["shipped_logistic"] for i in perm])
    by = collections.defaultdict(list)
    for r in rows:
        by[r["sid"]].append(r)
    units = sorted(by)
    out["bootstrap_auc"] = {}
    out["paired_bootstrap_auc_MINUS_shipped"] = {}
    for a in ("competition_patient_belief", "bf_belief_x_slot", "competition_margin",
              "shipped_logistic"):
        out["bootstrap_auc"][a] = _boot_paired(
            units, by, lambda rs, a=a: _auc([r["correct"] for r in rs], [r[a] for r in rs]),
            n_boot=n_boot, seed=seed)
        if a == "shipped_logistic":
            continue
        # THE PAIRED DIFFERENCE (both arms scored on the SAME resampled items, the sentence the unit)
        out["paired_bootstrap_auc_MINUS_shipped"][a] = _boot_paired(
            units, by,
            lambda rs, a=a: (_auc([r["correct"] for r in rs], [r[a] for r in rs])
                             - _auc([r["correct"] for r in rs], [r["shipped_logistic"] for r in rs])),
            n_boot=n_boot, seed=seed)
    yy = np.array(y)
    out["selective_accuracy"] = {}
    for a in ("shipped_logistic", "competition_patient_belief", "bf_belief_x_slot"):
        x = np.array([r[a] for r in rows])
        o = np.argsort(-x)
        out["selective_accuracy"][a] = {("cov%d" % int(c * 100)):
                                        float(yy[o[:max(1, int(len(o) * c))]].mean())
                                        for c in (0.5, 0.67, 0.8)}
    return out


# ==================================================================================================
# ARM 4 -- the purpose / complement decision
# ==================================================================================================
def run_goal(cap_train=None, cap_test=None, n_boot=2000, seed=SEED):
    from hdlab import goal_register as GR
    from hdlab.arc_labeler import ArcLabeler
    tg, ps = _frontend()
    lab = ArcLabeler.load(LAB_ASSET)
    train_all = purpose_sites(_load_ud(UD_TRAIN, cap_train), tg, ps)
    test = purpose_sites(_load_ud(UD_TEST, cap_test), tg, ps)
    # train-INTERNAL dev split (no dev file ships with UD-EWT here): every 5th sentence index is dev
    fit = [r for r in train_all if (r["sid"] % 5) != 0]
    dev = [r for r in train_all if (r["sid"] % 5) == 0 and r["gold"]]
    gs = [r for r in test if r["gold"]]

    def acc(tab, rs, tau, drop=()):
        h = 0
        for r in rs:
            cu = {k: v for k, v in r["cues"].items() if k not in drop}
            h += int((purpose_p_complement(tab, r["cfg"], cu) >= tau) == (r["gold"] == "complement"))
        return h / max(1, len(rs))

    CUES = list(train_all[0]["cues"].keys()) if train_all else []
    grid = []
    for drop in [()] + [(c,) for c in CUES]:
        tab = purpose_learn(fit, drop=drop)
        for tau in (0.45, 0.50, 0.55, 0.60, 0.65, 0.70):
            grid.append({"drop": list(drop), "tau": tau, "dev_acc": acc(tab, dev, tau, drop)})
    best = max(grid, key=lambda g: (g["dev_acc"], -g["tau"]))
    tab = purpose_learn(fit, drop=tuple(best["drop"]))
    tab_full = purpose_learn(train_all, drop=tuple(best["drop"]))       # the SHIPPED asset: fit + dev
    drop = tuple(best["drop"])
    tau = best["tau"]

    # the perceptron deprel filter as it ships, on the same population
    for r in test:
        deprels = lab.label(r["toks"], r["pos"], r["heads"], head_posterior=r["hp"])
        dep = deprels.get(r["inf1"]) or ""
        r["percep_reject"] = dep in GR._COMPLEMENT_DEPREL
        r["percep_dep"] = dep
        cu = {k: v for k, v in r["cues"].items() if k not in drop}
        r["cm_p_complement"] = purpose_p_complement(tab_full, r["cfg"], cu)
        r["cm_reject"] = r["cm_p_complement"] >= tau

    rng = np.random.default_rng(seed)
    rate = float(np.mean([r["percep_reject"] for r in gs])) if gs else 0.0
    twin = {id(r): bool(b) for r, b in zip(gs, rng.random(len(gs)) < rate)}

    def score(fn):
        tp = sum(1 for r in gs if fn(r) and r["gold"] == "complement")
        fp = sum(1 for r in gs if fn(r) and r["gold"] == "purpose")
        fn_ = sum(1 for r in gs if not fn(r) and r["gold"] == "complement")
        tn = sum(1 for r in gs if not fn(r) and r["gold"] == "purpose")
        return {"accuracy": (tp + tn) / max(1, len(gs)), "reject_precision": tp / max(1, tp + fp),
                "reject_recall": tp / max(1, tp + fn_), "tp": tp, "fp": fp, "fn": fn_, "tn": tn}

    maj = collections.Counter(r["gold"] for r in gs).most_common(1)
    arms = {"perceptron_deprel_filter_SHIPPED": score(lambda r: r["percep_reject"]),
            "competition_purpose_arm_BF": score(lambda r: r["cm_reject"]),
            "floor_never_reject": score(lambda r: False),
            "floor_always_reject": score(lambda r: True),
            "twin_same_rate_random": score(lambda r: twin[id(r)])}
    by = collections.defaultdict(list)
    for r in gs:
        by[r["sid"]].append(r)
    units = sorted(by)

    def d_stat(rs):
        a1 = np.mean([int(r["cm_reject"] == (r["gold"] == "complement")) for r in rs])
        a0 = np.mean([int(r["percep_reject"] == (r["gold"] == "complement")) for r in rs])
        return float(a1 - a0)

    # AGREEMENT with the shipped filter (the no-regress read the goal witnesses care about)
    agree = float(np.mean([int(r["cm_reject"] == r["percep_reject"]) for r in gs])) if gs else float("nan")
    return {"n_train_sites": len(train_all), "n_fit": len(fit), "n_dev": len(dev),
            "n_test_sites": len(test), "n_test_decidable": len(gs),
            "test_class_counts": dict(collections.Counter(r["gold"] for r in gs)),
            "majority_floor": (maj[0][1] / len(gs)) if maj and gs else float("nan"),
            "selected_on_dev": best, "dev_grid_top5": sorted(grid, key=lambda g: -g["dev_acc"])[:5],
            "arms": arms, "agreement_with_shipped": agree,
            "paired_bootstrap_accuracy_bf_minus_shipped": _boot_paired(units, by, d_stat, n_boot, seed),
            "asset": {"name": PURPOSE_ASSET_NAME, "n_cue_strengths": len(tab_full["strength"]),
                      "landed_path": PURPOSE_ASSET_LANDED},
            "_table": tab_full}


# ==================================================================================================
# ARM 5 -- the copular detection source
# ==================================================================================================
def run_state(cap=None, n_boot=2000, seed=SEED):
    import experiments.exp_copular_is_a_binding_readout_v1 as COP
    from hdlab import copular_binding as CB
    from hdlab import attachment_arm as AA
    from hdlab import lexical_categories as LC
    from hdlab.arc_labeler import ArcLabeler
    tg, ps = _frontend()
    lab = ArcLabeler.load(LAB_ASSET)
    lc = LC.get()
    sents = _load_ud(UD_TEST, cap)
    ARMS = ("cop_from_perceptron_SHIPPED", "cop_from_predicate_slot_BF", "label_path_dropped")
    per = collections.defaultdict(lambda: collections.defaultdict(int))
    n_gold = 0
    sids = []
    for si, s in enumerate(sents):
        toks = [t["form"] for t in s]
        n = len(toks)
        if n < 2 or n > 80:
            continue
        tup = [(t["id"], t["form"], t["form"], t["upos"], "", t["head"], t["deprel"]) for t in s]
        gold = [(h, p, ty) for (h, p, ty) in COP.typed_gold(tup) if ty in ("pred_adj", "pred_nom")]
        if not gold:
            continue
        up, tp, heads, hp, _conf, _marg = _parse_one(tg, ps, toks)
        mat = _tag_matrix(tp, n, lc.tags)
        labels = lab.label(toks, up, heads, head_posterior=hp)
        cp_perc = {h for h in (heads.get(d, 0) for d, r in labels.items() if r == "cop") if 1 <= h <= n}
        cp_slot = bf_cop_predicates(toks, up, mat, lc.tags)
        base = CB.robust_cop(toks, up, heads, gate=True)
        if mat is not None:
            base = base | AA.state_pairs_from_slot(toks, list(up), mat, list(lc.tags))
        pairs = {"cop_from_perceptron_SHIPPED": bf_holders_for(toks, up, heads, hp, cp_perc) | base,
                 "cop_from_predicate_slot_BF": bf_holders_for(toks, up, heads, hp, cp_slot) | base,
                 "label_path_dropped": set(base)}
        sids.append(si)
        n_gold += len(gold)
        per[si]["gold"] = len(gold)
        for a in ARMS:
            props = collections.defaultdict(set)
            for (h, p) in pairs[a]:
                if 0 <= h < n and 0 <= p < n:
                    props[toks[h].lower()].add(toks[p].lower())
            per[si][a] = sum(int(toks[p].lower() in props.get(toks[h].lower(), set())) for (h, p, _t) in gold)
            per[si]["pairs_" + a] = len(pairs[a])
    out = {"n_gold_predicational_states": n_gold, "n_sentences": len(sids), "arms": {}}
    for a in ARMS:
        hit = sum(per[s][a] for s in sids)
        out["arms"][a] = {"read_back_recall": hit / max(1, n_gold), "hits": hit, "gold": n_gold,
                          "pairs_emitted": sum(per[s]["pairs_" + a] for s in sids)}
    by = {s: [per[s]] for s in sids}

    def d(a, b):
        def stat(rs):
            g = sum(r["gold"] for r in rs)
            return ((sum(r[a] for r in rs) - sum(r[b] for r in rs)) / g) if g else float("nan")
        return _boot_paired(sids, by, stat, n_boot, seed)

    out["paired_bootstrap"] = {
        "bf_minus_shipped": d("cop_from_predicate_slot_BF", "cop_from_perceptron_SHIPPED"),
        "dropped_minus_shipped": d("label_path_dropped", "cop_from_perceptron_SHIPPED")}
    return out


# ==================================================================================================
# ARM 6 -- the is-a edge map
# ==================================================================================================
def _appos_constructions(toks, pos):
    """The apposition CONSTRUCTIONS as arc-free item-based schemas (the attachment arm's `constructions` family):
    CLOSE apposition -- a common noun immediately followed by a NAME, or a name followed by a role noun, or a
    noun followed by a quoted mention ("the word 'terrorist'") -- and LOOSE apposition -- two NP heads separated
    by a comma with no predicate or preposition between.  UD head conventions: a NAME phrase is headed by its
    FIRST token (flat), a NOUN compound by its LAST (compound)."""
    from hdlab.lexical_utils import concept_lemma
    n = len(toks)
    out = set()
    stop = ("VERB", "AUX", "ADP", "SCONJ", "CCONJ")
    for i in range(n - 1):
        if pos[i] == "NOUN" and pos[i + 1] == "PROPN":
            out.add(frozenset((concept_lemma(toks[i]), concept_lemma(toks[i + 1]))))
        if pos[i] == "PROPN" and pos[i + 1] == "NOUN":
            out.add(frozenset((concept_lemma(toks[i]), concept_lemma(toks[i + 1]))))
    for i in range(n - 2):
        if pos[i] == "NOUN" and toks[i + 1] in ('"', "'", "``") and pos[i + 2] in ("NOUN", "PROPN", "ADJ"):
            out.add(frozenset((concept_lemma(toks[i]), concept_lemma(toks[i + 2]))))

    def before(k):
        for j in range(k, max(-1, k - 6), -1):
            if pos[j] in NOM2:
                return j
            if pos[j] in stop or pos[j] == "PUNCT":
                return None
        return None

    def after(k):
        j = k
        while j < n and pos[j] in ("DET", "ADJ", "NUM", "ADV"):
            j += 1
        if j < n and pos[j] == "PROPN":
            return j
        if j < n and pos[j] == "NOUN":
            while j + 1 < n and pos[j + 1] == "NOUN":
                j += 1
            return j
        return None

    for k in range(1, n - 1):
        if toks[k] != ",":
            continue
        a, b = before(k - 1), after(k + 1)
        if a is None or b is None or a == b:
            continue
        out.add(frozenset((concept_lemma(toks[a]), concept_lemma(toks[b]))))
    return out


def run_isa(cap=None, n_boot=2000, seed=SEED):
    from hdlab import attachment_arm as AA
    from hdlab import lexical_categories as LC
    from hdlab import graded_role_assigner as GRA
    from hdlab.arc_labeler import ArcLabeler
    from hdlab.lexical_utils import concept_lemma
    tg, ps = _frontend()
    lab = ArcLabeler.load(LAB_ASSET)
    lc = LC.get()
    ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}
    sents = _load_ud(UD_TEST, cap)
    per = collections.defaultdict(lambda: collections.defaultdict(int))
    sids = []
    for si, s in enumerate(sents):
        toks = [t["form"] for t in s]
        n = len(toks)
        if n < 2 or n > 80:
            continue
        up, tp, heads, hp, _conf, _marg = _parse_one(tg, ps, toks)
        if sum(1 for t in up if t in NOM2) < 2:
            continue
        mat = _tag_matrix(tp, n, lc.tags)
        gh = {t["id"]: t["head"] for t in s}
        gd = {t["id"]: t["deprel"] for t in s}
        gu = {t["id"]: t["upos"] for t in s}

        def _isa(heads_map, rel_of, pos_of, cop_preds=None, holders=None):
            e_ap, e_cp = set(), set()
            for i in range(1, n + 1):
                d = rel_of(i)
                h = heads_map.get(i, 0)
                if d.startswith("appos") and 1 <= h <= n and pos_of(i) in NOM2 and pos_of(h) in NOM2:
                    e_ap.add(frozenset((concept_lemma(toks[i - 1]), concept_lemma(toks[h - 1]))))
                if toks[i - 1].lower() in BE_FORMS and d == "cop" and 1 <= h <= n and pos_of(h) in NOM2:
                    subj = None
                    for u in range(1, n + 1):
                        if heads_map.get(u, 0) == h and rel_of(u).startswith("nsubj"):
                            subj = u
                    if subj is not None and pos_of(subj) in NOM2:
                        e_cp.add(frozenset((concept_lemma(toks[h - 1]), concept_lemma(toks[subj - 1]))))
            return e_ap, e_cp

        g_ap, g_cp = _isa(gh, lambda i: gd.get(i, ""), lambda i: gu.get(i, "X"))
        deprels = lab.label(toks, up, heads, head_posterior=hp)
        p_ap, p_cp = _isa(heads, lambda i: deprels.get(i, ""), lambda i: up[i - 1] if 1 <= i <= n else "X")

        # BF arm: the APPOSITION CONSTRUCTIONS as item-based schemas, arc-free (the STRONGEST form built --
        # the first attempt saw only the comma-set-off LOOSE apposition and recovered 5 of 105, because
        # COUNTING the gold shapes showed only 24 of 105 carry a comma at all: 65 are COMMA-FREE CLOSE
        # apposition ("the terrorist group Hamas", "September 11 ringleader Muhammad Atta").  Both schemas are
        # built here, with the UD head conventions the gold uses -- a NAME phrase is headed by its FIRST token
        # (flat), a NOUN compound by its LAST (compound); getting that wrong alone cost 5 of the 17 recovered.
        b_ap = _appos_constructions(toks, up)
        # BF arm: the PREDICATE SLOT copula with the competition's SUBJ
        b_cp = set()
        for pred in bf_cop_predicates(toks, up, mat, lc.tags):
            if up[pred - 1] not in NOM2:
                continue
            best, bp = None, 0.0
            for d in range(1, n + 1):
                hpd = (hp or {}).get(d)
                if heads.get(d) == pred or (hpd and hpd.get(pred, 0.0) > 0.0):
                    if up[d - 1] not in NOM2:
                        continue
                    p = (GRA.coarse_role_posterior_headmarg(toks, up, heads, d, hpd) if hpd
                         else GRA.coarse_role_posterior(toks, up, heads, d))
                    pr = float(p[ix["SUBJ"]] + p[ix["PASS_SUBJ"]])
                    if pr > bp:
                        best, bp = d, pr
            if best is not None and bp >= 0.5:
                b_cp.add(frozenset((concept_lemma(toks[pred - 1]), concept_lemma(toks[best - 1]))))
        # ORACLE-ARC arm (locates how much of the residual is the heads rung): the shipped appos RECIPE run on
        # GOLD heads with a GOLD appos label is the gold itself, so the informative oracle is the ARC-BASED
        # construction on GOLD heads -- what a perfect governor would buy the comma schema.
        o_ap = set()
        for i in range(1, n + 1):
            h = gh.get(i, 0)
            if not (1 <= h <= n) or up[i - 1] not in NOM2 or up[h - 1] not in NOM2:
                continue
            lo, hi = min(i, h), max(i, h)
            if hi - lo > 6 or not any(toks[k - 1] == "," for k in range(lo, hi)):
                continue
            if any(c in ("VERB", "AUX", "ADP", "SCONJ", "CCONJ") for c in up[lo:hi - 1]):
                continue
            o_ap.add(frozenset((concept_lemma(toks[i - 1]), concept_lemma(toks[h - 1]))))
        sids.append(si)
        d = per[si]
        d["g_ap"], d["g_cp"] = len(g_ap), len(g_cp)
        d["perc_ap"], d["perc_cp"] = len(g_ap & p_ap), len(g_cp & p_cp)
        d["bf_ap"], d["bf_cp"] = len(g_ap & b_ap), len(g_cp & b_cp)
        d["oracle_ap"] = len(g_ap & o_ap)
        d["emit_perc"], d["emit_bf"] = len(p_ap | p_cp), len(b_ap | b_cp)
        d["emit_perc_ap"], d["emit_bf_ap"], d["emit_oracle_ap"] = len(p_ap), len(b_ap), len(o_ap)

    T = {k: sum(per[s][k] for s in sids) for k in
         ("g_ap", "g_cp", "perc_ap", "perc_cp", "bf_ap", "bf_cp", "oracle_ap",
          "emit_perc", "emit_bf", "emit_perc_ap", "emit_bf_ap", "emit_oracle_ap")}
    gt = T["g_ap"] + T["g_cp"]
    out = {"n_sentences": len(sids), "n_gold_isa_edges": gt, "totals": T, "arms": {
        "perceptron_appos_plus_cop_SHIPPED": {
            "recall": (T["perc_ap"] + T["perc_cp"]) / max(1, gt), "emitted": T["emit_perc"],
            "precision": (T["perc_ap"] + T["perc_cp"]) / max(1, T["emit_perc"])},
        "bf_construction_plus_slot": {
            "recall": (T["bf_ap"] + T["bf_cp"]) / max(1, gt), "emitted": T["emit_bf"],
            "precision": (T["bf_ap"] + T["bf_cp"]) / max(1, T["emit_bf"])}},
        "split_half": {
            "appos_gold": T["g_ap"], "appos_perceptron": T["perc_ap"], "appos_bf": T["bf_ap"],
            "appos_bf_on_ORACLE_heads": T["oracle_ap"],
            "cop_gold": T["g_cp"], "cop_perceptron": T["perc_cp"], "cop_bf": T["bf_cp"]}}
    by = {s: [per[s]] for s in sids}

    def stat(rs):
        g = sum(r["g_ap"] + r["g_cp"] for r in rs)
        if not g:
            return float("nan")
        return float((sum(r["bf_ap"] + r["bf_cp"] for r in rs)
                      - sum(r["perc_ap"] + r["perc_cp"] for r in rs)) / g)

    def stat_cop(rs):
        g = sum(r["g_cp"] for r in rs)
        if not g:
            return float("nan")
        return float((sum(r["bf_cp"] for r in rs) - sum(r["perc_cp"] for r in rs)) / g)

    out["paired_bootstrap_bf_minus_shipped"] = _boot_paired(sids, by, stat, n_boot, seed)
    out["paired_bootstrap_COP_HALF_bf_minus_shipped"] = _boot_paired(sids, by, stat_cop, n_boot, seed)
    return out


# ==================================================================================================
# ARM 7 -- the live reader's board rows, BOTH ARMS IN ONE PROCESS
# ==================================================================================================
def _install_bf_routing(reader, purpose_tab, purpose_tau, purpose_drop, appos="bf"):
    """Route this READER INSTANCE's four consumers to the labels rung.  Instance-level only (the module is not
    mutated), except `copular_binding.extract_entity_states`, which the reader calls as a module function --
    that patch is installed/removed by the caller around the arm."""
    from hdlab import lexical_categories as LC
    from hdlab import goal_register as GR
    lc = LC.get()

    def _pconf(toks, v, pk):
        try:
            pos = reader._cached_tag(list(toks))
            heads, conf, _marg = reader._cached_parse_conf(list(toks), pos)
            hp = reader._cached_head_posterior(list(toks), pos)
            return bf_patient_confidence(list(toks), list(pos), heads, hp, conf, v, pk)
        except Exception:
            return None

    class _PurposeShim:
        """The ONLY thing goal_register reads off a labeler is the infinitival verb's complement-vs-purpose
        verdict.  This hands it that verdict from the Competition-Model purpose arm -- no perceptron."""

        def label(self, toks, pos, heads, head_posterior=None):
            out = {}
            low = [t.lower() for t in toks]
            n = len(toks)
            for i in range(1, n - 1):
                if low[i] != "to" or not (i + 1 < n and pos[i + 1] == "VERB"):
                    continue
                mvi = None
                for j in range(i - 1, -1, -1):
                    if pos[j] == "VERB":
                        mvi = j
                        break
                    if low[j] in (".", ";", ":", "!", "?"):
                        break
                if mvi is None:
                    continue
                cfg, cues = _purpose_cues(list(toks), list(pos), low, i, mvi, heads)
                cu = {k: v for k, v in cues.items() if k not in purpose_drop}
                if purpose_p_complement(purpose_tab, cfg, cu) >= purpose_tau:
                    out[i + 2] = "xcomp"           # a name in GR._COMPLEMENT_DEPREL == "reject this site"
            return out

    def _appos(sents):
        """The is-a edge map WITHOUT the perceptron: the copular half from the predicate slot + the
        competition's SUBJ.  The apposition half is RETIRED (measured: --isa)."""
        from hdlab import graded_role_assigner as GRA
        from hdlab.lexical_utils import concept_lemma
        ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}
        typed = {}
        for toks in sents:
            toks = list(toks)
            n = len(toks)
            if n < 2:
                continue
            up = reader._cached_tag(toks)
            if sum(1 for t in up if t in NOM2) < 2:
                continue
            heads = reader._cached_parse_heads(toks, up)
            hp = reader._cached_head_posterior(toks, up)
            mat = reader._cached_tag_matrix(toks)
            links = set()
            for pred in bf_cop_predicates(toks, up, mat, lc.tags):
                if up[pred - 1] not in NOM2:
                    continue
                best, bp = None, 0.0
                for d in range(1, n + 1):
                    hpd = (hp or {}).get(d)
                    if heads.get(d) == pred or (hpd and hpd.get(pred, 0.0) > 0.0):
                        if up[d - 1] not in NOM2:
                            continue
                        p = (GRA.coarse_role_posterior_headmarg(toks, up, heads, d, hpd) if hpd
                             else GRA.coarse_role_posterior(toks, up, heads, d))
                        pr = float(p[ix["SUBJ"]] + p[ix["PASS_SUBJ"]])
                        if pr > bp:
                            best, bp = d, pr
                if best is not None and bp >= 0.5:
                    links.add(frozenset((concept_lemma(toks[pred - 1]), concept_lemma(toks[best - 1]))))
            for l in links:
                t = tuple(l)
                a, b = (t[0], t[1]) if len(t) == 2 else (t[0], t[0])
                if not a or not b:
                    continue
                typed.setdefault(a, set()).add(b)
                typed.setdefault(b, set()).add(a)
        return typed

    reader._patient_arc_confidence = _pconf
    reader._frontend_labeler = lambda: _PurposeShim()
    if appos == "bf":
        reader._commonnoun_appos_map = _appos
    elif appos == "empty":
        reader._commonnoun_appos_map = lambda sents: {}
    del GR
    return reader


def _bf_extract_entity_states(toks, up, arc, lab, heads=None, head_posterior=None):
    """The BF `extract_entity_states`: DETECTION from the predicate slot, HOLDER from the competition.
    `arc`/`lab` are accepted and IGNORED (the landed patch drops them from the signature)."""
    from hdlab import lexical_categories as LC
    lc = LC.get()
    if heads is None:
        return []
    n = len(toks)
    tp = None
    try:
        _t, tp = lc.tag_with_posterior(list(toks))
    except Exception:
        tp = None
    mat = _tag_matrix(tp, n, lc.tags) if tp else None
    cop_preds = bf_cop_predicates(list(toks), list(up), mat, lc.tags)
    return sorted(bf_holders_for(list(toks), list(up), heads, head_posterior, cop_preds))


def run_rows(gum_docs=16, ud_cap=400, n_boot=2000, seed=SEED, smoke=False, purpose=None):
    """The board's own rows through the LIVE reader, shipped consumers vs the BF routing, one process."""
    from experiments.exp_board_rows_on_the_reader_v1 import (_gum_test_docs, _write_two_conll, score_gum_doc,
                                                            _ud_sents, _ud_write_chunk, score_ud_chunk,
                                                            _install_role_snapshot, UD_CHUNK)
    from hdlab.situation_reader import SituationReader
    from hdlab import copular_binding as CB
    tab = purpose or {}
    p_tab = tab.get("_table")
    p_tau = (tab.get("selected_on_dev") or {}).get("tau", 0.55)
    p_drop = tuple((tab.get("selected_on_dev") or {}).get("drop", ()))
    docs, gaz = _gum_test_docs(n_docs=gum_docs, prefix=bool(smoke))
    tmp = tempfile.mkdtemp(prefix="p129rows_")
    paths = []
    for d in docs[:gum_docs]:
        _a, p_txt, _p = _write_two_conll(d, tmp)
        paths.append((d, p_txt))
    ud = _ud_sents(cap=ud_cap) if ud_cap and ud_cap > 0 else []     # ud_cap<=0 -> GUM rows only
    chunks = [ud[i:i + UD_CHUNK] for i in range(0, len(ud), UD_CHUNK)]
    ud_paths = []
    for k, ch in enumerate(chunks):
        p = os.path.join(tmp, "ud_%03d.conll" % k)
        _ud_write_chunk(ch, p, "udchunk%03d" % k)
        ud_paths.append((k, ch, p))

    # THREE arms: the shipped consumers; the BF routing; and the BF routing with the is-a map EMPTY -- the
    # can-fail test of whether the perceptron appos map is load-bearing for its own consumer at all.
    ARMS = ("shipped", "bf", "bf_isa_empty")
    res = {a: {"gum": collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])),
               "ud": collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])),
               "per_unit": collections.defaultdict(dict), "read_s": 0.0, "diag": []} for a in ARMS}
    _real_ees = CB.extract_entity_states
    try:
        for arm in ARMS:
            CB.extract_entity_states = _bf_extract_entity_states if arm != "shipped" else _real_ees
            for d, p_txt in paths:
                rng = np.random.default_rng(seed)
                rdr = SituationReader(gaz=gaz)
                _install_role_snapshot(rdr)
                if arm != "shipped" and p_tab:
                    _install_bf_routing(rdr, p_tab, p_tau, p_drop,
                                        appos=("empty" if arm == "bf_isa_empty" else "bf"))
                t0 = time.time()
                sm = rdr.read(p_txt)
                res[arm]["read_s"] += time.time() - t0
                sc, diag = score_gum_doc(d, sm, rdr, rng)
                res[arm]["diag"].append({"docid": d.docid, **{k: v for k, v in diag.items()
                                                              if "commonnoun" in k or "coref" in k}})
                for row, arms in sc.items():
                    for a2, (h, nn) in arms.items():
                        res[arm]["gum"][row][a2][0] += h
                        res[arm]["gum"][row][a2][1] += nn
                    res[arm]["per_unit"][("gum", d.docid)][row] = dict(arms)
            for k, ch, p in ud_paths:
                rng = np.random.default_rng(seed + k)
                rdr = SituationReader(gaz=gaz)
                if arm != "shipped" and p_tab:
                    _install_bf_routing(rdr, p_tab, p_tau, p_drop,
                                        appos=("empty" if arm == "bf_isa_empty" else "bf"))
                t0 = time.time()
                sm = rdr.read(p)
                res[arm]["read_s"] += time.time() - t0
                sc, _diag = score_ud_chunk(ch, sm, rdr, rng, "udchunk%03d" % k)
                for row, arms in sc.items():
                    for a2, (h, nn) in arms.items():
                        res[arm]["ud"][row][a2][0] += h
                        res[arm]["ud"][row][a2][1] += nn
                    res[arm]["per_unit"][("ud", k)][row] = dict(arms)
    finally:
        CB.extract_entity_states = _real_ees

    out = {"n_gum_docs": len(paths), "n_ud_chunks": len(ud_paths), "ud_sentences": len(ud),
           "read_seconds": {a: round(res[a]["read_s"], 1) for a in ARMS}, "rows": {}, "paired": {},
           "commonnoun_diag": {a: res[a]["diag"] for a in ARMS}}
    rownames = sorted(set(list(res["shipped"]["gum"].keys()) + list(res["shipped"]["ud"].keys())))
    for row in rownames:
        out["rows"][row] = {}
        for a in ARMS:
            src = res[a]["gum"] if row in res[a]["gum"] else res[a]["ud"]
            out["rows"][row][a] = {a2: {"score": (h / nn) if nn else float("nan"), "n": nn}
                                   for a2, (h, nn) in src[row].items()}
    units = sorted(set(list(res["shipped"]["per_unit"].keys())), key=lambda u: (str(u[0]), str(u[1])))
    for row in rownames:
        for other in ("bf", "bf_isa_empty"):
            by = {}
            for u in units:
                s = res["shipped"]["per_unit"].get(u, {}).get(row)
                b = res[other]["per_unit"].get(u, {}).get(row)
                if s and b and "model" in s and "model" in b:
                    by[u] = [{"sh": s["model"], "bf": b["model"]}]
            if not by:
                continue

            def stat(rs):
                n = sum(r["sh"][1] for r in rs)
                if not n:
                    return float("nan")
                return float((sum(r["bf"][0] for r in rs) - sum(r["sh"][0] for r in rs)) / n)

            out["paired"]["%s|%s_minus_shipped" % (row, other)] = _boot_paired(sorted(by), by, stat,
                                                                              n_boot, seed)
    return out


# ==================================================================================================
# self-test
# ==================================================================================================
def self_test():
    ok = fail = 0

    def chk(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print("  PASS %s %s" % (name, detail))
        else:
            fail += 1
            print("  FAIL %s %s" % (name, detail))

    print("S1 the BF patient reliability is a probability, and the slot factor is a real competition")
    from hdlab import frontend as FE
    tg, ps = FE.tagger(), FE.parser()
    toks = ["the", "dog", "chased", "the", "cat", "."]
    up, _tp, heads, hp, conf, _m = _parse_one(tg, ps, toks)
    v = 3
    c1 = bf_patient_confidence(toks, up, heads, hp, conf, v, 5)
    c2 = bf_patient_confidence(toks, up, heads, hp, conf, v, 2)
    chk("S1a in [0,1]", c1 is not None and 0.0 <= c1 <= 1.0, "cat=%.4f" % (c1 or -1))
    chk("S1b the object outranks the subject", (c1 or 0) > (c2 or 1), "cat %.4f > dog %.4f" % (c1 or -1, c2 or -1))
    chk("S1c out of range abstains", bf_patient_confidence(toks, up, heads, hp, conf, v, 99) is None)

    print("S2 the predicate slot finds the copular predicate with NO relation labeler")
    from hdlab import lexical_categories as LC
    lc = LC.get()
    t2 = ["the", "sky", "is", "blue", "."]
    up2, tp2, heads2, hp2, _c2, _m2 = _parse_one(tg, ps, t2)
    mat2 = _tag_matrix(tp2, len(t2), lc.tags)
    cps = bf_cop_predicates(t2, up2, mat2, lc.tags)
    chk("S2a blue holds the predicate slot", 4 in cps, "cop_preds=%s" % sorted(cps))
    pairs = bf_holders_for(t2, up2, heads2, hp2, cps)
    chk("S2b holder=sky property=blue", (1, 3) in pairs, "pairs=%s" % sorted(pairs))

    print("S3 the purpose arm learns from counts, decides, and OBSERVES (nothing frozen)")
    rows = [{"gold": "complement", "cfg": "adjacent", "cues": {"frame": "hi"}} for _ in range(6)] + \
           [{"gold": "purpose", "cfg": "pp", "cues": {"frame": "lo"}} for _ in range(6)]
    tab = purpose_learn(rows)
    pc_hi = purpose_p_complement(tab, "adjacent", {"frame": "hi"})
    pc_lo = purpose_p_complement(tab, "pp", {"frame": "lo"})
    chk("S3a complement config -> P(complement) high", pc_hi > 0.6, "%.4f" % pc_hi)
    chk("S3b purpose config -> P(complement) low", pc_lo < 0.4, "%.4f" % pc_lo)
    before = purpose_p_complement(tab, "pp", {"frame": "lo"})
    for _ in range(40):
        purpose_observe(tab, "pp", {"frame": "lo"}, "complement")
    after = purpose_p_complement(tab, "pp", {"frame": "lo"})
    chk("S3c observing outcomes MOVES the decision (online plasticity)", after > before + 0.1,
        "%.4f -> %.4f" % (before, after))

    print("S4 the AUC / bootstrap helpers are correct")
    chk("S4a perfect separation", abs(_auc([1, 1, 0, 0], [2.0, 3.0, 0.0, 1.0]) - 1.0) < 1e-9)
    chk("S4b all ties == 0.5", abs(_auc([1, 0, 1, 0], [1.0, 1.0, 1.0, 1.0]) - 0.5) < 1e-9)
    chk("S4c empty class -> nan", _auc([1, 1], [1.0, 2.0]) != _auc([1, 1], [1.0, 2.0]))
    b = _boot_paired([0, 1], {0: [{"x": 1.0}], 1: [{"x": 1.0}]},
                     lambda rs: float(np.mean([r["x"] for r in rs])), n_boot=50, seed=1)
    chk("S4d constant stat -> zero-width CI", abs(b["hi"] - b["lo"]) < 1e-9, str(b))

    print("S5 the import probe sees a NOT_BF module during a default read (the DEFECT reproduces)")
    pr = run_probe(n_docs=1, smoke=True)
    chk("S5a the probe read a document", pr["n_docs"] == 1 and pr["per_doc"][0]["events"] > 0,
        str(pr["per_doc"]))
    chk("S5b arc_labeler and/or parse_confidence imported DURING read",
        any(m in pr["notbf_imported_during_read"] for m in ("hdlab.arc_labeler", "hdlab.parse_confidence")),
        str(pr["notbf_imported_during_read"]))
    chk("S5c the call-site table names more than the three consumers the brief lists",
        len(pr["call_sites"]) >= 3, str(sorted(pr["call_sites"])))

    print("S6 the BF extract_entity_states drop-in has the shipped signature and needs no labeler")
    got = _bf_extract_entity_states(t2, up2, None, None, heads=heads2, head_posterior=hp2)
    chk("S6a returns (holder, property) pairs with arc=lab=None", (1, 3) in got, str(got))

    print("S7 the perceptron's label is discarded where structural_patient_pick reads it (small sample)")
    idn = run_identity(cap=200)
    chk("S7a pick identity 1.0 on the sample", idn["pick_identity"] == 1.0, str(idn["pick_identity"]))

    print("\nSELF-TEST %d/%d" % (ok, ok + fail))
    return fail == 0


# ==================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--patient", action="store_true")
    ap.add_argument("--goal", action="store_true")
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--isa", action="store_true")
    ap.add_argument("--rows", action="store_true")
    ap.add_argument("--gum-docs", type=int, default=16)
    ap.add_argument("--ud-cap", type=int, default=400)
    ap.add_argument("--cap", type=int, default=0)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--tag", default="")
    ap.add_argument("--timeout", type=int, default=0)
    a = ap.parse_args()
    if a.self_test:
        sys.exit(0 if self_test() else 1)
    smoke = bool(a.smoke) or a.mode == "smoke"          # BARE == FULL (the remote runner invokes cells bare)
    cap = a.cap or (200 if smoke else None)
    sel = {k for k in ("probe", "identity", "patient", "goal", "state", "isa", "rows") if getattr(a, k)}
    if not sel:
        sel = {"probe", "identity", "patient", "goal", "state", "isa", "rows"}
    os.makedirs(OUT_DIR, exist_ok=True)
    M = {"anchor": ANCHOR, "seed": a.seed, "smoke": smoke, "arms_run": sorted(sel),
         "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t0 = time.time()
    if "probe" in sel:
        M["probe"] = run_probe(n_docs=(2 if smoke else a.gum_docs), smoke=smoke)
        print("[probe] NOT_BF imported during read: %s" % M["probe"]["notbf_imported_during_read"])
    if "identity" in sel:
        M["identity"] = run_identity(cap=cap)
        print("[identity] pick identity %.6f over %d picks; %d tokens differ"
              % (M["identity"]["pick_identity"], M["identity"]["matrix_verb_picks"],
                 M["identity"]["tokens_membership_differs"]))
    if "patient" in sel:
        M["patient"] = run_patient(cap=cap, n_boot=a.n_boot, seed=a.seed)
        print("[patient] n=%d  AUC shipped %.4f  BF belief %.4f  BF belief x slot %.4f  twin %.4f"
              % (M["patient"]["n_items"], M["patient"]["auc"]["shipped_logistic"],
                 M["patient"]["auc"]["competition_patient_belief"],
                 M["patient"]["auc"]["bf_belief_x_slot"], M["patient"]["auc"]["twin_bf_permuted"]))
    purpose = None
    if "goal" in sel or "rows" in sel:
        purpose = run_goal(cap_train=(600 if smoke else None), cap_test=cap, n_boot=a.n_boot, seed=a.seed)
        tabl = purpose.pop("_table")
        tabl["tau"] = float((purpose.get("selected_on_dev") or {}).get("tau", 0.55))
        tabl["dropped_cues"] = list((purpose.get("selected_on_dev") or {}).get("drop", []))
        with open(os.path.join(OUT_DIR, PURPOSE_ASSET_NAME), "w", encoding="ascii", newline="\n") as fh:
            json.dump(tabl, fh, indent=1, sort_keys=True)
        purpose["_table"] = tabl
        M["goal"] = {k: v for k, v in purpose.items() if k != "_table"}
        print("[goal] n=%d  perceptron %.4f  BF competition %.4f  majority %.4f  twin %.4f  agree %.3f"
              % (purpose["n_test_decidable"],
                 purpose["arms"]["perceptron_deprel_filter_SHIPPED"]["accuracy"],
                 purpose["arms"]["competition_purpose_arm_BF"]["accuracy"],
                 purpose["majority_floor"], purpose["arms"]["twin_same_rate_random"]["accuracy"],
                 purpose["agreement_with_shipped"]))
    if "state" in sel:
        M["state"] = run_state(cap=cap, n_boot=a.n_boot, seed=a.seed)
        print("[state] recall shipped %.4f  BF slot %.4f  dropped %.4f"
              % (M["state"]["arms"]["cop_from_perceptron_SHIPPED"]["read_back_recall"],
                 M["state"]["arms"]["cop_from_predicate_slot_BF"]["read_back_recall"],
                 M["state"]["arms"]["label_path_dropped"]["read_back_recall"]))
    if "isa" in sel:
        M["isa"] = run_isa(cap=cap, n_boot=a.n_boot, seed=a.seed)
        print("[isa] recall shipped %.4f  BF %.4f  (cop half %d vs %d; appos half %d vs %d, oracle %d)"
              % (M["isa"]["arms"]["perceptron_appos_plus_cop_SHIPPED"]["recall"],
                 M["isa"]["arms"]["bf_construction_plus_slot"]["recall"],
                 M["isa"]["split_half"]["cop_perceptron"], M["isa"]["split_half"]["cop_bf"],
                 M["isa"]["split_half"]["appos_perceptron"], M["isa"]["split_half"]["appos_bf"],
                 M["isa"]["split_half"]["appos_bf_on_ORACLE_heads"]))
    if "rows" in sel:
        M["rows"] = run_rows(gum_docs=(2 if smoke else a.gum_docs), ud_cap=(60 if smoke else a.ud_cap),
                             n_boot=a.n_boot, seed=a.seed, smoke=smoke, purpose=purpose)
        for row, d in sorted(M["rows"]["rows"].items()):
            sh = d.get("shipped", {}).get("model", {})
            bf = d.get("bf", {}).get("model", {})
            em = d.get("bf_isa_empty", {}).get("model", {})
            print("[rows] %-20s shipped %.4f (n=%s)  bf %.4f (n=%s)  bf_isa_empty %.4f"
                  % (row, sh.get("score", float("nan")), sh.get("n"),
                     bf.get("score", float("nan")), bf.get("n"), em.get("score", float("nan"))))
    M["elapsed_s"] = round(time.time() - t0, 1)
    name = "metrics.json" if not a.tag else ("metrics%s.json" % a.tag)
    with open(os.path.join(OUT_DIR, name), "w", encoding="ascii") as fh:
        json.dump(M, fh, indent=1, default=str)
    print("\nwrote %s (%.1fs)" % (os.path.join(OUT_DIR, name), M["elapsed_s"]))


if __name__ == "__main__":
    main()
