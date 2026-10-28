import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { load } from 'cheerio';
import { DIST, allHtmlFiles } from './helpers.mjs';

const OLD_HOST = 'mpbel.yonsei.ac.kr';

const isFile = (path) => existsSync(path) && statSync(path).isFile();

const resolved = new Map();
/** Whether a site-root URL (`/x/`, `/x`, `/images/a.png`, with any `?query` or `#fragment`) is served from a file
 * in `dist/`: `/x/` → `dist/x/index.html`, `/x` → `dist/x` or `dist/x/index.html`. Percent-encoding is decoded and
 * the path is NFC-normalized, the form Korean path segments are written to disk in. */
function resolves(url) {
  if (!resolved.has(url)) {
    let path = null;
    try {
      path = decodeURIComponent(url.replace(/[?#].*$/, '')).normalize('NFC');
    } catch {
      // Malformed percent-encoding: counted as a miss.
    }
    const file = path === null ? null : join(DIST, path);
    resolved.set(
      url,
      file !== null && (path.endsWith('/') ? isFile(join(file, 'index.html')) : isFile(file) || isFile(join(file, 'index.html'))),
    );
  }
  return resolved.get(url);
}

test('every site-root a[href] and img[src] resolves to a file in dist/', () => {
  const misses = [];
  for (const file of allHtmlFiles()) {
    const $ = load(readFileSync(file, 'utf8'));
    $('a[href], img[src]').each((_, el) => {
      const url = $(el).attr(el.tagName === 'a' ? 'href' : 'src');
      if (url.startsWith('/') && !url.startsWith('//') && !resolves(url)) misses.push(`${relative(DIST, file)}: ${url}`);
    });
  }
  assert.deepEqual(misses, []);
});

test(`no href or src points at ${OLD_HOST} outside crawled post bodies`, (t) => {
  const outside = [];
  let inBodies = 0;
  for (const file of allHtmlFiles()) {
    const $ = load(readFileSync(file, 'utf8'));
    $(`[href*="${OLD_HOST}"], [src*="${OLD_HOST}"]`).each((_, el) => {
      // A post body (#bo_v_con) keeps the crawled text's links to the old board as faithful content.
      if ($(el).closest('#bo_v_con').length) inBodies += 1;
      else outside.push(`${relative(DIST, file)}: ${$(el).attr('href') ?? $(el).attr('src')}`);
    });
  }
  t.diagnostic(`${inBodies} links to ${OLD_HOST} kept inside post bodies (#bo_v_con)`);
  assert.deepEqual(outside, []);
});
