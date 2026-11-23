"""Run: python -m unittest discover -s tests -v"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app

class KnowledgeTests(unittest.TestCase):
    def test_stop_words_removed(self):
        self.assertEqual(app.terms('What is DNS?'), ['dns'])

    def test_answer_uses_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'knowledge').mkdir()
            (folder / 'knowledge' / 'network.md').write_text('DNS translates names into IP addresses.\nDHCP assigns IP addresses automatically.', encoding='utf-8')
            with patch.object(app, 'KNOWLEDGE', folder / 'knowledge'), patch.object(app, 'DB', folder / 'index.db'):
                app.initialize()
                result, sources = app.answer('What is DNS?')
                self.assertIn('DNS translates names', result)
                self.assertEqual(sources, ['network.md'])
                missing, sources = app.answer('What is quantum teleportation?')
                self.assertIn('couldn’t find', missing)
                self.assertEqual(sources, [])

if __name__ == '__main__':
    unittest.main()
