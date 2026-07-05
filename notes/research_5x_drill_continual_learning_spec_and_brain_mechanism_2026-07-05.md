# 5x Convergence Drill: Continual Learning — Exact Spec + Brain Mechanism

**Date:** 2026-07-05
**Requestor:** Director (continual learning = natural strength framing; NOT a vs-LLM comparison)
**Drill discipline:** 5x independent angles (systems/computational neuro, cognitive science, VSA/HDC theory, modern ML/DL, first-principles/info-theory) converged against ~18 months of substrate-internal empirical trail. Lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis cap 0.50; HARD-FAIL thresholds mandatory).
**Substrate-query-first:** this topic has been drilled twice before at 5x depth (2026-06-22 CLS drill, 2026-07-01 CRISPR regime map) plus a 2x architectural-revival drill (2026-06-24) and ~80 landed cells. This memo does NOT re-run that scan — it converges the prior substrate trail against five FRESH external angles and closes on the one question none of the 80 cells has tested: schema formation, as distinct from forgetting-prevention.

---

## HEADLINE

**The "no catastrophic forgetting" MVP is DONE — proven repeatedly, structurally guaranteed, and cheap. The "schema formation" full-goal has NEVER BEEN TESTED, and today's drill produces the sharpest evidence yet for why: an already-landed cell (`exp_substrate_c3_segregated_dual_W_spectrum_replication_v1`, MIDDLE_BAND, 2026-06/07) fixed forgetting almost perfectly (forgetting 0.678 -> 0.011, delta=0.667 vs the fused-weight baseline) using the exact brain-correct architecture (spatially segregated hippocampus/cortex stores + one-way replay) — and TRANSFER STAYED AT EXACTLY 0.000.** Zero-forgetting and schema-formation are not the same axis, and fixing one does not move the other at all. All five literatures converge on why: item-level replay (re-presenting old raw episodes into a shared write channel) is a retrieval-robustness operation, not an abstraction operation. Schema formation requires a mathematically distinct step — averaging/bundling many episodes' SHARED substructure into a separate, lossy, compressed representation (CLS's cortex, VSA's bundle-as-matched-filter, MDL's minimum-description-length model) — that the substrate has never built or tested, despite having landed ~80 cells nominally "about" continual learning.

**P_deflated (no-forgetting MVP, already proven): 0.90** — not novel synthesis, a repeated confirmed empirical fact (a8, CRISPR, distshift, c1, c3 all agree).
**P_deflated (schema-formation build, novel synthesis, first attempt): 0.32** (capped at 0.50 per novel-synthesis ceiling; further deflated because the VSA literature explicitly flags multi-schema interference as its own unsolved problem).

---

## A. WHAT WE WANT — exact spec + measurable success criteria

**Two genuinely separate capabilities, historically conflated under "continual learning."**

### A.1 MVP — no catastrophic forgetting (STRUCTURAL, ALREADY DONE)

Spec: ingest new content; old content's recall does not degrade.

Measured metric already in use across substrate cells: `forget_p1` = recall(task-1 / phase-1 items) after J subsequent ingests, relative to recall immediately after phase 1.

**Numbers, already on disk:**
- `a8_continual_writes_no_catastrophic_forgetting_v1`: HARD_PASS, recall=1.000 (std=0.000) up to alpha=0.3; cliff at alpha=0.5 (acc=0.527); collapse at alpha=1.5 (acc=0.10) — this is a CAPACITY cliff (crosstalk in a single shared Hebbian matrix), not per-se catastrophic forgetting.
- `crispr_plasticity_slab_replay_v1` (landed 2026-07-01, `data/exp_crispr_plasticity_slab_replay_v1/metrics.json`): `mean_forget_p1 = 0.000` in ALL four replay-budget arms (R=0,5,20,50) at J=5 phases, M=100/phase, N=4096. Append-only slab architecture: zero forgetting, unconditionally.
- `exp_substrate_c3_segregated_dual_W_spectrum_replication_v1` (landed, MIDDLE_BAND): segregated dual-W + one-way replay: forgetting=0.011 vs FUSED_W forgetting=0.678 (delta=0.667, mechanism confirmed).
- `substrate_continual_learning_distshift_v1` (v430, cap_map): HARD_PASS — current_state_acc=1.000, updated_returns=1.000, silent_contradiction_rate=0.000, audit_trace_acc=1.000 across 3 seeds.

**"Done" bar for MVP (already cleared):** forget_p1 <= 0.05 after >= 5 sequential disjoint ingests at realistic load (alpha <= 0.3, or any load under an append-only/segregated architecture). **This bar has been cleared 4 independent times under 4 different architectures.** MVP is not a research question anymore; it's an engineering-hardening question (does it hold at production scale/stream-length — CRISPR J=20 long-horizon cell is queued for that, rank-3 in the 07-01 regime map, not yet run).

### A.2 FULL GOAL — automatic schema formation (THE REAL GAP, UNTESTED)

Spec (sharpened from the first-pass): the substrate must extract, from many bound episodes that share latent relational structure, an OVERLAPPING generalizable representation that lets it correctly complete or retrieve **novel items it has never seen**, provided those items share the learned structure. This is qualitatively different from "does old recall survive new writes" — it is "does new capability emerge from old episodes that generalizes beyond them."

**Measurable success criteria (functional-requirement-first, proposed — does not yet exist in the substrate):**

1. **Forgetting retention** (carried over, already met): forget_p1 <= 0.05.
2. **Structural transfer accuracy (NEW metric, does not exist yet)**: train on bound (role, filler) episodes drawn from relation-set A (e.g., a KG relation-type such as `employs`, `located-in`); hold out a disjoint set of ENTITIES that never appear during training but participate in the SAME relation-type; measure completion/retrieval accuracy on these held-out entity-pairs against a random/no-schema baseline. **HARD-PASS bar (proposed): structural transfer accuracy >= 0.30 above random baseline. HARD-FAIL: <= 0.05 above random (indistinguishable from no-schema-formed).**
3. **Distinguish from item-level bleed-through**: a control arm must confirm the gain is NOT explained by accidental overlap/interference (the existing `transfer_final` metric in `crispr_plasticity_slab_replay_v1` and `c3_segregated...` measures exactly this weaker, confounded thing — see Section E for why it must NOT be reused as-is for the schema claim).

**MVP for the schema half:** a single relation-type, single consolidation pass, structural transfer accuracy statistically distinguishable from 0 (even a small positive effect, e.g. >= 0.10 above baseline, cv <= 0.30). **"Done" for the full goal:** multiple overlapping relation-types consolidated simultaneously without one schema corrupting another (the VSA literature's flagged open problem — see Section C), transfer holding at >= 0.30, and a live drift/staleness signal for when a schema needs updating.

---

## B. HOW THE BRAIN DOES IT — existence proof + the consolidation algorithm concretely

**The brain is lifelong-no-catastrophic-forgetting AND schema-forming. This is not aspirational — it is the empirical baseline of every intact hippocampus+neocortex system, and the mechanism is one of the best-characterized results in systems neuroscience (McClelland, McNaughton & O'Reilly 1995, *Psych. Review* — Complementary Learning Systems, CLS).**

**Architecture:** two systems, not one.
- **Hippocampus** (fast, sparse, pattern-separated): one-shot episodic encoding. DG sparsifies (~1-5% active), CA3 is a fast auto-associative attractor store, CA1 reads out / replays.
- **Neocortex** (slow, dense, overlapping): gradual, INTERLEAVED learning that extracts cross-episode statistical structure — this is where schemas live.
- **Replay** is the bridge: during sleep (sharp-wave ripples, ~150-200Hz, ~50-150ms bursts, ~5-10/sec during slow-wave sleep — Wilson & McNaughton 1994; Buzsaki 1986/2015; Klinzing/Niethard/Born 2019), the hippocampus re-activates stored episodes and the cortex receives them as additional, interleaved training signal.

**What replay concretely COMPUTES (the honest answer, not the metaphor):** established computational models (Kalí & Dayan 2004, *Nat Neurosci*) do NOT show the cortex taking one big gradient step on generated samples. They show **repeated small local Hebbian/error-correcting increments accumulated over MANY replay events**, functionally equivalent to interleaved rehearsal at a slow learning rate ~10x below the hippocampal one. Schapiro, Turk-Browne, Botvinick & Norman (2017) go further: the fast/slow split exists WITHIN the hippocampus itself — the monosynaptic (EC->CA1) path does fast statistical/regularity extraction; the trisynaptic (DG/CA3) path does one-shot pattern-separated storage. **The schema-specific finding that matters most for a build spec:** Tse, Morris et al. (2007, *Science* 316:76; 2011 follow-up) showed that once a cortical schema exists, a brand-new but schema-CONSISTENT fact becomes a stable cortical memory in as little as **one trial** instead of the normal slow interleaved-replay timescale — i.e., schemas are not just a byproduct of consolidation, they actively ACCELERATE future learning of consistent information. This is the single most important brain fact for product framing: schema formation isn't just "compression," it's a learning-rate multiplier for everything that fits the schema afterward.

**Divergence worth being honest about:** whether the hippocampus is ever fully "silenced" post-consolidation is contested — Multiple Trace Theory (Nadel & Moscovitch) holds detailed episodic traces stay permanently hippocampus-dependent while only gist/schema becomes cortex-independent. This matters for the build: **"no catastrophic forgetting" in the brain is not "everything gets converted to schema and the episode is discarded" — it's "the raw episode is RETAINED (at least for detailed recall) AND a separate abstracted schema is ALSO built."** Two stores, not a replacement of one by the other. This maps directly onto append-only-episodic-store (keep everything, structural) + a genuinely separate schema store (lossy, statistical) — not one system trying to do both.

---

## C. 5x CONVERGENCE — load-bearing consensus + divergence

All five independently-searched literatures agree on the same architectural answer, and — more valuably — all five independently flag the same limitation that the substrate's own data has now confirmed empirically.

| Angle | Convergent claim | Citations |
|---|---|---|
| Systems/computational neuro | Two systems (fast/sparse + slow/overlapping) bridged by replay; replay = many small Hebbian/error-corrective increments, not one gradient step | McClelland 1995; Kalí & Dayan 2004; Schapiro 2017; Tse 2007/2011 |
| Cognitive science | Schema = abstracted cross-episode structure that ACCELERATES new consistent learning; requires INTERLEAVED (not blocked) presentation to form without interference; measurable via train-on-A/transfer-to-structurally-similar-novel-B paradigms (transitive inference, artificial grammar learning) | Bartlett 1932; Tse 2007/2011; McClelland 1995; Kornell & Bjork 2008 |
| VSA/HDC theory | Bundling (sum+normalize) is a matched-filter/SNR operation: shared bound structure across many episodes grows coherently (~k), idiosyncratic noise grows incoherently (~sqrt(k)) — mathematically sound schema-extraction mechanism. BUT: published HDC continual-learning systems (LifeHD) explicitly avoid bundling everything into one vector — they keep SEPARATE per-cluster hypervectors + merge/evict, because crosstalk/interference from overlapping bundles is an unsolved failure mode | Kanerva 1988/2009; Plate (HRR); LifeHD arXiv:2403.04759; Kleyko et al. PMC9869149 |
| Modern ML/DL | Anti-forgetting (EWC, replay, architectural) is a MATURE, largely-solved problem with standard metrics (BWT/FWT, Lopez-Paz & Ranzato 2017). CLS-inspired dual-network systems (DualNet) measurably reduce forgetting. But genuine compositional/structural generalization is explicitly flagged by surveys (De Lange 2021, Parisi 2019) as UNSOLVED and rarely even tested — gains are inferred from linear-probe accuracy, not schema-extraction tests | McCloskey & Cohen 1989; Kirkpatrick 2017 (EWC); Zenke 2017 (SI); Lopez-Paz & Ranzato 2017 (GEM); Pham/Liu/Hoi 2021 (DualNet) |
| First-principles/info-theory | Catastrophic forgetting is NOT a universal law — it is a consequence of FIXED, SHARED, overwrite-able capacity (Hopfield's 0.138N bound is specific to one fixed N x N matrix). Non-parametric/append-only/Progressive-Network-style growing memory is explicitly called "immune to forgetting" in the literature. BUT abstraction/schema-formation is inherently a LOSSY COMPRESSION operation (MDL is the safe, uncontested formalization; the stronger information-bottleneck/compression-implies-generalization claim is CONTESTED — Saxe et al. 2018 showed it doesn't survive controlled tests) | Grossberg (ART); Rusu 2016 (Progressive Nets); Tishby & Zaslavsky 2015 (IB, contested); Saxe 2018 (IB rebuttal); Rissanen (MDL) |

**The convergent mechanism we build:** CLS fast-bind (episodic, append-only, already have) + slow-consolidate via a SEPARATE, spatially-segregated schema store fed ONE-WAY (never writes back) by a bundling/averaging operation over many episodes sharing structure — not by re-injecting raw individual episodes into a shared write channel.

**Divergence that matters most (and is now empirically confirmed on our own substrate, not just in the literature):** forgetting-prevention and schema-formation are SEPARATE MECHANISMS requiring separate fixes. `c3_segregated_dual_W_spectrum_replication_v1` proves this cleanly: segregation fixed forgetting almost perfectly (0.678 -> 0.011) using exactly the brain-correct architecture, and **transfer stayed at exactly 0.000.** No literature disagrees with this outcome — every angle predicts item-level replay ≠ abstraction; the substrate just gave the cleanest possible empirical confirmation of the theoretical split.

---

## D. AUGMENT BEYOND BIOLOGY

Per standing discipline, the brain's biological constraints are a floor, not a ceiling — we should exceed them where high-energy/non-biological compute allows, while keeping the efficient biological version as fallback baseline.

1. **Exact bundling instead of stochastic sleep-replay sampling.** The brain approximates its own schema (the shared structure across thousands of episodes) via ~10k-30k stochastic sharp-wave-ripple replay events per night, because it has no direct addressable read/write access to its own synapses — it has to sample. **The substrate does have direct addressable access.** It can compute `schema_vector = bundle(all episodes matching relation-type R)` EXACTLY, in one shot, as a single vector-addition pass over every matching stored atom, any time, with zero "sleep budget." This is a genuine, concrete non-biological advantage: exact schema extraction where biology has only noisy stochastic approximation.
2. **Exhaustive interleaving instead of random sampling.** Biology interleaves replay stochastically; the substrate can systematically enumerate every (old-episode, new-episode) pairing relevant to a schema update, with no metabolic cost, and can re-run the full consolidation pass on demand (e.g., nightly batch job) rather than being limited to a fixed sleep window.
3. **Explicit schema-extraction optimization (available, currently deprioritized).** A gradient/optimization-based distillation of the schema store (rather than pure Hebbian bundling) is available given non-biological compute, but cuts against this codebase's forward-only Hebbian convention (CLAUDE.md) — flagged as an available lever, not a default. Keep the Hebbian-bundling version as the primary, biologically-grounded fallback; treat backprop-consolidation as an escalation path only if bundling provably plateaus.
4. **Keep the efficient-biological version as baseline.** The one-way-replay + segregated-store architecture (cheap, Hebbian-only, already validated to fix forgetting) remains the default substrate primitive; the "beyond biology" augmentations above are additive passes on top, not replacements.

---

## E. SUBSTRATE FIT + FIRST BUILD

### E.1 What we have (verified on disk)

- **Append-only episodic store**: structural, already proven immune to forgetting (Section A.1). U1 multi-value KG store is the substrate's hippocampus-analog (CERT 584, set-recall 0.99 @ 50k scale).
- **W Hebbian matrix**: the substrate's cortex-analog; capacity-bounded (a8 cliff at alpha=0.5).
- **Segregated dual-W + one-way replay**: LANDED and validated to nearly eliminate forgetting (`c3_segregated_dual_W_spectrum_replication_v1`, forgetting 0.011 vs FUSED 0.678).
- **Item-level replay-into-new-slab**: LANDED, MIDDLE_BAND, weak/noisy (`crispr_plasticity_slab_replay_v1`, best R=50 -> transfer_final=0.125, cv=0.40; not monotone in R — R=5 and R=20 both give 0.033).
- **~80 cells** touching CL primitives in isolation (STC, SWR-gated replay, cascade-synapse metaplasticity, active/intentional forgetting, pseudoinverse pattern-downdate) — mostly landed, not composed into a schema-formation test.
- **Open-relation-vocabulary ingest design** (hippocampal-style role-filler binding, no closed enum) — designed, not yet ingested at the scale needed for a multi-relation schema test.

### E.2 The exact gap

**No cell has ever tested generalization to novel, previously-unseen items sharing learned relational structure.** Every "transfer" metric built so far (`crispr_plasticity_slab_replay_v1`'s `transfer_final = pr[J-1][J-1]`-style recall term; `c3`'s identical-in-spirit metric) measures whether OLD, ALREADY-STORED items survive new writes — a retrieval-robustness question. **None measures whether the substrate can correctly complete a relation instance it has never stored, using only the structure learned from other instances of the same relation.** This is the schema-formation test, and it does not exist yet. The mechanism to build it (bundling many bound (role, filler) episodes sharing a relation-type into one prototype vector, held in a segregated schema store, queried by binding a NEW role to the schema and reading out a filler-shaped answer) is directly implementable from primitives the substrate already has (Hebbian bind/bundle, codebook-NN cleanup, segregated dual-store harness from `c3`).

### E.3 Cheap decisive test (the single most decisive next build)

**Cell (proposed, not yet built): `schema_bundle_structural_transfer_v1`**

1. Ingest M bound (entity_A, entity_B) pairs for a single relation-type R (e.g. drawn from FB15k-237 or ConceptNet, already substrate-ingested) into the episodic store — standard append-only write, no change needed.
2. Consolidation pass (the new piece): bundle all M episode vectors for relation R into one schema vector `S_R = bundle(bind(role_subject, entity_A_i) , bind(role_object, entity_B_i)) for i in 1..M`, written into a SEPARATE schema store (never written back to by the episodic store — one-way, per Section C).
3. Held-out test: present a NOVEL entity pair (entity_C, entity_D) that participates in relation R but was NEVER in the training M — query the schema store (not the episodic store) for entity_D given entity_C bound to role_subject.
4. Metric: structural transfer accuracy = P(correct entity_D retrieved | novel entity_C) vs random-entity baseline.
5. Control arm: repeat with a SHUFFLED relation-assignment (entity pairs randomly relabeled) — schema should NOT transfer on shuffled data; this is the discriminator that separates "genuine structural generalization" from "the codebook is just small enough that anything looks close to anything."

**Compute cost:** cheap — pure vector arithmetic on already-ingested KG data (FB15k-237/ConceptNet atoms exist in the substrate); no LLM calls; single-CPU, likely <1 hour.

### E.4 Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 (PRIMARY):** bundling M >= 50 episodes of relation R into a segregated schema store yields structural transfer accuracy >= 0.30 above random baseline on held-out novel entity pairs.
- HARD-PASS: transfer accuracy - random_baseline >= 0.30, cv <= 0.30 across >= 3 seeds, shuffled-control arm shows transfer accuracy - random_baseline <= 0.05 (discriminator confirms genuine structure, not codebook artifact).
- HARD-FAIL: transfer accuracy - random_baseline <= 0.05 on the real (unshuffled) arm — bundling does not extract usable structure at this scale.
- **P_deflated = 0.32** (raw estimate 0.55; deflated 0.18 for novel-synthesis + the VSA literature's explicit warning that crosstalk/interference is the dominant unsolved failure mode for this exact operation; capped at 0.50 ceiling, further deflated below cap given no direct precedent for this composition on substrate's specific Hebbian-superposition arithmetic).

**Prediction 2 (MULTI-SCHEMA STRESS TEST, conditional on P1 HARD-PASS):** two DIFFERENT relation-types (R1, R2) bundled into two separate schema vectors coexist without cross-contamination (schema_R1 query does not leak schema_R2 answers).
- HARD-PASS: cross-contamination rate <= 0.05 (structural transfer for R1 queries against schema_R2 is at random-baseline).
- HARD-FAIL: cross-contamination rate >= 0.20 — confirms the VSA literature's flagged interference problem is load-bearing here too; would require moving to per-relation SEPARATE schema slots (LifeHD's engineering answer) rather than one shared bundle space.
- **P_deflated = 0.25** (this is exactly where the literature is most uncertain — no source found confirms non-interfering coexistence of many bundled schemas; if anything the evidence leans toward interference being likely).

**Prediction 3 (NULL BRACKET):** at M < 10 episodes per relation, structural transfer accuracy is indistinguishable from random (insufficient episodes for the SNR/bundling argument to kick in).
- HARD-PASS (as a sanity check, not the interesting result): transfer accuracy - random <= 0.10 at M=5.
- Purpose: confirms the mechanism has a real sample-size dependency, not an artifact of codebook size.

### E.5 Substrate-product implications

1. **This is the real "moat vs. LLMs" claim, correctly scoped.** The no-forgetting MVP is done and is a genuine, provable differentiator (LLMs need retraining; the substrate structurally does not forget). But "the substrate generalizes across episodes into schemas the way the brain does" is NOT yet true and should not be marketed as such until `schema_bundle_structural_transfer_v1` (or equivalent) lands HARD-PASS.
2. **Two separate product primitives, not one.** "Ingest without forgetting" (ship-ready, already proven) and "form a reusable schema from many facts" (research-stage, this memo's proposed cell) should be described and roadmapped separately — conflating them overclaims the current state.
3. **The schema store, once built, is also the natural place for staleness/drift detection** — a schema whose constituent episodes have been individually contradicted or superseded is a detectable divergence between the episodic store's current state and the schema's frozen bundle, giving a free "this generalization may be out of date" signal.
4. **Route the existing MIDDLE_BAND results forward.** `crispr_plasticity_slab_replay_v1` (2026-07-01) and `c3_segregated_dual_W_spectrum_replication_v1` are both landed MIDDLE_BAND with no 2x-revival note filed yet — per USER-standing routing discipline this drill IS that revival: the recommended next action is `schema_bundle_structural_transfer_v1` above, not further tuning of the R-parameter on the existing item-level replay cells (which the convergence in Section C says is the wrong axis to keep pushing).

---

## F. HONEST RATING (no smoke)

- **No-catastrophic-forgetting MVP: GOOD.** Proven four independent times under four architectures (a8, CRISPR append-only, distshift, segregated dual-W). This is genuinely our structural strength — append-only sidesteps the classical fixed-shared-capacity forgetting mechanism by construction, and the literature (Progressive Networks explicitly called "immune to forgetting," non-parametric/kNN methods likewise) backs this as a legitimate, not-cheating way to avoid the problem. Not smoke.
- **Consolidation-without-degrading-old-recall (the MVP-plus step): MEDIOCRE.** TWO_TIER/NREM replay hit HARD_PASS_PARTIAL (drift reduced 30-57%, never full HARD_PASS); STC selective downscale HARD_FAILED outright (destroys older patterns like naive global homeostasis). Real but partial, noisy (cv 0.40-0.87 across the relevant cells), and the composition-antagonism failure mode (cf-RPE + Hebbian fighting on shared weights) took a full 2x drill to correctly diagnose.
- **Schema formation (true abstraction/generalization to unseen items): BAD, essentially untouched.** Despite ~80 landed cells nominally "about continual learning," ZERO test generalization to novel structurally-similar items. This is genuinely the hard part, and it has NOT been drilled empirically until this memo's proposed cell. Do not let the MVP's GOOD rating bleed into a claim that this is solved — it isn't started.
- **Is the stability-plasticity wall fundamental or a design cost?** Per Section C/E5 (info-theory angle): the STABILITY half (don't forget) is a FIXED-SHARED-CAPACITY design artifact, not a fundamental law — append-only legitimately sidesteps it, this is PROVEN on our own substrate, not just argued. The PLASTICITY/ABSTRACTION half (form a compressed generalizable schema) re-inherits a real cost: MDL says compression-into-shared-structure is inherently lossy, so any finite schema store has its OWN capacity-accuracy tradeoff — this second bound is closer to fundamental, though "fundamental" here means "the schema store has a capacity limit like any compressor," not "abstraction is impossible." The stronger claim that compression IMPLIES generalization (information bottleneck) is CONTESTED in the literature (Saxe et al. 2018) and should not be leaned on as proven.
- **Proven-vs-speculative split:** PROVEN — no-forgetting (4x), composition-antagonism diagnosis (c3 empirical confirmation), item-level-replay-is-weak-and-noisy (crispr_plasticity_slab_replay_v1 MIDDLE_BAND numbers). SPECULATIVE — that bundling-based schema consolidation will work at the proposed HARD-PASS bar (P_deflated=0.32, below 50/50), that multiple schemas can coexist without interference (P_deflated=0.25, literature leans against), that Tse-style "one-trial schema-consistent learning" transfers to a substrate composition rather than being a purely biological (protein-synthesis/immediate-early-gene) phenomenon with no clean substrate analog yet identified.

---

## Citations (verified count: 24, across 5 independent lit-scans + substrate-internal)

1. McClelland JL, McNaughton BL, O'Reilly RC (1995). Why there are complementary learning systems in the hippocampus and neocortex. Psych Review 102:419-457.
2. McCloskey M, Cohen NJ (1989). Catastrophic interference in connectionist networks. Psych Learning & Motivation 24:109-165.
3. Kalí S, Dayan P (2004). Off-line replay maintains declarative memories in a model of hippocampal-neocortical interactions. Nat Neurosci.
4. Schapiro AC, Turk-Browne NB, Botvinick MM, Norman KA (2017). Complementary learning systems within the hippocampus. Phil Trans R Soc B 372:20160049.
5. Tse D, Langston RF, et al., Morris RGM (2007). Schemas and memory consolidation. Science 316:76-82.
6. Tse D, et al. (2011). Schema-dependent gene activation and memory encoding in neocortex. Science 333.
7. Kumaran D, Hassabis D, McClelland JL (2016). What learning systems do intelligent agents need? Trends Cog Sci 20:512-534.
8. Nadel L, Moscovitch M (1997). Multiple trace theory.
9. Bartlett FC (1932). Remembering.
10. van Kesteren MTR, et al. (2012). SLIMM: Schema-linear integration of memory model.
11. Kornell N, Bjork RA (2008). Learning concepts and categories: is spacing the "enemy of induction"? Psych Science.
12. Kang SHK, Pashler H (2012). Learning painting styles: spacing is advantageous when it promotes discriminative contrast.
13. Kanerva P (1988). Sparse Distributed Memory. MIT Press.
14. Kanerva P (2009). Hyperdimensional computing.
15. LifeHD (2024). arXiv:2403.04759 — HDC lifelong learning; per-cluster hypervectors + merge/evict.
16. Kleyko D, et al. Long- and short-term memory in VSA/HDC. PMC9869149.
17. Kirkpatrick J, et al. (2017). Overcoming catastrophic forgetting (EWC). PNAS 114:3521-3526.
18. Zenke F, Poole B, Ganguli S (2017). Continual learning through synaptic intelligence. ICML.
19. Lopez-Paz D, Ranzato MA (2017). Gradient Episodic Memory (GEM; BWT/FWT formalism). NeurIPS.
20. Rebuffi SA, et al. (2017). iCaRL. CVPR.
21. Rusu AA, et al. (2016). Progressive Neural Networks. arXiv:1606.04671.
22. Pham Q, Liu C, Hoi S (2021). DualNet: Continual learning, fast and slow. NeurIPS.
23. Grossberg S / Carpenter GA. Adaptive Resonance Theory (stability-plasticity dilemma).
24. Tishby N, Zaslavsky N (2015). Deep learning and the information bottleneck principle. arXiv:1503.02406. [Contested by Saxe A, et al. (2018), ICLR — compression-generalization link did not survive controlled tests.]

**Substrate-internal load-bearing evidence (verified on disk, not lit):**
- `data/exp_crispr_plasticity_slab_replay_v1/metrics.json` — MIDDLE_BAND, forget_p1=0.000 all arms, best transfer_final=0.125 at R=50, cv=0.40.
- `data/exp_substrate_c3_segregated_dual_W_spectrum_replication_v1/metrics.json` — MIDDLE_BAND, forgetting=0.011 vs FUSED 0.678 (delta=0.667), transfer=0.000.
- `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`, `notes/c1_cls_replay_continual_ingest_complete_2026-06-22.md`, `notes/research_continual_learning_architectural_revival_2x_drill_2026-06-24.md`, `notes/research_drill_continual_learning_CRISPR_regime_map_2026-07-01.md` — prior 5x/2x drill chain this memo converges against.
- cap_map v430 `substrate_continual_learning_distshift_v1` HARD_PASS row.

**Lit-scan calibration notes:** all P estimates deflated 0.15-0.25 from raw sub-agent confidence; novel-synthesis P capped at 0.50 (binding for Predictions 1 and 2); HARD-FAIL thresholds stated for every prediction. The MVP claim (no-forgetting) is explicitly NOT subject to the novel-synthesis cap — it is a repeated, confirmed empirical fact across 4 independent substrate cells, not a first-attempt synthesis.
