"""한성쇼케이스 블로그 — 랜딩 + 글 1,000편(posts/*.json)을 정적 페이지로 만든다. 주차별 순차 오픈.

  OPEN_WEEK=1 python -I build.py    →  site/index.html, site/blog/<슬러그>.html, site/sitemap.xml
  (OPEN_WEEK 주차까지만 페이지·목록·사이트맵에 넣는다. 열리지 않은 글은 파일 자체를 만들지 않는다)
"""
import glob, html, json, os, re, shutil
from urllib.parse import quote
from email.utils import format_datetime
from datetime import datetime, timezone
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')
DOMAIN = os.environ.get('SITE_URL', 'https://hansungshowcase.example')  # TODO: 실제 도메인
OPEN_WEEK = int(os.environ.get('OPEN_WEEK', '1'))
START = date(2026, 11, 2)  # 1주차 월요일 — TODO: 실제 오픈일
PHONE = '031-986-2458'
e = html.escape

def _load(f):
    try: return json.load(open(f, encoding='utf-8'))
    except ValueError: return None  # 작성 중인 파일


POSTS = sorted((d for d in map(_load, glob.glob(os.path.join(ROOT, 'posts', '*.json'))) if d), key=lambda d: d['no'])
IMG = json.load(open(os.path.join(ROOT, 'data', 'images.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'data', 'images.json')) else {}
ASSIGN = json.load(open(os.path.join(ROOT, 'data', 'assign.json'), encoding='utf-8'))
LANDING_IMGS = {im['n']: im for im in json.load(open(os.path.join(ROOT, 'images.json'), encoding='utf-8'))}
slug = lambda d: re.sub(r'[^0-9A-Za-z가-힣]+', '-', d['kw']).strip('-')
for d in POSTS:
    d['slug'] = slug(d)
    d['date'] = (START + timedelta(days=(d['week'] - 1) * 7 + (d['no'] % 5))).isoformat()
    d['imgs'] = IMG.get(str(d['case']['source']), []) + [i for r in ASSIGN.get(str(d['no']), {}).get('refs', []) for i in IMG.get(str(r), [])[:4]]
# 사진이 6장 미만이면 같은 카테고리 다른 글 사진으로 채운다(번호로 고정 선택)
POOL = {}
for d in POSTS:
    POOL.setdefault(d['cat'], []).extend(x for x in d['imgs'] if x not in POOL.get(d['cat'], []))
for d in POSTS:
    if len(d['imgs']) < 6:
        pool = [x for x in POOL.get(d['cat'], []) if x not in d['imgs']] or [x for v in POOL.values() for x in v if x not in d['imgs']]
        k = d['no'] % max(len(pool), 1)
        d['imgs'] = d['imgs'] + (pool[k:] + pool[:k])[:8 - len(d['imgs'])]
import sys as _s; _s.path.insert(0, os.path.join(ROOT, 'scripts'))
from graphic_score import score as _g
_GC = {}
def _gs(fn):
    if fn not in _GC: _GC[fn] = _g(os.path.join(SITE, 'img', 'c', fn))
    return _GC[fn]
OPEN = [d for d in POSTS if d['week'] <= OPEN_WEEK and d['imgs']]
for d in OPEN:  # 대표 사진: 앞쪽 5장 중 그래픽 점수가 가장 낮은 것
    k = min(range(min(5, len(d['imgs']))), key=lambda i: _gs(d['imgs'][i][0]))
    d['imgs'] = [d['imgs'][k]] + d['imgs'][:k] + d['imgs'][k + 1:]
OPEN_SET = {d['no'] for d in OPEN}


def head(title, desc, canon, pre, extra='', img=''):
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{DOMAIN}{canon}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="{'article' if pre else 'website'}">
<meta property="og:url" content="{DOMAIN}{canon}"><meta property="og:site_name" content="한성쇼케이스"><meta property="og:locale" content="ko_KR">
<meta property="og:image" content="{DOMAIN}/{img}"><meta property="og:image:alt" content="{e(title)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{DOMAIN}/{img}">
<link rel="alternate" type="application/rss+xml" title="한성쇼케이스 블로그" href="{DOMAIN}/rss.xml">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="{pre}style.css">{extra}</head><body>
<header class="top"><div class="wrap top-in"><a class="logo" href="{pre}index.html"><b>한성쇼케이스</b><small>HANSUNG SHOWCASE</small></a>
<nav><a href="{pre}index.html#blog">블로그</a><a href="{pre}index.html#cases">제품별</a><a class="call" href="tel:0319862458">{PHONE}</a></nav></div></header>'''


def foot(pre):
    return f'''<footer class="foot"><div class="wrap foot-in"><div><b>한성쇼케이스</b><p>업소용 냉장·냉동 쇼케이스 맞춤 제작</p></div>
<ul><li><span>대표전화</span>{PHONE}</li><li><span>A/S</span>전국 240여 개 전담 센터</li><li><span>사업자</span>추후 입력</li></ul></div></footer>
<a class="sticky" href="tel:0319862458">전화 상담 {PHONE}</a><script src="{pre}motion.js"></script></body></html>'''


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


WHY = '''<section class="why-box" data-reveal><h2>매장 조건에 맞춰 만드는 한성쇼케이스</h2>
<p>원하시는 제품 사진과 설치할 공간 사진만 보내 주셔도 매장에 맞는 구성을 추천해 드립니다.</p>
<ul class="ticks strong"><li>전국 240여 개 A/S 전담 센터 운영</li><li>본사 대량 자재 매입으로 품질 대비 합리적인 가격</li><li>유럽제·삼성 냉각 콤프레셔 적용</li><li>국내 최초 쇼케이스 전문 디자이너 상주</li></ul></section>'''


def render_post(d):
    im = d['imgs']; pre = '../'
    src = lambda k: f"{pre}img/c/{im[k % len(im)][0]}"
    rel = [x for x in OPEN if x['no'] != d['no'] and (x['cat'] == d['cat'] or x['prod'] == d['prod'])]
    rel = (rel + [x for x in OPEN if x['no'] != d['no'] and x not in rel])[:3]
    secs = []
    for i, s in enumerate(d['sections'], 1):
        b = f'<h2 id="s{i}">{i}. {e(s["h"])}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in s['paras'])
        if s.get('ticks'): b += '<ul class="ticks">' + ''.join(f'<li>{e(t)}</li>' for t in s['ticks']) + '</ul>'
        if i == 2 and len(im) >= 3: b += f'<div class="pair" data-reveal><img src="{src(1)}" alt="{e(d["prod"])} 제작 사례" loading="lazy"><img src="{src(2)}" alt="{e(d["prod"])} 설치 모습" loading="lazy"></div>'
        secs.append(b)
    spec = ''
    if d['spec']:
        hd, *rows = d['spec']
        spec = '<div class="spec" data-reveal><table><thead><tr>' + ''.join(f'<th>{e(c)}</th>' for c in hd) + '</tr></thead><tbody>' + \
               ''.join('<tr><th>' + e(r[0]) + '</th>' + ''.join(f'<td>{e(c)}</td>' for c in r[1:]) + '</tr>' for r in rows) + '</tbody></table></div>'
    gallery = ''.join(f'<img src="{src(k)}" alt="{e(d["prod"])} 출고 사진 {k - 3}" loading="lazy">' for k in range(4, min(len(im), 13)))
    case = f'''<h2 id="case">{e(d['case']['h'])}</h2>''' + ''.join(f'<p>{e(p)}</p>' for p in d['case']['paras']) + \
        (f'<figure class="fig" data-reveal><img src="{src(3)}" alt="{e(d["case"]["h"])}" loading="lazy"></figure>' if len(im) > 3 else '') + \
        (f'<div class="gallery reveal-group">{gallery}</div>' if gallery else '') + spec
    faq = ''.join(f'<details class="qa"><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in d['faq'])
    toc = ''.join(f'<li><a href="#s{i}">{e(s["h"])}</a></li>' for i, s in enumerate(d['sections'], 1)) + '<li><a href="#case">사례</a></li><li><a href="#faq">자주 묻는 질문</a></li>'
    url = f'/blog/{quote(d["slug"])}.html'
    lds = ld({'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': d['title'], 'description': d['description'], 'datePublished': d['date'],
              'image': f'{DOMAIN}/img/c/{im[0][0]}', 'author': {'@type': 'Organization', 'name': '한성쇼케이스'}, 'mainEntityOfPage': f'{DOMAIN}{url}'}) + \
        ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in d['faq']]}) + \
        ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': '블로그', 'item': f'{DOMAIN}/'},
            {'@type': 'ListItem', 'position': 2, 'name': d['cat'], 'item': f'{DOMAIN}/#blog'}, {'@type': 'ListItem', 'position': 3, 'name': d['title'], 'item': f'{DOMAIN}{url}'}]})
    if rel:
        lds += ld({'@context': 'https://schema.org', '@type': 'ItemList', 'name': '함께 보면 좋은 글', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': f"{DOMAIN}/blog/{quote(x['slug'])}.html", 'name': x['title']} for i, x in enumerate(rel)]})
    body = f'''<main class="article"><div class="wrap art-grid"><article>
<nav class="crumbs"><a href="{pre}index.html#blog">블로그</a><span>/</span><a href="{pre}index.html#blog">{e(d['cat'])}</a></nav>
<p class="label dark">{e(d['cat'])}</p><h1 class="art-title">{e(d['title'])}</h1>
<p class="meta">한성쇼케이스 · {d['date'].replace('-', '.')}</p>
<figure class="cover"><img src="{src(0)}" alt="{e(d['kw'])} — 한성쇼케이스 제작 사례"></figure>
<div class="answer" data-reveal><b>먼저 답부터</b><p>{e(d['answer'])}</p></div>
{''.join(f'<p>{e(p)}</p>' for p in d['intro'])}
{''.join(secs)}
<div class="check" data-reveal><h3>체크리스트</h3><ol>{''.join(f'<li>{e(c)}</li>' for c in d['checklist'])}</ol></div>
{case}
<h2 id="faq">자주 묻는 질문</h2>{faq}
{WHY}
<div class="cta" data-reveal><p>매장 폭과 원하는 진열 구성을 알려 주세요. 실측과 견적을 안내해 드립니다.</p><a class="btn" href="tel:0319862458">{PHONE}</a></div>
{('<section class="related"><h3>함께 보면 좋은 글</h3><ul>' + ''.join(f'<li><a href="{x["slug"]}.html">{e(x["title"])}</a></li>' for x in rel) + '</ul></section>') if rel else ''}
<p class="tags">{' · '.join(e(t) for t in d['tags'])}</p>
</article><aside class="toc"><div class="toc-in"><b>목차</b><ol>{toc}</ol><a class="btn small" href="tel:0319862458">{PHONE}</a></div></aside></div></main>'''
    return head(f'{d["title"]} | 한성쇼케이스', d['description'], url, pre, lds, f'img/c/{im[0][0]}') + body + foot(pre)


def render_index():
    cats = list(dict.fromkeys(d['cat'] for d in OPEN))
    cards = ''.join(f'''<li class="card{' feature' if i == 0 else ''}" data-cat="{e(d['cat'])}"><a href="blog/{d['slug']}.html">
<figure><img src="img/c/{d['imgs'][0][0]}" alt="{e(d['kw'])} — 한성쇼케이스 제작 사례" loading="{'eager' if i < 4 else 'lazy'}" width="{d['imgs'][0][1]}" height="{d['imgs'][0][2]}"></figure>
<div class="card-body"><span class="cat">{e(d['cat'])}</span><strong>{e(d['title'])}</strong><em>{e(d['description'][:60])}…</em><span class="more">읽기</span></div></a></li>''' for i, d in enumerate(sorted(OPEN, key=lambda d: (-d['week'], d['no']))))
    tabs = '<button class="on" data-f="">전체</button>' + ''.join(f'<button data-f="{e(c)}">{e(c)}</button>' for c in cats)
    L = LANDING_IMGS
    pick = {'꽃냉장고': 31, '정육쇼케이스': 12, '제과쇼케이스': 0, '와인(음료)쇼케이스': 4, '반찬(진열)쇼케이스': 7, '오픈쇼케이스': 14}
    names = [('꽃냉장고', '꽃냉장고', '생화 온도·습도에 맞춘 꽃 쇼케이스'), ('정육쇼케이스', '정육쇼케이스', '정육 평대·숙성고·고기 진열'),
             ('제과쇼케이스', '제과쇼케이스', '베이커리·카페 디저트 진열'), ('와인(음료)쇼케이스', '음료·와인', '음료·주류·와인셀러'),
             ('반찬(진열)쇼케이스', '반찬쇼케이스', '반찬가게 진열 냉장'), ('오픈쇼케이스', '오픈쇼케이스', '다단·평대 오픈형')]
    mosaic = ''.join(f'''<a class="tile" href="#blog" data-go="{e(c)}"><img src="img/{L[pick[c]]['file']}" alt="{e(n)} 제작 사례" loading="lazy"><span><b>{e(n)}</b><small>{e(t)}</small></span></a>''' for c, n, t in names if pick[c] in L)
    body = f'''<main>
<section class="hero photo"><img class="hero-bg" src="img/{L[26]['file']}" alt="한성쇼케이스 냉장 쇼케이스 출고 현장"><div class="wrap hero-in">
<p class="label">HANSUNG SHOWCASE</p><h1>매장에 맞춰 만드는<br><span>업소용 쇼케이스</span></h1>
<p class="lead">꽃냉장고·정육·제과·음료 쇼케이스를 매장 폭과 진열 방식에 맞춰 제작합니다. 실측부터 설치, A/S까지.</p>
<div class="actions"><a class="btn ice" href="tel:0319862458">{PHONE}</a><a class="link" href="#blog">쇼케이스 가이드 보기</a></div></div></section>
<section class="why"><div class="wrap"><ol class="why-list reveal-group">
<li><b>01</b><strong>전국 240여 개 A/S 전담 센터</strong><p>설치한 뒤에도 가까운 센터에서 점검과 수리를 받습니다.</p></li>
<li><b>02</b><strong>쇼케이스 전문 디자이너 상주</strong><p>매장 인테리어와 동선에 맞춰 도면부터 그립니다.</p></li>
<li><b>03</b><strong>본사 대량 자재 매입</strong><p>자재를 본사에서 직접 들여 품질 대비 가격을 맞춥니다.</p></li>
<li><b>04</b><strong>유럽제·삼성 냉각 콤프</strong><p>쇼케이스 수명을 정하는 콤프레셔부터 고릅니다.</p></li></ol></div></section>
<div class="wrap"><section class="sec" id="cases"><header class="sh" data-reveal><span>01</span><h2>제품별 제작 사례</h2></header><div class="mosaic reveal-group">{mosaic}</div></section>
<section class="sec" id="blog"><header class="sh" data-reveal><span>02</span><h2>쇼케이스 가이드</h2></header><div class="tabs" role="tablist">{tabs}</div>
<ul class="cards reveal-group">{cards}</ul></section></div>
<section class="band" data-reveal><div class="wrap band-in"><p>매장 실측과 도면은 <em>무료 상담</em>으로 먼저 받아 보세요.</p><a class="btn" href="tel:0319862458">{PHONE}</a></div></section></main>'''
    ilist = ld({'@context': 'https://schema.org', '@type': 'ItemList', 'name': '쇼케이스 가이드', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'url': f"{DOMAIN}/blog/{quote(d['slug'])}.html", 'name': d['title']} for i, d in enumerate(sorted(OPEN, key=lambda d: (-d['week'], d['no']))[:30])]})
    org = ld({'@context': 'https://schema.org', '@type': 'Organization', 'name': '한성쇼케이스', 'url': f'{DOMAIN}/', 'telephone': PHONE, 'sameAs': ['https://blog.naver.com/hansung_01']})
    return head('한성쇼케이스 | 업소용 쇼케이스 맞춤 제작·가이드', '꽃냉장고·정육·제과·음료 쇼케이스 맞춤 제작. 가격, 중고, 온도, 전기세, A/S 가이드.', '/', '', ilist + org, f"img/{L[26]['file']}") + body + foot('')


if __name__ == '__main__':
    blog = os.path.join(SITE, 'blog')
    shutil.rmtree(blog, ignore_errors=True); os.makedirs(blog)
    for d in OPEN:
        open(os.path.join(blog, f'{d["slug"]}.html'), 'w', encoding='utf-8').write(render_post(d))
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(render_index())
    urls = [f'{DOMAIN}/'] + [f'{DOMAIN}/blog/{quote(d["slug"])}.html' for d in OPEN]
    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    items = ''.join(f'''<item><title>{e(d['title'])}</title><link>{DOMAIN}/blog/{quote(d['slug'])}.html</link><guid isPermaLink="true">{DOMAIN}/blog/{quote(d['slug'])}.html</guid><description>{e(d['description'])}</description><category>{e(d['cat'])}</category><pubDate>{format_datetime(datetime.fromisoformat(d['date']).replace(hour=9, tzinfo=timezone.utc))}</pubDate></item>''' for d in sorted(OPEN, key=lambda d: d['date'], reverse=True)[:100])
    open(os.path.join(SITE, 'rss.xml'), 'w', encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>한성쇼케이스 블로그</title><link>{DOMAIN}/</link><description>업소용 쇼케이스 가격·중고·온도·전기세·A/S 가이드</description><language>ko</language>{items}</channel></rss>')
    for old in ('post.html',):  # 예전 시안 페이지 제거
        if os.path.exists(os.path.join(SITE, old)): os.remove(os.path.join(SITE, old))
    open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    print(f'글 {len(POSTS)}편 중 {OPEN_WEEK}주차까지 공개 {len(OPEN)}편')
