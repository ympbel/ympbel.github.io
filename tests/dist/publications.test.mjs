import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { exists, page } from './helpers.mjs';

const CONTENT = fileURLToPath(new URL('../../src/content/', import.meta.url));
const KINDS = { paper: 'papers', presentation: 'presentations', 'invited-talk': 'talks', patent: 'patents' };

/** Number of entries in `src/content/<collection>/ko/` (templates `_*.md` excluded, as in the collection loader). */
function fileCount(collection) {
  return readdirSync(`${CONTENT}${collection}/ko/`).filter((f) => f.endsWith('.md') && !f.startsWith('_')).length;
}

test('publication pages are built', () => {
  for (const kind of Object.keys(KINDS)) assert.ok(exists(`publication/${kind}`), kind);
});

test('every entry renders one row with its button row, striped bg1/bg0', () => {
  for (const [kind, collection] of Object.entries(KINDS)) {
    const $ = page(`publication/${kind}`);
    const count = fileCount(collection);
    assert.equal($('.tb_basic_s').length, count, kind);
    assert.equal($('.tb_basic_s td.btn_positon').length, count, kind);
    assert.equal($('tr.bg1').length + $('tr.bg0').length, count, kind);
    assert.equal($('#bo_cate_ul li').length, $('.year_title').length, kind);
    for (const a of $('#bo_cate_ul a').get()) {
      assert.equal($($(a).attr('href')).length, 1, `${kind} ${$(a).attr('href')}`);
    }
  }
});

test('paper: newest year first, numbering, authors and DOI links', () => {
  const $ = page('publication/paper');
  const count = fileCount('papers');
  assert.equal($('.year_title').first().text().trim(), '2025');
  assert.equal($('.tb_basic_s').length, count);
  assert.equal($('#bo_cate_ul li').length, $('.year_title').length);
  assert.ok($('a.btn_set01[href^="https://doi.org"]').length >= 50, String($('a.btn_set01[href^="https://doi.org"]').length));
  assert.ok($('.text_author').first().text().startsWith('Younghun Yoon'), $('.text_author').first().text());
  assert.equal($('td.num').first().text().trim(), String(count));
});

test('patent: labelled venue lines', () => {
  const journal = page('publication/patent')('.text_journal').first().text();
  assert.ok(journal.includes('등록번호'), journal);
  assert.ok(journal.includes('10-2020-0106825'), journal);
});

test('invited talk: pinned entry shows 공지', () => {
  const $ = page('publication/invited-talk');
  assert.equal($('td.num strong').first().text(), '공지');
});

test('paper: comma after the first venue line, as in the old paper skin', () => {
  const html = page('publication/paper')('.text_journal').first().html();
  assert.match(html, /^\s*<span class="text_vol">[^<]*<\/span>, ?<br>/, html);
});

test('presentation: no comma after venue lines', () => {
  const html = page('publication/presentation')('.text_journal').first().html();
  assert.ok(!html.includes('</span>,'), html);
});
