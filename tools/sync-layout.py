#!/usr/bin/env python3
"""모든 페이지의 공통 영역(head 자산, 헤더, 푸터)을 이 파일의 원본으로 맞춘다.

왜: 빌드 없이 정적 HTML로 두되, 헤더·푸터가 페이지마다 달라지는 사고를 막는다.

쓰는 법
  python3 tools/sync-layout.py          # 각 *.html의 표시 영역을 원본으로 교체
  python3 tools/sync-layout.py --check  # 다른 페이지가 있으면 1로 종료 (배포 전)

페이지 안의 표시
  <!-- @assets -->...<!-- /@assets -->   <head> 안 공통 자산
  <!-- @header -->...<!-- /@header -->   헤더
  <!-- @footer -->...<!-- /@footer -->   푸터
  <body data-page="toaster">            현재 메뉴 표시(aria-current)에 쓰임
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS_VERSION = "20261105a"  # CSS·JS·서체를 바꾸면 올린다 (캐시 갱신, site.css의 서체 URL에도 반영됨)

ASSETS = f"""<link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/ax-sans.woff2?v={CSS_VERSION}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/ax-heading-800.woff2?v={CSS_VERSION}" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap">
<link rel="stylesheet" href="/css/site.css?v={CSS_VERSION}">
<script src="/js/main.js?v={CSS_VERSION}" defer></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-0PF8YSG744"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-0PF8YSG744');</script>"""

NAV = [("toaster", "/toaster", "Toaster"), ("security", "/security", "보안·구축"), ("about", "/about", "회사")]
PRODUCTS = [("studio", "Studio"), ("forge", "Forge"), ("judge", "Judge"), ("index", "Index"), ("agent", "Agent")]

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>'
NE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'


def header(page: str) -> str:
    cur = ' aria-current="page"'
    links = "\n".join(
        f'    <a href="{href}"{cur if key == page else ""}>{label}</a>' for key, href, label in NAV
    )
    contact_cur = cur if page == "contact" else ""
    # 문의 페이지에서는 플로팅 문의 버튼을 두지 않는다
    quick = "" if page == "contact" else '\n<a class="quick" href="/contact">도입 문의</a>'
    return f"""<a class="skip-link" href="#main">본문 바로가기</a>
<header class="site-header">
  <a class="brand" href="/" aria-label="AvalonX 홈"><img src="/assets/brand/avalonx-wordmark-on-light.svg" width="224" height="32" alt="AvalonX"></a>
  <button class="menu-toggle" type="button" aria-label="메뉴 열기" aria-expanded="false" aria-controls="site-menu" hidden>Menu <span class="dot" aria-hidden="true"></span></button>
  <nav id="site-menu" class="site-nav" aria-label="주 메뉴">
{links}
    <a href="/contact" class="nav-contact"{contact_cur}>도입 문의</a>
  </nav>
</header>{quick}"""


def _footer() -> str:
    prods = "".join(f'<li><a href="/toaster#{k}">{n}</a></li>' for k, n in PRODUCTS)
    return f"""<footer class="site-footer">
  <div class="footer-top">
    <img class="footer-mark" src="/assets/brand/avalonx-wordmark-on-dark.svg" width="681" height="98" alt="AvalonX">
    <div class="footer-cols">
      <div><h2>AvalonX</h2><ul><li><a href="/about">아발론엑스</a></li><li><a href="mailto:homepage@avalonx.kr">homepage@avalonx.kr</a></li><li><address>서울특별시 강남구 언주로 535 11층</address></li></ul></div>
      <div><h2>Menu</h2><ul><li><a href="/toaster">Toaster</a></li><li><a href="/security">보안·구축</a></li><li><a href="/about">회사</a></li><li><a href="/contact">도입 문의</a></li></ul></div>
      <div><h2>Toaster</h2><ul>{prods}</ul></div>
    </div>
  </div>
  <div class="footer-bottom"><span>© 2026 AvalonX · 아발론엑스. Own your AI.</span><a href="#main">맨 위로 ↑</a></div>
</footer>"""


FOOTER = _footer()


def region(html: str, name: str, body: str) -> str:
    pat = re.compile(rf"<!-- @{name} -->.*?<!-- /@{name} -->", re.S)
    if not pat.search(html):
        raise SystemExit(f"표시 영역 @{name} 없음")
    return pat.sub(lambda _: f"<!-- @{name} -->\n{body}\n<!-- /@{name} -->", html, count=1)


def render(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    m = re.search(r'<body[^>]*data-page="([^"]+)"', html)
    page = m.group(1) if m else ""
    html = region(html, "assets", ASSETS)
    html = region(html, "header", header(page))
    html = region(html, "footer", FOOTER)
    return html


def sync_css_fonts(check: bool) -> int:
    """site.css의 서체 URL 버전(?v=)을 CSS_VERSION에 맞춘다. preload URL과 같아야 두 번 받지 않는다."""
    css = ROOT / "css" / "site.css"
    old = css.read_text(encoding="utf-8")
    new = re.sub(r"(/assets/fonts/ax-[a-z0-9-]+\.woff2)(\?v=\w+)?", rf"\1?v={CSS_VERSION}", old)
    if new == old:
        return 0
    if check:
        print("[다름] css/site.css 서체 버전")
        return 1
    css.write_text(new, encoding="utf-8")
    print("갱신: css/site.css 서체 버전")
    return 0


def main() -> int:
    check = "--check" in sys.argv
    bad = sync_css_fonts(check)
    for path in sorted(ROOT.glob("*.html")):
        new = render(path)
        if new != path.read_text(encoding="utf-8"):
            if check:
                print(f"[다름] {path.name}")
                bad += 1
            else:
                path.write_text(new, encoding="utf-8")
                print(f"갱신: {path.name}")
    if check:
        print("OK: 공통 영역 일치" if not bad else "→ python3 tools/sync-layout.py 로 맞추세요.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
