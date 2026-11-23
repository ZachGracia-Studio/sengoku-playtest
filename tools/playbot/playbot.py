import asyncio, json, sys, time
from playwright.async_api import async_playwright
# usage: playbot.py chapter seed [out.json]
CH, SEED = int(sys.argv[1]), int(sys.argv[2]); OUT = sys.argv[3] if len(sys.argv) > 3 else f"/tmp/bot_{CH}_{SEED}.json"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={'width': 390, 'height': 844}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        u = "http://localhost:8765/index.html?style=v2&r=3d&glb=1&fog=0"
        await pg.goto(u); await pg.evaluate("localStorage.setItem('sengoku.progress.v1', JSON.stringify({done:{'first-light':true,valley:true,pass:true,sandbox:true}}))")
        await pg.goto(u); await pg.wait_for_function("window.__sengoku && __sengoku.G3 && __sengoku.G3.ready", timeout=90000)
        await pg.add_script_tag(path="tools/playbot/bot.js")
        await pg.evaluate(f"BOT.begin({CH}, {SEED})")
        t0 = time.time(); shots = 0; nextShot = 0
        while True:
            r = await pg.evaluate("BOT.run(20)")
            if r['t'] >= nextShot:
                await pg.screenshot(path=f"/tmp/bot_{CH}_{SEED}_{shots:02d}.png"); shots += 1; nextShot += 120
            if r['over'] or r['t'] > 1800 or time.time() - t0 > 900: break
        res = await pg.evaluate("JSON.stringify({result: BOT.result||null, ev: BOT.ev, log: BOT.log})")
        open(OUT, 'w').write(res)
        d = json.loads(res); print(CH, SEED, 'result', d['result'] and d['result']['over'], 'gameT', r['t'], 'wall', round(time.time() - t0), 'errs', errs[:3])
        await b.close()
asyncio.run(main())
