<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  title: string
  value: string
  caption?: string
  tone?: 'neutral' | 'good' | 'warn' | 'danger'
  icon?: Component
}>()
</script>

<template>
  <article class="metric-card" :class="tone ? `metric-card--${tone}` : ''">
    <div class="metric-card__top">
      <span class="metric-card__title">{{ title }}</span>
      <span v-if="icon" class="metric-card__icon"><component :is="icon" :size="18" /></span>
    </div>
    <strong>{{ value }}</strong>
    <small v-if="caption">{{ caption }}</small>
  </article>
</template>
