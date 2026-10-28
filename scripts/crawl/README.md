# MPBEL 크롤러

옛 사이트(`http://mpbel.yonsei.ac.kr`, 그누보드5)의 내용을 읽어 Astro 콘텐츠(마크다운)와 이미지로 옮기는 도구입니다.

> **도메인 전환 후에는 실행 금지.** 전환 뒤에는 `mpbel.yonsei.ac.kr`이 새 사이트를 가리키므로 크롤러가 읽을 원본이 없습니다. 전환 후의 글은 `src/content/`의 마크다운을 직접 고쳐서 관리합니다.

## 준비 (최초 1회)

```bash
cd scripts/crawl
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

이후 모든 명령은 `scripts/crawl` 폴더에서 실행합니다.

## 실행

```bash
.venv/bin/python -m crawl                 # 전체 모드, 모든 종류
.venv/bin/python -m crawl --mode add      # 추가 모드
.venv/bin/python -m crawl --only assets   # 일부 종류만
```

### 두 가지 모드

- `--mode full` (기본값): **전체 모드.** 모든 결과 파일을 새로 씁니다(덮어쓰기). 최초 이전 때 한 번 실행합니다.
- `--mode add`: **추가 모드.** 목록 페이지(와 고정 페이지)는 캐시를 무시하고 옛 사이트에서 다시 받아 `reference/html/`의 캐시를 갱신합니다. 그 목록에서 새로 생긴 글만 추가하고, 이미 있는 마크다운 파일은 건드리지 않습니다(원본 글 번호 `legacy_id`로 판단). 이미 받아 둔 글 상세 페이지는 다시 받지 않습니다. 도메인 전환 직전에 한 번 더 실행해 그 사이 올라온 글(특히 연말 세미나 일괄 등록)을 반영합니다.
  - 고정 페이지(`pages`: 홈 `home.md`와 고정 페이지 7개)는 하나씩만 있는 페이지이므로 추가 모드에서도 **항상** 옛 사이트에서 다시 받아 8개 파일을 모두 새로 씁니다. 전환 전에 옛 사이트에서 고친 내용이 반영됩니다.
  - 지금은 `pages`와 `assets`만 동작하고, `members`, `publications`, `posts`는 이후 작업에서 추가됩니다(그 전까지는 `NotImplementedError`로 멈춥니다). 다시 받기는 `Fetcher.get(url, refresh=True)`로 하며, 오프라인 모드에서는 무시됩니다.

### 옵션

- `--only <종류,...>`: 쉼표로 구분한 목록 중 일부만 실행합니다. 종류는 `pages`, `members`, `publications`, `posts`, `assets`이고 기본값은 전부입니다. 예: `--only members,posts`
- `--out <폴더>`: 결과를 쓸 저장소 루트. 기본값은 이 저장소의 루트(`scripts/crawl` 기준 `../..`)입니다.
- `--offline`: 네트워크에 접속하지 않고 `reference/html/`에 저장된 원본만 사용합니다. 저장되지 않은 주소가 필요하면 오류로 멈춥니다.

실행이 끝나면 `collection  written  skipped` 표(종류별 새로 쓴 파일 수, 건너뛴 파일 수)를 출력합니다.

## 결과가 저장되는 곳 (저장소 루트 기준)

| 위치 | 내용 |
|---|---|
| `src/content/<collection>/ko/*.md` | 페이지, 멤버, 출판물, 뉴스·세미나·강의 글 (한 항목 = 한 파일) |
| `public/images/site/` | 로고, 아이콘, 배경 등 디자인 이미지 (`assets`). 옛 사이트의 `/images/x` → `/images/site/x`, `/img/x` → `/images/site/img/x`, `/skin/board/<스킨>/img/x` → `/images/site/skin/<스킨>/x`, `/skin/latest/basic/img/x` → `/images/site/skin/latest-basic/x`. CSS 안의 `url(...)`은 그 CSS 파일 위치 기준으로 해석합니다. |
| `public/images/pages/<slug>/` | 고정 페이지 이미지(썸네일이 아닌 원본). 받지 못한 이미지는 경고를 출력하고 본문에 옛 사이트 주소를 그대로 둡니다. |
| `public/images/...` | 멤버 사진 |
| `reference/html/` | 옛 사이트에서 받은 원본 그대로의 캐시(HTML, CSS, 이미지)와 `redirects.json`. 한 번 받은 주소는 다시 요청하지 않습니다. 옛 사이트의 기록으로 git에 함께 커밋합니다. |
| `reference/css/` | 옛 사이트 CSS 13개 원본 (`default.css`, `design.css`, `latest-basic.css`, `board-*.css`) |

고정 페이지와 홈의 본문은 옛 페이지의 HTML을 그대로 옮긴 것입니다. 마크다운은 빈 줄에서 HTML 덩어리를 끝내고 4칸 들여쓴 줄을 코드로 바꾸므로, 크롤러는 빈 줄과 줄 앞 공백을 모두 지워서 씁니다. 이 파일을 직접 고칠 때도 본문에 빈 줄이나 줄 앞 공백을 넣지 마세요.

## 서버 예절

- 요청마다 0.5초 기다리고, `User-Agent: mpbel-migration-crawler/1.0`을 보냅니다.
- 네트워크 오류와 5xx 응답은 1초, 2초, 4초 간격으로 세 번까지 다시 시도합니다. 4xx는 바로 실패합니다.
- 리다이렉트는 따라가지 않습니다. 옛 사이트는 없는 파일을 외부 404 페이지로 302 리다이렉트하므로, 이런 이미지는 경고만 출력하고 건너뜁니다.
- 캐시를 지우고 다시 받으려면 `reference/html/`의 해당 파일을 지운 뒤 실행합니다.

## 테스트

```bash
.venv/bin/python -m pytest -q
```

파서 테스트는 `tests/fixtures/*.html`(옛 사이트 페이지 20개)을 사용합니다. 이 파일들은 `tests/make_fixtures.py`로 한 번 받아 둔 것이며, 다시 받을 필요는 없습니다.
