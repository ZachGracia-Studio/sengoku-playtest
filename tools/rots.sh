#!/bin/bash
# rots.sh name  -> bakes 4 rotations and a labelled sheet
n=$1; cd /home/claude/tools
NORM=fp python3 bake.py models/kit/$n.glb /home/claude/kittl/3d/R_$n 0 90 180 270 >/dev/null
python3 - "$n" <<'PY'
import sys
from PIL import Image, ImageDraw
n=sys.argv[1]
ims=[Image.open(f'/home/claude/kittl/3d/R_{n}_{r}.png') for r in [0,90,180,270]]
H=max(i.height for i in ims); s=Image.new('RGBA',(sum(i.width for i in ims)+60,H+30),(171,149,106,255)); x=0
d=ImageDraw.Draw(s)
for r,i in zip([0,90,180,270],ims): s.alpha_composite(i,(x,H-i.height+30)); d.text((x+10,5),str(r),fill=(0,0,0)); x+=i.width+20
s.thumbnail((900,300)); s.save(f'/home/claude/kittl/3d/rots_{n}.png')
PY
