#!/usr/bin/env python3
"""Shrink the textures inside a GLB without touching geometry, skin or animation.
usage: glb_shrink_tex.py in.glb out.glb [max_px=512] [jpeg_quality=82]"""
import io, json, struct, sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
MAX = int(sys.argv[3]) if len(sys.argv) > 3 else 512
Q = int(sys.argv[4]) if len(sys.argv) > 4 else 82
b = open(src, "rb").read()
jl = struct.unpack("<I", b[12:16])[0]; j = json.loads(b[20:20 + jl])
bin0 = 20 + jl + 8; binl = struct.unpack("<I", b[20 + jl:24 + jl])[0]; BIN = b[bin0:bin0 + binl]
img_views = {im["bufferView"]: i for i, im in enumerate(j.get("images", [])) if "bufferView" in im}
out = bytearray()
for vi, v in enumerate(j["bufferViews"]):
    data = BIN[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]]
    if vi in img_views:
        im = Image.open(io.BytesIO(data)); im.thumbnail((MAX, MAX))
        buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=Q); data = buf.getvalue()
        j["images"][img_views[vi]]["mimeType"] = "image/jpeg"
    while len(out) % 4: out.append(0)
    v["byteOffset"] = len(out); v["byteLength"] = len(data); out += data
while len(out) % 4: out.append(0)
j["buffers"][0]["byteLength"] = len(out)
js = json.dumps(j, separators=(",", ":")).encode()
while len(js) % 4: js += b" "
glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(out)) + struct.pack("<I", len(js)) + b"JSON" + js + struct.pack("<I", len(out)) + b"BIN\x00" + out
open(dst, "wb").write(glb)
print(f"{src} -> {dst}: {len(b)//1024} KB -> {len(glb)//1024} KB")
