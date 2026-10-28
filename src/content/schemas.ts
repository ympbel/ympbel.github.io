import { z } from 'astro/zod';

// Every schema is strict: a misspelt or unknown frontmatter key (`pined: true`) fails the build instead of being
// silently dropped.

/** `YYYY-MM-DD`. An unquoted date in YAML (`date: 2026-11-04`) arrives as a Date and is read back as that day. */
const isoDate = z.preprocess(
  (v) => (v instanceof Date && !Number.isNaN(v.getTime()) ? v.toISOString().slice(0, 10) : v),
  z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
);

/** A category label. An unquoted year in YAML (`category: 2026`) arrives as a number and is read as `'2026'`. */
const category = z.preprocess((v) => (typeof v === 'number' ? String(v) : v), z.string());

export const pageSchema = z
  .object({
    title: z.string(),
    section: z.enum(['home', 'introduction', 'member', 'research']),
    images: z.array(z.string()).default([]),
    links: z.array(z.object({ label: z.string(), url: z.string() })).default([]),
    legacy_url: z.string().optional(),
  })
  .strict();

export const memberSchema = z
  .object({
    board: z.enum(['researchers', 'collaborators', 'alumni', 'internship']),
    category: category.optional(),
    name: z.string().min(1),
    photo: z.string().optional(),
    link: z.string().optional(),
    fields: z.array(z.object({ label: z.string().default(''), value: z.string() })).default([]),
    order: z.number().int(),
    legacy_url: z.string().optional(),
    legacy_id: z.number().int().optional(),
  })
  .strict();

export const publicationSchema = z
  .object({
    year: z.number().int().min(1990).max(2100),
    title: z.string().min(1),
    authors: z.string().default(''),
    venue: z.string().default(''),
    link: z.string().optional(),
    pinned: z.boolean().default(false),
    order: z.number().int().optional(),
    legacy_files: z.array(z.object({ name: z.string(), url: z.string() })).default([]),
    legacy_url: z.string().optional(),
    legacy_id: z.number().int().optional(),
  })
  .strict();

export const postSchema = z
  .object({
    title: z.string().min(1),
    date: isoDate,
    category: category.optional(),
    pinned: z.boolean().default(false),
    presenter: z.string().optional(),
    event_date: isoDate.optional(),
    legacy_images: z.array(z.string()).default([]),
    legacy_files: z.array(z.object({ name: z.string(), url: z.string() })).default([]),
    legacy_url: z.string().optional(),
    legacy_id: z.number().int().optional(),
  })
  .strict();
