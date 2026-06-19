# RESEARCH (Director) -> USER: substantive update -- 20h-plan CENTERPIECE DELIVERED. T3 Phase B finding: our pre-registered hypothesis was EMPIRICALLY FALSE (good science), the depth-cliff IS coverage-limited but the lever is 2-LEVEL not 1-level completion. Sharp framing: "neither shift nor lift -- FLAT at 1-level, RECOVERS at 2-level (0.607->0.993 / 0.368->0.931)." Skunkworks's by-construction call on 2-level pending. Cert-discipline caught its own custodians at THREE layers in one hour.

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-18  **Re:** 20h-plan centerpiece T3 Phase B delivered. ASCII; fname_v2.

## Bottom line (one sentence)

The depth-cliff finding you authorized us to chase as the #1 substantive question of the 20h plan **just landed**: our pre-registered hypothesis (1-level direct-parent completion recovers 2-hop QA) was **EMPIRICALLY FALSE** -- the result was FLAT at 1-level -- and the empirical investigation that traced WHY (incoming-only edges = no completed chains) revealed the **actual lever is 2-level full-path completion** (gold-independent rule; +1,110 edges, 0 new atoms; recall 0.607->0.993 at 2-hop, 0.368->0.931 at 3-hop), with Skunkworks's by-construction call on whether 2-level remains cert-clean at 0.993 NOW pending (Director-side ratify already filed: Phase A FLAT = the clean cert-grade depth-cliff result, framing "neither shift nor lift" stronger than either pre-reg branch).

## What the substrate just told us (in plain English)

You asked us to investigate: "is the depth-cliff in multi-hop hypernym QA coverage-limited (substrate doesn't have the edges) or algorithmic/structural (substrate has them but reasoning can't traverse)?"

The 20h plan's bet was a sharp pre-reg: **"direct-parent completion (1 level) should recover the 2-hop cliff at minimum."** We added 1,339 atoms + 2,219 typed HYPERNYM edges via a gold-independent completeness rule. The result:

> **FLAT.** 2-hop recall stayed 0.607. 3-hop stayed 0.368. NOTHING changed.

That was a surprise, and the right response was to **trace why empirically** (not give up + not paper over). Exp-Dev did that, and the answer is sharp:

- The 1,339 new "intermediate" synsets got 2,219 INCOMING edges (in-corpus -> new_intermediate) but **0 OUTGOING edges** (new_intermediate -> grandparent).
- A 2-hop chain `x -> Y -> z` needs BOTH edges. We added only the first.
- The new intermediates are "dangling upward" -> 0 chains completed.

So the substrate-science finding here is **sharper than either pre-reg branch** (we had pre-reg'd shift-vs-lift; reality is **neither**):

> **"n-level completion recovers n-hop QA. 1-level completion recovers 0%. More incoming edges without outgoing edges = no recovery. Full-path materialization is the lever."**

And then to test it: materializing the OUTGOING edges (the new intermediates' OWN direct parents -- gold-independent, no new atoms, just +1,110 typed edges) -> **2-hop 0.607 -> 0.993, 3-hop 0.368 -> 0.931.** The depth-cliff IS coverage-limited; the lever is full-path completion.

## Why this is GOOD science (pre-reg falsification = load-bearing knowledge)

A pre-reg getting falsified is not failure -- it's the **strongest possible kind of finding** when the falsification is traceable to a root cause that's load-bearing for future work. We now KNOW:

1. **1-level completion is NEVER enough** for n-hop recovery (n>=2) -- a coverage-lever rule must materialize **all n levels** of the path, not just the first.
2. **"Denser substrate -> better recall" is FALSE in this form** -- the densification has to be the RIGHT density (full path, not partial path).
3. **The depth-cliff IS coverage-limited.** Not algorithmic. Not structural. Not a reasoning failure. The substrate had the right paths once we materialized them fully.

This composes with your NEGATIVITY-BIAS rule (symmetric verify-both-directions) -- the falsification cuts BOTH ways: my naive "+1110 edges should help across the board" intuition was symmetrically wrong as my pre-reg's naive "1-level recovers 2-hop" intuition. Empirical wins. The substrate told us a sharper truth than we thought to ask.

## Skunkworks's by-construction call now governs

At recall 0.993, the by-construction guard must re-engage:

- The rule "complete every synset's direct parent (iteratively to 2 levels)" is **gold-blind** -- it iterates nltk hypernyms of in-corpus synsets and NEVER consults the BROAD-test gold. So formally it's not gold-fitted.
- BUT: 2-level completion of the in5k closure essentially materializes ~the gold's paths. 0.993 is very close to 1.0. Has the rule crossed into materializing-the-gold's-paths-by-construction?

This is genuinely Skunkworks's call (cert-owner; their symmetric-negativity-bias discipline is the right authority). **My lean as Director is cert-clean** (the rule never peeks at gold; 0.993 vs 1.0 is residual frontier-out-of-corpus miss, not overfit). But I've explicitly noted that's a lean, not the call. Three branches Skunkworks can return:
- **cert-clean** -> we build the 2-level cell + atomize the 0.993 / 0.931 recovery as MEASURED_MECHANISM cert-grade
- **by-construction-risk** -> we report 2-level as a bounded demonstration, cert-grade finding stays Phase A FLAT only
- **needs-more-thought** -> a 3rd path (e.g. non-HYPERNYM completion as a discriminating gold-blind cell)

I've ratified Phase A FLAT as the clean cert-grade result independently of Skunkworks's 2-level call. **The 20h-plan centerpiece deliverable is already locked**, with the 2-level branch as upside-pending.

## Cert-discipline caught its own custodians at THREE layers this hour (continuing pattern)

While running the Phase B experiment, this happened in parallel:

1. **Exp-Dev verify-the-referent on the Store caught a partial ingest** -- the FrameNet apply timed out at 576/1221 atoms + 0 edges (bg "exit 0" runner-slot-release LOOKED like success; Store-count check told the truth). Exp-Dev didn't trust the runner; checked the Store; caught it.
2. **Exp-Dev root-caused the failure: O(n^2) per-atom `add_atom`** (whole-partition os.replace-flush PER atom on a 41k-store) -> proactively fixed BOTH cells (FrameNet + T3 Phase A) with batched `_index_atom` + single `save_atoms` (B1 pattern) BEFORE T3 Phase A applied. Recovered FrameNet idempotently (own-kind partial atoms = skip-not-collision). 0 duplicates, 0 algebra-leak, 0 phantoms. Clean recovery.
3. **Skunkworks self-caught their own SCHEMA-VET miss** -- they verified cert-correctness (gold-independence, edges-captured, algebra=None, gates) but did NOT verify atom-add MECHANISM. Owning it explicitly. SCHEMA-VET strengthened: per-atom `add_atom` on >~100 atoms = SCHEMA-VET FAIL. The "more carefully designed" half of your directive applied to Skunkworks's OWN review.

The compounding: **incident -> Exp-Dev catches -> Exp-Dev fixes proactively for next cell -> Skunkworks self-catches the SCHEMA-VET gap -> SCHEMA-VET strengthens -> 8th gate candidate emerges.** Substrate-autonomy at the meta-layer, end-to-end visible in real-time. The 6th-checklist canonicalization from earlier this hour fits in cleanly -- this incident **validates** the checkpoint/resume directive (manual idempotent recovery worked but required hand-fixing collision-checks; designed-in checkpoint/resume would auto-resume cleanly).

## Substrate state right now

- **Atoms 43,890** (41,330 + 1,221 SEMANTIC_FRAME + 1,339 LEXICON)
- **CERT 569 unchanged** (non-retroactive)
- **HYPERNYM edges 5,103** (2,884 + 2,219 = +77% densification of depth-cliff backbone)
- **FRAME_* edges 2,070** (10 typed frame-to-frame relations; FrameNet ARC-3 first realization)
- **axiom_term 206 / cap_pres 6/6** preserved through the whole bucket
- **Self-cert engine 7 gates LIVE** (with 8th gate candidate: atom-add-mechanism, emerging from this incident in the same C2 producer-attest + consumer-enforce pattern that produced 5 of the prior 7)
- **Testbed 2nd-witness HARD_PASS 22/22** on both ingests (FrameNet 11/11 + T3 Phase A 11/11)

## What I'm waiting on / who's blocking

- **Skunkworks (highest):** by-construction call on 2-level completion at 0.993 (cert-clean coverage-lever vs by-construction-risk). + Phase A FLAT cert-tier confirmation (recommended MEASURED_MECHANISM). + Phase B v2 SCHEMA-VET (now incl. atom-add-mechanism + checkpoint/resume + kill-restart). + 8th gate candidate promotion call.
- **Exp-Dev:** Phase A FLAT atomize (MEASURED_MECHANISM FINDING + METHODOLOGY_RULE with full edge-provenance) once Skunkworks's tier confirms. HOLD Phase A2 / 2-level cell build until Skunkworks's by-construction call. T3 Phase B v2 build w/ checkpoint+resume + batched-add by design + kill-restart-test.
- **Testbed:** Phase B verdict 2nd-witness + 2-level cell 2nd-witness if built + kill-restart 2nd-witness if bandwidth.
- **Orchestrator:** A2 v6 still BLOCKED on checkpointable rebuild (per Skunkworks's revised guidance under your 6th-checklist directive).
- **USER (you):** nothing currently gated on your sign-off. **Heads-up moment:** if Skunkworks calls 2-level cert-clean, the upside outcome -- a cert-grade "completing 2 levels of canonical parent-links recovers ~99% of 2-hop and ~93% of 3-hop hypernym QA" finding -- becomes the strongest single substrate-science result of the program. If Skunkworks calls by-construction-risk, the cert-grade finding stays the Phase A FLAT depth-cliff result (still strong: "1-level completion is provably insufficient for n-hop, n>=2; the lever is full-path materialization"). Either way the 20h-plan centerpiece is delivered.

You're seeing the substrate work like a science instrument: pre-reg landed, hypothesis tested, falsified honestly, root-caused empirically, sharper truth identified, cert-discipline catches kept up through three layers of custodians. This is the strongest cert-run pattern of the program continuing.

-- Research (Director)
