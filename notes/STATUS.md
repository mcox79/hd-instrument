# STATUS

AS OF: 2026-08-16 | branch `dataprep/mcguffey-graded-corpus` | HEAD `03055c7fa` | GROWTH PAUSED | origin merge needs USER AUTH
Rules: `STATUS_SPEC.md`; every stub resolves in `STATUS_LESSONS.md` (uncapped: CIs, paths,
superseded-by). Cap 8704 B, AT CAP. FOUR literals MACHINE-PARSED, never reword: `AS OF:`,
`## POSITION`, `## TOP ITEM`, `## WHAT IS RUNNING` (`session_start_hook.py`, `board.py`).
CHAIN: HANDOFF...08-14 -> HERE -> LONG_TERM_PLAN.md -> RECOVERY_PROGRAM.md.

## POSITION
Read-out still BELOW its spelling floor: hit@1 4.80% vs TRIGRAM-ONLY 8.70%, CI-separated
(`exp_orthographic_floor_vet_v1`, reproduced off disk tonight). Two STRUCTURAL gaps measured
tonight: we built ONE of the brain's TWO relational hubs, and the target space is missing CHANNELS.
The missing hub did NOT rescue bridging. 0 of 7,769 banked cells meet the bar.

## TOP ITEM -- MISSING CHANNELS, NOT MISSING DIMENSIONS (LESSONS: TARGET SPACE)
Our 12-dim landing space covers 2 of the brain's 7 attribute blocks. Adding AFFECT (Warriner VAD, on
disk, unused) lifts the hand-rated SimLex ceiling 0.3130 -> 0.4143, paired +0.1013
[+0.0615,+0.1419] on 977 pairs, CI-SEPARATED; nouns +0.0253 NOT sep, verbs +0.1228 and adjectives
+0.3399 separated -- the GAIN profile mirrors the FAILURE profile. NEGATIVE CONTROL FIRED: +11
rater-SD cols (23d) 0.3035 and +6 derived cols (18d) 0.3025 sit BELOW the 12d incumbent, so widening
without a CHANNEL buys nothing (`03055c7fa`). SCOPE: ceiling diagnostic, K1, no floors, no null, NOT
a cell -- it clears nothing, it decides what enters a can-fail cell. Decider RUNNING. Two prior
gates had excluded affect on non-brain-framed criteria (LESSONS).

## BRIDGING -- THE CENTRAL NEGATIVE, AND IT IS READABLE (LESSONS: DO-NOT-REDO 38)
`exp_thematic_..._v2` SMOKE (FULL running): bridge rho 0.0270 vs floors 0.0412/0.0209/0.0900 on the
identical stratum (n=394) -> -0.0615 NOT_SEPARATED, BOTH known-answer arms PASSING (K1 0.3301,
K2_ORACLE 0.2893) -- a REAL null, not a dead instrument. BRIDGED CODES KEEP IDENTITY (96.1%
distinct) AND LOSE MEANING (retention 0.0819). Verbs/adjectives POWER_INSUFFICIENT, NEVER "verbs
fail"; noun>verb appears with NO graph and NO bridging too, so it is the TARGET SPACE, not the
ordering mechanism (Hills falsifier neither satisfied nor violated). AUDIT CORRECTION: the EXTERNAL
curated CSKG ceiling arm ALSO fails (0.0457 NOT_SEP), so the cell's "OUR relations are the limiter"
is unsupported -- verdict stands, framing does not.

## TWO HUBS / STORAGE / SPARSE CODE (LESSONS: TWO HUBS, STORAGE, SPARSE CODE, FLOOR VET)
TWO HUBS: taxonomic (anterior temporal) we had; THEMATIC (separate temporo-parietal, developmentally
PRIOR) we had not, despite owning `extract_predicates_v62` (221 facts, NO CALLERS). Enabling it:
bridge degree 1.216 -> 3.573, stratum 47 -> 394, verbs 0 -> 86; morph-blocking changes nothing.
STORAGE HAS AN ISOLATED INSTRUMENT NOW (supersedes "no instrument = step 1"): the flat store is
ADDRESS_ABSENT (key-sensitivity 0.0, facet addressing EXACTLY 0.2500 = chance, sd 0.0 over 5 seeds);
`HDFactStore` IS addressed but its live index dies at the FIRST FLIPPED BIT. SPARSE CODE:
`C1_KCAP_GRD_f005_BOOST` rho 0.2801 clears all three floors and keeps 3.5264/7 bits, yet its CELL
reads FAILS_BAR and on the REAL task all 18 arms sit CI-separated BELOW spelling -- we sparsified a
HIGH-rank anchor (88.74/256), not the LOW-rank grounded asset (9.15/1024). FOUNDATION v4 ~49%
(`d62acfe58`); TRIAGE -> `RECOVERY_PROGRAM.md`.

## TOOLING STATE (LESSONS: VERDICT BAR, SKIPPED FULLS, C31)
7,769 banked cells scanned (`verdict_bar_check.py`, `c0802fc36`): 0 MEET the bar; 2,966 NO_FLOOR,
264 SATURATED_CEILING, 4 NO_CI, 1 STRING_PASSES_BAR_FAILS; 238 flagged cells ARE cited by an index
-- OPEN OPERATOR DECISION, NOT TAKEN. KNOWN FALSE-PASS DEFECT (C31), anti-correlated with rigour --
DO NOT TRUST A `MEETS_BAR` UNTIL THE FIXED RE-SCAN LANDS. Checkpoint fix `ee7c42c0f`; ~128 skipped
fulls, 30 verified fake BY REPRODUCTION (23/29 bit-identical to a fresh smoke); 1 demotion, 2
upgrades, 0 of 30 meet the bar.

## DO NOT REDO -- NEVER-TRIM -- stubs; detail in LESSONS
All CLOSED. `*` = revival criterion. 1 intersection-over-argmax; 2 the "40% ceiling"; 3 syntactic
bootstrapping*; 4 F2 freq-corrected pool*; 5 same-sentence cosine/PMI; 6 FHRR superposition; 7 PBV;
8 read-out vs v5's 64%; 9 F1+F3 stabilisation; 10 news->textbook swap; 11 norms as FILTER*; 12 sense
selection v2; 13 minimum-grounded-basis; 14 `genuine_cross_source_corroboration_v1`*; 15 combined
dictionary v1; 16 "context vector is noise"; 17 co-occurrence as the explanation; 18 role-bound
structure alone -- STRUCTURE_HURTS*; 19 frontmatter `isolation:`/`background:`; 20 the voting
mechanism*; 21 hand-scored delta at 1-3%; 22 the 2-hop bridges; 23 extraction as DIRECT-BANK*;
24 distinctiveness as log-IDF*; 25 differentia/genus + supply; 26 `sign()` vs forgetting kernel;
27 rank-1 common-mode removal*; 28 FORAGE_REFUSAL; 29 five-stage read-out chain; 30 near-duplicate
anchors; 31 supply as an ADDITIVE CHANNEL -- NARROWED*; 32 DG/pattern-separation for grounding;
33 crowding as a gate criterion; 34 the GRADED SWITCH*; 35 +0.0602 as a C3 number; 36 `k_eff~=50` as
a MEASURED limit*; 37 "right neighbourhood, wrong member"*; 38 bridging WITH the THEMATIC hub --
MEASURED NULL*; 39 sparsifying the READING anchor -- dies on the real task*; 40 quoting +0.2285 as
the bridging margin; 41 quoting a "0.073 lift gap"; 42 `grounded_similarity()` AS A SCORER --
76.18% of SimLex on two values, NO revival.
CAVEATS: D1 near-vs-far; D2 encoder-swap; D3/D4 foraging reversals; D5 sharpening SMOKE-only;
CT1 consistent!=good; CT2 run_mode is an ingestion constant.
CORRECTIONS: C1 availability-binds-first; C2 CLIP-at-INGEST; C3 the 94% has NO floor;
C4 DGProj=interference; C5 an encoder EXISTS; C6 wrong checkpoint; C7 opp-map #5/#6; C8 comparator
was a LOOKUP TABLE; C9 results ARE searchable; C10 tautology=eligibility bug; C11 "58% common mode";
C12 doc date; C13 the FULL DID report; C14 whiten+pinv IS tested; C15 chain self-contradiction;
C16+C22 `A5_STRINGCTRL` not zero-meaning; C17 scramble is DONOR-RULE dependent; C18 conjunctive lean
QUALIFIED; C19 k_eff correction-of-a-correction; C20 "0.90 precision" UNSOURCED; C21 "0.95"=parse
coverage; C23 121.1M-token encoder/237.7M corpus; C24 norms stale BOTH ways; C25 shortlist-hit out
of scope; C26 FHRR 0.956 bare threshold; C27 VET residue; **C28 +0.2285 was a NEIGHBOUR-CHOICE
diagnostic -- the bridging cell's own instrument reads -0.0142 NOT_SEP; C29 the "0.073 lift loss" is
0.0034 (0.2667 vs 0.2701), populations mixed; C30 "retrieval fine / we tie spelling" is EXACT-KEY +
OPTIMISTIC-TIE ONLY; C31 the checker's false pass was THREE defects.**

## STANDING DISCIPLINES -- NEVER-TRIM -- LESSONS
1 NO HAND-SCORED MEANINGFUL-DELTA GATE WHILE THE GENERATOR SITS AT 1-3% -- cost TWO experiments, the
2nd claiming to have FIXED the 1st; gate on KNOWN-ANSWER RECALL. 2 SERIALIZE MEASUREMENT vs CODE
CHANGE (2x). 3 A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT (4x in one night; C31 = 5th).
4 ESTABLISH THE FINAL LANDED VERSION BEFORE EVALUATING A SUBSYSTEM (6x); AN ABSENCE CLAIM REQUIRES
AN ENUMERATION, NOT A SEARCH -- state HOW. 5 BEFORE GATING ON A BENCHMARK, CHECK THE BRAIN PERFORMS
THE OPERATION IT SCORES. 6 RUN A POSITIVE / KNOWN-ANSWER ARM (2x): a FLOOR says whether the EFFECT
is real, a KNOWN-ANSWER arm whether the INSTRUMENT is -- run both. 7 NO DEMOTION WITHOUT A FRESH
ON-DISK RE-CHECK -- ~11 wrongly demoted, 17 corrections-of-a-correction in 48h; keep
EXISTS/IS-REACHED/IS-GOOD separate. 8 A GATE IS A CI-SEPARATED MARGIN ABOVE max(ORTHOGRAPHIC,
FREQUENCY, SCRAMBLE) on the IDENTICAL scorer/n/pool/gold -- never a bare number, baseline STANDALONE.
9 DETECTORS FIRE ON HONESTY (49/49 flagged were false positives). 10 SILENT JOINS FABRICATE GREEN
AND RED -- ASSERT+COUNT joined rows. **11 A NUMBER MAY NOT BE CARRIED BETWEEN SCORERS OR
POPULATIONS -- cost 3x in one night (C28/C29/C30); name the scorer, n, pool and gold for BOTH sides
or you have no comparison. 12 A CLAIM MEASURED AT THE EXACT-KEY OPERATING POINT DOES NOT TRANSFER
TO THE PARTIAL-CUE REGIME, WHICH IS THE REAL ONE -- top-50 0.5566 exact-key vs 0.3758 partial-cue:
from "ties spelling" to CI-separated BELOW both spelling and pure popularity; state the cue regime
beside every retrieval number. 13 REPORT TIE CONVENTIONS BOTH WAYS, NEVER SILENTLY PICK THE
FLATTERING ONE -- the top-50 spelling comparison flips from +0.0105 NOT_SEP to +0.0641 ABOVE (in OUR
favour) because the floor holds 15.27% tie mass and we hold 0.0%.**

## WHAT IS RUNNING / BLOCKED
- Phase 2 FULL `exp_thematic_..._v2` -- `scratch/them_v2_full.pid` (shim 30812, worker 35328);
  LOCAL, hours. DO NOT TOUCH. AFFECT DECIDER `exp_target_space_vs_bridge_mechanism_v1`
  (`scratch/ts_decider_smoke.pid`), gate PASS n=372, owns `data/exp_target_space_*`. Checker-fix
  RE-SCAN running (C31). Sparsify-the-right-object: skeleton only, nothing measured.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB): NO BACKUP, gitignored.
- STEP 4 (`d=256->1024`) HELD PENDING USER AUTH. Merge to `origin/main`: USER AUTH required.
- `LONG_TERM_PLAN.md` is DIRECTOR-OWNED; its sec 2 rows 3/4/6 are superseded by STORAGE + C30.
- OVER CAP BY ~720 B AND DELIBERATELY SO: never-trim stubs alone now cost 4,536 B of 8704 (tonight
  added DO-NOT-REDO 38-42, C28-C31, disciplines 11-13). Every other section is already UNDER its
  SPEC budget. Escalation steps 1-2 are spent; step 3 (a raise to 9216 B) is MEASURED AND PROPOSED
  in `STATUS_SPEC.md` sec 7 and is the Director's call, not a maintainer's. Do NOT close the gap by
  evicting a never-trim entry.
