import { test } from 'node:test';
import assert from 'node:assert/strict';
import { memberSchema, publicationSchema, postSchema, pageSchema } from '../../src/content/schemas.ts';

test('member requires name and order', () => {
  assert.equal(memberSchema.safeParse({ board: 'researchers', order: 1 }).success, false);
  const ok = memberSchema.safeParse({ board: 'researchers', order: 1, name: '양고운 Gowoon Yang' });
  assert.equal(ok.success, true);
  assert.deepEqual(ok.data?.fields, []);
  const linked = memberSchema.safeParse({ board: 'researchers', name: 'x', order: 1, link: 'https://example.org' });
  assert.equal(linked.success, true);
  assert.equal(linked.data?.link, 'https://example.org');
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

test('post: an unquoted YAML date (a Date) is read as YYYY-MM-DD', () => {
  const ok = postSchema.safeParse({ title: 'x', date: new Date('2026-11-04T00:00:00Z') });
  assert.equal(ok.success, true);
  assert.equal(ok.data?.date, '2026-11-04');
  const lecture = postSchema.safeParse({ title: 'x', date: '2026-11-04', event_date: new Date('2026-11-05T00:00:00Z') });
  assert.equal(lecture.success, true);
  assert.equal(lecture.data?.event_date, '2026-11-05');
});

test('post and member: a numeric category (unquoted year) becomes a string', () => {
  const post = postSchema.safeParse({ title: 'x', date: '2026-11-04', category: 2026 });
  assert.equal(post.success, true);
  assert.equal(post.data?.category, '2026');
  const member = memberSchema.safeParse({ board: 'alumni', name: 'x', order: 1, category: 2026 });
  assert.equal(member.success, true);
  assert.equal(member.data?.category, '2026');
});

test('every schema rejects unknown keys', () => {
  const post = postSchema.safeParse({ title: 'x', date: '2026-11-04', pined: true });
  assert.equal(post.success, false);
  assert.match(JSON.stringify(post.error?.issues), /pined/);
  assert.equal(memberSchema.safeParse({ board: 'alumni', name: 'x', order: 1, nmae: 'y' }).success, false);
  assert.equal(publicationSchema.safeParse({ year: 2026, title: 'T', autors: 'A' }).success, false);
  assert.equal(pageSchema.safeParse({ title: 'T', section: 'home', link: [] }).success, false);
});
