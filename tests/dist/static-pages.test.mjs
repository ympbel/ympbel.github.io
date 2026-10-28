import { test } from 'node:test';
import assert from 'node:assert/strict';
import { exists, page } from './helpers.mjs';

test('static pages are built', () => {
  for (const path of [
    'introduction/welcome',
    'introduction/contact',
    'member/professor',
    'research/ai',
    'research/ct-reconstruction',
    'research/radiation-therapy',
    'research/particle-therapy',
  ]) {
    assert.ok(exists(path), path);
  }
});

test('welcome: title, active side menu, breadcrumb and local images', () => {
  const $ = page('introduction/welcome');
  assert.equal($('.cnt_title').text().trim(), 'Welcome to MPBEL');
  assert.equal($('.snb .vNav li.active a').attr('href'), '/introduction/welcome/');
  assert.equal($('.loc li.last').text().trim(), 'Welcome to MPBEL');
  assert.ok($('.contents img').attr('src').startsWith('/images/pages/welcome/'), $('.contents img').attr('src'));
});

test('contact: Google Maps iframe and CSS map-marker icon', () => {
  const $ = page('introduction/contact');
  assert.equal($('.contents iframe[src*="google.com/maps"]').length, 1);
  assert.equal($('.contents i.fa-map-marker').length, 1);
});

test('professor: profile block', () => {
  const $ = page('member/professor');
  assert.equal($('.prof_info').length, 1);
});

test('research/ai: five local images', () => {
  const $ = page('research/ai');
  const srcs = $('.contents img').map((_, el) => $(el).attr('src')).get();
  assert.equal(srcs.length, 5);
  for (const src of srcs) assert.ok(!src.includes('mpbel.yonsei.ac.kr'), src);
});

test('research/ct-reconstruction: not in the side menu, breadcrumb title', () => {
  const $ = page('research/ct-reconstruction');
  assert.equal($('.snb .vNav li.active').length, 0);
  assert.equal($('.loc li.last').text().trim(), 'Advanced CT Reconstruction');
});
