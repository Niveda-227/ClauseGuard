# Demo run-sheet: the web app (from Session 08; Session 09 adds the "Check it yourself" step)

For any live demo of ClauseGuard from Session 08 on, including demo day. The web app needs no internet connection: the page, the model and the example all come from the laptop.

## The day before, on the presenting laptop

```bash
cd ~/ClauseGuard
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
git switch main
git pull --ff-only origin main
python scripts/demo_check.py --output /tmp/demo_check_rehearsal.json
```

The last line must say `READY FOR THE DEMO`. The check confirms that the app runs the model the report quotes, that the demo document still gets the rehearsed flags, and that the web app returns exactly what the desktop app returns. The `--output` path keeps this rehearsal run out of the repository.

Then rehearse the flow below once, with a timer.

## One hour before

1. Plug in the charger. Turn on Do Not Disturb. Close chat apps and email.
2. Run the demo check again (same command). It must say `READY FOR THE DEMO`.
3. Start the app and leave it running:
   ```bash
   python -m webapp
   ```
   The browser opens `http://127.0.0.1:8641`. If port 8641 is busy: `python -m webapp --port 8642`.
4. Make the browser full screen. Zoom to 100% (Cmd+0 / Ctrl+0), or 110% for a projector.

## The flow (about 5 minutes)

| Step | Do | Say (in your own words) |
|---|---|---|
| 1 | Show the opening screen | "Terms of Service are long. ClauseGuard points you to the sentences that let a company change the deal, close your account, remove your content or choose the court." |
| 2 | Click the round "try the example" button | "This is an invented Terms of Service. It runs on this laptop; nothing is uploaded." |
| 3 | Click result 9 (Arbitration) | "Every flag links to the exact sentence, highlighted in place, with the score and the cut-off." |
| 4 | Click result 3 | "The model is not perfect: this sentence about changing the terms also gets 'Unilateral termination', which is wrong. That is why the original words are always one click away." |
| 5 | Choose **Clear**, then **Open .txt file**, and pick `examples/study/document_F.txt`, then **Analyze terms** | "This is one of our study documents." |
| 6 | Click result 12 | "This court sentence is not flagged: its score is just under the cut-off. Since Session 08 the app shows it as 'Possible: Jurisdiction' instead of hiding it." |
| 7 | Choose **Clear**, then **Open .txt file**, pick `examples/study/document_G.txt`, then **Analyze terms**. In Findings, scroll down to **Check it yourself** and open **Content removal** | "Nothing in this document is flagged for Content removal. That does not mean there is none. The panel says so, and lists two unflagged sentences that contain removal words: these are word matches, not predictions." |
| 8 | Click **Sentence 8 ('take down')** | "Here it is: they can take down your photos without telling you first. The model missed it; the panel sends you to it." |
| 9 | Scroll to the eight category cards | "These are the eight categories, from the UNFAIR-ToS research dataset." |
| 10 | Back in Findings, click **Download report (HTML)** | "You can keep a copy of the analysis. It contains the same Check it yourself panel." |

Never claim that a document with few flags is safe. The page itself says: a sentence with no flag can still matter.

Document G is a Session 09 study document. Use it in a demo only after the Session 09 user sessions are finished, so no future participant has seen it.

## If something goes wrong

| Problem | Do this |
|---|---|
| The browser shows "This site can't be reached" | The server stopped. In the terminal: `python -m webapp`, then reload the page |
| `Port 8641 is busy` | `python -m webapp --port 8642` and open `http://127.0.0.1:8642` |
| The page says the server is not reachable | Same as above: restart `python -m webapp` |
| The browser does not open by itself | Open `http://127.0.0.1:8641` by hand |
| The web app fails completely | Use the desktop app: `python app.py` (same model, same results) |
| Nothing graphical works | Open the HTML fallback written by the demo check: `analysis.html` in the repository folder |

## After the demo

Stop the server with Ctrl+C in the terminal. Nothing needs to be cleaned up: the app saves nothing unless you download a report.
