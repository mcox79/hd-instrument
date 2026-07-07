# Ingest gate-D re-gate: per-seed gate + stronger anti-lexical control (dispatch-ready spec)

Date 2026-07-07. Director preparatory scoping while the encoder-retrieval + resonator-VET + 970K-collision
agents run. Purpose: pre-design the gate-D hardening so it hands straight to exp_dev (Opus, HIGH) when the
critical path clears — no re-derivation. This is the HARD GATE before any ingest scale to 970K.

## The problem (from the Stage-0 FULL VET, QUALIFIED HARD_PASS)
- Gate-D = the encoder-only lexical-shortcut leak control: how much of the 2-hop-composition answer is
  recoverable by NAME/lexical surface alone, WITHOUT the structural ingest path. Lower = ingest is doing real
  relational work, not name-matching.
- FULL result: D = 0.148 MEAN across 3 seeds, prereg ceiling 0.15. It PASSED only on the mean.
  Per-seed [0.13, 0.157, 0.157] => 2 of 3 seeds EXCEED 0.15. ZERO scale headroom, and the leak GREW smoke
  0.117 -> full 0.148. At 970K entities (more name collisions, denser lexical neighborhoods) the leak is
  expected to grow further, not shrink.
- Prereg used MEAN, so this was NOT a violation — but a mean that masks 2/3 seeds over the line is a Goodhart
  signature. The core integration is genuinely CHAIN_GRADE (A-C gap = 1.0, all controls unanimous); this is
  strictly about bounding the ~15% name-shortcuttable fraction before we trust it at scale.

## Two fixes — do BOTH (they are independent and cheap)

### Fix 1: gate on PER-SEED, not mean (a prereg tightening, no code change to the control)
- New HARD-PASS: gate-D < 0.15 for EVERY seed (max-over-seeds < ceiling), not mean < ceiling.
- Report per-seed D + max-D as the ship metric. This removes the mean-masking Goodhart hole.
- HARD-FAIL: any seed >= 0.17, OR max-D trend increases vs smoke (leak growing with scale is the disqualifier).

### Fix 2: STRONGER anti-lexical control — the name-similar distractor pool
The current gate-D leak-check almost certainly draws distractors from a random/global pool, so the encoder-only
arm only has to beat lexically-UNRELATED names — an easy bar that understates the true shortcut. Harden it:
- For each query's correct answer entity, build the distractor pool from its NEAREST LEXICAL NEIGHBORS
  (surface-form similarity: shared tokens / high char-n-gram Jaccard / small edit distance on the entity name),
  NOT random draws. This forces the encoder-only arm to distinguish the true answer from names that LOOK alike.
- If ingest is doing real relational work, the STRUCTURAL arm (A) stays high on this harder pool (relation
  binding is name-agnostic) while the encoder-only arm (D) drops — WIDENING the A-D gap. That gap, on the
  hardened pool, is the honest non-vacuousness proof.
- Pool size: match the original gate-D negative count so the chance rate is unchanged (control the base rate;
  only the DIFFICULTY changes, per the paired-trials + base-rate disciplines).
- Firing control for the control: on a SCRAMBLED encoder (or shuffled name->code map), the hardened gate-D must
  collapse to chance — confirms the metric measures lexical shortcut, not an artifact of the harder pool.

## Expected outcome (honest pre-registration of the belief)
- Most likely: on the name-similar pool, encoder-only D drops (harder to shortcut when distractors look alike),
  A holds => A-D gap WIDENS => a STRONGER non-vacuousness proof than the current 0.85 bound. Good case.
- Possible: D stays ~0.15 or rises (the shortcut is partly genuine lexical co-occurrence the encoder learned) =>
  then the ~15% name-shortcuttable fraction is REAL and we must either (a) accept a bounded non-vacuousness of
  ~0.85 as the honest ceiling at scale, or (b) add a relation-only readout path that ignores name surface.
  Either way we learn the true number instead of a mean-masked pass.
- The scale question is the point: run the hardened per-seed gate at the CURRENT scale first (cheap, reuses the
  committed ConceptNet — re-encode HELD), and again at the >=400K scale-test, to measure whether the leak grows
  with entity count. That directly informs the 970K go/no-go.

## Dispatch recipe (when critical path clears)
- exp_dev (Opus, HIGH): amend exp_ingest_knowledge_integration_verify_v1's gate-D to (1) per-seed max gate,
  (2) name-similar distractor pool + its scramble firing-control; re-run the multi-seed FULL. re-encode HELD
  (reuse committed ConceptNet). NEVER git add -A. Route GPU/overnight dispatch via orchestrator; verify referent.
- Sequence: AFTER the encoder-retrieval GSBC lever reports (that is the higher-priority ingest-QUALITY unblock);
  this gate-D hardening is the ingest-INTEGRITY gate that must clear before the 970K scale, not before N8 cert.
- On landing -> XHIGH skunkworks VET (headline: does the hardened per-seed gate hold, and what is the honest
  non-vacuousness number at scale).

## Where it sits
Closes the one open caveat on the Stage-0 QUALIFIED HARD_PASS. Composes with the Stage-0 CG core (already
proven), the staged ingest plan (Stage0 -> N8 -> dogfood -> scale-test), and the base-rate/paired-trials +
firing-control disciplines. Monitor-not-control, narrow glass-box.
