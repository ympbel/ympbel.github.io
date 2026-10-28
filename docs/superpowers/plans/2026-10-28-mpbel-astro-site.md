# MPBEL Astro Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace http://mpbel.yonsei.ac.kr (Gnuboard5) with a look-alike, responsive Astro static site on GitHub Pages whose Korean content is crawled from the live site into one-markdown-file-per-entry collections.

**Architecture:** A Python crawler (`scripts/crawl/`) fetches the public HTTP site, caches raw HTML under `reference/`, and writes markdown entries into `src/content/<collection>/ko/` plus images into `public/images/`. An Astro 7 site reads those collections, reproduces the original DOM structure and class names so the original CSS (copied into `src/styles/legacy/`) applies unchanged, and adds a responsive layer. GitHub Actions builds and deploys `main` to `ympbel/ympbel.github.io`.

**Tech Stack:** Node 26 (CI: Node 24), npm, Astro ^7.4.2, `astro/zod` (Zod 4), `cheerio@1.2.0` + `node:test` for built-output tests; Python 3.14 venv with `beautifulsoup4==4.15.0`, `PyYAML==6.0.3`, `markdownify==1.2.3`, `pytest`; GitHub Actions `withastro/action@v6`, `actions/checkout@v7`, `actions/deploy-pages@v5`.

**Spec:** `docs/superpowers/specs/2026-10-28-mpbel-astro-site-design.md`

## Global Constraints

- Repository: `ympbel/ympbel.github.io`, public, default branch `main`, Pages source = GitHub Actions. `astro.config.mjs` has `site: 'https://ympbel.github.io'` and **no `base`** until cutover (then `site: 'https://mpbel.yonsei.ac.kr'` + `public/CNAME`). Do **not** add `public/CNAME` before cutover: it would redirect the preview URL to a domain that does not resolve yet.
- Korean only in phase 1. Every collection is read from `src/content/<collection>/ko/`; `src/content/<collection>/en/.gitkeep` exists; `src/pages/en/index.astro` is the only English page.
- One entry = one markdown file. Never a single aggregate file per collection.
- Files whose basename starts with `_` (templates) are excluded from every collection: `glob({ pattern: ['**/*.md', '!**/_*.md'], base: './src/content/<name>' })`.
- Same look: components reproduce the original element structure and class names (`topmenu`, `nav`, `sub_visual`, `snb`, `contentBox`, `cnt_title`, `loca`, `mb_peple`, `publication_oldver`, `tb_basic_s`, `bo_list`, `lat`, `lt_date`, etc.) so the copied CSS applies. The footer text is kept verbatim except the trailing `Design by DSSO` link and its separating spaces are removed. Fonts stay Google Fonts `Lato:300,400,700` and `Nanum Gothic`.
- No jQuery, bxslider or Font Awesome. The two Font Awesome icons that remain visible (bullhorn for pinned rows, home icon is an image already) are replaced by inline SVG or text.
- Crawler talks to `http://mpbel.yonsei.ac.kr` over plain HTTP, waits 0.5 s between network requests, sends `User-Agent: mpbel-migration-crawler/1.0`, and never runs after cutover. `legacy_url` keeps the full original URL; `legacy_images` / `legacy_files` keep **paths only** (no host).
- Internal links are absolute from site root and end with `/` (e.g. `/member/researchers/`). Astro default `build.format: 'directory'`.
- Dates in frontmatter are strings `YYYY-MM-DD`. Years are integers.
- Deferred (do not build): English content, gallery board content, news/seminar body images, comments, search, hit counts, old-URL redirects.

## Review Focus

1. Frontmatter values containing YAML-significant characters (a title like `A: B "C" #1`, an author list with leading `*`) must round-trip through the crawler writer and Astro's parser unchanged. Test in Task 3 (`test_write_entry_quotes_special_characters`).
2. Member `dd` cells pasted from Word contain nested `<dd>`, `<p>`, `<span style=...>`; the card must show plain text with single spaces, not raw tags or `&nbsp;` runs. Test in Task 5 (`test_fields_flatten_nested_html`).
3. Publication rows vary: no LINK row, a `공지` pinned row whose year is not on the row, patent rows with label spans, empty `text_vol` spans. The parser must not skip or misalign rows. Tests in Task 6 (`test_row_without_link`, `test_pinned_row_detected`, `test_patent_venue_labels`).
4. Seminar/news titles are truncated with `…` in list and view headings; the full title is only in `<title>`. A title that itself contains ` > ` or ` | ` must survive. Test in Task 7 (`test_title_from_title_tag_with_separators`). Pinned notices repeat on every list page; they must be collected once (`test_pinned_row_deduplicated` in Task 7).
5. Category values can be Korean (`연구실소식`), numeric (`2025`), contain spaces or `/`; category URLs must be valid single path segments and tabs must list numeric years descending before other names. Tests in Task 2 (`categorySlug`, `categoriesOf`) and Task 13 (dist test on `/notice/news/c/연구실소식/`).

---

## File Structure

```
.
├── .github/workflows/deploy.yml          Task 1
├── .gitignore  .nvmrc  package.json  astro.config.mjs  tsconfig.json   Task 1
├── README.md                             Task 1 stub, Task 15 full 운영 안내
├── public/
│   ├── favicon.svg                       Task 1
│   └── images/
│       ├── site/      (logo, banners, icons; from /images and /img)   Task 3 (assets) 
│       ├── pages/<slug>/                 Task 4
│       └── members/<board>/<wr_id>.<ext> Task 5
├── reference/                            raw HTML + CSS from the old site (committed, build-excluded)
│   ├── html/  css/                       Task 3
├── scripts/crawl/
│   ├── requirements.txt  README.md       Task 3
│   ├── crawl/__init__.py  __main__.py  config.py  fetch.py  markdown.py  assets.py   Task 3
│   ├── crawl/parse_common.py  parse_pages.py                             Task 4
│   ├── crawl/parse_members.py                                            Task 5
│   ├── crawl/parse_publications.py                                       Task 6
│   ├── crawl/parse_posts.py                                              Task 7
│   ├── crawl/run.py        (orchestrates kinds, full/add modes, summary) Task 3 skeleton, filled 4–8
│   └── tests/fixtures/*.html  tests/test_*.py                            Tasks 3–7
├── src/
│   ├── content.config.ts                 Task 2
│   ├── content/schemas.ts                Task 2
│   ├── content/{pages,members,papers,presentations,talks,patents,news,seminars,lectures}/{ko,en}/   Task 2 (+ _template.md)
│   ├── lib/content.ts                    Task 2  (locale/slug helpers, sorters, categories)
│   ├── lib/menu.ts                       Task 9  (menu tree, section lookup)
│   ├── i18n/ko.ts  en.ts  index.ts       Task 9
│   ├── styles/legacy/*.css  responsive.css  global.css     Task 9 (legacy+global), Task 14 (responsive)
│   ├── layouts/BaseLayout.astro          Task 9
│   ├── layouts/SubLayout.astro           Task 10
│   ├── components/Header.astro Footer.astro LatestList.astro   Task 9
│   ├── components/Snb.astro Breadcrumb.astro                   Task 10
│   ├── components/MemberCard.astro MemberList.astro CategoryTabs.astro   Task 11
│   ├── components/PubList.astro                                Task 12
│   ├── components/PostTable.astro Pagination.astro BoardPage.astro PostView.astro   Task 13
│   └── pages/
│       ├── index.astro                   Task 9
│       ├── introduction/welcome.astro contact.astro            Task 10
│       ├── member/professor.astro        Task 10
│       ├── research/[slug].astro         Task 10
│       ├── member/[board].astro          Task 11
│       ├── publication/[kind].astro      Task 12
│       ├── notice/[board]/index.astro  page/[page].astro  c/[category]/index.astro  c/[category]/page/[page].astro  [slug].astro   Task 13
│       ├── notice/gallery.astro  lecture/index.astro  lecture/[slug].astro          Task 13
│       └── en/index.astro  404.astro     Task 14
└── tests/
    ├── unit/*.test.ts                    Task 2 (run with `node --test`, Node type-stripping)
    └── dist/*.test.mjs  dist/helpers.mjs Task 9+ (cheerio over dist/)
```

Responsibilities: `schemas.ts` is the single source of frontmatter truth (crawler output must satisfy it; tests import it directly). `lib/content.ts` holds every ordering/grouping rule so pages stay declarative. `lib/menu.ts` is the one place that knows the six menus, their sub items and hrefs; `Header`, `Snb`, `Breadcrumb` all read it. The crawler's `config.py` is the one place that maps old `bo_table`s to collections and slugs.

---

### Task 1: Repository, Astro scaffold, GitHub Pages deploy

**Files:**
- Create: `package.json`, `astro.config.mjs`, `tsconfig.json`, `.gitignore`, `.nvmrc`, `README.md`, `public/favicon.svg`, `src/pages/index.astro`, `.github/workflows/deploy.yml`

**Interfaces:**
- Produces: npm scripts `dev`, `build`, `preview`, `test:unit`, `test:dist`, `test`; the GitHub repo `ympbel/ympbel.github.io` on `main`; live URL `https://ympbel.github.io/`.

- [ ] **Step 1: Create the GitHub repository and local git repo**

Run from the project folder `/Users/yongdo/Documents/Code_MBA/Claude_workspace/Website_20261028`:
```bash
git init -b main
gh repo create ympbel/ympbel.github.io --public --description "Yonsei Medical Physics and Biomedical Engineering Lab website" --source . --remote origin
```
Expected: `gh repo view ympbel/ympbel.github.io --json name,visibility` prints `"visibility":"PUBLIC"`.

- [ ] **Step 2: Scaffold Astro by hand (no interactive `create astro`)**

`package.json`:
```json
{
  "name": "ympbel.github.io",
  "private": true,
  "type": "module",
  "engines": { "node": ">=22.23.4" },
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "test:unit": "node --test tests/unit/",
    "test:dist": "node --test tests/dist/",
    "test": "npm run test:unit && npm run build && npm run test:dist"
  }
}
```
Then `npm install astro@^7.4.2` and `npm install -D cheerio@1.2.0`.

`astro.config.mjs`:
```js
import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://ympbel.github.io',
  i18n: { defaultLocale: 'ko', locales: ['ko', 'en'], routing: { prefixDefaultLocale: false } },
});
```
`tsconfig.json`: `{ "extends": "astro/tsconfigs/base", "include": [".astro/types.d.ts", "**/*"], "exclude": ["dist", "scripts", "reference"] }`.
`.nvmrc`: `24`. `.gitignore`: `node_modules/`, `dist/`, `.astro/`, `scripts/crawl/.venv/`, `__pycache__/`, `.pytest_cache/`, `.DS_Store`.
`src/pages/index.astro`: minimal page with `<title>MPBEL | 연세 의학물리 및 의공학 연구실</title>` and `<h1>MPBEL</h1>` (replaced in Task 9).
`README.md`: title line + "구축 중" (replaced in Task 15).
`public/favicon.svg`: any single-color "M" glyph SVG.

- [ ] **Step 3: Verify the build**

Run: `npm run build`
Expected: exit 0 and `dist/index.html` exists (`test -f dist/index.html && echo ok`).

- [ ] **Step 4: Add the deploy workflow**

`.github/workflows/deploy.yml` exactly:
```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: withastro/action@v6
        with:
          node-version: 24
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
```

- [ ] **Step 5: Commit and push**

```bash
git add -A
git commit -m "chore: scaffold Astro site and Pages deploy workflow"
git push -u origin main
```

- [ ] **Step 6: Set the Pages source to GitHub Actions and verify the live URL**

```bash
gh api -X POST repos/ympbel/ympbel.github.io/pages -f build_type=workflow 2>/dev/null || gh api -X PUT repos/ympbel/ympbel.github.io/pages -f build_type=workflow
gh run watch $(gh run list --workflow deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId') --exit-status
curl -s -o /dev/null -w '%{http_code}\n' https://ympbel.github.io/
```
Expected: run exits 0; curl prints `200` (retry up to 5 times, 30 s apart, the first deploy can lag).

---

### Task 2: Content schemas, collections, templates, content helpers

**Files:**
- Create: `src/content/schemas.ts`, `src/content.config.ts`, `src/lib/content.ts`
- Create: `src/content/<c>/ko/_template.md` for c in members, papers, presentations, talks, patents, news, seminars, lectures; `src/content/<c>/en/.gitkeep` for all nine collections (pages too); `src/content/pages/ko/.gitkeep`
- Test: `tests/unit/schemas.test.ts`, `tests/unit/content.test.ts`

**Interfaces:**
- Produces (schemas.ts, all exported):
  - `pageSchema = z.object({ title: z.string(), section: z.enum(['home','introduction','member','research']), images: z.array(z.string()).default([]), links: z.array(z.object({ label: z.string(), url: z.string() })).default([]), legacy_url: z.string().optional() })`
  - `memberSchema = z.object({ board: z.enum(['researchers','collaborators','alumni','internship']), category: z.string().optional(), name: z.string().min(1), photo: z.string().optional(), fields: z.array(z.object({ label: z.string().default(''), value: z.string() })).default([]), order: z.number().int(), legacy_url: z.string().optional(), legacy_id: z.number().int().optional() })`
  - `publicationSchema = z.object({ year: z.number().int().min(1990).max(2100), title: z.string().min(1), authors: z.string().default(''), venue: z.string().default(''), link: z.string().optional(), pinned: z.boolean().default(false), order: z.number().int().optional(), legacy_files: z.array(z.object({ name: z.string(), url: z.string() })).default([]), legacy_url: z.string().optional(), legacy_id: z.number().int().optional() })`
  - `postSchema = z.object({ title: z.string().min(1), date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/), category: z.string().optional(), pinned: z.boolean().default(false), presenter: z.string().optional(), event_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(), legacy_images: z.array(z.string()).default([]), legacy_files: z.array(z.object({ name: z.string(), url: z.string() })).default([]), legacy_url: z.string().optional(), legacy_id: z.number().int().optional() })`
- Produces (content.config.ts): collections `pages`(pageSchema), `members`(memberSchema), `papers`/`presentations`/`talks`/`patents`(publicationSchema), `news`/`seminars`/`lectures`(postSchema), each `glob({ pattern: ['**/*.md', '!**/_*.md'], base: './src/content/<name>' })`.
- Produces (lib/content.ts, pure TS, no `astro:content` runtime import):
  - `type Locale = 'ko' | 'en'`
  - `localeOf(id: string): Locale` — first path segment; `slugOf(id: string): string` — the rest joined by `/`.
  - `isLocale(locale: Locale): (e: { id: string }) => boolean`
  - `sortMembers<T extends { data: { order: number }; id: string }>(a: T[]): T[]` — `order` asc, tie `id` asc.
  - `sortPublications<T extends { data: { year: number; order?: number }; id: string }>(a: T[]): T[]` — `year` desc, then `order` desc with missing order treated as `Infinity`, tie `id` desc.
  - `groupByYear<T extends { data: { year: number } }>(a: T[]): Array<{ year: number; items: T[] }>` — preserves input order, years in first-seen order.
  - `sortPosts<T extends { data: { date: string; legacy_id?: number }; id: string }>(a: T[]): T[]` — `date` desc, then `legacy_id` desc (missing = `Infinity`), tie `id` desc.
  - `categoriesOf(posts: Array<{ data: { category?: string } }>): string[]` — distinct non-empty values; all-digit values first sorted desc numerically, then the rest sorted with `localeCompare('ko')`.
  - `categorySlug(category: string): string` — trim, replace `/` and whitespace runs with `-`; result used verbatim as the path segment (Korean allowed).
  - `paginateArray<T>(items: T[], size: number): T[][]`; `PAGE_SIZE = 20`.

- [ ] **Step 1: Write failing unit tests**

`tests/unit/schemas.test.ts` (import `{ memberSchema, publicationSchema, postSchema, pageSchema } from '../../src/content/schemas.ts'`):
- `test('member requires name and order')`: `memberSchema.safeParse({ board: 'researchers', order: 1 }).success === false`; with `name: '양고운 Gowoon Yang'` → success and `data.fields` deep-equals `[]`.
- `test('publication coerces defaults')`: parse `{ year: 2025, title: 'T' }` → `authors === ''`, `pinned === false`, `legacy_files` deep-equals `[]`; `{ year: '2025', title: 'T' }` → `success === false`.
- `test('post date format')`: `{ title: 'x', date: '2025-10-22' }` ok; `{ title: 'x', date: '25-10-22' }` fails; `event_date: '2018.04.19'` fails.
- `test('page section enum')`: `section: 'research'` ok; `section: 'notice'` fails.

`tests/unit/content.test.ts` (import from `../../src/lib/content.ts`):
- `localeOf('ko/researchers/gowoon-yang-19') === 'ko'`, `slugOf(...) === 'researchers/gowoon-yang-19'`.
- `sortPublications`: given `[{id:'a',data:{year:2024,order:5}},{id:'b',data:{year:2025}},{id:'c',data:{year:2025,order:9}}]` → ids `['b','c','a']`.
- `groupByYear` of that sorted list → `[{year:2025,items:[b,c]},{year:2024,items:[a]}]`.
- `sortPosts`: `[{id:'x',data:{date:'2025-01-01',legacy_id:1}},{id:'y',data:{date:'2025-01-01'}},{id:'z',data:{date:'2025-02-01',legacy_id:3}}]` → `['z','y','x']`.
- `categoriesOf([{data:{category:'연구실소식'}},{data:{category:'2024'}},{data:{}},{data:{category:'2025'}},{data:{category:'학회소식'}},{data:{category:'2024'}}])` → `['2025','2024','연구실소식','학회소식']`.
- `categorySlug(' A / B  C ') === 'A-B-C'`; `categorySlug('연구실소식') === '연구실소식'`.
- `paginateArray([1,2,3,4,5], 2)` → `[[1,2],[3,4],[5]]`; `paginateArray([], 2)` → `[[]]` (one empty page so an empty board still renders page 1).

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm run test:unit`
Expected: failures with `Cannot find module` for both source files.

- [ ] **Step 3: Implement `src/content/schemas.ts` and `src/lib/content.ts`** with the signatures above. Import `z` from `'astro/zod'`.

- [ ] **Step 4: Run unit tests to verify they pass**

Run: `npm run test:unit` → all pass.

- [ ] **Step 5: Add `src/content.config.ts`, the nine collection folders, templates, and verify template exclusion**

Each `_template.md` carries every schema field with placeholder values that would **fail** the schema if parsed (e.g. `year: YYYY`, `date: YYYY-MM-DD`, `order: N`) plus a Korean comment block explaining each field. Then:

Run: `npx astro sync`
Expected: exit 0 with no validation errors (proves `!**/_*.md` excludes templates; if templates were loaded, `year: YYYY` would fail).

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: content schemas, collections, templates and content helpers"
```

---

### Task 3: Crawler skeleton: config, fetcher with cache, markdown writer, site assets, fixtures

**Files:**
- Create: `scripts/crawl/requirements.txt`, `scripts/crawl/README.md`, `scripts/crawl/crawl/__init__.py`, `__main__.py`, `config.py`, `fetch.py`, `markdown.py`, `assets.py`, `run.py`
- Create fixtures by fetching once with the fetcher: `scripts/crawl/tests/fixtures/{index,sub1_1,sub2_1,sub3_1,sub2_3_p1,sub2_3_p2,sub2_2,sub2_4,sub2_5,sub4_1_2025,sub4_3,sub4_4,sub6_1_p1,sub6_1_p2,sub6_3_p1,sub5_1,view_sub6_1_92,view_sub6_3_471,view_sub5_1_1,view_sub4_3_3}.html`
- Test: `scripts/crawl/tests/test_fetch.py`, `test_markdown.py`, `test_config.py`

**Interfaces:**
- `config.py`: `BASE_URL = "http://mpbel.yonsei.ac.kr"`; `@dataclass(frozen=True) class BoardSpec: table: str; kind: Literal['page','members','publication','posts']; collection: str; slug: str | None = None; board: str | None = None; name: str = ''` (name = board title shown in `<title>`, e.g. `Seminar`); `BOARDS: list[BoardSpec]` with exactly these 18 entries (table, kind, collection, slug, board, name):

  | table | kind | collection | slug | board | name |
  |---|---|---|---|---|---|
  | sub1_1 | page | pages | welcome | – | Welcome to MPBEL |
  | sub1_2 | page | pages | contact | – | Contact us |
  | sub2_1 | page | pages | professor | – | Professor |
  | sub3_1 | page | pages | research-ct-reconstruction | – | Advanced CT Reconstruction |
  | sub3_2 | page | pages | research-ai | – | Medical Artificial Intelligence |
  | sub3_3 | page | pages | research-radiation-therapy | – | Radiation Therapy |
  | sub3_4 | page | pages | research-particle-therapy | – | Particle Therapy |
  | sub2_3 | members | members | – | researchers | Researchers |
  | sub2_2 | members | members | – | collaborators | Collaborators |
  | sub2_4 | members | members | – | alumni | Alumni |
  | sub2_5 | members | members | – | internship | Short-term internship |
  | sub4_1 | publication | papers | – | – | Paper |
  | sub4_2 | publication | presentations | – | – | Presentation |
  | sub4_3 | publication | talks | – | – | Invited talk |
  | sub4_4 | publication | patents | – | – | Patent |
  | sub6_1 | posts | news | – | – | News |
  | sub6_3 | posts | seminars | – | – | Seminar |
  | sub5_1 | posts | lectures | – | – | Lecture |
  - `PAGE_SECTION = {'welcome':'introduction','contact':'introduction','professor':'member','research-ct-reconstruction':'research','research-ai':'research','research-radiation-therapy':'research','research-particle-therapy':'research'}`
  - `board_url(table: str, **params) -> str` → `f"{BASE_URL}/bbs/board.php?bo_table={table}"` + `&k=v` for each param (values URL-encoded).
- `fetch.py`: `class Fetcher: __init__(self, cache_dir: Path, delay: float = 0.5, offline: bool = False, user_agent: str = 'mpbel-migration-crawler/1.0')`; `get(url: str) -> str` (UTF-8 text; cache file name = `cache_name(url)`; offline=True raises `FileNotFoundError` on miss and never touches the network); `get_bytes(url: str) -> bytes` (same cache, binary); `resolve_redirect(url: str) -> str | None` (one request with redirects disabled, returns `Location` header or None; cached in `cache_dir/redirects.json`); `cache_name(url: str) -> str` → `bbs_board_bo_table=sub6_3&page=2.html` style: path with `/` → `_`, query kept, characters outside `[A-Za-z0-9._=&%-]` → `_`.
- `markdown.py`: `write_entry(path: Path, frontmatter: dict, body: str) -> None` (YAML via `yaml.safe_dump(allow_unicode=True, sort_keys=False, default_flow_style=False, width=1000)`, file = `---\n<yaml>---\n\n<body>\n`); `read_frontmatter(path: Path) -> dict`; `slugify(text: str, max_words: int = 6) -> str` (NFKD → ASCII letters/digits, lowercase, words joined by `-`, at most `max_words` words, `'entry'` if empty); `html_to_markdown(html: str) -> str` (markdownify with `heading_style='ATX'`, `strip=['span','font']`, then collapse 3+ newlines to 2).
- `assets.py`: `download(fetcher: Fetcher, url: str, dest: Path) -> Path` (skip if `dest` exists); `site_asset_urls(html_docs: list[str], css_docs: list[str]) -> set[str]` (every `<img src>` and CSS `url(...)` that resolves under `/images/` or `/img/`, absolutized against BASE_URL, `../` resolved); `local_path_for_site_asset(url: str) -> str` → `/images/site/<path after /images/ or /img/>` with `/img/` assets placed under `/images/site/img/`; `copy_reference_css(fetcher, out_dir: Path)` downloads these CSS files into `reference/css/`: `css/default.css`, `css/design.css`, `skin/latest/basic/style.css`, `skin/board/html/style.css`, `skin/board/Student/css/style.css`, `skin/board/collaborators/css/style.css`, `skin/board/alumni/css/style.css`, `skin/board/patent/style.css`, `skin/board/patent2/style.css`, `skin/board/patent3/style.css`, `skin/board/lecture/style.css`, `skin/board/basic/style.css`, `skin/board/gallery/style.css`.
- `run.py`: `main(argv) -> int` parsing `--mode {full,add}` (default full), `--only` (comma list of `pages,members,publications,posts,assets`; default all), `--out` (repo root, default `../..` relative to `scripts/crawl`), `--offline`. Dispatch table `KIND_RUNNERS: dict[str, Callable[[Context], Summary]]` where `@dataclass class Context: fetcher: Fetcher; out: Path; mode: str` and `Summary = dict[str, int]` (collection → files written). Prints a table `collection  written  skipped` at the end. In this task only `assets` is implemented; the others raise `NotImplementedError` and are filled in Tasks 4–7.
- `__main__.py`: `sys.exit(main(sys.argv[1:]))`.

- [ ] **Step 1: Create the venv and requirements**

`scripts/crawl/requirements.txt`: `beautifulsoup4==4.15.0`, `PyYAML==6.0.3`, `markdownify==1.2.3`, `pytest`.
Run: `python3 -m venv scripts/crawl/.venv && scripts/crawl/.venv/bin/pip install -r scripts/crawl/requirements.txt`
Expected: `scripts/crawl/.venv/bin/python -c "import bs4, yaml, markdownify"` exits 0.

- [ ] **Step 2: Write failing tests**

`tests/test_config.py`: `test_all_boards_unique_tables` (18 specs, tables unique), `test_board_url_encodes_params` (`board_url('sub6_1', sca='연구실소식', page=2)` ends with `bo_table=sub6_1&sca=%EC%97%B0%EA%B5%AC%EC%8B%A4%EC%86%8C%EC%8B%9D&page=2`).
`tests/test_fetch.py`: `test_cache_name` (`cache_name('http://mpbel.yonsei.ac.kr/bbs/board.php?bo_table=sub6_3&page=2') == 'bbs_board.php_bo_table=sub6_3&page=2.html'`); `test_offline_reads_cache_and_misses_raise` (write a file at the cache name in `tmp_path`, `Fetcher(tmp_path, offline=True).get(url)` returns it; unknown URL raises `FileNotFoundError`).
`tests/test_markdown.py`: `test_write_entry_quotes_special_characters` (frontmatter `{'title': 'A: B "C" #1', 'authors': '* Kim, Lee'}` → `read_frontmatter` returns identical dict and file starts with `---\n`); `test_slugify` (`slugify('Anatomical Position-Guided Auto-segmentation and Dosimetric Evaluation', 5) == 'anatomical-position-guided-auto-segmentation-and'`, `slugify('양고운') == 'entry'`, `slugify('양고운 Gowoon Yang') == 'gowoon-yang'`); `test_html_to_markdown_strips_spans` (`'<p><span style="x">Hi</span> <b>there</b></p>'` → `'Hi **there**'`).

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd scripts/crawl && .venv/bin/python -m pytest -q`
Expected: ImportError/ModuleNotFoundError failures.

- [ ] **Step 4: Implement `config.py`, `fetch.py`, `markdown.py`** per the interfaces. `fetch.py` uses `urllib.request` only; `time.sleep(delay)` before every network request; three retries with doubling delay on `URLError`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts/crawl && .venv/bin/python -m pytest -q` → all pass.

- [ ] **Step 6: Capture fixtures and reference HTML with the real fetcher**

Write `scripts/crawl/tests/make_fixtures.py` that uses `Fetcher(Path('../../reference/html'))` to fetch the URLs below and copy each into `tests/fixtures/<name>.html`:
`index` = `BASE_URL/index.php`; `sub1_1`, `sub2_1`, `sub3_1`, `sub2_2`, `sub2_4`, `sub2_5`, `sub4_3`, `sub4_4`, `sub5_1` = `board_url(table)`; `sub2_3_p1`/`sub2_3_p2` = `board_url('sub2_3', page=1|2)`; `sub4_1_2025` = `board_url('sub4_1', sca='2025')`; `sub6_1_p1`/`sub6_1_p2` = `board_url('sub6_1', page=1|2)`; `sub6_3_p1` = `board_url('sub6_3', page=1)`; `view_sub6_1_92` = `board_url('sub6_1', wr_id=92)`; `view_sub6_3_471` = `board_url('sub6_3', wr_id=471)`; `view_sub5_1_1` = `board_url('sub5_1', wr_id=1)`; `view_sub4_3_3` = `board_url('sub4_3', wr_id=3)`.
Run it: `cd scripts/crawl && .venv/bin/python tests/make_fixtures.py`
Expected: 20 fixture files, each > 5 KB, and `grep -l 'bo_v_title' tests/fixtures/view_*.html` lists the three post views.

- [ ] **Step 7: Implement `assets.py` and the `assets` runner in `run.py`**

Test first in `tests/test_assets.py`: `test_site_asset_urls_resolves_relative` (HTML `<img src="../images/main/slogan.png">` and CSS `url(../img/btn_next.gif)` → `{BASE_URL+'/images/main/slogan.png', BASE_URL+'/img/btn_next.gif'}`); `test_local_path_for_site_asset` (`…/images/main/slogan.png` → `/images/site/main/slogan.png`; `…/img/btn_next.gif` → `/images/site/img/btn_next.gif`). Run → fail → implement → pass.
The `assets` runner feeds `site_asset_urls` with `html_docs` = the 20 fixture files and `css_docs` = the 13 reference CSS files (downloaded first by `copy_reference_css`). Then run the real thing: `cd scripts/crawl && .venv/bin/python -m crawl --only assets`
Expected: `public/images/site/logo.png`, `public/images/site/main/slogan.png`, `public/images/site/sub/sub_slogan.png`, `public/images/site/main/ico_more.png` exist; `reference/css/` holds the 13 CSS files; summary line `assets  <n>  0` with n ≥ 25.

- [ ] **Step 8: Write `scripts/crawl/README.md`** (Korean): venv setup, the two modes, `--only`, "전환 후에는 실행 금지", where output goes.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat(crawl): fetcher, config, markdown writer, site assets and fixtures"
```

---

### Task 4: Static pages crawler (welcome, contact, professor, research ×4, home)

**Files:**
- Create: `scripts/crawl/crawl/parse_common.py`, `scripts/crawl/crawl/parse_pages.py`
- Modify: `scripts/crawl/crawl/run.py` (implement `pages` runner)
- Test: `scripts/crawl/tests/test_parse_pages.py`

**Interfaces:**
- `parse_common.py`: `soup(html: str) -> BeautifulSoup` (`html.parser`); `page_count(s) -> int` (max `page=` value among `.pg_wrap a.pg_page[href]`, else 1); `categories(s) -> list[str]` (`#bo_cate_ul a` texts, stripped, in page order); `wr_id_of(href: str) -> int | None`; `path_of(url: str) -> str` (strip scheme+host; `../images/x` → `/images/x`; decode `fn=` of `view_image.php` links); `clean_text(el) -> str` (`get_text(' ', strip=True)`, `\xa0`→space, collapse whitespace); `full_title(s) -> str` (text of `<title>` with the suffix from the last ` > ` **that is followed by a board name and ` | MPBEL`** removed: implement as `re.sub(r'\s*>\s*[^>|]+\s*\|\s*MPBEL.*$', '', title)` and if no match, `re.sub(r'\s*\|\s*MPBEL.*$', '', title)`).
- `parse_pages.py`: `@dataclass class StaticPage: body_html: str; image_urls: list[str]` (the page title comes from `BoardSpec.name`); `parse_static_page(html: str) -> StaticPage` — locate `div.contents table.board_list td` (first `td`); drop `style`, `script`, comments and the `form#fboardlist` wrapper (keep its inner content); `image_urls` = absolutized `img[src]` in document order; `body_html` = inner HTML with each `img[src]` rewritten by the caller-supplied mapping (see `rewrite_images`). `rewrite_images(body_html: str, mapping: dict[str, str]) -> str` replaces every `src` whose absolutized URL is a key with the local path. `@dataclass class HomePage: about_html: str; links: list[tuple[str, str]]`; `parse_home(html: str) -> HomePage` — `about_html` = inner HTML of `div.about div.txt`; `links` = `(clean_text(a), a['href'])` for `div.link ul li a`.
- `run.py` pages runner: for each `BoardSpec(kind='page')` fetch `board_url(table)`, parse, download each image to `public/images/pages/<slug>/<basename>` via `assets.download`, write `src/content/pages/ko/<slug>.md` with frontmatter `{title, section: PAGE_SECTION[slug], images: [local paths], legacy_url}` and body = rewritten HTML. Also fetch `BASE_URL/index.php`, write `src/content/pages/ko/home.md` with `{title: 'MPBEL', section: 'home', links: [{label,url}…]}` and body = `about_html`. In `add` mode pages are **always rewritten** (they are singletons; document this in README).

- [ ] **Step 1: Write failing tests** on fixtures:
  - `test_full_title_strips_suffix`: from `view_sub6_3_471` → `'2025/12/29 [Research Seminar] Group Sparse Algorithm for RBE-Weighted Dose Optimization in Carbon Ion Radiotherapy'`; synthetic `<title>A &gt; B | C > Seminar | MPBEL | x</title>` → `'A > B | C'`.
  - `test_page_count`: `sub2_3_p1` → 2; `sub1_1` → 1.
  - `test_parse_welcome`: body contains `class="welcome_wrap"`, does not contain `<style`, `<form`, `fboardlist`; `image_urls == [BASE_URL+'/images/sub/welcomeVis.png']`.
  - `test_parse_professor_keeps_structure`: body contains `class="prof_info"` and `<h3>김진성`; `image_urls` has one `data/editor/1911/...png` URL.
  - `test_parse_research_ct_images`: `sub3_1` → 4 image URLs, first `BASE_URL+'/images/sub/r1.png'`.
  - `test_rewrite_images`: mapping applied, untouched srcs preserved.
  - `test_parse_home`: `about_html` contains `연세 의학물리 및 의공학 연구실`; `links[0] == ('김진성 교수님 블로그', 'http://mpjinsung.tistory.com/')`; `len(links) == 4`.

- [ ] **Step 2: Run tests → fail.** `cd scripts/crawl && .venv/bin/python -m pytest -q tests/test_parse_pages.py`

- [ ] **Step 3: Implement `parse_common.py`, `parse_pages.py`, and the `pages` runner.**

- [ ] **Step 4: Run tests → pass.**

- [ ] **Step 5: Run the real crawl for pages and inspect**

Run: `cd scripts/crawl && .venv/bin/python -m crawl --only pages`
Expected: 8 files in `src/content/pages/ko/` (`home`, `welcome`, `contact`, `professor`, 4× `research-*`); `grep -c '<img' src/content/pages/ko/research-ai.md` = 5 and every `src="/images/pages/research-ai/…"`; `grep -L 'mpbel.yonsei.ac.kr/data' src/content/pages/ko/*.md` lists all 8 (no remote image left). Then `npx astro sync` exits 0.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(crawl): static pages and home content"
```

---

### Task 5: Members crawler (researchers, collaborators, alumni, internship)

**Files:**
- Create: `scripts/crawl/crawl/parse_members.py`
- Modify: `scripts/crawl/crawl/run.py` (implement `members` runner)
- Test: `scripts/crawl/tests/test_parse_members.py`

**Interfaces:**
- `@dataclass class Member: wr_id: int; name: str; photo_url: str | None; fields: list[tuple[str, str]]; category: str | None`
- `parse_member_list(html: str, category: str | None = None) -> list[Member]` — one per `div.mb_peple` in page order; `name = clean_text(.mb_name h3 a)`; `photo_url` = absolutized `.mb_img img[src]` or None; `fields` from the first `dl` inside `.cnt`: iterate `dl.find_all(['dt','dd'], recursive=False)` pairing each `dt` with the following `dd` (a `dd` with no preceding `dt` gets label `''`); label/value via `clean_text`; skip pairs whose value is empty; `category` = argument.
- `original_photo_url(thumb_url: str) -> str` — on the basename remove leading `thumb-` and a trailing `_<w>x<h>` before the extension; directory unchanged.
- `member_filename(board: str, m: Member) -> str` → `f"{slugify(m.name, 4)}-{m.wr_id}.md"`.
- runner: for each `kind='members'` spec: if the first page has categories (`categories(s)` non-empty: Researchers → `MPBEL`,`Affiliate`; Alumni → `Graduate`,`Former`), iterate each category (`board_url(table, sca=cat, page=p)` for p in 1..page_count) so `category` is known; otherwise iterate `page=p` with category None. Keep page order; assign `order` = running index starting at 1 per board. Dedupe by `wr_id`. Photo: try `original_photo_url`; if `get_bytes` raises, fall back to the thumbnail URL; save to `public/images/members/<board>/<wr_id>.<ext>`. Write `src/content/members/ko/<board>/<member_filename>` with `{board, category?, name, photo?, fields: [{label, value}], order, legacy_url, legacy_id: wr_id}` and empty body. `add` mode: skip a member whose `legacy_id` already exists in that board folder (scan `read_frontmatter`).

- [ ] **Step 1: Write failing tests**
  - `test_parse_researchers_page1`: `sub2_3_p1` → first member `name == '양고운 Gowoon Yang'`, `wr_id == 19`, `photo_url` ends with `_202x150.png`, `fields[0] == ('Grade', 'M.D., Ph.D. Candidate')`, `('E-mail', 'gowoon1988@gmail.com') in fields`.
  - `test_fields_flatten_nested_html`: the same member's `Research Interest` value is exactly `'Medical Physics'` (nested `<dd><p><span>` flattened, no tags, no `&nbsp;`).
  - `test_collaborator_empty_labels`: `sub2_2` first member `name == 'Dong Wook Kim, Ph.D'`; `fields[0] == ('', 'Clinical Professor')`.
  - `test_original_photo_url`: `'.../thumb-3024172423_ULcQMJ5Y_5873_202x150.png'` → `'.../3024172423_ULcQMJ5Y_5873.png'`; a URL without `thumb-` is returned unchanged.
  - `test_member_filename`: `Member(19,'양고운 Gowoon Yang',None,[],None)` → `'gowoon-yang-19.md'`; name with no ASCII → `'entry-19.md'`.
  - `test_page_count_members`: `sub2_3_p1` → 2 pages; `len(parse_member_list(sub2_3_p1)) + len(parse_member_list(sub2_3_p2)) >= 16`.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Real crawl**

Run: `cd scripts/crawl && .venv/bin/python -m crawl --only members`
Expected: four folders under `src/content/members/ko/`; `ls src/content/members/ko/researchers | wc -l` ≈ 25–35; every entry has a `photo` whose file exists under `public/images/members/`; `grep -l 'category: MPBEL' src/content/members/ko/researchers/*.md | wc -l` ≥ 1 and same for `Affiliate`; `npx astro sync` exits 0. Re-run with `--mode add --only members` → summary shows `written 0`.

- [ ] **Step 6: Commit** `git commit -am "feat(crawl): member boards with profile photos"` (after `git add -A`).

---

### Task 6: Publications crawler (papers, presentations, invited talks, patents)

**Files:**
- Create: `scripts/crawl/crawl/parse_publications.py`
- Modify: `scripts/crawl/crawl/run.py` (implement `publications` runner)
- Test: `scripts/crawl/tests/test_parse_publications.py`

**Interfaces:**
- `@dataclass class Publication: wr_id: int; title: str; authors: str; venue: str; link_php: str | None; pinned: bool`
- `parse_publication_rows(html: str) -> list[Publication]` — rows are `table.tb_basic_s tr.bg0, tr.bg1` in order. `title = clean_text(.text_title a)`; `authors = clean_text(.text_author)` (empty if absent); `venue`: walk `.text_journal` children in order: `<span class="text_vol">` → value, `<span>` without class → pending label, `<br>` → line break; emit `label: value` when a label precedes a value on the same line, else `value`; drop empty lines; join with `\n`; `link_php` = href of `td.btn_positon a[href*="link.php"]` in the **next** `tr` of the same `table.tb_basic_s` (None if absent); `pinned` = `'공지' in clean_text(td.num)`.
- `parse_publication_detail_year(html: str) -> int | None` — on a detail page, the `td` after `th` text `Year of publication`, int.
- `parse_detail_files(html: str) -> list[tuple[str, str]]` — `#bo_v_file a.view_file_download` → `(strong text, path_of(href))`.
- `publication_filename(year: int, p: Publication) -> str` → `f"{year}-{p.wr_id}-{slugify(p.title, 5)}.md"`.
- runner: for each `kind='publication'` spec: `cats = categories(first page)`; for each cat (a year string) iterate `page=1..page_count`; rows on those pages get `year=int(cat)` **unless** `pinned`, in which case fetch the detail page and use `parse_publication_detail_year` (fallback: int(cat)). Dedupe by `wr_id`. If `link_php`, `link = fetcher.resolve_redirect(link_php)`. `legacy_files` only for pinned rows (detail already fetched) — other rows do not fetch details. Write `src/content/<collection>/ko/<publication_filename>` with `{year, title, authors, venue, link?, pinned, order: wr_id, legacy_files, legacy_url: board_url(table, wr_id=…), legacy_id: wr_id}`, empty body. `add` mode skips existing `legacy_id`.

- [ ] **Step 1: Write failing tests**
  - `test_paper_rows_2025`: `sub4_1_2025` → first row `wr_id == 197`, title starts `'Anatomical Position-Guided'`, authors start `'Younghun Yoon'`, `venue == 'Medical Physics\nVolume52, e70082\n26 November 2025'`, `link_php` contains `link.php?bo_table=sub4_1&wr_id=197`.
  - `test_row_without_link`: construct HTML of one `tb_basic_s` row with no following `btn_positon` tr → `link_php is None` and the row is still returned.
  - `test_pinned_row_detected`: `sub4_3` → a row with `pinned is True` and title `'AI-Driven Research & Clinic in Radiation Therapy'`.
  - `test_patent_venue_labels`: `sub4_4` → first row venue `== '등록국가: 대한민국\n등록번호: 10-2020-0106825\n등록일: 2020-08-25'`.
  - `test_detail_year_and_files`: `view_sub4_3_3` → year 2021; files `[('KAMPINA.KSMP special session flyer.final - Google Docs.pdf', '/bbs/download.php?bo_table=sub4_3&wr_id=3&no=0')]`.
  - `test_publication_filename`: `(2025, Publication(197,'Anatomical Position-Guided Auto-segmentation and Dosimetric Evaluation of …','','',None,False))` → `'2025-197-anatomical-position-guided-auto-segmentation.md'`.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Real crawl and count check**

Run: `cd scripts/crawl && .venv/bin/python -m crawl --only publications`
Expected counts (±3 allowed; investigate larger gaps): papers ≈ 182, presentations ≈ 285, patents ≈ 8, talks ≥ 1. `grep -l '^link: https://doi.org' src/content/papers/ko/*.md | wc -l` ≥ 50. `npx astro sync` exits 0.

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(crawl): publication boards with resolved links"`.

---

### Task 7: Posts crawler (news, seminars, lectures)

**Files:**
- Create: `scripts/crawl/crawl/parse_posts.py`
- Modify: `scripts/crawl/crawl/run.py` (implement `posts` runner)
- Test: `scripts/crawl/tests/test_parse_posts.py`

**Interfaces:**
- `@dataclass class PostRow: wr_id: int; category: str | None; pinned: bool`
- `parse_post_list(html: str) -> list[PostRow]` — `tbody tr` rows having `.bo_tit a[href]`; `category = clean_text(.bo_cate_link)` or None; `pinned = 'bo_notice' in tr['class']`.
- `@dataclass class PostView: title: str; date: str; category: str | None; body_html: str; image_paths: list[str]; files: list[tuple[str, str]]; event_date: str | None; presenter: str | None`
- `parse_post_view(html: str) -> PostView` — `title = full_title(s)` (fallback `clean_text(.bo_v_tit)`); `date` from `#bo_v_info .if_date` regex `(\d{2})-(\d{2})-(\d{2})` → `20YY-MM-DD`; `category = clean_text(.bo_v_cate)` or None; body = `#bo_v_con`: for every `img`, record `path_of(parent a[href*=view_image.php] fn param)` if wrapped, else `path_of(img src)`, then remove the wrapping `a` (or the `img`) and any now-empty `p`; `files` from `#bo_v_file a.view_file_download` as in Task 6; `event_date`: `.lec_date` text normalized (`2018.04.19`/`2018-04-01` → `YYYY-MM-DD`) if present, else `^(\d{4})/(\d{2})/(\d{2})` from title, else None; `presenter`: regex `Presenter\s*:\s*(.+?)\s*$` (multiline) on the body text, else None; `body_html` = remaining inner HTML.
- `post_filename(view: PostView, wr_id: int) -> str` → `f"{view.date}-{wr_id}.md"`.
- runner: for each `kind='posts'` spec iterate `page=1..page_count` of the unfiltered list, collecting rows; dedupe by `wr_id` (pinned rows appear on every page; keep `pinned=True`). For each row fetch the view page, build frontmatter `{title, date, category?, pinned, presenter?, event_date?, legacy_images: image_paths, legacy_files, legacy_url, legacy_id: wr_id}` and body = `html_to_markdown(body_html)`. Write `src/content/<collection>/ko/<post_filename>`. `add` mode: only fetch views for `wr_id`s not already present (so re-crawl cost is proportional to new posts).

- [ ] **Step 1: Write failing tests**
  - `test_parse_news_list_rows`: `sub6_1_p1` → first row `PostRow(5,'연구실소식',True)`, second `PostRow(92,'2025',False)`.
  - `test_pinned_row_deduplicated`: rows from `sub6_1_p1` + `sub6_1_p2` deduped by wr_id contain `wr_id 5` once; total ≥ 30.
  - `test_seminar_view`: `view_sub6_3_471` → title is the full untruncated string (ends `'Carbon Ion Radiotherapy'`), `date == '2025-12-31'`, `category == '2025'`, `presenter == '이혜진'`, `event_date == '2025-12-29'`, `image_paths == ['/data/editor/2512/9d39b5b8da291607cba002ff2d25bc82_1767148425_8757.png']`, `'<img' not in body_html`.
  - `test_title_from_title_tag_with_separators`: synthetic view with `<title>Why A &gt; B | matters &gt; News | MPBEL | x</title>` and a truncated `.bo_v_tit` → `title == 'Why A > B | matters'`.
  - `test_news_view_keeps_text`: `view_sub6_1_92` → body_html contains `Congratulations to Dong Min Jung!`, `len(image_paths) == 2`, both start with `/data/editor/2510/` and none contains `thumb-`.
  - `test_lecture_view`: `view_sub5_1_1` → `event_date == '2018-09-01'`, `title == '[2학기] 의료영상개론'`, `date == '2018-04-19'`.
  - `test_post_filename`: view with date `2025-12-31`, wr_id 471 → `'2025-12-31-471.md'`.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Real crawl and count check**

Run: `cd scripts/crawl && .venv/bin/python -m crawl --only posts` (about 480 view fetches ≈ 5 minutes at 0.5 s).
Expected: news 49, seminars 431, lectures 2 (exact; the lists print `Total N건`). `grep -c 'pinned: true' src/content/news/ko/*.md | grep -v ':0' | wc -l` = 1. `grep -L '^presenter:' src/content/seminars/ko/*.md | wc -l` small (< 40). `npx astro sync` exits 0. Then `--mode add --only posts` → `written 0` and finishes in < 60 s (no view fetches).

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(crawl): news, seminar and lecture posts"`.

---

### Task 8: Full crawl, verification report, content commit

**Files:**
- Modify: `scripts/crawl/crawl/run.py` (summary also writes `reference/crawl-summary.json`)
- Create: `reference/crawl-summary.json`

- [ ] **Step 1: Add the JSON summary** `write_summary(path: Path, summary: dict[str, dict[str, int]]) -> None` in `run.py` writing `{ "<collection>": {"written": n, "skipped": m}, "generated_at": "<ISO 8601>" }`, called at the end of every run with `reference/crawl-summary.json`; unit test `test_summary_json_written` in `tests/test_run.py` calls it on `tmp_path` and reads the JSON back.

- [ ] **Step 2: Full run from clean content**

```bash
find src/content -path '*/ko/*' -type f ! -name '_*' -delete        # crawled entries only; templates stay
rm -rf public/images/pages public/images/members
cd scripts/crawl && .venv/bin/python -m crawl --mode full && cd ../..
```
Expected summary within the spec table: pages 8, members (sum) 40–70, papers ≈182, presentations ≈285, talks ≥1, patents ≈8, news 49, seminars 431, lectures 2.

- [ ] **Step 3: Validate everything against the schemas**

Run: `npx astro sync` → exit 0. Run: `npm run test:unit` → pass.

- [ ] **Step 4: Spot-check five files by hand** (one per kind) against the live pages; fix parser bugs via new tests in the owning task's test file rather than hand-editing content.

- [ ] **Step 5: Commit the content**

```bash
git add -A
git commit -m "content: initial crawl of mpbel.yonsei.ac.kr (Korean)"
```

---

### Task 9: Legacy CSS port, menu model, i18n strings, BaseLayout, Header/Footer, home page

**Files:**
- Create: `src/styles/legacy/{default,design,latest-basic,board-html,board-student,board-collaborators,board-alumni,board-patent,board-patent2,board-patent3,board-lecture,board-basic,board-gallery,inline}.css`, `src/styles/global.css`
- Create: `src/lib/menu.ts`, `src/i18n/ko.ts`, `src/i18n/en.ts`, `src/i18n/index.ts`
- Create: `src/layouts/BaseLayout.astro`, `src/components/Header.astro`, `src/components/Footer.astro`, `src/components/LatestList.astro`
- Modify: `src/pages/index.astro`
- Test: `tests/dist/helpers.mjs`, `tests/dist/home.test.mjs`, `tests/unit/menu.test.ts`

**Interfaces:**
- `src/lib/menu.ts`: `type MenuItem = { label: string; href: string }`; `type SectionKey = 'introduction'|'member'|'research'|'publication'|'lecture'|'notice'`; `type MenuSection = { key: SectionKey; label: string; href: string; items: MenuItem[] }`; `MENU: Record<Locale, MenuSection[]>` with the Korean tree exactly:
  - `introduction` "INTRODUCTION": `welcome to MPBEL → /introduction/welcome/`, `contact us → /introduction/contact/`
  - `member` "MEMBER": `Professor → /member/professor/`, `Collaborators → /member/collaborators/`, `Researchers → /member/researchers/`, `Alumni → /member/alumni/`, `Short-term internship → /member/internship/`
  - `research` "RESEARCH": `Artificial Intelligence → /research/ai/`, `Radiation Therapy → /research/radiation-therapy/`, `Particle Therapy → /research/particle-therapy/` (Advanced CT Reconstruction is deliberately absent from the menu; it is reachable from the home card at `/research/ct-reconstruction/`)
  - `publication` "PUBLICATION": `Paper → /publication/paper/`, `Presentation → /publication/presentation/`, `Invited talk → /publication/invited-talk/`, `Patent → /publication/patent/`
  - `lecture` "LECTURE": `Lecture → /lecture/`
  - `notice` "NOTICE": `News → /notice/news/`, `Gallery → /notice/gallery/`, `Seminar → /notice/seminar/`
  - each section's `href` = its first item's href. `MENU.en` = same tree (phase 2 will prefix `/en`).
  - `sectionOf(pathname: string, locale?: Locale): MenuSection | undefined` by `pathname.startsWith('/' + key + '/')`.
  - `researchPath(pageSlug: string): string` → `'/research/' + pageSlug.replace(/^research-/, '') + '/'`; `researchSlugFromPath(param: string): string` → `'research-' + param`.
- `src/i18n/ko.ts` exports `const ko = { siteTitle: 'MPBEL | 연세 의학물리 및 의공학 연구실', logoAlt: '연세 의학물리 및 의공학연구실', more: '더보기', footer: { name: 'Yonsei Medical Physics and Biomedical Engineering Lab.', address: '03722 서울특별시 서대문구 연세로 50 연세대학교', tel: 'TEL. +82-2-2228-8118 / FAX. +82-2-2227-7823', copyright: 'COPYRIGHT @2018', copyrightName: 'MPBEL', copyrightTail: 'ALL RIGHT RESERVED.' }, home: { introBrand: 'MPBEL', introWord: 'Introduction', accName: '연세 의학물리 및 의공학 연구실', accTail: '은', research: [ { cls: 'rs1', num: 'RESEARCH 01', label: 'Advanced CT<br>Reconstruction', href: '/research/ct-reconstruction/' }, { cls: 'rs2', num: 'RESEARCH 02', label: 'Medical Artificial<br>Intelligence', href: '/research/ai/' }, { cls: 'rs3', num: 'RESEARCH 03', label: 'Radiation<br>Therapy', href: '/research/radiation-therapy/' }, { cls: 'rs4', num: 'RESEARCH 04', label: 'Particle<br>Therapy', href: '/research/particle-therapy/' } ], news: 'News', seminar: 'Seminar', publication: 'Publication', pubLinks: [ { cls: 'bg1', icon: '/images/site/main/ico_1.png', label: 'Paper', href: '/publication/paper/' }, { cls: 'bg2', icon: '/images/site/main/ico_2.png', label: 'Presentation', href: '/publication/presentation/' }, { cls: 'bg3', icon: '/images/site/main/ico_3.png', label: 'Patent', href: '/publication/patent/' } ] }, board: { total: (n: number) => `Total ${n}건`, pageOf: (p: number) => `${p} 페이지`, num: '번호', subject: '제목', author: '글쓴이', date: '날짜', lectureDate: '강의날짜', authorName: 'YMPBEL', pinned: '공지', list: '목록', prev: '이전글', next: '다음글', presenter: 'Presenter', all: '전체' }, preparing: '준비 중입니다.', home_nav: 'home' }`. (The original home "Patent" icon pointed at Invited talk; the new one points at Patent. Plan decision.) `en.ts` mirrors keys with English copy; `index.ts` exports `t(locale: Locale)` and `type Strings = typeof ko`.
- `BaseLayout.astro` props `{ title?: string; locale?: Locale; bodyClass?: string }`: `<html lang={locale}>`, `<meta charset>`, `<meta name="viewport" content="width=device-width, initial-scale=1">`, `<title>` = `title ? `${title} | MPBEL | 연세 의학물리 및 의공학 연구실` : siteTitle`, Google Fonts `<link>` for `Lato:300,400,700` and `Nanum+Gothic`, `import '../styles/global.css'`; body: `<div id="wrap" class={bodyClass}>` → `<Header locale>` → `<slot/>` → `<Footer locale>`.
- `Header.astro` props `{ locale }`: reproduces `div.topmenu` → `div.logo a[href="/"] img[src="/images/site/logo.png"]`, `div.langbut ul li(.active for current) a[href="/"]KR / a[href="/en/"]EN`, `div#navi ul#nav` with `li.menu1…menu6 > a.on[href=section.href]` + `ul.sub1…sub6 > li > a`. Also renders `<button class="nav-toggle" aria-label="메뉴" aria-expanded="false">` (hidden on desktop by CSS in Task 14) and a 10-line inline `<script>` toggling `#navi.open` and `aria-expanded`.
- `Footer.astro` props `{ locale }`: `div#footer` with `p.ft_name`, `p.ft_address` (address `<br>` tel), `p.ft_copy` = `COPYRIGHT @2018<span>MPBEL</span>ALL RIGHT RESERVED.` — nothing after it.
- `LatestList.astro` props `{ title: string; href: string; items: Array<{ title: string; href: string; date: string }>; more: string }` renders `div.main_notice > div.lat > h2.lat_title a` + `hr.underTit` + `ul li a + span.lt_date` (date shown as `MM-DD` = `date.slice(5)`) + `a.lt_more img[src=/images/site/main/ico_more.png]`.
- `index.astro`: `bodyClass="main"`; sections in order `div.visual > div.wrap > p.slogan img[src=/images/site/main/slogan.png]`, `div.about` (tit/txt from `pages/ko/home` body via `render()` placed inside `div.txt`), `div.research_wrap > div.bg_gray + ul > li.rsN > a > (.tit (span num, p label) and .img, order tit/img for rs1,rs3 and img/tit for rs2,rs4)`, `div.main_board > div.l_bo (LatestList news 4 + div.link ul li a from home.links, second and fourth li get class bor_l, first and third a get class oneline) + div.r_bo (LatestList seminar 4)`, `div.publication > div.tit + ul li.bgN a img span`. Latest news = `sortPosts(news ko).filter(!pinned).slice(0,4)`, latest seminars = `sortPosts(seminars ko).slice(0,4)`; links go to `/notice/news/<slugOf(id)>/` and `/notice/seminar/<slugOf(id)>/`.
- `tests/dist/helpers.mjs`: `import { load } from 'cheerio'`; `export function page(path)` → cheerio of `dist/<path>/index.html` (path `''` for root); `export function exists(path)`; `export function allHtmlFiles()` (recursive list of `dist/**/*.html`).

- [ ] **Step 1: Port the CSS**

Copy `reference/css/*.css` to `src/styles/legacy/` using the names above. In every file: `url(../images/` → `url(/images/site/`, `url(../img/` → `url(/images/site/img/`, delete lines containing `url(./img/` (unused "new" badge) and every `@import url(http…fonts.googleapis…)`. Create `inline.css` with: the `.board_list{position:relative;}` block from the old pages, `.snb .vNav li.active > a { display:block; color:#1563b4; background:#f5f5f5; }`, and `.nav-toggle { display:none; }`. `global.css` = `@import './legacy/default.css'; …` in the order: default, design, latest-basic, board-html, board-student, board-collaborators, board-alumni, board-patent, board-patent2, board-patent3, board-lecture, board-basic, board-gallery, inline. (Responsive layer is appended in Task 14.)

Run: `grep -rn 'url(\.\./' src/styles/legacy | wc -l` → `0`; `grep -rn 'googleapis' src/styles/legacy | wc -l` → `0`.

- [ ] **Step 2: Write failing tests**

`tests/unit/menu.test.ts`: `MENU.ko.length === 6`; total items `=== 18`; `sectionOf('/member/researchers/')?.key === 'member'`; `sectionOf('/')` is undefined; `researchPath('research-ai') === '/research/ai/'`; `researchSlugFromPath('ct-reconstruction') === 'research-ct-reconstruction'`; every href starts with `/` and ends with `/`.
`tests/dist/home.test.mjs`: `page('')`: `$('#nav > li').length === 6`; `$('#nav ul li a').length === 18`; `$('#nav > li:nth-child(3) ul li').length === 3`; `$('.research_wrap li').length === 4` and `$('.research_wrap li.rs1 a').attr('href') === '/research/ct-reconstruction/'`; `$('.l_bo .lat ul li').length === 4` and each `.lt_date` text matches `/^\d{2}-\d{2}$/`; `$('.r_bo .lat ul li').length === 4`; `$('.link ul li').length === 4`; `$('.publication li').length === 3` and third href `/publication/patent/`; `$('#footer').text()` includes `ALL RIGHT RESERVED.` and does not include `DSSO`; `$('meta[name=viewport]').length === 1`; `$('script[src*=jquery]').length === 0`; `$('link[href*="fonts.googleapis"]').length >= 1`; `$('.langbut li.active a').text().trim() === 'KR'`.

- [ ] **Step 3: Run → fail** (`npm run test:unit` for menu; `npm run build && npm run test:dist` for home: index page has no nav yet).

- [ ] **Step 4: Implement** `menu.ts`, `i18n/*`, `BaseLayout`, `Header`, `Footer`, `LatestList`, `index.astro`, `helpers.mjs`.

- [ ] **Step 5: Run → pass**: `npm test`.

- [ ] **Step 6: Visual check**: `npm run preview` and compare `http://localhost:4321/` with `http://mpbel.yonsei.ac.kr/` side by side at 1280 px width; fix CSS path or structure mismatches (not new styling) until banner, about, four cards, two lists, icons and footer line up.

- [ ] **Step 7: Commit** `git add -A && git commit -m "feat(site): legacy CSS, base layout, header/footer and home page"`.

---

### Task 10: SubLayout and static pages (introduction, professor, research)

**Files:**
- Create: `src/layouts/SubLayout.astro`, `src/components/Snb.astro`, `src/components/Breadcrumb.astro`
- Create: `src/pages/introduction/welcome.astro`, `src/pages/introduction/contact.astro`, `src/pages/member/professor.astro`, `src/pages/research/[slug].astro`
- Test: `tests/dist/static-pages.test.mjs`

**Interfaces:**
- `SubLayout.astro` props `{ title: string; sectionKey: SectionKey; currentHref: string; locale?: Locale }` → `BaseLayout` with `bodyClass="sub"` wrapping `div#sub_container > div.sub_visual > div.wrap > img[src=/images/site/sub/sub_slogan.png]` then `div#sub_contents > (Snb) + div.contentBox > h2.cnt_title{title} + (Breadcrumb) + div.contents > <slot/>`.
- `Snb.astro` props `{ sectionKey; currentHref; locale }` → `div.snb > p.tit{section.label} + div.vNav > ul > li(.active when item.href === currentHref) > a`.
- `Breadcrumb.astro` props `{ sectionKey; title; locale }` → `div.loca > ul.loc > li img[src=/images/site/sub/home.png alt=home] + li{section.label} + li.last{title}`.
- `welcome.astro`/`contact.astro`/`professor.astro`: `getEntry('pages', 'ko/<slug>')`, `render()` body inside `SubLayout` with the page title and matching `currentHref`.
- `research/[slug].astro`: `getStaticPaths` from `getCollection('pages', e => localeOf(e.id)==='ko' && e.data.section==='research')`, `params: { slug: slugOf(e.id).replace(/^research-/, '') }`; `currentHref = researchPath(slugOf(e.id))`.

- [ ] **Step 1: Write failing tests** (`static-pages.test.mjs`): `exists('introduction/welcome')`, `exists('introduction/contact')`, `exists('member/professor')`, `exists('research/ai')`, `exists('research/ct-reconstruction')`, `exists('research/radiation-therapy')`, `exists('research/particle-therapy')`; on `page('introduction/welcome')`: `$('.cnt_title').text().trim() === 'Welcome to MPBEL'`, `$('.snb .vNav li.active a').attr('href') === '/introduction/welcome/'`, `$('.loc li.last').text().trim() === 'Welcome to MPBEL'`, `$('.contents img').attr('src')` starts with `/images/pages/welcome/`; `page('introduction/contact')`: `$('.contents iframe[src*="google.com/maps"]').length === 1`; `page('member/professor')`: `$('.prof_info').length === 1`; `page('research/ai')`: `$('.contents img').length === 5` and none of their `src` contains `mpbel.yonsei.ac.kr`; `page('research/ct-reconstruction')`: `$('.snb .vNav li.active').length === 0` (not in menu) and `$('.loc li.last').text().trim() === 'Advanced CT Reconstruction'`.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass** (`npm test`).

- [ ] **Step 5: Visual check** of `/member/professor/` and `/research/ai/` against the live site; port any missing selector into `inline.css`.

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(site): sub layout and static pages"`.

---

### Task 11: Member pages

**Files:**
- Create: `src/components/MemberCard.astro`, `src/components/MemberList.astro`, `src/components/CategoryTabs.astro`, `src/pages/member/[board].astro`
- Test: `tests/dist/members.test.mjs`

**Interfaces:**
- `CategoryTabs.astro` props `{ tabs: Array<{ label: string; href: string; active: boolean }>; variant: 'members' | 'board' }` → `nav#bo_cate > ul.class_area > li > a(.active)` for `members`, `nav#bo_cate > ul#bo_cate_ul > li > a(.active)` for `board` (Task 13).
- `MemberCard.astro` props `{ member: CollectionEntry<'members'> }` → `div.mb_peple > div.cntWrap > div.mb_img (img[src=photo] if photo else empty div) + div.cnt > div.mb_name > h3{name} + dl > (dt{label} dd{value})*` (a field with empty label renders `<dt></dt>` to keep the original rhythm) + `div.link01`.
- `MemberList.astro` props `{ members: CollectionEntry<'members'>[] }` → `div#member_professor > div#gall_ul > div.member_list > MemberCard*`.
- `member/[board].astro`: `getStaticPaths` → the four boards (`researchers`, `collaborators`, `alumni`, `internship`); page title and `currentHref` from `MENU.ko` member items (`Researchers`, `Collaborators`, `Alumni`, `Short-term internship`); members = `sortMembers(getCollection('members', e => localeOf(e.id)==='ko' && e.data.board===board))`; if any member has `category`, render `CategoryTabs` with tabs `전체` + each distinct category in first-seen order, implemented as **in-page sections**: each category gets `<h3 class="mb_cate_title">{category}</h3>` followed by its `MemberList`; the tabs are anchor links `#cat-<categorySlug>` (no extra routes). Boards without categories render one `MemberList`.

- [ ] **Step 1: Write failing tests**: for each board `exists('member/<board>')`; `page('member/researchers')`: `$('.mb_peple').length` equals the number of files `src/content/members/ko/researchers/*.md` (count via `fs`), `$('#bo_cate a').length === 3` (전체, MPBEL, Affiliate), every `.mb_img img` src starts with `/images/members/researchers/`; `page('member/collaborators')`: `$('#bo_cate').length === 0`, first card `h3` text `=== 'Dong Wook Kim, Ph.D'`; `page('member/alumni')`: tabs include `Graduate` and `Former`; first `.mb_peple dl dd` of researchers is `M.D., Ph.D. Candidate`.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Visual check** `/member/researchers/` vs live (card grid, photo size 202×150, name/field typography).

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(site): member boards"`.

---

### Task 12: Publication pages

**Files:**
- Create: `src/components/PubList.astro`, `src/pages/publication/[kind].astro`
- Test: `tests/dist/publications.test.mjs`

**Interfaces:**
- `PUB_KINDS` (in `src/lib/content.ts`, add now): `[{ kind: 'paper', collection: 'papers', label: 'Paper' }, { kind: 'presentation', collection: 'presentations', label: 'Presentation' }, { kind: 'invited-talk', collection: 'talks', label: 'Invited talk' }, { kind: 'patent', collection: 'patents', label: 'Patent' }] as const`.
- `PubList.astro` props `{ groups: Array<{ year: number; items: CollectionEntry<'papers'|'presentations'|'talks'|'patents'>[] }>; total: number }` → `nav#bo_cate > ul#bo_cate_ul > li > a[href=#y-<year>]{year}` (years in group order) then `div#bo_list > div.publication_oldver > table.tb_basic >` for each group: `tr > td.title > div.year_title[id=y-<year>]{year}` then for each item `tr > td > table.tb_basic_s > tr.bg1 > td.num{n} + td.name_title > span.text_title (a[href=link target=_blank] if link else plain) + br + span.text_author + br + span.text_journal` where venue lines render as `span.text_vol` separated by `<br>`, and a following `tr > td.btn_positon > a.btn_set01[href=link target=_blank]{LINK}` only when `link` exists. `n` counts down from `total` to 1 in display order (matches the old numbering). Pinned items render `<strong>공지</strong>` instead of `n` and come first inside their year.
- `publication/[kind].astro`: `getStaticPaths` over `PUB_KINDS`; items = `sortPublications(getCollection(collection, isLocale('ko')))`; `groups = groupByYear(items)`; `SubLayout` with `sectionKey='publication'`, title = label, `currentHref='/publication/<kind>/'`.

- [ ] **Step 1: Write failing tests**: all four `exists('publication/<kind>')`; `page('publication/paper')`: `$('.year_title').first().text().trim() === '2025'`, `$('.tb_basic_s').length` equals file count in `src/content/papers/ko/`, `$('#bo_cate_ul li').length === $('.year_title').length`, at least 50 `a.btn_set01[href^="https://doi.org"]`, `$('.text_author').first().text()` starts with `Younghun Yoon`; `page('publication/patent')`: first `.text_journal` text contains `등록번호: 10-2020-0106825`; `page('publication/invited-talk')`: `$('td.num strong').first().text() === '공지'`; numbering: on paper page `$('td.num').first().text().trim()` equals the file count as a string.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Visual check** `/publication/paper/` vs live (year headers, row striping, LINK button).

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(site): publication lists"`.

---

### Task 13: Board pages (news, seminar), lecture, gallery placeholder

**Files:**
- Create: `src/components/PostTable.astro`, `src/components/Pagination.astro`, `src/components/BoardPage.astro`, `src/components/PostView.astro`
- Create: `src/pages/notice/[board]/index.astro`, `src/pages/notice/[board]/page/[page].astro`, `src/pages/notice/[board]/c/[category]/index.astro`, `src/pages/notice/[board]/c/[category]/page/[page].astro`, `src/pages/notice/[board]/[slug].astro`, `src/pages/notice/gallery.astro`, `src/pages/lecture/index.astro`, `src/pages/lecture/[slug].astro`
- Modify: `src/lib/content.ts` (add `BOARDS`)
- Test: `tests/dist/boards.test.mjs`

**Interfaces:**
- `BOARDS` in `content.ts`: `[{ board: 'news', collection: 'news', label: 'News', base: '/notice/news/' }, { board: 'seminar', collection: 'seminars', label: 'Seminar', base: '/notice/seminar/' }] as const`; `LECTURE = { collection: 'lectures', label: 'Lecture', base: '/lecture/' }`.
- `type PostEntry = CollectionEntry<'news' | 'seminars' | 'lectures'>` (type-only import from `astro:content`, exported from `content.ts`); `postHref(base: string, entry: PostEntry): string` → `base + slugOf(entry.id) + '/'`.
- `PostTable.astro` props `{ posts: PostEntry[]; base: string; startNumber: number; showEventDate?: boolean; locale }` → `div.tbl_head01.tbl_wrap > table > caption + thead (번호, 제목, [강의날짜], 글쓴이, 날짜) + tbody > tr(.bo_notice if pinned) > td.td_num2 (strong.notice_icon{공지} or number counting down from startNumber) + td.td_subject > (a.bo_cate_link[href=base+'c/'+categorySlug+'/']{category} if category) + div.bo_tit > a[href=postHref]{title} + [td.td_lec_date{event_date}] + td.td_name span.sv_member{YMPBEL} + td.td_datetime{date.slice(5)}`.
- `Pagination.astro` props `{ current: number; last: number; hrefFor: (p: number) => string }` → `nav.pg_wrap > span.pg` with `a.pg_page.pg_start`(처음) when current>1, numbered links (window of 10 like Gnuboard), `strong.pg_current` for current, `a.pg_page.pg_end`(맨끝) when current<last. Empty output when `last <= 1`.
- `BoardPage.astro` props `{ board: typeof BOARDS[number]; posts: PostEntry[] (already sorted and filtered); allPosts: PostEntry[] (for tabs); pageNo: number; category?: string }`: computes `pages = paginateArray(posts, PAGE_SIZE)`, renders `SubLayout(sectionKey='notice', title=label, currentHref=base)` → `div.bo_cate_wrap` CategoryTabs (`전체` → base, each of `categoriesOf(allPosts)` → `base + 'c/' + categorySlug(c) + '/'`, active = current) → `div.bo_count{Total N건 · P 페이지}` → `PostTable` (pinned posts first on page 1 of the 전체 view only; `startNumber = posts.length - (pageNo-1)*PAGE_SIZE` counting non-pinned) → `Pagination` with `hrefFor = p => p===1 ? listBase : listBase + 'page/' + p + '/'` where `listBase` is `base` or the category base.
- `PostView.astro` props `{ entry: PostEntry; base: string; locale: Locale; prev?: PostEntry; next?: PostEntry }` → `article#bo_v > header > h2#bo_v_title > (span.bo_v_cate{category}) span.bo_v_tit{title}` + (`div.lec_date{강의날짜 : event_date}` for lectures) + `section#bo_v_info` (작성자 YMPBEL, 작성일 date) + `section#bo_v_atc > div#bo_v_con > <Content/>` (if `presenter`, prepend `<p>Presenter: {presenter}</p>` only when the body does not already contain `Presenter`) + `div#bo_v_top > ul.bo_v_com > li a.btn_b01[href=listBase]{목록}` + `ul.bo_v_nb` with 이전글/다음글 links when given.
- Routes: `[board]/index.astro` → `BoardPage pageNo=1`; `[board]/page/[page].astro` → `getStaticPaths` with `paginate` is **not** used (keep one code path): generate params `{ board, page }` for `page in 2..pages.length`; `c/[category]/index.astro` and `c/[category]/page/[page].astro` same with `posts.filter(p => categorySlug(p.data.category ?? '') === category)`; `[slug].astro` → `getStaticPaths` over both boards' ko posts, `params: { board, slug: slugOf(id) }`, prev/next computed from `sortPosts` order (next = newer).
- `lecture/index.astro` → same `BoardPage` logic with `LECTURE` and `showEventDate=true` (no categories); `lecture/[slug].astro` → `PostView`.
- `notice/gallery.astro` → `SubLayout(sectionKey='notice', title='Gallery', currentHref='/notice/gallery/')` with `<p class="preparing">준비 중입니다.</p>`.

- [ ] **Step 1: Write failing tests** (`boards.test.mjs`):
  - The test derives `S` = number of `src/content/seminars/ko/*.md` files (excluding `_*`), `N` = number of news files, `NP` = news files without `pinned: true`, and `lastSeminarPage = Math.ceil(S / 20)`. Then: `exists('notice/news')`, `exists('notice/seminar')`, `exists('notice/seminar/page/2')`, `exists('notice/seminar/page/' + lastSeminarPage)`, `!exists('notice/seminar/page/' + (lastSeminarPage + 1))`, `exists('notice/news/c/연구실소식')`, `exists('notice/seminar/c/2025')`, `exists('lecture')`, `exists('notice/gallery')`.
  - `page('notice/news')`: `$('tbody tr').length === 21` (20 + 1 pinned), `$('tr.bo_notice').length === 1` and it is first, `$('.bo_count').text()` contains `` `Total ${N}건` ``, `$('#bo_cate_ul li a').first().text().trim() === '전체'`, categories order: text of tabs after 전체 starts with `2025` and contains `연구실소식`, `$('.pg_wrap strong.pg_current').text() === '1'`, `$('.pg_wrap a.pg_end').length === 1`.
  - `page('notice/news/page/3')`: `$('tbody tr').length === NP - 40` and `$('tr.bo_notice').length === 0`.
  - `page('notice/seminar')`: first `.bo_tit a` text ends with `Carbon Ion Radiotherapy` (full title) and its href matches `/^\/notice\/seminar\/2025-12-31-471\/$/`; `$('.td_datetime').first().text() === '12-31'`.
  - `page('notice/seminar/2025-12-31-471')`: `$('#bo_v_title .bo_v_cate').text() === '2025'`, `$('#bo_v_con').text()` contains `Presenter: 이혜진` exactly once, `$('#bo_v_con img').length === 0`, `$('.bo_v_com a').attr('href') === '/notice/seminar/'`.
  - `page('notice/news/c/연구실소식')`: every `tbody tr .bo_cate_link` text is `연구실소식`; `$('#bo_cate_ul a.active').text().trim() === '연구실소식'`.
  - `page('lecture')`: `$('thead th').length === 5` and includes `강의날짜`; `$('tbody tr').length === 2`; `page('lecture/2018-04-19-1')`: `$('.lec_date').text()` contains `2018-09-01`.
  - `page('notice/gallery')`: `$('.preparing').text().trim() === '준비 중입니다.'`.
  - `exists('notice/seminar/c/2020')` is false if no seminar has category `2020` (compute expectation from content files: the test derives expected category set from frontmatter via a tiny YAML-less regex `^category: (.+)$`).

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Visual check** `/notice/seminar/` list and one post vs live (table header, category link, pagination style).

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(site): news, seminar and lecture boards"`.

---

### Task 14: Responsive layer, mobile navigation, English placeholder, 404

**Files:**
- Create: `src/styles/responsive.css`, `src/pages/en/index.astro`, `src/pages/404.astro`
- Modify: `src/styles/global.css` (append `@import './responsive.css';` last), `src/components/Header.astro` (toggle already rendered in Task 9; wire classes), `src/i18n/en.ts`
- Test: `tests/dist/responsive.test.mjs`

**Interfaces / behaviour (all inside `@media (max-width: 1024px)` unless noted; the desktop layout above 1024 px must not change):**
- Containers that are fixed `width:1200px` (`.topmenu`, `.wrap`, `#sub_contents`, `.main_board`, `.contentBox` and any other `width:1200px`/`width:1180px` rule found in `design.css`) become `width:auto; max-width:1200px; padding:0 16px; box-sizing:border-box`.
- `html, body { overflow-x: hidden }`; images in `.contents`, `.visual`, `.sub_visual` get `max-width:100%; height:auto`.
- Header: `.nav-toggle { display:block; position:absolute; right:16px; top:30px; width:40px; height:40px; background:none; border:1px solid #0a347f; }` with three bars drawn by inline SVG; `#navi { display:none }` and `#navi.open { display:block; position:static }`; `#nav`, `#nav > li` become block/100 % width; `#nav ul` (sub menus) become `display:block; position:static; width:auto` (always expanded inside the open drawer, no hover dependency); `.langbut` stays visible left of the toggle.
- Home: `.research_wrap ul li` width 100 %, stacked, `.img` height ≥ 180 px with `background-size: cover`; `.main_board .l_bo, .main_board .r_bo` width 100 %, stacked; `.publication ul li` width 33 % → at ≤ 600 px 100 %.
- Sub pages: `.snb` width 100 %, `.vNav ul li` inline-block tabs; `.contentBox` width 100 %, float none.
- Members: `.mb_peple` width 100 % at ≤ 600 px, 50 % between 601 and 1024.
- Publications: `.tb_basic_s td.num { width:40px }`, `.text_title`, `.text_author`, `.text_journal` `word-break: break-word`.
- Boards: `.tbl_head01 th:nth-child(3), td.td_name { display:none }` at ≤ 600 px (hide 글쓴이 column), `td.td_subject { white-space: normal }`.
- `en/index.astro`: `BaseLayout(locale='en', bodyClass='sub')` with `langbut` active on EN and body `<div class="contentBox"><h2 class="cnt_title">English</h2><p class="preparing">The English pages are being prepared. Please use the Korean site for now.</p><p><a href="/">Go to Korean site</a></p></div>`.
- `404.astro`: `SubLayout(sectionKey='introduction', title='Page not found', currentHref='/')` with a link home.

- [ ] **Step 1: Write failing tests** (`responsive.test.mjs`): `exists('en')` and `page('en')` has `$('.langbut li.active a').text().trim() === 'EN'` and `$('html').attr('lang') === 'en'`; `exists('404')` (dist/404.html; adapt `exists` to accept a file path); `page('')` has `$('button.nav-toggle[aria-expanded="false"]').length === 1` and an inline script containing `nav-toggle`; the built CSS (find `dist/_astro/*.css`, concatenate) contains `@media (max-width: 1024px)` and `.nav-toggle{display:block` (whitespace-insensitive) and does **not** contain `url(../`.

- [ ] **Step 2: Run → fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run → pass.**

- [ ] **Step 5: Manual check** in a browser at 1280 px (unchanged), 768 px and 390 px widths on `/`, `/member/researchers/`, `/publication/paper/`, `/notice/seminar/`: no horizontal scroll, drawer opens and closes, every sub menu link reachable.

- [ ] **Step 6: Commit** `git add -A && git commit -m "feat(site): responsive layout, mobile nav, English placeholder, 404"`.

---

### Task 15: README (운영 안내), internal link check, deploy verification, cutover checklist

**Files:**
- Modify: `README.md`
- Create: `tests/dist/links.test.mjs`
- Modify: `scripts/crawl/README.md` (link from root README)

- [ ] **Step 1: Write the failing link test** (`links.test.mjs`): for every file in `allHtmlFiles()`, every `a[href]` and `img[src]` that starts with `/` (and not `//`) must resolve to an existing file in `dist/` (`/x/` → `dist/x/index.html`; `/images/..png` → that file). Collect all misses and `assert.deepEqual(misses, [])`. Also assert no `href`/`src` contains `mpbel.yonsei.ac.kr/` except inside `a[href^="http://mpbel.yonsei.ac.kr/bbs/link.php"]` (none expected) — i.e. `assert.equal(count, 0)`.

- [ ] **Step 2: Run → fix any broken link in the owning component → pass** (`npm test`).

- [ ] **Step 3: Write `README.md`** (Korean) with these sections, each with concrete commands or field lists copied from the templates:
  1. 사이트 개요와 폴더 구조 (one paragraph + the tree from this plan's File Structure, trimmed).
  2. 로컬 실행: `npm install`, `npm run dev`, `npm test`.
  3. 글 올리는 법 — 세미나 / 뉴스 / 강의: copy `_template.md` → `src/content/<collection>/ko/YYYY-MM-DD-<short-slug>.md`; field table (title, date, category, presenter, event_date, pinned, body); category tab rule ("기존 값 중 하나 또는 새 연도; 새 값을 적으면 탭이 자동으로 생깁니다"); images: "본문 이미지는 `public/images/posts/<year>/`에 넣고 `![](/images/posts/<year>/<file>)`" (folder convention for future posts).
  4. 논문 / 발표 / 초청강연 / 특허 추가: file name `YYYY-<short-slug>.md`, fields (year, title, authors, venue with line breaks, link), `order` optional ("비우면 그 해의 맨 위에 표시").
  5. 멤버 추가·수정·졸업 처리: folder per board, `order` rule, photo path `public/images/members/<board>/`, moving a researcher to alumni = move the file to `alumni/` and change `board` + `category`.
  6. 고정 페이지 수정 (`src/content/pages/ko/*.md`, HTML 허용).
  7. 배포: push to `main` → Actions → 2–3분; where to look when the build fails (Actions 로그의 `[InvalidContentEntryDataError]` 메시지 = frontmatter 오류, 파일명과 필드가 표시됨).
  8. 도메인 전환 체크리스트 (한 번만): (a) `cd scripts/crawl && .venv/bin/python -m crawl --mode add` 후 커밋 (전환 직전 새 글 반영); (b) 담당자에게 DNS 요청 — `mpbel.yonsei.ac.kr CNAME ympbel.github.io`, 선택적으로 `_github-pages-challenge-ympbel TXT <GitHub Pages 설정 화면 값>`; (c) DNS 반영 후 `astro.config.mjs`의 `site`를 `https://mpbel.yonsei.ac.kr`로 바꾸고 `public/CNAME` 파일(내용 `mpbel.yonsei.ac.kr`) 추가, 커밋·푸시; (d) 저장소 Settings → Pages → Custom domain 입력, DNS check 통과 후 Enforce HTTPS 체크; (e) `curl -I https://mpbel.yonsei.ac.kr/` 200 확인; (f) 이후 크롤러 실행 금지.
  9. 2차 작업 메모: 갤러리·본문 이미지(`legacy_images`, 옛 서버 IP로 받기), 영문(`src/content/*/en/`, `src/pages/en/`), 필요 시 Decap/Sveltia CMS.

- [ ] **Step 4: Push and verify the deployed site**

```bash
git add -A && git commit -m "docs: operations README and link check"
git push
gh run watch $(gh run list --workflow deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId') --exit-status
for p in / /member/researchers/ /publication/paper/ /notice/seminar/ /notice/seminar/page/2/ /research/ai/ /en/; do curl -s -o /dev/null -w "$p %{http_code}\n" "https://ympbel.github.io$p"; done
```
Expected: all `200`.

- [ ] **Step 5: Final whole-site visual pass** of the live URL against the old site on desktop and phone; log any mismatch as a follow-up issue in the repo rather than fixing ad hoc.

---

## Execution notes

- Implementer subagents run on **Opus** (user decision); plan, orchestration and reviews stay in the main session.
- Tasks 3→4→5→6→7→8 are sequential (shared `run.py`); Tasks 9→10 sequential; Tasks 11, 12, 13 are independent of each other once Task 10 exists; Task 14 after 13; Task 15 last.
- Every task ends with `npm test` (Node) and/or `pytest` (Python) green and a commit on `main`. Pushing after each task is allowed; the deploy workflow is cheap.
