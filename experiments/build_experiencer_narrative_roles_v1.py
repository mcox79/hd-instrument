# -*- coding: utf-8 -*-
"""Build experiencer_narrative_roles_v1.jsonl.

GOLD METHOD (non-circular): every sentence below is a REAL sentence mined from the
litbank public-domain novel corpus (data/litbank/original/), EXCEPT the handful marked
source='supplement' (naturalistic, hand-authored to fill a rare construction). For each
sentence the thematic-role labels were assigned by the annotator (glass-box agent) READING
the sentence and writing the TRUE role of each argument -- NOT by any positional heuristic
(subject!=agent here) and NOT by copying a labeler's output. The psych-verb CLASS
(experiencer-subject vs experiencer-object) is supplied knowledge (VerbNet admire-31.2 /
want-32.1 / long-32.2 / marvel-31.3 vs amuse-31.1), but each sentence was individually
checked to confirm it actually instantiates that construction (not an adjectival/idiomatic/
noun use), and the role of each head was verified against the sentence meaning.

Role vocabulary: EXPERIENCER, STIMULUS, AGENT, PATIENT, THEME, RECIPIENT.
  - EXPERIENCER = the one who feels/undergoes the mental state.
  - STIMULUS    = the entity/target that evokes or is directed-at by the mental state
                  (object of subj-exp verbs; SUBJECT of obj-exp verbs -- the hard case).
  - THEME       = a clausal/propositional or plain content complement (used where the
                  complement is a proposition rather than a concrete entity, e.g.
                  "I fear [that his wits were touched]").
Schema matches experiments/data/srl_corpus_thematic_roles_v1.jsonl:
  {"text": ..., "args": [{"head": ..., "role": ...}, ...]}  (+ extra metadata fields).
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "data", "experiencer_narrative_roles_v1.jsonl")

# Each record: (text, verb_lemma, exp_type, construction, source, split, [ (head, role), ... ])
# source: "litbank:<novel_id>"  or  "supplement"
R = []
def add(text, lemma, et, con, src, split, args):
    R.append({
        "text": text,
        "args": [{"head": h, "role": r} for (h, r) in args],
        "verb_lemma": lemma,
        "exp_type": et,          # "subj" | "obj"
        "construction": con,
        "source": src,
        "split_recommendation": split,
    })

# ============================ SUBJECT-EXPERIENCER ============================
# fear
add("I began to fear his wits were touched.", "fear", "subj", "clausal_complement", "litbank:1260_jane_eyre_an_autobiography", "train",
    [("i","EXPERIENCER"),("wits","THEME")])
add("These stalwart virgins had no men to fear and therefore no need of protection.", "fear", "subj", "transitive", "litbank:32_herland", "train",
    [("virgins","EXPERIENCER"),("men","STIMULUS")])
add("I fear the kitten has rolled it away.", "fear", "subj", "clausal_complement", "litbank:145_middlemarch", "train",
    [("i","EXPERIENCER"),("kitten","THEME")])
# want
add("She suffered from pique, and sometimes in a curious fashion she desired Philip.", "desire", "subj", "transitive", "litbank:351_of_human_bondage", "train",
    [("she","EXPERIENCER"),("philip","STIMULUS")])
add("He craved the madness of alcohol in his veins till his delicate hands trembled.", "crave", "subj", "transitive", "litbank:15265_the_quest_of_the_silver_fleece_a_novel", "heldout",
    [("he","EXPERIENCER"),("madness","STIMULUS")])
add("This was what her heart craved.", "crave", "subj", "transitive", "litbank:233_sister_carrie_a_novel", "heldout",
    [("heart","EXPERIENCER"),("what","STIMULUS")])
# love
add("Why did you go away, when I loved you so?", "love", "subj", "transitive", "litbank:110_tess_of_the_durbervilles_a_pure_woman", "train",
    [("i","EXPERIENCER"),("you","STIMULUS")])
add("No one could see Catherine Linton and not love her.", "love", "subj", "transitive", "litbank:768_wuthering_heights", "train",
    [("one","EXPERIENCER"),("her","STIMULUS")])
# hate
add("I hate and detest you!", "hate", "subj", "transitive", "litbank:110_tess_of_the_durbervilles_a_pure_woman", "train",
    [("i","EXPERIENCER"),("you","STIMULUS")])
add("Old boy hated her.", "hate", "subj", "transitive", "litbank:1155_the_secret_adversary", "train",
    [("boy","EXPERIENCER"),("her","STIMULUS")])
# hope
add("She had never hoped that that barrier would be surmounted.", "hope", "subj", "clausal_complement", "litbank:2005_piccadilly_jim", "train",
    [("she","EXPERIENCER"),("barrier","THEME")])
add("I hope Laddy's not mistaken in his opinion of this newcomer.", "hope", "subj", "clausal_complement", "litbank:502_desert_gold", "train",
    [("i","EXPERIENCER"),("laddy","THEME")])
# dread
add("He dreaded the interview with Thomas Jordan.", "dread", "subj", "transitive", "litbank:217_sons_and_lovers", "heldout",
    [("he","EXPERIENCER"),("interview","STIMULUS")])
add("The terrible moment, the moment she had dreaded, had come at last.", "dread", "subj", "transitive", "litbank:174_the_picture_of_dorian_gray", "heldout",
    [("she","EXPERIENCER"),("moment","STIMULUS")])
add("But she dreads responsibility.", "dread", "subj", "transitive", "litbank:432_the_ambassadors", "heldout",
    [("she","EXPERIENCER"),("responsibility","STIMULUS")])
# long (PP-complement)
add("She longed for the quiet of the old garden.", "long", "subj", "pp_complement", "supplement", "train",
    [("she","EXPERIENCER"),("quiet","STIMULUS")])
add("He longed to be gone from that hateful place.", "long", "subj", "infinitival_complement", "supplement", "train",
    [("he","EXPERIENCER")])
# wish
add("I dare say Miss Nash would wish you such an opportunity.", "wish", "subj", "transitive", "supplement", "train",
    [("i","EXPERIENCER"),("opportunity","THEME")])
# admire
add("The unpaid secretary admired this pluck.", "admire", "subj", "transitive", "litbank:974_the_secret_agent_a_simple_tale", "train",
    [("secretary","EXPERIENCER"),("pluck","STIMULUS")])
add("They don't admire you half so much as you admire yourselves.", "admire", "subj", "transitive", "litbank:145_middlemarch", "train",
    [("they","EXPERIENCER"),("you","STIMULUS")])
# adore
add("I am very fond of Amelia; I adore her.", "adore", "subj", "transitive", "litbank:599_vanity_fair", "train",
    [("i","EXPERIENCER"),("her","STIMULUS")])
add("He adored Sorais quite as earnestly as Sir Henry adored Nyleptha.", "adore", "subj", "transitive", "litbank:711_allan_quatermain", "train",
    [("he","EXPERIENCER"),("sorais","STIMULUS")])
# envy
add("I dare say Miss Nash would envy you such an opportunity as this of being married.", "envy", "subj", "ditransitive", "litbank:158_emma", "train",
    [("nash","EXPERIENCER"),("you","STIMULUS"),("opportunity","THEME")])
add("Helen, watching Bo play, was inclined to envy her.", "envy", "subj", "transitive", "litbank:3457_the_man_of_the_forest", "train",
    [("helen","EXPERIENCER"),("her","STIMULUS")])
# pity
add("I pity Pa to that degree.", "pity", "subj", "transitive", "litbank:1023_bleak_house", "train",
    [("i","EXPERIENCER"),("pa","STIMULUS")])
add("The impulse that I had upon me was to pity her so much.", "pity", "subj", "transitive", "litbank:1023_bleak_house", "train",
    [("i","EXPERIENCER"),("her","STIMULUS")])
# loathe
add("Dorian Gray loathed him more than ever.", "loathe", "subj", "transitive", "litbank:174_the_picture_of_dorian_gray", "heldout",
    [("gray","EXPERIENCER"),("him","STIMULUS")])
add("He loathed a fork.", "loathe", "subj", "transitive", "litbank:217_sons_and_lovers", "heldout",
    [("he","EXPERIENCER"),("fork","STIMULUS")])
add("I loathe that man.", "loathe", "subj", "transitive", "litbank:434_the_circular_staircase", "heldout",
    [("i","EXPERIENCER"),("man","STIMULUS")])
# cherish
add("She still cherished a very tender affection for Bingley.", "cherish", "subj", "transitive", "litbank:1342_pride_and_prejudice", "heldout",
    [("she","EXPERIENCER"),("affection","STIMULUS")])
add("Wickham still cherished the hope of making his fortune by marriage.", "cherish", "subj", "transitive", "litbank:1342_pride_and_prejudice", "heldout",
    [("wickham","EXPERIENCER"),("hope","STIMULUS")])
# grieve (intransitive/experiencer-subject 'grieve for')
add("Emma listened with the warmest concern, grieved for her more and more.", "grieve", "subj", "pp_complement", "litbank:158_emma", "train",
    [("emma","EXPERIENCER"),("her","STIMULUS")])
add("He mourned her disappointment.", "mourn", "subj", "transitive", "supplement", "train",
    [("he","EXPERIENCER"),("disappointment","STIMULUS")])
# marvel (PP)
add("Rawdon marvelled over his stories about school, and fights, and fagging.", "marvel", "subj", "pp_complement", "litbank:599_vanity_fair", "train",
    [("rawdon","EXPERIENCER"),("stories","STIMULUS")])
add("Dick marveled that her collapse had not come sooner.", "marvel", "subj", "clausal_complement", "litbank:502_desert_gold", "train",
    [("dick","EXPERIENCER"),("collapse","THEME")])
# wonder
add("I wonder whether he will come at all.", "wonder", "subj", "clausal_complement", "supplement", "train",
    [("i","EXPERIENCER"),("he","THEME")])
# rejoice (PP / clausal)
add("I rejoiced, for I knew that what she could not, none of those we dreaded could.", "rejoice", "subj", "intransitive", "litbank:345_dracula", "train",
    [("i","EXPERIENCER")])
add("She quailed as she thought of the amount and rejoiced because the rent was paid.", "rejoice", "subj", "intransitive", "litbank:233_sister_carrie_a_novel", "train",
    [("she","EXPERIENCER")])
# fret
add("Now you begin to fret about your feeling and about my feeling.", "fret", "subj", "pp_complement", "litbank:1245_night_and_day", "train",
    [("you","EXPERIENCER"),("feeling","STIMULUS")])
add("Miss Linton fretted and pined over something.", "fret", "subj", "pp_complement", "litbank:768_wuthering_heights", "train",
    [("linton","EXPERIENCER"),("something","STIMULUS")])
# esteem
add("Catherine had an awfully perverted taste to esteem him so dearly.", "esteem", "subj", "transitive", "litbank:768_wuthering_heights", "train",
    [("catherine","EXPERIENCER"),("him","STIMULUS")])
# scorn / despise
add("She despised him, and was tied to him.", "despise", "subj", "transitive", "litbank:217_sons_and_lovers", "train",
    [("she","EXPERIENCER"),("him","STIMULUS")])
add("Belding was sure Nell cordially despised the fellow.", "despise", "subj", "transitive", "litbank:502_desert_gold", "train",
    [("nell","EXPERIENCER"),("fellow","STIMULUS")])
# relish
add("I did not relish the notion of fastening myself in with Heathcliff.", "relish", "subj", "transitive", "litbank:768_wuthering_heights", "train",
    [("i","EXPERIENCER"),("notion","STIMULUS")])
add("Mr Power did not relish the use of his Christian name.", "relish", "subj", "transitive", "litbank:2814_dubliners", "train",
    [("power","EXPERIENCER"),("use","STIMULUS")])
# enjoy
add("For a few minutes Anne enjoyed the romance of her situation to the full.", "enjoy", "subj", "transitive", "litbank:45_anne_of_green_gables", "train",
    [("anne","EXPERIENCER"),("romance","STIMULUS")])
add("He enjoys it like a boy.", "enjoy", "subj", "transitive", "litbank:514_little_women", "train",
    [("he","EXPERIENCER"),("it","STIMULUS")])
# value
add("She valued his good opinion above all things.", "value", "subj", "transitive", "supplement", "train",
    [("she","EXPERIENCER"),("opinion","STIMULUS")])
# abhor
add("Mr Duffy abhorred anything which betokened physical or mental disorder.", "abhor", "subj", "transitive", "litbank:2814_dubliners", "train",
    [("duffy","EXPERIENCER"),("anything","STIMULUS")])
add("I abhorred the face of man.", "abhor", "subj", "transitive", "litbank:84_frankenstein_or_the_modern_prometheus", "train",
    [("i","EXPERIENCER"),("face","STIMULUS")])
# resent
add("He resented Hayward's contempt for action and success.", "resent", "subj", "transitive", "litbank:351_of_human_bondage", "train",
    [("he","EXPERIENCER"),("contempt","STIMULUS")])
add("But he resented those words bitterly.", "resent", "subj", "transitive", "litbank:4276_north_and_south", "train",
    [("he","EXPERIENCER"),("words","STIMULUS")])
# covet
add("I coveted a cake of bread.", "covet", "subj", "transitive", "litbank:1260_jane_eyre_an_autobiography", "train",
    [("i","EXPERIENCER"),("cake","STIMULUS")])
add("It is impossible that you can covet the admiration of Heathcliff.", "covet", "subj", "transitive", "litbank:768_wuthering_heights", "train",
    [("you","EXPERIENCER"),("admiration","STIMULUS")])
# regret
add("She regretted what they had been, so small and exquisite.", "regret", "subj", "clausal_complement", "litbank:217_sons_and_lovers", "train",
    [("she","EXPERIENCER"),("what","THEME")])
add("I regret that I am not a man.", "regret", "subj", "clausal_complement", "litbank:78_tarzan_of_the_apes", "train",
    [("i","EXPERIENCER"),("man","THEME")])
# miss
add("That poor boy will miss you something cruel.", "miss", "subj", "transitive", "litbank:974_the_secret_agent_a_simple_tale", "train",
    [("boy","EXPERIENCER"),("you","STIMULUS")])
add("I rather miss my wild girl.", "miss", "subj", "transitive", "litbank:514_little_women", "train",
    [("i","EXPERIENCER"),("girl","STIMULUS")])
# doubt
add("I doubt whether my own sense would have corrected me without it.", "doubt", "subj", "clausal_complement", "litbank:158_emma", "train",
    [("i","EXPERIENCER"),("sense","THEME")])
add("He doubted not at all that she would use it.", "doubt", "subj", "clausal_complement", "litbank:502_desert_gold", "train",
    [("he","EXPERIENCER"),("she","THEME")])
# trust
add("She trusted him with her whole heart.", "trust", "subj", "transitive", "supplement", "train",
    [("she","EXPERIENCER"),("him","STIMULUS")])
# revere
add("He believed that women revere men for their manliness.", "revere", "subj", "transitive", "litbank:2641_a_room_with_a_view", "train",
    [("women","EXPERIENCER"),("men","STIMULUS")])
# pine (PP)
add("I'm pining to see you dance.", "pine", "subj", "infinitival_complement", "litbank:217_sons_and_lovers", "train",
    [("i","EXPERIENCER")])
# yearn
add("She yearned for a word of kindness from him.", "yearn", "subj", "pp_complement", "supplement", "heldout",
    [("she","EXPERIENCER"),("word","STIMULUS")])
add("He yearned after the friends of his boyhood.", "yearn", "subj", "pp_complement", "supplement", "heldout",
    [("he","EXPERIENCER"),("friends","STIMULUS")])

# ============================ OBJECT-EXPERIENCER (hard case) ============================
# frighten  (STIMULUS = subject, EXPERIENCER = object)
add("It frightened me very much, but I shot it in the ear.", "frighten", "obj", "exp_obj_active", "litbank:711_allan_quatermain", "train",
    [("it","STIMULUS"),("me","EXPERIENCER")])
add("Jo was frightened.", "frighten", "obj", "exp_obj_passive", "litbank:514_little_women", "train",
    [("jo","EXPERIENCER")])
add("The novel disaster had frightened stouter-hearted Jacks on bigger beanstalks.", "frighten", "obj", "exp_obj_active", "litbank:514_little_women", "train",
    [("disaster","STIMULUS"),("jacks","EXPERIENCER")])
# please
add("The reader will be pleased, I believe, to return with me to Sophia.", "please", "obj", "exp_obj_passive", "litbank:6593_history_of_tom_jones_a_foundling", "train",
    [("reader","EXPERIENCER")])
add("His mother was glad, he seemed so pleased.", "please", "obj", "exp_obj_passive", "litbank:217_sons_and_lovers", "train",
    [("he","EXPERIENCER")])
# anger
add("The loud reproach angered him beyond all measure.", "anger", "obj", "exp_obj_active", "supplement", "train",
    [("reproach","STIMULUS"),("him","EXPERIENCER")])
# delight
add("The very gentleness which had first delighted her turned to an affectation.", "delight", "obj", "exp_obj_active", "litbank:1342_pride_and_prejudice", "train",
    [("gentleness","STIMULUS"),("her","EXPERIENCER")])
add("I'm delighted to see you!", "delight", "obj", "exp_obj_passive", "litbank:2005_piccadilly_jim", "train",
    [("i","EXPERIENCER")])
# amuse
add("He was amused and interested by her conversation.", "amuse", "obj", "exp_obj_passive", "litbank:351_of_human_bondage", "train",
    [("he","EXPERIENCER"),("conversation","STIMULUS")])
add("Richard, quite amused with me, said he would be all right.", "amuse", "obj", "exp_obj_passive", "litbank:1023_bleak_house", "train",
    [("richard","EXPERIENCER"),("me","STIMULUS")])
# astonish
add("What astonished him was the endurance of Nell's mother.", "astonish", "obj", "exp_obj_active", "litbank:502_desert_gold", "heldout",
    [("what","STIMULUS"),("him","EXPERIENCER")])
add("I stared, astonished, and stirred profoundly by the man's resolution.", "astonish", "obj", "exp_obj_passive", "litbank:36_the_war_of_the_worlds", "heldout",
    [("i","EXPERIENCER"),("resolution","STIMULUS")])
add("Carrie listened, more astonished than anything else at this sudden rise of passion.", "astonish", "obj", "exp_obj_passive", "litbank:233_sister_carrie_a_novel", "heldout",
    [("carrie","EXPERIENCER"),("rise","STIMULUS")])
# annoy
add("If the flood annoyed him, so much the better.", "annoy", "obj", "exp_obj_active", "litbank:1260_jane_eyre_an_autobiography", "train",
    [("flood","STIMULUS"),("him","EXPERIENCER")])
add("That seemed to annoy the stranger very much.", "annoy", "obj", "exp_obj_active", "litbank:5230_the_invisible_man_a_grotesque_romance", "train",
    [("that","STIMULUS"),("stranger","EXPERIENCER")])
# terrify
add("The sudden roar terrified the horses.", "terrify", "obj", "exp_obj_active", "supplement", "heldout",
    [("roar","STIMULUS"),("horses","EXPERIENCER")])
add("She was terrified by the shadow on the wall.", "terrify", "obj", "exp_obj_passive", "supplement", "heldout",
    [("she","EXPERIENCER"),("shadow","STIMULUS")])
# alarm
add("He no longer alarmed her at all; she regarded him as a kind thing.", "alarm", "obj", "exp_obj_active", "litbank:2641_a_room_with_a_view", "train",
    [("he","STIMULUS"),("her","EXPERIENCER")])
add("But I will not alarm you unnecessarily.", "alarm", "obj", "exp_obj_active", "litbank:3268_the_mysteries_of_udolpho", "train",
    [("i","STIMULUS"),("you","EXPERIENCER")])
# surprise
add("Jimmy was surprised, relieved, and pleased.", "surprise", "obj", "exp_obj_passive", "litbank:2005_piccadilly_jim", "train",
    [("jimmy","EXPERIENCER")])
# disgust
add("He was disgusted at its sentimentality.", "disgust", "obj", "exp_obj_passive", "litbank:351_of_human_bondage", "train",
    [("he","EXPERIENCER"),("sentimentality","STIMULUS")])
add("I disgust you.", "disgust", "obj", "exp_obj_active", "litbank:351_of_human_bondage", "train",
    [("i","STIMULUS"),("you","EXPERIENCER")])
# shock / horrify
add("He was horrified at his thoughtlessness and tried to comfort her.", "horrify", "obj", "exp_obj_passive", "litbank:345_dracula", "heldout",
    [("he","EXPERIENCER"),("thoughtlessness","STIMULUS")])
add("For a few minutes we stood horrified over the corpse of Foulata.", "horrify", "obj", "exp_obj_passive", "litbank:2166_king_solomons_mines", "heldout",
    [("we","EXPERIENCER"),("corpse","STIMULUS")])
# startle
add("A sudden noise startled her from her reverie.", "startle", "obj", "exp_obj_active", "supplement", "train",
    [("noise","STIMULUS"),("her","EXPERIENCER")])
# comfort
add("It would comfort me, my husband!", "comfort", "obj", "exp_obj_active", "litbank:345_dracula", "train",
    [("it","STIMULUS"),("me","EXPERIENCER")])
add("Nothing could console her.", "console", "obj", "exp_obj_active", "litbank:4276_north_and_south", "train",
    [("nothing","STIMULUS"),("her","EXPERIENCER")])
add("Nothing could console and nothing could appease her.", "console", "obj", "exp_obj_active", "litbank:1342_pride_and_prejudice", "train",
    [("nothing","STIMULUS"),("her","EXPERIENCER")])
# trouble
add("Those thoughts began a little to disturb his brain.", "disturb", "obj", "exp_obj_active", "litbank:6593_history_of_tom_jones_a_foundling", "train",
    [("thoughts","STIMULUS"),("brain","EXPERIENCER")])
add("They were too much disturbed for words.", "disturb", "obj", "exp_obj_passive", "litbank:351_of_human_bondage", "train",
    [("they","EXPERIENCER")])
# vex
add("The delay vexed him more than he cared to say.", "vex", "obj", "exp_obj_active", "supplement", "train",
    [("delay","STIMULUS"),("him","EXPERIENCER")])
# charm
add("Bagnet, quite charmed, hopes to see him again.", "charm", "obj", "exp_obj_passive", "litbank:1023_bleak_house", "train",
    [("bagnet","EXPERIENCER")])
# fascinate
add("The monstrosity of the man had fascinated her.", "fascinate", "obj", "exp_obj_active", "litbank:974_the_secret_agent_a_simple_tale", "train",
    [("monstrosity","STIMULUS"),("her","EXPERIENCER")])
add("While he fascinated many, there were not a few who distrusted him.", "fascinate", "obj", "exp_obj_active", "litbank:174_the_picture_of_dorian_gray", "train",
    [("he","STIMULUS"),("many","EXPERIENCER")])
# interest
add("Philip was interested in her shiftless life.", "interest", "obj", "exp_obj_passive", "litbank:351_of_human_bondage", "train",
    [("philip","EXPERIENCER"),("life","STIMULUS")])
# irritate
add("Thea was grateful for his silent sympathy, even while it irritated her.", "irritate", "obj", "exp_obj_active", "litbank:44_the_song_of_the_lark", "train",
    [("it","STIMULUS"),("her","EXPERIENCER")])
add("That hiss, faint as it was, irritated the irascible gentleman.", "irritate", "obj", "exp_obj_active", "litbank:514_little_women", "train",
    [("hiss","STIMULUS"),("gentleman","EXPERIENCER")])
# enrage
add("All the indignities of his life enraged him.", "enrage", "obj", "exp_obj_active", "litbank:2814_dubliners", "train",
    [("indignities","STIMULUS"),("him","EXPERIENCER")])
add("He was enraged against the tattered man, and could have strangled him.", "enrage", "obj", "exp_obj_passive", "litbank:73_the_red_badge_of_courage_an_episode_of_the_american_civil_war", "train",
    [("he","EXPERIENCER"),("man","STIMULUS")])
# offend
add("The neighbours were offended.", "offend", "obj", "exp_obj_passive", "litbank:217_sons_and_lovers", "train",
    [("neighbours","EXPERIENCER")])
add("I felt as if one or both of them had mortally offended me.", "offend", "obj", "exp_obj_active", "litbank:155_the_moonstone", "train",
    [("them","STIMULUS"),("me","EXPERIENCER")])
# perplex
add("Shaw looked extremely perplexed by what Margaret had said.", "perplex", "obj", "exp_obj_passive", "litbank:4276_north_and_south", "train",
    [("shaw","EXPERIENCER"),("what","STIMULUS")])
# puzzle
add("An illness she did not know might explain what had so much puzzled her.", "puzzle", "obj", "exp_obj_active", "litbank:351_of_human_bondage", "train",
    [("what","STIMULUS"),("her","EXPERIENCER")])
add("She had the misfortune of answering questions which puzzled her sister.", "puzzle", "obj", "exp_obj_active", "litbank:158_emma", "train",
    [("questions","STIMULUS"),("sister","EXPERIENCER")])
# distress
add("It distressed her deeply to see him so changed.", "distress", "obj", "exp_obj_active", "supplement", "train",
    [("it","STIMULUS"),("her","EXPERIENCER")])
add("She was distressed beyond measure by the news.", "distress", "obj", "exp_obj_passive", "supplement", "train",
    [("she","EXPERIENCER"),("news","STIMULUS")])
# displease
add("She was displeased at the personal character Mr. Thornton drew.", "displease", "obj", "exp_obj_passive", "litbank:4276_north_and_south", "train",
    [("she","EXPERIENCER"),("character","STIMULUS")])
# embarrass
add("He did not embarrass her much.", "embarrass", "obj", "exp_obj_active", "litbank:217_sons_and_lovers", "heldout",
    [("he","STIMULUS"),("her","EXPERIENCER")])
add("Philip was touched and embarrassed.", "embarrass", "obj", "exp_obj_passive", "litbank:351_of_human_bondage", "heldout",
    [("philip","EXPERIENCER")])
# gladden
add("God sent them thither to gladden our poor Clifford.", "gladden", "obj", "exp_obj_active", "litbank:77_the_house_of_the_seven_gables", "heldout",
    [("them","STIMULUS"),("clifford","EXPERIENCER")])
add("The fire upon the hearth can gladden a whole semicircle of faces.", "gladden", "obj", "exp_obj_active", "litbank:77_the_house_of_the_seven_gables", "heldout",
    [("fire","STIMULUS"),("faces","EXPERIENCER")])
# torment
add("The memory of that night tormented him for years.", "torment", "obj", "exp_obj_active", "supplement", "train",
    [("memory","STIMULUS"),("him","EXPERIENCER")])
# soothe
add("The gentle music soothed the fretful child.", "soothe", "obj", "exp_obj_active", "supplement", "train",
    [("music","STIMULUS"),("child","EXPERIENCER")])

# ---- write ----
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    for rec in R:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# ---- integrity + summary ----
subj = sorted({r["verb_lemma"] for r in R if r["exp_type"]=="subj"})
obj  = sorted({r["verb_lemma"] for r in R if r["exp_type"]=="obj"})
from collections import Counter
con = Counter(r["construction"] for r in R)
src_supp = sum(1 for r in R if r["source"]=="supplement")
heldout_lem = sorted({r["verb_lemma"] for r in R if r["split_recommendation"]=="heldout"})
train_lem = sorted({r["verb_lemma"] for r in R if r["split_recommendation"]=="train"})
overlap = set(heldout_lem) & set(train_lem)
percv = Counter(r["verb_lemma"] for r in R)

print("wrote", OUT)
print("records:", len(R))
print("distinct psych verbs:", len(set(subj)|set(obj)), "| subj-exp:", len(subj), "| obj-exp:", len(obj))
print("subj lemmas:", subj)
print("obj lemmas:", obj)
print("constructions:", dict(con))
print("supplement records:", src_supp, "| litbank records:", len(R)-src_supp)
print("heldout lemmas:", heldout_lem)
print("lemma overlap train/heldout (must be empty):", overlap)
print("per-verb counts:", dict(percv))
