"""The 100k noise sweep COULD have bitten -- I expected the opposite, and the result is stronger.

THE ROW. `data/cell4_results/metrics.json` (`substrate_hp12_v2_100k_pseudoinverse_v1`):

    recall@1 = 1.0000 at 100,000 facts, HARD_PASS
    recall_by_noise = {0.05: 1.0, 0.1: 1.0, 0.2: 1.0, 0.5: 1.0}

`ORGAN_MAP.md` flags it as one of two capacity results with **NO FLOOR AT ALL** -- "no random-key
arm, no scramble, no decoy -- and a noise sweep 0.05-0.5 that returns 1.0 at every level, i.e. **the
sweep never bit**". *(The other of those two was floored on 2026-08-23 and TIED with a dictionary,
which is why I came looking here.)*

**I EXPECTED TO SHOW THE SWEEP WAS UNINFORMATIVE. IT IS NOT.** A plain random-key baseline -- no
pseudoinverse, no PCA whitening, no padding, none of the machinery the verdict credits -- **BREAKS
INSIDE the swept range**: `0.9520` at noise `0.2` and `0.1580` at noise `0.5`, where the landed
system held `1.0000` at both.

➡️ **SO ORGAN_MAP'S "THE SWEEP NEVER BIT" IS WRONG, AND WRONG AGAINST THE SYSTEM. The range CAN
bite; it did not bite THIS system.** That is a fact about the system, not about the sweep.

⚠️ **THE CAVEAT THAT KEEPS IT HONEST: `noise_std` IS NOT SCALE-FREE.** My keys are unit-normalised,
so std `0.5` per dimension is enormous relative to the signal. If the cell added noise at a different
scale -- pre-normalisation, or relative to embedding magnitude -- **the two arms did not face the
same difficulty.** This establishes that the RANGE is capable of discriminating; it does NOT
establish that both arms were equally stressed. Settling that needs the cell's noise code.

📐 **WHAT STANDS REGARDLESS OF ALL THAT, and is the reframing worth carrying:**

    n_fragments             128
    per_fragment_capacity   819
    in_fragment_retrieval   "exhaustive (HNSW informational only; ~819 keys is fast)"

**"100,000 facts, recall@1 = 1.0" is 128 INDEPENDENT EXHAUSTIVE SCANS OF ~819 ITEMS EACH**, not one
100,000-way retrieval. It is in the record and it is not what the headline conveys.

    .venv/Scripts/python.exe verification/test_the_100k_noise_sweep_bites_and_the_system_survives_it.py
"""
import io
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDED = os.path.join(REPO, "data", "cell4_results", "metrics.json")

D = 2048                 # n_per_fragment_dim, from the record
KEYS = 819               # per_fragment_capacity, from the record
QUERIES = 1000           # n_queries, from the record
SWEPT = (0.05, 0.1, 0.2, 0.5)
EXTENDED = (1.0, 2.0, 4.0, 8.0, 16.0)


def recall_at_1(noise_std, rng, d=D, n=KEYS, q=QUERIES):
    """Exhaustive nearest-neighbour over one fragment of `n` random keys, query = key + noise."""
    keys = rng.normal(size=(n, d))
    keys /= np.linalg.norm(keys, axis=1, keepdims=True)
    idx = rng.integers(0, n, size=q)
    probes = keys[idx] + rng.normal(scale=noise_std, size=(q, d))
    probes /= np.linalg.norm(probes, axis=1, keepdims=True)
    return float((np.argmax(probes @ keys.T, axis=1) == idx).mean())


def main():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        print("[witness] %-56s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        ok = ok and bool(cond)

    landed = json.load(io.open(LANDED, encoding="utf-8"))
    print("[witness] LANDED: %s" % landed["verdict_msg"])
    print("[witness]   n_fragments=%s  per_fragment_capacity=%s  retrieval=%r"
          % (landed["n_fragments"], landed["per_fragment_capacity"],
             landed["in_fragment_retrieval"]))
    chk("retrieval really is EXHAUSTIVE within a fragment",
        "exhaustive" in str(landed["in_fragment_retrieval"]).lower())
    chk("the fragment is ~819 keys, not 100,000",
        int(landed["per_fragment_capacity"]) < 2000,
        "(%s)" % landed["per_fragment_capacity"])

    rng = np.random.default_rng(7)
    print()
    print("[witness] PLAIN RANDOM KEYS, exhaustive search, %d keys x %d dims -- NO pseudoinverse,"
          % (KEYS, D))
    print("[witness] NO PCA whitening, NO padding. The range the cell actually swept:")
    swept = {}
    for s in SWEPT:
        swept[s] = recall_at_1(s, rng)
        print("[witness]    noise_std %-5s  recall@1 %.4f   (landed: %.4f)"
              % (s, swept[s], landed["recall_by_noise"][str(s)]))

    # 🔻 I EXPECTED THIS TO PASS. IT FAILS, AND THAT IS THE FINDING.
    # The premise was that 0.05-0.5 could not break anything, so the sweep was uninformative. The
    # plain random baseline BREAKS INSIDE THAT RANGE -- 0.9520 at 0.2 and 0.1580 at 0.5 -- while the
    # landed system held 1.0000 at both. So the range CAN bite; it did not bite THE REAL SYSTEM.
    all_perfect = all(v >= 0.999 for v in swept.values())
    chk("(EXPECTED, AND REFUTED) the swept range breaks nothing", not all_perfect,
        "-- it DOES break the baseline: %.4f at 0.5" % swept[0.5])

    print()
    print("[witness] WHERE IT ACTUALLY BREAKS -- extending the sweep until it bites:")
    broke_at = None
    for s in EXTENDED:
        r = recall_at_1(s, rng)
        print("[witness]    noise_std %-5s  recall@1 %.4f" % (s, r))
        if broke_at is None and r < 0.99:
            broke_at = s
    chk("it DOES break eventually (so the instrument works)", broke_at is not None,
        "(first drop at noise_std %s)" % broke_at)

    print()
    print("[witness] WHAT THIS SHOWS:")
    print("  🔻 I SET OUT TO SHOW THE SWEEP WAS UNINFORMATIVE. IT IS NOT, AND THE RESULT IS")
    print("     STRONGER THAN ORGAN_MAP CREDITS. A plain random baseline with NONE of the machinery")
    print("     the verdict credits -- no pseudoinverse, no PCA, no padding -- BREAKS INSIDE the")
    print("     swept range: %.4f at noise 0.2 and %.4f at noise 0.5, where the landed system held"
          % (swept[0.2], swept[0.5]))
    print("     1.0000 at both. So the range CAN bite. It did not bite THE REAL SYSTEM.")
    print("     ➡️ ORGAN_MAP's \"the sweep never bit\" should read \"the sweep did not bite THIS")
    print("        system\" -- which is a fact about the system, not about the sweep.")
    print()
    print("  ⚠️  THE CAVEAT THAT KEEPS THIS HONEST: noise_std is not scale-free. My keys are")
    print("     unit-normalised, so std 0.5 per dimension is enormous relative to the signal. If")
    print("     the cell added noise at a different scale (pre-normalisation, or relative to")
    print("     embedding magnitude), the two arms did not face the same difficulty. **This")
    print("     establishes that the RANGE is capable of discriminating, NOT that the two arms")
    print("     were equally stressed.** Settling that needs the cell's noise code, not this file.")
    print()
    print("  📐 WHAT STANDS REGARDLESS: the headline needs its mechanism beside it. '100,000 facts,")
    print("     recall@1=1.0' is 128 INDEPENDENT EXHAUSTIVE SCANS OF ~819 ITEMS, not one")
    print("     100,000-way lookup. That is in the record and is not what the headline conveys.")
    print("[witness] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
