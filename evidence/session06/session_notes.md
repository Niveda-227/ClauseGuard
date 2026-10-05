# Session 06 user-session notes (protocol sep29_v2)

Observer: OBS01 · Model: 04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76
Documents: C and D · Tasks: C1, D1 · Limit: 180 s · ClauseGuard interface: desktop
Decision rule merged before these sessions: docs/decisions/midpoint_rule.json

## U003 - 2026-10-05, 18:12 · IN PERSON · consent: yes · screenshots: no
### Trial 1: ClauseGuard, task C1
- Prompt readings needed: 1
- What they did, in order: Opened ClauseGuard, looked through the results, identified the relevant clause about removing photos, and selected the answer.
- Used the Category filter? No
- Clicked a result to read the source sentence before answering? Yes
- The answer sentence shows three tags. What did they do or say about the tags? Looked at the tags but relied on the sentence itself to make the decision.
- Did they treat a wrong tag (Unilateral termination or Unilateral change) as true about the sentence? No
- Answer given: "They can remove photos or comments without giving me notice."
- Correct (sentence AND meaning)? Yes · Seconds (from the terminal): 46.705
- Anything they said aloud: "It says they can remove them without notice."
### Trial 2: Manual, task D1
- Prompt readings needed: 1
- What they did, in order: Read through the document, searched for the liability clause, found the relevant sentence, and gave the answer.
- Used Cmd+F / Ctrl+F? Yes; "liability"
- Answer given: "The company’s total liability is limited to the amount I paid in the twelve months before the claim."
- Correct (sentence AND meaning)? Yes · Seconds (from the terminal): 72.844
- Anything they said aloud: "So the maximum is what I paid in the last twelve months."

## U004 - 2026-10-05, 18:25 · IN PERSON · consent: yes · screenshots: no
### Trial 1: Manual, task C1
- Prompt readings needed: 1
- What they did, in order: Opened document C in Notepad, read through the document, searched for the relevant clause, and answered.
- Used Cmd+F / Ctrl+F? Yes; "remove"
- Answer given: "They can remove photos or comments I upload without notifying me."
- Correct (sentence AND meaning)? Yes · Seconds (from the terminal): 66.978
- Anything they said aloud: "It says they can remove them without notice."
### Trial 2: ClauseGuard, task D1
- Prompt readings needed: 1
- What they did, in order: Opened ClauseGuard, opened document D, clicked Analyze Terms, reviewed the results, opened the relevant liability result, and answered.
- Used the Category filter? No
- Clicked a result to read the source sentence before answering? Yes
- Mentioned or relied on the category tags? Looked at the tags but did not rely on them; they based the answer on the source sentence.
- Answer given: "The company’s total liability is limited to what I paid during the twelve months before the claim."
- Correct (sentence AND meaning)? Yes · Seconds (from the terminal): 51.568
- Anything they said aloud: "The liability is capped at the amount paid in the last twelve months."

## U005 - 2026-10-05, 18:32 · IN PERSON · consent: yes · screenshots: no
### Trial 1: Manual, task D1
- Prompt readings needed: 1
- What they did, in order: Opened document D in Notepad, read through the document, searched for the liability clause, and answered.
- Used Cmd+F / Ctrl+F? Yes; "liability"
- Answer given: "The total amount the company can be liable for is limited to what I paid in the twelve months before the claim."
- Correct (sentence AND meaning)? Yes · Seconds (from the terminal): 69.017
- Anything they said aloud: "It's limited to the amount I paid in the last twelve months."
### Trial 2: ClauseGuard, task C1
- Prompt readings needed: 1
- What they did, in order: Opened ClauseGuard, opened document C, clicked Analyze Terms, reviewed the results, clicked the relevant result, and answered.
- Used the Category filter? No
- Clicked a result to read the source sentence before answering? Yes
- The answer sentence shows three tags. What did they do or say about the tags? They noticed the three tags and read them, but focused on the source sentence rather than treating the tags as separate facts.
- Did they treat a wrong tag (Unilateral termination or Unilateral change) as true about the sentence? No; they did not treat the wrong tags as facts.
- Answer given: "They can remove any photos or comments I upload without notice."
- Correct (sentence AND meaning)? Yes · Seconds (from the terminal): 57.921
- Anything they said aloud: "The important part is that they can remove them without notice."

## Across participants
1. All three ClauseGuard trials (U003 C1, U004 D1, U005 C1) followed the same path: the participant opened the document, clicked Analyze terms, clicked a result to read the source sentence, and answered from that sentence. Nobody used the Category filter.
2. In all three ClauseGuard trials the participant looked at the category tags but based the answer on the source sentence, not on the tags.

## Issue #29 (task C1 with the app)
2 participants did C1 with ClauseGuard (U003, U005); 2 of 2 were correct (sentence and meaning) within 180 s. Both looked at the three tags on the answer sentence and based the answer on the source sentence; neither treated Unilateral termination or Unilateral change as true about the sentence. Two participants cannot show whether the extra tags mislead other readers.

## Measurement notes
- These notes were completed after the last session on 2026-10-05, not between trials. Seconds and start times above are copied from the saved trial records, not typed from memory.
- U003's first trial (C1, ClauseGuard) was run without the --interface, --observer and --output flags. The saved record shows interface desktop, observer OBS01, and it was written to evidence/session06/, so the defaults matched the intended values.
- On U004 D1 and U005 D1 the recorder showed the correctness question twice; the saved value for each is correct = 1, which matches the answers given.
- U005 D1 (manual): the participant worked on document D and gave a correct answer. The observer typed the wrong answer text into the recorder (the C1 answer instead of the D1 answer), and the saved observer note wrongly says "document C". The recorded correct = 1 is accurate. The participant's actual answer is the one given in the U005 Trial 1 section above. The raw JSON file was left unedited.

## What this does not show
3 new participants this week (plus U002 from Session 05), two short fictional documents. Tasks C1 and D1 differ in difficulty, so manual vs ClauseGuard is not a matched comparison, even counterbalanced. Not evidence about real legal documents or general benefit.
The three new participants were flatmates of the observer, who may be more forgiving than strangers would be.
