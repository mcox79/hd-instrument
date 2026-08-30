# Research drill — brain mechanism for a per-agent belief timeline ("what did A know when")

Date: 2026-08-29 · Author: research sub-agent (Opus) · Type: ONLINE literature scan
Calibration note: this is a lit-scan. P-estimates deflated 0.15–0.25; novel-synthesis capped at 0.50. Where the literature is genuinely mixed I say so and hand you a can-fail discriminator rather than a verdict.

## One-paragraph orientation
Your design is **mostly right at the computational (Marr level-1) level and wrong in KIND at the storage/algorithmic level.** The brain does NOT keep an equally-accessible dense per-time belief register that it reads at T. It keeps a richly-stored **CURRENT** per-agent belief (situation-model updating) plus **sparse, time-tagged observation events**, and it **RECONSTRUCTS** any *past* belief on demand — and that reconstruction is **systematically corrupted by current knowledge** (hindsight bias / curse of knowledge). Your sample-and-hold step function is the correct *idealized readout*; it is not how the substrate is stored. The single most load-bearing correction: **the agent-belief store must be architecturally DECOUPLED from the world/reality store** — that decoupling (not inertia) is where the brain's robustness lives, and it is also where the brain's failures come from.

---

## Q1 — STORED TRAJECTORY vs ON-DEMAND SIMULATION (the biggest fork)

**VERDICT: needs-correction. The brain is (c) hybrid, tilted toward reconstruction for PAST queries. A dense stored belief-timeline read at T is NOT brain-faithful; store sparse update-events + current state, reconstruct the past.**

What the evidence actually says:
- **Situation-model / event-indexing (Zwaan & Radvansky 1998; Radvansky & Zacks 2011).** Readers maintain a *current* situation model, updated incrementally at event boundaries along ~5 indices (time, space, entities, causation, intentionality/protagonist goals). What is *maintained* is the CURRENT state, not a full trajectory. fMRI: the **posterior-medial network** (PMN: hippocampus, angular gyrus, posterior cingulate, retrosplenial, mPFC) carries this updating for *all* dimensions (recent naturalistic-reading fMRI coding cause/character/goal/object/space/time — posterior-medial areas show the most robust updating).
- **The "here-and-now" dominance (Anderson, Garrod & Sanford 1983; Glenberg et al. 1987; Rinck & Bower).** The *current* protagonist state is most accessible; **prior states are demoted/less accessible** and accessibility tracks the protagonist's *current* situation, not recency of mention. So there is no equally-readable past register — the brain actively down-weights superseded states.
- **Memory-based / resonance processing (O'Brien, Rizzella, Albrecht & Halleran 1998; Myers & O'Brien).** Backgrounded/outdated/false info is **not held active on purpose**; it is *passively reactivated by resonance* when it shares features with current working-memory contents. Past belief states are cue-reconstructed, not indexed-and-read.
- **Constructive episodic simulation / scene construction (Schacter & Addis 2007; Hassabis & Maguire 2007; Addis et al. 2007).** Remembering a past episode (hence "what A knew then") is *constructive* — reassembled from elements via hippocampal pattern-completion, not replayed from a stored tape.
- **The clincher against a clean stored register (Fischhoff 1975; Birch & Bloom 2007).** If past belief were a stored value read at T, later knowledge could not corrupt it. It systematically does (see Q5). That is direct evidence *for* reconstruction and *against* a read-only trajectory.

**What to BUILD/CHANGE:** store the belief timeline as **sparse, time-tagged observation/update EVENTS per (agent, fact)** + a maintained CURRENT value; answer "what did A know at T" by **retrieving the most-recent update-edge before T** (a query, not a table read). Your dense piecewise-constant step function is the *ideal readout of* that sparse event store, not the store. This is cheaper, it is what enables the graded/confidence layer, and it naturally predicts the human failure mode.

---

## Q2 — PERSISTENCE: sample-and-hold vs decay vs reality-overwrite

**VERDICT: PINNED at the computational level (default-persistence/temporal inertia is the right model) BUT needs-correction — attributed belief is NOT held as cleanly as a physical state; it leaks toward reality and its ACCESS decays.**

- **Default-persistence is the right level-1 model, and it is the *same* principle physical states use.** Dowty's (1986) **temporal inertia** (states persist by default across the narrative "now" unless an event changes them) is the linguistic form; the AI form is McCarthy & Hayes' **common-sense law of inertia** / the **frame problem** (Dean's "rule of persistence"; Shanahan's *Solving the Frame Problem*; the Yale-shooting cautionary case). Discourse semantics carries this via Reichenbach's **reference time R** advanced across sentences (Kamp DRT; Partee). So invoking Dowty + frame-problem inertia for the belief register is defensible and **PINNED**.
- **But attributed belief differs in KIND from location/possession in two ways:**
  1. **Reality-intrusion / egocentric leak (curse of knowledge; Birch & Bloom 2007; Keysar et al. 2003; Samson's altercentric intrusions).** The default pressure is for the comprehender's *own current knowledge* to overwrite the attributed belief. A physical location is never "overwritten" by anything; a stale belief is under constant pressure to be overwritten by reality. False belief is *effortfully maintained against* that leak — which is exactly why false-belief is later-developing than knowledge-access and is inhibition-dependent, not representation-limited.
  2. **Access decays, value does not.** Time-since-last-update degrades *retrievability/confidence*, not the stored content (ordinary interference/decay). This matches your rep-B-as-confidence intuition.

**What to BUILD/CHANGE:** keep sample-and-hold for the *value*, but (a) add an explicit **anti-intrusion decoupling** so a world/reality update can never silently rewrite an agent-belief slot (see Q5, the #1 directive), and (b) attach a **confidence that decays with time-since-last-update** (recency), leaving the value constant. Do NOT model belief as decaying toward reality *by default* — the brain does that as a *bug*, and you almost certainly want the clean version (this is a place you can legitimately beat the brain; see Q5).

---

## Q3 — TEMPORAL BINDING: discrete event-model (rep A) vs graded temporal-context (rep B)

**VERDICT: PINNED. Your split is well-matched to the brain, and your expectation (discrete adequate for the value; graded = confidence/recency, not accuracy) is consistent with the evidence — with one refinement: rep B is not strictly dominated by rep A.**

- **The belief VALUE and its change-points are DISCRETE and event-based.** Event segmentation (Zacks, Speer, Swallow & Reynolds 2007; Kurby & Zacks 2008) and the event-indexing model say updating happens at **event boundaries**, not continuously. So rep A (discrete "sample-and-hold" intervals) is the accuracy-bearing representation for *what* is believed and *when it changed*.
- **"When did A last witness it / how recently" is GRADED.** Howard & Kahana's **Temporal Context Model** (2002; Sederberg et al. 2008) + hippocampal **time cells** (MacDonald et al. 2011; Eichenbaum 2014) implement a slowly-drifting context vector; temporal localization is *approximate*, with a forward-asymmetric contiguity gradient. This is exactly a lossy, graded recency/confidence signal — rep B.
- **Refinement:** rep B carries information rep A lacks — **order-uncertainty near boundaries** ("was A's observation before or after the theft?") and **staleness magnitude**. Treat B as the recency/confidence/**order-uncertainty channel**, not merely a lossy copy of A. Your FHRR temporal-context superposition is a good implementation of the drifting-context idea.

**What to BUILD/CHANGE:** (i) **derive the discretization grid from event boundaries** (align belief-update change-points to segmented events, per Zacks) rather than per-token; (ii) keep rep A as the value/change-point truth layer and rep B as the graded recency/confidence/order-uncertainty layer; (iii) when rep A gives a crisp interval but two events are near-simultaneous, let rep B express the order *uncertainty* rather than forcing a false crisp order.

---

## Q3b — Is it a COMPOSITION of two systems, or one integrated event-model?

**VERDICT: PINNED-faithful as a composition — with the load-bearing caveat that the two systems must be BOUND at event boundaries.**

- **Neural dissociation supports composition.** The **mentalizing network** (bilateral TPJ, mPFC, precuneus; Saxe & Kanwisher 2003; Schurz et al. 2014 meta-analysis "Fractionating theory of mind") is dissociable from the **episodic/temporal MTL–PMN system** (hippocampus + posterior-medial network; Howard/Eichenbaum). RTPJ carries belief *content*; hippocampus carries **event-specific temporal binding**; mPFC generalizes across schema/event-type. Impaired **RTPJ–hippocampus connectivity** degrades other-mind representation (schizophrenia work). So belief-attribution and event-ordering are genuinely separable systems — validating your compositional design.
- **BUT the event-indexing account treats the protagonist/intentionality dimension as ONE index of a SINGLE integrated event model**, and Apperly & Butterfill's efficient system tracks belief-like states *inside* fast processing. Reconciliation: **separable neural systems integrated/bound via the event model (PMN/hippocampus as the binding hub).** The hippocampus binds *who-believed-what* to *when* at event boundaries.

**What to BUILD/CHANGE:** build the composition (ToM system × temporal-order system) — but make the **BINDING explicit**: bind `belief_content ⊗ temporal_context` **at event boundaries**. This is precisely the job of your FHRR bind, and it is where the two systems become one queryable timeline. Do not leave belief and time as two unbound registers; the brain's integration site is the bind.

---

## Q4 — DRAMATIC IRONY / DECEPTION / STALE BELIEF; parallel states; capacity

**VERDICT: PINNED. The brain maintains PARALLEL per-agent knowledge states and actively tracks the reader–character GAP; capacity is limited, and the limit bites on RECURSION, not on first-order parallelism.**

- **Parallel states are actively maintained.** Dramatic-irony work (Bruckert/Levine-style eye-tracking; "The audience who knew too much," *Frontiers in Psychology* 2023; "**Viewers Actively Extract and Maintain** Spontaneous Theory-of-Mind Representations in Dramatic Irony Scenes," 2025) shows viewers hold the character's *outdated/false* knowledge state **in parallel with** their own superior knowledge, and the belief-discrepancy shapes **real-time attention and prediction**. This directly supports (a) parallel per-agent tracks and (b) the stale character belief being *actively held*, not overwritten.
- **The decision-relevant quantity is the GAP.** Dramatic irony = reader-knows-p ∧ character-believes-¬p; suspense/deception are computed over `belief_A vs reality` and `belief_A vs belief_B` — the substrate should compute the *difference*, not just per-agent states.
- **Capacity:** first-order per-agent beliefs — several can be tracked, organized around protagonists (character-indexed situation models; Cowan's ~4-item WM bound as a soft ceiling). **Recursion is the hard limit:** humans degrade sharply beyond ~2nd order and only reach ~4th–5th with effort (Kinderman, Dunbar & Bentall 1998; Stiller & Dunbar 2007; mirrored by the Hi-ToM LLM benchmark). Relational-complexity theory (Halford) explains why: each embedding adds re-entrant binding load.

**What to BUILD/CHANGE:** represent an explicit **reader/omniscient track** alongside per-agent tracks and make the **gap** a first-class query; expect and *test* graceful degradation with number of agents and (especially) recursion depth.

---

## Q5 — BOUNDS / WALLS (a rigorous, brain-grounded negative = a full pass)

**Wall 1 (biggest): past-belief reconstruction is systematically biased by current knowledge — HINDSIGHT BIAS / CURSE OF KNOWLEDGE.**
- Finding: Fischhoff (1975) creeping determinism; Birch & Bloom (2007) *Psych Science* — adults' knowledge of the true outcome contaminates their judgment of what an agent believed *before* they knew it (Vicki/violin: bias scales with perceived plausibility). Mechanism model: **SARA — Selective Activation and Reconstructive Anchoring** (Pohl, Erdfelder): current knowledge acts as an *anchor* on reactivated memories.
- **Why the brain succeeds when it does:** it maintains a **decoupled** agent-belief file (TPJ/mentalizing) and **inhibits** the reality intrusion (executive/inhibitory control — the reason 3–4-yr-olds fail is inhibitory immaturity, not representational lack). **Build across the gap:** keep the agent-belief store **strictly decoupled** from the world store; a world-state update may write an agent slot **only** via an explicit observed/communicated edge. A software store has no leak by default → **you can legitimately beat the brain here** (no curse of knowledge). *This is your #1 build directive and also your best can-fail control:* a correct reader must NOT let a later world-change contaminate its answer to "what did A believe at T." If it does, you have a leak = bug; if a brain-faithful reconstruction is your goal instead, you would deliberately *add* the anchor. Decide which, and test for it.

**Wall 2: higher-order/recursive ToM is capacity-limited (~2 orders robust).** Stiller & Dunbar 2007; Kinderman et al. 1998; Hi-ToM. Why: WM/relational-complexity (Halford). Build-across: nest beliefs as explicit nested belief files keyed by `(holder, about=<agent,fact>)`; a software store can exceed the human cap — **OUR-INVENTION-acceptable to beat the brain**, but validate that nesting doesn't blow up combinatorially.

**Wall 3: the identity/intensionality signature limit (Apperly & Butterfill 2009; Butterfill & Apperly 2013 "minimal ToM").** The efficient system CANNOT track beliefs that hinge on mistaken identity (Lois Lane believes Superman flies but not that Clark does — same referent). **If your belief facts are keyed by world REFERENT, you reproduce this exact failure.** Build: key beliefs by the agent's **mode-of-presentation/guise**, not referent alone, wherever intensional contexts matter. (You can beat the human efficient system here too, but only if you key intensionally.)

**Wall 4 (a correction to your "observed events only" rule): belief also updates on INFERENCE and COMMUNICATION/TESTIMONY.** "Seeing leads to knowing" (Pratt & Bryant 1990) is a *knowledge-access* competence — necessary but not sufficient. Deception specifically requires that an agent can *cause* a false belief in another via a (possibly false) assertion. Build: add update-edge TYPES — `observed(world-state)`, `inferred(from premises)`, `communicated(asserted content, which may be false)`. Deception = assert p while believing ¬p; testimony = A tells B p ⇒ B believes p ∧ A believes B-believes-p.

**Also correct — factive vs defeasible:** distinguish **KNOWS(A,p)** (factive, from observation, true) from **BELIEVES(A,p)** (defeasible, persists, can be false). *Stale/false belief is exactly an old KNOWS persisting as a now-false BELIEVES after an unobserved world change.* Model the transition explicitly: observe at t1 → world changes unobserved at t2 → at t3 the register still holds p (now false). That transition IS your use-case; make it a named edge.

---

## RANKED concrete design changes (most load-bearing first)

1. **DECOUPLE the agent-belief store from the world/reality store.** A world update may write an agent slot **only** through an explicit observed/communicated edge. This defeats curse-of-knowledge, is the brain's robustness mechanism, and is your #1 can-fail control. (Q2, Q5-Wall1)
2. **Store sparse time-tagged update EVENTS per (agent, fact) + current value; answer "knew at T" by retrieving the most-recent edge before T.** The dense step function is the *readout*, not the storage. (Q1)
3. **Align belief change-points to EVENT BOUNDARIES (event segmentation), not per-token.** (Q3)
4. **Add update-edge TYPES: observed / inferred / communicated(may-be-false).** Enables deception + testimony; fixes "observation-only." (Q5-Wall4)
5. **Distinguish factive KNOWS from defeasible BELIEVES; model stale belief as old-KNOWS-persisting-as-now-false-BELIEVES.** (Q5)
6. **Keep rep A as value/change-point truth; keep rep B (FHRR temporal-context) as recency/confidence/order-uncertainty AND as the belief⊗when BINDING at event boundaries — not a lossy copy.** Confidence decays with time-since-update; value does not. (Q3, Q3b)
7. **Represent an explicit reader/omniscient track; make the GAP (belief_A vs reality, belief_A vs belief_B) a first-class query.** (Q4)
8. **Key beliefs by mode-of-presentation/guise where identity matters, not referent alone** (avoid the minimal-ToM identity signature-limit). (Q5-Wall3)
9. **Nested beliefs as explicit nested files; you may exceed the human ~2-order recursion cap (OUR-INVENTION-acceptable) but validate against combinatorial blowup.** (Q5-Wall2)
10. **Optionally add a controllable curse-of-knowledge INTRUSION term** — as a discriminator (a clean reader shows none; a leak reveals a bug) and/or to *model* human-like errors when that is the goal. (Q5-Wall1)

## Where I am NOT confident (VET before trusting)
- The store-vs-reconstruct fork (Q1) is genuinely mixed in the literature; my "current-state-stored + past-reconstructed" synthesis is a defensible reading (P≈0.45 deflated), not settled. **Discriminator:** run the hindsight-bias probe — does your reader's answer to "what did A believe at T" shift when you change *only* a later, unobserved world event? A stored-clean substrate: no shift. A brain-faithful reconstruction: shift. Pick the target and test.
- Exact capacity numbers for parallel *first-order* character-belief tracks are under-reported for reading specifically (organized-around-protagonists is well-established; a hard N is not). Treat "several, soft ceiling ~4" as a hypothesis pending VET.

## TLDR (plain language)
The brain does not keep a neat little timeline of "what each character knew at every moment" and look up the answer. It keeps what each character believes *right now*, plus a few time-stamped memories of when they last saw things, and it *rebuilds* the past on demand — and that rebuild gets contaminated by what the reader now knows (the "I knew it all along" bias). Your sample-and-hold picture is the right *description* of how a belief behaves (it stays put until the character sees something change), but you should *store* it as a handful of "saw-it" events rather than a full frame-by-frame tape. The most important fix: keep each character's beliefs in a separate box from the real world, so real-world facts can only get in when the character actually observes or is told them — that one rule is what lets people (and will let your reader) hold a character's stale, wrong belief without it being silently corrected. Also: beliefs change not just from seeing, but from being *told* (which is how lies and deception work), so add that.

## QUESTIONS
None — the design is coherent and the corrections are concrete.

## NEXT STEPS
Implement changes 1–4 first (they are structural and cheap), then run the hindsight-bias discriminator (Q1 note) as your first can-fail test to decide whether you want the clean-store or the brain-faithful-reconstruction target.

---
### Key sources
- Zwaan & Radvansky 1998, *Psych Bulletin* — situation models / event-indexing.
- Radvansky & Zacks 2011/2017; Zacks, Speer, Swallow & Reynolds 2007 — event segmentation.
- Anderson, Garrod & Sanford 1983; Glenberg, Meyer & Lindem 1987; Rinck & Bower — here-and-now accessibility.
- O'Brien, Rizzella, Albrecht & Halleran 1998; Myers & O'Brien — memory-based/resonance processing.
- Schacter & Addis 2007; Hassabis & Maguire 2007; Addis, Wong & Schacter 2007 — constructive episodic simulation.
- Fischhoff 1975; Birch & Bloom 2007 *Psych Science*; Pohl & Erdfelder SARA model — hindsight bias / curse of knowledge.
- Keysar, Lin & Barr 2003; Samson et al. — egocentric/altercentric intrusion.
- Saxe & Kanwisher 2003; Schurz et al. 2014 — mentalizing network (TPJ/mPFC).
- Howard & Kahana 2002; Sederberg et al. 2008; MacDonald et al. 2011; Eichenbaum 2014 — temporal context model / time cells.
- Apperly & Butterfill 2009; Butterfill & Apperly 2013 — two-systems / minimal ToM + signature limit.
- Kinderman, Dunbar & Bentall 1998; Stiller & Dunbar 2007; Hi-ToM benchmark — recursive-ToM capacity.
- Pratt & Bryant 1990 — seeing-leads-to-knowing (knowledge access).
- Dowty 1986 (temporal inertia); McCarthy & Hayes / Shanahan (frame problem); Reichenbach reference time / Kamp DRT.
- "The audience who knew too much" *Frontiers in Psychology* 2023; "Viewers Actively Extract and Maintain Spontaneous ToM Representations in Dramatic Irony Scenes" 2025 — parallel per-agent states in dramatic irony.
- FANToM (Kim et al., EMNLP 2023) — the NLP information-asymmetry wall (contrast, not the human side).
