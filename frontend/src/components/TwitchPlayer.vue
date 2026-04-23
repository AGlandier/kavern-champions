<script setup>
defineProps({
  channel: {
    type: String,
    required: true,
  },
  parent: {
    type: String,
    default: 'localhost',
  },
})
</script>

<template>
  <div class="twitch-player-wrapper">
    <div class="twitch-player-container">
      <iframe
        :src="`https://player.twitch.tv/?channel=${channel}&parent=${parent}`"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>
