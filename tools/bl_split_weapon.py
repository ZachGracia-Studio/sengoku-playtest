"""Cut a held weapon out of a rigged GLB into its own unskinned mesh named "weapon", with its origin at the grip.
The game then carries it at the hand bone's position with its own (upright) orientation, because preset motions
rotate the wrist as if the hand were empty.
usage: blender-python bl_split_weapon.py -- in.glb out.glb Right|Left x y radius zfist_lo zfist_hi grip_z [label]
(label "bow" keeps a bow upright on the attack)
Vertices within `radius` (horizontal) of the vertical line (x, y), outside the fist band, become the weapon."""
import bpy, bmesh, sys
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
src, dst, SIDE = a[0], a[1], a[2]; X, Y, R, ZL, ZH, GZ = map(float, a[3:9]); LABEL = a[9] if len(a) > 9 else ""
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
o = max((m for m in bpy.data.objects if m.type == "MESH"), key=lambda m: len(m.data.vertices))
for m in [m for m in bpy.data.objects if m.type == "MESH" and m is not o]: bpy.data.objects.remove(m)
mw = o.matrix_world
bpy.context.view_layer.objects.active = o; o.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
n = 0
arm = [m for m in bpy.data.objects if m.type == "ARMATURE"][0]
hand = arm.matrix_world @ arm.data.bones[f"mixamorig:{SIDE}Hand"].head_local
names = {g.index: g.name for g in o.vertex_groups}
for v in o.data.vertices:
    p = mw @ v.co
    in_line = ((p.x - X) ** 2 + (p.y - Y) ** 2) ** .5 < R and not (ZL <= p.z <= ZH)
    top = max(v.groups, key=lambda g: g.weight) if v.groups else None
    hand_far = top is not None and f"{SIDE}Hand" in names[top.group] and (p - hand).length > .08   # the auto-rig skins the shaft to fingers
    v.select = in_line or hand_far
    n += v.select
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.separate(type="SELECTED"); bpy.ops.object.mode_set(mode="OBJECT")
w = [m for m in bpy.context.selected_objects if m is not o and m.type == "MESH"][0]
w.name = w.data.name = "weapon" + ("_" + LABEL if LABEL else "") + ("_L" if SIDE == "Left" else "_R")
w.vertex_groups.clear()
for md in list(w.modifiers): w.modifiers.remove(md)
wm = w.matrix_world.copy(); w.parent = None; w.matrix_world = wm
bpy.ops.object.select_all(action="DESELECT"); w.select_set(True); bpy.context.view_layer.objects.active = w
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.scene.cursor.location = Vector((X, Y, GZ)); bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
print("WEAPON", n, "verts; origin", tuple(round(c, 3) for c in w.location), "dims", tuple(round(c, 3) for c in w.dimensions))
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_animations=True, export_animation_mode="ACTIONS", export_image_format="JPEG", export_jpeg_quality=82)
