<script setup lang="ts">
import { ref } from 'vue';

const message = ref('World');
</script>

<template>
  <div>
    Hello {{message}}
  </div>
</template>
