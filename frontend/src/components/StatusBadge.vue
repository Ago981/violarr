<script setup lang="ts">
defineProps<{ tone?: 'success' | 'warning' | 'danger' | 'neutral'; label: string }>()
</script>
<template>
  <span class="badge" :class="`badge--${tone ?? 'neutral'}`">{{ label }}</span>
</template>
