"""exp_coref_abstain_downstream_whodidwhat_v1 -- Track B, item (c): a confidence-gated ABSTAIN on the
graded pronoun-binding posterior, CONSUMED by a downstream organ, makes it DEGRADE GRACEFULLY instead of
silently inheriting a wrong link.

THE BRAIN (frame): reference resolution outputs a maintained DISTRIBUTION over candidate antecedents
(Levy 2008; Swets et al. 2008); when cues conflict the retrieval posterior is FLAT (similarity-based /
retrieval interference -- Van Dyke & McElree 2006), and a flat posterior is the brain-faithful signal to
DEFER rather than commit. Here the confidence currency is the NORMALIZED ENTROPY of the softmax-over-ACT-R
binding posterior (the same graded-competition difficulty currency the parser uses; PINNED).

THE DOWNSTREAM ORGAN (already landed): hdlab.situation_model_accumulate -- each entity's FHRR register
accumulates bind(gov_verb, event-slot); decode(entity, slot) recovers what that entity DID (Zwaan event
indexing; Kintsch C-I). A pronoun-contributed event is retrievable from the entity's NAME anchor ONLY if the
pronoun was correctly bound into that thread. A WRONG binding pollutes the register with a foreign event.

ARMS (identical mention stream, identical events; only the pronoun-BINDING gate differs):
  COMMIT   : bind EVERY pronoun to its posterior argmax (the current default -- silently inherits errors).
  ABSTAIN  : bind a pronoun ONLY if its binding entropy <= theta (chosen on a DEV split); high-entropy
             pronouns are DEFERRED (not bound -> their event is left unattributed rather than mis-attributed).
  RAND_TWIN: defer the SAME NUMBER of pronouns, chosen at RANDOM (info-free twin: must NOT raise kept acc).

METRIC = governing-verb decode accuracy on the pronoun-contributed queries that were ANSWERED (not deferred),
bootstrap over DOCUMENTS. Graceful degradation = ABSTAIN answers FEWER queries but the answered ones are MORE
accurate than COMMIT's full set, CI-separated; RAND_TWIN at the same coverage does NOT achieve this.

Run: .venv/Scripts/python.exe experiments/exp_coref_abstain_downstream_whodidwhat_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_abstain_downstream_whodidwhat_v1.py --run
Reads the pre-parsed cache; imports the landed situation register. NO hdlab/ write.
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, ROLE_W, _gn_compat, _dt  # noqa: E402
from experiments.exp_litbank_entity_tracking_end_to_end_v1 import (  # noqa: E402
    _slots, _name_anchor, _torch_gen, D,
)

CACHE = os.path.join(REPO_ROOT, "data", "litbank", "who_did_what_events.json")
SEED = 20260828
DECAY_D = 2.0


def load_streams(docs: Optional[int] = None) -> List[Dict]:
    with open(CACHE, encoding="utf-8") as fh:
        recs = json.load(fh)
    return recs[:docs] if docs else recs


def _actr(hist, p_sent, d):
    s = sum(ROLE_W.get(r, 1.0) * (_dt(p_sent, sent) ** (-d)) for sent, r in hist)
    return math.log(s) if s > 0 else -1e9


def _norm_entropy(w: np.ndarray) -> float:
    n = len(w)
    if n <= 1:
        return 0.0
    return float(-(w * np.log(w + 1e-12)).sum() / math.log(n))


def bind_with_entropy(stream, d):
    """Process mentions in order; PRONOUNS get a softmax-over-ACT-R posterior over gn-compatible entities
    (the graded binding, argmax = hard pick). Returns per-mention (pred_cluster, binding_entropy) with
    entropy=0.0 for names and no-competition pronouns. Names cluster by head-token overlap (as in the
    landed end-to-end cell)."""
    STOP = frozenset({"the", "a", "an", "his", "her", "its", "their", "this", "that", "of", "and",
                      "mr", "mrs", "miss"})
    tbl = []   # {tokens, gender, number, hist:[(sent,role)]}
    pred, ent = [], []
    for m in stream:
        ht = m["head_text"]; role = m["role"]
        if ht in PRONOUNS:
            pg, pn = PRONOUNS[ht]
            compat = [i for i, e in enumerate(tbl)
                      if e["hist"] and _gn_compat(pg, pn, e["gender"], e["number"])]
            if not compat:
                tbl.append({"tokens": set(), "gender": pg, "number": pn, "hist": [(m["sent"], role)]})
                pred.append(len(tbl) - 1); ent.append(0.0); continue
            acts = np.array([_actr(tbl[i]["hist"], m["sent"], d) for i in compat])
            z = acts - acts.max(); w = np.exp(z); w = w / w.sum()
            best = compat[int(np.argmax(acts))]
            pred.append(best); ent.append(_norm_entropy(w))
            tbl[best]["hist"].append((m["sent"], role))
            if tbl[best]["gender"] is None: tbl[best]["gender"] = pg
            if tbl[best]["number"] is None: tbl[best]["number"] = pn
        else:
            toks = {ht} - STOP - {""}
            b, bo = None, 0.0
            for i, e in enumerate(tbl):
                if not e["tokens"]:
                    continue
                ov = len(toks & e["tokens"]) / len(toks | e["tokens"]) if toks else 0.0
                if ov > bo:
                    bo, b = ov, i
            if b is not None and bo > 0.0:
                pred.append(b); ent.append(0.0); tbl[b]["tokens"] |= toks
                tbl[b]["hist"].append((m["sent"], role))
            else:
                tbl.append({"tokens": set(toks), "gender": None, "number": "s",
                            "hist": [(m["sent"], role)]})
                pred.append(len(tbl) - 1); ent.append(0.0)
    return pred, ent


def _deferred_set(stream, ent, theta, mode, rng):
    pron_idx = [i for i, m in enumerate(stream) if m["head_text"] in PRONOUNS]
    if mode == "ABSTAIN":
        return {i for i in pron_idx if ent[i] > theta}
    if mode == "RAND":
        n_def = sum(1 for i in pron_idx if ent[i] > theta)
        if n_def and pron_idx:
            return set(rng.choice(pron_idx, size=min(n_def, len(pron_idx)), replace=False).tolist())
    return set()


def _decode_doc(stream, pred, ent, theta, mode, rng, gen_seed, backend="direct"):
    """Score pronoun-contributed who-did-what queries under a binding gate. mode in {COMMIT,ABSTAIN,RAND}.
    Returns list of (answered:bool, correct:bool). Deferred pronoun events are UNBOUND -> query unanswered.

    backend="direct": a LINK-BOTTLENECKED consumer -- per predicted-cluster a symbolic slot->verb tally
      (no capacity loss). Isolates whether the downstream inherits link correctness.
    backend="fhrr": the LANDED situation_model_accumulate FHRR register (superposed; capacity-limited)."""
    slot_map, n_slots = _slots(stream)
    verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
    if not verb_vocab:
        return []
    deferred = _deferred_set(stream, ent, theta, mode, rng)
    anchor = _name_anchor(stream, pred)
    has_name = {m["gold"] for m in stream if m["head_text"] not in PRONOUNS}
    if backend == "fhrr":
        import torch
        from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax
        from hdlab import binding
        gen = _torch_gen(gen_seed)
        verb_vec = {v: unit_phase_vec(D, gen) for v in verb_vocab}
        slot_vec = [unit_phase_vec(D, gen) for _ in range(max(n_slots, 1))]
        reg = defaultdict(lambda: torch.zeros(D, dtype=torch.complex64))
        for idx, m in enumerate(stream):
            v = m["gov_verb"]
            if v is None or idx in deferred:
                continue
            reg[pred[idx]] = reg[pred[idx]] + binding.bind(verb_vec[v], slot_vec[slot_map[m["sent"]]])

        def decode(cid, s):
            acc = reg.get(cid)
            if acc is None:
                return None
            best, _ = cleanup_argmax(binding.unbind(acc, slot_vec[s]), verb_vec)
            return best
    else:  # direct symbolic tally
        reg = defaultdict(lambda: defaultdict(Counter))   # cid -> slot -> Counter(verb)
        for idx, m in enumerate(stream):
            v = m["gov_verb"]
            if v is None or idx in deferred:
                continue
            reg[pred[idx]][slot_map[m["sent"]]][v] += 1

        def decode(cid, s):
            slots = reg.get(cid)
            if not slots or s not in slots:
                return None
            return slots[s].most_common(1)[0][0]

    out = []
    for idx, m in enumerate(stream):
        v = m["gov_verb"]
        if v is None or m["head_text"] not in PRONOUNS or m["gold"] not in has_name:
            continue
        answered = idx not in deferred
        ok = 0
        if answered:
            cid = anchor.get(m["gold"])
            if cid is not None:
                ok = int(decode(cid, slot_map[m["sent"]]) == v)
        out.append((answered, bool(ok)))
    return out


def cell(docs: Optional[int] = None, n_boot: int = 2000, target_abstain: float = 0.30,
         seed: int = SEED) -> Dict:
    streams = load_streams(docs)
    # DEV/TEST split by doc (same convention as exp1): pick theta on DEV, report on TEST
    names = sorted(rec["doc"] for rec in streams)
    dev_docs = set(names[0::2]); test_docs = set(names[1::2])
    # collect pronoun binding entropies on DEV to set theta
    dev_ent = []
    binds = {}
    for rec in streams:
        pred, ent = bind_with_entropy(rec["stream"], DECAY_D)
        binds[rec["doc"]] = (rec["stream"], pred, ent)
        if rec["doc"] in dev_docs:
            dev_ent += [e for i, e in enumerate(ent)
                        if rec["stream"][i]["head_text"] in PRONOUNS and e > 0.0]
    theta = float(np.quantile(np.array(dev_ent), 1.0 - target_abstain)) if dev_ent else 0.0

    def run_backend(backend):
        rng = np.random.default_rng(seed)
        per_doc = {m: defaultdict(lambda: [0, 0]) for m in ("COMMIT", "ABSTAIN", "RAND")}
        cov = {m: defaultdict(lambda: [0, 0]) for m in ("COMMIT", "ABSTAIN", "RAND")}
        for di, name in enumerate(sorted(test_docs)):
            stream, pred, ent = binds[name]
            for mode in ("COMMIT", "ABSTAIN", "RAND"):
                res = _decode_doc(stream, pred, ent, theta, mode, rng, seed + di, backend=backend)
                for answered, ok in res:
                    cov[mode][name][1] += 1
                    if answered:
                        cov[mode][name][0] += 1
                        per_doc[mode][name][0] += int(ok); per_doc[mode][name][1] += 1
        return per_doc, cov

    def ci(pairs, s):
        arr = np.array([v for v in pairs.values()], float)
        tot = arr[:, 1].sum(); acc = arr[:, 0].sum() / tot if tot else 0.0
        r = np.random.default_rng(s); nd = len(arr); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd); c, n = arr[idx, 0].sum(), arr[idx, 1].sum()
            boots.append(c / n if n else 0.0)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(tot)}

    def paired(a, b, s):
        docs_ = sorted(set(a) & set(b))
        A = np.array([a[d] for d in docs_], float); B = np.array([b[d] for d in docs_], float)
        delta = A[:, 0].sum() / max(A[:, 1].sum(), 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)
        r = np.random.default_rng(s); nd = len(docs_); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd)
            boots.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1) - B[idx, 0].sum() / max(B[idx, 1].sum(), 1))
        boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                "half_width": round(float(hi - lo) / 2, 4),
                "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    def coverage(cov, m):
        arr = np.array([v for v in cov[m].values()], float)
        return round(arr[:, 0].sum() / max(arr[:, 1].sum(), 1), 4)

    def summarize(backend, s0):
        per_doc, cov = run_backend(backend)
        return {
            "answered_acc": {m: ci(per_doc[m], s0 + i) for i, m in enumerate(("COMMIT", "ABSTAIN", "RAND"))},
            "coverage": {m: coverage(cov, m) for m in ("COMMIT", "ABSTAIN", "RAND")},
            # graceful degradation: ABSTAIN answered-acc beats COMMIT full-acc CI-separated
            "ABSTAIN_minus_COMMIT_answered": paired(per_doc["ABSTAIN"], per_doc["COMMIT"], s0 + 30),
            # info-free twin: RANDOM deferral at matched coverage does NOT beat COMMIT
            "RAND_minus_COMMIT_answered": paired(per_doc["RAND"], per_doc["COMMIT"], s0 + 31),
            # the flag beats an equally-selective random deferral
            "ABSTAIN_minus_RAND_answered": paired(per_doc["ABSTAIN"], per_doc["RAND"], s0 + 32),
        }

    return {
        "anchor": "coref_abstain_downstream_whodidwhat_v1",
        "downstream_task": "governing_verb decode of a pronoun's referent (who-did-what)",
        "entropy_theta": round(theta, 4), "target_abstain": target_abstain,
        "n_test_docs": len(test_docs),
        # PRIMARY: a link-bottlenecked consumer INHERITS the flag -> graceful degradation
        "direct_link_bottlenecked": summarize("direct", seed + 100),
        # ADJACENCY MAP: the landed FHRR register is CAPACITY-bottlenecked (fan effect), so the flag does
        # NOT move it -- register capacity is the separate addressed-storage problem, not link correctness.
        "fhrr_capacity_bottlenecked": summarize("fhrr", seed + 200),
    }


def self_test():
    """Fixture: 'she'@s4 is unambiguous (only Alice is fem) -> low entropy; a truly ambiguous later
    pronoun would be high entropy. Assert bind_with_entropy: names carry entropy 0, an unambiguous
    (single-compatible) pronoun carries entropy 0, and a 2-way-compatible pronoun carries entropy > 0."""
    stream = [
        {"sent": 0, "gold": 0, "role": "SUBJECT", "head_text": "alice", "gov_verb": "leave"},
        {"sent": 1, "gold": 0, "role": "SUBJECT", "head_text": "she", "gov_verb": "wait"},
        {"sent": 2, "gold": 1, "role": "SUBJECT", "head_text": "mary", "gov_verb": "run"},
        {"sent": 3, "gold": 1, "role": "SUBJECT", "head_text": "she", "gov_verb": "shout"},
        {"sent": 4, "gold": 0, "role": "SUBJECT", "head_text": "she", "gov_verb": "sing"},
    ]
    pred, ent = bind_with_entropy(stream, DECAY_D)
    assert ent[0] == 0.0 and ent[2] == 0.0, "name mentions carry entropy 0"
    assert ent[1] == 0.0, "first 'she' has a single compatible entity -> entropy 0"
    assert ent[4] > 0.0, "'she'@s4 competes between Alice and Mary -> entropy > 0"
    print(f"SELF-TEST PASS (name ent={ent[0]}, unambiguous-pron ent={ent[1]}, "
          f"competitive-pron ent={round(ent[4], 3)})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        print(json.dumps(cell(docs=args.docs, n_boot=args.n_boot), indent=2))
        return
    print("use --self-test | --run [--docs N]")


if __name__ == "__main__":
    main()
