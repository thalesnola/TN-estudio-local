"""Paths and in-process Metal selection for the personal Apple Silicon tools."""
import os
from pathlib import Path
import re


def media_root():
    root = Path(os.environ.get('NOLA_MEDIA_ROOT', '~/nola-macm5/midia')).expanduser().resolve()
    for name in ('fontes', 'blend', 'modelo-3d', 'renders', 'renders-esfera'):
        (root/name).mkdir(parents=True, exist_ok=True)
    return root


def asset_id(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value):
        raise ValueError('Identificador de asset inválido: use letras, números, hífen ou sublinhado.')
    return value


def configure_metal(bpy, allow_cpu=None):
    """Do not write Blender user preferences; choose an actual detected device."""
    if allow_cpu is None:
        allow_cpu = os.environ.get('NOLA_ALLOW_CPU') == '1'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        devices = [device for device in prefs.devices if device.type == 'METAL']
        if devices:
            for device in prefs.devices:
                device.use = device.type == 'METAL'
            bpy.context.scene.cycles.device = 'GPU'
            print('DISPOSITIVO METAL', [device.name for device in devices])
            return 'METAL'
    except (TypeError, RuntimeError) as error:
        if not allow_cpu:
            raise RuntimeError('Metal indisponível; NOLA_ALLOW_CPU=1 autoriza CPU.') from error
    if not allow_cpu:
        raise RuntimeError('Nenhuma GPU Metal detectada; NOLA_ALLOW_CPU=1 autoriza CPU.')
    bpy.context.scene.cycles.device = 'CPU'
    print('DISPOSITIVO CPU (autorizado explicitamente)')
    return 'CPU'


def configure_device(bpy):
    """CPU is the validated default; Metal is an explicit diagnostic choice."""
    device = os.environ.get('NOLA_BLENDER_DEVICE', 'CPU').upper()
    if device == 'CPU':
        bpy.context.scene.cycles.device = 'CPU'
        print('DISPOSITIVO CPU (padrão validado nola-macm5)')
        return 'CPU'
    if device == 'METAL':
        return configure_metal(bpy, allow_cpu=False)
    raise ValueError('NOLA_BLENDER_DEVICE deve ser CPU ou METAL.')
