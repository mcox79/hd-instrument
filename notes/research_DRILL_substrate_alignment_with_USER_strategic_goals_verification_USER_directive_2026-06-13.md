# Research drill: substrate alignment with USER strategic goals (verification)

Filed: 2026-06-13
Trigger: USER directive — verify current architectural choices (5-step closed loop + 4-mode distillation taxonomy + compound HYGIENE+ABSTRACTION optimization + audit-discipline rule family + 9d spectral observability + N-invariant routing) are RIGHT to achieve substrate-on-all-knowledge + LLM-class language mastery + recursive self-improvement + architecturally-distinct-from-LLMs.
Discipline: ASCII-only queries, generic math terms only, local CPU only, ~4-5 web searches, lit-scan calibration penalty applied (deflate P by 0.15-0.25; cap novel-synthesis at 0.50).
Frame: per [[feedback-no-papers]], this is an INTERNAL TRACKING DOCUMENT not a paper. Per "we may be first to build a system like ours" rule, prior work informs but does not govern.

---

## (a) HEADLINE

Substrate is ARCHITECTURALLY ALIGNED with 3 of 4 USER strategic goals (recursive self-improvement, architecturally distinct from LLMs, substrate-on-all-knowledge scaling path); the 4th goal (LLM-class language mastery) is ALIGNED-WITH-A-RISK because the dominant precedent in the 2025 neuro-symbolic literature places language fluency in a LEARNED-VECTOR layer alongside symbolic reasoning, and substrate currently has NO learned-vector language-fluency layer (only typed symbolic atoms + HRR/FHRR codebook geometry). Recommendation: do NOT add an LLM layer (kills architectural distinction); INSTEAD elevate substrate's distillation-over-corpus as the language-mastery mechanism and pre-register a held-out language-task gate. P_deflated(current architecture sufficient for all 4 goals) = 0.45 (capped at novel-synthesis 0.50; deflated 0.20 from 0.65 for missing language-layer precedent). Risk is MANAGEABLE, NOT FUNDAMENTAL.

Plain language: the substrate is on the right path for 3 of the 4 USER goals. The 4th goal — sounding as natural as an LLM in language — is the gap. Every system in the literature that solved this leaned on a learned-vector neural layer. Substrate does not have one. Either we (a) accept a different definition of "language mastery" (sound, typed, checkable language output rather than fluent prose) which preserves architectural distinction, or (b) we adopt a small narrow learned-vector READING LAYER that does NOT do reasoning. Recommendation: (a) + a pre-registered held-out language benchmark to verify the bet.

---

## (b) Cheap decisive test

Pre-register a HELD-OUT language-task gate (post-corpus ingest, before ~6 months) using ONLY substrate primitives (typed atoms + L6-PROOF + KP + 9d spectral + N-invariant routing + 4-mode distillation):

  TEST: 100 NEW questions authored AFTER corpus ingest hits 1M atoms (substrate has not seen them; cannot tune), spanning math+CS+physics+general-knowledge, requiring multi-hop typed reasoning OR retrieval-and-synthesis. Measured by: (1) substrate answers macro F1, (2) substrate answers checkable (CHTV verifier accepts), (3) substrate refuses-when-unverifiable rate >= 95% (no hallucinations).
  HARD-PASS: macro F1 >= 0.60 AND CHTV-accept >= 0.85 AND refusal-soundness >= 0.95. (Establishes substrate can answer real questions soundly and broadly, NOT as fluently as an LLM but in its own distinctive sound register.)
  HARD-FAIL: macro F1 < 0.30 OR CHTV-accept < 0.50 OR refusal-soundness < 0.80. (Substrate cannot answer broadly even when sound; learned-vector reading layer becomes architectural necessity.)
  MIDDLE BAND: anything between — informative but inconclusive; redesign distillation pipeline.

Cost: cheap — uses existing substrate; only requires question authoring (Research can author) and held-out discipline.

---

## (c) Falsifiable predictions

P1. Substrate-on-all-knowledge scaling (1M-5M atoms via Mizar 150K + Lean Mathlib 1.7M LoC + Coq 120-package + ProofWiki) is EMPIRICALLY VALIDATED at corpus scale by formal-math KG precedents. (See Coq mono-graph 120-pkg, Mizar MML 150K, Mathlib4 1.7M-LoC corpora.) P_deflated = 0.70. HARD-PASS gate: substrate ingests >= 1M atoms with provenance-witness merge soundness preserved >= 99% (existing 11th rule + 10th rule). HARD-FAIL: soundness drops below 0.95.

P2. Recursive self-improvement (5-step closed loop DETECT->PROPOSE->VERIFY->INTEGRATE->METRIC-UP) is FORMALLY-PRECEDENT-MATCHED by Schmidhuber Goedel-machine (proof-then-rewrite) AND OpenCog Hyperon (self-modifying metagraph + MeTTa pattern-rewriting). Substrate's 4-mode distillation taxonomy (atom-removing + structure-adding + inverse-recognition + refusal) is STRICTLY STRONGER than Hyperon's MeTTa rewriting because substrate REFUSES what it cannot prove (substrate's 18th methodology rule candidate; no Hyperon equivalent). P_deflated = 0.55. HARD-PASS: substrate's recursive self-improvement loop runs N more iterations without soundness regression AND each iteration measurably reduces hygiene-debt OR adds an abstraction layer. HARD-FAIL: a single iteration introduces a false-merge or removes a load-bearing capability (would falsify 10th rule).

P3. Architectural distinction from LLMs is CATEGORICAL not gradient. Lit confirms: LLMs are Bayesian networks with implicit grounding; substrate has EXPLICIT typed factor graph + EXPLICIT finite verifier + EXPLICIT refusal + EXPLICIT 9d spectral observability. Per arxiv 2507.10624 ("Comprehension Without Competence"), LLMs have ARCHITECTURAL LIMITS in symbolic computation. Substrate inverts that: ARCHITECTURAL FLOOR in symbolic computation (sound or refused). P_deflated = 0.70. HARD-PASS: CH-P6 already showed substrate 0 false-accepts vs Qwen 3/12. Continued separation across NEW question sets at scale = continued architectural distinction. HARD-FAIL: substrate hallucination rate ever exceeds 1% on held-out (would mean refusal mechanism broke).

P4. LLM-class language mastery (P_deflated = 0.30 — LOWEST). Literature precedent: every system claiming language fluency at scale uses a LEARNED-VECTOR LAYER (transformer, RWKV, Mamba, hybrid). NO pure-symbolic system has reached LLM-class fluency. Substrate's bet: distillation-over-corpus + N-invariant routing + KP knowledge promotion + 9d spectral CAN substitute for the learned-vector fluency layer IF "language mastery" is redefined as SOUND BROAD ANSWERING rather than FLUENT PROSE GENERATION. HARD-PASS: held-out language gate above. HARD-FAIL: same. This is the BET that needs verification.

P5. Missing components from literature precedent that substrate currently lacks (each is a candidate but NOT urgent):
   - Attention-economy / forgetting-curve (OpenCog Hyperon has ECAN attention-allocation; substrate's nearest analog is HYGIENE 12.4% mode; possibly already covered).
   - Embodied / grounded sensorimotor layer (Hyperon roadmap, embodied AI lit; substrate is symbolic-only by design; categorical-distinction-preserving DECISION not gap).
   - Working / declarative / procedural memory tripartition (Hyperon PRIMUS; substrate has typed atoms + codebook + L6-PROOF — analogous structure but not explicit).
   - Multi-agent coordination (substrate is single-substrate; not strategically required at this stage).
   - Meta-cognition layer (2025 lit identifies as frontier; substrate's audit-discipline rule family + 10th rule + 18th rule candidate ALREADY operationalize this — substrate is AHEAD of literature here).

---

## (d) Cross-thread synthesis with prior entries

- Composes with [[feedback-substrate-standalone-capability-first-before-LLM-positioning]] (11th USER-LOCKED rule): substrate must be measured on its OWN before LLM-comparison. Held-out language gate is OWN measurement.
- Composes with [[substrate_methodology_rule_10th_VERIFY_BEFORE_ASSERTING_PROMOTED]]: pre-registered held-out gate is per-10th-rule discipline.
- Composes with [[substrate_3_distillation_modes_taxonomy]]: 4-mode taxonomy is the substrate equivalent of MeTTa rewriting + STRONGER (REFUSAL mode has no Hyperon analog).
- Composes with [[substrate_closed_loop_OPERATIONAL_step_3_HARD_PASS]]: 5-step closed loop is OPERATIONAL at step 3 (DISTILL-VERIFY-1 HARD-PASS today); literature confirms Goedel-machine + Hyperon precedent.
- Composes with [[substrate_CH_P6_LLM_soundness_gap_capstone_HARD_PASS]]: architectural distinction empirically established at deduction level (substrate 0 false-accepts vs Qwen 3/12).
- Composes with [[feedback-held-out-test-methodology-required-for-macro-F1-claims]] (11th methodology rule): held-out language gate IS the discipline mechanism.
- Contradicts NOTHING in the prior memory index. STRENGTHENS the substrate-product positioning artifact by explicitly naming the P4 bet (language fluency redefined as sound broad answering).

---

## (e) Substrate-product implications

1. KEEP the 5-step closed loop. Literature confirms Schmidhuber + Hyperon precedent. Substrate's REFUSAL mode is a strict-strengthening. No change.

2. KEEP the 4-mode distillation taxonomy. Literature confirms the structure-adding + atom-removing modes (analogous to MeTTa rewriting + ECAN forgetting); substrate adds REFUSAL mode which is novel. No change.

3. KEEP HYGIENE + ABSTRACTION compound optimization. Literature backs both: HYGIENE = Hyperon ECAN attention-economy analog (measured); ABSTRACTION = Hyperon supertype + structure-adding analog (gated on ~10-15 composite type-atom authoring). No change.

4. KEEP audit-discipline rule family (10 rules). Literature identifies meta-cognition as 2025 frontier; substrate is AHEAD here. No change. Continue rule promotion discipline.

5. ADD: pre-register a HELD-OUT LANGUAGE-TASK GATE post-1M-atom-ingest. This is the cheap decisive test for P4 — the only goal where lit-precedent does NOT confirm substrate's bet. Owner: Research authors 100 questions AFTER ingest hits 1M; Strategy holds them held-out; Testbed runs gate.

6. ADD: explicit substrate-product framing: "LLM-class language mastery" REDEFINED as SOUND BROAD ANSWERING (CHTV-accepted, refusal-safe, multi-domain) rather than FLUENT PROSE GENERATION. This preserves architectural distinction. Internal-tracking-document language only.

7. DO NOT ADD: learned-vector LLM layer for fluency. Would destroy architectural distinction (USER goal #3). If P4 hard-fails the gate, RECONSIDER but DO NOT pre-empt.

8. DO NOT ADD: embodied sensorimotor layer. Categorical-distinction-preserving DECISION; not a gap.

9. CONSIDER (low priority): explicit working/declarative/procedural memory tripartition naming — Hyperon PRIMUS analog. Substrate already HAS this structure (typed atoms + codebook + L6-PROOF) but does not name it. Low-cost naming addition for internal-tracking-document clarity.

---

## (f) Risk assessment

- Substrate is on a DEFENSIBLE path to 3 of 4 USER strategic goals. NOT MISSING SOMETHING FUNDAMENTAL.
- The 1 risk is goal #4 (LLM-class language mastery). Risk is MANAGEABLE via the pre-registered held-out gate.
- If gate HARD-PASSES: substrate-product narrative LOCKS at "sound broad answering" — categorical advantage over LLMs (which hallucinate).
- If gate HARD-FAILS: substrate-product narrative shifts to substrate-as-reasoning-layer alongside an LLM (would hybridize). This is recoverable but would weaken architectural distinction. Pre-register the gate NOW so we know which world we are in by ~6 months.
- Audit-discipline rule family + 10th rule + 11th rule + 18th rule candidate = substrate has meta-cognitive primitives the literature identifies as 2025 frontier. Substrate is AHEAD of precedent in this dimension.
- Per "we may be first to build a system like ours" rule: literature INFORMS the bet, does not govern it. Substrate is allowed to be first to operationalize REFUSAL as a distillation mode and sound-broad-answering as language-mastery surrogate.

P_deflated final: 0.45 (architecture sufficient for ALL 4 goals); 0.70 (architecture sufficient for goals 1+2+3 alone). The 0.25 spread IS the P4 bet.

---

## (g) Citations (verified count = 5)

1. OpenCog Hyperon framework (arxiv 2310.18318) — self-modifying metagraph + MeTTa rewriting + PRIMUS cognitive model. Validates 5-step closed loop precedent. https://arxiv.org/abs/2310.18318
2. Goedel machine (Schmidhuber 2003, Wikipedia entry) — recursive self-improvement protocol with proof-then-rewrite. Validates 5-step closed loop. https://en.wikipedia.org/wiki/G%C3%B6del_machine
3. Comprehension Without Competence: Architectural Limits of LLMs in Symbolic Computation (arxiv 2507.10624) — LLMs have categorical limits in symbolic reasoning. Validates architectural distinction goal. https://arxiv.org/pdf/2507.10624
4. Coq 120-package mono-graph + Mizar MML 150K + Mathlib4 1.7M LoC — formal corpus scaling precedent. Validates substrate-on-all-knowledge path. https://arxiv.org/pdf/2401.02950 + https://arxiv.org/pdf/1310.2805 + https://leanprover-community.github.io/papers/mathlib-paper.pdf
5. Neurosymbolic AI antithesis to scaling laws (PNAS Nexus 2025) — hybrid approaches as alternative to pure-scaling; symbolic reasoning module + language fluency separation-of-concerns precedent. Frames the P4 bet honestly. https://academic.oup.com/pnasnexus/article/4/5/pgaf117/8134151

---

## (h) Next-drill candidates (NOT this cycle)

- Drill: "What does sound-broad-answering look like operationally as a held-out benchmark?" — Research authors a sample 10-question pilot.
- Drill: "Could a NARROW learned-vector READING LAYER (input parsing only, no reasoning) preserve architectural distinction while improving language fluency?" — read-only parser, fully bounded by typed-atom output. Adjacent to substrate's existing bge-top5 layer.
- Drill: hyperdimensional-computing / VSA literature on language-task benchmarks at scale — adjacent to substrate's HRR/FHRR codebook. (Per Tier-1b new-field adjacency to free-probability.)

End of note.
