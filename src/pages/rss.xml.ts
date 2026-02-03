import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET() {
  const posts = (await getCollection('posts'))
    .filter((p) => !p.data.draft)
    .sort((a, b) => new Date(b.data.date).valueOf() - new Date(a.data.date).valueOf());

  const site = import.meta.env.SITE ?? 'https://smadonkuan.github.io';

  return rss({
    title: '呂依璇 Elaine Lu - Blog',
    description: 'Information Security Researcher - 技術與資安文章',
    site,
    items: posts.map((post) => ({
      link: `/posts/${post.slug}`,
      title: post.data.title,
      pubDate: new Date(post.data.date),
      description: post.data.excerpt,
    })),
    customData: '<language>zh-tw</language>',
  });
}
