# 5x CONVERGENCE DRILL: deep-reasoning spec + brain mechanism (constructive build, not vs-LLM)

**Date:** 2026-07-05. **Type:** 5x-DEEPER convergence drill (operational, not fresh lit-scan) on the M3 cortex
reasoning-layer goal. **Framing:** constructive build over our own memory (matches USER 2026-07-05 reframe:
"do not compare us against an LLM... build towards a fully functional substrate with glass-box-LLM
capabilities" — see `notes/director_stage_status_reconciliation_2026-07-05.md` Part 2).
**Discipline:** lit-scan calibration -0.15..-0.25; novel-synthesis P cap 0.50; no-smoke default-deflated
(USER 2026-07-05 ground rule); brain = existence proof (basics proven because the brain does them);
mechanism-analog is NOT task-analog (all "reasoning" here is over synthetic/structured relational codes,
substrate knows nothing general yet).

**Substrate-query-first (what we already have, read before any external search):** this topic has been
drilled HEAVILY in the last 10 days. Six prior memos consulted and NOT repeated, only extended:
`research_5x_drill_brain_reasoning_cortex_emulation_static_algebra_gap_2026-07-04.md` (4 brain mechanisms ->
cortex modules), `research_5x_drill_vsa_reasoning_theory_limits_proven_vs_compute_cost_2026-07-04.md`
(PROVEN vs ASSERTED limit table + compute-cost reclassification), `research_5x_drill_glassbox_cortex_kill_
steelman_proven_wall_test_2026-07-04.md` (no proven wall found against the direction), `research_drill_
differentiating_capability_vs_llm_vectordb_glass_box_cortex_2026-07-05.md` (yesterday's vs-LLM angle, now
explicitly dropped per USER reframe), `inventory_prior_cortex_reasoning_work_build_vs_fresh_2026-07-04.md`
(~40% built, downstream utility HONEST_NEGATIVE), `research_drill_brain_multihop_7mechanism_inventory_
USER_PUSHBACK_2026-06-27.md` (8 brain mechanisms -> 7 substrate retest cell stubs, R1-R5+N1-N2), and today's
`research_drill_glassbox_llm_capability_gaps_build_roadmap_2026-07-05.md` (build-roadmap framing this drill
inherits). **This memo's new contribution: two fresh external lit-scans on the two angles NOT yet covered
in depth (modern ML/DL multi-hop analog; first-principles quantification of error-accumulation-over-depth),
then a single tight A-F convergence synthesis across all five angles + all prior arc work.**

---

## HEADLINE (one paragraph, intuitive)

Five independent angles — neuroscience, cognitive science, VSA math, modern ML, and information theory —
land on the **same mechanism**: reasoning over stored memory works when every hop is followed by a
**regenerative cleanup** (reset the noisy intermediate back to a clean, discrete state) held in a
**separate scratchpad**, not when errors are allowed to compound silently across hops. This is proven
telecom-grade math (a digital repeater resets a signal each hop so noise does not accumulate with distance;
an analog repeater amplifies noise along with signal and degrades with every hop) — and the brain does the
digital-repeater version literally: prefrontal cortex holds intermediates in a **separate persistent-activity
register**, and hippocampal/cortical circuits **clean up** the retrieved item back to a discrete stored
concept at every step, rather than letting each retrieval degrade the next. Modern ML converged on the same
shape from a completely different direction: the best multi-hop QA systems (IRCoT-style) re-ground their
query at every hop instead of retrieving once and reasoning blind, and self-consistency literally is
majority-vote regenerative cleanup applied to whole reasoning chains. Our own substrate already has every
piece of this on the shelf — bind/unbind, a codebook cleanup, a resonator-factorization primitive, a
multi-bank working-memory register, all CHAIN_GRADE or MEASURED_MECHANISM — but has **never run them
composed as "cleanup-after-every-hop" and measured whether that holds accuracy flat across depth**, which
is exactly the decisive, cheap, on-CPU experiment this drill recommends first. The honest quantified limit
is not a "reasoning wall" — it is a **threshold/phase-transition** (below a measurable operating-capacity
line, cleanup holds error flat regardless of depth; above it, no amount of iteration saves you), and our
own single-shot smoke data (K2=1.00, K3=0.733, N=2048/M=30) is the first hint of where that line sits for us
— but it is one seed, one config, and must be swept properly before being trusted as *the* limit.

---

## A. WHAT WE WANT — exact spec + measurable success criteria

Functional-requirement-first (per `[[feedback-functional-requirement-first-test-design]]`):

**The capability:** given a query that requires composing N stored relational facts (a chain
`a1 -R1-> a2 -R2-> a3 -> ... -> a_{N+1}`), the substrate must (1) traverse the chain by algebraic
bind/unbind + cleanup, (2) hold intermediate state in a scratchpad separate from the long-term store so
intermediates don't pollute memory, (3) **refuse** when the evidence chain does not actually support an
answer (broken hop, missing fact, ambiguous branch) rather than emit a confident wrong answer, and (4) stay
**faithful** — the emitted answer must be mechanically traceable to the specific sequence of bind/unbind/
cleanup operations that produced it (not a narrated post-hoc story, which is the well-documented LLM
chain-of-thought failure mode, Part C.4 below).

**MVP (numbers, not vibes):**
- Depth: reliable **3-5 hop** chains. "Reliable" = top-1 accuracy >= 0.50 at depth-5 on held-out chains
  (never-seen combination of stored facts), flat within +/- 0.05 across depths 3/4/5 (NOT the current
  ~0.69-per-hop multiplicative decay regime measured in `research_drill_brain_multihop_7mechanism_
  inventory_2026-06-27.md`, which gives depth-5 ~0.145 and depth-10 ~0.022 — that decay curve is the
  symptom of "no regeneration between hops," see Part C.5).
- Refuse-gate calibration target: false-accept rate (confidently wrong) <= 10% at the operating threshold;
  false-refuse rate (refuses a supported chain) <= 15%; refuse rate should be a MONOTONE function of the
  chain's true evidentiary support, not of depth alone (a well-supported depth-8 chain should refuse less
  than a poorly-supported depth-2 chain).
- Faithfulness definition (operational, testable): for >= 95% of non-refused answers, replaying the logged
  bind/unbind/cleanup trace using ONLY the logged intermediate atoms reproduces the emitted answer exactly
  (bit-identical or cosine >= 0.99 to codebook match). This is "faithful by construction," not observed —
  it is checkable mechanically because every hop is a named algebraic operation over named atoms, which a
  dense-NN hidden state cannot offer (Part E).
- Scale honesty: MVP targets are on SYNTHETIC/structured chains over REAL stored atoms (per USER
  "substrate doesn't know anything, stop testing against language" — mechanism != task).

**"Done" (full, not MVP):** flexible query-driven dynamic composition — the substrate decides WHICH
primitives to sequence (KG-2hop vs depth-N chain-walk vs bidirectional meet-in-middle vs resonator-settle)
per query, rather than a fixed hard-wired pipeline, gated by a goal-representation + PBWM-style control
layer (Part B.2, Part E). This is the M3 "planner" layer; explicitly Phase-2, not MVP.

---

## B. HOW THE BRAIN DOES IT — mechanisms, citations, existence-proof framing

Treated as basics-proven-because-the-brain-does-them (brain = best-in-class existence proof, not a
benchmark to beat). Five load-bearing mechanisms, each previously drilled in more depth
(`research_5x_drill_brain_reasoning_cortex_emulation_static_algebra_gap_2026-07-04.md`,
`research_drill_brain_multihop_7mechanism_inventory_2026-06-27.md`) and restated here at the level needed
for the convergence synthesis:

1. **Separate scratchpad, not shared store.** PFC holds task-relevant intermediates in **persistent
   neural-population activity**, physically/functionally separate from the sensory/episodic store (Miller &
   Cohen 2001, *Annu Rev Neurosci* — PFC cognitive-control theory; Constantinidis & Klingberg 2016, *Nat Rev
   Neurosci* — WM capacity ~4+/-1 items held in dedicated persistent activity, not sensory cortex).
   **Algorithm:** intermediates never overwrite the long-term store; they live in a bounded, separate
   register that is cleared/reused per query.

2. **Cleanup / regeneration at every hop, not accumulation.** Hippocampal pattern completion restores a
   noisy partial cue to the nearest clean stored memory at each retrieval step (Marr 1971; classic
   attractor-network theory; Renart & Brunel 2007 population-code completion). This is the brain's version of
   a **digital regenerative repeater**: reset to a clean discrete state after every hop so noise from hop
   *k* does not propagate into hop *k+1*'s starting point.

3. **Factorized relational code + structural reuse (TEM).** Whittington & Behrens 2020 (*Cell*), the Tolman-
   Eichenbaum Machine: hippocampal/entorhinal memory is a conjunctive code `p = g (x) x` — a learned
   structural/grid code `g` bound to sensory content `x`. This factorization IS a VSA bind, explicitly
   connected to VSA/HRR in Whittington's own follow-on work. It is why the brain can do one-shot transitive
   inference ("Bob's niece") without ever having stored that fact directly.

4. **Recurrent settling to a coherent joint state.** Cortical/hippocampal circuits recombine factorized
   codes via **attractor-network relaxation** — the network settles to the joint interpretation that best
   satisfies all constraints (analogy mapping: Gentner structure-mapping; Hummel & Holyoak LISA; frontopolar
   PFC relational integration, Bunge, Christoff). This is recurrent, not feed-forward-once.

5. **Stop rule = evidence accumulation over time, and sampling not point-estimate.** Decisions are made by
   accumulating noisy evidence until a bound is crossed (drift-diffusion model, Ratcliff 1978; Bogacz et al.
   2006 "physics of optimal decision-making" — decision variance shrinks with accumulation time T, the
   classic speed-accuracy tradeoff), and neural variability itself represents a posterior distribution via
   sampling (Buesing et al. 2011; Orban, Berkes, Fiser & Lengyel 2016) rather than a single deterministic
   argmax — this is how the brain knows WHEN to stop and how it represents "I'm not sure."

**Concrete brain algorithm, stated as pseudocode:** hold query-frame in PFC scratchpad -> probe relational
memory (hippocampal bind/unbind) -> settle a recurrent attractor over the retrieved + scratchpad state
(resolves ambiguity, factors multi-bound structure) -> cleanup to nearest discrete stored concept -> write
clean intermediate to scratchpad, NOT to long-term store -> accumulate evidence across hops until a
confidence bound is crossed (answer) or evidence stays flat/conflicting (refuse) -> offline replay later
consolidates frequently-used chains into a cortical shortcut (schema), so tomorrow's version of the same
query is 1-hop not 5-hop (Tse et al. 2007 *Science*; McClelland, McNaughton & O'Reilly 1995 *Psych Rev*,
Complementary Learning Systems).

---

## C. 5x CONVERGENCE — load-bearing consensus + divergence

### C.1 Systems/computational neuroscience
PFC-scratchpad (separate store) + hippocampal cleanup (regenerative reset) + attractor settling (recurrent,
not static) + replay-consolidation (offline schema formation) + sampling-based stopping. **Converges on:**
depth is handled by iterate-and-clean, not by a bigger single-shot buffer.

### C.2 Cognitive science
Working-memory capacity is famously small and fixed — **4 +/- 1 chunks** (Cowan 2001; Miller's classical
7+/-2 revised down by Cowan's chunking-controlled estimate; Constantinidis & Klingberg 2016). Humans do not
reason over depth-20 chains in one flat pass either — they **chunk** (schema-compress sub-chains into single
units) and **externally scaffold** (write it down — Clark & Chalmers 1998 Extended Mind; Donald 1991).
Analogical/relational reasoning is role-filler binding settled by mutual constraint satisfaction (Gentner
1983 structure-mapping; Hummel & Holyoak 1997 LISA). **Converges on:** the "4-7 item" ceiling is a
single-pass/no-scratchpad limit, routed around by chunking + iteration + external memory — never by holding
more in one register.

### C.3 VSA/HDC theory
Bind/unbind is genuine pointer-chase; cleanup-chained inference is real; **resonator networks** (Frady,
Kent, Olshausen & Sommer, *Neural Computation* 2020, two-part series) are a fully recurrent VSA dynamics
that factors a multi-bound structure by iterative relaxation — this is the VSA-native instantiation of
brain mechanism B.4 (recurrent settling), and it is NOT static/feed-forward, contrary to the common "static
algebra can't do recurrent reasoning" objection. Capacity is genuinely bounded: crosstalk variance scales
~K/D (Plate 1995 HRR analysis; confirmed across Kanerva 2009, Frady/Kleyko/Sommer surveys), and resonator
factorization has its own **operational-capacity phase transition** — below it, iterative relaxation reliably
decodes; above it, convergence time diverges (critical slowing down) and no amount of iteration recovers
the answer (Kent et al., measured). **Converges on:** VSA supplies both the memory-half (bind/unbind =
factorized code) AND an engineerable recurrent-settling core (resonators) — the "static algebra" framing of
the problem was a red herring; the real bounded resource is a per-hop SNR budget you can spend (grow D,
iterate) up to a threshold cliff.

### C.4 Modern ML/DL analog
**IRCoT** (Trivedi et al., ACL 2023) interleaves chain-of-thought generation WITH retrieval — each reasoning
step triggers a fresh, re-grounded retrieval instead of retrieving once and reasoning blind. This solves
exactly the brain's "cleanup between hops" problem from a different direction: don't let stale/wrong
intermediate state silently propagate. Failure mode when this ISN'T done: "lost-in-retrieval" and
irreversible early-hop errors (arXiv:2502.14245); a 2026 diagnostic (arXiv:2601.19827) shows degradation
scales with hop count independent of context size — confirming it's a reasoning-chain problem, not a
memory-capacity problem (single-paper, not yet broadly replicated). Neuro-symbolic architectures (GNN
message-passing, memory-augmented nets like DNC/NTM) hit an analogous **depth ceiling from over-smoothing**
— 2-4 layers before node representations collapse (arXiv:2502.04591, well-established, many replications) —
mirroring our own measured single-shot binding-depth cliff (J=32-64). Chain-of-thought **faithfulness** is a
live, quantified, unsolved LLM problem: verbalized reasoning steps frequently do NOT drive the actual answer
(Lanham et al. 2023, arXiv:2307.13702; unlearning-based faithfulness metrics, arXiv:2502.14829, EMNLP 2025 —
"unfaithful shortcuts" widespread across Claude/DeepSeek-R1/Qwen). Self-consistency (Wang et al. 2022) —
sample multiple reasoning paths, majority-vote — is literally regenerative cleanup applied at the
whole-chain level: independent errors decorrelate, the shared correct path survives voting. Recent
(single-paper, 2026) work reports **calibration error increases with reasoning depth** for uncorrected LLM
chains (arXiv:2506.18183) — longer uncorrected chains produce MORE confident wrong answers, not less.
**Converges on:** the exact same shape as neuroscience/VSA — re-ground/clean up at every step beats
carrying state blind, and mechanical (bind/unbind-traceable) faithfulness is a real, currently-missing
capability in the LLM world that our architecture gets "for free" by construction, not by training a
verifier on top.

### C.5 First-principles / information theory
**Two proven textbook regimes, cleanly separated:**
- **No correction between hops (Markov chain, data-processing inequality):** `I(X;Z) <= min(I(X;Y),I(Y;Z))`
  — information is monotonically non-increasing with hops (Cover & Thomas). Combined with Fano's inequality
  this is exactly the multiplicative `(1-eps)^K` decay our own multi-hop cells measure (depth-5 ~0.145,
  depth-10 ~0.022 per-hop ~0.69 floor). This is PROVEN and is the "analog repeater" regime — noise amplifies
  with distance.
- **Regeneration at every hop:** digital regenerative repeaters reset the signal to a clean codeword at
  every hop, so **noise does not accumulate with chain length at all** — reliability becomes near-independent
  of depth, at the cost of needing enough per-hop SNR margin to regenerate correctly. Forney (1966,
  concatenated codes) proved exponentially-decreasing error with only polynomial decoding cost, for any
  rate below capacity. LDPC/belief-propagation decoding (Richardson-Urbanke density evolution) shows the
  concrete shape of the "wall": a sharp noise **threshold** — below it, more iteration drives error to zero;
  above it, decoding fails regardless of resources. Evidence accumulation over time (drift-diffusion, Wald's
  SPRT — provably optimal) is the classic account of buying precision with time/samples rather than
  depth. **Direct answer to "is depth a real wall": NO universal wall specific to compositional/chained
  reasoning exists.** It is a cost curve, paid down by per-step regeneration (cleanup/codebook/majority
  vote), PROVIDED each step's effective channel operates below ITS OWN capacity/noise threshold. Where a
  real wall appears, it is not depth-specific — it is the per-step threshold (LDPC/resonator phase
  transition) or universal limits (Shannon capacity, P-vs-NP worst-case hardness, undecidability) that bind
  every computer and the brain equally.

### CONVERGENCE (the load-bearing consensus, all 5 angles independently)
**Chunk + regenerate-at-every-hop (cleanup/codebook-reset/majority-vote), held in a separate scratchpad,
with a calibrated stop rule, is the mechanism.** Every angle arrived at this from a completely different
literature: neuroscience (PFC scratchpad + hippocampal pattern-completion), cognitive science (chunking
beats the 4-7 item ceiling), VSA theory (resonator settling + cleanup between hops), modern ML (IRCoT
re-grounding + self-consistency voting), information theory (digital regenerative repeater vs analog
decay — the formal proof that this pattern, not raw compute, is what breaks the multiplicative-decay
curve). **Divergence:** the angles disagree only on WHERE the resource-provisioning cliff sits and how
sharp it is (VSA/info-theory say it's a phase transition; cognitive science's 4-7 number is softer/empirical;
ML's depth-vs-context-size independence claim is single-paper/preliminary). None of the five angles produced
a reason to doubt the convergent mechanism itself.

---

## D. AUGMENT BEYOND BIOLOGY (where high-energy compute exceeds the brain's single-pass limit)

Per USER-locked "high-energy non-bio compute is allowed; bio-efficient is baseline+proof, not a constraint"
(`feedback_high_energy_nonbiological_compute_allowed_brain_is_baseline_and_proof_not_constraint_2026-07-05.md`):

- **Dimension:** brain's WM is ~4-7 chunks; the substrate already runs at N=8192-16384 with WM multi-bank
  K=4096-8192 (CHAIN_GRADE) — no reason to artificially cap scratchpad slots at biological WM size. Grow D
  and bank count until the resonator/cleanup operating margin (Part C.3/C.5) is comfortably below threshold.
- **Iterate resonators to convergence, not real-time-constrained.** Biological settling happens in ~100s of
  ms; we can run resonator relaxation for as many iterations as needed (annealing, restarts, multiple
  initializations) since there's no real-time deadline — trading wall-clock for reliability near the
  capacity cliff.
- **Many-candidate parallel search.** Brain settles to ONE attractor per query (mostly); we can run K
  parallel resonator restarts / bidirectional forward+backward searches (Part R3 below) and take the
  consensus — a direct compute-for-reliability trade with no biological analog constraint.
- **Backprop-trained cleanup/gating**, where the brain uses local plasticity rules only. A learned M-CFU
  importance signal or a learned gate for what enters the scratchpad (PBWM-inspired, but gradient-trained
  rather than dopamine-gated) can outperform hand-designed heuristics — while the fallback (Hebbian
  outer-product, no-gradient) stays available as the efficient/interpretable baseline.
- **Explicit error-correcting redundancy** (concatenated-code-style, dense-float intermediate precision) —
  the brain's spikes are noisy by necessity; we can hold dense float32 intermediates and add deliberate
  redundancy (multiple independent codebook checks per hop) the way engineered systems do and biology cannot
  afford metabolically.
- **Complete, exact provenance logging.** The brain cannot fully introspect its own attractor dynamics;
  every one of our hops is a named operation over named atoms and can be logged exactly — this is a
  capability compute gives us for free that has no biological equivalent, and it is the actual product
  differentiator (mechanical faithfulness, Part A).
- **Keep the efficient-biological version as the explicit fallback baseline**, not a constraint: single-pass,
  ~4-7 item scratchpad, one resonator pass, Hebbian-only learning — this is the cheap/interpretable/
  low-power regime to fall back to when the high-energy version isn't warranted, per USER standing rule.

---

## E. SUBSTRATE FIT + FIRST BUILD

**What we have, verified off-disk (per Fix#28 discipline, not narrated):**
- `hdlab/cortex.py` (763 lines) — composed facade (NoiseChannel + refuse_gate + TwoTierContext +
  chunked_attention router + RoleSlotSummarizer + ClarifyGate). CG at the integration/plumbing level
  (`EXP_cortex_integration_end_to_end_v1` 3-seed FULL CHAIN_GRADE) — certifies the composition preserves the
  bind/unbind algebra, NOT that it improves task performance. Downstream-utility probe
  (`EXP_cortex_task_analog_downstream_v2b`) is **HONEST_NEGATIVE**: composition alone does not yet help.
- `hdlab/atom_consultation.py` (978 lines) — the "active constraints" Cortex-2 layer, MM_TENTATIVE, PARKED
  behind the encoder (advisory match-and-honored 0.80; dose-response stable; LIVE-mode enforcement unbuilt).
- Deep CG sub-capability bench: refuse-gate/self-audit device, KG 2-hop inference-transfer on real datasets
  (ConceptNet, FB15k-237, HotpotQA 1k-dev), depth-5 compositional chains, WM multi-bank K=4096-8192, TWO_TIER
  hippocampal/cortical separation primitive, `resonator_factorization_v1` (measured: K2 success 1.00, K3
  success 0.733 at N=2048, M=30 — **single-shot smoke, run_mode=smoke, n_seeds=1, 0.31s**, not yet a proper
  multi-seed FULL sweep).
- Encoder essentially DONE (GSBC_EXPAND2X, MM_STANDARD, all 4 USER goals met, teacher-dependent on BGE) —
  the gating dependency for feeding the cortex real (not purely synthetic) content is close to clearing
  (integration-verify in flight per `director_stage_status_reconciliation_2026-07-05.md`).

**The exact gap (not "everything," specifically):**
1. **Cleanup-between-hops has never been run as the explicit reasoning-core primitive and measured for
   depth-flatness.** Every prior multi-hop cell (pointer-chain v1/v2, WM-scaffold v1, CSP-gated v1) either
   used a SHARED store for intermediates (crosstalk pollution) or hard-argmax per hop with no regenerative
   reset — i.e., they tested the "analog repeater" regime, not the "digital regenerative repeater" regime
   that C.5's information theory and B.2's brain mechanism both say is the load-bearing difference. This is
   a genuine, previously-undrilled combination despite ~20 prior multi-hop cells.
2. **Recurrent settling (resonator loop) is VSA-native but NOT YET wired as the cortex's control core** —
   engineerable, not a theory gap (C.3).
3. **The learned-structural-code / learned-schema-attractor gap remains the one FUNDAMENTAL-feeling limit**
   (our R-codebook is random + Hebbian-only, not gradient-learned like TEM's grid code `g`) — this is what
   blocks cross-domain generalization specifically, NOT within-domain chaining, which is this drill's MVP
   target. Correctly out of scope for the MVP spec in Part A.

**The single most decisive next experiment (cheap, on-CPU, directly tests the C.5-convergent mechanism):**

`exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1` — one cell, depth-scaling sweep, isolating exactly
the mechanism all five angles converged on.

- **Arms:** (A) ANALOG_ACCUMULATE — current pointer-chain, no cleanup between hops (reproduces the known
  0.69-per-hop decay curve; this IS the sanity rail). (B) REGENERATIVE_CLEANUP — identical chain-walk, but
  after every hop's unbind, snap the noisy intermediate to its nearest codebook atom (cleanup) BEFORE using
  it as the next hop's input, held in a scratchpad bank separate from the main store (per Part B.1/C.1). (C)
  REGENERATIVE_CLEANUP_SCRATCHPAD_ISOLATED — same as B plus an explicit audit that zero writes touch the
  main store during the walk (tests B.1's "separate register" claim, not just cleanup).
- **Primary metric:** depth-flatness — accuracy at depth-5 minus accuracy at depth-3 for arm B/C should be
  within 0.05 (near-flat), vs arm A's known ~0.35 drop across the same range.
- **HARD-PASS:** arm C depth-5 >= 0.45 AND (depth-3 minus depth-5) <= 0.10 AND scratchpad-isolation audit
  clean (zero main-store writes) AND reproducible across >= 3 seeds.
- **HARD-FAIL:** arm C depth-5 <= 0.20 OR (depth-3 minus depth-5) >= 0.30 (cleanup doesn't flatten the
  curve — the regenerative-repeater analogy fails to transfer to our substrate's actual crosstalk
  structure) OR arm C is statistically indistinguishable from arm A (cleanup adds nothing).
- **Discriminator-must-survive-scale:** smoke at full N (8192), full V_C, depth up to 7, must show arm C
  beating arm A by >= 0.15 at depth-5 or abort before FULL dispatch.
- **P_deflated: 0.45** (raw ~0.65 — cleanup-between-hops is a textbook-proven mechanism in both the
  information-theory and brain literatures, and the substrate already has a working cleanup/codebook
  primitive; -0.20 novel-synthesis for combining scratchpad-isolation + per-hop-cleanup in one cell for the
  first time; capped per novel-synthesis-P<=0.50 rule). This is deliberately CHEAPER and more info-theory-
  direct than the previously-filed `cortex_resonator_boundary_noise_v1` cell (2026-07-04) — it isolates the
  single mechanism this drill converged on before adding resonator recurrence or stochastic noise on top.
  If it HARD-PASSes, `cortex_resonator_boundary_noise_v1` becomes the natural follow-on (adds recurrent
  settling + sampling on top of a now-validated regenerative-cleanup core).

---

## F. HONEST RATING (no smoke, deflated default)

- **Static algebra alone as an autonomous reasoner: MEDIOCRE.** Real primitives (bind/unbind/cleanup) but
  bounded and shallow without the regenerative/scratchpad discipline — this rating is unchanged from
  yesterday's VSA-theory drill and stands.
- **Substrate + regenerative-cleanup + separate scratchpad (the convergent brain-grounded mechanism): GOOD,
  and cheaply testable.** No proven wall stands against it; the mechanism is independently derived from five
  unrelated literatures, which is unusually strong convergence for a research synthesis. The gap to close is
  a specific, named, cheap experiment (Part E), not an open-ended research program.
- **Proven vs. speculative, explicitly split:**
  - **PROVEN (textbook, multi-decade, not our claim to defend):** data-processing inequality / cascaded
    channel decay without correction (Cover & Thomas); digital-repeater regeneration defeats depth-decay
    (classic information theory); Plate/HRR crosstalk ~K/D scaling; LDPC/resonator operational-capacity
    phase transition (Richardson-Urbanke; Kent et al. — measured, not asserted); human WM ~4+/-1 item
    single-pass capacity (Cowan 2001, many replications); GNN over-smoothing 2-4 layer depth ceiling
    (arXiv:2502.04591, well-replicated).
  - **SPECULATIVE / UNPROVEN ON OUR SUBSTRATE:** whether regenerative cleanup actually flattens OUR
    depth-accuracy curve at OUR N/codebook size (Part E's decisive experiment has not run yet); whether
    boundary-noise/sampling helps disambiguate on OUR substrate (P=0.40, prior cell not yet dispatched);
    the learned-schema/cross-domain generalization gap (Part E point 3) remains genuinely unsolved, not
    merely untested.
- **Is there a PROVEN wall?** No proven wall against compositional depth itself. The one thing that IS a
  proven, quantifiable limit is the **operating-capacity threshold** (phase transition): below it,
  regeneration holds error flat regardless of depth; above it, no iteration or redundancy saves you. This is
  a provisioning rule (build below the cliff), not a depth ceiling — and per the brain-violation test
  (USER anchor A1), the brain itself operates well below its own analogous cliff (chunking to 4-7 items,
  never flat-superposing everything) which is further evidence this is a design constraint, not a wall
  against the goal.
- **Quantifying the candidate real limit (error-accumulation-over-depth), honestly:** WITHOUT correction,
  our own measured multi-hop cells show per-hop degradation consistent with a ~0.69 floor (depth-5 ~0.145,
  depth-10 ~0.022 — the "analog repeater" regime, matches the proven `(1-eps)^K` decay exactly). WITH
  correction, the closest data point we have is `resonator_factorization_v1`'s K2=1.00/K3=0.733 at N=2048,
  M=30 — a single-seed SMOKE run, not a swept, multi-seed FULL result. That is the honest state: we have a
  PROVEN mathematical reason to expect regeneration flattens the curve, and one small unswept data point
  consistent with a threshold appearing somewhere between K=2 and K=3 at that specific N/M — but we do NOT
  yet have the swept, reproducible measurement of where OUR threshold sits at production N/depth. That
  measurement is exactly what Part E's decisive experiment produces.
- **"Field stalled" is explicitly NOT treated as proof** (per the 07-04 steelman drill's own finding, carried
  forward unchanged): Eliasmith's ABR commercial pivot and the field's 30-year non-delivery of a
  differentiating reasoning application are field-history/market observations, not information-theoretic
  bounds, and are excluded from this rating by design.

---

## Cheap decisive test (summary, per role-contract required section)

See Part E: `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1`, 3 arms, depth-flatness metric,
P_deflated=0.45, cheaper and more mechanism-isolating than the prior resonator+noise cell, and it directly
tests the single convergent finding of this 5x drill.

## Falsifiable predictions

- **HARD-PASS:** regenerative-cleanup arm holds depth-3-to-depth-5 accuracy within 0.05 (near-flat) at
  >= 0.45 absolute, with a clean scratchpad-isolation audit, reproducible across >= 3 seeds.
- **HARD-FAIL:** cleanup does not flatten the curve (drop >= 0.30 across the same depth range) OR is
  statistically indistinguishable from the no-cleanup baseline — this would falsify the transfer of the
  regenerative-repeater/brain analogy to our substrate's specific crosstalk structure and would be a
  genuinely important negative (would mean our crosstalk is NOT well-modeled by the textbook K/D scaling,
  worth its own follow-up drill).

## Cross-thread synthesis

Extends (does not repeat): the 07-04 brain-grounding drill (four brain mechanisms -> cortex modules), the
07-04 VSA-theory drill (PROVEN vs ASSERTED limit table), the 07-04 steelman drill (no proven wall against
the direction), the 06-27 mechanism-inventory drill (7 cell stubs R1-R5/N1-N2, several of which — R2 PFC-
scratchpad, R4 recurrent-attractor-per-hop — are subsumed/sharpened by this drill's single decisive
experiment), and today's build-roadmap drill (generation as the largest gap; reasoning as the current
frontier). The NEW contribution here is the information-theory quantification (regenerative-repeater vs
analog-repeater as the formal frame for "why cleanup-between-hops matters") and the modern-ML convergence
point (IRCoT re-grounding, self-consistency voting, CoT-faithfulness literature) that were not previously
tied together with the brain/VSA angles into one mechanism.

## Substrate-product implications

1. The mechanical-faithfulness property (Part A) is a genuine, currently-unclaimed-by-LLMs capability —
   CoT faithfulness is a live unsolved problem in the LLM literature (Part C.4); our architecture gets a
   checkable version of it by construction once cleanup-between-hops is wired in. This is a legitimate
   product angle IF the decisive experiment lands, independent of any vs-LLM competitive framing (which
   stays dropped per USER 2026-07-05).
2. Do not oversell "recurrent processing is missing" — resonator networks are VSA-native recurrence,
   already on the shelf; the actual gap is narrower and cheaper to close than "build a whole new dynamics."
3. Sequence: run the regenerative-cleanup cell (Part E) BEFORE the previously-filed resonator+boundary-noise
   cell — it isolates one mechanism at a time, cheaper, and directly informs whether the boundary-noise cell
   is worth its added complexity.
4. Keep the learned-schema/cross-domain gap explicitly OUT of MVP scope (Part A) — it is real and unsolved,
   but conflating it with the within-domain depth-chaining goal has caused scope-creep in past drills.

## Citations (verified count: 24 distinct sources across 5 angles, all traceable to author/year/venue or arXiv ID)

Neuroscience/cognitive (9): Miller & Cohen 2001 (*Annu Rev Neurosci*); Constantinidis & Klingberg 2016
(*Nat Rev Neurosci*); Cowan 2001 (WM capacity); Whittington & Behrens 2020 (*Cell*, TEM); Gentner 1983 /
Hummel & Holyoak 1997 (LISA); Tse et al. 2007 (*Science*); McClelland, McNaughton & O'Reilly 1995
(*Psych Rev*, CLS); Buesing et al. 2011 / Orban, Berkes, Fiser & Lengyel 2016 (sampling); Ratcliff 1978 /
Bogacz et al. 2006 (drift-diffusion).
VSA/HDC (3): Plate 1995 (HRR); Frady, Kent, Olshausen & Sommer 2020 (*Neural Computation*, Resonator
Networks 1&2); Kanerva 2009 / Frady-Kleyko-Sommer capacity surveys.
Modern ML/DL (7): Trivedi et al. 2023 (IRCoT, ACL); arXiv:2502.14245 (lost-in-retrieval); arXiv:2601.19827
(hop-count-independent-of-context diagnostic, single-paper); arXiv:2502.04591 (GNN over-smoothing); Lanham
et al. 2023 arXiv:2307.13702 (CoT faithfulness); arXiv:2502.14829 EMNLP 2025 (faithfulness-by-unlearning);
Wang et al. 2022 (self-consistency); arXiv:2506.18183 (calibration-vs-depth, single-paper).
Information theory (5): Cover & Thomas (data-processing inequality, textbook); Forney 1966 (concatenated
codes); Richardson & Urbanke (LDPC density evolution / threshold); Wald 1945 (SPRT); digital-vs-analog
regenerative repeater (standard telecom theory).
On-disk/measured (own substrate, not literature): `data/exp_resonator_factorization_v1/metrics.json`
(K2=1.00, K3=0.733, N=2048, M=30, smoke); multi-hop pointer-chain depth curve (~0.69/hop, depth-5 ~0.145,
depth-10 ~0.022, per `research_drill_brain_multihop_7mechanism_inventory_2026-06-27.md`).

---
-- Research (Director), 5x convergence drill; deflated-honest; constructive-build framing (vs-LLM dropped
per USER 2026-07-05); substrate-query-first (6 prior memos extended, not repeated) + 2 targeted external
lit-scans (modern-ML analog, info-theory quantification) dispatched to fill the two least-covered angles.
