"""글에 배정된 사례 원문의 사진을 받아 웹용으로 줄인다 → site/img/c/<logNo>_<k>.jpg, data/images.json

  python -I scripts/images.py            (posts/ 에 있는 글의 사례만, 이미 받은 것은 건너뜀)
"""
import glob, io, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graphic_score import score as gscore
GRAPHIC = 2.5  # 이보다 높으면 글자 배너·안내 그래픽 → 제외

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'img', 'c'); os.makedirs(OUT, exist_ok=True)
CORPUS = {str(json.loads(l)['logNo']): json.loads(l) for l in open(os.path.join(ROOT, 'data', 'corpus.jsonl'), encoding='utf-8')}
IDX = os.path.join(ROOT, 'data', 'images.json')
index = json.load(open(IDX, encoding='utf-8')) if os.path.exists(IDX) else {}
MAX = 12
sys.stdout.reconfigure(encoding='utf-8')


def fetch(logNo):
    if logNo in index: return logNo, index[logNo]
    got = []
    for u in CORPUS[logNo]['imgs']:
        if len(got) >= MAX: break
        try:
            raw = urllib.request.urlopen(u, timeout=30).read()
            im = Image.open(io.BytesIO(raw)); im.seek(0); im = im.convert('RGB')
            w, h = im.size
            if min(w, h) < 240 or w / h > 2.6 or h / w > 2.6: continue  # 배너·띠 이미지 제외
            im.thumbnail((900, 900))
            fn = f'{logNo}_{len(got)}.jpg'
            im.save(os.path.join(OUT, fn), quality=76, optimize=True, progressive=True)
            if gscore(os.path.join(OUT, fn)) > GRAPHIC:
                os.remove(os.path.join(OUT, fn)); continue
            got.append([fn, im.size[0], im.size[1]])
            time.sleep(0.15)
        except Exception:
            continue
    return logNo, got


ASSIGN = json.load(open(os.path.join(ROOT, 'data', 'assign.json'), encoding='utf-8'))
cases = set()
for f in glob.glob(os.path.join(ROOT, 'posts', '*.json')):
    d = json.load(open(f, encoding='utf-8'))
    cases |= {str(d['case']['source'])} | {str(x) for x in ASSIGN[str(d['no'])]['refs']}
cases = sorted(cases)
with ThreadPoolExecutor(4) as ex:
    for lg, got in ex.map(fetch, cases):
        index[lg] = got
json.dump(index, open(IDX, 'w', encoding='utf-8'))
print('cases', len(cases), 'images', sum(len(v) for v in index.values()))
