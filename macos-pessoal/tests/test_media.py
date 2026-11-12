import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import cv2
import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
VIDEO = SCRIPTS/'video/aplicar_emblema.py'
sys.path.insert(0, str(SCRIPTS))
from nola_paths import asset_id


class MediaTests(unittest.TestCase):
    def test_asset_id_rejects_paths(self):
        for value in ('../outside', '/tmp/out', 'with space', ''):
            with self.assertRaises(ValueError):
                asset_id(value)
        self.assertEqual(asset_id('nola-macm5'), 'nola-macm5')

    def test_video_composition_and_input_preservation(self):
        with tempfile.TemporaryDirectory(prefix='nola-macm5-test-') as temp:
            root = Path(temp)
            source, output, art = root/'input.mp4', root/'output.mp4', root/'art.png'
            rng = np.random.default_rng(4)
            patch = rng.integers(30, 220, (24, 24, 3), np.uint8)
            writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*'mp4v'), 12, (96, 96))
            self.assertTrue(writer.isOpened())
            for index in range(6):
                frame = np.full((96, 96, 3), 40, np.uint8)
                frame[10:34, 10+index:34+index] = patch
                writer.write(frame)
            writer.release()
            original = source.read_bytes()
            rgba = np.zeros((24, 24, 4), np.uint8)
            rgba[4:20, 4:20] = (10, 10, 250, 255)
            cv2.imwrite(str(art), rgba)
            command = [sys.executable, str(VIDEO), str(source), str(output), '--emblema', str(art),
                '--centro', '50', '55', '--diam', '16', '--modelo', '10', '10', '34', '34', '--suave', '0']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('quadros=6', result.stdout)
            self.assertEqual(source.read_bytes(), original)
            cap = cv2.VideoCapture(str(output))
            ok, frame = cap.read()
            self.assertTrue(ok)
            self.assertEqual(round(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 6)
            self.assertGreater(int(frame[55, 50, 2]), int(frame[55, 50, 0])+80)
            cap.release()
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('já existe', result.stderr)
            # Source and destination equality must be rejected before processing.
            same = command.copy()
            same[3] = str(source)
            result = subprocess.run(same, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), original)

    def test_preparation_pipeline_with_synthetic_art(self):
        with tempfile.TemporaryDirectory(prefix='nola-macm5-test-') as temp:
            root = Path(temp)
            (root/'fontes').mkdir()
            art = np.zeros((128, 128, 3), np.uint8)
            cv2.circle(art, (64, 64), 49, (120, 160, 200), -1)
            cv2.rectangle(art, (52, 38), (76, 90), (220, 220, 220), -1)
            cv2.imwrite(str(root/'fontes/nola-macm5.jpg'), art)
            env = dict(os.environ, NOLA_MEDIA_ROOT=str(root))
            for script in ('preparar.py', 'preparar_esfera.py'):
                result = subprocess.run([sys.executable, str(SCRIPTS/'3d/emblemas'/script), 'nola-macm5'],
                    env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((root/'fontes/nola-macm5-contorno.json').read_text())
            self.assertGreater(len(data['poly']), 8)
            height = cv2.imread(str(root/'fontes/nola-macm5-altura16.png'), cv2.IMREAD_UNCHANGED)
            self.assertEqual(height.dtype, np.uint16)
            self.assertTrue((root/'fontes/nola-macm5-esf-cor.png').exists())


if __name__ == '__main__':
    unittest.main()
