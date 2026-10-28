# MPBEL 연구실 웹사이트 Astro 재구축 설계

- 작성일: 2026-10-28
- 대상: http://mpbel.yonsei.ac.kr (연세 의학물리 및 의공학 연구실, Yonsei Medical Physics and Biomedical Engineering Lab)
- 상태: 빌더 검토 반영 완료, 사용자 승인 대기

---

## 1. 의도와 배경

현재 MPBEL 웹사이트는 2018년에 제작된 그누보드5(PHP/MySQL) 사이트다. 외주 업체(DSSO) 커스텀 스킨 위에서 돌아가고, 한글/영문 두 세트의 게시판을 갖고 있다.

이 프로젝트는 **그 사이트를 같은 외관과 같은 메뉴 구조를 가진 정적 사이트로 교체**한다. 콘텐츠는 전부 마크다운 파일로 GitHub 저장소에 들어가고, 파일을 수정하면 GitHub Pages로 자동 배포된다. 서버, DB, 관리자 화면은 없다.

동기는 사용자가 명시하지 않았다. 작성자의 추정은 "오래된 PHP 서버와 그누보드를 계속 유지보수하는 부담"이며, 사용자는 이 추정을 부정하지 않았다. 디자인에 대한 불만은 없다("그대로 만들어서 대체").

### 성공의 모습

1. 방문자가 바뀐 줄 거의 모른다. 메뉴, 페이지 구성, 색, 글꼴, 배치가 지금과 같다.
2. 연구실 구성원이 마크다운 파일 하나를 추가하고 커밋하면 세미나/뉴스 글이 올라간다.
3. 스마트폰에서 열어도 깨지지 않는다.
4. 한글 사이트의 텍스트 콘텐츠가 전부 옮겨져 있다.
5. 빌드와 배포가 옛 서버나 외부 서비스에 의존하지 않는다.

---

## 2. 범위

### 2.1 목표 (1차)

- **한글 사이트 전체.** 홈 + 6개 대메뉴 아래 18개 하위 페이지 + 뉴스/세미나/강의 게시글 상세 페이지.
- **반응형.** 보이는 디자인은 유지하되 모바일에서 레이아웃이 재배치된다. (사용자 결정)
- **콘텐츠 이전은 크롤링으로.** DB 권한은 있지만 쓰지 않는다. 공개 페이지를 크롤링해서 마크다운으로 변환하는 스크립트를 만들고, 그 결과물을 저장소에 넣는다. (사용자 결정)
- **이미지 중 1차에 포함하는 것** (작성자 결정, 아래 "작성자가 정한 것" 참조):
  - 디자인 자산: 로고, 메인/서브 배너, 아이콘, 연구 카드 배경, 홈 아이콘 등 `/images/`, `/img/` 아래 파일
  - 고정 페이지 안의 이미지: Welcome 비주얼, 교수 사진, 연구 소개 페이지의 그림
  - 멤버 프로필 사진: 연구원, 협력연구자, 졸업생, 단기 인턴
- **영문은 구조만.** 폴더 구조, 라우팅, 언어 전환 버튼까지만 만들고 콘텐츠는 넣지 않는다. (사용자 결정)
- **GitHub Pages 자동 배포.** GitHub Actions로 main 브랜치 푸시 시 빌드·배포.
- **글 작성 안내.** 저장소 README에 "세미나 글 올리는 법", "논문 추가하는 법" 등 종류별 절차와 템플릿 파일.

### 2.2 비목표 (1차에서 하지 않는 것)

- 영문 콘텐츠 이전. (영문 게시판에는 세미나 229건, 뉴스 45건, 갤러리 53건 등 별도 콘텐츠가 있다. 2차 이후.)
- 갤러리 게시판 사진 62건, 뉴스/세미나 게시글 본문에 붙은 이미지 약 480장. 사용자가 나중에 직접 처리한다. 옛 서버는 도메인 전환 후에도 접근 가능하므로(사용자 확인) 미리 받아 둘 필요는 없다. 크롤러는 각 글의 원본 이미지 경로를 frontmatter에 보존해 두어 나중에 스크립트로 받을 수 있게 한다.
- 관리자 화면, 로그인, 댓글, 조회수, 캡차, 게시판 내 검색.
- 기존 URL(`/bbs/board.php?bo_table=...&wr_id=...`) 호환이나 리다이렉트.
- 도메인 연결 작업 자체. 사용자가 학교 담당자에게 요청한다. 이 프로젝트는 필요한 DNS 레코드 값을 README에 적어 두는 것까지만 한다.
- 디자인 개선, 리뉴얼, 콘텐츠 정리. 옛 사이트에 있는 오타나 "test" 같은 잔여 텍스트도 그대로 옮긴다. 정리는 사용자가 마크다운에서 직접 한다.

### 2.3 반목표 (이렇게 되면 기술적으로 돌아가도 실패)

- 글 하나 올리려고 Astro 컴포넌트나 설정 파일을 건드려야 하는 구조.
- 두 사람이 같은 날 글을 올리면 git 충돌이 나는 구조. (한 파일에 모든 글을 몰아넣는 방식 금지)
- 빌드가 옛 서버, DB, 외부 API에 의존.
- 외관이 눈에 띄게 달라짐.
- 크롤링 결과를 손으로 많이 고쳐야 쓸 수 있는 상태.

---

## 3. 제약

| 항목 | 내용 | 누가 정했나 |
|---|---|---|
| 프레임워크 | Astro | 사용자 |
| 콘텐츠 형식 | 마크다운 (frontmatter + 본문) | 사용자 |
| 호스팅 | GitHub Pages | 사용자 |
| 글 작성자 | 전원 GitHub와 마크다운에 익숙 | 사용자 확인 |
| 콘텐츠 원본 | 공개 페이지 크롤링 | 사용자 |
| 최종 도메인 | mpbel.yonsei.ac.kr, HTTPS | 기존 |
| 크롤링 접근 | 옛 사이트는 HTTP 전용. HTTPS는 자가서명 인증서라 실패함. 크롤러는 `http://`로 접근 | 환경 |
| 작업 폴더 | `/Users/yongdo/Documents/Code_MBA/Claude_workspace/Website_20261028` (현재 비어 있음, git 미초기화) | 환경 |
| 옛 서버 | 도메인 전환 후에도 접근 가능. 2차 이미지 이전은 옛 서버에서 직접 받는다 | 사용자 확인 |
| 저장소 | 사용자가 만든 연구실 GitHub 조직 아래 공개 저장소. 저장소 이름은 `ympbel.github.io` | 사용자 결정 + 작성자 제안 |
| 푸터 | "Design by DSSO" 문구 삭제. 디자인 자산(CSS, 배너, 아이콘)은 재사용 | 사용자 결정 |

---

## 4. 현재 사이트 분석 (빌더 참고용)

### 4.1 기술 스택

- 그누보드5. 전역 변수 `g5_url`, `/bbs/board.php?bo_table=` 패턴.
- jQuery 1.8.3, jquery.menu.js(드롭다운), bxslider(로드만 되고 실제 슬라이더는 없음, 메인 배너는 정적 이미지 한 장), Font Awesome 4.
- Google Fonts: Lato 300/400/700, Nanum Gothic.
- CSS 총 36KB: `css/default.css` 20KB, `css/design.css` 12.6KB, `skin/latest/basic/style.css` 2.5KB. **미디어쿼리 없음, 고정폭.**
- 스크린샷/CSS/이미지는 크롤러가 받아서 `reference/` 폴더에 보관한다 (빌드에 포함하지 않음, 외관 대조용).

### 4.2 공통 레이아웃

- 상단: 로고(`images/logo.png`), 우측 상단 KR/EN 토글, 6개 대메뉴 가로 배치. 대메뉴에 마우스를 올리면 하위 메뉴가 드롭다운.
- 푸터: 영문 연구실명, 주소(03722 서울특별시 서대문구 연세로 50 연세대학교), TEL/FAX, COPYRIGHT @2018 MPBEL, "Design by DSSO". 새 사이트에서는 "Design by DSSO"를 뺀다(사용자 결정). 나머지는 그대로.

### 4.3 홈 (`index.php`)

위에서 아래로:

1. `visual`: 배경 이미지 위에 슬로건 이미지(`images/main/slogan.png`)
2. `about`: "MPBEL Introduction" 제목 + 연구실 소개문 5~6줄
3. `research_wrap`: 연구 카드 4개가 지그재그(제목/이미지 좌우 교대)로 배치. RESEARCH 01 Advanced CT Reconstruction, 02 Medical Artificial Intelligence, 03 Radiation Therapy, 04 Particle Therapy. 각각 연구 페이지로 링크.
4. `main_board`: 좌측에 News 최신 4건(제목, 월-일) + 외부 링크 블록(김진성 교수님 블로그, 연세암병원 의학물리팀 블로그, 교수 YouTube, 의과대학 방사선종양학교실, 연세암병원 방사선종양학과). 우측에 Seminar 최신 4건.
5. `publication`: Paper / Presentation / Patent 아이콘 3개 바로가기
6. 푸터

### 4.4 서브 페이지

- `sub_visual`: 서브 배너 이미지(`images/sub/sub_slogan.png`)
- 좌측 `snb`: 대메뉴 이름(예: INTRODUCTION) + 하위 메뉴 세로 목록, 현재 페이지 강조
- 우측 `contentBox`: 페이지 제목(`cnt_title`) + 홈 아이콘 브레드크럼(`loca`: 홈 > MEMBER > Researchers) + 본문

### 4.5 메뉴와 페이지 목록 (한글)

| 대메뉴 | 하위 메뉴 | 원본 | 유형 | 규모 |
|---|---|---|---|---|
| INTRODUCTION | welcome to MPBEL | sub1_1 | 고정 페이지 (HTML + 이미지 1) | 1 |
| | contact us | sub1_2 | 고정 페이지 (주소, 이메일, Google Maps iframe) | 1 |
| MEMBER | Professor | sub2_1 | 고정 페이지 (이름, 직함, 학력, 경력, 강의분야, 사진 1) | 1 |
| | Collaborators | sub2_2 | 멤버 카드 목록 | 수 명 |
| | Researchers | sub2_3 | 멤버 카드 목록, 카테고리 MPBEL / Affiliate | 약 30명, 2페이지 |
| | Alumni | sub2_4 | 멤버 카드 목록, 카테고리 Graduate / Former | 2페이지 |
| | Short-term internship | sub2_5 | 멤버 카드 목록 | 1페이지 |
| RESEARCH | Artificial Intelligence | sub3_2 | 고정 페이지 (긴 HTML, 그림 5) | 1 |
| | Radiation Therapy | sub3_3 | 고정 페이지 | 1 |
| | Particle Therapy | sub3_4 | 고정 페이지 | 1 |
| | (메뉴에 없음) Advanced CT Reconstruction | sub3_1 | 고정 페이지, 홈 카드에서만 링크 | 1 |
| PUBLICATION | Paper | sub4_1 | 출판물 목록, 연도 카테고리 2005~2025 | 약 182건 |
| | Presentation | sub4_2 | 출판물 목록, 연도 카테고리 | 약 285건 |
| | Invited talk | sub4_3 | 출판물 목록 | 수 건 |
| | Patent | sub4_4 | 출판물 목록 (등록국가, 등록번호, 등록일) | 약 8건 |
| LECTURE | Lecture | sub5_1 | 게시판 (제목, 강의날짜) | 2건 |
| NOTICE | News | sub6_1 | 게시판, 카테고리는 주제와 연도가 섞여 있음(연구실소식 31건, 학회소식 2건, 2025 등 일부 연도), 상단 고정 공지 1건, 본문 + 이미지 | 49건 |
| | Gallery | sub6_2 | 갤러리 | 62건 (1차 제외) |
| | Seminar | sub6_3 | 게시판, 연도 카테고리(비어 있는 해 있음, 예: 2020), 본문은 "Presenter: 이름" + 이미지 1 | 431건 |

참고: 영문 사이트에는 Research 아래 Intelligent Medical Imaging, Grant Lists가 더 있으나 한글 쪽 Grant Lists(sub3_5)는 오류 페이지다. 1차 범위 밖.

### 4.6 각 유형의 데이터 구조 (크롤러가 뽑아낼 필드)

- **멤버 카드**: 사진(202×150 썸네일, 원본은 `data/file/<board>/` 아래), 이름(한글 + 영문, 예: "양고운 Gowoon Yang"), 카테고리, `dl` 쌍들(E-mail, Research Interest, Grade, 소속 등 카드마다 다름). 정렬은 게시판마다 다르다(Researchers는 등록일 오름차순, Collaborators는 내림차순).
- **출판물 항목**: 연도(카테고리), 번호, 제목, 저자 문자열, 학술지/학회 정보(`text_journal` 안의 여러 `span`: 저널명, 권호/페이지, 발표 학회명, 장소, 날짜 등 유형별로 다름). 특허는 등록국가/등록번호/등록일.
- **뉴스 글**: 카테고리 문자열(주제 또는 연도, 혼합), 제목, 작성일, 본문 HTML(텍스트 + 이미지 URL). 목록 첫 행의 고정 공지는 모든 페이지에 반복 노출되므로 크롤러가 한 번만 수집한다.
- **세미나 글**: 카테고리 문자열(연도), 제목(보통 "YYYY/MM/DD [Research Seminar] 제목" 형식), 작성일, 본문("Presenter: 이름" + 이미지 URL 1개). 2025년 글은 작성일이 전부 12-31로 찍혀 있어 연말에 한 해치를 몰아 올리는 운영 패턴으로 보인다. 세미나 실제 날짜는 제목 앞의 YYYY/MM/DD에서 뽑는 것이 작성일보다 정확하다.
- **강의 글**: 제목, 강의날짜, 본문.

---

## 5. 새 사이트 설계

### 5.1 URL 구조

| 페이지 | 새 URL |
|---|---|
| 홈 | `/` |
| Welcome / Contact | `/introduction/welcome/`, `/introduction/contact/` |
| Professor / Collaborators / Researchers / Alumni / Internship | `/member/professor/`, `/member/collaborators/`, `/member/researchers/`, `/member/alumni/`, `/member/internship/` |
| Research 4종 | `/research/ct-reconstruction/`, `/research/ai/`, `/research/radiation-therapy/`, `/research/particle-therapy/` |
| Paper / Presentation / Invited talk / Patent | `/publication/paper/`, `/publication/presentation/`, `/publication/invited-talk/`, `/publication/patent/` |
| Lecture 목록 / 상세 | `/lecture/`, `/lecture/<slug>/` |
| News 목록 / 카테고리별 / 상세 | `/notice/news/`, `/notice/news/c/<category-slug>/`, `/notice/news/<slug>/` |
| Seminar 목록 / 카테고리별 / 상세 | `/notice/seminar/`, `/notice/seminar/c/<category-slug>/`, `/notice/seminar/<slug>/` |
| Gallery | `/notice/gallery/` (1차에는 "준비 중" 안내만) |
| 영문 | `/en/` 아래 같은 구조. 1차에는 `/en/` 한 페이지만 있고 "English page is being prepared" 안내 |

slug 규칙은 빌더가 정한다. 다만 같은 제목의 글이 여러 개 있어도 충돌하지 않아야 하고(세미나에 같은 제목이 반복됨), 한글 제목을 URL에 그대로 쓰지 않는다. 날짜 + 원본 글 번호(`wr_id`) 조합을 권장한다.

### 5.2 콘텐츠 모델

Astro content collections를 쓴다. **항목 하나가 파일 하나다.** 논문 182건이면 파일 182개다. 이유는 2.3 반목표: 두 사람이 동시에 글을 올려도 충돌하지 않아야 한다.

```
src/content/
  pages/          고정 페이지. welcome, contact, professor, research-* (마크다운, 필요하면 HTML 포함)
  members/        멤버 카드. 한 명이 파일 하나
  papers/         논문
  presentations/  학회 발표
  talks/          초청 강연
  patents/        특허
  lectures/       강의
  news/           뉴스
  seminars/       세미나
```

언어는 각 컬렉션 안에서 `ko/`, `en/` 하위 폴더로 나눈다. 1차에는 `en/` 폴더가 비어 있고(`.gitkeep`), 스키마와 라우팅만 두 언어를 받아들이도록 되어 있다.

각 컬렉션의 frontmatter 필드는 4.6의 데이터 구조를 그대로 담는다. 공통으로 다음을 둔다.

- `legacy_url`: 원본 글 주소. 나중에 대조용.
- `legacy_images`: 원본 글에 있던 이미지의 **경로** 목록(예: `/data/editor/2510/xxx.jpg`). 호스트명은 넣지 않는다. 도메인이 새 사이트로 넘어가면 `http://mpbel.yonsei.ac.kr/...` 전체 URL은 쓸모가 없어지기 때문이다. 2차 다운로드 스크립트는 베이스 URL(옛 서버 IP나 백업 폴더)을 설정값으로 받아 이 경로와 합친다. 1차에서 받은 이미지는 이 필드 대신 로컬 경로 필드(`photo`, `images`)로 들어간다.
- `order` 또는 `date`: 목록 정렬 기준. 원본 게시판의 정렬 순서를 보존한다.

정확한 스키마는 빌더가 크롤링 결과를 보고 확정한다. 단, 출판물의 학술지 정보처럼 항목마다 구성이 다른 필드는 억지로 쪼개지 말고 표시용 문자열 필드 하나(예: `venue`)에 줄바꿈 포함으로 담아도 된다. 크롤링 결과를 손으로 고쳐야 하는 상황을 피하는 쪽을 우선한다.

### 5.3 글 올리는 흐름 (운영)

1. 구성원이 저장소에서 `src/content/seminars/ko/` 폴더를 연다.
2. `_template.md`를 복사해 새 파일을 만든다. 파일명 규칙은 README에 있다.
3. frontmatter를 채우고 커밋한다. GitHub 웹 편집기든 로컬 git이든 상관없다.
4. GitHub Actions가 빌드해서 몇 분 안에 반영된다.
5. 빌드가 실패하면(필수 필드 누락 등) Actions 탭에 어떤 파일의 어떤 필드가 문제인지 뜬다. 스키마 검증 메시지가 그 역할을 하므로 스키마는 필수 필드를 명확히 한다.

README에는 종류별(세미나, 뉴스, 논문, 발표, 특허, 멤버 추가/수정, 졸업생으로 이동) 절차를 적는다. 한글로 쓴다. 뉴스와 세미나의 `category` 값은 기존 값 중 하나를 쓰거나 새 연도를 적으라고 안내한다. 목록 탭은 이 값에서 자동 생성되므로 새 값을 적으면 탭이 하나 늘어난다.

### 5.4 외관과 반응형

- 데스크톱에서는 지금 사이트와 같게 보인다. 원본 CSS를 참고해 색, 글꼴, 간격, 배경 이미지를 가져온다. jQuery는 쓰지 않는다. 드롭다운 메뉴는 CSS `:hover`와 소량의 바닐라 JS로 한다.
- 모바일 동작은 작성자가 정한 기본값이다.
  - 상단 메뉴: 햄버거 버튼으로 접고, 펼치면 대메뉴 아래 하위 메뉴가 세로로 나열된다.
  - 서브 페이지 좌측 메뉴: 본문 위로 올라가 가로 탭 또는 세로 목록이 된다.
  - 홈 연구 카드 4개: 세로로 쌓인다.
  - 홈 News/Seminar 두 칸: 세로로 쌓인다.
  - 멤버 카드: 한 줄에 1~2개.
  - 출판물 목록: 표가 아니라 줄바꿈되는 블록으로.
  - 배너 이미지: 폭에 맞춰 축소.
- 브레이크포인트 값과 세부 처리는 빌더가 정한다.
- 폰트는 지금처럼 Google Fonts에서 Lato와 Nanum Gothic을 불러온다. Font Awesome은 쓰이는 아이콘(홈, 확성기 등) 몇 개만 인라인 SVG로 대체한다.

### 5.5 목록 페이지 동작

- **출판물(Paper, Presentation, Invited talk, Patent)**: 한 페이지에 전체 항목을 연도 내림차순으로 나열하고, 연도별 소제목(`year_title`)으로 묶는다. 페이지 상단에 연도 링크 목록을 두어 해당 연도로 이동한다. 페이지네이션 없음. (현재는 15건씩 나뉘지만 정적 사이트에서는 한 페이지가 더 편하고 검색도 된다.)
- **News, Seminar**: 목록 상단에 카테고리 탭, 그 아래 목록. 탭은 frontmatter `category`의 고유값으로 자동 생성하며 현재 사이트의 카테고리 목록(뉴스는 주제와 연도가 섞인 상태 그대로)을 재현한다. 연도를 특별 취급하지 않는다. 전체 목록은 한 페이지당 일정 건수로 정적 페이지네이션한다(건수는 빌더가 정함, 20~30건 권장). 카테고리별 페이지도 같은 방식. 뉴스의 고정 공지는 전체 목록 첫 행에 고정한다. 상세 페이지는 제목, 날짜, 본문. 이전/다음 글 링크는 있으면 좋고 없어도 된다.
- **Lecture**: 2건뿐이므로 단순 목록 + 상세.
- **멤버**: 카테고리 탭(MPBEL/Affiliate, Graduate/Former)이 있는 게시판은 탭별 페이지 또는 한 페이지 안 섹션 구분. 상세 페이지는 만들지 않는다(현재 상세 페이지는 카드와 같은 정보).

### 5.6 크롤러

- 위치: `scripts/crawl/`. Python 3 표준 라이브러리 + `beautifulsoup4` 정도로 제한한다.
- 입력: `http://mpbel.yonsei.ac.kr` (HTTP). 출력: `src/content/**/ko/*.md`, `public/images/**`, `reference/`.
- 동작:
  - 게시판별로 모든 페이지(`page=N`)와 모든 연도 카테고리(`sca=`)를 순회해 항목을 빠짐없이 수집한다. 목록 페이지만으로 정보가 충분한 유형(출판물, 멤버)은 상세 페이지를 열지 않아도 된다. 뉴스/세미나/강의는 상세 페이지를 연다.
  - 요청 사이에 짧은 대기를 둔다(0.5초 정도). 학교 서버다.
  - 두 가지 모드가 있다. **전체 모드**는 모든 결과를 덮어쓴다(최초 1회). **추가 모드**는 이미 존재하는 마크다운 파일은 건드리지 않고 원본에 새로 생긴 글만 추가한다(`legacy_url` 또는 원본 글 번호로 판단). 옛 사이트에는 전환 직전까지 글이 더 올라올 수 있으므로(특히 연말 세미나 일괄 등록), 도메인 전환 직전에 추가 모드로 한 번 더 돌리는 단계를 운영 절차에 넣는다. 전환 후에는 크롤러를 돌리지 않는다는 점을 README에 적는다.
  - 원본 HTML을 `reference/html/`에 저장해 두어, 변환이 잘못됐을 때 재요청 없이 다시 변환할 수 있게 한다.
  - 1차 포함 이미지(5장 참조)는 받아서 `public/images/` 아래에 저장하고 frontmatter에 로컬 경로를 적는다. 멤버 사진은 썸네일이 아니라 원본을 받는다(원본 URL은 썸네일 파일명에서 `thumb-` 접두사와 `_202x150` 접미사를 제거하면 된다. 안 되면 썸네일로 대체).
  - 1차 제외 이미지(뉴스/세미나 본문, 갤러리)는 받지 않고 URL만 `legacy_images`에 적는다. 본문에서 해당 `<img>`는 제거한다.
  - 본문 HTML은 마크다운으로 변환하되, 연구 소개 페이지처럼 인라인 스타일이 많은 긴 HTML은 변환 품질이 떨어지면 HTML을 그대로 두어도 된다(Astro 마크다운은 HTML을 허용한다). 판단 기준은 "손으로 고치지 않아도 보기에 문제없는가"다.
  - 완료 후 수집 건수 요약을 출력한다(게시판별 건수). 이 숫자를 4.5 표의 규모와 대조해 누락을 확인한다.

### 5.7 배포

- GitHub Actions 워크플로: main 푸시 → `npm ci` → `astro build` → GitHub Pages 배포. Astro 공식 Pages 액션 사용.
- `public/CNAME`에 `mpbel.yonsei.ac.kr`.
- 저장소는 연구실 조직 `ympbel` 아래 공개 저장소 `ympbel.github.io`다. 이 이름이면 도메인 연결 전에도 `https://ympbel.github.io/`가 루트 경로라 `base` 전환 로직이 필요 없다. 도메인 연결 후에도 `base`는 `/`다.
- 저장소 생성과 Pages 설정은 `gh`로 한다. `gh`는 `yongdoyun` 계정으로 로그인되어 있고, 이 계정은 2026-10-28에 `ympbel` 조직의 member로 가입했다. 조직 설정상 멤버가 공개 저장소를 만들 수 있고, 만든 사람이 그 저장소의 admin이 되므로 Pages와 커스텀 도메인 설정까지 가능하다. 조직 수준의 도메인 소유 인증(선택 사항, 탈취 방지)은 owner만 할 수 있으므로, 가능하면 사용자가 People 탭에서 `yongdoyun`의 역할을 Owner로 올린다. 필수는 아니다.
- README에 담당자에게 전달할 DNS 요청 내용을 적는다: `mpbel.yonsei.ac.kr`에 대한 CNAME 레코드 → `ympbel.github.io`, 그리고 도메인 소유 확인용 TXT 레코드 `_github-pages-challenge-ympbel` (값은 GitHub Pages 도메인 설정 화면에서 나옴). HTTPS는 GitHub Pages가 자동 발급한다.

### 5.8 저장소 구조 (개요)

```
.
├── .github/workflows/deploy.yml
├── astro.config.mjs
├── package.json
├── README.md                 운영 안내 (한글)
├── docs/superpowers/specs/   이 문서
├── public/
│   ├── CNAME
│   └── images/               디자인 자산, 멤버 사진, 고정 페이지 이미지
├── reference/                원본 사이트 HTML/CSS/스크린샷 (빌드 제외, 대조용)
├── scripts/crawl/            크롤러
└── src/
    ├── content/              5.2 참조
    ├── content.config.ts     스키마
    ├── layouts/              BaseLayout, SubPageLayout
    ├── components/           Header, Nav, Footer, Snb, MemberCard, PubList ...
    ├── i18n/                 메뉴 라벨, 고정 문구 (ko, en)
    ├── pages/                5.1 라우팅
    └── styles/
```

---

## 6. 작성자가 정한 것 (사용자가 뒤집을 수 있음)

1. 멤버 프로필 사진과 고정 페이지 내 이미지는 1차에 포함한다. 사용자는 "사진은 나중에 내가" 라고 했지만, 이 이미지들은 수십 장이고 크롤러가 받기 쉬우며, 없으면 멤버 페이지와 연구 소개 페이지가 성립하지 않는다. 뉴스/세미나 본문 이미지와 갤러리만 미룬다.
2. 항목 하나 = 파일 하나. 논문처럼 많은 항목도 파일로 쪼갠다.
3. RESEARCH 메뉴는 지금처럼 3개(AI, Radiation Therapy, Particle Therapy)만 보이고, Advanced CT Reconstruction 페이지는 만들되 홈 카드에서만 링크한다. 현재 상태를 그대로 복제한 것이다. 메뉴에 넣고 싶으면 설정 한 줄로 바꿀 수 있게 한다.
4. 출판물 목록은 페이지네이션 없이 한 페이지에 연도별로 전부 보여준다.
5. 영문 토글을 누르면 `/en/`의 "준비 중" 페이지로 간다. 토글을 숨기지 않는다. 구조가 있다는 것을 보여 주고, 2차에서 콘텐츠만 채우면 되게 한다.
6. jQuery, bxslider, Font Awesome은 가져오지 않는다. 외관에 영향이 없다.
7. 설계 문서는 작업 폴더의 `docs/superpowers/specs/`에 둔다. 저장소 초기화는 구현 계획 단계에서 한다.
8. 크롤러 언어는 Python. 사이트 빌드와 분리되어 있고 한 번만 돌리는 도구라 Node로 통일할 이유가 없다.
9. 뉴스/세미나의 카테고리 탭은 현재 사이트 그대로 재현한다. 뉴스 카테고리가 주제와 연도가 섞여 있어도 정리하지 않는다. 정리는 사용자가 frontmatter 값을 바꾸면 되고 탭은 자동으로 따라온다. ("그대로" 원칙의 적용)
10. 크롤러에 추가 모드를 두고, 도메인 전환 직전 재크롤링을 절차에 넣는다. 옛 사이트가 전환 전까지 계속 갱신될 가능성에 대비한 것이다.
11. `legacy_images`에는 호스트명 없이 경로만 저장한다. 도메인 전환 후에도 옛 서버 IP나 백업 폴더에서 받을 수 있게 하기 위해서다.
12. 저장소 이름은 `ympbel.github.io`로 한다. 루트 경로 배포가 되어 스테이징 설정이 사라진다. 사용자는 조직 사용만 정했고 이름은 작성자 제안이다.
13. 공개 저장소다. 무료 조직 플랜에서 Pages는 공개 저장소에서만 동작한다. 멤버 이메일과 사진은 이미 공개 사이트에 있어 새로운 노출은 아니지만 git 이력에 남는다. `reference/` 폴더의 옛 사이트 원본 HTML도 공개된다.

---

## 7. 빌더에게 맡기는 것

- Astro 버전, 패키지 매니저, TypeScript 사용 여부
- 컴포넌트 분할, CSS 작성 방식(일반 CSS 권장, 프레임워크 불필요)
- 브레이크포인트 값과 모바일 세부 처리
- slug 생성 규칙 (5.1의 조건 안에서)
- 각 컬렉션의 정확한 frontmatter 스키마 (5.2의 원칙 안에서)
- 뉴스/세미나 페이지당 건수
- 크롤러 내부 구조, 재시도 처리, HTML→마크다운 변환 방식
- 테스트 범위. 최소한 (a) 스키마 검증이 빌드에서 돌고, (b) 크롤러 수집 건수가 4.5 표와 맞는지 확인하는 절차는 있어야 한다.

---

## 8. 2차 이후 (이 문서의 범위 밖, 연결 고리만)

- 갤러리 사진과 뉴스/세미나 본문 이미지 이전: `legacy_images`를 읽어 받는 스크립트. 사용자가 한다.
- 영문 콘텐츠: `src/content/*/en/`을 채우고 `/en/` 라우팅을 켠다.
- Git 기반 CMS(Decap, Sveltia)는 필요해지면 `/admin/` 정적 파일로 추가할 수 있다. 콘텐츠 구조를 바꿀 필요는 없다.
