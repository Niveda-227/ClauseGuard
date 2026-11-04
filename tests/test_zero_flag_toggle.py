"""Session 10: the "Only for categories with no flag" toggle in the Check it yourself panel (web app)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'webapp/static'


class ZeroFlagToggleTests(unittest.TestCase):
    def test_the_toggle_is_in_the_panel_and_off_by_default(self):
        html = (STATIC / 'index.html').read_text(encoding='utf-8')
        box = re.search(r'<input[^>]*id="check-zero-only"[^>]*>', html)
        self.assertIsNotNone(box)
        self.assertIn('type="checkbox"', box.group())
        self.assertNotIn('checked', box.group())
        self.assertIn('Only for categories with no flag', html)
        self.assertLess(html.index('id="check"'), html.index('id="check-zero-only"'))

    def test_the_script_hides_marks_only_for_flagged_categories_and_redraws_on_change(self):
        js = (STATIC / 'app.js').read_text(encoding='utf-8')
        self.assertIn("checkZeroOnly: $('check-zero-only')", js)
        self.assertIn('const hiddenByToggle = zeroOnly() && c.flagged > 0;', js)
        self.assertIn("els.checkZeroOnly.addEventListener('change', () => renderCheck())", js)


if __name__ == '__main__':
    unittest.main()
