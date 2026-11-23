"""Shrink a Tripo GLB for live play: decimate to a face budget, halve textures to 512, re-export as GLB.
usage: /opt/bl/bin/python decimate.py in.glb out.glb faces [texsize]"""
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
src, dst, faces = a[0], a[1], int(a[2]); tex = int(a[3]) if len(a) > 3 else 512
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
total = sum(len(o.data.polygons) for o in meshes)
import bmesh
for o in meshes:
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(o.data); bm.free()
for it in range(6):
    cur = sum(len(o.data.polygons) for o in meshes)
    if cur <= faces * 1.15: break
    for o in meshes:
        m = o.modifiers.new("dec", "DECIMATE"); m.ratio = max(0.02, faces / cur); m.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier="dec")
for img in bpy.data.images:
    print("IMG", img.name, tuple(img.size))
    if img.size[0] > tex:
        img.scale(tex, tex)
        img.pack()
after = sum(len(o.data.polygons) for o in meshes)
bpy.ops.export_scene.gltf(filepath=dst, export_apply=True, export_image_format="JPEG", export_jpeg_quality=85)
print(f"RESULT {os.path.basename(src)} {total} -> {after} faces, {os.path.getsize(dst)//1024} KB")
