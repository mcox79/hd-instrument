"""exp_frame_sense_context_scaleup_v1 -- the LEVER named by task #1b: the bottleneck to beating most-frequent-
sense (MFS) on verb-sense disambiguation is CONTEXT-MODEL TRAINING DATA. An ORACLE bag-of-words context model
(P(coarse_frame | context content-words), trained on train+test) reaches ~0.78 on the motion confusion; the same
model trained on the SemCor 80/20 split reaches only ~0.67; MFS is ~0.65. So the gap is DATA, not the model.

This cell BOOTSTRAP-LABELS a large external corpus (SimpleWiki + Tom Sawyer / Alice / Sherlock) with an INDEPENDENT
teacher -- the disambiguator's CONSTRUCTION / IDIOM / LIGHT-VERB cue -- which fires only when a diagnostic
argument-structure construction is present (v.diagnostic True AND v.route in {joint, idiom, light_verb}). Those are
HIGH-PRECISION, CONTEXT-INDEPENDENT labels: the teacher reads the realized syntax, NOT the surrounding content
words the context model learns from. So training a P(frame|context) model on (context content-lemmas -> teacher
frame) is legitimate CO-TRAINING (a second, disjoint view), not self-labeling. We then train the bag context model
on this large bootstrap set (COMBINED with the SemCor-train labels) and ask, on the HELD-OUT SemCor TEST split:

  does scaling the context training data close the oracle gap and beat MFS with override precision > 0.5?

FAIR TEST (one variable): every arm shares the IDENTICAL train-MFS prior (from the SemCor train split); the context
model is the only thing that changes across arms; nothing is ever trained on the SemCor TEST split except the
clearly-labelled ORACLE reference arm (which peeks TEST, is an upper bound, and makes NO fair claim). Populations:
MOTION (motion vs not) and PROP (perception/speech: communication|cognition vs not), each CURATED (exemplar verbs)
and AUTO (verb_confusions-selected). Metrics per arm: accuracy, SUBORDINATE recovery (gold != train-MFS),
OVERRIDE PRECISION c/(b+c) (of the items where the arm disagrees with MFS, how often it is right; >0.5 => beats
MFS), and McNemar(b,c,p) vs MFS.

spaCy-bound corpus parsing -> runs INLINE (remote has no spaCy). Bootstrap parses cached to a pkl. Reads the cached
SemCor instances (instances_v6.pkl, else v5, else builds a small split). Writes ONLY to
data/exp_frame_sense_context_scaleup_v1[/ _smoke]. NO hdlab writes. ASCII only.
"""
from __future__ import annotations
import argparse, json, math, os, pickle, random, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.frame_sense_disambiguator import FrameSenseDisambiguator, candidate_frames
from experiments.exp_frame_sense_context_v1 import learn_context, context_scores, mcnemar_p
from experiments.exp_frame_sense_confusion_pairs_v1 import MD_VERBS, PROP_VERBS, PROP, _FakeTok
from experiments.exp_frame_sense_semcor_v1 import _content_lemmas

ANCHOR = "frame_sense_context_scaleup_v1"
W_CTX = 3.0                                        # matches exp_frame_sense_context_v1 (the config behind ~0.67)
CACHE_V6 = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v6.pkl")
CACHE_V5 = os.path.join(REPO, "data", "exp_frame_sense_semcor_v1", "instances_v5.pkl")

_COR = os.path.join(REPO, "data", "corpora")
SIMPLEWIKI = os.path.join(_COR, "simplewiki", "simplewiki_clean_v1.txt")
LIT_FILES = [
    os.path.join(_COR, "tom_sawyer", "cleaned", "tom_sawyer.clean.txt"),
    os.path.join(_COR, "alice_in_wonderland", "cleaned", "alice_in_wonderland.clean.txt"),
    os.path.join(_COR, "sherlock_holmes", "cleaned", "adventures.clean.txt"),
    os.path.join(_COR, "sherlock_holmes", "cleaned", "memoirs.clean.txt"),
]
DIAG_ROUTES = ("joint", "idiom", "light_verb")


# ---------------------------------------------------------------------------
# Corpus readers: literary text is paragraph-wrapped (join blank-line-separated blocks); SimpleWiki is
# one-sentence-per-line -> uniform random-BYTE-OFFSET sampling across the whole 251MB file (cheap, unbiased).
# ---------------------------------------------------------------------------
def _lit_paragraphs(path):
    if not os.path.exists(path):
        return
    para = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                if para:
                    txt = " ".join(para)
                    if len(txt.split()) >= 5 and not txt.isupper():
                        yield txt
                    para = []
            else:
                para.append(line)
    if para:
        txt = " ".join(para)
        if len(txt.split()) >= 5 and not txt.isupper():
            yield txt


def _simplewiki_lines(path, seed, limit):
    """Uniform random-offset line sampler: seek to a random byte, drop the partial line, yield the next full one."""
    if not os.path.exists(path):
        return
    size = os.path.getsize(path)
    rng = random.Random(seed)
    seen = 0
    guard = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        while seen < limit and guard < limit * 20:
            guard += 1
            off = rng.randrange(max(1, size - 1))
            f.seek(off)
            f.readline()                          # discard the partial line we landed inside
            ln = f.readline()
            if not ln:
                continue
            ln = ln.strip()
            wc = len(ln.split())
            if 6 <= wc <= 60 and ln[:1].isalpha():
                seen += 1
                yield ln


def _blocks(seed, wiki_limit):
    """Text blocks to parse: literary paragraphs first, then random SimpleWiki lines."""
    for p in LIT_FILES:
        for para in _lit_paragraphs(p):
            yield para
    for ln in _simplewiki_lines(SIMPLEWIKI, seed, wiki_limit):
        yield ln


# ---------------------------------------------------------------------------
# BOOTSTRAP collection: parse the corpus, and for every polysemous VERB token where the construction/idiom teacher
# fires a DIAGNOSTIC label, record (context content-lemmas, teacher_frame). The teacher is context-INDEPENDENT.
# ---------------------------------------------------------------------------
def collect_bootstrap(max_sents, seed, batch_size=128, time_budget_s=1800.0, nlp=None):
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm", disable=["ner"])
    dis = FrameSenseDisambiguator(nlp="cached")   # disambiguate_token uses the passed live sent/tok, not self._nlp
    boot = []
    by_frame, by_route, top_lemma = Counter(), Counter(), Counter()
    n_sents = n_cand_tokens = 0
    t0 = time.time()
    stop = False
    for doc in nlp.pipe(_blocks(seed, wiki_limit=max_sents), batch_size=batch_size):
        for sent in doc.sents:
            n_sents += 1
            for tok in sent:
                if tok.pos_ != "VERB":
                    continue
                lemma = tok.lemma_.lower()
                if not lemma.isalpha():
                    continue
                cands = candidate_frames(lemma)
                if len(cands) < 2:
                    continue
                n_cand_tokens += 1
                v = dis.disambiguate_token(sent, tok)           # cand=None -> idiom / light_verb routes can fire
                if v.diagnostic and v.route in DIAG_ROUTES and v.frame in cands:
                    ctx = _content_lemmas(sent, skip_i=tok.i)[:24]
                    if not ctx:
                        continue
                    boot.append({"gold_frame": v.frame, "ctx": ctx, "lemma": lemma, "route": v.route})
                    by_frame[v.frame] += 1
                    by_route[v.route] += 1
                    top_lemma[lemma] += 1
            if n_sents >= max_sents or (time.time() - t0) > time_budget_s:
                stop = True
                break
        if stop:
            break
    meta = {"n_sents_parsed": n_sents, "n_verb_cand_tokens": n_cand_tokens,
            "n_bootstrap_instances": len(boot), "elapsed_collect_s": round(time.time() - t0, 1),
            "by_frame": dict(by_frame.most_common()), "by_route": dict(by_route.most_common()),
            "top_lemmas": dict(top_lemma.most_common(20))}
    return boot, meta


# ---------------------------------------------------------------------------
# SemCor test source
# ---------------------------------------------------------------------------
def load_semcor(smoke=False):
    """Prefer instances_v6.pkl; wait briefly if it looks mid-write; else v5; else build a small split."""
    for path in (CACHE_V6, CACHE_V5):
        for attempt in range(4):
            if os.path.exists(path) and os.path.getsize(path) > 100000:
                try:
                    insts, _ = pickle.load(open(path, "rb"))
                    if insts and all(k in insts[0] for k in ("lemma", "gold_frame", "cands", "train", "ctx")):
                        return insts, os.path.basename(path)
                except Exception:
                    pass
            if path == CACHE_V6:
                time.sleep(60)                     # v6 may still be building: retry a few times (~4 min total)
            else:
                break
    from experiments.exp_frame_sense_semcor_v1 import build_instances
    insts, _ = build_instances(max_sents=1200 if smoke else 6000)
    return insts, "built_fallback"


# ---------------------------------------------------------------------------
# Eval: mirrors exp_frame_sense_context_v1.eval_pop (matched prior, same CONTEXT scoring) but swaps the context
# model's TRAINING DATA across arms. MFS | CTX_SEMCOR (SemCor pop-train only) | CTX_BOOT (pop-train + bootstrap)
# | CTX_ORACLE (pop-train + TEST ctx+gold; upper-bound reference, peeks TEST, NOT a fair arm).
# ---------------------------------------------------------------------------
def _arm_stats(pred, mfs, gold, subord):
    b = int(((mfs == gold) & (pred != gold)).sum())          # MFS right, arm wrong
    c = int(((mfs != gold) & (pred == gold)).sum())          # MFS wrong, arm right
    prec = c / (b + c) if (b + c) else None
    return {"acc": round(float((pred == gold).mean()), 3),
            "subord_recovery": round(float((pred[subord] == gold[subord]).mean()) if subord.sum() else 0.0, 3),
            "override_precision": round(prec, 3) if prec is not None else None,
            "b_mfsonly": b, "c_armonly": c, "mcnemar_p": round(mcnemar_p(b, c), 4)}


def eval_pop(insts, which, curated, bootstrap, w_ctx=W_CTX):
    target_is = (lambda f: f == "motion") if which == "motion" else (lambda f: f in PROP)
    fam = "md" if which == "motion" else "prop"
    keyset = {"motion"} if which == "motion" else PROP
    from experiments.frame_sense_disambiguator import verb_confusions
    if curated:
        verbs = MD_VERBS if which == "motion" else PROP_VERBS
        sub = [it for it in insts if it["lemma"] in verbs and (set(it["cands"]) & keyset)]
    else:
        sub = [it for it in insts if fam in verb_confusions(it["cands"]) and (set(it["cands"]) & keyset)]
    train = [it for it in sub if it["train"]]
    test = [it for it in sub if not it["train"]]
    cpri = defaultdict(lambda: defaultdict(float))
    for it in train:
        cpri[it["lemma"]][it["gold_frame"]] += 1.0
    cpri = {lm: dict(d) for lm, d in cpri.items()}
    # DIAGNOSTIC of the scaling lever: is a regression (if any) caused by the large bootstrap SWAMPING the small
    # in-domain SemCor counts (fixable by re-weighting), or by the bootstrap being domain-mismatched / teacher-noisy
    # (a real ceiling for this corpus+teacher)? BOOT_ONLY = bootstrap alone; BOOT_MATCHED = bootstrap SUBSAMPLED to
    # the SemCor-train size before combining (50/50 mass, so neither view swamps the other).
    rng = random.Random(20260828)
    if len(bootstrap) > len(train) and len(train) > 0:
        boot_matched = rng.sample(bootstrap, len(train))
    else:
        boot_matched = list(bootstrap)
    m_semcor = learn_context(train)
    m_boot = learn_context(train + bootstrap)                # SemCor pop-train + the large bootstrap corpus
    m_boot_only = learn_context(bootstrap)                   # bootstrap teacher labels ALONE (transfer test)
    m_boot_matched = learn_context(train + boot_matched)     # size-matched combination (swamping control)
    m_oracle = learn_context(train + test)                   # reference upper bound (peeks TEST gold+ctx)
    models = {"CTX_SEMCOR": m_semcor, "CTX_BOOT": m_boot, "CTX_BOOT_ONLY": m_boot_only,
              "CTX_BOOT_MATCHED": m_boot_matched, "CTX_ORACLE": m_oracle}

    def mfs_pred(it):
        d = cpri.get(it["lemma"], {})
        return target_is(max(it["cands"], key=lambda c: d.get(c, 0.0))) if d else target_is(it["cands"][0])

    arm_names = ("MFS", "CTX_SEMCOR", "CTX_BOOT", "CTX_BOOT_ONLY", "CTX_BOOT_MATCHED", "CTX_ORACLE")
    gold, mfs = [], []
    arms = {k: [] for k in arm_names}
    for it in test:
        gold.append(target_is(it["gold_frame"]))
        cands = it["cands"]
        prio = cpri.get(it["lemma"]) or {}
        prior_arr = {c: prio.get(c, 0.0) for c in cands}
        mfs.append(mfs_pred(it))
        arms["MFS"].append(mfs_pred(it))
        for name, model in models.items():
            cz = context_scores(model, cands, it.get("ctx", []))
            pick = max(cands, key=lambda c: prior_arr[c] + w_ctx * cz[c])
            arms[name].append(target_is(pick))
    gold = np.array(gold); mfs = np.array(mfs)
    subord = mfs != gold
    out = {"n": len(gold), "n_subordinate": int(subord.sum()),
           "pct_subordinate": round(float(subord.mean()), 3) if len(gold) else 0.0,
           "n_train": len(train)}
    for name in arm_names:
        out[name] = _arm_stats(np.array(arms[name]), mfs, gold, subord)
    return out


# ---------------------------------------------------------------------------
def run(mode="full", seed=20260828, max_sents=None, w_ctx=W_CTX, nlp=None, reuse_boot=False):
    t0 = time.time()
    smoke = mode in ("smoke", "self_test")
    if max_sents is None:
        max_sents = {"full": 60000, "smoke": 600, "self_test": 40}[mode]
    out_dir = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    boot_cache = os.path.join(out_dir, f"bootstrap_{max_sents}_{seed}.pkl")
    if reuse_boot and os.path.exists(boot_cache):
        boot, boot_meta = pickle.load(open(boot_cache, "rb"))
        boot_meta["reused_cache"] = True
    else:
        boot, boot_meta = collect_bootstrap(max_sents, seed, nlp=nlp)
        try:
            pickle.dump((boot, boot_meta), open(boot_cache, "wb"))
        except Exception:
            pass
    insts, src = load_semcor(smoke=smoke)
    pops = {}
    for which in ("motion", "prop"):
        for cur in (True, False):
            pops[f"{which}_{'curated' if cur else 'auto'}"] = eval_pop(insts, which, cur, boot, w_ctx=w_ctx)
    # verdict: the LEVER's real question is whether SCALING the context training data (SemCor + bootstrap) moves
    # the SemCor-split context model TOWARD the ORACLE upper bound. gap_closed_frac = (BOOT - SemCor)/(ORACLE -
    # SemCor): >0 closes the gap, <0 regresses below the in-domain SemCor model. We ALSO report whether BOOT still
    # clears the MFS floor with override precision > 0.5 (the front-end's minimum bar).
    mv = []
    for pop in ("motion_curated", "motion_auto"):
        r = pops[pop]
        bt, sc, mf, orc = r["CTX_BOOT"], r["CTX_SEMCOR"], r["MFS"], r["CTX_ORACLE"]
        beats_mfs = bool(bt["acc"] > mf["acc"] and (bt["override_precision"] or 0) > 0.5 and bt["c_armonly"] > bt["b_mfsonly"])
        closes = bool(bt["acc"] > sc["acc"])
        closed = round((bt["acc"] - sc["acc"]) / (orc["acc"] - sc["acc"]), 3) if (orc["acc"] - sc["acc"]) > 1e-9 else None
        mv.append({"pop": pop, "mfs": mf["acc"], "ctx_semcor": sc["acc"], "ctx_boot": bt["acc"],
                   "ctx_boot_only": r["CTX_BOOT_ONLY"]["acc"], "ctx_boot_matched": r["CTX_BOOT_MATCHED"]["acc"],
                   "ctx_oracle": orc["acc"], "boot_beats_mfs_ovrprec>0.5": beats_mfs,
                   "boot_improves_on_semcor": closes, "gap_closed_frac": closed})
    any_close = any(m["boot_improves_on_semcor"] for m in mv)
    any_beat = any(m["boot_beats_mfs_ovrprec>0.5"] for m in mv)
    if any_close:
        verdict = "BOOTSTRAP_SCALING_CLOSES_ORACLE_GAP"
    elif any_beat:
        verdict = "BOOTSTRAP_BEATS_MFS_BUT_REGRESSES_VS_SEMCOR_CONTEXT"
    else:
        verdict = "BOOTSTRAP_SCALING_DOES_NOT_HELP"
    return {"anchor_name": ANCHOR, "run_mode": mode, "seed": seed, "w_ctx": w_ctx,
            "semcor_source": src, "bootstrap": boot_meta, "motion_verdict_detail": mv,
            "verdict": verdict, "pops": pops, "elapsed_s": round(time.time() - t0, 1),
            "ts_iso": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
def _self_test():
    """Hermetic: parse a tiny inline batch with clear constructions, verify the teacher fires and the arms compute.
    No corpora reads; deterministic."""
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    dis = FrameSenseDisambiguator(nlp="cached")
    sents = [
        "She left the keys on the table.", "He gave Mary the book.", "He observed that it was late.",
        "She took a long walk.", "He returned a sharp reply.", "They walked out into the cold night.",
        "He noticed that the door was open.", "She placed the cup on the shelf.",
    ]
    boot = []
    for doc in nlp.pipe(sents):
        for sent in doc.sents:
            for tok in sent:
                if tok.pos_ != "VERB":
                    continue
                lemma = tok.lemma_.lower()
                if len(candidate_frames(lemma)) < 2:
                    continue
                v = dis.disambiguate_token(sent, tok)
                if v.diagnostic and v.route in DIAG_ROUTES and v.frame in candidate_frames(lemma):
                    ctx = _content_lemmas(sent, skip_i=tok.i)[:24]
                    if ctx:
                        boot.append({"gold_frame": v.frame, "ctx": ctx, "lemma": lemma, "route": v.route})
    print(f"  bootstrap teacher fired on {len(boot)} tokens: {[(b['lemma'], b['gold_frame']) for b in boot]}")
    assert len(boot) >= 3, "teacher should fire on >=3 of the clear-construction sentences"
    m = learn_context(boot)
    cz = context_scores(m, ["motion", "possession"], ["table", "shelf", "cup"])
    assert all(math.isfinite(x) for x in cz.values()), "context_scores must be finite"
    # tiny synthetic eval to exercise the arm math
    fake = [
        {"lemma": "leave", "gold_frame": "motion", "cands": ["motion", "possession"], "train": True, "ctx": ["room", "door"]},
        {"lemma": "leave", "gold_frame": "possession", "cands": ["motion", "possession"], "train": True, "ctx": ["key", "table"]},
        {"lemma": "leave", "gold_frame": "motion", "cands": ["motion", "possession"], "train": False, "ctx": ["room", "quietly"]},
        {"lemma": "leave", "gold_frame": "possession", "cands": ["motion", "possession"], "train": False, "ctx": ["key", "table"]},
    ]
    r = eval_pop(fake, "motion", True, boot)
    assert set(("MFS", "CTX_SEMCOR", "CTX_BOOT", "CTX_ORACLE")).issubset(r), "all arms present"
    assert r["n"] == 2, "two test items"
    print(f"  self-test eval arms: MFS acc={r['MFS']['acc']} CTX_BOOT acc={r['CTX_BOOT']['acc']} (n={r['n']})")
    print("SELF-TEST frame_sense_context_scaleup_v1: PASS")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--seed", type=int, default=20260828)
    ap.add_argument("--max-sents", type=int, default=None)
    ap.add_argument("--w", type=float, default=W_CTX)
    ap.add_argument("--reuse-boot", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        ok = _self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if (args.smoke or args.mode == "smoke") else "full"
    out_dir = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    m = run(mode=mode, seed=args.seed, max_sents=args.max_sents, w_ctx=args.w, reuse_boot=args.reuse_boot)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    json.dump(m, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))

    bm = m["bootstrap"]
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s  w_ctx={m['w_ctx']} semcor={m['semcor_source']} ===")
    print(f"BOOTSTRAP: {bm['n_bootstrap_instances']} teacher-labelled instances from {bm['n_sents_parsed']} sents "
          f"({bm['n_verb_cand_tokens']} polysemous-verb tokens); by_frame={dict(list(bm['by_frame'].items())[:8])} "
          f"by_route={bm['by_route']}")
    for pop, r in m["pops"].items():
        print(f"\n[{pop}] n={r['n']} subordinate(MFS-wrong)={r['n_subordinate']} ({r['pct_subordinate']}) train={r['n_train']}")
        print(f"    {'arm':16s} {'acc':>6s} {'sub_rec':>8s} {'ovr_prec':>9s}  McNemar(b,c,p)")
        for arm in ("MFS", "CTX_SEMCOR", "CTX_BOOT", "CTX_BOOT_ONLY", "CTX_BOOT_MATCHED", "CTX_ORACLE"):
            a_ = r[arm]
            beat = "  <== beats MFS" if (a_["c_armonly"] > a_["b_mfsonly"] and (a_["override_precision"] or 0) > 0.5) else ""
            print(f"    {arm:16s} {a_['acc']:6.3f} {a_['subord_recovery']:8.3f} {str(a_['override_precision']):>9s}  "
                  f"b={a_['b_mfsonly']} c={a_['c_armonly']} p={a_['mcnemar_p']:.3f}{beat}")
    print("\nMOTION verdict detail (does scaling move SemCor-context toward the ORACLE?):")
    for mv in m["motion_verdict_detail"]:
        print(f"    {mv['pop']}: MFS={mv['mfs']} SemCor={mv['ctx_semcor']} BOOT+SemCor={mv['ctx_boot']} "
              f"(boot_only={mv['ctx_boot_only']} boot_matched={mv['ctx_boot_matched']}) ORACLE={mv['ctx_oracle']} "
              f"| improves_on_semcor={mv['boot_improves_on_semcor']} gap_closed_frac={mv['gap_closed_frac']} "
              f"beats_MFS(ovr>0.5)={mv['boot_beats_mfs_ovrprec>0.5']}")
    print("\nVERDICT:", m["verdict"])
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
