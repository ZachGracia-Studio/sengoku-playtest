import sys, asyncio
from playwright.async_api import async_playwright
async def main(url, out, z):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':375,'height':812}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(url); await pg.wait_for_timeout(2500)
        await pg.get_by_text("Test ground").first.click(); await pg.wait_for_timeout(3000)
        info=await pg.evaluate("""(z)=>{const g=window.__sengoku; const S=g.S;
          const k=S.buildings.find(b=>b.type==='keep'); const bx=k.tx+k.w+1.5, by=k.ty+k.h+1.5;
          S.units.length=0;
          const P=['spear','archer','samurai','gunner','monk','ninja'], E=['tengu','oni','kappa','kitsune'];
          P.forEach((t,i)=>{const u=g.addUnit(t,bx+i*0.9,by,1); u.face=1;});
          E.forEach((t,i)=>{const u=g.addUnit(t,bx+i*1.3+0.3,by+2.2,1); u.face=-1;});
          S.units.forEach(u=>{u.order=null;u.target=null;u.born=S.t-9;u.hitT=-9;});
          const c={X:(bx+2-(by+0.8))*32,Y:(bx+2+by+0.8)*18.5}; g.cam.x=c.X; g.cam.y=c.Y; g.cam.z=z; g.cam.tz=z;
          g.setRunning(false); return S.units.map(u=>u.type).join(',')}""", z)
        print(info); await pg.wait_for_timeout(600)
        await pg.screenshot(path=out); print(errs[:3]); await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], float(sys.argv[3])))
