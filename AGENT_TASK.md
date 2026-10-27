# 작성 작업 지시 (한성쇼케이스 블로그)

작업 폴더: C:\side_Prj\showcase_blog_prj — 업소용 냉장 쇼케이스 맞춤 제작 회사의 블로그 글을 한국어로 쓴다.

## 시작 전에 한 번 읽기
1. WRITING_RULES.md — 작성 규칙 (반드시 지킨다)
2. posts/689.json, posts/1.json — 완성된 기준 예시 (구성·말투·분량을 이 수준으로)

## 번호마다 반복
1. 자료: `cd /c/side_Prj/showcase_blog_prj && python -I scripts/packet.py <번호> > data/_pk_<번호>.txt` 후 Read 도구로 읽기.
   키워드·각도·제품·카테고리·주차, 사례 원문(logNo), 참고 원문 2편이 나온다.
2. Write 도구로 posts/<번호>.json 저장 (UTF-8 JSON).
   필드: no(정수), week(정수), kw, cat, prod (packet 값 그대로), title, description, answer, intro[], sections[{h, paras[], ticks[]}],
   checklist[], case{h, paras[], source(사례 원문 logNo 정수)}, spec[[...]], faq[{q,a}]×3, tags[].
   - case·spec은 사례 원문의 실제 내용만. 팁 글이면 case.h는 "현장에서 자주 보는 경우: …". 사양 표가 없으면 spec은 [].
   - 키워드 각도에 실제로 쓸모 있는 내용. 같은 각도 다른 제품 글과 문장을 돌려쓰지 말고, 이 제품만의 특성(진열 상품·습도·문 방식·조명·동선)으로 쓴다.
   - 공백 제외 1,850~2,800자. 가격(원)·통계·출처 없는 숫자 금지.
3. 5편 쓸 때마다 검사: `python -I scripts/validate.py <그 번호들>` → 실패는 고쳐서 재검사(번호당 최대 3회).
4. 다 쓰면 맡은 번호 전체를 한 번 더 검사.

## 보고 (짧게)
통과 번호 수, 실패 번호와 사유, 자료가 이상했던 번호가 있으면 한 줄씩. 글 내용은 보고에 붙이지 않는다.
