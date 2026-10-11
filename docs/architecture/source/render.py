import pathlib, json
from playwright.sync_api import sync_playwright
d = pathlib.Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 900}, device_scale_factor=2)
    pg.goto((d / 'architecture.html').resolve().as_uri()); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(1500)
    print(json.dumps(pg.evaluate("""()=>[...document.querySelectorAll('.bx')].filter(e=>e.scrollHeight>e.clientHeight+1||e.scrollWidth>e.clientWidth+1).map(e=>e.textContent.slice(0,20)+' '+(e.scrollHeight-e.clientHeight))"""), ensure_ascii=False))
    pg.locator('.pg').screenshot(path=str(d / 'architecture.png'))
    pg.pdf(path=str(d / 'architecture.pdf'), width='1600px', height='900px', print_background=True, page_ranges='1')
    b.close()
