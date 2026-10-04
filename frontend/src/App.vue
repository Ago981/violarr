<script setup lang="ts">
import AppShell from './components/AppShell.vue'
import { useLocale } from './i18n'

const { t } = useLocale()
</script>
<template>
  <a class="skip-link" href="#main-content">{{ t('app.skip') }}</a
  ><AppShell />
</template>
