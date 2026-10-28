import type { Locale } from '../lib/content.ts';
import { ko } from './ko.ts';
import { en } from './en.ts';

export type Strings = typeof ko;

const STRINGS: Record<Locale, Strings> = { ko, en };

/** UI strings for a locale. */
export function t(locale: Locale): Strings {
  return STRINGS[locale];
}
