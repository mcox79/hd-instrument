"""Learn the CUE VALIDITIES of the Competition-Model coarse role labeler (hdlab.graded_role_assigner.coarse_roles) from a
training treebank -- the brain's cue strengths are learned from experience as cue VALIDITY (MacWhinney, Bates & Kliegl
1984: availability x reliability), never hand-set. v2 (2026-09-12): every cue (config = head-class x order, voice_order,
prep, cop, case, post_rank) takes a categorical VALUE; for each value the strength toward each role is
    strength(value -> role) = log P(role | cue value)      (add-0.5 smoothed over the 6 roles)
plus the role prior log P(role). v3: every secondary cue is read WITHIN its head-class x order configuration as a CONTRAST
log P(role | config, value) - log P(role | config) (absent/uninformative values contribute ~0; no majority-class double
counting). The labeler adds the strengths of the fired values (graded_competition.net_activation)
and takes softmax / argmax -- the normative limit of additive cue competition. Also reports per-cue availability
(P(value fires)) and reliability (max_r P(r | value)) so the cue's validity is auditable.
Source: UD-EWT TRAIN with gold heads/POS (the cue functions read only toks/pos/heads); evaluation treebanks never used.
Writes data/frontend_assets/coarse_role_validities_ud_ewt.json.   Run: python tools/build_coarse_role_validities.py
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import graded_role_assigner as GRA

TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
OUT = os.path.join(REPO, "data", "frontend_assets", "coarse_role_validities_ud_ewt.json")
ALPHA = 0.5
M_SHRINK = 2.0
# pri 103 (2026-09-13): --v3 accrues the v3 cue set over the ARGUMENT-HEAD population and stamps "cue_set": "v3" into
# the asset, which is what switches the organ (graded_role_assigner is byte-identical on a table without that key).
# MIN_CONF is the RELIABILITY GATE on learning: a comprehension outcome teaches the cue validities only when the
# governor believed its own attachment. The brain consolidates what it UNDERSTOOD, not every parse it guessed
# (reliability-weighted learning, Ernst & Banks 2002; the confidence WEIGHT alone is not enough -- the low-confidence
# tail teaches the OTHER class the profile of the parser errors). Swept 0.0 / 0.5 / 0.8; 0.5 adopted as the operating
# point (UD-EWT test 700, gold heads, core role recall +0.044 at 0.5 vs +0.025 ungated).
MIN_CONF = 0.5
# hierarchical configuration backoff, stamped into the asset and applied by the organ (see graded_role_assigner)
M_CONFIG_BACKOFF = 0.0   # SWEPT and REJECTED: see graded_role_assigner (buys argument recall, loses the balanced metric)


def coarse_of(dep: str) -> str:
    d = (dep or "").split(":")[0]; full = dep or ""
    if full.startswith("nsubj:pass") or full == "nsubjpass": return "PASS_SUBJ"
    if d in ("nsubj", "csubj"): return "SUBJ"
    if d == "iobj": return "IOBJ"
    if d in ("obj", "dobj"): return "OBJ"
    if full == "obl:agent": return "BY_AGENT"
    # pri 108 (2026-09-14): with an NMOD class in the inventory a nominal licensed by a nominal has a name of its own.
    # The POSSESSIVE is a genitive-MARKED member of that same class (a property of a thing, marked by the one case
    # marker English puts to the right) -- filing it under OTHER was a workaround for having only OBL available, and it
    # is a quarter of the class (125 of 489 on UD-EWT test 700). Measured: mapping it to OTHER instead costs gold-heads
    # nmod 0.7239 -> 0.4683 CI-sep. A 7-class (pre-108) build is unchanged: `NMOD` simply is not in ROLE_CLASSES then.
    if "NMOD" in GRA.ROLE_CLASSES:
        if full == "nmod:poss": return "NMOD"
        if d == "nmod": return "NMOD"
        if d == "obl": return "OBL"
        return "OTHER"
    if full == "nmod:poss": return "OTHER"   # possessive = determiner-like modifier, not an oblique
    if d in ("obl", "nmod"): return "OBL"
    return "OTHER"


def sentences(path):
    toks, pos, heads, deps = [], [], {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    yield toks, pos, heads, deps
                toks, pos, heads, deps = [], [], {}, {}
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if "-" in cols[0] or "." in cols[0]:
                continue
            i = int(cols[0]); toks.append(cols[1]); pos.append(cols[3]); heads[i] = int(cols[6]); deps[i] = cols[7]
    if toks:
        yield toks, pos, heads, deps


def _perceive(toks, pos, heads):
    """Predicted POS + predicted heads from the live front-end (hdlab.causation_typing._frontend: tagger, parser)."""
    global _FE
    if _FE is None:
        import hdlab.causation_typing as CT
        _FE = CT._frontend()
    tg, pp, _ = _FE
    ppos = list(tg.tag(list(toks)))
    pheads = dict(pp.parse(list(toks), ppos).heads)
    return ppos, pheads


def _confidence(toks, ppos, pheads):
    """CONFIDENCE-WEIGHTED PERCEPTION (2026-09-13 14:50, strategy). The perceived-heads table (this morning) learned 'a NOUN left of
    a VERB is often not its subject' from the governor's own MISATTACHMENTS (at gold heads: matrix nsubj recall 0.873 with the
    gold-convention table vs 0.748 with the perceived table; 45 canonical subjects -> OTHER) while gaining objects. The brain learns
    cue validity from experience weighted by how reliable each experience was (reliability-weighted learning; Ernst & Banks 2002 for
    cue reliability; the governor's own graded belief is that reliability here) -- so each perceived instance counts with weight
    w = P(perceived head | dependent) under the attachment arm's exact single-root marginals (hdlab.attachment_arm.head_posterior).
    A confidently attached nominal teaches at full weight; a guess teaches a fraction. No gold tree is read."""
    global _TAB
    import hdlab.attachment_arm as AA
    if _TAB is None:
        _TAB = AA.load_attachment_validities()
    post = AA.head_posterior(list(toks), list(ppos), _TAB)
    return {i: float((post.get(i) or {}).get(h, 0.0)) for i, h in pheads.items()}


_TAB = None


_FE = None


def main():
    perceived = "--perceived" in sys.argv
    weighted = "--weight" in sys.argv                                   # confidence-weighted perception (see _confidence)
    v3 = "--v3" in sys.argv or "--v4" in sys.argv                       # pri 103 cue set + argument-head population
    # pri 108 (2026-09-14): --v4 accrues the v3 cue set PLUS the genitive case values and the arc-free LICENSOR cue over
    # the NMOD-bearing class space, and stamps "cue_set": "v4" into the asset, which is what switches the organ (a table
    # without that key leaves graded_role_assigner byte-identical to the pre-2026-09-14 behaviour).
    v4 = "--v4" in sys.argv
    out_path = OUT.replace(".json", "_perceived_w.json" if weighted else "_perceived.json") if perceived else OUT
    if v3:
        out_path = out_path.replace(".json", "_v4.json" if v4 else "_v3.json")
    K = len(GRA.ROLE_CLASSES)
    ix = {r: k for k, r in enumerate(GRA.ROLE_CLASSES)}
    cfg_counts = defaultdict(lambda: [0] * K)                      # config value -> role counts
    counts = defaultdict(lambda: defaultdict(lambda: [0] * K))     # cue -> "cfg|value" -> role counts
    prior = [0] * K; decisions = 0
    # pass 1: the verb-frame knowledge -- per head-verb lemma, how many nominal dependents were RECIPIENTS (iobj) out of all
    # nominal dependents (accrued from reading; here from the same treebank counts; the plastic form keeps accruing)
    from hdlab.thematic_role_labeler import lemma_verb
    lemma_frames = defaultdict(lambda: [0, 0])
    for toks, gpos, gheads, deps in sentences(TRAIN):
        for i in range(1, len(toks) + 1):
            h = gheads.get(i, 0)
            if gpos[i - 1] in GRA.NOMINAL and h and gpos[h - 1] in ("VERB", "AUX"):
                lf = lemma_frames[lemma_verb(toks[h - 1]).lower()]
                lf[1] += 1; lf[0] += int((deps.get(i) or "").split(":")[0] == "iobj")
    lemma_frames = {k: v for k, v in lemma_frames.items() if v[1] >= 5}
    for toks, gpos, gheads, deps in sentences(TRAIN):
        pos, heads = _perceive(toks, gpos, gheads) if perceived else (gpos, gheads)
        conf = _confidence(toks, pos, heads) if (perceived and weighted) else None
        for i in range(1, len(toks) + 1):
            if not (GRA.is_arg_head(toks, gpos, i) if v3 else gpos[i - 1] in GRA.NOMINAL):
                continue
            w = conf.get(i, 0.0) if conf is not None else 1
            if w <= 0 or (v3 and conf is not None and w < MIN_CONF):
                continue                    # no posterior mass, or below the reliability gate -> teaches nothing
            decisions += w
            g = ix[coarse_of(deps.get(i))]
            prior[g] += w
            cues = GRA.coarse_role_cues(toks, pos, heads, i, lemma_frames, v3, conf, v4)
            cfg = cues["config"]
            cfg_counts[cfg][g] += w
            for cue, val in cues.items():
                if cue != "config":
                    # the arc-free LICENSOR is accrued UNCONDITIONALLY (pri 108) -- see graded_role_assigner
                    key = ("GLOBAL|" + val) if cue in GRA._GLOBAL_CUES else f"{cfg}|{val}"
                    counts[cue][key][g] += w
            if v4:
                cfg_counts["GLOBAL"][g] += w
    # SLOT CAPACITY (verb-frame occupancy knowledge, in counts; owner-DONE pri 93): per core slot, how many verb tokens have >= 1
    # filler (n1) and >= 2 fillers (n2). lambda = -log P(2nd | >= 1) is a pure function of these (organ side, _slot_capacity).
    from collections import Counter as _Counter
    _n1, _n2 = _Counter(), _Counter()
    for toks, gpos, gheads, deps in sentences(TRAIN):
        by_verb = {}
        for i in range(1, len(toks) + 1):
            h = gheads.get(i, 0)
            if gpos[i - 1] in GRA.NOMINAL and h and gpos[h - 1] in ("VERB", "AUX"):
                by_verb.setdefault(h, []).append(coarse_of(deps.get(i)))
        for h, roles in by_verb.items():
            slotc = _Counter(GRA.ROLE_TO_SLOT.get(r) for r in roles if GRA.ROLE_TO_SLOT.get(r))
            for slot, c in slotc.items():
                _n1[slot] += 1
                if c >= 2:
                    _n2[slot] += 1
    slot_capacity = {s_: [int(_n1[s_]), int(_n2[s_])] for s_ in GRA.CORE_SLOTS}
    counts_doc = {"prior": prior, "config": {k: v for k, v in cfg_counts.items()},
                  "cues": {cue: {key: vec for key, vec in vals.items()} for cue, vals in counts.items()}}
    counts_doc["slot_capacity"] = slot_capacity
    built = GRA.strengths_from_counts(counts_doc, M_CONFIG_BACKOFF if v3 else 0.0)              # ONE implementation of the math (the organ's)
    logprior = [float(x) for x in built["prior"]]
    strength = {c: {v: [round(float(x), 4) for x in vec] for v, vec in vals.items()} for c, vals in built["strength"].items()}
    audit = {"config": {}}
    for cfg, vec in cfg_counts.items():
        n = sum(vec); best = max(range(K), key=lambda k: vec[k])
        if n <= 0:
            continue
        audit["config"][cfg] = {"n": round(float(n), 2), "availability": round(n / decisions, 4), "reliability": round(vec[best] / n, 4),
                                "cued_role": GRA.ROLE_CLASSES[best]}
    for cue, vals in counts_doc["cues"].items():
        audit[cue] = {}
        for key, vec in vals.items():
            n = sum(vec); best = max(range(K), key=lambda k: vec[k])
            if n <= 0:
                continue
            audit[cue][key] = {"n": round(float(n), 2), "availability": round(n / decisions, 4), "reliability": round(vec[best] / n, 4),
                               "cued_role": GRA.ROLE_CLASSES[best]}
    doc = {"source": "UD-EWT train (gold heads/POS). Competition Model, configuration-conditioned: activation(role) = "
                     "log P(role) + [log P(role|config) - log P(role)] + sum_c [log P(role|config,c=v) - log P(role|config)]; "
                     "add-0.5 on config, Dirichlet shrinkage m=%g on contrasts; availability = P(value fires), "
                     "reliability = max_r P(r|value)." % M_SHRINK,
           "decisions": decisions, "roles": GRA.ROLE_CLASSES, "prior": [round(x, 4) for x in logprior],
           "strength": strength, "audit": audit, "lemma_frames": lemma_frames, "counts": counts_doc}
    doc["perceived"] = perceived; doc["confidence_weighted"] = bool(perceived and weighted)
    if v3:
        doc["cue_set"] = "v4" if v4 else "v3"; doc["min_conf"] = MIN_CONF; doc["m_config_backoff"] = M_CONFIG_BACKOFF
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    print(f"decisions={decisions}  prior={dict(zip(GRA.ROLE_CLASSES, prior))}")
    print("[config]")
    for val, a in sorted(audit["config"].items(), key=lambda kv: -kv[1]["n"])[:12]:
        print(f"   {val:16s} n={a['n']:8.1f} avail={a['availability']:.4f} rel={a['reliability']:.3f} -> {a['cued_role']}")
    for cue in [c for c in (list(GRA.COARSE_CUES[1:]) + (["hostsurf", "vprep"] if v4 else [])) if c in audit]:
        print(f"[{cue}] (within VERB_pre / VERB_post / NOUN_pre / NOUN_post)")
        for key, a in sorted(audit[cue].items(), key=lambda kv: -kv[1]["n"]):
            if key.split("|")[0] in ("VERB_pre", "VERB_post", "NOUN_pre", "NOUN_post") and a["n"] >= 30:
                print(f"   {key:28s} n={a['n']:8.1f} rel={a['reliability']:.3f} -> {a['cued_role']}")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
