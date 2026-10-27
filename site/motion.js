// 스크롤 등장 · 숫자 카운트 · 카테고리 탭 필터
document.documentElement.classList.add('js');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const io = new IntersectionObserver((es) => es.forEach((e) => {
  if (!e.isIntersecting) return;
  e.target.classList.add('in'); io.unobserve(e.target);
}), { threshold: 0, rootMargin: "0px 0px -8% 0px" });
document.querySelectorAll('[data-reveal], .reveal-group').forEach((el) => io.observe(el));

document.querySelectorAll('[data-count]').forEach((el) => {
  const end = +el.dataset.count;
  if (reduce) return;
  const t0 = performance.now();
  const tick = (t) => {
    const p = Math.min(1, (t - t0) / 1200);
    el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))).toLocaleString('ko-KR');
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
});

document.querySelectorAll('.tabs button').forEach((b) => b.addEventListener('click', () => {
  document.querySelectorAll('.tabs button').forEach((x) => x.classList.toggle('on', x === b));
  const f = b.dataset.f;
  document.querySelectorAll('.cards li').forEach((li) => li.classList.toggle('hide', !!f && li.dataset.cat !== f));
}));

// 모자이크 타일 → 해당 카테고리 탭 선택
document.querySelectorAll('[data-go]').forEach((a) => a.addEventListener('click', () => {
  const b = document.querySelector(`.tabs button[data-f="${a.dataset.go}"]`);
  if (b) b.click();
}));
