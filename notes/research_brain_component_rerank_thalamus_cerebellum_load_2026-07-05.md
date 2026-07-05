# Research 2x-drill: brain-component build priorities RE-RANKED — is there load for thalamus/cerebellum NOW?

**Date:** 2026-07-05 (angle 2 of 5, level-2 operational drill on `research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md`)
**Type:** Operational re-rank, NOT a fresh lit-scan-as-verification. Drills deeper into the SAME missing-component list now that base capabilities exist and the substrate composes end-to-end.
**Discipline:** Lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis P capped 0.50). All internal figures verified via Grep/Read against `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md`, `hdlab/multi_hop.py`, and 4 prior notes (2026-06-26 to 2026-07-01) — not asserted from memory. Do NOT dispatch (per task).

---

## HEADLINE

**The earlier deferral of thalamus and cerebellum ("unloaded infrastructure — no traffic, no sequential-action loop") is now STALE for thalamus and PARTIALLY stale for cerebellum — and the evidence isn't hypothetical, it's a specific, already-named, already-partially-measured gap sitting inside code on disk since 2026-06-26. The substrate's flagship 5-hop multi-hop CHAIN_GRADE result (`partition_routed_chain`, 0.955 cv=0.007) is certified ONLY under `oracle_routing=True` — the function's own docstring says so explicitly, and 3 concrete real-router candidates (RC1 relation-typed, RC2 HRR-bind/algebraic, RC3 learned) have sat as an OPEN follow-up for over a week. A prior attempt at ONE candidate signal (bidirectional-meet-in-middle) measured a "substrate-native router" at a 0.66 floor — statistically indistinguishable from naive-centroid (0.658 vs 0.662) — i.e., real chance-beating signal exists (0.66 >> ~0.05 chance for 20 partitions) but it's geometric, not structural, and it's nowhere close to chain-grade. That is exactly what "genuine multi-subsystem traffic with no dynamic router yet" looks like, and it is loaded NOW because the underlying multi-hop capability it sits on top of is proven, not speculative, and today's separate integration finding (symbolic/algebraic cleanup beats a co-trained learned bridge at the reason->generate junction, hard/easy regimes both) plus an independent literature precedent (Hash Layers: fixed/algebraic routing matches-or-beats learned MoE gating in a directly analogous sparse-routing setting) both point the SAME direction: try an algebraic/structured router (RC2, instantiated via the ALREADY-CHAIN_GRADE CRT-residue decode mechanism) before a learned one (RC3). Cerebellum is real but one notch behind — it has a genuine target now (BG-gate control degrades 0.653→0.075 from depth-4 to depth-6, an explicitly open envelope-push question), but no named candidate cells exist yet, so it requires fresh design rather than composing two already-scoped pieces.**

**Re-ranked missing/weak components (was: 1. neuromodulation-RPE-training [RESOLVED this session], 2. same, 3. cerebellum DEFER, 4. thalamus DEFER, 5. predictive-coding DEPRIORITIZE):**

| Rank | Component | Verdict this drill | Why it moved |
|---|---|---|---|
| **1** | **Thalamic dynamic router** (RC2: CRT-residue-addressed, algebraic-first) | **LOADED — BUILD NEXT** | Sits directly on a proven CHAIN_GRADE mechanism as its sole honest-scope asterisk; 3 candidates pre-named; 1 negative result already banked (bidir-meet) narrows, doesn't refute; external + internal evidence both favor algebraic-first |
| **2** | **Cerebellar forward model** (anticipatory per-hop correction, feedforward vs feedback control) | **LOADED but needs fresh design — BUILD SECOND** | Depth-degradation curve (0.653→0.075) now EXISTS to correct against — didn't exist at the time of the original deferral; DAgger/Kawato lit gives a real "when is this worth it" criterion (compounding, not i.i.d., error) that matches the observed shape |
| 3 | Broad neuromodulation — ACh-style uncertainty gain | FOLD INTO #1, not standalone | Best framed as the routing SIGNAL for #1's learned fallback (RC3) or the ensemble-RPE cell already spec'd today (14:15) — not a separate component |
| 4 | CLS-consolidation | STILL LOW-PRIORITY | The capability map's OWN entry from earlier today explicitly says: "Only untested lever = CLS-consolidation... low-prior, not worth GPU without new leverage" — re-confirmed, not re-litigating |
| 5 | Cortical microcircuit / predictive coding | STILL DEPRIORITIZED | 2 narrow HARD_FAILs already banked (bigram -0.789 nats, trigram -1.019 nats, 3/3 seeds); nothing in today's work reopens it |

---

## Explicit verdict: is thalamus/cerebellum NOW loaded, or still premature?

**Thalamus: LOADED. Buildable now, not premature.** Three independent pieces of evidence, all verified off-disk:
1. `hdlab/multi_hop.py::partition_routed_chain` (the mechanism behind the 5-hop CHAIN_GRADE cell, 0.9550 cv=0.0074, 3 seeds, META_M7 rail-pass) has an `oracle_routing: bool = True` parameter with a docstring that says, verbatim: *"substrate-native routing is OPEN-FOLLOW-UP (cells RC1/RC2/RC3 per META_BARRIER_1_QUINTUPLE_RECONCILIATION); chain-grade not yet certified for substrate-native routing."* This is not a hypothetical gap — it is the literal thing standing between "certified with a ground-truth cheat" and "certified for real," attached to code that already ships.
2. A prior probe (`research_gap1_routing_bidirectional_as_router_2026-06-26.md` / `research_drill_brain_multihop_M3_bidirectional_meet_in_middle_3x_2026-06-27.md`) tested ONE candidate routing signal (state-cosine bidirectional meet-in-middle) and found it statistically tied to naive-centroid (PART_BIDIR_COLLIDE=0.658 vs PART_NAIVE_CENTROID=0.662, mean_midpoint_cosine=0.000) — explicitly ruled "NOT a substrate-native routing signal at HP threshold." This is informative, not disqualifying: it rules out ONE geometric candidate, leaving the three NAMED candidates (RC1 relation-typed, RC2 algebraic/HRR-bind, RC3 learned) untested, plus a queued composition cell (`RC-multihop-1`: substrate-native router @0.66 composed with oracle binding @0.965) sitting in the backlog since 2026-06-26 — never dispatched.
3. Today's own integration finding (`director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` INTEGRATION section) shows the reason→generate junction resolved decisively toward the ALGEBRAIC/symbolic option over a co-trained learned bridge, at BOTH easy and hard regimes (cot_minus_sym = -0.236 easy / -0.805 hard, sym dominates every regime tested). This is the SAME shape of decision the router needs to make (pick the reliable path, not the noisy learned one) and argues for trying RC2 (algebraic) before RC3 (learned) — not from analogy alone, but because it is the second time this exact substrate has shown symbolic-cleanup beating learned components at a junction.

The traffic is real: entity → hippocampal-index lookup → BG-gate (Go/NoGo) → partition selection (currently oracle) → CA3-style within-partition argmax → next-hop state, repeated up to K=5+ times, each step now independently proven CHAIN_GRADE EXCEPT the routing step. That is exactly "multiple working subsystems with a missing dynamic relay between them" — the condition the original ranking said didn't exist yet.

**Cerebellum: LOADED but one step behind — buildable, requires fresh cell design (not just composing existing pieces).** The specific target is new and concrete: `exp_pfc_gate_cfrpe_trained_v2` (control, PROVEN-at-depth-4, MEASURED_MECHANISM) shows **gonogo_lift DEGRADES with depth: 0.653 at d4 → 0.075 at d6**, and the capability map's own next-step note says verbatim: *"Envelope-push: deeper-regime control (why gonogo degrades d4→d6)."* This is an explicitly open question with a measured curve to fit, which is precisely the condition under which a cerebellar-style anticipatory forward-model (predict the next hop's state/confidence BEFORE committing, correct before the error compounds, as opposed to reactive cleanup after) becomes a well-motivated, falsifiable thing to try — a sequential, depth-dependent, apparently-compounding degradation curve now genuinely exists for it to act on, which it did not when cerebellum was deferred as "no motor/sequential-action loop." The caveat: unlike thalamus, there are no pre-named RC-style candidate cells for this — it needs to be designed from the theory (Marr/Albus/Ito/Wolpert-Kawato feedforward-vs-feedback framework) rather than picked off a backlog, so it is one increment less "shovel-ready" than the thalamic router.

---

## Cheap decisive test — TOP PICK (thalamic router, RC2 instantiation)

**`exp_multihop_router_crt_residue_addressed_v1`**

Reuses the EXACT harness already certified CHAIN_GRADE at K=5 (`partition_routed_chain`, N=8192, V_C=200, n_partitions=20, part_size=10, seeds {7,17,23}) and the ALREADY-PROVEN CRT/grid-modular residue-decode mechanism (today's CHAIN_GRADE generation extension to V=65536, 528x codebook compression). Instead of inventing a new learned router (RC3) or re-testing the already-falsified geometric one (bidir-meet), this re-architects the partition SCHEME itself to be CRT-residue-aligned (partitions = residue classes of the entity index under the same modular decomposition already used for generation), so the router becomes a DETERMINISTIC decode of the post-transition state's residue code — algebraic, parameter-free, glass-box — mirroring the mechanism that just won the reason→generate junction.

**Arms:**
1. `ORACLE_ROUTING` — reproduce the existing certified result (sanity rail, expect 0.9550 cv 0.0074).
2. `CRT_RESIDUE_ROUTER` — partition membership derived by decoding the post-transition state's CRT-residue code (test arm).
3. `NAIVE_CENTROID` — reproduce the already-measured 0.66 floor (informative control: is the new mechanism actually beating the best PRIOR real candidate, not just beating a strawman).
4. `RANDOM_ROUTER` — partition chosen uniformly at random (chance-level anchor, ~1/20 = 0.05; confirms the setup isn't saturated/vacuous).

**HARD-PASS:** `CRT_RESIDUE_ROUTER` per-hop routing accuracy >= 0.90 (clears the existing 0.66 geometric floor by a wide margin, approaching oracle-like reliability) AND end-to-end 5-hop composed accuracy >= 0.70 (recovers >=73% of the oracle's 0.955) AND cross-seed cv < 0.05 AND `RANDOM_ROUTER` lands near chance (0.05-0.15), ruling out a saturated/vacuous partition scheme.

**HARD-FAIL:** `CRT_RESIDUE_ROUTER` per-hop accuracy <= `NAIVE_CENTROID` + 0.05 (doesn't beat the already-known geometric baseline — the algebraic-addressing idea doesn't transfer from generation to mid-chain routing) OR end-to-end 5-hop <= 0.20 (doesn't clear the naive-centroid-composed floor).

**MIDDLE-BAND:** real improvement over `NAIVE_CENTROID` (per-hop 0.66-0.90) but below the chain-grade-composable bar — genuine partial win, needs an RC3 learned top-up layered on the algebraic residue signal (mixture, not replacement — per the Hash-Layers precedent below, a fixed router as the PRIMARY signal with a small learned residual correction is a well-precedented middle path, not just a fallback binary).

**Compute:** CPU, reuses the existing certified harness + the existing CRT-residue decoder implementation (no new representational machinery — the "new" work is re-deriving partition membership from an already-implemented decode function and wiring it as the `router` callable `partition_routed_chain` already accepts). Estimate 2-4 hr.

**P_deflated = 0.30** (raw ~0.50: two independent convergent priors favor algebraic-first — external Hash-Layers precedent for fixed-beats-learned routing in an analogous sparse-routing setting, AND today's own internal symbolic-beats-learned finding at the adjacent reason→generate junction; deflated for genuine novel-synthesis — this specific composition [CRT-residue decode repurposed as a MID-CHAIN routing address rather than a FINAL-output address] has never been tried, and it requires re-architecting the partition scheme, not a drop-in router swap, so there is real risk the residue structure doesn't align cleanly with whatever property determines "true next-hop target." Capped consistent with novel-synthesis P<=0.50.)

---

## Secondary decisive-test sketch (cerebellum, rank #2 — lighter spec, needs design before dispatch)

**Working name: `exp_reasoning_forward_model_anticipatory_correction_v1`** (not yet a full cell spec — this is the shape of the test, to be fleshed out by exp_dev if thalamus's build doesn't fully close the depth-degradation story).

Reuse the SAME control/reasoning-depth harness that measured gonogo_lift 0.653 (d4) → 0.075 (d6). Add a per-hop forward-model step: before committing to hop *t+1*'s transition, predict the expected next-state confidence/reliability from the current trajectory (efference-copy-style), and use a climbing-fiber-style scalar error signal (predicted vs. realized reliability) to correct the state BEFORE the next hop compounds it — as opposed to correcting reactively after the fact.

**Arms:** `NO_CORRECTION` (reproduce 0.653→0.075 decay), `FEEDBACK_ONLY_CONTROL` (denoise AFTER each hop, no anticipation — isolates whether "any correction" is doing the work), `FORWARD_MODEL_ANTICIPATORY` (predict-then-correct BEFORE the hop, the cerebellar-specific mechanism).

**HARD-PASS:** `FORWARD_MODEL_ANTICIPATORY` recovers >=50% of the d4-d6 gap at d6 (i.e., d6 accuracy >= 0.364) AND beats `FEEDBACK_ONLY_CONTROL` by >=0.10 (proves the anticipatory/feedforward property specifically matters — the theoretical crux of Wolpert-Kawato forward models — not just that denoising in general helps).

**HARD-FAIL:** `FORWARD_MODEL_ANTICIPATORY` <= 0.075 + 0.05 (no real lift) OR does not beat `FEEDBACK_ONLY_CONTROL` (the feedforward-specific story is wrong; a generic denoiser would have done the same job, no cerebellar-specific mechanism needed).

**MIDDLE-BAND:** real lift, but <50% gap recovery, or ties `FEEDBACK_ONLY_CONTROL` (real, but not distinctively cerebellar).

**P_deflated = 0.28** (raw ~0.40: three convergent literatures — Marr/Albus/Ito cerebellar theory, Wolpert-Kawato-Miall feedforward-vs-feedback framing, and DAgger's regret-bound criterion for when anticipatory correction beats reactive correction under compounding error — all point the same direction and the observed 0.653→0.075 shape over just 2 depth-steps looks compounding/multiplicative, not additive, which is exactly DAgger's "worth it" condition; deflated hard because no cell or backlog item names this specific mechanism yet — this is genuinely new design, not a queued composition, so uncertainty is higher than #1.)

---

## Cross-thread synthesis

- Builds on and SHARPENS `notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` (today, earlier): that note correctly flagged thalamus/cerebellum as real gaps but DEFERRED both on "no load yet." This drill found the deferral rationale was already stale for thalamus at the time it was written — `hdlab/multi_hop.py`'s oracle-routing scope flag and the RC1/RC2/RC3 backlog have existed since 2026-06-26, nine days before the deferral. The correction is not "thalamus matters" (already known) but "thalamus has ALREADY been carrying an open, named, load-bearing asterisk on a shipped CHAIN_GRADE result the whole time" — the load was real before today's integration work, and integration composing end-to-end makes it MORE valuable to close (closing it directly upgrades an existing capability's honest scope, rather than adding speculative new capability).
- Does NOT re-litigate CLS-consolidation (already deprioritized today, twice, in the FRONTIER/GENERALIZATION capability-map thread and the prior ranking note) or cortical predictive-coding (2x narrow HARD_FAIL banked).
- Complements, does not overlap, today's other in-flight specs: `exp_pfc_gate_ensemble_cfrpe_v1` (14:15 today, population-coded/ensemble RPE for the control gate's own variance, a DIFFERENT junction) and the hubness/content-dehub generalization threads (15:xx today, a DIFFERENT capability row). The routing gap sits specifically at the multi-hop REASONING row, not CONTROL or FRONTIER.
- The `partition_oracle_recovery_mechanism_G_correction_2026-07-01.md` note is the important sobering cross-check: the Markov-floor analysis there shows that even a WEAK real router (r=0.003, half the oracle's r=0.006) only buys a floor of ~0.15 at extreme depth (100s of hops) — meaning "closing the routing gap" should be scoped honestly as "materially better than naive-centroid's 0.66, not necessarily oracle-parity," which is exactly how the HARD-PASS/HARD-FAIL bands above are framed (0.70 end-to-end target, not 0.955).

## Substrate-product implications

Closing the thalamic-router gap converts the REASONING capability's headline CHAIN_GRADE claim from "certified under a ground-truth cheat" to "certified for real," which matters directly for the glass-box positioning story: an inspectable, algebraic (CRT-residue-decoded) router is a STRONGER credibility claim than either an oracle flag buried in a docstring or an opaque learned gate — it is the same "inspectable NN-argmax over a known codebook, no opaque learned component" story that today's integration finding already won at the reason→generate junction, extended to the routing junction. A cerebellar-style anticipatory corrector, if it works, would be the first genuinely NEW piece of glass-box machinery that directly targets the "how deep can reasoning go before it degrades" question — a concrete, quantifiable answer ("depth-6 recovers to X%") is a much better product claim than the current honest bound ("works at depth-4, degrades by depth-6, mechanism why is open").

## Citations (verified: 8 new this drill + 15 carried from same-day prior note = 23 total; new 8 cross-checked by 2 independent Sonnet lit-scan sub-agents using generic-terms-only queries per query-privacy discipline)

**New this drill:**
1. Sherman SM, Guillery RW (2017) Functioning of circuits connecting thalamus and cortex. *Compr Physiol* — driver/modulator framework (carried forward, re-verified against the specific routing question).
2. Halassa MM, Kastner S (2017) Thalamic functions in distributed cognitive control. *Nat Neurosci* 20(12).
3. Jégou H, Douze M, Schmid C (2011) Product quantization for nearest neighbor search. *IEEE TPAMI* 33(1) — algebraic/deterministic bucket-assignment precedent.
4. Roller S, Sukhbaatar S, Szlam A, Weston J (2021) Hash Layers For Large Sparse Models. *NeurIPS* — fixed/algebraic routing matches-or-beats learned MoE gating (Switch Transformer, BASE layers), the key precedent for algebraic-first strategy.
5. Shazeer N et al. (2017) Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer. arXiv — learned-gating baseline + routing-collapse failure mode.
6. Wolpert DM, Miall RC, Kawato M (1998) Internal models in the cerebellum. *Trends Cogn Sci* 2(9) — forward-model / feedforward-vs-feedback framework.
7. Schmahmann JD (2004, 2010) Dysmetria of thought / Universal Cerebellar Transform — extension of cerebellar theory beyond motor control.
8. Ross S, Gordon G, Bagnell D (2011) A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning (DAgger). *AISTATS* — regret-bound criterion for when anticipatory correction beats reactive correction under compounding error.

**Carried from `research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` (same day, not re-verified externally this cycle, per 2x-drill discipline — deepen, don't re-scan):** McClelland-McNaughton-O'Reilly 1995, Clarkson-Ubaru-Yang 2023, Krogh-Vedelsby 1995, Wood et al. 2023, Knight-Leveson 1986, Page (Diversity Prediction Theorem), Schultz-Dayan-Montague 1997, Yu-Dayan 2005, O'Reilly-Frank 2006, Frank-Seeberger-O'Reilly 2004, Ito/Marr/Albus 2020 synthesis, Bastos et al. 2012, Rao-Ballard 1999, Miller-Cohen 2001 (15 items, listed in full in the prior note).

**Internal artifacts verified off-disk this cycle (not lit citations, but load-bearing evidence):** `hdlab/multi_hop.py` lines 287-361 (oracle_routing docstring); `notes/partition_oracle_recovery_mechanism_G_correction_2026-07-01.md`; `notes/skunkworks_tier_rule_batch3_6artifact_2026-06-26.md` (bidir-meet 0.658 vs naive-centroid 0.662; RC-multihop-1 backlog item); `notes/skunkworks_batch2_atomize_complete_RC_backlog_2026-06-26.md` (RC1/RC2/RC3 definitions); `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` (CONTROL section, gonogo 0.653 d4 -> 0.075 d6; INTEGRATION section, symbolic-beats-learned-bridge finding).
