"""exp_register_native_pp_attachment_v1 -- REGISTER-NATIVE PP-attachment from RAW EXPOSURE (no gold parses).

THE PROBLEM (parent's two data-bounded levers): the substrate parser collapses on 19c/literary prose because it
has only MODERN gold. The parent named the fix "gold target-register PARSE data" and called it data-bounded (no
19c treebank on the shelf). BUT the brief's own brain section (and the psycholinguistics it cites) says PP-
attachment is resolved by "selectional expectations learned from USAGE" (Hindle & Rooth 1993; MacDonald 1994
constraint-satisfaction; Fine/Jaeger 2013 syntactic adaptation). The brain learns those from RAW EXPOSURE, never
from gold treebanks. So the register-native lever does NOT require gold parses -- it requires the verb-preposition
vs noun-preposition selectional statistics of the register, which are learnable from RAW 19c text (which we HAVE:
LitBank 100 novels, 11M words). This is DISTINCT from the refuted self-training (which reuses the model's own
modern-biased PARSE); here the signal is extracted from UNAMBIGUOUS raw-text anchors ("V P" -> verb-attach;
"N P" with no verb -> noun-attach), which are register-robust and independent of the modern parser's decisions.

MECHANISM (glass-box, no LLM, no spaCy at inference):
  1. Build a Hindle-Rooth verb-prep / noun-prep association table from RAW register text (tagged by our own
     pos_tagger; prepositions are a robust closed class).
  2. ADAPTER = post-parse PP re-attachment: for each PP object noun the arc-eager attached LOW (to a noun), if the
     register association says the nearby VERB selects that preposition (LA > tau), RE-ATTACH the object noun to
     the verb (nmod->obl correction). MacDonald constraint-satisfaction: the register selectional constraint
     overrides the modern structural prior. Symmetric low-attach guard protects modern.

MEASURE (parent's metrics, held-out): gold PP-attachment REACHABILITY (`_attaches_to_verb`, = PP-attach precision)
and CHAIN who-did-what accuracy, on LB_19c (register) + QA_modern (retention) + UD-EWT test (modern gold PP-attach).
ARMS: BASE (arc-eager operator) | ADAPT (HR register) | TWIN (SHUFFLED assoc, info-free, same shape) | NAIVE
(re-attach every PP-obj to nearest verb, no selectivity). PASS = ADAPT raises 19c reachability + who-did-what
CI-sep over BASE, TWIN loses, NAIVE loses on modern/selectivity, modern held, POS untouched.

CPU numpy only. ASCII. own dir. --smoke for a fast gate; default = full.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, math, re, sys, time, glob, random
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
from hdlab.predicate_argument_frontend import _attaches_to_verb

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_register_native_pp_attachment_v1")
LB_RAW = os.path.join(_REPO, "data/litbank/original")                       # 19c exposure (100 novels, 11M words)
MODERN_RAW = os.path.join(_REPO, "data/corpora/simplewiki/simplewiki_clean_v1.txt")  # modern exposure
MAX_HOPS = 8
WINDOW = 6           # look-back window for the competing verb/noun before a preposition
ALPHA = 0.5          # add-alpha smoothing on the association

# closed-class prepositions (register-robust; NO tagging needed to detect these)
PREPS = {"of", "in", "to", "for", "with", "on", "at", "from", "by", "into", "about", "over", "under",
         "through", "after", "between", "against", "during", "without", "before", "among", "around",
         "toward", "towards", "upon", "beneath", "beside", "beyond", "within", "along", "across",
         "behind", "below", "above", "amid", "amidst", "unto", "till", "until", "off", "onto"}


# ---------- raw-exposure ingestion + tagging ----------
def iter_raw_sentences(paths, max_sents, min_len=4, max_len=45):
    """yield whitespace-token lists from raw text; crude sentence split on .!?"""
    n = 0
    for fp in paths:
        try:
            txt = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        txt = re.sub(r"\s+", " ", txt)
        for s in re.split(r"(?<=[.!?])\s+", txt):
            toks = s.split()
            if min_len <= len(toks) <= max_len:
                yield toks
                n += 1
                if n >= max_sents:
                    return


def build_assoc(tagged_sents):
    """Hindle-Rooth verb-prep / noun-prep association from UNAMBIGUOUS raw-text anchors.
    'V P' (verb closest content word before prep) -> verb-attach anchor; 'N P' with NO verb in window ->
    noun-attach anchor; 'V .. N P' (noun closest, verb earlier) -> AMBIGUOUS, skipped."""
    VA = {}; NA = {}; TV = {}; TN = {}; GV = {}; GN = {}; gv_tot = 0; gn_tot = 0
    for toks, tags in tagged_sents:
        L = len(toks)
        low = [t.lower().strip(".,;:!?\"'()[]") for t in toks]
        for i in range(L):
            if tags[i] != "ADP" or low[i] not in PREPS:
                continue
            prep = low[i]
            vprev = nprev = None
            for j in range(i - 1, max(-1, i - 1 - WINDOW), -1):
                if tags[j] == "VERB" and vprev is None:
                    vprev = j
                if tags[j] in ("NOUN", "PROPN") and nprev is None:
                    nprev = j
                if vprev is not None and nprev is not None:
                    break
            if vprev is not None and (nprev is None or vprev > nprev):
                vl = V1._lem(toks[vprev])
                VA[(vl, prep)] = VA.get((vl, prep), 0) + 1
                TV[vl] = TV.get(vl, 0) + 1
                GV[prep] = GV.get(prep, 0) + 1; gv_tot += 1
            elif nprev is not None and vprev is None:
                nl = low[nprev]
                NA[(nl, prep)] = NA.get((nl, prep), 0) + 1
                TN[nl] = TN.get(nl, 0) + 1
                GN[prep] = GN.get(prep, 0) + 1; gn_tot += 1
    npv = len(PREPS)
    gv_def = 1.0 / max(1, gv_tot); gn_def = 1.0 / max(1, gn_tot)
    return {"VA": VA, "NA": NA, "TV": TV, "TN": TN,
            "GVrate": {p: GV[p] / max(1, gv_tot) for p in GV}, "GNrate": {p: GN[p] / max(1, gn_tot) for p in GN},
            "gv_def": gv_def, "gn_def": gn_def, "npv": npv,
            "n_va": sum(VA.values()), "n_na": sum(NA.values())}


def assoc_LA(A, v_lem, n_lem, prep):
    """log2 P(prep|verb) / P(prep|noun) -- Hindle-Rooth verb-vs-noun attachment preference."""
    if v_lem is None and n_lem is None:
        return 0.0
    tv = A["TV"].get(v_lem, 0); tn = A["TN"].get(n_lem, 0)
    if tv > 0:
        pv = (A["VA"].get((v_lem, prep), 0) + ALPHA) / (tv + ALPHA * A["npv"])
    else:
        pv = A["GVrate"].get(prep, A["gv_def"])
    if tn > 0:
        pn = (A["NA"].get((n_lem, prep), 0) + ALPHA) / (tn + ALPHA * A["npv"])
    else:
        pn = A["GNrate"].get(prep, A["gn_def"])
    return math.log2((pv + 1e-9) / (pn + 1e-9))


def shuffle_assoc(A, seed=17):
    """info-free TWIN: permute the verb identities so the (verb -> prep-distribution) map is scrambled but the
    marginal shape (same # of high-LA fires) is preserved."""
    rng = random.Random(seed)
    verbs = list(A["TV"].keys()); perm = verbs[:]; rng.shuffle(perm)
    vmap = dict(zip(verbs, perm))
    VA2 = {}; TV2 = {}
    for (vl, prep), c in A["VA"].items():
        vv = vmap.get(vl, vl); VA2[(vv, prep)] = VA2.get((vv, prep), 0) + c
    for vl, c in A["TV"].items():
        TV2[vmap.get(vl, vl)] = c
    B = dict(A); B["VA"] = VA2; B["TV"] = TV2
    return B


# ---------- the adapter: post-parse PP re-attachment ----------
def adapt_heads(toks, pos, heads, A, tau, naive=False):
    """re-attach each PP object noun verb-ward when the register association prefers the verb (LA>tau); symmetric
    low guard (LA<-tau) protects modern. naive=True ignores A and re-attaches every PP-obj to the nearest verb."""
    heads = dict(heads)
    L = len(toks)
    low = [t.lower().strip(".,;:!?\"'()[]") for t in toks]
    for p in range(1, L + 1):
        if pos[p - 1] != "ADP" or low[p - 1] not in PREPS:
            continue
        obj = heads.get(p)
        if obj is None or obj in (0, p) or not (1 <= obj <= L):
            continue
        prep = low[p - 1]
        # nearest preceding VERB and competing NOUN (before the prep)
        v = n = None
        for j in range(p - 2, max(-1, p - 2 - WINDOW * 2), -1):
            if pos[j] == "VERB" and v is None:
                v = j + 1
            if pos[j] in ("NOUN", "PROPN") and n is None and (j + 1) != obj:
                n = j + 1
            if v is not None and n is not None:
                break
        if v is None:
            continue
        h_obj = heads.get(obj)
        obj_on_verb = (h_obj is not None and 1 <= h_obj <= L and pos[h_obj - 1] == "VERB")
        if naive:
            if not obj_on_verb:
                heads[obj] = v
            continue
        vl = V1._lem(toks[v - 1]); nl = low[n - 1] if n else None
        la = assoc_LA(A, vl, nl, prep)
        if la > tau and not obj_on_verb:
            heads[obj] = v                       # verb-ward (nmod -> obl)
        elif la < -tau and obj_on_verb and n is not None:
            heads[obj] = n                       # noun-ward guard (obl -> nmod), protects modern low-attach
    return heads


# ---------- eval (parent's metrics) ----------
def cand_ok(r):
    return len(GD.cands(r)) >= 2 and sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2


def chain_pick(r, toks, pos, heads, prefer="far"):
    vi0 = r["verb_idx"]; v1 = vi0 + 1
    attached = [c0 for c0 in r["cand_idx"] if _attaches_to_verb(c0 + 1, v1, heads, pos, max_hops=MAX_HOPS)]
    post = [c for c in attached if c > vi0]
    pool = post or attached
    if not pool:
        return r.get("pos_pick")
    idx = max(pool) if prefer == "far" else min(pool)
    return toks[idx] if 0 <= idx < len(toks) else r.get("pos_pick")


def eval_population(path, W, tg, A, Amod, tau, eval_sents_out=None):
    rows = [r for r in V1.load_pop(path) if cand_ok(r)]
    recs = []
    for r in rows:
        toks = r["sent"].split()
        vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks)
        base, _, _ = AEO.parse_with_conf(toks, pos, W)
        v1 = vi0 + 1
        h_adapt = adapt_heads(toks, pos, base, A, tau)
        h_twin = adapt_heads(toks, pos, base, shuffle_assoc(A), tau)
        h_naive = adapt_heads(toks, pos, base, A, tau, naive=True)
        rec = {"gold_head": r["gold_head"], "sent": r["sent"]}
        for nm, H in (("base", base), ("adapt", h_adapt), ("twin", h_twin), ("naive", h_naive)):
            rec[nm + "_reach"] = int(_attaches_to_verb(gi0 + 1, v1, H, pos, max_hops=MAX_HOPS))
            rec[nm + "_wdw"] = int(chain_pick(r, toks, pos, H, "far") == r["gold_head"])
        recs.append(rec)
        if eval_sents_out is not None:
            eval_sents_out.add(r["sent"])
    return recs


def boot_delta(recs, key_a, key_b, nboot=2000, seed=13):
    a = np.array([x[key_a] for x in recs], float); b = np.array([x[key_b] for x in recs], float)
    d = a - b; rng = np.random.default_rng(seed); n = len(d)
    if n == 0:
        return {"delta": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "half": 0.0, "null_p95": 0.0, "a": 0.0, "b": 0.0, "n": 0}
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(nboot)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    null = np.array([(d * rng.choice([-1, 1], n))[:].mean() for _ in range(nboot)])
    return {"delta": float(d.mean()), "ci_lo": float(lo), "ci_hi": float(hi), "half": float((hi - lo) / 2),
            "null_p95": float(np.percentile(np.abs(null), 95)), "a": float(a.mean()), "b": float(b.mean()), "n": n}


def summarize(name, recs):
    print("\n=== %s (n=%d) ===" % (name, len(recs)), flush=True)
    out = {"n": len(recs)}
    for metric in ("reach", "wdw"):
        base = np.mean([x["base_" + metric] for x in recs]) if recs else 0
        print("  [%s] BASE=%.4f" % (metric, base), flush=True)
        out[metric] = {"base": round(float(base), 4)}
        for arm in ("adapt", "twin", "naive"):
            d = boot_delta(recs, arm + "_" + metric, "base_" + metric)
            sep = "CI-SEP" if d["ci_lo"] > 0 else ("CI-SEP-NEG" if d["ci_hi"] < 0 else "ns")
            print("    %-6s=%.4f  d=%+.4f CI[%+.4f,%+.4f] half=%.4f null_p95=%.4f  %s"
                  % (arm, d["a"], d["delta"], d["ci_lo"], d["ci_hi"], d["half"], d["null_p95"], sep), flush=True)
            out[metric][arm] = {k: round(v, 4) for k, v in d.items()}
    return out


# ---------- modern gold PP-attach precision (retention, UD-EWT test) ----------
def ud_pp_attach_precision(W, A, tau):
    """on UD-EWT test GOLD heads: for each ADP's object noun whose GOLD head is a verb-or-noun, does the arm's
    predicted head land on the correct governor? reports base vs adapt(modern). ONE clean modern PP-attach metric."""
    test = [s for s in AEO._load_ud_feats("test") if 1 <= len(s) <= AEO.MAXLEN]
    b_ok = b_t = a_ok = 0
    for s in test:
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        gold = {t[0]: t[3] for t in s}
        base, _, _ = AEO.parse_with_conf(toks, pos, W)
        adapt = adapt_heads(toks, pos, base, A, tau)
        L = len(toks); low = [w.lower() for w in toks]
        for p in range(1, L + 1):
            if pos[p - 1] != "ADP" or low[p - 1] not in PREPS:
                continue
            obj = gold.get(p)                                  # gold object of the prep
            if obj is None or not (1 <= obj <= L):
                continue
            g_head = gold.get(obj)                             # gold governor of the PP object (verb=high / noun=low)
            if g_head is None or not (1 <= g_head <= L) or pos[g_head - 1] not in ("VERB", "NOUN", "PROPN"):
                continue
            b_t += 1
            b_ok += int(base.get(obj) == g_head)
            a_ok += int(adapt.get(obj) == g_head)
    return {"n": b_t, "base": round(b_ok / max(1, b_t), 4), "adapt": round(a_ok / max(1, b_t), 4),
            "delta": round((a_ok - b_ok) / max(1, b_t), 4)}


def load_or_tag(cache, paths_or_file, max_sents, tg, is_file=False):
    if os.path.exists(cache):
        with open(cache, encoding="ascii") as fh:
            return [(d["t"], d["p"]) for d in (json.loads(l) for l in fh)]
    paths = [paths_or_file] if is_file else sorted(glob.glob(os.path.join(paths_or_file, "*.txt")))
    out = []
    with open(cache, "w", encoding="ascii") as fh:
        for toks in iter_raw_sentences(paths, max_sents):
            try:
                tags = tg.tag(toks)
            except Exception:
                continue
            asc = [t.encode("ascii", "ignore").decode() for t in toks]
            out.append((asc, tags))
            fh.write(json.dumps({"t": asc, "p": tags}) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--tau", type=float, default=1.0)
    ap.add_argument("--exposure_19c", type=int, default=120000)
    ap.add_argument("--exposure_modern", type=int, default=120000)
    ap.add_argument("--nboot", type=int, default=2000)
    args = ap.parse_args()
    if args.smoke:
        args.exposure_19c = 6000; args.exposure_modern = 6000; args.nboot = 400
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)

    print("[expose] tagging 19c (<=%d) + modern (<=%d) raw sentences..." % (args.exposure_19c, args.exposure_modern), flush=True)
    tag19 = load_or_tag(os.path.join(OUT_DIR, "tagged_19c_%d.jsonl" % args.exposure_19c), LB_RAW, args.exposure_19c, tg)
    tagmod = load_or_tag(os.path.join(OUT_DIR, "tagged_modern_%d.jsonl" % args.exposure_modern), MODERN_RAW, args.exposure_modern, tg, is_file=True)
    print("[expose] tagged 19c=%d modern=%d sents (%.0fs)" % (len(tag19), len(tagmod), time.time() - t0), flush=True)

    # dedup: remove any exposure sentence that appears in the eval populations (leak guard)
    eval_sent_set = set()
    for path in (V1.LB, V1.QA):
        for r in V1.load_pop(path):
            eval_sent_set.add(" ".join(r["sent"].split()))
    tag19 = [(t, p) for (t, p) in tag19 if " ".join(t) not in eval_sent_set]
    A19 = build_assoc(tag19); Amod = build_assoc(tagmod)
    print("[assoc] 19c: VA=%d NA=%d verbs=%d | modern: VA=%d NA=%d verbs=%d"
          % (A19["n_va"], A19["n_na"], len(A19["TV"]), Amod["n_va"], Amod["n_na"], len(Amod["TV"])), flush=True)
    # a couple of sanity peeks at the learned 19c selectional prefs
    for vl, prep in (("retire", "from"), ("hover", "in"), ("look", "at"), ("think", "of")):
        print("    LA(%s,<noun>,%s) 19c=%.2f" % (vl, prep, assoc_LA(A19, vl, "man", prep)), flush=True)

    lb = eval_population(V1.LB, W, tg, A19, Amod, args.tau)
    qa = eval_population(V1.QA, W, tg, Amod, Amod, args.tau)   # modern eval uses MODERN association
    res = {"tau": args.tau, "exposure_19c": len(tag19), "exposure_modern": len(tagmod),
           "assoc_19c": {"n_va": A19["n_va"], "n_na": A19["n_na"]},
           "LB_19c": summarize("LB_19c (register: 19c association)", lb),
           "QA_modern": summarize("QA_modern (retention: modern association)", qa)}
    print("\n[modern gold PP-attach precision on UD-EWT test]", flush=True)
    res["ud_pp_attach"] = ud_pp_attach_precision(W, Amod, args.tau)
    print("  UD-EWT test PP-object attach: BASE=%.4f ADAPT(modern)=%.4f d=%+.4f (n=%d)"
          % (res["ud_pp_attach"]["base"], res["ud_pp_attach"]["adapt"], res["ud_pp_attach"]["delta"], res["ud_pp_attach"]["n"]), flush=True)

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_native_pp_attachment_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
