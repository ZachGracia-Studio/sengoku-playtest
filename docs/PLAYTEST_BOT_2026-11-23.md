# Scripted playthrough — 2026-11-23

Bot: `tools/playbot/bot.js` (a sensible first-time player, drives the game only through CMD: storehouse → drill yard → lumber → houses as capacity fills, spear/archer/samurai, combines trios, upgrades when it can afford, never skips the day). Runner: `python3 tools/playbot/playbot.py <chapter> <seed>` against the local server (3D GLB mode). No micro, no walls, no hero abilities — a real player defends better than this.

## Results (3 runs per chapter, fixed bot)
| Chapter | Result | Length | Losses | Keep low point |
|---|---|---|---|---|
| Valley Keep (5 nights) | 3/3 win (6/6 incl. first bot) | ~7 min | 0–11 | 1482/1500 (never threatened) |
| Mountain Pass (7 nights) | 2/3 win | ~12 min | 11–25 | 6 HP (loss), 510 (win) |

## Findings
1. **Pass runs out of wood.** ~7 trees in cutter reach (40 wood each, no regrowth) ≈ 280 wood for the whole chapter. Wood hits 0 by Night 4 in every run; zero upgrades happen; houses stop, so troop capacity freezes and rice piles up to 1,800–2,500 with nothing to buy.
2. **Pass difficulty spikes at Nights 5–7.** Nights 1–4 cost 0–2 soldiers; Nights 5–7 cost 9–14 each. Partly a consequence of (1): the army can't grow after Night 4.
3. **A tai dies all at once.** Nine soldiers vanish in one moment; most losses in the Pass are single tai wipes.
4. **Valley has no tension.** The keep is never below ~85%; a passive player wins.
5. **Nights are short against days.** Nights run 17–35 s (Valley) against 60 s days.

## Round 2 — after the changes (same bot, 3 runs each)
Changes: felled trees regrow (70 s of spring growth; summer ×1, autumn ×0.55, winter none), a 10-tree home wood south of the Pass keep (protected from thinning), a tai at ⅓ health breaks into a kumi (6 lost, 3 fight on), 45 s days, Night-early bonus (3 rice per second given up), daylight raids from day 3 (~every other day, 2–5 small yokai, war-drum warning 6 s ahead), heavier late waves (Valley N4–5, Pass N5–7).

| Chapter | Result | Length | Losses | Notes |
|---|---|---|---|---|
| Valley Keep | 3/3 win | 6.3–7.9 min | 1–16 | 1–3 raids; still the gentle chapter |
| Mountain Pass | 3/3 win | 9.8–10.6 min | 28–30 | losses climb N3→N7 (2–11 a night) instead of one late cliff; wood lasts to the end; 4–7 upgrades; 2–3 tai breaks |
