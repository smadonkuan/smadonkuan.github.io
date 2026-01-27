import { defineCollection, z } from 'astro:content';

const postsCollection = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        date: z.string(),
        excerpt: z.string(),
        tags: z.array(z.string()),
        readTime: z.string().optional(),
    })
});

export const collections = {
    'posts': postsCollection,
};
