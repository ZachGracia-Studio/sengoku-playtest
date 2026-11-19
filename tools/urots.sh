#!/bin/bash
n=$1; cd /home/claude/tools
python3 bake.py models/kit/$n.glb /home/claude/kittl/3d/U_$n 0 90 180 270 >/dev/null
python3 - "$n" <<'PY'
import sys
from PIL import Image, ImageDraw
n=sys.argv[1]
ims=[Image.open(f'/home/claude/kittl/3d/U_{n}_{r}.png').crop((150,0,650,667)) for r in [0,90,180,270]]
s=Image.new('RGBA',(2000,697),(171,149,106,255)); d=ImageDraw.Draw(s)
for k,(r,i) in enumerate(zip([0,90,180,270],ims)): s.alpha_composite(i,(k*500,30)); d.text((k*500+10,5),str(r),fill=(0,0,0))
s.thumbnail((800,280)); s.save(f'/home/claude/kittl/3d/urots_{n}.png')
PY
