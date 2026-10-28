import { load } from 'cheerio';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const DIST = fileURLToPath(new URL('../../dist/', import.meta.url));

/** `dist/<path>/index.html` (`''` for the root page). */
function indexFile(path) {
  return join(DIST, path, 'index.html');
}

/** Cheerio document of the built page at `path`. */
export function page(path) {
  return load(readFileSync(indexFile(path), 'utf8'));
}

/** Whether the build produced a page at `path`. */
export function exists(path) {
  return existsSync(indexFile(path));
}

/** Absolute paths of every `dist/**\/*.html`, sorted. */
export function allHtmlFiles() {
  return readdirSync(DIST, { recursive: true })
    .filter((f) => f.endsWith('.html'))
    .map((f) => join(DIST, f))
    .sort();
}
