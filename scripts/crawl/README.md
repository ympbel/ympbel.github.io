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
  - 멤버(`members`)는 분류 탭(연구원 MPBEL·Affiliate, 졸업생 Graduate·Former)별 목록과 분류 없는 전체 목록을 모두 다시 받고, 게시판 폴더(`src/content/members/ko/<board>/`)에 같은 `legacy_id`가 없는 사람만 추가합니다. 어느 탭에도 없는 사람은 `category` 없이 들어갑니다. 카드의 LINK 버튼(`div.link01`의 첫 링크)은 주소 그대로 `link`에 적습니다. 옛 사이트에서는 `bbs/link.php?...` 주소이며, 출판물과 달리 리다이렉트를 따라가 실제 주소를 읽지는 않습니다.
  - 출판물(`publications`: 논문 `papers`, 학회 발표 `presentations`, 초청 강연 `talks`, 특허 `patents`)은 연도 탭(`sca=<연도>`)별 목록을 탭마다의 쪽수만큼, 그리고 분류 없는 전체 목록을 모두 다시 받고, `src/content/<collection>/ko/`에 같은 `legacy_id`가 없는 항목만 `<연도>-<wr_id>-<제목 앞 5단어>.md`로 추가합니다. 연도는 그 글이 있는 탭의 연도입니다. 두 가지 글만 상세 페이지를 받아 `Year of publication`과 첨부파일(`legacy_files`)을 가져옵니다: 공지(`pinned`) 글(옛 사이트는 전체 목록에서만 '공지'로 표시하고 연도 탭에서는 보통 글로 보여 줍니다)과, 탭이 없는 연도의 글(학회 발표 2002~2004년 9건, 전체 목록에만 나옵니다). 상세 페이지에도 연도가 없는 글은 경고를 출력하고 건너뜁니다. 목록의 LINK 버튼(`bbs/link.php`)은 따라가지 않고 리다이렉트 주소만 읽어 `link`에 적으며(`reference/html/redirects.json`에 저장), 리다이렉트가 없거나 오류이면 경고를 출력하고 `link` 줄 없이 씁니다.
  - 글(`posts`: 뉴스 `news`, 세미나 `seminars`, 강의 `lectures`)은 분류 탭을 따로 받지 않고 분류 없는 전체 목록만 쪽수만큼 다시 받습니다(분류는 목록의 각 줄과 상세 페이지에 있습니다). `src/content/<collection>/ko/`에 같은 `legacy_id`가 없는 글만 상세 페이지를 받아 `<작성일>-<wr_id>.md`로 추가하므로, 다시 실행하는 비용은 새 글 수에 비례합니다. 공지(`pinned`) 글은 여러 쪽에 다시 나와도 한 번만 씁니다. 제목(`title`)은 잘리지 않은 `<title>`의 제목, `date`는 작성일, `category`는 분류, `event_date`는 다음 중 처음 찾은 올바른 날짜(월 01~12, 일 01~31)입니다: 강의 날짜(`강의날짜`), 제목 맨 앞의 `YYYY/MM/DD`, 제목 안 어디든 처음 나오는 `YYYY/MM/DD`나 `YYYY-MM-DD`, 본문의 `Date : YYYY/MM/DD` 줄(예: `Announcement Date : 2020/03/30`, 대소문자 무관). `presenter`는 본문의 `Presenter: …` 줄(본문에도 그대로 남습니다)이며, 값이 없으면 그 줄을 쓰지 않습니다. 본문(`#bo_v_con`)은 마크다운으로 바꿉니다. 글자 `<`, `>`는 HTML 태그로 읽히지 않도록 `&lt;`, `&gt;`로 적고(화면에는 `<`, `>`로 보입니다), 보이지 않는 폭 0 문자(U+200B 등)는 지우며, 붙어 있는 굵은 글씨 두 덩어리는 글자를 바꾸지 않고 한 덩어리(`**앞뒤**`)로 합칩니다. 직접 고칠 때도 `<`, `>`는 `&lt;`, `&gt;`로 적으세요.
    - `legacy_images`: 글에 보이던 이미지의 옛 사이트 경로 목록(호스트 없이 `/data/...`). 본문 위에 따로 보이던 첨부 이미지(`#bo_v_img`, `/data/file/<게시판>/...`)가 먼저, 본문 이미지(`/data/editor/...`)가 본문 순서대로 그 뒤에 옵니다. 썸네일이 아니라 `view_image.php` 링크가 가리키는 원본이며, 링크 없이 썸네일(`thumb-<파일>_<가로>x<세로>.<확장자>`)만 있으면 원본 이름(`<파일>.<확장자>`)으로 적습니다. 옛 도메인 `ympbe.yonsei.ac.kr`의 주소도 같은 파일이 옛 사이트에 있으므로 호스트 없는 경로로 적습니다. 다른 사이트에서 복사해 온 이미지(뉴스 30의 `smart.yonsei.ac.kr`, 39의 `googleusercontent.com`)는 옛 사이트에 없으므로 전체 주소를 그대로 적습니다. 이미지는 본문에서 지우고(그 뒤 공백·`&nbsp;`·`<br>`만 남은 문단도 지웁니다) 받지는 않으므로, 새 사이트에 이미지를 옮길 때 이 목록을 씁니다.
    - `legacy_files`: 첨부파일 목록. 항목마다 `name`(파일 이름)과 `url`(호스트 없는 다운로드 경로 `/bbs/download.php?bo_table=...&wr_id=...&no=...`)이 있습니다. 출판물의 `legacy_files`도 같은 형식입니다.
  - 다섯 종류(`pages`, `members`, `publications`, `posts`, `assets`)가 모두 동작합니다. 다시 받기는 `Fetcher.get(url, refresh=True)`로 하며, 오프라인 모드에서는 무시됩니다.

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
| `public/images/members/<board>/<wr_id>.<ext>` | 멤버 사진 (`<board>`: researchers, collaborators, alumni, internship, `<ext>`는 소문자). 목록의 썸네일 대신 원본을 받고, 없으면 확장자를 대문자로 바꾼 주소(예: `.JPG`), 그것도 없으면 썸네일(202x150)을 받습니다. 긴 변이 800px를 넘으면 800px로 줄여 저장하며, `reference/html/`에는 받은 원본을 그대로 둡니다. 이미 있는 사진 파일은 다시 받지 않으므로, 새로 받으려면 그 파일을 지우고 실행합니다. |
| `reference/html/` | 옛 사이트에서 받은 원본 그대로의 캐시(HTML, CSS, 이미지)와 `redirects.json`. 한 번 받은 주소는 다시 요청하지 않습니다. 옛 사이트의 기록으로 git에 함께 커밋합니다. |
| `reference/css/` | 옛 사이트 CSS 13개 원본 (`default.css`, `design.css`, `latest-basic.css`, `board-*.css`) |
| `reference/crawl-summary.json` | 마지막 실행의 요약: 종류별 `{"written": 새로 쓴 파일 수, "skipped": 건너뛴 파일 수}`와 실행 시각 `generated_at`(UTC, ISO 8601). 실행할 때마다 새로 쓰며 결과와 함께 커밋합니다. |

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
