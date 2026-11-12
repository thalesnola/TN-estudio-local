"""Smoke opcional com mídia sintética; requer FFmpeg/ffprobe e Blender.

Uso: python tests/smoke_media.py --blender CAMINHO --output PASTA_NOVA
Não gera conteúdo por IA e não usa rede. Saídas ficam fora do repo.
"""
import argparse
import json
from pathlib import Path
import subprocess


def run(*args):
    return subprocess.run(args, check=True, capture_output=True)


def probe(path):
    return json.loads(run('ffprobe', '-v', 'error', '-show_streams', '-show_format',
                          '-of', 'json', str(path)).stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    originals = []
    for frame in range(2):
        pixels = bytes(c for y in range(8) for x in range(8)
                       for c in ((240, 80, 32) if x == frame + 2 else (16, 32, 64)))
        originals.append(pixels)
        (output / f'pixel-{frame:02}.ppm').write_bytes(b'P6\n8 8\n255\n' + pixels)
    video = output / 'pixel.mkv'
    run('ffmpeg', '-v', 'error', '-framerate', '12', '-i', str(output / 'pixel-%02d.ppm'),
        '-vf', 'scale=32:32:flags=neighbor,fps=24', '-c:v', 'ffv1', '-pix_fmt', 'bgr0', str(video))
    stream = probe(video)['streams'][0]
    assert (stream['width'], stream['height'], stream['r_frame_rate']) == (32, 32, '24/1')
    decoded = run('ffmpeg', '-v', 'error', '-i', str(video), '-f', 'rawvideo',
                  '-pix_fmt', 'rgb24', '-').stdout
    expanded = []
    for pixels in originals:
        expanded.append(bytes(c for y in range(32) for x in range(32)
                              for c in pixels[((y // 4) * 8 + x // 4) * 3:((y // 4) * 8 + x // 4) * 3 + 3]))
    assert decoded == expanded[0] * 2 + expanded[1] * 2, 'Escala ou exposição alterou pixels'
    blender_script = output / 'scene.py'
    blender_script.write_text('''import bpy, sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1])
bpy.ops.wm.read_factory_settings(use_empty=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=4
scene.render.resolution_x=64
scene.render.resolution_y=64
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
cube=bpy.data.objects['Cube']
for face in cube.data.polygons: face.use_smooth=False
material=bpy.data.materials.new('Synthetic orange')
material.diffuse_color=(0.8,0.12,0.03,1)
material.use_nodes=True
material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.8,0.12,0.03,1)
cube.data.materials.clear()
cube.data.materials.append(material)
scene.render.filepath=str(out/'low-poly.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'low-poly.blend'))
bpy.ops.render.render(write_still=True)
assert len(cube.data.polygons)==6
''', encoding='utf-8')
    result = run(args.blender, '--background', '--python-exit-code', '1',
                 '--python', str(blender_script), '--', str(output))
    (output / 'blender-stdout.txt').write_bytes(result.stdout)
    image = output / 'low-poly.png'
    stream = probe(image)['streams'][0]
    assert (stream['width'], stream['height']) == (64, 64)
    pixels = run('ffmpeg', '-v', 'error', '-i', str(image), '-f', 'rawvideo',
                 '-pix_fmt', 'rgb24', '-').stdout
    assert len(set(pixels[i:i+3] for i in range(0, len(pixels), 3))) > 16, 'Render vazio/uniforme'
    assert any(pixels[i] > 1.5 * max(pixels[i+1:i+3]) and pixels[i] > 40
               for i in range(0, len(pixels), 3)), 'Material laranja não apareceu no render'
    assert (output / 'low-poly.blend').stat().st_size > 0
    report = {'pixel': {'size': [32, 32], 'fps': 24, 'frames': 4,
                        'nearest_and_holds_exact': True},
              'blender': {'size': [64, 64], 'engine': 'CYCLES', 'device': 'CPU',
                          'native_scene_saved': True, 'nonuniform_image': True}}
    (output / 'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
