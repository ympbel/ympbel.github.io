import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  localeOf,
  slugOf,
  isLocale,
  sortMembers,
  sortPublications,
  groupByYear,
  sortPosts,
  categoriesOf,
  categorySlug,
  paginateArray,
} from '../../src/lib/content.ts';

test('localeOf and slugOf split the entry id', () => {
  assert.equal(localeOf('ko/researchers/gowoon-yang-19'), 'ko');
  assert.equal(slugOf('ko/researchers/gowoon-yang-19'), 'researchers/gowoon-yang-19');
});

const pubs = [
  { id: 'a', data: { year: 2024, order: 5 } },
  { id: 'b', data: { year: 2025 } },
  { id: 'c', data: { year: 2025, order: 9 } },
];

test('sortPublications: year desc, order desc with missing order first', () => {
  assert.deepEqual(sortPublications(pubs).map((p) => p.id), ['b', 'c', 'a']);
});

test('groupByYear keeps input order', () => {
  const [a, b, c] = pubs;
  assert.deepEqual(groupByYear(sortPublications(pubs)), [
    { year: 2025, items: [b, c] },
    { year: 2024, items: [a] },
  ]);
});

test('sortPosts: date desc, legacy_id desc with missing legacy_id first', () => {
  const posts = [
    { id: 'x', data: { date: '2025-01-01', legacy_id: 1 } },
    { id: 'y', data: { date: '2025-01-01' } },
    { id: 'z', data: { date: '2025-02-01', legacy_id: 3 } },
  ];
  assert.deepEqual(sortPosts(posts).map((p) => p.id), ['z', 'y', 'x']);
});

test('categoriesOf: numeric desc first, then names', () => {
  const posts = [
    { data: { category: '연구실소식' } },
    { data: { category: '2024' } },
    { data: {} },
    { data: { category: '2025' } },
    { data: { category: '학회소식' } },
    { data: { category: '2024' } },
  ];
  assert.deepEqual(categoriesOf(posts), ['2025', '2024', '연구실소식', '학회소식']);
});

test('categorySlug makes a single path segment', () => {
  assert.equal(categorySlug(' A / B  C '), 'A-B-C');
  assert.equal(categorySlug('연구실소식'), '연구실소식');
});

test('paginateArray splits into pages', () => {
  assert.deepEqual(paginateArray([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
  assert.deepEqual(paginateArray([], 2), [[]]);
});

test('isLocale, sortMembers and id tie-breaks', () => {
  const entries = [{ id: 'ko/a' }, { id: 'en/b' }, { id: 'ko/c' }];
  assert.deepEqual(entries.filter(isLocale('ko')).map((e) => e.id), ['ko/a', 'ko/c']);
  const members = [
    { id: 'm2', data: { order: 1 } },
    { id: 'm3', data: { order: 0 } },
    { id: 'm1', data: { order: 1 } },
  ];
  assert.deepEqual(sortMembers(members).map((m) => m.id), ['m3', 'm1', 'm2']);
  const pubTies = [
    { id: 'p1', data: { year: 2025, order: 1 } },
    { id: 'p2', data: { year: 2025, order: 1 } },
  ];
  assert.deepEqual(sortPublications(pubTies).map((p) => p.id), ['p2', 'p1']);
  const postTies = [
    { id: 'q1', data: { date: '2025-01-01' } },
    { id: 'q2', data: { date: '2025-01-01' } },
  ];
  assert.deepEqual(sortPosts(postTies).map((p) => p.id), ['q2', 'q1']);
});
