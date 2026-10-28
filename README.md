# MPBEL 연구실 웹사이트

연세 의학물리 및 의공학 연구실(MPBEL) 홈페이지의 소스입니다. 이 문서는 사이트를 운영하는 사람을 위한 안내서입니다. 글 올리기, 멤버 관리, 배포, 도메인 전환 방법을 다룹니다.

- 지금 주소: https://ympbel.github.io/ (도메인 전환 후: https://mpbel.yonsei.ac.kr/)
- 저장소: https://github.com/ympbel/ympbel.github.io (브랜치 `main`)
- 옛 사이트 크롤러: [`scripts/crawl/README.md`](scripts/crawl/README.md)

## 1. 사이트 개요와 폴더 구조

옛 사이트 http://mpbel.yonsei.ac.kr (그누보드5)의 내용과 디자인을 [Astro](https://astro.build/) 정적 사이트로 옮겼습니다. 사이트의 모든 내용은 `src/content/` 아래 마크다운 파일이며, 한 항목(글 하나, 논문 하나, 멤버 한 명)이 파일 하나입니다. 파일 맨 위 `---` 사이의 값(frontmatter)은 `src/content/schemas.ts`의 규칙을 따라야 합니다. 디자인은 옛 사이트의 CSS를 그대로 가져왔고(`src/styles/legacy/`), 1024px 이하 화면용 규칙은 `src/styles/responsive.css`에 있습니다. `main`에 push하면 GitHub Actions가 사이트를 빌드해 GitHub Pages에 올립니다.

```
.
├── .github/workflows/deploy.yml   main에 push하면 빌드하고 GitHub Pages에 배포
├── astro.config.mjs               사이트 주소(site) 설정
├── package.json                   npm 명령 (dev, build, test)
├── public/                        그대로 복사되는 파일
│   └── images/
│       ├── site/                  로고, 배경, 아이콘 (옛 사이트 디자인 이미지)
│       ├── pages/<slug>/          고정 페이지 이미지
│       ├── members/<board>/       멤버 사진
│       └── posts/<year>/          새 글의 본문 이미지 (필요할 때 만드는 폴더)
├── reference/                     옛 사이트 원본(HTML·CSS 캐시)과 크롤 요약. 빌드에는 쓰이지 않음
├── scripts/crawl/                 옛 사이트 크롤러 (Python)
├── src/
│   ├── content/                   ★ 사이트 내용. 대부분의 수정은 여기서 합니다
│   │   ├── pages/ko/              고정 페이지 (홈, 소개, 연락처, 교수, 연구)
│   │   ├── members/ko/<board>/    구성원 (researchers, collaborators, alumni, internship)
│   │   ├── papers/ko/  presentations/ko/  talks/ko/  patents/ko/   출판물
│   │   ├── news/ko/  seminars/ko/  lectures/ko/                    게시판 글
│   │   ├── <collection>/en/       영문 (2차 작업, 지금은 비어 있음)
│   │   └── schemas.ts             frontmatter 규칙 (필드 이름과 형식)
│   ├── content.config.ts          컬렉션 정의 (`_`로 시작하는 파일은 제외)
│   ├── lib/content.ts             정렬, 분류, 쪽 나누기 규칙
│   ├── lib/menu.ts                메뉴 구조
│   ├── components/  layouts/      화면 조각과 공통 틀
│   ├── pages/                     주소(URL)별 페이지
│   └── styles/                    global.css, responsive.css, legacy/ (옛 사이트 CSS)
└── tests/
    ├── unit/                      규칙 단위 테스트
    └── dist/                      빌드 결과(dist/) 검사: 페이지 내용, 링크, CSS 순서
```

주소와 내용 파일:

| 주소 | 내용 파일 |
|---|---|
| `/` | `src/content/pages/ko/home.md` (최신 글과 출판물 목록은 자동) |
| `/introduction/welcome/`, `/introduction/contact/` | `src/content/pages/ko/welcome.md`, `contact.md` |
| `/member/professor/` | `src/content/pages/ko/professor.md` |
| `/member/researchers/`, `collaborators/`, `alumni/`, `internship/` | `src/content/members/ko/<board>/*.md` |
| `/research/ai/`, `radiation-therapy/`, `particle-therapy/`, `ct-reconstruction/` | `src/content/pages/ko/research-<이름>.md` |
| `/publication/paper/`, `presentation/`, `invited-talk/`, `patent/` | `src/content/papers/`, `presentations/`, `talks/`, `patents/` 의 `ko/*.md` |
| `/lecture/` | `src/content/lectures/ko/*.md` |
| `/notice/news/`, `/notice/seminar/` | `src/content/news/ko/*.md`, `src/content/seminars/ko/*.md` |
| `/notice/gallery/`, `/en/` | 준비 중 안내 페이지 (2차 작업) |

## 2. 로컬 실행

Node.js 24를 권장합니다(`.nvmrc`, 최소 22.23.4). 저장소 폴더에서:

```bash
npm install     # 처음 한 번, 또는 package.json이 바뀌었을 때
npm run dev     # http://localhost:4321 에서 미리보기. 파일을 고치면 바로 반영됩니다
npm test        # 단위 테스트 → 빌드(dist/) → 빌드 결과 검사
```

- `npm run dev`는 Ctrl+C로 멈춥니다. 터미널이 아닌 곳(스크립트 등)에서 실행하면 Astro가 백그라운드로 띄우고 그렇다고 알려 줍니다. 이때는 `npx astro dev stop`으로 멈춥니다.
- `npm run build && npm run preview`: 배포될 결과(`dist/`)를 그대로 띄워 봅니다.
- `npx astro sync`: frontmatter만 1초 안에 검사합니다. 빌드 전에 오타를 빨리 찾을 때 씁니다.
- `npm test`는 모든 테스트가 `fail 0`이어야 통과입니다. 실패하면 맨 아래 `failing tests:` 부분에 파일과 이유가 나옵니다.

### 작업 규칙

- **push 전에 `npm test`.** GitHub Actions는 빌드만 하고 테스트는 돌리지 않습니다. 깨진 링크나 CSS 순서 문제는 로컬 테스트에서만 잡힙니다.
- **`src/pages/` 아래 모든 페이지 파일은 `global.css`를 첫 번째 import로 가져옵니다.** 폴더 깊이에 따라 `import '../styles/global.css';` 또는 `import '../../styles/global.css';` 처럼 씁니다. 그다음 줄들에서 그 페이지가 쓰는 게시판 스킨 CSS를 페이지마다 import합니다(옛 사이트가 게시판마다 스킨 하나를 불렀던 것과 같습니다):
  - 고정 페이지 → `legacy/board-html.css` (`StaticPageBody` 컴포넌트가 가져옴)
  - 멤버 → researchers `board-student.css`, collaborators `board-collaborators.css`, alumni·internship `board-alumni.css`
  - 출판물 → paper `board-patent.css`, presentation·invited-talk `board-patent2.css`, patent `board-patent3.css`
  - 뉴스·세미나 → `board-basic.css`, 강의 → `board-lecture.css`, 갤러리 → `board-gallery.css`

  순서가 바뀌면 옛 사이트와 CSS 우선순위가 달라져 모양이 깨집니다. `tests/dist/css-order.test.mjs`가 모든 페이지에서 이 순서를 검사합니다.
- **사이트 안 링크는 `/`로 시작하고 `/`로 끝나게** 씁니다(예: `/member/researchers/`). `tests/dist/links.test.mjs`가 모든 페이지의 `/`로 시작하는 링크(`a href`)와 이미지(`img src`)가 실제 파일로 이어지는지 검사합니다. 본문에 넣은 이미지 경로가 틀려도 여기서 걸립니다.
- 파일 이름이 `_`로 시작하면(`_template.md`) 사이트에 포함되지 않습니다.
- 메뉴를 바꾸려면 `src/lib/menu.ts`를 고칩니다.

## 3. 글 올리는 법 — 세미나 / 뉴스 / 강의

| 게시판 | 폴더 | 목록 주소 |
|---|---|---|
| 세미나 | `src/content/seminars/ko/` | `/notice/seminar/` |
| 뉴스 | `src/content/news/ko/` | `/notice/news/` |
| 강의 | `src/content/lectures/ko/` | `/lecture/` |

1. 그 폴더의 `_template.md`를 복사해 `YYYY-MM-DD-<짧은-영문-제목>.md`로 만듭니다. 파일 이름은 영문 소문자, 숫자, `-`만 씁니다. 파일 이름이 글 주소가 됩니다(`/notice/seminar/2026-11-04-journal-club/`).
   ```bash
   cp src/content/seminars/ko/_template.md src/content/seminars/ko/2026-11-04-journal-club.md
   ```
   옛 사이트에서 옮긴 글은 `<작성일>-<옛 글 번호>.md`(예: `2025-12-31-471.md`)입니다.
2. frontmatter를 채우고, 쓰지 않는 줄을 지웁니다. `legacy_`로 시작하는 줄과 그 아래 들여쓴 줄까지 모두 지웁니다.
3. 두 번째 `---` 밑의 안내 문단 대신 본문을 마크다운으로 씁니다.
4. `npm run dev`로 확인하고 `npm test` 후 commit, push 합니다 (7장).

| 필드 | 필수 | 적는 법 | 화면 |
|---|---|---|---|
| `title` | 필수 | 글자. `:`나 `#`이 들어가거나 `[`로 시작하면 큰따옴표로 감쌉니다(제목 안의 `"`는 `\"`) | 목록과 글 제목 |
| `date` | 필수 | `'YYYY-MM-DD'`, 작은따옴표로 감쌈(따옴표가 없으면 빌드 실패) | 목록의 날짜. 목록은 최신 날짜가 위 |
| `category` | 선택 | 기존 값 중 하나 또는 새 연도. 새 값을 적으면 탭이 자동으로 생깁니다. 연도는 `'2026'`처럼 작은따옴표로 감쌈(따옴표가 없으면 빌드 실패) | 분류 탭과 목록의 분류 표시 |
| `pinned` | 선택 | `true` 또는 `false` (기본 `false`) | `true`면 전체 목록 1쪽 맨 위에 공지로 고정 |
| `presenter` | 선택 | 이름 | 글 위에 `Presenter: 이름` 줄 (본문에 이미 presenter 줄이 있으면 생략) |
| `event_date` | 선택 | `'YYYY-MM-DD'`, 작은따옴표로 감쌈(따옴표가 없으면 빌드 실패) | 강의: 목록의 '강의날짜' 칸과 글 위. 뉴스·세미나: 기록만 |
| 본문 | — | 두 번째 `---` 아래, 마크다운 (HTML도 가능) | 글 내용 |

- 지금 쓰는 분류 값: 세미나 `'2022'`~`'2025'`(연도), 뉴스 `연구실소식`, `학회공지`, `학회소식`, `공지`, `'2022'`~`'2025'`. 탭은 연도가 먼저(최신순), 그다음 가나다순입니다. 분류 페이지 주소는 `/notice/<게시판>/c/<분류>/`입니다.
- **강의 게시판에는 분류가 없습니다.** 강의 글에는 `category`를 적지 않습니다(템플릿에서도 주석 처리되어 있습니다). 적으면 없는 분류 페이지로 링크가 생겨 `npm test`가 실패합니다.
- 날짜에 따옴표가 없으면 빌드가 실패합니다(YAML이 날짜나 숫자로 읽음). 연도 분류도 같습니다.
- 본문에 글자 `<`, `>`를 쓰려면 `&lt;`, `&gt;`로 적습니다.
- 본문 이미지는 `public/images/posts/<year>/`에 넣고 `![](/images/posts/<year>/<file>)`로 씁니다. 파일 이름은 영문 소문자로 합니다.

예 (세미나):

```markdown
---
title: "2026/11/04 [Research Seminar] Dose prediction with deep learning"
date: '2026-11-04'
category: '2026'
pinned: false
presenter: 홍길동
event_date: '2026-11-04'
---

발표 요약을 여기에 씁니다.

![](/images/posts/2026/journal-club-1.png)
```

## 4. 논문 / 발표 / 초청강연 / 특허 추가

| 종류 | 폴더 | 주소 |
|---|---|---|
| 논문 | `src/content/papers/ko/` | `/publication/paper/` |
| 학회 발표 | `src/content/presentations/ko/` | `/publication/presentation/` |
| 초청 강연 | `src/content/talks/ko/` | `/publication/invited-talk/` |
| 특허 | `src/content/patents/ko/` | `/publication/patent/` |

그 폴더의 `_template.md`를 복사해 `YYYY-<짧은-영문-제목>.md`로 만들고, 쓰지 않는 줄과 `legacy_` 줄, 아래 안내 문단을 지웁니다. 본문은 쓰지 않습니다. 옛 사이트에서 옮긴 항목은 `<연도>-<옛 글 번호>-<제목 앞 다섯 단어>.md`입니다.

```bash
cp src/content/papers/ko/_template.md src/content/papers/ko/2026-dose-prediction.md
```

| 필드 | 필수 | 적는 법 |
|---|---|---|
| `year` | 필수 | 4자리 정수, 따옴표 없이 (예: `2026`). 새 연도를 적으면 연도 탭이 자동으로 생깁니다 |
| `title` | 필수 | 제목. `:`나 `#`이 들어가거나 `[`로 시작하면 큰따옴표로 감쌉니다 |
| `authors` | 선택 | 저자를 쉼표로 구분 |
| `venue` | 선택 | `venue: \|-` 다음 줄부터 두 칸 들여 한 줄씩. 줄마다 화면에서도 한 줄입니다 (논문: 학술지, 권·쪽, 날짜 / 특허: `등록국가: …`, `등록번호: …`, `등록일: …`) |
| `link` | 선택 | 주소 (DOI 등). LINK 버튼으로 표시 |
| `pinned` | 선택 | `true`면 그 해의 맨 위에 '공지'로 표시 (기본 `false`) |
| `order` | 선택 | 같은 연도 안의 순서(정수). 큰 수가 위에 표시됩니다. 비우면 그 해의 맨 위에 표시 |

예 (논문):

```yaml
---
year: 2026
title: "Dose prediction with deep learning: a feasibility study"
authors: Gildong Hong, Jin Sung Kim
venue: |-
  Medical Physics
  Volume 53, e70001
  5 January 2026
link: https://doi.org/10.xxxx/xxxxx
pinned: false
---
```

## 5. 멤버 추가·수정·졸업 처리

멤버는 게시판별 폴더에 한 사람당 한 파일입니다. 교수님 페이지는 고정 페이지입니다(6장, `professor.md`).

| 게시판 (`board`) | 폴더 | 주소 | `category` 값 |
|---|---|---|---|
| `researchers` | `src/content/members/ko/researchers/` | `/member/researchers/` | `MPBEL`, `Affiliate` |
| `collaborators` | `src/content/members/ko/collaborators/` | `/member/collaborators/` | 없음 |
| `alumni` | `src/content/members/ko/alumni/` | `/member/alumni/` | `Graduate`, `Former` |
| `internship` | `src/content/members/ko/internship/` | `/member/internship/` | 없음 |

새 멤버는 `src/content/members/ko/_template.md`를 복사해 `src/content/members/ko/<board>/<영문-이름>.md`로 만듭니다. 옛 사이트에서 옮긴 파일은 `<영문-이름>-<옛 글 번호>.md`입니다.

```bash
cp src/content/members/ko/_template.md src/content/members/ko/researchers/gildong-hong.md
```

| 필드 | 필수 | 적는 법 |
|---|---|---|
| `board` | 필수 | `researchers`, `collaborators`, `alumni`, `internship` 중 하나. 파일이 있는 폴더 이름과 같게 |
| `category` | 선택 | 위 표의 값. 분류 없는 게시판이면 줄을 지웁니다. 분류마다 탭과 구역이 생깁니다 |
| `name` | 필수 | `한글이름 English Name` (예: `양고운 Gowoon Yang`) |
| `photo` | 선택 | `/images/members/<board>/<파일>.jpg`. 사진 파일은 `public/images/members/<board>/`에 넣습니다 |
| `link` | 선택 | 개인 홈페이지 등. 카드의 LINK 버튼 |
| `fields` | 선택 | 이름 아래 항목 목록. `- label: E-mail` 다음 줄 `value: …` 식으로 적은 순서대로 표시. 없으면 `fields: []` |
| `order` | 필수 | 게시판 안의 표시 순서(정수). **작은 수가 먼저** 나옵니다. 같으면 파일 이름순 |

- 맨 뒤에 넣으려면 지금 가장 큰 `order`보다 1 큰 수를 씁니다:
  ```bash
  grep -h '^order:' src/content/members/ko/researchers/*.md | sort -n -k2 | tail -1
  ```
  중간에 넣으려면 뒤 사람들의 `order`를 하나씩 늘립니다.
- 사진은 JPG, 긴 변 800px 이하로 줄여 넣습니다(옛 사진도 그렇게 줄였습니다).
- 연구원(researchers)은 `fields`에 보통 `Grade`, `E-mail`, `Research Interest`를, 졸업생(alumni)은 `E-mail`, `Research Interest`를 씁니다.

**졸업 처리** (연구원 → 졸업생): 파일을 `alumni/`로 옮기고 `board`와 `category`를 바꿉니다.

```bash
git mv src/content/members/ko/researchers/gildong-hong.md src/content/members/ko/alumni/
```

그다음 그 파일에서 `board: alumni`, `category: Graduate`(또는 `Former`)로 바꾸고, `order`를 졸업생 목록에 맞게 정하고, `fields`의 `Grade` 항목은 지웁니다. 사진은 그대로 두어도 보입니다. 정리하려면 `git mv`로 사진도 `public/images/members/alumni/`로 옮기고 `photo` 경로를 고칩니다.

## 6. 고정 페이지 수정

`src/content/pages/ko/*.md` 8개 파일입니다. 본문은 옛 페이지의 HTML을 그대로 옮긴 것이고, HTML을 그대로 써도 됩니다.

| 파일 | 주소 |
|---|---|
| `home.md` | `/` (홈 소개 문단, `links`: 홈 아래 링크 4개의 `label`과 `url`) |
| `welcome.md` | `/introduction/welcome/` |
| `contact.md` | `/introduction/contact/` |
| `professor.md` | `/member/professor/` |
| `research-ai.md`, `research-radiation-therapy.md`, `research-particle-therapy.md`, `research-ct-reconstruction.md` | `/research/ai/` 등 (`research-` 뒤가 주소) |

- **본문에 빈 줄이나 줄 앞 공백을 넣지 마세요.** 마크다운은 빈 줄에서 HTML 덩어리를 끝내고, 4칸 들여쓴 줄을 코드로 바꿉니다.
- 이미지는 `public/images/pages/<파일 이름>/`에 넣고 `<img src="/images/pages/<파일 이름>/<이미지>">`로 씁니다.
- `title`은 페이지 제목, `section`은 메뉴 구역(`home`, `introduction`, `member`, `research`)입니다. `images`, `legacy_url`은 크롤러가 남긴 기록이며 화면에는 쓰이지 않습니다.
- Advanced CT Reconstruction(`/research/ct-reconstruction/`)은 옛 사이트처럼 메뉴에 없고 홈의 연구 카드에서만 연결됩니다.

## 7. 배포

```bash
npm test
git add -A
git commit -m "content: 2026-11-04 세미나"
git push origin main
```

push하면 GitHub Actions의 "Deploy to GitHub Pages" 워크플로가 빌드(`build`)와 배포(`deploy`)를 합니다. 보통 1~3분 뒤 https://ympbel.github.io/ 에 반영됩니다(브라우저 캐시 때문에 몇 분 늦게 보이면 새로고침).

진행 상황은 https://github.com/ympbel/ympbel.github.io/actions 또는:

```bash
gh run list --workflow deploy.yml --limit 3
gh run watch $(gh run list --workflow deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId') --exit-status
```

**빌드가 실패하면** 실패한 실행 → `build` 작업 → `Run withastro/action@v6` 단계의 로그를 봅니다(`gh run view <번호> --log-failed`로도 볼 수 있습니다). `[InvalidContentEntryDataError]`는 frontmatter 오류이며, 어느 파일의 어느 필드가 왜 틀렸는지가 나옵니다:

```
[InvalidContentEntryDataError] news → ko/2026-11-04-journal-club data does not match collection schema.

  date: Invalid string: must match pattern /^\d{4}-\d{2}-\d{2}$/
```

흔한 원인: 날짜·연도 분류에 따옴표 없음, `:`가 든 제목에 따옴표 없음, `year`에 따옴표, `order`가 정수가 아님, `board` 값 오타. 파일을 고쳐 다시 push하면 됩니다. 배포에 실패해도 사이트는 이전 상태로 남아 있습니다. 올린 변경을 되돌리려면 `git revert <커밋>` 후 push합니다.

## 8. 도메인 전환 체크리스트 (한 번만)

`mpbel.yonsei.ac.kr`을 이 사이트로 옮길 때 한 번만 합니다.

0. **Pages 설정이 `workflow`인지 확인합니다.** 저장소 이름이 `ympbel.github.io`라서, Pages를 다시 설정하면 예전 방식(Jekyll 빌드)이 켜져 Actions 배포와 경쟁할 수 있습니다(한 번 있었습니다). Pages를 (다시) 설정할 때는 push 하기 **전에** 아래 명령으로 `build_type`을 `workflow`로 맞춥니다.
   ```bash
   gh api repos/ympbel/ympbel.github.io/pages --jq .build_type    # workflow 가 나와야 함
   gh api -X PUT repos/ympbel/ympbel.github.io/pages -f build_type=workflow
   ```
1. **(a) 전환 직전 새 글 반영.** 크롤러를 추가 모드로 한 번 더 돌려 그 사이 옛 사이트에 올라온 글·멤버·출판물을 가져옵니다 (처음이면 [`scripts/crawl/README.md`](scripts/crawl/README.md)의 "준비"로 `.venv`를 만듭니다).
   1. 글·멤버·출판물만 추가합니다. 고정 페이지(`pages`)는 넣지 않습니다. 추가 모드는 이미 있는 파일(옛 글 번호 `legacy_id`로 판단)을 건드리지 않고 새 항목만 추가하며, 졸업 처리로 다른 게시판 폴더로 옮긴 멤버도 다시 만들지 않습니다.
      ```bash
      cd scripts/crawl && .venv/bin/python -m crawl --mode add --only members,publications,posts
      cd ../..
      ```
   2. 옛 사이트의 고정 페이지(소개·교수·연구)를 1차 크롤링 이후에 고쳤다면 `--only pages`를 따로 실행하고 `git diff`로 확인합니다. 이 실행은 고정 페이지 8개(`home.md` 포함)를 모두 옛 사이트 내용으로 다시 쓰므로, 새 저장소에서 고친 내용(예: 홈 링크 라벨)이 되돌려집니다. 옛 사이트에서 고친 부분만 남깁니다.
      ```bash
      cd scripts/crawl && .venv/bin/python -m crawl --mode add --only pages
      cd ../..
      git diff src/content/pages/
      ```
   3. **커밋 전에 반드시 확인합니다.** `git status`와 `git diff`로 바뀐 파일을 모두 봅니다. 새 저장소에서 고친 내용이 되돌려졌으면 `git checkout -- <파일>`로 복구하고, 새로 추가된 글 중 새 저장소에 이미 손으로 올린 글과 겹치는 것은 지웁니다.
      ```bash
      git status
      git diff
      npm test
      git add -A && git commit -m "content: 전환 직전 새 글 반영"
      git push origin main
      ```

   추가 모드와 `--only` 실행은 `reference/crawl-summary.json`을 그 실행의 일부 수치로 덮어씁니다. 전체 수치가 필요하면 `.venv/bin/python -m crawl --mode full --offline`(캐시만 사용)로 다시 만듭니다. 단, 전체 모드는 `src/content/`의 파일을 모두 다시 쓰므로 손으로 고친 내용이 있으면 덮어씁니다.
2. **(b) DNS 요청.** 학교 DNS 담당자에게 다음 두 레코드를 함께 요청합니다.
   - `mpbel.yonsei.ac.kr  CNAME  ympbel.github.io`
   - `_github-pages-challenge-ympbel.mpbel.yonsei.ac.kr  TXT  <값>` (도메인 인증, 권장). 값은 GitHub 조직 ympbel의 Settings → Pages → Add a domain 화면에 나옵니다. 인증해 두면 다른 GitHub 계정이 이 도메인을 쓸 수 없습니다.

   DNS 요청 후 반영까지 며칠 걸릴 수 있으니, (a)는 전환 직전에 다시 실행합니다.
3. **(c) 사이트 주소 변경.** `dig mpbel.yonsei.ac.kr CNAME +short`에 `ympbel.github.io.`가 보이면 바로 (c)와 (d)를 합니다. DNS가 반영된 뒤 (d)를 마칠 때까지는 이 주소에 GitHub의 404 페이지가 보이기 때문입니다. `astro.config.mjs`의 `site`를 `'https://mpbel.yonsei.ac.kr'`로 바꾸고 `public/CNAME` 파일을 추가합니다.
   ```bash
   echo mpbel.yonsei.ac.kr > public/CNAME
   npm test
   git add astro.config.mjs public/CNAME
   git commit -m "chore: switch domain to mpbel.yonsei.ac.kr"
   git push origin main
   ```
4. **(d) GitHub 설정.** 저장소 Settings → Pages → Custom domain에 `mpbel.yonsei.ac.kr`을 입력하고 Save. "DNS check successful"이 나오면 Enforce HTTPS를 체크합니다(인증서 발급까지 시간이 걸리면 체크 상자가 비활성입니다. 기다렸다가 다시 시도합니다). Actions로 배포하는 사이트는 이 설정값이 실제로 쓰이고, `public/CNAME`은 기록용입니다. 명령으로 하려면:
   ```bash
   gh api -X PUT repos/ympbel/ympbel.github.io/pages -f cname=mpbel.yonsei.ac.kr
   gh api -X PUT repos/ympbel/ympbel.github.io/pages -F https_enforced=true
   ```
5. **(e) 확인.**
   ```bash
   curl -I https://mpbel.yonsei.ac.kr/                  # HTTP/2 200
   curl -I https://mpbel.yonsei.ac.kr/notice/seminar/   # HTTP/2 200
   ```
6. **(f) 이후 크롤러 실행 금지.** 전환 뒤에는 `mpbel.yonsei.ac.kr`이 새 사이트를 가리키므로 크롤러가 읽을 원본이 없습니다. 글은 `src/content/`의 마크다운을 직접 고칩니다.

## 9. 2차 작업 메모와 알려진 차이

### 2차 작업

- **갤러리와 본문 이미지.** 갤러리(`/notice/gallery/`)는 준비 중 페이지입니다. 뉴스·세미나·강의 글의 이미지는 아직 옮기지 않았고, 각 글의 `legacy_images`에 옛 서버의 경로(호스트 없는 `/data/...`)만 적혀 있습니다. 옛 서버는 전환 뒤에도 IP 주소로 접속할 수 있으므로, 그 IP로 받아 `public/images/posts/<year>/`에 넣고 본문에 넣습니다.
- **첨부파일.** `legacy_files`(게시판 글의 첨부, 출판물 DOWNLOAD 버튼 29개, 공지로 고정된 초청 강연의 PDF)도 경로만 기록되어 있고 화면에는 나오지 않습니다. 이미지와 같은 방법으로 옮깁니다.
- **영문 사이트.** 내용은 `src/content/<collection>/en/`(지금은 빈 폴더), 페이지는 `src/pages/en/`(지금은 `/en/` 안내 페이지 하나), 문구는 `src/i18n/en.ts`, 메뉴는 `src/lib/menu.ts`의 `MENU.en`입니다.
- **브라우저에서 글쓰기.** 필요하면 Decap CMS나 Sveltia CMS를 붙여 마크다운 파일을 웹 화면에서 편집하게 할 수 있습니다.

### 알려진 차이 (옛 사이트와 다른 점)

- 멤버 사진 5장(연구원 이혜진·이원형, 졸업생 이주영·최민서, 인턴 이강훈)은 202×150 썸네일입니다. 옛 서버에 원본이 없었습니다. 새 사진을 받으면 같은 파일을 바꿔 넣습니다.
- 멤버 카드의 글(이름·항목) 시작 위치가 카드마다 조금씩 다릅니다. 옛 사이트는 모든 사진을 202×150 썸네일로 보여 주었지만, 지금은 줄인 원본 사진을 쓰므로 사진마다 가로세로 비율이 달라 사진 폭이 다릅니다(위의 썸네일 5장만 옛 위치). 최종 수정 단계에서 고칠 예정입니다.
- 홈 아래 링크 2번, 4번(연세암병원 의학물리팀 블로그, 방사선종양학과)의 라벨은 옛 사이트의 `<br>` 줄바꿈이 없어 단어 중간에서 줄이 바뀌고, 오른쪽 화살표가 글자 끝과 겹칩니다. 라벨은 `src/content/pages/ko/home.md`의 `links`에 있고 `src/pages/index.astro`가 표시합니다.
- 연구(Research) 페이지의 왼쪽 메뉴는 현재 페이지 항목을 강조합니다. 옛 사이트는 한 칸 어긋나 있었습니다.
- 화면 폭 1025~1199px에서는 1200px 데스크톱 배치를 그대로 씁니다(가로 스크롤). 1024px 이하부터 모바일 배치입니다.
- 갤러리와 영문 페이지는 준비 중 안내만 있습니다.
- 첨부파일과 글 본문 이미지는 아직 옮기지 않았습니다(위 2차 작업).
- 조회수, 댓글, 검색은 없습니다. 옛 주소(`/bbs/board.php?...`)를 새 주소로 넘겨 주는 리다이렉트도 없습니다. 그래서 글 본문에 남아 있는 옛 사이트 링크 31개 중 옛 게시판 주소 30개는 전환 뒤 열리지 않습니다(`tests/dist/links.test.mjs`가 개수를 출력합니다).
