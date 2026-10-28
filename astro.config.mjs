import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://ympbel.github.io',
  i18n: { defaultLocale: 'ko', locales: ['ko', 'en'], routing: { prefixDefaultLocale: false } },
  // CSS minification targets. Without them Lightning CSS prints `@media (max-width: …)` as range syntax
  // `(width<=…)`, which phone browsers before iOS 16.4 / Chrome 104 ignore, dropping the whole responsive layer.
  vite: { build: { cssTarget: ['chrome87', 'edge88', 'firefox78', 'safari14', 'ios14'] } },
});
