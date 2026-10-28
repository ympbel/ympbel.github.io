import { test } from 'node:test';
import assert from 'node:assert/strict';
import { MENU, sectionOf, researchPath, researchSlugFromPath } from '../../src/lib/menu.ts';

test('the Korean menu has 6 sections and 18 items', () => {
  assert.equal(MENU.ko.length, 6);
  assert.equal(MENU.ko.reduce((n, s) => n + s.items.length, 0), 18);
});

test('sectionOf finds the section by path prefix', () => {
  assert.equal(sectionOf('/member/researchers/')?.key, 'member');
  assert.equal(sectionOf('/'), undefined);
});

test('researchPath and researchSlugFromPath convert between page slug and URL', () => {
  assert.equal(researchPath('research-ai'), '/research/ai/');
  assert.equal(researchSlugFromPath('ct-reconstruction'), 'research-ct-reconstruction');
});

test('every menu href is root-absolute and ends with a slash', () => {
  for (const section of MENU.ko) {
    for (const href of [section.href, ...section.items.map((i) => i.href)]) {
      assert.ok(href.startsWith('/') && href.endsWith('/'), href);
    }
  }
});
