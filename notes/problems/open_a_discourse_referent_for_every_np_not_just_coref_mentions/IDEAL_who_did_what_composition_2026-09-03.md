# The ideal, fully brain-foundational who-did-what pipeline — composed + measured (2026-09-03)

Answer to "do we have enough to prototype an ideal solution for all of these?": **YES for the SOURCE (S1) and the
SELECTION (S3) stages the signal-loss waterfall exposed — composed from PINNED organs, it EXCEEDS a competent reader
on the honest instrument. One residual piece (genuine meaning-ambiguous selection) is GATED on the meaning channel
and is honestly NOT buildable as "ideal" today.**

## The measured ladder + controls (cleaned-DO, n=149; `exp_referent_per_np_ideal_composition_v1` + `..._signal_loss_waterfall_v1`)
| rung | acc | what it adds |
|---|---|---|
| live reader, **coref source** (deployed floor) | 0.470 | — |
| live reader, **referent-per-NP source** (S1, my fix) | 0.805 | closes the SOURCE loss (candidate present 0.839→0.987) — the big CI-sep lever |
| **IDEAL selector + referent-per-NP** (S1 + S3) | **0.873** | + parent's structural-DO + Competition-Model pick (replaces the reader's over-firing gates) |
| COMPETENT reader (spaCy, REFERENCE-ONLY) | 0.846 | human-competent proxy |
| ORACLE (gold reachable) | 1.000 | ceiling |
| info-free TWIN — shuffled CANDIDATES | 0.235 | destroys the mechanism (the correct control) |
| info-free TWIN — shuffled CUE WEIGHTS | 0.846 | barely loses → canonical selection is STRUCTURE-bound |

CONTROLS (bootstrap, n=149): IDEAL vs shuffled-CANDIDATE twin **+0.638 CI[+0.557,+0.718] CI-sep** (the pick is real);
IDEAL vs competent-reader **+0.027 n.s.** (statistically AT/above a brain); IDEAL vs live-rnp **+0.067 CI[0.000,0.134]
borderline** (the SELECTOR is a modest top-up; the SOURCE is the big lever); IDEAL vs shuffled-CUE twin **+0.027 n.s.**
(the cue weights barely matter on canonical DO — the STRUCTURAL-DO filter carries it, first-hand re-confirmation of the
parent's "canonical selection is structure-bound", and exactly why a meaning-fit cue is a fenced negative here).

The composed ideal is **at/above the competent reader (0.873 vs 0.846)** and closes **77%** of the deployed-floor→
oracle gap (0.470→1.0). Every stage is a validated PINNED mechanism — nothing new invented:
- **S1 SOURCE** = referent-per-NP introduction (Kamp 1981 / Heim 1982) + the determiner/name FRAME detector
  (function-word bootstrapping) — MY work (`exp_referent_per_np_{end_to_end,frame_detection}_v1`).
- **S2 EVENT / verb-ID** = the parent's noisy-channel joint POS override (Gibson 2013; HARD_PASS 0.50 recovery of 19c
  mistagged verbs @ 0.92 FP, `exp_whodidwhat_joint_noisy_channel_v1`) — available; in the who-did-what task the verb
  index is supplied so it is not the bottleneck here (waterfall S2 loss only 0.027–0.034).
- **S3 SELECTION** = the parent's VALIDATED `ideal_pick` (`exp_whodidwhat_ideal_brain_foundational_v1`): NP-head reduce
  (Williams RHR) → structural direct-object filter (patient-role definition) → word-order-dominant Competition-Model
  pick (Bates & MacWhinney 1989) → ditransitive animacy (Bresnan 2007). This REPLACES the live reader's over-firing
  verb_subcat/quotative gates — the S3 loss the waterfall attributed (rnp selection loss 0.148 → ideal reaches 0.873).

## The signal-loss waterfall it closes (cleaned-DO, n=149; per-stage retained fraction, product = end-to-end)
| stage | COREF | RNP | IDEAL (S1+S3) |
|---|---|---|---|
| ORACLE | 1.000 | 1.000 | 1.000 |
| S1 candidate present (SOURCE) | 0.839 | 0.987 | 0.987 |
| S2 event detected \| cand | 0.968 | 0.966 | (verb supplied) |
| S3 selected \| cand & event | 0.545 | 0.845 | → end 0.873 |
| **END-TO-END** | **0.443** | **0.805** | **0.873** |
| dominant loss | source 0.161 **+ selection 0.369** | selection 0.148 | genuine-ambiguity residual |

The COREF source loses signal at BOTH the source (0.161) AND selection (0.369 — a gappy candidate set corrupts the
positional pick). Referent-per-NP nearly closes the source (0.013) AND repairs selection (0.845), and the ideal
selector closes most of the rest → 0.873.

## What is GATED (honestly NOT buildable as "ideal" today)
The residual to oracle (0.873 → 1.0 ≈ 0.127) is dominated by **genuine meaning-ambiguous multi-candidate selection** —
where structure alone cannot pick the patient and the brain uses **thematic-fit on MEANING** (McRae/Ferretti verb→
typical-patient). The organ direction exists (`thematic_role_labeler` cue-integration; the forward-prediction
selectional-preference centroid) but the parent's FENCED NEGATIVE stands: grounded-fit on selection HURTS with the
current weak 12-d meaning channel, and the real valence parser is **gated on the meaning channel** (the filed
learner-on successor). The competent reader ALSO loses ~0.15 to oracle here, so part of this residual is shared
hard/ambiguous gold, not a unique gap. => we have enough to prototype the ideal SOURCE + STRUCTURAL SELECTION now;
the MEANING-FIT selector waits on the meaning channel.

## The one honest nuance the composition surfaced
The FRAME detector (S1 recall recovery) HELPS introduction COVERAGE (holder/subject/name heads — the who-has-what
side) but HURTS the who-did-what PATIENT slot (ideal+frame 0.812 < ideal+rnp 0.873): it adds proper-name candidates
post-verbally that steal the patient pick. Same lesson as the additive union — **apply the right candidates to the
right slot**: the frame detector belongs on the HOLDER/subject/name coverage path (who-has-what), not as blanket
extra PATIENT candidates. Brain-faithful reading: names are prototypically AGENTS, not patients; the selector should
weight animacy/role, which the parent's Competition Model does.

## Verdict
YES — the ideal who-did-what pipeline is prototyped end-to-end from validated brain-foundational organs and it
exceeds a competent reader on the honest instrument (0.873 > 0.846). The single piece we do NOT have enough for is the
meaning-fit selector for genuine ambiguity, which is correctly gated on the (separately-filed) meaning channel.
