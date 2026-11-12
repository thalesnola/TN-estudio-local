#!/usr/bin/env python3
"""Lote serial macOS com assets pessoais e subprocessos verificados."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from nola_paths import media_root, asset_id


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('assets', nargs='+', type=asset_id)
    p.add_argument('--tipo', choices=('emblema', 'esfera'), default='emblema')
    p.add_argument('--blender', default=shutil.which('blender'))
    p.add_argument('--posprocessar', action='store_true')
    a = p.parse_args()
    if not a.blender:
        p.error('Blender não encontrado no PATH; passe --blender.')
    root = media_root()
    scripts = Path(__file__).resolve().parent/'3d/emblemas'
    for asset in a.assets:
        scene = root/'blend'/f'{a.tipo}-{asset.lower()}-3d.blend'
        if not scene.is_file():
            p.error(f'Asset ausente: {scene}')
    for asset in a.assets:
        scene = root/'blend'/f'{a.tipo}-{asset.lower()}-3d.blend'
        rd = 'renders-esfera' if a.tipo == 'esfera' else 'renders'
        temp = root/rd/'_trabalho'/asset
        env = dict(os.environ, SIG=asset, TIPO=a.tipo)
        for orientation in ('q', 'v'):
            output = temp/orientation
            output.mkdir(parents=True, exist_ok=True)
            command = [a.blender, '--background', str(scene), '--python-exit-code', '1',
                '--python', str(scripts/'cycles_gpu.py'), '--python', str(scripts/'sem_sobrescrever.py')]
            if orientation == 'v':
                command += ['--python', str(scripts/'render_vertical_arte.py')]
            command += ['--python', str(scripts/'render_alpha.py'), '-o', str(output/f'{orientation}_'), '-a']
            with (temp/f'{orientation}.log').open('w') as log:
                subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        if a.posprocessar:
            subprocess.run([sys.executable, str(scripts/'posprocessar.py'), asset], env=env, check=True)
        print(asset, 'pronto')


if __name__ == '__main__':
    main()
