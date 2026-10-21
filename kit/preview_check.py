"""Open build/<id>.html at phone size and confirm the page count and that nothing overflows sideways.

Usage:  python kit/preview_check.py <issue id> [expected pages, default 12; Sunday 13]
Optional last step of a run; needs Playwright and its Chromium (pre-installed in the scheduled environment).
"""
import os, sys
from playwright.sync_api import sync_playwright
import tptlib

iid, want = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 12
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium")) if os.path.exists("/opt/pw-browsers/chromium") else p.chromium.launch()
    pg = b.new_page(viewport={"width": 390, "height": 760})
    pg.goto("file://" + os.path.join(tptlib.ROOT, "build", iid + ".html"))
    pg.wait_for_timeout(2500)
    n = pg.evaluate("document.querySelectorAll('.page').length")
    over = pg.evaluate("document.documentElement.scrollWidth > innerWidth + 2")
    errs = []
    print(f"pages: {n} (expected {want}); horizontal overflow: {over}")
    b.close()
sys.exit(0 if n == want and not over else 1)
