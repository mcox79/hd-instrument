"""exp_frame_sense_semcor_v1 -- does the glass-box CONSTRUCTION cue beat most-frequent-sense on a REAL WSD gold?

THE GOLD: NLTK SemCor (WordNet sense-tagged running text). Each polysemous verb INSTANCE -> gold WordNet synset
-> gold LEXNAME -> gold COARSE FRAME (motion/possession/communication/perception/cognition/change/...). Predicting
the coarse event-FRAME is the grain the brain represents (verb supersenses; Ciaramita & Altun) and the grain the
downstream front-ends consume -- and it is where the argument-structure CONSTRUCTION carries the signal. The two
dominant confusions the brief names live inside it (motion vs possession; perception vs communication).

ONE VARIABLE: the CONSTRUCTION cue ON vs OFF. Both arms share the IDENTICAL train-split MFS frame prior (injected
into the disambiguator), so the ONLY difference is whether the realized argument frame + joint noun-sense fit
votes. This is why the entity_typing (learned object-supersense, +0.001 null) and the toy frame-gate (31 items,
scramble-fragile) verdicts do NOT settle this: neither ran the categorical construction cue on a real, powered gold.

ARMS (all on the SAME test instances):
  MFS            most-frequent coarse frame for the lemma, from the TRAIN split (the floor; recomputed per pop).
  DISAMBIG_JOINT train MFS prior + construction cue with JOINT (verb,noun)-sense co-selection (the mechanism).
  DISAMBIG_TYPED ablation: construction cue but noun typed FIRST (frequency-weighted union), not joint.
  TWIN           info-free: construction support shuffled per item (a fixed permutation of the candidate frames).

POPULATIONS (report all; recompute MFS on each):
  ALL_POLY   every polysemous-verb test instance (the honest, diluted full population -- MFS is a killer here).
  FRAME_ALT  verbs whose WordNet senses span >=2 coarse frames with a subordinate frame attested (frame-
             alternating verbs, selected by a FIXED lexicon criterion -- NOT by peeking at the gold labels).
  DIAGNOSTIC the mechanism-flagged diagnostic subpopulation (the construction cue fired + moved/sharpened;
             decided BLIND, no gold) -- where the brain commits off the prior.

spaCy-bound -> runs INLINE (remote has no spaCy). Parses are cached to a pkl; scoring reads the cache.
Writes ONLY to data/exp_frame_sense_semcor_v1[/ _smoke]. NO hdlab writes. ASCII only.
"""
from __future__ import annotations
import argparse, json, os, pickle, sys, time
from collections import defaultdict, Counter
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import (
    FrameSenseDisambiguator, extract_frame, candidate_frames, lexname_to_frame,
    is_homonym_split, noun_frame_types, COARSE_FRAMES)

ANCHOR = "frame_sense_semcor_v1"
SPLIT_MOD = 5                     # test = sent_idx % 5 == 0 (deterministic 80/20)


# ---------------------------------------------------------------------------
# Which verbs are FRAME-ALTERNATING -- a FIXED lexicon criterion (WordNet only, no gold peeking): the lemma's
# verb senses span >=2 coarse frames AND a subordinate frame carries real WordNet sense-frequency mass.
# ---------------------------------------------------------------------------
_FRAMEALT_CACHE = {}


def is_frame_alternating(lemma):
    if lemma in _FRAMEALT_CACHE:
        return _FRAMEALT_CACHE[lemma]
    from nltk.corpus import wordnet as wn
    frames = defaultdict(float)
    for rank, s in enumerate(wn.synsets(lemma, pos="v")):
        fr = lexname_to_frame(s.lexname())
        if fr is None:
            continue
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == lemma.lower())
        frames[fr] += c + 1.0 / (rank + 1.0)
    ans = False
    if len(frames) >= 2:
        tot = sum(frames.values())
        shares = sorted((v / tot for v in frames.values()), reverse=True)
        ans = bool(shares[1] >= 0.15)     # a subordinate coarse frame with >=15% of the mass
    _FRAMEALT_CACHE[lemma] = ans
    return ans


# ---------------------------------------------------------------------------
# Build instances: SemCor verb tokens aligned to a spaCy parse, with gold coarse frame + cached RealizedFrame.
# ---------------------------------------------------------------------------
def _content_lemmas(doc, skip_i=None):
    return [t.lemma_.lower() for t in doc
            if t.pos_ in ("NOUN", "PROPN", "ADJ", "ADV", "VERB") and (skip_i is None or t.i != skip_i)
            and not t.is_stop and t.is_alpha]


def build_instances(max_sents=None, smoke=False):
    """Iterate SemCor PER DOCUMENT so cross-sentence discourse context (#2) + anaphoric-object resolution (#3a)
    are available: a rolling buffer holds the prior sentences' content lemmas and their nouns."""
    import spacy
    from nltk.corpus import semcor, wordnet as wn
    from nltk.tree import Tree
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    insts = []
    dropped = Counter()
    gsi = 0                                        # global sentence index (deterministic 80/20 split)
    for fid in semcor.fileids():
        try:
            fsents = semcor.tagged_sents(fid, tag="sem")
        except Exception:
            continue
        buf_content = []                           # prior sentences' content lemmas (cross-sentence context)
        buf_nouns = []                             # prior sentences' (lemma) nouns, recent-last (coref antecedents)
        for s in fsents:
            if max_sents is not None and gsi >= max_sents:
                break
            gsi += 1
            leaves, gold_verbs = [], []
            for ch in s:
                if isinstance(ch, Tree):
                    lab = ch.label()
                    syn = None
                    if hasattr(lab, "synset"):
                        try:
                            syn = lab.synset()
                        except Exception:
                            syn = None
                    words = ch.leaves()
                    start = len(leaves)
                    if syn is not None and syn.pos() == "v" and words:
                        gold_verbs.append((start, words[0].lower(), syn))
                    leaves.extend(words)
                else:
                    leaves.extend(ch if isinstance(ch, list) else [ch])
            text = " ".join(leaves)
            offs, pos = [], 0
            for w in leaves:
                offs.append(pos)
                pos += len(w) + 1
            try:
                doc = nlp(text)
            except Exception:
                dropped["parse_fail"] += 1
                continue
            cur_content = _content_lemmas(doc)
            cur_nouns = [t.lemma_.lower() for t in doc if t.pos_ in ("NOUN", "PROPN")]
            prior_content = [w for sc in buf_content for w in sc]      # last <=2 sentences (set below)
            is_train = (gsi % SPLIT_MOD) != 0
            for (leaf_idx, surface, syn) in gold_verbs:
                lemma = None
                for lm in syn.lemmas():
                    lemma = lm.name().lower().replace("_", " ").split()[0]
                    break
                lemma = lemma or surface
                cands = candidate_frames(lemma)
                if len(cands) < 2:
                    dropped["monosemous_frame"] += 1
                    continue
                gold_frame = lexname_to_frame(syn.lexname())
                if gold_frame is None or gold_frame not in cands:
                    dropped["gold_unreachable"] += 1
                    continue
                target_off = offs[leaf_idx] if leaf_idx < len(offs) else 0
                best, bestd = None, 1e9
                for tok in doc:
                    if tok.pos_ not in ("VERB", "AUX"):
                        continue
                    if tok.lemma_.lower() != lemma and tok.text.lower() != surface:
                        continue
                    d = abs(tok.idx - target_off)
                    if d < bestd:
                        best, bestd = tok, d
                if best is None:
                    dropped["no_spacy_verb"] += 1
                    continue
                rf = extract_frame(best.sent, best)
                ctx = _content_lemmas(best.sent, skip_i=best.i)[:24]
                ctx_wide = (prior_content + ctx)[-40:]                 # cross-sentence discourse context (#2)
                # #3a coref: if the direct object is a PRONOUN, resolve to the nearest preceding NOUN (in-sentence
                # before the verb, else the most recent prior-sentence noun) and record it for typing.
                dobj_coref = None
                for ch in best.children:
                    if ch.dep_ in ("dobj", "obj") and ch.pos_ == "PRON":
                        preceding = [t.lemma_.lower() for t in best.sent
                                     if t.pos_ in ("NOUN", "PROPN") and t.i < best.i]
                        if preceding:
                            dobj_coref = preceding[-1]
                        elif buf_nouns:
                            dobj_coref = buf_nouns[-1]
                        break
                insts.append({"lemma": lemma, "gold_frame": gold_frame, "cands": cands,
                              "rf": rf, "train": is_train, "ctx": ctx,
                              "ctx_wide": ctx_wide, "dobj_coref": dobj_coref,
                              "frame_alt": is_frame_alternating(lemma),
                              "homonym": is_homonym_split(lemma)})
            # roll the discourse buffers forward (prior 2 sentences of context; recent nouns for coref)
            buf_content.append(cur_content)
            buf_content[:] = buf_content[-2:]
            buf_nouns.extend(cur_nouns)
            buf_nouns[:] = buf_nouns[-12:]
        if max_sents is not None and gsi >= max_sents:
            break
    return insts, dict(dropped)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def train_prior(insts):
    """lemma -> {frame: count} from TRAIN instances (the shared MFS prior)."""
    pri = defaultdict(lambda: defaultdict(float))
    for it in insts:
        if it["train"]:
            pri[it["lemma"]][it["gold_frame"]] += 1.0
    return {lm: dict(d) for lm, d in pri.items()}


def mfs_of(pri, lemma, cands):
    d = pri.get(lemma, {})
    if not d:
        return cands[0]
    return max(cands, key=lambda c: d.get(c, 0.0))


def predict(dis, it, pri, joint=True, shuffle=None):
    cands = it["cands"]
    prior_map = pri.get(it["lemma"], {})
    if not prior_map:                              # unseen lemma in train -> WordNet prior fallback (both arms)
        prior_map = None
    v = dis.disambiguate_token(None, _FakeTok(it["lemma"]), cand=cands, frame_feats=it["rf"],
                               shuffle_frame=shuffle, joint=joint, prior=prior_map)
    return v


class _FakeTok:
    """Minimal stand-in so disambiguate_token can read .lemma_ without a live spaCy token (rf is cached)."""
    def __init__(self, lemma):
        self.lemma_ = lemma
        self.pos_ = "VERB"


def bootstrap_ci(correct, seed, n_boot=2000):
    a = np.asarray(correct, float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    r = np.random.default_rng(seed)
    idx = r.integers(0, len(a), size=(n_boot, len(a)))
    means = a[idx].mean(1)
    return float(a.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def mcnemar_p(b, c):
    import math
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1))
    return min(1.0, tail * (0.5 ** n) * 2.0)


def eval_pop(insts, pri, dis, seed, name):
    test = [it for it in insts if not it["train"]]
    if name == "frame_alt":
        test = [it for it in test if it["frame_alt"]]
    # predictions (shared)
    rng = np.random.default_rng(seed + 7)
    mfs_ok, joint_ok, typed_ok, twin_ok, diag_flag = [], [], [], [], []
    b_mj = c_mj = 0                     # McNemar MFS-only vs JOINT-only
    for it in test:
        cands = it["cands"]
        mfs = mfs_of(pri, it["lemma"], cands)
        vj = predict(dis, it, pri, joint=True)
        vt = predict(dis, it, pri, joint=False)
        perm = rng.permutation(len(cands))
        vtw = predict(dis, it, pri, joint=True, shuffle=perm)
        g = it["gold_frame"]
        m_ok, j_ok = int(mfs == g), int(vj.frame == g)
        mfs_ok.append(m_ok); joint_ok.append(j_ok)
        typed_ok.append(int(vt.frame == g)); twin_ok.append(int(vtw.frame == g))
        diag_flag.append(bool(vj.diagnostic))
        if m_ok and not j_ok:
            b_mj += 1
        elif j_ok and not m_ok:
            c_mj += 1
    out = {"n": len(test), "n_diagnostic": int(sum(diag_flag))}
    for si, (k, v) in enumerate((("MFS", mfs_ok), ("DISAMBIG_JOINT", joint_ok),
                                 ("DISAMBIG_TYPED", typed_ok), ("TWIN", twin_ok))):
        m, lo, hi = bootstrap_ci(v, seed + 101 * (si + 1))     # fixed per-arm seed (PROT-023: no hash())
        out[k] = [m, lo, hi]
    out["mcnemar_b_mfs_only"], out["mcnemar_c_joint_only"] = b_mj, c_mj
    out["mcnemar_p"] = mcnemar_p(b_mj, c_mj)
    # DIAGNOSTIC subpopulation
    diag_idx = [i for i, d in enumerate(diag_flag) if d]
    if diag_idx:
        dm, dlo, dhi = bootstrap_ci([joint_ok[i] for i in diag_idx], seed + 11)
        fm, flo, fhi = bootstrap_ci([mfs_ok[i] for i in diag_idx], seed + 13)
        out["DIAG_JOINT"] = [dm, dlo, dhi]
        out["DIAG_MFS"] = [fm, flo, fhi]
        out["n_diag_pop"] = len(diag_idx)
    return out


def run(smoke=False, seed=20260828):
    t0 = time.time()
    cache = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""), "instances_v6.pkl")
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    max_sents = 1200 if smoke else 12000
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            insts, dropped = pickle.load(f)
    else:
        insts, dropped = build_instances(max_sents=max_sents, smoke=smoke)
        with open(cache, "wb") as f:
            pickle.dump((insts, dropped), f)
    pri = train_prior(insts)
    dis = FrameSenseDisambiguator(nlp="cached")     # rf is cached; never parses
    res = {"all_poly": eval_pop(insts, pri, dis, seed, "all_poly"),
           "frame_alt": eval_pop(insts, pri, dis, seed, "frame_alt")}
    # gates: on FRAME_ALT (and DIAGNOSTIC) DISAMBIG beats MFS CI-separated + TWIN loses
    fa = res["frame_alt"]
    j_lo = fa["DISAMBIG_JOINT"][1]
    mfs_hi = fa["MFS"][2]
    twin_hi = fa["TWIN"][2]
    gates = {
        "joint_beats_mfs_ci_frame_alt": bool(j_lo > mfs_hi),
        "twin_loses_ci_frame_alt": bool(fa["DISAMBIG_JOINT"][1] > twin_hi),
        "mcnemar_sig_frame_alt": bool(fa["mcnemar_p"] < 0.05 and fa["mcnemar_c_joint_only"] > fa["mcnemar_b_mfs_only"]),
    }
    if "DIAG_JOINT" in fa:
        gates["joint_beats_mfs_ci_diagnostic"] = bool(fa["DIAG_JOINT"][1] > fa["DIAG_MFS"][2])
    verdict = "HARD_PASS" if (gates["joint_beats_mfs_ci_frame_alt"] and gates["twin_loses_ci_frame_alt"]) else \
              ("MIDDLE_BAND" if gates.get("joint_beats_mfs_ci_diagnostic") else "HARD_FAIL")
    return {"anchor_name": ANCHOR, "verdict": verdict, "run_mode": "smoke" if smoke else "full",
            "seed": seed, "n_instances": len(insts), "dropped": dropped,
            "results": res, "gates": gates, "elapsed_s": round(time.time() - t0, 1),
            "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"
    out_dir = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out_dir, exist_ok=True)
    m = run(smoke=smoke, seed=args.seed)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  n_inst={m['n_instances']} dropped={m['dropped']} ===")
    for pop in ("all_poly", "frame_alt"):
        r = m["results"][pop]
        print(f"[{pop}] n={r['n']} diag={r['n_diagnostic']}")
        for k in ("MFS", "DISAMBIG_JOINT", "DISAMBIG_TYPED", "TWIN"):
            print(f"    {k:15s} {r[k][0]:.3f} [{r[k][1]:.3f},{r[k][2]:.3f}]")
        print(f"    McNemar p={r['mcnemar_p']:.2e} (b_mfs={r['mcnemar_b_mfs_only']} c_joint={r['mcnemar_c_joint_only']})")
        if "DIAG_JOINT" in r:
            print(f"    DIAGNOSTIC n={r['n_diag_pop']}: JOINT {r['DIAG_JOINT'][0]:.3f}[{r['DIAG_JOINT'][1]:.3f},{r['DIAG_JOINT'][2]:.3f}]"
                  f" vs MFS {r['DIAG_MFS'][0]:.3f}[{r['DIAG_MFS'][1]:.3f},{r['DIAG_MFS'][2]:.3f}]")
    print("VERDICT:", m["verdict"], "GATES:", m["gates"])
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
