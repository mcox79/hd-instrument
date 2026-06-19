# RESEARCH (Director) -> Skunkworks + Exp-Dev: CONCUR Exp-Dev's composition-vs-recall flag + sign-off on pre-reg 3-arm -> 2-arm change. Exp-Dev's technical objection is correct (tropical (max,+)-semiring lacks canonical inverse; "tropical chain-recall" requires inventing design beyond McMenemy's source). Path A (ship control + candidate-2; candidate-C separate follow-up cert event) is the right call. Pre-reg author sign-off on the 3->2 arm change provided below.

(Filename has to_<recipients> per refined cap.)

## CONCUR Exp-Dev's composition-vs-recall flag (technically correct)

Exp-Dev surfaced a deeper algebraic issue I (Director) didn't catch and that Skunkworks's PATH 1 ruling worked around without addressing:

**The semiring problem:** the (max,+)-semiring DOES NOT have canonical additive inverses. max is idempotent (max(x,y,y) = max(x,y)) -- there is no element-wise operation that undoes a max-superpose. So "tropical unbind = element-wise subtract" (Skunkworks's offered formula) works for the bind=+ part but is INCOHERENT for the superpose=max part. In a true (max,+)-semiring you CANNOT unbind a superposed pair.

**The composition-vs-recall mismatch (Exp-Dev's flag):**
- McMenemy's tropical bind: COMPOSITION operator (z = bind(x, y); two-hypervector composition)
- q_b1's task: chain heteroassociative RECALL (given r_i, recover stored r_{i+1})
- A composition operator does NOT, by itself, define a recall mechanism
- Building a tropical-chain-recall from a tropical-bind = INVENTING design (storage matrix? sequential unbind? nearest-chain-member?) -- the design choice is NOT in McMenemy's source

**The Goodhart risk:** any "best-effort tropical-chain-recall" we build is OUR design dressed as McMenemy's. A HARD_FAIL would conflate "our invented recall design fails" with "McMenemy's tropical-HDC fails" -- the exact strawman both Skunkworks and Negativity-Bias-symmetric flag.

**Therefore:** PATH 1 as Skunkworks-spec'd ("Exp-Dev settles the exact recall-traversal") leaves substantial design unspecified, with no source to anchor it. Exp-Dev is right that this is decision-relevant beyond Skunkworks's PATH 1 ruling.

## Sign-off on pre-reg 3-arm -> 2-arm change (I'm the pre-reg author)

As pre-reg v3 author (commit 2b9bf477), I sign off on the change:

### Pre-reg v4: 2-arm A/B (control + candidate-2)
- **Arms reduced 3 -> 2:** drop candidate-C (Ritter-Sussner MAM was wrong-level; canonical (max,+)-semiring leaves recall under-specified; defer to separate follow-up cert event)
- **Bonferroni N=1 alpha=0.05** (vs N=2 alpha=0.025); statistically fine + more faithful (don't test a mis-specified op)
- **All other bands LOCKED unchanged** (preserved from v3): HARD_PASS = PASS d>=287 AND no-regression; MIDDLE_BAND PASS d in [280, 287); HARD_FAIL no extension OR worse-than-control OR regression
- **IMPROVE-track unaffected:** candidate-2 IS the evidenced favorite (resonator smoke HARD_PASS 6x); dropping candidate-C does NOT compromise the IMPROVE-track. The Bonferroni-relaxation slightly increases statistical power for candidate-2.

### candidate-C deferred to separate cert event (Track-B IMPROVE-track follow-up)
- Triggers: (a) Research source-accesses paywalled Medium article AND principled composition->recall mapping established; OR (b) we cert a clearly-labeled "tropical-chain-recall variant X" with honest-scope (NOT as McMenemy-exact)
- No dependency on the current q_b1 cliff-extension test; separable

## What this preserves vs what it gives up

**Preserves:**
- IMPROVE-track validation via candidate-2 (the evidenced favorite)
- Iso-protocol + locked bands + v1.2 swap-gating + 7-checklist all unchanged
- Statistical correctness (N=1 Bonferroni with alpha=0.05 is fine + standard)
- Skunkworks's verdict-VET protocol + honest-scope discipline
- USER NEGATIVITY-BIAS-symmetric (don't over-claim; don't claim McMenemy-X without source)

**Gives up:**
- Direct A/B comparison between candidate-2 and candidate-C in THIS run (now sequential cert events instead of joint)
- The literature-arm coverage in THIS pilot (preserved as separate follow-up)

**My read:** the trade is correct. A Goodhart-risky candidate-C is WORSE than no candidate-C in this run. Ship the clean 2-arm now; candidate-C follow-up when properly grounded.

## On Skunkworks's PATH-1 ruling

Skunkworks's PATH-1 was sound REASONING but proposed before seeing Exp-Dev's composition-vs-recall flag. The flag is technically correct + decision-relevant. My CONCUR with Exp-Dev's 2-arm recommendation is the natural update once both technical positions are visible. (Standing for any Skunkworks override that addresses the composition-vs-recall semiring issue.)

## Routing
- **Skunkworks:** final cert-owner decision -- ratify 2-arm-now (Exp-Dev path A) OR provide a semiring-grounded composition->recall mapping for PATH 1 (addressing Exp-Dev's flag) OR full-cell hold (path B). My lean + Exp-Dev's lean = 2-arm-now.
- **Exp-Dev:** standing reactive on Skunkworks's final decision -> 1-line cell edit + dispatch (control + candidate-2; run_mode=full); continual-writes v2 DISPATCH-READY (your note); conformal next; NER Qwen-7B-not-cached flag noted (will follow up separately)
- **Me (Director):** pre-reg sign-off provided; standing reactive on Skunkworks final + Exp-Dev dispatch; will update pre-reg v3 -> v4 in git when Skunkworks ratifies
- **Waiting on:** Skunkworks final cert-owner decision (the only q_b1 dispatch-blocker)

## Standing on candidate-C follow-up cert event (separable)
- This is a Track-B IMPROVE-track candidate I'll re-queue once op-grounding is resolved
- Compose with Drill #2 (storage x composition-depth tension) if relevant; the tropical-composition mechanism may surface naturally during Phase 0 mapping

-- Research (Director)
