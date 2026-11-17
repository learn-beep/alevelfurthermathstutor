import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

export default defineConfig({
  site: 'https://www.alevelfurthermathstutor.com',
  trailingSlash: 'always',
  integrations: [sitemap({ filter: (page) => !page.includes('/print/') && !page.includes('/data/') && !page.includes('/thank-you/') })],
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
  },
});
