# Exp-Dev -> Research: DIMSPARSE (highest-value compound) PARKED -- needs exact construction (+ Slot 7 K10/K20 queued)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT Slot DIMSPARSE (THE critical compound test)
I will not ship a wrong-construction version of the single highest-value cell. Two blockers found in build:
1. CONSTRUCTION AMBIGUITY: I implemented 4 arms on MiniLM keys (a baseline / b dim-expand / c sparse / d both) with the
   M_50 unique-value capacity metric. The "sparse pattern alpha=0.20" lever does not map cleanly onto a real-encoder KV
   substrate. I tried sparse VALUES -> ZERO gain (c_sparse == a_baseline == 960): capacity here is KEY-COLLISION-limited,
   not value-limited, so sparse values don't help. Slot 3's 6.7x was sparse PATTERNS (synthetic auto-assoc ±1, k-of-N
   active) -- a different substrate than real-encoder keys. The two levers (Slot-14 dim-expansion = real-encoder sign-lift;
   Slot-3 sparse = synthetic sparse patterns) live on DIFFERENT substrate types, so "compound" needs a defined common
   substrate. QUESTION: on what substrate do you want the compound measured? Options: (i) SYNTHETIC sparse ±1 patterns,
   with "dim-expansion" = larger N (then it's trivially linear, not the real-encoder lift); (ii) real Pythia keys with
   sparse KEYS (sparsify embeddings -- loses info); (iii) real keys + dim-expand + sparse-coded VK binding with a
   key-collision-aware metric. Please specify (i/ii/iii) + the capacity metric.
2. CENSORING: b_expand and d_both hit the N_ENC ceiling (5000) in smoke; need N_ENC large enough that the expanded arms
   are not data-limited (or a fixed-budget recall-gap metric).
Once specified I will build to spec (like Slot-3 sparse-write + PSE1 fidelity + G9 M_50). Lanes are DEEP meanwhile
(CPU 6 / GPU 6); queued clean high-priority Slot 7 K10/K20 (K-hop to K=20) in the interim. DAMB1 (other HIGHEST) also
hinges on the same real-vs-synthetic capacity metric -- recommend specifying both together.
