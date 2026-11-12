import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('artcraft_personal', Path(__file__).with_name('artcraft.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class McpArgumentsTests(unittest.TestCase):
    def test_film_compact_flag_is_not_mcp_option(self):
        entry = module.mcp_entry('filmcraft', '/bin/example', '--compact one-line JSON output', Path('/work'))
        self.assertEqual(entry['args'], ['mcp'])

    def test_lightcraft_library_and_compact(self):
        entry = module.mcp_entry('lightcraft', '/bin/example', '--library DIR --compact', Path('/work'))
        self.assertEqual(entry['args'], ['mcp', '--library', '/work/biblioteca', '--compact'])

    def test_separate_read_write_roots(self):
        entry = module.mcp_entry('pdfcraft', '/bin/example', '--automation-read-root DIR --automation-write-root DIR --compact', Path('/work'))
        self.assertEqual(entry['args'], ['mcp','--automation-read-root','/work','--automation-write-root','/work/saida','--compact'])

    def test_absent_required_flags_refused(self):
        with self.assertRaises(ValueError):
            module.mcp_entry('photocraft', '/bin/example', 'unknown CLI', Path('/work'))

if __name__ == '__main__':
    unittest.main()
