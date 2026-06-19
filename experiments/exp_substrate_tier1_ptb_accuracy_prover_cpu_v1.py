"""
exp_substrate_tier1_ptb_accuracy_prover_cpu_v1.py -- DECISION 24b PROVER check: held-out accuracy of the 3 Tier-1 integrated modules at real (non-toy) scale -- CPU/local (no heat).

ROUTING: Director DECISION 24b (Exp-Dev = Prover). Tier-1 live-query tests were TOY (3-token); validate production-quality claim on held-out data.
  PTB needs LDC; substitute UD English-EWT (public; present at experiments/data/ud_english_ewt). For NER F1 use conll2000 BIO (public; present)
  as the sequence-labeling proxy (CoNLL-2003 NER not local) -- flagged honestly.

  Modules under test (Testbed-integrated today): backend/substrate_index/hmm_decoder.py viterbi_decode (T2/viterbi_decoder),
  hdlab/perceptron.py StructuredPerceptron, backend/substrate_index/sequence_labeler.py NERTagger.

PRE-REGISTERED (Director bars): HMM POS held-out tag_acc >= 0.90; Perceptron POS held-out tag_acc >= 0.90; BIO-labeler held-out F1 >= 0.50.
  Report ACTUAL (10th rule). FAIL does NOT block ONLINE counting; flags module PRODUCTION-UNVERIFIED. UNKNOWN if data missing. Perceptron/NER
  trained on a bounded subset for tractable pure-python CPU; config (n_train, epochs) reported -- a subset-limited miss is flagged as such, not a
  module verdict. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, math
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_tier1_ptb_accuracy_prover_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
UD = REPO / "experiments" / "data" / "ud_english_ewt"


def read_conllu(path: Path) -> List[List[Tuple[str, str]]]:
    seqs = []; cur = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln:
            if cur: seqs.append(cur); cur = []
            continue
        if ln.startswith("#"): continue
        f = ln.split("\t")
        if len(f) < 4 or "-" in f[0] or "." in f[0]: continue   # skip multiword/empty tokens
        cur.append((f[1], f[3]))                                  # (form, UPOS)
    if cur: seqs.append(cur)
    return seqs


def pos_features(obs, i, tag):
    w = obs[i]; wl = w.lower()
    feats = ["w=%s|t=%s" % (wl, tag), "suf3=%s|t=%s" % (wl[-3:], tag), "suf2=%s|t=%s" % (wl[-2:], tag),
             "pre2=%s|t=%s" % (wl[:2], tag), "cap=%d|t=%s" % (int(w[:1].isupper()), tag),
             "dig=%d|t=%s" % (int(any(c.isdigit() for c in w)), tag), "hyp=%d|t=%s" % (int("-" in w), tag),
             "bos=%d|t=%s" % (int(i == 0), tag), "eos=%d|t=%s" % (int(i == len(obs) - 1), tag)]
    if i > 0: feats.append("pw=%s|t=%s" % (obs[i - 1].lower(), tag))
    return feats


def pos_transition(prev_tag, cur_tag):
    return "trans=%s>%s" % (prev_tag, cur_tag)


def hmm_train(train, smooth=0.1):
    tags = sorted({t for s in train for _, t in s}); ti = {t: i for i, t in enumerate(tags)}; T = len(tags)
    start = np.zeros(T) + smooth; trans = np.zeros((T, T)) + smooth
    emit = defaultdict(lambda: defaultdict(float)); tagc = Counter()
    for s in train:
        start[ti[s[0][1]]] += 1
        for k, (w, t) in enumerate(s):
            emit[t][w.lower()] += 1; tagc[t] += 1
            if k > 0: trans[ti[s[k - 1][1]], ti[t]] += 1
    log_start = np.log(start / start.sum())
    log_trans = np.log(trans / trans.sum(axis=1, keepdims=True))
    vocab = {w for t in emit for w in emit[t]}; V = len(vocab)
    # suffix-based OOV backoff (module doc: "morphological-suffix fallback for OOV"): P(tag | last-3-chars) from training
    suf = defaultdict(lambda: defaultdict(float)); sufc = Counter()
    for s in train:
        for w, t in s:
            sfx = w.lower()[-3:]
            suf[sfx][t] += 1; sufc[sfx] += 1
    def emit_fn(obs, tag):
        c = emit.get(tag, {}); tot = tagc.get(tag, 0); wl = obs.lower()
        cnt = c.get(wl, 0)
        if cnt > 0 or wl in vocab:
            return math.log((cnt + smooth) / (tot + smooth * (V + 1)))
        sfx = wl[-3:]                                              # OOV: back off to suffix->tag distribution
        if sfx in suf and sufc[sfx] >= 3:
            return math.log((suf[sfx].get(tag, 0.0) + smooth) / (sufc[sfx] + smooth * len(tags)))
        return math.log(smooth / (tot + smooth * (V + 1)))
    return tags, log_start, log_trans, emit_fn


def _selftest():
    toy = [[("the", "DET"), ("dog", "NOUN")], [("a", "DET"), ("cat", "NOUN")]]
    tags, ls, lt, ef = hmm_train(toy)
    assert "DET" in tags and ls.shape[0] == len(tags) and lt.shape == (len(tags), len(tags))
    assert ef("the", "DET") > ef("the", "NOUN")                  # emission learned
    assert pos_features(["A", "b"], 0, "X") and pos_transition("A", "B")
    print("[selftest] PASS: substrate_tier1_ptb_accuracy_prover_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def tag_acc(gold_seqs, pred_seqs):
    n = 0; ok = 0
    for g, p in zip(gold_seqs, pred_seqs):
        for (w, gt), pt in zip(g, p):
            n += 1; ok += int(gt == pt)
    return round(ok / n, 4) if n else 0.0


def bio_f1(gold_seqs, pred_seqs):
    """Token-level F1 over non-O labels (entity tokens), micro-averaged."""
    tp = fp = fn = 0
    for g, p in zip(gold_seqs, pred_seqs):
        for (w, gt), pt in zip(g, p):
            ge = gt != "O"; pe = pt != "O"
            if ge and pe and gt == pt: tp += 1
            elif pe and (not ge or gt != pt): fp += 1
            if ge and (not pe or gt != pt): fn += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0; rec = tp / (tp + fn) if (tp + fn) else 0.0
    return round(2 * prec * rec / (prec + rec), 4) if (prec + rec) else 0.0


def run() -> Dict:
    if not UD.exists():
        return {"error": "no_ud_data"}
    from backend.substrate_index.hmm_decoder import HMMParams, viterbi_decode
    from hdlab.perceptron import StructuredPerceptron
    smoke = (RUN_MODE == "smoke")
    train = read_conllu(UD / "en_ewt-ud-train.conllu")
    test = read_conllu(UD / "en_ewt-ud-test.conllu")
    if smoke: train = train[:200]; test = test[:50]
    n_perc_train = (300 if smoke else 5000); perc_epochs = (3 if smoke else 6)
    out = {"n_train": len(train), "n_test": len(test)}

    # 1. HMM POS (full train estimate; numpy viterbi on full test)
    tags, ls, lt, ef = hmm_train(train)
    params = HMMParams(tags=tags, log_start=ls, log_trans=lt, emit_fn=ef)
    hmm_preds = [viterbi_decode([w for w, _ in s], params) for s in test]   # list[list[tag]]
    hmm_acc = tag_acc(test, hmm_preds)
    print("  HMM POS: tag_acc=%.4f (full train=%d, test=%d sents)" % (hmm_acc, len(train), len(test)), flush=True)

    # 2. Perceptron POS (bounded subset for pure-python tractability)
    pt = train[:n_perc_train]
    ptags = sorted({t for s in pt for _, t in s})
    perc = StructuredPerceptron(tags=ptags)
    perc.fit(pt, pos_features, pos_transition, epochs=perc_epochs)
    perc_preds = [perc.predict([w for w, _ in s], pos_features, pos_transition) for s in test]
    perc_acc = tag_acc(test, perc_preds)
    print("  Perceptron POS: tag_acc=%.4f (train=%d sents x %d epochs, test=%d)" % (perc_acc, len(pt), perc_epochs, len(test)), flush=True)

    # 3. NER/BIO labeler on conll2000 chunking (public BIO proxy; CoNLL-2003 NER not local)
    bio = {"error": "no_bio_data"}
    cpath = REPO / "experiments" / "data" / "conll2000.json"
    try:
        if cpath.exists():
            from backend.substrate_index.sequence_labeler import NERTagger
            doc = json.loads(cpath.read_text(encoding="utf-8"))
            spl = doc.get("splits", doc)
            def to_seqs(rows):
                seqs = []
                for r in rows:
                    toks = r.get("tokens") or r.get("words") or []
                    labs = r.get("chunk_bio") or r.get("chunk_tags") or r.get("labels") or r.get("tags") or []
                    if toks and labs and len(toks) == len(labs):
                        seqs.append(list(zip(toks, labs)))
                return seqs
            tr = to_seqs(spl.get("train", [])); te = to_seqs(spl.get("test", []) or spl.get("dev", []))
            if not tr and isinstance(doc, list):
                pass
            if tr and te:
                if smoke: tr = tr[:200]; te = te[:50]
                else: tr = tr[:4000]
                ner = NERTagger(tag_set=sorted({l for s in tr for _, l in s}))
                ner.fit(tr, epochs=(3 if smoke else 6))
                npred = [ner.tag([w for w, _ in s]) for s in te]   # list[list[tag]]
                f1 = bio_f1(te, npred)
                bio = {"f1": f1, "n_train": len(tr), "n_test": len(te), "proxy": "conll2000_chunking"}
                print("  BIO labeler (conll2000 chunking proxy): F1=%.4f (train=%d, test=%d)" % (f1, len(tr), len(te)), flush=True)
            else:
                bio = {"error": "conll2000_unparsed_schema", "keys": list(spl.keys())[:6] if isinstance(spl, dict) else "list"}
                print("  BIO labeler: conll2000 schema unparsed (%s)" % bio.get("keys"), flush=True)
    except Exception as e:
        bio = {"error": "ner_eval_failed:" + str(e)[:80]}
        print("  BIO labeler eval failed: %s" % str(e)[:100], flush=True)

    out.update({"hmm_pos_tag_acc": hmm_acc, "perceptron_pos_tag_acc": perc_acc,
                "perceptron_train_sents": len(pt), "perceptron_epochs": perc_epochs, "bio": bio})
    return out


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    h = r["hmm_pos_tag_acc"]; p = r["perceptron_pos_tag_acc"]; bio = r["bio"]; f1 = bio.get("f1")
    hp = h >= 0.90; pp = p >= 0.90; bp = (f1 is not None and f1 >= 0.50)
    s = ("DECISION 24b Prover production-quality check (UD en_ewt POS; conll2000 BIO proxy). HMM viterbi_decode tag_acc=%.4f (bar 0.90); "
         "StructuredPerceptron tag_acc=%.4f (bar 0.90; train=%d sents x %d epochs subset); BIO labeler F1=%s (bar 0.50; %s). Report ACTUAL "
         "(10th rule); a FAIL flags PRODUCTION-UNVERIFIED, does NOT remove ONLINE counting (executes-on-live-query is separate).") % (
        h, p, r["perceptron_train_sents"], r["perceptron_epochs"], f1, bio.get("proxy", bio.get("error", "n/a")))
    n_pass = sum([hp, pp, bp])
    if n_pass == 3:
        return ("HARD_PASS", "HARD_PASS: all 3 Tier-1 modules meet the production-quality bar at held-out scale (HMM %.4f, perceptron %.4f, BIO F1 %.4f). " % (h, p, f1) + s)
    if n_pass >= 1:
        flagged = [m for m, ok in [("HMM_POS", hp), ("perceptron_POS", pp), ("BIO_F1", bp)] if not ok]
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d/3 modules meet bar; PRODUCTION-UNVERIFIED (still ONLINE-counted): %s. Perceptron may be subset/epoch-limited (pure-python; %d sents x %d ep). " % (n_pass, flagged, r["perceptron_train_sents"], r["perceptron_epochs"]) + s)
    return ("HARD_FAIL", "HARD_FAIL: 0/3 modules meet the production-quality bar at held-out scale -- the integrated modules execute but are PRODUCTION-UNVERIFIED. " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
