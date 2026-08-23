---
problem: flat_store_destroys_the_code
status: REFUTED
bar: A read-out on the LIVE reading path that uses addressed storage instead of the flat sum, and beats the strongest floor CI-separated on HELD-OUT text.
result: addressed-storage held-out identity-recovery hit@1 = 0.1399 [0.1310,0.1494] (exemplar-max read-out over n=5490 candidate lemmas / 5490 held-out simplewiki queries, live reading path) is CI-separated BELOW the strongest floor; the bar is NOT met. Its headline strength is exact-key 0.9954 [0.9936,0.9971] which collapses to 0.1399 held-out (failure mode c). It DOES beat the flat sum on held-out (+0.0554 [+0.0457,+0.0656]) but that is not a capability win.
floor: first-order co-occurrence COUNTING (F_COUNT1) held-out hit@1 = 0.3242 [0.3115,0.3366] on the IDENTICAL population; addressed is -0.1843 [-0.1978,-0.1701] BELOW it (CI excludes 0). Corroborated on disk: exp_substrate_end_to_end_readout_v1 COOC_floor 0.02 beats episodic 0.0044 and semantic 0.0056 held-out; exp_cortical_read_consolidated_v1 COOC_floor 0.0867 beats cortical 0.0567 and episodic 0.0.
controls: (a) SCRAMBLE-CONTENT twin (donor cue, gold unchanged) -> addressed 0.0000 and flat 0.0000, removed 0 items (destroys the cue's CONTENT, collapses both to zero); (b) INFO-FREE addressed (random +/-1 episodes, same count/grouping) -> held-out 0.0000, exact 0.0005, removed 0 items (must-lose, satisfied); (c) ABLATION addressed->flat = -0.0554 [-0.0656,-0.0457] (addressing DOES move the score vs flat, but both are far below the floor); (d) POSITIVE CONTROL 2AFC self-retrieval 0.7433 >= 0.70 (instrument valid); (e) EXACT-vs-HELD-OUT diagnostic 0.9954 -> 0.1399 (the isolation win is exact-key memorization, not held-out capability); argmax tie density <= 0.87% (immaterial).
files_changed: experiments/exp_flat_vs_addressed_identity_recovery_livepath_v1.py, verification/verify_bundling_destroys_flat_sum.py, notes/problems/flat_store_destroys_the_code/DESIGN.md, data/exp_flat_vs_addressed_identity_recovery_livepath_v1/metrics.json
reverify: cd d:/AI/hd-instrument && .venv/Scripts/python.exe tools/reproduce.py exp_flat_vs_addressed_identity_recovery_livepath_v1  # SAFE FORM (2026-08-23). The ORIGINAL command re-ran the cell IN PLACE; I followed it and it rewrote the landed metrics.json's ts_iso and elapsed_s (science byte-identical; record restored from git). Re-verified numbers: held-out 0.1399 [0.1310,0.1494] vs counting floor 0.3242, exact-key 0.9954.
---

## What the brief asked, and the answer

The brief: the reading loop "adds each word's pattern into one running total per concept" (a flat
sum -- "mixing paint"), and a store that keeps a label on every item (addressed / episodic) would
"pull the red back out." **Fix proposed: stop adding into one bucket, use the addressed store, and
show the win survives on the real reading task.**

**Refuted as a route to a capability win.** Wiring in the addressed store does beat the flat sum on
held-out text, but it loses DECISIVELY to plain co-occurrence counting -- the strongest floor the bar
requires -- and its headline strength is exact-key memorization that collapses under the partial cues
real reading provides. Addressing is not the lever; the levers are upstream (meaning supply, Phase 1)
and code FORMAT (a sparse code, Phase 1), not addressed storage (Phase 3).

## What was built

1. **`experiments/exp_flat_vs_addressed_identity_recovery_livepath_v1.py`** -- the decisive,
   non-duplicative measurement: open-vocabulary IDENTITY RECOVERY ("pull the red back out") on the
   live reading path (reuses the validated C3 harness: corpus, 80/20 profile/held-out split,
   `context_vector_masked` cues, `paired_bootstrap`). Three arms on the IDENTICAL candidate set
   (n=5490 lemmas), gold, and n:
   - **A_FLAT** -- prototype: `ConceptSpace`-style raw sum of a lemma's context vectors (the incumbent).
   - **A_ADDRESSED** -- exemplar: keep EVERY encounter as a labelled episode (92,908 episodes),
     score each lemma by its best-matching episode. This is the CA3-completion / hippocampal
     read-out with NO discrete-codebook collision -- i.e. the FAIR re-test the plan flagged as
     pending (Phase 4: "our completer implementation is refuted at smoke, with a handicap we
     introduced ... a fair re-test pending").
   - **F_COUNT1 / F_COUNT2** -- the floor: explicit first/second-order PMI co-occurrence profiles
     (the validated `prof()` math from `tools/measure_counting_floors_through_the_harness.py`).
   Measured at EXACT-KEY (in-store cue) and HELD-OUT (novel cue), with a scramble-content twin, an
   info-free addressed arm, the addressed->flat ablation, a 2AFC self-retrieval positive control, and
   a tie-density report.
2. **`verification/verify_bundling_destroys_flat_sum.py`** -- discharges the brief's "check the
   `6.93 of 7 bits` claim FIRST" mandate.

## What was measured (full run, n=5490 candidates, self-retrieval 0.7433 >= 0.70 so the instrument is valid)

| arm | HELD-OUT hit@1 | EXACT-KEY hit@1 |
|---|---|---|
| **F_COUNT1 (counting floor, strongest)** | **0.3242 [0.3115,0.3366]** | -- |
| A_ADDRESSED (exemplar / episodic) | 0.1399 [0.1310,0.1494] | **0.9954** |
| A_FLAT (prototype / incumbent) | 0.0845 [0.0774,0.0918] | 0.3707 |
| F_COUNT2 (2nd-order counting) | 0.0046 | 0.0084 |
| chance (1/5490) | 0.00018 | -- |

- **The bar is not met:** addressed held-out (0.1399) is CI-separated BELOW the counting floor's
  upper bound (0.3366); the delta is -0.1843 [-0.1978,-0.1701], CI excludes zero.
- **Addressed beats flat on held-out** (+0.0554 [+0.0457,+0.0656]) -- so the brief's WITHIN-SUBSTRATE
  mechanism claim ("keep every item" > "one average") holds, and the fair exemplar is ~32x the prior
  handicapped episodic route (0.0044). This is a real sub-finding, not a capability win.
- **Addressed's power is exact-key MEMORIZATION** (0.9954) that collapses to 0.1399 under the partial
  cue of held-out reading -- the on-disk 0.9333/0.0044 "memorises but does not transfer" signature,
  reproduced on the clean, un-handicapped store. Failure mode (c): an exact-key win is not progress.

## Prior work this builds on and credits (disk-verified this session, not relayed)

The head-to-head was ALREADY answered twice; my cell confirms and extends it by removing the handicap:
- **`exp_substrate_end_to_end_readout_v1`**: EPISODIC (addressed) exact 0.9333 / held 0.0044; SEMANTIC
  (flat-sum) held 0.0056; COOC_floor 0.02 (strongest, beats both). Written up in
  `notes/brain_fidelity_drill_memorises_but_does_not_transfer_2026-08-19.md`.
- **`exp_cortical_read_consolidated_v1`**: flat-sum CORTICAL 0.0567 vs addressed EPISODIC 0.0
  (flat-sum CI-separated ABOVE addressed, perm p=0.0005); COOC_floor 0.0867 beats both at every k.
- **`exp_structured_code_vs_flat_bag_c3_v1`** -> `STRUCTURE_HURTS` (-0.0113 [-0.0195,-0.0030]): the
  one prior cell that connected a structured/addressed code to the real read-out; it lost.
- **The three isolation proofs** (`1.000 vs 0.003`, `1.000 vs 0.273`, `1.0 vs 0.06`) are SYNTHETIC
  mechanism-proofs; their own notes say "not chain-grade capability, real-text build still required."
  They reproduce here as the EXACT-KEY column (addressed 0.9954) and do not survive the partial cue.

## Disk-outranks-brief corrections (the disk won; stated per the protocol)

- **`6.93 of 7 bits` is a PHANTOM** -- absent from data/, experiments/, notes/, preregs/. The
  phenomenon is real: the incumbent flat-store code retains 0.8744/7 bits through the sum (loses
  ~6.13), a sparse graded code (C1_KCAP) retains 3.5264/7 (4.03x), C4_PHASOR dies at 0.0097/7
  (validated ruler `exp_meaning_lift_population_code_v1`, disk-verified). Independent computation
  (`verify_bundling_destroys_flat_sum.py`): summing near-ORTHOGONAL codes is loss-free, so the loss
  is a GEOMETRY property (matching the brief's own words), and **the survivable-superposition lever
  is CODE FORMAT, a Phase-1 change -- NOT addressed storage.**
- **The `use_index` "O(1) index is off on the live path" framing is imprecise.** `hdlab/substrate.py`
  constructs `HDFactStore(use_index=True)`, and the two index paths are byte-equivalent
  (`_selftest_index_equivalence`) -- a pure performance toggle, not a capability lever. The real
  defect is narrower and true: the reading loop's MEANING vector lives in the flat `ConceptSpace`
  sum; `HDFactStore.store` is used only as a side ledger of discrete canonical-sense labels, and no
  scored capability cell calls `HDFactStore.query`.
- **`LONG_TERM_PLAN` Phase 3 (this problem) is "BLOCKED UNTIL PHASE 1 CLEARS"** and Phase 1 has not
  cleared. The plan's supply-before-architecture diagnosis predicts exactly this: a storage change is
  "a better filing system for empty folders" while the codes carry no meaning. The result is
  consistent with that ordering.

## Brain-faithfulness (the honest framing)

This is the complementary-learning-systems dissociation, run on the real reading task: **hippocampal
exemplar** (keep every episode, addressed) vs **cortical prototype** (pool into one average). The
brain uses BOTH because they trade off -- the exemplar route wins at exact recall (0.9954) and does
NOT generalize (0.1399 held-out, collapsing from the ceiling); the prototype route generalizes
better relative to its own ceiling. The brief treats the flat sum's averaging as pure destruction;
the brain treats it as ABSTRACTION, and abstraction is what transfers to novel text. What is
UNPINNED (and I did not present as biology): the exact binding/addressing equation -- the binding
problem is open, so the addressed arm's math is engineering-under-test, not a copied brain formula.
What IS pinned and tested: the two-store shape and the memorize-vs-generalize trade-off between them.

## What was NOT established

- **Not that addressed storage is useless.** It beats the flat sum on held-out (+0.0554,
  CI-separated). It is a viable SECONDARY route candidate, not a floor-clearing capability. A future
  fast-episodic + slow-cortical blend (Phase 5) is not refuted by this.
- **Not that the counting floor is "comprehension."** F_COUNT1 at 0.324 is still just co-occurrence
  counting; this result says the substrate's stores are WORSE co-occurrence records than an explicit
  counter, not that counting understands anything.
- **Not a resolution of Phase 1.** By design the codes here are meaning-poor; a storage null is
  uninterpretable as evidence about storage-once-meaning-exists. The claim is narrower and sound:
  addressing is not the lever on the CURRENT codes, and the isolation win is exact-key memorization.

## What I would withdraw first if this were wrong

The 2nd-order counting arm (F_COUNT2) is weak here (0.0046) because the composed-profile query is too
diffuse over 5,490 candidates; F_COUNT1 (first-order) is the load-bearing floor. If any result turned
surprising, re-checking F_COUNT1's construction against `measure_counting_floors_through_the_harness`
is the cheapest first step. The headline (addressed CI-separated below F_COUNT1; exact->held-out
collapse) is a population property and does not hinge on any single item.

## What would have to change in hdlab/ (proposed; the strategy session lands it)

- **Do NOT wire the addressed/bound store into the reading read-out as a capability fix.** It does not
  clear the counting floor on held-out; doing so would repeat the isolation-to-capability error the
  plan warns about, and `STRUCTURE_HURTS` already showed a connected structured code losing.
- **If addressed storage is wired at all, wire it as a SECONDARY (fast-episodic) route, not a
  replacement for the flat sum, and gate it on beating the counting floor on held-out** (it currently
  does not). The honest, evidence-backed lever pair for `hdlab/reading_grounding_loop.py` is upstream:
  (1) meaning SUPPLY (Phase 1), and (2) CODE FORMAT -- a sparse graded code that survives
  superposition (C1_KCAP retains 4x the incumbent's bits), which is a change to how
  `context_vector` / `symbol_vector` build codes, not to where they are stored.

## TLDR (plain language)

We thought the reader was throwing away information by blending every encounter of a word into one
average, and that keeping a separate labelled copy of each encounter would fix it. Tested on real
text: keeping every copy IS better than the blend, but it wins only when you quiz it on the exact
sentences it already saw -- on new text it mostly fails, and a dead-simple "just count which words
appear together" method beats BOTH by a wide margin. So the blending isn't the villain; there was
never much worth keeping, because the word-codes don't carry meaning yet. The fix isn't a fancier
filing cabinet -- it's giving the words meaning in the first place, and using a sparser code that
doesn't smear when you add things up.

## Questions

None. The bar is unambiguously not met (addressed is below the counting floor with a separated
confidence interval), and two prior on-disk cells plus this fair re-test agree.

## Next steps (for the strategy session)

1. Re-verify with the one-line `reverify` command and integrate this REFUTED result; it independently
   confirms `notes/brain_fidelity_drill_memorises_but_does_not_transfer_2026-08-19.md` and closes the
   "fair re-test pending" item by showing the un-handicapped exemplar still loses to counting.
2. Keep Phase 3 blocked behind Phase 1, as the plan already has it. The evidence-backed next levers
   are meaning SUPPLY and CODE FORMAT (sparse), not addressed storage.
3. Optional: record the fair-exemplar-beats-flat sub-finding (+0.0554 held-out) as the reason
   addressed storage stays a WIRE_CANDIDATE for a future secondary route, not a WIRE.

---

## INTEGRATED_BY_STRATEGY -- 2026-08-22. ACCEPTED AS `REFUTED`, AND IT UNSEATS ITS OWN PRIORITY 1.

**Re-verified against `data/exp_flat_vs_addressed_identity_recovery_livepath_v1/metrics.json`, not
against the write-up. Every headline reproduces to six decimals:**

| claim | on disk | |
|---|---|---|
| addressed held-out hit@1 | `0.139891` | MATCH |
| **F_COUNT1 floor held-out** | **`0.324226`** | MATCH |
| addressed - floor | `-0.184335`, CI `[-0.197814, -0.170128]`, `ci_excludes_zero=True` | MATCH |
| exact-key addressed | `0.995446` | MATCH |
| addressed - flat, held-out | `+0.055373`, CI `[+0.045719, +0.065574]` | MATCH |
| `addr_beats_floor_heldout` | `False` | MATCH |

> ### 🔑 **THE DECIDING NUMBER IS THE ONE THEY VOLUNTEERED AGAINST THEMSELVES: EXACT-KEY `0.9954` COLLAPSING TO HELD-OUT `0.1399`.**
> **A `0.9954` in isolation is exactly the shape this project has mistaken for a capability before.**
> They ran the exact-vs-held-out diagnostic themselves and led with the collapse. *An addressed store
> can recall what it was handed; it cannot recognise the same thing from a partial cue.*
> 🧠 **AND IT REPRODUCES A KNOWN STRUCTURAL CAP FROM A NEW DIRECTION.** The archive already records a
> circular WordNet oracle reading `0.8787` at exact key and `0.0365` under the partial cue. **Two
> unrelated mechanisms, same cliff.** *That is the strongest thing in this submission and it is not
> in the headline.*

**CONTROLS -- the full battery, and the one that matters is the must-lose:** `INFO-FREE addressed`
(random episodes, same count and grouping) reads **`0.0000` held-out**; `SCRAMBLE-CONTENT` reads
`0.0000` for both arms; ablation addressed->flat is `-0.0554`; and the positive control (2AFC
self-retrieval `0.7433` >= `0.70`) shows **the instrument works** -- so the `0.1399` is a real
measurement of a real failure, not a broken harness. *Tie density `48/5490` = `0.87%`, immaterial.
`arms_must_differ_ok=True` with per-arm SHA digests, so the arms are provably distinct rather than
assumed to be.*

**AND THEY USED THE STRONGEST FLOOR, WHICH IS THE WHOLE GAME HERE.** Addressed BEATS second-order
counting (`F_COUNT2 0.0046`, delta `+0.1353`) and loses to FIRST-order (`0.3242`). **Quoting the
second-order comparison would have turned this into a win.** *They quoted the one that refutes them.*

### WHAT IT CHANGES -- AND IT COSTS THIS BRIEF ITS OWN RANK

🔻 **`flat_store_destroys_the_code` WAS PRIORITY 1**, on the reasoning that the store is upstream of
everything, so fixing it improves what everything else feeds in. **THAT REASONING IS REFUTED:
addressing is not the lever.** The brief's own analogy -- mixing paint, and a labelled store that
pulls the red back out -- **is right about the mechanism and wrong about the consequence: the red
comes back out at exact key, and not from a partial cue.**

✅ **AND IT CORROBORATES `LONG_TERM_PLAN.md` RATHER THAN CONTRADICTING IT.** That plan already says
**Phase 3 (ADDRESSED STORAGE) is "BLOCKED UNTIL PHASE 1 CLEARS"**, and its gate is worded for exactly
this trap: *"addressed beats flat CI-separated on the REAL reading task, not in isolation. An
isolation win is a construction proof; this project has repeatedly mistaken one for a capability."*
**The solver produced precisely that isolation win, recognised it, and refused it.** *The plan called
this shot; the measurement confirms the ordering.*

🚫 **WHAT IS NOT REFUTED: that the flat sum destroys information.** Addressed genuinely beats flat on
held-out (`+0.0554`, CI-separated). **The flat sum IS lossy -- recovering that loss simply does not
reach the floor.** *Do not cite this as "flat storage is fine".*
