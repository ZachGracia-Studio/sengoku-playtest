// Scripted "sensible first-time player" for Sengoku. Drives the game only through CMD, like the UI does.
// Usage in page: window.BOT.begin(chapterIndex, seed); then repeatedly BOT.run(seconds) until BOT.done.
(() => {
  const G = window.__sengoku;
  const B = window.BOT = { log: [], ev: [], done: false };
  const S = () => G.S, CH = () => G.CH;
  const keep = () => S().buildings.find(b => b.type === "keep");
  const count = t => S().buildings.filter(b => b.type === t).length;
  const soldiers = () => S().units.filter(u => u.team === "P" && !u.dead && !u.worker && !u.hero);
  const foes = () => S().units.filter(u => u.team === "E" && !u.dead);
  const note = (msg) => B.ev.push(`${fmt(S().t)} ${S().phase[0].toUpperCase()}${S().phase === "night" ? S().night : S().day} ${msg}`);
  const fmt = t => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;

  function place(type) {   // spiral out from the keep for the first legal spot
    const k = keep(), cx = k.tx + 1, cy = k.ty + 1;
    for (let r = 2; r < 12; r++) for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) {
      if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
      const tx = cx + dx, ty = cy + dy;
      if (G.canPlace(type, tx, ty)) { const res = G.CMD.build(type, tx, ty); if (res === "ok") { note(`build ${type}`); return true; } return false; }
    }
    return false;
  }
  function tryRecruit(type) { const r = G.CMD.recruit(type); if (r && (r === "ok" || r.queued || typeof r === "object")) { note(`recruit ${type}`); return true; } return false; }

  function decide() {
    const s = S(); if (s.over) return;
    const k = keep(); if (!k) return;
    if (!CH().dayLength && s.phase === "day" && (G.popUsed() >= 8 || s.phaseT < -9e9 || s.t - (B.dayStart ?? 0) > 150)) { G.CMD.startNight(); note("start night (manual)"); }
    const rice = s.rice, cap = G.popCap(), used = G.popUsed();
    // economy first
    if (count("granary") < 1) { if (rice >= 80 && place("granary")) return; if (s.t < 60) return; }
    if (count("dojo") < 1) { if (rice >= 100 && place("dojo")) return; if (s.t < 60) return; }
    if (count("lumber") < (s.wood < 60 && s.day >= 2 ? 3 : 1) && rice >= 60) { if (place("lumber")) return; }
    if (used >= cap - 1 && count("house") < 8 && rice >= 50 && s.wood >= 25) { if (place("house")) return; }
    if (count("granary") < 2 && soldiers().length >= 4 && rice >= 80) { if (place("granary")) return; }
    if (count("granary") < 3 && s.day >= 3 && rice >= 80) { if (place("granary")) return; }
    // keep upgrade once the basics stand
    if (k.tier === 0 && !k.upg && rice >= 260 && s.day >= 2) { if (G.CMD.upgrade(k.id) === "ok") note("upgrade keep"); return; }
    if (count("tower") < Math.min(3, s.day) && rice >= 140 && s.wood >= 30) { if (place("tower")) return; }
    // mid-game sinks a real player reaches for once rice piles up: upgrades, more housing, a second drill yard
    if (rice >= 220) {
      const up = ["dojo", "granary", "house", "keep", "lumber", "tower"].flatMap(t => S().buildings.filter(b => b.type === t && !b.upg && b.tier < 2));
      for (const b of up) if (G.CMD.upgrade(b.id) === "ok") { note(`upgrade ${b.type}→${b.tier + 2}`); return; }
      if (used >= cap - 2 && count("house") < 14 && s.wood >= 25) { if (place("house")) return; }
      if (count("dojo") < 2 && rice >= 300) { if (place("dojo")) return; }
    }
    // army: keep a reserve of ~40 rice by day, spend freely at night
    const reserve = s.phase === "day" ? 40 : 0;
    const n = soldiers().length, want = n % 3 === 2 ? "archer" : "spear";
    if (used < cap && rice >= 40 + reserve) { const dt = Math.max(0, ...S().buildings.filter(b => b.type === "dojo").map(b => b.tier)); tryRecruit(dt >= 1 && n % 3 === 1 ? "samurai" : want) || tryRecruit(want); }
    // combine any trios
    const ids = new Set(soldiers().filter(u => (u.size || 1) < 9).map(u => u.id));
    if (ids.size >= 3) { const made = G.CMD.combine(ids); if (made) note(`combine x${made}`); }
  }

  B.begin = (chapter, seed) => {
    Object.assign(B, { log: [], ev: [], done: false, chapter, seed, nextDecide: 0, lastNight: 0, lastLost: 0 });
    G.start(chapter, seed);
  };
  B.run = (secs) => {
    const s0 = S(); const end = s0.t + secs;
    while (!S().over && S().t < end) {
      G.step();
      const s = S();
      if (s.phase !== B.lastPhase) { if (s.phase === "day") B.dayStart = s.t; B.lastPhase = s.phase; note(s.phase === "night" ? `NIGHT ${s.night} begins: army ${soldiers().length} units, pop ${G.popUsed()}/${G.popCap()}, rice ${Math.round(s.rice)}` : `dawn`); }
      if (s.t >= B.nextDecide) { B.nextDecide = s.t + 1; decide();
        B.log.push([+s.t.toFixed(1), s.phase === "night" ? "N" + s.night : "D" + s.day, Math.round(s.rice), Math.round(s.wood || 0), G.popUsed(), G.popCap(), soldiers().length, foes().length, Math.round(keep() ? keep().hp : 0)]); }
      if (s.stats.lost > B.lastLost) { note(`lost ${s.stats.lost - B.lastLost} soldier(s)`); B.lastLost = s.stats.lost; }
    }
    const s = S();
    if (s.over) { B.done = true; B.result = { over: s.over, t: s.t, nights: s.log.nights, stats: s.stats, builds: s.log.builds }; }
    return { t: s.t, over: s.over || null };
  };
})();
