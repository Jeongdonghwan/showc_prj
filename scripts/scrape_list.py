"""한성쇼케이스 네이버 블로그 전체 글 목록 — Playwright로 모바일 블로그를 띄우고 페이지 안에서 목록 API를 호출한다.

  python -I scripts/scrape_list.py  →  data/posts_list.json
"""
import json, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = 'hansung_01'
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto(f'https://m.blog.naver.com/{BLOG}', wait_until='networkidle')
    items, n = [], 1
    while True:
        r = page.evaluate("""async (u) => { const res = await fetch(u, {credentials: 'include'}); return await res.json(); }""",
                          f'/api/blogs/{BLOG}/post-list?categoryNo=0&itemCount=30&page={n}')
        got = (r.get('result') or {}).get('items') or []
        if not got:
            break
        items += got
        n += 1
    b.close()

keep = [{k: it.get(k) for k in ('logNo', 'titleWithInspectMessage', 'categoryName', 'addDate', 'thumbnailUrl', 'briefContents')} for it in items]
json.dump(keep, open(os.path.join(ROOT, 'data', 'posts_list.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('posts', len(keep), 'pages', n - 1)
