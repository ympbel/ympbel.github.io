import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DIST, exists, page } from './helpers.mjs';

const SOURCE = fileURLToPath(new URL('../../src/styles/responsive.css', import.meta.url));

/** Every built stylesheet (`dist/_astro/*.css`), concatenated. */
const builtCss = readdirSync(join(DIST, '_astro'))
  .filter((f) => f.endsWith('.css'))
  .sort()
  .map((f) => readFileSync(join(DIST, '_astro', f), 'utf8'))
  .join('\n');
/** The same without whitespace, for whitespace-insensitive matching. */
const squashed = builtCss.replace(/\s+/g, '');

/** End index (exclusive) of the block whose `{` is at `open`. */
function blockEnd(css, open) {
  let depth = 0;
  for (let i = open; i < css.length; i++) {
    if (css[i] === '{') depth++;
    else if (css[i] === '}' && --depth === 0) return i + 1;
  }
  return css.length;
}

/** Bodies of the `@media<query>{…}` blocks of whitespace-free CSS, e.g. `query` = `(max-width:600px)`. */
function mediaBodies(css, query) {
  const head = `@media${query}{`;
  const bodies = [];
  for (let at = css.indexOf(head); at !== -1; at = css.indexOf(head, at + 1)) {
    bodies.push(css.slice(at + head.length, blockEnd(css, at + head.length - 1) - 1));
  }
  return bodies;
}

test('English placeholder: lang en, EN active, link to the Korean site', () => {
  assert.ok(exists('en'));
  const $ = page('en');
  assert.equal($('html').attr('lang'), 'en');
  assert.equal($('.langbut li.active a').text().trim(), 'EN');
  assert.equal($('.contentBox h2.cnt_title').text().trim(), 'English');
  assert.equal(
    $('.contentBox p.preparing').text().trim(),
    'The English pages are being prepared. Please use the Korean site for now.',
  );
  assert.equal($('.contentBox a[href="/"]').text().trim(), 'Go to Korean site');
});

test('404 page at dist/404.html with a link home', () => {
  assert.ok(exists('404.html'));
  const $ = page('404.html');
  assert.equal($('.contentBox h2.cnt_title').text().trim(), 'Page not found');
  assert.ok($('.contents').text().includes('요청하신 페이지를 찾을 수 없습니다.'));
  assert.equal($('.contents a[href="/"]').text().trim(), '홈으로');
});

test('home: closed mobile nav toggle and its inline script', () => {
  const $ = page('');
  assert.equal($('button.nav-toggle[aria-expanded="false"]').length, 1);
  const scripts = $('script:not([src])').filter((_, s) => $(s).text().includes('nav-toggle'));
  assert.equal(scripts.length, 1);
});

test('built CSS: responsive layer at ≤1024px shows the nav toggle, no relative url()', () => {
  assert.ok(squashed.includes('@media(max-width:1024px)'));
  assert.ok(squashed.includes('.nav-toggle{display:block'));
  assert.ok(!builtCss.includes('url(../'));
});

test('built CSS: drawer and member rules sit inside the media blocks', () => {
  assert.ok(mediaBodies(squashed, '(max-width:1024px)').some((b) => b.includes('#navi.open')));
  assert.ok(mediaBodies(squashed, '(max-width:600px)').some((b) => b.includes('.mb_peple{width:100%')));
});

test('responsive.css source: no rule outside @media blocks (desktop unchanged)', () => {
  assert.ok(existsSync(SOURCE));
  let css = readFileSync(SOURCE, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
  for (let at = css.indexOf('@media'); at !== -1; at = css.indexOf('@media')) {
    css = css.slice(0, at) + css.slice(blockEnd(css, css.indexOf('{', at)));
  }
  assert.ok(!css.includes('{'), `rule outside @media: ${css.trim().slice(0, 80)}`);
});
