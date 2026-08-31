---
owner_verdict: DONE
---

Problem: the_knowledge_store_has_no_correctness_or_consistency_cleanup — SOLVED (brain-foundational;
detect AND correct, leave-one-out-clean on a real dense store). WIP until owner_verdict: DONE.
No hdlab/ touched (Q111 — proposed diff + validated reference impl in SOLVED.md).

WHAT IT IS: hd_fact_store vets SOURCE-TRUST only — a clean fact just stores; conflicts resolve by
source rank, never by whether a fact CONTRADICTS the coherent majority. Built the missing "does this
fit?" check as a glass-box schema-congruence organ (no LLM at inference), and — the brain's actual
cleanup — made it CORRECT flagged facts toward the schema, not just flag them.

REVERIFY: .venv/Scripts/python.exe verification/test_knowledge_store_consistency_cleanup.py   # 15/15

BRAIN-FOUNDATIONAL ARCHITECTURE (validated by 3 literature drills; CLS = complementary learning systems):
- Hippocampal orthogonal binding store (random codes — faithful, interference-vs-capacity = VSA capacity
  theory) + a SEPARATE cortical relational schema for congruence (one code can't be both a clean binder
  and a semantic generalizer — the core CLS claim). Congruence = mPFC match-to-schema + ACC conflict
  energy; precision = mPFC/Friston inverse-variance; strict LEAVE-ONE-OUT (a memory never judges itself).
- Grounding drill: deriving semantic geometry from relational structure is how the congenitally blind
  ground meaning (dorsal-ATL linguistic spoke) — "keep the design; it's the win, not the compromise."

THE HONEST CHAIN (each step witnessed):
1. Mechanism + architecture proven brain-faithful.
2. LEAVE-ONE-OUT AUDIT (a self-correction that outranks the first headline): my initial relational
   result (paired 0.79/0.88) was NOT leave-one-out clean — it let a fact's own membership sit in the
   geometry judging it. Under strict LOO it collapses to ~chance (AUC 0.52) on the sparse store. Be
   clear on this: the optimistic non-LOO figure was withdrawn; the honest signal is what follows.
3. That collapse is a DENSITY PHASE TRANSITION, mapped (W13): holding the mechanism fixed and dialing
   store density, LOO-clean structural AUC crosses from chance to near-perfect as the independent-pair
   fraction (genus-pairs co-witnessed by >=2 subjects) crosses ~0.2. The real store is subcritical
   (0.036) — density-starved, not a broken mechanism.
4. CROSSED THE BOUNDARY ON REAL DATA (W14): densified the store's real concepts with WordNet hypernym
   chains — indep-pair fraction 0.036 -> 0.31 (supercritical) — and the SAME mechanism under strict LOO
   detects injected wrong is-a facts at AUC 0.88 far / 0.79 near, paired 0.89 / 0.81, info-free twin
   LOSING CI-separated (0.57), near-misses included.
5. DETECT AND CORRECT (W15, the brain-foundational final push): systems consolidation over-writes
   incongruent detail toward the gist (Bartlett; Winocur & Moscovitch). The organ predicts the
   schema-consistent value for a flagged fact — type-correct 144/144 = 1.000, EXACT original value
   recovered 142/144 = 0.986 (random 0.049). This completes the problem's literal title (CLEANUP): it
   says not just "this is wrong" but "it should be THIS."
Also integrated: a coherence CONFIDENCE tier (schema sharpness = Friston precision, W11 — the organ
knows when to trust itself) and INSUFFICIENT_SUPPORT as a first-class third verdict (a lonely fact is
neither congruent nor incongruent — brain-faithful).

BE CLEAR ABOUT THE ONE FIDELITY GAP (honest, named): the density here comes from WORDNET — a handed,
static taxonomy, ADMISSIBLE as a build-time foundation asset (the pivot allows any external tool to
BUILD the foundation; the runtime check stays glass-box and queries nothing, no LLM). But the MORE
brain-faithful route is to LEARN the category hierarchy from experience via consolidation, which the
brain does. The distributional/learned route measured weak on this corpus (AUC 0.57), so WordNet is the
admissible stand-in for now. This is a real fidelity gap to close UPSTREAM (p1 / a consolidation-learned
hierarchy), NOT a defect in the consistency mechanism — and it is the only brain-foundational
optimization left, which belongs to a different problem.

HONEST BOUNDS (withdraw-first): WordNet covers ~58% of concepts (is-a nouns only); the densifying
relation is hypernymy specifically; injections are synthetic (far/near hypernyms). On the RAW sparse
definitional store the LOO-clean signal is weak (the honest coverage/density limit) — the solution is
"here is a real dense store and the mechanism works on it," not "detection is easy on any store."
Rigorous-negative side-findings (all full passes): graph-diffused codes leak (self-camouflage +
over-smoothing) — member-Jaccard locality is the correct inductive bias; taxonomy-over-sparse-graph and
per-subject precision-weighting are negatives with mechanistic reasons.

KEY REALIZATIONS (the enabling moves): (a) measure PAIRED/ranking, not threshold precision, on a noisy
store — real store-noise legitimately out-ranks planted errors; (b) the whole problem is a connectivity
phase transition, so "fix the foundation's density" is THE lever, with a measured target (indep-pair
frac >= ~0.2); (c) precision = schema SHARPNESS, not amount (a Simpson's-paradox confound with
genericity — the Rosch basic-level advantage); (d) the disk outranked my own headline — strict LOO
turned a 0.88 into a self-correction, then density turned it back into a real 0.88.

FILES: experiments/exp_knowledge_store_consistency_cleanup_v1.py (mechanism + confidence tier);
exp_consistency_phase_transition_density_v1.py (the phase map); exp_consistency_wordnet_densified_
solved_v1.py (FULL SOLUTION: detect + correct on a real dense store); exp_consistency_cleanup_live_
store_v1.py (runs end-to-end through a real HDFactStore, survives INGEST-VET); verification/test_
knowledge_store_consistency_cleanup.py (15/15); + 4 follow-on cells + 3 research notes; SOLVED.md.

FOR STRATEGY (you own hdlab, Q111): (1) LAND the consistency pass (validated reference impl
consistency_energies() + a flag_high_energy() review queue + the CORRECTION predictor + the coherence
confidence field; default-off, byte-identical when off, W10 proves it runs on a live HDFactStore).
(2) DENSIFY the foundation to keep it supercritical (WordNet hypernyms now, or p1's richer extraction) —
without this the structural check is subcritical and near-chance under LOO. (3) FOLD the AUDIT UPDATE
into BRAIN_FOUNDATIONAL_AUDIT.md §2b (orthogonal-binding + separate relational schema = CLS-faithful;
consistency is a density phase transition, target indep-pair-frac >= ~0.2; detect+correct+confidence).
(4) SEED a follow-on: a CONSOLIDATION-LEARNED taxonomy to replace WordNet (the remaining fidelity gap).
Update notes/WIRING_MAP.md (fact-store -> consistency pass).
