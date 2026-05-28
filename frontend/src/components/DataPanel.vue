<script setup lang="ts">
defineProps<{
  title?: string
  description?: string
}>()
</script>

<template>
  <section class="data-panel">
    <div v-if="title || description || $slots.actions" class="data-panel__header">
      <div>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="description">{{ description }}</p>
      </div>
      <div v-if="$slots.actions" class="data-panel__actions">
        <slot name="actions" />
      </div>
    </div>
    <slot />
  </section>
</template>
