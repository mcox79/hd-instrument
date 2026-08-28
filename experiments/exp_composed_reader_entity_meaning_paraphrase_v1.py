"""CONSOLIDATION headline (part 1): do the ENTITY and MEANING organs COMPOSE end-to-end, not just work in isolation?

The three axes are each validated on their OWN gold (front-end 0.739 STEP-9; entity 0.184 STEP-13; meaning 0.750
STEP-14). This composes TWO of them on ONE cross-sentence task: answer a PARAPHRASED who-did-what question about a
PRONOUN-LINKED entity. Correct requires BOTH:
  (a) ENTITY: the pronoun was linked to the right character so the register decode returns that entity's verb
      (`hdlab.salience_binder` -- the landed ACT-R + Centering binder), AND
  (b) MEANING: the paraphrase cue is recognised as that verb (`hdlab.conceptual_meaning` -- the landed ATL channel);
      exact word-matching structurally cannot ("what did X PURSUE?" when the story said "chased").

Per pronoun query (entity E, slot s, true verb v), q = a WordNet synonym of v that is NOT a doc candidate string:
  pred_verb = reg.decode(anchor[E], s)          # entity-tracked retrieval (depends on the BIND arm)
  a_meaning = argmax_c conceptual_sim(q, c)      # meaning retrieval over doc candidate verbs (bind-independent)
  ok = int(pred_verb == v  AND  a_meaning == v)  # STRICT 2-axis conjunction

ARMS (the one variable is which axis is crippled):
  * FULL        : ACT-R binder  + meaning decode  -> both organs ON (the composed reader).
  * ENTITY_OFF  : string-identity binder + meaning decode -> entity axis crippled (isolates entity's contribution).
  * MEANING_OFF : ACT-R binder  + EXACT decode (a_exact = q if q in cand else None) -> meaning crippled; ~0 on paraphrase.
  * TWIN        : shuffled binder + meaning decode -> info-free binding control -> must lose to FULL.
FULL must beat ENTITY_OFF (entity axis load-bearing) AND MEANING_OFF (meaning axis load-bearing), both CI-separated,
with TWIN losing -> the two organs COMPOSE. (p2 refines the register STORE + scalar-magnitude refines ADJECTIVE meaning;
both apply to all arms equally / target a different read, so this baseline is a one-swap re-run when they land.)

Run:  .venv/Scripts/python.exe experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py [--docs N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H
from experiments.exp_litbank_entity_tracking_end_to_end_v1 import PRONOUNS, D, DECAY_D
from experiments.exp_composed_reader_litbank_full_v1 import build_links_landed
from experiments.exp_meaning_channel_paraphrase_comprehension_v1 import _verb_synonym
from hdlab.conceptual_meaning import ConceptualChannel
from hdlab.situation_model_accumulate import make_situation_register

SEED = 20260827
BIND = {"FULL": "ACTR_LANDED", "ENTITY_OFF": "STRING_IDENTITY", "MEANING_OFF": "ACTR_LANDED", "TWIN": "SHUFFLED_TWIN"}
ARMS = ["FULL", "ENTITY_OFF", "MEANING_OFF", "TWIN"]


def _register(stream, pred, verb_vocab, slot_map, n_slots, gtorch):
    reg = make_situation_register(list(verb_vocab), D, gtorch, max_event_slots=max(n_slots, 1),
                                  backend="multibank", n_banks=8)
    for m, cid in zip(stream, pred):
        if m["gov_verb"] is not None:
            reg.add_event(str(cid), m["gov_verb"], slot_map[m["sent"]])
    return reg


def _decode(reg, cid, slot):
    try:
        pv, _ = reg.decode(str(cid), slot)
        return pv
    except KeyError:
        return None


def main():
    docs = 60
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = H.load_cache()[:docs]
    chan = ConceptualChannel()
    rng = np.random.default_rng(SEED)

    per_doc = {a: [] for a in ARMS}   # (correct, n) per doc
    meaning_solo, entity_solo = [], []  # per-query bind-independent / meaning-independent single-axis rates
    for di, rec in enumerate(recs):
        stream = rec["stream"]
        if not stream:
            continue
        slot_map, n_slots = H._slots(stream)
        verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
        cand = [v for v in verb_vocab if v.isalpha() and len(v) >= 3]
        if len(cand) < 3:
            continue
        links = build_links_landed(stream, rng)
        # one register per BIND arm (ACTR_LANDED, STRING_IDENTITY, SHUFFLED_TWIN)
        regs, anchors = {}, {}
        for bind_arm in set(BIND.values()):
            g = H._torch_gen(SEED + di * 1000 + hash(bind_arm) % 97)
            regs[bind_arm] = _register(stream, links[bind_arm], verb_vocab, slot_map, n_slots, g)
            anchors[bind_arm] = H._name_anchor(stream, links[bind_arm])
        has_name = {m["gold"] for m in stream if m["head_text"] not in PRONOUNS}

        dc = {a: [0, 0] for a in ARMS}
        for m in stream:
            v = m["gov_verb"]
            if v is None or m["gold"] not in has_name:
                continue
            if m["head_text"] not in PRONOUNS:           # PRONOUN-contributed queries: where binding is decisive
                continue
            if v not in cand:
                continue
            q = _verb_synonym(v)
            if q is None or q in cand:                    # a TRUE paraphrase: a synonym NOT already a doc string
                continue
            sims = [(chan.similarity(q, "V", c, "V") or -1.0) for c in cand]
            if max(sims) <= -1.0:
                continue
            a_meaning = cand[int(np.argmax(sims))]
            a_exact = q if q in cand else None            # exact retrieval on the paraphrase -> None by construction
            E = m["gold"]; s = slot_map[m["sent"]]
            meaning_solo.append(int(a_meaning == v))
            pv_actr = _decode(regs["ACTR_LANDED"], anchors["ACTR_LANDED"].get(E), s) if anchors["ACTR_LANDED"].get(E) is not None else None
            entity_solo.append(int(pv_actr == v))
            for a in ARMS:
                bind_arm = BIND[a]
                cid = anchors[bind_arm].get(E)
                pv = _decode(regs[bind_arm], cid, s) if cid is not None else None
                ans = a_exact if a == "MEANING_OFF" else a_meaning
                dc[a][0] += int(pv == v and ans == v)
                dc[a][1] += 1
        for a in ARMS:
            if dc[a][1]:
                per_doc[a].append((dc[a][0], dc[a][1]))

    def acc_ci(pairs, s):
        arr = np.array(pairs, float); r = np.random.default_rng(s); nd = len(arr)
        tot = arr[:, 1].sum(); acc = arr[:, 0].sum() / tot if tot else 0.0
        b = []
        for _ in range(2000):
            idx = r.integers(0, nd, nd); b.append(arr[idx, 0].sum() / max(arr[idx, 1].sum(), 1))
        return acc, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    def paired(a_pairs, b_pairs, s):
        a = np.array(a_pairs, float); b = np.array(b_pairs, float); r = np.random.default_rng(s); nd = len(a)
        d = []
        for _ in range(2000):
            idx = r.integers(0, nd, nd)
            d.append(a[idx, 0].sum() / max(a[idx, 1].sum(), 1) - b[idx, 0].sum() / max(b[idx, 1].sum(), 1))
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        return {"delta": round(float(a[:, 0].sum() / max(a[:, 1].sum(), 1) - b[:, 0].sum() / max(b[:, 1].sum(), 1)), 4),
                "ci": [round(lo, 4), round(hi, 4)], "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    n_docs = len(per_doc["FULL"]); n_q = int(np.array(per_doc["FULL"])[:, 1].sum()) if n_docs else 0
    print(f"=== COMPOSED READER: ENTITY x MEANING on paraphrased cross-sentence who-did-what "
          f"(LitBank, {n_docs} docs, {n_q} pronoun queries) ===")
    print(f"  single-axis (context): meaning-solo {np.mean(meaning_solo):.4f}  entity-solo(ACT-R) {np.mean(entity_solo):.4f}\n")
    for a in ARMS:
        if per_doc[a]:
            acc, lo, hi = acc_ci(per_doc[a], SEED + ARMS.index(a))
            print(f"  {a:12s} {acc:.4f}  CI[{lo:.4f},{hi:.4f}]")
    print()
    checks = []
    d1 = paired(per_doc["FULL"], per_doc["MEANING_OFF"], SEED + 10)
    checks.append(("MEANING axis load-bearing: FULL beats MEANING_OFF (exact) CI-sep", d1["band"] == "ABOVE", d1))
    d2 = paired(per_doc["FULL"], per_doc["ENTITY_OFF"], SEED + 11)
    checks.append(("ENTITY axis load-bearing: FULL beats ENTITY_OFF (string-identity) CI-sep", d2["band"] == "ABOVE", d2))
    d3 = paired(per_doc["FULL"], per_doc["TWIN"], SEED + 12)
    checks.append(("info-free shuffled-binding TWIN loses to FULL CI-sep", d3["band"] == "ABOVE", d3))
    ok = True
    for name, passed, detail in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {detail}")
        ok = ok and passed
    print(f"\n{'BOTH AXES COMPOSE -- entity binding AND conceptual meaning each earn their keep in the SAME reader' if ok else 'COMPOSITION INCOMPLETE -- see failing check'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
