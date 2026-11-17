# ClauseGuard: final submission

ClauseGuard points a reader to the clauses in a Terms of Service that are worth reading: for every sentence it flags which of eight potentially unfair clause categories it states, always next to the original sentence. It runs entirely on the user's own computer.

This folder is the final submission (due Tuesday December 1, 2026, 5:00 pm). It was set up in Session 11; the numbers are added after the Session 12 freeze, each copied from the result file named next to it.

## Files in this folder

- `README.md`: this file (setup, how to run, the demo).
- `report.md`: the final report, with the five required sections.
- `slides.md`: the outline of the demo-day presentation.

## Run it from a clean clone

Requirements: Python 3.12 and git. Every package version is pinned in `requirements.txt`.

```bash
git clone https://github.com/Niveda-227/ClauseGuard.git
cd ClauseGuard
python3.12 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m clauses.cli data             # downloads and checks the pinned dataset (needed only to retrain or evaluate)
python -m webapp                       # opens http://127.0.0.1:8641
```

The web app works offline: the page, the model (`artifacts/selected.joblib`) and the example all come from the laptop, and no text is sent anywhere or stored.

Other useful commands:
- `python -m unittest discover -s tests`: the whole test suite.
- `python scripts/demo_check.py`: checks that the app runs the reported model and is ready for a demo; it must end `READY FOR THE DEMO`.
- `python scripts/reproduce_model.py`: rebuilds the product model from the train split and checks it is the model we report.

## The demo

The step-by-step demo is in [docs/DEMO_RUNSHEET_web.md](../../docs/DEMO_RUNSHEET_web.md), and the rehearsal checklist in [docs/DEMO_REHEARSAL.md](../../docs/DEMO_REHEARSAL.md). The model shown in the demo is the model the report and the slides describe (same SHA-256, in `artifacts/selected.json`).

## Where the evidence is

- Model results: `experiments/` (one folder per session) and [docs/MODEL_CARD.md](../../docs/MODEL_CARD.md).
- Decisions and the rules behind them (each record says when it was written): [docs/decisions/](../../docs/decisions/).
- Outside-user evidence: `evidence/` (one folder per session).
- Weekly reports: `reports/session04.md` to `reports/session12.md`.
