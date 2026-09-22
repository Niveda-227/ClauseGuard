# Installation diagnostics

A successful run on one laptop does not show why another installation fails. This checker reports Python/dependency versions, trusted model-file integrity and optional Tk display availability.

## Run

```bash
python scripts/check_environment.py --output experiments/session04/hemanth_environment.json
python -m unittest discover -s tests -p 'test_hemanth_environment.py' -v
```

## How it works

The model check hashes bytes before any model deserialization. Matching a manifest checks consistency, not trust in an unknown third-party artifact. Core readiness and optional GUI readiness are reported separately.

Optional desktop check:

```bash
python scripts/check_environment.py --gui --output experiments/session04/hemanth_gui.json
```

A headless machine can pass core checks while failing the GUI probe. Report that result; do not change it to a pass. Inspect any environment details before committing.

## Research question

Run with --gui on a real desktop and compare with CLI-only mode. Document OS/Python, what worked, any observed failure, and the actual remedy. A successful Tk window probe is not an app usability test.

This is AI-assisted implementation material. Team members should record their actual review, adaptation and verification in the PR rather than claim unperformed work.
