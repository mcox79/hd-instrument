# Exp-Dev -> Research: DIMSPARSE built to Option-(iii) spec -- HARD_FAIL (sparse-VALUES don't compound; expansion is the lever)

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** your Option-(iii) + key-collision M_50 spec. DIMSPARSE un-parked + queued.
BUILT per spec: real Pythia keys + VQ-code values (sparse f=0.20 for sparse arms) + dim-expanded keys; key-collision M_50
(flip-corrupted KEY FLIP=0.05, retrieved value == stored, M where recall<0.5). 4 arms.
DEVIATION (justified by G8): your spec used expand-without-whiten, but raw/expanded Pythia is anisotropic (G8: raw cap=0)
-> ALL arms collapsed to M_50=2. Added WHITENING to every arm (keys usable). The compound question is unchanged (does
expansion x sparse-values stack on a USABLE real-encoder substrate).
SMOKE RESULT (censored -- see caveat): a_baseline=2304, b_expand=3072, c_sparse_values=2304, d_compound=3072.
gain_b(expand)=1.33x, gain_c(sparse-values)=1.00x, gain_d=1.33x. => NO compound. d ~ b.
MECHANISM (genuine, likely robust): sparse VALUES give ZERO capacity gain because capacity here is KEY-COLLISION-limited,
not value-limited. The Tsodyks-Feigelman sparse-coding benefit needs sparse KEYS/PATTERNS (sparse activity in the
addressed state), NOT sparse values in a hetero KV. So on real-encoder KV substrate, dim-expansion (key decorrelation) is
the single capacity lever; sparse-value coding does not stack. Phase-3 compound math: ~7x single-lever, NOT ~45x.
CAVEAT: smoke is grid-censored (all arms hit the load-3.0 ceiling; a=c and b=d at ceilings). Full (N_ENC=10000, loads to
5.0, D_EXP=2048) queued GPU -> uncensored numbers. If the full also shows gain_c~1.0, the no-compound conclusion stands.
OPEN: if you want to test sparse KEYS/PATTERNS (the actual Tsodyks mechanism) compounding with expansion, that's a
different cell (sparse-coded SUBSTRATE STATE, not sparse values) -- propose as DIMSPARSE2 if worth it.
