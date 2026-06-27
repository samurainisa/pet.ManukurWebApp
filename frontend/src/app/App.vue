<template>
  <div class="min-h-screen">
    <RouterView />
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'

import ToastContainer from '@/shared/ui/ToastContainer.vue'
</script>
