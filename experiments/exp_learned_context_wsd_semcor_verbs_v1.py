#!/usr/bin/env python
# -*- coding: ascii -*-
# CELL-TEMPLATE MANDATORY (subset applicable to a LOCAL foreground analysis cell):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - baseline_in_band checked at smoke (META_RULE_AG; 0.05 < MFS < 0.95)
# - HARD_PASS strictly above floor + margin (pre-reg bands)
# - NO python hash()-seed / list(set()) nondeterminism (F.5); np.random.RandomState + sorted
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ in the pre-reg
# - crlb_n/a declared (no HD noise floor; supervised-classifier metric)
# - real_code_path N/A: no substrate KGStore/fit objects; numpy + nltk only.
#
# Learned glass-box contextual WSD vs MFS on SemCor verbs.
# Model = Naive Bayes over specific context content-words. It DECOMPOSES exactly:
#   score(sense) = log P(sense|lemma)  [PRIOR == the frequency signal]
#                + sum_w log P(w|sense,lemma)  [CONTEXT == the orthogonal signal]
# context-OFF (prior only) == supervised MFS baseline; context-ON == learned model.
# Pre-reg: preregs/2026-07-22_learned_context_wsd_semcor_verbs_v1.md

import os, sys, json, time, argparse, platform, traceback, collections
from datetime import datetime, timezone
import numpy as np

ANCHOR_NAME = "learned_context_wsd_semcor_verbs_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20260722
MIN_COUNT = 10          # min instances per polysemous lemma
TEST_FRAC = 0.30        # per-lemma held-out fraction
ALPHA = 0.1             # add-alpha smoothing on P(w|sense)
MIN_EV = 2              # min train co-occurrence count for a word to vote (hapax-noise cutoff)
WINDOW = 10             # bag-of-words content window (+/- tokens around the verb span)
LC_FRACTIONS = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
N_BOOT = 1000

# Basic glass-box stopword list (function words; explicit, inspectable).
STOP = set("""a an the of to in on at for and or but if then than that this these those
with without within from into onto over under again further here there when where why how
all any both each few more most other some such no nor not only own same so too very
is are was were be been being have has had having do does did doing would should could can
will shall may might must ought i you he she it we they them him her his hers its our their
my your me us as by up down out off no yes about above below between through during before
after because while about which who whom whose what one two three said say says get got go
went going come came make made take took see saw know knew think thought day time year man
men people way thing things much many well also just now new like back even still way""".split())


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": (type(exc).__name__ + ": " + str(exc)[:400]),
            "summary": "CELL_CRASHED: " + type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": _now_iso(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------
def _featurize(flat, start, end):
    """SPECIFIC context features for a verb span [start:end) in token list flat.
    Positional collocations (the dominant WSD cue: L1/L2/R1/R2, incl. function
    words) + a bag of content words within +/- WINDOW tokens. Prefixed so the
    feature space is inspectable/glass-box."""
    feats = []
    n = len(flat)
    def tok(i):
        return flat[i].lower() if 0 <= i < n and isinstance(flat[i], str) else None
    l1, l2 = tok(start - 1), tok(start - 2)
    r1, r2 = tok(end), tok(end + 1)
    if l1 and l1.isalpha():
        feats.append("L1:" + l1)
    if l2 and l2.isalpha():
        feats.append("L2:" + l2)
    if r1 and r1.isalpha():
        feats.append("R1:" + r1)
    if r2 and r2.isalpha():
        feats.append("R2:" + r2)
    lo, hi = max(0, start - WINDOW), min(n, end + WINDOW)
    for i in range(lo, hi):
        if start <= i < end:
            continue
        w = tok(i)
        if w is None or not w.isalpha() or len(w) < 3 or w in STOP:
            continue
        feats.append("BAG:" + w)
    return feats


def extract_instances(max_files=None):
    """Return list of (lemma, gold_synset_name, tuple(specific_features)) for sense-tagged verbs."""
    from nltk.corpus import semcor
    inst = []
    files = semcor.fileids()
    if max_files is not None:
        files = files[:max_files]
    for fn in files:
        try:
            sents = semcor.tagged_sents(fn, tag='sem')
        except Exception as e:  # specific: corpus-file parse failure; record + skip this file only
            sys.stderr.write("WARN semcor file %s parse fail: %s\n" % (fn, type(e).__name__))
            continue
        for s in sents:
            flat = []
            spans = []  # (lemma, syn, start, end)
            for chunk in s:
                leaves = chunk.leaves() if hasattr(chunk, 'leaves') else [chunk]
                strs = [w for w in leaves if isinstance(w, str)]
                start = len(flat)
                flat.extend(strs)
                end = len(flat)
                lbl = getattr(chunk, 'label', None)
                if lbl is None:
                    continue
                lab = chunk.label()
                if hasattr(lab, 'synset'):
                    syn = lab.synset()
                    if syn is not None and syn.pos() == 'v':
                        spans.append((lab.name(), syn.name(), start, end))
            for lemma, syn, start, end in spans:
                feats = _featurize(flat, start, end)
                inst.append((lemma, syn, tuple(feats)))
    return inst


def filter_polysemous(inst, min_count):
    bylemma = collections.defaultdict(collections.Counter)
    for lemma, syn, ctx in inst:
        bylemma[lemma][syn] += 1
    keep = set(l for l, c in bylemma.items() if len(c) >= 2 and sum(c.values()) >= min_count)
    return [(l, s, c) for (l, s, c) in inst if l in keep], keep


def split_train_test(inst, test_frac, seed):
    """Per-lemma stratified split. Deterministic: sorted order + RandomState (no python hash)."""
    rng = np.random.RandomState(seed)
    bylemma = collections.defaultdict(list)
    # stable sorted order of instances so the split is reproducible across processes
    for idx, rec in enumerate(inst):
        bylemma[rec[0]].append(idx)
    train, test = [], []
    for lemma in sorted(bylemma.keys()):
        idxs = sorted(bylemma[lemma])
        perm = rng.permutation(len(idxs))
        n_test = max(1, int(round(len(idxs) * test_frac)))
        # ensure at least 1 train instance too
        if n_test >= len(idxs):
            n_test = len(idxs) - 1
        test_local = set(perm[:n_test].tolist())
        for j, gi in enumerate(idxs):
            (test if j in test_local else train).append(inst[gi])
    return train, test


# ---------------------------------------------------------------------------
# Naive Bayes WSD model (glass-box)
# ---------------------------------------------------------------------------
def _supersense_map():
    from nltk.corpus import wordnet as wn
    cache = {}
    def mp(word):
        if word in cache:
            return cache[word]
        ss = wn.synsets(word)
        val = ss[0].lexname() if ss else None
        cache[word] = val
        return val
    return mp


class NBModel:
    """Per-lemma Naive Bayes. Weights = plain dicts -> glass-box / inspectable."""
    def __init__(self, alpha=ALPHA, min_ev=MIN_EV):
        self.alpha = alpha
        self.min_ev = min_ev
        self.prior = {}       # lemma -> {sense: count}
        self.wcount = {}      # lemma -> {sense: dict(word->count)}
        self.wtot = {}        # lemma -> {sense: total word tokens}
        self.vocab = {}       # lemma -> set(words seen for lemma)
        self.bg = {}          # lemma -> dict(word -> total count across senses)
        self.bgtot = {}       # lemma -> total context tokens for lemma

    def fit(self, train, transform=None):
        prior = collections.defaultdict(collections.Counter)
        wcount = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
        vocab = collections.defaultdict(set)
        bg = collections.defaultdict(collections.Counter)
        for lemma, syn, ctx in train:
            prior[lemma][syn] += 1
            feats = transform(ctx) if transform is not None else ctx
            for w in feats:
                wcount[lemma][syn][w] += 1
                vocab[lemma].add(w)
                bg[lemma][w] += 1
        self.prior = {l: dict(c) for l, c in prior.items()}
        self.wcount = {l: {s: dict(cc) for s, cc in d.items()} for l, d in wcount.items()}
        self.wtot = {l: {s: sum(cc.values()) for s, cc in d.items()} for l, d in wcount.items()}
        self.vocab = {l: v for l, v in vocab.items()}
        self.bg = {l: dict(c) for l, c in bg.items()}
        self.bgtot = {l: float(sum(c.values())) for l, c in bg.items()}

    def mfs(self, lemma):
        c = self.prior.get(lemma)
        if not c:
            return None
        return max(sorted(c.keys()), key=lambda s: c[s])

    def predict(self, lemma, ctx, use_context, transform=None):
        # score(s) = log P(s|lemma)  [PRIOR == MFS/frequency signal]
        #          + sum_{w in ctx, c(w,s)>=min_ev} log[ P(w|s) / Pbg(w) ]  [POSITIVE-EVIDENCE PMI]
        # Only context words that actually co-occurred with sense s in training vote for s;
        # the prior anchors the score so context cannot systematically drift below MFS.
        c = self.prior.get(lemma)
        if not c:
            return None
        senses = sorted(c.keys())
        total = float(sum(c.values()))
        V = max(1, len(self.vocab.get(lemma, ())))
        bg = self.bg.get(lemma, {})
        bgtot = self.bgtot.get(lemma, 0.0)
        feats = (transform(ctx) if transform is not None else ctx) if use_context else ()
        best_s, best_score = None, None
        for s in senses:
            score = np.log(c[s] / total)  # prior term == frequency signal
            if use_context:
                wc = self.wcount.get(lemma, {}).get(s, {})
                wt = self.wtot.get(lemma, {}).get(s, 0)
                for w in feats:
                    cws = wc.get(w, 0)
                    if cws < self.min_ev:
                        continue  # OOV-for-sense or hapax: no positive evidence
                    p_ws = (cws + self.alpha) / (wt + self.alpha * V)
                    p_bg = (bg.get(w, 0) + self.alpha) / (bgtot + self.alpha * V)
                    score += np.log(p_ws / p_bg)
            if best_score is None or score > best_score:
                best_score, best_s = score, s
        return best_s


def evaluate(model, test, use_context, transform=None):
    preds = []
    gold = []
    for lemma, syn, ctx in test:
        p = model.predict(lemma, ctx, use_context=use_context, transform=transform)
        preds.append(p)
        gold.append(syn)
    corr = np.array([1 if p == g else 0 for p, g in zip(preds, gold)], dtype=np.int32)
    return corr, preds


def mcnemar(corr_a, corr_b):
    b = int(np.sum((corr_a == 0) & (corr_b == 1)))  # A wrong, B right
    c = int(np.sum((corr_a == 1) & (corr_b == 0)))  # A right, B wrong
    if b + c == 0:
        return {"b": b, "c": c, "chi2": 0.0, "p": 1.0}
    chi2 = (abs(b - c) - 1.0) ** 2 / (b + c)
    # survival of chi2 with 1 dof
    from math import erfc, sqrt
    p = erfc(sqrt(chi2 / 2.0)) if chi2 > 0 else 1.0
    return {"b": b, "c": c, "chi2": float(chi2), "p": float(p)}


def bootstrap_delta_ci(corr_a, corr_b, n_boot, seed):
    rng = np.random.RandomState(seed)
    n = len(corr_a)
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.randint(0, n, n)
        deltas[i] = corr_b[idx].mean() - corr_a[idx].mean()
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return float(lo), float(hi)


def scramble_train(train, seed):
    """Permute context bags across TRAIN instances; keep (lemma,sense) labels.
    Preserves per-lemma sense marginals (the prior/MFS) exactly; destroys the
    word<->sense co-occurrence that context-ON exploits."""
    rng = np.random.RandomState(seed)
    ctxs = [rec[2] for rec in train]
    perm = rng.permutation(len(ctxs))
    return [(train[i][0], train[i][1], ctxs[perm[i]]) for i in range(len(train))]


def glassbox_dump(model, lemmas, topk=5):
    """Top log-likelihood-ratio context words per sense for example lemmas."""
    out = {}
    for lemma in lemmas:
        c = model.prior.get(lemma)
        if not c or len(c) < 2:
            continue
        V = max(1, len(model.vocab.get(lemma, ())))
        senses = sorted(c.keys())
        # background word prob across all senses of the lemma
        bg = collections.Counter()
        bgtot = 0
        for s in senses:
            for w, k in model.wcount.get(lemma, {}).get(s, {}).items():
                bg[w] += k
                bgtot += k
        lem_out = {}
        for s in senses:
            wc = model.wcount.get(lemma, {}).get(s, {})
            wt = model.wtot.get(lemma, {}).get(s, 0)
            denom = wt + model.alpha * V
            scored = []
            for w, k in wc.items():
                p_ws = (k + model.alpha) / denom
                p_bg = (bg[w] + model.alpha) / (bgtot + model.alpha * V)
                llr = float(np.log(p_ws / p_bg))
                scored.append((w, round(llr, 3), int(k)))
            scored.sort(key=lambda t: -t[1])
            lem_out[s] = scored[:topk]
        out[lemma] = lem_out
    return out


# ---------------------------------------------------------------------------
# Self-test: NB math + McNemar on a tiny synthetic set (no nltk needed)
# ---------------------------------------------------------------------------
def self_test():
    # Two senses of "bank": context {river,water} -> bank.river ; {money,loan} -> bank.money
    tr = []
    for _ in range(20):
        tr.append(("bank", "riverside", ("river", "water", "flow")))
        tr.append(("bank", "finance", ("money", "loan", "cash")))
    # make finance slightly more frequent so MFS predicts finance
    for _ in range(6):
        tr.append(("bank", "finance", ("money", "deposit")))
    te = [("bank", "riverside", ("river", "water")),
          ("bank", "finance", ("loan", "cash")),
          ("bank", "riverside", ("water", "flow")),
          ("bank", "finance", ("money", "deposit"))]
    m = NBModel()
    m.fit(tr)
    assert m.mfs("bank") == "finance", "MFS should be the more frequent sense"
    corr_off, _ = evaluate(m, te, use_context=False)
    corr_on, _ = evaluate(m, te, use_context=True)
    acc_off = corr_off.mean()
    acc_on = corr_on.mean()
    assert acc_off == 0.5, "MFS on balanced test = 0.5, got %s" % acc_off
    assert acc_on == 1.0, "context must resolve all 4, got %s" % acc_on
    # scramble must destroy the context signal -> collapse toward MFS
    sc = scramble_train(tr, seed=1)
    ms = NBModel(); ms.fit(sc)
    corr_sc, _ = evaluate(ms, te, use_context=True)
    assert corr_sc.mean() <= 0.75, "scramble should NOT resolve senses, got %s" % corr_sc.mean()
    # mcnemar sanity
    mc = mcnemar(corr_off, corr_on)
    assert mc["b"] == 2 and mc["c"] == 0, "mcnemar b/c wrong: %s" % mc
    # arms-must-differ
    import hashlib
    hoff = hashlib.sha256(corr_off.tobytes()).hexdigest()
    hon = hashlib.sha256(corr_on.tobytes()).hexdigest()
    assert hoff != hon, "arms bit-identical"
    print("[self-test] PASS: MFS=0.5 context=1.0 scramble<=0.75 mcnemar b=2 c=0 arms-differ")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(smoke=False):
    t0 = time.perf_counter()
    suffix = "_smoke" if smoke else ""
    output_dir = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    run_mode = "smoke" if smoke else "full"
    _write_start_marker(output_dir, run_mode, expected_n_units=4)

    print("[%s] extracting SemCor verb instances..." % run_mode)
    inst = extract_instances(max_files=25 if smoke else None)
    inst, kept = filter_polysemous(inst, MIN_COUNT if not smoke else 5)
    print("  instances=%d polysemous_lemmas=%d" % (len(inst), len(kept)))

    train, test = split_train_test(inst, TEST_FRAC, SEED)
    print("  train=%d test=%d" % (len(train), len(test)))

    ss_map = _supersense_map()
    def coarse_transform(feats):
        # fixed-TYPE reference: map bag content words to their WordNet supersense
        # bucket (reproduces the fixed supersense-typing gate in-cell).
        out = []
        for f in feats:
            if f.startswith("BAG:"):
                v = ss_map(f[4:])
                if v is not None:
                    out.append("SS:" + v)
        return out

    # --- fit models ---
    m = NBModel()
    m.fit(train)

    # Arm A (MFS / context OFF) and Arm B (learned context ON), full train
    corr_a, _ = evaluate(m, test, use_context=False)
    corr_b, _ = evaluate(m, test, use_context=True)
    acc_a = float(corr_a.mean())
    acc_b = float(corr_b.mean())

    # train-set accuracy for memorization check (evaluate B on TRAIN)
    corr_b_train, _ = evaluate(m, train, use_context=True)
    corr_a_train, _ = evaluate(m, train, use_context=False)
    acc_b_train = float(corr_b_train.mean())
    acc_a_train = float(corr_a_train.mean())

    # Arm C (fixed-coarse supersense typing)
    mc_model = NBModel()
    mc_model.fit(train, transform=coarse_transform)
    corr_c, _ = evaluate(mc_model, test, use_context=True, transform=coarse_transform)
    acc_c = float(corr_c.mean())

    # Arm D (scramble must-fail)
    scr = scramble_train(train, seed=SEED + 7)
    md = NBModel()
    md.fit(scr)
    corr_d, _ = evaluate(md, test, use_context=True)
    acc_d = float(corr_d.mean())

    # --- significance ---
    mc = mcnemar(corr_a, corr_b)
    ci_lo, ci_hi = bootstrap_delta_ci(corr_a, corr_b, N_BOOT if not smoke else 200, SEED + 3)

    lift = acc_b - acc_a
    lift_train = acc_b_train - acc_a_train
    scramble_lift = acc_d - acc_a
    coarse_lift = acc_c - acc_a

    # --- stratify by per-lemma TRAIN data density (is the null a thin-data artifact?) ---
    lemma_train_ct = {l: int(sum(d.values())) for l, d in m.prior.items()}
    test_tc = np.array([lemma_train_ct.get(rec[0], 0) for rec in test])
    strata = {}
    for label, lo, hi in [("all", 0, 10**9), ("ge35", 35, 10**9),
                          ("ge75", 75, 10**9), ("ge150", 150, 10**9)]:
        mask = (test_tc >= lo) & (test_tc < hi)
        n = int(mask.sum())
        if n == 0:
            continue
        a = float(corr_a[mask].mean()); b = float(corr_b[mask].mean())
        mcm = mcnemar(corr_a[mask], corr_b[mask])
        strata[label] = {"n": n, "acc_mfs": a, "acc_learned": b,
                         "lift": b - a, "mcnemar_p": mcm["p"], "mcnemar_chi2": mcm["chi2"]}

    # --- learning curve ---
    rng = np.random.RandomState(SEED + 11)
    train_sorted = list(train)
    perm = rng.permutation(len(train_sorted))
    lc = []
    for frac in LC_FRACTIONS:
        n = max(1, int(round(len(train_sorted) * frac)))
        sub = [train_sorted[perm[i]] for i in range(n)]
        mm = NBModel(); mm.fit(sub)
        cb, _ = evaluate(mm, test, use_context=True)
        ca, _ = evaluate(mm, test, use_context=False)
        lc.append({"frac": frac, "n_train": n,
                   "acc_context_on": float(cb.mean()), "acc_mfs": float(ca.mean())})
    lc_rise = lc[-1]["acc_context_on"] - lc[0]["acc_context_on"]

    # --- glass-box dump ---
    # pick 2 high-count polysemous lemmas present in train
    lemma_counts = collections.Counter(rec[0] for rec in train)
    example_lemmas = [l for l, _ in lemma_counts.most_common(6)
                      if len(m.prior.get(l, {})) >= 2][:2]
    gb = glassbox_dump(m, example_lemmas)
    weights_are_plain_dict = isinstance(m.wcount, dict)

    # --- arms-must-differ (META_RULE_AF) ---
    import hashlib
    digs = {"A_MFS": hashlib.sha256(corr_a.tobytes()).hexdigest(),
            "B_LEARNED": hashlib.sha256(corr_b.tobytes()).hexdigest(),
            "C_COARSE": hashlib.sha256(corr_c.tobytes()).hexdigest(),
            "D_SCRAMBLE": hashlib.sha256(corr_d.tobytes()).hexdigest()}
    arms_differ = len(set(digs.values())) == len(digs)

    # --- baseline in band (META_RULE_AG) ---
    baseline_in_band = 0.05 < acc_a < 0.95

    # --- verdict (pre-reg bands) ---
    hard_pass = (lift >= 0.03 and mc["p"] < 0.01 and lc_rise >= 0.02
                 and scramble_lift <= 0.01 and coarse_lift < 0.5 * lift)
    invalid_scramble = scramble_lift >= 0.5 * lift and lift > 0
    memorized = (acc_b_train - acc_b > 0.15) and lift < 0.01
    hard_fail = (lift <= 0 or mc["p"] > 0.05) or invalid_scramble or memorized
    middle = (mc["p"] < 0.05 and lift < 0.03) or (lift >= 0.03 and lc_rise < 0.02)

    if hard_pass:
        verdict, tier = "HARD_PASS", "MEASURED_MECHANISM"
    elif hard_fail:
        verdict, tier = "HARD_FAIL", ("INVALID" if (invalid_scramble or memorized) else "HONEST_NULL")
    elif middle:
        verdict, tier = "MIDDLE_BAND", "MIDDLE_BAND"
    else:
        verdict, tier = "MIDDLE_BAND", "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    vmsg = ("acc MFS=%.4f learned=%.4f lift=%+.4f (95%%CI [%.4f,%.4f]) McNemar chi2=%.1f p=%.2e | "
            "coarse=%.4f (lift %+.4f) scramble=%.4f (lift %+.4f) | LC rise=%+.4f | "
            "train_lift=%+.4f arms_differ=%s baseline_in_band=%s" %
            (acc_a, acc_b, lift, ci_lo, ci_hi, mc["chi2"], mc["p"],
             acc_c, coarse_lift, acc_d, scramble_lift, lc_rise, lift_train,
             arms_differ, baseline_in_band))

    metrics = {
        "verdict": verdict, "tier": tier, "verdict_msg": vmsg,
        "summary": "learned-context WSD vs MFS on SemCor verbs: " + verdict,
        "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "regime": {"n_instances": len(inst), "n_polysemous_lemmas": len(kept),
                   "n_train": len(train), "n_test": len(test),
                   "min_count": MIN_COUNT if not smoke else 5, "test_frac": TEST_FRAC,
                   "alpha": ALPHA, "seed": SEED},
        "arms": {
            "A_MFS": {"acc": acc_a, "note": "context OFF = argmax P(sense|lemma) = supervised MFS"},
            "B_LEARNED": {"acc": acc_b, "note": "context ON = NB specific context tokens"},
            "C_FIXED_COARSE": {"acc": acc_c, "note": "NB over WordNet supersense buckets (fixed type)"},
            "D_SCRAMBLE": {"acc": acc_d, "note": "must-fail: train context bags permuted"},
        },
        "lift": lift, "lift_train": lift_train, "coarse_lift": coarse_lift,
        "scramble_lift": scramble_lift,
        "mcnemar": mc, "delta_ci95": [ci_lo, ci_hi],
        "data_density_strata": strata,
        "learning_curve": lc, "lc_rise_full_minus_10pct": lc_rise,
        "memorization_check": {"acc_train_context_on": acc_b_train,
                               "acc_test_context_on": acc_b,
                               "train_minus_test": acc_b_train - acc_b},
        "glassbox": {"weights_are_plain_dict": weights_are_plain_dict,
                     "example_lemmas": example_lemmas,
                     "top_llr_context_words_per_sense": gb},
        "discipline": {"arms_differ_verified": arms_differ,
                       "baseline_in_band": baseline_in_band,
                       "final_metrics_atomicity": "tmp_replace",
                       "nondeterminism_guard": "RandomState+sorted; no python hash()",
                       "crlb_n_a": "supervised-classifier metric; feasibility set by MFS headroom"},
        "prereg": "preregs/2026-07-22_learned_context_wsd_semcor_verbs_v1.md",
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[%s] VERDICT %s (%s)" % (run_mode, verdict, tier))
    print("  " + vmsg)
    print("  metrics -> %s" % os.path.join(output_dir, "metrics.json"))
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.smoke:
        run(smoke=True)
        return
    if args.full:
        run(smoke=False)
        return
    # default: self-test only (safe)
    self_test()


if __name__ == "__main__":
    _out = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out, e)
        raise
