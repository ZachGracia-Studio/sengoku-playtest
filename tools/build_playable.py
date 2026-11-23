#!/usr/bin/env python3
"""Build the hosted playable (3D board) from the repo.

- Forces ?style=v2&r=3d&glb=1 through a __Q shim (the host can't take URL params).
- Packs assets/3d/*.glb into a few base64 bundles (the host serves .txt, not .glb,
  and caps an artifact at 512 files), with a JSON index of byte ranges.
- Copies the 2D assets and vendor modules.

usage: python3 tools/build_playable.py OUT_DIR [BASE_ASSETS_DIR]
BASE_ASSETS_DIR: an existing deploy whose assets/ to reuse (default: repo assets/).
"""
import base64, json, os, shutil, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
BASE = sys.argv[2] if len(sys.argv) > 2 else None
BUNDLE_BYTES = 9 * 1024 * 1024   # raw bytes per bundle (≈12 MB as base64, under the 20 MB file cap)

os.makedirs(OUT, exist_ok=True)
# 2D assets
src_assets = os.path.join(BASE, "assets") if BASE else os.path.join(REPO, "assets")
for root, _, files in os.walk(src_assets):
    rel = os.path.relpath(root, src_assets)
    if rel.split(os.sep)[0] in ("3d",) or "/src" in "/" + rel.replace(os.sep, "/"):
        continue
    for f in files:
        if f.endswith((".psd", ".glb")) or f.endswith(".glb.txt"):
            continue
        d = os.path.join(OUT, "assets", rel); os.makedirs(d, exist_ok=True)
        shutil.copy2(os.path.join(root, f), d)
# vendor
for p in ["vendor/three.module.js", "vendor/jsm/loaders/GLTFLoader.js", "vendor/jsm/utils/BufferGeometryUtils.js", "vendor/jsm/utils/SkeletonUtils.js"]:
    os.makedirs(os.path.dirname(os.path.join(OUT, p)), exist_ok=True); shutil.copy2(os.path.join(REPO, p), os.path.join(OUT, p))
# 3D bundles
d3 = os.path.join(OUT, "assets", "3d"); shutil.rmtree(d3, ignore_errors=True); os.makedirs(d3)
index, buf, bi = {}, bytearray(), 0
def flush():
    global buf, bi
    if buf:
        open(os.path.join(d3, f"b{bi}.txt"), "w").write(base64.b64encode(bytes(buf)).decode()); bi += 1; buf = bytearray()
for f in sorted(os.listdir(os.path.join(REPO, "assets", "3d"))):
    if not f.endswith(".glb"): continue
    data = open(os.path.join(REPO, "assets", "3d", f), "rb").read()
    if buf and len(buf) + len(data) > BUNDLE_BYTES: flush()
    index[f[:-4]] = [bi, len(buf), len(data)]; buf += data
flush()
json.dump(index, open(os.path.join(d3, "index.json"), "w"))
# index.html
s = open(os.path.join(REPO, "index.html")).read()
i = s.index("\n<script>", 200)
q = '<script>var __Q=(function(){var q=location.search||"";if(!/[?&]style=/.test(q))q+=(q?"&":"?")+"style=v2";if(!/[?&]r=/.test(q))q+="&r=3d";if(!/[?&]glb=/.test(q))q+="&glb=1";return q;})();</script>'
s = s[:i] + "\n" + q + s[i:]
head, body = s[:i + len(q) + 1], s[i + len(q) + 1:]
body = body.replace("location.search", "__Q")
old = "L.loadAsync(`assets/3d/${n}.glb`)"
assert old in body, "loader line changed"
body = body.replace(old, "glbBundle(n).then(b => L.parseAsync(b, \"assets/3d/\"))")
helper = """
/* hosted build: the models come packed in base64 bundles with a byte-range index */
const GLB_BUNDLES = {};
let GLB_INDEX = null;
async function glbBundle(n) {
  GLB_INDEX ||= fetch("assets/3d/index.json").then(r => r.json());
  const e = (await GLB_INDEX)[n]; if (!e) throw 0;
  GLB_BUNDLES[e[0]] ||= fetch(`assets/3d/b${e[0]}.txt`).then(r => r.text()).then(t => { const s = atob(t.trim()), a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a; });
  const a = await GLB_BUNDLES[e[0]]; return a.slice(e[1], e[1] + e[2]).buffer;
}
"""
body = body.replace("async function loadGLB3() {", helper + "async function loadGLB3() {", 1)
open(os.path.join(OUT, "index.html"), "w").write(head + body)
n = sum(len(f) for _, _, f in os.walk(OUT))
print(f"built {OUT}: {len(index)} models in {bi} bundles, {n} files")
