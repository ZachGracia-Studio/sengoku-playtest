import os
# bake.py model.glb out_prefix [rot ...]  -> renders toon sprite via proto3d/toonbake.html, then palette-snaps + ink outline
import sys, asyncio, base64, io
import numpy as np
from PIL import Image, ImageFilter
from playwright.async_api import async_playwright
PAL = np.array([[27,27,31],[58,58,64],[229,218,194],[188,176,152],[150,140,120],[74,52,40],[122,86,56],[156,127,74],[110,86,52],[199,173,112],[158,134,80],[170,166,158],[132,128,120],[96,93,88],[111,138,94],[76,99,68],[200,55,45],[140,38,32],[74,103,136],[217,180,143]],float)
def snap(im):
    P=PAL[:-1] if os.environ.get('NORM')=='fp' else PAL
    a=np.asarray(im).astype(float); rgb=a[...,:3]; al=a[...,3]
    from skimage.color import rgb2lab
    L=rgb2lab(rgb/255.0); LP=rgb2lab((P/255.0)[None])[0]
    d=((L[...,None,:]-LP[None,None])**2*np.array([0.6,1.4,1.4])).sum(-1); idx=d.argmin(-1); out=P[idx]
    o=np.dstack([out,np.where(al>110,255,0)]).astype(np.uint8)
    img=Image.fromarray(o,'RGBA')
    # ink outline: dilate alpha
    A=img.split()[3]; big=A.filter(ImageFilter.MaxFilter(int(os.environ.get('OUTLINE','5'))))
    ink=Image.new('RGBA',img.size,(27,27,31,0)); ink.putalpha(big)
    ink.alpha_composite(img); return ink
async def main(glb, prefix, rots, norm=""):
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={'width':800,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        for rot in rots:
            await pg.goto(f"http://localhost:8765/proto3d/toonbake.html?m={glb}&rot={rot}&size=800&norm={norm}")
            await pg.wait_for_function("window.__done", timeout=60000)
            d=await pg.evaluate("window.__done")
            im=Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGBA')
            im.save(f"{prefix}_raw_{rot}.png"); s=snap(im)
            if norm=="fp": s=s.crop(s.getbbox())
            else: s=s.crop((0,0,800,max(667,(s.getbbox() or (0,0,0,667))[3]) if os.environ.get('CROPB') else 667))
            s.save(f"{prefix}_{rot}.png"); print(rot, s.size, s.getbbox())
        print(errs[:3]); await b.close()
import os
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3:] or ["0"], os.environ.get("NORM","")))
