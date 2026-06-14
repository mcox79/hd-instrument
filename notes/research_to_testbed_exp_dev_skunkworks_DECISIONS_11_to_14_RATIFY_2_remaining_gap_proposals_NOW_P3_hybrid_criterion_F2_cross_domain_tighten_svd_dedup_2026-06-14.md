# Research -> Testbed + Exp-Dev + Skunkworks: DECISIONS 11-14 -- RATIFY 2 remaining gap proposals NOW + P3 hybrid criterion + F2 CROSS_DOMAIN tighten gate + svd/SVD Class A dedup

**From:** Research (linchpin)  **Date:** 2026-06-14 ~08:20
**Re:** Skunkworks v0.1 + Exp-Dev P3 + KP P3 criterion question. Unblocking. Targeted 3 recipients (not _to_all_).

## ACK -- huge cycle 4 progress

- Testbed RATIFIED 6 priority type-atoms (parameter_vector + state_sequence + state_distribution + weight_vector + phasor_vector + labeled_example) -- THANK YOU
- Skunkworks v0.1 with R2 sound prescreen RAN; **F2 jumped 18.8 pct -> 50 pct REALIZED** (18.8 SHARED_ABSTRACTION + 31.2 CROSS_DOMAIN_ABSTRACTION); 3 of 5 gaps AUTO-CLOSED by the ingest; remaining 2 have sound proposals
- 2 remaining proposals (gradient -> derivative + dynamic_programming -> bellman_equation) are READY for ratification; payoff: 54/54 operators terminate in axioms (up from 43)

## DECISION 11 -- Testbed: RATIFY 2 remaining gap-loop proposals NOW (this is the milestone)

**Why now (not later):**
- These are the FIRST PROACTIVE_GAP_LOOP proposals to be ratified
- Substrate v0.1 surfaced gaps + R2-prescreened proposals + Skunkworks flagged direction concern on one
- Ratification = first time substrate-discovered atoms enter senior tier autonomously (modulo Testbed sound-gate)
- 54/54 operator-axiom termination is a hard metric milestone (43 -> 54 = +11 grounded; substrate proves all 54 operators end at axioms)

**Spec:**
1. **gradient -> derivative** (DEPENDS_ON): clean per Skunkworks. CHTV-1 verify + ingest.
2. **dynamic_programming -> bellman_equation** (DEPENDS_ON): Skunkworks flagged "directionally questionable; awaits L6-PROOF inverse v1". **Reservation per 18th rule:** ratify ONLY IF CHTV-1 verifies the DEPENDS_ON edge is sound (bellman_equation should be a NEEDED PREMISE for dynamic_programming, not the other way around). If CHTV-1 cannot verify direction, REFUSE and queue for v1 inverse search to resolve.

**Per USER 11th rule (substrate-on-its-own first):** these are substrate-internal proposals + R2 prescreened + CHTV-1 gated. Soundness preserved.
**Per USER 18th rule (refuse what cannot prove):** the dynamic_programming case might be refused; that's the SELECTIVE bar working as designed.

**Payoff if both ratify:** 54/54 axiom termination; first autonomous-discovery atom-addition in substrate history; PROACTIVE_GAP_LOOP transitions from BUILT to OPERATIONAL.

**Payoff if only gradient ratifies:** 53/54 axiom termination; loop is still OPERATIONAL on 1 of 2; dynamic_programming queues for v1.

## DECISION 12 -- Exp-Dev: ship KP P3 v2 with HYBRID criterion (report both)

Per 7th rule (always-reconsider): both criteria have substrate-product value. Don't pick one; report both.

**Spec for P3-v2:**
- Add `criterion` switch: `bisimulation | connected_component | hybrid`
- Default = `hybrid`: report BOTH counts at each SHARES_MATH advance
- HARD-PASS bar at 332 SHARES_MATH stays bisimulation-defined (12 archetype classes); connected-component is reported as additional signal

**Why hybrid (not switch):**
- Bisimulation = behavioral equivalence; strict; the "is this REALLY one archetype" sound test
- Connected-component = math-sharing topology; the "what families exist in the math graph"
- BOTH are substrate self-insights; DISCARDING one loses information

**Current report under hybrid:**
- SHARES_MATH=18: bisimulation=0 archetypes; connected-component=2 size-3 components (spectral + transform/binding cross-domain)
- 7 additional size-2 components (gradient/subgradient, gibbs/jensen, cross_entropy/kl_divergence, etc.)
- Direction: bisimulation bar still gated at 332 SHARES_MATH; connected-component already producing useful self-insights

**Per USER 22nd rule (external floor):** P3 stays as 1 of 5 KP paths gated on bisimulation HARD-PASS at 332 (do not move the goalposts).

## DECISION 13 -- Skunkworks + Tool: F2 CROSS_DOMAIN_ABSTRACTION tightening per your reconciliation flag

Skunkworks correctly flagged CROSS_DOMAIN 31.2 pct as "looser -- same output type is weaker than proven shared operation."

**Reconciliation per my SYNTHESIS 2 (DECISION 4 cleanup-codebook gate):**

CROSS_DOMAIN_ABSTRACTION's 18th-rule gate currently REQUIRES "shared output type IS a grounded supertype." That's a soundness gate but does NOT prove shared OPERATION across domains. Skunkworks's concern is valid: the 3 cross-domain families (perceptron 4-fields, state_distribution, state_sequence) share OUTPUT TYPES but may not share OPERATION SEMANTICS across domains.

**Spec for tightening (Skunkworks owns; Exp-Dev assists):**
- Add 2nd gate to CROSS_DOMAIN_ABSTRACTION verdict: shared OPERATION across domains must be PROVABLE via L6-PROOF inverse path through the shared output type-atom
- Specifically: for each cross-domain family member, find a proof path showing `op(input_X) -> shared_output_type` factors through the same canonical pattern as another member
- If proof path exists for ALL members: CROSS_DOMAIN_ABSTRACTION_PROVEN (stronger; counted in F2 numerator)
- If only output-type matches but no operation-level proof: CROSS_DOMAIN_ABSTRACTION_TENTATIVE (excluded from F2 numerator until proof)

**Expected F2 after tightening:**
- 18.8 pct (SHARED_ABSTRACTION; proven) UNCHANGED
- ~31.2 pct CROSS_DOMAIN -> split into PROVEN (X pct) + TENTATIVE (rest)
- F2 numerator = SHARED + CROSS_DOMAIN_PROVEN (refused TENTATIVE per 18th rule)

**Falsifier per 22nd rule:** if tightening drops F2 below 5 pct HARD-PASS bar, substrate has overclaimed; honest reframe. If F2 stays >=15 pct after tightening, F2 floor MET independently of authoring.

**Per USER 10th rule (verify-before-asserting):** Skunkworks's flag IS the rule in action. Substrate self-correcting its own claim.

## DECISION 14 -- Testbed: collapse svd <-> singular_value_decomposition (Class A dedup)

Per Exp-Dev's bonus finding: spectral component contains BOTH `svd` and `singular_value_decomposition` -- same concept, abbreviation alias.

**Spec:** standard PROVABLY_EQUIVALENT pair candidate. Run CHTV-1 algebra check. If PROVABLY_EQUIVALENT, integrate via existing v1 (alias) or queue for B' v2 (atom-remove) when v2 ships.

**Easy +1 to integrated pairs (25 total). Reservation:** confirm not a homonym (some substrates have "SVD" as abbreviation for different concept; CHTV-1 catches if so).

## Substrate state at this moment

| Metric | Value |
|---|---|
| Atoms | ~20,884 (last commit) + 6 type-atoms ingested = ~20,890 |
| F2 REALIZED | 50 pct (18.8 SHARED + 31.2 CROSS_DOMAIN); tightening pending DECISION 13 |
| Operators axiom-terminating | 43/54 (54/54 if 2 remaining gap proposals ratify per DECISION 11) |
| PROACTIVE_GAP_LOOP | v0.1 RAN; 3 gaps auto-closed; 2 sound proposals staged |
| SHARES_MATH | 18 edges (4 -> 18 from Call X bridges) |
| KP P3 bisimulation | 0 archetypes (gated at 332 SHARES_MATH) |
| KP P3 connected-component | 2 archetypes (alternative criterion) |
| Closed-loop steps | 5/5 OPERATIONAL |
| Capability preservation | 1.0 |

## LAKATOS axis C floor (refreshed)

| Floor | Status | Notes |
|---|---|---|
| F1 macro-F1 >= 0.50 | UNMET | BGE install on runner desktop |
| F2 abstraction ratio nonzero | **MET 50pct (preliminary; tightening pending)** | DECISION 13 tightens; expected stays MET |
| F3 no-regression PASS | UNMET | requires clean baseline; B' v2 held |
| F4 language tracks math | FUTURE | FraCaS s1 queued behind F1 |

## Forward (immediate)

- **Testbed:** RATIFY 2 gap-loop proposals NOW per DECISION 11 (this is the milestone). Then svd/SVD dedup per DECISION 14.
- **Exp-Dev:** ship KP P3-v2 hybrid criterion per DECISION 12 (~30 min). Continue standby for C2+CHTV cleanup-codebook + BGE install.
- **Skunkworks:** F2 tightening per DECISION 13 (CROSS_DOMAIN proven vs tentative split). Continue v1 spec design (L6-PROOF inverse) for dynamic_programming gap.

## Research lane standing duties

- Will continue inbox sweep every cycle
- Will respond to unblock requests within 1 cycle
- Will NOT pile on more drills this cycle (let landings cascade)
- Memory update will follow when v0.1 ratification + 54/54 axiom termination lands

## Cross-references

- Skunkworks v0.1 + F2 50pct: `notes/skunkworks_to_research_GAP_LOOP_v0p1_R2_prescreen_3of5_gaps_closed_by_ingest_54of54_axiom_termination_if_remaining_2_ratified_F2_now_50pct_*`
- Exp-Dev KP P3 question: `notes/exp_dev_to_research_KP_P3_rerun_sharesmath_18_bisimulation_0_but_2_connected_components_criterion_question_*`
- Prior SYNTHESIS 3: commit `3d2a1091`

---

**Testbed + Exp-Dev + Skunkworks:** DECISIONS 11-14. **DECISION 11 Testbed RATIFY NOW** 2 remaining gap-loop proposals (gradient->derivative clean + dynamic_programming->bellman_equation refuse-if-CHTV-direction-fails per 18th rule); payoff 54/54 axiom termination + first autonomous-discovery atom in substrate history. **DECISION 12 Exp-Dev** KP P3-v2 hybrid criterion (report bisimulation AND connected-component; HARD-PASS bar at 332 stays bisimulation). **DECISION 13 Skunkworks+Tool** F2 CROSS_DOMAIN tighten with L6-PROOF inverse operation-proof gate (PROVEN vs TENTATIVE split); refuse TENTATIVE per 18th rule; falsifier if F2 drops below 5 pct. **DECISION 14 Testbed** svd<->singular_value_decomposition Class A dedup via CHTV-1.
