import { load } from 'cheerio';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const DIST = fileURLToPath(new URL('../../dist/', import.meta.url));

/** `dist/<path>` for a file path ending in `.html` (e.g. `404.html`), else `dist/<path>/index.html` (`''` for the
 * root page). */
function htmlFile(path) {
  return path.endsWith('.html') ? join(DIST, path) : join(DIST, path, 'index.html');
}

/** Cheerio document of the built page at `path`. */
export function page(path) {
  return load(readFileSync(htmlFile(path), 'utf8'));
}

/** Whether the build produced a page at `path`. */
export function exists(path) {
  return existsSync(htmlFile(path));
}

/** Absolute paths of every `dist/**\/*.html`, sorted. */
export function allHtmlFiles() {
  return readdirSync(DIST, { recursive: true })
    .filter((f) => f.endsWith('.html'))
    .map((f) => join(DIST, f))
    .sort();
}
