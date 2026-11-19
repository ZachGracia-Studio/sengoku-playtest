import bpy, math, bmesh
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)

def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def mat(name, rgb, emit=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*[lin(c) for c in rgb], 1)
    b.inputs["Roughness"].default_value = 1
    return m

ROBE = mat("robe", (232, 224, 204)); ROBE2 = mat("robe2", (200, 194, 180)); HAIR = mat("hair", (34, 34, 40)); SHEEN = mat("sheen", (70, 70, 80))
SKIN = mat("skin", (196, 200, 204)); TAIL = mat("tail", (178, 196, 214)); FLAME = mat("flame", (96, 150, 214))
BAND = mat("band", (240, 236, 222)); FLAME2 = mat("flame2", (190, 214, 236))

def add(op, m, bevel=0.0, smooth=False, **kw):
    op(**kw); o = bpy.context.active_object; o.data.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    if smooth:
        bpy.ops.object.shade_smooth()
    return o

cube = bpy.ops.mesh.primitive_cube_add; cyl = bpy.ops.mesh.primitive_cylinder_add
cone = bpy.ops.mesh.primitive_cone_add; sph = bpy.ops.mesh.primitive_uv_sphere_add
R = math.radians
# front of the figure faces -Y (glTF +Z), like the other baked models

# --- robe: hunched bell, wide ragged hem
body = add(cone, ROBE, 0.02, vertices=10, radius1=0.42, radius2=0.2, depth=0.72, location=(0, 0.04, 0.72), rotation=(R(-8), 0, 0))
# ragged hem teeth
for i in range(10):
    a = 2 * math.pi * i / 10 + 0.3
    L = 0.16 + 0.07 * (i % 3)
    add(cone, ROBE2 if i % 2 else ROBE, 0, vertices=4, radius1=0.12, radius2=0.0, depth=L,
        location=(0.37 * math.cos(a), 0.06 + 0.37 * math.sin(a), 0.36 - L / 2 + 0.02), rotation=(R(180), 0, a))
# belt
add(bpy.ops.mesh.primitive_torus_add, ROBE2, 0, major_radius=0.27, minor_radius=0.035, location=(0, 0.02, 0.88))
# kimono collar (left over right): two flat slabs crossing on the chest
for s in (1, -1):
    add(cube, BAND, 0.01, size=1, location=(0.05 * s, -0.19, 1.0), scale=(0.07, 0.03, 0.26), rotation=(R(-10), R(28 * s), 0))

# --- ghost tail: curling wisp under the hem, cold blue-white


# --- sleeves: big drooping bells held forward at chest height
for s in (1, -1):
    sl = add(cone, ROBE, 0.02, vertices=8, radius1=0.16, radius2=0.08, depth=0.42,
             location=(0.26 * s, -0.16, 0.96), rotation=(R(70), 0, R(-18 * s)))
    sl2 = add(cone, ROBE2, 0, vertices=6, radius1=0.15, radius2=0.0, depth=0.2,   # hanging sleeve flap
              location=(0.27 * s, -0.24, 0.78), rotation=(R(180), 0, 0))
    # limp hand and dangling fingers
    hx, hy, hz = 0.24 * s, -0.36, 0.9
    add(sph, SKIN, 0, smooth=True, segments=10, ring_count=8, radius=0.06, location=(hx, hy, hz), scale=(1, 1.2, 0.8))
    for f in range(3):
        add(cyl, SKIN, 0, smooth=True, vertices=6, radius=0.017, depth=0.13,
            location=(hx + (f - 1) * 0.03, hy - 0.04, hz - 0.08), rotation=(R(-20), 0, 0))

# --- head, mostly hidden by hair
add(sph, SKIN, 0, smooth=True, segments=14, ring_count=10, radius=0.17, location=(0, -0.06, 1.28))
# hair: a heavy curtain, back mass + front fringe falling over the face, a narrow gap on one side
add(cone, HAIR, 0.03, vertices=10, radius1=0.27, radius2=0.2, depth=0.6, location=(0, 0.03, 1.05), scale=(1.0, 0.9, 1.0))
add(sph, SHEEN, 0, smooth=True, segments=12, ring_count=8, radius=0.1, location=(0.06, -0.08, 1.49), scale=(1.4, 1.2, 0.35))
add(sph, HAIR, 0, smooth=True, segments=14, ring_count=10, radius=0.205, location=(0, -0.04, 1.33))
add(cube, HAIR, 0.02, size=1, location=(0.06, -0.2, 1.08), scale=(0.2, 0.06, 0.52), rotation=(R(6), 0, 0))
add(cube, HAIR, 0.02, size=1, location=(-0.14, -0.18, 1.04), scale=(0.08, 0.06, 0.56), rotation=(R(6), 0, R(8)))
# one pale eye in the gap
add(sph, BAND, 0, smooth=True, segments=8, ring_count=6, radius=0.025, location=(-0.07, -0.215, 1.3))
add(sph, HAIR, 0, segments=8, ring_count=6, radius=0.012, location=(-0.07, -0.235, 1.3))
# headband with the white triangle (hitaikakushi)
add(cube, BAND, 0.005, size=1, location=(0, -0.19, 1.43), scale=(0.2, 0.03, 0.03), rotation=(R(-20), 0, 0))
add(cone, BAND, 0.005, vertices=3, radius1=0.08, radius2=0, depth=0.02, location=(0, -0.235, 1.45), rotation=(R(90), 0, 0), scale=(1, 1.1, 1))

# --- hitodama: blue spirit flame floating by the right shoulder
fx, fy, fz = -0.42, 0.02, 1.42
add(sph, FLAME, 0, smooth=True, segments=12, ring_count=8, radius=0.09, location=(fx, fy, fz))
add(cone, FLAME, 0, smooth=True, vertices=10, radius1=0.085, radius2=0, depth=0.22, location=(fx + 0.02, fy, fz + 0.13), rotation=(0, R(-12), 0))
add(sph, FLAME2, 0, smooth=True, segments=10, ring_count=6, radius=0.04, location=(fx - 0.01, fy - 0.06, fz - 0.01))

for o in bpy.data.objects:
    if not o.name.startswith("tail"): o.location.z += 0.22
for i, (x, y, z, r) in enumerate([(0.0, 0.06, 0.5, 0.21), (-0.05, 0.02, 0.33, 0.16), (-0.12, -0.04, 0.19, 0.11), (-0.2, -0.08, 0.09, 0.07), (-0.26, -0.1, 0.03, 0.04)]):
    o = add(sph, TAIL, 0, smooth=True, segments=12, ring_count=8, radius=r, location=(x, y, z)); o.name = f"tail{i}"
for o in bpy.data.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath="/home/claude/sengoku-playtest/proto3d/models/kit/bl_yurei.glb", export_apply=True)
print("ok")
