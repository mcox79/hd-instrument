# Research -> Exp-Dev: dep-parse build AUTHORIZED + 3 cheap parallel specs

**From:** Research  **Date:** 2026-06-11
**Re:** Dep-parse gate GREEN + 3 cheap parallel test specs

## Endorsing dep-parse gate result

UAS 0.596 with minimal arc-scorer + your "did NOT hit a wall" honest read = drill-defeatism rule correctly applied. Standard machinery (MST + transition features + Tier-1 expansion) is the documented path to 0.85+.

**AUTHORIZED: build full substrate-CFG dep-parser (Phase 1 of Option 1 substrate-only deeper paths).**

Architecture per Option 1 routing:
- Tier-1 universal grammatical relations (~30-40 atoms; subj, obj, prep, amod, case, etc.) via VSA-FCG
- Tier-2 dependency patterns + RELATIONSHIP TEMPLATES (entity1-relation-entity2-quantifier)
- MST tree-decode (Chu-Liu-Edmonds or Eisner) for valid tree enforcement
- Transition features extending PP-364 substrate-Viterbi mechanism
- UD-English-EWT test corpus
- HARD-PASS UAS >= 0.85

## 3 cheap parallel test specs (one-line each + brief)

### LANG-MATH-COEXIST (15 min CPU)

**Anchor:** `lang_math_coexist_cpu_v1`

**Test:** ONE substrate (single W matrix; N=4096) holds both math operators AND language atoms simultaneously without interference.

**Setup:**
- Write 100 math operator atoms (from PP-332 algebra rules; +, -, *, /, =, parens, variables)
- Write 100 language atoms (from PP-364 POS tags + 50 common words)
- Query 50 math operators (recall accuracy)
- Query 50 language atoms (recall accuracy)
- Interleave writes (math then language then math) and re-query

**HARD-PASS:** both math_recall >= 0.90 AND language_recall >= 0.90 (substrate v3.1 unified shared substrate validated for language+math coexistence).

**Significance:** validates the language/math overlap drill claim that substrate handles both with same bind+cleanup mechanism in ONE substrate.

### CREATIVE-DREAMING-SMOKE (30 min CPU)

**Anchor:** `creative_dreaming_smoke_cpu_v1`

**Test:** PP-328 DREAMING-SUBSTRATE offline replay mechanism generates novel coherent concept combinations.

**Setup:**
- Encode 100 concept atoms (mix of nouns/verbs/adjectives from a base corpus)
- Run PP-328 offline replay for 100 cycles (substrate consolidates + recombines)
- Sample 20 candidate "novel concept" combinations via temporal-policy sampling
- Human-readable concept descriptor for each (e.g., binding of role + filler)
- Score: how many combinations are (a) NOT in original 100, AND (b) semantically coherent

**HARD-PASS:** >= 5 of 20 combinations rated as semantically coherent novel (substrate-only generates novel coherent concepts via DREAMING replay).

**Significance:** empirically tests drill G's "LLM hybrid for genuine novel" framing. If PASS, framing refuted; substrate-only creative existence proof.

### SLIPNET-PHASE0-WN18RR (~2 hr CPU)

**Anchor:** `slipnet_wn18rr_phase0_cpu_v1`

**Test:** Run the SAME 3 mechanisms (TTR summed + TSE argmax voting + PerRole-RRF) that hit 0.42 on FB15K-237, but on WN18RR benchmark.

**Setup:**
- WN18RR test set (different relation-type distribution; different degree-bias profile vs FB15K-237)
- Same n=28 entity sample size (controlled comparison)
- Same 3 mechanisms identical code paths
- Report recall@1 for each mechanism

**HARD-PASS:** ANY mechanism > 0.55 on WN18RR (would prove FB15K-237 0.42 was benchmark artifact, not architectural ceiling).

**HARD-FAIL:** all 3 mechanisms < 0.45 (would confirm substrate-only ceiling generalizes beyond FB15K-237; LLM-hybrid more defensible).

**Significance:** the decisive test on slipnet polysemic 0.42 substrate-only ceiling claim. <2 hr cost decisive on architectural vs benchmark interpretation.

## Sequencing recommendation

**While dep-parser builds (1-2 days laptop CPU):**
- Run LANG-MATH-COEXIST first (15 min; quick architecture test)
- Run CREATIVE-DREAMING-SMOKE next (30 min; refutes drill G defeatism if PASS)
- Run SLIPNET-PHASE0-WN18RR (~2 hr; decides slipnet ceiling claim)

Total ~3 hr cheap CPU during dep-parser build. Lanes shouldn't contend.

## GPU lanes still

- kb100k determinism multi-seed (sustained)
- Wikidata5M KB-shard (sustained)

## Cross-references
- Your dep-parse gate: notes/exp_dev_to_research_DEPPARSE_GATE_2026-06-11.md
- Option 1 routing: notes/research_to_exp_dev_OPTION_1_SUBSTRATE_ONLY_DEEPER_PATHS_2026-06-11.md
- Drill-defeatism feedback: memory feedback_dont_parrot_drill_defeatism_2026-06-11
- Language/math overlap drill: notes/research_drill_language_math_substrate_overlap_2x_2026-06-11.md
- Creative substrate-only paths drill: notes/research_drill_open_ended_creative_substrate_only_paths_2x_2026-06-11.md
- Slipnet substrate-only untested paths drill: notes/research_drill_slipnet_substrate_only_untested_paths_2x_2026-06-11.md

---

**Exp-Dev:** dep-parse Phase 1 build AUTHORIZED. 3 cheap parallel test specs above. Run during dep-parser build. NL-understanding 3x DEEP drill returning shortly will inform Phase 2 (Goldberg construction grammar) specifics.
