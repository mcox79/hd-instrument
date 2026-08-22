# COMMENTARY -- anything you want me to look at, without interrupting me

Type below. Newest goes at the BOTTOM. You do not need to run anything and you do not need to wait
for me to be idle: I am told about anything unread at every session start AND at every turn
boundary, including in the middle of an unattended overnight run.

You can write here from ANY device, in ANY markdown editor. A heading is nice but not required --
text typed at the end with no heading is still picked up and still marked as unread.

<!-- PARSER CONTRACT -- READ BEFORE REWORDING.
     This document is parsed by tools/commentary.py, and its unread entries are injected by
     tools/session_start_hook.py and data/hooks/staging/stop_hook.py.
     The API is ONE literal: an entry begins with a line starting `## `.
     Everything above the first such line is this header and is preserved verbatim.
     Editing or adding entry TEXT is always safe and is the intended use.
     (CLAUDE.md: "A doc parsed by code is coupled to it".) -->

## 2026-08-17T13:09:11Z  --  the status window

The waiting on tab needs a ui/ux evaluation It's very hard to use and see. It's worth running through ui/ux for all the tabs and the gui overall honestly

## 2026-08-17T13:09:53Z  --  the status window

The questions tab now only appears to have one question, and no way for me to select a new one? It's unclear how I would see other questions there

## 2026-08-18T10:43:07Z  --  the status window

I'm seeing a lot of negative experimental results - why? We should be narrowing in on GOOD results - why aren't we? All negative results you should drill (safely - we shouldn't be giving away any of our substrate specifics here) for brain fidelity and what we should do to get closer to that - every time.

## 2026-08-18T11:01:48Z  --  the status window

there should be a button on the "running" tab to turn off overnight or turn it back on, with an input for iterations.
There should also be a button on that tab to kill the orphans / zombie processes that haven't cleanly exited

## 2026-08-19T19:44:45Z  --  the status window

Why aren't you sharing any questions on the gui? Also please update the gui and add an "updated" timestamp on each tab so I know when the data is new or not

## 2026-08-19T20:22:05Z  --  the status window

Quick note on the note taking and a "newness detector" - I think we did do some work on this - so is worth looking back at the experimental corpus

## 2026-08-19T20:23:25Z  --  the status window

I want to make sure that you're properly drilling all negative findings and doing a brain fidelity check

## 2026-08-19T20:25:00Z  --  the status window

I want to know how you missed that surprise experimental data - I thought we had this all consolidated and known at this point? What else are we missing?

## 2026-08-19T22:27:04Z  --  the status window

don't forget the phase diagram for these different components
make sure you're drilling negative results and continue to evaluate brain fidelity

## 2026-08-20T01:31:37Z  --  the status window

adjusting a belief sounds like an important capability for substrate - so let's keep that finding and integrate where it needs to go

## 2026-08-20T02:14:39Z  --  the status window

I want to re-emphasize being brain foundational here. Don't just wire in organs because you think it could help - we're making connections because the brain does

## 2026-08-20T12:06:45Z  --  the status window

I want to make sure we've been drilling and evaluating deeply the brain foundationality of any negatives

## 2026-08-20T12:31:52Z  --  the status window

just a quick though on stories vs textbooks. When I read either of those, I read them in a very different way. You don't approach a textbook like a story - textbooks are supposed to have facts laid out for learning, stories are there to enjoy - to get a new perspective or imagine a different life or world. Yes, you can learn from stories, but it's not the same kind of learning at all.

## 2026-08-20T12:48:12Z  --  the status window

please turn off the hook loop when you see this, and in the running tab on gui make a button that turns the loop on, and another that turns it off

## 2026-08-20T14:41:29Z  --  the status window

there are ~8 questions in the "still need to be answered" section that I think are already answered / moot

## 2026-08-20T14:44:17Z  --  the status window

you should add some kind of error log or statistics that can figure out what's going wrong with the gui - weird things happenening and it's hanging a lot. the tabs keep changing slightly with every update too

## 2026-08-20T15:45:56Z  --  the status window

I did answer d6 but I don't think those legacy questions are working properly. Yes you can merge to main. These are all the questions that appear stil "unanswered" in the waiting on you tab - they are all legacy and need to be removed I believe:
D1-D7
OP1-OP4

## 2026-08-20T16:06:55Z  --  the status window

tehere are a lot of "no verdict" runs in the "latest results" tab - is that correct or old?

## 2026-08-20T21:59:25Z  --  the status window

Make sure you always have 2 high priority angles you can work on while you're waiting on results

## 2026-08-20T22:11:14Z  --  the status window

when evaluating what to work on next, you should do brain fidelity checks to identify what is the next most enabling feature. Also, consider doing very deep brain fidelity checks of organs or components, to make sure that each step is doing what it should be. Also, evauating each step of components / organs to idnetify the weak step and drilling in on that could be valuable

## 2026-08-21T01:07:13Z  --  the status window

just remember that in any sleep function, while the brain throws away detail, we can put that detail into cold storage and not lose it. We'll still want a consolidation function so we're not duplicating things, but we should never throw out useful information

## 2026-08-21T01:36:26Z  --  the status window

it seems like the main benefit of sleep might be to optimized the time for query - we should have a hierarchical memory - optimized, not in the weeds on details, and then a 2nd level based on what it finds there that is way faster. something like this?

Also - why did we stop working on reading? Were are we on the different functinos of substrate?

## 2026-08-21T01:36:58Z  --  the status window

also, there was a task that I just killed (python) that was taking about 8gigs of memory - it was hanging the gui and nimbalyst

## 2026-08-21T01:49:33Z  --  the status window

are you able to measure or set an alarm for when you have 10% context left?
Are you able to compact when you want to?

While you're considering this and answering me, please fully prepare for compaction

## 2026-08-21T02:12:20Z  --  the status window

i think this reading and grounding thing was figured out a while ago - but you clearly didn't pick up on that. look deeply at the old notes for what worked best

## 2026-08-21T02:22:53Z  --  the status window

You should make an overngiht plan with a clear and varied plan of attack, including a few high priority organs / capabilities

## 2026-08-21T02:54:54Z  --  the status window

Just make sure you know that your plan to expand to other sections of the substrate overnight as needed. Don't wander, but be diligent and with purpose

## 2026-08-21T13:00:04Z  --  the status window

So, we did a bunch of work on this I believe - the reading part. We explicitely built something that stored the knowledge we reaed.  We also developed something that tried to sense the ~distance from any new fact to the grounded foundation - which is essentially what we need to read next. You should look for those experiments.

## 2026-08-21T13:27:28Z  --  the status window

to be clear, the work we did was to figure out how FAR the new words were from the ~closest grounded foundation in ~conceptual space, and how many hops it might take. We were able to get a very good sense of what else we needed to learn to fill that space from that. drill the relevant previous experimental results to learn more

## 2026-08-21T15:40:17Z  --  the status window

I'd like you to do an audit of all the work you've been doing - what has been successful and what those wins are, and what has not been successful, and what you did in each case that helped achieve success and failure. I'd like you to figure out a more efficient method for future development from this. Do a deep job on this - we need to optimize our approach.

## 2026-08-21T18:19:51Z  --  the status window

what did you find after your deep review of your methodologies and positive vs negative results? I missed your report.

Also there are a lot of very old and not updated tabs in the gui - can we refresh and /or clean it up?

## 2026-08-21T18:41:58Z  --  the status window

I think you may have missed my point on the retrospective. I think that you may have a process flow that is not ideal for making progress on substrate - you often go for answers that might make sense in standard coding, but don't apply well here. I need you to imagine yourself as a neuroscience expert, working to recreate the human brain as an AI. You just happen to be an expert in coding too.

## 2026-08-22T01:50:19Z  --  the status window

how are we doing in performance now? did the perspective of being a neuroscience focused person result in better results? have we made that perspective concrete?

## 2026-08-22T01:54:35Z  --  the status window

also - i want you to evaluate your progress against what it would take for this to be ready commercially - I feel like I dont' have a sense of progress. are we making progress?

## 2026-08-22T01:55:05Z  --  the status window

we did a fuckton of work on grounding. make sure you understand all of it.

## 2026-08-22T16:10:07Z  --  the status window

in gen the top of the gui takes up too much space - I still can't read the questions on tab 3

## 2026-08-22T16:15:43Z  --  the status window

Whenever the warning for "old code" comes up in the gui it takes up a ton of unecessary space. Can you run an optimiaztion over the entire gui, and evaluate it for ui/ux and things that are completely unessecary, like the tab titles redrawing every ~10 seconds? I feel like a clean run over all aspects and using some heuristics would be very useful

## 2026-08-22T16:33:44Z  --  the status window

fyi the problem tab doesn't list any of the problems you submitted? How am I supposed to submit a solution there what is the proper process? we're almost done with our first solution
Also need to know what the priority order is for the problems. It would be great for the problem tab to also give me the promopt to kick off any problem

## 2026-08-22T17:09:32Z  --  the status window

I shared a note in the last (and first) problem solution submission, about the problem list submission being problemattic. in addition to that, please for each new problem, if I select it, I want the field to include an entire prompt and problem definition that I can paste in the solver session to kick it off. it should include the following, and any problem name / info that's required for kickoff:
"You are the SOLVER session (opus 4.8), not the strategy session. Do NOT touch the plan,
STATUS.md, the board, or other problem folders. Your slug is: <slug>.
Read notes/problems/README.md, then notes/problems/<slug>/PROBLEM.md in full, run its
VERIFY BEFORE YOU START block and `before_you_start.py` before doing anything, and
ignore the autoloop/STATUS injection if they fire."

## 2026-08-22T17:40:52Z  --  the status window

FYI on the problem tab - you need to make it clear when problems are solved or not. for instance, I submitted a solution to a problem, but there's no indication if you saw that, if it was correct, etc. if it's not correct or needs more, it needs a flag, and if it's done it needs to move into an archive so it's not taking up space in that list
