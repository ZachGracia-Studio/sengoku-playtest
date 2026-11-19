import bpy, math, bmesh, random
from mathutils import Vector, Matrix
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(7)
R = math.radians

def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def mat(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*[lin(c) for c in rgb], 1)
    b.inputs["Roughness"].default_value = 1
    return m

ROBE = mat("robe", (232, 224, 204)); ROBE2 = mat("robe2", (206, 198, 182)); HAIR = mat("hair", (30, 30, 36))
SHEEN = mat("sheen", (66, 66, 76)); SKIN = mat("skin", (200, 206, 212)); TAIL = mat("tail", (182, 200, 218))
FLAME = mat("flame", (86, 140, 210)); FLAME2 = mat("flame2", (182, 208, 234)); BAND = mat("band", (242, 238, 226))
EYE = mat("eye", (242, 240, 232))

def obj_from_bm(bm, m, name="mesh", smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def add(op, m, bevel=0.0, smooth=False, **kw):
    op(**kw); o = bpy.context.active_object; o.data.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    if smooth: bpy.ops.object.shade_smooth()
    return o

cube = bpy.ops.mesh.primitive_cube_add; cyl = bpy.ops.mesh.primitive_cylinder_add
cone = bpy.ops.mesh.primitive_cone_add; sph = bpy.ops.mesh.primitive_uv_sphere_add

def lathe(profile, segs, m, name, jag=None, lean=0.0):
    """Revolve [(radius, z)] around Z. jag(i, ring) -> z offset for a ragged hem. lean pushes upper rings toward -Y (hunch)."""
    bm = bmesh.new(); rings = []
    for k, (r, z) in enumerate(profile):
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            dz = jag(i, k) if jag else 0
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a) - lean * max(0, z - 0.6), z + dz)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]))
    bm.faces.new(list(reversed(rings[-1])))
    bm.normal_update()
    return obj_from_bm(bm, m, name)

# ---------------- robe: hunched bell, ragged hem of long and short tatters
hem = [-(0.22 if i % 2 else random.choice([0.0, 0.04])) - random.random() * 0.06 for i in range(16)]
lathe([(0.42, 0.44), (0.37, 0.58), (0.29, 0.8), (0.26, 0.98), (0.21, 1.12), (0.12, 1.2)], 16, ROBE, "robe",
      jag=lambda i, k: hem[i] if k == 0 else 0, lean=0.28)
lathe([(0.37, 0.47), (0.35, 0.62)], 16, ROBE2, "robe_inner", jag=lambda i, k: hem[(i + 1) % 16] * 0.8 if k == 0 else 0)
lathe([(0.29, 0.80), (0.27, 0.88)], 14, ROBE2, "obi", lean=0.28)
for s in (1, -1):   # collar, left over right
    add(cube, BAND, 0.008, size=1, location=(0.055 * s, -0.25, 1.0), scale=(0.06, 0.025, 0.24), rotation=(R(-18), R(26 * s), 0))

# ---------------- tail: wisp curling out from under the hem
for x, y, z, r in [(0.0, 0.03, 0.44, 0.24), (-0.04, 0.0, 0.3, 0.18), (-0.1, -0.04, 0.18, 0.13), (-0.17, -0.07, 0.09, 0.09), (-0.23, -0.07, 0.04, 0.06), (-0.27, -0.04, 0.02, 0.035)]:
    add(sph, TAIL, 0, smooth=True, segments=10, ring_count=7, radius=r, location=(x, y, z), scale=(1, 1, 0.8))

# ---------------- sleeves: wide drooping bells held forward
for s in (1, -1):
    sl = lathe([(0.075, 0.0), (0.12, 0.2), (0.16, 0.34)], 8, ROBE, f"sleeve{s}",
               jag=lambda i, k: (-0.05 if i % 2 else 0.0) if k == 2 else 0)
    sl.rotation_euler = (R(62), 0, R(-14 * s)); sl.location = (0.25 * s, -0.12, 1.06)
    add(cone, ROBE2, 0.01, vertices=5, radius1=0.13, radius2=0.04, depth=0.32, location=(0.29 * s, -0.27, 0.78), rotation=(R(172), 0, 0))
    hx, hy, hz = 0.27 * s, -0.43, 0.93
    add(sph, SKIN, 0, smooth=True, segments=10, ring_count=7, radius=0.055, location=(hx, hy, hz), scale=(1.0, 1.3, 0.75))
    for f in range(4):
        L = (0.12, 0.15, 0.14, 0.1)[f]
        add(cyl, SKIN, 0, smooth=True, vertices=6, radius=0.016, depth=L,
            location=(hx + (f - 1.5) * 0.026, hy - 0.05, hz - L / 2 - 0.01), rotation=(R(-12), 0, 0))

# ---------------- head, bowed forward
HX, HY, HZ = 0.0, -0.17, 1.32
add(sph, SKIN, 0, smooth=True, segments=14, ring_count=10, radius=0.15, location=(HX, HY - 0.01, HZ - 0.02), scale=(0.9, 0.95, 1.1))
add(sph, HAIR, 0, segments=12, ring_count=8, radius=0.19, location=(HX, HY + 0.03, HZ + 0.04), scale=(1.0, 1.0, 0.95))
add(sph, SHEEN, 0, segments=10, ring_count=6, radius=0.09, location=(HX + 0.06, HY - 0.02, HZ + 0.19), scale=(1.5, 1.3, 0.3), rotation=(R(-18), 0, 0))

def strand(x, y, z, w, L, rotz, tilt=0.0, m=HAIR):
    bm = bmesh.new(); t = 0.035
    v = [bm.verts.new(p) for p in [(-w, -t, 0), (w, -t, 0), (w, t, 0), (-w, t, 0), (-w * 0.35, -t * 0.6, -L), (w * 0.35, -t * 0.6, -L), (w * 0.35, t * 0.6, -L), (-w * 0.35, t * 0.6, -L)]]
    for f in [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]:
        bm.faces.new([v[i] for i in f])
    o = obj_from_bm(bm, m, "strand"); o.location = (x, y, z); o.rotation_euler = (R(tilt), 0, rotz)
    return o
for i in range(12):   # sides and back: a ring of long tapered strands
    a = math.pi * (-0.15 + 1.3 * i / 11)
    strand(HX + 0.19 * math.cos(a), HY + 0.03 + 0.19 * math.sin(a), HZ + 0.1, 0.075, 0.5 + 0.08 * (i % 3), a + math.pi / 2)
for x, L, tl in [(0.09, 0.5, 14), (-0.025, 0.46, 16), (-0.12, 0.4, 12)]:   # front curtain, gap shows one eye
    strand(HX + x, HY - 0.15, HZ + 0.08, 0.05 if x < 0 else 0.07, L, 0, tilt=tl)
add(sph, EYE, 0, smooth=True, segments=10, ring_count=7, radius=0.03, location=(HX + 0.035, HY - 0.15, HZ - 0.02), scale=(1, 0.6, 0.8))
add(sph, HAIR, 0, smooth=True, segments=8, ring_count=6, radius=0.013, location=(HX + 0.03, HY - 0.17, HZ - 0.025))
# hitaikakushi triangle above the curtain, headband visible at the temples
bm = bmesh.new(); v = [bm.verts.new(p) for p in [(-0.07, 0, 0), (0.07, 0, 0), (0, 0, 0.085)]]; bm.faces.new(v)
tri = obj_from_bm(bm, BAND, "hitai"); tri.location = (HX, HY - 0.19, HZ + 0.1); tri.rotation_euler = (R(-22), 0, 0)
tri.modifiers.new("s", "SOLIDIFY").thickness = 0.02
for s in (1, -1):
    add(cube, BAND, 0, size=1, location=(HX + 0.12 * s, HY - 0.12, HZ + 0.11), scale=(0.06, 0.02, 0.022), rotation=(0, 0, R(-35 * s)))

# ---------------- hitodama: spirit flame with a curling tip
fx, fy, fz = -0.44, -0.02, 1.4
add(sph, FLAME, 0, smooth=True, segments=12, ring_count=8, radius=0.1, location=(fx, fy, fz))
for x, y, z, r in [(0.0, 0.0, 0.1, 0.085), (0.02, 0.0, 0.18, 0.065), (0.06, 0.0, 0.25, 0.045), (0.11, 0.0, 0.29, 0.03), (0.15, 0.0, 0.28, 0.018)]:
    add(sph, FLAME, 0, smooth=True, segments=10, ring_count=6, radius=r, location=(fx + x, fy + y, fz + z))
add(sph, FLAME2, 0, smooth=True, segments=10, ring_count=6, radius=0.05, location=(fx - 0.01, fy - 0.07, fz - 0.01))

# ---------------- float: everything but the tail rises
for o in bpy.data.objects:
    if o.data and o.data.materials and o.data.materials[0].name != "tail": o.location.z += 0.2
for o in bpy.data.objects: o.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects[0]
bpy.ops.export_scene.gltf(filepath="/home/claude/sengoku-playtest/proto3d/models/kit/bl_yurei.glb", export_apply=True)
print("ok", len(bpy.data.objects))
