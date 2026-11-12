import bpy
p=bpy.context.preferences.addons['cycles'].preferences
for t in ('OPTIX','CUDA'):
    try:
        p.compute_device_type=t; p.get_devices()
        if any(d.type==t for d in p.devices):
            for d in p.devices: d.use=(d.type==t)
            print("DISPOSITIVO",t,[d.name for d in p.devices if d.use]); break
    except Exception as e: print("falhou",t,e)
bpy.context.scene.cycles.device='GPU'
