<script setup lang="ts">
defineProps<{ modelValue: boolean; label: string; description?: string; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
</script>
<template>
  <label class="toggle-row">
    <span
      ><strong>{{ label }}</strong
      ><small v-if="description">{{ description }}</small></span
    >
    <input
      :checked="modelValue"
      :disabled="disabled"
      type="checkbox"
      role="switch"
      @change="emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
    />
  </label>
</template>
