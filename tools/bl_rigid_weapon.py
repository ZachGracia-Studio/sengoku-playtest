"""Rebind a held weapon rigidly to one hand bone in a rigged GLB (Tripo auto-rig skins weapons like flesh).
usage: blender-python bl_rigid_weapon.py -- in.glb out.glb bone x y radius zfist_lo zfist_hi
Vertices within `radius` (horizontal) of the vertical line (x, y) and outside the fist band [zfist_lo, zfist_hi]
get 100% weight on `bone`. Animations are kept."""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
src, dst, bone = a[0], a[1], a[2]; X, Y, R, ZL, ZH = map(float, a[3:8])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = max((m for m in bpy.data.objects if m.type == "MESH"), key=lambda m: len(m.data.vertices))
for m in [m for m in bpy.data.objects if m.type == "MESH" and m is not o]: bpy.data.objects.remove(m)   # importer's bone-shape icosphere
mw = o.matrix_world; g = o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone); n = 0
for v in o.data.vertices:
    p = mw @ v.co
    if ((p.x - X) ** 2 + (p.y - Y) ** 2) ** .5 < R and not (ZL <= p.z <= ZH):
        for vg in list(v.groups): o.vertex_groups[vg.group].remove([v.index])
        g.add([v.index], 1.0, "REPLACE"); n += 1
print("RIGID", n, "verts ->", bone)
print("ACTIONS", [ac.name for ac in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_animations=True, export_animation_mode="ACTIONS", export_image_format="JPEG", export_jpeg_quality=82)
