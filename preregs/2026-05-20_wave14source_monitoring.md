# Pre-registration: wave14source_monitoring (Yonelinas dual-process)

Date: 2026-05-20
Status: Pre-registered, gated. From holy-grail research finding.

## Why

Holy-grail research finding: source-monitoring (Yonelinas 2002, Johnson 1993)
is a known cognitive science capability that NO deployed LLM has. The
substrate can implement it as an EXTRA binding axis:
  m = sum_{j,k} s_j ⊙ c_jk ⊙ v_jk
where s_j is a source key, c is cue, v is content.

Prediction: source-recall stays above chance at loads where item-recall has
collapsed. Yonelinas dual-process dissociation emerges from the algebra
(no separate model needed).

Materials analog: staggered transition in multi-component spin glass -
source order parameter relaxes at different rate than item order parameter.

## Hypothesis

At some alpha (item load), item_recall < 50% AND source_recall > 70%.
Strict dissociation: dual-process emerges algebraically.

## Operational

N=4096, K_sources=8, L_items in {20, 50, 100, 150, 250, 400, 600}. Total
alpha = K*L/N spans [0.04 to 1.17] (crosses alpha_c at L~80).
5 seeds. 50 probes per condition. Triple-binding s ⊙ c ⊙ v.

## Cited

- Yonelinas A.P. (2002) "Nature of recollection and familiarity" J Memory & Language
- Johnson M.K., Hashtroudi S., Lindsay D.S. (1993) "Source monitoring" Psych Bull
- Holy-grail research agent (this session)
- Plate 1995 HRR (multi-factor binding capacity)

## Expected runtime

Smoke: ~5 sec
Full: ~5-10 min (7 L values * 5 seeds * 50 probes * matrix ops)

## Verdict labels

- `SRCMON_DISSOCIATION_VALIDATED`: item<50%, source>70% at some alpha (HOLY GRAIL)
- `SRCMON_BOTH_PRESERVED`: need higher load to test
- `SRCMON_NO_DISSOCIATION`: both collapse together (algebra fails)
- `SRCMON_PARTIAL`: in between
- `SRCMON_INCONCLUSIVE`: empty
