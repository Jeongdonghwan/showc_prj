"""블로그 글 본문·표·사진 주소 수집 → data/corpus.jsonl (이어받기 가능)

  python -I scripts/scrape_posts.py
"""
import html, json, os, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = 'hansung_01'
OUT = os.path.join(ROOT, 'data', 'corpus.jsonl')
posts = json.load(open(os.path.join(ROOT, 'data', 'posts_list.json'), encoding='utf-8'))
done = set()
if os.path.exists(OUT):
    done = {json.loads(l)['logNo'] for l in open(OUT, encoding='utf-8')}
SKIP_IMG = re.compile(r'%EB%A1%9C%EA%B3%A0|%EB%A1%9C%EA%B7%B8|/00\d\.png|banner|%EB%B0%B0%EB%84%88', re.I)
txt = lambda s: html.unescape(re.sub(r'<[^>]+>', '', s)).replace('​', '').strip()


def parse(logNo):
    u = f'https://m.blog.naver.com/PostView.naver?blogId={BLOG}&logNo={logNo}'
    t = urllib.request.urlopen(u, timeout=30).read().decode('utf-8', 'replace')
    paras = [x for x in (txt(p) for p in re.findall(r'<p class="se-text-paragraph[^>]*>(.*?)</p>', t, re.S)) if x]
    heads = [txt(h) for h in re.findall(r'class="se-module se-module-text se-title-text[^"]*".*?</div>', t, re.S)]
    tables = []
    for tb in re.findall(r'<table class="se-table-content.*?</table>', t, re.S):
        rows = [[txt(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)] for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', tb, re.S)]
        tables.append([r for r in rows if any(r)])
    imgs = [i.replace('type=w400', 'type=w800').replace('type=w80_blur', 'type=w800') for i in re.findall(r'data-lazy-src="([^"]+)"', t)]
    imgs = [i for i in dict.fromkeys(imgs) if not SKIP_IMG.search(i)]
    return dict(logNo=logNo, paras=paras, tables=tables, imgs=imgs)


def job(p):
    for k in range(3):
        try:
            r = parse(p['logNo'])
            r.update(title=txt(p['titleWithInspectMessage'] or ''), cat=(p['categoryName'] or '').replace('\xa0', ' '), date=p['addDate'])
            time.sleep(0.4)
            return r
        except Exception as e:
            time.sleep(2 + k * 3)
    return None


todo = [p for p in posts if str(p['logNo']) not in {str(d) for d in done}]
with open(OUT, 'a', encoding='utf-8') as f, ThreadPoolExecutor(3) as ex:
    for r in ex.map(job, todo):
        if r:
            f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
n = sum(1 for _ in open(OUT, encoding='utf-8'))
print('corpus', n, '/', len(posts))
