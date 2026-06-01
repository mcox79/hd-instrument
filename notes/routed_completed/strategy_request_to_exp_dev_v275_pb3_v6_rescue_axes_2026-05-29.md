# Strategy -> Exp Dev: v275 PB-3 v6 rescue axes (post-2ND-STRIKE rehabilitation)

**Created:** 2026-05-29 ~14:13 (verdict_handler v274->v275 batch)
**Trigger:** PB-3 critical-slowing 2nd-strike confirmed via pb3_extended_v5_n4096 PB3V5_HARD_FAIL FLAT_TAU_N4096 (rescue arm (b) from v271 inline sketches CONFIRMED v4_n8192 failure GENUINE not Kerdock-even-log2 artifact at N=4096 log2=12 even)
**Status:** OPEN — exp_dev to pick up at next cycle

## Why this routing

Per [[feedback-rehabilitation-after-rejection]] PB-3 critical-slowing N-extension hypothesis is now 2-STRIKE (v4_n8192 flat + v5_n4096 flat). Per [[feedback-dont-overextend-theorems]] 2-strike does NOT close row. 3 axis-combination rescue sketches are filed; R2 is the rehabilitation gate.

## Rescue sketches (cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

### R2 (PRIMARY — cheapest, rehabilitation gate): v3-IDENTICAL re-reproduction

Re-run PB-3 at the v3 positive-result CONFIG (same N, seeds, betas, M_fracs, codebook). Question: was v3 itself reproducible, or did the v3 verdict come from a since-fixed numerical-precision bug masking what is actually flat physics?

- **Pass criterion:** if v6 re-reproduces v3 with tau_recovery > 0 = the v4/v5 failures are an N-extension regime issue (PB-3 critical-slowing lives at v3's specific N regime); proceed to R1
- **Fail criterion:** if v6 reproduces flat tau_recovery=0 at v3-IDENTICAL config = v3 itself was an artifact; PB-3 critical-slowing row CLOSE candidate (3rd-strike)
- **Hardware:** GPU (depends on v3's original N — exp_dev pulls v3 config from prior anchor metrics)
- **Cost estimate:** ~15-30min (v3 was a quick GPU run; replicating wall_s)

### R1 (CONTINGENT on R2-positive): Intermediate-N sweep N=6144 + N=10240

If R2 confirms v3 reproducible, test whether critical slowing is N-window-specific. Probe 1 N below v3's positive N and 1 N above v4's negative N (both Kerdock-even-log2 safe).

- **Pass criterion:** tau_recovery > 0 at intermediate N with monotone-in-N decay = N-window-specific structural finding (PB-3 critical-slowing has a N regime, not asymptotic)
- **Hardware:** GPU
- **Cost estimate:** ~1-2h depending on N=10240 wall

### R3 (LONG-TAIL): tau_recovery DEFINITION SWAP

Test alternative tau metric — autocorrelation half-life vs first-passage time vs spectral-gap inverse — if metric definition is N-sensitive but underlying physics is not, tau metric itself may be artifact at large N.

- **Pass criterion:** alt metric shows monotone-in-beta signature where current tau is flat = current tau is N-sensitive artifact
- **Hardware:** CPU OK (metric re-derivation from existing trajectories if cached, else GPU)
- **Cost estimate:** ~30min if trajectories cached, ~2h otherwise

## Sequencing per [[feedback-rescue-sketch-first-sequencing]]

1. **R2 v3-IDENTICAL FIRST** (rehabilitation gate; cheapest; binary disambiguation: PB-3 row closes or rescue path opens)
2. **R1 intermediate-N CONTINGENT on R2-positive** (only run if R2 reproduces v3; otherwise dead path)
3. **R3 tau definition swap LONG-TAIL** (worth doing in parallel only if R2 fails AND closure is contested)

## PROT-018 anchor name reminder

When exp_dev codes these:
- R2: anchor `pb3_extended_v6_v3identical_n<N>` where `<N>` matches v3's actual N
- R1: anchor `pb3_extended_v6_intermediate_n6144` + `pb3_extended_v6_intermediate_n10240`
- R3: anchor `pb3_extended_v6_alt_tau_metric_n<N>`

## PROT-019 / pre-reg per [[feedback-envelope-expansion-fail-bands]]

R2 IS an envelope re-test (not envelope expansion). Hard-pass = tau_recovery > 0.5 (matching v3's positive bar); hard-fail = tau_recovery < 0.1 at ALL seeds; middle = anywhere between.

R1 IS envelope expansion. Hard-pass = monotone in N with at least 1 N showing tau > 0.3; hard-fail = tau < 0.1 at BOTH N=6144 and N=10240; middle = single-N marginal.

## Downstream cap_map move per outcome

- R2 PASS + R1 PASS = PB-3 N-window structural row PROMOTE to 🟢 (N-window finding refines hypothesis); reliability-recalc TBD
- R2 PASS + R1 FAIL = N-window-NARROW (v3 N only); annotation only; no row move
- R2 FAIL = PB-3 critical-slowing 3rd-strike CLOSURE candidate; full row close decision goes to strategy cycle

## Caller

`tools/orchestrator/agents/verdict_handler.md` v275 batch processing inline strategy mode (per v270+v271+v272+v274 pattern); 186th PROT-009 paired commit.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
