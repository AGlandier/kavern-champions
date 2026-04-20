<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  loading: Boolean,
})
const emit = defineEmits(['submit'])

const teamlist = ref(props.modelValue)

watch(() => props.modelValue, (val) => { teamlist.value = val })
</script>

<template>
  <form class="teamlist-form" @submit.prevent="emit('submit', teamlist)">
    <textarea
      v-model="teamlist"
      class="kc-input teamlist-form__textarea"
      placeholder="Entrez votre teamlist..."
      rows="6"
    />
    <button type="submit" class="kc-btn" :disabled="loading">
      Enregistrer
    </button>
  </form>
</template>
