# Supporting material for SOLVED.md (folds in once full numbers land)

## A. PROPOSED hdlab DIFF (Q111 — strategy lands; I do not)

**Default-off `learner_growth` flag on the meaning read-out. Byte-identical when off.**

The grown store is an OFFLINE-BUILT asset (admissible per owner 08-16 "foundation is free to build"); the LIVE
change is only how the meaning read-out is *scored*.

1. **New default-off asset (offline):** `data/foundation/learner_growth_v1/` holding (i) the pre-growth
   base SELPREF store (the anchor), (ii) the slowly-consolidated EMA anchor store at the chosen `eta`, and
   (iii) the final grown store — all built by this cell's continual loop, git-committed binary/newline=''.

2. **`hdlab/situation_reader.py` (or the meaning read-out organ the learner attaches to):** add
   `learner_growth: bool = False`. When **off**: the meaning similarity is the incumbent base read-out
   (byte-identical — a witness must show the off-path is unchanged). When **on**: the read-out similarity =
   `hdlab.cls_growth.make_ensemble_sim(sim_base, sim_grown)` (keep-both; VERBATIM promoted primitive), where
   `sim_grown` is the EMA slow-anchor store's cosine. i.e. read through the fused sim, not the base sim.

3. **Rollback gate at load:** before adopting a freshly-grown store, run
   `hdlab.cls_growth.rollback_gate` against a frozen known-correct probe; accept only if probe corruption <
   0.15, else keep the prior store. This makes every growth step reversible in the live substrate.

4. **Operating point (from this problem's evidence):** `eta` small (frozen-to-0.1). The safe `eta` is
   **corpus-dependent** — use the FROZEN anchor (eta=0) as the conservative default; raise toward eta=0.1 on
   modern-text-dominated reading where the frontier shows it is safe AND gains more.

5. **DEPENDENCY (state it in the landing):** the meaning read-out is *not yet consulted by* `read()`
   (problem `reader_meaning_channel`, rank 4 — confirmed on disk: `situation_reader` imports no meaning
   store). So `learner_growth` lands on whatever consults the learner's meaning store; until
   `reader_meaning_channel` wires that path, the flag changes the meaning-read-out score but not `read()`.

6. **Flipping growth ON by default is a SEPARATE owner decision on this evidence** — landing stays default-off.

## B. ADJACENT COMPONENTS — brain-fidelity + optimization (candidate follow-on problems)

Per owner 08-28 (evaluate adjacent components for fidelity + optimization, don't just name them):

1. **Prioritized / at-risk-weighted replay (drill Q2).** OUR current fusion replays the anchor UNIFORMLY.
   The brain prioritizes replay toward the weakest / most-at-risk items (Mattar & Daw 2018 gain×need;
   Schapiro 2018 weak-item-first). *Fidelity:* our uniform anchor is a placeholder for prioritized replay.
   *Optimization:* weight the fusion per-dimension by drift/risk → likely raises the safe-`eta` on hard
   corpora (old fiction), where uniform replay wastes protection on already-safe dimensions. **High-value
   follow-on:** "prioritized-replay anchor for continual growth."

2. **Synaptic consolidation vs external anchor (drill Q4).** The brain's lifelong anti-drift is per-parameter
   stability that GROWS WITH CONFIRMATION (Fusi 2005 cascade; EWC Kirkpatrick 2017). Our slow-anchor + fuse
   reproduces the *effect* via an external store — a computational-level SUBSTITUTE, not the mechanism.
   *Optimization:* an EWC-style per-dimension stability that hardens confirmed meaning could give stability
   WITHOUT capping plasticity (the frontier's tradeoff), a strictly better stability/plasticity point.
   **Follow-on:** "synaptic-consolidation (confirmation-hardened) meaning store."

3. **The meaning read-out is unwired (`reader_meaning_channel`, rank 4).** `read()` consults no meaning store
   on disk — the live wire this problem's evidence supports has a hard dependency on that problem. *This is
   the immediate blocker to a truly LIVE (in-`read()`) canary.* Adjacent bottleneck, already filed.

4. **Corpus-age of the EVAL base (standing confound).** The safe-`eta` tightens on LitBank precisely because
   the base store is sparse on archaic verbs (OFF acc 0.073 vs modern 0.273) → wide corruption CIs. This is
   the reading-corpus-age confound (McGuffey/LitBank ~pre-1923). *Fidelity/optimization:* a modern eval base
   would widen the safe-`eta` envelope; connects to the packaged `mcguffey…migrate to modern text` problem.

## C. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy folds in)

> **AUDIT UPDATE (2026-08-31, `run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite`).**
> Extends the CLS safe-growth entry (§2b 08-25) from a fixed batch to a CONTINUAL live canary. The anti-drift
> lever is ONE parameter: the slow anchor store's **consolidation rate `eta`** (its neocortical slow-timescale
> learning rate). Read-out each round = keep-both ensemble(slow anchor, fast grown) via `hdlab.cls_growth`
> (verbatim). CORRECTION to the offline aligned-continual arm: its measured drift (0.114→0.196 over 3 rounds)
> was an anchor-DECAY artifact — running-fusion halves the anchor's weight each round — NOT an intrinsic
> ceiling. FIDELITY (drill 2026-08-31): a FROZEN original anchor is only PARTIAL fidelity — semantic/word
> meaning is continuously but SLOWLY updated over a lifetime (Winocur & Moscovitch trace-transformation;
> diachronic semantic update); the faithful anchor is a SLOWLY-CONSOLIDATED small-`eta` EMA (Kumaran 2016 slow
> store; mean-teacher). The slow-anchor+fuse device is a COMPUTATIONAL-LEVEL SUBSTITUTE for synaptic
> consolidation (Fusi 2005 cascade / EWC 2017), reproducing the anti-forgetting effect via an external store,
> not intrinsic per-synapse stability. MEASURED (full 5M→15M, 6 rounds, two downstreams): the
> stability-plasticity FRONTIER — terminal corruption rises monotonically with `eta`, gain rises with `eta`;
> the safe-`eta` (corruption CI-upper<0.15) is CORPUS-DEPENDENT (frozen on old fiction; up to eta≈0.1 on
> modern held-out). The decay control (eta=0.5) drifts CI-separated above the anchor (the can-fail fires).
> [numbers folded from SOLVED.md result block]
