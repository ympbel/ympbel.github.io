---
board: researchers | collaborators | alumni | internship  # 게시판. researchers(연구원), collaborators(공동연구자), alumni(졸업생), internship(단기 인턴십) 중 하나만 적고, 파일도 같은 이름의 폴더에 둡니다
category: 분류 이름  # (선택) 게시판 안의 분류 탭 (예: MPBEL, Affiliate, Graduate, Former). 분류가 없는 게시판이면 이 줄을 지우세요
name: 한글이름 English Name  # 화면에 보일 이름 (예: 양고운 Gowoon Yang). 필수
photo: /images/members/<게시판>/<파일이름>.jpg  # (선택) 사진 경로. 사진은 public/images/members/<게시판>/ 에 넣고 /images/... 로 적습니다. 없으면 이 줄을 지우세요
fields:  # 이름 아래에 표시할 항목 목록. 적은 순서대로 표시되며, 항목이 없으면 fields: [] 로 적습니다
  - label: 항목 이름  # 항목 이름 (예: E-mail). 이름 없이 내용만 적으려면 label: '' 로 적습니다
    value: 항목 내용  # 항목 내용 (예: M.D., Ph.D. Candidate)
order: N  # 게시판 안에서의 표시 순서. 정수(1, 2, 3 …)이며 작은 수가 먼저 나옵니다
legacy_url: http://mpbel.yonsei.ac.kr/...  # (선택) 옛 사이트 주소. 크롤러가 채우는 값이므로 새로 만들 때는 이 줄을 지우세요
legacy_id: N  # (선택) 옛 사이트 글 번호(정수). 크롤러가 채우는 값이므로 새로 만들 때는 이 줄을 지우세요
---

이 파일은 구성원 템플릿입니다. 이 파일을 복사해 `src/content/members/ko/<게시판>/<영문-이름>.md` 새 파일을 만들고, 위 값을 실제 값으로 바꾼 뒤 필요 없는 줄과 이 문단을 지우세요. `_`로 시작하는 파일은 사이트에 포함되지 않습니다.
