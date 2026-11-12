import bpy
s=bpy.context.scene
s.render.film_transparent=True
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA'
s.render.image_settings.color_depth='8'
