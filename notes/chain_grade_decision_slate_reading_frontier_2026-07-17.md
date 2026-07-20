# CHAIN-GRADE DECISION SLATE — the struggling reading frontier (2026-07-17)

USER-directed: 3x brain+ML drills on the 3 struggling reading sub-problems -> ranked chain-grade candidates, each triangulated across BIOLOGY + ML + failure-mode, each with a falsifiable cheap-decisive-test. **All three are CANDIDATE MECHANISMS with test specs -- NOT validated results; each needs a real cell to earn the tier (interpretation-discipline).** Glass-box / no-LLM confirmed for all three.

---

## BET 1 — PRECISION: joint discriminative reranking + self-training (NOT a post-hoc gate)
- **Mechanism:** score k-best parses with a glass-box log-linear model; selectional/lexical/structural cues are FEATURES AMONG MANY, summed into one weighted score over WHOLE candidates (early-fusion / at the decision), where weak signals compensate instead of vetoing. + an error-driven SELF-TRAINING loop (retrain on high-confidence output).
- **Triangulation (3 lanes converged):** BRAIN = thematic-fit integrated JOINTLY + IMMEDIATELY at the ambiguous region (Trueswell 1994, McRae 1998, Competition Model, Chang-Dell error-driven); post-hoc veto is only the REPAIR mechanism after blended integration fails. ML = the biggest classical precision gains are all JOINT reranking (Collins, Charniak-Johnson) + self-training (McClosky +28% err-red). FAILURE = hard gates fail (collider/restricted-range on a collapsed decision; hard-veto destroys a weak-but-real signal; AUC~0.5-per-instance despite real aggregate effect).
- **Why our selectional cell failed:** hard post-hoc gate = the exact anti-pattern. The signal may be real; the ARCHITECTURE killed it.
- **Cheap-decisive-test:** precision delta over the 0.347 base parser when the selectional signal is soft-blended at the decision vs base; measure on the disagreement subset; can-fail; one-variable (integration architecture). **The selectional REVIVAL cell (a5aef753, IN FLIGHT) is the first empirical look (soft-rerank at near-tie).**
- **Status:** HOLD the fuller reranker+self-training build until the revival cell lands (it informs whether soft-blend works at all).

## BET 2 — BREADTH: adaptor/fragment grammar (entrenchment + abstraction + Kneser-Ney brake) [the #1 barrier]
- **Mechanism:** grow a construction inventory from reading via a hierarchical Pitman-Yor process (rich-get-richer = entrenchment); ABSTRACT via structural alignment (schema when >=k exemplars share a relational skeleton, different fillers); COMBINE specific+general via Kneser-Ney back-off keyed on TYPE count (productivity); PREEMPTION = competing-form discount mass. ONE framework (Teh 2006: interpolated-KN === hierarchical-PYP === adaptor grammar).
- **Triangulation (3 lanes converged):** BIOLOGY = Tomasello usage-based (entrenchment + analogical schema-formation via SME + semantic-class bounds); type-freq>token-freq for productivity (Bybee). ML-grammar-induction = adaptor grammars (Johnson-Griffiths-Goldwater) -- principled anti-overgeneration (never-reused fragments -> ~0 posterior mass), glass-box. COMBINE = KN/HPYP back-off + a concrete glass-box recipe (store exemplars w/ counts -> cluster into schemas -> KN-interpolated license -> preemption discount).
- **Why it fixes the wall:** ReVerb OVERGENERATES (0.083 prec); flat-fragment grow-from-reading PLATEAUS. The PYP/KN brake is the PRINCIPLED overgeneration control ReVerb lacked; abstraction generalizes to unseen (the missing high-capability piece).
- **Cheap-decisive-test:** precision/recall on held-out NOVEL slot-fillers traces a Kneser-Ney-shaped curve (schema wins only when specific evidence sparse); breadth beats flat-fragment grow-from-reading v2 WITHOUT ReVerb-style overgeneration. Real baselines (grow-from-reading v2 + ReVerb + trained parser); can-fail; difficulty-on = general prose; one-variable = abstraction+backoff. P~0.42-0.55 (port + novelty risk).
- **Status: FIRING NOW (design-gate-ready, #1 barrier, strongest converged candidate).**

## BET 3 — DISCOURSE: entity-grid coherence discrimination (the RIGHT metric, not pronouns)
- **Mechanism:** build a per-passage entity x grammatical-role x sentence GRID from role-tagged entities (S/O/X); score via role-TRANSITION coherence; test by discriminating the real sentence order from K permutations. = the "who's-doing-what state of mind" made measurable.
- **Triangulation:** the drill's realignment -- pronoun-accuracy was RECENCY-COMPETITIVE (the wall we hit); entity-grid (Barzilay-Lapata, 20-yr literature-validated) is a NON-pronoun coherence metric, self-supervised (permutations = free negatives), ZERO annotation, correlated with human readability, with a REAL non-trivial baseline (co-occurrence) built in.
- **Cheap-decisive-test:** role-transition grid beats co-occurrence-only AND random at discriminating original vs permuted order, on BOTH full-shuffle AND the harder adjacent-swap condition; can-fail; one-variable (role-transition vs co-occurrence). P~0.42 (port risk; concept mature).
- **Status: FIRING NOW (design-gate-ready, zero-annotation, orthogonal, tests the state-of-mind's real value).**

---

## Sequencing (full-auto call)
- FIRE breadth + discourse NOW (both design-gate-ready, orthogonal, brain+ML-grounded).
- HOLD precision-fuller for the selectional revival cell (in flight = precision's empirical first-look).
- Each fired cell gets landed-VET before any tier claim (this session: exp_dev framings ran optimistic; VET caught 4+ over-reads incl. mine).
- The ONE-STEP-FROM-CHAIN-GRADE items (memory capacity decoupling; cheap-robust index seed-robust margin; focus decorr correlated-codebook) are separate queued follow-up CELLS, not part of this reading slate.
