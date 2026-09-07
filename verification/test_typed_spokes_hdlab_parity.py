"""Parity witness: the PROMOTED organ hdlab/typed_spokes reproduces the SOLVED experiment cells' key numbers,
byte-faithfully, on is-a / entails / part-whole / instrument / antonym / natural-logic reads. Writes nothing;
deterministic. Proves the C5/C6/C7 landing did not drift from the reference behavior the witness
verification/test_world_knowledge_typed_spokes.py holds (which imports the cells directly).

  P1  C5 is_a per-item AGREES with exp_isa_typed_spoke_monli_v1.isa_mfs_fn over the MoNLI vocab
  P2  C5 entails() reproduces the MoNLI directed-entailment accuracy (0.817) exactly
  P3  C5 negation subset via entails() reproduces the cell's monotonicity accuracy
  P4  C6 part_whole_score() reproduces the covered part-whole TYPED arm (0.926) within float16 tolerance
  P5  C6 part_whole_score(instrument) reproduces the covered instrument TYPED arm (0.828)
  P6  C7 antonym() recognizes EVERY hub-filtered ConceptNet antonym pair the cell uses
  P7  natural-logic is_downward() byte-matches the MED cell on every sentence1
  P8  natural_logic_label() byte-matches the MED cell per item

Run: .venv/Scripts/python.exe verification/test_typed_spokes_hdlab_parity.py
"""
from __future__ import annotations
import os
import sys
import pickle

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.typed_spokes as TS
import experiments.exp_isa_typed_spoke_monli_v1 as ISA
import experiments.exp_partwhole_typed_spoke_bridging_v1 as PW
import experiments.exp_antonym_typed_spoke_valence_v1 as ANT
import experiments.exp_natural_logic_monotonicity_med_v1 as NL

PASS = []


def chk(name, cond, detail=""):
    PASS.append(bool(cond))
    print(("  PASS " if cond else "  FAIL ") + name + ("  :: " + detail if detail else ""))


def main():
    print("parity witness: hdlab/typed_spokes vs the SOLVED experiment cells\n")

    # -- C5 is-a / entails on MoNLI --
    pm = ISA.load_monli("pmonli.jsonl")
    nt = ISA.load_monli("nmonli_test.jsonl")
    combined = pm + nt
    dis = sum(1 for r in combined for (a, b) in
              [(r["sentence1_lex"], r["sentence2_lex"]), (r["sentence2_lex"], r["sentence1_lex"])]
              if TS.is_a(a, b) != ISA.isa_mfs_fn(a, b))
    chk("P1 C5 is_a agrees with cell isa_mfs_fn on MoNLI vocab", dis == 0,
        "disagreements=%d/%d" % (dis, 2 * len(combined)))

    def judge_organ(items):
        ok = []
        for r in items:
            neg = ISA.has_neg(r["sentence1"])
            pred = "entailment" if TS.entails(r["sentence1_lex"], r["sentence2_lex"], negated=neg) else "neutral"
            ok.append(int(pred == r["gold_label"]))
        return np.array(ok, float)

    acc_org = float(judge_organ(combined).mean())
    acc_cell = float(ISA.judge(combined, ISA.isa_mfs_fn).mean())
    chk("P2 C5 entails reproduces MoNLI accuracy (ref 0.817)", abs(acc_org - acc_cell) < 1e-9,
        "organ=%.4f cell=%.4f" % (acc_org, acc_cell))
    mono_org = float(judge_organ(nt).mean())
    chk("P3 C5 negation subset via entails matches cell mono", abs(mono_org - float(ISA.judge(nt, ISA.isa_mfs_fn).mean())) < 1e-9,
        "organ-neg=%.4f" % mono_org)

    # -- C6 part-whole / instrument: reproduce the confusable-indomain TYPED arm via the organ --
    hub = pickle.load(open(PW.HUB_PATH, "rb"))["hub"]
    K = PW.K_DISTRACT

    def eval_typed_via_organ(source, family, seed=0):
        from nltk.corpus import wordnet as wn
        if source == "part_cn":
            gold_pairs = sorted({(s, o) for s, o in PW._load_cn("PartOf") if s in hub and o in hub and s != o})
        else:
            def is_art(w):
                ss = wn.synsets(w, pos="n")
                return any(x.lexname() in ("noun.artifact", "noun.object") for x in ss[:3])
            gold_pairs = sorted({(s, o) for s, o in PW._load_cn("UsedFor")
                                 if s in hub and o in hub and s != o and is_art(s)})
        U = {w: PW.unit(hub[w]) for w in hub}
        ante_pool = sorted({o for _, o in gold_pairs})
        rng = np.random.default_rng(seed)
        ok = []
        for (t, gold) in gold_pairs:
            if t not in U:
                continue
            tv = U[t]
            sims = sorted(((float(tv @ U[c]), c) for c in ante_pool if c != gold and c != t and c in U), reverse=True)
            cands = [gold] + [c for _, c in sims[:K]]
            rng.shuffle(cands)
            gi = cands.index(gold)
            sp = [TS.part_whole_score(t, c, family=family) for c in cands]
            ok.append(int(np.argmax(sp) == gi) if max(sp) > -9.0 else 1.0 / len(cands))
        return float(np.mean(ok)), len(ok)

    for source, family, pid, ref in (("part_cn", "part", "P4", 0.926), ("instrument", "instrument", "P5", 0.828)):
        acc, n = eval_typed_via_organ(source, family)
        conf_in = PW.eval_bridging(source, hub, PW.build_mfnd(), confusable=True, held_out=False, seed=0)
        cell_acc = float(conf_in["TYPED_directed_spoke"].mean())
        chk("%s C6 [%s] part_whole_score reproduces the cell TYPED arm (float16)" % (pid, source),
            abs(acc - cell_acc) < 0.02, "organ=%.4f cell=%.4f (ref %.3f) n=%d" % (acc, cell_acc, ref, n))

    # -- C7 antonym: organ recognizes every hub-filtered ConceptNet antonym the cell uses --
    cell_ant = ANT.load_antonyms(hub)
    miss = sum(1 for a, b in cell_ant if not TS.antonym(a, b))
    chk("P6 C7 antonym recognizes all cell (hub-filtered) ConceptNet antonym pairs", miss == 0,
        "missed=%d/%d ; hot/cold=%s good/bad=%s hot/warm=%s"
        % (miss, len(cell_ant), TS.antonym("hot", "cold"), TS.antonym("good", "bad"), TS.antonym("hot", "warm")))

    # -- natural logic: organ byte-matches the MED cell --
    rows = NL.load_med()
    dw = sum(1 for r in rows if TS.is_downward(r["sentence1"]) != NL.is_downward(r["sentence1"]))
    chk("P7 NL is_downward byte-matches MED cell on sentence1", dw == 0, "disagreements=%d/%d" % (dw, len(rows)))
    lab_dis = 0
    for r in rows:
        k, w1, w2 = NL.classify_edit(r["sentence1"], r["sentence2"])
        cell = NL.nat_logic_pred(k, w1, w2, NL.is_downward(r["sentence1"]))
        if cell != TS.natural_logic_label(r["sentence1"], r["sentence2"]):
            lab_dis += 1
    chk("P8 NL natural_logic_label byte-matches MED cell per item", lab_dis == 0,
        "disagreements=%d/%d" % (lab_dis, len(rows)))

    n = sum(PASS)
    print("\n%d/%d parity checks PASS" % (n, len(PASS)))
    sys.exit(0 if n == len(PASS) else 1)


if __name__ == "__main__":
    main()
