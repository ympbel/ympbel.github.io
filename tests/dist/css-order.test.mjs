import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { load } from 'cheerio';
import { DIST, allHtmlFiles } from './helpers.mjs';

// The global bundle is the one with the header rules; a board skin bundle is any other bundle with a skin's rules.
const GLOBAL_MARKER = '.topmenu';
const SKIN_MARKERS = ['.mb_peple', '.publication_oldver', '#bo_list', '.tbl_head01', '.gall_row', '.welcome_wrap', '.pfwrap'];

const cssCache = new Map();
/** Text of a built stylesheet, read once. */
function css(href) {
  if (!cssCache.has(href)) cssCache.set(href, readFileSync(join(DIST, href), 'utf8'));
  return cssCache.get(href);
}

test('every page links the global CSS before its board skin CSS, as the old pages loaded default.css first', () => {
  const wrong = [];
  for (const file of allHtmlFiles()) {
    const $ = load(readFileSync(file, 'utf8'));
    const hrefs = $('link[rel=stylesheet][href^="/_astro/"]')
      .map((_, link) => $(link).attr('href'))
      .get();
    const globalAt = hrefs.findIndex((h) => css(h).includes(GLOBAL_MARKER));
    const skinAt = hrefs.findIndex((h, i) => i !== globalAt && SKIN_MARKERS.some((m) => css(h).includes(m)));
    if (globalAt === -1 || (skinAt !== -1 && skinAt < globalAt)) wrong.push(`${relative(DIST, file)}: ${hrefs.join(' ')}`);
  }
  assert.deepEqual(wrong, []);
});
