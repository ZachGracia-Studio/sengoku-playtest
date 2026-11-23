import os
"""Bind a back banner (sashimono) rigidly to the upper spine in a rigged GLB.
Tripo's auto-rig often skins it to an arm, so it flails when the arm moves.
usage: blender-python bl_rigid_banner.py -- in.glb out.glb xmin xmax ymin ymax zflag pole_x0 pole_x1 zpole
Selects verts in the x/y box that are above zflag (the flag), or inside the pole column above zpole."""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
src, dst = a[0], a[1]; X0, X1, Y0, Y1, ZF, PX0, PX1, ZP = map(float, a[2:10])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = max((m for m in bpy.data.objects if m.type == "MESH"), key=lambda m: len(m.data.vertices))
for m in [m for m in bpy.data.objects if m.type == "MESH" and m is not o and not m.name.startswith("weapon")]: bpy.data.objects.remove(m)
mw = o.matrix_world; BONE = os.environ.get("BONE","mixamorig:Spine2"); g = o.vertex_groups.get(BONE); n = 0
for v in o.data.vertices:
    p = mw @ v.co
    if X0 <= p.x <= X1 and Y0 <= p.y <= Y1 and (p.z >= ZF or (PX0 <= p.x <= PX1 and p.z >= ZP)):
        for vg in list(v.groups): o.vertex_groups[vg.group].remove([v.index])
        g.add([v.index], 1.0, "REPLACE"); n += 1
print("BANNER", n, "verts ->", BONE)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_animations=True, export_animation_mode="ACTIONS", export_image_format="JPEG", export_jpeg_quality=82)
