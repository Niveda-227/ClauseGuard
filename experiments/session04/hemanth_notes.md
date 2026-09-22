# Environment and app check — 2026-09-22 (Hemanth)

## Machine
macOS 27.0 (arm64), Python 3.12.0, fresh `.venv` installed from `requirements.txt`.

## Results
- `test_hemanth_environment.py` — 3 tests, OK
- `check_environment.py` — `core_ready: true`; numpy 2.3.5, scipy 1.17.0,
  scikit-learn 1.8.0, joblib 1.5.3 all match the pinned versions
- Selected model `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`
  matches its manifest, so the artifact in the product is the evaluated one
- `check_environment.py --gui` — Tk module available and a window could be created
- Full suite — Ran 24 tests, OK
- `python -m clauses.cli data` — dataset downloaded, SHA-256 matches the pinned
  `934470d7…`

## Desktop app on a real laptop
The Tk window opened and both study documents analyzed correctly:
- `document_A.txt`: arbitration clause flagged at result 18 (task A1 answer)
- `document_B.txt`: account-termination clause flagged at result 16 (task B1 answer)
Category filter, source highlighting and export all worked. Confirmed to Niveda
that the user sessions can run with `--interface desktop`.

## Problems found
1. **macOS certificate failure (setup blocker).** On a python.org install,
   `python -m clauses.cli data` fails with `SSL: CERTIFICATE_VERIFY_FAILED`
   until `/Applications/Python 3.12/Install Certificates.command` is run.
   Anyone reproducing the evaluation hits this. Should go in the setup docs.
2. **Stale detail panel after loading a second document.** Opening a new file
   clears the results list but leaves the previous document's category detail
   visible in the lower-right panel until a new result is selected. A user could
   read it as belonging to the new document.
3. **Over-tagging on multi-category sentences.** In `document_B`, result 16
   ("We may terminate your account at any time, for any reason, without prior
   notice") is tagged Unilateral termination, Unilateral change and Content
   removal; only the first is correct. The same pattern appears in `document_A`
   result 12. Consistent with the class-balancing trade-off recorded in the
   session04 error analysis, and a risk for users who read the category list
   without checking the source sentence.

## Limitations of this check
- `check_environment.py` pins exact library versions, so a patch-level
  difference is reported as a failure rather than a warning. It passed here
  only because the `.venv` was built from `requirements.txt`.
- A successful Tk probe shows a window can be created; it is not a usability test.
- Hashing the model proves it matches its manifest, not that an unknown
  artifact is trustworthy.
