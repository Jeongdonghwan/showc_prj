"""글 JSON 검사 — 실패한 번호와 사유를 출력, 마지막 줄 OK=번호들

  python -I scripts/validate.py 1 2 3      (번호 생략 시 posts/ 전체)
"""
import json, os, re, sys, glob
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')
CORPUS = {str(json.loads(l)['logNo']): json.loads(l) for l in open(os.path.join(ROOT, 'data', 'corpus.jsonl'), encoding='utf-8')}
BAN = ['국내 유일', '최고의', '완벽', '100%', '무조건', '지금 바로', '놀라운', '혁신적', '한성쇼케이스여야', '만족도']
NEED = ['title', 'description', 'answer', 'intro', 'sections', 'case', 'spec', 'checklist', 'faq', 'tags']


def text_of(d):
    out = [d['title'], d['description'], d['answer']] + d['intro'] + d['checklist'] + d['tags']
    for s in d['sections']:
        out += [s['h']] + s['paras'] + s.get('ticks', [])
    out += [d['case']['h']] + d['case']['paras']
    for f in d['faq']:
        out += [f['q'], f['a']]
    return out


def sents(d):
    return {s.strip() for t in text_of(d) for s in re.split(r'(?<=[.?!])\s+', t) if len(s.strip()) > 25}


files = sorted(glob.glob(os.path.join(ROOT, 'posts', '*.json')), key=lambda f: int(os.path.basename(f)[:-5]))
ALL = {int(os.path.basename(f)[:-5]): json.load(open(f, encoding='utf-8')) for f in files}
want = [int(x) for x in sys.argv[1:]] or list(ALL)
SENT = Counter(s for d in ALL.values() for s in sents(d))
ok = []
for n in want:
    d = ALL.get(n); err = []
    if d is None:
        print(n, '파일 없음'); continue
    miss = [k for k in NEED if k not in d]
    if miss:
        print(n, '필드 없음', miss); continue
    body = ''.join(text_of(d)); L = len(re.sub(r'\s', '', body))
    if L < 1850: err.append(f'짧음 {L}자')
    if L > 3200: err.append(f'김 {L}자')
    if not 3 <= len(d['sections']) <= 5: err.append('섹션 수')
    if len(d['faq']) != 3: err.append('FAQ 3개 아님')
    if not d['kw'] or any(w not in d['title'].replace(' ', '') for w in d['kw'].split()): err.append('제목에 키워드 없음')
    for b in BAN:
        if b in body: err.append(f'금지 표현 "{b}"')
    if re.search(r'\d[\d,]*\s*(만\s*)?원(?![가-힣])', body): err.append('가격(원) 표기')
    if re.search(r'[\U0001F300-\U0001FAFF✅❌⭐]', body): err.append('이모지')
    src = CORPUS.get(str(d['case'].get('source')))
    if not src: err.append('사례 source 없음')
    else:
        stext = ' '.join(src['paras']) + ' ' + ' '.join(' '.join(' '.join(r) for r in t) for t in src['tables'])
        for row in d['spec']:
            for v in row[1:]:
                for num in re.findall(r'\d{3,4}', v):
                    if num not in stext: err.append(f'표 숫자 {num} 원문에 없음')
    dup = [s for s in sents(d) if SENT[s] > 1]
    if len(dup) > 2: err.append(f'다른 글과 같은 문장 {len(dup)}개')
    if err: print(n, ' / '.join(err))
    else: ok.append(n)
print(f'통과 {len(ok)}/{len(want)}')
print('OK=' + ','.join(map(str, ok)))
