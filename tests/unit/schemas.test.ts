import { test } from 'node:test';
import assert from 'node:assert/strict';
import { memberSchema, publicationSchema, postSchema, pageSchema } from '../../src/content/schemas.ts';

test('member requires name and order', () => {
  assert.equal(memberSchema.safeParse({ board: 'researchers', order: 1 }).success, false);
  const ok = memberSchema.safeParse({ board: 'researchers', order: 1, name: '양고운 Gowoon Yang' });
  assert.equal(ok.success, true);
  assert.deepEqual(ok.data?.fields, []);
});

test('publication coerces defaults', () => {
  const ok = publicationSchema.safeParse({ year: 2025, title: 'T' });
  assert.equal(ok.success, true);
  assert.equal(ok.data?.authors, '');
  assert.equal(ok.data?.pinned, false);
  assert.deepEqual(ok.data?.legacy_files, []);
  assert.equal(publicationSchema.safeParse({ year: '2025', title: 'T' }).success, false);
});

test('post date format', () => {
  assert.equal(postSchema.safeParse({ title: 'x', date: '2025-10-22' }).success, true);
  assert.equal(postSchema.safeParse({ title: 'x', date: '25-10-22' }).success, false);
  assert.equal(postSchema.safeParse({ title: 'x', date: '2025-10-22', event_date: '2018.04.19' }).success, false);
});

test('page section enum', () => {
  assert.equal(pageSchema.safeParse({ title: 'T', section: 'research' }).success, true);
  assert.equal(pageSchema.safeParse({ title: 'T', section: 'notice' }).success, false);
});
