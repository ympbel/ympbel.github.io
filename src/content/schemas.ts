import { z } from 'astro/zod';

export const pageSchema = z.object({
  title: z.string(),
  section: z.enum(['home', 'introduction', 'member', 'research']),
  images: z.array(z.string()).default([]),
  links: z.array(z.object({ label: z.string(), url: z.string() })).default([]),
  legacy_url: z.string().optional(),
});

export const memberSchema = z.object({
  board: z.enum(['researchers', 'collaborators', 'alumni', 'internship']),
  category: z.string().optional(),
  name: z.string().min(1),
  photo: z.string().optional(),
  fields: z.array(z.object({ label: z.string().default(''), value: z.string() })).default([]),
  order: z.number().int(),
  legacy_url: z.string().optional(),
  legacy_id: z.number().int().optional(),
});

export const publicationSchema = z.object({
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
});

export const postSchema = z.object({
  title: z.string().min(1),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  category: z.string().optional(),
  pinned: z.boolean().default(false),
  presenter: z.string().optional(),
  event_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  legacy_images: z.array(z.string()).default([]),
  legacy_files: z.array(z.object({ name: z.string(), url: z.string() })).default([]),
  legacy_url: z.string().optional(),
  legacy_id: z.number().int().optional(),
});
