# RESEARCH — the generative entity-state read (pri-1): how the brain picks the affected entity, and what the probes say (strategy, 2026-09-12; LIVING — updated as the build proceeds)

Problem: `generative_entity_state_reranks_which_entity_is_the_affected_undergoer`. After grammar (ACT-R salience prior x
Principle B x role parallelism; `hdlab/affected_entity_resolver`, deployed 0.42, gold roles 0.4632 on GUM n=1142) a residual
remains. Owner directive (2026-09-12): build it from mathematically brain-foundational ORGANS, do not replicate models;
research liberally; never declare a wall in auto.

## 1. How the brain does it (research agent report, 2026-09-12; full citations in the agent transcript; PINNED vs MODEL)

1. **Tokens.** Each discourse entity is a token / object file (Kahneman-Treisman-Gibbs 1992; Hommel event files) in the
   anterior-temporal item system; the situation model (posterior-medial system: PMC, angular gyrus, mPFC; Ranganath &
   Ritchey 2012) holds the configuration of tokens and is updated at event boundaries (Baldassano 2017; Zacks 2007). A
   token accrues ALL its references (reviewing + impletion) — PINNED.
2. **Expectation at the verb, before the pronoun.** P(undergoer = X | agent, verb) is computed incrementally from
   generalized event knowledge: the JOINT agent+verb expectation over the recipient's kind (Bicknell-Elman-Hare-McRae-Kutas
   2010; Kamide-Altmann-Haywood 2003 anticipatory looks; Metusalem 2012) — PINNED; learned as co-occurrence over
   event-role tuples (McRae & Matsuki 2009) — online counting, no batch training.
3. **Update magnitude.** The N400 is the size of the situation update (Rabovsky-McClelland 2018; Kuperberg-Jaeger 2016
   precision-weighted prediction error); the chosen candidate is the one needing the SMALLEST update = the one already
   predicted in the undergoer slot. Precision (sharpness of the prior) gates how much the semantic cue counts.
4. **Bayesian decomposition.** P(referent | pronoun) ∝ P(referent next-mentioned) x P(pronoun | referent)
   (Kehler-Rohde 2013). Grammar has spent the likelihood and the recency/topic part of the prior; the residual IS the
   semantic part of the prior.
5. **State compatibility.** A token whose stored state contradicts the event's preconditions/result is penalised
   (KTG impletion; Hommel partial-mismatch). Preconditions/results are lexicalised per verb class (VerbNet start(E)/result(E)
   predicates: alive, has_possession, location, state, together, visible, free / destroyed, covered, cooked, ...).
6. **Foreground.** Only a few tokens are available at once (Glenberg availability; Centering Cf; event-model foreground);
   entities situationally attached to the current event are accessible, others drop at boundaries — PINNED.

Assembled computation: plaus(X) = P(kind(X) | agent, verb) x compat(state(X), preconditions(verb)) x
(1 − contradiction(state(X), result(verb))), over the in-focus tokens, fused as a Bayesian likelihood with the salience
prior x grammatical likelihood; arg-max (= arg-min update); margin below threshold -> flag, not guess; then write the
result state into the winner's token (impletion) and foreground it. PINNED: 1, 2, 3-timing, 6. MODEL: the exact product form.

## 2. What the substrate has (organ map, 2026-09-12)
- `affected_entity_resolver` (the grammar half; hook `situation_reader.py:3274`); `salience_binder.actr_activation` (BF).
- `state_register`: on real prose a flat bag of copular properties keyed by SURFACE holder string, t=0, no aspects; LitBank
  coverage 0.33; nothing measured on GUM; NOT keyed by entity token -> the brief's intended input is starved upstream.
- `online_entity_cluster.online_cluster` (gold-free Heim files over non-pronoun mentions); `unified_referent`; pronouns
  are skipped (no pronoun mention ever accrues to a file) -> the token's history is incomplete by construction.
- `generalized_event_knowledge` (ROCStories forward PPMI, word-level); reading-grown `selectional_slots_v1.pkl`
  ((verb,role)->filler counts, simplewiki; SUBJ/OBJ/IOBJ/obl:*); `typed_selectional_preference` (Resnik over supersenses);
  `force_dynamics_valence.result_state_evidence` (VerbNet result/end-state predicates per sense, landed 2026-09-12);
  `sem_event_segmenter` (SEM schema-switch boundaries, island); `meaning_fusion.MeaningFusion.similarity` (reading+grounded).

## 3. Probes on the GUM slice (n=1142 pronoun undergoers; `experiments/probe_entity_state_residual_gum_v1..v6.py`)

**Slice composition (v4/v5) — the instrument mixes three brain tasks.** THIRD-person personal pronouns 596 (it 340,
them 79, he 48, him 42, her 36, they 22, reflexives 19); DEICTIC (I/me/you/we/us) 263; DEMONSTRATIVE (this/that) 115;
OTHER 168. The grammar resolver: THIRD 0.497, DEICTIC 0.445, DEMONSTR 0.435, OTHER 0.393. Perfect entity individuation
(oracle gold clusters with full history) lifts THIRD +0.091 CI[+0.059,+0.124] and does NOTHING for the other classes
(DEICTIC −0.027, DEMONSTR −0.070) — those are resolved by a speaker/addressee model and by abstract (event) reference,
different machines. **The entity problem proper is the THIRD class.**

**THIRD anatomy (v6).** ceiling (gold among legal candidates) 0.886; by form: it 0.491 (ceiling 0.909), them 0.684,
he 0.604, him 0.310, her 0.333, they 0.591. By the gold entity's last-mention distance: same sentence 0.753 (n=247),
previous sentence 0.587 (150), 2-3 back 0.282 (71), >=4 back 0.030 (66), no prior non-pronoun mention 0.000 (62).
In-focus ceiling (gold within the prior's top-k): k=2 0.653, k=3 0.753, k=4 0.792.

**Knowledge reads (v2/v3), fused in log space over all candidates and within the top-k focus, with scramble controls:**
R1 entity-specific event memory (X was a PATIENT of this verb before): small, real (+0.014 CI-sep at top-3/4, tau=2;
gold>pick 40:9 on the wrong set). R2 history->verb PPMI (ROC): null. R4 selectional log P(head|V)/P(head) (simplewiki
store, supersense back-off): INFORMATIVE on the wrong set (gold>pick 251:137) but HURTS when fused (−0.045 to −0.093,
CI-sep), even within top-2/3 unless gated to near-ties (then null). R5 GEK content->head (ROC): same pattern. Scrambles
are always worse than real -> information exists, but the fusion destroys more right picks than it fixes. Reading: the
generic-corpus marginals are miscalibrated for GUM's genres (conversation, academic, how-to; "it" -> abstract heads) and
the brain's expectation is the JOINT agent+verb over the in-focus tokens, not a marginal over 18 candidates.

**Operating point (v6, THIRD):** ACT-R decay and clock matter hugely; the incumbent is at decay d=DEFAULT_DECAY; d=0.5
(Anderson's lab value) collapses to 0.32 — this task is recency-dominated; token-position clock with d=1.5 0.512 (n.s.).
Foreground window (candidates mentioned within 2-3 sentences first): 0.520 with the sentence clock (+0.024, CI includes 0).

**Individuation (v5, THIRD):** gold-free entity files (online_cluster) +0.003; files + incremental pronoun resolution
+0.013 (n.s.) vs the oracle's +0.091 — the gold-free coref half does not yet realise the individuation prize.


**Forward half as one incremental engine (v7, THIRD):** gold tokens with PERFECT pronoun attribution (v5 oracle) gave
+0.091; the same gold tokens when earlier pronouns are resolved by the resolver itself and accrued give +0.008 (n.s.) and
+0.003 with accrual off -- the individuation prize is CIRCULAR: it needs correct pronoun resolution upstream. Gold-free
online entity files (Heim file-change, always-merge) are WORSE than head buckets (0.38-0.40, CI-sep) unless the
hold-under-uncertainty policy makes them behave like buckets (0.50, parity); centering bonus, clock and decay do not
rescue them; the foreground window adds ~+0.01 on files. => the coref token quality, not the salience equation, is the
upstream loss for individuation (the coref two-half problem's own line). The lever for THIS problem stays the in-focus
semantic fit (top-3 ceiling 0.753 vs 0.497).


**CORRECTION + FIRST REAL GAIN (v7 after engine parity, THIRD):** the v7 engine had two defects (token scored by majority
cluster instead of the last compatible mention; gender fixed from the first mention) — fixed, head buckets inside the engine
reproduce the incumbent exactly (0.4966). With parity: **pronoun ACCRUAL (every earlier pronoun resolved by the same
resolver, its mention written to the picked entity's history) 0.5235, +0.027 CI[+0.005,+0.047] CI-sep; + FOREGROUND
window (candidates referenced within 2 sentences first) 0.5319, +0.035 CI[+0.013,+0.059] CI-sep.** Both PINNED mechanisms
(KTG reviewing+impletion: every reference raises the token's activation; Glenberg availability). The earlier "files are
worse" reading was the engine defect; re-measured below.


**BUILD CELL `experiments/exp_affected_entity_token_history_gum_v1.py` (THIRD, n=596 gold roles / 593 predicted):**
three PINNED mechanisms over the landed resolver, full control stack:
| arm | gold roles | predicted parse (deployment) |
|---|---|---|
| incumbent (landed resolver) | 0.4966 | 0.4418 |
| + pronoun ACCRUAL (token impletion) + FOREGROUND window W=2 | 0.5252 (+0.0285 CI[+0.005,+0.054]) | 0.4654 (+0.024 CI[0.000,+0.047]) |
| + PRINCIPLE A for reflexives (must corefer with the clause-mate; 23 items) | **0.5403 (+0.0436 CI[+0.017,+0.071])** | **0.4789 (+0.0371 CI[+0.012,+0.062])** |
| CONTROL accrual scrambled (pronoun written to a random compatible entity) | 0.4446 (−0.052 CI-sep) | 0.3895 (−0.052 CI-sep) |
| CONTROL window scrambled (random same-size in-focus set) | 0.2164 (−0.280) | 0.1838 (−0.258) |
Sweeps (gold): W 1/2/3/5 = .525/.525/.520/.522 (flat); decay 1.0/1.5/2.0/3.0 = .478/.512/.525/.527; clock order/tokpos/sent =
.525/.525/.513 -> the organ's own operating point (d=2.0, mention-order clock) is kept; W=2 reported (W=1 identical).
Gold-free online entity files (Heim file-change) now measure at parity with head buckets (0.5235 vs 0.5235 with accrual):
the TOKENIZATION is not where the forward-half gain lives; the ACCRUAL and the FOREGROUND are.


**Arm-2 opening probe (v8, THIRD, on top of the landed forward half 0.5307 here):** in-focus event-history coherence
through OUR meaning hub (`coherence_reader.relatedness`, the ATL PPMI+SVD associative store): exact same-predicate null
(0.5307 -> 0.532, CI incl. 0); hub sim(V, past predicates) HURTS (top-2 −0.043 CI-sep at tau=1; gated to near-ties null);
patient-role-only sim null/negative. REFUTED-AS-BUILT: associative relatedness between predicates is NOT the brain's
event-role expectation (P(patient | agent, verb) is a role-typed joint, not word association). The residual is
structural by the counts (gold distance: same sentence 0.75 / previous 0.59 / 2-3 back 0.28 / >=4 0.03) -> next: Centering
Cb continuity (attentional state) and the anatomy of the in-focus residual.


**Residual anatomy inside the top-3 (v9, THIRD, 122 of 274 wrong items have gold in the top-3):** the wrong PICK is the more
established entity on every structural cue — n_mentions 6+: pick 57 vs gold 29 (gold single-mention 57 vs pick 21); current-
sentence subject: pick 44 vs gold 17; realised in the previous sentence's Cf list: pick 72 vs gold 56; same-sentence last
mention: pick 81 vs gold 52; gold's last role OTHER (oblique/possessive) 39 vs pick 20. Consistently, Centering Cb-continuity
bonuses (prev-utterance top Cf / any Cf) and a current-subject penalty all HURT (CI-sep) — the resolver is already too
topic-biased for OBJECT pronouns. Reading: object pronouns here point at NEW, low-prominence referents (recently introduced
objects/obliques), while the ACT-R sum with SUBJECT 4.0 / OBJECT 2.0 / OTHER 1.0 and unbounded history lets the protagonist
steal them. Next: sweep the operating point of the pinned computation (role-prominence magnitudes for the object-pronoun
resolver; history depth of the base-level sum; decay) rather than add a term.

## 4. Where the signal is lost (upstream trace, numbers)
1. **Instrument:** 48% of the slice is not an entity-salience task (deictic/demonstrative/other). Measure THIRD separately;
   route DEICTIC to a speech-situation (speaker/addressee) arm and DEMONSTRATIVE to abstract anaphora.
2. **Individuation (coref forward half):** tokens are head-lemma buckets with no pronoun history. Oracle prize +0.091 on
   THIRD. Gold-free files so far capture ~+0.01. This is the coref two-half machine (owner-DONE 09-10) — the forward half.
3. **Reachability:** 10% of THIRD items have no prior non-pronoun mention (62) and 11% have the gold >=4 sentences back
   where the prior is blind (0.03) — the PROTAGONIST/topic index (Zwaan) that keeps the discourse topic available
   regardless of recency; the brain's entity token for the protagonist does not decay like a peripheral mention.
4. **Semantic fit inside the focus:** top-3 ceiling 0.753 vs 0.497 — the brain's JOINT agent+verb expectation over the
   in-focus tokens plus state compatibility; generic marginals do not carry it here.

## 5. Rejected / not to redo (with numbers)
Marginal selectional or GEK reads fused over all candidates (−0.045..−0.118 CI-sep); same inside top-k without a
prior-precision gate; ROC history->verb PPMI (null); the state register as an input (no entity-keyed state on GUM).

## 6. Build direction (next)
A. THIRD-only instrument + class routing. B. Entity tokens with full history: the resolver resolves every pronoun
incrementally and accrues it to the file (forward half), sweep decay/clock; protagonist persistence (frequency term of
ACT-R with the FULL history is exactly this). C. In-focus semantic fit from the document's own event history via the
meaning hub (similar predicates -> same token) and VerbNet start/result compatibility (the state read), gated by the
prior's precision (Kuperberg-Jaeger) — tau swept. D. Control stack + predicted parse + board arm.
