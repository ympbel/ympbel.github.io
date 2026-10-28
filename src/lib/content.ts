export type Locale = 'ko' | 'en';

export const PAGE_SIZE = 20;

/** The four publication boards: route segment under `/publication/`, content collection and page title. */
export const PUB_KINDS = [
  { kind: 'paper', collection: 'papers', label: 'Paper' },
  { kind: 'presentation', collection: 'presentations', label: 'Presentation' },
  { kind: 'invited-talk', collection: 'talks', label: 'Invited talk' },
  { kind: 'patent', collection: 'patents', label: 'Patent' },
] as const;

/** Ascending comparison for numbers or strings; equal values (including Infinity) give 0. */
function asc<V extends number | string>(a: V, b: V): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Locale of a collection entry id such as `ko/researchers/gowoon-yang-19`. */
export function localeOf(id: string): Locale {
  return id.split('/')[0] as Locale;
}

/** Entry id without its locale segment: `ko/researchers/gowoon-yang-19` → `researchers/gowoon-yang-19`. */
export function slugOf(id: string): string {
  return id.split('/').slice(1).join('/');
}

export function isLocale(locale: Locale): (e: { id: string }) => boolean {
  return (e) => localeOf(e.id) === locale;
}

/** `order` ascending, ties by `id` ascending. */
export function sortMembers<T extends { data: { order: number }; id: string }>(a: T[]): T[] {
  return [...a].sort((x, y) => asc(x.data.order, y.data.order) || asc(x.id, y.id));
}

/** `year` descending, then `order` descending (missing order first), ties by `id` descending. */
export function sortPublications<T extends { data: { year: number; order?: number }; id: string }>(a: T[]): T[] {
  return [...a].sort(
    (x, y) =>
      asc(y.data.year, x.data.year) ||
      asc(y.data.order ?? Infinity, x.data.order ?? Infinity) ||
      asc(y.id, x.id),
  );
}

/** Groups items by year, keeping input order within a group and years in first-seen order. */
export function groupByYear<T extends { data: { year: number } }>(a: T[]): Array<{ year: number; items: T[] }> {
  const groups = new Map<number, T[]>();
  for (const item of a) {
    const items = groups.get(item.data.year);
    if (items) items.push(item);
    else groups.set(item.data.year, [item]);
  }
  return [...groups].map(([year, items]) => ({ year, items }));
}

/** `date` descending, then `legacy_id` descending (missing legacy_id first), ties by `id` descending. */
export function sortPosts<T extends { data: { date: string; legacy_id?: number }; id: string }>(a: T[]): T[] {
  return [...a].sort(
    (x, y) =>
      asc(y.data.date, x.data.date) ||
      asc(y.data.legacy_id ?? Infinity, x.data.legacy_id ?? Infinity) ||
      asc(y.id, x.id),
  );
}

/** Distinct non-empty categories: all-digit values (years) first, descending; then the rest in Korean collation order. */
export function categoriesOf(posts: Array<{ data: { category?: string } }>): string[] {
  const distinct = [...new Set(posts.map((p) => p.data.category).filter((c): c is string => !!c))];
  const isNumeric = (c: string) => /^\d+$/.test(c);
  const numeric = distinct.filter(isNumeric).sort((a, b) => Number(b) - Number(a));
  const named = distinct.filter((c) => !isNumeric(c)).sort((a, b) => a.localeCompare(b, 'ko'));
  return [...numeric, ...named];
}

/** Single URL path segment for a category: trimmed, with runs of `/` and whitespace replaced by `-`. */
export function categorySlug(category: string): string {
  return category.trim().replace(/[\s/]+/g, '-');
}

/** Splits items into pages of `size`; an empty list gives one empty page. */
export function paginateArray<T>(items: T[], size: number): T[][] {
  if (items.length === 0) return [[]];
  const pages: T[][] = [];
  for (let i = 0; i < items.length; i += size) pages.push(items.slice(i, i + size));
  return pages;
}
