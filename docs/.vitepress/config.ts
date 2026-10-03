import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'ICVDB Torznab',
  description: 'Self-hosted ICVDB bridge for Torznab clients',
  base: '/icvdb-torznab/',
  cleanUrls: true,
  lastUpdated: true,
  head: [['meta', { name: 'theme-color', content: '#7c3aed' }]],
  themeConfig: {
    siteTitle: 'ICVDB Torznab',
    nav: [
      { text: 'Getting Started', link: '/getting-started/installation' },
      { text: 'Configuration', link: '/configuration/webui' },
      { text: 'Features', link: '/features/torznab' },
      { text: 'Reference', link: '/reference/api' },
      { text: 'Changelog', link: '/changelog' },
    ],
    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Installation', link: '/getting-started/installation' },
          { text: 'Docker', link: '/getting-started/docker' },
          { text: 'Docker Compose', link: '/getting-started/docker-compose' },
          { text: 'First setup', link: '/getting-started/first-setup' },
        ],
      },
      {
        text: 'Configuration',
        items: [
          { text: 'WebUI', link: '/configuration/webui' },
          { text: 'Database updates', link: '/configuration/database-updates' },
          {
            text: 'Result processing',
            link: '/configuration/result-processing',
          },
          { text: 'Prowlarr integration', link: '/configuration/prowlarr' },
          { text: 'Environment variables', link: '/configuration/environment' },
        ],
      },
      {
        text: 'Features',
        items: [
          { text: 'Torznab', link: '/features/torznab' },
          { text: 'Italian ranking', link: '/features/italian-ranking' },
          { text: 'Custom filters', link: '/features/custom-filters' },
          {
            text: 'Automatic DB updates',
            link: '/features/automatic-db-updates',
          },
        ],
      },
      {
        text: 'How it works',
        items: [
          { text: 'Architecture', link: '/how-it-works/architecture' },
          { text: 'PostgreSQL', link: '/how-it-works/postgresql' },
          { text: 'Snapshot system', link: '/how-it-works/snapshots' },
          { text: 'Safe updates', link: '/how-it-works/safe-updates' },
          {
            text: 'Result processing',
            link: '/how-it-works/result-processing',
          },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'API', link: '/reference/api' },
          {
            text: 'Torznab capabilities',
            link: '/reference/torznab-capabilities',
          },
          {
            text: 'Configuration schema',
            link: '/reference/configuration-schema',
          },
        ],
      },
      {
        text: 'Help',
        items: [
          { text: 'Troubleshooting', link: '/troubleshooting' },
          { text: 'Changelog', link: '/changelog' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/xbit18/icvdb-torznab' },
    ],
    editLink: {
      pattern: 'https://github.com/xbit18/icvdb-torznab/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },
    search: { provider: 'local' },
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'ICVDB Torznab documentation',
    },
  },
})
