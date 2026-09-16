"""THE INFINITIVAL GOVERNOR as TWO COMPETING CUES inside the attachment competition (pri 133).

THE PROBLEM (pri 129 6b, counted).  The heads rung attaches an infinitival verb ("to leave") to the wrong head on
32.3% of UD-EWT test infinitivals (109 of 337, the organ's own categories), and the loss is TWO cues it does not
own: (a) `acl_nominal` "a plan TO LEAVE" is 0.2321 correct -- 32 of its 43 errors are "the arm says a VERB or the
ROOT where the gold governor is a NOUN", because every infinitival cue the arm owns pushes the clause AWAY from a
nominal governor; (b) `csubj_extrapos` "it is hard TO SAY" is 0.5652 -- 22 errors across three classes are "the arm
says the expletive PRON where the gold governor is the ADJ that HOLDS THE PREDICATE SLOT", a graded quantity pri
110's `predicate_sites` computes on every read and the infinitival arc never reads.

THE BRAIN.  Infinitival attachment is LEXICALIST constraint satisfaction (MacDonald, Pearlmutter & Seidenberg 1994;
Trueswell, Tanenhaus & Kello 1993 and Garnsey et al. 1997 on lexical frame bias), settled by competition among the
retrieved candidates (Vosse & Kempen 2000; Bates & MacWhinney's validity = availability x reliability).  ONE stored
expectation does the work whatever the candidate's category -- plan/attempt/chance/way (NOUN), want/try (VERB),
hard/easy/eager (ADJ) -- so this is ONE cue, not a list of infinitival-taking nouns, and the same statistic supplies
the verb's own control expectation the nominal has to compete with.  The extraposed family adds the second
constraint: a clause predicates ONE thing (Spivey-Knowlton 1993) and an expletive is a PLACEHOLDER, not a predicate
(Postal & Pullum 1988), so the predicate slot's graded occupancy is a cue FOR its holder and the expletive takes the
competing value.  BOTH LAND AS CUES, NOT OVERRIDES: pri 129's prototype was a separate argmax and LOST
advcl_purpose 0.6338 -> 0.5775 exactly because it overrode the arm's other cues.

ARMS (UD-EWT test, the organ's own categories; population = every infinitival VERB, n=337):
  repro      pri 129's `--infin` table reproduced by calling ITS OWN scorer (the disk outranks the brief)
  accrue     the lexical expectation from READING (no tree, no treebank head, no gold column) + the two cue
             channels' cells accrued from the arm's own graded outcome signal -> a NEW validity asset
  arms       lever decomposition: base / +islot / +iexp / +both, with the twins
  live-ab    THE HEADLINE, through the DIFF: the organ as shipped vs the patched organ, both in one process
  purpose    pri 129's purpose decision re-measured on the patched organ's heads (its own cell, unmodified)
  board      the product's agent / patient / state rows, both arms, exp_board_rows_on_the_reader_v1
NO-REGRESS: the four constructions, UAS, per relation, verbal/non-verbal subjects, read time.

Run: .venv/Scripts/python.exe experiments/exp_infinitival_governor_competition_v1.py --self-test
     [--repro] [--accrue --cap 4000] [--arms --cap 700] [--live-ab] [--purpose] [--oos] [--sweep] [--board]
NO spaCy, NO external parser, NO LLM, no gold head anywhere on the learning path.
hdlab/ and tools/ are READ-ONLY here: the proposal is notes/problems/<slug>/infinitival_governor_patch.diff, and
every number below is produced BY THAT DIFF's own code.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import argparse
import collections
import json
import re
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA

OUT = str(get_output_dir("infinitival_governor_competition_v1"))
SLUG = ("the_attachment_arm_mis_attaches_30_percent_of_infinitival_verbs_wire_the_predicate_slot_into_the_"
        "infinitival_arc_and_add_a_nominal_governor_cue_accrued_from_counts")
DIFF = os.path.join(REPO, "notes", "problems", SLUG, "infinitival_governor_patch.diff")
UD_TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
# THE NEW ASSET (a new file name: the shipped table is never overwritten) = the landed counts + the two new cues'
# accrued cells + the lexical expectation store.
INFIN_ASSET = os.path.join(REPO, "data", "frontend_assets", "attachment_validities_infin_v1.json")
SEED = 20260915
NOMINAL = ("NOUN", "PROPN", "PRON")
INFIN_CLASSES = ("xcomp_control", "advcl_purpose", "acl_nominal", "csubj_extrapos", "in_order_to", "other")


def out_dir():
    os.makedirs(OUT, exist_ok=True)
    return OUT


def _w(name, obj):
    with open(os.path.join(out_dir(), name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=float)


# ---------------------------------------------------------------------------------- the diff IS the organ
def _apply_unified(src, diff_text, path):
    """Apply the hunks of `diff_text` that target `path` to the string `src` (pure python, no git).
    Ported from pri 117's cell, including its blank-context-line lesson."""
    NL = chr(10); CR = chr(13)
    lines = src.split(NL)
    out = []; i = 0; cur = None; hunks = []
    for ln in diff_text.split(NL):
        if ln.startswith("--- a/"):
            cur = ln[6:].strip()
            continue
        if ln.startswith("+++ b/") or ln.startswith("diff "):
            continue
        if ln.startswith("@@"):
            if cur == path:
                m = re.match(r"@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", ln)
                hunks.append([int(m.group(1)), int(m.group(2) or 1), []])
            continue
        if cur == path and hunks and ln[:1] in (" ", "+", "-"):
            hunks[-1][2].append(ln)
    for (start, count, body) in hunks:
        s0 = start - 1
        out.extend(lines[i:s0]); i = s0
        for b in body:
            tag, txt = b[0], b[1:]
            if tag == " ":
                assert lines[i].rstrip(CR) == txt.rstrip(CR), (i, lines[i], txt)
                out.append(lines[i]); i += 1
            elif tag == "-":
                assert lines[i].rstrip(CR) == txt.rstrip(CR), (i, lines[i], txt)
                i += 1
            else:
                out.append(txt)
    out.extend(lines[i:])
    return NL.join(out)


def _patched_source(path="hdlab/attachment_arm.py"):
    src = open(os.path.join(REPO, *path.split("/")), encoding="utf-8", newline="").read()
    dif = open(DIFF, encoding="utf-8", newline="").read()
    return _apply_unified(src, dif, path)


def _fresh_module(src, name, asset=None, real="hdlab/attachment_arm.py"):
    """Load a module from SOURCE TEXT under `name`.  __file__ is pinned to the real organ: the organ derives its
    asset paths from it and a copy loaded elsewhere silently loses the hold expectation and the plausibility store
    (pri 117's measured trap, UAS 0.6328 -> 0.6138)."""
    import importlib.util
    import tempfile
    d = os.path.join(tempfile.gettempdir(), "pri133_mods")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, name + ".py")
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    spec = importlib.util.spec_from_file_location(name, f)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = os.path.join(REPO, *real.split("/"))
    sys.modules[name] = m
    spec.loader.exec_module(m)
    assert m._REPO == REPO, (m._REPO, REPO)
    assert os.path.isfile(m.HOLD_ASSET) and os.path.isfile(m.BF_TSP_ASSET), "the copy lost an asset path"
    if asset:
        m.ASSET = asset; m._TABLE = None
    return m


def shipped_module(name="pri133_arm_shipped"):
    src = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8", newline="").read()
    return _fresh_module(src, name, AA.ASSET)


def patched_module(name="pri133_arm_patched", asset=None):
    return _fresh_module(_patched_source(), name, asset or (INFIN_ASSET if os.path.isfile(INFIN_ASSET) else AA.ASSET))


def install_patched(name="hdlab.attachment_arm"):
    """Bind the patched organ ONTO the live `hdlab.attachment_arm` object, so consumers that already did
    `import hdlab.attachment_arm as AA` see the diff's code (replacing sys.modules would not reach them)."""
    M = patched_module("pri133_arm_live")
    import hdlab.attachment_arm as LIVE
    for k in dir(M):
        if k.startswith("__"):
            continue
        setattr(LIVE, k, getattr(M, k))
    LIVE.ASSET = M.ASSET; LIVE._TABLE = None
    return LIVE


# ---------------------------------------------------------------------------------- the population + the cache
def _load_ud(path, cap=None):
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    s = load_ud(path)
    return s[:cap] if cap else s


def _frontend():
    from hdlab import frontend as FE
    return FE.tagger(), FE.parser()


_CACHE = {}


def cache(pop="ud", cap=None, maxlen=80):
    """The live-chain READ of each sentence, ONCE: the organ's own categories + graded posterior (no gold column;
    the gold heads/labels are the measuring instrument only).  Every arm then re-scores the SAME read, so an A/B
    compares organs and not tagger noise."""
    key = (pop, cap, maxlen)
    if key in _CACHE:
        return _CACHE[key]
    tg, _ps = _frontend()
    if pop == "gum":
        from experiments.exp_one_convention_two_losses_v1 import gum_sentences
        raw = [{"toks": t, "upos": u, "heads": h, "deprels": r} for (t, u, h, r) in gum_sentences(cap=cap or 1200)]
    else:
        raw = []
        for s in _load_ud(UD_TEST if pop == "ud" else UD_TRAIN, cap):
            raw.append({"toks": [t["form"] for t in s], "upos": [t["upos"] for t in s],
                        "heads": [t["head"] for t in s], "deprels": [t["deprel"] for t in s]})
    rows = []
    for si, s in enumerate(raw):
        toks = list(s["toks"]); n = len(toks)
        if n < 3 or n > maxlen:
            continue
        up, tp = tg.tag_with_posterior(toks)
        rows.append({"sid": si, "toks": toks, "up": list(up), "tp": tp, "n": n,
                     "gpos": list(s["upos"]), "gh": list(s["heads"]),
                     "rel": [(r or "").split(":")[0] for r in s["deprels"]]})
    _CACHE[key] = rows
    return rows


def infin_class(low, up, i, dep):
    """pri 129's GOLD construction classes, verbatim (its `_infin_sites`), so the table is comparable."""
    marked = (i >= 3 and low[i - 3] == "in" and low[i - 2] == "order") or \
             (i >= 3 and low[i - 3] == "so" and low[i - 2] == "as")
    if marked:
        return "in_order_to"
    if dep == "xcomp":
        return "xcomp_control"
    if dep == "advcl":
        return "advcl_purpose"
    if dep == "acl":
        return "acl_nominal"
    if dep in ("csubj", "ccomp"):
        return "csubj_extrapos"
    return "other"


def infin_population(rows):
    """Every infinitival VERB by the ORGAN's own categories (a VERB immediately preceded by `to`) with its gold head
    and construction class -- pri 129's population, computed off the same cache every arm scores."""
    out = []
    for r in rows:
        low = [t.lower() for t in r["toks"]]
        if "to" not in low:
            continue
        for i in range(1, r["n"]):
            if r["up"][i] != "VERB" or low[i - 1] != "to":
                continue
            vid = i + 1
            dep = r["rel"][i]
            out.append({"sid": r["sid"], "vid": vid, "cls": infin_class(low, r["up"], i, dep),
                        "gold_head": r["gh"][i], "gold_dep": dep,
                        "gold_head_cat": (r["gpos"][r["gh"][i] - 1] if r["gh"][i] else "ROOT")})
    return out


def _nearest_prev_verb(up, k):
    for j in range(k - 1, -1, -1):
        if up[j] == "VERB":
            return j + 1
    return 0


# ---------------------------------------------------------------------------------- scoring one organ
def score(M, tab, rows, pop_index, occ_fn=None):
    """Decode every cached sentence with organ `M` + table `tab`; return per-sentence records for the paired
    bootstrap: the infinitival hits by class, UAS, per-relation, verbal / non-verbal subject."""
    per = []
    t0 = time.time()
    for r in rows:
        A, nn = M.arc_scores_graded(list(r["toks"]), list(r["up"]), r["tp"], tab)
        hd = M.decode(list(r["toks"]), list(r["up"]), A, nn)[0]
        rec = {"sid": r["sid"], "infin": [], "uas": [0, 0], "rel": {}, "nv": [0, 0], "vb": [0, 0]}
        for i in range(r["n"]):
            g = r["gh"][i]
            if not (0 <= g <= r["n"]):
                continue
            ok = int(hd.get(i + 1, -1) == g)
            rec["uas"][0] += ok; rec["uas"][1] += 1
            rl = r["rel"][i]
            c = rec["rel"].setdefault(rl, [0, 0]); c[0] += ok; c[1] += 1
            if rl in ("nsubj", "nsubj:pass") and 1 <= g <= r["n"]:
                (rec["nv"] if r["gpos"][g - 1] != "VERB" else rec["vb"])[0] += ok
                (rec["nv"] if r["gpos"][g - 1] != "VERB" else rec["vb"])[1] += 1
        for it in pop_index.get(r["sid"], ()):
            rec["infin"].append((it["cls"], int(hd.get(it["vid"], 0) == it["gold_head"]), it["vid"],
                                 int(hd.get(it["vid"], 0))))
        per.append(rec)
    return per, round(time.time() - t0, 1)


def agg_infin(per):
    tot = collections.defaultdict(lambda: [0, 0])
    for rec in per:
        for (cls, ok, _v, _h) in rec["infin"]:
            tot[cls][0] += ok; tot[cls][1] += 1
            tot["ALL"][0] += ok; tot["ALL"][1] += 1
    return {k: (v[0] / max(1, v[1]), v[1]) for k, v in tot.items()}


def agg_key(per, key):
    a = sum(r[key][0] for r in per); b = sum(r[key][1] for r in per)
    return a / max(1, b), b


def agg_rel(per):
    tot = collections.defaultdict(lambda: [0, 0])
    for r in per:
        for k, v in r["rel"].items():
            tot[k][0] += v[0]; tot[k][1] += v[1]
    return {k: (v[0] / max(1, v[1]), v[1]) for k, v in tot.items()}


def boot(perA, perB, stat, n_boot=2000, seed=SEED):
    """Paired bootstrap over SENTENCES of stat(A) - stat(B)."""
    rng = np.random.default_rng(seed)
    m = len(perA); vals = []
    d0 = stat(perA) - stat(perB)
    for _ in range(int(n_boot)):
        pick = rng.integers(0, m, m)
        a = [perA[i] for i in pick]; b = [perB[i] for i in pick]
        v = stat(a) - stat(b)
        if v == v:
            vals.append(v)
    a = np.sort(np.array(vals, float))
    lo = float(a[int(0.025 * len(a))]); hi = float(a[int(0.975 * len(a))])
    return {"delta": float(d0), "lo": lo, "hi": hi, "half_width": (hi - lo) / 2.0, "n_boot": len(a),
            "separated": "UP" if lo > 0 else ("DOWN" if hi < 0 else "no")}


def _stat_infin(cls=None):
    def f(per):
        h = n = 0
        for r in per:
            for (c, ok, _v, _hh) in r["infin"]:
                if cls is None or c == cls:
                    h += ok; n += 1
        return h / n if n else float("nan")
    return f


def _stat_key(key):
    def f(per):
        a = sum(r[key][0] for r in per); b = sum(r[key][1] for r in per)
        return a / b if b else float("nan")
    return f


def _report(name, perA, perB, n_boot, labels=("patched", "shipped")):
    iA = agg_infin(perA); iB = agg_infin(perB)
    print("  %-22s %8s %8s" % ("construction (n)", labels[1], labels[0]))
    rowsout = {}
    for c in ["ALL"] + [k for k in INFIN_CLASSES if k in iA or k in iB]:
        a = iB.get(c, (float("nan"), 0)); b = iA.get(c, (float("nan"), 0))
        bb = boot(perA, perB, _stat_infin(None if c == "ALL" else c), n_boot)
        rowsout[c] = {"n": a[1], labels[1]: a[0], labels[0]: b[0], "paired": bb}
        print("    %-20s %-4d %.4f -> %.4f   %+.4f CI[%+.4f,%+.4f] %s"
              % (c, a[1], a[0], b[0], bb["delta"], bb["lo"], bb["hi"], bb["separated"]))
    for key, lab in (("uas", "UAS"), ("nv", "non-verbal nsubj"), ("vb", "verbal nsubj")):
        a = agg_key(perB, key); b = agg_key(perA, key); bb = boot(perA, perB, _stat_key(key), n_boot)
        rowsout[lab] = {"n": a[1], labels[1]: a[0], labels[0]: b[0], "paired": bb}
        print("    %-20s %-4d %.4f -> %.4f   %+.4f CI[%+.4f,%+.4f] %s"
              % (lab, a[1], a[0], b[0], bb["delta"], bb["lo"], bb["hi"], bb["separated"]))
    rA = agg_rel(perA); rB = agg_rel(perB)
    print("    per relation (%s -> %s; n >= 20):" % (labels[1], labels[0]))
    rel = {}
    for k in sorted(set(rA) | set(rB), key=lambda x: -rB.get(x, (0, 0))[1]):
        a = rB.get(k, (0.0, 0)); b = rA.get(k, (0.0, 0))
        rel[k] = {"n": a[1], labels[1]: a[0], labels[0]: b[0]}
        if a[1] >= 20:
            flag = "" if abs(b[0] - a[0]) < 1e-12 else ("  UP" if b[0] > a[0] else "  DOWN")
            print("      %-10s %.4f -> %.4f (n=%d)%s" % (k, a[0], b[0], a[1], flag))
    return {"per_construction": rowsout, "per_relation": rel}


# ---------------------------------------------------------------------------------- ARM: reproduce pri 129
def repro(cap=None, n_boot=2000):
    """pri 129's `--infin` table, reproduced by calling ITS OWN scorer (imported, never run as a script, so its
    landed metrics.json is untouched) -- and cross-checked against MY cache-based population."""
    import experiments.exp_labels_rung_to_live_consumers_v1 as L
    t0 = time.time()
    r = L.run_infin(cap_train=None, cap_test=cap, n_boot=n_boot, seed=SEED)
    tab = r.pop("_table")
    o = r["overall"]
    print("  pri 129 --infin reproduced: n=%d arm %.4f (error %.4f) prototype %.4f nearest-verb floor %.4f twin %.4f"
          % (o["n"], o["arm_head_accuracy"], o["arm_error_rate"], o["prototype_accuracy"],
             o["floor_nearest_preceding_verb"], o["twin_permuted_strengths"]))
    for c, v in r["per_construction"].items():
        print("    %-16s n=%-4d arm %.4f  proto %.4f  floor %.4f"
              % (c, v["n"], v["arm_head_accuracy"], v["prototype_accuracy"], v["floor_nearest_preceding_verb"]))
    rows = cache("ud", cap)
    pop = infin_population(rows)
    mine = collections.Counter(p["cls"] for p in pop)
    theirs = {c: v["n"] for c, v in r["per_construction"].items()}
    print("  my population vs theirs: n %d vs %d | classes %s vs %s"
          % (len(pop), o["n"], dict(mine), theirs))
    out = {"pri129_infin": r, "my_population_n": len(pop), "my_classes": dict(mine),
           "n_cue_strengths_prototype": len(tab["strength"]), "seconds": round(time.time() - t0, 1)}
    _w("metrics_repro.json", out)
    return out


# ---------------------------------------------------------------------------------- ARM: accrue the knowledge
def accrue(cap=4000, rounds=1, teacher="arm", alpha=1.0, out=INFIN_ASSET, maxlen=40, quiet=False):
    """Accrue BOTH halves of the new knowledge from READING, and write the new asset.

    (1) THE LEXICAL EXPECTATION.  `infin_assoc_from_reading` over UD-EWT train read through the ORGAN'S OWN
        CATEGORIES -- no gold column, no tree, no treebank head.  A parse-free availability estimate plus Hindle-
        Rooth reallocation.
    (2) THE TWO CUES' VALIDITIES.  Two selectable outcome signals, both measured (section 3 of SOLVED.md):
        --teacher arm    the arm's OWN graded tree posterior (the self-supervision this organ is built on).
                         MEASURED AND REJECTED: it teaches the error back (NOUN>VERB:L|NOM:hi +0.157 against
                         VERB>VERB:L|VERB:hi +3.123; PRON>VERB:L|expl +0.116, i.e. the expletive the arm wrongly
                         picks is REWARDED), because the outcome signal IS the belief being repaired.
        --teacher clear  ACQUISITION FROM THE CLEAR CASES (`observe_infinitival_site`, the organ's own observe
                         path): at each site whose governor is unambiguous by adjacency, the clear-case governor
                         accrues the confirmed outcome and every competitor the zero outcome.  No tree, no gold.
        ONLY the two new cue channels are written: every other cell of the landed table is byte-identical, which
        is what makes the A/B a measurement of these cues and not of a rebuild.
    """
    # The asset CARRIES the refuted context channel's cells so that switch stays measurable without a re-accrual,
    # but the READ default is OFF -- so the override is scoped to the module this function loads and RESTORED
    # immediately.  (Measured cost of getting this wrong, in this very cell: leaving it set leaked into a --live-ab
    # run in the same process and reported 0.7359 with advcl_purpose 0.5915, i.e. the refuted arm's profile.)
    _env0 = os.environ.get("HDLAB_ARM_INFIN_CTX")
    os.environ["HDLAB_ARM_INFIN_CTX"] = "1"
    M = patched_module("pri133_arm_accrue", AA.ASSET)
    if _env0 is None:
        os.environ.pop("HDLAB_ARM_INFIN_CTX", None)
    else:
        os.environ["HDLAB_ARM_INFIN_CTX"] = _env0
    tg, _ps = _frontend()
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    sents = load_ud(UD_TRAIN)[:cap]
    read = []
    t0 = time.time()
    for s in sents:
        toks = [t["form"] for t in s]
        if len(toks) < 3 or len(toks) > maxlen:
            continue
        up, tp = tg.tag_with_posterior(toks)
        read.append((toks, list(up), tp))
    if not quiet:
        print("  read %d sentences through the organ's own categories in %.0fs" % (len(read), time.time() - t0))
    assoc = M.infin_assoc_from_reading([(t, p) for (t, p, _q) in read], rounds=rounds)
    if not quiet:
        print("  lexical infinitival expectation: %d keys, %d sites, base %.4f; top:"
              % (len(assoc["n"]), int(assoc["sites"]), assoc["base"]))
        top = sorted(((M.infin_rate(assoc, k) or 0.0, k) for k in assoc["t"] if assoc["n"].get(k, 0) >= 8),
                     reverse=True)[:18]
        print("    " + ", ".join("%s %.3f" % (k, v) for v, k in top))
    tab = M.load_attachment_validities(AA.ASSET)
    tab["infin_assoc"] = assoc
    base = json.loads(json.dumps(tab["counts"]))            # the landed counts, untouched, as the contrast base
    cells = {"iexp": {}, "islot": {}, "ictx": {}}
    kf = None
    if teacher in ("kf", "mix"):
        from tools.build_attachment_validities import knowledge_free_teacher
        kf = knowledge_free_teacher([(t, p, None, None) for (t, p, _q) in read], beta=10.0,
                                    pp_assoc=tab.get("pp_assoc_v2"))
        if not quiet:
            print("  knowledge-free teacher ready in %.0fs" % (time.time() - t0))
    nsent = 0
    clear_tab = None
    if teacher == "clear":
        clear_tab = {"counts": json.loads(json.dumps(base)), "frames": tab.get("frames", {}),
                     "pp_assoc": tab.get("pp_assoc"), "pp_assoc_v2": tab.get("pp_assoc_v2"),
                     "infin_assoc": assoc, "strength": tab["strength"]}
        for _c in ("iexp", "islot", "ictx"):
            clear_tab["counts"]["cues"][_c] = {}
    for (toks, up, tp) in read:
        if not any(t.lower() == "to" for t in toks):
            continue
        occ = M.occupancy_from_posterior(toks, up, tp)
        if teacher == "clear":
            # ACQUISITION FROM THE CLEAR CASES -- the organ's own observe path, one sentence at a time, exactly
            # as it would run online at read time.
            if M.observe_infinitival_site(toks, up, occ, clear_tab, 1.0):
                nsent += 1
            continue
        sc = M.SentenceCues(toks, up, tab.get("frames", {}), tab.get("pp_assoc"), tab.get("pp_assoc_v2"),
                            occ=occ, infin_assoc=assoc)
        if not (sc.iexp_arc or sc.islot_arc):
            continue
        marg = M.head_posterior(toks, up, tab, occ=occ)
        if kf is not None:
            Ak, nk = kf._score_matrix(toks, up)
            from hdlab.graded_parser import single_root_marginals
            mt = single_root_marginals(M.predication_boost(M.parallelism_boost(Ak, toks, up), toks, up), nk, 1.0)
            w = alpha if teacher == "mix" else 0.0
            marg = {j: {h: w * marg.get(j, {}).get(h, 0.0) + (1 - w) * mt.get(j, {}).get(h, 0.0)
                        for h in set(marg.get(j, {})) | set(mt.get(j, {}))} for j in marg}
        for cue, arcs in (("iexp", sc.iexp_arc), ("islot", sc.islot_arc), ("ictx", sc.ictx_arc)):
            for (h, j), val in arcs.items():
                cfg = sc.config(j, h)
                if cfg not in base["config"]:
                    continue                     # an unseen configuration has no base rate to contrast against
                cell = cells[cue].setdefault(cfg + "|" + val, [0.0, 0.0])
                cell[0] += float(marg.get(j, {}).get(h, 0.0)); cell[1] += 1.0
        nsent += 1
    counts = json.loads(json.dumps(base))
    if teacher == "clear":
        for cue in ("iexp", "islot", "ictx"):
            cells[cue] = clear_tab["counts"]["cues"][cue]
    for cue in ("iexp", "islot", "ictx"):
        counts["cues"][cue] = cells[cue]
    tab2 = {"counts": counts, "frames": tab.get("frames", {}), "pp_assoc": tab.get("pp_assoc"),
            "pp_assoc_v2": tab.get("pp_assoc_v2"), "infin_assoc": assoc,
            "strength": M.strengths_from_arc_counts(counts)}
    M.save_attachment_validities(out, tab2)
    st = tab2["strength"]
    if not quiet:
        print("  accrued on %d sentences: %d iexp cells, %d islot cells -> %s"
              % (nsent, len(cells["iexp"]), len(cells["islot"]), os.path.basename(out)))
        for cue in ("iexp", "islot", "ictx"):
            vv = collections.defaultdict(list)
            for k, v in st.get(cue, {}).items():
                vv[k.split("|", 1)[1]].append(v)
            print("    %-6s mean validity by value: %s" % (cue, ", ".join(
                "%s %+.2f(%d)" % (k, float(np.mean(v)), len(v)) for k, v in sorted(vv.items()))))
    other = [c for c in base["cues"] if c not in ("iexp", "islot", "ictx")]
    same = all(base["cues"][c] == counts["cues"][c] for c in other)
    if not quiet:
        print("  every other cue channel byte-identical to the landed table: %s (%d channels)" % (same, len(other)))
    meta = {"cap": cap, "rounds": rounds, "teacher": teacher, "alpha": alpha, "n_read": len(read),
            "n_accrued_sentences": nsent, "n_lex_keys": len(assoc["n"]), "sites": assoc["sites"],
            "base_rate": assoc["base"], "cells": {k: len(v) for k, v in cells.items()},
            "other_channels_identical": bool(same), "asset": out,
            "validity_by_value": {cue: {k.split("|", 1)[1]: 0 for k in st.get(cue, {})} for cue in ("iexp", "islot", "ictx")}}
    _w("metrics_accrue.json", meta)
    return meta


# ---------------------------------------------------------------------------------- ARM: the lever decomposition
def arms(cap=None, pop="ud", n_boot=2000, which=None):
    """Lever by lever on the SAME live-chain read, through the patched organ, switching one cue at a time."""
    rows = cache(pop, cap)
    pidx = collections.defaultdict(list)
    for it in infin_population(rows):
        pidx[it["sid"]].append(it)
    M = patched_module("pri133_arm_arms", INFIN_ASSET)
    tabI = M.load_attachment_validities(INFIN_ASSET)
    S = shipped_module()
    tabS = S.load_attachment_validities(AA.ASSET)
    res = {}
    per = {}

    def run(name, mod, tab):
        p, secs = score(mod, tab, rows, pidx)
        per[name] = p
        ia = agg_infin(p)
        res[name] = {"infin": {k: v[0] for k, v in ia.items()}, "n": {k: v[1] for k, v in ia.items()},
                     "uas": agg_key(p, "uas")[0], "nv": agg_key(p, "nv")[0], "vb": agg_key(p, "vb")[0],
                     "seconds": secs}
        print("  %-14s ALL %.4f | acl %.4f | csubj %.4f | advcl %.4f | xcomp %.4f | UAS %.4f | %.0fs"
              % (name, ia.get("ALL", (0, 0))[0], ia.get("acl_nominal", (0, 0))[0],
                 ia.get("csubj_extrapos", (0, 0))[0], ia.get("advcl_purpose", (0, 0))[0],
                 ia.get("xcomp_control", (0, 0))[0], agg_key(p, "uas")[0], secs))

    want = set(which or ("base", "islot", "iexp", "cues", "reanal", "both", "ictx", "twin_perm", "twin_shuf",
                         "twin_uniform"))
    if "base" in want:
        run("base(shipped)", S, tabS)
    env0 = dict(os.environ)

    def with_env(name, label, **env):
        os.environ.update({k: v for k, v in env.items()})
        Mx = patched_module("pri133_arm_" + name, INFIN_ASSET)
        run(label, Mx, Mx.load_attachment_validities(INFIN_ASSET))
        os.environ.clear(); os.environ.update(env0)

    if "islot" in want:
        with_env("islot", "+islot only", HDLAB_ARM_INFIN_CUE="0", HDLAB_ARM_INFIN_REANALYSIS="0")
    if "iexp" in want:
        with_env("iexp", "+iexp only", HDLAB_ARM_INFIN_SLOT="0", HDLAB_ARM_INFIN_REANALYSIS="0")
    if "cues" in want:
        with_env("cues", "+both cues", HDLAB_ARM_INFIN_REANALYSIS="0")
    if "reanal" in want:
        with_env("reanal", "+reanalysis only", HDLAB_ARM_INFIN_CUE="0", HDLAB_ARM_INFIN_SLOT="0")
    if "noswap" in want:
        with_env("noswap", "+cues+reanal no swap", HDLAB_ARM_INFIN_REANALYSIS_SWAP="0")
    if "ictx" in want:
        with_env("ictx", "+the REFUTED ctx cue", HDLAB_ARM_INFIN_CTX="1")
    if "both" in want:
        run("SHIPPED FORM", M, tabI)
    if "twin_perm" in want:
        t = json.loads(json.dumps({k: v for k, v in tabI.items() if k != "strength" and k != "_idx"}))
        rng = np.random.default_rng(SEED)
        for cue in ("iexp", "islot", "ictx"):
            d = t["counts"]["cues"][cue]
            ks = list(d); vs = [d[k] for k in ks]
            perm = list(rng.permutation(len(vs)))
            t["counts"]["cues"][cue] = {ks[i]: vs[perm[i]] for i in range(len(ks))}
        t["strength"] = M.strengths_from_arc_counts(t["counts"])
        run("twin_permuted", M, t)
    if "twin_shuf" in want:
        t = json.loads(json.dumps({k: v for k, v in tabI.items() if k not in ("strength", "_idx")}))
        rng = np.random.default_rng(SEED + 1)
        A = t["infin_assoc"]
        ks = list(A["t"]); vs = [A["t"][k] for k in ks]
        perm = list(rng.permutation(len(vs)))
        A["t"] = {ks[i]: vs[perm[i]] for i in range(len(ks))}
        t["strength"] = M.strengths_from_arc_counts(t["counts"])
        run("twin_lex_shuffled", M, t)
    res["floor_nearest_preceding_verb"] = _floor_nearest(rows, pidx)
    _w("metrics_arms_%s.json" % pop, res)
    if "twin_uniform" in want:
        # THE OFFSET TWIN.  A targeted overlay accrues its cells over the SITE population while the contrast is
        # taken against the landed CONFIGURATION rate, so every value of a new cue carries a per-configuration
        # OFFSET as well as its information.  This twin collapses every value of both channels to ONE string:
        # the offset survives, the information does not.  It must lose.
        t = json.loads(json.dumps({k: v for k, v in tabI.items() if k not in ("strength", "_idx")}))
        for cue in ("iexp", "islot"):
            agg = [0.0, 0.0]
            for k, v in t["counts"]["cues"][cue].items():
                agg[0] += v[0]; agg[1] += v[1]
            cfgs = {k.split("|", 1)[0] for k in t["counts"]["cues"][cue]}
            share = [agg[0] / max(1, len(cfgs)), agg[1] / max(1, len(cfgs))]
            t["counts"]["cues"][cue] = {c + "|flat": list(share) for c in cfgs}
        t["strength"] = M.strengths_from_arc_counts(t["counts"])
        MU = patched_module("pri133_arm_uniform", INFIN_ASSET)
        MU.INFIN_BINS = (1e9, 1e9, 1e9)
        _orig = MU._infin_bin; MU._infin_bin = lambda r: "flat"
        _origc = MU._csubg_bin; MU._csubg_bin = lambda o: "flat"
        _origv = MU.infin_arc_values

        def flat_values(toks, pos, assoc, occ, _f=_origv):
            a, b, c = _f(toks, pos, assoc, occ)
            return ({k: "flat" for k in a}, {k: "flat" for k in b}, c)
        MU.infin_arc_values = flat_values
        run("twin_uniform_value", MU, t)
        MU._infin_bin = _orig; MU._csubg_bin = _origc; MU.infin_arc_values = _origv
    if "base(shipped)" in per and "SHIPPED FORM" in per:
        print("  PAIRED, the shipped form vs the organ as shipped:")
        res["paired_both_minus_shipped"] = _report("arms", per["SHIPPED FORM"], per["base(shipped)"], n_boot)
    _w("metrics_arms_%s.json" % pop, res)
    return res


def twin_cis(cap=None, n_boot=2000):
    """THE CONTROLS, PAIRED AND CI'd against the SHIPPED FORM (a twin that merely scores lower is not a control).
      twin_permuted      the two cues' accrued cells permuted across their values -> the validities carry no
                         information, the cue VALUES and the sites are unchanged.
      twin_lex_shuffled  the lexical expectation store's counts shuffled across words -> "plan" and "market" swap
                         expectations; everything else, including the predicate-slot cue, is untouched.
      twin_uniform_value EVERY value of both channels collapsed to one string.  This is the control for the
                         ARITHMETIC rather than the information: a targeted overlay accrues its cells over the
                         SITE population while the contrast is taken against the landed CONFIGURATION rate, so a
                         new cue carries a per-configuration OFFSET as well as its information.  The offset
                         survives this twin and the information does not."""
    rows = cache("ud", cap)
    pidx = collections.defaultdict(list)
    for it in infin_population(rows):
        pidx[it["sid"]].append(it)
    M = patched_module("pri133_twin", INFIN_ASSET)
    tabI = M.load_attachment_validities(INFIN_ASSET)
    perM, _s = score(M, tabI, rows, pidx)
    rng = np.random.default_rng(SEED)
    out = {"shipped_form": {"ALL": agg_infin(perM).get("ALL", (0, 0))[0], "uas": agg_key(perM, "uas")[0]}}
    twins = {}
    t = json.loads(json.dumps({k: v for k, v in tabI.items() if k not in ("strength", "_idx")}))
    for cue in ("iexp", "islot"):
        d = t["counts"]["cues"][cue]; ks = list(d); vs = [d[k] for k in ks]
        pm = list(rng.permutation(len(vs)))
        t["counts"]["cues"][cue] = {ks[i]: vs[pm[i]] for i in range(len(ks))}
    t["strength"] = M.strengths_from_arc_counts(t["counts"])
    twins["twin_permuted_validities"] = t
    t2 = json.loads(json.dumps({k: v for k, v in tabI.items() if k not in ("strength", "_idx")}))
    A = t2["infin_assoc"]; ks = list(A["t"]); vs = [A["t"][k] for k in ks]
    pm = list(np.random.default_rng(SEED + 1).permutation(len(vs)))
    A["t"] = {ks[i]: vs[pm[i]] for i in range(len(ks))}
    t2["strength"] = M.strengths_from_arc_counts(t2["counts"])
    twins["twin_shuffled_lexicon"] = t2
    for name, tb in twins.items():
        perT, _ = score(M, tb, rows, pidx)
        b = boot(perM, perT, _stat_infin(None), n_boot)
        ia = agg_infin(perT)
        out[name] = {"ALL": ia.get("ALL", (0, 0))[0],
                     "per": {k: v[0] for k, v in ia.items()}, "uas": agg_key(perT, "uas")[0],
                     "shipped_form_minus_twin": b}
        print("    %-26s ALL %.4f   shipped form - twin %+.4f CI[%+.4f,%+.4f] %s"
              % (name, out[name]["ALL"], b["delta"], b["lo"], b["hi"], b["separated"]))
    _w("metrics_twins.json", out)
    return out


def _floor_nearest(rows, pidx):
    """FLOOR: attach the infinitival verb to the nearest preceding VERB (the arm's dominant existing behaviour)."""
    h = n = 0
    per = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        for it in pidx.get(r["sid"], ()):
            g = _nearest_prev_verb(r["up"], it["vid"] - 2)
            ok = int(g == it["gold_head"])
            h += ok; n += 1
            per[it["cls"]][0] += ok; per[it["cls"]][1] += 1
    return {"ALL": h / max(1, n), "n": n, "per_construction": {k: v[0] / max(1, v[1]) for k, v in per.items()}}


# ---------------------------------------------------------------------------------- ARM: the headline A/B
def live_ab(cap=None, pop="ud", n_boot=2000):
    """THE HEADLINE, through the DIFF: the organ exactly as shipped (landed asset) vs the PATCHED organ (the new
    asset), BOTH IN ONE PROCESS, same sentences, same live-chain read."""
    rows = cache(pop, cap)
    pidx = collections.defaultdict(list)
    for it in infin_population(rows):
        pidx[it["sid"]].append(it)
    S = shipped_module("pri133_ab_shipped"); M = patched_module("pri133_ab_patched", INFIN_ASSET)
    tS = S.load_attachment_validities(AA.ASSET); tM = M.load_attachment_validities(INFIN_ASSET)
    perS, secS = score(S, tS, rows, pidx)
    perM, secM = score(M, tM, rows, pidx)
    print("  %s: %d sentences, %d infinitivals; shipped %.0fs, patched %.0fs"
          % (pop, len(rows), sum(len(v) for v in pidx.values()), secS, secM))
    out = {"pop": pop, "cap": cap, "n_sentences": len(rows), "seconds": {"shipped": secS, "patched": secM},
           "ms_per_sentence": {"shipped": 1000.0 * secS / max(1, len(rows)),
                               "patched": 1000.0 * secM / max(1, len(rows))}}
    out.update(_report("live_ab", perM, perS, n_boot))
    out["floor_nearest_preceding_verb"] = _floor_nearest(rows, pidx)
    print("    floor (nearest preceding VERB) ALL %.4f | per construction %s"
          % (out["floor_nearest_preceding_verb"]["ALL"],
             {k: round(v, 4) for k, v in out["floor_nearest_preceding_verb"]["per_construction"].items()}))
    resid = collections.Counter()
    for rec, r in zip(perM, rows):
        for (cls, ok, vid, got) in rec["infin"]:
            if ok:
                continue
            gc = [it for it in pidx.get(r["sid"], ()) if it["vid"] == vid]
            gcat = gc[0]["gold_head_cat"] if gc else "?"
            acat = r["gpos"][got - 1] if got and got <= r["n"] else "ROOT"
            resid["%s -> arm says %s (gold %s)" % (cls, acat, gcat)] += 1
    out["residual_where_it_goes"] = dict(resid.most_common(16))
    _w("metrics_live_ab_%s.json" % pop, out)
    return out


def residual(cap=None, arm="patched"):
    """EVERY REMAINING MISS, ATTRIBUTED: is the gold governor (a) not RETRIEVED at all (outside the candidate set:
    a window or a category failure), (b) retrieved but OUT-SCORED by the competition, or (c) preferred by the
    competition and LOST BY THE DECODE?  The three have different owners and only (b) is this cue's own residual."""
    rows = cache("ud", cap)
    pidx = collections.defaultdict(list)
    for it in infin_population(rows):
        pidx[it["sid"]].append(it)
    P = patched_module("pri133_resid", INFIN_ASSET)          # the retrieval-set question is asked with the SAME
    #                                                          candidate function in both arms, so "not retrieved"
    #                                                          means the same thing for the shipped organ too.
    M = P if arm == "patched" else shipped_module("pri133_resid_s")
    tab = M.load_attachment_validities(INFIN_ASSET if arm == "patched" else AA.ASSET)
    why = collections.Counter(); bycls = collections.defaultdict(collections.Counter)
    cat_of_gold = collections.Counter(); examples = []
    tot = 0
    for r in rows:
        if not pidx.get(r["sid"]):
            continue
        A, nn = M.arc_scores_graded(list(r["toks"]), list(r["up"]), r["tp"], tab)
        hd = M.decode(list(r["toks"]), list(r["up"]), A, nn)[0]
        for it in pidx[r["sid"]]:
            j = it["vid"]; g = it["gold_head"]; got = hd.get(j, 0)
            tot += 1
            if got == g:
                continue
            cands = P.infin_candidates(r["up"], j)
            if g == 0:
                k = "gold is ROOT"
            elif g not in cands:
                k = ("not retrieved: outside the window" if abs(g - j) > P.INFIN_WINDOW
                     else "not retrieved: category %s not a candidate class" % r["up"][g - 1])
                cat_of_gold[(r["gpos"][g - 1], r["up"][g - 1])] += 1
            else:
                best = max(cands + [0], key=lambda x: A[x][j])
                k = "competition prefers the gold, DECODE lost it" if best == g else \
                    "competition OUT-SCORED the gold (prefers %s)" % (r["up"][best - 1] if best else "ROOT")
            why[k] += 1; bycls[it["cls"]][k] += 1
            if len(examples) < 12 and it["cls"] == "acl_nominal":
                examples.append({"sent": " ".join(r["toks"])[:160], "infin": r["toks"][j - 1],
                                 "gold": (r["toks"][g - 1] if g else "ROOT"), "gold_cat_organ": (r["up"][g - 1] if g else "-"),
                                 "gold_cat_ud": (r["gpos"][g - 1] if g else "-"),
                                 "got": (r["toks"][got - 1] if got else "ROOT"), "why": k})
    out = {"arm": arm, "n": tot, "why": dict(why.most_common()),
           "by_construction": {k: dict(v.most_common()) for k, v in bycls.items()},
           "unretrieved_gold_category_ud_vs_organ": {str(k): v for k, v in cat_of_gold.most_common()},
           "examples_acl_nominal": examples}
    print("  residual attribution (%s, n=%d, %d misses):" % (arm, tot, sum(why.values())))
    for k, v in why.most_common():
        print("    %-52s %d" % (k, v))
    for c, d in sorted(bycls.items(), key=lambda kv: -sum(kv[1].values())):
        print("    %-16s %s" % (c, dict(d.most_common(4))))
    if cat_of_gold:
        print("    unretrieved gold governors (UD category, organ category): %s"
              % {str(k): v for k, v in cat_of_gold.most_common(8)})
    _w("metrics_residual_%s.json" % arm, out)
    return out


# ---------------------------------------------------------------------------------- ARM: the purpose consumer
def purpose(cap=None, n_boot=2000):
    """pri 129's PURPOSE decision (its own cell, unmodified) re-measured on the PATCHED organ's heads: the
    downstream consumer the brief names, whose oracle-ceiling probe said +0.1084 CI-sep is available from correct
    infinitival heads."""
    out = {}
    import experiments.exp_labels_rung_to_live_consumers_v1 as L
    import hdlab.frontend as FE
    print("  ARM A: pri 129's purpose decision on the organ as shipped ...", flush=True)
    a = L.run_goal(cap_train=None, cap_test=cap, n_boot=n_boot, seed=SEED)
    out["shipped"] = {k: v for k, v in a.items() if not k.startswith("_")}
    install_patched()
    FE._P = None                              # the parser caches the organ's TABLE; rebuild it on the new asset
    print("  ARM B: the same decision on the PATCHED organ's heads ...", flush=True)
    b = L.run_goal(cap_train=None, cap_test=cap, n_boot=n_boot, seed=SEED)
    out["patched"] = {k: v for k, v in b.items() if not k.startswith("_")}
    for nm in ("shipped", "patched"):
        d = out[nm]
        print("  %-8s n=%d  competition %.4f | perceptron %.4f | majority %.4f | twin %.4f"
              % (nm, d["n_test_decidable"], d["arms"]["competition_purpose_arm_BF"]["accuracy"],
                 d["arms"]["perceptron_deprel_filter_SHIPPED"]["accuracy"], d["majority_floor"],
                 d["arms"]["twin_same_rate_random"]["accuracy"]))
        print("           paired BF - shipped %+.4f CI[%+.4f,%+.4f]"
              % (d["paired_bootstrap_accuracy_bf_minus_shipped"]["mean"],
                 d["paired_bootstrap_accuracy_bf_minus_shipped"]["lo"],
                 d["paired_bootstrap_accuracy_bf_minus_shipped"]["hi"]))
    _w("metrics_purpose.json", out)
    return out


def board(ud_cap=600, n_boot=1000):
    """THE PRODUCT ROWS the owner reads, both arms in ONE PROCESS (pri 122's reader-driven cell, UNMODIFIED, called
    as a library so its own landed directory is never written -- every file this arm writes lands in MY out_dir).
    The UD rows (who_did_what agent / patient / state) are the ones this rung can reach."""
    import experiments.exp_board_rows_on_the_reader_v1 as B
    import hdlab.frontend as FE
    out = {}
    print("  ARM A: the product's UD rows on the organ as shipped (cap %s) ..." % ud_cap, flush=True)
    t0 = time.time()
    out["shipped"] = B.run_ud(cap=ud_cap, n_boot=n_boot)
    print("    arm A in %.0fs" % (time.time() - t0), flush=True)
    install_patched()
    FE._P = None
    B.OUT_DIR = out_dir()
    print("  ARM B: the same rows on the PATCHED organ ...", flush=True)
    t0 = time.time()
    out["patched"] = B.run_ud(cap=ud_cap, n_boot=n_boot)
    print("    arm B in %.0fs" % (time.time() - t0), flush=True)
    rowsA = out["shipped"].get("rows", out["shipped"]); rowsB = out["patched"].get("rows", out["patched"])
    print("  %-34s %8s %8s" % ("row (provenance)", "shipped", "patched"))
    for k in sorted(set(rowsA) | set(rowsB)):
        a = rowsA.get(k); b = rowsB.get(k)
        if not isinstance(a, dict) or not isinstance(b, dict):
            continue
        for f in ("model_acc", "acc", "model", "f1"):
            if f in a and f in b:
                d = (b[f] or 0.0) - (a[f] or 0.0)
                print("    %-32s %.4f -> %.4f  %+.4f  n=%s" % (k, a[f] or 0.0, b[f] or 0.0, d, a.get("n")))
                break
    _w("metrics_board_ud.json", out)
    return out


# ---------------------------------------------------------------------------------- self-test
def self_test():
    ok = [0, 0]

    def ck(name, cond, extra=""):
        ok[1] += 1
        if cond:
            ok[0] += 1; print("  ok   " + name)
        else:
            print("  FAIL " + name + "  " + str(extra))

    M = patched_module("pri133_selftest", AA.ASSET)
    ck("the diff applies in memory and the patched organ imports", hasattr(M, "infin_arc_values"))
    ck("both new cues are in CUES", "iexp" in M.CUES and "islot" in M.CUES, M.CUES)
    ck("the organ file on disk is untouched",
       "infin_arc_values" not in open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8").read())
    tk = "it is hard to say so".split(); ps = ["PRON", "AUX", "ADJ", "PART", "VERB", "ADV"]
    ck("the infinitival site is found by the organ's own categories", M.infin_sites(tk, ps) == [5])
    ck("`to` as ADP is also a marker (the category organ reads it either way)",
       M.infin_sites(tk, ["PRON", "AUX", "ADJ", "ADP", "VERB", "ADV"]) == [5])
    ck("a finite verb after `to` is NOT a site", M.infin_sites("go to the shop".split(),
                                                              ["VERB", "ADP", "DET", "NOUN"]) == [])
    cands = M.infin_candidates(ps, 5)
    ck("candidates are the retrieved predicate-capable/nominal words, not every token", cands == [1, 2, 3], cands)
    occ = M.occupancy_from_tags(tk, ps)
    ck("the predicate slot is held by the ADJ, graded, not by the expletive",
       occ[2] > 0.9 and occ[0] == 0.0, occ)
    A = M.infin_assoc_from_reading([(tk, ps), ("a plan to leave now".split(), ["DET", "NOUN", "PART", "VERB", "ADV"]),
                                    ("we went to the market to buy it".split(),
                                     ["PRON", "VERB", "ADP", "DET", "NOUN", "PART", "VERB", "PRON"])], rounds=1)
    ck("the lexical expectation is accrued with no tree and no gold column", A["sites"] >= 2 and A["n"])
    iex, isl, ict = M.infin_arc_values(tk, ps, A, occ)
    ck("islot values the slot holder high and marks the expletive a placeholder",
       isl[(3, 5)].startswith("slot:") and isl[(1, 5)] == "expl", isl)
    ck("iexp values each candidate by its own class x expectation bin", iex[(3, 5)].startswith("ADJ:"), iex)
    iex0, isl0, ict0 = M.infin_arc_values(tk, ps, None, None)
    ck("each channel degrades to SILENCE when its input is absent (no exception)", iex0 == {} and isl0 == {})
    # the organ's fastpath invariant must hold WITH the new cues
    tabI = M.load_attachment_validities(INFIN_ASSET) if os.path.isfile(INFIN_ASSET) else None
    if tabI is not None:
        ck("the new asset carries both cue channels",
           "iexp" in tabI["strength"] and "islot" in tabI["strength"] and tabI.get("infin_assoc"))
        from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
        worst = 0.0; nsent = 0
        for s in load_ud(UD_TEST)[:60]:
            toks = [t["form"] for t in s]
            if len(toks) > 24:
                continue
            up = [t["upos"] for t in s]
            o = M.occupancy_from_tags(toks, up)
            X, n = M.arc_scores(toks, up, tabI, o); Y, _ = M.arc_scores_reference(toks, up, tabI, o)
            fa = np.isfinite(X)
            if not np.array_equal(fa, np.isfinite(Y)):
                worst = 1e9; break
            worst = max(worst, float(np.max(np.abs(X[fa] - Y[fa]))) if fa.any() else 0.0); nsent += 1
        ck("vectorised readout == the reference loop to 1e-9 WITH all three new cues (%d sentences)" % nsent,
           worst <= 1e-9, worst)
        # the observe path moves the knowledge and the strengths
        t2 = M.load_attachment_validities(INFIN_ASSET)
        before = M.infin_rate(t2["infin_assoc"], M.infin_key(tk, ps, 3))
        n_acc = M.observe_infinitival_governor(tk, ps, 5, 3, t2)
        after = M.infin_rate(t2["infin_assoc"], M.infin_key(tk, ps, 3))
        ck("the observe path accrues cue cells AND raises the governor's lexical expectation (plastic)",
           n_acc > 0 and after > before, (n_acc, before, after))
    # the switches reproduce the shipped organ exactly
    env0 = dict(os.environ)
    os.environ["HDLAB_ARM_INFIN_CUE"] = "0"; os.environ["HDLAB_ARM_INFIN_SLOT"] = "0"; os.environ["HDLAB_ARM_INFIN_CTX"] = "0"
    os.environ["HDLAB_ARM_INFIN_REANALYSIS"] = "0"
    Moff = patched_module("pri133_selftest_off", AA.ASSET)
    S = shipped_module("pri133_selftest_shipped")
    os.environ.clear(); os.environ.update(env0)
    tS = S.load_attachment_validities(AA.ASSET); tO = Moff.load_attachment_validities(AA.ASSET)
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    diffs = 0; nn = 0
    for s in load_ud(UD_TEST)[:40]:
        toks = [t["form"] for t in s]; up = [t["upos"] for t in s]
        if len(toks) < 3 or len(toks) > 30:
            continue
        o = S.occupancy_from_tags(toks, up)
        X, n1 = S.arc_scores(toks, up, tS, o); Y, n2 = Moff.arc_scores(toks, up, tO, o)
        fa = np.isfinite(X) & np.isfinite(Y)
        if not np.array_equal(np.isfinite(X), np.isfinite(Y)) or (fa.any() and np.max(np.abs(X[fa] - Y[fa])) > 1e-12):
            diffs += 1
        nn += 1
    ck("with every new switch OFF the patched organ reproduces the shipped readout exactly (%d sentences)" % nn,
       diffs == 0 and nn > 0, diffs)
    # the builder half of the diff
    bsrc = _patched_source("tools/build_attachment_validities.py")
    ck("the builder's diff passes the new argument at EVERY SentenceCues call site it owns",
       bsrc.count("infin_assoc=infin_assoc") == 2 and "infin_assoc_from_reading" in bsrc,
       bsrc.count("infin_assoc=infin_assoc"))
    ck("the builder carries the association into the saved table (both rounds)",
       bsrc.count('"infin_assoc": infin_assoc') == 2)
    print(chr(10) + "%d/%d checks passed" % (ok[0], ok[1]))
    return ok


# ---------------------------------------------------------------------------------- sweeps
def sweep(cap=None, n_boot=500):
    """The operating points that are FREE to move: the expectation bins, the retrieval window, the reallocation
    rounds, the shrinkage.  Reported as a phase diagram, never adopted from a number."""
    rows = cache("ud", cap)
    pidx = collections.defaultdict(list)
    for it in infin_population(rows):
        pidx[it["sid"]].append(it)
    res = {}
    for name, env in (("window 4", {"HDLAB_ARM_INFIN_WINDOW": "4"}),
                      ("window 6", {"HDLAB_ARM_INFIN_WINDOW": "6"}),
                      ("window 8 (default)", {}),
                      ("window 12", {"HDLAB_ARM_INFIN_WINDOW": "12"})):
        env0 = dict(os.environ); os.environ.update(env)
        Mx = patched_module("pri133_sw_" + re.sub(r"\W", "", name), INFIN_ASSET)
        p, _s = score(Mx, Mx.load_attachment_validities(INFIN_ASSET), rows, pidx)
        ia = agg_infin(p)
        res[name] = {"ALL": ia.get("ALL", (0, 0))[0], "uas": agg_key(p, "uas")[0],
                     "per": {k: v[0] for k, v in ia.items()}}
        print("  %-20s ALL %.4f UAS %.4f  acl %.4f csubj %.4f advcl %.4f"
              % (name, res[name]["ALL"], res[name]["uas"], ia.get("acl_nominal", (0, 0))[0],
                 ia.get("csubj_extrapos", (0, 0))[0], ia.get("advcl_purpose", (0, 0))[0]))
        os.environ.clear(); os.environ.update(env0)
    _w("metrics_sweep.json", res)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("self-test", "repro", "accrue", "arms", "live-ab", "purpose", "oos", "sweep", "board", "residual", "twins"):
        ap.add_argument("--" + k, action="store_true")
    ap.add_argument("--cap", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--teacher", default="arm")
    ap.add_argument("--alpha", type=float, default=1.0)
    ap.add_argument("--out", default=INFIN_ASSET)
    a = ap.parse_args(argv)
    t0 = time.time()
    M = {}
    if getattr(a, "self_test"):
        M["self_test"] = self_test()
    if a.repro:
        print("REPRO -- pri 129's --infin table, its own scorer:"); M["repro"] = repro(a.cap, a.n_boot)
    if a.accrue:
        print("ACCRUE -- the lexical expectation + the two cues' validities, from reading:")
        M["accrue"] = accrue(cap=a.cap or 4000, rounds=a.rounds, teacher=a.teacher, alpha=a.alpha, out=a.out)
    if a.arms:
        print("ARMS -- lever by lever:"); M["arms"] = arms(a.cap, "ud", a.n_boot)
    if getattr(a, "live_ab"):
        print("LIVE A/B -- the organ as shipped vs the patched organ, one process:")
        M["live_ab"] = live_ab(a.cap, "ud", a.n_boot)
    if a.oos:
        print("OUT OF SUPPLY -- GUM / GENTLE:"); M["oos"] = live_ab(a.cap or 1200, "gum", a.n_boot)
    if a.purpose:
        print("PURPOSE -- pri 129's own consumer:"); M["purpose"] = purpose(a.cap, a.n_boot)
    if a.twins:
        print("TWINS -- the information-free controls, paired against the shipped form:")
        M["twins"] = twin_cis(a.cap, a.n_boot)
    if a.board:
        print("BOARD -- the product's UD rows, both arms one process:"); M["board"] = board(a.cap or 600, 1000)
    if a.residual:
        print("RESIDUAL -- every remaining miss, attributed:")
        M["residual_shipped"] = residual(a.cap, "shipped"); M["residual"] = residual(a.cap, "patched")
    if a.sweep:
        print("SWEEP -- the free operating points:"); M["sweep"] = sweep(a.cap)
    M["elapsed_s"] = round(time.time() - t0, 1)
    print("done in %.0fs" % M["elapsed_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
