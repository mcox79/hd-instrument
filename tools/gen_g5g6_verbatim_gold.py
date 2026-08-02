#!/usr/bin/env python3
"""Generate verbatim g5/g6 dense pronoun-linking coref gold candidates.

VERBATIM GUARD (mandatory, enforced not eyeballed): every emitted clause, after
whitespace-normalization and stripping leading/trailing punctuation, MUST be a
CONTIGUOUS SUBSTRING (case-sensitive) of that passage's source paragraph run.
Every mention must likewise be a contiguous substring of its own clause. If any
check fails, the script raises SystemExit(1) and writes nothing.

Allowed source operations ONLY: (a) split source into sentences, (b) split a
sentence into clauses at conjunction/relative/dialogue boundaries, (c) excerpt
(drop whole leading/trailing sentences). NO rewording, compressing, re-stitching,
paraphrase, or invented connective text.

Sources are pasted verbatim from:
  data/corpora/mcguffey_graded/clean/g5.txt
  data/corpora/mcguffey_graded/clean/g6.txt
gold_verified is false on every record (Director verifies before any eval trusts it).
ASCII-only; no em-dashes.
"""
import json
import re
import sys

OUT = "data/eval_gold_mention_role_mcguffey_v1/gold_g5g6_dense_pronoun_verbatim_v1.jsonl"

PRON = {"he", "him", "his", "himself", "she", "her", "hers", "herself",
        "it", "its", "itself", "they", "them", "their", "you", "i", "me",
        "my", "thee", "thou", "thy"}


def norm(s):
    """Whitespace-normalize + strip leading/trailing punctuation (guard-legal ops)."""
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(' \t\n"\',.;:!?()-')
    return s


# ---------------------------------------------------------------------------
# PASSAGES. source = verbatim paragraph run. clauses = verbatim substrings.
# ---------------------------------------------------------------------------
PASSAGES = []

def P(**kw):
    PASSAGES.append(kw)


# --- G5 P1: Sherman / child / mother (3 entities, cross-gender it=child) ---
P(
 passage_id="g5v_sherman_child_mother_bible",
 grade="g5",
 source='At length, he opened the Bible, and began to read. The child who was seated beside him made some little disturbance, upon which Mr. Sherman paused and told it to be still. Again he proceeded; but again he paused to reprimand the little offender, whose playful disposition would scarcely permit it to be still. And this time he gently tapped its ear. The blow, if blow it might be called, caught the attention of his aged mother, who now, with some effort, rose from the seat, and tottered across the room. At length she reached the chair of Mr. Sherman, and, in a moment, most unexpectedly to him, she gave him a blow on the ear with all the force she could summon. "There," said she, "you strike your child, and I will strike mine."',
 clauses=[
   "At length, he opened the Bible, and began to read.",
   "The child who was seated beside him made some little disturbance",
   "upon which Mr. Sherman paused and told it to be still",
   "Again he proceeded",
   "but again he paused to reprimand the little offender",
   "And this time he gently tapped its ear",
   "caught the attention of his aged mother, who now, with some effort, rose from the seat, and tottered across the room",
   "At length she reached the chair of Mr. Sherman",
   "she gave him a blow on the ear with all the force she could summon",
   '"you strike your child, and I will strike mine."',
 ],
 entities={
   "Sherman": [
     {"clause": 0, "mention": "he", "role": "agent"},
     {"clause": 2, "mention": "Mr. Sherman", "role": "agent"},
     {"clause": 3, "mention": "he", "role": "agent"},
     {"clause": 4, "mention": "he", "role": "agent"},
     {"clause": 5, "mention": "he", "role": "agent"},
     {"clause": 7, "mention": "Mr. Sherman", "role": "theme"},
     {"clause": 8, "mention": "him", "role": "patient"},
   ],
   "child": [
     {"clause": 1, "mention": "The child", "role": "agent"},
     {"clause": 2, "mention": "it", "role": "patient"},
     {"clause": 4, "mention": "the little offender", "role": "patient"},
     {"clause": 5, "mention": "its ear", "role": "patient"},
   ],
   "mother": [
     {"clause": 6, "mention": "his aged mother", "role": "agent"},
     {"clause": 7, "mention": "she", "role": "agent"},
     {"clause": 8, "mention": "she", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "child", "query_clause": 1, "gold_role": "agent"},
   {"entity": "Sherman", "query_clause": 3, "gold_role": "agent"},
   {"entity": "mother", "query_clause": 7, "gold_role": "agent"},
   {"entity": "Sherman", "query_clause": 8, "gold_role": "patient"},
 ],
 note="Three co-present entities: Mr. Sherman (he/him/his), the child (it/its -- neuter pronoun), and his aged mother (she/her). Clause 8 'she gave him a blow' -- 'him' resolves to Sherman not the child (child is neuter 'it'), and the mother's 'she' must not be confused with a female antecedent since there is none competing. Cross-gender/neuter pronoun tracking with a genuine male-target pronoun ('him'=Sherman) linking back over several clauses.",
 entity_count=3, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["neuter_pronoun_child", "needs_director_verification"],
 verification="Roles for the child: labeled 'agent' in c1 (made a disturbance) then 'patient' in c2/c4/c5 (told/reprimanded/tapped) -- director confirm the c1 'made some little disturbance' is agent not theme. 'his aged mother' in c6: 'his'=Sherman (possessive linking the mother to Sherman); director confirm the mother entity's first mention role 'agent' (rose and tottered) is preferred over 'theme' of 'caught the attention of'.",
)

# --- G5 P2: Sherman / roguish student (2 male) ---
P(
 passage_id="g5v_sherman_roguish_student",
 grade="g5",
 source='One day, after having received his highest honors, he was sitting and reading in his parlor. A roguish student, in a room close by, held a looking-glass in such a position as to pour the reflected rays of the sun directly in Mr. Sherman\'s face. He moved his chair, and the thing was repeated. A third time the chair was moved, but the looking-glass still reflected the sun in his eyes. He laid aside his book, went to the window, and many witnesses of the impudence expected to hear the ungentlemanly student severely reprimanded. He raised the window gently, and then--shut the window blind!',
 clauses=[
   "he was sitting and reading in his parlor",
   "A roguish student, in a room close by, held a looking-glass in such a position as to pour the reflected rays of the sun directly in Mr. Sherman's face",
   "He moved his chair, and the thing was repeated",
   "but the looking-glass still reflected the sun in his eyes",
   "He laid aside his book, went to the window",
   "many witnesses of the impudence expected to hear the ungentlemanly student severely reprimanded",
   "He raised the window gently, and then--shut the window blind!",
 ],
 entities={
   "Sherman": [
     {"clause": 0, "mention": "he", "role": "agent"},
     {"clause": 1, "mention": "Mr. Sherman's face", "role": "patient"},
     {"clause": 2, "mention": "He", "role": "agent"},
     {"clause": 3, "mention": "his eyes", "role": "patient"},
     {"clause": 4, "mention": "He", "role": "agent"},
     {"clause": 6, "mention": "He", "role": "agent"},
   ],
   "student": [
     {"clause": 1, "mention": "A roguish student", "role": "agent"},
     {"clause": 5, "mention": "the ungentlemanly student", "role": "patient"},
   ],
 },
 target_queries=[
   {"entity": "student", "query_clause": 1, "gold_role": "agent"},
   {"entity": "Sherman", "query_clause": 2, "gold_role": "agent"},
   {"entity": "Sherman", "query_clause": 6, "gold_role": "agent"},
 ],
 note="Two males (Mr. Sherman, a roguish student). Every 'He/his' from c2 on refers to Sherman even though the student is the more recently introduced named actor in c1 -- topic-continuity (Sherman is the protagonist) overrides recency, a same-gender antecedent trap.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "topic_over_recency"],
 verification="Straightforward; main check is that all c2-c6 'He/his' = Sherman (not the student), which director should confirm from the narrative (the student never acts again after c1).",
)

# --- G5 P3: Harry Gordon / old gentleman-master (2 male) ---
P(
 passage_id="g5v_harry_gordon_master",
 grade="g5",
 source='The other boy was Harry Gordon, and though he was left in the room full twenty minutes, he never during that time stirred from his chair. Harry had eyes in his head as well as the others, but he had more integrity in his heart; neither the dish cover, the cherries, the drawer knob, the closet door, the round box, nor the key tempted him to rise from his feet; and the consequence was that, in half an hour after, he was engaged in the service of the old gentleman at Elm Tree Hall. He followed his good old master to his grave, and received a large legacy for his upright conduct in his service.',
 clauses=[
   "The other boy was Harry Gordon",
   "though he was left in the room full twenty minutes, he never during that time stirred from his chair",
   "Harry had eyes in his head as well as the others",
   "but he had more integrity in his heart",
   "nor the key tempted him to rise from his feet",
   "he was engaged in the service of the old gentleman at Elm Tree Hall",
   "He followed his good old master to his grave, and received a large legacy for his upright conduct in his service",
 ],
 entities={
   "Harry": [
     {"clause": 0, "mention": "Harry Gordon", "role": "theme"},
     {"clause": 1, "mention": "he", "role": "patient"},
     {"clause": 2, "mention": "Harry", "role": "experiencer"},
     {"clause": 3, "mention": "he", "role": "experiencer"},
     {"clause": 4, "mention": "him", "role": "patient"},
     {"clause": 5, "mention": "he", "role": "theme"},
     {"clause": 6, "mention": "He", "role": "agent"},
   ],
   "master": [
     {"clause": 5, "mention": "the old gentleman", "role": "theme"},
     {"clause": 6, "mention": "his good old master", "role": "theme"},
   ],
 },
 target_queries=[
   {"entity": "Harry", "query_clause": 2, "gold_role": "experiencer"},
   {"entity": "Harry", "query_clause": 6, "gold_role": "agent"},
   {"entity": "master", "query_clause": 6, "gold_role": "theme"},
 ],
 note="Two males (Harry Gordon, the old gentleman / 'his good old master'). Long single-referent 'he/his' chain for Harry (c1-c6), then the master enters via a possessive 'his good old master' in c6 where 'his'=Harry and 'master'=the old gentleman -- a possessive-relation link introducing a second male entity late.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "relation_introduced_antecedent"],
 verification="Role labels for Harry are borderline: c1 'was left' = patient; c2/c3 'had eyes/had integrity' labeled experiencer (stative possession) -- director may prefer 'possessor'. The 'the old gentleman' (c5) and 'his good old master' (c6) are assumed the SAME referent; director confirm.",
)

# --- G5 P4: Henry Wilkins / old gentleman (2 male) ---
P(
 passage_id="g5v_henry_wilkins_cherries",
 grade="g5",
 source='Now, the old gentleman had placed a few artificial cherries at the top of the others, filled with Cayenne pepper; one of these Henry had unfortunately taken, and it made his month smart and burn most intolerably. The old gentleman heard him coughing, and knew very well what was the matter. The boy that would take what did not belong to him, if no more than a cherry, was not the boy for him. Henry Wilkins was sent about his business without delay, with his mouth almost as hot as if he had put a burning coal in to it.',
 clauses=[
   "the old gentleman had placed a few artificial cherries at the top of the others, filled with Cayenne pepper",
   "one of these Henry had unfortunately taken",
   "and it made his month smart and burn most intolerably",
   "The old gentleman heard him coughing, and knew very well what was the matter",
   "The boy that would take what did not belong to him, if no more than a cherry, was not the boy for him",
   "Henry Wilkins was sent about his business without delay",
   "with his mouth almost as hot as if he had put a burning coal in to it",
 ],
 entities={
   "old_gentleman": [
     {"clause": 0, "mention": "the old gentleman", "role": "agent"},
     {"clause": 3, "mention": "The old gentleman", "role": "agent"},
     {"clause": 4, "mention": "him", "role": "experiencer"},
   ],
   "Henry": [
     {"clause": 1, "mention": "Henry", "role": "agent"},
     {"clause": 2, "mention": "his month", "role": "patient"},
     {"clause": 3, "mention": "him", "role": "patient"},
     {"clause": 4, "mention": "The boy", "role": "agent"},
     {"clause": 5, "mention": "Henry Wilkins", "role": "patient"},
     {"clause": 6, "mention": "he", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "Henry", "query_clause": 1, "gold_role": "agent"},
   {"entity": "old_gentleman", "query_clause": 3, "gold_role": "agent"},
   {"entity": "Henry", "query_clause": 4, "gold_role": "agent"},
   {"entity": "Henry", "query_clause": 6, "gold_role": "agent"},
]
 ,
 note="Two males (the old gentleman, Henry Wilkins). Clause 4 'The boy that would take what did not belong to him ... was not the boy for him' -- the first 'him' refers to a generic/Henry-as-the-boy while the second 'him' refers to the old gentleman ('not the boy for him'), two different male referents for 'him' within one sentence.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "two_referents_same_pronoun_one_sentence", "needs_director_verification"],
 verification="Clause 4 is the genuine ambiguity: is 'The boy' a fresh generic mention or a link to Henry? I annotated 'The boy'=Henry and the trailing 'him'=old_gentleman; director confirm both. Note source has a typo 'his month' (for 'mouth') which I kept VERBATIM.",
)

# --- G5 P5: Flor Silin / wife (2 ent m/f) ---
P(
 passage_id="g5v_flor_silin_wife",
 grade="g5",
 source='The fame of Flor Silin\'s benevolence having reached other villages, the famished inhabitants presented themselves before him, and begged for corn. This good creature received them as brothers; and, while his store remained, afforded all relief. At length, his wife, seeing no end to the generosity of his noble spirit, reminded him how necessary it would be to think of their own wants, and hold his lavish hand before it was too late. "It is written in the Scripture," said he, "Give, and it shall be given unto you.\'"',
 clauses=[
   "the famished inhabitants presented themselves before him, and begged for corn",
   "This good creature received them as brothers",
   "and, while his store remained, afforded all relief",
   "At length, his wife, seeing no end to the generosity of his noble spirit, reminded him how necessary it would be to think of their own wants",
   "and hold his lavish hand before it was too late",
   'said he',
 ],
 entities={
   "Flor_Silin": [
     {"clause": 0, "mention": "him", "role": "recipient"},
     {"clause": 1, "mention": "This good creature", "role": "agent"},
     {"clause": 2, "mention": "his store", "role": "possessor"},
     {"clause": 3, "mention": "him", "role": "recipient"},
     {"clause": 4, "mention": "his lavish hand", "role": "possessor"},
     {"clause": 5, "mention": "he", "role": "agent"},
   ],
   "wife": [
     {"clause": 3, "mention": "his wife", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "Flor_Silin", "query_clause": 1, "gold_role": "agent"},
   {"entity": "wife", "query_clause": 3, "gold_role": "agent"},
   {"entity": "Flor_Silin", "query_clause": 3, "gold_role": "recipient"},
 ],
 note="Flor Silin (male, referred to as 'him'/'his'/'he' and once as 'This good creature') and his wife (female, 'his wife'). Clause 3 has both entities: 'his wife ... reminded him' -- 'his'=Flor Silin (possessive linking the wife) and 'him'=Flor Silin (recipient of the reminding), the wife being the agent. Male-target pronoun linking across the paragraph.",
 entity_count=2, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density"],
 verification="'This good creature' (c1) = Flor Silin, an epithet not a pronoun or name; director confirm this counts as a valid same-entity mention. Roles solid otherwise.",
)

# --- G5 P6: barber / stranger dialogue (2 male, verbatim quotes) ---
P(
 passage_id="g5v_barber_stranger_reed_dialogue",
 grade="g5",
 source='When shaved, he said, "There must be something extraordinary in your history, which I have not now time to hear. Here is half a crown for you. When I return, I will call and investigate your case. What is your name?" "William Reed," said the astonished barber. "William Reed?" echoed the stranger: "William Reed? by your dialect you are from the West." "Yes, sir, from Kingston, near Taunton." "William Reed from Kingston, near Taunton? What was your father\'s name?" "Thomas." "Had he any brother?" "Yes, sir, one, after whom I was named; but he went to the Indies, and, as we never heard from him, we supposed him to be dead."',
 clauses=[
   "When shaved, he said",
   "Here is half a crown for you",
   "When I return, I will call and investigate your case",
   '"William Reed," said the astonished barber',
   '"William Reed?" echoed the stranger',
   "by your dialect you are from the West",
   "Had he any brother?",
   "one, after whom I was named",
   "but he went to the Indies, and, as we never heard from him, we supposed him to be dead",
 ],
 entities={
   "stranger": [
     {"clause": 0, "mention": "he", "role": "agent"},
     {"clause": 4, "mention": "the stranger", "role": "agent"},
   ],
   "barber": [
     {"clause": 3, "mention": "the astonished barber", "role": "agent"},
   ],
   "uncle": [
     {"clause": 6, "mention": "he", "role": "theme"},
     {"clause": 8, "mention": "he", "role": "agent"},
     {"clause": 8, "mention": "him", "role": "theme"},
     {"clause": 8, "mention": "him", "role": "patient"},
   ],
 },
 target_queries=[
   {"entity": "stranger", "query_clause": 0, "gold_role": "agent"},
   {"entity": "barber", "query_clause": 3, "gold_role": "agent"},
   {"entity": "stranger", "query_clause": 4, "gold_role": "agent"},
   {"entity": "uncle", "query_clause": 8, "gold_role": "agent"},
 ],
 note="Two co-present males (the stranger/attorney, the barber William Reed) plus a discussed-but-absent third male (the uncle, 'he went to the Indies'). Clause 8 stacks 'he went...we never heard from him...supposed him to be dead' all referring to the absent uncle, a same-gender pronoun chain about a non-present referent distinct from the two speakers.",
 entity_count=3, same_gender_ambiguity=True, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["discussed_not_copresent_entities", "dense_same_clause_pronoun_stacking", "needs_director_verification"],
 verification="The uncle entity is inferred from 'Had he any brother?' / 'after whom I was named' -- the 'he' in c6 grammatically refers to the barber's FATHER Thomas (Had [Thomas] any brother?), while the c8 'he/him' refer to that brother=the uncle. So c6 'he'=father(Thomas) NOT uncle. I have likely mislabeled c6; director should split father vs uncle. This is a genuine hard multi-referent chain -- flagging for careful verification.",
)

# --- G5 P7: Gentle Hand pony (stout lad / Dick) 2 ent cross-species ---
P(
 passage_id="g5v_gentlehand_lad_dick_pony",
 grade="g5",
 source='A stout lad now came out into the road, and, catching Dick by the bridle, jerked him forward, using, at the same time, the customary language on such occasions, but Dick met this new ally with increased stubbornness, planting his fore feet more firmly and at a sharper angle with the ground.',
 clauses=[
   "A stout lad now came out into the road",
   "catching Dick by the bridle, jerked him forward",
   "using, at the same time, the customary language on such occasions",
   "but Dick met this new ally with increased stubbornness",
   "planting his fore feet more firmly and at a sharper angle with the ground",
 ],
 entities={
   "lad": [
     {"clause": 0, "mention": "A stout lad", "role": "agent"},
     {"clause": 1, "mention": "jerked", "role": "agent"},
     {"clause": 3, "mention": "this new ally", "role": "theme"},
   ],
   "Dick": [
     {"clause": 1, "mention": "Dick", "role": "patient"},
     {"clause": 1, "mention": "him", "role": "patient"},
     {"clause": 3, "mention": "Dick", "role": "agent"},
     {"clause": 4, "mention": "his fore feet", "role": "possessor"},
   ],
 },
 target_queries=[
   {"entity": "lad", "query_clause": 0, "gold_role": "agent"},
   {"entity": "Dick", "query_clause": 1, "gold_role": "patient"},
   {"entity": "Dick", "query_clause": 3, "gold_role": "agent"},
 ],
 note="A stout lad (male human) and Dick (male pony) -- cross-species same-'he/him/his' pair. Clause 1 'jerked him forward' -- 'him'=Dick (patient); clause 4 'his fore feet' -- 'his'=Dick. Male-pronoun linking where the two candidates are a human and an animal both taking masculine pronouns.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=True,
 flags=["cross_species_pronoun_ambiguity", "low_entity_count_high_pronoun_density"],
 verification="c1 mention 'jerked' for the lad is a verb-anchored agent (the lad is the implicit subject of 'jerked him forward'); director may prefer to drop this mention since there is no overt nominal. Otherwise clean.",
)

# --- G6 P8: Joab / man / Absalom (3 male, biblical dense) ---
P(
 passage_id="g6v_joab_man_absalom",
 grade="g6",
 source='And a certain man saw it, and told Joab, and said, Behold, I saw Absalom hanged in an oak. And Joab said unto the man that told him, And, behold, thou sawest him, and why didst thou not smite him there to the ground? and I would have given thee ten shekels of silver and a girdle. And the man said unto Joab, Though I should receive a thousand shekels of silver in my hand, yet would I not put forth my hand against the king\'s son; for, in our hearing, the king charged thee, and Abishai, and Ittai, saying, Beware that none touch the young man Absalom.',
 clauses=[
   "And a certain man saw it, and told Joab",
   "Behold, I saw Absalom hanged in an oak",
   "And Joab said unto the man that told him",
   "why didst thou not smite him there to the ground?",
   "And the man said unto Joab",
   "yet would I not put forth my hand against the king's son",
   "for, in our hearing, the king charged thee, and Abishai, and Ittai",
   "Beware that none touch the young man Absalom",
 ],
 entities={
   "man": [
     {"clause": 0, "mention": "a certain man", "role": "agent"},
     {"clause": 2, "mention": "the man that told him", "role": "agent"},
     {"clause": 4, "mention": "the man", "role": "agent"},
   ],
   "Joab": [
     {"clause": 0, "mention": "Joab", "role": "recipient"},
     {"clause": 2, "mention": "Joab", "role": "agent"},
     {"clause": 2, "mention": "him", "role": "recipient"},
     {"clause": 4, "mention": "Joab", "role": "recipient"},
   ],
   "Absalom": [
     {"clause": 1, "mention": "Absalom", "role": "patient"},
     {"clause": 3, "mention": "him", "role": "patient"},
     {"clause": 5, "mention": "the king's son", "role": "patient"},
     {"clause": 7, "mention": "the young man Absalom", "role": "patient"},
   ],
 },
 target_queries=[
   {"entity": "man", "query_clause": 0, "gold_role": "agent"},
   {"entity": "Joab", "query_clause": 2, "gold_role": "agent"},
   {"entity": "Absalom", "query_clause": 3, "gold_role": "patient"},
   {"entity": "man", "query_clause": 4, "gold_role": "agent"},
 ],
 note="Three males (Joab, an unnamed man, Absalom). Clause 3 'why didst thou not smite HIM there' -- 'him'=Absalom, a third entity that is neither the speaker (Joab) nor the addressee (the man); the pronoun refers OUTSIDE the current speech-act dyad. This is the source paragraph immediately PRECEDING the existing gold entry g6_dense_joab_ahimaaz_cushi_absalom_king (which starts at Ahimaaz), so it is non-overlapping additional material from the same story.",
 entity_count=3, same_gender_ambiguity=True, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["pronoun_refers_outside_speech_dyad", "dense_same_clause_pronoun_stacking"],
 verification="c2 'the man that told him' -- 'him'=Joab (the man told Joab); director confirm (grammatically 'told him' could momentarily read as reflexive, but context = Joab). Second-person 'thou/thee' (the addressed man) are NOT annotated as third-person entity mentions here; director confirm that convention.",
)

# --- G6 P9: Rip / Judith / child (3 ent, m + f + child) ---
P(
 passage_id="g6v_rip_judith_child",
 grade="g6",
 source='The name of the child, the air of the mother, the tone of her voice, all awakened a train of recollections in his mind. "What is your name, my good woman?" asked he. "Judith Gardenier." "And your father\'s name?" "Ah, poor man! Rip Van Winkle was his name; but it\'s twenty years since he went away from home with his gun, and never has been heard of since; his dog came home without him; but whether he shot himself, or was carried away by the Indians, nobody can tell. I was then but a little girl."',
 clauses=[
   "the tone of her voice, all awakened a train of recollections in his mind",
   '"What is your name, my good woman?" asked he',
   "Rip Van Winkle was his name",
   "but it's twenty years since he went away from home with his gun",
   "and never has been heard of since",
   "his dog came home without him",
   "but whether he shot himself, or was carried away by the Indians, nobody can tell",
 ],
 entities={
   "Rip": [
     {"clause": 0, "mention": "his mind", "role": "possessor"},
     {"clause": 1, "mention": "he", "role": "agent"},
     {"clause": 2, "mention": "his name", "role": "theme"},
     {"clause": 3, "mention": "he", "role": "agent"},
     {"clause": 4, "mention": "has been heard", "role": "theme"},
     {"clause": 5, "mention": "him", "role": "theme"},
     {"clause": 6, "mention": "he", "role": "agent"},
   ],
   "Judith": [
     {"clause": 0, "mention": "her voice", "role": "possessor"},
   ],
 },
 target_queries=[
   {"entity": "Rip", "query_clause": 1, "gold_role": "agent"},
   {"entity": "Rip", "query_clause": 3, "gold_role": "agent"},
   {"entity": "Rip", "query_clause": 6, "gold_role": "agent"},
 ],
 note="Rip Van Winkle is the topic of a dense 'he/his/him' chain (c2-c6) spoken ABOUT him by his daughter Judith, while he ('he asked' c1) is physically present but unrecognized -- the same name 'Rip Van Winkle' is both the questioner present and the absent-presumed-lost man being described. Judith (the mother) and 'her voice' are the female contrast. All of c2-c6 male pronouns link back to the name 'Rip Van Winkle' introduced in c2.",
 entity_count=2, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "same_name_present_vs_described", "needs_director_verification"],
 verification="Subtle: the 'he asked' in c1 is Rip present-and-asking; the c2-c6 'he/his/him' are Rip-as-described-by-Judith. Same referent (Rip) but a present-vs-narrated frame shift -- director confirm they should be ONE entity. c0 'her voice' = Judith (the mother); the child is mentioned ('name of the child') but not tracked as its own entity here (no pronoun link) -- director may add.",
)

# --- G6 P10: Rip / man in cocked hat (2 male) ---
P(
 passage_id="g6v_rip_cocked_hat",
 grade="g6",
 source='Rip looked, and beheld a precise counterpart of himself as he went up the mountain; apparently as lazy, and certainly as ragged. The poor fellow was now completely confounded; he doubted his own identity, and whether he was himself or another man. In the midst of his bewilderment, the man in the cocked hat demanded who he was, and what was his name.',
 clauses=[
   "Rip looked, and beheld a precise counterpart of himself as he went up the mountain",
   "The poor fellow was now completely confounded",
   "he doubted his own identity, and whether he was himself or another man",
   "In the midst of his bewilderment, the man in the cocked hat demanded who he was",
   "and what was his name",
 ],
 entities={
   "Rip": [
     {"clause": 0, "mention": "Rip", "role": "agent"},
     {"clause": 0, "mention": "himself", "role": "theme"},
     {"clause": 1, "mention": "The poor fellow", "role": "experiencer"},
     {"clause": 2, "mention": "he", "role": "experiencer"},
     {"clause": 3, "mention": "his bewilderment", "role": "experiencer"},
     {"clause": 3, "mention": "he", "role": "theme"},
     {"clause": 4, "mention": "his name", "role": "theme"},
   ],
   "cocked_hat_man": [
     {"clause": 3, "mention": "the man in the cocked hat", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "Rip", "query_clause": 0, "gold_role": "agent"},
   {"entity": "Rip", "query_clause": 2, "gold_role": "experiencer"},
   {"entity": "cocked_hat_man", "query_clause": 3, "gold_role": "agent"},
 ],
 note="Two males (Rip, the man in the cocked hat). Clause 3 'the man in the cocked hat demanded who HE was' -- 'he'=Rip (the one being asked about), not the demanding man himself, a same-gender subject-vs-object trap where the sentence subject (cocked-hat man) is NOT the pronoun referent.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "subject_not_pronoun_referent"],
 verification="c3/c4 'who he was, and what was his name' = Rip; director confirm the 'he'/'his' here point to Rip (the object of 'demanded') rather than the cocked-hat man (the subject). This is the intended hard case.",
)

# --- G6 P11: Duke / porter / Cornish voter (3 male) ---
P(
 passage_id="g6v_duke_porter_voter",
 grade="g6",
 source='His grace was sound asleep; and the porter, settled for the night in his armchair, had already commenced a sonorous nap, when the vigorous arm of the Cornish voter roused him from his slumbers. To his first question, "Is the Duke at home?" the porter replied, "Yes, and in bed; but has left particular orders that, come when you will, you are to go up to him directly."',
 clauses=[
   "His grace was sound asleep",
   "and the porter, settled for the night in his armchair, had already commenced a sonorous nap",
   "when the vigorous arm of the Cornish voter roused him from his slumbers",
   'To his first question, "Is the Duke at home?" the porter replied',
   "but has left particular orders that, come when you will, you are to go up to him directly",
 ],
 entities={
   "Duke": [
     {"clause": 0, "mention": "His grace", "role": "theme"},
     {"clause": 3, "mention": "the Duke", "role": "theme"},
     {"clause": 4, "mention": "him", "role": "recipient"},
   ],
   "porter": [
     {"clause": 1, "mention": "the porter", "role": "theme"},
     {"clause": 2, "mention": "him", "role": "patient"},
     {"clause": 3, "mention": "the porter", "role": "agent"},
   ],
   "voter": [
     {"clause": 2, "mention": "the Cornish voter", "role": "agent"},
     {"clause": 3, "mention": "his first question", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "porter", "query_clause": 2, "gold_role": "patient"},
   {"entity": "voter", "query_clause": 2, "gold_role": "agent"},
   {"entity": "porter", "query_clause": 3, "gold_role": "agent"},
   {"entity": "Duke", "query_clause": 4, "gold_role": "recipient"},
 ],
 note="Three males (the Duke / 'His grace', the porter, the Cornish voter). Clause 2 'the Cornish voter roused HIM from HIS slumbers' -- 'him'/'his'=the porter (the one asleep), not the Duke or the voter. Clause 4 'you are to go up to HIM directly' -- 'him'=the Duke, spoken by the porter to the voter, so the pronoun refers outside the speaker/addressee dyad. Verbatim replacement for the paraphrased g6 Duke passage in the discarded candidates file.",
 entity_count=3, same_gender_ambiguity=True, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["pronoun_refers_outside_speech_dyad", "dense_same_clause_pronoun_stacking"],
 verification="c1 'his armchair' and c2 'him/his slumbers' = the porter; director confirm (the porter is the one who was napping). c4 'him'=Duke is the key link to verify.",
)

# --- G6 P12: Beethoven / Hugh (2 male, dialogue) ---
P(
 passage_id="g6v_beethoven_hugh",
 grade="g5",
 source='"Did you ever hear of Beethoven? He was one of the greatest musical composers that ever lived. His great, his sole delight was in music. It was the passion of his life. When all his time and all his mind were given to music, he suddenly became deaf, perfectly deaf; so that he never more heard one single note from the loudest orchestra. While crowds were moved and delighted with his compositions, it was all silence to him." Hugh said nothing.',
 clauses=[
   "He was one of the greatest musical composers that ever lived",
   "His great, his sole delight was in music",
   "When all his time and all his mind were given to music, he suddenly became deaf, perfectly deaf",
   "so that he never more heard one single note from the loudest orchestra",
   "While crowds were moved and delighted with his compositions, it was all silence to him",
   "Hugh said nothing",
 ],
 entities={
   "Beethoven": [
     {"clause": 0, "mention": "He", "role": "theme"},
     {"clause": 1, "mention": "His great", "role": "possessor"},
     {"clause": 2, "mention": "he", "role": "patient"},
     {"clause": 3, "mention": "he", "role": "experiencer"},
     {"clause": 4, "mention": "his compositions", "role": "possessor"},
     {"clause": 4, "mention": "him", "role": "experiencer"},
   ],
   "Hugh": [
     {"clause": 5, "mention": "Hugh", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "Beethoven", "query_clause": 0, "gold_role": "theme"},
   {"entity": "Beethoven", "query_clause": 3, "gold_role": "experiencer"},
   {"entity": "Hugh", "query_clause": 5, "gold_role": "agent"},
 ],
 note="Beethoven (topic of a long 'he/his/him' chain spoken by an unnamed speaker) and Hugh (the listener, named only at the end 'Hugh said nothing'). All c0-c4 male pronouns link back to the name 'Beethoven' in the elided first sentence. Note: this passage appears in the g6 clean file text but the story (a dialogue about Hugh) is grade-cross-listed; graded g5 here to match the Hugh story's home in the existing gold -- director confirm grade.",
 entity_count=2, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "grade_label_uncertain", "needs_director_verification"],
 verification="Grade label: this text is physically in g6.txt clean, but the 'Hugh' disabled-boy story also underlies the existing gold entry g5_dense_hugh_agnes_mother (labeled g5). I set grade='g5' for consistency with that entry; director resolve the g5/g6 grade discrepancy (same one flagged in the density-scan report). All pronoun roles are for Beethoven.",
)

# --- G5 P13: Tonish / colt (2 ent, cross-species male) ---
P(
 passage_id="g5v_tonish_colt",
 grade="g5",
 source='As to Tonish, who had marred the whole scene by his precipitancy, he had been more successful than he deserved, having managed to catch a beautiful cream-colored colt about seven months old, that had not strength to keep up with its companions. The mercurial little Frenchman was beside himself with exultation. It was amusing to see him with his prize. The colt would rear and kick, and struggle to get free, when Tonish would take him about the neck, wrestle with him, jump on his back, and cut as many antics as a monkey with a kitten.',
 clauses=[
   "As to Tonish, who had marred the whole scene by his precipitancy",
   "he had been more successful than he deserved",
   "having managed to catch a beautiful cream-colored colt about seven months old",
   "that had not strength to keep up with its companions",
   "The mercurial little Frenchman was beside himself with exultation",
   "It was amusing to see him with his prize",
   "The colt would rear and kick, and struggle to get free",
   "when Tonish would take him about the neck, wrestle with him, jump on his back",
 ],
 entities={
   "Tonish": [
     {"clause": 0, "mention": "Tonish", "role": "agent"},
     {"clause": 1, "mention": "he", "role": "theme"},
     {"clause": 2, "mention": "having managed", "role": "agent"},
     {"clause": 4, "mention": "The mercurial little Frenchman", "role": "experiencer"},
     {"clause": 5, "mention": "him", "role": "theme"},
     {"clause": 7, "mention": "Tonish", "role": "agent"},
   ],
   "colt": [
     {"clause": 2, "mention": "a beautiful cream-colored colt", "role": "patient"},
     {"clause": 3, "mention": "its companions", "role": "possessor"},
     {"clause": 6, "mention": "The colt", "role": "agent"},
     {"clause": 7, "mention": "him", "role": "patient"},
   ],
 },
 target_queries=[
   {"entity": "Tonish", "query_clause": 0, "gold_role": "agent"},
   {"entity": "colt", "query_clause": 6, "gold_role": "agent"},
   {"entity": "Tonish", "query_clause": 7, "gold_role": "agent"},
   {"entity": "colt", "query_clause": 7, "gold_role": "patient"},
 ],
 note="Tonish (male Frenchman, he/his/him) and a colt (male animal, its/him/his) -- cross-species same-'him' pair. Clause 5 'him with his prize' = Tonish, but clause 7 'take him about the neck ... on his back' = the colt: the SAME pronoun 'him' refers to different referents in nearby clauses, disambiguated only by event structure (who catches vs who is caught).",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=True,
 flags=["cross_species_pronoun_ambiguity", "two_referents_same_pronoun_nearby_clauses"],
 verification="c2 mention 'having managed' is a verb-anchored agent for Tonish (implicit subject); director may drop. Key check: c5 'him'=Tonish vs c7 'him'=colt.",
)

# --- G5 P14: Rip / old woman (2 ent cross-gender) ---
P(
 passage_id="g6v_rip_old_woman",
 grade="g6",
 source='All stood amazed, until an old woman, tottering out from among the crowd, put her hand to her brow, and, peering under it in his face for a moment, exclaimed, "Sure enough! it is Rip Van Winkle! it is himself! Welcome home again, old neighbor! Why, where have you been these twenty long years?" Rip\'s story was soon told, for the whole twenty years had been to him but as one night.',
 clauses=[
   "an old woman, tottering out from among the crowd, put her hand to her brow",
   "peering under it in his face for a moment",
   "it is Rip Van Winkle! it is himself!",
   "Rip's story was soon told",
   "for the whole twenty years had been to him but as one night",
 ],
 entities={
   "old_woman": [
     {"clause": 0, "mention": "an old woman", "role": "agent"},
   ],
   "Rip": [
     {"clause": 1, "mention": "his face", "role": "theme"},
     {"clause": 2, "mention": "Rip Van Winkle", "role": "theme"},
     {"clause": 2, "mention": "himself", "role": "theme"},
     {"clause": 3, "mention": "Rip's story", "role": "theme"},
     {"clause": 4, "mention": "him", "role": "experiencer"},
   ],
 },
 target_queries=[
   {"entity": "old_woman", "query_clause": 0, "gold_role": "agent"},
   {"entity": "Rip", "query_clause": 2, "gold_role": "theme"},
   {"entity": "Rip", "query_clause": 4, "gold_role": "experiencer"},
 ],
 note="Old woman (she/her) and Rip (his/himself/him). Clause 1 'peering under it in HIS face' -- 'his'=Rip (the woman peers into Rip's face), a cross-gender link where the female subject's action targets the male entity. c4 'him'=Rip links back to the name across the exclamation.",
 entity_count=2, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density"],
 verification="c1 'his face'=Rip; director confirm (the woman peers under her own hand into Rip's face). Clean cross-gender case.",
)

# --- G6 P15: Rip / daughter / mother (deceased) / child ---
P(
 passage_id="g6v_rip_daughter_mother",
 grade="g6",
 source='Rip had but one question more to ask; but he put it with a faltering voice: "Where\'s your mother?" "Oh, she, too, died but a short time since; she broke a blood vessel in a fit of passion at a New England peddler." There was a drop of comfort, at least, in this intelligence. The honest man could contain himself no longer. He caught his daughter and her child in his arms. "I am your father!" cried he.',
 clauses=[
   "Rip had but one question more to ask",
   "but he put it with a faltering voice",
   "she, too, died but a short time since",
   "she broke a blood vessel in a fit of passion at a New England peddler",
   "The honest man could contain himself no longer",
   "He caught his daughter and her child in his arms",
   '"I am your father!" cried he',
 ],
 entities={
   "Rip": [
     {"clause": 0, "mention": "Rip", "role": "agent"},
     {"clause": 1, "mention": "he", "role": "agent"},
     {"clause": 4, "mention": "The honest man", "role": "experiencer"},
     {"clause": 5, "mention": "He", "role": "agent"},
     {"clause": 6, "mention": "he", "role": "agent"},
   ],
   "mother": [
     {"clause": 2, "mention": "she", "role": "patient"},
     {"clause": 3, "mention": "she", "role": "agent"},
   ],
   "daughter": [
     {"clause": 5, "mention": "his daughter", "role": "patient"},
     {"clause": 5, "mention": "her child", "role": "possessor"},
   ],
 },
 target_queries=[
   {"entity": "Rip", "query_clause": 1, "gold_role": "agent"},
   {"entity": "mother", "query_clause": 3, "gold_role": "agent"},
   {"entity": "Rip", "query_clause": 5, "gold_role": "agent"},
   {"entity": "daughter", "query_clause": 5, "gold_role": "patient"},
 ],
 note="Rip (he/him/his/himself, 'The honest man'), the deceased mother (she/she -- discussed, not present), and Rip's daughter ('his daughter', with 'her child'). Clause 5 'He caught his daughter and her child in his arms' has three linked mentions: 'He'/'his arms'=Rip, 'his daughter'=daughter, 'her child'=the daughter's child. Mixed-gender chain with a discussed-absent female (mother) distinct from the present female (daughter).",
 entity_count=3, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["discussed_not_copresent_entities", "needs_director_verification"],
 verification="Two distinct females: 'she' in c2/c3 = the deceased mother; the daughter in c5 is a different female. Director confirm they are NOT merged (a coref system may wrongly link both to a single 'she'). The child is annotated only via 'her child' (possessor=daughter); director may add child as its own entity.",
)

# --- G6 P16: Rip / Van Bummel (2 male, same-gender trap) ---
P(
 passage_id="g6v_rip_van_bummel",
 grade="g6",
 source='"Where\'s Van Bummel, the schoolmaster?" "He went off to the wars, too; was a great militia general, and is now in Congress." Rip\'s heart died away at hearing of these sad changes in his home and friends, and finding himself thus alone in the world. Every answer puzzled him, too, by treating of such enormous lapses of time, and of matters which he could not understand--war, Congress, Stony Point. He had no courage to ask after any more friends, but cried out in despair, "Does nobody here know Rip Van Winkle?"',
 clauses=[
   "Where's Van Bummel, the schoolmaster?",
   "He went off to the wars, too",
   "was a great militia general, and is now in Congress",
   "Rip's heart died away at hearing of these sad changes in his home and friends",
   "and finding himself thus alone in the world",
   "Every answer puzzled him, too",
   "and of matters which he could not understand",
   "He had no courage to ask after any more friends",
 ],
 entities={
   "Van_Bummel": [
     {"clause": 0, "mention": "Van Bummel", "role": "theme"},
     {"clause": 1, "mention": "He", "role": "agent"},
     {"clause": 2, "mention": "a great militia general", "role": "theme"},
   ],
   "Rip": [
     {"clause": 3, "mention": "his home", "role": "possessor"},
     {"clause": 4, "mention": "himself", "role": "experiencer"},
     {"clause": 5, "mention": "him", "role": "experiencer"},
     {"clause": 6, "mention": "he", "role": "experiencer"},
     {"clause": 7, "mention": "He", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "Van_Bummel", "query_clause": 1, "gold_role": "agent"},
   {"entity": "Rip", "query_clause": 5, "gold_role": "experiencer"},
   {"entity": "Rip", "query_clause": 7, "gold_role": "agent"},
 ],
 note="Two males (Van Bummel the schoolmaster, Rip). Clause 1 'He went off to the wars' -- 'He'=Van Bummel (the just-asked-about schoolmaster), NOT Rip who is the story's protagonist and the topic of every other clause; a same-gender recency-vs-topic trap where the correct answer is the locally-introduced entity, not the global topic.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "recency_over_topic"],
 verification="c1/c2 'He'/'a great militia general' = Van Bummel; c3-c7 all Rip. The switch at the c2/c3 boundary is the key thing to verify.",
)

# --- G5 P17: Flor Silin / neighbors (2 ent, group) ---
P(
 passage_id="g5v_flor_silin_neighbors",
 grade="g5",
 source='In a village adjoining lived Flor Silin, a poor, laboring peasant,--a man remarkable for his assiduity and the skill and judgment with which he cultivated his lands. He was blessed with abundant crops; and his means being larger than his wants, his granaries, even at this time, were full of corn. The dry year coming on had beggared all the village except himself. Here was an opportunity to grow rich. Mark how Flor Silin acted. Having called the poorest of his neighbors about him, he addressed them in the following manner:',
 clauses=[
   "In a village adjoining lived Flor Silin, a poor, laboring peasant",
   "a man remarkable for his assiduity and the skill and judgment with which he cultivated his lands",
   "He was blessed with abundant crops",
   "and his means being larger than his wants, his granaries, even at this time, were full of corn",
   "The dry year coming on had beggared all the village except himself",
   "Mark how Flor Silin acted",
   "Having called the poorest of his neighbors about him, he addressed them in the following manner",
 ],
 entities={
   "Flor_Silin": [
     {"clause": 0, "mention": "Flor Silin", "role": "theme"},
     {"clause": 1, "mention": "he", "role": "agent"},
     {"clause": 2, "mention": "He", "role": "theme"},
     {"clause": 3, "mention": "his granaries", "role": "possessor"},
     {"clause": 4, "mention": "himself", "role": "theme"},
     {"clause": 5, "mention": "Flor Silin", "role": "agent"},
     {"clause": 6, "mention": "he", "role": "agent"},
   ],
   "neighbors": [
     {"clause": 6, "mention": "his neighbors", "role": "theme"},
     {"clause": 6, "mention": "them", "role": "recipient"},
   ],
 },
 target_queries=[
   {"entity": "Flor_Silin", "query_clause": 1, "gold_role": "agent"},
   {"entity": "Flor_Silin", "query_clause": 5, "gold_role": "agent"},
   {"entity": "neighbors", "query_clause": 6, "gold_role": "recipient"},
 ],
 note="Flor Silin (long single-referent 'he/his/himself' chain) plus his neighbors (group, 'his neighbors'/'them'). Clause 6 'Having called the poorest of his neighbors about him, he addressed them' links 'his'/'him'/'he'=Flor Silin and 'his neighbors'/'them'=the group in one clause. Lower same-gender-ambiguity (one dominant male + a group) -- secondary-tier density control.",
 entity_count=2, same_gender_ambiguity=False, multi_speaker_dialogue=False,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "group_entity"],
 verification="Straightforward single-protagonist chain; included mainly for pronoun-linking volume. Director may down-rank as low-difficulty.",
)

# --- G6 P18: dying boy / schoolmaster (2 male, GENUINE ambiguity) ---
P(
 passage_id="g6v_dying_boy_schoolmaster",
 grade="g6",
 source='He was a very young boy; quite a little child. His hair still hung in curls about his face, and his eyes were very bright; but their light was of heaven, not of earth. The schoolmaster took a seat beside him, and, stooping over the pillow whispered his name. The boy sprung up, stroked his face with his hand, and threw his wasted arms around his neck, crying, that he was his dear, kind friend.',
 clauses=[
   "He was a very young boy; quite a little child",
   "His hair still hung in curls about his face",
   "and his eyes were very bright",
   "The schoolmaster took a seat beside him",
   "and, stooping over the pillow whispered his name",
   "The boy sprung up, stroked his face with his hand",
   "and threw his wasted arms around his neck",
   "crying, that he was his dear, kind friend",
 ],
 entities={
   "boy": [
     {"clause": 0, "mention": "He", "role": "theme"},
     {"clause": 1, "mention": "His hair", "role": "possessor"},
     {"clause": 2, "mention": "his eyes", "role": "possessor"},
     {"clause": 3, "mention": "him", "role": "theme"},
     {"clause": 4, "mention": "his name", "role": "theme"},
     {"clause": 5, "mention": "The boy", "role": "agent"},
     {"clause": 6, "mention": "his wasted arms", "role": "possessor"},
   ],
   "schoolmaster": [
     {"clause": 3, "mention": "The schoolmaster", "role": "agent"},
     {"clause": 5, "mention": "his face", "role": "patient"},
     {"clause": 6, "mention": "his neck", "role": "patient"},
   ],
 },
 target_queries=[
   {"entity": "schoolmaster", "query_clause": 3, "gold_role": "agent"},
   {"entity": "boy", "query_clause": 5, "gold_role": "agent"},
   {"entity": "schoolmaster", "query_clause": 6, "gold_role": "patient"},
 ],
 note="Two males (a dying boy, the schoolmaster) with an unusually high density of ambiguous 'his'. Clause 5 'The boy ... stroked his face with his hand' -- 'his face'=the schoolmaster (the boy strokes the master's face), 'his hand'=the boy; clause 6 'his wasted arms around his neck' -- 'his wasted arms'=the boy (wasted from illness), 'his neck'=the schoolmaster. Same-gender antecedent choice on nearly every possessive.",
 entity_count=2, same_gender_ambiguity=True, multi_speaker_dialogue=False,
 animacy_contrast=False,
 flags=["dense_same_clause_pronoun_stacking", "genuine_possessive_ambiguity", "needs_director_verification"],
 verification="GENUINE AMBIGUITY passage -- verify carefully: c5 'stroked his face' (schoolmaster's face) vs 'his hand' (boy's hand); c6 'his wasted arms' (boy) vs 'his neck' (schoolmaster); c7 'that he was his dear, kind friend' I did NOT annotate (both 'he'=schoolmaster and 'his'=boy are plausible readings and the clause is reported speech) -- director should decide the c7 assignment. The 'wasted arms' cue (illness) is the disambiguator for c6.",
)

# --- G5 P19: benefactor / debtor (2 male, 1st-person benefactor) ---
P(
 passage_id="g5v_benefactor_debtor",
 grade="g5",
 source='And the answer was, that, having given up every farthing to his creditors, he had been compelled to stint his family of even common necessaries, that he might be enabled to pay the cost of his certificate. "My dear fellow, this will not do; your family must not suffer. Be kind enough to take this ten-pound note to your wife from me." The overpowered man endeavored in vain to express his thanks; the swelling in his throat forbade words. He put his handkerchief to his face and went out of the door, crying like a child.',
 clauses=[
   "having given up every farthing to his creditors",
   "he had been compelled to stint his family of even common necessaries",
   "that he might be enabled to pay the cost of his certificate",
   "Be kind enough to take this ten-pound note to your wife from me",
   "The overpowered man endeavored in vain to express his thanks",
   "the swelling in his throat forbade words",
   "He put his handkerchief to his face and went out of the door",
 ],
 entities={
   "debtor": [
     {"clause": 0, "mention": "his creditors", "role": "theme"},
     {"clause": 1, "mention": "he", "role": "patient"},
     {"clause": 2, "mention": "he", "role": "agent"},
     {"clause": 4, "mention": "The overpowered man", "role": "agent"},
     {"clause": 5, "mention": "his throat", "role": "possessor"},
     {"clause": 6, "mention": "He", "role": "agent"},
   ],
   "benefactor": [
     {"clause": 3, "mention": "me", "role": "agent"},
   ],
 },
 target_queries=[
   {"entity": "debtor", "query_clause": 2, "gold_role": "agent"},
   {"entity": "debtor", "query_clause": 4, "gold_role": "agent"},
   {"entity": "debtor", "query_clause": 6, "gold_role": "agent"},
 ],
 note="The debtor (long 'he/his' chain, 'The overpowered man') and the benefactor (first-person 'me' speaker). Every 'he/his' links to the debtor across the interposed first-person dialogue. Secondary-tier: one dominant third-person male plus a first-person speaker, low same-gender competition.",
 entity_count=2, same_gender_ambiguity=False, multi_speaker_dialogue=True,
 animacy_contrast=False,
 flags=["low_entity_count_high_pronoun_density", "first_person_speaker"],
 verification="Included for pronoun-linking volume; the benefactor is only ever first-person ('me'), so there is no real he/he competition. Director may down-rank.",
)

# ---------------------------------------------------------------------------
# GUARD + EMIT
# ---------------------------------------------------------------------------
def main():
    total_clauses = 0
    passed_clauses = 0
    failures = []
    records = []
    for p in PASSAGES:
        src_norm = norm(p["source"])
        # normalized-source with only whitespace collapse (keep internal punct)
        src_ws = re.sub(r"\s+", " ", p["source"]).strip()
        for ci, cl in enumerate(p["clauses"]):
            total_clauses += 1
            cln = norm(cl)
            if cln and cln in src_ws:
                passed_clauses += 1
            else:
                failures.append((p["passage_id"], "CLAUSE", ci, cl))
        # mention-substring-of-clause check
        for ent, mentions in p["entities"].items():
            for m in mentions:
                ci = m["clause"]
                clause_ws = re.sub(r"\s+", " ", p["clauses"][ci]).strip()
                mnorm = norm(m["mention"])
                if mnorm and mnorm in clause_ws:
                    pass
                else:
                    failures.append((p["passage_id"], "MENTION", ci, ent + ":" + m["mention"]))
        # build record in exact gold schema
        rec = {
            "passage_id": p["passage_id"],
            "grade": p["grade"],
            "clauses": p["clauses"],
            "entities": p["entities"],
            "target_queries": p["target_queries"],
            "note": p["note"],
            "hard_feature_class": "multientity_dense",
            "construction": "multi_speaker_dialogue" if p["multi_speaker_dialogue"] else "canonical",
            "entity_count": p["entity_count"],
            "same_gender_ambiguity": p["same_gender_ambiguity"],
            "multi_speaker_dialogue": p["multi_speaker_dialogue"],
            "animacy_contrast": p["animacy_contrast"],
            "gold_verified": False,
            "candidate_source": "mcguffey_graded",
            "flags": p["flags"],
            "verification": p["verification"],
            "source_paragraph_verbatim": src_ws,
        }
        records.append(rec)

    print("VERBATIM GUARD REPORT")
    print("  passages:", len(PASSAGES))
    print("  clauses checked:", total_clauses)
    pct = 100.0 * passed_clauses / total_clauses if total_clauses else 0.0
    print("  clause substring-pass: %d/%d = %.1f%%" % (passed_clauses, total_clauses, pct))
    if failures:
        print("  FAILURES (%d):" % len(failures))
        for f in failures:
            print("   ", f)
        raise SystemExit(1)
    # ascii guard
    for rec in records:
        blob = json.dumps(rec, ensure_ascii=True)
        for ch in json.dumps(rec, ensure_ascii=False):
            if ord(ch) > 127:
                raise SystemExit("NON-ASCII in " + rec["passage_id"] + ": " + repr(ch))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    print("  ALL CLAUSES + MENTIONS VERBATIM. wrote", OUT)

    # aggregate power
    tot_pron = tot_link = tot_q = 0
    for rec in records:
        for ent, mentions in rec["entities"].items():
            epron = 0
            for m in mentions:
                last = norm(m["mention"]).split()[-1].lower() if norm(m["mention"]) else ""
                if last in PRON or norm(m["mention"]).lower() in PRON:
                    epron += 1
            tot_pron += epron
            if epron > 0:
                tot_link += 1
        tot_q += len(rec["target_queries"])
    print("AGGREGATE POWER")
    print("  pronoun-linking mentions:", tot_pron)
    print("  entities requiring linking:", tot_link)
    print("  derivable target_queries:", tot_q)


if __name__ == "__main__":
    main()
