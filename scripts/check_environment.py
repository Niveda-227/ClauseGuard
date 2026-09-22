"""Diagnose the local ClauseGuard installation; never install or upload anything."""
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_model(root):
    root = Path(root)
    model = root / 'artifacts/selected.joblib'
    manifest = root / 'artifacts/selected.json'
    if not model.is_file() or not manifest.is_file():
        return {'ok': False, 'detail': 'Missing selected.joblib or selected.json; restore the trusted project artifacts.'}
    try:
        expected = json.loads(manifest.read_text(encoding='utf-8'))['artifact_sha256']
        actual = hashlib.sha256(model.read_bytes()).hexdigest()
        return {'ok': expected == actual, 'sha256': actual,
                'detail': 'Matches manifest.' if expected == actual else 'Hash mismatch; inspect artifact provenance before loading.'}
    except (ValueError, KeyError, OSError) as e:
        return {'ok': False, 'detail': str(e)}


def inspect(root=ROOT, probe_gui=False):
    root = Path(root)
    checks = [{'name': 'python', 'ok': platform.python_version_tuple()[:2] == ('3', '12'),
               'actual': platform.python_version(), 'expected': '3.12.x'}]
    for line in (root/'requirements.txt').read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, expected = line.split('==', 1)
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        checks.append({'name': name, 'expected': expected, 'actual': actual, 'ok': actual == expected})
    checks.append({'name': 'selected_model', **check_model(root)})
    available = importlib.util.find_spec('tkinter') is not None
    gui = {'module_available': available, 'display_probe_requested': probe_gui,
           'display_usable': None, 'detail': 'Not probed. CLI/HTML does not require Tk.'}
    if probe_gui:
        if not available:
            gui.update(display_usable=False, detail='Install the Tk support matching your Python distribution, or use CLI/HTML.')
        else:
            try:
                import tkinter
                window = tkinter.Tk()
                try:
                    window.withdraw()
                    window.update_idletasks()
                finally:
                    window.destroy()
                gui.update(display_usable=True, detail='A Tk window could be created; this does not test the app workflow.')
            except Exception as e:
                gui.update(display_usable=False, detail=f'{type(e).__name__}: {e}. Use a desktop session or CLI/HTML.')
    ok = all(c['ok'] for c in checks)
    return {'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(),
            'core_ready': ok, 'checks': checks, 'gui': gui,
            'requested_checks_passed': ok and (not probe_gui or gui['display_usable'] is True),
            'remedy': 'Use Python 3.12 and python -m pip install -r requirements.txt; no changes were made by this checker.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gui', action='store_true', help='Also attempt to create and close a Tk window.')
    parser.add_argument('--output', help='Optional JSON output; review system details before committing.')
    args = parser.parse_args()
    try:
        result = inspect(probe_gui=args.gui)
        payload = json.dumps(result, indent=2)+'\n'
        if args.output:
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(payload,encoding='utf-8')
        print(payload)
        return 0 if result['requested_checks_passed'] else 1
    except (ValueError, OSError) as e:
        parser.exit(2, f'Environment check failed: {e}\n')


if __name__ == '__main__':
    raise SystemExit(main())
