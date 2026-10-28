import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { exists, page } from './helpers.mjs';

const CONTENT = fileURLToPath(new URL('../../src/content/', import.meta.url));

/** Frontmatter blocks of `src/content/<collection>/ko/` (templates `_*.md` excluded, as in the collection loader). */
function frontmatters(collection) {
  const dir = `${CONTENT}${collection}/ko/`;
  return readdirSync(dir)
    .filter((f) => f.endsWith('.md') && !f.startsWith('_'))
    .map((f) => readFileSync(dir + f, 'utf8').split(/^---$/m)[1]);
}

/** Distinct `category:` values, unquoted and trimmed. */
function categories(blocks) {
  return new Set(
    blocks
      .map((fm) => fm.match(/^category: (.+)$/m)?.[1])
      .filter(Boolean)
      .map((c) => c.trim().replace(/^(['"])(.*)\1$/, '$2').trim()),
  );
}

const news = frontmatters('news');
const seminars = frontmatters('seminars');
const N = news.length;
const NP = news.filter((fm) => !/^pinned: true$/m.test(fm)).length;
const S = seminars.length;
const lastSeminarPage = Math.ceil(S / 20);

test('board pages are built', () => {
  assert.ok(exists('notice/news'));
  assert.ok(exists('notice/seminar'));
  assert.ok(exists('notice/seminar/page/2'));
  assert.ok(exists('notice/seminar/page/' + lastSeminarPage));
  assert.ok(!exists('notice/seminar/page/' + (lastSeminarPage + 1)));
  assert.ok(exists('notice/news/c/연구실소식'));
  assert.ok(exists('notice/seminar/c/2025'));
  assert.ok(exists('lecture'));
  assert.ok(exists('notice/gallery'));
});

test('news page 1: the pinned row first, then 20 rows; count, tabs and pagination', () => {
  const $ = page('notice/news');
  assert.equal($('tbody tr').length, 21);
  assert.equal($('tr.bo_notice').length, 1);
  assert.ok($('tbody tr').first().hasClass('bo_notice'));
  assert.ok($('.bo_count').text().includes(`Total ${N}건`), $('.bo_count').text());
  assert.equal($('#bo_cate_ul li a').first().text().trim(), '전체');
  const tabs = $('#bo_cate_ul li a')
    .slice(1)
    .map((_, a) => $(a).text().trim())
    .get();
  assert.equal(tabs[0], '2025', tabs.join(' '));
  assert.ok(tabs.includes('연구실소식'), tabs.join(' '));
  assert.equal($('.pg_wrap strong.pg_current').text(), '1');
  assert.equal($('.pg_wrap a.pg_end').length, 1);
});

test('news: the pinned row shows the bullhorn and 공지; numbers count non-pinned posts; no hits column', () => {
  const $ = page('notice/news');
  const icon = $('tr.bo_notice td.td_num2 strong.notice_icon');
  assert.equal(icon.length, 1);
  assert.equal(icon.find('svg').length, 1);
  assert.equal(icon.find('span.sound_only').text(), '공지');
  assert.equal($('tbody tr').eq(1).find('td.td_num2').text().trim(), String(NP));
  assert.equal($('th').filter((_, th) => $(th).text().includes('조회')).length, 0);
  const last = page('notice/news/page/3')('tbody tr').last().find('td.td_num2').text().trim();
  assert.equal(last, '1');
});

test('news page 3: the remaining rows, no pinned row', () => {
  const $ = page('notice/news/page/3');
  assert.equal($('tbody tr').length, NP - 40);
  assert.equal($('tr.bo_notice').length, 0);
});

test('seminar list: newest post first with its full title, MM-DD date', () => {
  const $ = page('notice/seminar');
  const a = $('.bo_tit a').first();
  assert.ok(a.text().trim().endsWith('Carbon Ion Radiotherapy'), a.text());
  assert.match(a.attr('href'), /^\/notice\/seminar\/2025-12-31-471\/$/);
  assert.equal($('.td_datetime').first().text(), '12-31');
});

test('seminar pagination: windows of 10 with 다음/맨끝 and 처음/이전', () => {
  const $ = page('notice/seminar');
  assert.equal($('.pg_wrap a.pg_page').not('.pg_next, .pg_end').length, 9);
  assert.equal($('.pg_wrap a.pg_next').attr('href'), '/notice/seminar/page/11/');
  assert.equal($('.pg_wrap a.pg_end').attr('href'), `/notice/seminar/page/${lastSeminarPage}/`);
  assert.equal($('.pg_wrap a.pg_start').length, 0);
  const $12 = page('notice/seminar/page/12');
  assert.equal($12('.pg_wrap strong.pg_current').text(), '12');
  assert.equal($12('.pg_wrap a.pg_start').attr('href'), '/notice/seminar/');
  assert.equal($12('.pg_wrap a.pg_prev').attr('href'), '/notice/seminar/page/10/');
  const $last = page('notice/seminar/page/' + lastSeminarPage);
  assert.equal($last('.pg_wrap a.pg_end').length, 0);
  assert.equal($last('.pg_wrap a.pg_next').length, 0);
});

test('seminar view: category, one Presenter line, no images, list link, older post as 다음글', () => {
  const $ = page('notice/seminar/2025-12-31-471');
  assert.equal($('#bo_v_title .bo_v_cate').text(), '2025');
  assert.equal($('#bo_v_con').text().split('Presenter: 이혜진').length - 1, 1, $('#bo_v_con').text());
  assert.equal($('#bo_v_con img').length, 0);
  assert.equal($('.bo_v_com a').attr('href'), '/notice/seminar/');
  // The newest post: no 이전글 (newer), and 다음글 is the next row of the list, as on the old board.
  assert.equal($('.bo_v_nb li').length, 1);
  assert.equal($('.bo_v_nb li .nb_tit').text().trim(), '다음글');
  assert.match($('.bo_v_nb li a').attr('href'), /^\/notice\/seminar\/2025-12-31-470\/$/);
});

test('news category page: only that category, its tab active', () => {
  const $ = page('notice/news/c/연구실소식');
  const links = $('tbody tr .bo_cate_link');
  assert.ok(links.length > 0);
  for (const a of links.get()) assert.equal($(a).text(), '연구실소식');
  assert.equal($('#bo_cate_ul a.active').text().trim(), '연구실소식');
});

test('lecture list and view', () => {
  const $ = page('lecture');
  const ths = $('thead th')
    .map((_, th) => $(th).text().trim())
    .get();
  assert.equal(ths.length, 5);
  assert.ok(ths.includes('강의날짜'), ths.join(' '));
  assert.equal($('tbody tr').length, 2);
  assert.ok(page('lecture/2018-04-19-1')('.lec_date').text().includes('2018-09-01'));
});

test('lecture: a single page today, so no pagination and no page/2', () => {
  assert.ok(!exists('lecture/page/2'));
  assert.equal(page('lecture')('.pg_wrap').length, 0);
});

test('document titles as on the old boards: `<post title> > <board>` and `<board> <n> 페이지`', () => {
  const view = page('notice/seminar/2025-12-31-471')('title').text();
  assert.ok(view.startsWith('2025/12/29 [Research Seminar] Group Sparse Algorithm'), view);
  assert.ok(view.includes(' > Seminar | MPBEL'), view);
  assert.ok(page('notice/news')('title').text().startsWith('News 1 페이지 | '), page('notice/news')('title').text());
  const p12 = page('notice/seminar/page/12')('title').text();
  assert.ok(p12.startsWith('Seminar 12 페이지 | '), p12);
});

test('gallery placeholder', () => {
  assert.equal(page('notice/gallery')('.preparing').text().trim(), '준비 중입니다.');
});

test('seminar category pages follow the content', () => {
  const cats = categories(seminars);
  assert.equal(exists('notice/seminar/c/2020'), cats.has('2020'));
  for (const c of cats) assert.ok(exists('notice/seminar/c/' + c), c);
});
