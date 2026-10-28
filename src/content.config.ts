import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { pageSchema, memberSchema, publicationSchema, postSchema } from './content/schemas.ts';

// Files whose basename starts with `_` (templates) are excluded from every collection.
const markdownIn = (name: string) =>
  glob({ pattern: ['**/*.md', '!**/_*.md'], base: `./src/content/${name}` });

export const collections = {
  pages: defineCollection({ loader: markdownIn('pages'), schema: pageSchema }),
  members: defineCollection({ loader: markdownIn('members'), schema: memberSchema }),
  papers: defineCollection({ loader: markdownIn('papers'), schema: publicationSchema }),
  presentations: defineCollection({ loader: markdownIn('presentations'), schema: publicationSchema }),
  talks: defineCollection({ loader: markdownIn('talks'), schema: publicationSchema }),
  patents: defineCollection({ loader: markdownIn('patents'), schema: publicationSchema }),
  news: defineCollection({ loader: markdownIn('news'), schema: postSchema }),
  seminars: defineCollection({ loader: markdownIn('seminars'), schema: postSchema }),
  lectures: defineCollection({ loader: markdownIn('lectures'), schema: postSchema }),
};
