# Demo run-sheet: mid-semester presentation (October 6, 2026)

The live demo is 80 seconds inside a 5-minute talk. It shows the real app running the shipped model on a fictional document. It is rehearsed click by click, so nothing on screen is a surprise.

**Presenter:** Niveda (her laptop). **Backup operator:** Hemanth (has the app running on a second laptop, ready to share his screen). There is no recorded backup.

## One hour before

On the presenting laptop, in the ClauseGuard folder with the virtual environment active:

```bash
git switch main
git pull --ff-only origin main
python scripts/demo_check.py
```

It must end with `READY FOR THE DEMO`. It also rewrites `analysis.html`, the web-page fallback. If a line says `FAIL`, stop and fix it (see the table at the end) before the talk. Do not commit the new `demo_check.json` from this run; it is only a check.

Then:

1. Close every other app, browser tab and chat window. Turn on **Do Not Disturb** (macOS: Control Centre → Focus; Windows: Focus assist).
2. Start the app: `python app.py`. Leave it open, **empty**, at full size.
3. Open `reports/midpoint/slides.html` in Chrome. Press **F** for full screen.
4. Open `analysis.html` in a second browser tab (the fallback). Do not show it unless needed.
5. Zoom: **Share screen → Screen** (the whole screen, not a window), so switching between the slides and the app is visible.

## The 80 seconds, click by click

| # | Click | Say (short) | What the audience sees |
|---|---|---|---|
| 1 | Switch to the app (Cmd+Tab / Alt+Tab) | "This is the app running on my laptop." | Empty ClauseGuard window |
| 2 | **Load fictional example** | "A fictional terms document we wrote." | 11 lines of text on the left |
| 3 | **Analyze terms** | "It analyzes locally, nothing is uploaded." | List on the right; status bar: `11 sentences; 8 flagged. Model 04713fbf6e23.` |
| 4 | Point at the status bar | "This model ID is the model behind every number in this talk." | The model ID |
| 5 | **Category → Arbitration**, click the one result | "Every flag is tied to the original sentence, with a plain explanation and a score." | Sentence 9 highlighted in yellow; explanation and score in the lower panel |
| 6 | **Category → All sentences**, click line **3** | "Here it fails: two tags, 'Unilateral change' is right, 'Unilateral termination' is wrong. Over-tagging is our main problem." | `3. Unilateral termination, Unilateral change` |
| 7 | Switch back to the slides, press → | "So how good is the model overall?" | Slide 4 |

Timing check: steps 1 to 7 take 70 to 80 seconds when rehearsed. If you are behind, skip step 4 and say the model ID sentence during step 3.

## If something fails (decide in 5 seconds, do not debug live)

| What happens | Do this |
|---|---|
| The app window does not respond, or crashes | Switch to the browser tab with `analysis.html`. Say: "Here is the same analysis as a web page." Scroll to the Arbitration row and to sentence 3 |
| The browser fallback also fails | Say: "Hemanth will show the same app on his laptop." Hemanth shares his screen and runs the same 3 steps |
| Zoom shows only the slides | You shared a window, not the screen. Stop sharing, **Share screen → Screen** |
| The list looks different from the table above | Carry on and say what you see. After the talk, run `python scripts/demo_check.py` to find out why |

## Fixes for `demo_check.py` failures (the day before, not during the talk)

| FAIL line | Fix |
|---|---|
| `package scikit-learn` | `python -m pip install -r requirements.txt` inside the virtual environment |
| `demo model is the reported model` | Someone changed `artifacts/selected.joblib`. `git status`; restore it with `git checkout main -- artifacts/selected.joblib` and tell the team |
| `demo document flags match the rehearsal` | The flags changed. Usually a different scikit-learn version; fix packages first. Never edit the expected list to make it pass |
| `desktop app (Tk) available` | macOS: install Python 3.12 from python.org (it includes Tk). Windows: re-run the Python installer and tick **tcl/tk and IDLE**. Until fixed, demo with `analysis.html` |
