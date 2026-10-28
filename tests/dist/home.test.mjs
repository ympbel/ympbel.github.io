import { test } from 'node:test';
import assert from 'node:assert/strict';
import { page } from './helpers.mjs';

const $ = page('');

test('header: menu with 6 sections and 18 links, KR active', () => {
  assert.equal($('#nav > li').length, 6);
  assert.equal($('#nav ul li a').length, 18);
  assert.equal($('#nav > li:nth-child(3) ul li').length, 3);
  assert.equal($('.langbut li.active a').text().trim(), 'KR');
});

test('research cards', () => {
  assert.equal($('.research_wrap li').length, 4);
  assert.equal($('.research_wrap li.rs1 a').attr('href'), '/research/ct-reconstruction/');
});

test('latest news and seminars, 4 each with MM-DD dates', () => {
  assert.equal($('.l_bo .lat ul li').length, 4);
  const dates = $('.l_bo .lat .lt_date').map((_, el) => $(el).text()).get();
  assert.equal(dates.length, 4);
  for (const d of dates) assert.match(d, /^\d{2}-\d{2}$/);
  assert.equal($('.r_bo .lat ul li').length, 4);
});

test('external links and publication icons', () => {
  assert.equal($('.link ul li').length, 4);
  assert.equal($('.publication li').length, 3);
  assert.equal($('.publication li').eq(2).find('a').attr('href'), '/publication/patent/');
});

test('external link labels 2 and 4 keep the old <br> line break', () => {
  assert.equal($('.link ul li:nth-child(1) a br').length, 0);
  assert.equal($('.link ul li:nth-child(2) a br').length, 1);
  assert.equal($('.link ul li:nth-child(3) a br').length, 0);
  assert.equal($('.link ul li:nth-child(4) a br').length, 1);
});

test('footer without the DSSO credit', () => {
  assert.ok($('#footer').text().includes('ALL RIGHT RESERVED.'));
  assert.ok(!$('#footer').text().includes('DSSO'));
});

test('head: viewport, Google Fonts, no jQuery', () => {
  assert.equal($('meta[name=viewport]').length, 1);
  assert.equal($('script[src*=jquery]').length, 0);
  assert.ok($('link[href*="fonts.googleapis"]').length >= 1);
});

test('head: Nanum Gothic is loaded with its bold weights', () => {
  const hrefs = $('link[href*="fonts.googleapis"]').map((_, el) => $(el).attr('href')).get();
  assert.ok(hrefs.some((h) => h.includes('Nanum+Gothic:400,700,800')), hrefs.join(' '));
});
