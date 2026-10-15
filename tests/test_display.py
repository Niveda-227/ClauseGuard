import unittest

from clauses.display import NO_FLAG, result_label, snippet


def row(i, text, labels):
    return {'sentence_id': i, 'text': text, 'labels': labels}


class DisplayTests(unittest.TestCase):
    def test_short_sentence_is_shown_whole(self):
        self.assertEqual(snippet('We may change these terms.'), 'We may change these terms.')

    def test_long_sentence_is_cut_at_a_word_and_marked(self):
        text = 'To the maximum extent permitted by applicable law, we are not liable for indirect damages.'
        out = snippet(text, 40)
        self.assertTrue(out.endswith('…'))
        self.assertLessEqual(len(out), 40)
        self.assertTrue(text.startswith(out[:-1]))
        self.assertFalse(out[:-1].endswith(' '))

    def test_whitespace_and_line_breaks_are_collapsed(self):
        self.assertEqual(snippet('We may\n  remove   content.'), 'We may remove content.')

    def test_label_shows_number_tags_and_sentence(self):
        out = result_label(row(2, 'We may change these terms at any time without notice.',
                               ['Unilateral termination', 'Unilateral change']))
        self.assertEqual(out, '3. Unilateral termination, Unilateral change | We may change these terms at any time without notice.')

    def test_unflagged_sentence_says_so(self):
        self.assertTrue(result_label(row(9, 'Support is available on weekdays.', [])).startswith(f'10. {NO_FLAG} | '))

    def test_tiny_width_is_refused(self):
        with self.assertRaises(ValueError):
            snippet('anything', 5)


if __name__ == '__main__':
    unittest.main()
