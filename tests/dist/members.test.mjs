import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { exists, page } from './helpers.mjs';

const MEMBERS = fileURLToPath(new URL('../../src/content/members/ko/', import.meta.url));
const BOARDS = ['researchers', 'collaborators', 'alumni', 'internship'];

/** Member entries of a board as `<board>/<slug>` (templates `_*.md` excluded, as in the collection loader). */
function memberFiles(board) {
  return readdirSync(MEMBERS + board)
    .filter((f) => f.endsWith('.md') && !f.startsWith('_'))
    .map((f) => `${board}/${f.slice(0, -3)}`);
}

function fileCount(board) {
  return memberFiles(board).length;
}

/** Raw frontmatter text of `src/content/members/ko/<file>.md`. */
function frontmatter(file) {
  return readFileSync(`${MEMBERS}${file}.md`, 'utf8').split('---')[1];
}

/** A top-level scalar frontmatter value such as `name` or `link`, or undefined. */
function scalar(file, key) {
  return frontmatter(file).match(new RegExp(`^${key}: (.+)$`, 'm'))?.[1];
}

/** The card whose name is the `name` of the given member file. */
function cardOf($, file) {
  const name = scalar(file, 'name');
  const card = $('.mb_peple').filter((_, el) => $(el).find('.mb_name h3').text().trim() === name);
  assert.equal(card.length, 1, name);
  return card;
}

test('member boards are built', () => {
  for (const board of BOARDS) assert.ok(exists(`member/${board}`), board);
});

test('every member file renders one card', () => {
  for (const board of BOARDS) {
    assert.equal(page(`member/${board}`)('.mb_peple').length, fileCount(board), board);
  }
  assert.equal(fileCount('alumni'), 18);
});

test('researchers: tabs, local photos and first field', () => {
  const $ = page('member/researchers');
  assert.equal($('#bo_cate a').length, 3);
  assert.deepEqual(
    $('#bo_cate a').map((_, el) => $(el).text().trim()).get(),
    ['전체', 'MPBEL', 'Affiliate'],
  );
  for (const a of $('#bo_cate a[href^="#"]').get()) {
    assert.equal($($(a).attr('href')).length, 1, $(a).attr('href'));
  }
  const srcs = $('.mb_img img').map((_, el) => $(el).attr('src')).get();
  assert.equal(srcs.length, fileCount('researchers'));
  for (const src of srcs) assert.ok(src.startsWith('/images/members/researchers/'), src);
  assert.equal($('.mb_peple dl dd').first().text(), 'M.D., Ph.D. Candidate');
});

test('collaborators: no tabs, first card name', () => {
  const $ = page('member/collaborators');
  assert.equal($('#bo_cate').length, 0);
  assert.equal($('.mb_peple h3').first().text().trim(), 'Dong Wook Kim, Ph.D');
});

test('alumni: Graduate and Former tabs', () => {
  const $ = page('member/alumni');
  const labels = $('#bo_cate a').map((_, el) => $(el).text().trim()).get();
  assert.ok(labels.includes('Graduate'), labels.join());
  assert.ok(labels.includes('Former'), labels.join());
});

test('LINK button only for members with a link', () => {
  const $ = page('member/researchers');
  const linked = 'researchers/jaehyun-seok-31';
  const button = cardOf($, linked).find('div.link01 a.btn_set01[target=_blank]');
  assert.equal(button.length, 1);
  assert.equal(button.attr('href'), scalar(linked, 'link'));

  const unlinked = 'researchers/gowoon-yang-19';
  assert.equal(scalar(unlinked, 'link'), undefined);
  const box = cardOf($, unlinked).find('div.link01');
  assert.equal(box.length, 1);
  assert.equal(box.children().length, 0);
  assert.equal(box.text().trim(), '');
});

test('multi-line field value renders <br> between its lines', () => {
  const file = 'alumni/byeongguk-min-33';
  const block = frontmatter(file).match(/^ {2}value: \|-\n((?: {4}.*\n?)+)/m);
  assert.ok(block, 'file has a multi-line value');
  const lines = block[1].trimEnd().split('\n').map((l) => l.slice(4));
  assert.ok(lines.length > 1);

  const $ = page('member/alumni');
  const dd = cardOf($, file)
    .find('dl dd')
    .filter((_, el) => $(el).find('br').length > 0);
  assert.equal(dd.length, 1);
  assert.equal(dd.find('br').length, lines.length - 1);
  assert.equal(dd.text(), lines.join(''));
});

test('researchers: the active tab carries the skin highlight id', () => {
  const $ = page('member/researchers');
  assert.equal($('#bo_cate a#bo_cate_on').length, 1);
  assert.equal($('#bo_cate a#bo_cate_on').text().trim(), '전체');
});

test('collaborators: an empty-label dt drops its padding', () => {
  const $ = page('member/collaborators');
  const dt = $('.mb_peple').first().find('dt').first();
  assert.equal(dt.text(), '');
  assert.equal(dt.attr('style'), 'padding-left:0');
});

/** One wrapper per page; one `.member_list` per category plus one for the uncategorised members, if any. */
function assertSections(board) {
  const $ = page(`member/${board}`);
  assert.equal($('#member_professor').length, 1);
  assert.equal($('#gall_ul').length, 1);
  const files = memberFiles(board);
  const categories = new Set(files.map((f) => scalar(f, 'category')).filter(Boolean));
  const uncategorised = files.some((f) => !scalar(f, 'category')) ? 1 : 0;
  assert.equal($('#gall_ul .member_list').length, categories.size + uncategorised);
  assert.equal($('#gall_ul h3.mb_cate_title').length, categories.size);
  $('#gall_ul h3.mb_cate_title').each((_, h) => assert.ok($(h).next().is('.member_list'), $(h).text()));
}

test('researchers: unique list ids, one list per category', () => {
  assertSections('researchers');
  assert.equal(page('member/researchers')('#gall_ul .member_list').length, 2);
});

test('alumni: unique list ids, one list per category plus the uncategorised one', () => {
  assertSections('alumni');
  assert.equal(page('member/alumni')('#gall_ul .member_list').length, 3);
});

test('boards without categories: one wrapper and one list', () => {
  for (const board of ['collaborators', 'internship']) {
    const $ = page(`member/${board}`);
    assert.equal($('#member_professor').length, 1, board);
    assert.equal($('#gall_ul').length, 1, board);
    assert.equal($('#gall_ul .member_list').length, 1, board);
  }
});
