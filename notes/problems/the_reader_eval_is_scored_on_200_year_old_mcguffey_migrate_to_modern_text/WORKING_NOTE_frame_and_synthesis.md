# Working note — brain-foundational frame + prior-work synthesis (solver_opus48_mcguffey)

Opened 2026-08-30. This is my scratch/plan; SOLVED.md is the deliverable.

## THE BRAIN-FOUNDATIONAL SPINE (why this is not bookkeeping)
The brief frames this as pure measurement-fidelity ("change the eval distribution, not the mechanism").
Deeper truth (owner directive 2026-08-30): **the corpus-age delta IS a brain-fidelity probe.** A human who
learned on modern text comprehends modern text — the brain's coref + role-assignment mechanisms are
DISTRIBUTION-INVARIANT. So if a reader organ wins on McGuffey but LOSES on modern text, that proves the organ
copied a McGuffey-specific REGULARITY, not the brain's operation.
- **Role assignment discriminator:** McGuffey (1830s schoolbook) is almost all canonical SVO, animate-agent-first.
  Bever's NVN "first-noun=agent" shortcut scores high there. Modern text (UD-EWT web, passives/clefts/non-canonical
  order) breaks the shortcut but the brain's STRUCTURE-based mechanism (Competition Model cue-validity; Lewis &
  Vasishth 2005 graded cue-based retrieval; localised pMTG/inferior-parietal per audit) handles it. **The delta on
  a NON-CANONICAL subset measures structural-mechanism vs NVN-shortcut directly.**
- **Coref discriminator:** McGuffey chains are short/recency-clean. Brain resolves via salience-ranked discourse
  entity file + feature agreement (Centering; ACT-R activation). LitBank long chains with competing antecedents
  stress THAT mechanism. Already validated: graded ACT-R 0.775 on LitBank competitive pronouns (owner-DONE).

## PRIOR WORK — DO NOT RE-DERIVE (cite these)
1. Who-did-what/binder on LitBank: `exp_wire_predarg_binder_litbank_whodidwhat_v1` arc+GRADED 0.3328 vs RAND-twin
   0.1064 (CI-sep), 100 docs; PARSE_CAP arc-minus-gold delta -0.0047 NOT_SEP (parse not the cap).
2. Parse survives 19c prose: `role_assignment_is_untested_on_archaic_literary_prose` SOLVED/EXCELLENT (integrated
   2026-08-29). LitBank subject-ID 0.9423 >= modern 0.8909; downstream coref delta -0.0009 (CI incl 0); shuffle
   positive control DOES move it (0.613->0.528). => parse is NOT the confound; eval DISTRIBUTION is.
3. UD-EWT gold-parse->role pipelines exist: `exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1`
   (PATIENT_LABELS={"obj","nsubj:pass"}, gold from gold conllu); `exp_reader_endtoend_modern_indomain_construction_
   gold_v1` (who-affected UD-EWT gold-parse-derived, end-to-end BACKOFF 0.7611, held-out UD test 0.9048).
4. **McGuffey-vs-modern who-affected delta ALREADY measured: -0.0011** (0.7611 modern vs 0.7622 McGuffey), verdict
   DEEPER_BOUND_REGISTER_NOT_LIMITER. McGuffey ingest harmless (`exp_mcguffey_ingest..._degradation_v1` HAND=NAIVE=
   HARDENED=0.5833). Cross-domain modern-Wikipedia coref: `exp_coref_residual_crossdomain_gap_v1` structural 0.684
   vs recency 0.525, residual SEMANTIC_WALL_NOT_PARSE_WALL.
5. The 57-passage McGuffey situation-model eval = `exp_wire_organs_endtoend_v1`. DISK numbers (metrics.json,
   verdict MEASURED): live end-to-end role_acc **0.4831 all / 0.5621 in-scope**; vargs-frontend **0.7360 all /
   0.8562 in-scope**; front-end in-scope 0.359->0.822; info-free twins LOSE (0.438 all / 0.510 in-scope).
   **DISK OUTRANKS BRIEF: brief's "0.517->0.742" is approximate; real is 0.483->0.736.**
6. Name/nominal branch shattering (65.6% multi-name entities) is a SEPARATE filed problem
   (`the_name_branch_shatters...`, claimed by solver_opus48_nameclustering). NOT MINE.

## THE NET-NEW GAP (mine)
No single unified per-organ **McGuffey-population vs modern-population delta scoreboard** exists (role + coref +
situation-model, both populations, recomputed floors + info-free twins). Pieces exist per-organ, unassembled.
Specifically the COMPOSED situation-model REGISTER eval (the 57-passage entity-role-at-clause-T task) has NEVER
been migrated to modern text. That + the brain-fidelity discriminator (non-canonical order) is my contribution.

## HONEST INTERSECTION BOUND (state it, don't hide it)
No modern NARRATIVE corpus on the shelf has BOTH gold coref AND gold roles on the same passages. Gold sources are
DISJOINT: LitBank = gold coref chains (incl pronouns, 19c literary); UD-EWT = gold roles/parse (modern web, no
coref). race/social_iqa/onestop/simplewiki/mcscript2 ship no reader gold (mcscript2 = NO_TEXT_SOURCE on disk).
=> validate ROLE on UD-EWT gold + COREF on LitBank gold separately; the fully-composed both-gold situation-model
on ONE modern narrative is the next gold to build (propose it).

## PLAN
1. Reproduce McGuffey baseline (scaffold-free) — pin the McGuffey-population numbers.
2. Build MODERN situation-model gold from UD-EWT gold parse (transparent UD deprel->role; string-identity entity
   tracking across a doc's clauses), in the McGuffey gold SHAPE, WITH a CANONICAL vs NON-CANONICAL split.
3. Revalidate the SAME reader pipeline (live_extract_raw position/vargs -> resolve_raw -> score_endtoend) on it:
   each arm beats strongest floor recomputed on modern population, info-free twin LOSES CI-sep.
4. Coref dimension: confirm/cite LitBank gold-coref revalidation for the scoreboard.
5. Assemble unified per-organ McGuffey-vs-modern delta scoreboard + recommendation.
6. Scaffold-free witness in verification/. SOLVED.md + ledger --check.

NO LLM at inference or for gold. Glass-box. Change the CORPUS, not the organ.
