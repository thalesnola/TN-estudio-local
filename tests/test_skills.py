"""Integridade das skills distribuídas; sem dependências ou serviços externos."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills-animacao'


class SkillPackageTests(unittest.TestCase):
    def test_discovery_metadata_and_references(self):
        entries = sorted(SKILLS.glob('*/SKILL.md'))
        self.assertTrue(entries, 'Nenhuma skill distribuída')
        for entry in entries:
            with self.subTest(skill=entry.parent.name):
                text = entry.read_text(encoding='utf-8')
                frontmatter = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
                self.assertIsNotNone(frontmatter)
                fields = dict(line.split(': ', 1) for line in frontmatter[1].splitlines())
                self.assertEqual(fields['name'], entry.parent.name)
                self.assertTrue(json.loads(fields['description']).strip())
                linked = set()
                for document in entry.parent.rglob('*.md'):
                    for target in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                        if '://' in target or target.startswith('#'):
                            continue
                        path = (document.parent / target.split('#')[0]).resolve()
                        self.assertTrue(path.is_relative_to(entry.parent.resolve()), target)
                        self.assertTrue(path.is_file(), target)
                        linked.add(path)
                for reference in (entry.parent / 'references').glob('*.md'):
                    self.assertIn(reference.resolve(), linked, 'Receita inacessível pelo entrypoint')

    def test_distribution_has_no_machine_paths_or_binary_payloads(self):
        for file in SKILLS.glob('*/**/*'):
            if not file.is_file():
                continue
            with self.subTest(file=str(file.relative_to(ROOT))):
                self.assertIn(file.suffix, {'.md', '.yaml'})
                text = file.read_text(encoding='utf-8')
                self.assertNotRegex(text, r'(?i)[a-z]:[/\\](?:users|wangp)[/\\]')
                self.assertNotIn('\x00', text)


if __name__ == '__main__':
    unittest.main()
