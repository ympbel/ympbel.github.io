import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://ympbel.github.io',
  i18n: { defaultLocale: 'ko', locales: ['ko', 'en'], routing: { prefixDefaultLocale: false } },
});
