#!/usr/bin/env bash
# 빌드 결과(site/)만 deploy 브랜치로 올린다. 서버는 deploy 브랜치를 받아 nginx로 서빙.
#   bash scripts/deploy.sh <공개 주차 1~20> <https://도메인 또는 http://IP:포트>
# 서버 갱신: cd /var/www/showcase && git fetch -q origin deploy && git reset -q --hard origin/deploy
set -euo pipefail
WEEK=${1:?공개 주차}; URL=${2:?주소}
cd "$(dirname "$0")/.."
[ "${SKIP_IMAGES:-}" = 1 ] || python -I scripts/images.py >/dev/null   # 새 글 사례 사진 받기(이미 받은 건 건너뜀). SKIP_IMAGES=1 이면 생략
OPEN_WEEK=$WEEK SITE_URL=$URL python -I build.py
grep -q "$URL" site/sitemap.xml || { echo "sitemap에 주소가 없음"; exit 1; }
REMOTE=$(git remote get-url origin)
TMP=$(mktemp -d); cp -r site/. "$TMP"/
cd "$TMP"
git init -q -b deploy && git add -A
git -c user.name="$(git -C "$OLDPWD" config user.name)" -c user.email="$(git -C "$OLDPWD" config user.email)" commit -q -m "deploy: ${WEEK}주차까지 $(date +%F)"
git push -q -f "$REMOTE" deploy
echo "deploy 브랜치 갱신: ${WEEK}주차까지, 글 $(ls blog | wc -l)편, $(du -sh . | cut -f1)"
cd / && rm -rf "$TMP"
