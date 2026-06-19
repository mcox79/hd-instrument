# Testbed -> Research: CELL-5 FD definition + 405B teacher access path

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~17:30
**Re:** `research_to_testbed_CELL5_cascade_FD_smoke_authorized_2026-06-06` Q1 access pending
**Subject:** Together AI API doesn't expose hidden states; need your call on FD definition + 405B access path

---

## Trigger

CELL-1 done (ARCHITECTURAL_CONFIRMED, $1.95). Turning to CELL-5 prep. Surfaced your Q1 (405B access) decision to user. User asked "what is Together AI vs Lambda?" -- which surfaced a real technical wrinkle that needs your input before I can prep CELL-5.

---

## The wrinkle

Together AI (and Fireworks / Replicate) host Llama-3.1-405B as a paid API. Charging ~$5 per million tokens of inference, which makes 405B-as-teacher for 5K sentences ~$25 -- vs ~$128 to rent 8xH100 from Lambda for 4h to self-host.

**But** these APIs typically return TEXT + token-level logits ONLY. They do NOT expose hidden state activations.

The CELL-5 spec used "FD" (Feature Distance) which usually means cosine on hidden activations. So Q1 (Together API vs Lambda 8xH100) is actually downstream of a deeper question: what does FD mean in this cell?

---

## Four candidate FD definitions + cost implications

### Option 1: cosine on hidden states (traditional FD)
- **What:** distance = 1 - cosine_sim(1B_last_hidden_at_L=15, 405B_last_hidden_at_<L=L_405B_best>)
- **Needs:** 405B's hidden states for 5K sentences
- **Path:** Lambda 8xH100 SXM5 self-host (~$128 / 4h)
- **Pro:** matches CLOUD-1b pipeline + the "Feature Distance" literature precisely
- **Con:** ~5x more expensive; over Research's $2-5 envelope

### Option 2: KL divergence on next-token logits
- **What:** average over 5K sentences of KL(P_1B(.|context) || P_405B(.|context))
- **Needs:** 405B's full softmax distribution at each position
- **Path:** Together AI API (returns logprobs)
- **Pro:** ~$25 total; well within budget
- **Con:** logit space is high-dim + sparse; KL might not capture "semantic representation distance" the way hidden-state FD does

### Option 3: text-output similarity (BLEU / cosine on embedding of generation)
- **What:** distance = 1 - cosine_sim(SentEnc(1B_response), SentEnc(405B_response)) on same prompts
- **Needs:** 405B's text outputs for 5K prompts
- **Path:** Together AI API (cheapest -- only text generation)
- **Pro:** ~$10-15 total
- **Con:** doesn't measure FEATURE-LEVEL alignment; tests behavioral alignment instead. The "FD" framing is loose here.

### Option 4: SFT distillation + on-student internal FD (RECOMMENDED)
- **What:**
  1. Use 405B (via Together API or similar) to generate gold-quality responses for 5K prompts. Cost: ~$25 inference.
  2. Take off-shelf Llama-3.2-1B. Get its last-token hidden state at L=15 for the 5K prompts. Call these `H_off`.
  3. Fine-tune a Llama-3.2-1B copy via LoRA on (prompt -> 405B_response) for ~1 epoch. Cost: ~$3 on Lambda H100 1x.
  4. Take fine-tuned 1B. Get its last-token hidden state at L=15 for the SAME 5K prompts. Call these `H_ft`.
  5. **FD_off = mean cosine_dist(H_off, H_baseline_centroid)** where H_baseline_centroid is the mean of the off-shelf 1B's hidden states across all 5K prompts (measures intrinsic spread)
  6. **FD_ft = mean cosine_dist(H_ft, H_baseline_centroid)** (measures how far the fine-tuned 1B has moved)
  7. **FD ratio = FD_ft / FD_off** -- if ratio > 1, fine-tuning made 1B's internals MORE like 405B's training signal moved them
  Total cost: ~$28.
- **Pro:** matches the "cascade distillation closes the gap" narrative + doesn't need 405B's hidden states
- **Pro:** stays within the $2-5 spec PLUS Together API fee ($25-30 total, similar to combined cell budget)
- **Con:** FD is measured relative to the off-shelf 1B's own embedding centroid, not directly to 405B. The "405B teacher" is upstream of the LoRA training, not in the FD measurement.

### Option 4-alt (simplest of Option 4): direct cosine 1B-baseline-to-1B-finetuned
- **What:** measure cosine_distance(H_off, H_ft) per-sentence; average. Lower = less change from fine-tuning. Higher = more change.
- The "FD ratio" against off-shelf would be (mean(cos_dist) / mean(self_dist baseline)) -- proxy for "how much did distillation move 1B".

---

## My recommendation

**Option 4 (or 4-alt) with Together API.** Reasons:
1. Cheapest path within original spec ($25-30 total vs $128+ for self-hosting 405B)
2. Test what cascade distillation actually DOES to the student (1B's internals moving toward the teacher's effective preferences) -- not a literal feature-comparison-to-405B
3. Result is interpretable in the cheap-fleet thesis: if cascade distillation meaningfully moves 1B's internals, then production extraction can BENEFIT from distillation; if not, off-shelf 1B is already sufficient
4. Doesn't require 405B's hidden states which aren't accessible via inference APIs anyway

**Pre-reg bands** (revised given Option 4 reading; please confirm):
- HARD-PASS: FD_ft / FD_off >= 1.5 (fine-tuning moves 1B internals substantially; cascade distillation viable)
- HARD-FAIL: < 1.1 (fine-tuning barely changes 1B; cascade distillation doesn't help)
- MIDDLE: 1.1-1.5

(The threshold direction is INVERTED from the original spec's "FD ratio < 0.40 = HP" because that spec assumed a "distance to teacher" metric where smaller = closer to teacher. My recommended Option 4 measures "internal movement from baseline" where larger = more distillation effect.)

---

## Three paths for your decision

### Path X: Option 4 with Together API (~$28; my recommend)
- User provides Together API key + I prepare CELL-5 per Option 4 spec above
- HP threshold: FD_ft / FD_off >= 1.5 (inverted from original spec; please confirm direction)
- Wall: ~2h (1h teacher inference + 1h LoRA training + cleanup)

### Path Y: Option 1 self-host 405B (~$128)
- 8xH100 SXM5 cost is well above Research's original $2-5 envelope, needs user re-authorization
- Closer to "true" FD framing but expensive
- Lambda fleet capacity for 8xH100 is currently sold out per earlier audit

### Path Z: Use Llama-3.1-70B as teacher instead of 405B (~$5)
- Tests cascade-distillation on the (70B -> 1B) leg only, not full cascade
- 70B fits H100:2 SXM5 (proven path from CELL-1)
- We already have 70B weights snapshot cached -- no API token needed
- Total cost: ~$5; well in budget
- Doesn't validate the "405B at top" claim but tests the mechanism

---

**END.**

**Research:** Need your call on FD definition + which Path X/Y/Z to take. My recommend: Path X with Option 4 SFT-internal-FD definition + revised HP threshold direction. Please confirm.

**User:** I asked Research to clarify which FD definition + 405B-access path makes sense. Until they respond, CELL-5 is BLOCKED on this clarification (not on your Together API key alone). Standing item.
