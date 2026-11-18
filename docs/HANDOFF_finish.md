# Sengoku: art-direction finishing handoff

You're taking over the last stretch of the art direction for **Sengoku**, a phone-first isometric base-builder set in Sengoku-era Japan (about 1467–1615). The pitch: "Build by day. Hold the keep through the night." The direction is set and mostly built. Your job is to finish it so the game needs only final polish and sound files.

> **Update, 18 Nov: revised scope after your first report.**
> Your test browser can't run the game, so the work is now split:
> - **You (ChatGPT): Task 1, painting only.** No browser is needed. The guides and references are already exported in `docs/guides/` on the branch:
>   - `guide_{range,hideout,dojo}_2048.png`: the 2048×2048 camera guides, with labelled corners L, F, R and B.
>   - `guide_*_2048_clean.png`: the same guides without the legend.
>   - `style_reference_v2_buildings.png`: the approved v2 buildings, to match their style.
>   - `layout_reference_old_{range,hideout,dojo}.png`: the old art, to keep each building's layout and function.
>
>   The footprint diamond in every guide is exactly L(224, 1437), R(1824, 1437), B(1024, 975), F(1024, 1900); width 1600, height 925, ratio 0.578.
>
>   **Deliver** three transparent PNGs at 2048×2048, framed exactly like the guide, with the base corners on those four points. Commit them to `assets/style/v2/buildings/src/{range,hideout,dojo}_2048.png` on the branch, or attach them to your reply.
> - **Claude: Tasks 2–6, plus the Task 1 checks.** Claude will crop, wire and footprint-check your three buildings in the running game, measure their angles, and send back fixes if needed.
>
> You don't need to do Tasks 2–6 or run the game.

Read this whole brief before starting. Work in the order given. Where a step says STOP, stop and report.

---

## 1. Where the work lives

- **Repo:** `ZachGracia-Studio/sengoku-playtest` (public).
- **Branch:** `gemini/design-tests`. All your work goes here or on a branch created from it.
  - Never commit to, merge into or push `main`. GitHub Pages deploys the live game from `main`.
  - Open a pull request from your branch into `gemini/design-tests` (not into `main`), or push to `gemini/design-tests` directly if you have access. Either way, Zach merges to `main` himself.
- **Last known commits on the branch:**
  - `710e25d`: import of the earlier Gemini work
  - `cb66e53`: v2 construction, upgrade and damage states
- **The game:** one static file, `index.html` (about 4,700 lines, Canvas 2D), plus `assets/`. There's no build step. Serve the folder with any static server (for example `python3 -m http.server 8765`) and open `http://localhost:8765/index.html?...`.
- **Test URL for the new direction:** `index.html?r=2d&style=v2&test=board=c1`
  - Chapters to check: **First Light** (the tutorial) and **Test ground** (shows every building and unit at once).
  - `&test=footprint` draws each building's footprint diamond in red, to check camera alignment.
  - `&test=scale=1.3` overrides the unit scale.
  - `&house=1|2&keep=1|2` switch the house and tier-1 keep variants. The defaults are house 1 and keep 2.
- **Debug handle:** `window.__sengoku`, which exposes `S` (state), `cam`, `ASSETS`, `IMG`, `BUILDINGS`, `setRunning()`, and so on.

---

## 2. What's locked (don't change these)

- **Camera:** fixed orthographic, 45° azimuth, elevation `asin(37/64)` ≈ **35.3°**. Tiles are `TW = 64`, `TH = 37`, so the footprint diamond's height-to-width ratio is 0.578. No rotation and no perspective. Every building must sit on its tile diamond.
- **Characters:** the approved angular, lanky graphic-ink style (`assets/style/mj_*`). The yokai use `assets/style/raw_*`. The unit scale is **1.5×** under `style=v2` (`UNIT_SCALE_MULT`).
- **Rejected; don't reuse or imitate:**
  - the chunky `style_*` sprites
  - 3D box or Tripo models as final art
  - posterised 3D renders
  - soft generic watercolour
  - saturated "mobile game" colour
- **Board c1, the clarity model:** the Sengoku-era *Rakuchū rakugai-zu* folding screens.
  - A mid-tone **muted gold-ochre** ground (about `#AB956A`) with paper grain and broad, soft wash pools.
  - Brushed ochre roads.
  - Faint malachite-green field blocks.
  - Gold cloud bands (*suyari-gasumi*) with a thin ink outline, at the map edges only.
  - Ink tree groves whose light areas are tinted gold, never paper-white.
- **Value structure (the most important rule):**

  | Band | House scale (1 = black, 10 = white) | What goes in it |
  |---|---|---|
  | Light | 8–10 | Lit plaster walls and lit roof planes only; never the ground |
  | Middle | 4–6 | Ground, fields, water. The measured playfield median brightness is about 0.55–0.59 (0–1 scale), and must stay within 0.50–0.60. |
  | Dark | 1–3 | Ink: shadows, units, trees, roof undersides |

- **Palette:**

  | Colour | Hex | Use |
  |---|---|---|
  | Ink | `#1B1B1F` | Line, shadow, units, trees |
  | Plaster (gofun) | `#EFE8D8` | Lit walls; buildings only |
  | Ground gold | about `#AB956A` | The board |
  | Ochre | `#9C7F4A` | Earth, roads |
  | Malachite | `#6F8A5E` | Fields |
  | Azurite | `#4A6788` | Water |
  | Vermilion | `#C8372D` | The player's clan only (banners, one keep accent), plus UI seals. Never on terrain or enemies. |

- **Building look:**
  - white gofun plaster on the lit planes, dark tile, board or thatch roofs
  - a confident brush-ink contour whose weight matches the units at in-game scale
  - an ink contact shadow and earthen or stone base, so nothing floats
  - clean transparent edges: no paper rectangle, halo or fringe
- **Approved v2 buildings** (in `assets/style/v2/buildings/`): `house_v1`, `house_v2`, `keep1_v1`, `keep1_v2`, `keep2`, `keep3`, `kura`, `lumber`, `smith`, `tower`, `temple`, `stable`.
  - These are wired at about line 539 (`if (STYLE_V2) { … ASSETS[...] = { src: "assets/style/v2/buildings/…" } }`).
  - The v2 drawing path is `drawIsoBuildingV2()`, used for the types in `V2_ART`.
- **Player-facing text:** never mention AI anywhere a player can see it (in-game text, credits, store copy or code comments that ship).

---

## 3. What's left, in order

### Task 1: paint the last three buildings (the only real painting task)

These still use the old art (`assets/style/b_range.webp`, `b_hideout.webp`, `b_dojo.webp`), only cleaned up for the gold board. They break the family: the hideout reads as a pale cut-out with a heavy dark yard edge.

| Building | `BUILDINGS` key | Footprint | Old art | What it is |
|---|---|---|---|---|
| Archery range | `range` | 2×2 | `b_range.webp`, 503×422 | Covered shooting line (an earthen *azuchi* butt), straw targets, a light timber shelter. Already on the camera angle; keep its layout. |
| Shinobi hideout | `hideout` | 2×2 | `b_hideout.webp`, 486×408 | An unassuming farmhouse with a low fence. Thatch or board roof, small plaster walls; it must not look military. The current one is about +3.9° off the camera angle. |
| Drill yard | `dojo` | 2×2 | `b_dojo.webp`, 520×318 | An open training yard with a palisade and weapon racks, plus a small roofed hall. Keep the yard readable as open ground. About −2.7° off. |

**How to make each one:**
1. **Make the guide.** Open `tools/paintover.html` in a browser. It renders a 2048×2048 guide of the footprint slab at the exact game camera. Make the 2×2 guide.
2. **Paint over the guide.** Paint or generate the building over that guide so the footprint corners land exactly on the guide's diamond. Use the old art as a layout reference and the approved v2 buildings (especially `stable.webp`, `temple.webp` and `kura.webp`) as the **style** reference. Match their line weight, plaster white, dark roofs and ground contact.
   - If you generate images, use the guide as the control or reference image, and the v2 buildings as style references.
   - One finished image per building, at most **two attempts each**. If an attempt drifts off the camera angle or off-style, say so.
3. **Clean it up.** Background fully transparent, no paper box, no halo or fringe, no text, signature or watermark. Export a WebP of about 500 px width, framed like the other v2 files: footprint at the bottom, the front corner at the bottom centre.
4. **Save it** as `assets/style/v2/buildings/range.webp`, `hideout.webp` and `dojo.webp`.
5. **Wire it** in the `if (STYLE_V2)` block. Point `range_t1..t3`, `hideout_t1..t3` and `dojo_t1..t3` at the new files with `pivotX: 0.500, own: true`, exactly like the other v2 entries. Add `"range"`, `"hideout"` and `"dojo"` to `V2_ART` so they get the v2 construction, upgrade and damage states.
6. **Check alignment** with `?r=2d&style=v2&test=board=c1&test=footprint`. The footprint diamond must hug the building's base. If it doesn't, adjust only that asset's pivot or fit.
7. **Measure the angle.** Find the base corners L, F, R and B, measure the diamond's width (L to R) and height (B to F), then elevation = **asin(height ÷ width)**. The target ratio is 0.578, which gives 35.3°. Pass is within **±1.5° of 35.3°**, which means a ratio between about 0.556 and 0.600.

**Done when:** in the Test ground, all buildings read as one family, and the three new ones pass the footprint check and the angle measurement.

### Task 2: make character crowds readable (code only)

At 1.5×, groups of black-ink units bunch into a single dark mass where they overlap each other and the buildings.

**Fix it with value and shape separation, not blur:**
- **Separate the figures.** Draw a thin ink-dark rim, plus a very subtle gold-paper inner rim of 1–1.5 px at about 25–35% opacity, only where a unit overlaps another unit or a building. A cheap approach: draw each unit's silhouette dilated by about 1.5 px in the ground colour just before the unit itself (a "cut-out" separation). See the existing `cleanUnitPaperForGold()` and `getInkRimImg()` helpers.
- **Lighten up spacing.** If the formation code allows it, make the idle and rally spacing slightly wider (about +10–15%), without changing combat balance. Don't touch unit stats.
- **Keep the existing contact shadows.** They should stay the soft ink pool under the feet.

**Done when:** in a 375×812 Test ground screenshot, every unit in the central group can be told apart, and there are no white sticker halos.

### Task 3: fix the night HUD overflow on phone

At 375×812 at night, the top-right phase pill (`#phaseBtn`: icon, "NIGHT 1/99", season icon, `#phaseT`) runs off the right edge. It shows most in the Test ground, which allows 99 nights.

**Fix it:**
- Below 420 px width, shorten it to a compact form (for example "N1/99", or drop `#phaseT` and the season icon).
- Or reduce the font size, so the whole pill fits and clears the pause button.

Check it at 375 and 414 px wide, day and night.

### Task 4: make the new look work without test flags (code only)

Right now the gold board only appears with `&test=board=c1`.

**Change it:**
- Make `style=v2` imply board c1 (`IS_BOARD_C` true whenever `STYLE_V2` is on, unless `test=board=` explicitly asks for another board). Then the whole new direction is one flag: `?style=v2`.
- **Don't make `style=v2` the global default yet, and don't change `USE3D`.** Note the renderer default: on this branch the game opens in 2D (`USE3D = /[?&]r=3d/`), while `main` opens in 3D. That decision is Zach's; just list it in your report.

### Task 5: list the sound hooks (no audio files)

Sound files will be added later by hand. Find where the code already plays sounds, or has a natural spot for one:
- build start and complete
- upgrade
- recruit
- unit select and command
- melee hit, arrow, death
- building damaged and destroyed
- night falls, dawn
- wave start
- victory and defeat
- UI tap

For each, report:
- the function or line
- whether a hook already exists
- a suggested file name (for example `sfx_build_complete.ogg`)

The game currently has no audio code at all (no `Audio` or `AudioContext`), so add a tiny no-op `sfx(name)` stub and call it at those points, so dropping files in later needs no code changes. **No audio content.**

### Task 6: final audit, then STOP

1. **Playthrough check:** First Light (tutorial) and Test ground, at 375×812 and 1280×800, day and night, including a building under construction, one upgrading and one badly damaged (use `window.__sengoku.S.buildings` to set `progress`, `upg` and `hp`).
2. **Value study:** a grayscale version reduced to five value bands, beside the Civilization VI reference look. Report the measured playfield median brightness. It must stay within 0.50–0.60.
3. **Consistency sheet:** every building (all tiers) and every unit type at in-game scale on the gold ground, in one image.
4. **Performance:** report load time and rough frame rate on a mid-range phone, or under 4× CPU throttling in browser devtools. Flag anything new that's slow; for example, the per-building canvas filters for the burnt state are cached in `CHAR_IMG`, but check it.
5. **Diff hygiene:** no unrelated behaviour changes; one commit per task with a clear message.

---

## 4. Rules of the road

- **Branch:** only `gemini/design-tests`, or your own branch created from it. Never `main`.
- **Commits:** one per task, in the order above. Don't rewrite history. Never delete `.git`.
- **Test before reporting.** Serve the game locally and actually look at it. Don't report a change you haven't seen running.
- **Be honest.** If something didn't work, or is only partly done, say so plainly with a screenshot. Never invent file names, commit hashes, line numbers or results.
- **Respect the style.** Get clarity from value, shape contrast and grouping. Don't reach for blur, softening or extra detail.
- **Budget:** at most 8 image generations in total (Task 1 only). Report how many you used.

---

## 5. Deliverables (report in this format, then STOP)

1. **Summary:** one paragraph on what changed and what's left.
2. **Commits:** a list of each commit hash and message on the branch, plus the PR link if you opened one.
3. **Task 1:** for each of the three buildings:
   - the final art, a 100% in-game crop beside a unit, and the footprint-check screenshot
   - the measured angle
   - how it was made: tool, guide and references used
4. **Task 2:** before and after of the Test ground centre group at 375×812.
5. **Task 3:** before and after of the night HUD at 375 and 414 px wide.
6. **Task 4:** confirmation that `?style=v2` alone shows the full new direction.
7. **Task 5:** the sound-hook table.
8. **Task 6:** the audit images, the measured median, the performance numbers, and anything you'd still flag.
9. **Open decisions for Zach:**
   - the default renderer (2D or 3D)
   - when to make `style=v2` the default
   - the merge to `main`

Then STOP and wait. Don't merge anything to `main`.
