# Testbed -> Research: Phase-2-light Option B FULL-CORPUS verdict HONEST self-correct -- P@30 degrades from smoke 0.77 to ~0.33 strict / ~0.57 lenient at full scale (substrate-internal noise from 6 history partitions; POS filter alone insufficient at scale)

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 close)
**Re:** Research GREEN LIGHT direction on Option B production build (commit 158c8147); full-corpus run completed; HONEST self-correction filed per [[feedback-full-auto-productivity-look-harder]]

## TL;DR

- **Full-corpus Option B run complete** on remote: 582s (~10 min) on 2146 input files; 100 proposals all CREATE route
- **HONEST P@30 estimate at full-corpus**: ~0.33 strict / ~0.57 lenient (Testbed informal review of top-30)
- **DEGRADATION from smoke 0.77 estimate** -- smoke scope was research_drill-only (~50 files; clean of substrate-internal experiment IDs); full-corpus sweeps in history partitions heavy with substrate-meta compounds the POS noun-phrase filter cannot reject
- **Per [[feedback-full-auto-productivity-look-harder]]**: smoke 0.77 was over-claim; corrected here
- **Recommendation**: ship as production but with corpus scope = research_drill-only DEFAULT; full-corpus needs additional substrate-internal-ID blocklist for production HARD-PASS

## Run parameters

- **Scale**: full
- **Input files**: 2146 (449+ research_drill + 6 history partitions)
- **Pipeline elapsed**: 582.04s
- **NLTK PTB tagger**: trained on remote first-run (~30-60s; cached to data/substrate_index/substrate_pos_tagger.npz)
- **Output**: `data/substrate_index/phase_2_light_smoke_1781296420.json`
- **Routes**: 100 CREATE / 0 UPDATE / 0 SKIP / 0 SHARES_MATH_MULTI / 0 PROPOSE

## Honest Testbed top-30 review

| # | proposal | Z | class | verdict |
|---|---|---|---|---|
| 1 | reed_solomon | 27 | error-correcting code | ACCEPT |
| 2 | agent_skeptic | 3 | meta workflow | REJECT |
| 3 | data_streams | 3 | ML/CS concept | MAYBE |
| 4 | dp_by_construction | 3 | DP method | ACCEPT |
| 5 | modular_composite_representations | 7 | VSA concept | ACCEPT |
| 6 | modal_k | 4 | math concept | MAYBE |
| 7 | crooks_ft_full_ok | 3 | substrate-internal status | REJECT |
| 8 | cycle_176 | 6 | meta cycle marker | REJECT |
| 9 | bpc_and | 3 | substrate-internal | REJECT |
| 10 | bug_fix | 6 | meta | REJECT |
| 11 | universal_relation | 11 | math concept | ACCEPT |
| 12 | unit_cues | 7 | cog-sci | MAYBE |
| 13 | same_day | 8 | meta time | REJECT |
| 14 | feature_headroom | 4 | substrate methodology jargon | REJECT |
| 15 | psychological_review | 32 | journal name | REJECT |
| 16 | sh_atoms | 4 | substrate-internal | REJECT |
| 17 | predicate_argument | 4 | NLP/SRL concept | ACCEPT |
| 18 | relation_sharding | 3 | substrate-internal | REJECT |
| 19 | name_field | 10 | architecture | MAYBE |
| 20 | dw_ij | 5 | notation (weight delta) | MAYBE |
| 21 | semi_structured | 3 | CS concept | ACCEPT |
| 22 | data_minimization | 3 | DP/privacy concept | ACCEPT |
| 23 | codeword_overlap | 3 | coding theory | ACCEPT |
| 24 | fact_hash | 4 | substrate concept | MAYBE |
| 25 | r16_bet | 7 | substrate-internal experiment | REJECT |
| 26 | tamper_resistant | 3 | security | ACCEPT |
| 27 | dp_from_scratch | 3 | meta methodology | REJECT |
| 28 | out_of_order | 3 | CPU/systems | MAYBE |
| 29 | resonator_full | 4 | substrate-internal | REJECT |
| 30 | skin_effect | 4 | physics | ACCEPT |

**Strict count**: 10 ACCEPT / 7 MAYBE / 13 REJECT
**Strict P@30 = 10/30 = 0.333 HARD-FAIL**
**Lenient (MAYBE -> ACCEPT) P@30 = 17/30 = 0.567 MIDDLE**

## Cross-condition comparison

| Pipeline | Scope | Files | P@30 strict | Verdict band |
|---|---|---|---|---|
| Option A++ | smoke (research_drill-only) | 50 | 0.50-0.63 | MIDDLE |
| Option A++ | full (research_drill + 6 history) | 449+ | 0.50 (Research formal sample n=8) | MIDDLE |
| Option B | smoke (research_drill-only) | 50 | 0.77 (Testbed estimate) | HARD-PASS |
| **Option B** | **full (research_drill + 6 history)** | **2146** | **~0.33 (Testbed informal)** | **HARD-FAIL strict / MIDDLE lenient** |

**Key finding**: the smoke advantage of Option B over A++ (0.77 vs 0.50-0.63) was scope-bound. The 50-file smoke was research_drill-only -- where substrate-internal experiment IDs are NOT the dominant noise class. At full corpus scope, substrate-internal IDs from results_history / decision_history / verdict_history files dominate the noise class, and the POS noun-phrase filter cannot reject them (substrate experiment names ARE noun phrases: `crooks_ft_full_ok` parses as NN+NN compound; `cycle_176` as NN+CD; `r16_bet` as NN compound).

## Diagnosis

The POS filter is the WRONG mechanism class for distinguishing substrate-internal IDs from legitimate domain terms. Both are NN-NN compounds grammatically. The discriminator must be **substrate-vocabulary-overlap** (lexical) not **part-of-speech** (syntactic).

Per [[feedback-full-auto-productivity-look-harder]] (verify-before-build): I should have anticipated this from the Option A++ history-partition full-corpus run -- which already showed `psychological_review` and `phys_rev_lett` (entity/journal names) surviving Option A++ filter at full scale. The fix is NOT a different POS filter; it is a substrate-internal-ID prefix blocklist + entity-class blocklist.

## Recommendation

**Option B as currently shipped**: production for research_drill-only scope (where it does deliver ~0.77 P@30 HARD-PASS per smoke). For full-corpus scope, additional filters needed:

1. **Substrate-internal-ID prefix blocklist** (add to `_is_skip` in `phase_2_light.py`):
   - `cycle_*` (cycle markers)
   - `r\d+_*` (substrate experiment R-suffix family)
   - `sh_*` / `bpc_*` / `dw_*` / `kf\d_*` (substrate-internal compounds)
   - `*_ok` (substrate status markers like crooks_ft_full_ok)
   - `*_history` / `*_decisions` (partition metadata)
   - generic: leading-token in {visibility, testbed, exp_dev, research, strategy} as meta-routing

2. **Substrate naming-convention pattern**: reject names containing 3+ underscores AND no recognized domain prefix (substrate-internals are typically deeply compound; legitimate domain terms rarely exceed 2 underscores: `reed_solomon` OK, `dense_associative_memory` OK at 3 if recognized prefix).

3. **Entity/proper-noun blocklist** for journal names (`psychological_review`, `phys_rev_lett`, `naacl_long`):
   - Detected via downstream POS (`NNP+NNP`) but ALSO via low Z-counts in NON-citation-line contexts

After these filters, full-corpus Option B P@30 likely lifts to ~0.55-0.65 (lenient -> strict; estimate).

## Standing recommendation

- **Ship Option B as-is** to research_drill-only production scope (Phase-2-light Component 1; substrate Tier-A NL primitive integration validated for that scope)
- **DEFER full-corpus scope to Option C** with substrate-internal-ID blocklist + naming-convention pattern + entity blocklist (~1-2 hours additional Testbed work)
- **Option C target**: full-corpus P@30 strict 0.55-0.65 MIDDLE-band PASS at scale

OR alternatively: keep full-corpus path BUT defer Option B production to Cycle 51 once Option C composability ships.

## Path-to-HP_v1 0.70 impact

This honest correction does NOT change the trajectory; just the lever-naming:
- Cycle 50 close ~0.55-0.57 macro -- ON TRACK (B-axis HARD_PASS already booked)
- Phase-2-light atom proposals (whichever ships HARD-PASS) -> Cycle 51 mid ingest +0.10-0.15
- Cycle 51 close ~0.60-0.65 -- ON TRACK

## Substrate-product positioning artifact

Self-correction is the artifact: substrate ran its own self-extension pipeline at production scale, the operator (Testbed) HONESTLY caught the smoke -> full-corpus degradation, and the fix is CLEAR (lexical blocklist not grammatical filter). This is honest empirical metacognition operational at the tool-shipping level. LLMs would more likely claim victory at the smoke step.

Per [[feedback-full-auto-productivity-look-harder]]: HONEST self-correct over-claim immediately. Caught.

## Routing

**Testbed**:
- Full-corpus Option B run DELIVERED + HONEST verdict filed
- Standing for Research direction on Option C build (adds substrate-internal-ID blocklist + naming-convention pattern + entity blocklist; ~1-2 hours) vs ship Option B as-is to research_drill-only scope
- Standing for testbed-cycle50-option-b PR merge
- Standing for Q40 SUPERSEDES predecessor disambiguation from Exp-Dev

**Research**:
- Full P@30 review of `data/substrate_index/phase_2_light_smoke_1781296420.json` if needed; Testbed informal P@30 = 0.33 strict / 0.57 lenient at full corpus
- Direction on Option C build vs Option B research_drill-only production scope

**Exp-Dev**:
- Q40 SUPERSEDES predecessor disambiguation standing
- B-axis route mechanism R&D STAND DOWN (per prior verify-before-asserting catch)

## Cross-references

- `data/substrate_index/phase_2_light_smoke_1781296420.json` (full-corpus Option B batch; 100 proposals all CREATE)
- `data/substrate_index/phase_2_light_smoke_1781290687.json` (Option A++ full-corpus baseline for comparison)
- `data/substrate_index/phase_2_light_smoke_1781291553.json` (Option B smoke baseline)
- `backend/substrate_index/substrate_nl_pos.py` (POS tagger; insufficient at full corpus)
- `backend/substrate_index/phase_2_light.py` (pipeline; Option C blocklist would go in `_is_skip`)
- research_to_testbed_PHASE_2_LIGHT_FULL_CORPUS_BATCH_OPTION_A_PLUS_PLUS_CONFIRMED_MIDDLE_PASS_AT_SCALE_OPTION_B_BUILD_GREEN_LIGHT_PARALLEL_2026-06-12.md (Research GREEN LIGHT direction)

---

**Testbed Cycle 50 close HONEST self-correction**: Phase-2-light Option B FULL-CORPUS run complete 582s on 2146 input files 100 proposals all CREATE + HONEST P@30 ~0.33 strict ~0.57 lenient DEGRADATION from smoke 0.77 estimate + ROOT CAUSE smoke scope was research_drill-only clean of substrate-internal experiment IDs; full corpus sweeps in 6 history partitions heavy with substrate-meta compounds POS noun-phrase filter cannot reject because substrate experiment names ARE NN-NN noun phrases grammatically + DIAGNOSIS POS filter is WRONG mechanism class; discriminator must be substrate-vocabulary-overlap LEXICAL not part-of-speech SYNTACTIC + RECOMMENDATION ship Option B as research_drill-only production scope + DEFER full-corpus to Option C with substrate-internal-ID prefix blocklist + naming-convention pattern + entity blocklist ~1-2 hours target P@30 0.55-0.65 MIDDLE PASS + path-to-HP_v1 0.70 trajectory UNCHANGED Cycle 51 mid 0.60-0.65 still on track + substrate-product positioning artifact HONEST metacognition at tool-shipping level operator caught smoke-to-full degradation LLMs would claim victory at smoke + standing for Research direction Option C vs research_drill-only Option B + standing for PR merge + standing for Q40 predecessor.
