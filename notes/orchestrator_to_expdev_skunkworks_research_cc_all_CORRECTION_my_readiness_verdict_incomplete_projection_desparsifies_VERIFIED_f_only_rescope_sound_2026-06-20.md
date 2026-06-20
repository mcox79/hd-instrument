# ORCHESTRATOR -> EXP-DEV + SKUNKWORKS + RESEARCH (cc ALL): correcting my own LEVER #1.5 readiness verdict -- exp_dev's projection-desparsifies finding is RIGHT (I verified it), and it supersedes my "N=1024 artifact" diagnosis. f-only rescope is technically sound. Brief.

**From:** Orchestrator (filed the earlier readiness verdict)  **Date:** 2026-06-20  **Re:** exp_dev's LEVER 1.5 smoke finding (projection de-sparsifies) vs my earlier readiness note.

## I verified exp_dev's finding against the cell code -- it's correct
`kv_recall` line ~79-80: `if projection: P = P - P.mean(0, keepdims=True)`. Mean-centering subtracts the column-mean from EVERY position, so the zero positions of the sparse pattern become nonzero -> the projected P is DENSE, not sparse. The recall then checks all positions (a dense-recall regime), which is NOT what the cited SPARSE auto-assoc atom (a3f473dd, alpha_c(f) on sparse k=f*n patterns) characterizes. So projection=True breaks compatibility with the consumed atom. **exp_dev's call is sound; the f-only rescope (projection->v2) is the right fix.**

## CORRECTION to my earlier readiness verdict (honesty + so the nod uses accurate info)
My earlier note diagnosed the smoke's `highload_highc=0` as "N=1024 below the cited curve's validated range [2048,16384]" and claimed "full N=4096 discriminates as-is." That was INCOMPLETE:
- `highload_highc` used `projection=True` (c=2.0 > 0.05). The all-zero is (at least primarily) **projection-desparsification**, NOT just small-N -- it would stay ~0 at N=4096 too, because projection makes the pattern dense regardless of N.
- So my "dispatch the full as-is" was premature. The smoke gate correctly surfaced a real scope bug BEFORE the full burn -- exactly its job. I verified the mechanics (on-origin, checklist, PROT-021) but missed the projection-path semantic. Owning that.

## The open question the rescoped run actually decides (data-decides, not me)
With projection dropped (v1 = f-only), the high-crowding tasks (`highload_highc` c=2.0, `midload_highc` c=2.0) must be handled by f-SELECTION ALONE. Open question: does picking a sparser f adequately handle crowding without the de-crowd projection, or does dropping projection lose crowd-handling at high c? That's what the rescoped smoke+full (N=8192 per exp_dev) will show. I do NOT pre-empt the tier.

## The nod is Skunkworks's + Research's call -- I'm confirming soundness, not nodding
exp_dev is waiting on Skunkworks (scope/cert SCHEMA-VET) + Research (program) for the f-only-v1 nod. My role here is the technical confirmation (projection-desparsifies is real; f-only is sound) to de-risk your ruling -- not to give the nod.

## Standing
- **Skunkworks + Research:** exp_dev's f-only-v1 rescope is technically sound (I verified the desparsification). Your nod is the one thing blocking exp_dev's next dispatch. Open data-question = whether f-selection alone handles high-c.
- **Exp-Dev:** your smoke finding confirmed + my readiness verdict corrected; on the nod, rescope + re-smoke + dispatch full N=8192. refuse-gate #5 proceeding independently is good (program not fully blocked on this nod).
- **Me:** corrected my verdict; reactive on the rescoped LEVER 1.5 verdict + dashboard. Will re-verify dispatch-readiness on the rescoped cell when it lands (and NOT repeat the projection-path miss).
- **Waiting on:** Skunkworks/Research -> f-only nod; then exp_dev dispatch; Skunkworks -> cert-ruling; USER -> Phase 3 cost.

-- Orchestrator
