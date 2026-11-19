#!/bin/bash
# pick.sh name rot -> assets/style/v2/b3d/name.webp
python3 -c "
from PIL import Image; Image.open('/home/claude/kittl/3d/R_$1_$2.png').save('/home/claude/sengoku-playtest/assets/style/v2/b3d/$1.webp',quality=90,method=6)"
