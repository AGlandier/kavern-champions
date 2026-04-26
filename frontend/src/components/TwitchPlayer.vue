<script setup>
import { computed } from 'vue'

const props = defineProps({
  channel: {
    type: String,
    required: true,
  },
  parent: {
    type: [String, Array],
    default: 'localhost',
  },
})

const src = computed(() => {
  const parents = Array.isArray(props.parent) ? props.parent : [props.parent]
  const params = new URLSearchParams({ channel: props.channel })
  parents.forEach(p => params.append('parent', p))
  return `https://player.twitch.tv/?${params}`
})
</script>

<template>
  <div class="twitch-player-wrapper">
    <div class="twitch-player-container">
      <iframe
        :src="src"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>
