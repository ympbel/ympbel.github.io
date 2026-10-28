import type { Locale } from './content.ts';

export type MenuItem = { label: string; href: string };
export type SectionKey = 'introduction' | 'member' | 'research' | 'publication' | 'lecture' | 'notice';
export type MenuSection = { key: SectionKey; label: string; href: string; items: MenuItem[] };

/** A section whose `href` is its first item's href. */
function section(key: SectionKey, label: string, items: MenuItem[]): MenuSection {
  return { key, label, href: items[0].href, items };
}

// Advanced CT Reconstruction is deliberately absent from the menu; the home card links to /research/ct-reconstruction/.
const ko: MenuSection[] = [
  section('introduction', 'INTRODUCTION', [
    { label: 'welcome to MPBEL', href: '/introduction/welcome/' },
    { label: 'contact us', href: '/introduction/contact/' },
  ]),
  section('member', 'MEMBER', [
    { label: 'Professor', href: '/member/professor/' },
    { label: 'Collaborators', href: '/member/collaborators/' },
    { label: 'Researchers', href: '/member/researchers/' },
    { label: 'Alumni', href: '/member/alumni/' },
    { label: 'Short-term internship', href: '/member/internship/' },
  ]),
  section('research', 'RESEARCH', [
    { label: 'Artificial Intelligence', href: '/research/ai/' },
    { label: 'Radiation Therapy', href: '/research/radiation-therapy/' },
    { label: 'Particle Therapy', href: '/research/particle-therapy/' },
  ]),
  section('publication', 'PUBLICATION', [
    { label: 'Paper', href: '/publication/paper/' },
    { label: 'Presentation', href: '/publication/presentation/' },
    { label: 'Invited talk', href: '/publication/invited-talk/' },
    { label: 'Patent', href: '/publication/patent/' },
  ]),
  section('lecture', 'LECTURE', [{ label: 'Lecture', href: '/lecture/' }]),
  section('notice', 'NOTICE', [
    { label: 'News', href: '/notice/news/' },
    { label: 'Gallery', href: '/notice/gallery/' },
    { label: 'Seminar', href: '/notice/seminar/' },
  ]),
];

/** Same tree for both locales in phase 1 (phase 2 prefixes the English hrefs with `/en`). */
export const MENU: Record<Locale, MenuSection[]> = { ko, en: ko };

/** The menu section a pathname belongs to, by its first path segment. */
export function sectionOf(pathname: string, locale: Locale = 'ko'): MenuSection | undefined {
  return MENU[locale].find((s) => pathname.startsWith('/' + s.key + '/'));
}

/** `research-ai` → `/research/ai/`. */
export function researchPath(pageSlug: string): string {
  return '/research/' + pageSlug.replace(/^research-/, '') + '/';
}

/** `ai` (route param) → `research-ai` (page slug). */
export function researchSlugFromPath(param: string): string {
  return 'research-' + param;
}
