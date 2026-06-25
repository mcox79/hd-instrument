# Cell spec proposal — Barrier 1 closer: multi-hop via pointer-chain hybrid

Director-level proposal; NOT dispatched. Pre-authored Stage 2 spec for USER dispatch decision.

## Why this cell

Last night's beta-sweep confirmed Barrier 1 diagnosis: at ALL betas {0.5, 2, 10, 50, 500, 8192} top1 ≤ baseline 0.65 for 2-hop retrieval. The multi-hop ceiling is **upstream of the decoder**. META gap-map drill predicted this; pure-math L5 (category theory) explains it: HRR bind is a quotient map; composing two quotient maps multiplies information loss. At N=8192 V_P=10 K=2, substrate sits BELOW the retraction-existence threshold (N >> V·K). No decoder cleanup can recover what the storage primitive lost.

The META drill named two escape hatches:
1. **Anisotropic encoder** (Resonator-family then works) → Wave D hub-spoke v3 tests this
2. **External pointer chains** (non-compositional; chain-grade in Store at `exp_pointer_chain` depth 100)

This cell uses path 2: pointer-chain hybrid. Substrate stores triples normally via HRR bind for 1-hop retrieval BUT also maintains an external `(subject, predicate) → object_atom_id` index. Multi-hop traversal uses the external index to get next-hop key (no compounding HRR error), then HRR retrieval handles 1-hop unbinding within each step.

## Cell anchor

`substrate_multihop_pointer_chain_hybrid_v1`

## Lane / routing / config

- Lane 1 (substrate-native; pointer chain is a Store-side index, not external LLM call)
- Routing: local_cpu_queue OR remote_cpu_queue (CPU-feasible at production scale; N=8192 K_SET=20 chains=200 is small matmul)
- Config: V_C=200, V_P=10, N=8192, K_SET=20, 3 seeds [7, 17, 23], n_chains=300 per hop-depth

## Arms (one knob varies: chain mechanism)

1. **ARM_BASELINE_HRR_2HOP**: naive HRR chain (control; reproduces 0.65)
2. **ARM_POINTER_CHAIN_2HOP**: external `(s, p) → atom_id` index; 1-hop HRR retrieval per step
3. **ARM_POINTER_CHAIN_5HOP**: 5-hop chain depth
4. **ARM_POINTER_CHAIN_10HOP**: 10-hop chain depth (matches `exp_pointer_chain` Store ref at depth 100)
5. **ARM_POINTER_HRR_HYBRID**: pointer-chain for KEY routing + HRR bind for content cleanup at retrieval node (the proposed substrate-product mode)

## Sanity rail

ARM_BASELINE_HRR_2HOP must reproduce within ±0.02 of last night's beta-sweep baseline 0.65 (provenance check — same regime).

## HARD bands

- HARD_PASS_BREAK_CEILING (PRIMARY): ARM_POINTER_CHAIN_2HOP top1 ≥ 0.95 AND ARM_POINTER_HRR_HYBRID top1 ≥ 0.85 AND CV ≤ 0.05
- HARD_PASS_DEPTH_RETENTION: ARM_POINTER_CHAIN_10HOP top1 ≥ 0.80 (proves pointer-chain doesn't compound errors at depth)
- MIDDLE_BAND: 0.75 < PRIMARY ≤ 0.95
- HARD_FAIL: PRIMARY ≤ 0.75 (pointer-chain doesn't help; substrate multi-hop limit is more fundamental than chaining mechanism)

## Honest scope flags

- **WHAT THIS DOES**: tests whether non-compositional pointer-chain (Store cell `exp_pointer_chain` proved at depth 100 in different regime) transfers to apples-to-apples Lane 1 synthetic random-bipolar regime. Closes Barrier 1 if HARD_PASS via the escape-hatch path.
- **WHAT THIS DOES NOT DO**: prove pure-HRR composition works at multi-hop. The compositional path (Barrier 4 anisotropic encoder) still requires hub-spoke v3 + Resonator together.
- **WHAT COULD KILL IT**: (a) verify-the-referent — confirm Store `exp_pointer_chain` actually verdict=HARD_PASS not MIDDLE_BAND (per Skunkworks lesson, ALWAYS check verdict field, not gap-map framing); (b) the pointer-chain index needs to be substrate-native (NOT a Python dict); we need to encode the index as substrate atoms with HRR cleanup retrieval; (c) the discriminator between "compositional" and "non-compositional" matters — pointer-chain that uses external index for routing but HRR for content IS still substrate-native; pure external index without any HRR retrieval is NOT
- **APPLES-TO-APPLES**: same encoder / N / K_SET / chains as last night's beta-sweep so the +0.30 lift is comparable

## Substrate-product framing

This cell is the **non-compositional escape hatch** for multi-hop. If HARD_PASS, the substrate-product story is:
- **1-hop content retrieval**: HRR exact, chain-grade
- **Multi-hop traversal**: pointer-chain index (Store-side substrate atoms holding next-hop pointers)
- **Per-step cleanup**: HRR at retrieval node

This is brain-aligned: hippocampus does pattern-completion via attractor dynamics (HRR analog) but place cells + grid cells provide INDEX structure (pointer-chain analog). The two systems aren't redundant; they're complementary.

## Cross-thread

- `notes/director_multihop_composition_store_scour_2026-06-24.md` — confirms `exp_pointer_chain` HARD_PASS depth=100 in Store
- `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md` — L5 category theory: pointer-chain is non-compositional escape hatch from the morphism-composition info-loss
- Last night's `substrate_resonator_softchain_beta_sweep_v1` HARD_FAIL — closes the decoder-side rescue path; pointer-chain is the alternative

## Expected outcome

P_deflated(POINTER_CHAIN_2HOP lifts 0.65 → 0.95): **0.55**
- Brain prior +0.10 (hippocampus + place cells)
- Store precedent +0.10 (exp_pointer_chain depth=100 — pending Skunkworks verify-referent on actual verdict field)
- Calibration penalty -0.20

P_deflated(POINTER_CHAIN_HYBRID 2HOP ≥ 0.85 + 10HOP ≥ 0.80): **0.40** (stronger claim; both depth retention AND HRR cleanup at retrieval node)

## Dispatch sequence (proposed)

Can dispatch IMMEDIATELY after Wave D lands (parallel to Barrier 2 cell). They test orthogonal mechanisms and orthogonal barriers.

Sequence:
1. Wait for Wave D landings (hub-spoke v3, heterog v3, SEMANTIC v3) — ~2-4h on GPU
2. Skunkworks verify-referent on `exp_pointer_chain` — confirm actual verdict (not gap-map framing)
3. If exp_pointer_chain confirmed chain-grade in Store, dispatch this cell
4. Parallel dispatch with Barrier 2 role-tagged LM cell

## Status

Not authored as code yet. Awaiting USER green-light + Skunkworks verify-referent confirmation.

## Summary of Stage 2 cell sequence

Two pre-authored Stage 2 specs ready:
- `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md` (THIS — multi-hop escape hatch)
- `notes/director_barrier2_role_tagged_LM_cell_spec_2026-06-25.md` (substrate-as-LM beat bigram via role-tags)

Both depend on Wave D landings to inform encoder choice (hub-spoke v3 if HARD_PASS, else word2vec rail). Both can ship in parallel post-Wave-D.

Stage 2 architectural wins so far:
- Cross-layer compose: independent W beats shared W +0.376 BPC (Barrier 3 resolved)
- Calibration: ECE 0.017 chain-grade (audit-corrected gap closed)
- SEMANTIC concept-learner: A3 generalization top1=1.000 (substrate IS the generalizer)

Barriers remaining post-Wave-D:
- Barrier 1 multi-hop ceiling 0.65 → pointer-chain hybrid cell tests escape hatch
- Barrier 2 substrate-as-LM bigram-equivalence → role-tagged Plate context cell tests role-filler generalization at LM
- Barrier 4 random-bipolar isotropic → hub-spoke v3 (Wave D in flight) tests anisotropic encoder
- Barrier 5 audit-trail smear → S2 atom-graph spoke (if Wave D hub-spoke v3 HARD_PASSes, the S2 spoke IS the provenance channel)
