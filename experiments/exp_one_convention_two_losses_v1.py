"""ONE CONVENTION, TWO LOSSES -- the clause's PREDICATE SLOT as one shared computation (pri 110).

UD tags a clause's main-verb / copular `be` and `have` as AUX.  The count-based category organ learned that
convention, so a real main verb comes out AUX: 23 tokens of UD-EWT test 700 carry 87 NET head flips = 58% of the
whole tag-to-head loss (data/exp_diag_tag_to_head_loss_v1), and an ADDITIVE predicate rescue cannot see them at all
(4.7-38.8% of dropped verbs, pri 107 4(g)).  Two consumers, one cause.

THE BRAIN.  One predicate per clause (Spivey-Knowlton 1993).  An auxiliary is a TENSE CARRIER for another verbal
element; when the clause holds no such host, the be/have token IS the predicate (Pustet 2003 on the copula as the
tense carrier of a non-verbal predication).  So the shared computation is the clause's PREDICATE-SLOT OCCUPANCY,
read off the category organ's own graded posterior, NOT the argmax tag:

    P(slot free | clause) = prod_{j in clause, j != i} (1 - P(VERB_j))            [no other verbal predicate]
    P(host)               = max over the clause-local host positions of P(verbal host at that position)
    occ_i                 = P(slot free) * (1 - P(host))                          [the AUX at i IS the predicate]

Both consumers read `occ`: the predicate rescue's sole-AUX arm (a boolean clause flag today) and the governor's
main-assertion competition (an AUX is an assertion candidate only when the WHOLE SENTENCE is verbless today).

Run: python experiments/exp_one_convention_two_losses_v1.py --diag | --self-test | --gov | --reader | --board
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import json
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from tools.build_attachment_validities import sentences, TEST

OUT = str(get_output_dir("one_convention_two_losses_v1"))


def out_dir():
    os.makedirs(OUT, exist_ok=True)
    return OUT


# ------------------------------------------------------------------ phase 1: what IS the population, on disk
def diag(cap=700):
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    rows = []
    conf = Counter(); rel_of = Counter(); word_of = Counter()
    n_tok = 0
    for toks, gold_pos, gold_heads, rels in test:
        pred_pos, post_d = lc.tag_with_posterior(list(toks))
        n_tok += len(toks)
        for i, (g, p) in enumerate(zip(gold_pos, pred_pos)):
            if g == p:
                continue
            conf[(g, p)] += 1
            if g == "VERB" and p == "AUX":
                rel_of[rels[i]] += 1
                word_of[toks[i].lower()] += 1
                rows.append({"w": toks[i], "rel": rels[i], "head": gold_heads[i],
                             "pv": round(float(post_d[i].get("VERB", 0.0)), 4),
                             "pa": round(float(post_d[i].get("AUX", 0.0)), 4),
                             "sent": " ".join(toks)[:130]})
    # the gold side of the convention: how often is a gold AUX the clause's ONLY verbal token?
    gold_sole_aux = 0; gold_sole_aux_root = 0; gold_aux = 0
    for toks, gold_pos, gold_heads, rels in test:
        for i, g in enumerate(gold_pos):
            if g != "AUX":
                continue
            gold_aux += 1
            if not any(p == "VERB" for p in gold_pos):
                gold_sole_aux += 1
                if gold_heads[i] == 0:
                    gold_sole_aux_root += 1
    res = {"tokens": n_tok, "verb_as_aux_tokens": sum(rel_of.values()),
           "verb_as_aux_by_rel": dict(rel_of.most_common()),
           "verb_as_aux_by_word": dict(word_of.most_common(15)),
           "aux_as_verb_tokens": conf[("AUX", "VERB")],
           "gold_aux_tokens": gold_aux, "gold_sole_aux_in_verbless_sentence": gold_sole_aux,
           "gold_sole_aux_is_root": gold_sole_aux_root,
           "examples": rows[:40]}
    json.dump(res, open(os.path.join(out_dir(), "diag.json"), "w", encoding="utf-8"), indent=1)
    print("tokens %d | gold VERB tagged AUX: %d | gold AUX tagged VERB: %d" %
          (n_tok, res["verb_as_aux_tokens"], res["aux_as_verb_tokens"]))
    print("by gold relation:", res["verb_as_aux_by_rel"])
    print("by word:", res["verb_as_aux_by_word"])
    print("gold AUX tokens %d; in a sentence with NO gold VERB %d (of which gold-root %d)" %
          (gold_aux, gold_sole_aux, gold_sole_aux_root))
    for r in rows[:25]:
        print("  %-8s rel=%-8s P(V)=%.3f P(A)=%.3f | %s" % (r["w"], r["rel"], r["pv"], r["pa"], r["sent"]))
    return res


# =====================================================================================================================
# THE SHARED COMPUTATION -- the clause's PREDICATE-SLOT constraint, applied INSIDE the category organ's own decode.
# ---------------------------------------------------------------------------------------------------------------------
# pri 107's alternate path A, filed into this brief.  The organ is an HMM over categories; its forward pass already
# computes Z = sum over all category sequences of P(words, categories).  Run the SAME pass again with the VERB state
# masked out over one clause and the result is Z_noV = the mass of every decode in which that clause has NO verbal
# predicate.  The one-predicate-per-clause expectation (Spivey-Knowlton 1993) is then an EXACT conditioning, with no
# free parameter at all:
#     w_c                      = Z_noV(c) / Z                 = P(clause c has no verbal predicate)
#     P(c_i = VERB | E)        = post_i(VERB) / (1 - w_c)
#     P(c_i = t    | E)        = (post_i(t) - w_c * postNoV_i(t)) / (1 - w_c)      [the exact mixture decomposition]
# post = (1 - w) * post_E + w * post_noV holds because the two events partition the space, so ONE extra masked
# forward-backward per clause gives the whole conditional distribution.  This is a REVISION at the clause boundary
# (clause wrap-up, Just & Carpenter 1980), not a new organ: the belief the categories rung hands DOWN is the revised
# one, so every consumer -- the governor, the predicate rescue, the events, the roles, the states -- reads it.
# alpha (the expectation's STRENGTH) is the only knob and it is swept; alpha = 1 is the exact constraint.
# =====================================================================================================================

NEG = -1e9


def _le_and_post(lc, words, lag="live"):
    """The organ's OWN emission rows + posterior for this sentence (replays `posterior()` including the frame channel
    and the stem-reanalysis revision, so these are its numbers, not a re-implementation)."""
    import math
    lag = LC.LAG if lag == "live" else lag
    if lc._dirty:
        lc.finalize()
    n = len(words)
    lc._sent_pos = [LC.position_class(words, i) for i in range(n)]
    lc._sent_lows = [w.lower() for w in words]
    lc._sent_i = 0
    le = np.stack([lc._log_emit(w) for w in words])
    if lc.use_frame and LC.FRAME and LC.FRAME_KAPPA > 0:
        le = le + LC.FRAME_KAPPA * lc._log_frame(words, lag)
    post = lc._posterior_le(le, lag)
    if lc._reg is not None:
        lc._reg.sent_no += 1
    if LC.STEM_REANALYSIS:
        changed = False
        for k, w in enumerate(words):
            wl = w.lower()
            if wl in lc.vocab:
                t_star = lc.tags[int(post[k].argmax())]
                if lc.emit[t_star][wl] == 0:
                    spri = lc._log_stem_prior(wl)
                    if spri is not None:
                        cw = sum(lc.emit[t][wl] for t in lc.tags); a = cw / (cw + LC.STEM_KAPPA)
                        le[k] = np.logaddexp(math.log(a) + le[k], math.log(1.0 - a) + spri); changed = True
        if changed:
            post = lc._posterior_le(le, lag)
    return le, post


def _logZ(lc, le):
    """log Z = log sum over category sequences of P(words, categories) -- the organ's own forward recursion."""
    n, T = le.shape
    if n == 0:
        return 0.0
    if lc.order >= 2:
        L2 = lc.log_trans2
        fwd = np.full((T + 1, T), NEG)
        fwd[0, :] = L2[0, 0, :] + le[0]
        for i in range(1, n):
            m = fwd[:, :, None] + L2[:, 1:, :]
            mx = m.max(axis=0)
            cur = mx + np.log(np.exp(m - mx).sum(axis=0))
            nf = np.full((T + 1, T), NEG); nf[1:, :] = cur + le[i][None, :]
            fwd = nf
        f = fwd
    else:
        A = lc.log_trans[1:]
        f = lc.log_trans[0] + le[0]
        for i in range(1, n):
            m = f[:, None] + A
            mx = m.max(axis=0); f = mx + np.log(np.exp(m - mx).sum(axis=0)) + le[i]
    mx = f.max()
    return float(mx + np.log(np.exp(f - mx).sum()))


def clause_units(toks, tags, unit="clause"):
    """The competition domains.  `clause` = the predicate rescue's OWN clause_spans (punctuation, coordinators,
    subordinators -- the closed-class cues a reader has before any parse), so the two consumers share one segmentation."""
    n = len(toks)
    if unit == "sent":
        return [list(range(n))]
    from hdlab.predicate_detector import clause_spans
    span = clause_spans(list(toks), list(tags))
    out = defaultdict(list)
    for i in range(n):
        out[span[i]].append(i)
    return [out[k] for k in sorted(out)]


def constrained_posterior(lc, toks, alpha=1.0, unit="clause", gate="aux", lag="live", ret_w=False):
    """The category posterior REVISED by the clause's predicate-slot expectation (the math in the block above).
    gate: which clauses carry the expectation --
      "all"    every clause domain;
      "aux"    a clause holding a TENSE CARRIER (an AUX-tagged token): a finite clause asserts, so it has a predicate;
      "auxbh"  the same, restricted to a `be`/`have` carrier (the convention's own population)."""
    from hdlab.attachment_arm import AUX_BE, AUX_HAVE
    le, post = _le_and_post(lc, list(toks), lag=lag)
    n = len(toks)
    if n == 0:
        return (post, {}) if ret_w else post
    vi = lc.tags.index("VERB")
    tags = [lc.tags[int(post[i].argmax())] for i in range(n)]
    lows = [t.lower() for t in toks]
    units = clause_units(toks, tags, unit=unit)
    logZ = None
    out = post.copy(); ws = {}
    for ix in units:
        if not ix:
            continue
        if gate != "all":
            carriers = [i for i in ix if tags[i] == "AUX"]
            if gate == "auxbh":
                carriers = [i for i in carriers if lows[i] in AUX_BE or lows[i] in AUX_HAVE]
            if not carriers:
                continue
        if logZ is None:
            logZ = _logZ(lc, le)
        le2 = le.copy()
        for i in ix:
            le2[i, vi] = NEG
        w = float(np.exp(min(0.0, _logZ(lc, le2) - logZ)))
        ws[ix[0]] = w
        if w <= 1e-9 or w >= 1.0 - 1e-9:
            continue
        pn = lc._posterior_le(le2, LC.LAG if lag == "live" else lag)
        for i in ix:
            row = (post[i] - w * pn[i]) / (1.0 - w)
            row = np.clip(row, 0.0, None)
            s = row.sum()
            if s <= 0:
                continue
            row = row / s
            out[i] = (1.0 - alpha) * post[i] + alpha * row
    if ret_w:
        return out, ws
    return out


def tags_from(lc, post):
    return [lc.tags[int(post[i].argmax())] for i in range(post.shape[0])]


def dist_from(lc, post, eps=0.01):
    return [{t: float(post[i, j]) for j, t in enumerate(lc.tags) if post[i, j] >= eps} for i in range(post.shape[0])]


# ------------------------------------------------------------------ phase 2: the categories rung, measured
def _boot(pairs, n=2000, seed=0):
    """Paired bootstrap over SENTENCES of a (hit_a, hit_b, n_items) per-sentence list -> (mean delta, lo, hi)."""
    rng = np.random.default_rng(seed)
    A = np.array([p[0] for p in pairs], float); B = np.array([p[1] for p in pairs], float)
    N = np.array([p[2] for p in pairs], float)
    tot = N.sum() or 1.0
    d0 = (A.sum() - B.sum()) / tot
    m = len(pairs)
    if m == 0:
        return 0.0, 0.0, 0.0
    idx = rng.integers(0, m, size=(n, m))
    ds = (A[idx].sum(1) - B[idx].sum(1)) / np.maximum(N[idx].sum(1), 1e-9)
    return float(d0), float(np.quantile(ds, 0.025)), float(np.quantile(ds, 0.975))


def cat(cap=700, arms=None, seed=0):
    """Category accuracy under the clause predicate-slot constraint: overall, and on the VERB-as-AUX class that
    carries 58% of the tag-to-head loss.  Floor = the organ as it stands.  Twin = the same NUMBER of AUX tokens
    flipped to VERB at random."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    arms = arms or [("all|clause|1.0", "all", "clause", 1.0), ("aux|clause|1.0", "aux", "clause", 1.0),
                    ("auxbh|clause|1.0", "auxbh", "clause", 1.0), ("aux|sent|1.0", "aux", "sent", 1.0),
                    ("auxbh|sent|1.0", "auxbh", "sent", 1.0)]
    rng = np.random.default_rng(seed)
    res = {}
    base_rows = []
    for toks, gold_pos, gold_heads, rels in test:
        le, post = _le_and_post(lc, list(toks))
        base_rows.append((toks, gold_pos, post))
    def score(tag_of):
        ok = 0; tot = 0; cls_ok = 0; cls_n = 0; flips = 0; per_sent = []
        for (toks, gold_pos, post) in base_rows:
            tg = tag_of(toks, gold_pos, post)
            bs = tags_from(lc, post)
            s_ok = 0
            for i, g in enumerate(gold_pos):
                tot += 1
                if tg[i] == g:
                    ok += 1; s_ok += 1
                if bs[i] != tg[i]:
                    flips += 1
                if g == "VERB" and bs[i] == "AUX":
                    cls_n += 1
                    if tg[i] == "VERB":
                        cls_ok += 1
            per_sent.append((s_ok, len(gold_pos)))
        return {"acc": ok / max(1, tot), "n_tok": tot, "class_recovered": cls_ok, "class_n": cls_n,
                "flips_vs_base": flips, "per_sent": per_sent}
    base = score(lambda t, g, post: tags_from(lc, post))
    res["base"] = {k: v for k, v in base.items() if k != "per_sent"}
    print("BASE  acc %.4f  VERB-as-AUX class recovered %d/%d" % (base["acc"], base["class_recovered"], base["class_n"]))
    for name, gate, unit, alpha in arms:
        def tag_of(toks, g, post, gate=gate, unit=unit, alpha=alpha):
            return tags_from(lc, constrained_posterior(lc, toks, alpha=alpha, unit=unit, gate=gate))
        a = score(tag_of)
        pairs = [(x[0], y[0], x[1]) for x, y in zip(a["per_sent"], base["per_sent"])]
        d, lo, hi = _boot(pairs, seed=seed)
        res[name] = {k: v for k, v in a.items() if k != "per_sent"}
        res[name].update({"d_acc": d, "ci": [lo, hi]})
        print("%-18s acc %.4f (%+.4f CI[%+.4f,%+.4f])  class %d/%d  flips %d"
              % (name, a["acc"], d, lo, hi, a["class_recovered"], a["class_n"], a["flips_vs_base"]))
    # INFORMATION-FREE TWIN: flip the same number of AUX-tagged tokens to VERB, chosen at random
    best = max((k for k in res if k != "base"), key=lambda k: res[k]["flips_vs_base"])
    k_flip = res[best]["flips_vs_base"]
    aux_sites = [(si, i) for si, (toks, g, post) in enumerate(base_rows)
                 for i, t in enumerate(tags_from(lc, post)) if t == "AUX"]
    twins = []
    for s_i in range(3):
        rr = np.random.default_rng(seed + 100 + s_i)
        pick = set(map(tuple, np.array(aux_sites)[rr.choice(len(aux_sites), size=min(k_flip, len(aux_sites)), replace=False)].tolist()))
        def tag_of(toks, g, post, si=[0], pick=pick):
            tg = tags_from(lc, post)
            return [("VERB" if (si[0], i) in pick else t) for i, t in enumerate(tg)]
        ok = 0; tot = 0; cok = 0; cn = 0
        for si, (toks, gold_pos, post) in enumerate(base_rows):
            bs = tags_from(lc, post)
            tg = [("VERB" if (si, i) in pick else t) for i, t in enumerate(bs)]
            for i, gp in enumerate(gold_pos):
                tot += 1
                if tg[i] == gp:
                    ok += 1
                if gp == "VERB" and bs[i] == "AUX":
                    cn += 1
                    if tg[i] == "VERB":
                        cok += 1
        twins.append({"acc": ok / tot, "class_recovered": cok, "class_n": cn})
        print("TWIN seed %d  acc %.4f  class %d/%d (k=%d)" % (s_i, ok / tot, cok, cn, k_flip))
    res["twin"] = twins
    json.dump(res, open(os.path.join(out_dir(), "cat.json"), "w", encoding="utf-8"), indent=1)
    return res


def flips(cap=700, gate="aux", unit="clause", alpha=1.0, show=25):
    """WHICH tokens the constraint moves, and whether UD agrees -- the audit behind the accuracy delta."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    good = Counter(); bad = Counter(); ex_bad = []; ex_good = []
    for toks, gold_pos, gold_heads, rels in test:
        le, post = _le_and_post(lc, list(toks))
        b = tags_from(lc, post)
        p2 = constrained_posterior(lc, toks, alpha=alpha, unit=unit, gate=gate)
        t2 = tags_from(lc, p2)
        for i in range(len(toks)):
            if b[i] == t2[i]:
                continue
            key = (gold_pos[i], b[i], t2[i])
            if t2[i] == gold_pos[i]:
                good[key] += 1
                if len(ex_good) < show:
                    ex_good.append("%-10s %s->%s (gold %s) | %s" % (toks[i], b[i], t2[i], gold_pos[i], " ".join(toks)[:90]))
            elif b[i] == gold_pos[i]:
                bad[key] += 1
                if len(ex_bad) < show:
                    ex_bad.append("%-10s %s->%s (gold %s) | %s" % (toks[i], b[i], t2[i], gold_pos[i], " ".join(toks)[:90]))
    print("REPAIRS (%d):" % sum(good.values()))
    for k, v in good.most_common(12):
        print("   gold %-6s %s -> %-6s  n=%d" % (k[0], k[1], k[2], v))
    print("BREAKS (%d):" % sum(bad.values()))
    for k, v in bad.most_common(12):
        print("   gold %-6s %s -> %-6s  n=%d" % (k[0], k[1], k[2], v))
    print("-- example breaks --")
    for e in ex_bad[:show]:
        print("  ", e)
    print("-- example repairs --")
    for e in ex_good[:12]:
        print("  ", e)
    return {"repairs": sum(good.values()), "breaks": sum(bad.values())}


# ------------------------------------------------------------------ THE ONE SHARED QUANTITY
def predicate_slot(lc, toks, alpha=1.0, unit="clause", gate="aux", lag="live"):
    """P(token i is the verbal predicate of its clause | the clause HAS a predicate), per token -- the exact
    renormalisation above.  ONE number, read by the governor AND by the predicate rescue.
    Returns (occ [n], revised posterior [n, T], w per clause)."""
    post2, ws = constrained_posterior(lc, toks, alpha=alpha, unit=unit, gate=gate, lag=lag, ret_w=True)
    vi = lc.tags.index("VERB")
    return post2[:, vi].astype(float), post2, ws


# =====================================================================================================================
# THE PREDICATE-SLOT OCCUPANCY, v2 -- the FUNCTION an auxiliary performs, read gradedly off the organ's posterior.
# ---------------------------------------------------------------------------------------------------------------------
# MEASURED NEGATIVE that forced this form (gov --cap 250, gate "aux"): conditioning on "the clause has a VERB" fires on
# EVERY sole-AUX clause, and a sole-AUX clause is USUALLY A COPULAR ONE, whose predicate slot is already occupied by a
# non-verbal predicate the arm promotes itself (cop_predicates).  Result: cop arcs 0.727 -> 0.505, UAS -0.0172.
# The slot is not empty -- it is filled by something the VERB mask cannot see.
#
# THE FUNCTION, stated exactly (Pustet 2003 on the copula; Bybee 1994 on auxiliation).  An auxiliary carries TENSE for
# a predicate that is not itself finite.  There are exactly three ways a clause's tense carrier can be discharged:
#   (1) a VERBAL HOST in its own verb group           -> the host is the predicate          (an ordinary auxiliary)
#   (2) a NON-VERBAL PREDICATE predicated of a SUBJECT -> the complement is the predicate    (copular predication)
#   (3) neither                                       -> THE CARRIER ITSELF is the predicate (existential / possessive)
# so
#     occ_i = (1 - P(verbal host in i's verb group)) * (1 - P(copular predication available at i))
# Term 1 is GRADED off the category posterior (max P(VERB) over the verb-group continuation: adverbs and negation are
# skipped; infinitival `to`, a preposition, a subordinator, a coordinator or punctuation CLOSE the group, because a
# verb behind any of them belongs to another clause -- the same locality cop_predicates already respects, which is why
# `have to see` leaves `have` predicative).  Term 2 is a CONSTRUCTION test: `have` is never a copula, and a `be` whose
# pivot is the expletive `there` predicates EXISTENCE rather than a property of a subject (Goldberg 1995 -- the
# existential-there construction is acquired as a construction; `there` is a closed-class form, like the WH_FORMS and
# COP_FORMS lists this organ already carries).
# =====================================================================================================================

EXPLETIVE = frozenset({"there"})
NP_COMPLEMENT = os.environ.get("HDLAB_PS_NP_COMPLEMENT", "1") == "1"   # phase-4 ablation switch
_SKIP = frozenset({"ADV", "INTJ"})
_NEG = frozenset({"not", "n't", "never", "also", "just", "really", "only", "still", "already", "n`t"})
# the forms that can HEAD a clause on their own.  A modal cannot (Bybee 1994: modals are the fully auxiliated class);
# `be` predicates existence or location, `have` possession, `do` an activity.
MAIN_VERB_CARRIERS = None


def _carriers():
    global MAIN_VERB_CARRIERS
    if MAIN_VERB_CARRIERS is None:
        from hdlab.attachment_arm import AUX_BE, AUX_HAVE
        MAIN_VERB_CARRIERS = frozenset(set(AUX_BE) | set(AUX_HAVE) | {"do", "does", "did", "doing", "done"})
    return MAIN_VERB_CARRIERS


def host_belief(lc, toks, tags, post, i):
    """P(a VERBAL HOST stands in the verb group of the tense carrier at 0-based i) -- graded, off the organ's own
    posterior.  The verb group is CONTIGUOUS modulo adverbs / negation / an inverted subject pronoun, and an
    auxiliary CHAIN counts (`has been roiled`: the host of `has` is `been`, itself a carrier), so the host belief is
    P(VERB) + P(AUX) at the position reached.  Infinitival `to` CLOSES the group (`have to see` leaves `have`
    predicative -- a to-infinitive is a complement, not an auxiliary's host).
    THE WALK IS GRADED, NOT ARGMAX (the discipline pri 107 named): stepping over an intervening token costs that
    token's own belief that it is skippable, P(ADV) + P(PART) + P(PRON under inversion), so a word the organ is
    unsure about cannot silently carry the walk into the next phrase.  Measured: `i have stronger will than you
    think` -- `stronger` is argmax-ADV, so the argmax walk stepped over it and read the NOUN `will` (argmax-AUX)
    as the host, scoring the possessive `have` 0.04; the graded walk scores it by P(ADV | stronger)."""
    from hdlab.attachment_arm import AUX_MOD
    vi = lc.tags.index("VERB"); ai = lc.tags.index("AUX")
    advi = lc.tags.index("ADV"); pai = lc.tags.index("PART"); pri = lc.tags.index("PRON")
    n = len(toks); lows = [t.lower() for t in toks]
    reach = 1.0; best = 0.0; seen_pron = False
    for k in range(i + 1, n):
        if tags[k] == "PART" and lows[k] == "to":
            break
        # AUXILIARY ORDER (modal > have > be > V; Chomsky 1957's Aux rule, a PINNED descriptive fact of English):
        # a MODAL can never be the host of a `have` / `be` / `do` carrier (*have will), so its AUX belief cannot count
        # as host evidence.  Without this, `i have stronger will than you think` reads the NOUN `will` -- which this
        # organ tags AUX -- as the host of the possessive `have`, and the carrier scores 0.24 instead of 0.99.
        v = float(post[k, vi]) + (0.0 if lows[k] in AUX_MOD else float(post[k, ai]))
        best = max(best, min(1.0, reach * v))
        skip = float(post[k, advi] + post[k, pai])
        if lows[k] in _NEG:
            skip = max(skip, 1.0)
        if not seen_pron and k <= i + 2 and lows[k] not in EXPLETIVE:
            skip = max(skip, float(post[k, pri]))        # subject-auxiliary inversion: "Should HE have known"
            seen_pron = True
        reach *= min(1.0, skip)
        if reach < 0.02:
            break
    return min(1.0, best)


def is_existential(toks, tags, i):
    """The existential-there construction (Goldberg 1995): the pivot adjacent to the carrier is the expletive
    `there`, so nothing is predicated OF anything and the carrier asserts EXISTENCE."""
    lows = [t.lower() for t in toks]
    n = len(toks)
    for k in range(i - 1, max(-1, i - 4), -1):
        if tags[k] in _SKIP or lows[k] in _NEG or tags[k] == "AUX":
            continue                                     # the pivot sits before the WHOLE chain: "there had BEEN none"
        if lows[k] in EXPLETIVE:
            return True
        break
    for k in range(i + 1, min(n, i + 3)):
        if tags[k] in _SKIP or lows[k] in _NEG:
            continue
        if lows[k] in EXPLETIVE:
            return True
        break
    return False


def copular_available(toks, tags, i):
    """1.0 when the carrier at 0-based i is a COPULA with a PREDICABLE COMPLEMENT -- the predicate slot is then held
    by that non-verbal predicate, which the governor's `cop_predicates` already promotes and which UD makes the
    clause head.  0.0 when the carrier cannot be a copula at all (`have` / `do`), when the construction is
    existential (nothing is predicated OF anything), or when no complement follows (a bare locative / elliptical
    `be`, which predicates by itself).
    The COMPLEMENT, not the subject, is the test: measured on UD-EWT test 700, keying on the subject instead left 31
    false promotions, 26 of them copular clauses whose subject scan failed (inversion, a participial NP, a fronted
    PP) -- the slot's occupant is the complement, so that is what has to be looked for."""
    from hdlab.attachment_arm import COP_FORMS
    lows = [t.lower() for t in toks]
    if lows[i] not in COP_FORMS or is_existential(toks, tags, i):
        return 0.0
    from hdlab.attachment_arm import WH_FORMS
    det = False
    for k in range(i + 1, len(toks)):
        if tags[k] == "DET":
            # A DETERMINER OPENS A NOMINAL, and that nominal IS the copula's complement (NP_COMPLEMENT, phase 4):
            # whatever stands next belongs to the phrase the determiner opened, so its own argmax category is not the
            # question. Without this, `Here is a revised draft` reads the participial modifier `revised` (argmax-VERB)
            # as if a verb stood in the complement position, and the copula is promoted.
            det = True
            if k == len(toks) - 1 or all(tags[m] == "PUNCT" for m in range(k + 1, len(toks))):
                return 1.0                               # a clause-final determiner is a demonstrative: `Wtf is this ?`
            continue
        if tags[k] in _SKIP or tags[k] == "NUM" or lows[k] in _NEG or tags[k] == "PUNCT":
            continue                                     # "The answer is , \" Yes ! \"" -- the complement is behind the comma
        if det and NP_COMPLEMENT:
            return 1.0
        if tags[k] == "SCONJ" or lows[k] in WH_FORMS or tags[k] == "PART":
            return 1.0                                   # a CLAUSAL / infinitival complement occupies the slot too
        if tags[k] in ("ADJ", "NOUN", "PROPN", "PRON", "ADP", "SYM", "X", "INTJ"):
            return 1.0
        return 0.0
    return 0.0


def predicate_slot_v2(lc, toks, tags=None, post=None, use_clause_mass=False, alpha=1.0,
                      unit="clause", gate="aux"):
    """occ per token: P(this token occupies its clause's predicate slot).  Non-AUX tokens score 0 (the rescue's noun
    arm and the arm's VERB cues already own them); an AUX scores the product in the block above.
    use_clause_mass: multiply in the EXACT clause-level mass P(no VERB anywhere in the clause) as well."""
    if post is None:
        _le, post = _le_and_post(lc, list(toks))
    if tags is None:
        tags = tags_from(lc, post)
    n = len(toks)
    occ = np.zeros(n)
    ws = {}
    if use_clause_mass:
        _o, _p2, ws = predicate_slot(lc, toks, alpha=alpha, unit=unit, gate=gate)
    lows = [t.lower() for t in toks]
    carriers = _carriers()
    for i in range(n):
        if tags[i] != "AUX" or lows[i] not in carriers:
            continue                                    # a MODAL cannot head a clause
        a = 1.0 - host_belief(lc, toks, tags, post, i)
        b = 1.0 - copular_available(toks, tags, i)
        occ[i] = a * b
        if use_clause_mass and ws:
            occ[i] *= 1.0
    return occ


def occ_audit(cap=700, th=0.5, show=30):
    """Precision/recall of the predicate-slot signal against UD's OWN VERB column on the AUX population -- the one
    question UD CAN adjudicate (is this be/have a main verb or an auxiliary?), since UD marks existential `be` and
    possessive `have` VERB and the copula AUX."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    tp = fp = fn = 0; n_aux = 0
    ex_fp = []; ex_fn = []
    hist = Counter()
    for toks, gold_pos, gold_heads, rels in test:
        le, post = _le_and_post(lc, list(toks))
        tags = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        for i in range(len(toks)):
            if tags[i] != "AUX":
                continue
            n_aux += 1
            hist[round(float(occ[i]), 1)] += 1
            promoted = occ[i] >= th
            gold_v = gold_pos[i] == "VERB"
            if promoted and gold_v:
                tp += 1
            elif promoted and not gold_v:
                fp += 1
                if len(ex_fp) < show:
                    ex_fp.append("%-8s occ=%.2f gold=%s rel=%s | %s" % (toks[i], occ[i], gold_pos[i], rels[i], " ".join(toks)[:95]))
            elif (not promoted) and gold_v:
                fn += 1
                if len(ex_fn) < show:
                    ex_fn.append("%-8s occ=%.2f gold=%s rel=%s | %s" % (toks[i], occ[i], gold_pos[i], rels[i], " ".join(toks)[:95]))
    print("AUX tokens %d | promoted@%.2f: TP %d  FP %d  FN %d  -> precision %.4f recall %.4f"
          % (n_aux, th, tp, fp, fn, tp / max(1, tp + fp), tp / max(1, tp + fn)))
    print("occ histogram:", dict(sorted(hist.items())))
    print("-- false promotions (gold AUX) --")
    for e in ex_fp:
        print("  ", e)
    print("-- missed (gold VERB, not promoted) --")
    for e in ex_fn:
        print("  ", e)
    return {"tp": tp, "fp": fp, "fn": fn, "n_aux": n_aux}


def revise_posterior(lc, toks, post, tags=None, th=0.5, occ=None):
    """THE HAND-OFF, REVISED ONCE.  The category organ hands DOWN a posterior; the clause's predicate-slot
    occupancy is a top-down constraint on that belief (MacDonald 1994 constraint satisfaction), so it is applied
    HERE, before the hand-off, and every consumer downstream reads the revised belief without a second organ:
        P'(VERB) = occ,   P'(t != VERB) = P(t) * (1 - occ) / (1 - P(VERB))
    Only a tense carrier its clause leaves holding the predicate slot is touched; every other token is byte-identical."""
    if tags is None:
        tags = tags_from(lc, post)
    if occ is None:
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
    vi = lc.tags.index("VERB")
    out = post.copy()
    sites = []
    for i in range(len(toks)):
        if tags[i] != "AUX" or occ[i] < th:
            continue
        pv = float(post[i, vi])
        if occ[i] <= pv:
            continue
        scale = (1.0 - occ[i]) / max(1e-9, 1.0 - pv)
        out[i] = out[i] * scale
        out[i, vi] = occ[i]
        out[i] = out[i] / max(1e-12, out[i].sum())
        sites.append(i)
    return out, sites


def gov_live(cap=700, seed=0, th=0.5, twin_seeds=3):
    """THE LIVE A/B.  Both arms are the frontend's own configuration -- the category organ's graded posterior handed
    to `arc_scores_graded` -- so the only difference is whether the predicate-slot constraint was applied to that
    posterior before the hand-off."""
    from hdlab.predicate_detector import clause_spans
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities()
    cache = []
    rows = {a: [] for a in ("base", "occ")}
    per_rel = {a: defaultdict(lambda: [0, 0]) for a in ("base", "occ", "twin")}
    per_rel_sub = {a: defaultdict(lambda: [0, 0]) for a in ("base", "occ", "twin")}
    n_sites = 0; n_sub = 0; sent_rel = []
    for toks, gold_pos, gold_heads, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks))
        tags = tags_from(lc, post)
        dist = dist_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        post2, sites = revise_posterior(lc, toks, post, tags=tags, th=th, occ=occ)
        tags2 = tags_from(lc, post2); dist2 = dist_from(lc, post2)
        n_sites += len(sites)
        span = clause_spans(list(toks), tags)
        hasv = {c: any(tags[j] == "VERB" for j in range(n) if span[j] == c) for c in set(span)}
        sub_tok = [i for i in range(n) if tags[i] == "AUX" and not hasv[span[i]]]
        keep = None
        if sub_tok:
            n_sub += 1
            cl = set(span[i] for i in sub_tok)
            keep = set(j + 1 for j in range(n) if span[j] in cl)
        A0, nn = AA.arc_scores_graded(list(toks), tags, dist, tab)
        h0 = AA.decode(list(toks), tags, A0, nn)[0]
        A1, _ = AA.arc_scores_graded(list(toks), tags2, dist2, tab)
        h1 = AA.decode(list(toks), tags2, A1, nn)[0]
        srel = {}
        for a, hp, tg in (("base", h0, tags), ("occ", h1, tags2)):
            hit, nt, per = _score_tree(hp, gold_heads, rels, None)
            hs, ns, pers = _score_tree(hp, gold_heads, rels, keep) if keep else (0, 0, {})
            rows[a].append((hit, nt, hs, ns))
            srel[a] = ({r: tuple(v) for r, v in per.items()}, {r: tuple(v) for r, v in (pers or {}).items()})
            for r, (x, y) in per.items():
                per_rel[a][r][0] += x; per_rel[a][r][1] += y
            for r, (x, y) in (pers or {}).items():
                per_rel_sub[a][r][0] += x; per_rel_sub[a][r][1] += y
        sent_rel.append(srel)
        cache.append((toks, gold_pos, gold_heads, rels, tags, post, dist, keep, nn))
    res = {"cap": cap, "th": th, "promoted_tokens": n_sites, "sole_aux_sentences": n_sub, "arms": {}}
    for a in ("base", "occ"):
        R = rows[a]; B = rows["base"]
        uas = sum(r[0] for r in R) / max(1, sum(r[1] for r in R))
        uas_s = sum(r[2] for r in R) / max(1, sum(r[3] for r in R))
        d, lo, hi = _boot([(R[i][0], B[i][0], R[i][1]) for i in range(len(R))], seed=seed)
        ds, los, his = _boot([(R[i][2], B[i][2], R[i][3]) for i in range(len(R))], seed=seed)
        res["arms"][a] = {"uas": uas, "uas_sub": uas_s, "d_uas": d, "ci": [lo, hi], "d_uas_sub": ds, "ci_sub": [los, his],
                          "rel": {r: [per_rel[a][r][0], per_rel[a][r][1]] for r in REL_KEYS if per_rel[a][r][1]},
                          "rel_sub": {r: [per_rel_sub[a][r][0], per_rel_sub[a][r][1]] for r in REL_KEYS if per_rel_sub[a][r][1]}}
        print("%-6s UAS %.4f (%+.4f CI[%+.4f,%+.4f]) | SOLE-AUX UAS %.4f (%+.4f CI[%+.4f,%+.4f])"
              % (a, uas, d, lo, hi, uas_s, ds, los, his))
        print("       all: " + " ".join("%s %.3f(%d)" % (r, per_rel[a][r][0] / per_rel[a][r][1], per_rel[a][r][1]) for r in REL_KEYS if per_rel[a][r][1]))
        print("       sub: " + " ".join("%s %.3f(%d)" % (r, per_rel_sub[a][r][0] / per_rel_sub[a][r][1], per_rel_sub[a][r][1]) for r in REL_KEYS if per_rel_sub[a][r][1]))
    # PER-RELATION PAIRED BOOTSTRAP over sentences, for the relations the bar names
    res["rel_ci"] = {}
    for r in ("root", "cop", "nsubj", "expl", "ccomp", "xcomp", "obj", "obl", "nmod"):
        for scope, sl in (("all", 0), ("sub", 1)):
            pairs = []
            for sr in sent_rel:
                o = sr["occ"][sl].get(r); b = sr["base"][sl].get(r)
                if not o and not b:
                    continue
                pairs.append((o[0] if o else 0, b[0] if b else 0, (o or b)[1]))
            if not pairs or sum(x[2] for x in pairs) == 0:
                continue
            d, lo, hi = _boot(pairs, seed=seed)
            res["rel_ci"]["%s_%s" % (r, scope)] = {"n": sum(x[2] for x in pairs), "d": round(d, 4),
                                                   "ci": [round(lo, 4), round(hi, 4)],
                                                   "sep": bool(lo > 0 or hi < 0)}
            print("  %-6s %-3s n=%-5d occ-base %+.4f CI[%+.4f,%+.4f] %s"
                  % (r, scope, sum(x[2] for x in pairs), d, lo, hi, "SEP" if (lo > 0 or hi < 0) else "ns"))
    aux_sites = [(si, i) for si, c in enumerate(cache) for i in range(len(c[0])) if c[4][i] == "AUX"]
    tw = []
    for s_i in range(twin_seeds):
        rr = np.random.default_rng(seed + 900 + s_i)
        pick = set(aux_sites[j] for j in rr.choice(len(aux_sites), size=min(n_sites, len(aux_sites)), replace=False))
        R = []
        for si, (toks, gold_pos, gold_heads, rels, tags, post, dist, keep, nn) in enumerate(cache):
            ot = np.zeros(len(toks))
            for i in range(len(toks)):
                if (si, i) in pick:
                    ot[i] = 1.0
            p2, st = revise_posterior(lc, toks, post, tags=tags, th=th, occ=ot)
            t2 = tags_from(lc, p2); d2 = dist_from(lc, p2)
            A, _ = AA.arc_scores_graded(list(toks), t2, d2, tab)
            hp = AA.decode(list(toks), t2, A, nn)[0]
            hit, nt, per = _score_tree(hp, gold_heads, rels, None)
            hs, ns, pers = _score_tree(hp, gold_heads, rels, keep) if keep else (0, 0, {})
            R.append((hit, nt, hs, ns))
            if s_i == 0:
                for r, (x, y) in per.items():
                    per_rel["twin"][r][0] += x; per_rel["twin"][r][1] += y
        u = sum(r[0] for r in R) / max(1, sum(r[1] for r in R))
        us = sum(r[2] for r in R) / max(1, sum(r[3] for r in R))
        d, lo, hi = _boot([(R[i][0], rows["base"][i][0], R[i][1]) for i in range(len(R))], seed=seed)
        tw.append({"uas": u, "uas_sub": us, "d": d, "ci": [lo, hi]})
        print("twin%d  UAS %.4f (%+.4f CI[%+.4f,%+.4f]) | SOLE-AUX UAS %.4f" % (s_i, u, d, lo, hi, us))
    res["twin"] = tw
    json.dump(res, open(os.path.join(out_dir(), "gov_live_th%s_cap%d.json" % (th, cap)), "w", encoding="utf-8"), indent=1)
    return res


# ------------------------------------------------------------------ phase 2b: the GOVERNOR, measured
REL_KEYS = ("root", "nsubj", "obj", "obl", "cop", "expl", "ccomp", "advcl", "nmod", "xcomp", "case", "amod", "det")


def _score_tree(hp, gold_heads, rels, keep):
    """(hits, n, per-relation [hits, n]) restricted to 1-based indices in `keep` when given."""
    hit = 0; n = 0; per = defaultdict(lambda: [0, 0])
    for i, g in enumerate(gold_heads, start=1):
        if not (0 <= g <= len(gold_heads)):
            continue
        if keep is not None and i not in keep:
            continue
        n += 1; ok = 1 if hp.get(i, -1) == g else 0; hit += ok
        r = rels[i - 1]
        per[r][0] += ok; per[r][1] += 1
    return hit, n, per


def _occ_mix_tree(lc, toks, tags, occ, tab, A0, nn, th):
    """THE GRADED HAND-OFF, through the arm's OWN first-order category mixture (`arc_scores_graded`): a tense carrier
    its clause leaves holding the predicate slot is handed down as P(VERB) = occ, P(AUX) = 1 - occ.  Above the arm's
    own tau the promotion is full; below it the AUX reading stays alive and the activations are mixed."""
    sites = [i for i in range(len(toks)) if tags[i] == "AUX" and occ[i] >= th]
    if not sites:
        return AA.decode(list(toks), list(tags), A0, nn)[0]
    pos2 = list(tags); tp = []
    for i in range(len(toks)):
        if i in sites:
            pos2[i] = "VERB"
            tp.append({"VERB": float(min(1.0, occ[i])), "AUX": float(max(0.0, 1.0 - occ[i]))})
        else:
            tp.append({tags[i]: 1.0})
    A, _ = AA.arc_scores_graded(list(toks), pos2, tp, tab)
    return AA.decode(list(toks), pos2, A, nn)[0]


def gov(cap=700, seed=0, arms=("base", "revised", "occ_aux"), th=0.3, alpha=1.0, gate="aux", unit="clause"):
    """Heads on UD-EWT test under the LIVE chain, with and without the predicate-slot signal.
    Populations: ALL sentences, and the SOLE-AUX CLAUSES (a clause the organ tags with an AUX and no VERB) --
    defined on the PREDICTION side only, so no gold is consulted to build the population."""
    from hdlab.predicate_detector import clause_spans
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities()
    rng = np.random.default_rng(seed)
    arms = list(arms)
    rows = {a: [] for a in arms + ["twin"]}
    per_rel = {a: defaultdict(lambda: [0, 0]) for a in arms + ["twin"]}
    per_rel_sub = {a: defaultdict(lambda: [0, 0]) for a in arms + ["twin"]}
    n_sub_sent = 0; n_occ_tok = 0; cache = []
    for toks, gold_pos, gold_heads, rels in test:
        n = len(toks)
        le, post = _le_and_post(lc, list(toks))
        base_tags = tags_from(lc, post)
        if gate == "fn":
            base_tags0 = tags_from(lc, post)
            occ = predicate_slot_v2(lc, toks, tags=base_tags0, post=post)
            post2 = post; rev_tags = list(base_tags0)
        else:
            occ, post2, ws = predicate_slot(lc, toks, alpha=alpha, unit=unit, gate=gate)
            rev_tags = tags_from(lc, post2)
        span = clause_spans(list(toks), base_tags)
        hasv = {c: any(base_tags[j] == "VERB" for j in range(n) if span[j] == c) for c in set(span)}
        sub_tok = set(i + 1 for i in range(n) if base_tags[i] == "AUX" and not hasv[span[i]])
        keep = None
        if sub_tok:
            n_sub_sent += 1
            cl = set(span[i - 1] for i in sub_tok)
            keep = set(j + 1 for j in range(n) if span[j] in cl)
        trees = {}
        A0, nn = AA.arc_scores(list(toks), base_tags, tab)
        trees["base"] = AA.decode(list(toks), base_tags, A0, nn)[0]
        if "revised" in arms:
            A1, _ = AA.arc_scores(list(toks), rev_tags, tab)
            trees["revised"] = AA.decode(list(toks), rev_tags, A1, nn)[0]
        if "occ_aux" in arms:
            trees["occ_aux"] = _occ_mix_tree(lc, toks, base_tags, occ, tab, A0, nn, th)
        n_occ_tok += sum(1 for i in range(n) if base_tags[i] == "AUX" and occ[i] >= th)
        cache.append((toks, gold_pos, gold_heads, rels, base_tags, occ, keep, A0, nn))
        for a, hp in trees.items():
            h, nt, per = _score_tree(hp, gold_heads, rels, None)
            hs, ns, pers = _score_tree(hp, gold_heads, rels, keep) if keep else (0, 0, {})
            rows[a].append((h, nt, hs, ns))
            for r, (x, y) in per.items():
                per_rel[a][r][0] += x; per_rel[a][r][1] += y
            for r, (x, y) in (pers or {}).items():
                per_rel_sub[a][r][0] += x; per_rel_sub[a][r][1] += y
    # INFORMATION-FREE TWIN (the brief's own): the SAME NUMBER of AUX tokens, chosen at random over the whole test
    # set, promoted with the same strength.  Three seeds.
    aux_sites = [(si, i) for si, c in enumerate(cache) for i in range(len(c[0])) if c[4][i] == "AUX"]
    twin_rows = []
    for s_i in range(3):
        rr = np.random.default_rng(seed + 700 + s_i)
        pick = set()
        for j in rr.choice(len(aux_sites), size=min(n_occ_tok, len(aux_sites)), replace=False):
            pick.add(aux_sites[j])
        R = []
        for si, (toks, gold_pos, gold_heads, rels, base_tags, occ, keep, A0, nn) in enumerate(cache):
            ot = np.zeros(len(toks))
            for i in range(len(toks)):
                if (si, i) in pick:
                    ot[i] = 1.0
            hp = _occ_mix_tree(lc, toks, base_tags, ot, tab, A0, nn, th)
            h, nt, per = _score_tree(hp, gold_heads, rels, None)
            hs, ns, pers = _score_tree(hp, gold_heads, rels, keep) if keep else (0, 0, {})
            R.append((h, nt, hs, ns))
            if s_i == 0:
                for r, (x, y) in per.items():
                    per_rel["twin"][r][0] += x; per_rel["twin"][r][1] += y
                for r, (x, y) in (pers or {}).items():
                    per_rel_sub["twin"][r][0] += x; per_rel_sub["twin"][r][1] += y
        twin_rows.append(R)
        if s_i == 0:
            rows["twin"] = R
    res = {"cap": cap, "th": th, "alpha": alpha, "gate": gate, "unit": unit,
           "sole_aux_sentences": n_sub_sent, "occ_promoted_tokens": n_occ_tok, "arms": {}}
    base_rows = rows["base"]
    for a in rows:
        R = rows[a]
        uas = sum(r[0] for r in R) / max(1, sum(r[1] for r in R))
        uas_s = sum(r[2] for r in R) / max(1, sum(r[3] for r in R))
        d, lo, hi = _boot([(R[i][0], base_rows[i][0], R[i][1]) for i in range(len(R))], seed=seed)
        ds, los, his = _boot([(R[i][2], base_rows[i][2], R[i][3]) for i in range(len(R))], seed=seed)
        res["arms"][a] = {"uas": uas, "uas_sub": uas_s, "d_uas": d, "ci": [lo, hi],
                          "d_uas_sub": ds, "ci_sub": [los, his],
                          "rel": {r: round(per_rel[a][r][0] / max(1, per_rel[a][r][1]), 4) for r in REL_KEYS if per_rel[a][r][1]},
                          "rel_n": {r: per_rel[a][r][1] for r in REL_KEYS if per_rel[a][r][1]},
                          "rel_sub": {r: round(per_rel_sub[a][r][0] / max(1, per_rel_sub[a][r][1]), 4) for r in REL_KEYS if per_rel_sub[a][r][1]},
                          "rel_sub_n": {r: per_rel_sub[a][r][1] for r in REL_KEYS if per_rel_sub[a][r][1]}}
        A = res["arms"][a]
        print("%-9s UAS %.4f (%+.4f CI[%+.4f,%+.4f]) | SOLE-AUX UAS %.4f (%+.4f CI[%+.4f,%+.4f])"
              % (a, uas, d, lo, hi, uas_s, ds, los, his))
        print("          all: " + " ".join("%s %.3f(%d)" % (r, A["rel"][r], A["rel_n"][r]) for r in REL_KEYS if r in A["rel"]))
        print("          sub: " + " ".join("%s %.3f(%d)" % (r, A["rel_sub"][r], A["rel_sub_n"][r]) for r in REL_KEYS if r in A["rel_sub"]))
    res["twin_seeds"] = []
    for R in twin_rows:
        u = sum(r[0] for r in R) / max(1, sum(r[1] for r in R))
        us = sum(r[2] for r in R) / max(1, sum(r[3] for r in R))
        res["twin_seeds"].append({"uas": u, "uas_sub": us})
    print("twin seeds: " + " ".join("UAS %.4f/sub %.4f" % (t["uas"], t["uas_sub"]) for t in res["twin_seeds"]))
    json.dump(res, open(os.path.join(out_dir(), "gov_th%s_%s_%s_cap%d.json" % (th, gate, unit, cap)), "w", encoding="utf-8"), indent=1)
    return res


# ------------------------------------------------------------------ phase 2c: the SECOND consumer -- the reader
def reader(cap=2100, th=0.5, cross=150, seed=0, pop="ud"):
    """THE CONVENTION-FREE INSTRUMENT (pri 107's): does the clause produce an EVENT at all?  UD's VERB column cannot
    adjudicate a question about UD's own convention, but `a gold-verb sentence that yields ZERO events` is a whole
    clause every downstream organ never sees, and that is convention-free.
    Arms:  OFF       the reader's UPOS==VERB detector alone
           LIVE      + the landed BF rescue (noun class; the live default)
           AUX107    + pri 107's sole-AUX arm (the BOOLEAN clause gate, HDLAB_PREDICATE_RESCUE_AUX=1)
           OCC       the SAME rescue, but the categories rung hands down the predicate-slot-revised belief
           OCC_AUX   OCC plus the boolean sole-AUX arm on what is left"""
    from hdlab.predicate_detector import (BFPredicateDetector, bf_cue_block, category_emission,
                                          clause_spans, has_verb_reading_glassbox)
    if pop == "qasrl":
        # QA-SRL dev -- the brief's SECOND convention-free population, entirely outside the organ's count supply.
        import gzip
        test = []
        with gzip.open(os.path.join(REPO, "data/benchmark_trap_check/qasrl/qasrl-v2/orig/dev.jsonl.gz"),
                       "rt", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                toks = d["sentenceTokens"]
                gv = set(int(k) for k in d["verbEntries"].keys())
                test.append((toks, ["VERB" if i in gv else "X" for i in range(len(toks))], [], []))
                if len(test) >= cap:
                    break
    else:
        test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    model = BFPredicateDetector.load()
    rth = model.threshold
    ARMS = ("OFF", "LIVE", "AUX107", "OCC", "OCC_AUX", "OCC_COP")
    per = {a: [] for a in ARMS}; blind = {a: 0 for a in ARMS}
    gold_n = []; n_gold_sent = 0; nsent = 0; mism = 0; n_cross = 0
    r_off = None
    for toks, gold_pos, gold_heads, rels in test:
        if not toks or any(" " in t for t in toks):
            continue
        gold_verb = set(i for i, g in enumerate(gold_pos) if g == "VERB")
        _le, post = _le_and_post(lc, list(toks))
        tags = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        post2, sites = revise_posterior(lc, toks, post, tags=tags, th=th, occ=occ)
        tags2 = tags_from(lc, post2)
        base = set(i for i in range(len(toks)) if tags[i] == "VERB")
        base2 = set(i for i in range(len(toks)) if tags2[i] == "VERB")
        cues = bf_cue_block(lc, list(toks), list(tags), post, category_emission(lc, list(toks)))
        cand = [i for i in range(len(toks)) if tags[i] not in ("VERB", "AUX") and has_verb_reading_glassbox(toks[i])]
        bf = set(i for i in cand if model.score(cues[i]) >= rth)
        span = clause_spans(list(toks), tags)
        hv = {c: any(tags[j] == "VERB" for j in range(len(toks)) if span[j] == c) for c in set(span)}
        aux = set(i for i in range(len(toks)) if tags[i] == "AUX" and not hv[span[i]] and model.score(cues[i]) >= rth)
        cues2 = bf_cue_block(lc, list(toks), list(tags2), post2, category_emission(lc, list(toks)))
        cand2 = [i for i in range(len(toks)) if tags2[i] not in ("VERB", "AUX") and has_verb_reading_glassbox(toks[i])]
        bf2 = set(i for i in cand2 if model.score(cues2[i]) >= rth)
        span2 = clause_spans(list(toks), tags2)
        hv2 = {c: any(tags2[j] == "VERB" for j in range(len(toks)) if span2[j] == c) for c in set(span2)}
        aux2 = set(i for i in range(len(toks)) if tags2[i] == "AUX" and not hv2[span2[i]] and model.score(cues2[i]) >= rth)
        # PHASE-4 LEVER (alternate path D, built): a COPULAR clause has a predicate -- the NON-VERBAL COMPLEMENT
        # (Pustet 2003) -- and the occupancy deliberately leaves the copula alone there.  The event should fire on
        # the predicate, and the governor's OWN `cop_predicates` already computes which token that is, so this is a
        # READ of an existing organ, not a new one.  Fires only in a clause the revised tags leave with no VERB.
        cp = set()
        for q in AA.cop_predicates(list(toks), list(tags2)):
            if not hv2[span2[q - 1]]:
                cp.add(q - 1)
        sets = {"OFF": base, "LIVE": base | bf, "AUX107": base | bf | aux,
                "OCC": base2 | bf2, "OCC_AUX": base2 | bf2 | aux2, "OCC_COP": base2 | bf2 | cp}
        for a in ARMS:
            S = sets[a]
            per[a].append((len(S & gold_verb), len(S), len(gold_verb)))
            if gold_verb and not S:
                blind[a] += 1
        if gold_verb:
            n_gold_sent += 1
        gold_n.append(len(gold_verb)); nsent += 1
        if n_cross < cross:
            if r_off is None:
                from hdlab.situation_reader import SituationReader
                r_off = SituationReader(predicate_recall=False)
            ev, _ = r_off._extract_events(" ".join(toks))
            if set(e.idx for e in ev) != base:
                mism += 1
            n_cross += 1
    G = float(sum(gold_n))
    out = {"n_sent": nsent, "n_gold_verbs": int(G), "n_gold_verb_sentences": n_gold_sent,
           "rescue_threshold": rth, "occ_threshold": th,
           "live_reader_crosscheck_sentences": n_cross, "arm_OFF_vs_live_reader_mismatched_sents": mism, "arms": {}}
    for a in ARMS:
        H = sum(x[0] for x in per[a]); F = sum(x[1] for x in per[a])
        out["arms"][a] = {"event_recall": round(H / max(1.0, G), 4),
                          "event_precision": round(H / max(1.0, F), 4),
                          "false_events_per_sent": round((F - H) / max(1, nsent), 4),
                          "blind_gold_verb_sentences": blind[a],
                          "blind_share": round(blind[a] / max(1, n_gold_sent), 4)}
    for a in ARMS:
        if a == "OFF":
            continue
        d, lo, hi = _boot([(per[a][i][0], per["OFF"][i][0], per[a][i][2]) for i in range(nsent)], seed=seed)
        out["arms"][a]["d_recall_vs_OFF"] = [round(d, 4), round(lo, 4), round(hi, 4)]
    for a in ("OCC", "OCC_AUX", "OCC_COP"):
        d, lo, hi = _boot([(per[a][i][0], per["LIVE"][i][0], per[a][i][2]) for i in range(nsent)], seed=seed)
        out["arms"][a]["d_recall_vs_LIVE"] = [round(d, 4), round(lo, 4), round(hi, 4)]
    print("sentences %d (%d with a gold verb), gold verbs %d; OFF-arm vs live reader mismatches %d/%d"
          % (nsent, n_gold_sent, int(G), mism, n_cross))
    print("%-8s %8s %8s %8s %8s %8s" % ("arm", "recall", "precis", "falseEv", "blind", "share"))
    for a in ARMS:
        A = out["arms"][a]
        print("%-8s %8.4f %8.4f %8.4f %8d %8.4f  %s" % (a, A["event_recall"], A["event_precision"],
              A["false_events_per_sent"], A["blind_gold_verb_sentences"], A["blind_share"],
              ("dRecall vs OFF %+.4f CI[%+.4f,%+.4f]" % tuple(A["d_recall_vs_OFF"])) if "d_recall_vs_OFF" in A else ""))
    json.dump(out, open(os.path.join(out_dir(), "reader_%s_cap%d_th%s.json" % (pop, cap, th)), "w", encoding="utf-8"), indent=1)
    return out


# ------------------------------------------------------------------ phase 3: the 7-dimension modern board, A/B
def board(arm="base", th=0.5, n_boot=1000, fast=False):
    """Run the modern 7-dimension board with the predicate-slot revision ON or OFF.  The board's arms read the ONE
    frontend (hdlab/frontend.py), which reads the category organ, so patching the organ's hand-off reaches every
    dimension -- which is exactly why the bar requires this run."""
    name = "one_convention_two_losses_v1_board_" + arm
    os.environ["HDLAB_EXP_NAME"] = name
    if arm != "base":
        lcmod = LC.LexicalCategories
        orig = lcmod.posterior

        def patched(self, words, lag=None):
            post = orig(self, words, lag)
            if post is None or getattr(post, "shape", (0,))[0] == 0:
                return post
            tags = [self.tags[int(post[i].argmax())] for i in range(post.shape[0])]
            occ = predicate_slot_v2(self, list(words), tags=tags, post=post)
            out, _sites = revise_posterior(self, list(words), post, tags=tags, th=th, occ=occ)
            return out
        lcmod.posterior = patched
        LC.get.cache_clear() if hasattr(LC.get, "cache_clear") else None
    import importlib
    B = importlib.import_module("experiments.exp_situation_model_qa_modern_v1")
    if fast:
        # the board cell's OWN capped configuration (its --self-test caps): all 7 core dimensions, heavy new arms
        # off, canonical metrics.json NOT written. An EARLY READ while the full A/B runs -- reported as capped.
        res = B.run(caps={"gum": 40, "ud": 300, "state": 300, "wic_mode": "smoke"}, n_boot=300,
                    run_new_arms=False, write_metrics=False)
        print("BOARD(capped) ARM %s aggregate %.4f" % (arm, res["aggregate_19c_free"]["model_acc"]))
        for k, v in res["per_dimension"].items():
            if v:
                print("   %-20s n=%-6s acc=%.4f floor=%.4f" % (k, v.get("n"), v.get("model_acc", float("nan")),
                                                               v.get("strongest_floor", float("nan"))))
        json.dump({k: {kk: vv for kk, vv in (v or {}).items() if kk in ("n", "model_acc", "strongest_floor", "twin_acc")}
                   for k, v in res["per_dimension"].items()},
                  open(os.path.join(out_dir(), "board_fast_%s.json" % arm), "w", encoding="utf-8"), indent=1)
        return res
    res = B.run(caps={"wic_mode": "full"}, n_boot=n_boot)
    B._print(res)
    print("BOARD ARM %s aggregate %.4f" % (arm, res["aggregate_19c_free"]["model_acc"]))
    return res


# ------------------------------------------------------------------ phase 3: the 7-dimension modern board, A/B
def board(arm="base", th=0.5, n_boot=1000, fast=False):
    """Run the modern 7-dimension board with the predicate-slot revision ON or OFF.  The board's arms read the ONE
    frontend (hdlab/frontend.py), which reads the category organ, so patching the organ's hand-off reaches every
    dimension -- which is exactly why the bar requires this run."""
    name = "one_convention_two_losses_v1_board_" + arm
    os.environ["HDLAB_EXP_NAME"] = name
    if arm != "base":
        lcmod = LC.LexicalCategories
        orig = lcmod.posterior

        def patched(self, words, lag=None):
            post = orig(self, words, lag)
            if post is None or getattr(post, "shape", (0,))[0] == 0:
                return post
            tags = [self.tags[int(post[i].argmax())] for i in range(post.shape[0])]
            occ = predicate_slot_v2(self, list(words), tags=tags, post=post)
            out, _sites = revise_posterior(self, list(words), post, tags=tags, th=th, occ=occ)
            return out
        lcmod.posterior = patched
        LC.get.cache_clear() if hasattr(LC.get, "cache_clear") else None
    import importlib
    B = importlib.import_module("experiments.exp_situation_model_qa_modern_v1")
    if fast:
        # the board cell's OWN capped configuration (its --self-test caps): all 7 core dimensions, heavy new arms
        # off, canonical metrics.json NOT written. An EARLY READ while the full A/B runs -- reported as capped.
        res = B.run(caps={"gum": 40, "ud": 300, "state": 300, "wic_mode": "smoke"}, n_boot=300,
                    run_new_arms=False, write_metrics=False)
        print("BOARD(capped) ARM %s aggregate %.4f" % (arm, res["aggregate_19c_free"]["model_acc"]))
        for k, v in res["per_dimension"].items():
            if v:
                print("   %-20s n=%-6s acc=%.4f floor=%.4f" % (k, v.get("n"), v.get("model_acc", float("nan")),
                                                               v.get("strongest_floor", float("nan"))))
        json.dump({k: {kk: vv for kk, vv in (v or {}).items() if kk in ("n", "model_acc", "strongest_floor", "twin_acc")}
                   for k, v in res["per_dimension"].items()},
                  open(os.path.join(out_dir(), "board_fast_%s.json" % arm), "w", encoding="utf-8"), indent=1)
        return res
    res = B.run(caps={"wic_mode": "full"}, n_boot=n_boot)
    B._print(res)
    print("BOARD ARM %s aggregate %.4f" % (arm, res["aggregate_19c_free"]["model_acc"]))
    return res


# ------------------------------------------------------------------ SELF-TEST (scaffold-free)
PATCH = os.path.join(REPO, "notes", "problems",
                     "one_convention_two_losses_ud_tags_main_verb_be_and_have_as_aux_so_the_governor_and_the"
                     "_predicate_rescue_both_miss_the_clauses_only_verb", "predicate_slot_patch.diff")


def _load_patch_module():
    """Execute the PROPOSED DIFF's OWN added code (the hunk against hdlab/attachment_arm.py) in a fresh namespace,
    so `patch == cell` is tested against the shipped text and not against a copy of it."""
    import io
    import types
    src = io.open(PATCH, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    body = src.split("diff --git a/hdlab/lexical_categories.py")[0]
    lines = [l[1:] for l in body.split("\n") if l.startswith("+") and not l.startswith("+++")]
    code = "\n".join(l for l in lines if not l.strip().startswith('"root_cue_values"')
                     and not l.strip().startswith('"predicate_slot_occupancy"')
                     and not l.strip().startswith('"is_existential"'))
    m = types.ModuleType("patched_predicate_slot")
    from hdlab.attachment_arm import AUX_BE, AUX_HAVE, COP_FORMS, WH_FORMS, NOMINAL, NP_RUN
    from hdlab.attachment_arm import AUX_MOD
    m.__dict__.update({"os": os, "np": np, "AUX_BE": AUX_BE, "AUX_HAVE": AUX_HAVE, "AUX_MOD": AUX_MOD,
                       "COP_FORMS": COP_FORMS, "WH_FORMS": WH_FORMS, "NOMINAL": NOMINAL, "NP_RUN": NP_RUN})
    m.__dict__["Sequence"] = __import__("typing").Sequence
    exec(compile(code, "predicate_slot_patch.diff", "exec"), m.__dict__)
    return m


def self_test():
    import io as _io
    ok = 0
    lc = LC.get()

    def check(name, cond, extra=""):
        nonlocal ok
        assert cond, "FAIL: %s %s" % (name, extra)
        ok += 1
        print("  PASS %s %s" % (name, extra))

    # 1-6: the computation on the constructions it is FOR (no gold, no corpus)
    CASES = [
        ("But there is no proof .", 2, True, "existential be -> the carrier predicates"),
        ("i have stronger will than you think .", 1, True, "possessive have -> the carrier predicates"),
        ("You have to see these slides .", 1, True, "have + to-INFINITIVE: the infinitive is a complement, not a host"),
        ("Google is a nice search engine .", 1, False, "copular be with a complement -> the complement predicates"),
        ("Falluja has long been roiled by tense relations .", 1, False, "auxiliary CHAIN: `been` is the host of `has`"),
        ("The political will to end the crisis expired .", None, None, "a modal form is never a clause head"),
    ]
    for text, idx, want, why in CASES:
        toks = text.split()
        _le, post = _le_and_post(lc, toks)
        tags = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        if idx is None:
            continue
        if want:
            check("occ fires: %s" % why, occ[idx] >= 0.5, "(%s occ=%.3f tag=%s)" % (toks[idx], occ[idx], tags[idx]))
        else:
            check("occ silent: %s" % why, occ[idx] < 0.5, "(%s occ=%.3f tag=%s)" % (toks[idx], occ[idx], tags[idx]))
    # a modal never scores, whatever the structure
    toks = "Important news should , frankly .".split()
    _le, post = _le_and_post(lc, toks); tags = tags_from(lc, post)
    occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
    check("a MODAL is never promoted", all(occ[i] == 0.0 for i in range(len(toks)) if toks[i].lower() == "should"))

    # 7: the revision touches ONLY promoted carriers, and leaves a proper distribution
    toks = "But there is no proof .".split()
    _le, post = _le_and_post(lc, toks); tags = tags_from(lc, post)
    p2, sites = revise_posterior(lc, toks, post, tags=tags, th=0.5)
    check("revision is surgical", sites == [2] and all(np.allclose(p2[i], post[i]) for i in range(len(toks)) if i != 2),
          "(sites=%s)" % sites)
    check("revision stays a distribution", abs(float(p2[2].sum()) - 1.0) < 1e-9 and float(p2[2].min()) >= 0.0)
    check("revision flips the tag", tags_from(lc, p2)[2] == "VERB" and tags[2] == "AUX")

    # 8: PATCH == CELL -- the diff's own code, over real sentences
    M = _load_patch_module()
    test = sentences(TEST, cap=250, maxlen=10**6)
    worst = 0.0; nmis = 0; ntok = 0
    for toks, gp, gh, rl in test:
        _le, post = _le_and_post(lc, list(toks))
        tags = tags_from(lc, post)
        a = predicate_slot_v2(lc, toks, tags=tags, post=post)
        b = M.predicate_slot_occupancy(list(toks), list(tags), post, list(lc.tags))
        for i in range(len(toks)):
            ntok += 1
            worst = max(worst, abs(float(a[i]) - float(b[i])))
            if (a[i] >= 0.5) != (b[i] >= 0.5):
                nmis += 1
        pa, sa = revise_posterior(lc, toks, post, tags=tags, th=0.5)
        pb, sb = M.revise_for_predicate_slot(list(toks), post, list(lc.tags), 0.5)
        if sa != sb or not np.allclose(pa, pb):
            nmis += 1
    check("PATCH == CELL over %d tokens / 250 sentences" % ntok, worst == 0.0 and nmis == 0,
          "(max |cell - patch| = %.1e, decision mismatches %d)" % (worst, nmis))

    # 9: PLASTIC -- the occupancy MOVES when the category organ's counts move (its own online observe path)
    toks = "But there is no proof .".split()
    _le, post = _le_and_post(lc, toks); tags = tags_from(lc, post)
    before = predicate_slot_v2(lc, toks, tags=tags, post=post)[2]
    n_before = lc.emit["VERB"]["proof"]
    lc.observe(["proof"] * 400, ["VERB"] * 400)
    lc.finalize()
    _le2, post_b = _le_and_post(lc, toks); tags_b = tags_from(lc, post_b)
    after = predicate_slot_v2(lc, toks, tags=tags_b, post=post_b)[2]
    check("occupancy is PLASTIC (reading changes it)", after < before,
          "(occ %.4f -> %.4f after observing `proof` as a VERB 400x; n(VERB,proof) %d -> %d)"
          % (before, after, n_before, lc.emit["VERB"]["proof"]))
    LC._LC = None    # the mutated organ must not leak into any later call in this process

    # 10: the diff applies
    import subprocess
    r = subprocess.run(["git", "apply", "--check", os.path.relpath(PATCH, REPO)], cwd=REPO,
                       capture_output=True, text=True)
    check("git apply --check is clean", r.returncode == 0, r.stderr.strip()[:200])
    print("\n[self-test] PASS (%d checks)" % ok)


# ------------------------------------------------------------------ GENERALISATION: a population OUTSIDE the supply
def gum_sentences(cap=1200, maxlen=40, stride=None):
    """GUM/GENTLE (modern, 12+ genres, gold UPOS AND gold heads) -- held out from the category organ's count supply
    (UD-EWT train) and from its own genre.  Taken by STRIDE so every genre file is represented."""
    import glob
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "data/corpora/gum/conllu/*.conllu"))):
        cur = []
        for line in open(f, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if not line.strip():
                if cur and len(cur) <= maxlen:
                    out.append(([c[1] for c in cur], [c[3] for c in cur],
                                [int(c[6]) for c in cur], [c[7].split(":")[0] for c in cur]))
                cur = []
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0] or len(c) < 8 or not c[6].isdigit():
                continue
            cur.append(c)
    if cap and len(out) > cap:
        st = max(1, len(out) // cap)
        out = out[::st][:cap]
    return out


def gum(cap=1200, th=0.5, seed=0):
    """The SAME two measurements on GUM: the occupancy decision against UD's own VERB column, and the governor A/B."""
    from hdlab.predicate_detector import clause_spans
    test = gum_sentences(cap=cap)
    lc = LC.get(); tab = AA.load_attachment_validities()
    tp = fp = fn = n_aux = 0
    rows = {"base": [], "occ": []}
    per_rel = {a: defaultdict(lambda: [0, 0]) for a in ("base", "occ")}
    per_rel_sub = {a: defaultdict(lambda: [0, 0]) for a in ("base", "occ")}
    cache = []; n_sites = 0
    for toks, gold_pos, gold_heads, rels in test:
        n = len(toks)
        _le, post = _le_and_post(lc, list(toks))
        tags = tags_from(lc, post); dist = dist_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        for i in range(n):
            if tags[i] != "AUX":
                continue
            n_aux += 1
            if occ[i] >= th and gold_pos[i] == "VERB":
                tp += 1
            elif occ[i] >= th:
                fp += 1
            elif gold_pos[i] == "VERB":
                fn += 1
        post2, sites = revise_posterior(lc, toks, post, tags=tags, th=th, occ=occ)
        n_sites += len(sites)
        tags2 = tags_from(lc, post2); dist2 = dist_from(lc, post2)
        span = clause_spans(list(toks), tags)
        hasv = {c: any(tags[j] == "VERB" for j in range(n) if span[j] == c) for c in set(span)}
        sub = [i for i in range(n) if tags[i] == "AUX" and not hasv[span[i]]]
        keep = set(j + 1 for j in range(n) if span[j] in set(span[i] for i in sub)) if sub else None
        A0, nn = AA.arc_scores_graded(list(toks), tags, dist, tab)
        h0 = AA.decode(list(toks), tags, A0, nn)[0]
        A1, _ = AA.arc_scores_graded(list(toks), tags2, dist2, tab)
        h1 = AA.decode(list(toks), tags2, A1, nn)[0]
        for a, hp in (("base", h0), ("occ", h1)):
            hit, nt, per = _score_tree(hp, gold_heads, rels, None)
            hs, ns, pers = _score_tree(hp, gold_heads, rels, keep) if keep else (0, 0, {})
            rows[a].append((hit, nt, hs, ns))
            for r, (x, y) in per.items():
                per_rel[a][r][0] += x; per_rel[a][r][1] += y
            for r, (x, y) in (pers or {}).items():
                per_rel_sub[a][r][0] += x; per_rel_sub[a][r][1] += y
        cache.append((toks, gold_pos, gold_heads, rels, tags, post, keep, nn))
    res = {"n_sent": len(test), "n_aux": n_aux, "tp": tp, "fp": fp, "fn": fn,
           "precision": round(tp / max(1, tp + fp), 4), "recall": round(tp / max(1, tp + fn), 4),
           "promoted_tokens": n_sites, "arms": {}}
    print("GUM %d sentences | AUX %d | promoted@%.2f TP %d FP %d FN %d -> precision %.4f recall %.4f"
          % (len(test), n_aux, th, tp, fp, fn, res["precision"], res["recall"]))
    for a in ("base", "occ"):
        R = rows[a]; B = rows["base"]
        uas = sum(r[0] for r in R) / max(1, sum(r[1] for r in R))
        uas_s = sum(r[2] for r in R) / max(1, sum(r[3] for r in R))
        d, lo, hi = _boot([(R[i][0], B[i][0], R[i][1]) for i in range(len(R))], seed=seed)
        ds, los, his = _boot([(R[i][2], B[i][2], R[i][3]) for i in range(len(R))], seed=seed)
        res["arms"][a] = {"uas": uas, "uas_sub": uas_s, "d_uas": d, "ci": [lo, hi], "d_uas_sub": ds, "ci_sub": [los, his],
                          "rel": {r: [per_rel[a][r][0], per_rel[a][r][1]] for r in REL_KEYS if per_rel[a][r][1]}}
        print("%-6s UAS %.4f (%+.4f CI[%+.4f,%+.4f]) | SOLE-AUX UAS %.4f (%+.4f CI[%+.4f,%+.4f])"
              % (a, uas, d, lo, hi, uas_s, ds, los, his))
        print("       " + " ".join("%s %.3f(%d)" % (r, per_rel[a][r][0] / per_rel[a][r][1], per_rel[a][r][1])
                                   for r in REL_KEYS if per_rel[a][r][1]))
    # information-free twin on GUM too
    aux_sites = [(si, i) for si, c in enumerate(cache) for i in range(len(c[0])) if c[4][i] == "AUX"]
    for s_i in range(2):
        rr = np.random.default_rng(seed + 11 + s_i)
        pick = set(aux_sites[j] for j in rr.choice(len(aux_sites), size=min(n_sites, len(aux_sites)), replace=False))
        R = []
        for si, (toks, gold_pos, gold_heads, rels, tags, post, keep, nn) in enumerate(cache):
            ot = np.zeros(len(toks))
            for i in range(len(toks)):
                if (si, i) in pick:
                    ot[i] = 1.0
            p2, _st = revise_posterior(lc, toks, post, tags=tags, th=th, occ=ot)
            t2 = tags_from(lc, p2); d2 = dist_from(lc, p2)
            A, _ = AA.arc_scores_graded(list(toks), t2, d2, tab)
            hp = AA.decode(list(toks), t2, A, nn)[0]
            hit, nt, per = _score_tree(hp, gold_heads, rels, None)
            hs, ns, _p = _score_tree(hp, gold_heads, rels, keep) if keep else (0, 0, {})
            R.append((hit, nt, hs, ns))
        u = sum(r[0] for r in R) / max(1, sum(r[1] for r in R))
        us = sum(r[2] for r in R) / max(1, sum(r[3] for r in R))
        d, lo, hi = _boot([(R[i][0], rows["base"][i][0], R[i][1]) for i in range(len(R))], seed=seed)
        print("twin%d  UAS %.4f (%+.4f CI[%+.4f,%+.4f]) | SOLE-AUX UAS %.4f" % (s_i, u, d, lo, hi, us))
        res.setdefault("twin", []).append({"uas": u, "uas_sub": us, "d": d, "ci": [lo, hi]})
    json.dump(res, open(os.path.join(out_dir(), "gum_th%s_cap%d.json" % (th, cap)), "w", encoding="utf-8"), indent=1)
    return res


def cost(cap=400):
    """READ-TIME COST of the revision, measured on the same path the reader uses."""
    import time
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    t0 = time.perf_counter()
    P = []
    for toks, gp, gh, rl in test:
        _le, post = _le_and_post(lc, list(toks))
        P.append((list(toks), post))
    t1 = time.perf_counter()
    for toks, post in P:
        tags = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        revise_posterior(lc, toks, post, tags=tags, th=0.5, occ=occ)
    t2 = time.perf_counter()
    n = len(test)
    print("posterior %.3f ms/sentence | predicate-slot revision %.3f ms/sentence (+%.1f%%), n=%d"
          % (1000 * (t1 - t0) / n, 1000 * (t2 - t1) / n, 100 * (t2 - t1) / (t1 - t0), n))
    return {"posterior_ms": 1000 * (t1 - t0) / n, "revision_ms": 1000 * (t2 - t1) / n, "n": n}


def cost(cap=400):
    """READ-TIME COST of the revision, measured on the same path the reader uses."""
    import time
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get()
    t0 = time.perf_counter()
    P = []
    for toks, gp, gh, rl in test:
        _le, post = _le_and_post(lc, list(toks))
        P.append((list(toks), post))
    t1 = time.perf_counter()
    for toks, post in P:
        tags = tags_from(lc, post)
        occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
        revise_posterior(lc, toks, post, tags=tags, th=0.5, occ=occ)
    t2 = time.perf_counter()
    n = len(test)
    print("posterior %.3f ms/sentence | predicate-slot revision %.3f ms/sentence (+%.1f%%), n=%d"
          % (1000 * (t1 - t0) / n, 1000 * (t2 - t1) / n, 100 * (t2 - t1) / (t1 - t0), n))
    return {"posterior_ms": 1000 * (t1 - t0) / n, "revision_ms": 1000 * (t2 - t1) / n, "n": n}


# ------------------------------------------------------------------ does it REPAIR the 58% the brief names?
def attrib(cap=700, th=0.5):
    """The brief's own headline statistic, re-measured under the revision.  Replicates
    experiments/_diag_tag_to_head_loss.py: decode heads under GOLD categories and under the ORGAN's categories, and
    attribute every head FLIP (right under gold tags, wrong under organ tags) to the mis-tagged tokens in that
    sentence.  Run for the BASE hand-off and for the REVISED one, so the VERB-as-AUX row can be compared directly."""
    test = sentences(TEST, cap=cap, maxlen=10**6)
    lc = LC.get(); tab = AA.load_attachment_validities()
    out = {}
    for arm in ("base", "occ"):
        conf_loss = Counter(); conf_gain = Counter(); conf_tok = Counter()
        n_loss = n_gain = n_tok = n_tagerr = 0
        for toks, gold_pos, gold_heads, rels in test:
            _le, post = _le_and_post(lc, list(toks))
            tags = tags_from(lc, post)
            if arm == "occ":
                occ = predicate_slot_v2(lc, toks, tags=tags, post=post)
                post, _st = revise_posterior(lc, toks, post, tags=tags, th=th, occ=occ)
                tags = tags_from(lc, post)
            n_tok += len(toks)
            errs = {i + 1: (gold_pos[i], tags[i]) for i in range(len(toks)) if tags[i] != gold_pos[i]}
            n_tagerr += len(errs)
            for pair in errs.values():
                conf_tok[pair] += 1
            if not errs:
                continue
            hg = AA.heads(list(toks), list(gold_pos), tab)
            hp = AA.heads(list(toks), list(tags), tab)
            for i, g in enumerate(gold_heads, start=1):
                if not (0 <= g <= len(toks)):
                    continue
                okg = hg.get(i, -1) == g; okp = hp.get(i, -1) == g
                if okg == okp:
                    continue
                if i in errs:
                    pair = errs[i]
                elif g in errs:
                    pair = errs[g]
                else:
                    pair = errs[min(errs, key=lambda k: abs(k - i))]
                if okg and not okp:
                    n_loss += 1; conf_loss[pair] += 1
                else:
                    n_gain += 1; conf_gain[pair] += 1
        net = n_loss - n_gain
        va = conf_loss[("VERB", "AUX")] - conf_gain.get(("VERB", "AUX"), 0)
        out[arm] = {"tokens": n_tok, "tag_errors": n_tagerr, "tag_agreement": round(1 - n_tagerr / n_tok, 4),
                    "head_flips_lost": n_loss, "head_flips_gained": n_gain, "net_head_loss": net,
                    "net_uas_points": round(100 * net / n_tok, 2),
                    "verb_as_aux_tokens": conf_tok[("VERB", "AUX")], "verb_as_aux_net": va,
                    "verb_as_aux_share_of_net": round(va / max(1, net), 4),
                    "top": [{"gold": k[0], "pred": k[1], "tagerr": conf_tok[k],
                             "net": conf_loss[k] - conf_gain.get(k, 0)}
                            for k, _v in Counter({k: conf_loss[k] - conf_gain.get(k, 0)
                                                  for k in set(conf_loss) | set(conf_gain)}).most_common(6)]}
        A = out[arm]
        print("%-5s tag agreement %.4f | net head loss %d (%.2f UAS points) | VERB-as-AUX: %d tokens, net %d = %.1f%% of it"
              % (arm, A["tag_agreement"], net, A["net_uas_points"], A["verb_as_aux_tokens"], va,
                 100 * A["verb_as_aux_share_of_net"]))
        print("      top confusions by net loss: " + ", ".join("%s->%s %d" % (r["gold"], r["pred"], r["net"]) for r in A["top"]))
    json.dump(out, open(os.path.join(out_dir(), "attrib_cap%d.json" % cap), "w", encoding="utf-8"), indent=1)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--diag" in a:
        diag()
    elif "--cat" in a:
        cat()
    elif "--attrib" in a:
        attrib(cap=int(a[a.index("--cap") + 1]) if "--cap" in a else 700)
    elif "--cost" in a:
        cost()
    elif "--gum" in a:
        gum(cap=int(a[a.index("--cap") + 1]) if "--cap" in a else 1200,
            th=float(a[a.index("--th") + 1]) if "--th" in a else 0.5)
    elif "--self-test" in a:
        self_test()
    elif "--board" in a:
        board(arm=(a[a.index("--arm") + 1] if "--arm" in a else "base"),
              th=float(a[a.index("--th") + 1]) if "--th" in a else 0.5,
              fast="--fast" in a)
    elif "--reader" in a:
        reader(cap=int(a[a.index("--cap") + 1]) if "--cap" in a else 2100,
               th=float(a[a.index("--th") + 1]) if "--th" in a else 0.5,
               pop=(a[a.index("--pop") + 1] if "--pop" in a else "ud"),
               cross=0 if "--pop" in a else 150)
    elif "--gov-live" in a:
        gov_live(cap=int(a[a.index("--cap") + 1]) if "--cap" in a else 700,
                 th=float(a[a.index("--th") + 1]) if "--th" in a else 0.5)
    elif "--gov" in a:
        gov(cap=int(a[a.index("--cap") + 1]) if "--cap" in a else 700,
            th=float(a[a.index("--th") + 1]) if "--th" in a else 0.3,
            gate=(a[a.index("--gate") + 1] if "--gate" in a else "aux"))
    elif "--occ" in a:
        occ_audit(th=float(a[a.index("--th") + 1]) if "--th" in a else 0.5)
    elif "--flips" in a:
        flips(gate=(a[a.index("--gate") + 1] if "--gate" in a else "aux"),
              unit=(a[a.index("--unit") + 1] if "--unit" in a else "clause"))
    else:
        print(__doc__)
