import { defineConfig } from 'vitepress'

const italianSidebar = [
  {
    text: 'Per iniziare',
    items: [
      { text: 'Installazione', link: '/getting-started/installation' },
      { text: 'Docker', link: '/getting-started/docker' },
      { text: 'Docker Compose', link: '/getting-started/docker-compose' },
      { text: 'Prima configurazione', link: '/getting-started/first-setup' },
    ],
  },
  {
    text: 'Configurazione',
    items: [
      { text: 'WebUI', link: '/configuration/webui' },
      {
        text: 'Aggiornamenti database',
        link: '/configuration/database-updates',
      },
      {
        text: 'Elaborazione risultati',
        link: '/configuration/result-processing',
      },
      { text: 'Integrazione Prowlarr', link: '/configuration/prowlarr' },
      { text: "Variabili d'ambiente", link: '/configuration/environment' },
    ],
  },
  {
    text: 'Funzionalità',
    items: [
      { text: 'Torznab', link: '/features/torznab' },
      { text: 'Priorità italiana', link: '/features/italian-ranking' },
      { text: 'Filtri personalizzati', link: '/features/custom-filters' },
      {
        text: 'Aggiornamenti automatici',
        link: '/features/automatic-db-updates',
      },
    ],
  },
  {
    text: 'Come funziona',
    items: [
      { text: 'Architettura', link: '/how-it-works/architecture' },
      { text: 'PostgreSQL', link: '/how-it-works/postgresql' },
      { text: 'Sistema snapshot', link: '/how-it-works/snapshots' },
      { text: 'Aggiornamenti sicuri', link: '/how-it-works/safe-updates' },
      {
        text: 'Elaborazione risultati',
        link: '/how-it-works/result-processing',
      },
    ],
  },
  {
    text: 'Riferimenti',
    items: [
      { text: 'API', link: '/reference/api' },
      { text: 'Funzionalità Torznab', link: '/reference/torznab-capabilities' },
      {
        text: 'Schema di configurazione',
        link: '/reference/configuration-schema',
      },
    ],
  },
  {
    text: 'Aiuto',
    items: [
      { text: 'Risoluzione problemi', link: '/troubleshooting' },
      { text: 'Changelog', link: '/changelog' },
    ],
  },
]

const englishLabels: Record<string, string> = {
  'Per iniziare': 'Getting Started',
  Configurazione: 'Configuration',
  Funzionalità: 'Features',
  'Come funziona': 'How it works',
  Riferimenti: 'Reference',
  Aiuto: 'Help',
  Installazione: 'Installation',
  'Prima configurazione': 'First setup',
  'Aggiornamenti database': 'Database updates',
  'Elaborazione risultati': 'Result processing',
  'Integrazione Prowlarr': 'Prowlarr integration',
  "Variabili d'ambiente": 'Environment variables',
  'Priorità italiana': 'Italian ranking',
  'Filtri personalizzati': 'Custom filters',
  'Aggiornamenti automatici': 'Automatic DB updates',
  Architettura: 'Architecture',
  'Sistema snapshot': 'Snapshot system',
  'Aggiornamenti sicuri': 'Safe updates',
  'Funzionalità Torznab': 'Torznab capabilities',
  'Schema di configurazione': 'Configuration schema',
  'Risoluzione problemi': 'Troubleshooting',
}

const englishSidebar = italianSidebar.map((section) => ({
  ...section,
  text: englishLabels[section.text] ?? section.text,
  items: section.items.map((item) => ({
    ...item,
    text: englishLabels[item.text] ?? item.text,
    link: `/en${item.link}`,
  })),
}))

export default defineConfig({
  title: 'Violarr',
  description: 'L’integrazione Prowlarr per Il Corsaro Viola',
  base: '/violarr/',
  cleanUrls: true,
  lastUpdated: true,
  head: [['meta', { name: 'theme-color', content: '#7c3aed' }]],
  locales: {
    root: {
      label: 'Italiano',
      lang: 'it-IT',
      themeConfig: {
        siteTitle: 'Violarr',
        nav: [
          { text: 'Per iniziare', link: '/getting-started/installation' },
          { text: 'Configurazione', link: '/configuration/webui' },
          { text: 'Funzionalità', link: '/features/torznab' },
          { text: 'Come funziona', link: '/how-it-works/architecture' },
          { text: 'Riferimenti', link: '/reference/api' },
          {
            text: 'Aiuto',
            items: [
              { text: 'Risoluzione problemi', link: '/troubleshooting' },
              { text: 'Changelog', link: '/changelog' },
            ],
          },
        ],
        sidebar: italianSidebar,
        outline: { label: 'In questa pagina' },
        docFooter: { prev: 'Pagina precedente', next: 'Pagina successiva' },
        editLink: {
          pattern: 'https://github.com/xbit18/violarr/edit/main/docs/:path',
          text: 'Modifica questa pagina su GitHub',
        },
        footer: {
          message: 'Distribuito con licenza MIT.',
          copyright: 'Documentazione Violarr',
        },
      },
    },
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
      title: 'Violarr',
      description: 'The Prowlarr integration for Il Corsaro Viola',
      themeConfig: {
        siteTitle: 'Violarr',
        nav: [
          { text: 'Getting Started', link: '/en/getting-started/installation' },
          { text: 'Configuration', link: '/en/configuration/webui' },
          { text: 'Features', link: '/en/features/torznab' },
          { text: 'How it works', link: '/en/how-it-works/architecture' },
          { text: 'Reference', link: '/en/reference/api' },
          {
            text: 'Help',
            items: [
              { text: 'Troubleshooting', link: '/en/troubleshooting' },
              { text: 'Changelog', link: '/en/changelog' },
            ],
          },
        ],
        sidebar: englishSidebar,
        outline: { label: 'On this page' },
        docFooter: { prev: 'Previous page', next: 'Next page' },
        editLink: {
          pattern: 'https://github.com/xbit18/violarr/edit/main/docs/:path',
          text: 'Edit this page on GitHub',
        },
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Violarr documentation',
        },
      },
    },
  },
  themeConfig: {
    socialLinks: [
      { icon: 'github', link: 'https://github.com/xbit18/violarr' },
    ],
    search: { provider: 'local' },
  },
})
