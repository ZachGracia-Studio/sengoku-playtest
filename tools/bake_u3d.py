# bake.py model.glb out_prefix [rot ...]  -> renders toon sprite via proto3d/toonbake.html, then palette-snaps + ink outline
import sys, asyncio, base64, io
import numpy as np
from PIL import Image, ImageFilter
from playwright.async_api import async_playwright
PAL = np.array([[27,27,31],[58,58,64],[229,218,194],[188,176,152],[200,55,45],[140,38,32],[199,173,112],[150,128,80],[74,103,136],[205,170,140]],float)
def snap(im):
    a=np.asarray(im).astype(float); rgb=a[...,:3]; al=a[...,3]
    d=((rgb[...,None,:]-PAL[None,None])**2).sum(-1); idx=d.argmin(-1); out=PAL[idx]
    o=np.dstack([out,np.where(al>110,255,0)]).astype(np.uint8)
    img=Image.fromarray(o,'RGBA')
    # ink outline: dilate alpha
    A=img.split()[3]; big=A.filter(ImageFilter.MaxFilter(5))
    ink=Image.new('RGBA',img.size,(27,27,31,0)); ink.putalpha(big)
    ink.alpha_composite(img); return ink
async def main(glb, prefix, rots):
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={'width':600,'height':600})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        for rot in rots:
            await pg.goto(f"http://localhost:8765/proto3d/toonbake.html?m={glb}&rot={rot}&size=600")
            await pg.wait_for_function("window.__done", timeout=60000)
            d=await pg.evaluate("window.__done")
            im=Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGBA')
            im.save(f"{prefix}_raw_{rot}.png"); s=snap(im); s=s.crop((0,0,600,500)); s.save(f"{prefix}_{rot}.png"); print(rot, s.size, s.getbbox())
        print(errs[:3]); await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3:] or ["0"]))
