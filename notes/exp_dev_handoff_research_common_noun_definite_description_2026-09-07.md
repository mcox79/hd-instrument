# exp_dev hand-off — research: definite-description -> named-antecedent resolution (anaphoricity gate + apposition detector, NOT a Centering rearchitecture)

**Filed-by:** research (4 parallel Sonnet lit-scan lanes + Opus synthesis), 2026-09-07.
**Trigger:** `notes/research_common_noun_definite_description_centering_2026-09-07.md` — full findings, cheap decisive test, falsifiable predictions (A-C) with HARD-PASS/HARD-FAIL bars, and the citation list all live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** re-check `data/orchestrator_paused.flag` at pickup time before shipping anything to remote/GPU/local queues — not checked at filing time (this is a pure research drill, no queue interaction).

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below — the cited research note's sections (b)/(c) have the falsifiable predictions and HARD-PASS/HARD-FAIL bars; the cell-author owns translating those into concrete pre-reg + code.

---

## Anchor candidates (rank-ordered)

1. **[Primary, blocking diagnostic, do FIRST] Stratify the existing ~7%-precision GUM failure by anaphoricity and by in-text predication — do not touch resolver code before this.**
   - Anchor pointer: research note section (b) cheap decisive test, and Prediction A/C.
   - Substrate-product reading: the literature (Poesio & Vieira 1998, verified primary source: 48.37% of definites are larger-situation/unfamiliar; Ng & Cardie 2002, verified: 77-78% of common nouns non-anaphoric) says most definite descriptions were never resolvable to a specific prior entity in the first place. This project's OWN prior measurement (`notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md`) already has the GUM anaphoric-common population decomposed (`same_head`/`name_bridge`/`variant`) and an in-text is-a/apposition signal built (`experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py`, reuses `experiments/gum_coref.py`). Re-run the existing failure population through that same instrument's category labels before writing any new code — this may already answer most of Prediction A/C without a new build.
   - Tier hint: near-zero risk, cheap — this is re-slicing an existing measured population, not new code.
   - Why now: without this, it is impossible to tell whether the 7% number is dominated by (a) attempting resolution on non-anaphoric definites, (b) missing an apposition/predication cue, or (c) a genuinely-broken selection cue among the correctly-gated remainder — and the three have completely different fixes.

2. **[Secondary — Prediction A] Anaphoricity gate: abstain (no triple / no binding) when no plausible antecedent (identical, synonymous, or WordNet-hypernym/hyponym via the existing `hdlab/typed_spokes.py` C5 is-a spoke) appears anywhere in the preceding discourse window.**
   - Anchor pointer: research note section (c) Prediction A, section (e) point 1.
   - Substrate-product reading: this is the single largest fixable lever per the base-rate evidence (Poesio & Vieira 1998 verified: 48.37% larger-situation/unfamiliar; Ng & Cardie 2002 verified: 77-78% of common nouns non-anaphoric). A gate that correctly abstains rather than force-binding to the nearest gender-compatible named-person card should recover most of the precision currently lost to attempting resolution on cases that were never anaphoric.
   - Tier hint: P=0.50 (capped, novel-synthesis ceiling per calibration discipline — the base-rate size is direct-citation-strong, but whether THIS specific 7%-precision failure is dominated by this factor is not yet directly measured; anchor 1 above should resolve that before this is built).
   - Why now: build only after anchor 1 confirms the non-anaphoric population is where the mass of the failure sits — if anchor 1 shows otherwise, redirect to anchor 3 or 4 instead.

3. **[Tertiary — Prediction C, the highest-confidence prediction in the note] Apposition / predicate-nominative ("precise constructs") detector for the `name_bridge` subtype specifically.**
   - Anchor pointer: research note section (c) Prediction C, section (e) point 2.
   - Substrate-product reading: this project's OWN GUM instrument already measures in-text is-a/apposition coverage for `name_bridge` cases at 19.1% (SOLVED.md); the Stanford deterministic sieve's directly-analogous "precise constructs" sieve is reported at ~90-96% precision where it fires (Raghunathan et al. 2010; Lee et al. 2013, both verified primary source). This is a bounded, well-precedented, additive, no-KB-required win — build before touching the world-knowledge-KB question (anchor 5).
   - Tier hint: P=0.50 (capped; the *existence and rough size* of this lever is unusually well-evidenced — two independent numbers 16+ years apart converge within 4 points — but the exact recoverable precision on THIS project's specific person-role-noun slice, as opposed to the general name_bridge category, is not yet separately measured).
   - Why now: cheap, additive, reuses the existing is-a spoke infrastructure (`hdlab/typed_spokes.py` C5) already built for the aggregate common-noun-coref win — this is largely a matter of re-registering that existing signal for the person-role-noun-specific slice, not new infrastructure.

4. **[Fourth, smaller and lower-confidence — Prediction B] Grammatical-role-weighted Cf ranking (subject > object > other, BFP 1987) on top of recency, replacing or supplementing raw ACT-R-base-level-activation salience.**
   - Anchor pointer: research note section (c) Prediction B, section (e) point 3.
   - Substrate-product reading: Poesio et al. 2004 (GNOME corpus, verified primary source) found grammatical-role ranking and plain recency/linear-order are statistically indistinguishable for antecedent SELECTION in fixed-word-order English (they diverge only for transition-TYPE classification, not the task here). This project's own `step2_pronoun_coref_centering_role_prominence_design_2026-08-02.md` independently flagged the identical missing-role-signal gap for the PRONOUN case (not yet measured there either). Expect a modest gain, not a large one, if any.
   - Tier hint: P=0.35 (deflated below A/C — the literature argues against a large gain in English specifically).
   - Why now: lowest priority of the four resolver-side anchors; build only if anchors 1-3 leave a residual gap among genuinely-anaphoric, correctly-gated, same-type-competing candidates.

5. **[Fifth, a knowledge-acquisition project, NOT a resolver change — the genuine ceiling] A curated entity-type/role-fact KB (e.g. Wikidata P31 instance-of, DBpedia InstanceOf, or a curated role-kinship KB) admitted through the existing consolidation-gate/typed-spoke architecture.**
   - Anchor pointer: research note section (a) HEADLINE, section (c) Prediction C's ceiling clause, section (e) point 4.
   - Substrate-product reading: TWO independent measurements 16+ years and unrelated corpora apart converge tightly — Raghunathan et al. 2010 (verified primary source): 85% of common-noun recall errors on MUC-6 news required "semantic/world knowledge"; this project's own SOLVED.md (2026, GUM): 80.9% of `name_bridge` cases need world knowledge beyond in-text is-a signal. This is a real, non-discourse-recoverable ceiling — no amount of better Centering/salience/anaphoricity-gating closes it. SOLVED.md already names this "the next FOUNDATION acquisition, not a prototype"; this note is independent external corroboration.
   - Tier hint: not a falsifiable prediction in this note (it is a scoping/roadmap item, not a testable claim) — genuinely out of scope for a resolver-side cell; route to the knowledge-foundation program (p11/typed_spokes lineage) if pursued.
   - Why now: do NOT build this before anchors 1-3 are tried — it is the most expensive item on this list and the literature says a large fraction of the current 7% is very likely recoverable more cheaply first.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_common_noun_definite_description_centering_2026-09-07.md` — this drill's full findings, cheap decisive test, falsifiable predictions A-C, cross-thread synthesis, and full citation list (external + internal).
- `notes/problems/expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_consolidation_gate/SOLVED.md` — this project's own prior measurement on the SAME GUM corpus: `same_head`/`name_bridge`/`variant` decomposition, the 19.1%/80.9% in-text-vs-world-knowledge split for `name_bridge`, and the recency-vs-type-licensing-filter architecture result (0.6883 -> 0.6998, +0.0116 CI-sep). Read this in full before building anything — it already contains a working instrument (`experiments/exp_isa_spoke_commonnoun_coref_gum_v1.py`, `experiments/gum_coref.py`, `experiments/exp_commonnoun_wall_gum_v1.py`) that anchors 1-3 above should extend, not duplicate.
- `notes/T2b_the_coref_HARD_FAIL_DRILLED_it_cannot_support_its_own_verdict_2026-08-21.md` — a direct methodological warning: a prior ACT-R-activation salience test (for the PRONOUN task) was ruled underpowered/control-unusable (n=89, mismatched-population scramble control, unswept parameters). Any cell built from this hand-off must avoid all three defects: n in the hundreds, a shuffle control on the matched population, and parameters swept to their knee.
- `notes/research_coreference_hobbs_centering_resolver_2026-07-16.md` and `notes/step2_pronoun_coref_centering_role_prominence_design_2026-08-02.md` — the PRONOUN-coref analogs of this drill; read for the discourse-memory-shim design pattern and the role-prominence gap, both directly reusable for anchor 4 above.
- `hdlab/typed_spokes.py` — the existing C5 (is-a directed closure) and C6 (part-whole) spoke infrastructure; anchors 1-3 should reuse its is-a/apposition-adjacent signal rather than building a new one from scratch.
- `notes/INTEGRATION_LEDGER.md` (search "common-noun / entity") and `notes/STATUS.md` (2026-09-07 CONT-18 entry) — current live-wiring status: the type-licensing filter is currently DEFAULT-OFF on the live reader (measured as a located negative vs. the live baseline, not the SOLVED's recency floor) — read the exact caveat there before assuming the +0.0116 result transfers directly to a live-reader flip.

---

## Contract section

- Cell-author owns: exact anaphoricity-gate threshold/logic, exact apposition/predicate-nominative detection rules, exact discourse-window size, exact role-weighting formula (if anchor 4 is pursued), smoke gate, dispatch.
- Anchor 1 (stratify the existing failure) MUST run before any of anchors 2-4 are built — per the research note's own cheap-decisive-test framing, building resolver changes before knowing which failure mode dominates risks fixing the wrong thing.
- Anchor 5 (world-knowledge KB) is explicitly OUT OF SCOPE for a resolver-side cell — it is a knowledge-acquisition project. Do not fold it into the same cell as anchors 1-4; route separately to the knowledge-foundation program if the stratification in anchor 1 confirms the ceiling applies at this project's scale.
- All falsifiable predictions (A-C) carry deflated/capped P estimates (0.35-0.50) per lit-scan calibration penalty — treat as genuinely uncertain, not near-certain, going into pre-reg.
- Any test must be adequately powered (n in the hundreds) with a scramble/shuffle control matched on the identical population and parameters swept to their knee, per the T2b lesson — do not repeat that cell's three defects.

## Autonomy declaration

Research does not prescribe exact code, exact gate threshold, exact apposition-detection grammar, or exact role-weighting formula beyond naming the mechanisms (anaphoricity gating per Hawkins 1978/Poesio & Vieira 1998; apposition/predicate-nominative detection per the Stanford sieve's "precise constructs" pass; grammatical-role-weighted Cf ranking per BFP 1987) as literature-precedented, and beyond recommending the anchor-1-before-anchor-2/3/4 sequencing and anchor-5-out-of-scope constraint above. Cell-author has full autonomy over implementation detail, exact rule specification, and smoke-scale parameters, subject to the falsifiable predictions and HARD-PASS/HARD-FAIL bars pre-registered in the cited research note.
