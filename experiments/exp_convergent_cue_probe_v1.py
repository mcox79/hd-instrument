"""PROBE (not the deliverable): can a convergent-cue readout beat the STRONGEST floor here?

The STEP-18 baseline composes entity(episodic) + meaning(ATL) by an INDEPENDENT AND (0.119). The
brief says beat that. But entity-solo (0.19) and meaning-solo (0.70) each ALREADY beat the AND, so
the AND is a straw floor -- the STRONGEST floor actually run is meaning-solo 0.70. A real
convergent-cue win (joint cue combination > best single cue) must beat meaning-solo CI-separated,
because meaning-solo IS the pure-semantic special case (episodic weight = 0) of the convergent read.

This probe extracts, per pronoun query: the episodic readback score over candidate verbs (from the
LANDED ACT-R register decode) and the ATL semantic sim over the same candidates, then sweeps the
top-down gain lambda for the Bayesian cue-combination readout softmax(epi_z + lambda*sem_z) argmax.
Reports accuracy per lambda beside entity-solo / meaning-solo / AND. Decides positive vs negative.

Run: .venv/Scripts/python.exe experiments/exp_convergent_cue_probe_v1.py [--docs N]
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
from experiments.exp_litbank_entity_tracking_end_to_end_v1 import PRONOUNS, D
from experiments.exp_composed_reader_litbank_full_v1 import build_links_landed
from experiments.exp_meaning_channel_paraphrase_comprehension_v1 import _verb_synonym
from hdlab.conceptual_meaning import ConceptualChannel
from hdlab.situation_model_accumulate import make_situation_register

SEED = 20260827


def _zn(x):
    x = np.asarray(x, float)
    s = x.std()
    return (x - x.mean()) / s if s > 1e-12 else x - x.mean()


def main():
    docs = 8
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = H.load_cache()[:docs]
    chan = ConceptualChannel()
    rng = np.random.default_rng(SEED)

    # per query: (epi_scores over cand, sem_sims over cand, idx of true verb v in cand)
    QU = []
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
        g = H._torch_gen(SEED + di * 1000 + hash("ACTR_LANDED") % 97)
        reg = make_situation_register(list(verb_vocab), D, g, max_event_slots=max(n_slots, 1),
                                      backend="multibank", n_banks=8)
        for m, cid in zip(stream, links["ACTR_LANDED"]):
            if m["gov_verb"] is not None:
                reg.add_event(str(cid), m["gov_verb"], slot_map[m["sent"]])
        anchor = H._name_anchor(stream, links["ACTR_LANDED"])
        has_name = {m["gold"] for m in stream if m["head_text"] not in PRONOUNS}
        cand_idx = {c: i for i, c in enumerate(cand)}

        for m in stream:
            v = m["gov_verb"]
            if v is None or m["gold"] not in has_name or m["head_text"] not in PRONOUNS or v not in cand:
                continue
            q = _verb_synonym(v)
            if q is None or q in cand:
                continue
            sims = [(chan.similarity(q, "V", c, "V") or -1.0) for c in cand]
            if max(sims) <= -1.0:
                continue
            E = m["gold"]; s = slot_map[m["sent"]]
            cid = anchor.get(E)
            # episodic readback scores over cand (from the LANDED register decode cleanup scores)
            epi = np.full(len(cand), -1e9)
            if cid is not None:
                try:
                    _, scores = reg.decode(str(cid), s)
                    for c in cand:
                        epi[cand_idx[c]] = scores.get(c, -1e9)
                except KeyError:
                    pass
            QU.append((epi, np.asarray(sims, float), cand_idx[v]))

    n = len(QU)
    print(f"probe: {docs} docs, {n} pronoun-paraphrase queries\n")

    # single-axis anchors
    entity_solo = np.mean([int(np.argmax(epi) == vi) for epi, _, vi in QU])
    meaning_solo = np.mean([int(np.argmax(sem) == vi) for _, sem, vi in QU])
    # independent AND (recompute in-harness): entity argmax==v AND meaning argmax==v
    and_base = np.mean([int(np.argmax(epi) == vi and np.argmax(sem) == vi) for epi, sem, vi in QU])
    print(f"  entity-solo (episodic argmax) {entity_solo:.4f}")
    print(f"  meaning-solo (semantic argmax) {meaning_solo:.4f}   <- STRONGEST FLOOR")
    print(f"  independent-AND (brief baseline) {and_base:.4f}\n")

    print("  convergent  softmax(epi_z + lambda*sem_z) argmax:")
    best = (None, -1)
    for lam in [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 100.0]:
        acc = np.mean([int(np.argmax(_zn(epi) + lam * _zn(sem)) == vi) for epi, sem, vi in QU])
        star = "  <-- beats meaning-solo" if acc > meaning_solo else ""
        print(f"    lambda={lam:6.2f}  acc={acc:.4f}{star}")
        if acc > best[1]:
            best = (lam, acc)
    print(f"\n  best convergent: lambda={best[0]} acc={best[1]:.4f}  "
          f"(meaning-solo {meaning_solo:.4f}, delta {best[1]-meaning_solo:+.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
