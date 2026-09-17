"""
Scrape nisa.peachworlds.com with Playwright — capture full-page screenshots
at multiple scroll positions so we can extract the exact visual design.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("scripts/nisa_screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://nisa.peachworlds.com/"


async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        print(f"Navigating to {URL} ...")
        await page.goto(URL, wait_until="networkidle", timeout=60_000)

        # Wait extra for JS animations / 3D blob to load
        await page.wait_for_timeout(4000)

        # ── Full page screenshot first ──────────────────────────
        full_path = OUTPUT_DIR / "00_full_page.png"
        await page.screenshot(path=str(full_path), full_page=True)
        print(f"Saved: {full_path}")

        # ── Get total scroll height ─────────────────────────────
        total_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = 900
        print(f"Total scroll height: {total_height}px")

        # ── Screenshot at each section ──────────────────────────
        num_sections = 8
        scroll_step = total_height // num_sections

        for i in range(num_sections + 1):
            scroll_y = min(i * scroll_step, total_height - viewport_height)
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await page.wait_for_timeout(800)  # let animations settle
            section_path = OUTPUT_DIR / f"{i+1:02d}_section_y{scroll_y}.png"
            await page.screenshot(path=str(section_path))
            print(f"Saved: {section_path}  (scrollY={scroll_y})")

        # ── Also grab computed CSS variables / colors ───────────
        colors = await page.evaluate("""() => {
            const style = getComputedStyle(document.documentElement);
            const body  = getComputedStyle(document.body);
            const allEls = [...document.querySelectorAll('*')];
            const unique_bg = new Set();
            const unique_fg = new Set();
            allEls.forEach(el => {
                const s = getComputedStyle(el);
                unique_bg.add(s.backgroundColor);
                unique_fg.add(s.color);
            });
            return {
                body_bg: body.backgroundColor,
                body_color: body.color,
                body_font: body.fontFamily,
                unique_backgrounds: [...unique_bg].filter(c => c && c !== 'rgba(0, 0, 0, 0)').slice(0, 20),
                unique_foregrounds: [...unique_fg].filter(c => c && c !== 'rgba(0, 0, 0, 0)').slice(0, 20),
            };
        }""")
        print("\n── Extracted colors / fonts ──────────────────")
        import json
        print(json.dumps(colors, indent=2))

        # ── Grab all font-face declarations from stylesheets ────
        fonts = await page.evaluate("""() => {
            const fonts = [];
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.type === CSSRule.FONT_FACE_RULE) {
                            fonts.push(rule.cssText.substring(0, 200));
                        }
                    }
                } catch(e) {}
            }
            return fonts;
        }""")
        print("\n── Font faces found ──────────────────────────")
        for f in fonts[:15]:
            print(f)

        await browser.close()
        print(f"\nAll screenshots saved to: {OUTPUT_DIR.resolve()}")


asyncio.run(scrape())
