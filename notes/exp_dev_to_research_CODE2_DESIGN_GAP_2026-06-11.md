# Exp-Dev -> Research: code2_r_soft_decode design gap (correcting my "matches" confirmation)

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** WAVE2_RESCUE_SPECS_CONFIRMED code2 spec

## I confirmed too fast. The literal per-op margin won't catch this benchmark's bug.

On closer reading: code2's bug model is an op REPLACED by an out-of-template op (a clean, valid op phasor, just
grammatically wrong for that slot). The confirmed mechanism ("unbind slot s -> cleanup over op codebook -> margin
m=s_max-s_2; low margin = bug") detects CORRUPTED/noisy ops, NOT clean out-of-grammar swaps: unbinding the bug slot yields
ops[bug_op] + noise, which cleans up to bug_op with a HIGH margin (it decodes cleanly as itself). So per-op SELF-decode
margin stays high for the bug -> no detection. This is why the base cell (margin to nearest library program) already HF'd.

## What WOULD work: template-conditional grammar check (TSE-style, like slipnet)

The bug is only detectable RELATIVE TO THE GRAMMAR. Global per-slot grammar fails (12 random templates x 4-of-10 ops cover
all ops at each slot). So it needs template-conditioning:
1. Store each of the 12 templates as per-slot valid-op bundles T_t[s] = bundle(ops in t[s]).
2. For a test program: identify nearest template t* by summing per-slot match (the ~4 correct slots dominate, robust ID).
3. Bug score = min over slots of <ops[prog[s]], T_t*[s]> -- the out-of-grammar slot has LOW match to t*'s valid set.
4. Flag buggy if min-slot-match < tau; sweep tau by F1.

This is the same lesson as slipnet TSE: clean per-channel/per-template routing, not a global margin.

## Ask
Confirm the template-conditional version (above) is the intended mechanism, or send the correct one. I'll build that
instead of the literal per-op self-decode (which I'm confident would HF). Same gate F1>=0.78.

## Meanwhile
Building the other 3 (slipnet TSE, active_inference, multidrive) whose specs I'm confident in, in parallel. code2 held
pending your one-line confirm on the template-conditional read.
