"""exp_commonnoun_referent_linker_v1 -- the FAITHFUL glass-box common-noun discourse-referent former,
measured against the reader's surface-head floor on coref chain-F1 (LitBank gold mentions).

THE BRAIN (PINNED): comprehension opens a DISCOURSE REFERENT for every entity at first mention
(Gernsbacher Structure Building; Kamp/Heim DRT introduction) and re-identifies later mentions by
CONTENT-ADDRESSABLE match over the active referents, gated by the GIVENNESS hierarchy (indefinite = new;
definite = link) and ACCESSIBILITY (recency/salience). Common-noun DIRECT anaphora links by descriptive
content: head-noun match (Poesio-Vieira 1998 dominant case) and, for the ~66% of literary links that do
NOT share a head lemma (diagnostic: head-match recall 0.341), ASSOCIATIVE/bridging via lexical-semantic
relation (Clark-Haviland 1977; "the fellow" ~ "the man"; "the girl" is-a "the child") -- built glass-box
over WordNet (a static offline lexical foundation; NO external LLM at inference).

THE MECHANISM (this cell): read non-pronoun mentions in order; each PERSON-denoting common-noun mention
either LINKS to the most-ACCESSIBLE compatible active referent (head-lemma match OR WordNet person-bridge;
gender/number/modifier compatible; within a recency window) or OPENS a new referent (indefinite, or none
compatible). Names alias via the landed EntityAliaser; non-person nouns keep the reader's exact-head
grouping (surface_head, which already works for objects). Output = a predicted cluster per mention.

ARMS (non-pronoun coref chain-F1, MUC/B3/CEAFe/CoNLL-avg; doc-level bootstrap):
  name_only      proper-name-centric reader: NO common-noun link (the "forms no referent" baseline).
  surface_head   the reader's overlay: all same-head merged (THE STRONGEST FLOOR, diagnostic 0.687).
  LINKER         the faithful incremental former (head-match + recency window + gender/number/mods).
  LINKER+bridge  + WordNet person-bridge for non-head-match links (the recall lever for the 66%).
  TWIN           LINKER+bridge predicted labels, PERMUTED within-doc (info-free: same cluster-size
                 distribution, link structure destroyed). Must LOSE.
scored on ALL non-pronoun mentions AND on CHARACTER-cluster mentions only (the affect/who-did-what pop).

Glass-box, deterministic, NO LLM, hdlab READ-only. ASCII. own data dir.
Run: .venv/Scripts/python.exe experiments/exp_commonnoun_referent_linker_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_commonnoun_referent_linker_v1.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, glob, json, random, time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, EntityAliaser, name_content_tokens, load_name_gender
from hdlab.graded_coref_pick import ROLE_W, DEFAULT_ACTR_D   # PINNED ACT-R constants (reuse the organ)
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG   # reuse metrics + head_lemma + floors

CONLL_DIR = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_referent_linker_v1")
SEED = 20260904

head_lemma = DIAG.head_lemma
modifiers = DIAG.modifiers
definiteness = DIAG.definiteness
is_name = DIAG.is_name
PERS_PRON = DIAG.PERS_PRON


# ============================ WordNet person-bridge (offline lexical foundation) ======================
_WN = None
_PERSON_SYN = None
_person_cache = {}
_bridge_cache = {}


def _wn():
    global _WN, _PERSON_SYN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
        _PERSON_SYN = wn.synset("person.n.01")
    return _WN


def person_synset(lemma):
    """The most-common PERSON-denoting noun synset of `lemma` (person.n.01 in its hypernym paths), or None."""
    if lemma in _person_cache:
        return _person_cache[lemma]
    wn = _wn()
    best = None
    for s in wn.synsets(lemma, "n"):
        paths = s.hypernym_paths()
        if any(_PERSON_SYN in p for p in paths):
            best = s
            break
    _person_cache[lemma] = best
    return best


def bridge_compat(hl_a, hl_b, thr):
    """True iff two PERSON-denoting common-noun heads are lexically bridge-compatible: one subsumes the
    other in the WordNet hypernymy, OR path-similarity >= thr (associative anaphora). Symmetric, cached."""
    if hl_a == hl_b:
        return True
    key = (hl_a, hl_b, thr) if hl_a <= hl_b else (hl_b, hl_a, thr)
    if key in _bridge_cache:
        return _bridge_cache[key]
    sa, sb = person_synset(hl_a), person_synset(hl_b)
    out = False
    if sa is not None and sb is not None:
        # ancestor/synonym or close taxonomic sibling under person
        if sa == sb:
            out = True
        else:
            lch = sa.lowest_common_hypernyms(sb)
            # ancestor relation (one subsumes the other) -> strong bridge
            if sa in sb.closure(lambda x: x.hypernyms()) or sb in sa.closure(lambda x: x.hypernyms()):
                out = True
            else:
                ps = sa.path_similarity(sb)
                out = (ps is not None and ps >= thr)
        _bridge_cache[key] = out
    else:
        _bridge_cache[key] = False
    return _bridge_cache[key]


# ============================ the incremental discourse-referent former ==============================
class Ref:
    __slots__ = ("key", "hls", "gender", "number", "mods", "last_sent", "last_midx", "count",
                 "is_name", "person", "hist")

    def __init__(self, key, hl, gender, number, mods, sent, midx, is_name, person, role):
        self.key = key; self.hls = {hl}; self.gender = gender; self.number = number; self.mods = set(mods)
        self.last_sent = sent; self.last_midx = midx; self.count = 1; self.is_name = is_name
        self.person = person; self.hist = [(sent, role)]      # (sentence, role_rank) for ACT-R activation

    def update(self, hl, gender, mods, sent, midx, role):
        self.hls.add(hl); self.mods |= mods; self.last_sent = sent; self.last_midx = midx
        self.count += 1; self.hist.append((sent, role))
        if self.gender is None:
            self.gender = gender


def _actr(ref, cur_sent, d=DEFAULT_ACTR_D):
    """PINNED ACT-R base-level activation A = ln(sum_k w_role(k) * dt_k^-d) over the referent's past
    mentions (recency x frequency x grammatical-role prominence; Anderson-Schooler; Lewis-Vasishth).
    Copied verbatim from hdlab.graded_coref_pick; dt >= 1 (sentence distance)."""
    s = 0.0
    for (sent, role) in ref.hist:
        rw = ROLE_W["SUBJECT"] if role == 0 else ROLE_W["OTHER"]
        dt = float(max(1, cur_sent - sent + 1))
        s += rw * (dt ** (-d))
    return np.log(s) if s > 0 else -1e9


def _gender_ok(g1, g2):
    if g1 in ("masc", "fem") and g2 in ("masc", "fem"):
        return g1 == g2
    return True


def _number_ok(n1, n2):
    if n1 in ("sing", "plur") and n2 in ("sing", "plur"):
        return n1 == n2
    return True


def _num_of(m):
    n = m.get("number")
    if n in ("singular", "sing"):
        return "sing"
    if n in ("plural", "plur"):
        return "plur"
    h = head_lemma(m["head"])
    raw = m["head"].lower()
    if raw != h and raw.endswith("s"):
        return "plur"
    return "sing"


def link_predicted(mentions, gaz, *, window=6, mode="access", thr=0.34, use_indef=True, use_mods=True,
                   hmatch_bonus=1.5):
    """Incremental discourse-referent former. Returns {midx -> cluster_label} for NON-PRONOUN mentions.

    A PERSON-denoting common-noun mention is re-identified by the brain's CONTENT-ADDRESSABLE cue-based
    retrieval (Lewis-Vasishth; the landed graded_coref_pick op, extended from pronouns to definite
    descriptions): among the ACTIVE person referents that are gender/number-compatible and within the
    recency window, LINK to the highest ACT-R activation (recency x frequency x role), with the head
    lemma as an ADDITIVE cue (bonus when it matches -- NOT a gate). This recovers name->epithet and
    synonym links ("the girl" -> the active female referent 'Elizabeth') that head-identity cannot.
      mode='access'    the full mechanism above (head-lemma is a bonus cue, not required).
      mode='headmatch' ABLATION: require a head-lemma match (descriptive content only, no accessibility
                       binding) -- isolates the recall contribution of accessibility-based retrieval.
      mode='bridge'    'access' + a WordNet person-bridge PRE-FILTER (candidates must head-match OR be
                       lexically bridge-compatible) -- tests whether lexical typing helps or hurts.
    Indefinite ('a man') OPENS a new referent (Givenness/Heim). Non-person nouns keep exact-head grouping
    (surface_head, which already works for objects). Names alias via the landed EntityAliaser."""
    aliaser = EntityAliaser()
    refs = []                       # active discourse referents (Ref)
    name_key_to_ref = {}            # aliaser canon -> Ref
    head_group = {}                 # non-person exact-head label cache
    labels = {}
    ln = 0
    for m in sorted([x for x in mentions if not x["is_pronoun"]], key=lambda x: x["midx"]):
        mi = m["midx"]; si = m["sent_idx"]; role = m.get("sent_role_rank", 99)
        span = m.get("span_toks", [m["head"]])
        g = m.get("gender") or m.get("name_gender"); num = _num_of(m); mods = modifiers(m)
        if is_name(m, gaz):
            canon = aliaser.assign(span, g)
            if canon is not None and canon in name_key_to_ref:
                name_key_to_ref[canon].update(head_lemma(m["head"]), g, mods, si, mi, role)
                r = name_key_to_ref[canon]
            else:
                r = Ref("R%d" % ln, head_lemma(m["head"]), g, num, mods, si, mi, True, True, role); ln += 1
                refs.append(r)
                if canon is not None:
                    name_key_to_ref[canon] = r
            labels[mi] = r.key
            continue
        hl = head_lemma(m["head"])
        person = person_synset(hl) is not None
        if not person:
            if hl not in head_group:
                head_group[hl] = "H%d" % ln; ln += 1
            labels[mi] = head_group[hl]
            continue
        defn = definiteness(m)
        cand = None
        if not (use_indef and defn == "indef"):
            best = -1e18
            for r in refs:
                if not r.person or (window and (si - r.last_sent) > window):
                    continue
                if not _gender_ok(g, r.gender) or not _number_ok(num, r.number):
                    continue
                hmatch = hl in r.hls
                if mode == "headmatch" and not hmatch:
                    continue
                if mode == "bridge" and not hmatch:
                    if not any(rh and bridge_compat(hl, rh, thr) for rh in r.hls):
                        continue
                if use_mods and hmatch and mods and r.mods and mods.isdisjoint(r.mods):
                    continue          # same head, contradicting modifiers (old man vs young man) -> distinct
                score = _actr(r, si) + (hmatch_bonus if hmatch else 0.0)
                if score > best:
                    best = score; cand = r
        if cand is not None:
            cand.update(hl, g, mods, si, mi, role); labels[mi] = cand.key
        else:
            r = Ref("R%d" % ln, hl, g, num, mods, si, mi, False, person, role); ln += 1
            refs.append(r); labels[mi] = r.key
    return labels


# ============================ scoring harness ========================================================
def _char_clusters(ms):
    """gold cluster ids that are PERSON/character clusters (contain a personal pronoun or gendered head)."""
    by_c = defaultdict(list)
    for m in ms:
        by_c[m["cluster"]].append(m)
    out = set()
    for c, cms in by_c.items():
        if any(mm["head"] in PERS_PRON for mm in cms) or \
           any((mm.get("gender") in ("masc", "fem")) and not mm["is_pronoun"] for mm in cms):
            out.add(c)
    return out


_ARM_MODE = {"LINKER_headmatch": "headmatch", "LINKER": "access", "LINKER_bridge": "bridge"}


def predicted_for_arm(ms, gaz, arm, window=6, thr=0.34):
    if arm in ("name_only", "surface_head"):
        return DIAG.cluster_labels(ms, gaz, arm)
    if arm in _ARM_MODE:
        return link_predicted(ms, gaz, mode=_ARM_MODE[arm], window=window, thr=thr)
    raise ValueError(arm)


def _doc_stats(pred, gold):
    """Per-doc SUFFICIENT STATISTICS for B3/MUC/CEAFe (all pool ADDITIVELY across doc-disjoint clusters,
    so the bootstrap just resamples cached stats -- no giant pooled CEAFe matrix). Returns a 10-tuple:
    (b3_psum, b3_rsum, n, muc_rnum, muc_rden, muc_pnum, muc_pden, ceaf_phi, ceaf_npred, ceaf_ngold)."""
    n = len(pred)
    if n == 0:
        return (0.0, 0.0, 0, 0, 0, 0, 0, 0.0, 0, 0)
    gp = defaultdict(set); gg = defaultdict(set)
    for i in range(n):
        gp[pred[i]].add(i); gg[gold[i]].add(i)
    ps = rs = 0.0
    for i in range(n):
        pc = gp[pred[i]]; gc = gg[gold[i]]; ov = len(pc & gc)
        ps += ov / len(pc); rs += ov / len(gc)
    pred_of = {i: pred[i] for i in range(n)}; gold_of = {i: gold[i] for i in range(n)}

    def muc_side(key_clusters, resp_of):
        num = den = 0
        for c in key_clusters:
            if len(c) <= 1:
                continue
            parts = len({resp_of[i] for i in c})
            num += (len(c) - parts); den += (len(c) - 1)
        return num, den
    rnum, rden = muc_side(gg.values(), pred_of)
    pnum, pden = muc_side(gp.values(), gold_of)
    R = list(gp.values()); G = list(gg.values())
    sim = np.zeros((len(R), len(G)))
    for i, r in enumerate(R):
        for j, g in enumerate(G):
            inter = len(r & g)
            if inter:
                sim[i, j] = 2.0 * inter / (len(r) + len(g))
    try:
        from scipy.optimize import linear_sum_assignment
        ri, gi = linear_sum_assignment(-sim); phi = float(sim[ri, gi].sum())
    except Exception:
        phi = 0.0; uR = set(); uG = set()
        for s, i, j in sorted(((sim[i, j], i, j) for i in range(len(R)) for j in range(len(G))), reverse=True):
            if s <= 0:
                break
            if i in uR or j in uG:
                continue
            uR.add(i); uG.add(j); phi += s
    return (ps, rs, n, rnum, rden, pnum, pden, phi, len(R), len(G))


def _conll_from_stats(sts):
    ps = sum(s[0] for s in sts); rs = sum(s[1] for s in sts); n = sum(s[2] for s in sts)
    rnum = sum(s[3] for s in sts); rden = sum(s[4] for s in sts)
    pnum = sum(s[5] for s in sts); pden = sum(s[6] for s in sts)
    phi = sum(s[7] for s in sts); npred = sum(s[8] for s in sts); ngold = sum(s[9] for s in sts)
    b3p = ps / n if n else 0.0; b3r = rs / n if n else 0.0
    b3 = 2 * b3p * b3r / (b3p + b3r) if b3p + b3r else 0.0
    mp = pnum / pden if pden else 0.0; mr = rnum / rden if rden else 0.0
    mu = 2 * mp * mr / (mp + mr) if mp + mr else 0.0
    cp = phi / npred if npred else 0.0; cr = phi / ngold if ngold else 0.0
    ce = 2 * cp * cr / (cp + cr) if cp + cr else 0.0
    return {"muc_f1": round(mu, 4), "b3_f1": round(b3, 4), "ceafe_f1": round(ce, 4),
            "conll_avg": round((mu + b3 + ce) / 3.0, 4)}


def per_doc_stats(docs, gaz, arm, twin_seed=None, window=6, thr=0.34):
    """Per-doc (all-nonpron, char-cluster) sufficient-statistic tuples for one arm."""
    st_all, st_char = [], []
    rng = random.Random(twin_seed) if twin_seed is not None else None
    for di, (doc, ms) in enumerate(docs):
        lab = predicted_for_arm(ms, gaz, arm, window, thr) if arm != "TWIN" \
            else predicted_for_arm(ms, gaz, "LINKER", window, thr)
        noms = [m for m in ms if not m["is_pronoun"]]
        pred = [lab[m["midx"]] for m in noms]
        if rng is not None:
            perm = pred[:]; rng.shuffle(perm); pred = perm
        gold = ["g%d" % m["cluster"] for m in noms]
        st_all.append(_doc_stats(pred, gold))
        chars = _char_clusters(ms)
        idx = [k for k, m in enumerate(noms) if m["cluster"] in chars]
        st_char.append(_doc_stats([pred[k] for k in idx], [gold[k] for k in idx]))
    return st_all, st_char


def bootstrap_delta(sts_a, sts_b, n_boot=1000, seed=SEED, key="conll_avg"):
    k = len(sts_a); idx = list(range(k)); rng = random.Random(seed)
    base = _conll_from_stats(sts_a)[key] - _conll_from_stats(sts_b)[key]
    ds = []
    for _ in range(n_boot):
        sel = [rng.randrange(k) for _ in range(k)]
        ds.append(_conll_from_stats([sts_a[i] for i in sel])[key]
                  - _conll_from_stats([sts_b[i] for i in sel])[key])
    ds.sort()
    lo, hi = ds[int(0.025 * n_boot)], ds[int(0.975 * n_boot)]
    null = sorted(abs(d - base) for d in ds)
    return {"delta": round(base, 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "hw": round((hi - lo) / 2, 4), "null_p95": round(null[int(0.95 * n_boot)], 4),
            "ci_sep": bool(lo > 0 or hi < 0)}


def run(n=None, n_boot=1000, window=6, thr=0.34):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    docs, gaz = DIAG.load_docs(n)
    arms = ["name_only", "surface_head", "LINKER_headmatch", "LINKER", "LINKER_bridge"]
    pd_all, pd_char = {}, {}
    for arm in arms:
        pd_all[arm], pd_char[arm] = per_doc_stats(docs, gaz, arm, window=window, thr=thr)
    pd_all["TWIN"], pd_char["TWIN"] = per_doc_stats(docs, gaz, "TWIN", twin_seed=SEED, window=window, thr=thr)
    allarms = arms + ["TWIN"]
    pooled_all = {a: _conll_from_stats(pd_all[a]) for a in allarms}
    pooled_char = {a: _conll_from_stats(pd_char[a]) for a in allarms}
    pairs = [("LINKER", "surface_head"), ("LINKER", "LINKER_headmatch"),
             ("LINKER_bridge", "surface_head"), ("LINKER", "TWIN"), ("surface_head", "name_only")]
    deltas_all = {"%s-%s" % (a, b): bootstrap_delta(pd_all[a], pd_all[b], n_boot) for a, b in pairs}
    deltas_char = {"%s-%s" % (a, b): bootstrap_delta(pd_char[a], pd_char[b], n_boot) for a, b in pairs}
    res = {"n_docs": len(docs), "window": window, "bridge_thr": thr,
           "pooled_all_nonpron": pooled_all, "pooled_char_cluster": pooled_char,
           "deltas_all_nonpron": deltas_all, "deltas_char_cluster": deltas_char,
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_referent_linker_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    for pop, pooled, deltas in (("ALL non-pronoun", res["pooled_all_nonpron"], res["deltas_all_nonpron"]),
                                ("CHARACTER clusters", res["pooled_char_cluster"], res["deltas_char_cluster"])):
        print("=" * 88)
        print("COREF CHAIN-F1 -- %s mentions (%d docs, window=%d, bridge_thr=%.2f)"
              % (pop, res["n_docs"], res["window"], res["bridge_thr"]))
        print("  %-14s %8s %8s %8s %8s" % ("arm", "MUC", "B3", "CEAFe", "CoNLL"))
        for a, sc in pooled.items():
            print("  %-14s %8.4f %8.4f %8.4f %8.4f" % (a, sc["muc_f1"], sc["b3_f1"], sc["ceafe_f1"], sc["conll_avg"]))
        print("  " + "-" * 84)
        for kk, d in deltas.items():
            print("  %-28s CoNLL %+.4f  CI[%+.4f,%+.4f] hw=%.4f null_p95=%.4f ci_sep=%s"
                  % (kk, d["delta"], d["lo"], d["hi"], d["hw"], d["null_p95"], d["ci_sep"]))
    print("=" * 88)


def sweep_window(n=None, windows=(2, 4, 6, 10, 16), n_boot=500):
    """Sweep the recency-window PARAMETER (OUR-INVENTION-under-test) for LINKER and LINKER_headmatch,
    reporting the character-cluster CoNLL delta vs the surface_head floor -- to confirm NO window value
    lets the faithful cue-based former clear the floor CI-separated (the ceiling is set by the diagnostic
    head-match recall 0.341, which no window can exceed). WordNet cache stays warm across windows."""
    docs, gaz = DIAG.load_docs(n)
    # surface_head reference (char clusters)
    _, sh_char = per_doc_stats(docs, gaz, "surface_head")
    out = {}
    for w in windows:
        row = {}
        for arm in ("LINKER_headmatch", "LINKER"):
            _, st_char = per_doc_stats(docs, gaz, arm, window=w)
            d = bootstrap_delta(st_char, sh_char, n_boot)
            row[arm] = {"conll": _conll_from_stats(st_char)["conll_avg"], "delta_vs_surface_head": d}
        out[w] = row
    print("=" * 84)
    print("WINDOW SWEEP -- character-cluster CoNLL vs surface_head floor (%d docs)" % len(docs))
    print("  surface_head floor CoNLL = %.4f" % _conll_from_stats(sh_char)["conll_avg"])
    for w, row in out.items():
        for arm, r in row.items():
            d = r["delta_vs_surface_head"]
            print("  W=%-3d %-16s CoNLL %.4f  delta %+.4f CI[%+.4f,%+.4f] ci_sep=%s"
                  % (w, arm, r["conll"], d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    print("=" * 84)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "window_sweep.json"), "w", encoding="ascii") as fh:
        json.dump({"surface_head_char_conll": _conll_from_stats(sh_char)["conll_avg"], "sweep": out},
                  fh, indent=2, default=str)
    return out


def self_test():
    # WordNet person typing + bridge (sense-aware): man/fellow are person-denoting; man/table is not a
    # person-bridge (table is not a person). man-man trivially compatible.
    assert person_synset("man") is not None and person_synset("table") is None
    assert bridge_compat("man", "table", 0.34) is False
    assert bridge_compat("man", "man", 0.34) is True
    # ACT-R activation: a more-recent, more-frequent, subject referent outranks a stale one
    a = Ref("A", "man", "masc", "sing", set(), 0, 0, False, True, 0)
    a.update("man", "masc", set(), 1, 5, 0); a.update("man", "masc", set(), 2, 9, 0)
    b = Ref("B", "man", "masc", "sing", set(), 0, 1, False, True, 1)
    assert _actr(a, 3) > _actr(b, 3)
    # gender gate blocks man/woman; None permissive
    assert _gender_ok("masc", "fem") is False and _gender_ok(None, "fem") is True
    # linker runs and produces labels for every non-pronoun mention
    docs, gaz = DIAG.load_docs(n=5)
    lab = link_predicted(docs[0][1], gaz, mode="access")
    n_nonpron = sum(1 for m in docs[0][1] if not m["is_pronoun"])
    assert len(lab) == n_nonpron, (len(lab), n_nonpron)
    res = run(n=5, n_boot=200)
    assert "LINKER" in res["pooled_all_nonpron"] and "TWIN" in res["pooled_all_nonpron"]
    print("[self-test] PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--window", type=int, default=6)
    ap.add_argument("--thr", type=float, default=0.34)
    ap.add_argument("--nboot", type=int, default=1000)
    ap.add_argument("--sweep", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    if a.sweep:
        sweep_window(n=a.n); return
    res = run(n=(5 if a.smoke else a.n), n_boot=a.nboot, window=a.window, thr=a.thr)
    _print(res)


if __name__ == "__main__":
    main()
