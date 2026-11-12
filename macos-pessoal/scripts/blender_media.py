"""Blender nola-macm5: render, pack, GLB export and inspection with explicit paths.

blender --background --python blender_media.py -- render --input scene.blend --output frame.png
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nola_paths import configure_metal


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('render', 'pack', 'export-glb', 'verify-glb'))
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--width', type=int, default=700)
    parser.add_argument('--height', type=int, default=700)
    parser.add_argument('--samples', type=int, default=32)
    parser.add_argument('--frame', type=int, default=1)
    parser.add_argument('--transparent', action='store_true')
    parser.add_argument('--device', choices=('METAL', 'CPU'), default='CPU')
    parser.add_argument('--sobrescrever', action='store_true')
    a = parser.parse_args(argv)
    a.input, a.output = a.input.expanduser().resolve(), a.output.expanduser().resolve()
    if not a.input.is_file():
        parser.error(f'Asset ausente: {a.input}')
    if a.input == a.output:
        parser.error('A saída deve ser diferente do asset original.')
    if a.output.exists() and a.action != 'verify-glb' and not a.sobrescrever:
        parser.error('Saída existente: use --sobrescrever.')
    if min(a.width, a.height, a.samples) < 1:
        parser.error('Dimensões e samples devem ser positivos.')
    import bpy
    if a.action == 'verify-glb':
        if a.output.exists() and any(a.output.iterdir()) and not a.sobrescrever:
            parser.error('Pasta de inspeção não vazia: use --sobrescrever.')
        a.output.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(a.input))
        from mathutils import Vector
        points = [obj.matrix_world @ Vector(corner) for obj in bpy.context.scene.objects if obj.type == 'MESH' for corner in obj.bound_box]
        if not points:
            parser.error('GLB não contém malhas.')
        lower = Vector(tuple(min(point[i] for point in points) for i in range(3)))
        upper = Vector(tuple(max(point[i] for point in points) for i in range(3)))
        center = (lower+upper)/2
        span = max(upper-lower)
        bpy.ops.object.camera_add()
        camera = bpy.context.object
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = max(span*1.35, 0.1)
        bpy.context.scene.camera = camera
        bpy.ops.object.light_add(type='AREA', location=center+Vector((span*2, -span*2, span*3)))
        lamp = bpy.context.object
        lamp.data.energy, lamp.data.size = max(span*span*200, 100), max(span*2, 1)
        lamp.rotation_euler = (center-lamp.location).to_track_quat('-Z', 'Y').to_euler()
        world = bpy.data.worlds.new('nola-macm5-world')
        world.use_nodes = True
        world.node_tree.nodes['Background'].inputs[0].default_value = (0.35, 0.35, 0.35, 1)
        bpy.context.scene.world = world
        shots = []
        for side, direction in [('frente', -1), ('verso', 1)]:
            camera.location = center+Vector((0, direction*max(span*3, 1), span*0.1))
            camera.rotation_euler = (center-camera.location).to_track_quat('-Z', 'Y').to_euler()
            shots.append((side, camera.location.copy(), camera.rotation_euler.copy()))
    else:
        bpy.ops.wm.open_mainfile(filepath=str(a.input))
        a.output.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    if a.action == 'pack':
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(a.output), copy=True)
        return
    if a.action == 'export-glb':
        scene.frame_set(a.frame)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type in ('MESH', 'EMPTY'):
                obj.select_set(True)
        if not bpy.context.selected_objects:
            parser.error('Nenhuma malha/empty selecionável no arquivo.')
        bpy.ops.export_scene.gltf(filepath=str(a.output), export_format='GLB', use_selection=True,
            export_apply=True, export_animations=False, export_yup=True, export_image_format='AUTO')
        return
    scene.render.engine = 'CYCLES'
    if a.device == 'METAL':
        configure_metal(bpy)
    else:
        scene.cycles.device = 'CPU'
    scene.cycles.samples = a.samples
    scene.render.resolution_x, scene.render.resolution_y = a.width, a.height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = a.transparent
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA' if a.transparent else 'RGB'
    scene.frame_set(a.frame)
    if scene.camera is None:
        parser.error('Cena sem câmera; forneça uma cena pessoal com câmera configurada.')
    if a.action == 'verify-glb':
        for side, location, rotation in shots:
            scene.camera.location, scene.camera.rotation_euler = location, rotation
            scene.render.filepath = str(a.output/f'nola-macm5-{side}.png')
            bpy.ops.render.render(write_still=True)
    else:
        scene.render.filepath = str(a.output)
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
