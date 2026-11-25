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

    def test_markdown_sections_are_cited(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'knowledge').mkdir()
            (folder / 'knowledge' / 'guide.md').write_text(
                '# Networking\n## DNS\nDNS translates domain names into IP addresses.\n'
                '## DHCP\nDHCP assigns network addresses to clients.\n', encoding='utf-8')
            with patch.object(app, 'KNOWLEDGE', folder / 'knowledge'), patch.object(app, 'DB', folder / 'index.db'):
                app.initialize()
                reply, sources = app.answer('What is DNS?')
                self.assertIn('DNS translates', reply)
                self.assertIn('guide.md — DNS', sources)

    def test_long_documents_split_into_small_passages(self):
        passages = list(app.split_passages(' '.join(['network'] * 400), '.txt', max_chars=100))
        self.assertGreater(len(passages), 1)
        self.assertTrue(all(len(text) <= 100 for _section, text in passages))

if __name__ == '__main__':
    unittest.main()
