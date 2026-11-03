# avalonx.kr

AvalonX 회사 홈페이지. 빌드 없는 정적 HTML이며 Cloudflare Pages가 `master`를 배포한다(브랜치를 push하면 `<브랜치>.avalonx.pages.dev` 미리보기가 생긴다).

| 페이지 | 파일 |
| --- | --- |
| / | index.html |
| /toaster | toaster.html |
| /security | security.html |
| /about | about.html |
| /contact | contact.html |

디자인 값의 원본은 AvalonX 브랜드 시스템(tokens.json)이며 `css/site.css` 맨 위에 옮겨 두었다.

## 문구·페이지를 고친 뒤 (배포 전)

```sh
python3 tools/sync-layout.py            # 헤더·푸터·공통 head를 모든 페이지에 맞춤
python3 tools/subset-fonts.py --check   # 새 글자가 서체에 빠졌는지 검사
```

`--check`가 빠진 글자를 보고하면 브랜드 시스템의 원본 서체로 서브셋을 다시 만든다.

```sh
pip install fonttools brotli
python3 tools/subset-fonts.py --src <원본 서체 폴더>
```

CSS·JS를 바꾸면 `tools/sync-layout.py`의 `CSS_VERSION`을 올리고 다시 실행한다(캐시 갱신).

## 그 밖의 파일

- `_redirects`: 옛 주소(/technology, /use-cases) 이동
- `_headers`: 미리보기 주소 검색 제외, 서체 캐시
- `assets/fonts/LICENSE.md`: 서체 라이선스(SIL OFL 1.1)
