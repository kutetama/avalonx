#!/usr/bin/env python3
"""사이트에 실제로 쓰인 글자만 남긴 웹 서체를 만든다.

왜: 한글 웹폰트 CDN 분할본은 페이지마다 600KB 이상을 받는다. 사이트 글자는
수백 자뿐이라, 쓰인 글자만 남기면 서체 전체가 약 200KB 이하로 줄어든다.

쓰는 법
  pip install fonttools brotli
  python3 tools/subset-fonts.py --src <원본 서체 폴더>   # 서체 재생성
  python3 tools/subset-fonts.py --check                  # 빠진 글자 검사 (배포 전)

원본 서체 폴더에는 다음 파일이 있어야 한다(AvalonX 브랜드 시스템 fonts/):
  PretendardVariable.woff2, WantedSans-Bold.woff2, WantedSans-ExtraBold.woff2, Galmuri11.woff2

HTML·JS의 문구를 바꾼 뒤에는 이 스크립트를 다시 돌린다. 안 돌리면 새 글자만
시스템 서체(맑은 고딕 등)로 보인다. --check가 그 상태를 잡아낸다.

라이선스: 세 서체 모두 SIL OFL 1.1. Pretendard는 예약 서체명(RFN)이 있어,
서브셋(수정본)의 내부 이름을 AX Sans 등으로 바꾼다. 원 저작권 표기는 유지한다.
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts"

# (원본 파일, 출력 파일, 새 서체명, 굵기 이름)
FONTS = [
    ("PretendardVariable.woff2", "ax-sans.woff2", "AX Sans", "Regular"),
    ("WantedSans-Bold.woff2", "ax-heading-700.woff2", "AX Heading", "Bold"),
    ("WantedSans-ExtraBold.woff2", "ax-heading-800.woff2", "AX Heading", "ExtraBold"),
]
# 갈무리는 짧은 라벨 전용이라 고정 글자만 넣는다 (사이트 전체 글자를 넣지 않음)
PIXEL = ("Galmuri11.woff2", "ax-pixel.woff2", "AX Pixel", "Regular")
PIXEL_TEXT = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ ▶·:-!?"

# 문구가 바뀌어도 항상 있어야 하는 글자: 기본 라틴, 문장부호, 화살표 등
BASE_TEXT = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + " ©·×—–‘’“”…→←↑↓•※"
)


class TextCollector(HTMLParser):
    """화면에 그려지는 글자만 모은다 (script·style 내용 제외, alt·placeholder 포함)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        for name, value in attrs:
            if name in ("alt", "placeholder", "value", "data-label") and value:
                self.chunks.append(value)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.chunks.append(data)


def site_text() -> str:
    parts = [BASE_TEXT]
    for html in ROOT.glob("*.html"):
        c = TextCollector()
        c.feed(html.read_text(encoding="utf-8"))
        parts.extend(c.chunks)
    # JS가 화면에 넣는 문구(복사 완료 안내 등)
    for js in (ROOT / "js").glob("*.js"):
        parts.extend(re.findall(r"'([^'\n]*)'", js.read_text(encoding="utf-8")))
    # CSS content: 속성 문자열
    for css in (ROOT / "css").glob("*.css"):
        parts.extend(re.findall(r'content:\s*"([^"]*)"', css.read_text(encoding="utf-8")))
    return "".join(sorted({ch for ch in "".join(parts) if ch.isprintable() or ch == " "}))


def rename(font: TTFont, family: str, style: str) -> None:
    """RFN 때문에 수정본의 서체명을 바꾼다. 저작권(0)·라이선스(13,14)는 그대로 둔다."""
    full = f"{family} {style}".strip()
    ps = full.replace(" ", "-")
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            name.removeNames(nameID=rec.nameID)
    for nid, val in ((1, family), (2, "Regular" if style == "Regular" else "Bold"), (3, f"{ps};subset"), (4, full), (6, ps), (16, family), (17, style)):
        name.setName(val, nid, 3, 1, 0x409)
    name.setName(
        "Subset of the original font for avalonx.kr. Original copyright and SIL OFL 1.1 retained.",
        5, 3, 1, 0x409,
    )


def make(src_dir: Path, src: str, out: str, family: str, style: str, text: str) -> int:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]       # 커닝·합자 유지
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.hinting = False               # 웹에서는 힌팅 정보가 용량만 차지
    font = TTFont(src_dir / src)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    rename(font, family, style)
    dest = OUT / out
    font.flavor = "woff2"
    font.save(dest)
    return dest.stat().st_size


def check() -> int:
    text = site_text()
    missing_all = 0
    for _, out, family, _ in FONTS:
        cmap = TTFont(OUT / out).getBestCmap()
        missing = sorted({ch for ch in text if ord(ch) not in cmap and not ch.isspace()})
        if missing:
            missing_all += len(missing)
            print(f"[빠짐] {out}: {''.join(missing)}")
    if missing_all:
        print("→ python3 tools/subset-fonts.py --src <원본 서체 폴더> 로 다시 만드세요.")
        return 1
    print(f"OK: 사이트 글자 {len(text)}자 모두 서체에 있음")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, help="원본 서체 폴더")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check()
    if not args.src:
        ap.error("--src 또는 --check 가 필요합니다")
    OUT.mkdir(parents=True, exist_ok=True)
    text = site_text()
    total = 0
    for src, out, family, style in FONTS:
        size = make(args.src, src, out, family, style, text)
        total += size
        print(f"{out}: {size / 1024:.1f}KB")
    size = make(args.src, *PIXEL, PIXEL_TEXT)
    total += size
    print(f"{PIXEL[1]}: {size / 1024:.1f}KB")
    print(f"글자 {len(text)}자, 합계 {total / 1024:.1f}KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
