"""제목 그래픽(글자 배너) 판별 점수 — 평평한 배경 비율 × 날카로운 글자 경계 비율. 높을수록 그래픽."""
from PIL import Image


def score(path):
    im = Image.open(path).convert('L').resize((128, 128))
    px = im.load(); flat = sharp = 0
    for by in range(0, 128, 4):
        for bx in range(0, 128, 4):
            v = [px[bx + i, by + j] for i in range(4) for j in range(4)]
            r = max(v) - min(v)
            flat += r < 6; sharp += r > 110
    n = 32 * 32
    return (flat / n) * (sharp / n) * 100
