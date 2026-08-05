"""mine_goal_outcome_litbank_v1 -- mine REAL goal->outcome passages from data/litbank/original/*.txt
(100 real public-domain novels), prioritizing STRUCTURAL DIVERSITY, to give the goal-owner pipeline
(exp_situation_model_goal_outcome_dimension_v1 / exp_component5_gold_role_isolated_v1 /
exp_component5_wired_endtoend_v1) a REAL-CORPUS item bank -- the one thing the authored deepen-N set
(commit 469cc2ac0, N=23, one template repeated) could not give.

WHAT (per task brief): scan each novel sentence-by-sentence for
  (1) a GOAL sentence: an animate owner + a psych/desiderative verb (want/hope/long/wish/desire/
      crave/dread/fear/love/hate/...), owner identified via a glass-box proper-noun roster +
      nearest-preceding-mention pronoun resolution (heuristic, NOT the real coref resolver --
      documented as a KNOWN LIMITATION affecting owner-label precision, verified by human sample);
  (2) a later OUTCOME sentence within a forward window: broader achieve/block lexicon than the
      authored cell's V2_OUTCOME_* (real prose does not share the authored template's vocabulary);
  (3) a FOIL: any OTHER roster name mentioned between goal and outcome, more recently than the
      owner -> the anti-recency candidate this pipeline exists to test.
Diversity axes tracked explicitly (structure_type): goal polarity (positive_desire vs
aversive_desire), outcome polarity (achieved vs blocked), goal-outcome distance bucket (adjacent /
near / dispersed), foil presence, embedded-clause syntax. NOT the authored template's single shape
('X wanted... Y acted... she [bad outcome]').

HONESTY CONTRACT (per task brief): this is a HEURISTIC miner (proper-noun roster + nearest-mention
pronoun resolution), not the pipeline's own coref/attribution mechanism -- so gold labels can be
WRONG. Every mined item is machine-extracted, not hand-verified, until the human-verification pass
(reads a sample of >=15 and reports accuracy). If yield or verification accuracy is low, THAT IS THE
FINDING (report honestly), not something to paper over by relaxing thresholds after the fact.

Writes incrementally (append + flush per item, per task brief 'do NOT background') to
experiments/data/goal_outcome_mined_litbank_v1.jsonl.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "hdlab")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.thematic_role_labeler import lemma_verb, PSYCH_VERBS  # noqa: E402

LITBANK_DIR = os.path.join(REPO_ROOT, "data", "litbank", "original")
OUT_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_outcome_mined_litbank_v1.jsonl")

# ============================================================================ target goal-verb set
# surface inflections of the task-specified desiderative verbs (want/hope/long/wish/desire/crave/
# dread/fear/love/hate), tagged by polarity (positive_desire = seeking; aversive_desire = avoiding).
GOAL_VERBS_POS = {
    "want": "want", "wants": "want", "wanted": "want", "wanting": "want",
    "hope": "hope", "hopes": "hope", "hoped": "hope", "hoping": "hope",
    "long": "long", "longs": "long", "longed": "long", "longing": "long",
    "wish": "wish", "wishes": "wish", "wished": "wish", "wishing": "wish",
    "desire": "desire", "desires": "desire", "desired": "desire", "desiring": "desire",
    "crave": "crave", "craves": "crave", "craved": "crave", "craving": "crave",
    "love": "love", "loves": "love", "loved": "love", "loving": "love",
    "yearn": "yearn", "yearns": "yearn", "yearned": "yearn", "yearning": "yearn",
}
GOAL_VERBS_AVERSIVE = {
    "dread": "dread", "dreads": "dread", "dreaded": "dread", "dreading": "dread",
    "fear": "fear", "fears": "fear", "feared": "fear", "fearing": "fear",
    "hate": "hate", "hates": "hate", "hated": "hate", "hating": "hate",
}
GOAL_VERBS = {**GOAL_VERBS_POS, **GOAL_VERBS_AVERSIVE}

# ============================================================================ outcome lexicon
# broader than V2_OUTCOME_UNMET/MET (exp_self_extension_grounded_realprose_v1) -- that lexicon was
# tuned to the authored template's exact vocabulary (skating/fair/market vignettes) and does not
# fire on real 19th-c. novel prose. This is a general achieve/block cue set for MINING (candidate
# identification), independent of the pipeline's own typing lexicon.
ACHIEVE_CUES = {
    "succeeded", "succeed", "achieved", "achieve", "granted", "grant", "agreed", "agree",
    "obtained", "obtain", "won", "win", "arrived", "arrive", "escaped", "escape", "saved", "save",
    "secured", "secure", "triumphed", "triumph", "satisfied", "satisfy", "fulfilled", "fulfil",
    "fulfill", "allowed", "allow", "consented", "consent", "attained", "attain", "gained", "gain",
    "rewarded", "reward", "delighted", "delight", "relieved", "relieve", "content", "glad", "joy",
    "joyful", "successful", "victory", "reached", "reach", "accomplished", "accomplish",
}
BLOCK_CUES = {
    "failed", "fail", "refused", "refuse", "denied", "deny", "forbidden", "forbid", "forbade",
    "prevented", "prevent", "lost", "lose", "disappointed", "disappoint", "thwarted", "thwart",
    "defeated", "defeat", "ruined", "ruin", "ashamed", "shame", "despair", "grief", "grieved",
    "grieve", "sorrow", "sorry", "wept", "weep", "cried", "cry", "vain", "impossible", "rejected",
    "reject", "declined", "decline", "withheld", "withhold", "never", "unable", "helpless",
    "hopeless", "broken", "break", "crushed", "crush", "dying", "died", "die", "dead", "sank",
    "sink", "fell", "fall", "missed", "miss", "silent", "silence",
}

STOP_CAPS = {
    "The", "A", "An", "It", "He", "She", "They", "I", "We", "You", "But", "And", "If", "When",
    "Chapter", "Mr", "Mrs", "Miss", "Dr", "Sir", "Lady", "Lord", "Aunt", "Uncle", "Oh", "Yes",
    "No", "So", "As", "Now", "Then", "There", "This", "That", "These", "Those", "What", "Why",
    "How", "Who", "Where", "Which", "Not", "Nor", "For", "Nay", "Well", "Indeed", "Perhaps",
    "Presently", "Suddenly", "Meanwhile", "Afterwards", "At", "In", "On", "Of", "To", "With",
    "God", "Heaven", "Christmas", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
}
PRON = {"he", "she", "him", "her", "his", "hers", "himself", "herself", "they", "them", "their"}


def _normalize_ascii(s: str) -> str:
    repl = {
        "‘": "'", "’": "'", "“": '"', "”": '"',
        "—": "--", "–": "-", "…": "...",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s.encode("ascii", errors="ignore").decode("ascii")


def load_sentences(path: str):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    raw = _normalize_ascii(raw)
    # paragraph-join: collapse single newlines to spaces, keep sentence content intact
    text = re.sub(r"\r\n", "\n", raw)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # crude but consistent sentence splitter (mirrors the project's existing _sentences convention,
    # extended to keep terminal punctuation for outcome/polarity readability in the mined text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", text)
    return [p.strip() for p in parts if p.strip()]


def build_roster(sentences):
    """glass-box proper-noun roster: capitalized tokens NOT at sentence-start, frequency>=3,
    excluding common closed-class capitalized words (STOP_CAPS)."""
    counts = Counter()
    for sent in sentences:
        toks = sent.split(" ")
        for i, tok in enumerate(toks):
            w = tok.strip(".,\"'();:!?")
            if not w or not w[0].isupper() or not w.isalpha():
                continue
            if i == 0:
                continue  # sentence-initial capitalization is uninformative
            if w in STOP_CAPS:
                continue
            counts[w] += 1
    return {w for w, c in counts.items() if c >= 3}


def _tokens(sent: str):
    return [t.strip(".,\"'();:!?") for t in sent.split(" ") if t.strip(".,\"'();:!?")]


def sentence_owner(sent: str, roster: set, last_named: list):
    """first roster NAME in sentence wins; else first pronoun resolves to nearest prior roster name
    (heuristic, NOT the real coref/attribution mechanism -- documented limitation)."""
    toks = _tokens(sent)
    for t in toks:
        if t in roster:
            return t, "named"
    low = [t.lower() for t in toks]
    for t in low:
        if t in PRON:
            for name in reversed(last_named):
                return name, "pronoun_resolved"
            return None, None
    return None, None


def mentions_in(sent: str, roster: set):
    return [t.strip(".,\"'();:!?") for t in sent.split(" ") if t.strip(".,\"'();:!?") in roster]


def mine_novel(path: str, roster_min_names: int = 3):
    novel = os.path.splitext(os.path.basename(path))[0]
    sentences = load_sentences(path)
    if len(sentences) < 50:
        return []
    roster = build_roster(sentences)
    if len(roster) < roster_min_names:
        return []
    last_named = []  # running list of roster names mentioned so far, in order
    items = []
    n = len(sentences)
    for i, sent in enumerate(sentences):
        low_sent = sent.lower()
        goal_tok = None
        for t in _tokens(sent):
            lw = t.lower()
            if lw in GOAL_VERBS:
                goal_tok = lw
                break
        # update running mention list up to and including this sentence BEFORE resolving owner of
        # THIS sentence (owner should not resolve to a name only introduced later in same sentence)
        owner, how = sentence_owner(sent, roster, last_named)
        for m in mentions_in(sent, roster):
            if not last_named or last_named[-1] != m:
                last_named.append(m)
        if goal_tok is None or owner is None:
            continue
        goal_verb_lemma = lemma_verb(goal_tok)
        verb_in_frames = goal_verb_lemma in PSYCH_VERBS
        polarity = "positive_desire" if goal_tok in GOAL_VERBS_POS else "aversive_desire"
        # embedded-clause check: goal verb followed within 3 tokens by 'to' or 'that'
        toks_low = [t.lower() for t in _tokens(sent)]
        try:
            gi = toks_low.index(goal_tok)
        except ValueError:
            gi = -1
        embedded = gi >= 0 and any(
            toks_low[j] in ("to", "that") for j in range(gi + 1, min(gi + 4, len(toks_low))))

        # forward outcome scan (window of 7 sentences after the goal sentence)
        outcome_idx = None
        outcome_polarity = None
        between_mentions = []  # (sentence_idx, name) for foil detection
        for j in range(i + 1, min(i + 8, n)):
            osent = sentences[j]
            ol = osent.lower()
            otoks = {t.lower() for t in _tokens(osent)}
            hit_block = bool(otoks & BLOCK_CUES)
            hit_achieve = bool(otoks & ACHIEVE_CUES)
            for m in mentions_in(osent, roster):
                between_mentions.append((j, m))
            if hit_block or hit_achieve:
                outcome_idx = j
                outcome_polarity = "blocked" if hit_block and not hit_achieve else (
                    "achieved" if hit_achieve and not hit_block else "mixed")
                break
        if outcome_idx is None:
            continue

        dist = outcome_idx - i
        dist_bucket = "adjacent" if dist <= 1 else ("near" if dist <= 3 else "dispersed")

        foil = None
        for j, m in between_mentions:
            if m != owner:
                foil = m  # keep updating -> last one wins (most recent before outcome)
        structure_type = f"{polarity}_{outcome_polarity}_{dist_bucket}_{'foil' if foil else 'nofoil'}"

        span_text = " ".join(sentences[i:outcome_idx + 1])
        item = dict(
            id=f"{novel}__s{i}",
            text=span_text[:900],
            goal_owner=owner,
            owner_resolution=how,
            goal_verb=goal_tok,
            goal_verb_lemma=goal_verb_lemma,
            verb_in_VERB_FRAMES=bool(verb_in_frames),
            outcome_span=sentences[outcome_idx][:400],
            outcome_polarity=outcome_polarity,
            foil=foil,
            source_novel=novel,
            structure_type=structure_type,
            goal_polarity=polarity,
            dist_sentences=dist,
            dist_bucket=dist_bucket,
            has_embedded_clause=bool(embedded),
            goal_sentence=sent[:300],
        )
        items.append(item)
    return items


def select_diverse(all_items, target_n=40, per_novel_cap=2):
    """greedy round-robin over structure_type buckets, capped per-novel, preferring items WITH a
    foil (the structural axis the authored template could not supply)."""
    by_bucket = {}
    for it in all_items:
        by_bucket.setdefault(it["structure_type"], []).append(it)
    for k in by_bucket:
        by_bucket[k].sort(key=lambda x: (x["foil"] is None, len(x["text"])))
    bucket_keys = sorted(by_bucket.keys(), key=lambda k: ("nofoil" in k, k))
    novel_counts = Counter()
    selected = []
    idxs = {k: 0 for k in bucket_keys}
    progress = True
    while len(selected) < target_n and progress:
        progress = False
        for k in bucket_keys:
            if len(selected) >= target_n:
                break
            lst = by_bucket[k]
            while idxs[k] < len(lst):
                cand = lst[idxs[k]]
                idxs[k] += 1
                if novel_counts[cand["source_novel"]] >= per_novel_cap:
                    continue
                selected.append(cand)
                novel_counts[cand["source_novel"]] += 1
                progress = True
                break
    return selected


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    paths = sorted(
        os.path.join(LITBANK_DIR, f) for f in os.listdir(LITBANK_DIR) if f.endswith(".txt"))
    print(f"[mine] scanning {len(paths)} novels under {LITBANK_DIR}", flush=True)

    all_items = []
    for pi, path in enumerate(paths):
        try:
            found = mine_novel(path)
        except Exception as e:
            print(f"[mine] SKIP {os.path.basename(path)}: {type(e).__name__}: {e}", flush=True)
            continue
        all_items.extend(found)
        if pi % 10 == 0 or found:
            print(f"[mine] [{pi+1}/{len(paths)}] {os.path.basename(path)}: "
                  f"+{len(found)} candidates (total={len(all_items)})", flush=True)

    n_with_foil = sum(1 for it in all_items if it["foil"] is not None)
    print(f"[mine] RAW candidates={len(all_items)} with_foil={n_with_foil}", flush=True)

    selected = select_diverse(all_items, target_n=40, per_novel_cap=2)
    struct_counts = Counter(it["structure_type"] for it in selected)
    print(f"[mine] SELECTED n={len(selected)} structure_type breakdown={dict(struct_counts)}",
          flush=True)

    # write incrementally (append + flush per item, per task brief -- not one atomic end-write)
    if os.path.exists(OUT_PATH):
        os.remove(OUT_PATH)
    with open(OUT_PATH, "a", encoding="utf-8", newline="") as f:
        for it in selected:
            f.write(json.dumps(it, ensure_ascii=True) + "\n")
            f.flush()
            os.fsync(f.fileno())

    print(f"[mine] wrote {len(selected)} items to {OUT_PATH}", flush=True)
    return selected


if __name__ == "__main__":
    main()
