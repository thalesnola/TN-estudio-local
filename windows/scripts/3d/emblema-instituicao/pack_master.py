import bpy
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\<USUARIO>\Documents\Emblema-INSTITUICAO-Padrao\blend\emblema-instituicao-3d.blend", copy=True)
print("PACOTE OK", [i.name for i in bpy.data.images if i.packed_file])
