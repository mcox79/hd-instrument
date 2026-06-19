# Prereg: asdiv_cascade_wk_cpu_v1
**Date:** 2026-06-11  **Lane:** CPU  **Routing:** Research ASDiv solver realize-ceiling (extend BEST existing solver, cascade v2 0.309, with question-guided WK gating).
Extend cascade v2 (1-op+2-op+verifier) with QUESTION-GUIDED WK constants: "X_per_Y" fires only when target~X and Y in text (conditional gating per Research). A/B base vs +WK. Filter relaxed to >=1 digit (WK may supply the 2nd number).
HARD-PASS >=0.40. MIDDLE >=0.33 OR lift>=0.02. HARD-FAIL <0.33 and lift<0.02. Smoke (100): base 0.34, WK lift ~0 (too few WK items in sample); full (1150) decisive on the small realizable lift.
